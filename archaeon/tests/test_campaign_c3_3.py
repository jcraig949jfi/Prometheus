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
    pf = C.preflight(n_random=12, seed=0)
    g = pf["gates_printed_before_any_gate"]
    assert set(g) >= {"R-C3-1 p_mode <= 0.50", "corpus_random_tables", "expected_nondegenerate_per_region",
                      "regions_with_>=8_nondegenerate_expected", "neighbourhood_>=16"}
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
