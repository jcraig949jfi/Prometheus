"""Regression tests for W2-46 ichecks.

Every check has (i) a REAL positive -- a committed Wave-2 / campaign case it must FLAG, (ii) a REAL negative -- a
committed case it must PASS (feedback rule: guards need real negative controls), (iii) a NOT_VERIFIED case, and
where useful a constructed edge case. Real inputs are read-only from roles/Nestor/ (holdout / secrets never touched).
Each check has a test that expects a DEFECT verdict and one that expects OK on real data, so no constant-verdict
stub can pass both.

Run from the W2-46_instrument_checks directory:  python -B -m pytest -q ichecks/tests
"""
import ast
import json
import pathlib

from ichecks import NOT_VERIFIED, OK
from ichecks._static import index_dirs
from ichecks.block_pooling import check_block_exchangeability
from ichecks.label_integrity import check_label_absorbing, check_label_readout_write_back
from ichecks.max_of_cached import check_max_amplification, scan_max_of_cached, single_draw_tail
from ichecks.readout_pairing import check_readout_pairing, check_record_key_pairing
from ichecks.ruler_match import check_ruler_agreement, load_function, world_member_rule
from ichecks.screen_context import check_screen_context, screen_contexts, world_carries_registers
from ichecks.single_seed import check_certificate_seeds
from ichecks.stores_genomes import check_stores_genomes, load_records

HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parents[2]                                  # inference_saturation_wave2/
NESTOR = W2.parent
CAMP = NESTOR / "campaigns"
WORLD = CAMP / "z80atlas-verify-2026-09-22"
C9X = CAMP / "c9x-explore-2026-09-24"
FRONT = CAMP / "npe-frontier-2026-09-30"
ROOTS = [CAMP]
IDX = index_dirs(ROOTS)

assert "holdout" not in str(W2).lower()


def _jsonl(p):
    return [json.loads(l) for l in pathlib.Path(p).read_text().splitlines() if l.strip()]


# ===================================================================== (a) screen context
def test_world_carries_registers_real():
    assert world_carries_registers(WORLD / "world.py") is True


def test_screen_context_flags_xmat_zero_screen():
    # REAL POSITIVE: X-MAT-INTERNALIZE's "competent"/state-free screens (run_de.competent -> run_dd.assay_one with
    # fresh=(None,0,0); run_fair ENTRY constants) -- the N13 / W2-34 / W2-38 zero-screen-in-carried-world family.
    r = check_screen_context(FRONT / "x_mat_internalize" / "run_xmi.py", WORLD, ROOTS, _index=IDX)
    assert r.verdict == "CONTEXT_MISMATCH", r.details
    files = {pathlib.Path(c["file"]).name for c in r.details["contexts"]}
    assert "run_dd.py" in files and "CARRIED" not in r.details["kinds"]


def test_screen_context_flags_x_acquire():
    # REAL POSITIVE 2: X-ACQUIRE screens the founder with fresh registers only (run_xa.py:53).
    assert check_screen_context(C9X / "x_acquire" / "run_xa.py", WORLD, ROOTS, _index=IDX).verdict == "CONTEXT_MISMATCH"


def test_screen_context_passes_x_stall_carried():
    # REAL NEGATIVE: X-STALL re-assays with the partner's observed registers (pst = p.regs ...).
    r = check_screen_context(C9X / "x_stall" / "run_st.py", WORLD, ROOTS, _index=IDX)
    assert r.verdict == OK and r.details["kinds"] == ["CARRIED"]


def test_screen_context_passes_w2_38_rescreen():
    # REAL NEGATIVE 2: W2-38's carried-context rescreen (the Wave-2 repair of the zero screen).
    r = check_screen_context(W2 / "W2-38_replay_dumps" / "rescreen.py", WORLD, ROOTS + [W2], _index=IDX)
    assert r.verdict == OK, r.details


def test_screen_context_x_state_mixed_is_ok_and_wrapper_not_counted():
    # X-STATE compares observed (forwarded world kwargs) vs fresh: a deliberate comparison -> OK, and the capturing
    # wrapper's `real_assay(z8m, **kw)` must NOT be counted as a carried screen.
    r = check_screen_context(C9X / "x_state" / "run_st.py", WORLD, ROOTS, _index=IDX)
    assert r.verdict == OK and set(r.details["kinds"]) == {"CARRIED", "ZERO"}
    assert all(c["line"] != 43 for c in r.details["contexts"])


def test_screen_context_not_verified_without_screen():
    # X-TICKET calls no screen: the check cannot look.
    assert check_screen_context(C9X / "x_ticket" / "run_tk.py", WORLD, ROOTS, _index=IDX).verdict == NOT_VERIFIED


def test_screen_context_world_that_resets(tmp_path):
    w = tmp_path / "w"
    w.mkdir()
    (w / "world.py").write_text("class R:\n    def step(self, o, ctx):\n        o.regs = None\n")
    s = tmp_path / "s.py"
    s.write_text("import p11\np11.assay(1, st_a=(None, 0, 0), st_b=(None, 0, 0))\n")
    assert check_screen_context(s, w, [tmp_path]).verdict == OK


def test_screen_context_unknown_param_is_not_verified():
    tree = ast.parse("def f(sa):\n    p11.assay(1, st_a=sa, st_b=sa)\n")
    assert {c["kind"] for c in screen_contexts(tree, "x")} == {"UNKNOWN"}


# ===================================================================== (c) label integrity
def test_label_write_back_flags_x_ticket_base():
    # REAL POSITIVE: X-TICKET counts anc == 0 / causal-set membership in a BASE world.Runner (W2-35: its
    # lineage-loss wording is affected by the BASE label leak).
    r = check_label_readout_write_back(C9X / "x_ticket" / "run_tk.py", ROOTS, WORLD, _index=IDX)
    assert r.verdict == "LABEL_READOUT_IN_BASE"


def test_label_write_back_passes_c_core_atomic():
    # REAL NEGATIVE: C-CORE reads anc0_share under the ATOMIC runner_cls (W2-35: ATOMIC label verdicts immune).
    r = check_label_readout_write_back(C9X / "c_core" / "run_ck.py", ROOTS, WORLD, _index=IDX)
    assert r.verdict == OK and r.details["label_readouts"] and not r.details["write_back"]["BASE"]


def test_label_write_back_flags_x_runaway_descendant_share():
    # REAL POSITIVE 2: X-RUNAWAY's causal_descendant_share (W2-35: "70-97%" is a lower bound) in BASE.
    assert check_label_readout_write_back(C9X / "x_runaway" / "run_rw.py", ROOTS, WORLD,
                                          _index=IDX).verdict == "LABEL_READOUT_IN_BASE"


def test_label_write_back_not_verified_without_runner(tmp_path):
    s = tmp_path / "s.py"
    s.write_text("x = [o for o in orgs if o.anc == 0]\n")
    assert check_label_readout_write_back(s, [tmp_path], None).verdict == NOT_VERIFIED


def _ca3_series():
    out = {}
    for p in sorted((CAMP / "npe-arc3-2026-09-28" / "c_a3_internalize" / "results").glob("*.json")):
        r = json.loads(p.read_text())
        out[p.stem] = [c["L_share"] for c in sorted(r["checkpoints"], key=lambda c: c["epoch"])]
    return out


def test_label_absorbing_flags_c_a3():
    # REAL POSITIVE: W2-34 -- 11 C-A3 runs reach L = 1.0 and 0/11 ever drop, closed 256-site tape.
    r = check_label_absorbing(_ca3_series(), closed_population=True)
    assert r.verdict == "ABSORBED_LABEL"
    assert len(r.details["reached_full"]) == 11 and r.details["dropped_after_full"] == []


def test_label_absorbing_passes_run_that_never_saturates():
    # REAL NEGATIVE: 7ae3 27000009 (L 0.58-0.78; W2-34 Q2): non-L writers remain, persistence is informative.
    s = _ca3_series()
    r = check_label_absorbing({"7ae3_27000009": s["7ae3_27000009"]}, closed_population=True)
    assert r.verdict == OK and not r.details["reached_full"]


def test_label_absorbing_drop_refutes_premise_and_unknown_closure():
    assert check_label_absorbing({"a": [0.5, 1.0, 0.9]}, True).verdict == OK
    assert check_label_absorbing({"a": [1.0, 1.0]}, None).verdict == NOT_VERIFIED


# ===================================================================== (d) max of cached
def test_max_scan_flags_h1r():
    # REAL POSITIVE: C9-H1R reads held_max_final (W2-19).
    r = scan_max_of_cached(C9X / "c9_h1r" / "run_h1r.py", ROOTS, WORLD, _index=IDX)
    assert r.verdict == "MAX_OF_CACHED" and r.details["world_caches_scores"] is True


def test_max_scan_passes_x_ticket():
    # REAL NEGATIVE: X-TICKET reads max_causal_replication_depth -- a deterministic world count, not a cached score.
    assert scan_max_of_cached(C9X / "x_ticket" / "run_tk.py", ROOTS, WORLD, _index=IDX).verdict == OK


def test_max_amplification_reproduces_w2_19():
    # REAL POSITIVE: recorded held 1.0 (12/12 answer-before-read crossings), k = 6 episodes, guesser p0 = 0.5,
    # N = 100 validation epochs. Must reproduce W2-19's analytic numbers exactly.
    ref = json.loads((W2 / "W2-19_rescore" / "rescore_h1.json").read_text())["analytic_single_draw_guesser"]
    r = check_max_amplification(1.0, k=6, n_draws=100)
    assert r.verdict == "MAX_AMPLIFIED"
    assert abs(r.details["P_single_draw"] - ref["P_held_eq_1.0_single_draw"]) < 1e-4
    assert abs(r.details["P_max_of_N"] - ref["P_any_cross_in_100_validation_epochs"]) < 1e-3


def test_max_amplification_passes_fresh_rescore():
    # REAL NEGATIVE: W2-19's cache-bypassed fresh score (0.4959, one draw) is not amplified.
    ref = json.loads((W2 / "W2-19_rescore" / "rescore_h1.json").read_text())["class_summary"]["ANSWER_BEFORE_READ"]
    assert check_max_amplification(ref["fresh_held_mean"], k=6, n_draws=1).verdict == OK


def test_max_amplification_extreme_even_as_max_and_not_verified():
    assert check_max_amplification(1.0, k=60, n_draws=100).verdict == OK     # 2^-60: genuinely extreme
    assert check_max_amplification(1.0, k=6, n_draws=0).verdict == NOT_VERIFIED
    assert abs(single_draw_tail(5 / 6, 6, 0.5) - 7 / 64) < 1e-12


# ===================================================================== (e) block pooling
def _w233():
    return json.loads((W2 / "W2-33_splice_on" / "stats.json").read_text())["tests"]


def _blocks(t):
    return {b: (h, n) for b, h, n in zip(t["blocks"], t["hits"], t["n"])}


def test_block_pooling_flags_w2_33_depth5():
    # REAL POSITIVE: W2-33 depth >= 5 across the four non-C9 splice-on blocks (recorded p_mc 0.0065); dropping
    # C-NORECOMB alone restores homogeneity.
    t = next(t for t in _w233() if t["thr"] == 5 and len(t["blocks"]) == 4)
    r = check_block_exchangeability(_blocks(t), n_mc=20000)
    assert r.verdict == "NON_EXCHANGEABLE"
    assert abs(r.details["chi2"] - t["chi2"]) < 0.01            # same statistic as W2-33
    assert r.details["p_mc"] < 0.02
    assert r.details["single_block_culprits"] == ["C-NORECOMB"]


def test_block_pooling_passes_w2_33_depth1():
    # REAL NEGATIVE: the same five blocks at depth >= 1 (recorded p_mc 0.47).
    t = next(t for t in _w233() if t["thr"] == 1 and len(t["blocks"]) == 5)
    r = check_block_exchangeability(_blocks(t), n_mc=20000)
    assert r.verdict == OK and abs(r.details["p_mc"] - t["p_mc"]) < 0.03


def test_block_pooling_not_verified():
    assert check_block_exchangeability({"a": (1, 10)}).verdict == NOT_VERIFIED
    assert check_block_exchangeability({"a": (0, 10), "b": (0, 12)}).verdict == NOT_VERIFIED


# ===================================================================== (f) single-seed certificates
def _w216_units():
    rows = json.loads((W2 / "W2-16_side1_heredity" / "s3_victim_controls.json").read_text())
    return {r["key"]: {"record": r["record_cvtr"], "reseeds": r["RESEED_accept"]} for r in rows}


def test_single_seed_flags_w2_16_cvtr():
    # REAL POSITIVE: W2-16 reseeded CVT-R 4x; q1_competent:19/:54 recorded FAIL pass 4/4; x_p2_bridge:5 recorded
    # PASS passes 0/4.
    r = check_certificate_seeds(_w216_units())
    assert r.verdict == "SEED_UNSTABLE"
    bad = {f["unit"] for f in r.findings}
    assert {"b:q1_competent:19", "b:q1_competent:54", "a:x_p2_bridge:5"} <= bad


def test_single_seed_flags_record_only():
    # REAL POSITIVE 2: the same 35 units as CVT-R originally reported them (record seed only).
    units = {k: {"record": v["record"], "reseeds": []} for k, v in _w216_units().items()}
    assert check_certificate_seeds(units).verdict == "SINGLE_SEED"


def test_single_seed_passes_w2_36_stable_rand_arm():
    # REAL NEGATIVE: W2-36 s2 controls, SF_7ae3 positives in the RAND arm: record PASS and 8/8 reseeds PASS.
    rows = json.loads((W2 / "W2-36_cvtr_audit" / "s2_controls.json").read_text())["rows"]
    units = {r["name"]: {"record": r["record_seed"]["CVTR"], "reseeds": [p["CVTR_accept"] for p in r["per_seed"][1:]]}
             for r in rows if r["arm"] == "RAND" and r["name"].startswith("SF_7ae3")}
    assert len(units) == 8
    assert check_certificate_seeds(units).verdict == OK


def test_single_seed_flags_w2_36_e700_2():
    rows = json.loads((W2 / "W2-36_cvtr_audit" / "s2_controls.json").read_text())["rows"]
    r = next(r for r in rows if r["name"] == "E700_2" and r["arm"] == "RAND")
    u = {"E700_2": {"record": r["record_seed"]["CVTR"], "reseeds": [p["CVTR_accept"] for p in r["per_seed"][1:]]}}
    assert check_certificate_seeds(u).verdict == "SEED_UNSTABLE"          # 5/8 reseeds: agreement 0.625


def test_single_seed_not_verified():
    assert check_certificate_seeds({}).verdict == NOT_VERIFIED
    assert check_certificate_seeds({"a": {"record": True, "reseeds": [True]}}).verdict == NOT_VERIFIED


# ===================================================================== (g) readout pairing
def _w214_model():
    return [r for r in _jsonl(W2 / "W2-14_F_calibration" / "ladder.jsonl")
            if (r["struct"], r["partner"], r["rule"]) == ("FIELD", "BANK", "ATOMIC")]


def _w222_world():
    return _jsonl(W2 / "W2-22_second_regime" / "runs_ATOMIC_world.jsonl")


def test_record_pairing_flags_w2_14_depth_f_vs_world2000():
    # REAL POSITIVE: W2-14's ATOMIC validation compared model depth_f (founder tree, 300 ep) with the world's
    # depth at 2000 epochs; W2-22 showed the matched readout depth_world exists on both sides.
    r = check_record_key_pairing(_w214_model(), "depth_f", _w222_world(), "world2000_depth")
    assert r.verdict == "UNLIKE_READOUTS"
    assert "depth_world" in r.details["matched_keys_available"]


def test_record_pairing_passes_w2_22_matched():
    # REAL NEGATIVE: W2-22's matched comparison (depth_world on both sides).
    assert check_record_key_pairing(_w214_model(), "depth_world", _w222_world(), "depth_world").verdict == OK


def test_spec_pairing_flags_per_call_vs_lifetime_m():
    # REAL POSITIVE (transcribed from W2-28 SYNTHESIS_WAVE2_ADDENDUM: per-call m ~ 1 vs lifetime m_c 0.77).
    per_call = {"quantity": "m", "unit": "births per interaction", "horizon": "one call", "estimator": "mean",
                "population": "founder vs realized partners"}
    lifetime = {"quantity": "m", "unit": "certified births per member", "horizon": "member lifetime",
                "estimator": "mean", "population": "founder vs realized partners"}
    r = check_readout_pairing(per_call, lifetime)
    assert r.verdict == "UNLIKE_READOUTS" and {d["field"] for d in r.findings} == {"unit", "horizon"}


def test_spec_pairing_flags_denominator_mismatch():
    # REAL POSITIVE 2 (W2-28 trace of W2-2's "1 vs 7.7"): expected from 320 runs, observed from the 192-run pool.
    a = dict(quantity="gap count", unit="runs", horizon="2000", estimator="count", population="f=1", denominator=320)
    b = dict(a, denominator=192)
    assert check_readout_pairing(a, b).verdict == "UNLIKE_READOUTS"


def test_spec_pairing_ok_and_not_verified():
    a = dict(quantity="depth", unit="causal depth", horizon=300, estimator="max", population="whole field")
    assert check_readout_pairing(a, dict(a)).verdict == OK
    assert check_readout_pairing({"quantity": "m"}, {"quantity": "m"}).verdict == NOT_VERIFIED
    assert check_record_key_pairing([], "x", [{"x": 1}], "x").verdict == NOT_VERIFIED
    assert check_record_key_pairing([{"y": 1}], "x", [{"x": 1}], "x").verdict == NOT_VERIFIED


# ===================================================================== (b) ruler match
def _w226_pairs():
    e = json.loads((W2 / "W2-26_switch_source" / "s2_switch_diffs.json").read_text())["edges"]
    return [(bytes.fromhex(x["Pg"]), bytes.fromhex(x["kE2"])) for x in e]


def test_world_member_rule_extracted_from_world():
    rule = world_member_rule(WORLD)
    assert rule is not None and rule.threshold == 0.9
    assert rule.fidelity(b"\x01\x02", b"\x01\x03") == 0.5


def test_ruler_flags_exact_identity_on_real_lineage_pairs():
    # REAL POSITIVE: W2-26's 605 real in-world (parent at birth, member at switch) genome pairs. The world keeps
    # drifted members (FID >= 0.90, no keep test); an exact-identity keep ruler drops them (W2-40 / W2-30).
    r = check_ruler_agreement(world_member_rule(WORLD), lambda a, b: a == b, _w226_pairs())
    assert r.verdict == "RULER_MISMATCH" and r.details["readout_drops_world_member"] > 100


def test_ruler_passes_p11_fidelity_readout():
    # REAL NEGATIVE: P-11's own fidelity readout (p11.fidelity, a separate committed function) at the world threshold.
    pf = load_function(WORLD / "p11.py", "fidelity")
    r = check_ruler_agreement(world_member_rule(WORLD), lambda a, b: pf(a, b) >= 0.9, _w226_pairs())
    assert r.verdict == OK and r.details["disagreement"] == 0


def test_ruler_not_verified():
    assert check_ruler_agreement(world_member_rule(WORLD), lambda a, b: True, []).verdict == NOT_VERIFIED

    def boom(a, b):
        raise ValueError("x")
    assert check_ruler_agreement(world_member_rule(WORLD), boom, [(b"a", b"a")]).verdict == NOT_VERIFIED


# ===================================================================== (h) stores genomes
def test_stores_genomes_flags_c_a3():
    # REAL POSITIVE: W2-34 -- no C-A3 run saved genomes.
    recs = load_records(sorted((CAMP / "npe-arc3-2026-09-28" / "c_a3_internalize" / "results").glob("*.json")))
    assert check_stores_genomes(recs, genome_len=64).verdict == "NO_GENOMES"


def test_stores_genomes_flags_h1r():
    # REAL POSITIVE 2: W2-19 -- C9-H1R saved 0 genomes.
    recs = load_records([C9X / "c9_h1r" / "RESULTS.json"])
    assert check_stores_genomes(recs, genome_len=64).verdict == "NO_GENOMES"


def test_stores_genomes_passes_w2_38_dump():
    # REAL NEGATIVE: W2-38's bit-exact replay with genome + register dumps.
    recs = load_records([W2 / "W2-38_replay_dumps" / "replay_ffa6_27000052.json.gz"])
    r = check_stores_genomes(recs, genome_len=64, require_registers=True)
    assert r.verdict == OK and r.details["n_register_sites"] > 0


def test_stores_genomes_sha_is_not_a_genome_and_not_verified():
    rec = [{"tag": "ab" * 32, "sha": "0123456789abcdef" * 4}]          # 32-byte hashes, L = 64
    assert check_stores_genomes(rec, genome_len=64).verdict == "NO_GENOMES"
    assert check_stores_genomes([{"g": "ab" * 64}], genome_len=64, require_registers=True).verdict == "NO_REGISTERS"
    assert check_stores_genomes([]).verdict == NOT_VERIFIED
