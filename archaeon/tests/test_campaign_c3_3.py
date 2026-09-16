"""C3-3: declared regions, plan shape, and the pre-issue preflight (small, offline)."""
from archaeon.producer import campaign_c3_3 as C


def test_regions_are_declared_from_the_table_alone_and_cover_ten_deciles():
    assert len(C.REGION_EDGES) == C.N_REGIONS - 1 and C.REGION_EDGES == sorted(C.REGION_EDGES)
    assert 55 < C.REGION_EDGES[0] < 64 < C.REGION_EDGES[-1] < 73          # Binomial(128, 1/2) deciles straddle 64
    assert C.region_of("0" * 32) == "pc00" and C.region_of("f" * 32) == "pc09"
    regs = {C.region_of(C.random_rule_hex(j)) if hasattr(C, "random_rule_hex") else C.region_of(C.C3.random_rule(j)) for j in range(200)}
    assert len(regs) >= 8                                                   # random tables spread across the deciles


def test_plan_keeps_hist_base_null_and_sizes_the_acquisition_arm():
    rows = C.plan(130)
    arms = {}
    for r in rows:
        arms[r["arm_id"]] = arms.get(r["arm_id"], 0) + 1
    assert arms == {"C3-hist": 6, "C3-base": 6, "C3-null": 18, "C3-acq": 130}
    assert all(r["spec"]["work"]["payload"]["success_criterion"] == "cellwise_majority_match" for r in rows)
    assert all(r["spec"]["world"]["seed_root"] == C.SEED_ROOT for r in rows)      # paired with C3-2's IC samples
    assert all("region" in r and r["descriptors"]["popcount"] == C.popcount(r["rule_hex"]) for r in rows)
    assert len({r["request_key"] for r in rows}) == len(rows)


def test_preflight_prints_the_gates_before_any_gate_and_the_null_holds():
    pf = C.preflight(n_random=12, seed=0, band_reps=200)
    g = pf["gates_printed_before_any_gate"]
    # 2026-09-16: "regions_with_>=8_nondegenerate_expected" was an ASSERTED constant (Harmonia #255); the
    # computed keys replace it and the superseded key is named in the block
    assert set(g) >= {"R-C3-1 p_mode <= 0.50", "corpus_random_tables", "expected_nondegenerate_per_region",
                      "p_every_region_>=_8_at_corpus", "expected_neighbourhood_per_region", "neighbourhood_>=16_every_region",
                      "superseded_2026-09-16"}
    assert g["corpus_random_tables"] == C.CORPUS_OPTION_B and g["corpus_option"] == "B"
    r = pf["random"]
    assert r["support_size"] >= 2 and 0.40 < r["location_mean"] < 0.60 and r["f_nondegenerate"] > 0.9
    assert r["p_mode"] <= 0.5 and g["corpus_random_tables"] >= 120
    assert all(v["identical"] for v in pf["null_under_third_criterion"]["transforms"].values())
    # constants: per-IC match is 0 or 1 -> mean exactly 0.5, sd_across_ics at the 0/1 CEILING (~0.5), not zero
    # location = fraction of ICs whose majority equals the constant: Binomial noise around 0.5 at n_ic = 100
    assert abs(pf["named"]["all_zero"]["location"] - 0.5) < 0.15 and pf["named"]["all_zero"]["dispersion"] > 0.45
    assert pf["regions"]["expected_ratio_inside_band"] is True and pf["regions"]["expected_true_ratio"] == 1.0
    assert pf["random"]["dispersion_mean"] < 0.2                            # random tables: small dispersion
    assert pf["named"]["maj"]["location"] > 0.55                              # unmeasurable zero under the masks, measurable here
    assert "X1" in pf["h2_instrument"] or "Harmonia" in pf["h2_instrument"]
    # G5 is DERIVED from executed outputs and must reproduce Harmonia F3's three classes
    go = pf["go_predicate"]["items"]
    g5 = [v for k, v in go.items() if k.startswith("G5")][0]
    assert set(g5["value"]) == C.BASELINE_CLASSES_EXPECTED and g5["pass"]
    assert pf["h2_band_chance_floor"]["eligible_regions_only"]["reps"] == 200
    assert isinstance(pf["go_predicate"]["GO"], bool)


# --------------------------------------------------------------------------
# The computed region gate (Harmonia #255 section 3 and the GO predicate G1-G4)
# --------------------------------------------------------------------------
HARMONIA_MASSES = {"pc00": .1252, "pc01": .0880, "pc02": .1161, "pc03": .1355, "pc04": .0704,
                   "pc05": .0693, "pc06": .1274, "pc07": .1027, "pc08": .0731, "pc09": .0923}


def test_region_masses_are_exact_binomial_and_match_the_ruling_to_four_places():
    m = C.region_masses()
    assert abs(sum(m.values()) - 1.0) < 1e-12 and set(m) == set(HARMONIA_MASSES)
    for r, v in HARMONIA_MASSES.items():
        assert abs(m[r] - v) < 5e-5, (r, m[r], v)
    assert m["pc04"] < 0.075 and m["pc05"] < 0.075                          # popcounts 64 and 65 alone: the thin regions


def test_gate_is_computed_and_can_say_no_and_yes():
    m = C.region_masses()
    at120 = C.p_all_regions_ge(120, m)                                       # NEGATIVE: the declared corpus fails G2
    at180 = C.p_all_regions_ge(C.CORPUS_OPTION_B, m)                         # POSITIVE: option B passes G2
    assert 0.10 < at120 < 0.14 and at120 < C.G2_THRESHOLD                    # Harmonia MC 0.123 (4,000 corpora)
    assert 0.80 <= at180 < 0.86                                              # Harmonia MC 0.834
    assert C.min_corpus_for(C.G2_THRESHOLD, m) <= C.CORPUS_OPTION_B
    assert C.p_all_regions_ge(79, m) == 0.0 and C.p_all_regions_ge(600, m) > 0.99999
    # the OLD assumption (1/10 each) is measurably wrong at 120: even equal masses give only 0.39,
    # 3.3x the true 0.118 -- and the old code printed the gate as 10/10 regardless
    equal = {r: 0.1 for r in m}
    assert 0.38 < C.p_all_regions_ge(120, equal) < 0.40 and C.p_all_regions_ge(120, equal) > 3 * at120


def test_gate_cheat_control_a_starved_region_drives_the_probability_to_zero():
    m = C.region_masses()
    starved = dict(m); starved["pc05"] = 0.005
    tot = sum(starved.values()); starved = {r: v / tot for r, v in starved.items()}
    assert C.p_all_regions_ge(C.CORPUS_OPTION_B, starved) < 0.01
    # degeneracy is slack, never a region: f < 1 lowers the probability monotonically
    assert C.p_all_regions_ge(C.CORPUS_OPTION_B, m, f=0.5) < C.p_all_regions_ge(C.CORPUS_OPTION_B, m, f=0.9) < C.p_all_regions_ge(C.CORPUS_OPTION_B, m, f=1.0)


def test_exact_dp_agrees_with_monte_carlo_occupancies():
    import numpy as np
    m = C.region_masses(); names = sorted(m)
    rng = np.random.default_rng(3)
    occ = rng.multinomial(C.CORPUS_OPTION_B, [m[r] for r in names], size=20000)
    mc = float((occ >= C.MIN_REGION_N).all(axis=1).mean())
    assert abs(mc - C.p_all_regions_ge(C.CORPUS_OPTION_B, m)) < 0.012                     # 3 SE at n = 20,000


def test_neighbourhoods_come_from_the_masses_and_the_band_floor_is_seeded():
    m = C.region_masses()
    n = C.expected_neighbourhoods(180, m)
    assert all(abs(v - 180 * (1 - m[r])) < 1e-9 for r, v in n.items()) and min(n.values()) > 150
    a = C.band_chance_floor(180, m, reps=300, seed=5); b = C.band_chance_floor(180, m, reps=300, seed=5)
    assert a == b and a["reps"] == 300 and 0.0 <= a["p_any_region_outside"] <= 1.0
    # Harmonia's convention (every region with n >= 2) reproduces the ruling's 0.136 at 180 and ~0.38 at 120
    h180 = C.band_chance_floor(180, m, reps=2000, seed=7, min_n=2)["p_any_region_outside"]
    h120 = C.band_chance_floor(120, m, reps=2000, seed=7, min_n=2)["p_any_region_outside"]
    assert 0.10 < h180 < 0.17 and 0.33 < h120 < 0.45
