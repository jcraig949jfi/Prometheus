"""The reader's cases against the first version, carried over to the CURRENT harness (API adapted, fault unchanged)."""
import sys, pathlib, json, copy
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "harness"))
from rso_harness import meta, audits, claims, registration, stats, rulers, retain1, search, torture
from rso_harness.verdict import *
CF = meta.COUNTERFEIT
R = retain1
out = {"E": [], "S": []}


def show(kind, n, tag, thunk):
    try:
        v = thunk().verdict
    except Exception as e:
        v = "RAISES " + type(e).__name__
    out[kind].append((n, tag, v))
    print("%s%-3d %-96s -> %s" % (kind, n, tag[:96], v))


c = meta.cell
print("######## the reader's 12 sound cases, on the current harness")
show("S", 1, "no design runs were made, design_seeds=[]", lambda: registration.check_cell(c(design_seeds=[])))
show("S", 2, "zero exposure declared as {}", lambda: registration.check_cell(c(exposure={})))
show("S", 3, "same clock tick ran_at == registered_at", lambda: registration.check_receipt(c(), meta.run_receipt(ran_at=100), meta.SOURCE))
a = dict(audits.RUN3)
b = dict(audits.RUN3, parts_shared=True)
show("S", 4, "same setting worded differently in the two runs", lambda: audits.audit_contrast("parts_shared", a, dict(b, cost="tasks until a procedure is accepted (8 passes in a row), no cut-off")))
show("S", 5, "sound positive, 16 seeds", lambda: rulers.entry_gate("REGISTER", R.PANEL, list(range(1000, 1016))))
show("S", 6, "sound positive, 19 seeds", lambda: rulers.entry_gate("REGISTER", R.PANEL, list(range(1000, 1019))))
five = dict(R.PANEL, CHEMISTRY=(None, None))
show("S", 7, "CLASS_EXCLUSION SHARED, right on 4 physics, a 5th registered with no organism", lambda: rulers.neutrality_gate("CLASS_EXCLUSION", rulers.exclusion_ruler, "SHARED", five, meta.SEEDS))
show("S", 8, "null stated as a bound on reach, not impossibility (now the scope field)", lambda: search.check_report(meta.null()))
show("S", 9, "bound rounded to four places", lambda: search.check_report(meta.null(upper_bound=round(stats.zero_hit_upper(len(meta.REPORTED)), 4))))
show("S", 10, "a more cautious bound (99%)", lambda: search.check_report(meta.null(upper_bound=stats.zero_hit_upper(len(meta.REPORTED), 0.99))))
capped = [{"naive_B": 400, "dev_B": 40, "lesion_B": 400, "sham_B": 41 + i % 2} for i in range(24)]
show("S", 11, "separate computations that both hit a 400-task cap (naive, lesion)", lambda: audits.audit_arms(capped, ("naive_B", "dev_B", "lesion_B", "sham_B")))
show("S", 12, "a neutral sham at small counts (3 intact, 4 after the sham)", lambda: audits.audit_sham([{"dev_B": 3, "sham_B": 4} for _ in range(24)], {"GOOD": 24, "BAD": 0}))

print("######## the reader's broken cases that the first version passed, G9 to G12 (rows 10-25, 69-71 of the replay receipt)")
K = audits.KEYS
show("E", 10, "kit rows whose receipts are unrelated files that exist", lambda: audits.ruler_status("BITS", "BITS@KEYS", CF, [(m, s, ("README.md",) + src[1:], an) for m, s, src, an in audits.RUNS]))
kit11 = [("GENUINE_LEARNED_UPDATER", "S19@RUN2", (K, "keys", "ACQUIRER(16)"), {"STRONG": "POSITIVE"})] + [
    (m, "S19@RUN2", (audits.G1, "v01", "MATURATION"), {"STRONG": "NEGATIVE"})
    for m in ("WORLD_PARKING", "NESTED_COMPILER_CARGO", "HIERARCHICAL_SELECTOR", "FLATTENED_EQUIVALENT")]
show("E", 11, "strong claim: a 'positive' and four members merely pointed at existing receipts", lambda: audits.ruler_status("STRONG", "S19@RUN2", CF, kit11, {}))
OK = meta.SETTING_OK
show("E", 13, "power registered as 0.2", lambda: audits.audit_setting(dict(audits.RUN2, power=0.2, amortization_horizon="three")))
show("E", 14, "power 'not computed', horizon 'n/a'", lambda: audits.audit_setting(dict(audits.RUN2, power="not computed", amortization_horizon="n/a")))
show("E", 15, "every field is the string 'tbd'", lambda: audits.audit_setting({k: "tbd" for k in audits.SETTING}))
show("E", 16, "two things change, one of them not in the dictionary", lambda: audits.audit_contrast("parts_shared", a, b))
cu, side = meta.custody, meta.side
show("E", 17, "same generator, a different hash typed in (was: renamed)", lambda: claims.check_custody(cu(discovery=dict(seeds=[1, 2, 3], panel_sha256="d" * 64, generator_sha256="a" * 64), confirmation=side(generator_sha256="A" * 64))))
show("E", 18, "confirmation with no seeds at all", lambda: claims.check_custody(cu(confirmation=side(seeds=[]))))
show("E", 19, "world filter chosen after design runs (still no field for it)", lambda: claims.check_custody(cu(world_filter="chosen after design runs")))
show("E", 20, "same custodian holds discovery and confirmation", lambda: claims.check_custody(cu(confirmation_custodian="tuner")))
show("E", 21, "tuning_evaluations negative", lambda: claims.check_custody(cu(tuning_evaluations=-5)))
show("E", 22, "a structure claim whose exact_null facet is simply asserted PASS", lambda: claims.promote(meta.claim(kind="TRANSFER"), 2))
show("E", 23, "L3 with reproduced asserted", lambda: claims.promote(meta.claim(reproduced=PASS), 3))
show("E", 24, "render with a setting that is not the registered one", lambda: claims.render(dict(meta.claim(), setting={"note": "see the paper"})))
show("E", 25, "render of a claim whose facets all FAILED", lambda: claims.render(meta.claim(**{f: FAIL for f in claims.L1})))
r3 = meta.run3()
show("E", 69, "run 3 arms, one replicate of 24 nudged", lambda: audits.audit_arms(meta.nudged(r3["STRATEGIST"]["replicates"]), meta.ARMS3))
show("E", 70, "one catch-all cell where nothing works", lambda: audits.audit_clauses(meta.toy_cells(**meta.CATCH_ALL), meta.toy_clauses))
t3 = audits.clause_table(r3, audits.clauses_run3)
rigged = dict(t3["NESTING.sham_harmless"], FIRE_TEST_WITH_A_DIFFERENT_HARMFUL_SHAM=0)
show("E", 71, "run 3 idle sham + one cell in which another operation is called sham", lambda: audits.audit_sham(r3["STRATEGIST"]["replicates"], rigged))

print("######## a few of the reader's broken cases outside G9-G12 (one line each; the other reviewer covers these gates)")
show("E", 7, "cell whose world text says 16 episodes while the table counts 24", lambda: registration.check_cell(c(world="RETAIN-1 gap 6, 16 episodes")))
show("E", 26, "positive declared at 1.0, n=20 (minimum reachable)", lambda: stats.preflight(20, 0.5, 1e-6, 1.0))
for f in (0.95, 0.9, 0.8, 0.7, 0.6):
    show("E", 48, "estimator that ran %d%% of the registered budget" % round(100 * f), lambda: search.calibration("NEEDLE", "NEUTRAL", meta.BUDGET, "COLD", meta.FOUNDERS, 0, meta.short_budget(f)))
for k in (2, 6, 12, 20, 24, 28, 40):
    show("E", 54, "estimator that adds %d phantom hits of 256" % k, lambda: search.calibration("NEEDLE", "NEUTRAL", meta.BUDGET, "COLD", meta.FOUNDERS, 0, meta.phantom(k)))
g0 = stats.khash(4000, 0) % len(search.FOUNDERS)
same = [s for s in range(4000, 400000) if stats.khash(s, 0) % len(search.FOUNDERS) == g0][:128]
rep = meta.report()
rep = dict(rep, policies={"NEUTRAL": {"seeds": same, "hits": search.sample_reach("NEEDLE", "NEUTRAL", meta.BUDGET, "COLD", same)}})
show("E", 65, "128 founders 'independent' by seed, all starting from one genome (%d seeds found)" % len(same), lambda: search.check_report(rep))
print()
print("SOUND: still not PASS on the current harness:", [(n, v) for n, t, v in out["S"] if v != PASS])
inscope = [(n, v) for n, t, v in out["E"] if 10 <= n <= 25 or n >= 69]
print("BROKEN, G9-G12 rows: still PASS on the current harness:", [n for n, v in inscope if v == PASS], "of", len(inscope), "rows ported")
