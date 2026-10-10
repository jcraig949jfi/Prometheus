import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1].parent.parent / "bel48h_2026-10-08" / "tools"))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[5]))
import analyze_d2
from plan_w5 import BASE
from prometheus.z80atlas.world import Config


def test_selective_worlds_partition_imports():
    from origin import OriginWorld
    from uptake_select import LdirUptakeBlockWorld, NoLdirUptakeBlockWorld
    c = Config(**dict(BASE, ticks=80, cells=64))
    a = LdirUptakeBlockWorld(c, 3); a.run(); b = NoLdirUptakeBlockWorld(c, 3); b.run()
    for w in (a, b):
        assert w.O["import_exec_ldir"] + w.O["import_exec_noldir"] > 0
    assert a.O["blocked_bytes"] > 0 or a.O["import_exec_ldir"] == 0
    assert b.O["blocked_bytes"] > 0 or b.O["import_exec_noldir"] == 0


def test_analysis_branches(tmp_path):
    rows = []
    for s, ldir_gain in (("S_A", True), ("S_B", False)):
        for k in range(30):
            for arm in ("normal", "block_all", "block_ldir", "block_noldir"):
                ev = (arm in ("block_all", "block_ldir") and ldir_gain and k < 15) or (k >= 28)
                rows.append({"cell": s, "pair": k, "arm": arm, "origin": {"origin_event": {"x": 1} if ev else None, "O": {"blocked_bytes": 1}}})
    rows.append({"void": True})
    p = tmp_path / "r.jsonl"; p.write_text("\n".join(map(json.dumps, rows)))
    o = analyze_d2.main(str(p), str(tmp_path / "o.json"))
    assert o["substrates"]["S_A"]["holds"] is True and o["substrates"]["S_B"]["holds"] is False and o["D2"]["holds"] is False
    assert o["substrates"]["S_A"]["origins"]["block_ldir"] == 17 and o["voids"] == 1
