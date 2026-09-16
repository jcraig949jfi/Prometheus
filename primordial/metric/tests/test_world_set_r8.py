"""G-R8 world set: each test is aimed at one claim of LAUNCH_R8 s6-s8 / the G R8 build brief."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import numpy as np
import pytest

from primordial.metric import world_set_r8 as WS

ROOT = pathlib.Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def body():
    return WS.build_manifest()


def _all(body):
    return body["entries"] + body["duplicates"]


# --- the base and the measured distance-1 table (LAUNCH_R8 s6) ---------------------------------------------------

def test_base_is_w13_with_the_frozen_mechanism():
    g = WS.base_genome()
    assert (g.grammar_version, g.generation_seed, g.world_id) == ("wforge-grammar-0.1", 13, "Wf250db380cb2afd3")
    assert WS.summary(WS.expand(g)) == {
        "T": 32, "S": 1, "W": 1, "n": 32, "n_regs": 7, "lin_ops": 4, "corrupt_rate": 16, "obs_delay": 0,
        "horizon_class": "SHORT", "act_targets": [5], "yield_reg": 5, "yield_amt": 10, "start_charge": 191}
    assert WS.rule()["grammar_version"] == WS.GRAMMAR_VERSION == "wforge-grammar-0.1"


def _d1(op, s):
    base = WS.mechanism(WS.expand(WS.base_genome()))
    g = WS.mutate(WS.base_genome(), op, s)
    m = WS.mechanism(WS.expand(g))
    return g, m, {k for k in m if m[k] != base[k]}


def test_measured_distance_1_effects_reproduce():
    for s, amt in zip((1, 2, 3), (9, 8, 13)):
        _, m, ch = _d1("PARAM_PERTURB", s)
        assert ch == {"yield_amt"} and m["yield_amt"] == amt
    for s, tgt in zip((1, 2, 3, 4), (1, 2, 6, 3)):
        _, m, ch = _d1("REWIRE", s)
        assert ch == {"act_targets"} and m["act_targets"] == [tgt]
    for s in (1, 2, 3, 4):
        assert len(_d1("PRIMITIVE_INSERT", s)[1]["lin_ops"]) == 5
        assert len(_d1("PRIMITIVE_DELETE", s)[1]["lin_ops"]) == 3
    _, m, ch = _d1("BUDGET_MUTATE", 1)
    assert m["horizon"] == 64 and m["n"] == 64
    for s in (1, 2, 3, 4):
        _, m, ch = _d1("INTERFACE_MUTATE", s)
        assert ch == {"corrupt_rate", "obs_delay", "horizon_class"}
        assert (m["corrupt_rate"], m["obs_delay"], m["horizon_class"]) == (0, 2, "MEDIUM")


def test_silent_mutations_have_new_ids_but_the_base_mechanism():
    base = WS.base_genome()
    for op, s in (("PARAM_PERTURB", 4), ("BUDGET_MUTATE", 2), ("BUDGET_MUTATE", 3), ("BUDGET_MUTATE", 4)):
        g, _, ch = _d1(op, s)
        assert g.world_id != base.world_id and ch == set()
        assert WS.expand(g).manifest_hash() == WS.expand(base).manifest_hash()


# --- band rule (R13) --------------------------------------------------------------------------------------------------

def test_l1_is_exactly_one_single_axis_op_and_size_preserving(body):
    l1 = [e for e in _all(body) if e["band"] == "L1"]
    assert l1 and all(len(e["ops"]) == 1 and e["ops"][0] in WS.SINGLE_AXIS for e in l1)
    assert not any(o in WS.STRUCTURAL for e in l1 for o in e["ops"])
    assert all(e["label"] == "SINGLE_AXIS" and e["structural_ops"] == [] for e in l1)
    b = body["base"]["summary"]
    for e in l1:
        assert e["size_preserving"] and (e["summary"]["T"], e["summary"]["S"], e["summary"]["W"]) == (b["T"], b["S"], b["W"])


def _band_ok(band, ops):
    st = [o for o in ops if o in WS.STRUCTURAL]
    if band == "L2":
        return (len(ops) == 2 and not st) or (len(ops) == 1 and len(st) == 1)
    if band == "L3":
        return (len(ops) == 3 and not st) or (len(ops) == 2 and len(st) >= 1)
    return len(ops) == 1 and not st


def test_every_draw_obeys_its_band_and_structural_ops_are_always_labelled(body):
    ents = [e for e in _all(body) if e["stratum"] == "L"]
    assert {e["band"] for e in ents} == {"L1", "L2", "L3"}
    for e in ents:
        assert _band_ok(e["band"], e["ops"]), e
        st = [o for o in e["ops"] if o in WS.STRUCTURAL]
        assert e["structural_ops"] == st
        assert (e["label"] == "SINGLE_AXIS") == (not st) and all(o in e["label"] for o in st)
    # the templates admit exactly the rule, nothing more
    for band, tpl in WS.TEMPLATES.items():
        assert all(_band_ok(band, list(t)) for t in tpl) and len(set(tpl)) == len(tpl)
    assert len(WS.TEMPLATES["L2"]) == 16 + 2 and len(WS.TEMPLATES["L3"]) == 64 + 20
    assert {e["ops"][0] for e in ents if e["band"] == "L2" and len(e["ops"]) == 1} == set(WS.STRUCTURAL)


def test_op_seeds_come_from_the_frozen_pcg64_stream(body):
    for k, band in enumerate(WS.BANDS):
        rng = np.random.Generator(np.random.PCG64(20260924).jumped(k))
        draws = sorted((e for e in _all(body) if e["band"] == band), key=lambda e: e["draw_index"])
        assert [e["draw_index"] for e in draws] == list(range(WS.CAPACITY[band]))
        for e in draws:
            assert list(e["ops"]) == list(WS.TEMPLATES[band][e["draw_index"] % len(WS.TEMPLATES[band])])
            assert e["op_seeds"] == [int(x) for x in rng.integers(1, 1 << 31, size=len(e["ops"]))]
    l1_first = np.random.Generator(np.random.PCG64(20260924)).integers(1, 1 << 31)
    assert [e for e in _all(body) if e["band"] == "L1" and e["draw_index"] == 0][0]["op_seeds"] == [int(l1_first)]


def test_draws_are_prefix_stable_across_capacity():
    small = {b: WS.l_draws(b, 8) for b in WS.BANDS}
    for b in WS.BANDS:
        big = WS.l_draws(b, 20)
        assert [(d["world_id"], d["op_seeds"]) for d in big[:8]] == [(d["world_id"], d["op_seeds"]) for d in small[b]]


# --- mechanism-level dedup (mandatory) --------------------------------------------------------------------------------

def test_no_two_screenable_worlds_share_a_mechanism_and_none_is_the_base(body):
    hashes = [e["mech_hash"] for e in body["entries"]]
    assert len(hashes) == len(set(hashes)) and body["base"]["mech_hash"] not in hashes
    assert len(body["screen_order"]) == len(body["entries"]) == len(set(body["screen_order"]))
    assert {e["world_id"] for e in body["entries"]} == set(body["screen_order"])


def test_every_draw_is_accounted_for_and_every_duplicate_is_recorded_against_its_representative(body):
    for b in (*WS.BANDS, "B"):
        c = body["counts"][b]
        assert c["drawn"] == WS.CAPACITY[b] == c["kept"] + c["duplicates"]
    by_id = {e["world_id"]: e for e in body["entries"]}
    for d in body["duplicates"]:
        if d["duplicate_of_band"] == "BASE":
            assert d["duplicate_of"] == WS.BASE_WORLD_ID and d["mech_hash"] == body["base"]["mech_hash"]
            assert d["reason"] == "SILENT_MUTATION_EQUALS_BASE"
        else:
            rep = by_id[d["duplicate_of"]]
            assert rep["mech_hash"] == d["mech_hash"] and d["reason"] == "MECHANISM_IDENTICAL"
            assert (WS.BANDS + ("B",)).index(rep["band"]) <= (WS.BANDS + ("B",)).index(d["band"])
            if rep["band"] == d["band"]:
                assert (tuple(rep["op_seeds"]), rep["draw_index"]) < (tuple(d["op_seeds"]), d["draw_index"])
    assert body["counts"]["L1"]["duplicates"] > 0     # the phenomenon is present in the real draw, not only planted


def _planted(op, seeds, band="L1"):
    out = []
    for i, s in enumerate(seeds):
        g = WS.mutate(WS.base_genome(), op, s)
        out.append({"stratum": "L", "band": band, "draw_index": i, "ops": [op], "op_seeds": [s],
                    "world_id": g.world_id, "mech_hash": WS.expand(g).manifest_hash()})
    return out


def test_planted_silent_mutations_are_discarded_and_recorded_not_counted_twice():
    draws = {"L1": _planted("PARAM_PERTURB", [4, 1]), "L2": _planted("BUDGET_MUTATE", [4, 3, 2, 1], "L2")}
    kept, dups = WS.dedup(draws)
    assert [(e["band"], e["op_seeds"]) for e in kept] == [("L1", [1]), ("L2", [1])]
    assert sorted((d["band"], d["op_seeds"][0], d["reason"]) for d in dups) == [
        ("L1", 4, "SILENT_MUTATION_EQUALS_BASE"), ("L2", 2, "SILENT_MUTATION_EQUALS_BASE"),
        ("L2", 3, "SILENT_MUTATION_EQUALS_BASE"), ("L2", 4, "SILENT_MUTATION_EQUALS_BASE")]


def test_lowest_op_seed_is_kept_even_when_drawn_last():
    kept, dups = WS.dedup({"L2": _planted("INTERFACE_MUTATE", [9, 7, 3, 5], "L2")})
    assert [e["op_seeds"] for e in kept] == [[3]]
    assert sorted(d["op_seeds"][0] for d in dups) == [5, 7, 9]
    assert all(d["duplicate_of"] == kept[0]["world_id"] and d["reason"] == "MECHANISM_IDENTICAL" for d in dups)


def test_a_higher_band_collision_defers_to_the_lower_band():
    l1 = _planted("REWIRE", [1])
    g = WS.mutate(WS.mutate(WS.base_genome(), "PARAM_PERTURB", 4), "REWIRE", 1)   # silent step, then REWIRE 1
    l2 = [{"stratum": "L", "band": "L2", "draw_index": 0, "ops": ["PARAM_PERTURB", "REWIRE"], "op_seeds": [4, 1],
           "world_id": g.world_id, "mech_hash": WS.expand(g).manifest_hash()}]
    kept, dups = WS.dedup({"L1": l1, "L2": l2})
    assert [e["band"] for e in kept] == ["L1"] and dups[0]["duplicate_of_band"] == "L1"


# --- reproduction from the genome alone -------------------------------------------------------------------------------

def test_every_genome_alone_reproduces_its_world(body):
    for e in _all(body) + [body["base"]]:
        g = WS.genome_from_payload(json.loads(json.dumps(e["genome"])))
        assert g.world_id == e["world_id"] and WS.expand(g).manifest_hash() == e["mech_hash"]
        assert WS.expand(g).manifest_hash() == WS.expand(g).manifest_hash()
    for e in body["entries"]:
        if e["stratum"] == "L":
            assert e["lineage"][0] == WS.BASE_WORLD_ID and e["lineage"][-1] == e["world_id"]
            assert e["genome"]["parent_ids"] == [e["lineage"][-2]]
            assert [m["op"] for m in e["genome"]["mutation_history"]] == e["ops"]


def test_manifest_is_byte_deterministic():
    assert json.dumps(WS.build_manifest(), sort_keys=True) == json.dumps(WS.build_manifest(), sort_keys=True)


# --- stratum B (LAUNCH_R8 s7) -----------------------------------------------------------------------------------------

def test_stratum_b_is_fresh_untouched_seeds_with_frozen_ids(body):
    b = [e for e in _all(body) if e["band"] == "B"]
    assert [e["gen_seed"] for e in sorted(b, key=lambda e: e["draw_index"])] == [900000 + i for i in range(WS.CAPACITY["B"])]
    assert all(e["gen_seed"] >= 1000 and e["gen_seed"] not in WS.CONSUMED_GEN_SEEDS for e in b)
    for e in b:
        g = WS.de_novo("wforge-grammar-0.1", e["gen_seed"])
        assert g.world_id == e["world_id"] and e["genome"]["mutation_history"] == [] and e["ops"] == []


# --- sizing (R11): measure-then-size, no constant ---------------------------------------------------------------------

def test_screen_order_is_l1_first_template_balanced_then_interleaved(body):
    order, by_id = body["screen_order"], {e["world_id"]: e for e in body["entries"]}
    n_l1 = body["counts"]["L1"]["kept"]
    assert all(by_id[w]["band"] == "L1" for w in order[:n_l1]) and all(by_id[w]["band"] != "L1" for w in order[n_l1:])
    first = [tuple(by_id[w]["ops"]) for w in order[:WS.bootstrap_n()]]
    assert sorted(first) == sorted(WS.TEMPLATES["L1"])
    assert [by_id[w]["band"] for w in order[n_l1:n_l1 + 6]] == ["B", "L2", "L3", "B", "L2", "L3"]
    assert WS.screen_order(body) == order


def test_before_measurement_only_the_bootstrap_block_is_admitted(body):
    order = body["screen_order"]
    s = WS.size_next(order, {}, [], remaining_cpu_s=1e12)
    assert s["status"] == "BOOTSTRAP" and s["admit"] == order[:4] and s["est_cpu_s_per_world"] is None
    assert WS.size_next(order, {}, order[:3], remaining_cpu_s=1e12)["admit"] == order[3:4]


def test_size_follows_the_measurement_not_a_constant(body):
    order = body["screen_order"]
    cheap = WS.size_next(order, {w: 100.0 for w in order[:4]}, [], remaining_cpu_s=10_000.0)
    dear = WS.size_next(order, {w: 2_500.0 for w in order[:4]}, [], remaining_cpu_s=10_000.0)
    assert len(cheap["admit"]) == 100 and len(dear["admit"]) == 4
    assert cheap["est_cpu_s_per_world"] == 100.0 and dear["est_cpu_s_per_world"] == 2500.0
    inflight = WS.size_next(order, {w: 2_500.0 for w in order[:4]}, order[4:6], remaining_cpu_s=10_000.0)
    assert len(inflight["admit"]) == 2 and inflight["admit"] == order[6:8]
    for s in (cheap, dear, inflight):
        assert s["est_cpu_s_per_world"] * (len(s["admit"]) + s["in_flight"]) <= s["remaining_cpu_s"]
        cut = [w for w in order if w not in s["admit"] and w not in order[:6]]
        assert {r["world_id"] for r in s["why_not_run"]} >= set(cut)
        assert all(r["record"] == "WHY_NOT_RUN" and r["projection"]["cpu_s_needed_through_this_world"] > s["remaining_cpu_s"]
                   for r in s["why_not_run"])


def test_no_planning_constant_is_written_into_the_module():
    src = (ROOT / "primordial" / "metric" / "world_set_r8.py").read_text()
    for token in ("2222", "2,222", "612.22", "2671", "313200", "313,200"):
        assert token not in src


# --- generation is separately gated (ADAPT-6) -------------------------------------------------------------------------

def test_freezing_needs_no_bus_fabric_or_screen_code_and_never_overwrites(tmp_path):
    out = tmp_path / "manifest.json"
    code = ("import sys, json; from primordial.metric import world_set_r8 as WS; "
            f"WS.freeze_manifest(r'{out}', capacity={{'L1': 8, 'L2': 18, 'L3': 84, 'B': 4}}); "
            "bad = [m for m in sys.modules if m.startswith(('primordial.bus', 'primordial.fabric', 'redis', "
            "'primordial.metric.screen', 'primordial.metric.r16', 'primordial.ops'))]; print(json.dumps(bad))")
    p = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True,
                       env={**__import__("os").environ, "PYTHONPATH": str(ROOT)})
    assert p.returncode == 0, p.stderr
    assert json.loads(p.stdout.strip().splitlines()[-1]) == []
    assert WS.verify_manifest(out) == []
    with pytest.raises(FileExistsError, match="MANIFEST_ALREADY_FROZEN"):
        WS.freeze_manifest(out)


def test_verify_catches_a_tampered_manifest(tmp_path):
    out = tmp_path / "m.json"
    WS.freeze_manifest(out, capacity={"L1": 4, "L2": 18, "L3": 84, "B": 2})
    doc = json.loads(out.read_text())
    doc["body"]["entries"][0]["genome"]["mutation_history"][0]["op_seed"] += 1
    out.write_text(json.dumps(doc))
    bad = WS.verify_manifest(out)
    assert "BODY_SHA_MISMATCH" in bad and "REGENERATION_DIFFERS" in bad
    assert any(b.startswith("GENOME_DOES_NOT_REPRODUCE") for b in bad)


# --- reproduction anchors (G-R8-2) ------------------------------------------------------------------------------------

def test_wforge_pin_is_the_committed_blob_not_the_hosts_line_endings(tmp_path, body):
    for name, pin in body["wforge_sha256"].items():
        blob = subprocess.run(["git", "show", f"HEAD:SerendipityFoundry/worldfoundry/wforge/{name}"], cwd=ROOT,
                              capture_output=True).stdout
        assert blob and pin == __import__("hashlib").sha256(blob).hexdigest()
        lf, crlf = tmp_path / f"lf_{name}", tmp_path / f"crlf_{name}"
        lf.write_bytes(blob)
        crlf.write_bytes(blob.replace(b"\n", b"\r\n"))
        assert WS._file_sha(lf) == WS._file_sha(crlf) == pin


def test_cli_freeze_stamps_head_and_verify_rc_follows_the_file(tmp_path):
    out, env = tmp_path / "frozen.json", {**__import__("os").environ, "PYTHONPATH": str(ROOT)}
    cli = [sys.executable, "-m", "primordial.metric.world_set_r8"]
    f = subprocess.run(cli + ["freeze", str(out)], cwd=ROOT, capture_output=True, text=True, env=env)
    assert f.returncode == 0, f.stderr
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    doc = json.loads(out.read_text())
    assert doc["git_head"] == head and doc["frozen_at_utc"].endswith("Z") and doc["body"]["rule"]["capacity"] == WS.CAPACITY
    assert subprocess.run(cli + ["verify", str(out)], cwd=ROOT, capture_output=True, env=env).returncode == 0
    again = subprocess.run(cli + ["freeze", str(out)], cwd=ROOT, capture_output=True, text=True, env=env)
    assert again.returncode != 0 and "MANIFEST_ALREADY_FROZEN" in again.stderr
    doc["body"]["duplicates"] = doc["body"]["duplicates"][1:]            # "deleting an ugly world" is detected
    out.write_text(json.dumps(doc))
    assert subprocess.run(cli + ["verify", str(out)], cwd=ROOT, capture_output=True, env=env).returncode == 1
