"""Hephaestus ledger shape. Apparatus control first (LAW N14), then:
  - per-period yield with instrument-state rows separated from genuine battery failures
  - battery-version recovery per row from the accuracy/calibration fractions (denominator inference)
  - scrap-reason class histogram per recovered battery version
  - forged-tool accuracy/calibration distributions vs chance floor
"""
import sys, types, json, os, re, collections
from fractions import Fraction
m=types.ModuleType("openai"); m.OpenAI=object; sys.modules["openai"]=m
sys.path.insert(0,'agents/hephaestus/src')
import hephaestus as H
OUT={}
led_rows=[json.loads(l) for l in open('agents/hephaestus/ledger.jsonl',encoding='utf-8') if l.strip()]
led=H.load_ledger()
OUT['apparatus']={'ledger_lines':len(led_rows),'unique_keys':len(led),'fields':sorted(set(k for r in led_rows for k in r))}
def rclass(r):
    s=str(r.get('reason',''))
    if r.get('status')=='forged': return 'FORGED'
    if s.startswith('api_call_failed'): return 'INSTR:api_call_failed'
    if s.startswith('wall_clock_timeout'): return 'INSTR:wall_clock_timeout'
    if s.startswith('test_harness_error'): return 'INSTR:test_harness_error'
    if s.startswith('trap_battery_failed'): return 'BATTERY:trap_battery_failed'
    if s.startswith('adversarial'): return 'BATTERY:adversarial_failed'
    if s.startswith('validation:'): return 'GEN:'+s.split(':')[1].split(' ')[0]
    if s.startswith('scrap:'): return 'GEN:'+s[6:].split(' ')[0]
    if 'no_code' in s or 'code_extract' in s: return 'GEN:no_code_found'
    if 'novelty' in s.lower(): return 'GATE:novelty'
    return 'OTHER:'+s[:30]
# denominator inference: smallest n<=200 s.t. acc*n, cal*n both ~integer
def infer_n(r):
    vals=[r.get('accuracy',0),r.get('calibration',0)]
    if all(v in (0,0.0) for v in vals): return None
    for n in (15,116,58,30,29,20,10,25,50,100,40,60,80,120,150,200):
        if all(abs(v*n-round(v*n))<1e-6 for v in vals): return n
    for n in range(2,201):
        if all(abs(v*n-round(v*n))<1e-6 for v in vals): return n
    return 'unresolved'
per=collections.defaultdict(collections.Counter); nper=collections.defaultdict(collections.Counter)
by_day=collections.defaultdict(collections.Counter)
for r in led_rows:
    d=str(r.get('timestamp',''))[:10]; c=rclass(r); by_day[d][c]+=1
    # battery-version windows by commit time (local -0400 timestamps)
    t=str(r.get('timestamp',''))
    if t<'2026-03-25T10:46': w='W0_pre_v2(<03-25 10:46)'
    elif t<'2026-03-27T06:49': w='W1_15trap(03-25..03-27 06:49)'
    elif t<'2026-05-17T06:52': w='W2_58cat(03-27..05-17)'
    elif t<'2026-05-18T07:58': w='W3_revival(05-17..05-18)'
    elif t<'2026-05-26T11:44': w='W4_tier_strat(05-18..05-26)'
    else: w='W5_behav_ncd(>=05-26 11:44)'
    per[w][c]+=1; n=infer_n(r)
    if n is not None: nper[w][str(n)]+=1
OUT['reason_class_by_window']={w:dict(c.most_common()) for w,c in sorted(per.items())}
OUT['inferred_n_traps_by_window']={w:dict(c.most_common(6)) for w,c in sorted(nper.items())}
# yield tables
tab={}
for w,c in sorted(per.items()):
    tot=sum(c.values()); forged=c['FORGED']; instr=sum(v for k,v in c.items() if k.startswith('INSTR'))
    gen=sum(v for k,v in c.items() if k.startswith('GEN')); bat=sum(v for k,v in c.items() if k.startswith('BATTERY'))
    tab[w]={'rows':tot,'forged':forged,'instrument':instr,'generation_defect':gen,'battery_fail':bat,
            'yield_raw':round(forged/tot,4) if tot else None,
            'yield_excl_instrument':round(forged/(tot-instr),4) if tot-instr else None,
            'yield_among_battery_tested':round(forged/(forged+bat),4) if forged+bat else None}
OUT['yield_by_window']=tab
OUT['by_day']={d:dict(c) for d,c in sorted(by_day.items())}
# forged acc/cal distributions per window
dist=collections.defaultdict(list)
for r in led_rows:
    if r.get('status')=='forged':
        t=str(r.get('timestamp','')); w='pre0327' if t<'2026-03-27T06:49' else ('mar_post' if t<'2026-05' else 'may')
        dist[w].append((r.get('accuracy',0),r.get('calibration',0),r.get('margin_accuracy',0),r.get('margin_calibration',0)))
import statistics as st
OUT['forged_metrics']={w:{'n':len(v),'acc_mean':round(st.mean(x[0] for x in v),3),'acc_min':min(x[0] for x in v),'acc_max':max(x[0] for x in v),
   'cal_mean':round(st.mean(x[1] for x in v),3),'margin_acc_mean':round(st.mean(x[2] for x in v),3),'margin_cal_mean':round(st.mean(x[3] for x in v),3),
   'acc_hist':dict(collections.Counter(round(x[0],2) for x in v).most_common(8))} for w,v in dist.items()}
# duplicate-key overwrite: keys appearing more than once (ledger dict keeps LAST)
cnt=collections.Counter(r['key'] for r in led_rows); dup=[k for k,c in cnt.items() if c>1]
OUT['duplicate_keys']={'n_keys_with_multiple_rows':len(dup),'example':dup[:3]}
# did any api_call_failed key ever get retried later in ledger?
first=collections.defaultdict(list)
for r in led_rows: first[r['key']].append(rclass(r))
retried=sum(1 for k,v in first.items() if v[0]=='INSTR:api_call_failed' and len(v)>1)
OUT['api_failed_keys_ever_retried']={'api_failed_first_keys':sum(1 for v in first.values() if v[0]=='INSTR:api_call_failed'),'retried_later':retried}
# frame/model coverage
OUT['frame_hist']=dict(collections.Counter(r.get('frame','<absent>') for r in led_rows).most_common())
OUT['model_hist']=dict(collections.Counter(r.get('model','<absent>') for r in led_rows).most_common(8))
json.dump(OUT,open(os.path.join(os.environ.get('SP',os.path.dirname(os.path.abspath(__file__))),'heph_ledger_shape_result.json'),'w'),indent=1)
for k in ['apparatus','yield_by_window','reason_class_by_window','inferred_n_traps_by_window','forged_metrics','duplicate_keys','api_failed_keys_ever_retried','frame_hist','model_hist']:
    print('##',k); print(json.dumps(OUT[k],indent=1))
