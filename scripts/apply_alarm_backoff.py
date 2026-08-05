import json, subprocess, tempfile, os
ENV="/Users/Born/mds-digest-web/.env.local"
def env(k):
    for l in open(ENV):
        if l.startswith(k+"="): return l.split("=",1)[1].strip().strip('"').strip("'")
BASE=env("N8N_API_URL").rstrip("/"); KEY=env("N8N_API_KEY")
WID="argZgYHPgdVKJqCS"
def api(m,p,payload=None):
    cmd=["curl","-sS","-X",m,f"{BASE}/api/v1{p}","-H","X-N8N-API-KEY: "+KEY,
         "-H","Content-Type: application/json","--max-time","180"]
    if payload is not None: cmd+=["--data-binary","@-"]
    r=subprocess.run(cmd,input=json.dumps(payload) if payload is not None else None,
                     capture_output=True,text=True)
    return json.loads(r.stdout)
wf=api("GET",f"/workflows/{WID}")
NEW = """// #16 (2026-08-01): UNLATCHED so an outage can never be buried — the old latch fired once on
// healthy->down and then went silent forever (that is how the 07-26 outage was lost).
// 2026-08-05 (Andy: "wtf is this spam"): un-latched was right, but a FLAT 30-min repeat is the
// same failure from the other side — the 2-day derive_niches outage produced ~96 identical
// messages and became scenery. Now it backs off while staying un-latched:
//     < 2h down  -> every 30 min   (the window where someone might act now)
//     < 12h      -> every 2h
//     < 48h      -> every 6h
//     >= 48h     -> once a day     (a standing fact, not news)
// Degraded still never pages; the daily summary covers steady state.
const data = $getWorkflowStaticData('global');
const cur = ($input.first().json.overall) || 'healthy';
const prev = data.lastHealth;
const now = Date.now();
const MIN = 60 * 1000, HOUR = 60 * MIN;
data.lastHealth = cur;
if (cur === 'down') {
  if (prev !== 'down' || !data.downSince) { data.downSince = now; }
  const age = now - data.downSince;
  const gap = age < 2 * HOUR ? 30 * MIN
            : age < 12 * HOUR ? 2 * HOUR
            : age < 48 * HOUR ? 6 * HOUR
            : 24 * HOUR;
  const repeatDue = !data.lastAlertAt || now - data.lastAlertAt > gap;
  if (prev !== 'down' || repeatDue) {
    data.lastAlertAt = now;
    return [{ json: { alert: true, from: prev || 'unknown', to: cur, repeat: prev === 'down',
                      down_for_min: Math.round(age / MIN), next_check_in_min: Math.round(gap / MIN) } }];
  }
  return [];
}
if (prev === 'down') {
  data.lastAlertAt = null; data.downSince = null;
  return [{ json: { alert: true, recovered: true, from: prev, to: cur } }];
}
data.lastAlertAt = null; data.downSince = null;
return [];"""
hit=False
for n in wf["nodes"]:
    if n["name"]=="Alert only on worsening":
        n["parameters"]["jsCode"]=NEW; hit=True
assert hit, "node not found"
with tempfile.NamedTemporaryFile("w",suffix=".js",delete=False) as f:
    f.write(NEW); tmp=f.name
chk=subprocess.run(["node","--check",tmp],capture_output=True,text=True); os.unlink(tmp)
assert chk.returncode==0, chk.stderr
print("node --check OK")
body={"name":wf["name"],"nodes":wf["nodes"],"connections":wf["connections"],
      "settings":{k:v for k,v in (wf.get("settings") or {}).items()
                  if k in ("errorWorkflow","executionOrder","executionTimeout",
                           "saveDataErrorExecution","saveDataSuccessExecution",
                           "saveExecutionProgress","saveManualExecutions","timezone")}}
r=api("PUT",f"/workflows/{WID}",body)
assert r.get("id"), str(r)[:300]
api("POST",f"/workflows/{WID}/deactivate"); api("POST",f"/workflows/{WID}/activate")
wf2=api("GET",f"/workflows/{WID}")
ok=any("downSince" in (n.get("parameters",{}).get("jsCode") or "") for n in wf2["nodes"])
print("VERIFY backoff live:", ok, "| active:", wf2.get("active"), "| version:", str(wf2.get("versionId"))[:8])
