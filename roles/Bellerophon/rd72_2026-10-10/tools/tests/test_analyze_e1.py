import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import analyze_e1


def _run(i, cell, seq, extinct=False):
    C = [{"tick": 100 * (k + 1), "alive": 10, "halves": {}, "halves_func": hf} for k, hf in enumerate(seq)]
    return {"id": i, "cell": cell, "census": C, "summary": {"extinct": extinct}, "exposure": 5, "first_both": None}


def test_branches(tmp_path):
    rows = [_run("a", "C1_ON", [{}, {"LO": 3}, {"LO": 2}, {"LO": 1, "BOTH": 1}]),      # LO first, BOTH at 400, retained
            _run("b", "C1_ON", [{"HI": 1}, {}, {"BOTH": 2}]),                         # HI first; LO via BOTH at 300
            _run("c", "C1_ON", [{"BOTH": 1}]),                                        # NONE_PRIOR
            _run("d", "C1_OFF", [{}, {}], extinct=True),
            _run("e", "C1_OFF", [{"LO": 1}, {}, {}]),                                 # lost: retention 0
            {"id": "v", "cell": "C1_ON", "void": True}]
    p = tmp_path / "r.jsonl"; p.write_text("\n".join(json.dumps(r) for r in rows))
    o = analyze_e1.main(str(p), str(tmp_path / "o.json"))
    a = o["cells"]["C1_ON"]
    assert (a["runs"], a["LO"], a["HI"], a["BOTH"]) == (3, 3, 3, 3) and o["voids"] == 1
    assert a["order"] == {"LO_FIRST": 1, "HI_FIRST": 1, "BOTH_PRIOR": 0, "NONE_PRIOR": 1}
    r = {x["id"]: x for x in o["runs"]["C1_OFF"]}
    assert r["e"]["retention_LO"] == 0.0 and r["d"]["t_LO"] is None and o["cells"]["C1_OFF"]["survived"] == 1
    assert r_a(o) == 1.0 and o["replay_queue"] == ["a", "b", "c"]


def r_a(o):
    return {x["id"]: x for x in o["runs"]["C1_ON"]}["a"]["retention_LO"]
