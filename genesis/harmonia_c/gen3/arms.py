"""The six generative arms and the single shared search engine.

Frozen by PREREGISTRATION.md section 4.  The arms differ ONLY in the variation
operator; the initial population, selection rule, archive-write rule, budget and RNG
discipline are byte-identical across arms by construction (one engine, one code path).

Ancestry is recorded as it happens (never inferred afterwards).  Every candidate gets a
compact row; genomes are persisted for every node on a recorded lineage, which is what
makes exact replay possible.

Self-test:  python arms.py --test
"""

from __future__ import annotations

import argparse
import random

import numpy as np

from arena import (L_MAX, N_OPS, N_REG, OUT_LO, World, prog_hash, run)

# op 12 is CALL, available ONLY to arm D.  It never appears in an expressed program.
OP_CALL = 12

ARMS = ["A_LOCAL", "B_STRUCT", "C_COMPOSE", "D_ENCAPS", "E_COMP_REF", "F_RANDOM"]

MU = 12              # population size
INIT_LEN = (6, 16)   # initial random program length range
EVALS = 40_000       # frozen per-run evaluation budget (bootstrap + arm phase)
BOOTSTRAP = 20_000   # shared, arm-identical phase that builds the archive every arm
                     # inherits.  Without it the campaign measures each arm's ability to
                     # bootstrap primitives from nothing, which is not the hypothesis:
                     # the claim is about reuse of PREVIOUSLY VIABLE behaviors.


# ------------------------------------------------------------------ genome utilities

def rand_instr(rng):
    op = rng.randrange(N_OPS)
    a = rng.randrange(N_REG)
    b = rng.randrange(N_REG)
    return (op, a, b)


def rand_prog(rng, lo=INIT_LEN[0], hi=INIT_LEN[1]):
    return [rand_instr(rng) for _ in range(rng.randint(lo, hi))]


def expand(genome, macros):
    """Genome -> expressed straight-line program.  CALL m splices macro m inline."""
    out = []
    for ins in genome:
        if ins[0] == OP_CALL:
            body = macros[ins[1] % len(macros)] if macros else []
            out.extend(body)
        else:
            out.append(ins)
        if len(out) >= L_MAX:
            return out[:L_MAX], True
    return out, False


def edit_radius(pa, pb):
    """Aligned edit count between two EXPRESSED programs.

    Defined explicitly rather than left implicit: |len difference| plus the number of
    positions in the common prefix whose instruction triples differ.  Cheap, symmetric,
    and monotone in the thing it is measuring.  It is a lower bound on true Levenshtein
    distance and it is applied identically to every arm.
    """
    n = min(len(pa), len(pb))
    diff = sum(1 for i in range(n) if pa[i] != pb[i])
    return diff + abs(len(pa) - len(pb))


# ------------------------------------------------------------------------- operators

def op_local(rng, genome, **kw):
    """A: point mutation -- one instruction's op OR one operand."""
    if not genome:
        return [rand_instr(rng)], []
    g = list(genome)
    i = rng.randrange(len(g))
    op, a, b = g[i]
    which = rng.randrange(3)
    if which == 0:
        op = rng.randrange(N_OPS)
    elif which == 1:
        a = rng.randrange(N_REG)
    else:
        b = rng.randrange(N_REG)
    g[i] = (op, a, b)
    return g, []


def op_struct(rng, genome, **kw):
    """B: segment mutation -- insert / delete / duplicate / move a contiguous block."""
    g = list(genome)
    kind = rng.randrange(4)
    if kind == 0 or not g:                       # insert a fresh random block
        blk = [rand_instr(rng) for _ in range(rng.randint(1, 4))]
        i = rng.randint(0, len(g))
        g[i:i] = blk
    elif kind == 1:                              # delete a block
        i = rng.randrange(len(g))
        j = min(len(g), i + rng.randint(1, 4))
        del g[i:j]
    elif kind == 2:                              # duplicate a block
        i = rng.randrange(len(g))
        j = min(len(g), i + rng.randint(1, 4))
        blk = g[i:j]
        k = rng.randint(0, len(g))
        g[k:k] = blk
    else:                                        # move a block
        i = rng.randrange(len(g))
        j = min(len(g), i + rng.randint(1, 4))
        blk = g[i:j]
        del g[i:j]
        k = rng.randint(0, len(g))
        g[k:k] = blk
    return g[:L_MAX], []


def op_compose(rng, genome, mates=None, **kw):
    """C: graft two DISTINCT viable archive members.  No follow-up mutation."""
    pa, pb = mates
    cut_a = rng.randint(1, max(1, len(pa)))
    cut_b = rng.randint(0, max(0, len(pb) - 1))
    child = pa[:cut_a] + pb[cut_b:]
    return child[:L_MAX], ["parentA", "parentB"]


def op_comp_ref(rng, genome, mates=None, **kw):
    """E: compose, then one arm-A mutation."""
    child, reused = op_compose(rng, None, mates=mates)
    child, _ = op_local(rng, child)
    return child[:L_MAX], reused


def op_encaps(rng, genome, macros=None, **kw):
    """D: mutate over the macro-extended alphabet (a CALL costs one token)."""
    g = list(genome)
    if macros and rng.random() < 0.35:
        ins = (OP_CALL, rng.randrange(len(macros)), 0)
        if g and rng.random() < 0.5:
            g[rng.randrange(len(g))] = ins
        else:
            g.insert(rng.randint(0, len(g)), ins)
        return g[:L_MAX], ["macro%d" % (ins[1],)]
    return op_local(rng, g)


def op_random(rng, genome, **kw):
    """F: uniform random program of matched expressed length (the control)."""
    n = len(genome) if genome else rng.randint(*INIT_LEN)
    return [rand_instr(rng) for _ in range(max(1, n))], []


OPERATORS = {
    "A_LOCAL": op_local, "B_STRUCT": op_struct, "C_COMPOSE": op_compose,
    "D_ENCAPS": op_encaps, "E_COMP_REF": op_comp_ref, "F_RANDOM": op_random,
}
USES_ARCHIVE = {"C_COMPOSE", "D_ENCAPS", "E_COMP_REF"}


# --------------------------------------------------------------------------- engine

class Run:
    """One (arm, world, seed) run.  Ancestry is written as it happens."""

    def __init__(self, arm, world_name, seed, evals=EVALS, radius_cap=None,
                 bootstrap=BOOTSTRAP):
        self.arm = arm
        self.world = World(world_name)
        self.seed = seed
        self.evals = evals
        self.bootstrap = bootstrap
        self.radius_cap = radius_cap      # E3: reject children beyond this edit radius
        # Bootstrap RNG depends ONLY on the seed, so the shared phase -- and therefore
        # the archive every arm inherits -- is byte-identical across arms.
        self.boot_rng = random.Random(seed * 7919 + 13)
        self.rng = random.Random(seed * 7919 + ARMS.index(arm) * 104729)
        # The INITIAL POPULATION depends only on the seed -- identical across arms.
        init_rng = random.Random(seed * 7919)
        self.pop = [rand_prog(init_rng) for _ in range(MU)]

        self.rows = []        # (id, pa, pb, opname, gen, exact, frac, viable, sig)
        self.genomes = {}     # id -> genome, for every node on a recorded lineage
        self.archive = {}     # frozenset(train capset) -> (genome, id)
        self.next_id = 0
        self.n_evals = 0
        self.vm_instructions = 0
        self.fallbacks = 0
        self.truncations = 0
        self.radii = []
        self.radii_arm = []   # arm-phase only; pooling the shared bootstrap made
                              # A_LOCAL read 6.46 when its true radius is ~1
        self.rejected_by_radius = 0
        self.crossings = []   # (id, capset, gen, evals_at)
        self.best = (-1, -1.0, None)
        self.first_cross_eval = {}   # slot -> eval index of first heldout acquisition
        self.pop_ids = []
        self._refit_done = False

    # -- bookkeeping ------------------------------------------------------------
    def _record(self, genome, pa, pb, opname, exact, frac, viable, sig, keep_genome):
        i = self.next_id
        self.next_id += 1
        self.rows.append((i, pa, pb, opname, self.n_evals, exact, round(frac, 6),
                          int(viable), sig))
        if keep_genome:
            self.genomes[i] = list(genome)
        return i

    def _evaluate(self, expressed, slots=None):
        """One charged evaluation.  HELDOUT measurement is NOT charged here and is never
        visible to selection -- it is the instrument, not the search signal."""
        self.n_evals += 1
        self.vm_instructions += len(expressed) * self.world.train.shape[1]
        return self.world.eval_train(expressed, slots)

    # -- main loop --------------------------------------------------------------
    def go(self):
        w = self.world
        fits = []
        pop_sigs = set()
        pop_sigs_by_slot = []
        # seed the population records (one charged evaluation each, no double count)
        for g in self.pop:
            expressed, trunc = expand(g, [])
            exact, frac, tcap = self._evaluate(expressed, self.world.boot_slots)
            viable = exact >= 1
            sig = w.signature(expressed)
            i = self._record(g, -1, -1, "INIT", exact, frac, viable, sig, True)
            self.pop_ids.append(i)
            fits.append((exact, frac))
            pop_sigs.add(sig)
            pop_sigs_by_slot.append(sig)
            self._maybe_archive(g, expressed, tcap, i)
            self._check_cross(g, expressed, i, tcap)

        while self.n_evals < self.evals:
            in_bootstrap = self.n_evals < self.bootstrap
            rng = self.boot_rng if in_bootstrap else self.rng
            macros = [v[1] for v in self.archive.values()]   # EXPRESSED, CALL-free
            distinct = len(self.archive)
            pi = rng.randrange(MU)
            parent = self.pop[pi]
            pa_id, pb_id = self.pop_ids[pi], -1
            opname = "BOOTSTRAP" if in_bootstrap else self.arm
            mates = None

            if in_bootstrap:
                # Shared bootstrap: EVERY arm runs the identical operator on the
                # identical RNG stream, so all six arms enter their own phase from the
                # same population, the same archive and the same candidate count.
                child, reused = op_random(rng, parent)
            elif self.arm in USES_ARCHIVE:
                if distinct >= 2:
                    keys = sorted(self.archive.keys(), key=lambda f: sorted(f))
                    ka, kb = rng.sample(keys, 2)
                    mates = (self.archive[ka][1], self.archive[kb][1])  # expressed forms
                    pa_id, pb_id = self.archive[ka][2], self.archive[kb][2]
                elif self.arm != "D_ENCAPS":
                    self.fallbacks += 1
                    opname = self.arm + "->B_fallback"

            if in_bootstrap:
                pass
            elif self.arm in ("C_COMPOSE", "E_COMP_REF") and mates is None:
                child, reused = op_struct(rng, parent)
            else:
                child, reused = OPERATORS[self.arm](
                    rng, parent, mates=mates, macros=macros)

            expressed, trunc = expand(child, macros)
            if trunc:
                self.truncations += 1
            if not expressed:
                expressed = [(9, OUT_LO, 0)]

            # The cap must NOT apply during the shared bootstrap: bootstrap children are
            # fresh random programs whose radius always exceeds a small cap, so capping
            # there rejects ~85% of the budget and destroys the archive every arm
            # inherits.  Found by inspecting E3b's first run, in which W2's B_STRUCT
            # collapsed 10/12 -> 0/12 for that reason and not for a radius reason.
            if self.radius_cap is not None and not in_bootstrap:
                p_expr, _ = expand(parent, macros)
                r = edit_radius(p_expr, expressed)
                if r > self.radius_cap:
                    self.rejected_by_radius += 1
                    # A rejected child costs no evaluation, so an arm whose natural
                    # radius greatly exceeds the cap can spin.  Bound the spin and
                    # REPORT it: an arm that exhausts this budget is radius-starved,
                    # which is itself the measurement E3 wants.
                    if self.rejected_by_radius > 20 * self.evals:
                        break
                    continue

            p_expr, _ = expand(parent, macros)
            _r = edit_radius(p_expr, expressed)
            self.radii.append(_r)
            if not in_bootstrap:
                self.radii_arm.append(_r)

            exact, frac, tcap = self._evaluate(
                expressed, self.world.boot_slots if in_bootstrap else None)
            viable = exact >= 1
            sig = w.signature(expressed)
            cid = self._record(child, pa_id, pb_id, opname, exact, frac, viable, sig, viable)

            self._maybe_archive(child, expressed, tcap, cid)
            self._check_cross(child, expressed, cid, tcap)

            # Replace-worst-if-NOT-WORSE, with BEHAVIORAL DUPLICATE REJECTION.
            # Accepting ties allows neutral drift; rejecting children whose behavioral
            # signature already sits in the population stops the population collapsing
            # onto one plateau program.  Both were forced by pre-E1 calibration, in which
            # every population-based arm was beaten by pure random sampling because the
            # population converged and mutation became a random walk on a plateau.
            # Arm-neutral: identical rule and identical code path in every arm.
            if (not in_bootstrap) and not self._refit_done:
                fits = [self.world.eval_train(expand(g, macros)[0])[:2] for g in self.pop]
                self._refit_done = True
            worst = min(range(MU), key=lambda j: fits[j])
            if sig in pop_sigs and (exact, frac) <= fits[worst]:
                continue
            if (exact, frac) >= fits[worst]:
                pop_sigs.discard(pop_sigs_by_slot[worst])
                pop_sigs.add(sig)
                pop_sigs_by_slot[worst] = sig
                self.pop[worst] = child
                self.pop_ids[worst] = cid
                fits[worst] = (exact, frac)
                self.genomes[cid] = list(child)
            if (exact, frac) > self.best[:2]:
                self.best = (exact, frac, list(child))

        return self

    def _maybe_archive(self, genome, expressed, key, cid):
        """Archive keyed by TRAIN capability set -- the 'previously viable behaviors'
        store.  Every arm writes to it under this identical rule; only C/D/E read it.

        The EXPRESSED (fully expanded, CALL-free) program is stored alongside the genome.
        Macros are built from the expressed form: storing raw genomes let a CALL token
        leak into a spliced macro body, where run() has no opcode 12 and silently
        executed it as a no-op.  Found in pre-E1 calibration -- arm D scored 0/12."""
        if not key:
            return
        cur = self.archive.get(key)
        if cur is None or len(genome) < len(cur[0]):
            self.archive[key] = (list(genome), list(expressed), cid)
            self.genomes[cid] = list(genome)

    def _check_cross(self, genome, expressed, cid, train_cap=None):
        """HELDOUT acquisition -- the frozen capability test.  Never used for selection.

        Gated on train-viability for speed (a 64-probe check on every candidate is 4x the
        cost of the search itself).  Bounded blind spot, disclosed: a program that matches
        all 64 HELDOUT probes exactly while failing a TRAIN probe would be missed.  For
        exact-identity targets that requires an input-dependent split between two disjoint
        uniform streams; E1 re-checks the final best program of every run without the gate.
        """
        if train_cap is not None and not train_cap:
            return
        cs = self.world.capset(expressed, "heldout")
        if cs:
            phase = "bootstrap" if self.n_evals <= self.bootstrap else "arm"
            self.crossings.append((cid, sorted(cs), self.n_evals, phase))
            self.genomes[cid] = list(genome)
            for k in cs:
                self.first_cross_eval.setdefault(k, self.n_evals)

    # -- reporting --------------------------------------------------------------
    def summary(self):
        held, held_arm, held_boot = set(), set(), set()
        for _, cs, _, phase in self.crossings:
            held |= set(cs)
            (held_arm if phase == "arm" else held_boot).update(cs)
        return dict(
            arm=self.arm, world=self.world.name, seed=self.seed,
            evals=self.n_evals, vm_instructions=self.vm_instructions,
            archive_size=len(self.archive), fallbacks=self.fallbacks,
            truncations=self.truncations, rejected_by_radius=self.rejected_by_radius,
            mean_radius=(sum(self.radii) / len(self.radii)) if self.radii else 0.0,
            mean_radius_arm=(sum(self.radii_arm) / len(self.radii_arm))
            if self.radii_arm else 0.0,
            median_radius_arm=(sorted(self.radii_arm)[len(self.radii_arm) // 2]
                               if self.radii_arm else 0.0),
            n_candidates=self.next_id, n_viable=sum(r[7] for r in self.rows),
            best_exact=self.best[0], best_frac=round(self.best[1], 6),
            heldout_slots=sorted(held), n_crossings=len(self.crossings),
            heldout_slots_arm_phase=sorted(held_arm),
            heldout_slots_bootstrap=sorted(held_boot),
            goal_met_arm_phase=bool(self.world.goal <= held_arm),
            goal_met_at_bootstrap=bool(self.world.goal <= held_boot),
            first_cross_eval={str(k): v for k, v in sorted(self.first_cross_eval.items())},
        )


def lineage(run_obj, cid):
    """Exact ancestral chain of a candidate, from the recorded rows only."""
    by_id = {r[0]: r for r in run_obj.rows}
    seen, stack, out = set(), [cid], []
    while stack:
        i = stack.pop()
        if i < 0 or i in seen:
            continue
        seen.add(i)
        r = by_id.get(i)
        if r is None:
            continue
        out.append(r)
        stack.extend([r[1], r[2]])
    return sorted(out, key=lambda r: r[0])


# --------------------------------------------------------------------------- tests

def _test():
    ok = True

    # 1. the initial population is identical across arms at a fixed seed (fairness rule 1)
    pops = []
    for arm in ARMS:
        r = Run(arm, "W1_PIPELINE", 5)
        pops.append([prog_hash(g) for g in r.pop])
    good = all(p == pops[0] for p in pops)
    ok &= good
    print("  [%s] initial population identical across all six arms at a fixed seed"
          % ("PASS" if good else "FAIL"))

    # 2. every operator returns a legal genome and respects the length cap
    rng = random.Random(1)
    base = rand_prog(rng)
    mates = (rand_prog(rng), rand_prog(rng))
    for name, fn in OPERATORS.items():
        child, _ = fn(rng, base, mates=mates, macros=[rand_prog(rng)])
        expressed, _ = expand(child, [rand_prog(rng)])
        legal = all(0 <= i[0] <= OP_CALL and 0 <= i[1] < N_REG and 0 <= i[2] < N_REG
                    for i in child) and len(expressed) <= L_MAX
        ok &= legal
        print("  [%s] operator %s emits a legal genome within the length cap"
              % ("PASS" if legal else "FAIL", name))

    # 3. no arm except D may emit a CALL into an expressed program
    good = True
    for name, fn in OPERATORS.items():
        if name == "D_ENCAPS":
            continue
        for _ in range(200):
            child, _ = fn(rng, base, mates=mates, macros=[rand_prog(rng)])
            if any(i[0] == OP_CALL for i in child):
                good = False
    ok &= good
    print("  [%s] only arm D emits CALL tokens" % ("PASS" if good else "FAIL"))

    # 4. edit radius is symmetric and zero on identity
    p = rand_prog(rng)
    q = rand_prog(rng)
    good = edit_radius(p, p) == 0 and edit_radius(p, q) == edit_radius(q, p)
    ok &= good
    print("  [%s] edit_radius is zero on identity and symmetric" % ("PASS" if good else "FAIL"))

    # 5. a short run terminates, respects its budget, and replays exactly
    r = Run("E_COMP_REF", "W1_PIPELINE", 3, evals=600).go()
    s = r.summary()
    good = s["evals"] >= 600 and s["n_candidates"] > 0
    ok &= good
    print("  [%s] engine honours the eval budget (evals=%d, candidates=%d)"
          % ("PASS" if good else "FAIL", s["evals"], s["n_candidates"]))

    if r.genomes:
        gid = sorted(r.genomes)[0]
        g = r.genomes[gid]
        e1, _ = expand(g, [])
        good = np.array_equal(run(e1, r.world.heldout), run(e1, r.world.heldout))
        ok &= good
        print("  [%s] recorded genome replays exactly from the ancestry store"
              % ("PASS" if good else "FAIL"))

    print("\n  %s" % ("ALL PASS" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    if ap.parse_args().test:
        raise SystemExit(_test())
    print("arms:", ", ".join(ARMS))
