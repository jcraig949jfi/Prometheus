import json, sys, pathlib, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import analyze_a3


def _write(tmp, informative_moves):
    rng = random.Random(1); scan, test = [], []
    for c in ("ENDOGENOUS_PARTIAL", "PAIR_EXECUTION", "ENDOGENOUS_COPY"):
        rows = []
        for i in range(40):
            mv = rng.randrange(0, 50); sub = rng.randrange(0, 3); tape = bytes([i, len(c)] + [1] * (i % 7)).hex()
            rows.append({"tape": tape, "SUB": sub, "MOVE": mv, "INS": 0, "DEL": 0})
            hit = (mv > 25) if informative_moves else (sub > 0)
            for k in range(2):
                test.append({"cell": c, "arm": "REPLANT", "precursor": tape, "origin": {"origin_event": {"x": 1} if (hit and k == 0) else None}})
        scan.append({"cell": c, "scan": rows})
        test.append({"cell": c, "arm": "BACKGROUND", "precursor": None, "origin": {"origin_event": None}})
    test.append({"void": True})
    (tmp / "s.jsonl").write_text("\n".join(map(json.dumps, scan))); (tmp / "t.jsonl").write_text("\n".join(map(json.dumps, test)))


def test_moves_informative(tmp_path):
    _write(tmp_path, True)
    o = analyze_a3.main(str(tmp_path / "s.jsonl"), str(tmp_path / "t.jsonl"), str(tmp_path / "o.json"), B=200)
    assert o["voids"] == 1 and o["tapes"] == 120 and o["A3-P1"] is True and o["A3-P2"] is True and o["A3-P3"] is True


def test_sub_only_informative(tmp_path):
    _write(tmp_path, False)
    o = analyze_a3.main(str(tmp_path / "s.jsonl"), str(tmp_path / "t.jsonl"), str(tmp_path / "o.json"), B=200)
    assert o["A3-P1"] is False
