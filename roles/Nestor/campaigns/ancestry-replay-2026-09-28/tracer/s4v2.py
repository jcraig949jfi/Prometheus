"""s4 v2.2: CONFORMANCE REPAIR of v2.1 after its 2-replica review (review_s4v21/, Fabric tsk-5b65fada2d69 /
tsk-6e51a53bfbf6; both DOES NOT CONFORM, same blocking finding). Post-exposure, declared as such: the v2.1 tallies were
seen. Changes no threshold, floor, class key, sample, K or bootstrap seed; the tallies stay UNUSED until reviewed.
  V1 [B1]    gate = POINT ESTIMATE vs floor (PASS / FAIL / NO_DATA); MARGINAL is a separate mark = the 95% CI
             straddles the floor (C4.4, addendum 3 ruling 2). v2.1 let MARGINAL replace the decision.
  V2 [S1]    completeness universe includes the persisted flags fz/fc per side, flipped exactly as the frozen
             interventions.per_byte_arms does (interventions.py:305, :323-326).
  V3 [S2/S3] completeness unit = per unnamed BYTE as R5 / s4_run count it: a byte leaks if any of its K draws leaks; a
             byte is APPLICABLE if at least one of its K draws is applicable (path, acceptance and the write preserved).
             leak share = leaking bytes / applicable bytes. Per-draw figures are reported alongside, not gated.
  V4 [S2/N1] the completeness draws use a NEW deterministic stream (S4V2CA|SEED|run|child); the birth SUBSET is s4_run's
             (per_byte_sampled), the draws are not s4_run's draws. v2.1's "identical seeds" claim was false; retracted.
  V5 [S4/N5] rule-identified loci with NO usable dependence draws (q8c None) are counted and reported, with the coverage
             excluding them as a REPORTED sensitivity only (the gate stays on the literal R1 reading); ruling is Archaeon's.
  V6 [S5/N2] every statistic reports its cluster count (simulations with a nonzero denominator) and the number of
             bootstrap resamples dropped for a zero denominator; a 1-cluster statistic is marked SINGLE_CLUSTER.
  V7 [N6/N2] input guard: PRODUCTION_INDEX.json is checked against END_RECEIPT's sha256 and every births file against
             its index births_sha256 (LF-normalised); any mismatch -> REFUSED. Written sets in S4_RESULTS must equal the
             births files' written sets.
Not changed (reviewers' notes kept as notes): K_R1 tie ordering (ruling text: a tie in either majority -> TIED);
NO_MATERIAL counts kind "E" only (only E and C occur); '__ep' births files (none exist).

s4 v2.1 (adds the RULED class key K_R1, Archaeon GO_FINAL addendum 3 ruling 3; otherwise identical to v2).

s4 v2: CONFORMANCE REPAIR of the owner's s4 instrument tests (post-exposure; declared as such).

Why: the independent review of production run 2 (review_run2/, Fabric tsk-c62639a26351 / tsk-db7cff995c19) found
s4_run.py (68779d3e) does not conform. This module repairs conformance only. It changes no threshold, rule, sample,
seed or K. It does NOT edit any frozen file (interventions.py, s4_run.py and run_production.py stay byte-identical to
freeze v4 / GO_FINAL v2): it RECOMPUTES from the committed per-birth rows (exports/S4_RESULTS.jsonl, sha256 e232fd04...),
plus one NEW measurement (the completeness applicability count) made with the frozen engine through interventions.Run.
The tallies stay UNUSED until reviewed (GO_FINAL addendum 1). Nothing here computes a Q, a prediction or a verdict.

Repairs (review item):
  R-a identified = rule-identified ENTITY-MOVE AND flip under the GATING C7.2 PREFIX rule not FAILED AND R1 dependence
      changes == 0 (was: the strict flip rule)                                        [F6 / S1]
  R-b flip coverage = (CONFIRMED + FAILED) / RULE-IDENTIFIED MOVE loci, i.e. loci with R1 dependence changes == 0
      (was: / all flip-tested loci); also reported over all MOVE loci                 [S3]
  R-c classes (v5 R1): NO_MATERIAL (<= 10% of written loci ENTITY-labelled) is its own class and excluded from the
      identifiability denominator; TIED when the top performer counts tie; BOTH class keys are reported because the
      key is unruled (#924): K_DONOR (self = performer is the donor/writer) and K_EXEC (self = performer entity ==
      the store_by slice, as G2 used)                                                 [F2, F3, N3]
  R-d Q8c None (every draw suppressed) is counted as NO_USABLE_DRAWS, never as 0      [F8]
  R-e floors evaluated in code with a run-clustered bootstrap over the 9 distinct simulations (B = 2000, seed fixed
      here): PASS if the CI lies entirely on the passing side, FAIL if entirely on the failing side, else MARGINAL
      (C4.4). Flip coverage floor 0.50; FAILED share <= 0.01; completeness leak share <= 0.05 [F1, B2]
  R-f completeness applicability: on the SAME seeded 20% per-byte subset (identical selection hash and seeds as s4_run),
      every unnamed single-byte randomisation is classified APPLICABLE (path and birth preserved) or INAPPLICABLE; the
      leak share is over APPLICABLE draws only, and the applicability share is reported, so 0.0 is never read as
      evidence when nearly nothing was applicable                                    [F7]
  R-g unit guard: a record missing from PRODUCTION_INDEX is REFUSED (fail closed), not counted as distinct [N2]

    python s4v2.py           -> exports/S4V2_SUMMARY.json, exports/S4V2_COMPLETENESS.jsonl
"""
import hashlib, json, pathlib, random, sys
from collections import Counter, defaultdict
from multiprocessing import Pool

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
EXPORTS = HERE.parent / "exports"
SEED = 20260928                  # the s4_run seed, unchanged
K_BYTE = 4                       # unchanged
BOOT_B, BOOT_SEED = 2000, 20260929
FLOORS = {"flip_coverage": (0.50, "ge"), "flip_failed_share": (0.01, "le"), "completeness_leak_share": (0.05, "le")}
S4_RESULTS_SHA = "e232fd04cb4ae5a0b9044f4c92c140ada41019503c488f5ab08492227976f137"
INDEX_SHA = "f478ce0d88c3a575baf3e5aaca07896866fb55331f6e85e445d9b28a87481f10"      # END_RECEIPT.json


def lf_sha(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def h(s):
    return hashlib.sha256(s.encode()).hexdigest()


def class_of(loci, donor, key):
    written = [l for l in loci if l["written"]]
    if not written or sum(1 for l in written if l["kind"] == "E") <= 0.10 * len(written):
        return "NO_MATERIAL"
    if key == "K_R1":
        # v2.1 (Archaeon addendum 3, ruling 3): R1's executing organism = the slice organism (store_by). Per birth,
        # self iff the MAJORITY performer entity == the MAJORITY store_by entity; ties in either majority -> TIED;
        # a majority performer that is not an ENTITY -> none.
        pc = Counter(l["performer_ent"] if l["performer_ent"] else "none" for l in written)
        sc = Counter(l.get("store_by_ent") for l in written)
        pt, st = pc.most_common(), sc.most_common()
        if (len(pt) > 1 and pt[0][1] == pt[1][1]) or (len(st) > 1 and st[0][1] == st[1][1]):
            return "TIED"
        if pt[0][0] == "none":
            return "none"
        return "self" if pt[0][0] == st[0][0] else "other"
    c = Counter()
    for l in written:
        pe = l["performer_ent"]
        if pe is None:
            c["none"] += 1
        elif key == "K_DONOR":
            c["self" if pe == donor else "other"] += 1
        else:
            c["self" if pe == l.get("store_by_ent", pe) else "other"] += 1
    top = c.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return "TIED"
    return top[0][0]


def completeness_applicability(args):
    """R-f: unnamed single-byte randomisations on the frozen engine, classified by applicability."""
    import interventions as I
    import z8shadow as S
    rec = args
    key = "%s|%d" % (rec["run"], rec["child"])
    rng = random.Random(int(h("S4V2CA|%d|%s" % (SEED, key))[:16], 16))
    pre = I.Pre(rec)
    base = I.Run(pre)
    universe = [("T", s, i) for s in (0, 1) for i in range(len(pre.g[s]))]
    for s in (0, 1):
        if pre.regs[s] is not None:
            universe += [("R", s, r) for r in range(8)] + [("R", s, "fz"), ("R", s, "fc")]      # V2
    out = {"run": rec["run"], "child": rec["child"], "draws": 0, "applicable": 0, "leaks": 0,
           "bytes": 0, "bytes_applicable": 0, "bytes_leaking": 0}
    for j in range(pre.n):
        if not base.written(j):
            continue
        st = base.last[base.voff + j]
        named = I._named_bytes(S.deps(st.cell) | st.ctrl | st.exec_, pre)
        for u in universe:
            if u in named:
                continue
            b_app = b_leak = False
            for _k in range(K_BYTE):
                c = pre.copy()
                if u[0] == "T":
                    c.g[u[1]][u[2]] = rng.randrange(256)
                elif u[2] == "fz":                                   # as interventions.per_byte_arms
                    c.flags[u[1]] = (1 - c.flags[u[1]][0], c.flags[u[1]][1])
                elif u[2] == "fc":
                    c.flags[u[1]] = (c.flags[u[1]][0], 1 - c.flags[u[1]][1])
                else:
                    c.regs[u[1]][u[2]] = rng.randrange(256)
                r = I.Run(c)
                out["draws"] += 1
                if r.path == base.path and r.accepted and r.written(j):
                    out["applicable"] += 1
                    lk = r.victim[j] != base.victim[j]
                    out["leaks"] += lk
                    b_app = True
                    b_leak |= lk
            out["bytes"] += 1                                         # V3: the R5 unit
            out["bytes_applicable"] += b_app
            out["bytes_leaking"] += b_leak
    return out


def boot_ci(per_sim, stat):
    sims = sorted(per_sim)
    rng = random.Random(BOOT_SEED)
    vals = []
    for _ in range(BOOT_B):
        smp = [sims[rng.randrange(len(sims))] for _ in sims]
        v = stat([per_sim[s] for s in smp])
        if v is not None:
            vals.append(v)
    if not vals:
        return None, BOOT_B
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4)], BOOT_B - len(vals)


def gate(point, floor):
    """V1: the gate is the POINT ESTIMATE against the floor."""
    if point is None:
        return "NO_DATA"
    thr, kind = floor
    return ("PASS" if point >= thr else "FAIL") if kind == "ge" else ("PASS" if point <= thr else "FAIL")


def marginal(ci, floor):
    """V1: the MARGINAL mark = the 95% CI straddles the floor (both sides of it). A mark, never the decision."""
    if ci is None:
        return None
    thr, kind = floor
    lo, hi = ci
    return (lo < thr <= hi) if kind == "ge" else (lo <= thr < hi)


def main():
    raw = (EXPORTS / "S4_RESULTS.jsonl").read_bytes().replace(b"\r\n", b"\n")      # checkout may convert to CRLF
    if hashlib.sha256(raw).hexdigest() != S4_RESULTS_SHA:
        sys.exit("REFUSED: S4_RESULTS.jsonl is not the committed run-2 file")
    if lf_sha(EXPORTS / "PRODUCTION_INDEX.json") != INDEX_SHA:
        sys.exit("REFUSED: PRODUCTION_INDEX.json is not END_RECEIPT's (V7)")
    idx = json.loads((EXPORTS / "PRODUCTION_INDEX.json").read_text(encoding="utf-8"))
    births = {}
    for p in sorted(EXPORTS.glob("*.births.jsonl")):
        run = p.name[:-len(".births.jsonl")]
        if run not in idx or lf_sha(p) != idx[run]["births_sha256"]:
            sys.exit("REFUSED: %s does not match its PRODUCTION_INDEX births_sha256 (V7)" % p.name)
        for line in open(p, encoding="utf-8"):
            b = json.loads(line)
            births[(b["run"], b["child"])] = b
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
    for r in rows:
        if r["run"] not in idx:
            sys.exit("REFUSED: %s missing from PRODUCTION_INDEX (R-g)" % r["run"])
        b = births[(r["run"], r["child"])]
        sb = {st["j"]: st.get("store_side") for st in b["loci"] if st.get("written")}
        if set(sb) != {l["j"] for l in r["loci"] if l["written"]}:
            sys.exit("REFUSED: written sets differ between S4_RESULTS and births for %s|%s (V7)" % (r["run"], r["child"]))
        for l in r["loci"]:
            l["store_by_ent"] = sb.get(l["j"])
        r["donor"] = b["donor_side"]
        r["sim"] = idx[r["run"]]["sim_id"]
    distinct = [r for r in rows if not idx[r["run"]]["duplicate_of"]]
    sampled = [births[(r["run"], r["child"])] for r in distinct if r["per_byte_sampled"]]
    with Pool(8, maxtasksperchild=2) as pool:
        comp = pool.map(completeness_applicability, sampled, chunksize=1)
    with open(EXPORTS / "S4V2_COMPLETENESS.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for c in comp:
            f.write(json.dumps(c, sort_keys=True) + "\n")
    comp_by = {(c["run"], c["child"]): c for c in comp}
    summary = {"version": "s4v2.2", "repairs": "R-a..R-g, V1..V7 (docstring)", "index_sha256": INDEX_SHA,
               "completeness_draws": "NEW deterministic stream S4V2CA|SEED|run|child on s4_run's per_byte_sampled subset (V4)", "s4_results_sha256": S4_RESULTS_SHA, "boot": [BOOT_B, BOOT_SEED],
               "n_distinct_births": len(distinct), "n_duplicate_births": len(rows) - len(distinct), "keys": {}}
    for key in ("K_R1", "K_DONOR", "K_EXEC"):          # K_R1 = the RULED key (addendum 3); the others reported
        per_class = defaultdict(lambda: defaultdict(lambda: Counter()))
        for r in distinct:
            c = class_of(r["loci"], r["donor"], key)
            t = per_class[c][r["sim"]]
            t["births"] += 1
            for l in r["loci"]:
                if not l.get("flip_prefix"):
                    continue
                t["move_loci"] += 1
                rule_id = l.get("dep_changes") == 0
                t["rule_identified"] += rule_id
                if l.get("q8c") is None:
                    t["q8c_no_usable_draws"] += 1
                if rule_id:
                    t["cov_" + l["flip_prefix"]] += 1
                    if l.get("q8c") is None:                                # V5: rule-identified with no usable draws
                        t["rule_id_no_usable_draws"] += 1
                        t["nud_cov_" + l["flip_prefix"]] += 1
                    t["identified_prefix"] += l["flip_prefix"] != "FAILED"
            cc = comp_by.get((r["run"], r["child"]))
            if cc:
                t["ca_draws"] += cc["draws"]; t["ca_applicable"] += cc["applicable"]; t["ca_leaks"] += cc["leaks"]
                t["cb_bytes"] += cc["bytes"]; t["cb_applicable"] += cc["bytes_applicable"]
                t["cb_leaking"] += cc["bytes_leaking"]
        out = {}
        for c, sims in per_class.items():
            tot = Counter()
            for s in sims.values():
                tot.update(s)

            def cov(ts):
                a = sum(t["cov_CONFIRMED"] + t["cov_FAILED"] for t in ts); d = sum(t["rule_identified"] for t in ts)
                return a / d if d else None

            def fail(ts):
                a = sum(t["cov_FAILED"] for t in ts); d = sum(t["cov_CONFIRMED"] + t["cov_FAILED"] for t in ts)
                return a / d if d else None

            def leak(ts):                                   # V3: per byte, the gated unit
                a = sum(t["cb_leaking"] for t in ts); d = sum(t["cb_applicable"] for t in ts)
                return a / d if d else None

            def cov_excl_nud(ts):                           # V5: reported sensitivity only
                a = sum(t["cov_CONFIRMED"] + t["cov_FAILED"] - t["nud_cov_CONFIRMED"] - t["nud_cov_FAILED"] for t in ts)
                d = sum(t["rule_identified"] - t["rule_id_no_usable_draws"] for t in ts)
                return a / d if d else None
            den = {"flip_coverage": lambda t: t["rule_identified"],
                   "flip_failed_share": lambda t: t["cov_CONFIRMED"] + t["cov_FAILED"],
                   "completeness_leak_share": lambda t: t["cb_applicable"]}
            fn = {"flip_coverage": cov, "flip_failed_share": fail, "completeness_leak_share": leak}
            vs = list(sims.values())
            point, ci, dropped, clusters, gates, marks = {}, {}, {}, {}, {}, {}
            for k in FLOORS:
                point[k] = fn[k](vs)
                ci[k], dropped[k] = boot_ci(sims, fn[k])
                clusters[k] = sum(1 for t in vs if den[k](t) > 0)
                gates[k] = gate(point[k], FLOORS[k])
                marks[k] = [m for m in (("MARGINAL" if marginal(ci[k], FLOORS[k]) else None),
                                        ("SINGLE_CLUSTER" if clusters[k] == 1 else None)) if m]
            out[c] = {"n_sims": len(sims), "totals": dict(tot), "point": point,
                      "reported": {"completeness_applicability_share_bytes": (tot["cb_applicable"] / tot["cb_bytes"]) if tot["cb_bytes"] else None,
                                   "completeness_leak_share_draws": (tot["ca_leaks"] / tot["ca_applicable"]) if tot["ca_applicable"] else None,
                                   "completeness_applicability_share_draws": (tot["ca_applicable"] / tot["ca_draws"]) if tot["ca_draws"] else None,
                                   "flip_coverage_excluding_no_usable_draw_loci": cov_excl_nud(vs)},
                      "ci95_run_clustered": ci, "boot_resamples_dropped_zero_denominator": dropped,
                      "n_clusters": clusters, "gate": gates, "marks": marks}
        summary["keys"][key] = out
    summary["ruled_class_key"] = "K_R1 (addendum 3); K_DONOR and K_EXEC reported only"
    (EXPORTS / "S4V2_SUMMARY.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: {c: {g: [v["gate"][g]] + v["marks"][g] for g in FLOORS} for c, v in d.items()}
                      for k, d in summary["keys"].items()}))


if __name__ == "__main__":
    main()
