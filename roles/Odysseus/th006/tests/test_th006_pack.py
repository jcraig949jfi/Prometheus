"""TH-006 verification pack: controls (written before the tool).

Synthetic specimens in BEE's births-row shape (20 fields) with probe
codeprov counts. The real specimen (r038751) is exercised by the node
check (tools/node_check.sh), not here: its replay output is 13 MB.
"""
import gzip
import json
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import th006_pack as P  # noqa: E402


def _specimen(n=2500, seed=1):
    rng = random.Random(seed)
    rows, cp = [], []
    for i in range(n):
        writes = rng.choice([0, 3, 10, 64, 64, 64])
        own = rng.randint(0, writes)
        byown = rng.randint(0, own)
        rows.append([i // 3, rng.randint(0, 99), 1000 + i, rng.choice(["pair", "exec"]),
                     round(rng.random(), 3), rng.choice([None, round(rng.random(), 3)]),
                     rng.choice(["writer", "target"]), writes, own, byown, rng.randint(0, 64),
                     rng.randint(0, 1), rng.randint(0, 3), rng.randint(0, 99), rng.randint(0, 99),
                     rng.randint(0, 9), rng.randint(0, 1), round(rng.random(), 3), rng.randint(0, 1),
                     rng.randint(0, 1)])
        a = rng.randint(0, writes)
        b = rng.randint(0, writes - a)
        c = rng.randint(0, writes - a - b)
        cp.append({"own_region": a, "self_copied": b, "foreign": c, "elsewhere": writes - a - b - c})
    return rows, cp


def _replay_file(tmp_path, rows, cp, name="out.json"):
    p = tmp_path / name
    body = {"births_rows": rows, "codeprov": cp}
    p.write_text(json.dumps({"rid": "rTEST", "births": len(rows),
                             "result_sha256": P.result_sha256(rows, cp), **body}))
    return p


def _pack(tmp_path, rows, cp):
    replay = _replay_file(tmp_path, rows, cp, "ref.json")
    pack = P.make_pack(str(replay), rid="rTEST", L=64)
    path = tmp_path / "pack.json"
    path.write_text(P.dump_pack(pack))
    return path, P.file_sha256(str(path))


def _verify(pack_path, pack_sha, replay_path):
    return P.verify(str(pack_path), str(replay_path), expected_pack_sha256=pack_sha)


@pytest.fixture
def spec(tmp_path):
    rows, cp = _specimen()
    pack_path, pack_sha = _pack(tmp_path, rows, cp)
    return rows, cp, pack_path, pack_sha


def _row_flipping_location(rows):
    # a row classified NO by location (foreign code wrote the majority) with writes > 0
    for i, r in enumerate(rows):
        if P.by_location(r) == "NO":
            return i
    raise AssertionError("specimen has no NO row")


def test_pack_is_small_ascii_and_self_describing(spec, tmp_path):
    rows, cp, pack_path, _ = spec
    text = pack_path.read_text()
    assert text.isascii()
    pack = json.loads(text)
    assert pack["schema"] == P.SCHEMA
    assert pack["source"]["row_count"] == len(rows)
    assert pack["claim"]["fields_used"] == [7, 8, 9, 11]
    assert len(pack["chunks"]["sha256"]) == (len(rows) + 999) // 1000
    assert len(text) < 20_000


def test_positive_control_honest_replay_passes(spec, tmp_path):
    rows, cp, pack_path, pack_sha = spec
    v = _verify(pack_path, pack_sha, _replay_file(tmp_path, rows, cp))
    assert v["verdict"] == "PASS", v
    assert v["identity"]["status"] == "PASS" and v["claim"]["status"] == "PASS"


def test_cheat_relevant_field_that_changes_the_claim(spec, tmp_path):
    rows, cp, pack_path, pack_sha = spec
    i = _row_flipping_location(rows)
    bad = [list(r) for r in rows]
    bad[i][9] = bad[i][7]  # by_own_code := writes -> location says YES
    v = _verify(pack_path, pack_sha, _replay_file(tmp_path, bad, cp))
    assert v["verdict"] == "FAIL"
    assert v["identity"]["status"] == "FAIL"
    assert v["identity"]["first_bad_row"] == i
    assert v["identity"]["fields_changed"] == [9]
    assert v["identity"]["claim_fields_changed"] == [9]
    assert v["claim"]["status"] == "FAIL"


def test_cheat_relevant_field_that_leaves_the_table_unchanged(spec, tmp_path):
    rows, cp, pack_path, pack_sha = spec
    # find a row where nudging field 8 by one does not move its classification
    for i, r in enumerate(rows):
        r2 = list(r)
        r2[8] = r[8] + 1
        if r[7] > 0 and P.by_location(r2) == P.by_location(r):
            break
    bad = [list(r) for r in rows]
    bad[i][8] += 1
    v = _verify(pack_path, pack_sha, _replay_file(tmp_path, bad, cp))
    # Explicit choice: identity protects every field, so this still FAILS,
    # and the report says the scientific table itself did not move.
    assert v["verdict"] == "FAIL"
    assert v["identity"]["claim_fields_changed"] == [8]
    assert v["claim"]["status"] == "PASS"


def test_cheat_irrelevant_field_fails_identity_but_is_labelled_outside_the_claim(spec, tmp_path):
    rows, cp, pack_path, pack_sha = spec
    bad = [list(r) for r in rows]
    bad[1234][0] += 1  # tick: not used by the claim
    v = _verify(pack_path, pack_sha, _replay_file(tmp_path, bad, cp))
    assert v["verdict"] == "FAIL"
    assert v["identity"]["fields_changed"] == [0]
    assert v["identity"]["claim_fields_changed"] == []
    assert v["claim"]["status"] == "PASS"


def test_cheat_codeprov_tamper_is_caught(spec, tmp_path):
    rows, cp, pack_path, pack_sha = spec
    i = next(k for k, r in enumerate(rows) if r[7] >= 10)
    bad = [dict(c) for c in cp]
    w = rows[i][7]
    bad[i] = {"own_region": 0, "self_copied": 0, "foreign": w, "elsewhere": 0}
    if bad[i] == cp[i]:
        bad[i] = {"own_region": w, "self_copied": 0, "foreign": 0, "elsewhere": 0}
    v = _verify(pack_path, pack_sha, _replay_file(tmp_path, rows, bad))
    assert v["verdict"] == "FAIL"
    assert v["codeprov"]["status"] == "FAIL"


@pytest.mark.parametrize("how", ["drop_last", "extra_row", "swap_two"])
def test_cheat_row_set_and_order(spec, tmp_path, how):
    rows, cp, pack_path, pack_sha = spec
    r2, c2 = [list(r) for r in rows], [dict(c) for c in cp]
    if how == "drop_last":
        r2.pop(); c2.pop()
    elif how == "extra_row":
        r2.append(list(r2[-1])); c2.append(dict(c2[-1]))
    else:
        r2[10], r2[11] = r2[11], r2[10]
        c2[10], c2[11] = c2[11], c2[10]
    v = _verify(pack_path, pack_sha, _replay_file(tmp_path, r2, c2))
    assert v["verdict"] == "FAIL"
    assert v["identity"]["status"] == "FAIL"


def test_cheat_tampered_pack_is_refused(spec, tmp_path):
    rows, cp, pack_path, pack_sha = spec
    pack = json.loads(pack_path.read_text())
    k = next(iter(pack["claim"]["table"]["location_vs_material"]))
    pack["claim"]["table"]["location_vs_material"][k] += 1
    pack_path.write_text(P.dump_pack(pack))
    v = _verify(pack_path, pack_sha, _replay_file(tmp_path, rows, cp))
    assert v["verdict"] == "FAIL"
    assert v["pack"]["status"] == "FAIL"


def test_attest_matches_the_source_log_it_was_predicted_from(spec, tmp_path):
    rows, cp, pack_path, _ = spec
    gz = tmp_path / "rTEST.jsonl.gz"
    with gzip.open(gz, "wt", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(json.dumps(r) + "\n" for r in rows))
    a = P.attest(str(pack_path), str(gz))
    assert a["status"] == "MATCH", a
    assert a["source_gz_sha256"] == P.file_sha256(str(gz))


def test_attest_catches_a_source_log_that_differs(spec, tmp_path):
    rows, cp, pack_path, _ = spec
    bad = [list(r) for r in rows]
    bad[77][14] += 1
    gz = tmp_path / "rTEST.jsonl.gz"
    with gzip.open(gz, "wt", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(json.dumps(r) + "\n" for r in bad))
    a = P.attest(str(pack_path), str(gz))
    assert a["status"] == "MISMATCH"
    assert a["first_bad_chunk"] == 0 and a["fields_changed"] == [14]


def test_by_location_agrees_with_the_archaeon_adapter_on_edge_rows():
    # The verifier reimplements the one rule it needs; the committed adapter is the definition.
    repo = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    sys.path.insert(0, repo)
    from archaeon.causal_lens import adapters_v02 as A2
    edge = []
    for writes in (0, 1, 2, 3, 4, 64):
        for own in range(writes + 1):
            for byown in range(own + 1):
                r = [0] * 20
                r[7], r[8], r[9] = writes, own, byown
                edge.append(r)
    for r in edge:
        assert P.by_location(r) == A2.bee_row(list(r), 64)["autonomy_write"], r
