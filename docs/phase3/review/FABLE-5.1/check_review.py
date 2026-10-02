"""Checks on the three review responses. Every check can fail.

Run from the repository root:

    python docs/phase3/review/FABLE-5.1/check_review.py

What is checked:
  1. form: ASCII, LF, no tab, at most 80 columns, no code fence, for every
     response; ASCII and LF for the READMEs and preregistrations;
  2. quotes: every double-quoted string in a response appears verbatim
     (whitespace collapsed) in a saved input, or in one of my own files, or
     is on the short list of words I put in quotes myself;
  3. numbers: every figure quoted from the four runs, from the exploratory
     probes and from my prototype is recomputed from the receipts;
  4. preregistration: for each of the four runs, the code that produced the
     receipt is the code committed before the receipt existed; the probes
     ran on that code and on design seeds only;
  5. consistency: R0-R9 dispositions agree between RESPONSE_1 and RESPONSE_3;
     the section tally in RESPONSE_2's headline equals the count of its sheets;
     sentences withdrawn after review are gone;
  6. record: figures taken from my salvage matrix and requirements are in them.

Exit code 0 only if every check passes. It does not test whether the
arguments are right.
"""
import hashlib
import io
import json
import math
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
CF = HERE / "counterfeit"
ROOT = HERE.parents[3]
INPUTS = ROOT / "roles" / "Dionysus" / "prompts" / "2026-10-01_review_charter"
PKG = ROOT / "docs" / "phase3" / "design" / "FABLE-5.1"
P1 = PKG / "prototype" / "p1_slice"
RUNS = [  # script, receipt, preregistration commit
    ("gauntlet.py", "RECEIPT_gauntlet.json", "8dc9ef542"),
    ("gauntlet2.py", "RECEIPT_gauntlet2.json", "619472376"),
    ("gauntlet3.py", "RECEIPT_gauntlet3.json", "c6adb3a57"),
    ("keys.py", "RECEIPT_keys.json", "635b3cba1"),
]

R1 = HERE / "RESPONSE_1_REVIEW_REPORT.md"
R2 = HERE / "RESPONSE_2_RSO_WIND_TUNNEL_v0.1.md"
R3 = HERE / "RESPONSE_3_RACE_CAR_PORTFOLIO_R0-R9.md"
RESPONSES = [R1, R2, R3]

# Words and phrases I put in double quotes myself. Each is my own term or a
# single ordinary word used as a term; none is presented as a quotation.
OWN_QUOTED = {
    "recursive", "pays", "fresh", "interesting", "useful", "observatory", "plastic",
    "substrate-neutral", "in parallel", "operated correctly",
    "nested improvement, order k",
    "returned the registered answers on designed positives and impostors",
}

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print("%-4s %s%s" % ("PASS" if ok else "FAIL", name, (" -- " + detail) if detail else ""))


def text(path):
    return io.open(path, encoding="utf-8", newline="").read()


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def f1(x):
    return "%.1f" % x


def f2(x):
    return "%.2f" % x


def lf_sha(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


# ------------------------------------------------------------------ 1. form
form_files = sorted(HERE.glob("*.md")) + sorted(CF.glob("*.md"))
for p in form_files:
    raw = io.open(p, "rb").read()
    problems = []
    if b"\r" in raw:
        problems.append("CR present")
    if b"\t" in raw:
        problems.append("tab present")
    try:
        raw.decode("ascii")
    except UnicodeDecodeError:
        problems.append("non-ASCII")
    lines = raw.decode("utf-8", "replace").split("\n")
    wide = [i + 1 for i, l in enumerate(lines) if len(l) > 80]
    if p in RESPONSES and wide:
        problems.append("lines over 80: %s" % wide[:5])
    if p in RESPONSES and "```" in raw.decode("utf-8", "replace"):
        problems.append("code fence inside a paste block")
    check("form %s" % p.relative_to(HERE), not problems, "; ".join(problems))

# ---------------------------------------------------------------- 2. quotes
package_sources = [norm(text(p)) for p in sorted(INPUTS.glob("0[1-4]_*.md"))]
own_sources = [norm(text(p)) for p in (PKG / "SALVAGE_MATRIX.md", PKG / "REQUIREMENTS.md", P1 / "README.md")]
for p in RESPONSES:
    body = norm(text(p))
    quotes = re.findall(r'"([^"]+)"', body)
    missing, from_package, from_own, own_terms = [], 0, 0, 0
    for q in quotes:
        qn = norm(q)
        if any(qn in s for s in package_sources):
            from_package += 1
        elif qn in OWN_QUOTED:
            own_terms += 1
        elif any(qn in s for s in own_sources):
            from_own += 1
        else:
            missing.append(qn[:70])
    check("quotes %s" % p.name, body.count('"') % 2 == 0 and not missing,
          "%d quoted: %d in the package, %d in my files, %d my own terms%s" % (
              len(quotes), from_package, from_own, own_terms,
              ("; NOT FOUND: %s" % missing) if missing else ""))

# --------------------------------------------------------------- 3. numbers
r1, r2, r3 = text(R1), text(R2), text(R3)
n1, n2, n3 = norm(r1), norm(r2), norm(r3)
cf_readme = text(CF / "README.md")
ncf = norm(cf_readme)
top_readme = norm(text(HERE / "00_README.md"))
rec = {name: json.loads(text(CF / name)) for _, name, _ in RUNS}
g1, g2, g3, keys = (rec[name] for _, name, _ in RUNS)
seeds = {"RECEIPT_gauntlet.json": 2026100121, "RECEIPT_gauntlet2.json": 2026100123,
         "RECEIPT_gauntlet3.json": 2026100124, "RECEIPT_keys.json": 2026100122}
check("all four receipts: gate PASS on the registered seeds",
      all(rec[n]["gate"] == "PASS" and rec[n]["matches_expectation"] is True
          and rec[n]["params"]["seed_base"] == seeds[n] for n in seeds))

# run 1
def arm(org, target, name):
    a = g1["result"]["protocol"][org][target][name]
    return f2(a["errors_total"] / a["tasks_total"])


pairs = [("STATIC", "SHIFT", "8.12", "8.12"), ("MATURATION", "SHIFT", "8.07", "1.00"),
         ("GEARBOX", "SHIFT", "8.04", "1.00"), ("GEARBOX", "SCALE", "8.66", "1.00"),
         ("BUILDER", "AFFINE", "11.26", "1.94")]
check("run 1: naive -> developed figures in the counterfeit README",
      all((arm(o, t, "naive"), arm(o, t, "intact")) == (a, b) and ("%s -> %s" % (a, b)) in cf_readme
          for o, t, a, b in pairs)
      and arm("GEARBOX", "SHIFT", "irrelevant_history") == "11.28" and "11.28" in cf_readme
      and arm("GEARBOX", "SCALE", "irrelevant_history") == "11.93" and "11.93" in cf_readme)
sweep = json.loads(text(CF / "RECEIPT_gauntlet_sweep_exploratory.json"))["cases"]
costs = [(sweep[k]["tasks_to_an_acceptable_U_naive"], sweep[k]["tasks_to_an_acceptable_U_developed"])
         for k in ("GEARBOX SHIFT", "GEARBOX SCALE", "BUILDER AFFINE")]
windows = [sweep[k]["budgets_that_pass"] for k in ("GEARBOX SHIFT", "GEARBOX SCALE", "BUILDER AFFINE")]
check("run 1: budget windows and task counts (exploratory sweep)",
      costs == [(2, 1), (3, 1), (8, 4)] and windows == [[1], [1, 2], [4, 5, 6, 7]]
      and "2 against 1, 3 against 1 and 8 against 4" in n1, "%s %s" % (costs, windows))
n_templates = g2["params"]["candidate_templates"]
n_parts = len(g2["params"]["canonical_parts"])
check("developed state, two measures: 2.6, 5 and 37.5 bits of capacity; 11.6 bits selected by experience",
      f1(math.log2(6)) == "2.6" and g3["params"]["K"] == 32 and n_templates == 660 and n_parts == 9
      and f1(4 * math.log2(n_templates)) == "37.5" and f1(math.log2(9 * 8 * 7 * 6)) == "11.6"
      and all(x in n1 and x in ncf for x in ("2.6 bits", "5 bits", "37.5 bits", "11.6 bits")))

# run 2
b = g2["cells"]["BUILDER"]
m = b["medians"]
want2 = {"naive_B": "313.5", "dev_B": "20.5", "naive_D": "334.0", "dev_D": "19.0", "naive_E": "346.5",
         "dev_E": "20.0", "lifecycle_naive": "1045.5", "lifecycle_developed": "171.0", "lesion_B": "316.0",
         "sham_B": "12.0", "rescue_B": "16.0", "v_donor_B": "22.0", "wrong_history_B": "323.5",
         "random_library_B": "323.5"}
bad = [k for k, v in want2.items() if f1(m[k]) != v or v not in r1 or v not in cf_readme]
check("run 2: BUILDER medians in RESPONSE_1 and the counterfeit README equal the receipt", not bad, "%s" % bad)
check("run 2: BUILDER passes with every conjunct true in 24 of 24",
      b["verdict"] == "PASS" and set(b["counts"].values()) == {24} and f2(m["q_C_same_kind"]) == "2.00"
      and b["cheaper_than_naive_on_one_target_alone"] == 24)
fire = {"SELECTOR": "SAVINGS", "STATIC": "SAVINGS", "WASTEFUL": "LIFECYCLE", "HIDDEN": "NESTING",
        "BADSHAM": "NESTING", "MATURATION": "PROVENANCE", "MEMORISER": "SAVINGS", "OFFHISTORY": "REPEAT"}
check("run 2: the selector and seven fire tests each FAIL on the intended conjunct, at 0 of 24",
      all(g2["cells"][c]["verdict"] == "FAIL" and g2["cells"][c]["counts"][j] == 0 for c, j in fire.items())
      and g2["cells"]["MEMORISER"]["savings_if_content_reset_skipped"] == 24)
several = sorted(c for c in fire if c != "SELECTOR" and len(g2["cells"][c]["failing"]) > 1)
check("run 2: three of the seven fire tests fail more than one conjunct (STATIC and MEMORISER five, HIDDEN two)",
      several == ["HIDDEN", "MEMORISER", "STATIC"] and len(g2["cells"]["HIDDEN"]["failing"]) == 2
      and len(g2["cells"]["STATIC"]["failing"]) == len(g2["cells"]["MEMORISER"]["failing"]) == 5
      and "three fail others too" in n1, "%s" % several)
check("run 2: RESPONSE_3 quotes 313.5 and 20.5", "313.5" in r3 and "20.5" in r3)

# run 3
s = g3["cells"]["STRATEGIST"]
m = s["medians"]
want3 = {"naive_B": "398.0", "dev_B": "57.0", "naive_D": "356.0", "dev_D": "44.5", "naive_E": "362.0",
         "dev_E": "42.0", "lifecycle_naive": "1097.5", "lifecycle_developed": "424.0", "lesion_B": "398.0",
         "sham_B": "57.0", "irrelevant_history_B": "398.0", "random_V_B": "486.5"}
bad = [k for k, v in want3.items() if f1(m[k]) != v or v not in r1 or v not in cf_readme]
check("run 3: STRATEGIST medians in RESPONSE_1 and the counterfeit README equal the receipt", not bad, "%s" % bad)
c3 = s["counts"]
check("run 3: STRATEGIST passes, five conjuncts at 24 and provenance at 23",
      s["verdict"] == "PASS" and c3["PROVENANCE"] == 23
      and all(c3[k] == 24 for k in c3 if k != "PROVENANCE"))
lb = g3["cells"]["BUILDER"]
check("run 3: the library learner fails, savings 0 of 24, 353.0 against 354.0",
      lb["verdict"] == "FAIL" and lb["counts"]["SAVINGS"] == 0 and f1(lb["medians"]["dev_B"]) == "353.0"
      and f1(lb["medians"]["naive_B"]) == "354.0" and "353.0 tasks against 354.0" in n1
      and g3["cells"]["STATIC"]["counts"]["SAVINGS"] == 0 and g3["cells"]["EAGER"]["counts"]["PROVENANCE"] == 0)

# run 4
rows_k = [("ELIM (carries nothing)", "ELIM"), ("SELECTOR (64 inherited)", "SELECTOR(64)"),
          ("ACQUIRER of 4 symbols", "ACQUIRER(4)"), ("ACQUIRER of 8 symbols", "ACQUIRER(8)"),
          ("ACQUIRER of 12 symbols", "ACQUIRER(12)"), ("ACQUIRER of 16 symbols", "ACQUIRER(16)")]
ok, detail = True, []
for label, cell in rows_k:
    c = keys["cells"][cell]
    got = re.search(r"^\s+%s\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s*$" % re.escape(label), r1, flags=re.M)
    want = (f2(c["later_family_mean_correct"]), f2(c["certified_bits_carried"]))
    if got is None or got.groups() != want:
        ok = False
        detail.append("%s: text %s receipt %s" % (label, got.groups() if got else None, want))
check("run 4: table in RESPONSE_1 equals the receipt", ok, "; ".join(detail))
ka = keys["known_answers"]
check("run 4: figures quoted in RESPONSE_1",
      f2(keys["params"]["selection_bound_bits"]) == "11.49" and "11.49" in r1
      and f2(keys["params"]["exact_nothing_carried_bound"]) == "3.38" and "3.38 correct" in r1
      and f2(ka["ACQUIRER(8)"]["stored_key_bits"]) == "24.95" and "24.95" in r1
      and keys["params"]["LIVES"] == 2000 and all(v["ok"] for v in ka.values())
      and all(keys["fire_tests"][k] for k in ("A_ruler_fooled_when_world_check_skipped",
                                              "C_power_gate_refuses_at_200_lives",
                                              "D_ruler_fooled_when_irrelevant_history_arm_skipped")))
ok = True
for cell in ("ELIM", "SELECTOR(64)", "ACQUIRER(4)", "ACQUIRER(8)", "ACQUIRER(12)", "ACQUIRER(16)"):
    c = keys["cells"][cell]
    got = re.search(r"^    %s\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s" % re.escape(cell), cf_readme, flags=re.M)
    want = (f2(c["later_family_mean_correct"]), f2(c["last_family_mean_correct_after_irrelevant_history"]),
            f2(c["certified_bits_carried"]))
    ok = ok and got is not None and got.groups() == want
check("run 4: table in the counterfeit README equals the receipt", ok)

# exploratory probes of runs 2 and 3 (design seeds; not preregistered)
pr = json.loads(text(CF / "RECEIPT_probes_exploratory.json"))
pp = pr["probes"]
ALL6 = lambda v, word: v == [word] * 6
nseq = lambda xs: " ".join(str(x) for x in xs)
check("probes: receipt is from the current probe script, on the preregistered run code, on design seeds only",
      pr["source_sha256_lf"] == lf_sha((CF / "probes_exploratory.py").read_bytes())
      and pr["gauntlet2_sha256_lf"] == g2["source_sha256_lf"] and pr["gauntlet3_sha256_lf"] == g3["source_sha256_lf"]
      and max(pr["design_bases_gauntlet2"] + pr["design_bases_gauntlet3"]) < 100
      and pr["registered_seed_bases_never_used"] == [2026100123, 2026100124]
      and ALL6(pp["baseline"]["run2_BUILDER_factor4"]["verdicts"], "PASS")
      and ALL6(pp["baseline"]["run3_STRATEGIST_factor2"]["verdicts"], "PASS"))
cur = pp["curriculum"]
want_cur = {  # family A -> (library learner, order selector)
    "four_parts_of_the_targets": ("PASS", "FAIL"), "four_parts_disjoint": ("FAIL", "FAIL"),
    "one_composite_of_the_targets_parts": ("FAIL", "PASS"), "one_composite_disjoint": ("FAIL", "PASS")}
rows_cur = ["four part families yes PASS fails", "four part families no fails fails",
            "one composite family yes fails PASS", "one composite family no fails PASS"]
mixed = cur["four_parts_disjoint_plus_one_composite__STRATEGIST"]
check("probes: the curriculum table (family A by shared parts) in RESPONSE_1 equals the receipt",
      all(ALL6(cur[k + "__BUILDER"]["verdicts"], lib) and ALL6(cur[k + "__STRATEGIST"]["verdicts"], sel)
          for k, (lib, sel) in want_cur.items())
      and all(row in n1 for row in rows_cur)
      and cur["four_parts_of_the_targets__STRATEGIST"]["developed_cost_equals_naive"] == [24] * 6
      and cur["four_parts_disjoint__BUILDER"]["SAVINGS"] == [0] * 6
      and cur["one_composite_of_the_targets_parts__BUILDER"]["SAVINGS"] == [0] * 6
      and mixed["LIFECYCLE"] == [21, 21, 23, 21, 22, 23] and mixed["verdicts"].count("INDETERMINATE") == 3
      and nseq(mixed["LIFECYCLE"]) in ncf)
sc = pp["strict_c"]
meds = sc["BUILDER_run2_world"]["kind_of_D_median_errors"] + sc["BUILDER_run2_world"]["kind_of_E_median_errors"]
check("probes: with C a kind never met the frozen U is good in 0 of 24 on every seed",
      all(sc[o][k] == [0] * 6 for o in sc for k in ("kind_of_D_good_of_24", "kind_of_E_good_of_24"))
      and all(sc[o]["same_kind_good_of_24"] == [24] * 6 for o in sc)
      and (f2(min(meds)), f2(max(meds))) == ("10.65", "11.17") and "10.65 to 11.17" in ncf
      and "good in 0 of 24 replicates on every seed" in n1)
fac = pp["factor"]
reg = pp["registered_arithmetic"]
check("probes: run 2's BUILDER by savings factor (passes to 6, indeterminate at 8 on five seeds, fails at 16)",
      all(ALL6(fac["factor=%d" % f]["verdicts"], "PASS") for f in (2, 4, 6))
      and fac["factor=8"]["verdicts"].count("INDETERMINATE") == 5 and ALL6(fac["factor=16"]["verdicts"], "FAIL")
      and nseq(fac["factor=8"]["SAVINGS"]) in ncf
      and [reg["run2_BUILDER_by_factor"]["factor=%d" % f]["verdict"] for f in (8, 10, 16)]
      == ["PASS", "INDETERMINATE", "FAIL"]
      and "passes at factors up to 6, is indeterminate at 8 on five of the six seeds, and fails at 16" in n1)
fam = pp["families"]
check("probes: run 2's BUILDER fails with one, two or three of the four part families",
      all(ALL6(fam["development_families=%d" % k]["verdicts"], "FAIL") for k in (1, 2, 3))
      and ALL6(fam["development_families=4"]["verdicts"], "PASS")
      and "Developed on one, two or three of the four part families, it fails" in n1)
con = pp["confirm"]
check("probes: run 2's BUILDER by acceptance rule (fails on five of six seeds at one passed task)",
      con["CONFIRM=1"]["verdicts"].count("FAIL") == 5 and con["CONFIRM=2"]["verdicts"].count("PASS") == 5
      and ALL6(con["CONFIRM=3"]["verdicts"], "PASS") and ALL6(con["CONFIRM=8"]["verdicts"], "PASS")
      and nseq(con["CONFIRM=1"]["NESTING"]) in ncf and "At 1, BUILDER fails on five of the six seeds" in n1)
sel = pp["selection"]
st = sel["over_2000_design_worlds_base_137"]
off = sel["BUILDER_with_the_conditions_off"]
check("probes: how the worlds are chosen (13% of unselected worlds; nothing is redrawn)",
      sel["variant_with_conditions_equals_gauntlet2_setup_on_144_worlds"] is True and st["worlds"] == 2000
      and st["salt_above_zero"] == 0 and st["first_four_other_parts_compose_B"] == 264
      and st["first_candidate_B_rejected_second_decomposition"] == 124
      and round(100 * 264 / 2000) == 13 and "In 13% of unselected worlds" in n1 and "13.2%" in ncf
      and (min(off["PROVENANCE"]), max(off["PROVENANCE"])) == (17, 24) and "holds in 17 to 24 of 24" in n1
      and off["verdicts"].count("INDETERMINATE") == 3 and nseq(off["PROVENANCE"]) in ncf
      and reg["world_salt_above_zero_in_registered_replicates"] == {"replicates": 312, "run2": 0, "run3": 0})
mem = pp["memoriser"]
check("probes: skipping the content resets moves the memoriser's SAVINGS and not its verdict",
      mem["resets_applied"]["SAVINGS"] == [0] * 6 and mem["resets_skipped"]["SAVINGS"] == [24] * 6
      and ALL6(mem["resets_applied"]["verdicts"], "FAIL") and ALL6(mem["resets_skipped"]["verdicts"], "FAIL")
      and "its verdict is FAIL either way" in n1)
ks = pp["k"]
s3 = reg["run3_STRATEGIST"]
status = lambda c: "HOLDS" if c >= 22 else "FAILS" if c <= 12 else "INDETERMINATE"
check("probes: STRATEGIST by number of inherited orders (8: indeterminate on five; 4 or fewer: holds on none)",
      [status(c) for c in ks["K=8"]["PROVENANCE"]].count("INDETERMINATE") == 5
      and max(max(ks["K=%d" % k]["PROVENANCE"]) for k in (2, 3, 4)) < 22
      and ALL6(ks["K=32"]["verdicts"], "PASS") and ALL6(ks["K=64"]["verdicts"], "PASS")
      and all(nseq(ks["K=%d" % k]["PROVENANCE"]) in ncf for k in (2, 3, 4, 8, 16, 32, 64))
      and "PROVENANCE is indeterminate on five of six seeds; with 4 or fewer it holds on none" in n1)
check("probes: run 3's arms coincide and its same-compute arm holds in 15 of 24 (registered receipt)",
      all(s3[k] == 24 for k in ("lesion_equals_naive", "sham_equals_intact", "rescue_equals_intact",
                                "v_donor_equals_intact", "irrelevant_history_equals_naive"))
      and s3["development_plus_B_cheaper_than_naive_B"] == 15
      and all("15 of 24" in t for t in (n1, n2, ncf))
      and reg["run2_BUILDER"]["sham_cheaper_than_intact"] == 24
      and reg["run2_BUILDER"]["lesioned_line_scores_12.0_the_default_for_nothing_built"] == 24
      and (reg["run2_BUILDER"]["max_developed_cost_B_D_E"], reg["run2_BUILDER"]["min_naive_cost_B_D_E"]) == (27, 166)
      and "27 tasks" in ncf and "166" in ncf)
sf = reg["run3_STRATEGIST_by_factor"]
check("probes: their relations reproduce the registered counts at the registered factors (4 in run 2, 2 in run 3)",
      g3["params"]["FACTOR"] == 2 and sf["factor=2"]["counts"] == g3["cells"]["STRATEGIST"]["counts"]
      and reg["run2_BUILDER_by_factor"]["factor=4"]["counts"] == g2["cells"]["BUILDER"]["counts"]
      and "The factor is 2 where run 2 used 4" in n1)
check("probes: run 3's STRATEGIST by factor on the registered seeds (passes at 4, indeterminate at 6, fails at 8)",
      [sf["factor=%d" % f]["verdict"] for f in (2, 3, 4, 6, 8)] == ["PASS", "PASS", "PASS", "INDETERMINATE", "FAIL"]
      and pp["baseline"]["run3_STRATEGIST_factor4"]["verdicts"].count("PASS") == 5
      and "the pass survives at 4 and is indeterminate at 6" in n1)
sv = pp["strategist_variants"]
three = sv["three_composite_families__registered_organism"]["LIFECYCLE"]
check("probes: STRATEGIST variants (three families; the superseded list; ranking the accepted template only)",
      (min(three), max(three)) == (21, 23) and "LIFECYCLE holds in 21 to 23 of 24" in n1 and nseq(three) in ncf
      and sv["three_composite_families__superseded_list_of_144_pairs"]["LIFECYCLE"][0] == 18
      and nseq(sv["three_composite_families__superseded_list_of_144_pairs"]["LIFECYCLE"]) in ncf
      and nseq(sv["switch_ranks_only_the_accepted_template"]["SAVINGS"]) in ncf
      and ALL6(sv["switch_ranks_only_the_accepted_template"]["verdicts"], "INDETERMINATE"))
pw = pp["power"]
facts_p = pp["facts"]
check("probes: power (one of ten blocks indeterminate) and facts about run 3's world",
      pw["factor=2"]["block_verdicts"].count("INDETERMINATE") == 1 and len(pw["factor=2"]["block_verdicts"]) == 10
      and pw["factor=4"]["block_verdicts"].count("INDETERMINATE") == 4
      and (pw["factor=2"]["holds_of_240"]["LIFECYCLE"], pw["factor=2"]["holds_of_240"]["PROVENANCE"]) == (235, 232)
      and "Of ten blocks of 24 design replicates, one came out indeterminate" in n1
      and facts_p["STRATEGIST_index_after_development_of_144"]["useful"] == 142 and "142 of 144" in n1
      and facts_p["STRATEGIST_index_after_irrelevant_history_of_144"] == {"plain": 144}
      and facts_p["BUILDER_library_after_development_of_144"] == {"entries=1 depth=[4] pairs=0": 144}
      and facts_p["targets"] == facts_p["targets_in_the_inherited_pairs_first_list"] == 432
      and facts_p["targets_covered_by_a_pair_of_history_parts"] == 0
      and facts_p["templates_of_depth_3_or_less"] == 147 and "147 shallower templates" in n1)
never_false = ["NESTING.rescue_restores", "PROVENANCE.random_library_no_help",
               "U_TRANSFER.frozen_U_good_on_C", "U_TRANSFER.frozen_U_good_on_narrower_C"]
third = reg["run2_clause_true_of_24_by_cell"]["U_TRANSFER.lesioned_line_bad_on_C"]
check("probes: four clauses of run 2 are never false in any cell; the third clause of U_TRANSFER does fail",
      reg["run2_clauses_never_false_in_any_cell"] == never_false and len(reg["run2_clause_true_of_24_by_cell"]) == 13
      and third["BUILDER"] == 24 and min(third.values()) == 0
      and "Four clauses are never false in any cell of run 2" in n1 and "four clauses have no fire test" in n1
      and "four clauses have no fire test" in ncf, "%s" % reg["run2_clauses_never_false_in_any_cell"])
rd = pp["reading1"]
check("probes: run 1's reading under run 2's cost (library learner)",
      rd["LIFECYCLE"] == [0] * 6 and nseq(rd["SAVINGS_factor4"]) in ncf)

# prototype
reach = json.loads(text(P1 / "RECEIPT_reach.json"))
table = {}
for rule in ("margin", "strict", "neutral"):
    got = re.search(r"^\s+%s rule\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$" % rule, r1, flags=re.M)
    table[rule] = [int(x) for x in got.groups()] if got else None
want = {rule: [reach["cells"]["%s d=%d" % (rule, d)]["recovered"] for d in (1, 2, 3, 8)]
        for rule in ("margin", "strict", "neutral")}
check("prototype: reach table in RESPONSE_1 equals the receipt", table == want, "%s" % want)
check("prototype: random programs", reach["random"]["hits_at_0.9"] == 0 and reach["random"]["programs"] == 2000000
      and reach["budget_per_lineage"] == 200000 and reach["lineages_per_cell"] == 24)
check("prototype: zero of 24 bounds the per-lineage rate below 11.7%",
      f1(100 * (1 - 0.05 ** (1 / 24))) == "11.7" and "11.7%" in r1)
qual = json.loads(text(P1 / "RECEIPT_qualify.json"))
probes = qual["A"]["builder(8)"]["build"]["eligible"]
lives = qual["n_lives"]
check("prototype: probes, lives, throughput",
      probes == 18854 and lives == 2400 and f2(qual["G"]["lives_per_second"] / 1e6) == "1.86")
check("prototype: one stored mapping is worth 0.74 probes per life",
      f2(probes / (lives * 8) * 0.75) == "0.74" and "0.74" in r1)
v1 = json.loads(text(P1 / "RECEIPT_qualify_v1_GATE_FAILED.json"))
h = v1["C"]["interchange"]["holder(8)"]
check("prototype: first gate failed as described",
      v1["gate"] == "FAIL" and h["followed_donor"] == 722 and h["eligible"] == 2785
      and h["verdict"] == "INDETERMINATE" and "0.865" in text(P1 / "README.md"))

# -------------------------------------------------------- 4. preregistration
def git(*args):
    return subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True)


for script, receipt, commit in RUNS:
    path = "docs/phase3/review/FABLE-5.1/counterfeit/"
    anc = git("merge-base", "--is-ancestor", commit, "HEAD")
    blob = git("show", "%s:%s%s" % (commit, path, script))
    had = git("cat-file", "-e", "%s:%s%s" % (commit, path, receipt))
    now = lf_sha((CF / script).read_bytes())
    check("prereg %s at %s: ancestor; receipt from that code; code unchanged; no receipt then" % (script, commit),
          anc.returncode == 0 and blob.returncode == 0 and lf_sha(blob.stdout) == rec[receipt]["source_sha256_lf"] == now
          and had.returncode != 0)
check("run 3 ran against the preregistered gauntlet2.py",
      g3["gauntlet2_sha256_lf"] == g2["source_sha256_lf"] == lf_sha((CF / "gauntlet2.py").read_bytes()))
for tag in ("8dc9ef542", "619472376", "c6adb3a57", "635b3cba1"):
    check("commit %s is named in RESPONSE_1 and the counterfeit README" % tag, tag in r1 and tag in cf_readme)

# ------------------------------------------------------------ 5. consistency
pat = r"^\s{4}(R\d+\+?)\s{2,}([A-Z]+)\s{2,}"
d1 = dict(re.findall(pat, r1, flags=re.M))
d3_table = dict(re.findall(pat, r3, flags=re.M))
d3_sheets = dict(re.findall(r"^(R\d+\+?) -- .*? \.{3,} ([A-Z]+)$", r3, flags=re.M))
ids = ["R%d" % i for i in range(10)] + ["R10+"]
allowed = {"KEEP", "MERGE", "MODIFY", "DEFER", "RETIRE", "REPLACE"}
check("dispositions: all eleven present in each list, each one of the charter's six words",
      all(set(d) == set(ids) and set(d.values()) <= allowed for d in (d1, d3_table, d3_sheets)),
      "%d, %d, %d" % (len(d1), len(d3_table), len(d3_sheets)))
check("dispositions: RESPONSE_1 table = RESPONSE_3 table = RESPONSE_3 sheets",
      d1 == d3_table == d3_sheets, "%s" % d1)

rows = re.findall(r"^S(\d+)\s+(.+?)\s\.{3,}\s(.+)$", r2, flags=re.M)
tally = {"keep": 0, "modify": 0, "defer": 0}
deferred = []
for num, _, disp in rows:
    d = disp.strip()
    if d.startswith("DEFER"):           # a sheet whose disposition begins with DEFER is postponed
        tally["defer"] += 1
        deferred.append(int(num))
    elif d == "KEEP":                   # kept as written
        tally["keep"] += 1
    else:
        tally["modify"] += 1
head = re.search(r"Of 24 sections: keep (\d+) with one addition each, modify (\d+),\s+defer (\d+) "
                 r"\(sections ([0-9, and]+)\)\.", r2)
check("RESPONSE_2: 24 section sheets, numbered 1 to 24",
      [int(n) for n, _, _ in rows] == list(range(1, 25)))
check("RESPONSE_2: headline tally and its list of deferred sections equal the sheets",
      head is not None and [int(x) for x in head.groups()[:3]] == [tally[k] for k in ("keep", "modify", "defer")]
      and [int(x) for x in re.findall(r"\d+", head.group(4))] == deferred,
      "%s deferred %s" % (tally, deferred))
n_where = len(re.findall(r"^    (?:\d+(?:, \d+)?: )", r2, flags=re.M))
check("RESPONSE_2: three rows in the table of presumptions, as the verdict states",
      n_where == 3 and "Three of its definitions still fix the organism's shape" in r2, "%d" % n_where)
titles = re.findall(r"^-{80}\n(\d+)\. [^\n]+\n-{80}$", r1, flags=re.M)
check("RESPONSE_1: fifteen numbered sections in order", titles == [str(i) for i in range(1, 16)], "%s" % titles)
effort = [int(x) for x in re.findall(r"\.{3,} about (\d+)%", r1)]
check("RESPONSE_1: the effort table sums to 100 and the instrument share is 65",
      sum(effort) == 100 and effort[0] + effort[1] == 65 and "about 65% instrument" in r1, "%s" % effort)

# Sentences withdrawn after the third review, and wording that went stale with it.
withdrawn = ["Each tightening removes", 'No reading of "fresh"', "A pass under 2 with a fail under 3",
             "A pass under the second with a fail", "run 3 confirms it", "strict protocol", "about sixty",
             "Two read-only reviewers", "three members have run", "namesake protocol",
             "four choices the steps leave open", "TERMS USED IN ALL THREE", "nothing I built",
             "three clauses have no fire test", "(as run 2)", "fails REPEAT in 0", "Each changes a verdict",
             "what passed all six"]
everything = {"RESPONSE_1": n1, "RESPONSE_2": n2, "RESPONSE_3": n3, "00_README": top_readme, "counterfeit/README": ncf}
left = ["%s: %s" % (name, w) for name, t in everything.items() for w in withdrawn if w in t]
left += ["%s: 18 of 24" % name for name, t in (("RESPONSE_1", n1), ("RESPONSE_2", n2), ("RESPONSE_3", n3))
         if "18 of 24" in t]
check("withdrawn sentences and stale wording are gone from the responses and READMEs", not left, "%s" % left)
check("the open choices are counted as five, and the kit as five members, wherever they are counted",
      "leaves five choices open" in n1 and "leaves five choices" in n2 and "five choices open" in top_readme
      and "five open choices" in ncf and "five kit members that have run" in n1.lower()
      and n3.count("ive members have run") == 3 and "five kit members" in n3)
check("three review rounds, 38 + 21 + 26 = 85 defects, and the closure check, stated the same way",
      38 + 21 + 26 == 85 and "38, 21 and 26 defects" in n1 and "38, 21 and 26 defects" in top_readme
      and "85 defects" in top_readme and "hree read-only reviewers" in n2 and "hree read-only reviewers" in n3
      and "22 of its 26 closed, 4 partly" in n1 and "22 of its 26 closed, 4 partly" in top_readme)

# ------------------------------------------------------------------ 6. record
matrix = norm(text(PKG / "SALVAGE_MATRIX.md"))
facts = ["3,132 of 4,881 sampled children were neutral", "19,873,536", ".850 and .978", ".503 and .479",
         "28-line block clock", "139 passed", "0 schemas in 8 of 8", "47 and 345 times",
         "96 exact copiers in 10,000,000", "93 of 93", "a known-answer corpus for a lattice arm",
         "no closed-loop network organism that keeps weights or topology across episodes",
         "a shortcut search over a hand-built list of cheap policies"]
absent = [f for f in facts if f not in matrix]
check("record: figures cited from the salvage matrix are in it", not absent, "%s" % absent)
req = norm(text(PKG / "REQUIREMENTS.md"))
lines = ["A fixed hierarchical learner already speeds up inside its hypothesis space",
         "New seeds of the same structure test noise robustness",
         "an arm given the same total compute on the target alone",
         "a random structure of equal size and with a wrong-history donor's structure"]
absent = [f for f in lines if f not in req]
check("record: the four transfer requirements cited are worded as cited", not absent, "%s" % absent)

failed = [n for n, ok, _ in results if not ok]
print("\n%d checks, %d failed" % (len(results), len(failed)))
sys.exit(1 if failed else 0)
