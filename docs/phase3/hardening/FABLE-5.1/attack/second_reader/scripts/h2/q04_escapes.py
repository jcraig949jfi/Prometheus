import sys, pathlib, json, copy
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "harness"))
from rso_harness import meta, audits, claims
from rso_harness.verdict import *
CF = meta.COUNTERFEIT


def show(tag, thunk):
    try:
        r = thunk()
        print("%-100s -> %s %s" % (tag, r.verdict, ("| " + str(r.reason)[:230]) if r.reason else ""))
        return r
    except Exception as e:
        print("%-100s -> RAISES %s: %s" % (tag, type(e).__name__, str(e)[:150]))


r2, r3 = meta.run2(), meta.run3()
t2, t3 = audits.clause_table(r2, audits.clauses_run2), audits.clause_table(r3, audits.clauses_run3)
print("################ G9.arms")


def nudge(reps, which):
    reps = copy.deepcopy(reps)
    for i in which:
        for arm, d in (("lesion_B", 1), ("sham_B", 1), ("rescue_B", 2), ("v_donor_B", 3), ("irrelevant_history_B", 2)):
            reps[i][arm] += d
    return reps


S3 = r3["STRATEGIST"]["replicates"]
show("registered mutant: run 3 arms nudged in 1 replicate", lambda: audits.audit_arms(nudge(S3, [0]), meta.ARMS3))
show("E run 3 arms nudged in 2 replicates (22 of 24 still equal)", lambda: audits.audit_arms(nudge(S3, [0, 1]), meta.ARMS3))
show("E run 3 arms nudged in 3 replicates (21 of 24 equal)", lambda: audits.audit_arms(nudge(S3, [0, 1, 2]), meta.ARMS3))
off = copy.deepcopy(S3)
for o in off:
    o["lesion_B"] = o["naive_B"] + 1
    o["irrelevant_history_B"] = o["naive_B"] + 2
    o["sham_B"] = o["dev_B"] + 1
    o["rescue_B"] = o["dev_B"] + 2
    o["v_donor_B"] = o["dev_B"] + 3
show("E run 3: the same three computations, each copy reported with a constant offset of 1..3 tasks", lambda: audits.audit_arms(off, meta.ARMS3))
show("? empty replicate list (no data)", lambda: audits.audit_arms([], ("naive_B", "dev_B")))
det = [{"naive_B": 100 + i, "dev_B": 10 + i % 3, "sham_B": 10 + i % 3, "lesion_B": 90 + i, "rescue_B": 10 + i % 3} for i in range(24)]
toy_row = audits.clause_table(meta.toy_cells(**meta.ISOLATING), meta.toy_clauses)["NESTING.sham_harmless"]
show("S deterministic runtime, exactly neutral sham and exact rescue: G9.sham says", lambda: audits.audit_sham(det, toy_row))
show("S the same replicates: G9.arms says", lambda: audits.audit_arms(det, ("naive_B", "dev_B", "sham_B", "lesion_B", "rescue_B")))
print("################ G9.sham")
B2 = r2["BUILDER"]["replicates"]
perm = [dict(o, sham_B=B2[(i + 1) % 24]["dev_B"]) for i, o in enumerate(B2)]
r = show("S run 2 BUILDER, sham arm := the intact arm of the next replicate (same distribution, no operation)", lambda: audits.audit_sham(perm, t2["NESTING.sham_harmless"]))
print("     detail:", r.detail, "| dev_B values:", sorted(o["dev_B"] for o in B2))
show("E run 3 idle sham judged with a clause row borrowed from run 2", lambda: audits.audit_sham(S3, t2["NESTING.sham_harmless"]))
show("  dev_B = 0, sham_B = 1", lambda: audits.audit_sham([{"dev_B": 0, "sham_B": 1}] * 24, toy_row))
show("  empty replicate list", lambda: audits.audit_sham([], toy_row))
show("  21 of 24 near", lambda: audits.audit_sham([{"dev_B": 10, "sham_B": 10}] * 21 + [{"dev_B": 10, "sham_B": 30}] * 3, toy_row))
print("################ G9.clauses")


def cells_n(n_good, n_other):
    out = {"GOOD": {"replicates": [dict(meta.TOY) for _ in range(24)]}}
    for name, change in meta.ISOLATING.items():
        bad_all = dict(meta.TOY, **meta.CATCH_ALL["NOTHING_WORKS"])
        out[name] = {"replicates": [dict(meta.TOY, **change) for _ in range(n_good)] + [bad_all for _ in range(n_other)]}
    return out


c = cells_n(22, 218)
tab = audits.clause_table(c, meta.toy_clauses)
print("   clause table with 240 replicates per isolating cell:", tab)
show("E 240 replicates per cell; in each isolating cell the other clauses hold in 22 of 240 (9%)", lambda: audits.audit_clauses(c, meta.toy_clauses))
c12 = {k: {"replicates": v["replicates"][:12]} for k, v in meta.toy_cells(**meta.ISOLATING).items()}
show("S the registered clean toy, with 12 replicates per cell instead of 24", lambda: audits.audit_clauses(c12, meta.toy_clauses))


def clauses_run2_minus(o, factor=4):
    d = audits.clauses_run2(o, factor)
    for k in ("NESTING.rescue_restores", "PROVENANCE.random_store_no_help", "U_TRANSFER.frozen_U_good_on_C", "U_TRANSFER.frozen_U_good_on_narrower_C"):
        d.pop(k)
    return d


show("E run 2 audited with the four clauses that cannot fail left out of the clause function", lambda: audits.audit_clauses(r2, clauses_run2_minus))
print("################ G10.setting")
OK = meta.SETTING_OK
show("clean", lambda: audits.audit_setting(OK))
show("E run 3 as registered plus two typed numbers: power=0.99, horizon=3 (measured power was 0.9)", lambda: audits.audit_setting(dict(audits.RUN3, power=0.99, amortization_horizon=3)))
show("E six choices registered as [], {}, False, 0, 0.0, ()", lambda: audits.audit_setting(dict(OK, cost=[], later_families={}, content_reset=False, sham=0, family_A=0.0, wrong_history=())))
show("E six choices registered as pending, -, see above, to be decided, t.b.d., same as before", lambda: audits.audit_setting(dict(OK, cost="pending", later_families="-", content_reset="see above", sham="to be decided", family_A="t.b.d.", wrong_history="same as before")))
show("S power registered as the integer 1", lambda: audits.audit_setting(dict(OK, power=1)))
show("  power = True", lambda: audits.audit_setting(dict(OK, power=True)))
show("  power = nan", lambda: audits.audit_setting(dict(OK, power=float("nan"))))
show("  horizon = 10**9", lambda: audits.audit_setting(dict(OK, amortization_horizon=10**9)))
show("  effect_threshold = 1e-300", lambda: audits.audit_setting(dict(OK, effect_threshold=1e-300)))
show("  effect_threshold = inf", lambda: audits.audit_setting(dict(OK, effect_threshold=float("inf"))))
print("################ G10.contrast")
a = dict(audits.RUN3)
b = dict(audits.RUN3, parts_shared=True)
show("registered CLEAN case (= the reader's E: two things change, one of them not in the dictionary)", lambda: audits.audit_contrast("parts_shared", a, b))
show("E run 2 against run 3 written as one coarse field", lambda: audits.audit_contrast("curriculum_and_parts", {"curriculum_and_parts": "RUN2"}, {"curriculum_and_parts": "RUN3"}))
five = ("content_reset", "effect_threshold", "family_A", "sham", "wrong_history")
show("E run 2 against run 3 after leaving out of both the five other fields that differ", lambda: audits.audit_contrast("parts_shared", {k: v for k, v in audits.RUN2.items() if k not in five}, {k: v for k, v in audits.RUN3.items() if k not in five}))
show("S one variable changed, the unchanged cost worded differently", lambda: audits.audit_contrast("parts_shared", a, dict(b, cost="tasks to accepted procedure, no cut-off")))
show("S effect_threshold 2 against the string 2", lambda: audits.audit_contrast("parts_shared", a, dict(b, effect_threshold="2")))
show("  named variable absent from both", lambda: audits.audit_contrast("temperature", a, a))
print("################ G10.ruler")
K = audits.KEYS
forged = [("GENUINE_LEARNED_UPDATER", "S19@NEW", (K, "keys", "ACQUIRER(16)"), {"STRONG": "POSITIVE"}),
          ("PROCEDURE_SELECTOR", "S19@NEW", (K, "keys", "ELIM"), {"STRONG": "NEGATIVE"})]
show("E STRONG claim: a genuine updater and a selector whose rows point at two verdicts of the keys receipt", lambda: audits.ruler_status("STRONG", "S19@NEW", CF, forged, {}))
drop = [r for r in audits.RUNS if not (r[0] == "LIBRARY_FIXED_BUILDER" and r[1] == "S19@RUN2")] + [("GENUINE_LEARNED_UPDATER", "S19@RUN2", (audits.G2, "cell", "BUILDER"), {"STRONG": "POSITIVE"})]
show("E STRONG at run 2: the BUILDER row re-registered as the genuine positive, unbuilt list emptied", lambda: audits.ruler_status("STRONG", "S19@RUN2", CF, [r for r in drop if r[1] == "S19@RUN2"], {}))
plus8 = audits.RUNS + [("KEY_ACQUIRER_8", "BITS@KEYS", (K, "keys", "ACQUIRER(8)"), {"BITS": "POSITIVE"})]
show("? BITS with ACQUIRER(8) registered as a positive (it carries 24.95 bits; certified 9.46)", lambda: audits.ruler_status("BITS", "BITS@KEYS", CF, plus8))
plus4 = audits.RUNS + [("KEY_ACQUIRER_4", "BITS@KEYS", (K, "keys", "ACQUIRER(4)"), {"BITS": "POSITIVE"})]
show("? BITS with ACQUIRER(4) registered as a positive (carries 11.41 bits; certified 1.44)", lambda: audits.ruler_status("BITS", "BITS@KEYS", CF, plus4))
plus12 = audits.RUNS + [("KEY_ACQUIRER_12", "BITS@KEYS", (K, "keys", "ACQUIRER(12)"), {"BITS": "POSITIVE"})]
show("? BITS with ACQUIRER(12) registered as a positive", lambda: audits.ruler_status("BITS", "BITS@KEYS", CF, plus12))
plusA = audits.RUNS + [("KEY_SELECTOR_OWN_LIST", "BITS@KEYS", (K, "keys", "fire test A: SELECTOR(64), key drawn from its own list"), {"BITS": "NEGATIVE"})]
show("? BITS with fire test A registered NEGATIVE (the ruler returned RULER_NOT_APPLICABLE)", lambda: audits.ruler_status("BITS", "BITS@KEYS", CF, plusA))
sand = [(m, ("BITS@KEYS_ONE_KEY_REUSED" if m == "KEY_SANDBAGGER" else s), src, an) for m, s, src, an in audits.RUNS]
show("? BITS with the sandbagger's setting named for what it was (a harness that reuses one key)", lambda: audits.ruler_status("BITS", "BITS@KEYS", CF, sand))
for cellname, ans in (("WASTEFUL", "POSITIVE"), ("HIDDEN", "POSITIVE"), ("BADSHAM", "POSITIVE"), ("OFFHISTORY", "POSITIVE"), ("STATIC", "NEGATIVE")):
    runs = audits.RUNS + [("RUN2_" + cellname, "S19@RUN2", (audits.G2, "cell", cellname), {"STRONG": "NEGATIVE", "REUSE": ans})]
    show("? REUSE at run 2 with cell %s registered %s for reuse" % (cellname, ans), lambda: audits.ruler_status("REUSE", "S19@RUN2", CF, runs))
    show("     and with the unbuilt list emptied and the order selector dropped", lambda: audits.ruler_status("REUSE", "S19@RUN2", CF, [r for r in runs if r[1] == "S19@RUN2"], {}))
show("? REUSE at run 2 as registered, unbuilt list emptied, order selector dropped (the four rows alone)", lambda: audits.ruler_status("REUSE", "S19@RUN2", CF, [r for r in audits.RUNS if r[1] == "S19@RUN2"], {}))
b3 = [(m, s, src, dict(an, REUSE="POSITIVE") if (m == "LIBRARY_FIXED_BUILDER" and s == "S19@RUN3") else an) for m, s, src, an in audits.RUNS]
show("? REUSE at run 3 with the builder registered POSITIVE there too", lambda: audits.ruler_status("REUSE", "S19@RUN3", CF, b3))
show("  a claim nobody registered", lambda: audits.ruler_status("LAW", "S19@RUN2", CF))
print("   returned() on every verdict row of the keys receipt:")
keys = json.loads((CF / K).read_text())
for k, v in keys["verdicts"].items():
    print("      %-62s receipt says %-24s -> returned() %s" % (k, v, audits.returned(CF, (K, "keys", k))))
print("################ G11.custody")
cu, side = meta.custody, meta.side
show("clean", lambda: claims.check_custody(cu()))
show("E a TRANSFER claim on new seeds of the discovery generator (claim field is not NEW_FAMILY)", lambda: claims.check_custody(cu(claim="TRANSFER", confirmation=side(generator_sha256="1" * 64))))
show("E the same with claim = new family (lower case, a space)", lambda: claims.check_custody(cu(claim="new family", confirmation=side(generator_sha256="1" * 64))))
show("E confirmation seeds are the discovery seeds typed as strings", lambda: claims.check_custody(cu(confirmation=side(seeds=["1", "2", "3"]))))
show("E one custodian under two spellings (tuner, Tuner+space)", lambda: claims.check_custody(cu(confirmation_custodian="Tuner ")))
show("E generator hashes differ only in letter case", lambda: claims.check_custody(cu(discovery=dict(seeds=[1, 2, 3], panel_sha256="d" * 64, generator_sha256="a" * 64), confirmation=side(generator_sha256="A" * 64))))
show("E rule fixed at tick 0, data opened at tick 1, tuning budget 10**9", lambda: claims.check_custody(cu(rule_fixed_at=0, confirmation_opened_at=1, tuning_budget=10**9)))
show("S selection_data = Discovery (capital D)", lambda: claims.check_custody(cu(selection_data="Discovery")))
show("  record is not a dict of dicts (discovery = x)", lambda: claims.check_custody(cu(discovery="x")))
print("################ G12.promote / render")
cl = meta.claim
show("E a structure (TRANSFER) claim at L2 with exact_null typed PASS", lambda: claims.promote(cl("TRANSFER"), 2))
show("E NESTED claim at L2, all four nested facets typed PASS, source = the harness receipt", lambda: claims.promote(cl("NESTED"), 2))
show("E L3 with reproduced typed PASS", lambda: claims.promote(cl(reproduced=PASS), 3))
show("E L4 with reproduced and predicted typed PASS", lambda: claims.promote(cl(reproduced=PASS, predicted=PASS), 4))
show("E a facet whose source is one space", lambda: claims.promote(cl(demand={"verdict": PASS, "source": " "}), 1))
show("  level 0", lambda: claims.promote(cl(), 0))
show("  level 5", lambda: claims.promote(cl(), 5))
show("  level -3 with no custody facet", lambda: claims.promote(cl(drop="custody"), -3))
show("  kind unknown", lambda: claims.promote(dict(cl(), kind="STRUCTURE"), 1))
show("  kind missing", lambda: claims.promote({k: v for k, v in cl().items() if k != "kind"}, 1))
show("  render, kind unknown", lambda: claims.render(dict(cl(), kind="STRUCTURE")))
forged2 = dict(cl(), setting={"note": "see the paper"}, setting_sha256=claims.setting_hash({"note": "see the paper"}))
show("E a setting that is not the one registered, with the hash recomputed by the quoter", lambda: claims.render(forged2))
show("E a claim whose cell is one space", lambda: claims.render(dict(cl(), cell=" ")))
show("  render of a claim whose seven L1 facets all FAILED", lambda: claims.render(cl(**{f: FAIL for f in claims.L1})))
show("  setting not serialisable (a set)", lambda: claims.render(dict(cl(), setting={"s": {1, 2}})))
print("   level of a NESTED claim with typed facets:", claims.level(cl("NESTED")), "| ORIGIN:", claims.level(cl("ORIGIN")), "| LAW:", claims.level(cl("LAW")), "| ECONOMY:", claims.level(cl("ECONOMY")))
print("   nested facets of the registered SOUND NESTED claim and their sources:", {k: v["source"] for k, v in cl("NESTED")["facets"].items() if k in claims.KIND["NESTED"]})
