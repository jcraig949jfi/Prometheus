"""Target-blind archive descriptors and the OUTCOME-FREE descriptor qualification test.

A descriptor maps (program, its dev outputs, its probe outputs, the LearnerView) to a hashable CELL. It may use dev
targets (learner feedback) and target-free probe inputs; it never sees test outputs, the witness or the tribunal (the
LearnerView does not hold them).

Candidates (may guide an archive only after passing qualification):
  D-BEH   coarse behavioural fingerprint on the 8 target-free PROBE inputs: per probe, FAIL | Int (sign, bucket
          floor(log2(|v|+1)) capped at 16) | List (len capped at 8, sign of sum, log2 bucket of |sum|) | Bool value.
  D-CERT  partial-mechanism certificate on dev: per dev example a level 3 = exact, 2 = partial credit >= 1/2,
          1 = partial credit > 0, 0 = none / FAIL (Int/Bool outputs only take 3 or 0).
  D-RES   residual signature on dev: per dev example '=' exact, 'F' FAIL, 'T' wrong type, Int '<' / '>' (output
          below/above target), List: length relation '<' '=' '>' plus, for equal length, 'p' (some positions exact)
          or 'n' (none), Bool '!' wrong.
Must-fail controls and references (never guide an archive):
  C-FIT   the exact dev credit (score bin)          -> must FAIL R1 (equal score = same cell by construction).
  GENO    the comm-canonical genotype text          -> must FAIL R2 (synonyms are different genomes).
  TRACE   exact dev outputs + exact probe outputs   -> the finest behaviour descriptor; reported beside.
  RAND:K  blake2b(salt, genotype) mod K             -> the random-archive control cell function (not qualified).

Qualification test = the committed C-013 D1 procedure (rso/reach/descriptor.py + PREREGISTRATION s0: R1 / R1c / R2
with planted must-fail controls C-FIT and GENO, TRACE beside), PORTED to TFS-1 (their world is not imported); the
D1 numbers (C-BEH R1 0.006 on p1_slice) are world-specific and are not a comparator here:
  intermediates  = the witness's pruning lattice under the search's own mutation operator (route.lattice) minus W.
  others (pool)  = (as D1) uniform random programs -- every size class 1..min(8, size(W)+1) -- plus OFF-PATH one- and
                   two-step mutants of the target and of every intermediate; plus short random mutation walks from the
                   generic starts; lattice members excluded. "Score" = exact dev credit (the search's fitness).
                   20 equal-score others per intermediate (D1 `per`).
  R1  separation = share of (intermediate, equal-score other) pairs put in DIFFERENT cells.          PASS >= 0.90
  R1c            = R1 restricted to pairs whose TRACE differs (behaviourally distinguishable pairs).
  R2  invariance = share of (intermediate, semantics-preserving synonym) pairs put in the SAME cell.  PASS >= 0.90
  G   granularity= distinct cells / distinct genotypes over the pool (Beta-04 addition, Nyx A4 over-splitting guard;
                   REPORTED as OVERSPLIT_WARNING if > 0.50, NOT part of the D1 verdict)
  Minimum evidence: >= 20 R1 pairs and >= 20 R2 pairs, else INSUFFICIENT.
  controls_ok    = C-FIT fails R1 AND GENO fails R2 (else the test itself is broken -> every verdict VOID).
A candidate is QUALIFIED iff R1 and R2 pass (the D1 rule), evidence is sufficient and controls_ok. A failed descriptor makes any
archive arm guided by it INSTRUMENT_UNVALIDATED.
"""
import math
from typing import Dict, List, Optional, Sequence

from tfs1 import core as C
from tfs1.enum import Enumerator, canon_comm
from tfs1.mutate import Mutator

from . import common as K
from . import route as R
from .sample import sample_uniform

R1_PASS = 0.90
R2_PASS = 0.90
G_PASS = 0.50
MIN_PAIRS = 20


def _hashable(v):
    return tuple(v) if isinstance(v, list) else v


def _bucket(v: int) -> int:
    return min(16, int(math.log2(abs(v) + 1)))


def _coarse(v):
    if v == C.FAIL:
        return "F"
    if isinstance(v, bool):
        return ("b", v)
    if isinstance(v, int):
        return ("i", (v > 0) - (v < 0), _bucket(v))
    s = sum(v)
    return ("l", min(len(v), 8), (s > 0) - (s < 0), _bucket(s))


def _cert_level(v, o) -> int:
    p = K._partial_one(v, o)
    if p == 1.0:
        return 3
    if p >= 0.5:
        return 2
    if p > 0:
        return 1
    return 0


def _res(v, o):
    if v == C.FAIL:
        return "F"
    if type(v) is not type(o):
        return "T"
    if v == o:
        return "="
    if isinstance(o, bool):
        return "!"
    if isinstance(o, int):
        return "<" if v < o else ">"
    if len(v) != len(o):
        return "<" if len(v) < len(o) else ">"
    return "=p" if any(a == b for a, b in zip(v, o)) else "=n"


class Descriptor:
    name = "?"
    needs_probes = False
    guides = True                 # may guide an archive (after qualification)

    def cell(self, text: str, dev_outs, probe_outs, view) -> object:
        raise NotImplementedError


class DBeh(Descriptor):
    name, needs_probes = "D-BEH", True

    def cell(self, text, dev_outs, probe_outs, view):
        return tuple(_coarse(v) for v in probe_outs)


class DCert(Descriptor):
    name = "D-CERT"

    def cell(self, text, dev_outs, probe_outs, view):
        return tuple(_cert_level(v, o) for v, o in zip(dev_outs, view.targets))


class DRes(Descriptor):
    name = "D-RES"

    def cell(self, text, dev_outs, probe_outs, view):
        return tuple(_res(v, o) for v, o in zip(dev_outs, view.targets))


class CFit(Descriptor):
    name, guides = "C-FIT", False

    def cell(self, text, dev_outs, probe_outs, view):
        return K.exact_credit(dev_outs, view.targets)


class Geno(Descriptor):
    name, guides = "GENO", False

    def cell(self, text, dev_outs, probe_outs, view):
        return text


class Trace(Descriptor):
    name, needs_probes, guides = "TRACE", True, False

    def cell(self, text, dev_outs, probe_outs, view):
        return (tuple(_hashable(v) for v in dev_outs), tuple(_hashable(v) for v in probe_outs))


class RandHash(Descriptor):
    """Random-archive control: a structure-free hash of the genotype into K buckets (matched cell count)."""
    guides = True

    def __init__(self, k: int, salt: str = "RAND"):
        self.k = max(1, int(k))
        self.salt = salt
        self.name = "RAND:%d" % self.k

    def cell(self, text, dev_outs, probe_outs, view):
        return K.h64("%s/%s" % (self.salt, text)) % self.k


CANDIDATES = {"D-BEH": DBeh, "D-CERT": DCert, "D-RES": DRes}
CONTROLS = {"C-FIT": CFit, "GENO": Geno, "TRACE": Trace}


def get(name: str) -> Descriptor:
    if name.startswith("RAND:"):
        return RandHash(int(name.split(":")[1]))
    return {**CANDIDATES, **CONTROLS}[name]()


# ================================================================ qualification
def _record(t, view: K.LearnerView, lib):
    fn = K.compile_p(t, lib)
    dev = K.outs_of(t, view.dev_inputs, lib, fn)
    probes = K.outs_of(t, view.probes, lib, fn)
    return {"text": C.to_str(canon_comm(t)), "dev": dev, "probes": probes,
            "score": K.exact_credit(dev, view.targets), "size": C.size(t)}


def build_pool(E: Enumerator, mut: Mutator, view: K.LearnerView, T: str, max_n: int, per_size: int,
               walk_n: int, seed, exclude: set) -> List[tuple]:
    r = K.rng("POOL", view.family_id, seed)
    seen, pool = set(exclude), []
    for n in range(1, max_n + 1):
        tot = E.count(T, (), n)
        if tot == 0:
            continue
        want = min(per_size, tot)
        tries = 0
        got = 0
        while got < want and tries < 4 * want:
            tries += 1
            t = sample_uniform(E, T, (), n, r)
            k = C.to_str(t)
            if k in seen:
                continue
            seen.add(k)
            pool.append(t)
            got += 1
    starts = [C.parse(s) for s in K.STARTS[T]]
    for _ in range(walk_n):
        t = starts[r.randrange(len(starts))]
        for _d in range(r.randint(1, 6)):
            c = mut.mutate(t, T, r)
            if c is not None:
                t = c
        k = C.to_str(canon_comm(t))
        if k not in seen:
            seen.add(k)
            pool.append(t)
    return pool


def qualify(task: Dict, witness: str, lib=None, names: Sequence[str] = ("D-BEH", "D-CERT", "D-RES"),
            per_size: int = 1500, walk_n: int = 6000, max_pairs: int = 20, n_syn: int = 6, seed=0,
            max_fill: int = 3, mutants_per_node: int = 60) -> Dict:
    """Outcome-free descriptor qualification on a task with a known witness. No search outcome is used."""
    view = K.LearnerView(task)
    T = task["output_type"]
    E = Enumerator(lib)
    mut = Mutator(E, max_fill=max_fill)
    W = C.parse(witness)
    lat = R.lattice(mut, W, T)
    wkey = C.to_str(W)
    inter_terms = [nd["term"] for k, nd in sorted(lat["nodes"].items()) if k != wkey]
    exclude = set(lat["nodes"]) | {R.canon_text(nd["term"]) for nd in lat["nodes"].values()}
    inter = [_record(t, view, lib) for t in inter_terms]
    depth_of = {C.to_str(nd["term"]): nd["depth"] for nd in lat["nodes"].values()}
    for rec, t in zip(inter, inter_terms):
        rec["term"] = t
        rec["depth"] = depth_of[C.to_str(t)]
    max_n = min(8, C.size(W) + 1)
    pool_t = build_pool(E, mut, view, T, max_n, per_size, walk_n, seed, exclude)
    # D1: off-path one- and two-step mutants of the target and of the intermediates (lattice members excluded)
    rm = K.rng("POOL-MUT", view.family_id, seed)
    seen = exclude | {C.to_str(canon_comm(t)) for t in pool_t}
    for nd in lat["nodes"].values():
        for j in range(mutants_per_node):
            c = mut.mutate(nd["term"], T, rm)
            if c is not None and j % 2 == 1:
                c2 = mut.mutate(c, T, rm)
                c = c2 if c2 is not None else c
            if c is None:
                continue
            k = C.to_str(canon_comm(c))
            if k in seen or C.to_str(c) in exclude:
                continue
            seen.add(k)
            pool_t.append(c)
    pool = [_record(t, view, lib) for t in pool_t]
    by_score: Dict[int, List[int]] = {}
    for j, p in enumerate(pool):
        by_score.setdefault(p["score"], []).append(j)
    descs = [get(n) for n in list(names) + list(CONTROLS)]
    cell = lambda d, rec: d.cell(rec["text"], rec["dev"], rec["probes"], view)   # noqa: E731
    r = K.rng("QUAL", view.family_id, seed)
    # R1 pairs (deterministic sample of equal-score others per intermediate)
    pairs, no_match = [], 0
    for i, rec in enumerate(inter):
        js = by_score.get(rec["score"], [])
        if not js:
            no_match += 1
            continue
        pick = js if len(js) <= max_pairs else r.sample(js, max_pairs)
        pairs += [(i, j) for j in pick]
    # R2 synonyms
    syn = []
    syn_mismatch = 0
    for i, rec in enumerate(inter):
        for q in R.synonyms(mut, rec["term"], T, r, n_syn):
            srec = _record(q, view, lib)
            srec["text"] = C.to_str(q)          # synonyms keep their own (non-canonical) spelling as genotype
            if srec["dev"] != rec["dev"] or srec["probes"] != rec["probes"]:
                syn_mismatch += 1
                continue
            syn.append((i, srec))
    trace = get("TRACE")
    out = {"witness": witness, "family_id": view.family_id, "lattice_size": len(lat["nodes"]),
           "lattice_truncated": lat["truncated"], "intermediates": len(inter),
           "intermediate_scores": sorted({x["score"] for x in inter}),
           "intermediates_with_no_equal_score_other": no_match, "pool_size": len(pool),
           "pool_score_hist": {str(k): len(v) for k, v in sorted(by_score.items())},
           "pairs_R1": len(pairs), "pairs_R2": len(syn), "synonym_semantic_mismatches": syn_mismatch,
           "thresholds": {"R1_PASS": R1_PASS, "R2_PASS": R2_PASS, "G_PASS_max": G_PASS, "MIN_PAIRS": MIN_PAIRS},
           "descriptors": {}}
    pool_geno = len({p["text"] for p in pool})
    pool_traces = len({cell(trace, p) for p in pool})
    for d in descs:
        ic = [cell(d, x) for x in inter]
        pc = [cell(d, p) for p in pool]
        diff = [ic[i] != pc[j] for i, j in pairs]
        bdist = [(ic[i] != pc[j]) for i, j in pairs if cell(trace, inter[i]) != cell(trace, pool[j])]
        same = [ic[i] == cell(d, s) for i, s in syn]
        by_lvl, by_depth = {}, {}
        for (i, j), dd in zip(pairs, diff):
            by_lvl.setdefault(inter[i]["score"], []).append(dd)
            by_depth.setdefault(inter[i]["depth"], []).append(dd)
        cells = len(set(pc))
        r1 = sum(diff) / len(diff) if diff else None
        r2 = sum(same) / len(same) if same else None
        g = cells / pool_geno if pool_geno else None
        rec = {"R1_separation": r1, "R1c_given_trace_differs": (sum(bdist) / len(bdist)) if bdist else None,
               "pairs_R1c": len(bdist), "R2_invariance": r2, "granularity_cells_per_genotype": g,
               "cells_per_distinct_trace": cells / pool_traces if pool_traces else None, "pool_cells": cells,
               "R1_by_intermediate_score": {str(k): round(sum(v) / len(v), 4) for k, v in sorted(by_lvl.items())},
               "R1_by_prune_depth": {str(k): round(sum(v) / len(v), 4) for k, v in sorted(by_depth.items())},
               "R1c": "PASS" if bdist and sum(bdist) / len(bdist) >= R1_PASS else "FAIL",
               "R1": "PASS" if r1 is not None and r1 >= R1_PASS else "FAIL",
               "R2": "PASS" if r2 is not None and r2 >= R2_PASS else "FAIL",
               "G": "PASS" if g is not None and g <= G_PASS else "FAIL",
               "OVERSPLIT_WARNING": bool(g is not None and g > G_PASS)}
        out["descriptors"][d.name] = rec
    ds = out["descriptors"]
    out["controls_ok"] = ds["C-FIT"]["R1"] == "FAIL" and ds["GENO"]["R2"] == "FAIL"
    enough = len(pairs) >= MIN_PAIRS and len(syn) >= MIN_PAIRS
    for n in names:
        x = ds[n]
        if not out["controls_ok"]:
            v = "VOID_CONTROLS"
        elif not enough:
            v = "INSUFFICIENT"
        else:
            v = "QUALIFIED" if (x["R1"] == x["R2"] == "PASS") else "FAIL"      # the C-013 D1 rule
        x["verdict"] = v
    out["qualified"] = [n for n in names if ds[n]["verdict"] == "QUALIFIED"]
    return out
