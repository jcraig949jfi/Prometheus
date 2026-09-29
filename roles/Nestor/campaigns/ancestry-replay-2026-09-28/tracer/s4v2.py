"""s4 v2.1 (adds the RULED class key K_R1, Archaeon GO_FINAL addendum 3 ruling 3; otherwise identical to v2).

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
            universe += [("R", s, r) for r in range(8)]
    out = {"run": rec["run"], "child": rec["child"], "draws": 0, "applicable": 0, "leaks": 0}
    for j in range(pre.n):
        if not base.written(j):
            continue
        st = base.last[base.voff + j]
        named = I._named_bytes(S.deps(st.cell) | st.ctrl | st.exec_, pre)
        for u in universe:
            if u in named:
                continue
            for _k in range(K_BYTE):
                c = pre.copy()
                if u[0] == "T":
                    c.g[u[1]][u[2]] = rng.randrange(256)
                else:
                    c.regs[u[1]][u[2]] = rng.randrange(256)
                r = I.Run(c)
                out["draws"] += 1
                if r.path == base.path and r.accepted and r.written(j):
                    out["applicable"] += 1
                    out["leaks"] += r.victim[j] != base.victim[j]
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
        return None
    vals.sort()
    return [round(vals[int(0.025 * len(vals))], 4), round(vals[int(0.975 * len(vals)) - 1], 4)]


def verdict(ci, floor):
    if ci is None:
        return "NO_DATA"
    thr, kind = floor
    lo, hi = ci
    if kind == "ge":
        return "PASS" if lo >= thr else ("FAIL" if hi < thr else "MARGINAL")
    return "PASS" if hi <= thr else ("FAIL" if lo > thr else "MARGINAL")


def main():
    raw = (EXPORTS / "S4_RESULTS.jsonl").read_bytes().replace(b"\r\n", b"\n")      # checkout may convert to CRLF
    if hashlib.sha256(raw).hexdigest() != S4_RESULTS_SHA:
        sys.exit("REFUSED: S4_RESULTS.jsonl is not the committed run-2 file")
    idx = json.loads((EXPORTS / "PRODUCTION_INDEX.json").read_text(encoding="utf-8"))
    births = {}
    for p in sorted(EXPORTS.glob("*.births.jsonl")):
        for line in open(p, encoding="utf-8"):
            b = json.loads(line)
            births[(b["run"], b["child"])] = b
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
    for r in rows:
        if r["run"] not in idx:
            sys.exit("REFUSED: %s missing from PRODUCTION_INDEX (R-g)" % r["run"])
        b = births[(r["run"], r["child"])]
        sb = {st["j"]: st.get("store_side") for st in b["loci"] if st.get("written")}
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
    summary = {"repairs": "R-a..R-g (docstring)", "s4_results_sha256": S4_RESULTS_SHA, "boot": [BOOT_B, BOOT_SEED],
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
                    t["identified_prefix"] += l["flip_prefix"] != "FAILED"
            cc = comp_by.get((r["run"], r["child"]))
            if cc:
                t["ca_draws"] += cc["draws"]; t["ca_applicable"] += cc["applicable"]; t["ca_leaks"] += cc["leaks"]
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

            def leak(ts):
                a = sum(t["ca_leaks"] for t in ts); d = sum(t["ca_applicable"] for t in ts)
                return a / d if d else None
            ci = {"flip_coverage": boot_ci(sims, cov), "flip_failed_share": boot_ci(sims, fail),
                  "completeness_leak_share": boot_ci(sims, leak)}
            out[c] = {"n_sims": len(sims), "totals": dict(tot),
                      "point": {"flip_coverage": cov(list(sims.values())), "flip_failed_share": fail(list(sims.values())),
                                "completeness_leak_share": leak(list(sims.values())),
                                "completeness_applicability_share": (tot["ca_applicable"] / tot["ca_draws"]) if tot["ca_draws"] else None},
                      "ci95_run_clustered": ci, "floor_verdict": {k: verdict(ci[k], FLOORS[k]) for k in FLOORS}}
        summary["keys"][key] = out
    summary["ruled_class_key"] = "K_R1 (addendum 3); K_DONOR and K_EXEC reported only"
    (EXPORTS / "S4V2_SUMMARY.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: {c: v["floor_verdict"] for c, v in d.items()} for k, d in summary["keys"].items()}))


if __name__ == "__main__":
    main()
