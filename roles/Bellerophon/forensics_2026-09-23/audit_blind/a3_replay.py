import json, sys, time
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import grammar as G
from prometheus.z80atlas.world import World
W=r"C:\Users\James\z80atlas_campaign_2026-09-19\runs"
for rid in sys.argv[1:]:
    cfgj=json.load(open(W+"\\"+rid+"\config.json")); summ=json.load(open(W+"\\"+rid+"\summary.json"))
    cfg=G.to_config(cfgj["vec"],cfgj["ticks"],cfgj["cells"],cfgj["budget"],tuple(cfgj["init_tapes"]))
    assert cfg.to_dict()==dict(cfgj["config"],init_tapes=tuple(cfgj["config"]["init_tapes"])), "config mismatch"
    t=time.time(); w=World(cfg,cfgj["seed"]); s=w.run()
    s2=json.loads(json.dumps(s,sort_keys=True,default=str))
    diff=[k for k in s2 if k not in ("geometry","wall_s","config_sha256") and s2[k]!=summ.get(k)]
    print(rid, cfgj["vec"]["reproduction"], "kind", cfgj["reason"][:40], "init_tapes", len(cfgj["init_tapes"]), "replay_diff_keys", diff, "%.0fs"%(time.time()-t))
