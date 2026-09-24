"""One run of one spec: world physics, reproduction physics, pressure coupling, ecology, observatory, anti-cheat.
Pure function of (spec, seed). Writes nothing itself; run_dir handling lives in the scheduler. No thresholds are changed
here after launch: every number is read from the spec or from grammar.FROZEN.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Dict, List, Optional

from proteus.foundry.prng import SplitMix64, seed_from
from archaeon.z80atlas import vm, tasks as T
from archaeon.z80atlas.grammar import FROZEN

ENDO = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION")
ORIGIN_RANDOM, ORIGIN_SEEDED, ORIGIN_TRANSPLANTED = "random", "seeded_replicator", "transplanted_lineage"
PROVENANCE_SCHEMA = "archaeon.z80atlas.provenance.v1"


def random_tape(rng: SplitMix64, G: int) -> bytes:
    """The ONLY source of random-origin founder material. Tests replace it to simulate a lucky draw; nothing else may."""
    return bytes(rng.randbelow(256) for _ in range(G))


def donor_contributes(occupied: bool, res: dict, phys: str) -> bool:
    """Could the PREVIOUS occupant of the target cell have contributed genetic material to the child written there?
    Yes if the parent read or executed neighbour memory, if the window was sealed (a snapshot that can hold the occupant's bytes),
    or if any window byte was left unwritten and kept (every physics except ENDOGENOUS_PARTIAL, which refills unwritten bytes
    from the RNG). A complete write with no neighbour reads and no foreign execution carries none of the occupant's bytes."""
    if not occupied:
        return False
    if res["reads_nbr"] > 0 or res["exec_foreign"] > 0 or res["sealed"]:
        return True
    return phys != "ENDOGENOUS_PARTIAL" and not all(res["nbr_mask"])


def _h(o) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()[:16]


class World:
    def __init__(self, spec: dict, rng: SplitMix64):
        w = spec["world"]; self.spec = spec; self.rng = rng
        self.N = spec["population"]["N"]; self.topology = w["topology"]; self.K = w.get("niches", 1) if self.topology == "niches" else 1
        self.side = int(math.sqrt(self.N)) if self.topology == "grid_vn" else 0
        self.niche = [i * self.K // self.N for i in range(self.N)]
        self.graph = None
        if self.topology == "graph":                                      # GraphWorld-like: fixed sparse random interaction graph, degree ~3
            self.graph = [[] for _ in range(self.N)]
            for i in range(self.N):
                while len(self.graph[i]) < 3:
                    j = rng.randbelow(self.N)
                    if j != i and j not in self.graph[i]:
                        self.graph[i].append(j); self.graph[j].append(i)
        self.resource = [FROZEN["resource_cap"]] * self.N
        # environment: per-niche task + params; env lineage ids (env can mutate / reproduce)
        base = spec["task"]["name"]; self.env_dyn = w.get("env_dynamics", "fixed")
        self.tasks = [base] * self.K; self.params = [{"K": T.TASKS[base].get("K", 0)} for _ in range(self.K)]
        self.env_lineage = list(range(self.K)); self.env_births = 0; self.env_changes = []
        if w.get("reservoir") and self.K > 1:
            self.tasks[0] = "CONST_incremental"; self.params[0] = {"K": 0xB7}   # a persistent easy niche
        self.cur_idx = [0] * self.K

    def neighbour(self, i: int) -> int:
        r = self.rng
        if self.topology == "well_mixed":
            j = r.randbelow(self.N - 1); return j if j < i else j + 1
        if self.topology == "ring_soup":
            return (i + (1 if r.randbelow(2) else -1)) % self.N
        if self.topology == "grid_vn":
            s = self.side; x, y = i % s, i // s; d = r.randbelow(4)
            x, y = ((x + 1) % s, y) if d == 0 else ((x - 1) % s, y) if d == 1 else (x, (y + 1) % s) if d == 2 else (x, (y - 1) % s)
            return (y * s + x) % self.N                                   # torus; ragged last row wraps
        if self.topology == "graph":
            g = self.graph[i]; return g[r.randbelow(len(g))]
        # niches: well mixed inside the niche
        k = self.niche[i]; lo = k * self.N // self.K; hi = (k + 1) * self.N // self.K
        j = lo + r.randbelow(hi - lo - 1); return j if j < i else j + 1

    def step_env(self, epoch: int, niche_mean_score: List[float]) -> Optional[str]:
        """Nonstationary / local shift / env mutation / env co-evolution. Returns a label when something changed."""
        d = self.env_dyn; P = FROZEN["env_period"]
        if d == "fixed" or epoch == 0:
            return None
        changed = None
        if d == "nonstationary" and epoch % P == 0:
            for k in range(self.K):
                self.cur_idx[k] = (self.cur_idx[k] + 1) % len(T.CURRICULUM); self.tasks[k] = T.CURRICULUM[self.cur_idx[k]]
            changed = "nonstationary_switch"
        elif d == "local_shift" and epoch % P == 0:
            k = self.rng.randbelow(self.K); self.cur_idx[k] = (self.cur_idx[k] + 1) % len(T.CURRICULUM); self.tasks[k] = T.CURRICULUM[self.cur_idx[k]]; changed = "local_shift"
        elif d == "env_mutate" and epoch % (P // 2) == 0:
            k = self.rng.randbelow(self.K); self.params[k] = {"K": (self.params[k]["K"] + self.rng.randbelow(17) - 8) & 255}; changed = "env_mutate"
        elif d == "env_coevolve" and epoch % (P // 2) == 0:
            # an environment whose population is competent reproduces (copies its task+params, mutated) into another niche
            for k in range(self.K):
                if niche_mean_score[k] >= FROZEN["env_reproduce_score"] and self.K > 1:
                    j = self.rng.randbelow(self.K)
                    if j != k:
                        self.tasks[j] = self.tasks[k]; self.params[j] = {"K": (self.params[k]["K"] + self.rng.randbelow(5) - 2) & 255}
                        self.env_lineage[j] = self.env_lineage[k]; self.env_births += 1; changed = "env_reproduce"
        if changed:
            self.env_changes.append({"epoch": epoch, "kind": changed, "tasks": list(self.tasks), "params": [p["K"] for p in self.params]})
        return changed


def mutate(tape: bytes, kind: str, rng: SplitMix64, rate: float) -> bytes:
    """Background / external mutation operators (frozen grammar). Genome length is fixed; structural ops shift within it."""
    G = len(tape); b = bytearray(tape); n = 0
    for _ in range(G):
        if rng.randbelow(1000000) < rate * 1000000: n += 1
    if n == 0:
        return tape
    if kind == "structural":
        for _ in range(n):
            op = rng.randbelow(3); L = 1 + rng.randbelow(max(1, G // 4)); a = rng.randbelow(G); c = rng.randbelow(G)
            if op == 0:                                                    # duplicate block a -> c
                blk = bytes(b[a:a + L]); b[c:c + len(blk)] = blk; del b[G:]
            elif op == 1:                                                  # insert byte (shift right, drop last)
                b.insert(a, rng.randbelow(256)); del b[G:]
            else:                                                          # delete byte (shift left, append 0)
                del b[a]; b.append(0)
        return bytes(b)
    operand_pos = set(); opcode_pos = set(); i = 0
    while i < G:                                                           # linear decode: which positions are operands
        op = b[i] & 31; opcode_pos.add(i)
        if op in (1, 13, 14, 15, 16, 17, 19, 27) and i + 1 < G: operand_pos.add(i + 1); i += 2
        else: i += 1
    for _ in range(n):
        pool = None
        if kind == "operand_bias" and operand_pos and rng.randbelow(10) < 7: pool = sorted(operand_pos)
        elif kind == "opcode_bias" and rng.randbelow(10) < 7: pool = sorted(opcode_pos)
        p = pool[rng.randbelow(len(pool))] if pool else rng.randbelow(G)
        b[p] = rng.randbelow(256)
    return bytes(b)


def copy_noise(window: bytes, mask: bytes, rng: SplitMix64, rate: float) -> bytes:
    b = bytearray(window)
    for i, m in enumerate(mask):
        if m and rng.randbelow(1000000) < rate * 1000000: b[i] = rng.randbelow(256)
    return bytes(b)


def fidelity(a: bytes, b: bytes) -> float:
    return sum(1 for x, y in zip(a, b) if x == y) / max(1, len(a))


def _crossed_forced(tname, tape, nbr, tparams, step_cap, copy_prim, layout, G, seed, epoch, i) -> bool:
    """ANSWER_BEFORE_READ tasks: a crossing counts only if the organism also solves fresh FORCED cases (it reads, not guesses)."""
    if T.TASKS[tname]["regime"] != "ANSWER_BEFORE_READ":
        return True
    forced = tname.replace("_abr", "_forced"); cs = T.cases(forced, ("abr_check", seed, i), 4, epoch)
    pc0 = G // 2 if layout == "separated" else 0
    return all(T.score_case(forced, vm.execute(tape, nbr, c, step_cap, copy_prim, pc0=pc0, allow_nbr_write=False)["outputs"], c, tparams) >= 1.0 for c in cs)


def run(spec: dict, seed: int, progress=None) -> dict:
    """Execute a spec. Returns {'signals', 'telemetry', 'events', 'snapshots', 'final_population', 'exploits', ...}."""
    F = FROZEN; rng = SplitMix64(seed_from("z80atlas.run", spec["spec_id"], seed))
    rep = spec["representation"]; G = rep["genome"]; copy_prim = rep["substrate"] == "vmcopy"; layout = rep["layout"]
    phys = spec["reproduction"]; press = set(spec["pressure"]); mut = spec["mutation"]; task_spec = spec["task"]
    N = spec["population"]["N"]; step_cap = spec["budget"]["step_cap"]; budget = spec["budget"]["vm_steps"]; max_epochs = spec["budget"]["max_epochs"]
    W = World(spec, rng)
    genomes: List[Optional[bytes]] = [None] * N; energy = [0.0] * N; age = [0] * N; oid = [0] * N; lin = [0] * N; parent = [0] * N; born = [0] * N; score = [0.0] * N
    next_id = 1
    # ---- genetic provenance (DF-017, 2026-09-23). Every founder is stamped with its ORIGIN CLASS at the moment its tape is
    # created, and each organism carries anc = the set of founders whose genetic material may have reached it. Origin is never
    # inferred from spec["init"]: the 72-hour campaign's transplant constructor labelled inserted tapes init="random", and the old
    # predicate read the label. The sets are conservative (any founder that COULD have contributed bytes is included), so a lineage
    # is called random-only only when no seeded or transplanted material could have entered it. No RNG draw is added or reordered:
    # every historical (spec, seed) replays byte-identically in all pre-existing outputs.
    founders: Dict[int, dict] = {}; inserted_founders: set = set(); anc: List[frozenset] = [frozenset()] * N; gen = [0] * N; cross_prov: Dict[str, dict] = {}; clean_cross: Dict[str, dict] = {}
    # init: random tapes everywhere, or a seeded replicator in a fraction of cells (never counted as spontaneous)
    seeded = spec["init"] == "seeded_replicator"; repl = T.pad(T.replicator(copy_prim), G)
    if task_spec["name"] != "none" and seeded and spec["init_hybrid"]:
        repl = T.pad(T.task_then_replicate(task_spec["name"], copy_prim), G)
    transplant = spec.get("transplant")                                   # late-stage lineage transport: tapes carried in the spec itself
    for i in range(N):
        origin = None
        if transplant:
            tapes = transplant["tapes"]
            if i < len(tapes):
                genomes[i] = bytes.fromhex(tapes[i])[:G].ljust(G, bytes(1)); origin = ORIGIN_TRANSPLANTED
        elif rng.randbelow(100) < F["init_fill_pct"]:
            if seeded and rng.randbelow(100) < F["seed_fraction_pct"]:    # same draws, same order as the campaign's one-line conditional
                genomes[i] = repl; origin = ORIGIN_SEEDED
            else:
                genomes[i] = random_tape(rng, G); origin = ORIGIN_RANDOM
        if genomes[i] is not None:
            energy[i] = F["energy_init"]; oid[i] = next_id; lin[i] = next_id; parent[i] = 0; age[i] = rng.randbelow(F["max_age"] // 2)
            founders[next_id] = {"origin": origin, "cell": i, "tape_sha": hashlib.sha256(genomes[i]).hexdigest()[:16],
                                 "from_run": transplant.get("from_run") if transplant else None}
            if origin != ORIGIN_RANDOM: inserted_founders.add(next_id)
            anc[i] = frozenset((next_id,)); next_id += 1
    telemetry = []; events = []; snapshots = []; exploits = []; archive = set(); qd: Dict[tuple, float] = {}
    steps_total = 0; epoch = 0; births_total = 0; births_endo = 0; fid_sum = 0.0; fid_n = 0; migrations = 0; first_cross = {}; new_arch = 0; archs_seen = set()
    span_first = None; span_last = None; best_ever = 0.0; last_snap_sig = None; coexist_epochs = 0; env_changes = 0; extinct_epoch = None; cap_hits = 0; execs = 0
    prev_env_snapshot_epoch = -1; dependence = 0; dependents = []
    n_cases = F["cases_per_opportunity"]

    def snapshot(reason: str):
        if len(snapshots) >= F["snapshot_cap"]: return
        snapshots.append({"epoch": epoch, "reason": reason, "tasks": list(W.tasks), "params": [p["K"] for p in W.params],
                          "organisms": [{"cell": i, "id": oid[i], "lineage": lin[i], "parent": parent[i], "born": born[i], "niche": W.niche[i], "score": round(score[i], 3), "energy": round(energy[i], 1), "tape": genomes[i].hex(),
                                                        "gen": gen[i], "ins": is_inserted(anc[i])} for i in range(N) if genomes[i] is not None]})

    pv = {"endo_clean": 0, "endo_inserted": 0, "fid_clean": 0.0, "fid_inserted": 0.0, "donor_mixed": 0, "recomb_mixed": 0,
          "first_replication": None, "first_clean_replication": None, "first_inserted_replication": None, "max_gen_clean": 0, "max_gen_inserted": 0,
          "endo_clean_hifi": 0, "first_clean_hifi_replication": None}

    def is_inserted(a: frozenset) -> bool:
        return not a.isdisjoint(inserted_founders)

    def place(j: int, child: bytes, p: int, mech: str, fid: float, mig: bool = False, contrib: frozenset = frozenset()):
        nonlocal next_id, births_total, births_endo, fid_sum, fid_n
        ptape = genomes[p]
        genomes[j] = child; energy[j] = F["energy_init"]; age[j] = 0; oid[j] = next_id; lin[j] = lin[p]; parent[j] = oid[p]; born[j] = epoch; score[j] = 0.0; next_id += 1
        anc[j] = anc[p] | contrib; gen[j] = gen[p] + 1
        births_total += 1; fid_sum += fid; fid_n += 1
        ins = is_inserted(anc[j])
        if mech != "EXTERNAL":
            births_endo += 1
            key = "inserted" if ins else "clean"
            pv["endo_" + key] += 1; pv["fid_" + key] += fid; pv["max_gen_" + key] = max(pv["max_gen_" + key], gen[j])
            rec = None
            slots = ["first_replication", "first_%s_replication" % key]
            if not ins and fid >= F["spont_fid"]:
                pv["endo_clean_hifi"] += 1; slots.append("first_clean_hifi_replication")
            for slot in slots:
                if pv[slot] is None:
                    rec = rec or {"epoch": epoch, "mech": mech, "fid": round(fid, 3), "parent_id": oid[p], "child_id": oid[j], "cell": j, "niche": W.niche[j],
                                  "lineage": lin[j], "generation": gen[j], "founders": sorted(anc[j]),
                                  "origins": sorted({founders[f]["origin"] for f in anc[j]}), "inserted_ancestry": ins,
                                  "parent_tape": ptape.hex(), "child_tape": child.hex(), "task": W.tasks[W.niche[p]]}
                    pv[slot] = rec
        if len(events) < F["event_cap"]:
            events.append({"e": epoch, "k": "birth", "mech": mech, "p": parent[j], "c": oid[j], "cell": j, "fid": round(fid, 3), "mig": mig, "ins": ins})

    snapshot("init")
    while epoch < max_epochs and steps_total < budget:
        occupied = [i for i in range(N) if genomes[i] is not None]
        if not occupied:
            extinct_epoch = epoch; events.append({"e": epoch, "k": "extinction"}); break
        niche_scores = [[] for _ in range(W.K)]
        for i in occupied: niche_scores[W.niche[i]].append(score[i])
        nm = [sum(s) / len(s) if s else 0.0 for s in niche_scores]
        if W.env_dyn != "fixed" and epoch > 0 and (epoch % (F["env_period"] // 2) == 0) and prev_env_snapshot_epoch != epoch:
            snapshot("standing_variation_before_env_step"); prev_env_snapshot_epoch = epoch      # standing variation before environmental change
        ch = W.step_env(epoch, nm)
        if ch: env_changes += 1
        order = list(occupied)
        for a in range(len(order) - 1, 0, -1):
            b_ = rng.randbelow(a + 1); order[a], order[b_] = order[b_], order[a]
        pair_done = set()
        for i in order:
            if genomes[i] is None: continue
            # interaction opportunity
            p = 1.0
            if "competence_gated" in press: p = F["gate_floor"] + (1 - F["gate_floor"]) * score[i]
            if "minimal_criterion" in press and task_spec["name"] != "none" and score[i] < F["minimal_criterion"] and age[i] > 0: p *= F["mc_penalty"]
            if p < 1.0 and rng.randbelow(1000000) >= p * 1000000: age[i] += 1; continue
            tname = W.tasks[W.niche[i]]; tparams = W.params[W.niche[i]]
            j = W.neighbour(i); nbr = genomes[j] if genomes[j] is not None else bytes(G)
            cs = T.cases(tname, (spec["spec_id"], seed, i), n_cases, epoch)
            e_in = energy[i] if "metabolic" in press else -1.0
            outs = []; res0 = None; sc = 0.0; steps_i = 0
            if phys == "PAIR_EXECUTION":
                if i in pair_done or genomes[j] is None: age[i] += 1; continue
                pair_done.add(i); pair_done.add(j)
            for ci, c in enumerate(cs):
                if layout == "separated":                                   # task code in the upper half, reproduction code in the lower half
                    r = vm.execute(genomes[i], nbr, c, step_cap // 2, copy_prim, e_in, pc0=G // 2, allow_nbr_write=False)
                    if ci == 0: res0 = vm.execute(genomes[i], nbr, (), step_cap // 2, copy_prim, e_in, pc0=0); steps_i += res0["steps"]
                else:
                    r = vm.execute(genomes[i], nbr, c, step_cap, copy_prim, e_in)
                    if ci == 0: res0 = r
                steps_i += r["steps"]; sc += T.score_case(tname, r["outputs"], c, tparams); outs.append(tuple(r["outputs"][:4]))
                if not r["halted"] and not r["starved"]: cap_hits += 1
                execs += 1
                if tname == "none": break
            steps_total += steps_i
            sc = sc / len(cs) if tname != "none" else 0.0
            score[i] = sc; age[i] += 1
            if sc > best_ever:
                best_ever = sc; snapshot("new_best_score")
            if sc >= F["cross_score"] and tname not in first_cross and tname != "none" and _crossed_forced(tname, genomes[i], nbr, tparams, step_cap, copy_prim, layout, G, seed, epoch, i):
                first_cross[tname] = {"epoch": epoch, "id": oid[i], "lineage": lin[i], "cell": i}; events.append({"e": epoch, "k": "first_crossing", "task": tname, "id": oid[i]}); snapshot("first_crossing")
                cross_prov[tname] = {"epoch": epoch, "id": oid[i], "generation": gen[i], "inserted_ancestry": is_inserted(anc[i]),
                                     "origins": sorted({founders[f]["origin"] for f in anc[i]}), "is_unmodified_founder_tape": gen[i] == 0 and oid[i] in founders
                                     and hashlib.sha256(genomes[i]).hexdigest()[:16] == founders[oid[i]]["tape_sha"]}
            # provenance-QUALIFIED crossing (operator ruling 1, 2026-09-23): the first crossing by an organism with random-only ancestry,
            # recorded even when an inserted organism crossed first. Observation only: no snapshot, no event, no RNG draw (the forced-case
            # check draws from its own case stream), so every pre-existing output is unchanged.
            if sc >= F["cross_score"] and tname != "none" and tname not in clean_cross and not is_inserted(anc[i]) \
                    and _crossed_forced(tname, genomes[i], nbr, tparams, step_cap, copy_prim, layout, G, seed, epoch, i):
                clean_cross[tname] = {"epoch": epoch, "id": oid[i], "generation": gen[i], "lineage": lin[i], "origins": sorted({founders[f]["origin"] for f in anc[i]}),
                                      "tape": genomes[i].hex()}
            # energy / resources
            if "metabolic" in press: energy[i] = res0["energy"] if res0 else energy[i]
            if "exec_time" in press: energy[i] -= steps_i * F["exec_cost"]
            if "tape_cost" in press: energy[i] -= G * F["tape_cost"]
            intake = F["intake_base"] + (F["intake_gain"] * sc if ("competence_gated" in press or "resource_gated" in press) else F["intake_gain"] * 0.5)
            if "resource_gated" in press or "resource_competition" in press or spec["world"].get("resources") == "limited":
                k = W.niche[i]; cell = i if spec["world"].get("resources") == "limited" else k
                pool_idx = cell % N; take = min(W.resource[pool_idx], intake); W.resource[pool_idx] -= take; intake = take
            energy[i] += intake
            sig = (tuple(outs), vm.arch_signature(res0["hist"]) if res0 else 0)
            if "novelty" in press and sig not in archive: archive.add(sig); energy[i] += F["novelty_bonus"]
            if "qd" in press and res0:
                key = (res0["steps"] // 32, res0["writes_nbr"] // 4)
                if sc > qd.get(key, -1): qd[key] = sc; energy[i] += F["qd_bonus"]
            asig = vm.arch_signature(res0["hist"]) if res0 else 0
            if asig not in archs_seen: archs_seen.add(asig); new_arch += 1
            # ---- reproduction physics (never runner-provided when ENDOGENOUS)
            if phys in ENDO and res0 is not None and res0["writes_nbr"] > 0:
                mask = res0["nbr_mask"]; wrote = sum(mask); frac = wrote / G; ok = False
                if "minimal_criterion" in press and tname != "none" and sc < F["minimal_criterion"]: ok = False
                elif phys == "ENDOGENOUS_COPY": ok = frac >= F["copy_min_frac"]
                elif phys == "ENDOGENOUS_PARTIAL": ok = wrote >= 1
                elif phys == "OVERWRITE": ok = frac >= F["copy_min_frac"]
                elif phys == "CONSTRUCTIVE": ok = frac >= F["copy_min_frac"] and genomes[j] is None
                elif phys == "PAIR_EXECUTION": ok = frac >= F["copy_min_frac"]
                if ok and (genomes[j] is None or phys in ("OVERWRITE", "ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "PAIR_EXECUTION")):
                    win = res0["nbr_window"]
                    if phys == "ENDOGENOUS_PARTIAL":
                        b = bytearray(win)
                        for q in range(G):
                            if not mask[q]: b[q] = rng.randbelow(256)
                        win = bytes(b)
                    child = copy_noise(win, mask, rng, F["copy_noise"])
                    if genomes[j] is not None and phys in ("OVERWRITE", "ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "PAIR_EXECUTION") and len(events) < F["event_cap"]:
                        events.append({"e": epoch, "k": "overwrite", "victim": oid[j], "by": oid[i]})
                    span = sum(res0["executed"]); span_first = span if span_first is None else span_first; span_last = span
                    donor = anc[j] if donor_contributes(genomes[j] is not None, res0, phys) else frozenset()
                    if donor - anc[i]: pv["donor_mixed"] += 1
                    place(j, child, i, phys, fidelity(child, genomes[i]), contrib=donor)
            if res0 is not None and res0["exec_foreign"] > 0 and len(events) < F["event_cap"]:
                events.append({"e": epoch, "k": "exec_foreign", "id": oid[i], "n": res0["exec_foreign"]})
            if res0 is not None and res0["reads_nbr"] > 0 and W.topology != "ring_soup" and sc >= F["cross_score"] and tname != "none":
                # stale-neighbour exploit probe: does the score survive a zeroed neighbour?
                r2 = [T.score_case(tname, vm.execute(genomes[i], bytes(G), c, step_cap, copy_prim)["outputs"], c, tparams) for c in cs]
                if sum(r2) / len(r2) < sc - 0.3:
                    # the organism's competence depends on the live neighbour's bytes (it reads or executes them): an INTERACTION, recorded
                    # and preserved as a specimen, not an evaluator exploit (the neighbour window is world state, not validation state)
                    dependence += 1
                    if len(dependents) < 50: dependents.append({"e": epoch, "id": oid[i], "nbr_id": oid[j] if genomes[j] is not None else 0, "tape": genomes[i].hex(), "nbr_tape": nbr.hex()})
                    if dependence == 1: snapshot("neighbour_dependence")
        # ---- external reproduction (population manager) -- only under EXTERNAL physics
        if phys == "EXTERNAL":
            occ = [i for i in range(N) if genomes[i] is not None]
            nb = max(1, int(N * F["external_replace_frac"]))
            for _ in range(nb):
                if not occ: break
                if "explicit_fitness" in press or "competence_gated" in press:
                    a, b_ = occ[rng.randbelow(len(occ))], occ[rng.randbelow(len(occ))]; p = a if score[a] >= score[b_] else b_
                else:
                    p = occ[rng.randbelow(len(occ))]
                empties = [i for i in range(N) if genomes[i] is None]
                j = empties[rng.randbelow(len(empties))] if empties and rng.randbelow(2) else W.neighbour(p)
                if j == p: continue
                child = mutate(genomes[p], mut, rng, F["mutation_rate"]); partner = frozenset()
                if "recombination" in press and len(occ) > 1:
                    q = occ[rng.randbelow(len(occ))]; x = rng.randbelow(G); child = child[:x] + genomes[q][x:]; partner = anc[q]
                    if partner - anc[p]: pv["recomb_mixed"] += 1
                place(j, child, p, "EXTERNAL", fidelity(child, genomes[p]), contrib=partner)
        # ---- background mutation (endogenous physics evolve through copy noise + this), deaths, migration, resources
        for i in range(N):
            if genomes[i] is None: continue
            if phys in ENDO and rng.randbelow(1000000) < F["background_mutation"] * 1000000:
                genomes[i] = mutate(genomes[i], mut, rng, F["mutation_rate"])
            dead = False
            if "metabolic" in press or "exec_time" in press or "tape_cost" in press or "resource_gated" in press or "resource_competition" in press:
                dead = energy[i] <= 0
            if age[i] > F["max_age"]: dead = True
            if rng.randbelow(1000000) < F["death_rate"] * 1000000: dead = True
            if "explicit_fitness" in press and phys == "EXTERNAL" and rng.randbelow(1000000) < (1 - score[i]) * F["fitness_death"] * 1000000: dead = True
            if dead:
                genomes[i] = None; anc[i] = frozenset()
        mig = spec["world"].get("migration", "none")
        if W.K > 1 and mig != "none":
            for i in range(N):
                if genomes[i] is None: continue
                m = F["migration"][mig] if mig in F["migration"] else 0.0
                if mig == "periodic" and epoch % F["env_period"] != 0: m = 0.0
                if mig == "competence": m = F["migration"]["high"] * score[i]
                if mig == "env_dependent": m = F["migration"]["high"] if nm[W.niche[i]] < F["stress_score"] else 0.0
                if m > 0 and rng.randbelow(1000000) < m * 1000000:
                    k = rng.randbelow(W.K)
                    if k == W.niche[i]: continue
                    lo = k * N // W.K; hi = (k + 1) * N // W.K; j = lo + rng.randbelow(hi - lo)
                    if genomes[j] is None or rng.randbelow(2):
                        genomes[j] = genomes[i]; energy[j] = energy[i]; age[j] = age[i]; oid[j] = oid[i]; lin[j] = lin[i]; parent[j] = parent[i]; born[j] = born[i]; score[j] = score[i]
                        anc[j] = anc[i]; gen[j] = gen[i]; anc[i] = frozenset()      # provenance moves with the organism
                        genomes[i] = None; migrations += 1
                        if len(events) < F["event_cap"]: events.append({"e": epoch, "k": "migration", "id": oid[j], "from": W.niche[i], "to": k})
        for i in range(N): W.resource[i] = min(F["resource_cap"], W.resource[i] + F["resource_regen"])
        # ---- telemetry row + serendipity snapshots
        occ = [i for i in range(N) if genomes[i] is not None]
        lcount: Dict[int, int] = {}
        for i in occ: lcount[lin[i]] = lcount.get(lin[i], 0) + 1
        big = sum(1 for v in lcount.values() if v >= F["coexist_frac"] * len(occ)) if occ else 0
        if big >= 2: coexist_epochs += 1
        row = {"e": epoch, "pop": len(occ), "births": births_total, "endo": births_endo, "fid": round(fid_sum / fid_n, 3) if fid_n else None,
               "smax": round(max((score[i] for i in occ), default=0.0), 3), "smean": round(sum(score[i] for i in occ) / len(occ), 3) if occ else 0.0,
               "lineages": len(lcount), "big": big, "archs": len(archs_seen), "steps": steps_total, "mig": migrations, "span": span_last,
               "pop_clean": sum(1 for i in occ if not is_inserted(anc[i])), "endo_clean": pv["endo_clean"]}
        telemetry.append(row)
        sig = (row["pop"] // max(1, N // 8), row["archs"], round(row["smax"], 1), len(lcount) // 4)
        if last_snap_sig is not None and sig != last_snap_sig and epoch % F["snapshot_min_gap"] == 0:
            snapshot("telemetry_shift")
        last_snap_sig = sig
        if progress and epoch % 50 == 0: progress(epoch, steps_total)
        epoch += 1
    snapshot("final")
    occ = [i for i in range(N) if genomes[i] is not None]
    # ---- damage ruler on the best organism (accessible-neighbour density): fraction of single-byte mutants non-deleterious / beneficial
    ruler = None
    if occ and task_spec["name"] != "none":
        b = max(occ, key=lambda i: score[i]); tname = W.tasks[W.niche[b]]; tparams = W.params[W.niche[b]]; cs = T.cases(tname, ("ruler", seed), 4, 0)
        def sc_of(tape):
            return sum(T.score_case(tname, vm.execute(tape, bytes(G), c, step_cap, copy_prim)["outputs"], c, tparams) for c in cs) / len(cs)
        s0 = sc_of(genomes[b]); nd = 0; ben = 0; M = F["ruler_samples"]
        for _ in range(M):
            t = bytearray(genomes[b]); t[rng.randbelow(G)] = rng.randbelow(256); s1 = sc_of(bytes(t))
            if s1 >= s0 - 1e-9: nd += 1
            if s1 > s0 + 1e-9: ben += 1
        ruler = {"score": round(s0, 3), "non_deleterious": nd / M, "beneficial": ben / M, "id": oid[b]}
        # generalisation: 16 fresh cases (inputs are fresh per epoch by construction, so a deterministic-input exploit is structurally
        # impossible here; the fresh-16 score records how far the best organism's competence extends beyond its 3 training cases)
        cs16 = T.cases(tname, ("fresh16", seed, b), 16, epoch); ruler["fresh16"] = round(sum(T.score_case(tname, vm.execute(genomes[b], bytes(G), c, step_cap, copy_prim)["outputs"], c, tparams) for c in cs16) / 16, 3)
    if phys in ENDO and births_total != births_endo:
        raise AssertionError("INTEGRITY: runner-provided birth under endogenous physics")
    last = telemetry[-1] if telemetry else {"pop": 0, "smax": 0.0, "fid": None}
    pop_clean = sum(1 for i in occ if not is_inserted(anc[i]))
    fid_clean = pv["fid_clean"] / pv["endo_clean"] if pv["endo_clean"] else 0.0; fid_ins = pv["fid_inserted"] / pv["endo_inserted"] if pv["endo_inserted"] else 0.0
    late = telemetry[-max(1, len(telemetry) // 5):]
    signals = {"final_pop_frac": round(last["pop"] / N, 3), "mean_pop_frac": round(sum(r["pop"] for r in telemetry) / max(1, len(telemetry)) / N, 3),
               "births": births_total, "births_endo": births_endo, "replication_rate": round(births_endo / max(1, sum(r["pop"] for r in telemetry)), 4),
               "fidelity_late": round(sum(r["fid"] for r in late if r["fid"] is not None) / max(1, sum(1 for r in late if r["fid"] is not None)), 3) if any(r["fid"] is not None for r in late) else None,
               "task_max_final": round(max((score[i] for i in occ), default=0.0), 3), "best_ever": round(best_ever, 3), "first_crossing": first_cross,
               "moat_crossed": bool(first_cross), "archs": len(archs_seen), "new_arch_events": new_arch, "coexist_epochs": coexist_epochs,
               "lineages_final": len({lin[i] for i in occ}), "max_lineage_age": max((epoch - born[i] for i in occ), default=0), "migrations": migrations,
               "env_births": W.env_births, "env_changes": env_changes, "span_first": span_first, "span_last": span_last,
               "compression": bool(span_first and span_last and span_last <= F["compression_ratio"] * span_first),
               # DEFECTIVE (kept verbatim for replay comparison only): reads the nominal init label, blind to seeded/transplanted ancestry
               "spontaneous_replication_legacy_label": bool(spec["init"] == "random" and phys in ENDO and births_endo >= F["spont_births"] and last["pop"] / N >= F["spont_pop_frac"] and (last["fid"] or 0) >= F["spont_fid"]),
               # REPAIRED: same frozen thresholds, applied only to births and survivors whose genetic ancestry contains no inserted founder
               "spontaneous_replication": bool(phys in ENDO and pv["endo_clean"] >= F["spont_births"] and pop_clean / N >= F["spont_pop_frac"] and fid_clean >= F["spont_fid"]),
               "inserted_lineage_replication": bool(phys in ENDO and pv["endo_inserted"] >= F["spont_births"] and (len(occ) - pop_clean) / N >= F["spont_pop_frac"] and fid_ins >= F["spont_fid"]),
               "provenance": {"schema": PROVENANCE_SCHEMA, "founders": {o: sum(1 for f in founders.values() if f["origin"] == o) for o in (ORIGIN_RANDOM, ORIGIN_SEEDED, ORIGIN_TRANSPLANTED)},
                              "world_has_inserted_material": bool(inserted_founders), "births_endo_clean": pv["endo_clean"], "births_endo_inserted": pv["endo_inserted"],
                              "fid_clean": round(fid_clean, 3), "fid_inserted": round(fid_ins, 3), "final_pop_clean": pop_clean, "final_pop_inserted": len(occ) - pop_clean,
                              "donor_mixed_births": pv["donor_mixed"], "recombination_mixed_births": pv["recomb_mixed"], "max_generation_clean": pv["max_gen_clean"],
                              "max_generation_inserted": pv["max_gen_inserted"], "first_replication": pv["first_replication"],
                              "first_clean_replication": pv["first_clean_replication"], "first_inserted_replication": pv["first_inserted_replication"],
                              "first_crossing": cross_prov, "first_clean_crossing": clean_cross, "births_endo_clean_hifi": pv["endo_clean_hifi"],
                              "first_clean_hifi_replication": pv["first_clean_hifi_replication"]},
               "ruler": ruler, "exploits": len(exploits), "neighbour_dependence": dependence, "cap_hit_frac": round(cap_hits / max(1, execs), 3), "extinct_epoch": extinct_epoch, "epochs": epoch, "vm_steps": steps_total}
    final_population = [{"cell": i, "id": oid[i], "lineage": lin[i], "parent": parent[i], "born": born[i], "niche": W.niche[i], "score": round(score[i], 3), "tape": genomes[i].hex(),
                         "generation": gen[i], "founders": sorted(anc[i]), "inserted_ancestry": is_inserted(anc[i]),
                         "origin_class": "inserted_lineage" if is_inserted(anc[i]) else "random_only"} for i in occ]
    return {"signals": signals, "telemetry": telemetry, "events": events, "snapshots": snapshots, "final_population": final_population, "exploits": exploits, "dependents": dependents, "env_changes": W.env_changes, "seed": seed,
            "founders": founders}
