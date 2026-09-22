"""Third measurement line: Nemesis adversarial results (contemporaneous consumer of forged tools).
Per-tool accuracy over the adversarial prompts vs the per-prompt chance floor; plus what the forge's own
'tools_broken' field says about the forged population."""
import json, os, collections, statistics as st
rows=[json.loads(l) for l in open('agents/nemesis/adversarial/adversarial_results.jsonl',encoding='utf-8') if l.strip()]
OUT={'n_prompts':len(rows)}
tool_hits=collections.defaultdict(lambda:[0,0]); floor=[]
for r in rows:
    floor.append(1/len(r['candidates']))
    for t,res in r.get('tool_results',{}).items():
        a=res.get('answer') if isinstance(res,dict) else res
        tool_hits[t][1]+=1; tool_hits[t][0]+=int(a==r['correct'])
OUT['chance_floor_mean']=round(st.mean(floor),4)
accs={t:h[0]/h[1] for t,h in tool_hits.items() if h[1]>=20}
OUT['n_tools_evaluated']=len(accs)
OUT['tool_accuracy']={'median':round(st.median(accs.values()),4),'mean':round(st.mean(accs.values()),4),'min':round(min(accs.values()),4),'max':round(max(accs.values()),4),
  'n_above_floor_by_0.10':sum(1 for a in accs.values() if a>OUT['chance_floor_mean']+0.10),'n_below_floor_by_0.10':sum(1 for a in accs.values() if a<OUT['chance_floor_mean']-0.10)}
OUT['tools_broken_per_prompt']={'median':st.median(r.get('tools_broken',0) for r in rows),'max':max(r.get('tools_broken',0) for r in rows),'n_tools_per_prompt_median':st.median(len(r.get('tool_results',{})) for r in rows)}
OUT['blind_spot_prompts']=sum(1 for r in rows if r.get('blind_spot'))
OUT['category_hist']=dict(collections.Counter(r.get('category') for r in rows).most_common(10))
json.dump(OUT,open(os.path.join(os.environ.get('SP',os.path.dirname(os.path.abspath(__file__))),'heph_nemesis_consumer_result.json'),'w'),indent=1)
print(json.dumps(OUT,indent=1))

# --- tail check: are the above-floor tools skilled or constant-index answerers? (position-bias null)
pos=collections.Counter(r['candidates'].index(r['correct']) if r['correct'] in r['candidates'] else -1 for r in rows)
OUT['correct_index_hist']=dict(sorted(pos.items()))
def const_index_acc(i): return sum(1 for r in rows if r['correct'] in r['candidates'] and r['candidates'].index(r['correct'])==i and i<len(r['candidates']))/len(rows)
OUT['constant_index_tool_accuracy']={f'always_{i}':round(const_index_acc(i),4) for i in range(5)}
top=sorted(accs.items(),key=lambda kv:-kv[1])[:8]; det=[]
for t,a in top:
    ans=collections.Counter()
    for r in rows:
        res=r['tool_results'].get(t); x=res.get('answer') if isinstance(res,dict) else res
        if x is not None and x in r['candidates']: ans[r['candidates'].index(x)]+=1
    tot=sum(ans.values()) or 1
    det.append({'tool':t,'acc':round(a,4),'answered':tot,'top_index_share':round(max(ans.values())/tot,3) if ans else None,'index_hist':dict(ans)})
OUT['top_tools_answer_index_profile']=det
json.dump(OUT,open(os.path.join(os.environ.get('SP',os.path.dirname(os.path.abspath(__file__))),'heph_nemesis_consumer_result.json'),'w'),indent=1)
print(json.dumps({k:OUT[k] for k in ('correct_index_hist','constant_index_tool_accuracy','top_tools_answer_index_profile')},indent=1))

# --- decisive: first-or-last position null vs top tools on MIDDLE-position prompts only
def is_first_or_last(r): 
    i=r['candidates'].index(r['correct']) if r['correct'] in r['candidates'] else -1
    return i==0 or i==len(r['candidates'])-1
fl=[r for r in rows if is_first_or_last(r)]; mid=[r for r in rows if not is_first_or_last(r) and r['correct'] in r['candidates']]
OUT['first_or_last_null']={'n_prompts_first_or_last':len(fl),'n_prompts_middle':len(mid),'ceiling_acc_of_first_or_last_picker':round(len(fl)/len(rows),4)}
mid_acc=[]
for t,a in top:
    c=n=0
    for r in mid:
        res=r['tool_results'].get(t); x=res.get('answer') if isinstance(res,dict) else res
        if x is not None: n+=1; c+=int(x==r['correct'])
    mid_acc.append({'tool':t,'overall_acc':round(a,4),'middle_prompts_answered':n,'middle_prompts_acc':round(c/n,4) if n else None})
OUT['top_tools_on_middle_prompts']=mid_acc
OUT['middle_prompt_chance_floor']=round(st.mean(1/len(r['candidates']) for r in mid),4) if mid else None
json.dump(OUT,open(os.path.join(os.environ.get('SP',os.path.dirname(os.path.abspath(__file__))),'heph_nemesis_consumer_result.json'),'w'),indent=1)
print(json.dumps({k:OUT[k] for k in ('first_or_last_null','top_tools_on_middle_prompts','middle_prompt_chance_floor')},indent=1))
