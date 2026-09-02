"""Phase 2 Stage B (DEV ONLY): which ADMISSIBLE pairings carry
task-conditional signal?

Screens candidate scoring functions S(artifact_bytes, train_examples) -- all
computable from admissible information only -- against the oracle relevance
matrix. Reports how much of the available CONDITIONAL headroom each captures
above the unconditional (global-best) reference.

    capture = (mean relevance of S's top-k  -  global-best top-k relevance)
              / (conditional-oracle top-k relevance - global-best top-k)

capture <= 0 means the pairing carries no task-conditional signal, i.e. it
is no better than ignoring the query. This is a cheap screen on the oracle
relevance proxy; anything promising is then validated downstream.
"""
import sys, json, itertools
import numpy as np
sys.path.insert(0, "d10")
from lib import organizer as og
from foundry.tasks.base import ExactTask
from foundry.engines.gp.stackvm import vm

K = 4
D = json.load(open("d10/phase2/dataset.json"))
corpus = [bytes.fromhex(h) for h in D["corpus_hex"]]
dev = [(d["family"], d["train"]) for d in D["dev_tasks"]]
R = np.load("d10/phase2/relevance_dev.npy")
print(f"corpus={len(corpus)} dev={len(dev)} R={R.shape}", flush=True)

VIS = og.MAX_ARTIFACT_WORDS * 8          # bytes KA can see at all
VM_AFFORDABLE = 24                       # bytes KA can process within 300 steps


def topk_rel(scores, j):
    idx = np.argsort(-scores, kind="stable")[:K]
    return float(R[idx, j].mean())


glob = np.argsort(-R.mean(axis=1), kind="stable")[:K]
ref_global = float(np.mean([R[glob, j].mean() for j in range(R.shape[1])]))
ref_oracle = float(np.mean([np.sort(R[:, j])[-K:].mean()
                            for j in range(R.shape[1])]))
ref_unif = float(R.mean())
span = ref_oracle - ref_global
print(f"uniform={ref_unif:.4f} global_best={ref_global:.4f} "
      f"cond_oracle={ref_oracle:.4f} conditional_span={span:.4f}", flush=True)


def bitset(vals, mod=64):
    m = 0
    for v in vals:
        m |= 1 << (int(v) % mod)
    return m


def ham(a, b):
    return bin(a ^ b).count("1")


# ---- precompute artifact-side representations (admissible) ----
A_bits_all = [bitset(g[:VIS]) for g in corpus]
A_bits_vm = [bitset(g[:VM_AFFORDABLE]) for g in corpus]
A_byteset = [set(g[:VIS]) for g in corpus]
A_hist = np.stack([np.bincount(np.frombuffer(g[:VIS], dtype=np.uint8),
                               minlength=256).astype(float)
                   if g[:VIS] else np.zeros(256) for g in corpus])
A_hist /= (np.linalg.norm(A_hist, axis=1, keepdims=True) + 1e-9)
A_ops = [set(b % vm.N_OPCODES for b in g[:VIS]) for g in corpus]

cands = {}
for j, (fi, train) in enumerate(dev):
    outs = [o for _, o in train]
    ins = [v for i, _ in train for v in i]
    q_bits = bitset(outs)
    q_set = set(outs)
    q_hist = np.bincount(np.array([o % 256 for o in outs], dtype=int),
                         minlength=256).astype(float)
    q_hist /= (np.linalg.norm(q_hist) + 1e-9)
    q_io_bits = bitset(outs + ins)

    cands.setdefault("bitset64_out_vs_allbytes", []).append(
        topk_rel(np.array([-ham(a, q_bits) for a in A_bits_all], float), j))
    cands.setdefault("bitset64_out_vs_first24B", []).append(
        topk_rel(np.array([-ham(a, q_bits) for a in A_bits_vm], float), j))
    cands.setdefault("bitset64_inout_vs_allbytes", []).append(
        topk_rel(np.array([-ham(a, q_io_bits) for a in A_bits_all], float), j))
    cands.setdefault("exact_byteset_overlap", []).append(
        topk_rel(np.array([len(s & q_set) for s in A_byteset], float), j))
    cands.setdefault("byte_hist_cosine", []).append(
        topk_rel(A_hist @ q_hist, j))
    cands.setdefault("opcode_set_vs_outmod33", []).append(
        topk_rel(np.array([len(s & {o % vm.N_OPCODES for o in outs})
                           for s in A_ops], float), j))

res = {"uniform": round(ref_unif, 5), "global_best": round(ref_global, 5),
       "cond_oracle": round(ref_oracle, 5),
       "conditional_span": round(span, 5), "candidates": {}}
for name, vals in cands.items():
    m = float(np.mean(vals))
    cap = (m - ref_global) / span if span > 1e-12 else 0.0
    res["candidates"][name] = {"mean_topk_relevance": round(m, 5),
                               "capture_of_conditional_span": round(cap, 4)}
    print(f"{name:32s} rel={m:.5f}  capture={cap:+.4f}", flush=True)

# ---- learned upper bound: leave-one-FAMILY-out RF on cross features ----
try:
    from sklearn.ensemble import RandomForestRegressor
    fams = np.array([fi for fi, _ in dev])
    A_feat = np.hstack([A_hist, np.array([[len(g)] for g in corpus], float)])
    rows, ys, tj_of_row = [], [], []
    for j, (fi, train) in enumerate(dev):
        outs = np.array([o for _, o in train], float)
        qf = np.array([outs.mean(), outs.std(), outs.min(), outs.max(),
                       len(set(outs.tolist()))])
        qh = np.bincount((outs.astype(int) % 256), minlength=256).astype(float)
        qh /= (np.linalg.norm(qh) + 1e-9)
        sub = np.random.default_rng(j).choice(len(corpus),
                                              size=min(400, len(corpus)),
                                              replace=False)
        for ai in sub:
            rows.append(np.concatenate([A_feat[ai], qf, [A_hist[ai] @ qh]]))
            ys.append(R[ai, j]); tj_of_row.append(j)
    X = np.stack(rows); y = np.array(ys); tjr = np.array(tj_of_row)
    caps = []
    for held in sorted(set(fams.tolist())):
        tr = np.array([fams[t] != held for t in tjr])
        if tr.sum() == 0 or (~tr).sum() == 0:
            continue
        rf = RandomForestRegressor(n_estimators=80, random_state=0, n_jobs=-1)
        rf.fit(X[tr], y[tr])
        for j in [t for t in range(len(dev)) if fams[t] == held]:
            outs = np.array([o for _, o in dev[j][1]], float)
            qf = np.array([outs.mean(), outs.std(), outs.min(), outs.max(),
                           len(set(outs.tolist()))])
            qh = np.bincount((outs.astype(int) % 256), minlength=256).astype(float)
            qh /= (np.linalg.norm(qh) + 1e-9)
            Xall = np.hstack([A_feat,
                              np.tile(qf, (len(corpus), 1)),
                              (A_hist @ qh).reshape(-1, 1)])
            caps.append(topk_rel(rf.predict(Xall), j))
    m = float(np.mean(caps))
    res["candidates"]["learned_RF_leave_one_family_out"] = {
        "mean_topk_relevance": round(m, 5),
        "capture_of_conditional_span": round((m - ref_global) / span, 4)}
    print(f"{'learned_RF_LOFO':32s} rel={m:.5f}  "
          f"capture={(m-ref_global)/span:+.4f}", flush=True)
except Exception as e:                                    # noqa: BLE001
    res["learned_error"] = str(e)
    print("learned model failed:", e)

print(json.dumps(res, indent=1))
json.dump(res, open("d10/phase2/capacity_pairings.json", "w"), indent=1)
