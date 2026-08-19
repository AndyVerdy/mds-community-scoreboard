#!/usr/bin/env python3
"""#18 — load a team-written document into the org knowledge library.

  python3 scripts/load_org_docs.py <file.pdf> --title "..." --type faq|sop|policy|guide \
      [--audience member|staff] [--event "MDS Summit Singapore"] [--topics a,b] [--dry-run]

Parsing (review with --dry-run before every first load — extraction is heuristic):
  faq          lines that END WITH ? and are short become questions; everything up
               to the next question is the answer (kind='qa')
  sop/policy/guide
               paragraph blocks grouped to ~900 chars; the first line of each
               block names the section (kind='section')

AUDIENCE IS FAIL-CLOSED: default 'staff' — a doc only reaches member answers when
loaded with --audience member on purpose. Embeddings: voyage-3.5-lite @ 1024, the
same model as every other vector in the warehouse (mixing models breaks distance).
Idempotent per title: reloading a title replaces its entries.
"""
import argparse, json, os, re, subprocess, sys

ENV = "/Users/Born/mds-digest-web/.env.local"
SUPA = "https://nadtudwuwjhckotrngzn.supabase.co/rest/v1"
MODEL, DIM = "voyage-3.5-lite", 1024


def env(k):
    for l in open(ENV):
        if l.startswith(k + "="):
            return l.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"missing {k} in {ENV}")


def supa(method, path, key, body=None, prefer=None, schema="digest"):
    cmd = ["curl", "-s", "-m", "60", "-X", method, f"{SUPA}/{path}",
           "-H", f"Authorization: Bearer {key}", "-H", f"apikey: {key}",
           "-H", f"Accept-Profile: {schema}", "-H", f"Content-Profile: {schema}",
           "-H", "Content-Type: application/json"]
    if prefer:
        cmd += ["-H", f"Prefer: {prefer}"]
    if body is not None:
        cmd += ["--data-binary", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out or "[]")
    except json.JSONDecodeError:
        return {"_raw": out[:300]}


def voyage_embed(texts, key):
    r = subprocess.run(
        ["curl", "-sS", "-X", "POST", "https://api.voyageai.com/v1/embeddings",
         "-H", f"Authorization: Bearer {key}", "-H", "Content-Type: application/json",
         "--max-time", "120", "--data-binary", "@-"],
        input=json.dumps({"model": MODEL, "input": texts, "input_type": "document",
                          "output_dimension": DIM}),
        capture_output=True, text=True)
    d = json.loads(r.stdout)
    if "data" not in d:
        sys.exit(f"voyage error: {str(d)[:300]}")
    return [row["embedding"] for row in d["data"]]


def extract_text(path):
    if not path.lower().endswith(".pdf"):
        return open(path, encoding="utf-8").read()
    r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout
    sys.exit(f"pdftotext failed on {path}: {r.stderr[:200]}")


def parse_faq(text):
    """A question is a shortish line ending in '?'. Everything to the next
    question is its answer. Front-matter before the first question is dropped.
    A heading wrapped across two lines ("...add items after / purchasing?") is
    re-joined: the previous line is folded in when it reads like a heading
    fragment (short, capitalized, no closing punctuation). Duplicate questions
    (multi-tab exports repeat sections) keep the LONGEST answer."""
    entries, q, buf = [], None, []

    def flush():
        if q and "\n".join(buf).strip():
            entries.append({"kind": "qa", "question": q, "body": "\n".join(buf).strip()})

    for raw in text.splitlines():
        line = raw.strip()
        if re.fullmatch(r".{4,120}\?", line):
            prev = buf[-1].strip() if buf else ""
            if (prev and len(prev) < 70 and prev[0].isupper()
                    and not re.search(r"[.:!?]$", prev) and len(line) < 60):
                line = prev + " " + line
                buf.pop()
            flush()
            q, buf = line, []
        elif q is not None:
            buf.append(line)
    flush()

    best = {}
    for e in entries:
        k = e["question"].lower()
        if k not in best or len(e["body"]) > len(best[k]["body"]):
            best[k] = e
    return list(best.values())


def parse_faq_table(text):
    """The 'Possible Question | Answer | Category' table layout: pdftotext -layout
    preserves columns, so split every line at the offsets of 'Answer' and
    'Category' in the header row. Question fragments accumulate in the left
    column; a new row starts when left-column text reappears after blank left
    lines. Category becomes a topic tag on the entry."""
    lines = text.splitlines()
    hdr = next((l for l in lines if "Possible Question" in l and "Answer" in l), None)
    if not hdr:
        return None
    # The header row is CENTERED — its 'Answer' offset lies. Data columns are
    # left-aligned: questions at col 0, answers ~col 26, category ~col 77
    # (measured). Only the Category header offset is trustworthy.
    c_off = hdr.index("Category") - 4 if "Category" in hdr else 10**6
    Q_MAX = 24
    entries, q, a, cat, left_gap, new_cat_armed = [], [], [], [], True, False

    def flush():
        if q and a:
            entries.append({"kind": "qa", "question": " ".join(q).strip(" ?") + "?",
                            "body": "\n".join(x for x in a if x).strip(),
                            "section_path": ", ".join(dict.fromkeys(cat)) or None})

    for l in lines[lines.index(hdr) + 1:]:
        cells = [(m.start(1), m.group(1).strip())
                 for m in re.finditer(r"(?:^|\s{3,})(\S(?:.*?\S)?)(?=\s{3,}|$)", l)]
        left = " ".join(t for s, t in cells if s < Q_MAX)
        mid = " ".join(t for s, t in cells if Q_MAX <= s < c_off)
        right = " ".join(t for s, t in cells if s >= c_off)
        # A wrapped question spans several left-column fragments with answer
        # lines between them — a new ROW begins when the fresh left fragment
        # starts a sentence AND either the accumulated question reads complete
        # (ends in ?) or a NEW category value has appeared (some source rows
        # omit the question mark; a category that does not end in ',' belongs
        # to the next row).
        if left and left_gap and q and left[0].isupper() \
                and (" ".join(q).rstrip().endswith("?") or new_cat_armed):
            flush()
            q, a, cat = [], [], []
            new_cat_armed = False
        if left:
            q.append(left)
        left_gap = not left
        if mid:
            a.append(mid)
        elif a and not l.strip():
            a.append("")
        if right:
            if cat and not cat[-1].endswith(","):
                new_cat_armed = True
            cat.append(right)
    flush()
    for e in entries:
        if e.get("section_path"):
            e["section_path"] = re.sub(r",\s*,", ",", e["section_path"]).strip(", ")
    return entries


def parse_sections(text, max_chars=900):
    """Paragraph blocks packed to ~max_chars; the first line of each pack names it."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    entries, buf = [], ""
    for p in paras:
        if buf and len(buf) + len(p) > max_chars:
            entries.append(buf)
            buf = p
        else:
            buf = (buf + "\n\n" + p).strip()
    if buf:
        entries.append(buf)
    return [{"kind": "section",
             "section_path": e.splitlines()[0][:120],
             "body": e} for e in entries]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--title", required=True)
    ap.add_argument("--type", required=True, choices=["faq", "sop", "policy", "guide"])
    ap.add_argument("--audience", default="staff", choices=["member", "staff"])
    ap.add_argument("--event", help="event TITLE in event.events; scopes the doc")
    ap.add_argument("--topics", help="comma-separated")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    key = env("SUPABASE_SECRET_KEY")

    text = extract_text(os.path.expanduser(args.path))
    if args.type == "faq":
        entries = parse_faq_table(text) or parse_faq(text)
    else:
        entries = parse_sections(text)
    assert len(entries) >= 3, f"only {len(entries)} entries parsed — wrong file or parser miss; refusing"

    print(f"{args.title}: {len(entries)} {entries[0]['kind']} entries · audience={args.audience}"
          + (f" · event={args.event}" if args.event else ""))
    for e in entries:
        label = e.get("question") or e.get("section_path")
        print(f"  - {label[:100]}  [{len(e['body'])} ch]")
    if args.dry_run:
        print("(dry run, nothing written)")
        return

    event_id = None
    if args.event:
        ev = supa("GET", f"events?select=id&title=eq.{args.event.replace(' ', '%20')}", key, schema="event")
        assert isinstance(ev, list) and len(ev) == 1, f"event lookup failed: {ev}"
        event_id = ev[0]["id"]

    doc = {"title": args.title, "doc_type": args.type, "audience": args.audience,
           "event_id": event_id, "source_file": os.path.basename(args.path),
           "topics": args.topics.split(",") if args.topics else None}
    r = supa("POST", "docs?on_conflict=title", key, [doc],
             prefer="resolution=merge-duplicates,return=representation")
    assert isinstance(r, list) and r and r[0].get("id"), f"doc upsert failed: {r}"
    doc_id = r[0]["id"]

    supa("DELETE", f"doc_entries?doc_id=eq.{doc_id}", key, prefer="return=minimal")

    embed_texts = [(e.get("question") or "") + "\n" + e["body"] for e in entries]
    vecs = []
    for i in range(0, len(embed_texts), 96):
        vecs += voyage_embed(embed_texts[i:i + 96], env("VOYAGE_API_KEY"))
    rows = [{"doc_id": doc_id, "kind": e["kind"], "question": e.get("question"),
             "body": e["body"], "section_path": e.get("section_path"),
             "order_idx": i, "embedding": vecs[i]}
            for i, e in enumerate(entries)]
    r = supa("POST", "doc_entries", key, rows, prefer="return=minimal")
    assert not (isinstance(r, dict) and r.get("_raw")), f"entries insert failed: {r}"

    n = supa("GET", f"doc_entries?select=id&doc_id=eq.{doc_id}", key)
    print(f"loaded doc {doc_id}: {len(n)} entries, embedded {len(vecs)}")


if __name__ == "__main__":
    main()
