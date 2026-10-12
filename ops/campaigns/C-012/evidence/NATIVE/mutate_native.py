"""C-012-T007 mutation table for the native wforge runtime (moonshot/epoch/native_wforge.py): every restored field
and every refusal must be load-bearing. Same mechanics as ../T002/mutate_pg.py (no database needed).
    python ops/campaigns/C-012/evidence/NATIVE/mutate_native.py [--out results.json]
"""
import importlib.util
import os
from pathlib import Path

os.environ.setdefault("EW_DB_HOST", "unused-no-database")       # the harness checks it is set; nothing connects
_spec = importlib.util.spec_from_file_location("mutate_pg", Path(__file__).resolve().parents[1] / "T002" / "mutate_pg.py")
MP = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MP)

MP.EXTRA_TREES[:] = ["SerendipityFoundry/worldfoundry/wforge"]
T = "moonshot.epoch.tests.test_native_wforge."
N = "epoch/native_wforge.py"
CONF = [T + "TestConformance"]
MP.M[:] = [
    ("NM01", "the stochastic stream is not restored", N, "    enc._s_stoch.s = o[\"s_stoch\"]\n", "", CONF),
    ("NM02", "pending writes are not restored", N, "    enc.pending = [tuple(x) for x in o[\"pending\"]]\n", "", CONF),
    ("NM03", "the observation history is not restored", N, "    enc.history = [list(h) for h in o[\"history\"]]\n", "",
     CONF),
    ("NM04", "the corruption streams are not restored", N, "    for x, s in zip(enc._s_corrupt, o[\"s_corrupt\"]):\n        x.s = s\n",
     "", CONF),
    ("NM05", "charge is not restored", N, "        setattr(enc, k, list(o[k]))", "        pass", CONF),
    ("NM06", "the tick is not restored", N, "    enc.tick = o[\"tick\"]\n", "", CONF),
    ("NM07", "the policy may act beyond its charge", N, " or sum(a) * mech.act_cost > enc.charge[s]:", ":",
     [T + "TestConformance.test_the_policy_never_takes_an_unaffordable_action"]),
    ("NM08", "another wforge implementation is accepted", N,
     "    if p[\"wforge_world_sha256\"] != world_sha256():", "    if False:",
     [T + "TestIdentityAndRefusals.test_a_different_wforge_is_refused"]),
    ("NM09", "a checkpoint of another world is accepted", N,
     "    if (o.get(\"world_id\"), o.get(\"episode_seed\")) != (p[\"world_id\"], p[\"episode_seed\"]):", "    if False:",
     [T + "TestIdentityAndRefusals"]),
    ("NM10", "a finished world keeps ticking", N,
     "        if enc.tick >= mech.horizon or not any(enc.alive):\n            break                                                       # a finished world stays finished",
     "        if False:\n            break",
     [T + "TestConformance.test_a_finished_world_stays_finished"]),
]

if __name__ == "__main__":
    MP.main()
