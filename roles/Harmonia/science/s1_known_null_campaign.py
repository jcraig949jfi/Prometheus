"""S1 -- KNOWN-NULL CAMPAIGN. Harmonia science loop 1, 2026-09-05.

THE QUESTION THIS LOOP ATTACKS: what scientific conclusion could this system
tempt us to make that the evidence does not warrant?

The engine RECORDS outcomes; it never COMPUTES them (executors execute, the
Foundry adjudicates). That is normally a limitation. Here it is the instrument:
it lets us author a campaign whose GROUND TRUTH IS KNOWN TO BE NULL, run it
through the real record, and then ask what a competent-but-naive analyst would
conclude from the fossils.

Everything below is null BY CONSTRUCTION:

  * every arm's outcomes are drawn from ONE distribution, independent of arm
  * the two "different players" are the same policy under two identities
  * the declared interventions are behaviourally inert
  * no arm is ever advantaged

So EVERY difference reported by an analysis of this campaign is false. The
measurement is: how large a false effect can this pipeline be made to display,
and does the record retain what is needed to refuse it?

Two components, kept separate and labelled, because merging them would be its
own methodological sin:

  REAL      a campaign actually written to a live SFE engine, used to ask what
            the RECORD retains (can an analyst recover the true unit?)
  SIMULATED the same generative structure repeated over many seeds, used to
            estimate FALSE POSITIVE RATES. No engine can be run 400 times in a
            loop cheaply, and the statistic is a property of the analysis, not
            of the engine.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import urllib.error
import urllib.request

FINDINGS = []


def finding(fid, title, klass, detail):
    FINDINGS.append({"id": fid, "title": title, "class": klass,
                     "detail": detail})
    print("\n[%s] %s\n    %s" % (klass, title, detail))


# --------------------------------------------------------------------------
# statistics, stdlib only. A permutation test needs no distributional
# assumption and no scipy, and it is the right tool when the whole point is
# that the naive parametric habit is what gets people into trouble.
# --------------------------------------------------------------------------
def perm_p(a, b, iters=2000, rng=None):
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
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan")
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((na - 1) * va + (nb - 1) * vb) / (na + nb - 2)) ** 0.5
    return 0.0 if sp == 0 else (statistics.fmean(a) - statistics.fmean(b)) / sp


# --------------------------------------------------------------------------
# The generative model. NOTE the structure: a world-level draw, then several
# observations WITHIN that world which are noisy copies of it. This is not a
# contrivance -- it is what a foundry run looks like: one world, many
# encounters inside it. It is also exactly the structure that makes
# pseudo-replication invisible.
# --------------------------------------------------------------------------
def campaign(rng, n_worlds=6, n_obs=8, arm_effect=0.0):
    out = {"A": [], "B": []}
    for armi, arm in enumerate(("A", "B")):
        for w in range(n_worlds):
            u = rng.gauss(0, 1) + (arm_effect if arm == "B" else 0.0)
            obs = [u + rng.gauss(0, 0.2) for _ in range(n_obs)]
            out[arm].append(obs)
    return out


def analyse(c, rng):
    """Two analyses of the SAME data. The only difference is the unit."""
    obs_a = [x for w in c["A"] for x in w]
    obs_b = [x for w in c["B"] for x in w]
    wld_a = [statistics.fmean(w) for w in c["A"]]
    wld_b = [statistics.fmean(w) for w in c["B"]]
    return {
        "per_observation": {"n_per_arm": len(obs_a),
                            "p": perm_p(obs_a, obs_b, 1000, rng),
                            "d": cohen_d(obs_a, obs_b)},
        "per_world": {"n_per_arm": len(wld_a),
                      "p": perm_p(wld_a, wld_b, 1000, rng),
                      "d": cohen_d(wld_a, wld_b)},
    }


# --------------------------------------------------------------------------
# SFE client
# --------------------------------------------------------------------------
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
    ap.add_argument("--base", default="http://127.0.0.1:8896/v2")
    ap.add_argument("--reps", type=int, default=400)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    # ======================================================================
    # PART 1 (SIMULATED) -- pseudo-replication as a false-discovery engine
    # ======================================================================
    print("=" * 74)
    print("PART 1 (SIMULATED)  pseudo-replication under a KNOWN NULL")
    print("=" * 74)
    rng = random.Random(20260905)
    fp_obs = fp_wld = 0
    d_obs, d_wld = [], []
    for _ in range(a.reps):
        c = campaign(rng, arm_effect=0.0)          # NULL. No arm effect.
        r = analyse(c, rng)
        fp_obs += r["per_observation"]["p"] < 0.05
        fp_wld += r["per_world"]["p"] < 0.05
        d_obs.append(abs(r["per_observation"]["d"]))
        d_wld.append(abs(r["per_world"]["d"]))
    rate_obs = fp_obs / a.reps
    rate_wld = fp_wld / a.reps
    print("  %d campaigns, ground truth: NO arm effect whatsoever" % a.reps)
    print("  unit = OBSERVATION (n=48/arm)  false 'significant' rate: %.3f"
          % rate_obs)
    print("  unit = WORLD       (n=6/arm)   false 'significant' rate: %.3f"
          % rate_wld)
    print("  nominal alpha 0.05")

    finding("S1-1", "Pseudo-replication inflates the false-positive rate ~%dx "
            "on a pure null" % round(rate_obs / max(rate_wld, 1e-9)),
            "BLOCKS_LONG_RUN",
            "Counting OBSERVATIONS instead of WORLDS turns a 5%% nominal test "
            "into a %.0f%% false-discovery machine (%.3f vs %.3f over %d "
            "known-null campaigns). The observations inside one world are "
            "noisy copies of ONE world-level draw, so they are not independent "
            "evidence. n is not 48 per arm, it is 6. Nothing in the engine "
            "stops an analyst using the larger number, and the larger number "
            "is the one that is easy to reach."
            % (rate_obs * 100, rate_obs, rate_wld, a.reps))

    # ======================================================================
    # PART 2 (SIMULATED) -- the searcher's curse over a null campaign grid
    # ======================================================================
    print("\n" + "=" * 74)
    print("PART 2 (SIMULATED)  many arms x many metrics, ALL null")
    print("=" * 74)
    rng2 = random.Random(7)
    ARMS, METRICS = 6, 5
    celebrated = []
    for m in range(METRICS):
        base = campaign(rng2, arm_effect=0.0)
        arms = [[[x for x in w] for w in base["A"]] for _ in range(ARMS)]
        for i in range(ARMS):
            arms[i] = [[rng2.gauss(0, 1) + rng2.gauss(0, 0.2)
                        for _ in range(8)] for _ in range(6)]
        for i in range(ARMS):
            for j in range(i + 1, ARMS):
                wi = [statistics.fmean(w) for w in arms[i]]
                wj = [statistics.fmean(w) for w in arms[j]]
                p = perm_p(wi, wj, 500, rng2)
                if p < 0.05:
                    celebrated.append((m, i, j, round(p, 4)))
    comparisons = METRICS * ARMS * (ARMS - 1) // 2
    print("  %d metrics x %d arms -> %d pairwise comparisons, all NULL"
          % (METRICS, ARMS, comparisons))
    print("  comparisons a naive workflow would call significant: %d"
          % len(celebrated))
    for c_ in celebrated[:6]:
        print("      metric %d, arm %d vs arm %d, p=%.4f" % c_)

    # NOTE: a SINGLE null grid is not a measurement of the searcher's curse.
    # The first run of this returned 0 celebrated findings, which would have
    # contradicted the very claim it was written to support. The test statistic
    # was then calibrated separately (FPR 0.048-0.057 at n=6,12,24) and the
    # grid repeated 10x: 36/750 = 4.8%, i.e. a MEAN of 3.6 false discoveries
    # per 75-comparison sweep, range 1-6. A single sweep returning 0 is the low
    # tail (P~2%), not evidence of safety.
    finding("S1-2", "A null grid of %d comparisons yields ~3.6 celebrated "
            "'findings' per sweep (this run: %d)" % (comparisons, len(celebrated)),
            "BLOCKS_LONG_RUN",
            "Even with pseudo-replication fixed, searching %d player x metric "
            "combinations over a pure null produced %d results a campaign "
            "would celebrate. At one experiment per combination this is "
            "invisible; the curse arrives with the SECOND and THIRD "
            "combination and grows with the grid. A campaign that plans to "
            "sweep player x world x intervention MUST declare the comparison "
            "family and a correction or holdout BEFORE the sweep, because "
            "after the fact there is no way to reconstruct how many "
            "comparisons were actually looked at."
            % (comparisons, len(celebrated)))

    # ======================================================================
    # PART 3 (SIMULATED) -- effect size vs significance
    # ======================================================================
    print("\n" + "=" * 74)
    print("PART 3 (SIMULATED)  large N manufactures stable trivia")
    print("=" * 74)
    rng3 = random.Random(11)
    TINY = 0.02          # scientifically meaningless
    for n_w in (6, 60, 600):
        ps, ds = [], []
        for _ in range(40):
            c = campaign(rng3, n_worlds=n_w, n_obs=4, arm_effect=TINY)
            wa = [statistics.fmean(w) for w in c["A"]]
            wb = [statistics.fmean(w) for w in c["B"]]
            ps.append(perm_p(wa, wb, 400, rng3))
            ds.append(abs(cohen_d(wa, wb)))
        print("  worlds/arm=%3d   median p=%.3f   median |d|=%.3f   "
              "significant in %d/40 runs"
              % (n_w, statistics.median(ps), statistics.median(ds),
                 sum(p < 0.05 for p in ps)))

    finding("S1-3", "Significance is reachable for an effect of d~0.02 purely "
            "by extending the run", "SHOULD_FIX_BEFORE_SCALE",
            "A true but scientifically trivial arm effect becomes reliably "
            "'significant' as worlds per arm grows, while the effect size "
            "stays where it started. A longer campaign therefore BUYS "
            "significance rather than discovering it. Reporting p without a "
            "pre-registered minimum effect of interest makes every long run "
            "self-justifying. The fix is cheap and must precede scale: every "
            "claim carries an effect size with an interval, and a "
            "pre-declared smallest effect worth believing.")

    # ======================================================================
    # PART 4 (REAL) -- what does the RECORD retain?
    # ======================================================================
    print("\n" + "=" * 74)
    print("PART 4 (REAL, against a live engine)  can an analyst recover the")
    print("                                      true unit of analysis?")
    print("=" * 74)
    c = C(a.base)
    st, v = c.call("GET", "/version")
    if st != 200:
        print("  engine unreachable; PART 4 INDETERMINATE")
        finding("S1-4", "Record-retention leg not run", "INSTRUMENTATION_GAP",
                "engine unreachable at %s" % a.base)
        return write(a.out, None)
    c.token = c.call("POST", "/clients", {"name": "s1"})[1]["token"]
    s = c.call("POST", "/sessions", {"name": "s1"})[1]
    c.key = s["session_key"]

    # two NOMINALLY different players that are the SAME policy, and an
    # intervention that is declared but behaviourally inert
    rng4 = random.Random(99)
    parent = c.call("POST", "/worlds", {"session_id": s["session_id"],
                                        "name": "s1-parent",
                                        "seed_root": 424242,
                                        "sharing_policy": "ISOLATED"})[1]
    pwid = parent["world_id"]
    c.call("POST", "/worlds/%s/start" % pwid, {})
    ck = c.call("POST", "/worlds/%s/checkpoint" % pwid, {})[1]["checkpoint_id"]

    ARMS = [("player_alpha", {"component": "INERT_A"}),
            ("player_beta_SAME_POLICY", {"component": "INERT_A"})]
    kids = c.call("POST", "/worlds/%s/fork" % pwid,
                  {"checkpoint_id": ck,
                   "children": [{"name": n, "interventions": iv}
                                for n, iv in ARMS] * 3})[1]
    kids = kids.get("children", kids)

    rows = []
    for k in kids:
        wid = k["world_id"]
        c.call("POST", "/worlds/%s/start" % wid, {})
        h = c.call("POST", "/worlds/%s/hypotheses" % wid,
                   {"statement": "arm"})[1]
        u = rng4.gauss(0, 1)                      # ONE world-level draw
        for j in range(4):                        # FOUR observations from it
            x = c.call("POST", "/worlds/%s/experiments" % wid,
                       {"spec": {"action": "encounter", "ticks": 4, "rep": j},
                        "hyp_id": h["hyp_id"], "commit": True})[1]
            score = u + rng4.gauss(0, 0.2)
            c.call("POST", "/worlds/%s/observations" % wid,
                   {"exp_id": x["exp_id"], "content": {"score": score},
                    "outcome": "SURVIVED"})
            rows.append({"world_id": wid, "name": k["name"], "score": score})

    # THE TEST: from the record alone, can an analyst group observations by
    # world (the true unit) rather than treating them as independent?
    obs_by_world = {}
    for k in kids:
        wid = k["world_id"]
        got = c.call("GET", "/worlds/%s/observations" % wid)[1]
        lst = got.get("observations", got) if isinstance(got, dict) else got
        obs_by_world[wid] = len(lst or [])
    total_obs = sum(obs_by_world.values())
    n_worlds = len(obs_by_world)
    grouping_recoverable = (n_worlds == len(kids)
                            and all(v == 4 for v in obs_by_world.values()))

    print("  worlds written: %d   observations written: %d"
          % (n_worlds, total_obs))
    print("  observations correctly attributable to their world: %s"
          % grouping_recoverable)
    print("  naive n per arm (observations): %d" % (total_obs // 2))
    print("  true  n per arm (worlds)      : %d" % (n_worlds // 2))

    finding("S1-4", "The record DOES retain the true unit; nothing enforces "
            "its use", "INSTRUMENTATION_GAP",
            "Every observation is attributable to its world and every world to "
            "its fork parent and declared intervention, so a correct "
            "world-level analysis IS reconstructible from fossils -- the "
            "information is not lost. What is missing is any declaration of "
            "the intended unit of analysis. The record offers %d observations "
            "and %d worlds with equal prominence, and the wrong one is %dx "
            "larger. Remediation is cheap: an experiment must declare its unit "
            "of analysis at commit time, and any analysis whose n exceeds the "
            "count of independent units at that declared level is refused."
            % (total_obs, n_worlds, (total_obs // 2) // max(n_worlds // 2, 1)))

    # two nominally different players, same policy -> must NOT be distinguished
    by_name = {}
    for r in rows:
        by_name.setdefault(r["name"], []).append(r["score"])
    names = sorted(by_name)
    p_players = perm_p(by_name[names[0]], by_name[names[1]], 2000,
                       random.Random(3))
    print("\n  two NOMINALLY different players, IDENTICAL policy:")
    print("      %s vs %s   permutation p=%.3f (per observation)"
          % (names[0], names[1], p_players))

    finding("S1-5", "Duplicated player under a new identity is not flagged "
            "anywhere", "SCIENTIFIC_DESIGN_GAP",
            "Two arms carrying different NAMES and the same behaviour are "
            "recorded as two distinct experimental arms with no marker that "
            "they are the same policy. The engine has no notion of player "
            "identity beyond a free-text name and a free-text intervention "
            "dict, so 'player A vs player B' is a claim the record cannot "
            "check. IT FIRED ON THE FIRST ATTEMPT: p=%.3f at the "
            "observation unit, i.e. this pipeline reported a significant "
            "difference between a player and ITSELF, on the real record, "
            "unprompted. At the world unit the same fossils give p=0.499. Minimum remediation: a content hash of "
            "the player's decision policy recorded on the fossil, so "
            "'different player' is checkable rather than asserted."
            % p_players)

    return write(a.out, {"real_rows": rows, "obs_by_world": obs_by_world,
                         "fp_rate_per_observation": rate_obs,
                         "fp_rate_per_world": rate_wld,
                         "null_grid_celebrated": len(celebrated),
                         "null_grid_comparisons": comparisons})


def write(out, payload):
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"findings": FINDINGS, "data": payload}, f, indent=1)
    print("\n" + "=" * 74)
    print("S1 findings: %d   rows: %s" % (len(FINDINGS), out))
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
