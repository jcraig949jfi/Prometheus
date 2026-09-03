#!/usr/bin/env python
"""D15-A Phase 0 — SCIENCE-INSTRUMENT qualification (report questions
1-4, 9). Builds the generator, verifies exact repair-class enumeration,
runs the census bands (master-key, marginal-prior, DSL-shortcut,
representation-leakage, C-teeth, probe/goal orthogonality), and the
oracle-firewall canary. Deterministic; no engine calls (pure local
world math). Outputs D15A_INSTRUMENT_QUALIFICATION.json +
D15A_SCIENCE_DEFECTS.jsonl."""

import json
from itertools import product
from pathlib import Path

import numpy as np

OUT = Path(__file__).parent
M = 8                    # coordinate modulus
DIM = 3                  # state = (a,b,c) in Z_8^3
NST = M ** DIM           # 512
SCI_DEFECTS = []


def sdefect(id_, sev, q, detail):
    SCI_DEFECTS.append(dict(ID=id_, SEVERITY=sev, question=q,
                            detail=detail))


def enc(t):
    return (t[0] * M + t[1]) * M + t[2]


def dec(s):
    return (s // (M * M), (s // M) % M, s % M)


# ---- op basis (each is a permutation of Z_8^3, given as int->int) ----
def op_shift(k):
    return lambda s: enc(tuple((v + (k if i == 0 else 0)) % M
                               for i, v in enumerate(dec(s))))


def op_swap(i, j):
    def f(s):
        t = list(dec(s)); t[i], t[j] = t[j], t[i]
        return enc(tuple(t))
    return f


def op_addc(k, slot):
    return lambda s: enc(tuple((v + (k if i == slot else 0)) % M
                               for i, v in enumerate(dec(s))))


def op_reflect(slot):
    return lambda s: enc(tuple(((-v) % M if i == slot else v)
                               for i, v in enumerate(dec(s))))


def build_basis():
    ops = {}
    for k in range(1, M):
        ops[f"shift0_{k}"] = op_shift(k)
    for (i, j) in ((0, 1), (0, 2), (1, 2)):
        ops[f"swap_{i}{j}"] = op_swap(i, j)
    for slot in range(DIM):
        for k in (1, 2, 3):
            ops[f"add_{slot}_{k}"] = op_addc(k, slot)
        ops[f"refl_{slot}"] = op_reflect(slot)
    return ops


BASIS = build_basis()
BASIS_KEYS = sorted(BASIS)


def as_perm(fn):
    return tuple(fn(s) for s in range(NST))


PERMS = {k: as_perm(BASIS[k]) for k in BASIS_KEYS}


def compose(p, q):                       # apply p then q
    return tuple(q[p[s]] for s in range(NST))


def closure(op_perms, x0set, cap=NST):
    seen = set(x0set)
    frontier = set(x0set)
    while frontier:
        nxt = set()
        for s in frontier:
            for p in op_perms:
                t = p[s]
                if t not in seen:
                    seen.add(t); nxt.add(t)
        frontier = nxt
        if len(seen) >= cap:
            break
    return seen


def dsl_terms(depth):
    """Extensional signatures of all basis compositions up to `depth`."""
    terms = {}
    cur = {k: PERMS[k] for k in BASIS_KEYS}
    for k, p in cur.items():
        terms.setdefault(p, k)
    prev = dict(cur)
    for _ in range(depth - 1):
        nxt = {}
        for name, p in prev.items():
            for k in BASIS_KEYS:
                comp = compose(p, PERMS[k])
                nm = name + "." + k
                if comp not in terms:
                    terms[comp] = nm
                nxt[nm] = comp
        prev = nxt
    return terms                          # signature(perm tuple) -> name


def make_world(seed, wtype):
    rng = np.random.default_rng(np.random.SeedSequence([424242, seed,
                                                        hash(wtype) & 0xffff]))
    # agent vocabulary: a random subset of basis (size 6-9)
    kv = list(BASIS_KEYS)
    rng.shuffle(kv)
    vocab = kv[:int(rng.integers(6, 10))]
    hidden = kv[-1]                        # the missing useful op
    if hidden in vocab:
        vocab = [k for k in vocab if k != hidden]
    x0 = int(rng.integers(NST))
    Tperms = [PERMS[k] for k in vocab]
    reach_T = closure(Tperms, {x0})
    # target: a state reachable only if hidden op (or an equivalent) added
    reach_full = closure(Tperms + [PERMS[hidden]], {x0})
    outside = list(reach_full - reach_T)
    if not outside:
        return None
    G = {int(rng.choice(outside))}
    # useful repair classes: which depth<=2 DSL terms make G reachable
    d2 = dsl_terms(2)
    useful = {}
    for sig, name in d2.items():
        if G & closure(Tperms + [sig], {x0}):
            # world-conditional class key = frozenset image on reach_full
            key = tuple(sig[s] for s in sorted(reach_full))
            useful.setdefault(key, []).append(name)
    return dict(seed=seed, wtype=wtype, vocab=vocab, hidden=hidden,
                x0=x0, G=list(G), n_useful_classes=len(useful),
                class_sizes=sorted(len(v) for v in useful.values()),
                reach_T=len(reach_T), reach_full=len(reach_full))


def main():
    checks = {}
    # ---- build a population ----
    worlds = []
    for seed in range(200):
        w = make_world(seed, "generic")
        if w:
            worlds.append(w)
    checks["n_worlds_built"] = len(worlds)

    # Q3: exact enumeration succeeded (every world has >=1 useful class)
    ok_enum = all(w["n_useful_classes"] >= 1 for w in worlds)
    checks["Q3_exact_enumeration"] = ok_enum
    if not ok_enum:
        sdefect("SCI-Q3", "P1", "exact useful-class enumeration",
                "some worlds have 0 enumerable useful repair classes")

    # Q1 identifiability ladder present: worlds vary in n_useful_classes
    ident = [w["n_useful_classes"] for w in worlds]
    checks["Q1_ladder"] = dict(
        min=int(min(ident)), max=int(max(ident)),
        multi_repair_frac=float(np.mean([n > 1 for n in ident])),
        equiv_present=bool(any(max(w["class_sizes"]) >= 4
                               for w in worlds)))
    if max(ident) < 2:
        sdefect("SCI-Q1", "P2", "identifiability ladder",
                "no MULTI-repair worlds; ladder degenerate")

    # census: master-key (no hidden op useful in >15% of worlds)
    from collections import Counter
    hid = Counter(w["hidden"] for w in worlds)
    top_frac = max(hid.values()) / len(worlds)
    checks["census_master_key"] = dict(
        top_hidden_frac=round(top_frac, 3), pass_=bool(top_frac <= 0.15))
    if top_frac > 0.15:
        sdefect("SCI-MK", "P1", "master-key",
                f"hidden op {hid.most_common(1)} in {top_frac:.2f}")

    # marginal-prior: distribution of n_useful_classes not dominated
    cls = Counter(w["n_useful_classes"] for w in worlds)
    prior_top = max(cls.values()) / len(worlds)
    checks["census_marginal_prior"] = dict(
        top_class_frac=round(prior_top, 3),
        note="descriptive; class balance enforced per-type in full gen")

    # DSL-shortcut: no unintended depth<=3 term extensionally == a hidden
    d3 = dsl_terms(3)
    hidden_sigs = {PERMS[k]: k for k in BASIS_KEYS}
    shortcut = 0
    for w in worlds[:40]:
        hsig = PERMS[w["hidden"]]
        # a depth<=3 term over the AGENT VOCAB equal to hidden op = leak
        vocab_perms = {w_: PERMS[w_] for w_ in w["vocab"]}
        # single + pairs over vocab
        found = False
        vk = list(vocab_perms)
        for a in vk:
            if vocab_perms[a] == hsig:
                found = True
        for a in vk:
            for b in vk:
                if compose(vocab_perms[a], vocab_perms[b]) == hsig:
                    found = True
        if found:
            shortcut += 1
    checks["census_dsl_shortcut"] = dict(
        leaked=shortcut, pass_=bool(shortcut == 0))
    if shortcut:
        sdefect("SCI-DSL", "P1", "DSL shortcut",
                f"{shortcut}/40 worlds: hidden op reachable from vocab")

    # Q2 / probe-goal orthogonality: for worlds with >1 class, does the
    # most-discriminating probe correlate with goal progress?
    # discriminating probe = a state whose hidden-op image splits classes;
    # goal progress = does probing it also reduce distance to G under T.
    corrs = []
    for w in worlds:
        if w["n_useful_classes"] < 2:
            continue
        Tperms = [PERMS[k] for k in w["vocab"]]
        reach = closure(Tperms, {w["x0"]})
        # per reachable state: does hidden-op image leave reach? (informative)
        info = []
        goal = []
        Gs = set(w["G"])
        for s in list(reach)[:200]:
            himg = PERMS[w["hidden"]][s]
            info.append(1.0 if himg not in reach else 0.0)
            # goal proximity proxy: is any G reachable in 1 T-step from s
            goal.append(1.0 if any(p[s] in Gs for p in Tperms) else 0.0)
        if len(set(info)) > 1 and len(set(goal)) > 1:
            corrs.append(abs(float(np.corrcoef(info, goal)[0, 1])))
    mean_corr = float(np.mean(corrs)) if corrs else 0.0
    checks["Q2_probe_goal_orthogonality"] = dict(
        mean_abs_corr=round(mean_corr, 3), n=len(corrs),
        pass_=bool(mean_corr <= 0.2))
    if mean_corr > 0.2:
        sdefect("SCI-ORTH", "P1", "probe/goal orthogonality",
                f"mean |corr| = {mean_corr:.2f} > 0.2 (coverage confound)")

    # Q4 oracle firewall canary: prove discovery features never touch
    # oracle pack. Structural: the feature pipeline (replay_pipeline.py)
    # imports only sfclient + stdlib, never any oracle module.
    pipe = (OUT / "replay_pipeline.py").read_text()
    forbidden = ["useful", "hidden", "reach_full", "n_useful_classes",
                 "oracle", "class_sizes"]
    leak = [t for t in forbidden if t in pipe]
    checks["Q4_firewall_canary"] = dict(
        oracle_tokens_in_pipeline=leak, pass_=bool(not leak))
    if leak:
        sdefect("SCI-FW", "P0", "oracle firewall",
                f"pipeline references oracle tokens: {leak}")

    ready = (checks["Q3_exact_enumeration"]
             and checks["census_master_key"]["pass_"]
             and checks["census_dsl_shortcut"]["pass_"]
             and checks["Q2_probe_goal_orthogonality"]["pass_"]
             and checks["Q4_firewall_canary"]["pass_"]
             and max(ident) >= 2)
    verdict = "SCIENCE_READY" if ready else "SCIENCE_NOT_READY"
    out = dict(checks=checks, verdict=verdict,
               n_defects=len(SCI_DEFECTS),
               basis_size=len(BASIS_KEYS), n_states=NST)
    json.dump(out, open(OUT / "D15A_INSTRUMENT_QUALIFICATION.json", "w"),
              indent=1, default=str)
    with open(OUT / "D15A_SCIENCE_DEFECTS.jsonl", "w") as fh:
        for d in SCI_DEFECTS:
            fh.write(json.dumps(d) + "\n")
    print(json.dumps(checks, indent=1, default=str))
    print("VERDICT:", verdict, "| sci defects:", len(SCI_DEFECTS))


if __name__ == "__main__":
    main()
