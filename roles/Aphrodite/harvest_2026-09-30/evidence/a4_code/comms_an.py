import json,re,collections,datetime as dt,statistics as st
D='C:/Users/jcrai/AppData/Local/Temp/claude/C--Prometheus/0f14ab93-b7f3-49de-b318-37ede7c700a4/scratchpad/data/'
m=json.load(open(D+'comms_messages.json',encoding='utf-8'))
M={x['id']:x for x in m}
def T(x): return dt.datetime.fromisoformat(x['created_at'])
def day(x): return T(x).astimezone(dt.timezone.utc).strftime('%m-%d')
def seat(s): return s.split('[')[0].strip()
def txt(x): return x['subject']+'\n'+x['body']
INFRA=re.compile(r'lease|fabric|comms\b|machine|\bM[124]\b|cpu|gpu|broker|promexec|CLI\b|worktree|gitignore|crlf|disk|memory leak|scheduler|watchdog|install|venv|ollama|quota|evidence_wiki|db hang|postgres',re.I)
SCI=re.compile(r'PASS|FAIL|verdict|prereg|freeze|frozen|holdout|null|control|effect|result|hypothes|experiment|campaign|specimen|fossil|seal|audit|ruler|novelty|bootstrap|replicat|ablation|\barm\b|estimator|adjudicat',re.I)
def cat(x):
    k=x['kind']; s=x['subject']; b=x['body'][:600]
    if k=='ack': return 'coord:ack'
    if k=='broadcast': return 'coord:broadcast'
    if re.search(r'heartbeat|VISIBILITY_STALE|census',s,re.I): return 'coord:heartbeat/census'
    if re.search(r'adopt|base-role|\bboot\b|reactivat|seat creation|next work|roll ?call|WORK_STATE',s,re.I): return 'coord:adoption/state'
    if k=='question': return 'question'
    if k=='ruling': return 'ruling'
    if k in('prompt','delegation'): return 'tasking'
    sc=len(SCI.findall(s+' '+b)); inf=len(INFRA.findall(s+' '+b))
    if sc>=inf and sc>0: return 'report:science'
    if inf>0: return 'report:infra'
    return 'report:other'
for x in m: x['cat']=cat(x); x['seat']=seat(x['sender']); x['day']=day(x)
days=sorted({x['day'] for x in m})
cats=['coord:ack','coord:broadcast','coord:heartbeat/census','coord:adoption/state','tasking','question','ruling','report:science','report:infra','report:other']
out=[]
out.append('### A. Message taxonomy by UTC day\n\n| day | n | seats | '+' | '.join(c.replace('coord:','c:').replace('report:','r:') for c in cats)+' | coord share | science share |')
out.append('|'+'---|'*(len(cats)+5))
tot=collections.Counter()
for d in days:
    xs=[x for x in m if x['day']==d]; c=collections.Counter(x['cat'] for x in xs); tot.update(c)
    co=sum(v for k,v in c.items() if k.startswith('coord')); sc=c['report:science']
    out.append(f"| {d} | {len(xs)} | {len({x['seat'] for x in xs})} | "+' | '.join(str(c[k]) for k in cats)+f" | {co/len(xs):.0%} | {sc/len(xs):.0%} |")
co=sum(v for k,v in tot.items() if k.startswith('coord'))
out.append(f"| ALL | {len(m)} | {len({x['seat'] for x in m})} | "+' | '.join(str(tot[k]) for k in cats)+f" | {co/len(m):.0%} | {tot['report:science']/len(m):.0%} |")
hb=sum(1 for x in m if re.search(r'heartbeat',txt(x),re.I))
out.append(f"\nLoose count: {hb}/{len(m)} messages mention 'heartbeat' anywhere in subject/body.")
# ---- B operator-relay messages
OPR=re.compile(r'operator (ruling|directive|decision|instruction|approv\w*|confirm\w*|charter|challenge|time ?box|says|said|asked|wants|note|prompt|release)|\(operator 2026|OPERATOR[_ ](RULING|DIRECTIVE|PROMPT|CHARTER|CREATION|CHALLENGE|TIME BOX)|per (the )?operator|operator-approved|operator verbatim|verbatim operator|\bMWO-\d{4}\b|\bCWO-2026',re.I)
opr=[x for x in m if OPR.search(txt(x))]
out.append(f"\n### B. Messages relaying/citing operator-originated authority\n\n{len(opr)}/{len(m)} messages match the operator-authority regex (see Methods).")
out.append('\n| day | all msgs | operator-citing msgs | share | distinct citing seats | msgs addressed to `operator` |\n|---|---|---|---|---|---|')
toop=[x for x in m if 'operator' in [r.lower() for r in x['recipients']]]
for d in days:
    xs=[x for x in opr if x['day']==d]; n=sum(1 for x in m if x['day']==d)
    out.append(f"| {d} | {n} | {len(xs)} | {len(xs)/n:.0%} | {len({x['seat'] for x in xs})} | {sum(1 for x in toop if x['day']==d)} |")
sc=collections.Counter(x['seat'] for x in opr)
out.append('\nTop operator-citing seats: '+', '.join(f'{k} {v}' for k,v in sc.most_common(15)))
out.append(f"\nMessages ADDRESSED to recipient 'operator': {len(toop)}; by sender: "+', '.join(f'{k} {v}' for k,v in collections.Counter(x['seat'] for x in toop).most_common()))
json.dump({'opr':[x['id'] for x in opr]},open(D+'a4/opr_ids.json','w'))
# ---- D waits
rep=collections.defaultdict(list); refs=collections.defaultdict(list)
for x in m:
    if x.get('reply_to') in M: rep[x['reply_to']].append(x)
    for n in set(re.findall(r'#(\d{2,4})\b',x['subject']+' '+x['body'][:800])):
        n=int(n)
        if n in M and n<x['id'] and x['seat']!=M[n]['seat']: refs[n].append(x)
def first_resp(q):
    cands=[y for y in rep[q['id']] if y['seat']!=q['seat']]+refs[q['id']]
    cands=[y for y in cands if T(y)>=T(q)]
    if not cands: return None
    y=min(cands,key=T); return y,(T(y)-T(q)).total_seconds()/3600
BLK=re.compile(r'\bBLOCKED\b|\bblocker\b|waiting on|awaiting (your|operator|a ruling|ruling|decision)|decision needed|OPERATOR DECISION',re.I)
qs=[x for x in m if x['kind']=='question' or BLK.search(x['subject'])]
rows=[(q,first_resp(q)) for q in qs]
ans=[r[1] for q,r in rows if r]
out.append(f"\n### D. Waits: question / blocker messages -> first cross-seat response\n\nPopulation: kind=question ({sum(1 for x in m if x['kind']=='question')}) plus subject-level blocker markers -> {len(qs)} messages. Responded (reply_to or later '#id' reference by another seat): {len(ans)} ({len(ans)/len(qs):.0%}).")
qq=sorted(ans)
out.append(f"Latency hours: median {st.median(qq):.2f}, p75 {qq[int(.75*len(qq))]:.2f}, p90 {qq[int(.9*len(qq))]:.2f}, max {max(qq):.1f}.")
isop=lambda q: 'operator' in [z.lower() for z in q['recipients']] or re.search('operator',q['subject'],re.I)
for lab,R in (('operator-addressed / operator-decision',[z for z in rows if isop(z[0])]),('seat-to-seat',[z for z in rows if not isop(z[0])])):
    a=sorted(r[1] for q,r in R if r)
    if a: out.append(f"- {lab}: n={len(R)}, responded {len(a)}, median {st.median(a):.2f} h, max {max(a):.1f} h, no visible response in window {len(R)-len(a)}")
out.append('\nLongest waits (and unanswered):\n\n| id | day | from | to | subject (trunc) | first response | hours |\n|---|---|---|---|---|---|---|')
for q,r in sorted(rows,key=lambda z:-(z[1][1] if z[1] else 999))[:30]:
    s=q['subject'][:80].replace('|','/')
    if r: out.append(f"| {q['id']} | {q['day']} | {q['seat']} | {','.join(q['recipients'])[:30]} | {s} | #{r[0]['id']} {r[0]['seat']} | {r[1]:.1f} |")
    else: out.append(f"| {q['id']} | {q['day']} | {q['seat']} | {','.join(q['recipients'])[:30]} | {s} | none in window | - |")
# ---- E blocked-on edges
E=collections.Counter(); ex={}
seats={x['seat'] for x in m}
pat=re.compile(r'(?:BLOCKED|waiting|waits|awaiting|pending|depends|dependency wait|HOLD)\s+(?:on|for)\s+(?:an?\s+|the\s+)?([A-Z][A-Za-z\-]+|operator)',re.I)
for x in m:
    for g in pat.findall(txt(x)):
        g2='operator' if g.lower()=='operator' else g
        if (g2 in seats or g2=='operator') and g2!=x['seat']:
            E[(x['seat'],g2)]+=1; ex.setdefault((x['seat'],g2),x['id'])
out.append('\n### E. "X blocked/waiting on Y" edges extracted from text\n\n| waiter | waits on | mentions | first msg |\n|---|---|---|---|')
for (a,b),v in E.most_common(40): out.append(f"| {a} | {b} | {v} | #{ex[(a,b)]} |")
G=collections.defaultdict(set)
for (a,b),v in E.items(): G[a].add(b)
chains=sorted({(a,b,c) for a in G for b in G[a] for c in G.get(b,()) if c not in (a,b)})
out.append('\nLength-3 chains ending at operator: '+'; '.join(' -> '.join(c) for c in chains if c[2]=='operator'))
out.append('\nOther length-3 chains: '+'; '.join(' -> '.join(c) for c in chains if c[2]!='operator'))
# ---- G thread depth
def depth(x):
    d=0;seen=set()
    while x.get('reply_to') in M and x['id'] not in seen:
        seen.add(x['id']); x=M[x['reply_to']]; d+=1
    return d,x['id']
thr=collections.defaultdict(list)
for x in m:
    d,root=depth(x); thr[root].append((d,x))
out.append('\n### G. Deepest reply_to chains\n\n| root | root subject | msgs | max depth | seats | span h |\n|---|---|---|---|---|---|')
for root,L in sorted(thr.items(),key=lambda kv:-max(d for d,_ in kv[1]))[:15]:
    xs=[x for _,x in L]; span=(max(map(T,xs))-min(map(T,xs))).total_seconds()/3600
    out.append(f"| #{root} | {M[root]['subject'][:70].replace('|','/')} | {len(L)} | {max(d for d,_ in L)} | {','.join(sorted({x['seat'] for x in xs}))[:60]} | {span:.1f} |")
dist=collections.Counter(max(d for d,_ in L) for L in thr.values())
out.append('\nThread max-depth distribution (roots incl. singletons): '+', '.join(f'd{k}:{v}' for k,v in sorted(dist.items())))
open(D+'a4/comms_out.md','w',encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
