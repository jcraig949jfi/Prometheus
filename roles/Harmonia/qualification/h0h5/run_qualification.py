"""Run the H0-H5 qualification rules and the adversarial battery, and size the
lanes.  2026-09-08.  Writes ledgers/h0h5_qualification.json.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qualification_rules import (                                    # noqa: E402
    RULES_VERSION, LanePlan, PlanRefused, validate_plan, h0_estimands,
    required_blocks, min_attainable_p_paired, H4_ADAPTIVE_PROTOCOL,
    H4_PROTOCOL_VERSION)
from adversarial_fixtures import (                                   # noqa: E402
    FIXTURES_VERSION, run_battery, detect_f6)

OUT = {}
print("=" * 74)
print("H0-H5 QUALIFICATION  rules %s  fixtures %s" % (RULES_VERSION, FIXTURES_VERSION))
print("=" * 74)

# ------------------------------------------------------------- 1. battery
print("\n1. ADVERSARIAL FIXTURE BATTERY (no LLM verdict anywhere)\n")
bat = run_battery()
for r in bat:
    print("  [%s] %-22s defect=%s detected=%s"
          % ("PASS" if r["pass"] else "FAIL", r["fixture"],
             r["defect_present"], r["detected"]))
    for e in r["evidence"]:
        print("         %s" % e)
OUT["battery"] = bat
print("\n  battery: %d/%d" % (sum(r["pass"] for r in bat), len(bat)))

# F6 is a RATE, not a single run
print("\n  F6_no_effect_synthetic  (calibration: false-SUPPORT RATE, 8000 draws)")
print("  run at TWO thresholds -- a forced zero is not a passing control\n")
f6 = detect_f6(trials=8000, n_blocks=12, thresholds=(0.0, 0.05))
for k, v in f6.items():
    tag = "VACUOUS (threshold %.1f SE from 0)" % v["threshold_distance_in_se"] \
        if v["vacuous"] else "informative"
    exp = "  expect %.4f" % v["expected"] if v["expected"] else ""
    print("      %-42s %.4f%s   %s"
          % (k, v["false_support_rate"], exp, tag))
OUT["f6_false_support_rate"] = f6

# --------------------------------------------- 2. the sqrt(2) design fact
print("\n" + "=" * 74)
print("2. H0's TWO ESTIMANDS: THE INTERACTION IS UNDERPOWERED BY CONSTRUCTION")
print("=" * 74)
print("""
  Var(S11-S00) = 2 s^2 (1-rho)      coefficients ( 1, 0, 0,-1)
  Var(I)       = 4 s^2 (1-rho)      coefficients ( 1,-1,-1, 1)
  => SE(I) = sqrt(2) * SE(main), for ANY within-block correlation rho.
     rho cancels. Pairing does not rescue it.
""")
rng = random.Random(4242)
ratios = []
for _ in range(3000):
    blocks = []
    for _ in range(16):
        base = rng.uniform(.2, .6)
        blocks.append({c: base + rng.gauss(0, .05)
                       for c in ("S00", "S10", "S01", "S11")})
    g, i = h0_estimands(blocks)
    if g.se > 0:
        ratios.append(i.se / g.se)
obs = sum(ratios) / len(ratios)
print("  measured SE(I)/SE(main) over 3000 synthetic block sets : %.4f" % obs)
print("  predicted sqrt(2)                                      : %.4f" % math.sqrt(2))
OUT["se_ratio_interaction_over_main"] = {"measured": obs, "predicted": math.sqrt(2)}

# --------------------------------------- 3. is 5 pp decidable, and at what n
print("\n" + "=" * 74)
print("3. IS THE PROPOSED 5 pp THRESHOLD DECIDABLE? BLOCKS REQUIRED")
print("=" * 74)
print("""
  The operator's rule makes INCONCLUSIVE the default: a verdict needs the CI
  to clear the threshold on one side. So the block count is set by the
  threshold and the block-level SD, not by taste. Below: blocks needed for a
  CONCLUSIVE verdict, two primary contrasts (Bonferroni), alpha 0.05.
""")
rows = []
print("  block SD   contrast      true effect   blocks needed")
print("  --------   -----------   -----------   -------------")
for sd in (0.05, 0.10, 0.15, 0.20):
    for eff, lab in ((0.00, "0 pp (null)"), (0.15, "15 pp (real)")):
        n_main = required_blocks(sd, 0.05, n_primary=2, true_effect=eff)
        n_int = required_blocks(sd * math.sqrt(2), 0.05, n_primary=2, true_effect=eff)
        print("  %8.2f   main          %-11s   %s" % (sd, lab, n_main))
        print("  %8s   interaction   %-11s   %s" % ("", lab, n_int))
        rows.append({"block_sd": sd, "true_effect": eff,
                     "blocks_main": n_main, "blocks_interaction": n_int})
OUT["blocks_required"] = rows

# ------------------------------------------------------- 4. plan validation
print("\n" + "=" * 74)
print("4. PLAN VALIDATION -- refusals fire BEFORE any pilot data exists")
print("=" * 74)

good = LanePlan(
    lane="H0", plan_version="H0-plan-0.1.0",
    unit_definition="paired (seed x task_block)",
    n_blocks=16, assigned_tasks_per_block=24,
    denominator_rule="all_assigned_tasks",
    exclusion_rule="identical_across_arms:v1",
    retry_rule="identical_across_arms:v1",
    paired=True,
    primary_contrasts=["additive_gain_S11_minus_S00", "interaction_I"],
    practical_threshold=0.05, threshold_status="PROPOSED",
    uncertainty_procedure="paired-block t, Bonferroni over 2 primaries",
    multiplicity="BONFERRONI",
    pilot_task_ids=tuple(range(0, 100)),
    confirmation_task_ids=tuple(range(100, 300)))

checks = validate_plan(good)
print("\n  H0 reference plan ACCEPTED  digest %s" % good.digest()[:26])
for c in checks:
    print("      ok  %s" % c)
OUT["reference_plan"] = {"digest": good.digest(), "checks": checks}

print("\n  refusals, each raised mechanically:")
bad = []
b1 = LanePlan(**{**good.__dict__, "n_blocks": 4})
bad.append(("4 blocks", b1))
b2 = LanePlan(**{**good.__dict__, "multiplicity": "NONE"})
bad.append(("2 primaries, multiplicity NONE", b2))
b3 = LanePlan(**{**good.__dict__,
                 "confirmation_task_ids": tuple(range(50, 250))})
bad.append(("pilot/confirmation overlap", b3))
b4 = LanePlan(**{**good.__dict__, "unit_definition": "per candidate"})
bad.append(("unit = candidate", b4))
b5 = LanePlan(**{**good.__dict__, "denominator_rule": "completed_tasks"})
bad.append(("denominator = completed only", b5))
ref = []
for label, p in bad:
    try:
        validate_plan(p)
        print("      NOT REFUSED (defect!) : %s" % label)
        ref.append({"case": label, "refused": False})
    except PlanRefused as e:
        print("      REFUSED  %-32s %s" % (label, str(e)[:74]))
        ref.append({"case": label, "refused": True, "reason": str(e)})
OUT["refusals"] = ref

print("\n  minimum attainable two-sided p, paired sign-flip lattice:")
for n in (4, 5, 6, 8, 12, 16):
    print("      %2d blocks   %.5f   %s"
          % (n, min_attainable_p_paired(n),
             "eligible" if min_attainable_p_paired(n) <= 0.05 else "INELIGIBLE"))

# --------------------------------------------------------- 5. H4 protocol
print("\n" + "=" * 74)
print("5. H4 ADAPTIVE PROTOCOL  %s" % H4_PROTOCOL_VERSION)
print("=" * 74)
print("\n  HOW IT DIFFERS FROM M-SIGNAL")
print("    M-SIGNAL : %s" % H4_ADAPTIVE_PROTOCOL["distinct_from_m_signal"]["m_signal"])
print("    H4       : %s" % H4_ADAPTIVE_PROTOCOL["distinct_from_m_signal"]["h4"])
print("    =>         %s" % H4_ADAPTIVE_PROTOCOL["distinct_from_m_signal"]["consequence"])
print("\n  PROHIBITED ENDPOINT")
print("    %s" % H4_ADAPTIVE_PROTOCOL["endpoint_surface"]["PROHIBITED"])
OUT["h4_protocol"] = H4_ADAPTIVE_PROTOCOL

led = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ledgers")
os.makedirs(led, exist_ok=True)
with open(os.path.join(led, "h0h5_qualification.json"), "w") as f:
    json.dump(OUT, f, indent=2, default=str)
print("\nledger -> ledgers/h0h5_qualification.json")
