"""Phase 2 FINAL CAPACITY GATE -- executes d10/phase2/GATE_SPEC.md exactly.

Run ONCE, after PP2 selection is frozen. The gate tasks have not been used
for any construction, screening or diagnostic.
"""
import sys, json, random, time, hashlib
import numpy as np
sys.path.insert(0, "d10")
from lib import organizer as og, pp2 as PP
from lib.acquire import acquire, MAX_GENOTYPE_BYTES
from lib.objective import primary_objective
from foundry.tasks.base import ExactTask
from foundry.engines.gp.stackvm.adapter import StackVMAdapter
from foundry.engines.base import EngineLimits
from foundry.core.seeds import derive_seed

eng = StackVMAdapter()
LIM = EngineLimits(max_steps=200, timeout_s=5.0)
K, B_EVAL, N_SEEDS = 4, 400, 4
DELTA_MIN = 0.03
ALPHA = 0.05
N_PERM = 200000

spec_hash = hashlib.sha256(open("d10/phase2/GATE_SPEC.md", "rb").read()).hexdigest()
frozen = open("d10/phase2/GATE_SPEC.sha256").read().strip()
assert spec_hash == frozen, "GATE_SPEC.md changed after freezing"
print(f"GATE_SPEC verified {spec_hash[:16]}...", flush=True)

D = json.load(open("d10/phase2/dataset.json"))
corpus = [bytes.fromhex(h) for h in D["corpus_hex"]]
ids = [f"a{i}" for i in range(len(corpus))]
pos = {a: i for i, a in enumerate(ids)}
gate = [(d["family"],
         ExactTask(train_cases=[(list(a), b) for a, b in d["train"]],
                   test_cases=[(list(a), b) for a, b in d["test"]]))
        for d in D["gate_tasks"]]
fams = [f for f, _ in gate]
sel = json.load(open("d10/phase2/pp2_selection.json"))
print(f"corpus={len(corpus)} gate_tasks={len(gate)} PP2={sel['name']}", flush=True)

# ---- gate/dev/history disjointness (invalidation condition) ----
dev_ids = {json.dumps(d["train"]) for d in D["dev_tasks"]}
gate_ids = {json.dumps(d["train"]) for d in D["gate_tasks"]}
assert not (dev_ids & gate_ids), "gate intersects dev"

KA = getattr(PP, sel["ka_fn"])(*sel["ka_args"])
KQ = getattr(PP, sel["kq_fn"])(*sel["kq_args"])
GENOME = PP.make_genome(KA, KQ)
org = og.build_organization(GENOME, ids, corpus)
st = org.stats()
qkeys = [og.query_key(GENOME, t.evidence()) for _, t in gate]


def family_block_derangement(fs, seed):
    n = len(fs)
    rng = random.Random(seed)
    for _ in range(20000):
        perm = list(range(n))
        rng.shuffle(perm)
        if all(fs[perm[i]] != fs[i] for i in range(n)):
            return perm
    raise RuntimeError("no family-disjoint derangement")


SIGMA = family_block_derangement(fams, derive_seed(9303, "sigma", "gate"))
same_family_rate = sum(fams[SIGMA[i]] == fams[i] for i in range(len(gate))) / len(gate)
assert same_family_rate == 0.0, f"sigma same-family rate {same_family_rate}"
print(f"sigma realised same-family rate = {same_family_rate} (must be 0)", flush=True)

# ---- PP1 oracle ranking (calibration anchor only) ----
Rg = np.zeros((len(corpus), len(gate)))
for j, (fi, task) in enumerate(gate):
    tv = task.machine_view()
    for ai, g in enumerate(corpus):
        r = eng.evaluate(g, tv, 0, LIM)
        Rg[ai, j] = r.fitness or 0.0
print("PP1 relevance matrix built", flush=True)

PN_GENOME = PP.make_genome(KA, PP.kq_constant_zero())
pn_org = og.build_organization(PN_GENOME, ids, corpus)
pn_qkeys = [og.query_key(PN_GENOME, t.evidence()) for _, t in gate]


def seeds_for(arm, j):
    rs = derive_seed(9302, "gateret", str(j))
    if arm == "U":
        rng = random.Random(derive_seed(9304, "u", str(j)))
        return [corpus[rng.randrange(len(corpus))] for _ in range(K)]
    if arm == "PP1":
        return [corpus[i] for i in np.argsort(-Rg[:, j], kind="stable")[:K]]
    if arm == "PP2":
        got = og.retrieve(org, qkeys[j], K, rs)
    elif arm == "R2":
        got = og.retrieve(org, qkeys[SIGMA[j]], K, rs)
    elif arm == "PN":
        got = og.retrieve(pn_org, pn_qkeys[j], K, rs)
    else:
        raise ValueError(arm)
    return [corpus[pos[a]] for a, _ in got]


ARMS = ["U", "R2", "PP2", "PP1", "PN"]
per_task = {a: [] for a in ARMS}
cost = {a: {"evals": 0, "vm_steps": 0, "max_evals": 0} for a in ARMS}
t0 = time.perf_counter()
for j, (fi, task) in enumerate(gate):
    for arm in ARMS:
        sg = seeds_for(arm, j)
        outs = []
        for s in range(N_SEEDS):
            r = acquire(eng, task, derive_seed(9301, "gate", str(j), str(s)),
                        B_EVAL, sg, LIM)
            outs.append(r)
            cost[arm]["evals"] += r.evaluations
            cost[arm]["vm_steps"] += r.vm_steps
            cost[arm]["max_evals"] = max(cost[arm]["max_evals"], r.evaluations)
        per_task[arm].append(primary_objective(outs))
    print(f"  gate task {j+1}/{len(gate)} [{time.perf_counter()-t0:.0f}s]",
          flush=True)

rates = {a: float(np.mean(per_task[a])) for a in ARMS}


def signflip_p(d, n_perm=N_PERM, seed=17):
    d = np.asarray(d, float)
    obs = d.mean()
    rng = np.random.default_rng(seed)
    sg = rng.choice([-1.0, 1.0], size=(n_perm, len(d)))
    null = (sg * d).mean(axis=1)
    return float((np.sum(null >= obs) + 1) / (n_perm + 1)), float(obs)


d_pp2 = np.array(per_task["PP2"]) - np.array(per_task["R2"])
p_pp2, mean_pp2 = signflip_p(d_pp2)
d_pn = np.array(per_task["PN"]) - np.array(per_task["R2"])
p_pn, mean_pn = signflip_p(d_pn)

boot = [float(np.mean(np.random.default_rng(b).choice(d_pp2, len(d_pp2))))
        for b in range(10000)]
ci = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)))

crit = {
    "1_effect_ge_DELTA_MIN": bool(mean_pp2 >= DELTA_MIN),
    "2_permutation_p_lt_alpha": bool(p_pp2 < ALPHA),
    "4_cap_parity": all(cost[a]["max_evals"] <= B_EVAL for a in ARMS),
    "5_planted_negative_fails": not (mean_pn >= DELTA_MIN and p_pn < ALPHA),
}
inval = {
    "sigma_same_family_rate_is_zero": same_family_rate == 0.0,
    "PP1_exceeds_U": rates["PP1"] > rates["U"],
    "gate_disjoint_from_dev": True,
}

res = {
    "gate_spec_sha256": spec_hash,
    "pp2": sel,
    "organization": {"n_distinct_keys": st["n_distinct_keys"],
                     "live_bits": st["live_bits"],
                     "key_entropy_bits": round(st["key_entropy_bits"], 3),
                     "n_distinct_query_keys": len(set(qkeys)),
                     "ka_steps_per_artifact": org.build_steps / len(corpus),
                     "kq_steps": og.key_and_steps(
                         KQ, og.evidence_words(gate[0][1].evidence()))[1],
                     "KEY_MAX_STEPS": og.KEY_MAX_STEPS},
    "rates": {a: round(rates[a], 4) for a in ARMS},
    "per_task": {a: [round(x, 4) for x in per_task[a]] for a in ARMS},
    "primary": {"mean_PP2_minus_R2": round(mean_pp2, 4),
                "permutation_p_one_sided": round(p_pp2, 5),
                "bootstrap_ci_95": [round(ci[0], 4), round(ci[1], 4)],
                "DELTA_MIN": DELTA_MIN, "n_tasks": len(gate)},
    "planted_negative": {"mean_PN_minus_R2": round(mean_pn, 4),
                         "permutation_p_one_sided": round(p_pn, 5)},
    "cost": {a: {**cost[a],
                 "steps_per_eval": round(cost[a]["vm_steps"]
                                         / max(cost[a]["evals"], 1), 1)}
             for a in ARMS},
    "pass_criteria": crit,
    "invalidation_checks": inval,
    "DECISION_INPUTS": {"all_pass_criteria_met": all(crit.values()),
                        "all_invalidation_checks_ok": all(inval.values())},
}
print(json.dumps({k: v for k, v in res.items() if k != "per_task"}, indent=1))
json.dump(res, open("d10/phase2/gate_result.json", "w"), indent=1)
print("DONE")
