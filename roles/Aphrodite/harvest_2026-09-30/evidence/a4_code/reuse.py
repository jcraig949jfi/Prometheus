import os,re,subprocess,collections,json
R='C:/Prometheus-worktrees/aphrodite-harvest/'
D='C:/Users/jcrai/AppData/Local/Temp/claude/C--Prometheus/0f14ab93-b7f3-49de-b318-37ede7c700a4/scratchpad/data/a4/'
files=subprocess.run(['git','-C',R,'ls-files','*.py','*.ps1','*.sh','*.md','*.json','*.toml','*.yaml'],capture_output=True,text=True).stdout.split('\n')
files=[f for f in files if f]
# add dates
add={}
cur=None
for l in open(D+'py_adds.txt',encoding='utf-8'):
    l=l.rstrip('\n')
    if l.startswith('@@'): cur=l[2:]; continue
    if l: add[l]=cur  # oldest wins (log newest first)
seats=sorted(os.listdir(R+'roles'))
seatlow={s.lower():s for s in seats}
TOP={d for d in os.listdir(R) if os.path.isdir(R+d) and not d.startswith('.')}
SHARED={'comms','fabric','evidence_wiki','ops','sigma_kernel','prometheus_math','agora','scripts','prometheus','engine','prometheus_llm','prometheus_data','infra','pipelines','integration','watchers','stations','genesis','falsification','zoo','forge','primordial','cartography','agents','tests','charon','ergon'}
def owner(f):
    p=f.split('/')
    if p[0]=='roles' and len(p)>2: return p[1]
    if p[0].lower() in seatlow and p[0] not in ('agora',): return seatlow[p[0].lower()]
    if p[0] in SHARED: return 'shared:'+p[0]
    return 'other:'+p[0]
def target_of_module(mod):
    top=mod.split('.')[0]
    if top not in TOP: return None
    if top=='ops' and len(mod.split('.'))>1: return 'shared:ops.'+mod.split('.')[1]
    if top.lower() in seatlow and top!='agora': return seatlow[top.lower()]
    return 'shared:'+top
IMP=re.compile(r'^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))',re.M)
PATHREF=re.compile(r'roles/([A-Z][A-Za-z0-9\-]+)/([\w\-/\.]+\.py)')
TOPREF=re.compile(r'(?:python(?:3)?\s+-m\s+)([a-z_]+)|(?<![\w/])(fabric|comms|evidence_wiki|ops/tools|sigma_kernel|prometheus_math)/[\w/\.]*\.py')
edges=collections.defaultdict(lambda:{'n':0,'first':None,'files':set(),'kind':set()})
for f in files:
    if not (f.endswith('.py') or f.endswith('.ps1') or f.endswith('.sh')): continue
    o=owner(f)
    if o.startswith('other:') : pass
    try: t=open(R+f,encoding='utf-8',errors='replace').read()
    except Exception: continue
    tg=set()
    if f.endswith('.py'):
        for a,b in IMP.findall(t):
            x=target_of_module(a or b)
            if x: tg.add((x,'import'))
    for s,_ in PATHREF.findall(t): tg.add((s,'path'))
    for a,b in TOPREF.findall(t):
        x=a or b
        if x:
            x=x.replace('/','.')
            if x.startswith('ops.'): x='ops.tools'
            tg.add(('shared:'+x if not x.lower() in seatlow else seatlow[x.lower()],'cli/path'))
    for x,k in tg:
        if x==o: continue
        if x.startswith('shared:') and o=='shared:'+x.split(':')[1].split('.')[0]: continue
        e=edges[(o,x)]; e['n']+=1; e['files'].add(f); e['kind'].add(k)
        d=add.get(f)
        if d and (e['first'] is None or d<e['first']): e['first']=d
rows=[]
for (o,x),e in edges.items():
    rows.append(dict(user=o,target=x,files=len(e['files']),first=(e['first'] or '?')[:10],kind=sorted(e['kind']),ex=sorted(e['files'])[:3]))
json.dump(rows,open(D+'reuse_edges.json','w'),indent=0)
seat_users=lambda r: not r['user'].startswith(('shared:','other:'))
# 1. shared infra consumers
out=['#### Shared-module consumers (seat-owned code only: roles/<Seat>/ and seat-named top-level dirs)\n','| shared module | consuming seats | files | first use (file add date) | seats |','|---|---|---|---|---|']
by=collections.defaultdict(list)
for r in rows:
    if seat_users(r) and r['target'].startswith('shared:'): by[r['target']].append(r)
for t,L in sorted(by.items(),key=lambda kv:-len(kv[1])):
    out.append(f"| {t[7:]} | {len(L)} | {sum(r['files'] for r in L)} | {min(r['first'] for r in L)} | {', '.join(sorted(r['user'] for r in L))[:200]} |")
out.append('\n#### Seat-to-seat instrument reuse (user seat code imports / path-references another seat\'s code)\n\n| user seat | provider seat | files | first use | mechanism | example file |\n|---|---|---|---|---|---|')
for r in sorted([r for r in rows if seat_users(r) and not r['target'].startswith(('shared:','other:'))],key=lambda r:(-r['files'])):
    out.append(f"| {r['user']} | {r['target']} | {r['files']} | {r['first']} | {'/'.join(r['kind'])} | {r['ex'][0][:80]} |")
open(D+'reuse_out.md','w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))
