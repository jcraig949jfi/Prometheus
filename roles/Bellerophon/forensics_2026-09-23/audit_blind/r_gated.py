import sys
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas.world import World, Config
for p in ("IMPLICIT","GATED_INTERACTION"):
    cfg=Config(pressure=p, reproduction="ENDOGENOUS_COPY", cells=64, ticks=120, world="SOUP", spatial="WELL_MIXED", scoring="ATOMIC", task="COND_MULTI")
    w=World(cfg,3)
    for _ in range(120): w.step()
    alive=[o for o in w.cells if o]
    print(p,"tick 120: alive",len(alive),"deaths",w.deaths,"max(tick-birth)",max((w.tick-o.birth) for o in alive) if alive else None,"max age",max((o.age for o in alive),default=None),"(lifespan 40)")
