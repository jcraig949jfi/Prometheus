"""HT-8a87057933 / W6 controls (Pass 3 v2). NO TREATMENT CODE.

World: identify an unknown plant among N candidate plants by excitation
probes. Candidate plant c (c = 0..N-1) is "component c is faulty". Probe p
exercises a fixed subset E_p of components; the plant's response is 1 iff
its faulty component is in E_p. Library: P probes, |E_p| drawn uniformly
from SIZES, members uniform without replacement. A library is regenerated
until it separates every pair of candidates (so identification is always
possible). The agent keeps the version space V (candidates consistent with
all responses so far); an episode ends when |V| == 1.

Arms here (controls only; the TREATMENT, SAT/hitting-set separating-family
probing, is NOT here):
  POSITIVE_CONTROL : truth oracle -- among unapplied probes, pick the one
                     whose REALISED response removes the most candidates
                     (ties: lowest index). Upper bound on elimination per
                     probe; it uses the hidden truth.
  GREEDY_REF       : greedy information gain -- pick the unapplied probe
                     maximising the binary entropy of the split of V
                     (ties: lowest index). The spec's CONTROL (the simpler
                     alternative named for M4).
  NULL_TWIN        : uniformly random unapplied probe (same stop rule,
                     same library, same truths; probe choice destroyed).
  CHEAT            : NULL_TWIN episodes with success injected into the
                     observable (probes := 1); the logged trace is kept, so
                     the replay audit sees the mismatch.
Every candidate is the truth once per library (exhaustive, no truth
sampling noise). One row per (arm, seed, truth), flushed per row; each row
carries its probe trace so the observable can be recomputed by replay.
"""
import json, math, os, random, time

HERE = os.path.dirname(os.path.abspath(__file__))
N, P = 64, 48
SIZES = [2, 4, 8, 16, 32]
SEEDS = list(range(10))
ENTROPY_BOUND = math.log2(N)   # mean depth of any binary identification tree >= log2 N


def make_library(seed):
    rng = random.Random(seed * 7919 + 11)
    while True:
        lib = []
        for _ in range(P):
            k = rng.choice(SIZES)
            lib.append(frozenset(rng.sample(range(N), k)))
        sigs = {tuple(c in e for e in lib) for c in range(N)}
        if len(sigs) == N:
            return lib


def h2(q):
    return 0.0 if q <= 0 or q >= 1 else -(q * math.log2(q) + (1 - q) * math.log2(1 - q))


def episode(arm, lib, truth, rng):
    V = set(range(N))
    used = set()
    trace = []
    while len(V) > 1:
        cand = [p for p in range(P) if p not in used]
        if arm == "POSITIVE_CONTROL":
            best, bestv = None, -1
            for p in cand:
                resp = truth in lib[p]
                newV = (V & lib[p]) if resp else (V - lib[p])
                if len(V) - len(newV) > bestv:
                    best, bestv = p, len(V) - len(newV)
            p = best
        elif arm == "GREEDY_REF":
            best, bestv = None, -1.0
            for p in cand:
                q = len(V & lib[p]) / len(V)
                if h2(q) > bestv + 1e-12:
                    best, bestv = p, h2(q)
            p = best
        else:  # NULL_TWIN / CHEAT
            p = cand[rng.randrange(len(cand))]
        used.add(p)
        resp = truth in lib[p]
        V = (V & lib[p]) if resp else (V - lib[p])
        trace.append([p, int(resp)])
    return trace


def replay(lib, truth, trace):
    """Recompute the observable from the raw trace; None if the trace is
    inconsistent with the library/truth or does not identify the truth."""
    V = set(range(N))
    for i, (p, r) in enumerate(trace):
        if int(truth in lib[p]) != r:
            return None
        V = (V & lib[p]) if r else (V - lib[p])
        if len(V) == 1:
            return i + 1 if V == {truth} else None
    return None


THRESH = {"S1": 1.05, "S2": 9.0, "S3": 8}
S1_FACTOR = THRESH["S1"]


def p95(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(math.ceil(0.95 * len(xs))) - 1)]


def clause_values(X, ref):
    mx = sum(r["probes"] for r in X) / len(X)
    mr = sum(r["probes"] for r in ref) / len(ref)
    return {"S1": mx / mr, "S2": mx, "S3": p95([r["probes"] for r in X])}


def passes(v):
    return {"S1": v["S1"] <= THRESH["S1"], "S2": v["S2"] <= THRESH["S2"],
            "S3": v["S3"] <= THRESH["S3"]}


if __name__ == "__main__":
    t0 = time.process_time()
    rows = {}
    with open(os.path.join(HERE, "control_rows.jsonl"), "w") as f:
        for seed in SEEDS:
            lib = make_library(seed)
            for arm in ["GREEDY_REF", "POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"]:
                rng = random.Random(seed * 1000 + 3)   # same stream for NULL_TWIN and CHEAT
                for truth in range(N):
                    trace = episode(arm, lib, truth, rng)
                    row = {"arm": arm, "seed": seed, "truth": truth,
                           "probes": len(trace), "trace": trace}
                    if arm == "CHEAT":
                        row["probes"] = 1
                        row["cheat_injected"] = True
                    rows.setdefault(arm, []).append(row)
                    f.write(json.dumps(row) + "\n"); f.flush()
    cpu = time.process_time() - t0
    libs = {s: make_library(s) for s in SEEDS}
    audit = {}
    for arm, rs in rows.items():
        bad = sum(1 for r in rs if replay(libs[r["seed"]], r["truth"], r["trace"]) != r["probes"])
        audit[arm] = {"rows": len(rs), "replay_mismatch": bad}
    ref = rows["GREEDY_REF"]
    out = {a: {"values": clause_values(rows[a], ref)} for a in ["POSITIVE_CONTROL", "NULL_TWIN", "CHEAT"]}
    for a in out:
        out[a]["pass"] = passes(out[a]["values"])
    greedy_mean = sum(r["probes"] for r in ref) / len(ref)
    must = {"S1": "mean probes to identification <= %.3f (= %.2f x GREEDY_REF %.3f); entropy bound for any non-oracle policy is %.1f, so this bar is %s by a legitimate policy"
                  % (S1_FACTOR * greedy_mean, S1_FACTOR, greedy_mean, ENTROPY_BOUND,
                     "reachable in principle" if S1_FACTOR * greedy_mean >= ENTROPY_BOUND else "NOT reachable"),
            "S2": "mean probes to identification <= 9.0",
            "S3": "95th percentile of probes over the 640 episodes <= 8 (GREEDY_REF p95 = %d)" % p95([r["probes"] for r in ref])}
    clauses = []
    for cid in ["S1", "S2", "S3"]:
        clauses.append({"id": cid,
                        "positive_value": out["POSITIVE_CONTROL"]["values"][cid],
                        "twin_value": out["NULL_TWIN"]["values"][cid],
                        "attainable": out["POSITIVE_CONTROL"]["pass"][cid],
                        "discriminating": not out["NULL_TWIN"]["pass"][cid],
                        "treatment_must_reach": must[cid]})
    cheat_pass_all = all(out["CHEAT"]["pass"].values())
    cheat_flagged = audit["CHEAT"]["replay_mismatch"] > 0
    clean = all(audit[a]["replay_mismatch"] == 0 for a in ["GREEDY_REF", "POSITIVE_CONTROL", "NULL_TWIN"])
    cheat_detected = cheat_pass_all and cheat_flagged
    frozen = all(c["attainable"] and c["discriminating"] for c in clauses) and cheat_detected and clean \
        and S1_FACTOR * greedy_mean >= ENTROPY_BOUND
    summ = {a: {"mean_probes": sum(r["probes"] for r in rs) / len(rs),
                "median_probes": sorted(r["probes"] for r in rs)[len(rs) // 2],
                "p95_probes": p95([r["probes"] for r in rs]),
                "max_probes": max(r["probes"] for r in rs)} for a, rs in rows.items()}
    revisions = json.load(open(os.path.join(HERE, "revisions.json")))
    att = {"clauses": clauses, "cheat_detected": cheat_detected,
           "cheat_detail": {"cheat_meets_all_success_clauses": cheat_pass_all,
                            "cheat_flagged_by_trace_replay": cheat_flagged,
                            "replay_audit": audit},
           "legitimate_policy_feasibility": {"entropy_bound_mean_probes": ENTROPY_BOUND,
                                             "S1_bar_mean_probes": S1_FACTOR * greedy_mean,
                                             "S1_bar_above_bound": S1_FACTOR * greedy_mean >= ENTROPY_BOUND},
           "frozen": frozen, "revisions": revisions,
           "control_cpu_seconds": cpu, "seeds_per_arm": len(SEEDS), "episodes_per_seed": N,
           "arm_summary": summ}
    with open(os.path.join(HERE, "ATTAINABILITY.json"), "w") as f:
        json.dump(att, f, indent=1)
    print(json.dumps({k: v for k, v in att.items() if k != "revisions"}, indent=1))
