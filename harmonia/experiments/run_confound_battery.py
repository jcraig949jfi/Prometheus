"""Confound-control battery for the Opus<Sonnet R2/R5 inversion (EXPERIMENTAL).

Before promoting "execution-control is a distinct axis" we kill the confounds the
frontier reviewers flagged:

  C-THINK : adaptive thinking lets each model self-allocate compute. Re-run Opus on
            R2+R5 at PINNED effort {low, high, max} (same probes across levels). If
            accuracy climbs toward Sonnet's 1.00 as effort rises, the gap was
            thinking-ALLOCATION, not a latent execution axis. Sonnet@high = reference.
  C-FORMAT: R2 (execution) was free-gen; R8 (recognition) was multiple-choice, so the
            split is confounded with format. Run Opus & Sonnet on the SAME legality
            skill in a STRUCTURED form (sqrt_label: label given candidate roots
            valid/invalid). If Opus recovers to Sonnet's level when structured, the
            R2 gap was free-gen FORMAT, not execution-control.
  C-POWER : Wilson 95% CIs on every proportion (R5 was 5/40 — edge of significance).

C-MEMO (procedural NON-canonical families) is the remaining control — deferred; needs
new problem families, noted for the next sprint.

Usage: python harmonia/experiments/run_confound_battery.py [N_THINK] [N_FMT]
"""
import sys, random, math
import numpy as np

sys.path.insert(0, "harmonia/experiments")
from reasoning_phase0 import gen_R2, gen_R5, gen_sqrt_label, grade
from reasoners_llm import make_opus_reasoner

N_THINK = int(sys.argv[1]) if len(sys.argv) > 1 else 12
N_FMT = int(sys.argv[2]) if len(sys.argv) > 2 else 15


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def run(model, probes, use_thinking=True, effort=None):
    log = []
    r = make_opus_reasoner(model=model, use_thinking=use_thinking, effort=effort, call_log=log)
    res = []
    for p in probes:
        ans, tr = r(p)
        _v, ok = grade(p, ans, tr)
        res.append(bool(ok))
    perr = len([c for c in log if c.get("parse_error")])
    return res, perr


def line(label, res, perr):
    k, n = sum(res), len(res)
    lo, hi = wilson(k, n)
    print(f"  {label:34s} acc={k}/{n}={k/max(1,n):.2f}  95%CI=[{lo:.2f},{hi:.2f}]  failures={perr}")


def main():
    rng = random.Random(20260529)
    # ---- C-THINK probes (same set reused across effort levels) ----
    def sample(gen, n):
        allp = gen(rng); rng.shuffle(allp); picked = allp[:n]
        for i, p in enumerate(picked):
            p.data["phrasing"] = i % 3
        return picked
    r2 = sample(gen_R2, N_THINK)
    r5 = sample(gen_R5, N_THINK)

    print(f"CONFOUND BATTERY | N_THINK={N_THINK} N_FMT={N_FMT}")
    print("\n===== C-THINK: Opus 4.8 effort dose-response (same probes across levels) =====")
    print("(if Opus accuracy rises toward Sonnet's 1.00 as effort increases => allocation artifact)")
    for effort in ("low", "high", "max"):
        for tier, probes in (("R2", r2), ("R5", r5)):
            res, perr = run("claude-opus-4-8", probes, effort=effort)
            line(f"Opus@{effort:4s} {tier}", res, perr)
    print("  -- reference --")
    for tier, probes in (("R2", r2), ("R5", r5)):
        res, perr = run("claude-sonnet-4-6", probes, effort="high")
        line(f"Sonnet@high {tier}", res, perr)

    # ---- C-FORMAT probes ----
    r2f = sample(gen_R2, N_FMT)
    cf = sample(gen_sqrt_label, N_FMT)
    print("\n===== C-FORMAT: free-gen R2 vs STRUCTURED sqrt_label (same legality skill) =====")
    print("(if Opus's free-gen<Sonnet but structured Opus≈Sonnet => the R2 gap was FORMAT, not execution)")
    for model in ("claude-opus-4-8", "claude-sonnet-4-6"):
        for label, probes in (("R2-freegen", r2f), ("sqrt_label-structured", cf)):
            res, perr = run(model, probes)
            line(f"{model.split('-')[1]}-{model.split('-')[2]} {label}", res, perr)

    print("\nREAD:")
    print("  C-THINK kill: Opus@max ≈ 1.00 on R2/R5  => inversion was thinking-allocation, demote to default-policy claim.")
    print("  C-THINK survive: Opus@max still < Sonnet => not just thinking budget.")
    print("  C-FORMAT kill: Opus structured ≈ Sonnet while free-gen < Sonnet => mislabeled format sensitivity.")
    print("  C-FORMAT survive: Opus < Sonnet on the structured legality check too => execution-control, not format.")
    print("  C-MEMO still owed: procedural non-canonical R2/R5 families.")


if __name__ == "__main__":
    main()
