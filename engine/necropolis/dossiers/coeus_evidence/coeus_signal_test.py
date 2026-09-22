"""Necromancer test for Coeus: do its shipped concept scores carry predictive signal about forge success?
Preregistered before running:
  H_alive: shipped forge_boost ranks OOS attempted triples with AUC > permutation-null 97.5th pct AND adds over Nous composite.
  H_dead:  AUC within permutation null (0.5 +- noise) OOS.
  Reorder-null: random score vectors change >=99% of queue positions (shows autopsy observable is vacuous).
"""
import sys, types, json, os, numpy as np, random
m=types.ModuleType("openai"); m.OpenAI=object; sys.modules["openai"]=m
sys.path.insert(0,'agents/coeus/src'); import coeus, causal_graph as cg
from hephaestus import load_ledger, combo_key, _forge_priority, _composite
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
rng=np.random.default_rng(20260910)
OUT={}
scores=json.load(open('agents/coeus/graphs/concept_scores.json',encoding='utf-8'))
nous=coeus.load_all_nous(); led=load_ledger()
CUT='2026-03-27T06:49'
rows=[]
for e in nous:
    k=combo_key(e)
    if k not in led: continue
    y=1 if led[k].get('status')=='forged' else 0
    names=e.get('concept_names',[])
    fb=sum(scores['concept_influence'].get(n,{}).get('forge_effect',0) for n in names)
    sb=0.0
    for i,c1 in enumerate(names):
        for c2 in names[i+1:]:
            for kf in (f"{c1} + {c2}",f"{c2} + {c1}"):
                sb+=scores['pair_synergy'].get(kf,0) if isinstance(scores['pair_synergy'].get(kf,0),(int,float)) else 0
    rows.append(dict(key=k,ts=e.get('timestamp',''),y=y,comp=_composite(e),fb=fb,sb=sb,prio=_forge_priority(e,scores),names=names))
ts=np.array([r['ts'] for r in rows]); y=np.array([r['y'] for r in rows])
ins=ts<CUT; oos=~ins
OUT['n_attempted']=len(rows); OUT['n_in_sample']=int(ins.sum()); OUT['n_oos']=int(oos.sum())
OUT['forge_rate_in']=float(y[ins].mean()); OUT['forge_rate_oos']=float(y[oos].mean()); OUT['n_forged_oos']=int(y[oos].sum())
def auc(s,mask): 
    return float(roc_auc_score(y[mask],s[mask])) if 0<y[mask].sum()<mask.sum() else float('nan')
comp=np.array([r['comp'] for r in rows]); fb=np.array([r['fb'] for r in rows]); sb=np.array([r['sb'] for r in rows]); prio=np.array([r['prio'] for r in rows])
for nm,s in [('nous_composite',comp),('coeus_forge_boost',fb),('coeus_synergy_boost',sb),('coeus_boost_total',fb+sb),('hephaestus_priority',prio)]:
    OUT[f'auc_in::{nm}']=auc(s,ins); OUT[f'auc_oos::{nm}']=auc(s,oos)
# permutation null OOS (shuffle scores)
nullA=[auc(rng.permutation(fb),oos) for _ in range(2000)]
OUT['perm_null_oos_forge_boost']={'mean':float(np.mean(nullA)),'p2.5':float(np.percentile(nullA,2.5)),'p97.5':float(np.percentile(nullA,97.5))}
OUT['perm_p_oos_forge_boost']=float((np.sum(np.array(nullA)>=OUT['auc_oos::coeus_forge_boost'])+1)/(len(nullA)+1))
# does coeus add over composite? residual test: AUC of composite+boost vs composite alone, bootstrap CI of difference OOS
idx=np.where(oos)[0]; diffs=[]
for _ in range(2000):
    b=rng.choice(idx,len(idx),replace=True)
    if 0<y[b].sum()<len(b):
        diffs.append(roc_auc_score(y[b],prio[b])-roc_auc_score(y[b],comp[b]))
OUT['oos_delta_auc_priority_minus_composite']={'mean':float(np.mean(diffs)),'p2.5':float(np.percentile(diffs,2.5)),'p97.5':float(np.percentile(diffs,97.5))}
# precision@top10% OOS
def p_at(s,mask,frac=0.1):
    ii=np.where(mask)[0]; k=max(1,int(frac*len(ii))); top=ii[np.argsort(-s[ii])[:k]]; return float(y[top].mean())
for nm,s in [('nous_composite',comp),('coeus_forge_boost',fb),('hephaestus_priority',prio)]:
    OUT[f'prec@10%_oos::{nm}']=p_at(s,oos)
OUT['prec@10%_oos::random_mean']=float(np.mean([p_at(rng.random(len(rows)),oos) for _ in range(500)]))
# held-out refit of Coeus's own mechanism (concept indicators -> forge) on all attempted rows, 5-fold
X,names,_=cg._encode_dataset(nous,led,combo_key)
ci=[i for i,n in enumerate(names) if n.startswith('concept:')]
keys_all=[combo_key(e) for e in nous]; kidx={k:i for i,k in enumerate(keys_all)}
Xa=X[[kidx[r['key']] for r in rows]][:,ci]
skf=StratifiedKFold(5,shuffle=True,random_state=0); pred=np.zeros(len(rows))
for tr,te in skf.split(Xa,y):
    clf=LogisticRegression(C=1.0,max_iter=5000).fit(Xa[tr],y[tr]); pred[te]=clf.predict_proba(Xa[te])[:,1]
OUT['cv5_auc_concept_indicators_logreg']=float(roc_auc_score(y,pred))
yp=rng.permutation(y); predp=np.zeros(len(rows))
for tr,te in skf.split(Xa,yp):
    clf=LogisticRegression(C=1.0,max_iter=5000).fit(Xa[tr],yp[tr]); predp[te]=clf.predict_proba(Xa[te])[:,1]
OUT['cv5_auc_label_permuted']=float(roc_auc_score(yp,predp))
# reorder-null: random scores reorder a queue of this size
N=len(rows); base=np.argsort(-comp); changed=[]
for _ in range(200):
    r=np.argsort(-(comp+rng.normal(0,1e-3,N))); changed.append(float(np.mean(base!=r)))
OUT['reorder_null_frac_positions_changed_by_1e-3_noise']={'mean':float(np.mean(changed)),'min':float(np.min(changed))}
r=np.argsort(-prio); OUT['reorder_actual_frac_positions_changed_by_coeus']=float(np.mean(base!=r))
json.dump(OUT,open(os.environ.get('SP', os.path.dirname(os.path.abspath(__file__)))+'/coeus_signal_result.json','w'),indent=1)
for k,v in OUT.items(): print(f"{k:60s} {v}")
