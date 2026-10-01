"""W2-X check: does physics_from_levels' in-place lv mutation (dc46fd00f) leak a forced dest_mode into
descendant specs? Emulates wave_A0/_draw_cell (lv stored WITHOUT copying), then a wave-B topology
transect from that global base. Run with PYTHONPATH=scratch/pre or scratch/post."""
import os; os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import torch; torch.set_num_threads(2); assert not torch.cuda.is_available()
from prometheus.ananke import campaign as C
cfg = C.CampaignConfig()
lv = C.draw_levels(1, C.DIALS); lv.update(topology="global", dest_mode="all")
ph = C.physics_from_levels(lv, topo_seed=5)          # as _draw_cell / wave_A do: no copy
base = {"levels": lv, "env_levels": {"d": 1, "delta": 4, "gap": 4, "block": 2},
        "physics": ph.to_dict(), "cell_id": "x"}
for s in C._transect_specs(cfg, "RELAY", base, 0, "topology", "phys", "census", {}, 1):
    s["cell_id"] = C.cell_id(s)
    print(s["physics"]["topology"], "ran dest_mode =", s["physics"]["dest_mode"], "cell", s["cell_id"])
