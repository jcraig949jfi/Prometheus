"""C-017-T030 observation loop: engine.run (archaeon/z80atlas/engine.py:159-465) re-implemented for the declared subset, so that
every BIRTH can be observed. run() keeps its population in locals (rso/z80/CONTRACT.md s3); the Ensorain precedent is to observe
from outside against a pinned engine. Every RNG draw is made in the engine's order with the engine's own SplitMix64, vm.execute,
tasks.cases / score_case, engine.mutate / copy_noise / random_tape and World.neighbour: nothing is copied but the bookkeeping.
tests/test_attribution.py Replay checks byte-equality of the final population (cell, tape, generation) and the birth counts.

What the loop adds, per organism: TAGS, one letter per byte naming the last writer of that byte --
  I  inserted at founder creation (transplant / seeded / random fill); FOUNDERS records each founder's source path:
     S supplied (transplant tapes or the seeded replicator, engine.py:176-188) or R drawn by random_tape (engine.py:21)
  P  written by the PARENT'S OWN EXECUTION: in the vm nbr_mask of the parent's res0 (engine.py:317-332) AND the same value and
     mask when the parent is re-executed, same tape and input, over two altered pre-windows (COUNTERFACTUAL below)
  K  environment: an unwritten window byte (kept from the target cell), or a written byte whose value or mask changes with the
     target cell's prior content (the parent read, executed or sealed neighbour memory: engine.py:26-35, decided per byte by
     re-execution instead of by the read / exec counters, which also fire when a parent runs its own fresh copy)
  R  written by the RUNNER (EXTERNAL birth, engine.py:351-367)
  M  changed by copy noise or background mutation (engine.py:139-143, 371-372)
and SITU: at its last observed opportunity, if the organism read or executed neighbour memory, whether it solves all 8 probe cases
with THAT neighbour (assay.label calls it environmental when it does not also solve them with a zeroed one).
Labels the engine stores (provenance, origin, score, mech, spontaneous_replication) are never produced or read here.
"""
from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas import engine as E, tasks as T, vm
from archaeon.z80atlas.grammar import FROZEN

SUBSET = {("world", "topology"): "well_mixed", ("world", "migration"): "none", ("world", "resources"): "unlimited",
          ("world", "env_dynamics"): "fixed", ("world", "reservoir"): False, ("representation", "layout"): "shared",
          ("mutation",): "local_byte"}
PHYS = ("ENDOGENOUS_COPY", "EXTERNAL")
PRESS = ({"competence_gated"}, {"implicit_survival"})


class Unsupported(Exception):
    pass


def unsupported(spec):
    """Reasons this spec is outside the re-implemented subset (empty list = supported)."""
    bad = []
    for path, want in SUBSET.items():
        v = spec
        for p in path:
            v = v.get(p) if isinstance(v, dict) else None
        if v != want:
            bad.append("%s=%r" % (".".join(path), v))
    if spec.get("reproduction") not in PHYS:
        bad.append("reproduction=%r" % spec.get("reproduction"))
    if set(spec.get("pressure", ())) not in PRESS:
        bad.append("pressure=%r" % spec.get("pressure"))
    if spec.get("task", {}).get("name") in (None, "none") or T.TASKS[spec["task"]["name"]]["regime"] != "FORCED_READ":
        bad.append("task=%r" % spec.get("task"))
    return bad


def probe_cases(seed, task="ECHO_forced", n=8):
    """The run's fixed probe cases (own SplitMix64 stream; the engine's RNG is not touched)."""
    return tuple(T.cases(task, ("z80attr", seed), n, 0))


def counterfactual(tape, nbr, case, step_cap, copy_prim):
    """The parent's res0 re-executed over two altered pre-windows (complement; +0x55): what of the window depends on them."""
    return [vm.execute(tape, bytes(alt(b) for b in nbr), case, step_cap, copy_prim, -1.0)
            for alt in (lambda b: b ^ 0xFF, lambda b: (b + 0x55) & 255)]


def endo_tags(res0, child, alts):
    """Writer of each byte of an ENDOGENOUS_COPY child (child = copy_noise(res0 window)); alts = counterfactual(...)."""
    win = res0["nbr_window"]
    return "".join("M" if child[k] != win[k] else
                   "P" if res0["nbr_mask"][k] and all(a["nbr_mask"][k] and a["nbr_window"][k] == win[k] for a in alts) else "K"
                   for k in range(len(win)))


def replay(spec, seed):
    bad = unsupported(spec)
    if bad:
        raise Unsupported("; ".join(bad))
    F = FROZEN
    rng = SplitMix64(seed_from("z80atlas.run", spec["spec_id"], seed))
    G = spec["representation"]["genome"]; copy_prim = spec["representation"]["substrate"] == "vmcopy"
    phys = spec["reproduction"]; press = set(spec["pressure"]); mut = spec["mutation"]; tname = spec["task"]["name"]
    N = spec["population"]["N"]; step_cap = spec["budget"]["step_cap"]; budget = spec["budget"]["vm_steps"]; max_epochs = spec["budget"]["max_epochs"]
    W = E.World(spec, rng); tparams = W.params[0]; probe = probe_cases(seed, tname)
    genomes = [None] * N; age = [0] * N; gen = [0] * N; score = [0.0] * N; tags = [None] * N; situ = [None] * N
    seeded = spec["init"] == "seeded_replicator"; repl = T.pad(T.replicator(copy_prim), G)
    if seeded and spec["init_hybrid"]:
        repl = T.pad(T.task_then_replicate(tname, copy_prim), G)
    transplant = spec.get("transplant"); founders = []                # (tape, S supplied by transplant / seeding | R random_tape)
    for i in range(N):                                                   # engine.py:180-196
        if transplant:
            if i < len(transplant["tapes"]):
                genomes[i] = bytes.fromhex(transplant["tapes"][i])[:G].ljust(G, bytes(1))
            src = "S"
        elif rng.randbelow(100) < F["init_fill_pct"]:
            supplied = seeded and rng.randbelow(100) < F["seed_fraction_pct"]
            genomes[i] = repl if supplied else E.random_tape(rng, G); src = "S" if supplied else "R"
        if genomes[i] is not None:
            age[i] = rng.randbelow(F["max_age"] // 2); tags[i] = "I" * G; founders.append((genomes[i], src))
    births = births_endo = steps_total = epoch = 0

    def place(j, child, p, t):
        nonlocal births
        genomes[j] = child; age[j] = 0; gen[j] = gen[p] + 1; score[j] = 0.0; tags[j] = t; situ[j] = None; births += 1

    while epoch < max_epochs and steps_total < budget:                  # engine.py:242
        occupied = [i for i in range(N) if genomes[i] is not None]
        if not occupied:
            break
        order = list(occupied)
        for a in range(len(order) - 1, 0, -1):
            b_ = rng.randbelow(a + 1); order[a], order[b_] = order[b_], order[a]
        for i in order:                                                  # engine.py:257-338
            if genomes[i] is None:
                continue
            p = 1.0
            if "competence_gated" in press:
                p = F["gate_floor"] + (1 - F["gate_floor"]) * score[i]
            if p < 1.0 and rng.randbelow(1000000) >= p * 1000000:
                age[i] += 1; continue
            j = W.neighbour(i); nbr = genomes[j] if genomes[j] is not None else bytes(G)
            cs = T.cases(tname, (spec["spec_id"], seed, i), F["cases_per_opportunity"], epoch)
            res0 = None; sc = 0.0; touched = False
            for ci, c in enumerate(cs):
                r = vm.execute(genomes[i], nbr, c, step_cap, copy_prim, -1.0)
                if ci == 0:
                    res0 = r
                steps_total += r["steps"]; sc += T.score_case(tname, r["outputs"], c, tparams)
                touched = touched or r["reads_nbr"] > 0 or r["exec_foreign"] > 0
            score[i] = sc / len(cs); age[i] += 1
            # SITU = competence WITH the live neighbour on the 8 probe cases (the bar F0 uses with a zeroed one; assay.label compares
            # the two, the engine's own dependence probe made exact, engine.py:341-348). An untouched neighbour cannot matter.
            situ[i] = touched and all(T.score_case(tname, vm.execute(genomes[i], nbr, c, step_cap, copy_prim, -1.0)["outputs"], c, tparams) >= 1.0
                                      for c in probe)
            if phys == "ENDOGENOUS_COPY" and res0["writes_nbr"] > 0 and sum(res0["nbr_mask"]) / G >= F["copy_min_frac"]:
                child = E.copy_noise(res0["nbr_window"], res0["nbr_mask"], rng, F["copy_noise"])
                alts = counterfactual(genomes[i], nbr, cs[0], step_cap, copy_prim)
                place(j, child, i, endo_tags(res0, child, alts)); births_endo += 1
        if phys == "EXTERNAL":                                           # engine.py:351-367
            occ = [i for i in range(N) if genomes[i] is not None]
            for _ in range(max(1, int(N * F["external_replace_frac"]))):
                if not occ:
                    break
                if "competence_gated" in press:
                    a, b_ = occ[rng.randbelow(len(occ))], occ[rng.randbelow(len(occ))]; p = a if score[a] >= score[b_] else b_
                else:
                    p = occ[rng.randbelow(len(occ))]
                empties = [i for i in range(N) if genomes[i] is None]
                j = empties[rng.randbelow(len(empties))] if empties and rng.randbelow(2) else W.neighbour(p)
                if j == p:
                    continue
                place(j, E.mutate(genomes[p], mut, rng, F["mutation_rate"]), p, "R" * G)
        for i in range(N):                                               # engine.py:369-380
            if genomes[i] is None:
                continue
            if phys == "ENDOGENOUS_COPY" and rng.randbelow(1000000) < F["background_mutation"] * 1000000:
                new = E.mutate(genomes[i], mut, rng, F["mutation_rate"])
                if new != genomes[i]:
                    tags[i] = "".join("M" if a != b else t for a, b, t in zip(new, genomes[i], tags[i])); situ[i] = None
                genomes[i] = new
            dead = age[i] > F["max_age"]
            if rng.randbelow(1000000) < F["death_rate"] * 1000000:
                dead = True
            if dead:
                genomes[i] = None
        epoch += 1
    final = [dict(cell=i, tape=genomes[i], gen=gen[i], tags=tags[i], situ=situ[i]) for i in range(N) if genomes[i] is not None]
    return dict(final=final, founders=founders, births=births, births_endo=births_endo, epochs=epoch)
