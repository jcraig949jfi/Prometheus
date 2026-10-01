import json
from common import *
r = runner()
c = r.cell
print(json.dumps({k: c[k] for k in sorted(c)}, indent=0))
print("derived", r.d)
print("tier", r.tier_name, r.t, "L", r.L, "ops_mask", hex(r._ops_mask()), "copy_mut", r.copy_mut, "policy", r._policy())
print("spec", r.spec.as_dict(), "cue_index", r.spec.cue_index())
print("tasks.z8 is plain:", tasks.z8 is z8_plain, " world.z8 is dense:", world.z8 is DENSE)
