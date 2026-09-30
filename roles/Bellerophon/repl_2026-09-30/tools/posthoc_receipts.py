"""POST-HOC receipts for E-BEL-REPL-01 (added 2026-09-30 in answer to the two adversarial merge reviews tsk-ad966fa39590 /
tsk-750695b70564). It recomputes, from the sealed production files and the post-hoc replay file, every number that
RESULT.md s2 quotes outside production/ANALYSIS.json:
  - the FM/G trajectory (tick 0 and ticks 100/500/1000/2000 per arm);
  - the s2 table, with "founder threshold" DEFINED as any of: kmer4 >= 0.25, lcs >= 8, shift_id >= 16;
  - a PAIRED check (review F7): per pair, treatment event vs ZERO event; exact one-sided sign test on the discordant pairs;
  - the post-hoc planted controls of posthoc_k3_shift.measures (self, 5-byte rotation, random tape, 22 point mutations).
It feeds no gate and no verdict.
    python posthoc_receipts.py <production dir> <POSTHOC_K3_SHIFT.jsonl>  -> JSON on stdout
"""
import glob, json, math, random, statistics as st, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import repl_analysis as RA  # noqa: E402
import posthoc_k3_shift as P  # noqa: E402

THR = (("kmer4", 0.25), ("lcs", 8), ("shift_id", 16))


def sign_test(b, c):
    """P(X >= b) for X ~ Binomial(b + c, 0.5): b = pairs where only the treatment arm has an event, c = only ZERO."""
    n = b + c
    return sum(math.comb(n, k) for k in range(b, n + 1)) / 2 ** n if n else 1.0


def main(prod, ph):
    R = [json.loads(l) for f in sorted(glob.glob(str(pathlib.Path(prod) / "runs_*.jsonl"))) for l in open(f, encoding="utf-8")]
    out = {"trajectory": {}, "s2_table": {}, "paired": {}, "planted_controls": {}}
    c0 = [r["checkpoints"][0] for r in R]
    out["trajectory"]["tick0_mean"] = {k: round(st.mean(c[k] for c in c0), 4) for k in ("FM_share", "G_share", "L_share")}
    for arm in ("ZERO", "P90", "P75"):
        for t in (100, 500, 1000, 2000):
            cs = [c for r in R if r["arm"] == arm for c in r["checkpoints"] if c["tick"] == t and c["alive"] > 0]
            out["trajectory"]["%s@%d" % (arm, t)] = {"n_alive_runs": len(cs), "G_share": round(st.mean(c["G_share"] for c in cs), 4),
                                                      "FM_share": round(st.mean(c["FM_share"] for c in cs), 4)}
    H = [json.loads(l) for l in open(ph, encoding="utf-8")]
    for arm in ("ZERO", "P90", "P75"):
        rs = [r for r in H if r["arm"] == arm]
        gs = [g for r in rs for g in r["free_G"]]; nl = [g for r in rs for g in r["null_random"]]
        row = {"runs": len(rs), "genomes": len(gs), "replay_gate_pass": sum(r["replay_gate"] for r in rs)}
        for k in ("pos_id", "shift_id", "kmer4", "lcs"):
            row[k] = {"median": st.median(g[k] for g in gs), "max": max(g[k] for g in gs), "null_median": st.median(g[k] for g in nl),
                      "null_max": max(g[k] for g in nl)}
        row["runs_ge80pct_over_any_threshold"] = sum(
            sum(any(g[k] >= t for k, t in THR) for g in r["free_G"]) >= 0.8 * len(r["free_G"]) for r in rs)
        row["runs_any_genome_over_any_threshold"] = sum(any(any(g[k] >= t for k, t in THR) for g in r["free_G"]) for r in rs)
        out["s2_table"][arm] = row
    ev = {(r["arm"], r["pair"]): RA.score(r)["event"] for r in R}
    for t in ("P90", "P75"):
        b = sum(ev[(t, s)] and not ev[("ZERO", s)] for s in range(100)); c = sum(ev[("ZERO", s)] and not ev[(t, s)] for s in range(100))
        both = sum(ev[(t, s)] and ev[("ZERO", s)] for s in range(100))
        out["paired"][t + "_vs_ZERO"] = {"only_treatment": b, "only_ZERO": c, "both": both, "sign_test_one_sided_p": sign_test(b, c)}
    Rg = random.Random(1); f = bytes(Rg.randrange(256) for _ in range(64)); r = bytes(Rg.randrange(256) for _ in range(64))
    m = bytearray(f)
    for i in range(0, 64, 3):
        m[i] = Rg.randrange(256)
    out["planted_controls"] = {"self": P.measures(f, f), "rot5": P.measures(f[5:] + f[:5], f), "random": P.measures(r, f),
                               "22_point_mutations": P.measures(bytes(m), f)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
