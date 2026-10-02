exec(open(__file__.replace("p07_audits.py", "drv.py")).read())
import copy
import json
from rso_harness import stats, retain1, rulers, search, torture, audits, claims, registration
from rso_harness.verdict import *


def show(tag, r):
    print("%-92s -> %s %s" % (tag, r.verdict, ("| " + r.reason) if r.reason else ""))


CF = meta.COUNTERFEIT
full2 = json.loads((CF / "RECEIPT_gauntlet2.json").read_text())
full3 = json.loads((CF / "RECEIPT_gauntlet3.json").read_text())
r2, r3 = full2["cells"], full3["cells"]
print("################ audits.py against the receipts it reads")
groups = {"SAVINGS": ["SAVINGS"], "LIFECYCLE": ["LIFECYCLE"],
          "U_TRANSFER": ["U_TRANSFER.frozen_U_good_on_C", "U_TRANSFER.frozen_U_good_on_narrower_C", "U_TRANSFER.lesioned_line_bad_on_C"],
          "NESTING": ["NESTING.lesion_hurts", "NESTING.sham_harmless", "NESTING.rescue_restores", "NESTING.donor_V_helps"],
          "PROVENANCE": ["PROVENANCE.wrong_history_no_help", "PROVENANCE.random_store_no_help"],
          "REPEAT": ["REPEAT.D", "REPEAT.E"]}
for tag, cells, fn in (("run2", r2, audits.clauses_run2), ("run3", r3, audits.clauses_run3)):
    bad = []
    for cname, cell in cells.items():
        for conj, parts in groups.items():
            n = sum(1 for o in cell["replicates"] if all(fn(o)[p] for p in parts))
            if n != cell["counts"][conj]:
                bad.append((cname, conj, n, cell["counts"][conj]))
    print("  %s: conjunct counts recomputed from the audit's 13 clauses equal the receipt's own counts: %s %s"
          % (tag, not bad, bad[:3]))
print("  receipt params: run2", {k: full2["params"][k] for k in ("GOOD_MAX", "BAD_MIN", "HOLDS_AT", "FAILS_AT", "N_REP")},
      "| run3", {k: full3["params"][k] for k in ("FACTOR", "HOLDS_AT", "FAILS_AT", "N_REP")})
for tag, cells, fn in (("run2", r2, audits.clauses_run2), ("run3", r3, audits.clauses_run3)):
    t = audits.clause_table(cells, fn)
    print("  --- clause table", tag, "(cells:", ", ".join(cells), ")")
    for c, row in t.items():
        print("     %-42s min %2d max %2d  %s" % (c, min(row.values()), max(row.values()), [row[k] for k in cells]))
    a = audits.audit_clauses(cells, fn)
    print("     ->", a.verdict, a.reason)
    never_false = sorted(c for c, row in t.items() if min(row.values()) == 24)
    print("     clauses true in 24 of 24 in every cell (never false at all):", never_false)
print("################ medians quoted in document 1, section 5")
m = r2["BUILDER"]["medians"]
print("  ", {k: m[k] for k in ("naive_B", "dev_B", "lesion_B", "sham_B", "rescue_B", "v_donor_B", "wrong_history_B", "random_library_B")})
print("   candidate_templates:", full2["params"]["candidate_templates"])
print("################ G9.arms")
show("run 2 BUILDER", audits.audit_arms(r2["BUILDER"]["replicates"], meta.ARMS2))
show("run 3 STRATEGIST", audits.audit_arms(r3["STRATEGIST"]["replicates"], meta.ARMS3))
for cname in r2:
    a = audits.audit_arms(r2[cname]["replicates"], meta.ARMS2)
    print("     run 2 %-11s %s %s" % (cname, a.verdict, a.reason))
for cname in r3:
    a = audits.audit_arms(r3[cname]["replicates"], meta.ARMS3)
    print("     run 3 %-11s %s %s" % (cname, a.verdict, a.reason))
reps = copy.deepcopy(r3["STRATEGIST"]["replicates"])
reps[0]["lesion_B"] += 1
reps[0]["sham_B"] += 1
reps[0]["rescue_B"] += 2
reps[0]["v_donor_B"] += 3
reps[0]["irrelevant_history_B"] += 2
show("E run 3 arms, one replicate of 24 nudged by 1 to 3 tasks", audits.audit_arms(reps, meta.ARMS3))
capped = [{"naive_B": 400, "dev_B": 40, "lesion_B": 400, "sham_B": 41 + i % 2} for i in range(24)]
show("S separate computations that both hit a 400-task cap (naive, lesion)", audits.audit_arms(capped, ("naive_B", "dev_B", "lesion_B", "sham_B")))
print("################ G9.sham")
t2 = audits.clause_table(r2, audits.clauses_run2)
t3 = audits.clause_table(r3, audits.clauses_run3)
print("   run 2 sham clause row:", t2["NESTING.sham_harmless"])
print("   run 3 sham clause row:", t3["NESTING.sham_harmless"])
for mg in (0.25, 0.4, 0.42, 0.45, 0.5):
    show("run 2 BUILDER sham, margin %.2f" % mg, audits.audit_sham(r2["BUILDER"]["replicates"], t2["NESTING.sham_harmless"], mg))
rigged = dict(t3["NESTING.sham_harmless"], FIRE_TEST_WITH_A_DIFFERENT_HARMFUL_SHAM=0)
show("E run 3 STRATEGIST idle sham + one cell in which another (harmful) operation is called sham",
     audits.audit_sham(r3["STRATEGIST"]["replicates"], rigged))
small = [{"dev_B": 3, "sham_B": 4} for _ in range(24)]
show("S a neutral sham at small counts (3 tasks intact, 4 after the sham)", audits.audit_sham(small, {"GOOD": 24, "BAD": 0}))
print("################ G9.clauses")
cells = meta.toy_cells()
show("clean toy", audits.audit_clauses(cells, meta.toy_clauses))
only_naive = {"GOOD": cells["GOOD"], "NOTHING_DEVELOPED": cells["BAD"]}
show("E every clause 'can fail' in one catch-all cell where nothing works (no clause-specific fire test)",
     audits.audit_clauses(only_naive, meta.toy_clauses))
halfway = {"GOOD": cells["GOOD"], "HALF": {"replicates": [dict(cells["GOOD"]["replicates"][0]) for _ in range(12)] +
                                                 [dict(cells["BAD"]["replicates"][0]) for _ in range(12)]}}
show("? clause false in exactly 12 of 24 in one cell", audits.audit_clauses(halfway, meta.toy_clauses))
print("################ G10.setting / G10.contrast")
show("clean", audits.audit_setting(meta.SETTING_OK))
show("E power registered as 0.2", audits.audit_setting(dict(audits.RUN2, power=0.2, amortization_horizon="three")))
show("E power 'not computed', horizon 'n/a'", audits.audit_setting(dict(audits.RUN2, power="not computed", amortization_horizon="n/a")))
show("E every field is the string 'tbd'", audits.audit_setting({k: "tbd" for k in audits.SETTING}))
show("? power registered as 0 (number)", audits.audit_setting(dict(audits.RUN2, power=0, amortization_horizon="three")))
a = dict(audits.RUN3)
b = dict(audits.RUN3, parts_shared=True)
show("clean contrast", audits.audit_contrast("parts_shared", a, b))
show("E two things change, one of them not in the dictionary", audits.audit_contrast("parts_shared", a, b))
show("S same setting worded differently in the two runs",
     audits.audit_contrast("parts_shared", a, dict(b, cost="tasks until a procedure is accepted (8 passes in a row), no cut-off")))
print("   keys of RUN2/RUN3 dictionaries:", sorted(audits.RUN2))
print("################ G10.ruler")
show("clean ORDER3_BITS", audits.ruler_status("ORDER3_BITS", receipts=CF))
kit = {"MY_POSITIVE": {"built": True, "X": "POSITIVE", "receipt": "README.md"},
       "MY_NEGATIVE": {"built": True, "X": "NEGATIVE", "receipt": "MANIFEST.md"}}
show("E any claim, members 'built', receipts are unrelated files that exist (README.md, MANIFEST.md)", audits.ruler_status("X", kit, receipts=CF))
kit2 = dict(audits.KIT, GENUINE={"built": True, "STRONG_RECURSION": "POSITIVE", "receipt": "RECEIPT_keys.json"})
for k in ("WORLD_PARKING", "NESTED_COMPILER_CARGO", "HIERARCHICAL_SELECTOR", "FLATTENED_EQUIVALENT"):
    kit2[k] = dict(kit2[k], built=True, receipt="RECEIPT_gauntlet.json")
show("E strong claim: a 'positive' and four members merely flagged built, pointing at existing receipts", audits.ruler_status("STRONG_RECURSION", kit2, receipts=CF))
show("E same without the receipts argument (as test_unqualified_and_blocked_are_not_fail calls it)", audits.ruler_status("ORDER3_BITS"))
keys = json.loads((CF / "RECEIPT_keys.json").read_text())
print("   RECEIPT_keys.json: what the bits ruler returned on the members the registry calls ORDER3_BITS negatives/positives")
for c in keys["cells"]:
    v = keys["cells"][c]
    print("     %-62s verdict %-22s bits %6.2f  if irrelevant-history arm skipped: %s"
          % (c, v["verdict"], v["certified_bits_carried"], v["verdict_if_irrelevant_history_arm_skipped"]))
print("################ G11.custody")
show("clean", claims.check_custody(meta.custody()))
show("E same generator renamed", claims.check_custody(meta.custody(discovery={"seeds": [1, 2, 3], "panel_sha256": "d" * 64, "generator": "renewal"},
                                                                    confirmation={"seeds": [7, 8, 9], "panel_sha256": "c" * 64, "generator": "Renewal "})))
show("E confirmation with no seeds at all", claims.check_custody(meta.custody(confirmation={"seeds": [], "panel_sha256": "c" * 64, "generator": "renewal-v2"})))
show("E acceptance rule and world filter fixed after discovery output (no field for it)", claims.check_custody(meta.custody(acceptance_rule_fixed="after discovery output", world_filter="chosen after design runs")))
show("E same custodian holds discovery and confirmation (no field for it)", claims.check_custody(meta.custody(custodian_discovery="A", custodian_confirmation="A")))
show("E selection_data = 'discovery' while tuning_evaluations is negative", claims.check_custody(meta.custody(tuning_evaluations=-5)))
print("################ G12")
show("clean L2", claims.promote(meta.claim(), 2))
show("precedence: detection absent AND demand FAIL (FAIL should outrank BLOCKED)", claims.promote(meta.claim(drop="detection", demand=FAIL), 1))
show("E a structure claim whose exact_null facet is simply asserted PASS", claims.promote(meta.claim(kind="TRANSFER"), 2))
show("  the registered 'structure' mutant is the generic unqualified-facet path", claims.promote(meta.claim(kind="EFFECT", exact_null=UNQUALIFIED), 2))
show("E L3 with reproduced asserted", claims.promote(meta.claim(reproduced=PASS), 3))
try:
    claims.promote(meta.claim(detection="passed"), 1)
except Exception as e:
    print("   a facet with an unknown value raises instead of returning a verdict:", type(e).__name__, e)
show("E render with conditions that are not the registered setting", claims.render(dict(meta.claim(), conditions={"note": "see the paper"})))
show("E render of a claim whose facets all FAILED (still PASS, level L0)", claims.render(meta.claim(**{f: FAIL for f in claims.L1})))
print("   ", claims.render(meta.claim(**{f: FAIL for f in claims.L1})).reason)
print("################ verdict.combine and INDETERMINATE")
import inspect
srcs = {n: inspect.getsource(mod) for n, mod in (("stats", stats), ("retain1", retain1), ("rulers", rulers), ("search", search), ("torture", torture), ("audits", audits), ("claims", claims), ("registration", registration))}
for n, s in srcs.items():
    uses = [ln.strip() for ln in s.splitlines() if "INDETERMINATE" in ln and not ln.strip().startswith(("#", "from", "import", '"""'))]
    print("   %-13s lines that can produce or mention INDETERMINATE: %s" % (n, uses))
print("   three_way is called from:", [n for n, s in srcs.items() if "three_way(" in s and n != "stats"] or "nowhere outside stats.py and the unit test")
