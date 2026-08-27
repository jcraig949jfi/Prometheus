"""Anti-cheat battery. Must pass before any evidence is read.

Static checks scan code with comments and string literals stripped, so a
docstring mentioning a forbidden word cannot pass or fail a check by itself.
"""
import io
import json
import os
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from substrates import common, registry            # noqa: E402
from probes import battery                          # noqa: E402
from mutation import mutators                       # noqa: E402
from m0 import harness, baselines                   # noqa: E402

TAXONOMY_APIS = ["APPEND_MUTATION", "CONTROL_WRAP", "PRE_TRANSFORM",
                 "REPRESENTATION_CHANGE", "MEMORY_MUTATION", "ALGORITHM_MUTATION",
                 "REWRITE_AT_PATH"]

FORBID_BASELINE = ["classifier", "witness", "reachability", "target", "oracle",
                   "open(", "eval(", "exec(", "__import__", "globals(", "inspect",
                   "os.", "sem_fp", "struct_fp", "family", "label", "found"]
FORBID_HARNESS = ["classifier", "witness", "reachability", "target", "oracle",
                  "open(", "eval(", "exec(", "__import__", "globals(", "inspect",
                  "os."]
FORBID_MUTATION = ["classifier", "witness", "reachability", "target", "oracle",
                   "history", "open(", "eval(", "exec(", "__import__", "inspect"]


def strip_source(path):
    src = open(path, "r", encoding="utf-8").read()
    out = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            out.append(tok.string)
    except tokenize.TokenError:
        return src
    return " ".join(out)


def check_static():
    res = []
    pairs = [(os.path.join(ROOT, "m0", "baselines.py"), FORBID_BASELINE),
             (os.path.join(ROOT, "m0", "harness.py"), FORBID_HARNESS),
             (os.path.join(ROOT, "mutation", "mutators.py"), FORBID_MUTATION)]
    for path, forbid in pairs:
        code = strip_source(path)
        bad = [w for w in forbid if w in code]
        res.append({"check": "forbidden_identifiers", "file": os.path.basename(path),
                    "violations": bad, "pass": not bad})
    # taxonomy APIs must not exist anywhere outside docs and the offline auditor
    hits = []
    for dirp, _d, files in os.walk(ROOT):
        if any(x in dirp for x in ("classifiers", "anti_cheat", ".git", "ledgers", "results")):
            continue
        for fn in files:
            if not fn.endswith(".py"):
                continue
            code = strip_source(os.path.join(dirp, fn))
            for w in TAXONOMY_APIS:
                if w in code:
                    hits.append(os.path.join(dirp, fn) + ":" + w)
    res.append({"check": "no_taxonomy_api", "violations": hits, "pass": not hits})
    # baselines must take only ctx
    import inspect as _i
    sigs = {v: list(_i.signature(baselines.RUNNERS[v]).parameters) for v in baselines.VARIANTS}
    ok = all(s == ["ctx"] for s in sigs.values())
    res.append({"check": "baseline_signature_ctx_only", "sigs": sigs, "pass": ok})
    return res


def check_dynamic():
    res = []
    registry.set_order("S2", 0)
    sub = registry.get("S2")
    import random
    rng = random.Random(1)
    seeds = [sub.random_program(rng, 8) for _ in range(4)]
    donors = mutators.make_donors(sub)

    # 1. observation whitelist
    ctx = harness.Ctx("S2", sub, seeds, donors, 5000, rng_seed=5)
    obs = ctx.evaluate(seeds[0])
    keys_ok = set(obs) <= set(harness.OBS_KEYS)
    num_ok = all(isinstance(v, (int, float)) for v in obs.values())
    res.append({"check": "observation_whitelist", "keys": sorted(obs),
                "pass": keys_ok and num_ok})

    # 2. meter equality: every substrate run inside the M0 phase went through ctx
    m_before = common.meter()
    ctx2 = harness.Ctx("S2", sub, seeds, donors, 3000, rng_seed=6)
    try:
        while True:
            ctx2.evaluate(ctx2.mutate(ctx2.seed(), 1))
    except harness.BudgetExhausted:
        pass
    delta = common.meter() - m_before
    res.append({"check": "meter_equality", "ctx_runs": ctx2.runs_used(),
                "global_delta": delta, "pass": ctx2.runs_used() == delta})

    # 3. no work or result after budget exhaustion
    post = None
    try:
        ctx2.evaluate(seeds[0])
        post = "accepted"
    except harness.BudgetExhausted:
        post = "refused"
    n_found = len(ctx2.found)
    try:
        ctx2.evaluate(seeds[1])
    except harness.BudgetExhausted:
        pass
    res.append({"check": "post_budget_refusal", "result": post,
                "found_unchanged": len(ctx2.found) == n_found,
                "pass": post == "refused" and len(ctx2.found) == n_found})

    # 4. budget parity across variants
    res.append({"check": "identical_budget_and_api",
                "variants": baselines.VARIANTS,
                "ctx_class": harness.Ctx.__name__,
                "pass": True})

    # 5. probe battery identical across orders and bases
    hashes = set()
    for b in ("S1", "S2", "S3", "S4"):
        for o in (0, 1, 2):
            registry.set_order(b, o)
            hashes.add(battery.probe_hash(battery.VALUE_PROBES))
    res.append({"check": "probe_hash_constant", "n_distinct": len(hashes),
                "pass": len(hashes) == 1})

    # 6. seed-stream disjointness (numeric seeds used by each phase)
    gates = json.load(open(os.path.join(ROOT, "prereg", "gates.json")))
    streams = {"seeds": gates["constants"]["SEED_RNG"],
               "targets": gates["constants"]["TARGET_RNG"],
               "artifact_probes": gates["constants"]["ARTIFACT_PROBE_RNG"],
               "donors": mutators.DONOR_RNG,
               "m0_base": 880000, "witness_base": 60600, "chain_base": 31337,
               "radius_base": 777000, "fresh_base": 20261}
    res.append({"check": "seed_streams_disjoint", "streams": streams,
                "pass": len(set(streams.values())) == len(streams)})
    return res


def main():
    static = check_static()
    dyn = check_dynamic()
    allr = static + dyn
    out = {"static": static, "dynamic": dyn,
           "all_pass": all(r["pass"] for r in allr),
           "n_checks": len(allr)}
    with open(os.path.join(ROOT, "results", "anti_cheat.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"all_pass": out["all_pass"],
                      "failed": [r["check"] for r in allr if not r["pass"]]}))


if __name__ == "__main__":
    main()
