"""COLLISION ENGINE and CONCEPT TENSOR.

A collision takes an ORDERED tuple of k parent entities and produces one
child genome by executable operations only (no language step):

  1. bind      from parent j take a seeded subset of its rules (its bound
               executable properties) and remap its channels by position:
               channel c of parent j -> (c + j) mod C_child (hyperedge binding;
               position-dependent, so A x B x C != C x B x A);
  2. law       generate a k-ary interaction law: a "react" rule whose sources
               are one bound channel per parent (up to 8; above 8 the parents
               are split over several law rules) and whose per-source gains are
               an entry of the CONCEPT TENSOR, T[i1..ik], represented in
               low-rank CP form: gain_j = 2 tanh(<u_{i_j}, w_j>), where u_i is
               the entity's latent factor and w_j a per-position factor. The
               dense tensor is never allocated; realised entries are stored
               sparsely as hyperedges (TensorStore);
  3. operators a seeded subset of: parameter inheritance, transformation
               substitution, symmetry inheritance, cross-scale coupling,
               memory transfer, boundary-condition exchange, state-space
               merging, mutation. Every operator applied is recorded;
  4. order     parent blocks are concatenated in parent order with the law
               inserted at a seeded position; size is capped at MAXRULES.

Rule provenance: rules copied unchanged keep their "prov"; any modified or
generated rule gets a provenance naming the collision, so the raw-human
rule fraction is exact.

Lens entities (kind "lens", a Tyche lens genome) enter a collision as a
"lensmap" rule that applies the lens along the field.
"""

from __future__ import annotations

import copy
import hashlib
import json

import numpy as np

from . import substrate as sb

LATENT = 8
OPERATORS = ("param_inherit", "substitute", "symmetry_inherit", "cross_scale",
             "memory_transfer", "bc_exchange", "state_merge", "mutate")


def _seed(*parts):
    return int(hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()[:12], 16)


class TensorStore:
    """Sparse higher-order interaction store + low-rank latent factors."""

    def __init__(self, master_seed=0):
        self.u = {}
        self.edges = {}  # tuple(parent ids, ordered) -> record
        rng = np.random.default_rng(master_seed + 17)
        self.w = rng.standard_normal((16, LATENT)) / np.sqrt(LATENT)
        self.proj = None
        self.uses = {}
        self.pair_uses = {}

    def latent(self, e):
        if e["id"] not in self.u:
            fp = e.get("behavioralFingerprint")
            if fp is not None and self.proj is not None:
                v = np.tanh(np.asarray(fp) @ self.proj)
            else:
                v = np.random.default_rng(_seed("u", e["id"])).standard_normal(LATENT) / np.sqrt(LATENT)
            self.u[e["id"]] = v
        return self.u[e["id"]]

    def set_projection(self, dim, seed):
        self.proj = np.random.default_rng(seed).standard_normal((dim, LATENT)) / np.sqrt(dim)

    def refresh_latent(self, e):
        self.u.pop(e["id"], None)
        return self.latent(e)

    def gains(self, parents):
        return [float(2.0 * np.tanh(self.latent(p) @ self.w[j % 16] * 2.0)) for j, p in enumerate(parents)]

    def record(self, pids, child_id, law, outcome=None):
        key = tuple(pids)
        self.edges[key] = {"parents": list(pids), "child": child_id, "law": law, "outcome": outcome}
        for p in pids:
            self.uses[p] = self.uses.get(p, 0) + 1
        s = sorted(set(pids))
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                k = (s[i], s[j])
                self.pair_uses[k] = self.pair_uses.get(k, 0) + 1

    def set_outcome(self, pids, outcome):
        self.edges[tuple(pids)]["outcome"] = outcome


def _remap(rule, C, shift):
    r = copy.deepcopy(rule)
    r["src"] = [(s + shift) % C for s in r["src"]]
    r["dst"] = (r["dst"] + shift) % C
    return r


def _mark(rule, cid, how):
    rule["prov"] = f"x:{cid}:{how}|{rule.get('prov', '?')}"
    return rule


def collide(parents, tensor, cid, extra_seed=0, operators=None, law=True, aligned=False, random_law_gains=False):
    """parents: ordered list of entity dicts. Returns (genome, record).

    law=False (THESEUS-28 ablation): the k-ary interaction law is generated (so every RNG
    draw is identical to law=True) but NOT inserted into the child.

    aligned=True (THESEUS-34): parent channels keep their indices (no positional remap
    (c + j) mod C), so parts inherited from different lineages address the same memory
    slots; every RNG draw is unchanged."""
    k = len(parents)
    rng = np.random.default_rng(_seed("collide", cid, [p["id"] for p in parents], extra_seed))
    genomes = []
    for p in parents:
        if p.get("kind") == "lens":
            genomes.append(None)
        else:
            genomes.append(p["executableRepresentation"])
    Cs = [g["C"] for g in genomes if g is not None] or [1]
    C = max(Cs)
    ops_used = []
    if operators is None:
        n_ops = int(rng.integers(1, 4))
        operators = list(rng.choice(OPERATORS, size=n_ops, replace=False))
    if "state_merge" in operators and C < sb.CMAX:
        C = min(sb.CMAX, C + 1)
        ops_used.append("state_merge")
    budget = sb.MAXRULES - int(np.ceil(k / 8))
    share = max(1, int(round(budget / k)))
    blocks = []
    primaries = []
    for j, (p, g) in enumerate(zip(parents, genomes)):
        if g is None:  # lens entity
            src = int(rng.integers(C))
            dst = (src + 1 + j) % C
            r = {"op": "lensmap", "src": [src], "dst": dst, "p": [float(rng.uniform(0.1, 0.6))],
                 "lens": p["executableRepresentation"], "prov": f"L:{p['id']}"}
            blocks.append([r])
            primaries.append(src)
            continue
        rules = g["rules"]
        n = min(len(rules), share)
        if n < len(rules):
            start = int(rng.integers(len(rules)))
            idx = [(start + i) % len(rules) for i in range(n)]  # contiguous (cyclic) run: keeps local order
        else:
            idx = list(range(len(rules)))
        blk = [_remap(rules[i], C, 0 if aligned else j) for i in idx]
        blocks.append(blk)
        primaries.append((blk[0]["dst"] if blk else j) % C)

    # generated k-ary interaction law(s): concept-tensor entry in CP form
    gains = tensor.gains(parents)
    if random_law_gains:
        # THESEUS-51: same law placement/sources/dst/amp/bias, but per-source gains drawn from an
        # independent RNG instead of the concept tensor (no tensor content). The main rng is
        # untouched, so every other draw is identical to the default.
        grng = np.random.default_rng(_seed("randgain", cid, [p["id"] for p in parents], extra_seed))
        gains = [float(x) for x in grng.uniform(-2.0, 2.0, size=len(gains))]
    amp = float(rng.uniform(-1.0, 1.0))
    bias = float(rng.uniform(-1.0, 1.0))
    laws = []
    for s0 in range(0, k, 8):
        srcs = primaries[s0:s0 + 8]
        gs = gains[s0:s0 + 8]
        dst = int(primaries[(s0 + len(srcs)) % k] if k > 1 else primaries[0])
        laws.append({"op": "react", "src": [int(s) for s in srcs], "dst": dst % C,
                     "p": [amp, bias] + [float(np.clip(g, -2, 2)) for g in gs], "prov": f"law:{cid}"})
    law_record = {"gains": gains, "amp": amp, "bias": bias, "n_law_rules": len(laws)}
    if random_law_gains:
        law_record["gains_source"] = "random"

    flat = [r for b in blocks for r in b]
    if "param_inherit" in operators:
        by_op = {}
        for r in flat:
            by_op.setdefault(r["op"], []).append(r)
        for op, rs in by_op.items():
            if len(rs) > 1 and op not in ("react", "lensmap"):
                w = np.linspace(1.0, 0.5, len(rs))
                w = w / w.sum()
                mean = [float(sum(w[i] * rs[i]["p"][jj] for i in range(len(rs)))) for jj in range(len(rs[0]["p"]))]
                tgt = rs[-1]
                tgt["p"] = [sb.clamp_param(op, jj, v) for jj, v in enumerate(mean)]
                _mark(tgt, cid, "inherit")
                ops_used.append("param_inherit")
                break
    if "substitute" in operators and len(blocks) > 1:
        a = int(rng.integers(len(flat)))
        donors = [r["op"] for r in flat if r["op"] != flat[a]["op"] and sb.OPS[r["op"]][0] == sb.OPS[flat[a]["op"]][0]
                  and r["op"] not in ("lensmap", "react")]
        if donors and flat[a]["op"] not in ("lensmap", "react"):
            new = donors[int(rng.integers(len(donors)))]
            flat[a]["op"] = new
            flat[a]["p"] = sb.rand_params(new, rng, len(flat[a]["src"]))
            _mark(flat[a], cid, "substitute")
            ops_used.append("substitute")
    extra = []
    if "symmetry_inherit" in operators:
        sym = [r for r in flat if r["op"] in ("mirror", "conserve")]
        if sym:
            r = copy.deepcopy(sym[0])
            r["dst"] = int(primaries[-1]) % C
            extra.append(_mark(r, cid, "symmetry"))
            ops_used.append("symmetry_inherit")
    if "cross_scale" in operators and k > 1:
        extra.append(_mark({"op": "coarse", "src": [int(primaries[0])], "dst": int(primaries[-1]) % C,
                            "p": [int(rng.integers(1, 4)), float(rng.uniform(0.05, 0.5))]}, cid, "cross_scale"))
        ops_used.append("cross_scale")
    if "memory_transfer" in operators and k > 1:
        a, b = int(primaries[0]), int(primaries[-1]) % C
        extra.append(_mark({"op": "remember", "src": [a], "dst": b, "p": [float(rng.uniform(0.05, 0.5))]}, cid, "memory"))
        extra.append(_mark({"op": "recall", "src": [], "dst": b, "p": [float(rng.uniform(-0.8, 0.8))]}, cid, "memory"))
        ops_used.append("memory_transfer")

    rules = flat[:]
    pos = int(rng.integers(len(rules) + 1))
    if not law:
        laws = []
        law_record["ablated"] = True
    rules[pos:pos] = laws
    rules += extra
    if len(rules) > sb.MAXRULES:
        keep_law = [i for i, r in enumerate(rules) if r["prov"] == f"law:{cid}"]
        others = [i for i in range(len(rules)) if i not in keep_law]
        drop = set(rng.choice(others, size=len(rules) - sb.MAXRULES, replace=False).tolist())
        rules = [r for i, r in enumerate(rules) if i not in drop]

    real = [g for g in genomes if g is not None]
    first = real[0] if real else {"topo": {"kind": "ring", "seed": 0}, "bc": "periodic", "init": {"kind": "spike", "amp": 1.0}}
    last = real[-1] if real else first
    mid = real[len(real) // 2] if real else first
    topo = copy.deepcopy(first["topo"])
    bc = first["bc"]
    if "bc_exchange" in operators:
        bc = last["bc"]
        topo = copy.deepcopy(last["topo"]) if last["topo"]["kind"] != topo["kind"] else topo
        ops_used.append("bc_exchange")
    g = {"C": C, "topo": topo, "bc": bc, "init": copy.deepcopy(mid["init"]), "rules": rules}
    if "mutate" in operators:
        g = mutate(g, rng, cid)
        ops_used.append("mutate")
    errs = sb.validate(g)
    assert not errs, (errs, g)
    return g, {"cid": cid, "parents": [p["id"] for p in parents], "arity": k,
               "operators_requested": list(operators), "operators_applied": ops_used, "law": law_record}


def mutate(g, rng, cid, n=1):
    g = copy.deepcopy(g)
    for _ in range(n):
        kind = rng.random()
        if kind < 0.5 and g["rules"]:
            i = int(rng.integers(len(g["rules"])))
            r = g["rules"][i]
            if r["p"]:
                j = int(rng.integers(len(r["p"])))
                v = r["p"][j] * float(rng.uniform(0.5, 1.5)) + float(rng.normal(0, 0.1))
                r["p"][j] = sb.clamp_param(r["op"], j, v)
                _mark(r, cid, "mut_param")
        elif kind < 0.7 and len(g["rules"]) < sb.MAXRULES:
            r = sb.rand_rule(rng, g["C"], prov=f"x:{cid}:mut_insert")
            g["rules"].insert(int(rng.integers(len(g["rules"]) + 1)), r)
        elif kind < 0.85 and len(g["rules"]) > 1:
            g["rules"].pop(int(rng.integers(len(g["rules"]))))
        elif len(g["rules"]) > 1:
            i, j = rng.choice(len(g["rules"]), size=2, replace=False)
            g["rules"][i], g["rules"][j] = g["rules"][j], g["rules"][i]
    return g


def random_genome(rng, n_rules, C, max_src=3, prov="rand"):
    """Complexity-matched random program (control)."""
    rules = [sb.rand_rule(rng, C, prov=prov, arity=int(rng.integers(1, max_src + 1))) for _ in range(n_rules)]
    g = {"C": C, "topo": {"kind": sb.TOPOS[int(rng.integers(len(sb.TOPOS)))], "seed": int(rng.integers(1 << 16))},
         "bc": sb.BCS[int(rng.integers(len(sb.BCS)))],
         "init": {"kind": sb.INITS[int(rng.integers(len(sb.INITS)))], "amp": 1.0}, "rules": rules}
    assert not sb.validate(g)
    return g
