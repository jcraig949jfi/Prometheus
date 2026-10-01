"""Each check: FAILS (returns its defect verdict) on a constructed defective input modelled on the
historical incident, PASSES (OK) on a correct input, and returns NOT_VERIFIED when it cannot look.

Run from the W2-5_error_autopsy directory:  python -B -m pytest -q checks/tests
"""
import random

from checks import NOT_VERIFIED, OK
from checks.identical_arms import detect_identical_arms
from checks.label_vs_content import check_label_vs_content
from checks.padding_inflation import check_padding_inflation
from checks.plugin_baseline import binom_sf, check_plugin_baseline, chi2_sf
from checks.rng_pairing import CountingRandom, check_rng_pairing
from checks.ruler_reachability import check_guard_sides_distinct, check_ruler_reachability
from checks.run_level_label import check_label_holds_for_unit
from checks.similarity_copy import check_similarity_detector
from checks.single_context import check_context_stability


# ---------------------------------------------------------------- identical arms (C9-D16)
def _h1_rows(wired: bool):
    rows = []
    for arm_i, arm in enumerate(["M0I0", "M1I0", "M0I1", "M1I1"]):
        for seed in range(20):
            r = random.Random(seed)            # common random numbers per seed
            base = r.random()
            effect = 0.1 * arm_i if wired else 0.0   # unwired: gate never reaches the task
            rows.append({"arm": arm, "seed": seed, "held": round(base + effect, 6),
                         "competence": round(base * 0.5 + effect, 6)})
    return rows


def test_identical_arms_fails_on_unwired_intervention():
    res = detect_identical_arms(_h1_rows(wired=False))
    assert res.verdict == "IDENTICAL_PER_SEED"
    assert len(res.findings) == 6          # all 4C2 pairs identical


def test_identical_arms_passes_when_wired():
    assert detect_identical_arms(_h1_rows(wired=True)).verdict == OK


def test_identical_arms_declared_pair_does_not_fire():
    rows = [r for r in _h1_rows(wired=False) if r["arm"] in ("M0I0", "M1I0")]
    res = detect_identical_arms(rows, declared_identical={("M0I0", "M1I0"): "cost-free cue: gate is a no-op by design"})
    assert res.verdict == OK and res.details["declared"]


def test_identical_arms_marginal_without_shared_seeds():
    rows = [{"arm": "A", "seed": s, "x": [0.2, 0.4, 0.3][s % 3]} for s in range(6)] + \
           [{"arm": "B", "seed": 100 + s, "x": [0.4, 0.3, 0.2][s % 3]} for s in range(6)]
    assert detect_identical_arms(rows).verdict == "IDENTICAL_MARGINAL"


def test_identical_arms_not_verified_single_arm():
    assert detect_identical_arms([{"arm": "A", "seed": 1, "x": 1.0}]).verdict == NOT_VERIFIED


# ---------------------------------------------------------------- RNG pairing (C9-D24)
L, N = 8, 6
IMPLANT = bytes(range(L))


def _setup_defective(arm, seed):
    rng = CountingRandom(seed)                       # ONE stream for implant + background
    if arm == "B_ACTUAL":
        org0 = IMPLANT                                # consumes 0 draws
    else:                                             # A in situ, C RANDOM_MATCHED: L draws
        org0 = bytes(rng.randrange(256) for _ in range(L))
    bg = [bytes(rng.randrange(256) for _ in range(L)) for _ in range(N - 1)]
    return {"background": bg, "treatment": org0, "draws": rng.draws}


def _setup_fixed(arm, seed):
    bg_rng = random.Random(seed)                      # background drawn FIRST, own stream
    bg = [bytes(bg_rng.randrange(256) for _ in range(L)) for _ in range(N - 1)]
    imp_rng = random.Random("%d-%s" % (seed, arm))   # per-arm implant stream
    org0 = IMPLANT if arm == "B_ACTUAL" else bytes(imp_rng.randrange(256) for _ in range(L))
    return {"background": bg, "treatment": org0}


def test_rng_pairing_fails_on_shifted_stream():
    res = check_rng_pairing(_setup_defective, ["A_INSITU", "B_ACTUAL", "C_RANDOM"], range(10))
    assert res.verdict == "UNPAIRED"
    pairs = {f["arms"] for f in res.findings}
    assert ("A_INSITU", "B_ACTUAL") in pairs and ("A_INSITU", "C_RANDOM") not in pairs
    assert res.details["same_simulation"] == [{"arms": ("A_INSITU", "C_RANDOM"), "seeds": 10}]


def test_rng_pairing_fails_on_same_simulation():
    res = check_rng_pairing(_setup_defective, ["A_INSITU", "C_RANDOM"], range(10))
    assert res.verdict == "SAME_SIMULATION"


def test_rng_pairing_passes_on_separated_streams():
    res = check_rng_pairing(_setup_fixed, ["A_INSITU", "B_ACTUAL", "C_RANDOM"], range(10))
    assert res.verdict == OK, res.findings


def test_rng_pairing_not_verified_on_error():
    def boom(arm, seed):
        raise KeyError("epoch")
    assert check_rng_pairing(boom, ["A", "B"], [1]).verdict == NOT_VERIFIED


def test_counting_random_counts():
    r = CountingRandom(1)
    r.randrange(256); r.random()
    assert r.draws >= 2


# ---------------------------------------------------------------- padding inflation (W12)
def _whole_slot_identity(p, c, core_len):        # defective: scores the padded tail too
    return sum(1 for a, b in zip(p, c) if a == b) / len(p)


def _core_identity(p, c, core_len):              # correct: scores the core span only
    return sum(1 for a, b in zip(p[:core_len], c[:core_len]) if a == b) / core_len


PARENT = bytes([0x21, 0x00, 0x40, 0x11, 0x00, 0x00, 0x01, 0x40, 0x00, 0xED, 0xB0, 0x18, 0xF2, 0x3E, 0x05, 0xC9])
CHILD = bytes([0x21, 0x00, 0x41, 0x11, 0x00, 0x07, 0x01, 0x40, 0x00, 0xED, 0xB1, 0x18, 0xF2, 0x3F, 0x05, 0xC9])


def test_padding_fails_on_whole_slot_identity():
    res = check_padding_inflation(_whole_slot_identity, PARENT, CHILD, L=64)
    assert res.verdict == "PADDING_INFLATED"
    assert res.details["mean_constant"] > 0.9 and res.details["mean_random"] < 0.3


def test_padding_passes_on_core_identity():
    assert check_padding_inflation(_core_identity, PARENT, CHILD, L=64).verdict == OK


def test_padding_not_verified_without_padding():
    assert check_padding_inflation(_core_identity, PARENT, CHILD, L=16).verdict == NOT_VERIFIED


# ---------------------------------------------------------------- run-level label (D U1)
def _establish_records(n_zero):
    recs = []
    for i in range(23):
        recs.append({"run": "s%d" % i, "label": "ESTABLISHED", "lineage_births": 0 if i < n_zero else 5 + i})
    recs += [{"run": "x%d" % i, "label": "NO_COPY", "lineage_births": 0} for i in range(18)]
    return recs


def test_run_label_fails_when_d0_never_copied():
    res = check_label_holds_for_unit(_establish_records(8), "label", "ESTABLISHED", "lineage_births")
    assert res.verdict == "LABEL_NOT_UNIT" and len(res.findings) == 8


def test_run_label_passes_when_unit_evidenced():
    assert check_label_holds_for_unit(_establish_records(0), "label", "ESTABLISHED",
                                      "lineage_births").verdict == OK


def test_run_label_not_verified_when_field_missing():
    recs = [{"run": "a", "label": "ESTABLISHED"}]
    assert check_label_holds_for_unit(recs, "label", "ESTABLISHED", "lineage_births").verdict == NOT_VERIFIED


# ---------------------------------------------------------------- label vs content (C9-D14, X-CONTENT)
FOUNDER = bytes(random.Random(7).randrange(256) for _ in range(64))


def _population(keep_frac, n=256, seed=3):
    rng = random.Random(seed)
    pop = []
    for _ in range(n):
        g = bytes(FOUNDER[i] if rng.random() < keep_frac else rng.randrange(256) for i in range(64))
        pop.append((True, g))                       # every member carries the founder LABEL
    return pop


def test_label_vs_content_fails_under_turnover():
    res = check_label_vs_content(_population(0.13), FOUNDER)
    assert res.verdict == "LABEL_EXCEEDS_CONTENT"
    assert 0.08 < res.details["mean_founder_byte_share"] < 0.2


def test_label_vs_content_passes_when_material_carried():
    assert check_label_vs_content(_population(0.95), FOUNDER).verdict == OK


def test_label_vs_content_not_verified_empty():
    assert check_label_vs_content([], FOUNDER).verdict == NOT_VERIFIED


# ---------------------------------------------------------------- ruler reachability (REDTEAM B4, #605/#631)
def _turnover_population(epochs, descended, seed):
    """Planted DESCENDED population under content turnover: identity to founder decays,
    provenance (tracked by construction) stays with the founder lineage."""
    rng = random.Random(seed)
    per_epoch = 0.006
    keep = (1 - per_epoch) ** epochs
    genomes = [bytes(FOUNDER[i] if rng.random() < keep else rng.randrange(256) for i in range(64))
               for _ in range(64)]
    return {"genomes": genomes, "provenance_share": 1.0 if descended else 0.0}


def _implant_identity_ruler(pop):                 # O_F: share of sites >= 0.9 identical to implant
    sites = [sum(a == b for a, b in zip(g, FOUNDER)) / 64 for g in pop["genomes"]]
    return sum(s >= 0.9 for s in sites) / len(sites) >= 0.5


def _provenance_ruler(pop):
    return pop["provenance_share"] >= 0.5


POS = [_turnover_population(500, True, s) for s in range(5)]
NEG = [_turnover_population(500, False, s) for s in range(5)]


def test_reachability_fails_on_decaying_identity_ruler():
    assert check_ruler_reachability(_implant_identity_ruler, POS, NEG).verdict == "UNREACHABLE"


def test_reachability_passes_on_provenance_ruler():
    assert check_ruler_reachability(_provenance_ruler, POS, NEG).verdict == OK


def test_reachability_fails_on_substring_release_guard():
    weak = lambda s: "HOLD" in s.upper() and "RELEASE" in s.upper()
    exact = lambda s: s.startswith("HOLD-RELEASE: ")
    positives = ["HOLD-RELEASE: SI01 freeze 3b2e11a3e"]
    negatives = ["HOLD stands; release criterion fixed", "not a release ... under the HOLD", "status"]
    assert check_ruler_reachability(weak, positives, negatives).verdict == "CANNOT_REFUSE"
    assert check_ruler_reachability(exact, positives, negatives).verdict == OK


def test_reachability_not_verified_without_planted_positive():
    assert check_ruler_reachability(_provenance_ruler, [], NEG).verdict == NOT_VERIFIED


def test_reachability_degenerate_constant_ruler():
    assert check_ruler_reachability(lambda x: True, ["a"], ["b"], min_pos_rate=1.0).verdict == "CANNOT_REFUSE"
    assert check_ruler_reachability(lambda x: False, ["a"], ["b"]).verdict == "UNREACHABLE"
    flip = lambda x: x == "b"
    assert check_ruler_reachability(flip, ["a"], ["b"]).verdict == "DEGENERATE"


def test_guard_sides():
    kw = {"law": "sum", "carrier": "empty"}
    assert check_guard_sides_distinct(kw, kw).verdict == "SELF_COMPARISON"
    assert check_guard_sides_distinct(dict(kw), dict(kw)).verdict == "SIDES_EQUAL"
    assert check_guard_sides_distinct(kw, dict(kw, law="max")).verdict == OK


# ---------------------------------------------------------------- single-context ruler (ARC3 RULER DEFECT)
def _rule(v, ref):
    return "ROBUST" if v >= 0.25 * ref else "POISONED"


def test_single_context_fails_on_cycling_state():
    cycling = lambda k: 1.0 if k in (0, 2, 5) else 0.0     # 16000006: copies after 0,2,5
    res = check_context_stability(cycling, list(range(1, 7)), _rule, reference_context=0, single_point=1)
    assert res.verdict == "CONTEXT_UNSTABLE"
    assert res.details["single_label"] == "POISONED"


def test_single_context_passes_on_stable_assay():
    stable = lambda k: 0.9 if k == 0 else 0.85
    assert check_context_stability(stable, list(range(1, 7)), _rule, 0, 1).verdict == OK


def test_single_context_not_verified_one_context():
    assert check_context_stability(lambda k: 1.0, [1], _rule, 0, 1).verdict == NOT_VERIFIED


# ---------------------------------------------------------------- similarity as copying (09-19, Z80A-D05)
def _fid(a, b):
    return sum(x == y for x, y in zip(a, b)) / len(a)


def similarity_only(donor, before, after, wrote):            # 09-19 rehearsal detector
    return _fid(donor, after) >= 0.9


def predecessor(donor, before, after, wrote):                # shipped pair criterion
    n = len(donor)
    return _fid(donor, after) >= 0.9 and _fid(before, after) < 0.9 and sum(wrote) >= n / 4


def authored(donor, before, after, wrote):                   # credit only bytes the donor wrote
    n = len(donor)
    return sum(1 for i in range(n) if wrote[i] and after[i] == donor[i]) / n >= 0.9


def test_similarity_detector_fails_similarity_only():
    res = check_similarity_detector(similarity_only)
    assert res.verdict == "FIRES_WITHOUT_WRITING"
    assert "converged_no_write" in res.reason and "splice_no_write" in res.reason


def test_similarity_detector_fails_predecessor_on_partial_overwrite():
    res = check_similarity_detector(predecessor)
    assert res.verdict == "FIRES_WITHOUT_WRITING" and res.reason.endswith("partial_overwrite")


def test_similarity_detector_passes_authored():
    assert check_similarity_detector(authored).verdict == OK


def test_similarity_detector_unreachable():
    assert check_similarity_detector(lambda *a: False).verdict == "UNREACHABLE"


# ---------------------------------------------------------------- plug-in baseline (D-12)
def test_stats_helpers():
    assert abs(chi2_sf(3.841, 1) - 0.05) < 1e-3
    assert abs(chi2_sf(5.991, 2) - 0.05) < 1e-3
    assert abs(chi2_sf(7.815, 3) - 0.05) < 1e-3
    assert abs(binom_sf(1, 10, 0.1) - (1 - 0.9 ** 10)) < 1e-12


def test_plugin_baseline_fails_on_small_arm_baseline():
    # k=1 arm drew low (5/80); the other doses are consistent with independent founders at p ~ 0.15
    counts = {1: (5, 80), 2: (22, 80), 4: (41, 80), 8: (58, 80)}
    res = check_plugin_baseline(counts, target_k=4)
    assert res.verdict == "PLUGIN_BASELINE_ARTIFACT", res.details
    assert res.details["p_plugin"] < 1e-4


def test_plugin_baseline_passes_on_true_superadditivity():
    counts = {1: (12, 80), 2: (22, 80), 4: (75, 80), 8: (79, 80)}
    res = check_plugin_baseline(counts, target_k=4)
    assert res.verdict == OK and res.details["p_joint_lrt"] < 0.05


def test_plugin_baseline_not_verified_without_k1():
    assert check_plugin_baseline({2: (1, 10), 4: (3, 10)}, 4).verdict == NOT_VERIFIED


def test_identical_summaries_fails_on_c9_h1_shape_and_passes_on_differing():
    from checks.identical_arms import detect_identical_summaries
    same = {a: {"held": 0.325, "crossed_ever": 0.2, "crossed_at_final": 0.05}
            for a in ["gate_off_cost_vm", "gate_on_cost_vm", "gate_off_cost_free", "gate_on_cost_free"]}
    assert detect_identical_summaries(same).verdict == "IDENTICAL_SUMMARY"
    diff = dict(same, gate_on_cost_vm={"held": 0.0, "crossed_ever": 0.0, "crossed_at_final": 0.0},
                gate_on_cost_free={"held": 0.31, "crossed_ever": 0.2, "crossed_at_final": 0.05},
                gate_off_cost_free={"held": 0.29, "crossed_ever": 0.15, "crossed_at_final": 0.05})
    assert detect_identical_summaries(diff).verdict == OK
