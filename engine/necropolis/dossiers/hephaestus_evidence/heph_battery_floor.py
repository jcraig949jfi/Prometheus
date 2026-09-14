"""Measurement carries its answer: what does the forge's pass gate actually measure?
Deterministic: runs the trap batteries (15-trap static, extended generator) against the NCD baseline and
against RANDOM tools. No LLM calls. Reports chance floor, NCD baseline acc/cal, and P(random tool passes gate).
"""
import sys, types, json, os, random, statistics as st
m=types.ModuleType("openai"); m.OpenAI=object; sys.modules["openai"]=m
sys.path.insert(0,'agents/hephaestus/src')
import test_harness as T
OUT={}
class RandomTool:
    def __init__(self,seed): self.r=random.Random(seed)
    def evaluate(self,prompt,candidates):
        c=list(candidates); self.r.shuffle(c); return [{"candidate":x,"score":1.0-i*0.01} for i,x in enumerate(c)]
    def confidence(self,prompt,cand): return self.r.random()
class ConstantFirst:
    def evaluate(self,prompt,candidates): return [{"candidate":x,"score":1.0-i*0.01} for i,x in enumerate(candidates)]
    def confidence(self,prompt,cand): return 0.5
def gate(tool_res,ncd_res):
    ta,tc,na,nc=tool_res['accuracy'],tool_res['calibration'],ncd_res['accuracy'],ncd_res['calibration']
    return (ta>na or tc>nc) and not (ta<na) and not (tc<nc)
batteries={'static_15':T.TRAPS}
ext=T._load_expanded_battery()
if ext: batteries['extended_generator(seed42)']=ext
for name,traps in batteries.items():
    n=len(traps); floor=st.mean(1/len(t['candidates']) for t in traps)
    ncd=T._run_battery(T._ncd_baseline,traps)
    const=T._run_battery(ConstantFirst(),traps)
    passes=0; accs=[]; cals=[]; N=2000
    for s in range(N):
        r=T._run_battery(RandomTool(s),traps); accs.append(r['accuracy']); cals.append(r['calibration']); passes+=gate(r,ncd)
    cats=len(set(t.get('category','?') for t in traps))
    OUT[name]={'n_traps':n,'n_categories':cats,'candidate_count_hist':dict(sorted(__import__('collections').Counter(len(t['candidates']) for t in traps).items())),
      'chance_floor_accuracy':round(floor,4),'chance_floor_calibration':0.5,
      'ncd_baseline':{'accuracy':round(ncd['accuracy'],4),'calibration':round(ncd['calibration'],4)},
      'constant_first_candidate':{'accuracy':round(const['accuracy'],4),'calibration':round(const['calibration'],4)},
      'random_tool':{'acc_mean':round(st.mean(accs),4),'cal_mean':round(st.mean(cals),4),'P_pass_gate':round(passes/N,4)}}
    print(name, json.dumps(OUT[name],indent=1))
json.dump(OUT,open(os.path.join(os.environ.get('SP',os.path.dirname(os.path.abspath(__file__))),'heph_battery_floor_result.json'),'w'),indent=1)
