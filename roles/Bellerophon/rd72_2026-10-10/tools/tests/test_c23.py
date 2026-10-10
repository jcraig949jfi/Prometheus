import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import plan_c23, analyze_c23


def _cen(seq):
    return [{"tick": 100 * (i + 1), "alive": 50, "halves": {}, "halves_func": hf, "top_func": {"LO": "aa" if hf.get("LO") else None}} for i, hf in enumerate(seq)]


def test_plan_and_analysis(tmp_path):
    e1 = [{"id": "w1", "cell": "C1_ON", "census": _cen([{}, {"LO": 2}, {"LO": 2}, {"LO": 3}, {"LO": 3}]), "summary": {"extinct": False}},
          {"id": "w2", "cell": "C1_ON", "census": _cen([{}] * 6), "summary": {"extinct": False}},
          {"id": "w3", "cell": "CM_ON", "census": _cen([{"LO": 1}, {}, {"LO": 1}, {"BOTH": 1}]), "summary": {"extinct": False}},
          {"id": "w4", "cell": "C1_ON", "census": _cen([{"LO": 1}]), "summary": {"extinct": True}}, {"id": "v", "void": True}]
    plan = [{"id": i, "seed": k, "cfg": {"ticks": 2000}} for k, i in enumerate(("w1", "w2", "w3", "w4", "v"))]
    (tmp_path / "e.jsonl").write_text("\n".join(map(json.dumps, e1))); (tmp_path / "p.json").write_text(json.dumps(plan))
    P = plan_c23.plan(str(tmp_path / "e.jsonl"), str(tmp_path / "p.json"))
    lanes = sorted((p["lane"], p["pair"], p["arm"], p["at"]) for p in P)
    assert ("C2", "w1", "REMOVE", 400) in lanes and ("C3", "w1", "ABLATE", 400) in lanes
    assert ("C2", "w3", "REMOVE", 300) in lanes and not any(l[0] == "C3" and l[1] == "w3" for l in lanes)
    assert ("C3F", "w2", "IMPLANT", 500) in lanes and not any(l[1] == "w4" for l in lanes)
    imp = next(p for p in P if p["arm"] == "IMPLANT"); assert imp["tapes"] == ["aa"] and imp["cfg"]["ticks"] == 2000
    rows = []
    for p in P:
        lo = p["arm"] in ("NONE", "SHAM", "A_PRESENT", "IMPLANT")
        cen = [{"tick": p["at"] + 100, "halves_func": {"LO": 1} if lo else {}}, {"tick": p["at"] + 200, "halves_func": {"LO": 1, "BOTH": 1} if lo else {}}]
        rows.append({"pair": p["pair"], "arm": p["arm"], "lane": p["lane"], "intervention": {"tick": p["at"], "affected": 3}, "census": cen,
                     "summary": {"extinct": False}})
    (tmp_path / "c.jsonl").write_text("\n".join(map(json.dumps, rows)))
    o = analyze_c23.main(str(tmp_path / "c.jsonl"), str(tmp_path / "e.jsonl"), str(tmp_path / "o.json"))
    assert o["C2-a"]["sham_lo_end"] == [2, 2] and o["C2-a"]["remove_lo_end"] == [0, 2]
    assert o["C2-b"]["holds"] == "NOT_TESTABLE" and o["C3-P1"]["holds"] == "NOT_TESTABLE"
