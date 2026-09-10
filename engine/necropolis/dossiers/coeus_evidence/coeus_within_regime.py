import sys, types, json, os, numpy as np, collections
m=types.ModuleType("openai"); m.OpenAI=object; sys.modules["openai"]=m
sys.path.insert(0,'agents/coeus/src'); import coeus, causal_graph as cg
from hephaestus import load_ledger, combo_key, _composite
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
rng=np.random.default_rng(1); OUT={}
nous=coeus.load_all_nous(); led=load_ledger(); CUT='2026-03-27T06:49'
# ledger field inspection for regime shift
ex=next(iter(led.values())); OUT['ledger_entry_fields']=sorted(ex.keys())
bydate=collections.Counter()
for k,v in led.items():
    d=str(v.get('timestamp',v.get('forged_at',v.get('date',''))))[:10]; bydate[(d,v.get('status'))]+=1
OUT['ledger_status_by_date']={f"{d}|{s}":c for (d,s),c in sorted(bydate.items())}
X,names,_=cg._encode_dataset(nous,led,combo_key)
keys=[combo_key(e) for e in nous]; ts=np.array([e.get('timestamp','') for e in nous])
ci=[i for i,n in enumerate(names) if n.startswith('concept:')]
fi=[i for i,n in enumerate(names) if n.startswith('field:')]
att=np.array([k in led for k in keys]); y=np.array([1 if (k in led and led[k].get('status')=='forged') else 0 for k in keys])
comp=np.array([_composite(e) for e in nous])
def cv(Xm,yv,label,seed=0):
    skf=StratifiedKFold(5,shuffle=True,random_state=seed); p=np.zeros(len(yv))
    for tr,te in skf.split(Xm,yv):
        p[te]=LogisticRegression(C=1.0,max_iter=5000).fit(Xm[tr],yv[tr]).predict_proba(Xm[te])[:,1]
    a=roc_auc_score(yv,p); k=max(1,len(yv)//10); top=np.argsort(-p)[:k]
    return dict(auc=float(a),prec_at_10pct=float(yv[top].mean()),base_rate=float(yv.mean()))
for regime,mask in [('pre_0327_regime',att&(ts<CUT)),('post_0327_regime',att&(ts>=CUT))]:
    yv=y[mask]; OUT[regime+'::n']=int(mask.sum()); OUT[regime+'::n_forged']=int(yv.sum())
    if yv.sum()<20: OUT[regime+'::note']='too few positives for CV'; continue
    OUT[regime+'::composite_only']=cv(comp[mask][:,None],yv,'comp')
    OUT[regime+'::concepts_only']=cv(X[mask][:,ci],yv,'concepts')
    OUT[regime+'::fields_only']=cv(X[mask][:,fi],yv,'fields')
    OUT[regime+'::composite+concepts']=cv(np.hstack([comp[mask][:,None],X[mask][:,ci]]),yv,'both')
    nulls=[cv(X[mask][:,ci],rng.permutation(yv),'null')['auc'] for _ in range(20)]
    OUT[regime+'::concepts_label_permuted_null']={'mean':float(np.mean(nulls)),'max':float(np.max(nulls))}
    # bootstrap CI on concepts-only minus composite-only delta (paired over folds via seeds)
    deltas=[cv(np.hstack([comp[mask][:,None],X[mask][:,ci]]),yv,'b',seed=s)['auc']-cv(comp[mask][:,None],yv,'c',seed=s)['auc'] for s in range(10)]
    OUT[regime+'::delta_auc_(comp+concepts)-(comp)']={'mean':float(np.mean(deltas)),'min':float(np.min(deltas)),'max':float(np.max(deltas))}
json.dump(OUT,open(os.environ.get('SP', os.path.dirname(os.path.abspath(__file__)))+'/coeus_within_regime_result.json','w'),indent=1)
for k,v in OUT.items():
    if k!='ledger_status_by_date': print(f"{k:50s} {v}")
print("ledger status by date:"); [print("  ",k,v) for k,v in OUT['ledger_status_by_date'].items()]
