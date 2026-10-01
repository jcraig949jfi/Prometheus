import os,re,glob,hashlib,collections,json
R='C:/Prometheus-worktrees/aphrodite-harvest/'
D='C:/Users/jcrai/AppData/Local/Temp/claude/C--Prometheus/0f14ab93-b7f3-49de-b318-37ede7c700a4/scratchpad/data/'
# first-add commit time per dir
first={}
cur=None
for l in open(D+'prompt_adds.txt',encoding='utf-8'):
    l=l.strip()
    if l.startswith('@@'): cur=l[2:].split('|',2); continue
    if not l: continue
    p=l.split('/')
    if len(p)>=4: first[(p[1],p[3])]=cur[1]
rows=[]
for d in sorted(glob.glob(R+'roles/*/prompts/2026-09-*')):
    if not os.path.isdir(d): continue
    seat=d.split('/')[-3] if '/' in d else None
    seat=os.path.normpath(d).split(os.sep)[-3]; name=os.path.basename(d)
    if name[:10]<'2026-09-11': continue
    files=[f for f in os.listdir(d) if os.path.isfile(os.path.join(d,f))]
    opfiles=[f for f in files if re.search('OPERATOR',f,re.I)]
    op_reason=None
    if opfiles: op_reason='filename'
    elif 'operator' in name.lower(): op_reason='dirname'
    else:
        for f in files:
            if f.startswith('MANIFEST'): continue
            if re.search(r'verbatim|DIRECTIVE|CHARTER|CREATION|RULING|PROMPT',f,re.I):
                t=open(os.path.join(d,f),encoding='utf-8',errors='replace').read(3000)
                if re.search(r'\boperator\b|\bJames\b',t,re.I): op_reason='text'; opfiles=[f]; break
    if not op_reason:
        rows.append(dict(seat=seat,dir=name,op=False)); continue
    src=opfiles[0] if opfiles else [f for f in files if not f.startswith('MANIFEST')][0]
    t=open(os.path.join(d,src),encoding='utf-8',errors='replace').read()
    h=hashlib.sha256(re.sub(r'\s+',' ',t).strip().encode()).hexdigest()[:10]
    rows.append(dict(seat=seat,dir=name,op=True,reason=op_reason,file=src,hash=h,chars=len(t),text=t[:4000],when=first.get((seat,name),name[:10])))
json.dump(rows,open(D+'a4/prompt_rows.json','w'),indent=0)
ops=[r for r in rows if r['op']]
print(len(rows),len(ops),collections.Counter(r['reason'] for r in ops))
for r in ops: print(r['when'][:16],r['seat'],r['dir'][11:],r['file'][:40],r['hash'],r['chars'])
