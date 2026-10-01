import os,re,subprocess,collections,json,hashlib,difflib
R='C:/Prometheus-worktrees/aphrodite-harvest/'
D='C:/Users/jcrai/AppData/Local/Temp/claude/C--Prometheus/0f14ab93-b7f3-49de-b318-37ede7c700a4/scratchpad/data/a4/'
files=[f for f in subprocess.run(['git','-C',R,'ls-files','*.py'],capture_output=True,text=True).stdout.split('\n') if f]
seats=sorted(os.listdir(R+'roles')); seatlow={s.lower():s for s in seats}
add={};cur=None
for l in open(D+'py_adds.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if l.startswith('@@'): cur=l[2:]; continue
    if l: add[l]=cur
def owner(f):
    p=f.split('/')
    if p[0]=='roles' and len(p)>2: return p[1]
    if p[0].lower() in seatlow: return seatlow[p[0].lower()]
    if p[0] in ('comms','fabric','evidence_wiki','ops','sigma_kernel','prometheus_math','prometheus','engine','scripts'): return 'shared:'+p[0]
    return None
def norm(t): return re.sub(r'#.*','',re.sub(r'\s+',' ',t))
out=[]
# --- capability families
CAP={
 'lease ledger / acquire-release':r'def\s+(acquire|release|renew|take|hold)_?lease|def\s+lease_(acquire|release|status|held)|class\s+\w*Lease\b',
 'heartbeat writer':r'def\s+\w*heartbeat\w*\s*\(',
 'prereg / freeze manifest (sha256 over files)':r'def\s+\w*(freeze|prereg|manifest)\w*\s*\(',
 'workspace / checkout guard':r'def\s+\w*(workspace_guard|assert_not_canonical|guard_workspace|check_worktree|refuse_canonical)\w*\s*\(|workspace_guard',
 'novelty ruler / scorer':r'def\s+\w*novelty\w*\s*\(|class\s+\w*Novelty\w*',
 'comms posting helper (own client)':r'def\s+\w*(post_comms|send_comms|comms_post|post_message|send_message)\w*\s*\(',
 'sha256 file hasher':r'def\s+(sha256_file|file_sha256|sha256_of|hash_file|_sha256|sha256)\s*\(',
 'seal / commit-reveal':r'def\s+\w*(seal|unseal|commit_reveal)\w*\s*\(',
 'process/host census (psutil)':r'psutil\.process_iter',
}
hits=collections.defaultdict(lambda:collections.defaultdict(list))
for f in files:
    o=owner(f)
    if not o: continue
    try: t=open(R+f,encoding='utf-8',errors='replace').read()
    except: continue
    for k,p in CAP.items():
        if re.search(p,t): hits[k][o].append(f)
out.append('| capability | owners implementing it (files) | n owners | n files | earliest add | imports a shared impl? |\n|---|---|---|---|---|---|')
SHAREDIMPL={'lease ledger / acquire-release':r'from fabric|import fabric|lease_compat','heartbeat writer':r'from comms|import comms','comms posting helper (own client)':r'from comms|import comms','prereg / freeze manifest (sha256 over files)':r'comms\.manifest|from comms import manifest|comms/manifest'}
capsum={}
for k,d in hits.items():
    allf=[f for L in d.values() for f in L]
    sh=0
    if k in SHAREDIMPL:
        for f in allf:
            if re.search(SHAREDIMPL[k],open(R+f,encoding='utf-8',errors='replace').read()): sh+=1
    seatowners=[o for o in d if not o.startswith('shared:')]
    out.append(f"| {k} | {', '.join(f'{o}({len(L)})' for o,L in sorted(d.items(),key=lambda kv:-len(kv[1])))[:300]} | {len(d)} ({len(seatowners)} seats) | {len(allf)} | {min((add.get(f) or '9')[:10] for f in allf)} | {str(sh)+'/'+str(len(allf)) if k in SHAREDIMPL else 'n/a'} |")
    capsum[k]={o:L for o,L in d.items()}
json.dump(capsum,open(D+'cap_hits.json','w'),indent=0)
# --- same basename across owners
bn=collections.defaultdict(list)
for f in files:
    o=owner(f)
    if not o or o.startswith('shared:'): continue
    b=os.path.basename(f)
    if b in ('__init__.py','__main__.py','conftest.py','run.py','main.py','analyze.py','analysis.py','common.py','utils.py','config.py','setup.py','cli.py','test.py','run_all.py','report.py'): continue
    bn[b].append((o,f))
rows=[]
for b,L in bn.items():
    owners={o for o,_ in L}
    if len(owners)<2: continue
    txt={f:open(R+f,encoding='utf-8',errors='replace').read() for _,f in L}
    hs=collections.Counter(hashlib.sha1(norm(t).encode()).hexdigest() for t in txt.values())
    # pairwise max similarity across different owners (cap work)
    best=0; pair=None
    LL=L[:8]
    for i in range(len(LL)):
        for j in range(i+1,len(LL)):
            if LL[i][0]==LL[j][0]: continue
            a,bb=txt[LL[i][1]],txt[LL[j][1]]
            if max(len(a),len(bb))>60000: continue
            r=difflib.SequenceMatcher(None,a[:20000],bb[:20000],autojunk=False).quick_ratio()
            if r>best: best=r; pair=(LL[i][1],LL[j][1])
    rows.append((b,sorted(owners),len(L),max(hs.values()),best,pair,min((add.get(f) or '9')[:10] for _,f in L)))
rows.sort(key=lambda r:(-len(r[1]),-r[4]))
out.append('\n| basename | owners | files | max identical copies | best cross-owner similarity (quick_ratio) | earliest add |\n|---|---|---|---|---|---|')
for b,ow,n,ident,best,pair,first in rows[:45]:
    out.append(f"| {b} | {', '.join(ow)[:120]} | {n} | {ident} | {best:.2f} | {first} |")
open(D+'dups_out.md','w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))
json.dump([(r[0],r[1],r[2],r[3],r[4],r[5]) for r in rows],open(D+'dups_rows.json','w'))
