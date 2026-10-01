import json,re,collections
D='C:/Users/jcrai/AppData/Local/Temp/claude/C--Prometheus/0f14ab93-b7f3-49de-b318-37ede7c700a4/scratchpad/data/'
rows=[r for r in json.load(open(D+'a4/prompt_rows.json')) if r['op']]
EXCL=re.compile(r'^(ACK|REPLY|PROMPT_TO|PROMPT_D_TO|PROMPT_FOREIGN|HANDOVER|01_RULINGS_R|02_ARCHAEON|PROMPT_ARCHAEON|PROMPT_THEO|01_STEWARD|00_PROMPTS_VERBATIM|SEASON1_PROMPT)')
for r in rows: r['strict']= r['reason']!='text' or not EXCL.search(r['file'])
for r in rows:
    if r['reason']=='text' and EXCL.search(r['file']): r['strict']=False
# dir-name rules first (most reliable), then text
NAME=[('infrastructure/process',r'creation|adoption|reactivation$|reseating|seating|bootstrap|cwo|base_role|comms|m1_reboot|gitignore|operator_rulings$|reboot_resume|ops_pilot|direct_operator_control|fabric|distributed_brain|steward_freeze|pairing|heartbeat'),
      ('correct an error',r'challenge|correction|repair_order|freeze$|erratum|journal'),
      ('approve a gate',r'approval|authorization|clearance|signoff|release|promotion|publication|disposition|ruling|gate|go_final|review|e002_handoff|amend'),
      ('unblock',r'unblock|time_?box|resolution'),
      ('redirect science',r'charter|campaign|direction|directive|program|portfolio|frontier|research|harvest|survey|raid|batch|block|atlas|library|benchmark|essay|assay|pressure_map|expeditionary|ecology|selective|swarm|sequence|execution|kernel|pilot|tdd|forensics|th006|thread|dials|engine|refinery|poet|topology|foundry|point_release|attribution|portability|contract|environmental|envgate|lm01|arc3|wse|rsi|feedback|state|v1_|v2_|round2|amendment2|archaeology|cut|alien|gating|deep|z80|lane|court|season|next|addendum|rulings|lawful|steering|selftest|retrospective|inference|cycle')]
def cls(r):
    n=r['dir'][11:].lower().lstrip('_')
    for lab,p in NAME:
        if re.search(p,n): return lab
    return 'other'
OV={('Herakles','2026-09-11_replies'):'DROP',('Aporia','2026-09-25_ananke_pte_si01'):'redirect science',('Aether','2026-09-26_resume_science'):'unblock',('Aphrodite','2026-09-21_c1_patch1'):'approve a gate',('Cosmos','2026-09-24_c3_external_seats'):'redirect science',('Ensorain','2026-09-26_lm01_operator_rulings'):'approve a gate',('Harmonia','2026-09-18_operator_rulings'):'redirect science',('Nestor','2026-09-25_reboot_resume'):'unblock'}
for r in rows:
    r['cls']=OV.get((r['seat'],r['dir']),cls(r)); r['day']=r['when'][5:10]
    if r['cls']=='DROP': r['strict']=False
    t=r['text'].lower()
    r['f_correct']=bool(re.search(r"\b(wrong|mistake|incorrect|misread|overclaim|not what i|you did not|you didn't|that is not|stop (doing|running|launching)|do not repeat|violat\w*|error)\b",t))
    r['f_unblock']=bool(re.search(r"\b(unblock\w*|blocked|go ahead|you may (now )?proceed|proceed|released?|lift(ed)? the hold)\b",t))
    r['f_gate']=bool(re.search(r"\b(approv\w*|authoriz\w*|go|sign-?off|accepted)\b",t))
    r['f_infra']=bool(re.search(r"\b(lease|heartbeat|machine|m1|m2|m4|fabric|comms|cpu|gpu|workers?|install)\b",t))
S=[r for r in rows if r['strict']]
print('strict',len(S),'loose',len(rows))
uh={}
for r in S: uh.setdefault(r['hash'],r)
print('unique texts strict',len(uh))
C=collections.Counter(r['cls'] for r in S); print(C)
for r in S:
    if r['cls']=='other': print('OTHER',r['seat'],r['dir'])
json.dump(rows,open(D+'a4/prompt_rows_cls.json','w'),indent=0)
# tables
days=sorted({r['day'] for r in S})
labs=['redirect science','approve a gate','infrastructure/process','correct an error','unblock','other']
out=['| day (local, commit) | operator prompts filed | unique texts | seats touched | '+' | '.join(labs)+' |','|'+'---|'*(len(labs)+4)]
for d in days:
    xs=[r for r in S if r['day']==d]; c=collections.Counter(r['cls'] for r in xs)
    out.append(f"| {d} | {len(xs)} | {len({r['hash'] for r in xs})} | {len({r['seat'] for r in xs})} | "+' | '.join(str(c[l]) for l in labs)+' |')
c=collections.Counter(r['cls'] for r in S)
out.append(f"| ALL | {len(S)} | {len(uh)} | {len({r['seat'] for r in S})} | "+' | '.join(str(c[l]) for l in labs)+' |')
out.append('\n| seat | operator prompts | '+' | '.join(labs)+' | total verbatim chars |\n|'+'---|'*(len(labs)+3))
for s,n in collections.Counter(r['seat'] for r in S).most_common():
    xs=[r for r in S if r['seat']==s]; c=collections.Counter(r['cls'] for r in xs)
    out.append(f"| {s} | {n} | "+' | '.join(str(c[l]) for l in labs)+f" | {sum(r['chars'] for r in xs):,} |")
out.append('\nMulti-label text flags (strict set, verbatim text first 4,000 chars): '+', '.join(f"{k}={sum(1 for r in S if r[k])}" for k in ('f_correct','f_unblock','f_gate','f_infra')))
open(D+'a4/prompts_out.md','w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))
