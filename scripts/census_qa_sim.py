#!/usr/bin/env python3
"""
Census QA simulator + covering-set generator for the MDS Annual Census (Typeform DFeK5yop).

WHY THIS EXISTS: a Typeform's logic *definition* can look correct while the *runtime*
misbehaves (the 2026-07-29 group-exit bug: fields inside a question `group` that jump out
made Typeform end the form early). So QA is layered:
  L1  exhaustive logic sim  (this file, `sweep`)          -> catches logic errors
  L2  covering-set replay   (this file emits it, `cover`) -> drive the LIVE form, diff vs expected
  L3  data verification     (submit test rows -> Airtable)
  L4  human UAT

Usage:
  python3 census_qa_sim.py sweep      # exhaustive: every path, verify completion + gating
  python3 census_qa_sim.py cover      # emit minimal covering set (each branch >=1) + expected paths -> /tmp/census_cover.json
Token: CENTURION_TYPEFORM_PAT in mds-digest-web/.env.local. Form id below.
"""
import json, itertools, subprocess, sys, os
FORM_ID = "DFeK5yop"
ENV = "/Users/Born/mds-digest-web/.env.local"

def load_form():
    tok = subprocess.check_output(
        f"grep -E '^CENTURION_TYPEFORM_PAT=' {ENV} | cut -d= -f2- | tr -d '\"'", shell=True).decode().strip()
    out = subprocess.check_output(
        ["curl","-s","-H",f"Authorization: Bearer {tok}",f"https://api.typeform.com/forms/{FORM_ID}"])
    d = json.loads(out)
    if "fields" not in d: raise SystemExit("GET failed: "+str(d)[:200])
    return d

def build(d):
    linear=[]; gf={}
    for f in d["fields"]:
        if f.get("type")=="group":
            ks=f["properties"]["fields"]; gf[f["ref"]]=ks[0]["ref"] if ks else None
            for c in ks: linear.append((c["ref"],c["type"],f["ref"]))
        else: linear.append((f["ref"],f["type"],None))
    idx={r:i for i,(r,t,g) in enumerate(linear)}; grpof={r:g for r,t,g in linear}
    logic={x["ref"]:x["actions"] for x in d.get("logic",[])}
    def resolve(r): return idx[r] if r in idx else (idx.get(gf.get(r)) if r in gf else None)
    def exits(s,dst):
        sg=grpof.get(s)
        if sg is None: return False
        di=resolve(dst); dg=grpof[linear[di][0]] if di is not None else None
        return dg!=sg
    return linear,idx,grpof,logic,resolve,exits

def ev(c,a):
    o=c["op"]
    if o=="always": return True
    if o=="or":  return any(ev(v,a) for v in c["vars"])
    if o=="and": return all(ev(v,a) for v in c["vars"])
    if o in ("is","equal"):
        x,y=c["vars"]; f=x["value"]
        return (y["value"] in a.get(f,set())) if y["type"]=="choice" else (a.get(f)==y["value"])
    return False

def simulate(a, linear, logic, resolve, exits, quirk=False):
    i=0; path=[]; seen=set(); step=0
    while i is not None and 0<=i<len(linear):
        step+=1
        if step>500: return path,"LOOP"
        r=linear[i][0]
        if r in seen: return path,"LOOP"
        seen.add(r); path.append(r); nx=None; cr=False
        for act in logic.get(r,[]):
            if act["action"]=="add": continue
            if act["action"]=="jump" and ev(act["condition"],a):
                dst=act["details"]["to"]["value"]; cr=exits(r,dst); nx=dst; break
        if nx is not None:
            if quirk and cr: return path,"EARLY_SUBMIT"
            di=resolve(nx)
            if di is None: return path,"END"
            i=di
        else: i+=1
    return path,"END"

COUNTRIES=["m_cn","m_us","m_in","m_vn","m_mx","m_ot"]; CH=["c_dtc","c_tt","c_ret","c_other"]; SEC=["o_role","o_biz","o_ops","o_fam"]
OPBLOCK=["new_products","cogs_pct","ad_pct","opex_pct","cost_surprise"]  # cbm_cost removed per Eugene
def powset(xs): return [set(c) for r in range(len(xs)+1) for c in itertools.combinations(xs,r)]

def sweep():
    d=load_form(); linear,idx,grpof,logic,resolve,exits=build(d)
    S=lambda a,q=False: simulate(a,linear,logic,resolve,exits,q)
    scr_states=[set(c) for r in range(5) for c in itertools.combinations(SEC,r)]+[{"o_unsure"},{"o_none"}]
    progs=list(itertools.product([set(),{"chap_no"}],[set(),{"prog_no"}],[set(),{"squad_no"}]))
    distinct=set(); tested=0; fails=[]
    for scr in scr_states:
        fam=("o_fam" in scr) or ("o_unsure" in scr); ops=("o_ops" in scr) or ("o_unsure" in scr)
        kids=[(False,0),(True,0),(True,3)] if fam else [(True,3)]
        mfgs=powset(COUNTRIES) if ops else [set()]
        for hk,nk in kids:
         for mfg in mfgs:
          for chan in powset(CH):
           for inv in [{"op"},{"ci_inv"}]:
            for cn,pn,sn in progs:
             a=dict(screening=scr,have_kids=hk,num_kids=nk,mfg_locations=mfg,what_channels=chan,
                    current_involvement=inv,chapter_attend=cn,programs_part=pn,squad_attend=sn,activities=set())
             p,st=S(a); pq,sq=S(a,True); tested+=1; distinct.add(tuple(p))
             if st!="END" or "gsuite" not in p: fails.append(("no-complete",scr,st))
             if sq=="EARLY_SUBMIT": fails.append(("group-quirk-early",scr))
             nonop=inv=={"ci_inv"}; opshown=[q for q in OPBLOCK if q in p]
             if nonop and opshown: fails.append(("nonop-not-skipped",scr,opshown))
             if (not nonop) and len(opshown)!=len(OPBLOCK): fails.append(("operator-missing-opblock",scr,opshown))
             for c,q in [("c_dtc","pct_dtc"),("c_tt","pct_tiktok"),("c_ret","pct_retail"),("c_other","pct_other")]:
                 if (q in p)!=(c in chan): fails.append(("chan%",c,chan))
             for c,q in zip(COUNTRIES,["mfg_cn","mfg_us","mfg_in","mfg_vn","mfg_mx","mfg_ot"]):
                 if (q in p)!=((c in mfg) and ops): fails.append(("mfg%",c,scr))
    xg=sum(1 for x in d.get("logic",[]) for act in x["actions"]
           if act["action"]=="jump" and exits(x["ref"],act["details"]["to"]["value"]))
    print(f"combos tested : {tested}")
    print(f"distinct paths: {len(distinct)}")
    print(f"cross-group jumps (must be 0): {xg}")
    print(f"FAILURES: {len(fails)}")
    from collections import Counter
    for k,v in Counter(f[0] for f in fails).items(): print("   ",k,v)
    for f in fails[:10]: print("    e.g.",f)
    return 0 if (not fails and xg==0) else 1

def cover():
    """Minimal covering set: hit each structural branch >=1, emit expected question sequence for live replay."""
    d=load_form(); linear,idx,grpof,logic,resolve,exits=build(d)
    S=lambda a: simulate(a,linear,logic,resolve,exits)[0]
    cases=[]
    def add(name, **a):
        a.setdefault("activities",set())
        cases.append({"name":name,"answers":{k:(sorted(v) if isinstance(v,set) else v) for k,v in a.items()},
                      "expected_path":S(a)})
    add("none",        screening={"o_none"}, what_channels=set(), current_involvement={"op"})
    add("unsure-all",  screening={"o_unsure"}, have_kids=True,num_kids=2, mfg_locations={"m_cn","m_mx"}, what_channels=set(CH), current_involvement={"op"})
    for s in SEC:
        add(f"only-{s[2:]}", screening={s}, have_kids=True,num_kids=2, mfg_locations={"m_cn"}, what_channels=set(), current_involvement={"op"})
    add("fam-nokids",  screening={"o_fam"}, have_kids=False, current_involvement={"op"})
    add("fam-0kids",   screening={"o_fam"}, have_kids=True,num_kids=0, current_involvement={"op"})
    for ci in ["op","ci_soldno","ci_cons","ci_inv","ci_expl"]:
        add(f"involve-{ci}", screening=set(), what_channels=set(), current_involvement={ci})
    for ch in [set(),{"c_dtc"},{"c_tt"},{"c_ret"},set(CH)]:
        add("chan-"+("+".join(x[2:] for x in ch) or "none"), screening=set(), what_channels=ch, current_involvement={"op"})
    for mf in [set(),{"m_cn"},set(COUNTRIES)]:
        add("mfg-"+("+".join(x[2:] for x in mf) or "none"), screening={"o_ops"}, mfg_locations=mf, what_channels=set(), current_involvement={"op"})
    for cn,pn,sn in [(set(),set(),set()),({"chap_no"},{"prog_no"},{"squad_no"})]:
        add("prog-"+("no" if cn else "yes"), screening=set(), what_channels=set(), current_involvement={"op"},
            chapter_attend=cn,programs_part=pn,squad_attend=sn)
    json.dump(cases, open("/tmp/census_cover.json","w"), indent=1)
    print(f"covering set: {len(cases)} cases -> /tmp/census_cover.json")
    for c in cases: print(f"  {c['name']:16} {len(c['expected_path'])} questions")

def coverui():
    """Emit UI-drivable covering cases (choice LABELS + expected present/absent question TITLES)
    for the Playwright suite -> census-qa/covering-cases.json."""
    d=load_form(); linear,idx,grpof,logic,resolve,exits=build(d)
    S=lambda a: simulate(a,linear,logic,resolve,exits)[0]
    title={}; lab={}
    for f in d["fields"]:
        grp=[f]+(f["properties"]["fields"] if f.get("type") in ("group","matrix") else [])
        for ff in grp:
            title[ff["ref"]]=ff.get("title","")
            for c in ff.get("properties",{}).get("choices",[]) or []:
                if c.get("ref"): lab[c["ref"]]=c["label"]
    OP="I actively own & operate an ecommerce business"
    MARK=["official_role","business_models","ops_warehousing","have_kids","num_kids",
          "orders_shipped","cogs_pct","pct_dtc","pct_tiktok","pct_retail","mfg_cn","chapter_rating"]
    def case(name,a):
        a.setdefault("activities",set()); scr=a.get("screening",set()); p=S(a)
        fam=("o_fam" in scr) or ("o_unsure" in scr); inv=list(a.get("current_involvement",{"op"}))[0]
        return {"name":name,
          "inputs":{
            "screening":[lab[r] for r in scr if r in lab],
            "have_kids":("Yes" if a.get("have_kids") else "No") if fam else None,
            "num_kids":a.get("num_kids") if (fam and a.get("have_kids")) else None,
            "manufacturing":[lab[r] for r in a.get("mfg_locations",set()) if r in lab],
            "channels":[lab[r] for r in a.get("what_channels",set()) if r in lab],
            "current_involvement":OP if inv=="op" else lab.get(inv,inv),
            "chapter":"No" if "chap_no" in a.get("chapter_attend",set()) else "Yes",
            "programs":"No" if "prog_no" in a.get("programs_part",set()) else "Yes",
            "squad":"No" if "squad_no" in a.get("squad_attend",set()) else "Yes"},
          "expect_present":[title[m] for m in MARK if m in p and title.get(m)],
          "expect_absent":[title[m] for m in MARK if m not in p and title.get(m)],
          "must_reach_submit":True,"expected_question_count":len(p)}
    C=[]; add=lambda n,**a: C.append(case(n,a))
    add("none",screening={"o_none"},what_channels=set(),current_involvement={"op"})
    add("unsure-all",screening={"o_unsure"},have_kids=True,num_kids=2,mfg_locations={"m_cn","m_mx"},what_channels=set(CH),current_involvement={"op"})
    for s in SEC: add(f"only-{s[2:]}",screening={s},have_kids=True,num_kids=2,mfg_locations={"m_cn"},what_channels=set(),current_involvement={"op"})
    add("fam-nokids",screening={"o_fam"},have_kids=False,current_involvement={"op"})
    add("fam-0kids",screening={"o_fam"},have_kids=True,num_kids=0,current_involvement={"op"})
    for ci in ["op","ci_soldno","ci_cons","ci_inv","ci_expl"]: add(f"involve-{ci}",screening=set(),what_channels=set(),current_involvement={ci})
    for ch in [set(),{"c_dtc"},{"c_tt"},{"c_ret"},set(CH)]: add("chan-"+("+".join(x[2:] for x in ch) or "none"),screening=set(),what_channels=ch,current_involvement={"op"})
    for mf in [set(),{"m_cn"},set(COUNTRIES)]: add("mfg-"+("+".join(x[2:] for x in mf) or "none"),screening={"o_ops"},mfg_locations=mf,what_channels=set(),current_involvement={"op"})
    for tag,pr in [("yes",(set(),set(),set())),("no",({"chap_no"},{"prog_no"},{"squad_no"}))]:
        add("prog-"+tag,screening=set(),what_channels=set(),current_involvement={"op"},chapter_attend=pr[0],programs_part=pr[1],squad_attend=pr[2])
    out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","census-qa","covering-cases.json")
    os.makedirs(os.path.dirname(out),exist_ok=True)
    json.dump({"form_id":FORM_ID,"url":f"https://form.typeform.com/to/{FORM_ID}","cases":C},open(out,"w"),indent=1)
    print(f"wrote {len(C)} UI cases -> {out}")

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "sweep"
    if   cmd=="sweep":   sys.exit(sweep())
    elif cmd=="cover":   sys.exit(cover() or 0)
    elif cmd=="coverui": sys.exit(coverui() or 0)
    else: print("usage: census_qa_sim.py sweep|cover|coverui"); sys.exit(2)
