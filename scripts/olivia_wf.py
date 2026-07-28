#!/usr/bin/env python3
"""
Olivia workflow safety tool — staging copy, named snapshots, one-command rollback,
and a single-editor lock.

Why this exists (backlog #4): edits went straight into the workflow members are
talking to. No test copy, no rollback. Two sessions overwrote each other; one bad
edit killed every inbound for eight minutes; Andy was testing on his real number
while the live graph was being rewritten under him.

The three guarantees:
  1. A test copy takes the change first        -> `stage`, then `promote`
  2. A named version to roll back to           -> `snapshot`, then `rollback`
  3. One editing session at a time, ENFORCED   -> `lock` + the PreToolUse hook
     (.claude/hooks/olivia_wf_lock.py blocks n8n writes to the prod workflow
      when the lock is missing, expired, or held by someone else)

Usage
  python3 scripts/olivia_wf.py status
  python3 scripts/olivia_wf.py lock   --reason "why" [--session <id>] [--force]
  python3 scripts/olivia_wf.py unlock

  python3 scripts/olivia_wf.py snapshot [--label good-before-x] [--target prod|staging]
  python3 scripts/olivia_wf.py list
  python3 scripts/olivia_wf.py diff <A> <B>        # A/B = prod | staging | snapshot file/label

  python3 scripts/olivia_wf.py stage               # prod graph -> staging copy (creates it once)
  python3 scripts/olivia_wf.py promote             # staging graph -> prod (gate + validate + bounce)
  python3 scripts/olivia_wf.py rollback <snapshot> # snapshot -> prod (fast path, no gate)

Rules baked in, not remembered:
  - every write to prod snapshots prod FIRST (pre-promote / pre-rollback)
  - the webhook path + webhookId of the TARGET always win, so a staging graph can
    never carry the live Meta path onto the wrong workflow (or vice versa)
  - activation order is always edit -> ONE deactivate+activate bounce, never
    deactivate-first (that is what killed 8.5h of inbounds on 2026-07-21)
  - `promote` requires the leak gate GREEN; `rollback` deliberately skips it so the
    emergency path is fast
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = "/Users/Born/mds-digest-web/.env.local"
SNAP_DIR = os.path.join(REPO, "olivia_snapshots")
TARGETS_PATH = os.path.join(SNAP_DIR, "_targets.json")
LOCK_PATH = os.path.join(REPO, ".olivia_wf.lock")
GATE = os.path.join(REPO, "scripts", "olivia_leak_gate.py")

PROD_ID = "12wj6h1TWqb0d4Dq"
PROD_WEBHOOK_PATH = "olivia-wa-live"
STAGING_WEBHOOK_PATH = "olivia-wa-staging"
STAGING_NAME = "Olivia WA — STAGING (test copy · Meta must never point here)"
LOCK_TTL_MIN = 120

GRAPH_KEYS = ("name", "nodes", "connections", "settings")

# The public API validates `settings` against a narrower schema than the UI writes
# (prod carries `binaryMode`, which the API rejects on POST and PUT — the n8n MCP
# drops it silently too). So every write sends the representable subset of the
# TARGET's own settings and then reads them back; put_graph() shouts if the API
# dropped anything, because a lost setting is invisible until something stops working.
API_SETTINGS_KEYS = ("errorWorkflow", "executionOrder", "executionTimeout",
                     "saveDataErrorExecution", "saveDataSuccessExecution",
                     "saveExecutionProgress", "saveManualExecutions", "timezone")


# ---------------------------------------------------------------- env / http

def env(key):
    with open(ENV_PATH) as fh:
        for line in fh:
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    sys.exit(f"{key} not found in {ENV_PATH}")


def api(method, path, payload=None, retries=3):
    """n8n public API via curl (urllib has SSL trouble on this Mac).

    Retries are safe for GET/PUT/activate (idempotent) but NOT for creating a
    workflow — a lost response there would leave a duplicate behind, so `stage`
    passes retries=1 and reconciles by name instead."""
    base = env("N8N_API_URL").rstrip("/")
    cmd = ["curl", "-sS", "-X", method, f"{base}/api/v1{path}",
           "-H", f"X-N8N-API-KEY: {env('N8N_API_KEY')}",
           "-H", "Content-Type: application/json",
           "--connect-timeout", "20", "--max-time", "180",
           "-w", "\n%{http_code}"]
    if payload is not None:
        cmd += ["--data-binary", "@-"]
    body_in = json.dumps(payload) if payload is not None else None
    for attempt in range(1, retries + 1):
        res = subprocess.run(cmd, input=body_in, capture_output=True, text=True)
        if res.returncode == 0:
            break
        # half-megabyte graph writes to n8n cloud drop a connection now and then
        print(f"  curl attempt {attempt} failed ({res.stderr.strip()[:120]})")
        if attempt < retries:
            time.sleep(3)
    if res.returncode != 0:
        sys.exit(f"curl failed after {retries} attempt(s): {res.stderr.strip()}")
    body, _, code = res.stdout.rpartition("\n")
    try:
        parsed = json.loads(body) if body.strip() else None
    except json.JSONDecodeError:
        parsed = body
    return int(code), parsed


def fetch(workflow_id):
    code, wf = api("GET", f"/workflows/{workflow_id}")
    if code != 200:
        sys.exit(f"GET workflow {workflow_id} -> HTTP {code}: {str(wf)[:300]}")
    return wf


# ---------------------------------------------------------------- targets

def targets():
    if os.path.exists(TARGETS_PATH):
        with open(TARGETS_PATH) as fh:
            return json.load(fh)
    return {"prod": PROD_ID, "staging": None}


def save_targets(t):
    os.makedirs(SNAP_DIR, exist_ok=True)
    with open(TARGETS_PATH, "w") as fh:
        json.dump(t, fh, indent=2, sort_keys=True)
        fh.write("\n")


def resolve_id(name):
    t = targets()
    if name == "prod":
        return t["prod"]
    if name == "staging":
        if not t.get("staging"):
            sys.exit("no staging workflow yet — run: python3 scripts/olivia_wf.py stage")
        return t["staging"]
    sys.exit(f"unknown target {name!r} (use prod|staging)")


# ---------------------------------------------------------------- lock

def read_lock():
    if not os.path.exists(LOCK_PATH):
        return None
    with open(LOCK_PATH) as fh:
        lock = json.load(fh)
    if datetime.now(timezone.utc) > datetime.fromisoformat(lock["expires_at"]):
        return None          # expired locks are dead, not sticky
    return lock


def cmd_lock(args):
    held = read_lock()
    if held and not args.force:
        sys.exit(f"LOCKED by {held['holder']} since {held['acquired_at']} "
                 f"(expires {held['expires_at']})\nreason: {held.get('reason')}\n"
                 f"If that session is gone: python3 scripts/olivia_wf.py lock --force --reason ...")
    if held and args.force:
        print(f"⚠ stealing lock from {held['holder']} ({held.get('reason')})")
    now = datetime.now(timezone.utc)
    lock = {
        "holder": args.holder or f"{os.environ.get('USER', 'unknown')}@{os.uname().nodename}",
        # the agent session id, so the PreToolUse hook can tell THIS session's
        # n8n writes apart from a second session's
        "session": args.session or os.environ.get("CLAUDE_CODE_SESSION_ID"),
        "pid": os.getpid(),
        "reason": args.reason,
        "acquired_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=LOCK_TTL_MIN)).isoformat(),
    }
    with open(LOCK_PATH, "w") as fh:
        json.dump(lock, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"LOCK ACQUIRED by {lock['holder']} until {lock['expires_at']}")
    print("Prod edits are now permitted for this session only. Staging-first is still the path:")
    print("  stage -> edit staging -> test -> promote")


def cmd_unlock(_args):
    if os.path.exists(LOCK_PATH):
        os.remove(LOCK_PATH)
        print("LOCK RELEASED")
    else:
        print("no lock held")


def require_lock(action):
    lock = read_lock()
    if not lock:
        sys.exit(f"REFUSED: {action} needs the editing lock.\n"
                 f"  python3 scripts/olivia_wf.py lock --reason \"<what you are changing>\"")
    print(f"lock held by {lock['holder']} (expires {lock['expires_at']})")


# ---------------------------------------------------------------- snapshots

def graph_of(wf):
    return {k: wf.get(k) for k in GRAPH_KEYS}


def snap_path(label_or_file):
    for cand in (label_or_file,
                 os.path.join(SNAP_DIR, label_or_file),
                 os.path.join(SNAP_DIR, label_or_file + ".json")):
        if os.path.isfile(cand):
            return cand
    matches = sorted(f for f in os.listdir(SNAP_DIR)
                     if f.endswith(".json") and label_or_file in f) if os.path.isdir(SNAP_DIR) else []
    if len(matches) == 1:
        return os.path.join(SNAP_DIR, matches[0])
    if len(matches) > 1:
        sys.exit(f"{label_or_file!r} matches {len(matches)} snapshots: {matches}")
    sys.exit(f"no snapshot matching {label_or_file!r} — run: python3 scripts/olivia_wf.py list")


def take_snapshot(target, label):
    wf = fetch(resolve_id(target))
    os.makedirs(SNAP_DIR, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    safe = re.sub(r"[^a-z0-9-]+", "-", (label or "snapshot").lower()).strip("-")
    path = os.path.join(SNAP_DIR, f"{target}_{stamp}_{safe}.json")
    doc = {
        "_meta": {
            "target": target,
            "workflow_id": wf["id"],
            "workflow_name": wf.get("name"),
            "active": wf.get("active"),
            "version_id": wf.get("versionId"),
            "version_counter": wf.get("versionCounter"),
            "taken_at": stamp,
            "label": label,
            "node_count": len(wf.get("nodes") or []),
        },
        **graph_of(wf),
    }
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    print(f"snapshot -> {os.path.relpath(path, REPO)}  "
          f"({doc['_meta']['node_count']} nodes, versionId {doc['_meta']['version_id']})")
    return path


def load_graph(ref):
    """ref = 'prod' | 'staging' | snapshot label/path."""
    if ref in ("prod", "staging"):
        return graph_of(fetch(resolve_id(ref))), ref
    path = snap_path(ref)
    with open(path) as fh:
        doc = json.load(fh)
    return {k: doc.get(k) for k in GRAPH_KEYS}, os.path.relpath(path, REPO)


def cmd_snapshot(args):
    take_snapshot(args.target, args.label)


def cmd_list(_args):
    if not os.path.isdir(SNAP_DIR):
        print("no snapshots yet")
        return
    files = sorted(f for f in os.listdir(SNAP_DIR) if f.endswith(".json") and not f.startswith("_"))
    if not files:
        print("no snapshots yet")
        return
    for f in files:
        with open(os.path.join(SNAP_DIR, f)) as fh:
            m = json.load(fh).get("_meta", {})
        print(f"{f}\n    {m.get('node_count')} nodes · versionId {m.get('version_id')} · {m.get('label')}")


# ---------------------------------------------------------------- diff

def cmd_diff(args):
    a, a_name = load_graph(args.a)
    b, b_name = load_graph(args.b)
    an = {n["name"]: n for n in a["nodes"]}
    bn = {n["name"]: n for n in b["nodes"]}
    added = sorted(set(bn) - set(an))
    removed = sorted(set(an) - set(bn))
    changed = sorted(n for n in set(an) & set(bn)
                     if json.dumps(an[n], sort_keys=True) != json.dumps(bn[n], sort_keys=True))
    conn_same = json.dumps(a["connections"], sort_keys=True) == json.dumps(b["connections"], sort_keys=True)
    print(f"A = {a_name} ({len(an)} nodes)\nB = {b_name} ({len(bn)} nodes)\n")
    print(f"added   : {added or '—'}")
    print(f"removed : {removed or '—'}")
    print(f"changed : {changed or '—'}")
    print(f"connections: {'identical' if conn_same else 'DIFFERENT'}")
    for n in changed:
        ap, bp = an[n].get("parameters", {}), bn[n].get("parameters", {})
        keys = sorted(set(ap) | set(bp))
        fields = [k for k in keys
                  if json.dumps(ap.get(k), sort_keys=True) != json.dumps(bp.get(k), sort_keys=True)]
        meta = sorted(k for k in set(an[n]) | set(bn[n])
                      if k != "parameters"
                      and json.dumps(an[n].get(k), sort_keys=True) != json.dumps(bn[n].get(k), sort_keys=True))
        print(f"  · {n}: params{fields or []}{' meta' + str(meta) if meta else ''}")
    if not (added or removed or changed) and conn_same:
        print("\nIDENTICAL")


# ---------------------------------------------------------------- writes

def apply_webhook_identity(graph, target_wf):
    """The TARGET's webhook path + webhookId always win — a graph can never carry
    the live Meta path onto staging, or the staging path onto prod."""
    live = {n["name"]: n for n in (target_wf.get("nodes") or [])
            if n["type"] == "n8n-nodes-base.webhook"}
    fallback_path = STAGING_WEBHOOK_PATH if target_wf["id"] != PROD_ID else PROD_WEBHOOK_PATH
    for node in graph["nodes"]:
        if node["type"] != "n8n-nodes-base.webhook":
            continue
        twin = live.get(node["name"])
        if twin:
            node["parameters"]["path"] = twin["parameters"].get("path", fallback_path)
            node["webhookId"] = twin.get("webhookId") or str(uuid.uuid4())
        else:
            node["parameters"]["path"] = fallback_path
            node["webhookId"] = str(uuid.uuid4())
    return graph


def api_settings(settings):
    return {k: v for k, v in (settings or {}).items() if k in API_SETTINGS_KEYS}


def put_graph(workflow_id, graph, keep_name, keep_settings):
    """Write the graph, keeping the TARGET's settings.

    The public API rejects settings keys it doesn't know (`binaryMode` is UI-only,
    and prod carries it), so we send the representable subset and then read the
    settings back — a silently dropped setting is the kind of change nobody would
    notice until images stopped sending."""
    body = {"name": keep_name, "nodes": graph["nodes"], "connections": graph["connections"],
            "settings": api_settings(keep_settings)}
    code, res = api("PUT", f"/workflows/{workflow_id}", body)
    if code not in (200, 201):
        sys.exit(f"PUT failed HTTP {code}: {str(res)[:500]}")
    after = fetch(workflow_id).get("settings") or {}
    lost = {k: v for k, v in (keep_settings or {}).items() if k not in after}
    if lost:
        print(f"⚠ SETTINGS DROPPED BY THE API: {lost}\n"
              f"  re-set them in n8n: Workflow → ⋯ → Settings (the API cannot write them)")
    else:
        print("settings preserved:", json.dumps(after, sort_keys=True))
    return res


def bounce(workflow_id):
    """Edit first, THEN one deactivate+activate. Never deactivate before editing."""
    c1, _ = api("POST", f"/workflows/{workflow_id}/deactivate")
    c2, _ = api("POST", f"/workflows/{workflow_id}/activate")
    print(f"bounce: deactivate {c1} -> activate {c2}")
    if c2 != 200:
        sys.exit("ACTIVATION FAILED — the workflow is DOWN. Re-activate in n8n immediately.")


def run_gate():
    print("running leak gate…")
    res = subprocess.run([sys.executable, GATE], capture_output=True, text=True)
    tail = res.stdout.strip().splitlines()[-2:] if res.stdout else []
    print("  " + "\n  ".join(tail))
    if res.returncode != 0:
        sys.exit("GATE RED — refusing to write. Fix the gate first.")


def find_by_name(name):
    code, res = api("GET", "/workflows?limit=250")
    if code != 200:
        sys.exit(f"list workflows -> HTTP {code}")
    hits = [w for w in res.get("data", []) if w.get("name") == name]
    return hits[0]["id"] if len(hits) == 1 else None


def cmd_stage(args):
    prod = fetch(PROD_ID)
    t = targets()
    if not t.get("staging"):
        # reconcile: a create whose response was lost still made the workflow
        orphan = find_by_name(STAGING_NAME)
        if orphan:
            print(f"adopting existing staging workflow {orphan}")
            t["staging"] = orphan
            save_targets(t)
    graph = graph_of(prod)
    if t.get("staging"):
        staging = fetch(t["staging"])
        take_snapshot("staging", "pre-stage")
        graph = apply_webhook_identity(graph, staging)
        put_graph(staging["id"], graph, staging["name"], staging.get("settings"))
        if staging.get("active"):
            bounce(staging["id"])
        print(f"staging {staging['id']} refreshed from prod ({len(graph['nodes'])} nodes)")
    else:
        graph = apply_webhook_identity(graph, {"id": "new", "nodes": []})
        code, created = api("POST", "/workflows", {
            "name": STAGING_NAME, "nodes": graph["nodes"],
            "connections": graph["connections"], "settings": api_settings(graph["settings"]),
        }, retries=1)
        if code not in (200, 201):
            sys.exit(f"create staging failed HTTP {code}: {str(created)[:500]}")
        t["staging"] = created["id"]
        save_targets(t)
        print(f"staging CREATED {created['id']} ({len(graph['nodes'])} nodes), inactive")
        print(f"activate it when you want to fire probes: "
              f"python3 scripts/olivia_wf.py activate --target staging")
    print(f"staging webhook: {env('N8N_API_URL')}/webhook/{STAGING_WEBHOOK_PATH}")


def cmd_promote(args):
    require_lock("promote")
    staging = fetch(resolve_id("staging"))
    prod = fetch(PROD_ID)
    graph = graph_of(staging)
    graph = apply_webhook_identity(graph, prod)
    a = {n["name"]: json.dumps(n, sort_keys=True) for n in prod["nodes"]}
    b = {n["name"]: json.dumps(n, sort_keys=True) for n in graph["nodes"]}
    delta = sorted(set(b) - set(a)) + sorted(set(a) - set(b)) + \
        sorted(n for n in set(a) & set(b) if a[n] != b[n])
    if not delta:
        print("staging is identical to prod — nothing to promote")
        return
    print(f"promoting {len(delta)} changed node(s): {delta}")
    if not args.skip_gate:
        run_gate()
    take_snapshot("prod", "pre-promote")
    put_graph(PROD_ID, graph, prod["name"], prod.get("settings"))
    if prod.get("active"):
        bounce(PROD_ID)
    after = fetch(PROD_ID)
    ok = json.dumps(graph["nodes"], sort_keys=True) == json.dumps(after["nodes"], sort_keys=True)
    print(f"prod now versionId {after.get('versionId')} · active={after.get('active')} · "
          f"graph matches staging: {ok}")
    take_snapshot("prod", args.label or "post-promote")


def cmd_rollback(args):
    require_lock("rollback")
    graph, src = load_graph(args.snapshot)
    prod = fetch(PROD_ID)
    graph = apply_webhook_identity(graph, prod)
    print(f"rolling prod back to {src} ({len(graph['nodes'])} nodes) "
          f"from live versionId {prod.get('versionId')}")
    take_snapshot("prod", "pre-rollback")
    put_graph(PROD_ID, graph, prod["name"], prod.get("settings"))
    if prod.get("active"):
        bounce(PROD_ID)
    after = fetch(PROD_ID)
    ok = json.dumps(graph["nodes"], sort_keys=True) == json.dumps(after["nodes"], sort_keys=True)
    print(f"ROLLED BACK — versionId {after.get('versionId')} · active={after.get('active')} · "
          f"graph matches snapshot: {ok}")
    if not ok:
        sys.exit("MISMATCH after rollback — inspect n8n now.")


def cmd_activate(args):
    wid = resolve_id(args.target)
    code, _ = api("POST", f"/workflows/{wid}/{'activate' if not args.off else 'deactivate'}")
    print(f"{args.target} {'deactivate' if args.off else 'activate'} -> HTTP {code}")


def cmd_status(_args):
    t = targets()
    lock = read_lock()
    print("LOCK  :", f"{lock['holder']} until {lock['expires_at']} — {lock.get('reason')}"
          if lock else "free")
    for name in ("prod", "staging"):
        wid = t.get(name)
        if not wid:
            print(f"{name.upper():6}: not created")
            continue
        wf = fetch(wid)
        paths = [n["parameters"].get("path") for n in wf["nodes"]
                 if n["type"] == "n8n-nodes-base.webhook"]
        print(f"{name.upper():6}: {wid} · active={wf.get('active')} · {len(wf['nodes'])} nodes · "
              f"webhook={sorted(set(paths))} · versionId {wf.get('versionId')}")
    if os.path.isdir(SNAP_DIR):
        snaps = sorted(f for f in os.listdir(SNAP_DIR) if f.endswith(".json") and not f.startswith("_"))
        print(f"SNAPS : {len(snaps)}" + (f" · newest {snaps[-1]}" if snaps else ""))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status").set_defaults(fn=cmd_status)

    lk = sub.add_parser("lock")
    lk.add_argument("--reason", required=True)
    lk.add_argument("--session", default=None, help="agent session id, so the hook can match it")
    lk.add_argument("--holder", default=None)
    lk.add_argument("--force", action="store_true")
    lk.set_defaults(fn=cmd_lock)

    sub.add_parser("unlock").set_defaults(fn=cmd_unlock)

    sn = sub.add_parser("snapshot")
    sn.add_argument("--label", default="snapshot")
    sn.add_argument("--target", default="prod", choices=["prod", "staging"])
    sn.set_defaults(fn=cmd_snapshot)

    sub.add_parser("list").set_defaults(fn=cmd_list)

    df = sub.add_parser("diff")
    df.add_argument("a")
    df.add_argument("b")
    df.set_defaults(fn=cmd_diff)

    sub.add_parser("stage").set_defaults(fn=cmd_stage)

    pr = sub.add_parser("promote")
    pr.add_argument("--label", default=None)
    pr.add_argument("--skip-gate", action="store_true")
    pr.set_defaults(fn=cmd_promote)

    rb = sub.add_parser("rollback")
    rb.add_argument("snapshot")
    rb.set_defaults(fn=cmd_rollback)

    ac = sub.add_parser("activate")
    ac.add_argument("--target", default="staging", choices=["prod", "staging"])
    ac.add_argument("--off", action="store_true")
    ac.set_defaults(fn=cmd_activate)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
