"""The LIVE structural transition kernel, measured in parallel. V0.6 brief sections 2 and 5.

The adjudicated kernel is estimated by EXECUTING grammar.mutate, never by modelling it. V0.5
showed the analytic kernel is off by up to 0.17 total variation, so the analytic form is admitted
only as secondary evidence.

Parallelism is exact, not approximate. Each state's random stream is derived as
root.derive(L, T) and `derive` does not advance the parent, so the stream for a state depends only
on (seed, tag, L, T). Splitting states across worker processes therefore produces byte-identical
counts to a serial run; a unit test asserts this on a subspace.

Per state we record, as the brief requires: transition counts, self-loops, per-operator
destination counts, and the rejection reason recorded by the operator itself.
"""
from __future__ import annotations

import os
from collections import Counter, defaultdict

from proteus.foundry import grammar
from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import SCHEMA

IW = 4
_CFG = {"n_regs": 8, "persist": "none", "code_writable": False, "tick_budget": 64, "out_cap": 4}


def manifest(rng, L, T):
    return {"schema_version": SCHEMA, "n_regs": _CFG["n_regs"], "tape_words": T,
            "genome": [rng.next_u32() for _ in range(IW * L)],
            "code_writable": _CFG["code_writable"], "persist": _CFG["persist"],
            "tick_budget": _CFG["tick_budget"], "out_cap": _CFG["out_cap"]}


def measure_state(args):
    """One state. Returns (state, dest_counts, op_dest_counts, noop_reasons, escapes).

    `escapes` counts destinations outside the supplied valid-state set; the brief requires this to
    be zero over the whole space and treats any nonzero value as an instrument failure.
    """
    (L, T), samples, seed, tag, inside, fold = args
    r = SplitMix64(seed_from("proteus.v0_6.kernel", seed, tag)).derive(L, T)
    dest = Counter()
    opdest = defaultdict(Counter)
    noop = Counter()
    escapes = Counter()
    for _ in range(samples):
        m = manifest(r, L, T)
        mate = manifest(r, L, T)
        child, rec = grammar.mutate(m, r, mate)
        j = (len(child["genome"]) // IW, child["tape_words"])
        if inside is not None and j not in inside:
            escapes[j] += 1
            if fold:
                j = (L, T)          # rejection semantics; a no-op on a CLOSED space
        dest[j] += 1
        opdest[rec["operator"]][j] += 1
        if "noop" in rec["args"]:
            noop[(rec["operator"], str(rec["args"]["noop"]))] += 1
    return ((L, T), dict(dest), {k: dict(v) for k, v in opdest.items()},
            {f"{a}:{b}": n for (a, b), n in noop.items()}, dict(escapes))


def measure_kernel_parallel(states, samples, seed, tag, workers=None, chunk=8, fold_escapes=True):
    """Full live kernel over `states`. Deterministic and independent of worker count.

    `fold_escapes` folds a destination outside `states` into the self-loop, which is a NO-OP on a
    closed state set. The V0.6 production space is proved closed (zero escapes over 817,600
    proposals), so this only matters when the analysis tools are exercised on a truncated subset,
    where a leaking row would otherwise not be a stochastic matrix. Escapes are ledgered either way.
    """
    import multiprocessing as mp
    inside = frozenset(states)
    work = [(s, samples, seed, tag, inside, fold_escapes) for s in states]
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    if workers == 1:
        rows = [measure_state(w) for w in work]
    else:
        with mp.Pool(workers) as pool:
            rows = pool.map(measure_state, work, chunksize=chunk)
    P, OP, NOOP, ESC = {}, {}, {}, {}
    for st, dest, opdest, noop, esc in rows:
        tot = sum(dest.values())
        P[st] = {j: n / tot for j, n in dest.items()}
        OP[st] = opdest
        if noop:
            NOOP[st] = noop
        if esc:
            ESC[st] = esc
    return P, OP, NOOP, ESC


def counts_from(P, samples):
    """Recover integer counts from probabilities (exact: probabilities are n/samples)."""
    return {i: {j: int(round(p * samples)) for j, p in row.items()} for i, row in P.items()}


def row_tv(a, b):
    keys = set(a) | set(b)
    return 0.5 * sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)


def compare(PA, PB, states):
    return [row_tv(PA[s], PB[s]) for s in states]
