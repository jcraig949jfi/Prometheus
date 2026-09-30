"""The Avida ancestry apparatus, on SYNTHETIC fixtures only. No test here opens a .spop from the body: the packet
MECH-AVIDA-ANCESTRY-RETENTION-001 is blind and stays blind for its author."""
import hashlib
import json
from pathlib import Path

from nyx.atlas.experiments.avida_ancestry import adjudicate, definedness, spop, strata
from nyx.atlas.experiments.avida_ancestry.model import World
from nyx.atlas.predictions import schema as ps

HERE = Path(__file__).resolve().parents[1] / "atlas" / "experiments" / "avida_ancestry"
PRED = Path(__file__).resolve().parents[1] / "atlas" / "predictions"
PID = "MECH-AVIDA-ANCESTRY-RETENTION-001"


def test_reader_follows_the_writer_and_survives_spaces_in_src_args():
    plain = "7 div:int (none) 3 2 5 12 97 389 0.25 4 17 -1 3 0 heads_default abcdefghijkl 4,9 12,40 0,0 ".split()
    r = spop.parse_row(plain)
    assert (r["id"], r["parents"], r["num_units"], r["update_born"], r["depth"], r["sequence"], r["n_cells"], r["shift"]) == \
        (7, [3], 2, 17, 3, "abcdefghijkl", 2, 0)
    shifted = "8 div:ext whole-genome duplication (none) 1 1 24 0 0 0 -1 100 -1 0 0 heads_default abcdefghijklabcdefghijkl 5 0 0 ".split()
    r = spop.parse_row(shifted)
    assert (r["src_args"], r["parents"], r["update_born"], r["depth"], r["shift"]) == ("whole-genome duplication", [], 100, 0, 1)
    assert spop.parse_row("not a row at all".split()) is None
    dead = "9 div:int (none) 7,7 0 4 12 0 0 0 -1 20 31 4 0 heads_default abcdefghijkm ".split()
    r = spop.parse_row(dead)
    assert (r["parents"], r["num_units"], r["update_deactivated"], r["n_cells"]) == ([7, 7], 0, 31, 0)


def test_a5_definedness_and_controls_on_fixtures():
    r = definedness.run()
    bad = [c for c in r["controls_and_expectations"] if not c["ok"]]
    assert not bad, bad
    assert r["table"]["BASE"]["I2"]["verdict"] == "HOLDS" and r["table"]["UNPRUNED"]["I2"]["verdict"] == "VIOLATED"
    assert r["table"]["HIST0"]["I2"]["verdict"] == "NOT_ELIGIBLE"          # refused at plan time, never a pass
    committed = json.loads((HERE / "DEFINEDNESS.json").read_text(encoding="utf-8"))
    assert committed["table"] == json.loads(json.dumps(r["table"])), "DEFINEDNESS.json is stale: re-run the module"


def test_the_clock_never_stamps_zero_and_stamps_update_zero_as_minus_one():
    w = World(mu=1.0)                                       # every birth founds a genotype
    w.run(3)
    stamps = sorted({g.update_born for g in w.arb.ever})
    assert 0 not in stamps and stamps[0] == -1 and set(stamps) <= {-1, 1, 2, 3}
    assert sum(1 for g in w.arb.ever if g.update_born == -1) > 1   # the ancestor AND what update 0 founded


def _strata_for(world: World, test: str, **flags):
    rows = []
    for name, text in world.files.items():
        f = spop.read_text(text, name)
        rows.append(({"path": f"tree/avida-core/tests/{test}/expected/data/{name}", "sha256": hashlib.sha256(text.encode()).hexdigest(),
                      "bytes": len(text), "test": test, "role": "expected", "kind": "population", "T": f["T"], "hist0": False,
                      "loaded": False, "deme": False, "class_off": False, "sexual_config": False, "series": None, "sever_at": None,
                      **flags}, text))
    return rows


def _adjudicate(*groups):
    rows = [r for g in groups for r in g]
    texts = {r["path"]: t for r, t in rows}
    return adjudicate.run({"files": [r for r, _ in rows]}, lambda row: (texts[row["path"]], hashlib.sha256(texts[row["path"]].encode()).hexdigest()))


def test_harness_supports_a_faithful_world_and_fails_each_broken_one():
    ok = _adjudicate(_strata_for(definedness._arm("BASE"), "base", series="base"),
                     _strata_for(definedness._arm("SEVER"), "sever", series="sever", sever_at=20),
                     _strata_for(definedness._arm("HIST0"), "hist0", hist0=True))
    assert {k: v["verdict"] for k, v in ok["rows"].items()} == {k: "SUPPORTED" for k in ok["rows"]}, ok["rows"]
    assert all(v["eligible"] > 0 for v in ok["rows"].values())
    assert not ok["cut_kill"]

    unpruned = _adjudicate(_strata_for(definedness._arm("UNPRUNED"), "u"))
    assert unpruned["rows"]["I2-NO-DEAD-LEAF"]["verdict"] == "PREDICTION_FAILED"
    assert unpruned["rows"]["I1-PARENT-CLOSURE"]["verdict"] == "SUPPORTED"

    holder = _adjudicate(_strata_for(definedness._arm("ACTIVE_HOLDER"), "h"))
    assert holder["rows"]["I1-PARENT-CLOSURE"]["verdict"] == "PREDICTION_FAILED"

    # the exclusions work: the same broken worlds, flagged as the packet's strata flag them, are simply not claimed
    excl = _adjudicate(_strata_for(definedness._arm("PASSIVE_HOLDER"), "d", deme=True),
                       _strata_for(definedness._arm("ACTIVE_HOLDER"), "s", sexual_config=True),
                       _strata_for(definedness._arm("SEXUAL"), "m"), _strata_for(definedness._arm("PARASITE"), "p"))
    assert excl["rows"]["I2-NO-DEAD-LEAF"]["verdict"] == "PREDICTION_INDETERMINATE"
    assert excl["rows"]["I1-PARENT-CLOSURE"]["violations"] == 0
    # the content rule is per FILE: the sexual run's begin save holds one parentless ancestor and passes it, harmlessly
    assert excl["stratum_sizes"]["S_B"] == 1 and excl["rows"]["I4-LIVING-GENOME-IS-A-KEY"]["eligible"] == 1


def test_harness_refuses_wrong_bytes_and_refuses_its_author():
    rows = _strata_for(definedness._arm("BASE"), "base")
    res = adjudicate.run({"files": [r for r, _ in rows]}, lambda row: ("tampered", "0" * 64))
    assert len(res["hash_mismatch"]) == len(rows) and res["cut_kill"]
    assert all(v["verdict"] == "PREDICTION_INDETERMINATE" for v in res["rows"].values())
    assert adjudicate.main([]) == 2 and adjudicate.main(["--adjudicator", "Nyx[gandalf]"]) == 2


def test_strata_table_is_the_techne_hash_list_and_nothing_else():
    s = json.loads((HERE / "STRATA.json").read_text(encoding="utf-8"))
    listed = {}
    for line in strata.HASHES.read_text(encoding="utf-8").splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3 and parts[2].strip().endswith(".spop"):
            listed[parts[2].strip().replace("\\", "/")] = parts[0]
    assert {f["path"]: f["sha256"] for f in s["files"]} == listed and len(listed) == s["n_files"] == 177
    assert all(f["loaded"] is None for f in s["files"] if f["role"] == "config")       # inputs are never claimed
    series = [f for f in s["files"] if f["series"]]
    assert {f["series"] for f in series} == set(strata.SERIES) and all(f["sever_at"] == 100 for f in series)
    assert strata._fires_at("0:10:end", 100) and not strata._fires_at("0:10:end", 95) and strata._fires_at("begin", -1)


def test_packet_is_valid_frozen_and_bound_to_its_apparatus():
    p = json.loads((PRED / f"{PID}.json").read_text(encoding="utf-8"))
    assert ps.validate(p) == []
    assert ps.packet_hash(p) == (PRED / f"{PID}.FREEZE").read_text(encoding="utf-8").split()[0]
    assert {iv["intervention_id"] for iv in p["interventions"]} == set(adjudicate.ROWS) | {"I7-SERIES-PERSISTENCE", "I8-SEVERANCE"}
    assert all(iv["expected_magnitude_band"] == [0, 0] and iv.get("novelty_kind") for iv in p["interventions"])
    for name, sha in p["apparatus_sha256"].items():          # the frozen domain and rules cannot drift under the packet
        assert hashlib.sha256((HERE / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest() == sha, name
