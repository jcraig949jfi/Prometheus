import sys, types, json, os, glob, numpy as np
m=types.ModuleType("openai"); m.OpenAI=object; sys.modules["openai"]=m
sys.path.insert(0,'agents/coeus/src'); import coeus, causal_graph as cg
from hephaestus import load_ledger, combo_key, _composite
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, LeaveOneGroupOut
rng=np.random.default_rng(2); OUT={}
led=load_ledger(); CUT='2026-03-27T06:49'
# load nous with run-id groups (mirror coeus.load_all_nous ordering by re-reading run dirs)
nous=[]; grp=[]
for d in sorted(glob.glob('agents/nous/runs/*/')):
    p=os.path.join(d,'responses.jsonl')
    if not os.path.exists(p): continue
    for l in open(p,encoding='utf-8'):
        if l.strip(): nous.append(json.loads(l)); grp.append(os.path.basename(os.path.normpath(d)))
grp=np.array(grp)
X,names,_=cg._encode_dataset(nous,led,combo_key)
ci=[i for i,n in enumerate(names) if n.startswith('concept:')]
keys=[combo_key(e) for e in nous]; ts=np.array([e.get('timestamp','') for e in nous])
att=np.array([k in led for k in keys]); y=np.array([1 if (k in led and led[k].get('status')=='forged') else 0 for k in keys])
apifail=np.array([k in led and str(led[k].get('reason','')).startswith('api_call_failed') for k in keys])
comp=np.array([_composite(e) for e in nous])
def fit_pred(Xm,yv,splits):
    p=np.zeros(len(yv))
    for tr,te in splits:
        if yv[tr].sum()==0: p[te]=0; continue
        p[te]=LogisticRegression(C=1.0,max_iter=5000).fit(Xm[tr],yv[tr]).predict_proba(Xm[te])[:,1]
    return p
def report(tag,mask,groups=None):
    yv=y[mask]; Xc=X[mask][:,ci]; c=comp[mask][:,None]; both=np.hstack([c,Xc])
    if groups is None: splits=list(StratifiedKFold(5,shuffle=True,random_state=0).split(Xc,yv))
    else: splits=list(LeaveOneGroupOut().split(Xc,yv,groups[mask]))
    r={'n':int(mask.sum()),'n_forged':int(yv.sum()),'base_rate':float(yv.mean())}
    for nm,Xm in [('composite',c),('concepts',Xc),('composite+concepts',both)]:
        p=fit_pred(Xm,yv,splits); r['auc::'+nm]=float(roc_auc_score(yv,p))
    r['delta_(comp+concepts)-(comp)']=r['auc::composite+concepts']-r['auc::composite']
    nulls=[float(roc_auc_score(yp,fit_pred(Xc,yp,splits))) for yp in (rng.permutation(yv) for _ in range(10))]
    r['concepts_null_mean']=float(np.mean(nulls)); r['concepts_null_max']=float(np.max(nulls))
    OUT[tag]=r; print(tag); [print(f"   {k:34s} {v}") for k,v in r.items()]
pre=att&(ts<CUT)
#report('A_pre_regime_all_attempted_stratCV', pre)
#report('B_pre_regime_EXCL_api_failed_stratCV', pre&~apifail)
report('C_pre_regime_EXCL_api_failed_LEAVE_ONE_NOUS_RUN_OUT', pre&~apifail, grp)
OUT['n_api_failed_pre']=int((pre&apifail).sum()); OUT['n_api_failed_post']=int((att&(ts>=CUT)&apifail).sum())
OUT['runs_in_pre_regime']={g:int((pre&~apifail&(grp==g)).sum()) for g in sorted(set(grp[pre]))}
print("api_failed pre/post:",OUT['n_api_failed_pre'],OUT['n_api_failed_post']); print("runs pre:",OUT['runs_in_pre_regime'])
json.dump(OUT,open(os.environ.get('SP', os.path.dirname(os.path.abspath(__file__)))+'/coeus_attacks_result.json','w'),indent=1)
# per-fold LOGO AUC on runs with >=50 rows and >=5 positives
mask=pre&~apifail; yv=y[mask]; Xc=X[mask][:,ci]; c=comp[mask][:,None]; both=np.hstack([c,Xc]); g=grp[mask]
PF={}
for run in sorted(set(g)):
    te=g==run; tr=~te
    if te.sum()<50 or yv[te].sum()<5 or yv[te].sum()==te.sum(): continue
    row={'n':int(te.sum()),'pos':int(yv[te].sum())}
    for nm,Xm in [('composite',c),('concepts',Xc),('both',both)]:
        p=LogisticRegression(C=1.0,max_iter=5000).fit(Xm[tr],yv[tr]).predict_proba(Xm[te])[:,1]; row[nm]=round(float(roc_auc_score(yv[te],p)),3)
    nulls=[]
    for _ in range(10):
        yp=yv.copy(); yp[tr]=rng.permutation(yv[tr])
        p=LogisticRegression(C=1.0,max_iter=5000).fit(Xc[tr],yp[tr]).predict_proba(Xc[te])[:,1]; nulls.append(roc_auc_score(yv[te],p))
    row['concepts_null_max']=round(float(np.max(nulls)),3); row['delta_both-comp']=round(row['both']-row['composite'],3)
    PF[run]=row; print(run,row)
OUT['per_fold_LOGO']=PF
json.dump(OUT,open(os.environ.get('SP', os.path.dirname(os.path.abspath(__file__)))+'/coeus_attacks_result.json','w'),indent=1)
print("=== leave-one-FORGE-DAY-out (excl api failures) ===")
fday=np.array([str(led[k].get('timestamp',''))[:10] if k in led else '' for k in keys])
mask=att&~apifail; yv=y[mask]; Xc=X[mask][:,ci]; c=comp[mask][:,None]; both=np.hstack([c,Xc]); g=fday[mask]
FD={}
for day in sorted(set(g)):
    te=g==day; tr=~te
    if te.sum()<50 or yv[te].sum()<5 or yv[te].sum()==te.sum(): continue
    row={'n':int(te.sum()),'pos':int(yv[te].sum())}
    for nm,Xm in [('composite',c),('concepts',Xc),('both',both)]:
        p=LogisticRegression(C=1.0,max_iter=5000).fit(Xm[tr],yv[tr]).predict_proba(Xm[te])[:,1]; row[nm]=round(float(roc_auc_score(yv[te],p)),3)
    nulls=[]
    for _ in range(10):
        yp=yv.copy(); yp[tr]=rng.permutation(yv[tr])
        p=LogisticRegression(C=1.0,max_iter=5000).fit(Xc[tr],yp[tr]).predict_proba(Xc[te])[:,1]; nulls.append(roc_auc_score(yv[te],p))
    row['concepts_null_max']=round(float(np.max(nulls)),3); row['delta_both-comp']=round(row['both']-row['composite'],3)
    FD[day]=row; print(day,row)
OUT['per_forge_day_LOGO']=FD
json.dump(OUT,open(os.environ.get('SP', os.path.dirname(os.path.abspath(__file__)))+'/coeus_attacks_result.json','w'),indent=1)
print("=== run x forge-day crosstab (excl api fail) ===")
import collections
ct=collections.Counter(zip(grp[att&~apifail],fday[att&~apifail]))
days=sorted(set(fday[att&~apifail])); print("day".ljust(18),*[d[5:] for d in days])
for r in sorted(set(grp[att&~apifail])): print(r.ljust(18),*[str(ct[(r,d)]).rjust(5) for d in days])
print("=== WITHIN-single-forge-day stratified 5-fold CV (excl api fail) ===")
WD={}
for day in days:
    mk=att&~apifail&(fday==day); yv=y[mk]
    if mk.sum()<150 or yv.sum()<20 or yv.sum()==mk.sum(): continue
    Xc=X[mk][:,ci]; c=comp[mk][:,None]; both=np.hstack([c,Xc])
    splits=list(StratifiedKFold(5,shuffle=True,random_state=0).split(Xc,yv))
    row={'n':int(mk.sum()),'pos':int(yv.sum())}
    for nm,Xm in [('composite',c),('concepts',Xc),('both',both)]: row[nm]=round(float(roc_auc_score(yv,fit_pred(Xm,yv,splits))),3)
    nulls=[float(roc_auc_score(yp,fit_pred(Xc,yp,splits))) for yp in (rng.permutation(yv) for _ in range(20))]
    row['concepts_null_mean']=round(float(np.mean(nulls)),3); row['concepts_null_max']=round(float(np.max(nulls)),3); row['delta_both-comp']=round(row['both']-row['composite'],3)
    WD[day]=row; print(day,row)
OUT['within_forge_day_CV']=WD; OUT['run_x_forgeday']={f"{r}|{d}":c for (r,d),c in ct.items()}
json.dump(OUT,open(os.environ.get('SP', os.path.dirname(os.path.abspath(__file__)))+'/coeus_attacks_result.json','w'),indent=1)
