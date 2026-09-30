import json,subprocess,re,datetime as dt,sys
def g(*a): return subprocess.run(["git",*a],capture_output=True,text=True,encoding="utf-8").stdout.strip()
now=dt.datetime.now(dt.timezone.utc)
Q=json.loads(g("show","origin/main:ops/fleet/QUEUE.json"))
who=open(sys.argv[1],encoding='utf-8').read().splitlines()
comms={}
for l in who:
    m=re.match(r"^(\w+)\s+(yes|no)\s+(\d+)/(\d+)\s+(\w+)\s+\w+\s+\S+.*?(\d{4}-\d\d-\d\d \d\d:\d\d)\s+(\w+)",l)
    if m: comms[m[1]]=dict(online=m[2],status=m[5],last_sync_local=m[6],sync_sha=m[7])
def parse(t):
    try: return dt.datetime.fromisoformat(t.replace('Z','+00:00')) if t else None
    except: return None
seats=sorted(set(p.split('/')[1] for p in g("ls-tree","-r","--name-only","origin/main","roles/").split() if p.endswith('/WORK_STATE.json') and p.count('/')==2))
rows=[]
for s in sorted(set(seats)|set(Q['seats'])|{k for k in comms if comms[k]['online']=='yes'}):
    ws={}
    if s in seats: ws=json.loads(g("show",f"origin/main:roles/{s}/WORK_STATE.json"))
    f=[]
    u=parse(ws.get('updated_at_utc'))
    ci=g("log","-1","--format=%H %cI","origin/main","--",f"roles/{s}/WORK_STATE.json")
    ctime=parse(ci.split()[1]) if ci else None
    if u and u>now: f.append(f"FUTURE_UPDATE updated_at {ws['updated_at_utc']} > now")
    if u and ctime and u>ctime+dt.timedelta(minutes=10): f.append(f"UPDATED_AFTER_COMMIT claims {ws['updated_at_utc']}, committed {ctime:%Y-%m-%dT%H:%MZ}" if ctime.utcoffset() else "")
    if u and ctime and ctime-u>dt.timedelta(hours=2): f.append(f"COMMIT_LATER_THAN_CLAIM committed {ctime.astimezone(dt.timezone.utc):%m-%dT%H:%MZ} vs updated_at {ws['updated_at_utc']}")
    hs=ws.get('head_sha','')
    if hs and re.fullmatch(r"[0-9a-f]{7,40}",hs):
        if not g("cat-file","-t",hs): f.append(f"HEAD_SHA_UNKNOWN {hs[:9]}")
        elif subprocess.run(["git","merge-base","--is-ancestor",hs,"origin/main"]).returncode: f.append(f"HEAD_SHA_NOT_ON_MAIN {hs[:9]}")
    br=ws.get('branch')
    if br and not g("ls-remote","origin","refs/heads/"+br): f.append(f"BRANCH_NOT_ON_ORIGIN {br}")
    qs=Q['seats'].get(s)
    if s in seats and not qs: f.append("HAS_WORK_STATE_NOT_IN_QUEUE")
    if qs and s not in seats: f.append("IN_QUEUE_NO_WORK_STATE")
    c=comms.get(s)
    if c:
        ls=dt.datetime.strptime(c['last_sync_local'],"%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)+dt.timedelta(hours=4)
        age=(now-ls).total_seconds()/3600
        if ws.get('state') in('ACTIVE','WORKING') and age>6: f.append(f"STATE_{ws['state']}_BUT_COMMS_SYNC_{age:.0f}h_AGO online={c['online']}")
        if u and ls+dt.timedelta(hours=1)<u and c['online']=='no': f.append(f"WS_NEWER_THAN_LAST_COMMS_SYNC by {(u-ls).total_seconds()/3600:.0f}h")
        if ws.get('state')=='HOLD' and c['status']=='active': f.append("WS_HOLD_COMMS_STATUS_active")
    elif s in seats or qs: f.append("NO_COMMS_ROW")
    if qs and ws and qs.get('current') and ws.get('current') and qs['current'][:40].lower()!=str(ws['current'])[:40].lower(): f.append("QUEUE_CURRENT!=WS_CURRENT")
    rows.append((s,ws.get('state'),ws.get('updated_at_utc'),c and c['online'],c and c['last_sync_local'],[x for x in f if x]))
    if qs and ws.get('current'): rows[-1]+=(("Q: "+str(qs.get('current'))[:110]),("W: "+str(ws.get('current'))[:110]))
for r in rows:
    print(r[0],r[1],r[2],"comms_online",r[3],"last_sync_local",r[4])
    for x in r[5]: print("   -",x)
    for x in r[6:]: print("     ",x)
