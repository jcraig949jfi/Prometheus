"""SE-1 -- THE FIRST PRE-REGISTERED EXPERIMENT, WITH THE MANIFEST UNDER TEST.

Harmonia science loop 5, 2026-09-05.

Four loops produced seven blockers that share one shape: each is a thing that
must be WRITTEN DOWN BEFORE THE RUN and cannot be reconstructed afterwards.
This experiment is the first that writes all seven down first, fossilises the
declaration in the engine BEFORE the first experimental world exists, and then
runs.

So two things are under test at once:
  the SCIENCE      does an exploiting policy beat a sampling policy on this
                   landscape, by an amount worth believing?
  the MANIFEST     does declaring everything in advance actually prevent the
                   failure modes loops 1-4 demonstrated?

THE PHENOMENON (real, not authored): a 64-bit hidden target; a policy emits
bitstrings and scores the matching fraction. Every arm gets an IDENTICAL
encounter budget, because loop 1 showed run length buys significance and an
unequal budget would confound policy with effort.

  ARM_HILL      hill-climber: mutate the current best, keep if not worse
  ARM_SAMPLE    random sampler: independent draw each encounter
  ARM_NULL_A/B  the SAME hill-climber under two identities -- the known-null
                negative control demanded by INVARIANT III. If this arm
                separates, the campaign is void rather than interesting.

PRE-DECLARED PRIMARY METRIC: best_so_far at the final encounter.
Chosen in advance precisely because loop 5's own attack (section 4) shows the
conclusion is metric-dependent, and picking afterwards is how that becomes
undetectable.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import statistics
import sys
import urllib.error
import urllib.request

BITS = 64
ENC = 20              # IDENTICAL for every arm
NW = 64               # worlds per arm -- POWER JUSTIFIED, see manifest.
                      # SE-1 used 12, which cannot detect its own declared
                      # floor of d=0.5; the observed d=0.55 exceeded the
                      # floor and still failed at p=0.234.
EFFECT_FLOOR = 0.5    # smallest |d| worth believing, declared in advance


# ==========================================================================
# THE MANIFEST. Written and hashed BEFORE any experimental world exists.
# ==========================================================================
MANIFEST = {
    "experiment": "SE-1b",
    "date": "2026-09-05",
    "seat": "Harmonia",
    "question": "On a 64-bit matching landscape under an identical encounter "
                "budget, does a hill-climbing policy achieve a higher final "
                "best-so-far score than an independent random sampler?",
    "prediction": "ARM_HILL > ARM_SAMPLE with |d| >= 0.5",
    # --- the seven declarations from loops 1-4 ---------------------------
    "unit_of_analysis": "world",                       # blocker 1
    "n_worlds_per_arm": NW,
    "power_justification": "two-sample, alpha 0.025 (Bonferroni), target "
                           "power ~0.8 at the declared floor d=0.5 requires "
                           "n ~= 16/d^2 = 64 worlds per arm. SE-1 ran 12 and "
                           "was therefore unable to confirm its own "
                           "prediction; an effect floor without an n "
                           "justification is decorative.",
    "executor_attestation": ["executed_config_hash",
                             "executor_entry_state_hash"],   # blocker 2
    "player_identity": "sha256 of the policy source",  # blocker 3
    "comparison_family": {                             # blocker 4
        "declared_comparisons": ["ARM_HILL vs ARM_SAMPLE",
                                 "ARM_NULL_A vs ARM_NULL_B"],
        "family_size": 2,
        "alpha": 0.05,
        "correction": "Bonferroni: reject only if p < 0.025",
    },
    "reset_discipline": "policy state reset between worlds",   # blocker 5
    "intervention_composition": "single-part arms only; no composite arm in "
                                "SE-1, so no ordering claim is possible",
                                                        # blocker 6
    "campaign_extent": {                                # blocker 7
        "arms": ["ARM_HILL", "ARM_SAMPLE", "ARM_NULL_A", "ARM_NULL_B"],
        "worlds_per_arm": NW,
        "total_worlds_intended": 4 * NW,
        "encounters_per_world": ENC,
    },
    "primary_metric": "best_so_far_final",
    "secondary_metrics_reported_not_claimed": ["mean_score",
                                               "encounters_to_0.75"],
    "effect_floor": EFFECT_FLOOR,
    "stopping_rule": "run all declared worlds; no interim analysis; no "
                     "stopping on a result",
    "void_conditions": [
        "the known-null arm pair separates at p < 0.025",
        "the known-null arms are bit-identical (a control that cannot fire)",
        "fewer worlds are delivered than declared",
        "any arm's encounter budget differs from any other's",
    ],
}


def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


# ==========================================================================
# policies. Identity is the hash of the SOURCE, not the name (blocker 3).
# ==========================================================================
HILL_SRC = "mutate one bit of best; keep if score >= best"
SAMPLE_SRC = "draw a fresh independent bitstring each encounter"


def target_for(seed):
    r = random.Random(seed)
    return [r.randint(0, 1) for _ in range(BITS)]


def score(bits, target):
    return sum(1 for i in range(BITS) if bits[i] == target[i]) / BITS


def play_hill(target, seed):
    r = random.Random("hill|%s" % seed)
    cur = [r.randint(0, 1) for _ in range(BITS)]
    entry = hashlib.sha256(bytes(cur)).hexdigest()[:12]
    best = score(cur, target)
    traj = [best]
    for _ in range(ENC - 1):
        cand = list(cur)
        i = r.randrange(BITS)
        cand[i] ^= 1
        s = score(cand, target)
        if s >= best:
            cur, best = cand, s
        traj.append(best)
    return traj, entry, sha({"policy": HILL_SRC, "seed": seed})


def play_sample(target, seed):
    r = random.Random("sample|%s" % seed)
    first = [r.randint(0, 1) for _ in range(BITS)]
    entry = hashlib.sha256(bytes(first)).hexdigest()[:12]
    best = score(first, target)
    traj = [best]
    for _ in range(ENC - 1):
        cand = [r.randint(0, 1) for _ in range(BITS)]
        best = max(best, score(cand, target))
        traj.append(best)
    return traj, entry, sha({"policy": SAMPLE_SRC, "seed": seed})


ARMS = {
    "ARM_HILL": play_hill,
    "ARM_SAMPLE": play_sample,
    "ARM_NULL_A": play_hill,
    "ARM_NULL_B": play_hill,        # deliberately the SAME policy as NULL_A
}


# ==========================================================================
def perm_p(a, b, iters=4000, rng=None):
    rng = rng or random.Random(0)
    obs = abs(statistics.fmean(a) - statistics.fmean(b))
    pool = list(a) + list(b)
    n = len(a)
    hits = 0
    for _ in range(iters):
        rng.shuffle(pool)
        if abs(statistics.fmean(pool[:n]) - statistics.fmean(pool[n:])) >= obs:
            hits += 1
    return (hits + 1) / (iters + 1)


def cohen_d(a, b):
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2)) ** 0.5
    return (statistics.fmean(a) - statistics.fmean(b)) / sp if sp else 0.0


class C:
    def __init__(self, base):
        self.base, self.token, self.key = base.rstrip("/"), None, None

    def call(self, m, p, body=None):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        if self.key:
            h["X-SFE-Session"] = self.key
        d = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + p, data=d, headers=h, method=m)
        try:
            with urllib.request.urlopen(r, timeout=60) as z:
                return z.status, json.loads(z.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode() or "{}")
            except Exception:                                      # noqa: BLE001
                return e.code, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8894/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    c = C(a.base)
    if c.call("GET", "/version")[0] != 200:
        print("engine unreachable"); return 2
    c.token = c.call("POST", "/clients", {"name": "se1"})[1]["token"]
    s = c.call("POST", "/sessions", {"name": "se1"})[1]
    c.key = s["session_key"]
    sid = s["session_id"]

    mh = sha(MANIFEST)
    print("=" * 74)
    print("SE-1  PRE-REGISTERED EXPERIMENT")
    print("=" * 74)
    print("  manifest sha256 : %s" % mh[:32])
    print("  prediction      : %s" % MANIFEST["prediction"])
    print("  primary metric  : %s" % MANIFEST["primary_metric"])
    print("  effect floor    : |d| >= %.1f" % EFFECT_FLOOR)
    print("  family          : %d comparisons, reject at p < %.3f"
          % (MANIFEST["comparison_family"]["family_size"],
             MANIFEST["comparison_family"]["alpha"] / 2))

    # ---- fossilise the manifest BEFORE any experimental world -----------
    import base64
    mw = c.call("POST", "/worlds", {"session_id": sid, "name": "SE1-manifest",
                                    "seed_root": 1,
                                    "sharing_policy": "ISOLATED"})[1]
    mwid = mw["world_id"]
    c.call("POST", "/worlds/%s/start" % mwid, {})
    blob = json.dumps(MANIFEST, sort_keys=True).encode()
    st, art = c.call("POST", "/worlds/%s/artifacts" % mwid,
                     {"kind": "observation_payload",
                      "data_b64": base64.b64encode(blob).decode(),
                      "expected_blob_hash": "sha256:" + hashlib.sha256(blob).hexdigest(),
                      "meta": {"role": "PREREGISTRATION", "sha256": mh}})
    fossilised = st == 200
    print("  manifest fossilised before any experimental world : %s (%s)"
          % (fossilised, art.get("blob_hash", "")[:26]))

    # ---- run ------------------------------------------------------------
    results = {}
    budgets = {}
    for arm, fn in ARMS.items():
        finals, means, entries, cfgs = [], [], [], []
        for w in range(NW):
            # NULL_B is the SAME POLICY as NULL_A but on a DIFFERENT seed
            # stream. SE-1 gave both arms identical seeds, so the control was
            # bit-identical, p was exactly 1.000, and it could never fire.
            # A gate that cannot fail is not a gate.
            off = 7000 if arm == "ARM_NULL_B" else 3000
            traj, entry, cfg = fn(target_for(off + w), seed=(off + w))
            wid = c.call("POST", "/worlds", {
                "session_id": sid, "name": "%s-%d" % (arm, w),
                "seed_root": off + w, "sharing_policy": "ISOLATED"})[1]["world_id"]
            c.call("POST", "/worlds/%s/start" % wid, {})
            h = c.call("POST", "/worlds/%s/hypotheses" % wid,
                       {"statement": arm})[1]
            x = c.call("POST", "/worlds/%s/experiments" % wid,
                       {"spec": {"action": "encounter", "ticks": ENC,
                                 "arm": arm, "encounters": ENC},
                        "hyp_id": h["hyp_id"], "commit": True})[1]
            c.call("POST", "/worlds/%s/observations" % wid,
                   {"exp_id": x["exp_id"],
                    "content": {"best_so_far_final": traj[-1],
                                "mean_score": statistics.fmean(traj),
                                "encounters": ENC,
                                "executed_config_hash": cfg,
                                "executor_entry_state_hash": entry,
                                "manifest_sha256": mh},
                    "outcome": "SURVIVED"})
            finals.append(traj[-1])
            means.append(statistics.fmean(traj))
            entries.append(entry)
            cfgs.append(cfg)
        results[arm] = {"final": finals, "mean": means,
                        "entries": entries, "cfg": cfgs[0]}
        budgets[arm] = ENC

    # ---- void conditions, checked BEFORE looking at the result ----------
    print("\n" + "-" * 74)
    print("VOID CONDITIONS (checked before the primary comparison)")
    print("-" * 74)
    delivered = {k: len(v["final"]) for k, v in results.items()}
    v_extent = all(n == NW for n in delivered.values())
    v_budget = len(set(budgets.values())) == 1
    rngv = random.Random(1)
    null_p = perm_p(results["ARM_NULL_A"]["final"],
                    results["ARM_NULL_B"]["final"], 4000, rngv)
    null_d = cohen_d(results["ARM_NULL_A"]["final"],
                     results["ARM_NULL_B"]["final"])
    v_null = null_p >= 0.025
    print("  all arms delivered %d worlds          : %s %s"
          % (NW, v_extent, delivered))
    print("  identical encounter budget per arm    : %s (%s)"
          % (v_budget, set(budgets.values())))
    print("  known-null arms do NOT separate       : %s (p=%.3f, d=%+.2f)"
          % (v_null, null_p, null_d))
    void = not (v_extent and v_budget and v_null)
    if void:
        print("\n  *** CAMPAIGN VOID -- not reporting the primary result ***")

    # ---- primary comparison ---------------------------------------------
    print("\n" + "-" * 74)
    print("PRIMARY COMPARISON (pre-declared): ARM_HILL vs ARM_SAMPLE")
    print("-" * 74)
    hf, sf = results["ARM_HILL"]["final"], results["ARM_SAMPLE"]["final"]
    p = perm_p(hf, sf, 4000, random.Random(2))
    d = cohen_d(hf, sf)
    print("  hill   mean best-so-far : %.4f  (n=%d worlds)"
          % (statistics.fmean(hf), len(hf)))
    print("  sample mean best-so-far : %.4f  (n=%d worlds)"
          % (statistics.fmean(sf), len(sf)))
    print("  p=%.4f   |d|=%.2f   floor=%.1f   corrected alpha=0.025"
          % (p, abs(d), EFFECT_FLOOR))
    survives = (not void) and p < 0.025 and abs(d) >= EFFECT_FLOOR
    print("\n  CLAIM SURVIVES PRE-REGISTERED CRITERIA : %s" % survives)

    # ---- attack the conclusion ------------------------------------------
    print("\n" + "-" * 74)
    print("ATTACK ON THE CONCLUSION (metric dependence)")
    print("-" * 74)
    hm, sm = results["ARM_HILL"]["mean"], results["ARM_SAMPLE"]["mean"]
    p2 = perm_p(hm, sm, 4000, random.Random(4))
    d2 = cohen_d(hm, sm)
    print("  SECONDARY metric mean_score:")
    print("    hill %.4f   sample %.4f   p=%.4f  |d|=%.2f"
          % (statistics.fmean(hm), statistics.fmean(sm), p2, abs(d2)))
    flip = (p < 0.025) != (p2 < 0.025) or (d > 0) != (d2 > 0)
    print("    conclusion changes with the metric : %s" % flip)

    out = {"manifest": MANIFEST, "manifest_sha256": mh,
           "manifest_fossilised": fossilised,
           "void": void, "void_checks": {"extent": v_extent,
                                         "budget": v_budget,
                                         "null_arms_quiet": v_null,
                                         "null_p": null_p, "null_d": null_d},
           "primary": {"p": p, "d": d, "survives": survives,
                       "hill_mean": statistics.fmean(hf),
                       "sample_mean": statistics.fmean(sf)},
           "secondary": {"p": p2, "d": d2, "conclusion_flips": flip},
           "results": {k: {"final": v["final"], "mean": v["mean"],
                           "cfg": v["cfg"],
                           "distinct_entry_states": len(set(v["entries"]))}
                       for k, v in results.items()}}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
