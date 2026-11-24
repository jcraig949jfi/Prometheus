"""Frozen offline artifact (Library of verified XAG Macros), deterministic miner (A3), and SHAM (A5).

Every macro stored in a Library is content-addressed by SHA-256 and re-verified on load.
No macro can ever receive an artificial gate-count discount (flattening is enforced in circuit.py).
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from comp_sprint.circuit import Gate, Macro, StrashBuilder, XAGCircuit, full_mask
from comp_sprint.npn import npn4_canonical
from comp_sprint.sat_exact import sat_exact_synthesize


@dataclass(frozen=True)
class RewriteRule:
    """Verified exact XAG rewrite rule (lhs -> rhs) proven sound by exhaustive truth table.

    Supports both shrinking rules (`rhs.gate_count() < lhs.gate_count()`) and
    equal-gate algebraic bridge rules (`rhs.gate_count() == lhs.gate_count()`) that expose
    global StrashBuilder deduplication across multi-output DAGs.
    """
    name: str
    n_inputs: int
    lhs_gates: Tuple[Gate, ...]
    lhs_outputs: Tuple[Tuple[int, bool], ...]
    rhs_gates: Tuple[Gate, ...]
    rhs_outputs: Tuple[Tuple[int, bool], ...]
    truth_tables: Tuple[int, ...]
    sha256: str
    origin: str = "unknown"

    @classmethod
    def from_circuits(
        cls,
        name: str,
        lhs: XAGCircuit,
        rhs: XAGCircuit,
        origin: str = "unknown",
    ) -> "RewriteRule":
        cl = lhs.strash_and_prune()
        cr = rhs.strash_and_prune()
        if cl.n_inputs != cr.n_inputs:
            raise ValueError(f"RewriteRule {name!r}: input arity mismatch ({cl.n_inputs} vs {cr.n_inputs})")
        if not (2 <= cl.n_inputs <= 4):
            raise ValueError(f"RewriteRule {name!r}: n_inputs={cl.n_inputs} outside [2, 4]")
        if cl.truth_tables() != cr.truth_tables():
            raise ValueError(f"RewriteRule {name!r}: UNSOUND rewrite (lhs != rhs truth tables)")
        if cr.gate_count() > cl.gate_count():
            raise ValueError(f"RewriteRule {name!r}: rhs ({cr.gate_count()}) > lhs ({cl.gate_count()})")
        if cl.sha256() == cr.sha256():
            raise ValueError(f"RewriteRule {name!r}: trivial identity rule (lhs == rhs)")
        payload = {
            "n_inputs": cl.n_inputs,
            "lhs": cl.sha256(),
            "rhs": cr.sha256(),
        }
        rsha = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
        return cls(
            name=name,
            n_inputs=cl.n_inputs,
            lhs_gates=cl.gates,
            lhs_outputs=cl.outputs,
            rhs_gates=cr.gates,
            rhs_outputs=cr.outputs,
            truth_tables=cr.truth_tables(),
            sha256=rsha,
            origin=origin,
        )

    def rhs_as_macro(self) -> Macro:
        circ = XAGCircuit(n_inputs=self.n_inputs, gates=self.rhs_gates, outputs=self.rhs_outputs)
        return Macro.from_circuit(f"rw_{self.name}", circ, origin=self.origin)


@dataclass(frozen=True)
class SearchStrategy:
    """Typed deterministic offline search strategy configuration `S`."""
    enable_linear_precond: bool = False
    enable_bijective_factor: bool = False
    enable_bridge_rewrites: bool = False
    cut_priority: str = "deep_first"  # "deep_first" | "fanout_aware"
    max_factor_depth: int = 6

    def is_default(self) -> bool:
        return (
            not self.enable_linear_precond
            and not self.enable_bijective_factor
            and not self.enable_bridge_rewrites
            and self.cut_priority == "deep_first"
            and self.max_factor_depth == 6
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "enable_linear_precond": bool(self.enable_linear_precond),
            "enable_bijective_factor": bool(self.enable_bijective_factor),
            "enable_bridge_rewrites": bool(self.enable_bridge_rewrites),
            "cut_priority": str(self.cut_priority),
            "max_factor_depth": int(self.max_factor_depth),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object] | None) -> "SearchStrategy":
        if not data:
            return cls()
        cp = str(data.get("cut_priority", "deep_first"))
        if cp not in ("deep_first", "fanout_aware"):
            cp = "deep_first"
        mfd = max(2, min(8, int(data.get("max_factor_depth", 6))))
        return cls(
            enable_linear_precond=bool(data.get("enable_linear_precond", False)),
            enable_bijective_factor=bool(data.get("enable_bijective_factor", False)),
            enable_bridge_rewrites=bool(data.get("enable_bridge_rewrites", False)),
            cut_priority=cp,
            max_factor_depth=mfd,
        )


@dataclass(frozen=True)
class Artifact:
    arm: str
    generation: int
    macros: Tuple[Macro, ...]
    parent_sha256: str | None = None
    rewrites: Tuple[RewriteRule, ...] = ()
    strategy: SearchStrategy = SearchStrategy()

    def sha256(self) -> str:
        payload: Dict[str, object] = {
            "arm": self.arm,
            "generation": self.generation,
            "parent_sha256": self.parent_sha256,
            "macro_shas": [m.sha256 for m in self.macros],
        }
        # Preserve exact backward-compatible SHA when rewrites & strategy are default
        if self.rewrites or not self.strategy.is_default():
            payload["rewrite_shas"] = [r.sha256 for r in self.rewrites]
            payload["strategy"] = self.strategy.to_dict()
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
        return hashlib.sha256(raw).hexdigest()

    def to_dict(self) -> Dict[str, object]:
        out: Dict[str, object] = {
            "arm": self.arm,
            "generation": self.generation,
            "parent_sha256": self.parent_sha256,
            "artifact_sha256": self.sha256(),
            "macros": [
                {
                    "name": m.name,
                    "n_inputs": m.n_inputs,
                    "gates": [[g.op, g.left, g.left_inv, g.right, g.right_inv] for g in m.gates],
                    "outputs": [[n, inv] for n, inv in m.outputs],
                    "truth_tables_hex": [hex(t) for t in m.truth_tables],
                    "sha256": m.sha256,
                    "origin": m.origin,
                }
                for m in self.macros
            ],
        }
        if self.rewrites or not self.strategy.is_default():
            out["rewrites"] = [
                {
                    "name": r.name,
                    "n_inputs": r.n_inputs,
                    "lhs_gates": [[g.op, g.left, g.left_inv, g.right, g.right_inv] for g in r.lhs_gates],
                    "lhs_outputs": [[n, inv] for n, inv in r.lhs_outputs],
                    "rhs_gates": [[g.op, g.left, g.left_inv, g.right, g.right_inv] for g in r.rhs_gates],
                    "rhs_outputs": [[n, inv] for n, inv in r.rhs_outputs],
                    "truth_tables_hex": [hex(t) for t in r.truth_tables],
                    "sha256": r.sha256,
                    "origin": r.origin,
                }
                for r in self.rewrites
            ]
            out["strategy"] = self.strategy.to_dict()
        return out

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "Artifact":
        """Load and strictly re-verify every macro, rewrite rule (lhs==rhs), strategy, and SHA-256."""
        macros: List[Macro] = []
        for md in data["macros"]:
            gates = tuple(Gate(g[0], int(g[1]), bool(g[2]), int(g[3]), bool(g[4])) for g in md["gates"])
            outs = tuple((int(o[0]), bool(o[1])) for o in md["outputs"])
            circ = XAGCircuit(n_inputs=int(md["n_inputs"]), gates=gates, outputs=outs)
            m = Macro.from_circuit(str(md["name"]), circ, origin=str(md.get("origin", "loaded")))
            if "sha256" in md and md["sha256"] and m.sha256 != md["sha256"]:
                raise ValueError(f"Macro {m.name!r} SHA mismatch on load!")
            if "truth_tables_hex" in md:
                expected = tuple(int(h, 16) for h in md["truth_tables_hex"])
                if m.truth_tables != expected:
                    raise ValueError(f"Macro {m.name!r} truth-table mismatch on load!")
            macros.append(m)

        rewrites: List[RewriteRule] = []
        for rd in data.get("rewrites", ()):
            lg = tuple(Gate(g[0], int(g[1]), bool(g[2]), int(g[3]), bool(g[4])) for g in rd["lhs_gates"])
            lo = tuple((int(o[0]), bool(o[1])) for o in rd["lhs_outputs"])
            rg = tuple(Gate(g[0], int(g[1]), bool(g[2]), int(g[3]), bool(g[4])) for g in rd["rhs_gates"])
            ro = tuple((int(o[0]), bool(o[1])) for o in rd["rhs_outputs"])
            lhs_c = XAGCircuit(n_inputs=int(rd["n_inputs"]), gates=lg, outputs=lo)
            rhs_c = XAGCircuit(n_inputs=int(rd["n_inputs"]), gates=rg, outputs=ro)
            rw = RewriteRule.from_circuits(str(rd["name"]), lhs_c, rhs_c, origin=str(rd.get("origin", "loaded")))
            if "sha256" in rd and rd["sha256"] and rw.sha256 != rd["sha256"]:
                raise ValueError(f"RewriteRule {rw.name!r} SHA mismatch on load!")
            rewrites.append(rw)

        strat = SearchStrategy.from_dict(data.get("strategy"))
        art = cls(
            arm=str(data["arm"]),
            generation=int(data["generation"]),
            macros=tuple(macros),
            parent_sha256=data.get("parent_sha256"),
            rewrites=tuple(rewrites),
            strategy=strat,
        )
        if "artifact_sha256" in data and art.sha256() != data["artifact_sha256"]:
            raise ValueError("Artifact SHA mismatch on load!")
        return art


def _extract_k_cut_macro(
    circ: XAGCircuit,
    root_nodes: Sequence[int],
    max_inputs: int = 4,
    max_gates: int = 6,
) -> Macro | None:
    """Extract the induced sub-DAG feeding `root_nodes` if it has 2..max_inputs leaves and 2..max_gates gates."""
    n_in = circ.n_inputs
    # Collect backward cone from root_nodes stopping when we exceed max_gates
    visited = set()
    queue = [r for r in root_nodes if r >= n_in]
    while queue:
        nid = queue.pop()
        if nid in visited or nid < n_in:
            continue
        visited.add(nid)
        if len(visited) > max_gates:
            return None
        g = circ.gates[nid - n_in]
        if g.left >= n_in:
            queue.append(g.left)
        if g.right >= n_in:
            queue.append(g.right)

    if len(visited) < 2:
        return None

    # Leaves are nodes referenced by gates in `visited` that are NOT themselves in `visited`
    leaves = set()
    for nid in visited:
        g = circ.gates[nid - n_in]
        if g.left >= 0 and g.left not in visited:
            leaves.add(g.left)
        if g.right >= 0 and g.right not in visited:
            leaves.add(g.right)
    if not (2 <= len(leaves) <= max_inputs):
        return None

    ordered_leaves = sorted(leaves)
    ordered_gates = sorted(visited)
    remap: Dict[int, int] = {-1: -1}
    for i, lf in enumerate(ordered_leaves):
        remap[lf] = i
    new_gates: List[Gate] = []
    for idx, old_nid in enumerate(ordered_gates):
        remap[old_nid] = len(ordered_leaves) + idx
        g = circ.gates[old_nid - n_in]
        new_gates.append(Gate(g.op, remap[g.left], g.left_inv, remap[g.right], g.right_inv))

    sub_outs = tuple((remap[r], False) for r in root_nodes if r in remap)
    if not sub_outs:
        return None
    sub_circ = XAGCircuit(n_inputs=len(ordered_leaves), gates=tuple(new_gates), outputs=sub_outs)
    clean = sub_circ.strash_and_prune()
    if clean.gate_count() < 2 or clean.n_inputs < 2:
        return None
    # Filter trivial constant/projection outputs
    mask = full_mask(clean.n_inputs)
    if any(t in (0, mask) for t in clean.truth_tables()):
        return None
    return Macro.from_circuit(f"det_{clean.sha256()[:8]}", clean, origin="zero_llm_miner")


def _compress_macro_exact(
    macro: Macro,
    meter: object | None = None,
    phase: str = "sleep_compress",
) -> Macro:
    """Compress a 2..4-input macro to exact minimum XAG gates via CaDiCaL (charged to meter)."""
    if not (2 <= macro.n_inputs <= 4):
        return macro
    n_outs = len(macro.outputs)
    if n_outs > 2:
        return macro
    cur_g = len(macro.gates)
    # Try strictly smaller circuits first (up to cur_g - 1); if UNSAT, keep original!
    max_try = min(cur_g - 1, 7 if n_outs == 1 else 6)
    if max_try < 1:
        return macro
    opt = sat_exact_synthesize(
        n_inputs=macro.n_inputs,
        targets=macro.truth_tables,
        basis="XAG",
        min_gates=1,
        max_gates=max_try,
        meter=meter,
        phase=phase,
    )
    if opt is not None and opt.gate_count() < cur_g:
        return Macro.from_circuit(f"opt_{opt.sha256()[:8]}", opt, origin=macro.origin)
    return macro


def mine_deterministic_library(
    dev_circuits: Sequence[XAGCircuit],
    max_macros: int = 12,
    generation: int = 1,
    parent_sha256: str | None = None,
    compress_exact: bool = True,
    meter: object | None = None,
    phase: str = "A3_sleep_mine",
) -> Artifact:
    """Arm A3 (ZERO-LLM-LEARN): mine recurring 3..4-input k-cuts across dev circuits
    (grouped by NPN4 class for single-output cuts), and compress top-K via exact SAT."""
    from comp_sprint.synth_base import _embed_to_4bit, _enumerate_cuts, _eval_cut_tt

    npn_score: Counter[int] = Counter()
    pair_counts: Counter[Tuple[int, Tuple[int, int]]] = Counter()
    pair_rep: Dict[Tuple[int, Tuple[int, int]], Macro] = {}

    def cone_size(circ: XAGCircuit, root_nid: int, leaves: Tuple[int, ...]) -> int:
        lset = set(leaves)
        seen = set()
        stack = [root_nid]
        n_in = circ.n_inputs
        while stack:
            u = stack.pop()
            if u in seen or u in lset or u < n_in:
                continue
            seen.add(u)
            g = circ.gates[u - n_in]
            stack.append(g.left)
            stack.append(g.right)
        return len(seen)

    for circ in dev_circuits:
        cuts = _enumerate_cuts(circ, max_k=4, max_cuts_per_node=24)
        n_in = circ.n_inputs
        best_cone_for_npn: Dict[int, int] = {}
        for idx in range(circ.gate_count()):
            nid = n_in + idx
            for leaves in cuts.get(nid, ()):
                if not (3 <= len(leaves) <= 4):
                    continue
                csize = cone_size(circ, nid, leaves)
                # Only mine cuts whose current cone costs >= 4 gates (where real savings live!)
                if csize < 4:
                    continue
                tt4 = _eval_cut_tt(circ, nid, leaves)
                if tt4 is None:
                    continue
                c = npn4_canonical(tt4)
                if c in (0x0000, 0x00FF, 0x000F, 0x0FF0):
                    continue
                if csize > best_cone_for_npn.get(c, 0):
                    best_cone_for_npn[c] = csize
        for c, csize in best_cone_for_npn.items():
            # Weight by bloated cone size so mining targets the highest-leverage abstractions
            npn_score[c] += csize

        # Also mine 2-output shared cones directly from the DAG
        out_nids = [on for on, _ in circ.outputs if on >= n_in]
        seen_pairs = set()
        for a in range(len(out_nids)):
            for b in range(a + 1, len(out_nids)):
                m = _extract_k_cut_macro(circ, [out_nids[a], out_nids[b]], max_inputs=4, max_gates=6)
                if m is not None and len(m.outputs) == 2:
                    pkey = (m.n_inputs, m.truth_tables)
                    if pkey not in seen_pairs:
                        seen_pairs.add(pkey)
                        pair_counts[pkey] += 1
                        if pkey not in pair_rep or len(m.gates) < len(pair_rep[pkey].gates):
                            pair_rep[pkey] = m

    selected: List[Macro] = []
    # Reserve up to 1/4 of slots for recurring multi-output shared cones
    n_pair_slots = max(1, max_macros // 4)
    top_pairs = sorted(
        pair_counts.keys(),
        key=lambda k: (pair_counts[k], len(pair_rep[k].gates), pair_rep[k].sha256),
        reverse=True,
    )
    for pk in top_pairs[:n_pair_slots]:
        m = pair_rep[pk]
        if compress_exact:
            m = _compress_macro_exact(m, meter=meter, phase=phase)
        selected.append(m)

    # Fill remaining slots with highest-leverage NPN4 single-output classes synthesized optimally
    rem_slots = max_macros - len(selected)
    top_npns = sorted(npn_score.keys(), key=lambda c: (npn_score[c], -c), reverse=True)
    for canon_tt in top_npns[:rem_slots]:
        if compress_exact:
            opt = sat_exact_synthesize(
                n_inputs=4, targets=(canon_tt,), basis="XAG",
                min_gates=2, max_gates=7, meter=meter, phase=phase
            )
            if opt is not None:
                selected.append(Macro.from_circuit(f"det_npn_{canon_tt:04x}", opt, origin="zero_llm_miner"))
        else:
            from comp_sprint.synth_base import _davio_synthesize
            c_dav, _ = _davio_synthesize(4, (canon_tt,), [0, 1, 2, 3], use_greedy_var=True)
            selected.append(Macro.from_circuit(f"det_npn_{canon_tt:04x}", c_dav, origin="zero_llm_miner"))

    return Artifact(arm="ZERO-LLM-LEARN", generation=generation, macros=tuple(selected), parent_sha256=parent_sha256)


def build_sham_matched_library(
    reference: Artifact,
    seed: int = 99991,
    compress_exact: bool = True,
    meter: object | None = None,
    phase: str = "A5_sham_build",
) -> Artifact:
    """Arm A5 (SHAM-MATCHED): exact same count, arities, and optimal compression quality as
    `reference`, on random task-irrelevant NPN4 classes / random multi-output functions."""
    from comp_sprint.npn import enumerate_npn4_classes
    from comp_sprint.synth_base import _embed_to_4bit

    rng = random.Random(seed)
    ref_npns = {
        npn4_canonical(_embed_to_4bit(m.truth_tables[0], m.n_inputs))
        for m in reference.macros
        if len(m.outputs) == 1 and m.n_inputs <= 4
    }
    all_npns = sorted(
        c for c in enumerate_npn4_classes().keys()
        if c not in (0x0000, 0x00FF, 0x000F, 0x0FF0) and c not in ref_npns
    )
    rng.shuffle(all_npns)
    npn_iter = iter(all_npns)

    shams: List[Macro] = []
    for idx, rm in enumerate(reference.macros):
        k_in = rm.n_inputs
        n_g = max(2, len(rm.gates))
        n_out = len(rm.outputs)

        if n_out == 1 and k_in <= 4 and compress_exact:
            # Draw an unused random NPN4 class and synthesize it optimally (fair optimal sham!)
            cand_c = next(npn_iter, None)
            if cand_c is not None:
                opt = sat_exact_synthesize(
                    n_inputs=4, targets=(cand_c,), basis="XAG",
                    min_gates=2, max_gates=7, meter=meter, phase=phase
                )
                if opt is not None:
                    shams.append(Macro.from_circuit(f"sham_npn_{cand_c:04x}", opt, origin="sham_matched"))
                    continue

        # Multi-output or fallback random valid XAG subcircuit
        mask = full_mask(k_in)
        chosen = None
        for _ in range(200):
            builder = StrashBuilder(k_in)
            pool: List[Tuple[int, bool]] = [(i, False) for i in range(k_in)]
            for _ in range(n_g):
                op = rng.choice(("AND", "AND", "XOR"))
                (u, ui), (v, vi) = rng.sample(pool, 2)
                nd = builder.add_gate(op, u, ui ^ rng.choice((False, True)), v, vi ^ rng.choice((False, True)))
                pool.append(nd)
            cand_outs = [p for p in pool if p[0] >= k_in]
            if len(cand_outs) < n_out:
                continue
            outs = [(n, inv ^ rng.choice((False, True))) for n, inv in rng.sample(cand_outs, n_out)]
            circ = builder.build(outs, prune_dead=True)
            if circ.gate_count() < 2:
                continue
            tts = circ.truth_tables()
            if any(t in (0, mask) for t in tts):
                continue
            chosen = Macro.from_circuit(f"sham_{idx:02d}_{circ.sha256()[:6]}", circ, origin="sham_matched")
            if compress_exact and n_out <= 2 and k_in <= 4:
                chosen = _compress_macro_exact(chosen, meter=meter, phase=phase)
            break
        if chosen is not None:
            shams.append(chosen)

    return Artifact(arm="SHAM-MATCHED", generation=reference.generation, macros=tuple(shams))


def extract_dev_cofactor_partitions(
    tasks: Sequence[object],
    max_partitions: int = 12,
    meter: object | None = None,
    phase: str = "ac_partition_mine",
) -> List[Dict[str, object]]:
    """Deterministic Ashenhurst-Curtis 3-variable cofactor partition discovery on DEV tasks ONLY.

    100% black-box from dev truth tables alone (never inspects hidden witness circuits).
    For each 3-input subset (i, j, k), checks whether the 8 cofactors collapse to 3..4 distinct
    equivalence classes (lossless 3->2 state compression), canonicalizes the partition modulo
    the 48 input permutations/negations, and synthesizes the minimum-gate 3-in 2-out XAG cell.
    """
    import itertools
    from comp_sprint.synth_base import _davio_synthesize

    part_counts: Counter[Tuple[Tuple[int, ...], ...]] = Counter()
    part_examples: Dict[Tuple[Tuple[int, ...], ...], List[str]] = {}

    for task in tasks:
        n_in = int(task.n_inputs)
        if n_in < 4 or n_in > 6:
            continue
        targets = tuple(task.targets)
        seen_in_task = set()

        for comb in itertools.combinations(range(n_in), 3):
            rem = [v for v in range(n_in) if v not in comb]
            sigs: List[Tuple[int, ...]] = []
            for v3 in range(8):
                res_outs = []
                for t in targets:
                    rt = 0
                    for rr in range(1 << len(rem)):
                        full_r = 0
                        for bit_idx, cv in enumerate(comb):
                            if (v3 >> bit_idx) & 1:
                                full_r |= 1 << cv
                        for bit_idx, rv in enumerate(rem):
                            if (rr >> bit_idx) & 1:
                                full_r |= 1 << rv
                        if (t >> full_r) & 1:
                            rt |= 1 << rr
                    res_outs.append(rt)
                sigs.append(tuple(res_outs))

            classes: Dict[Tuple[int, ...], List[int]] = {}
            for v3, s in enumerate(sigs):
                classes.setdefault(s, []).append(v3)
            if not (3 <= len(classes) <= 4):
                continue

            raw_blocks = tuple(sorted(tuple(sorted(vs)) for vs in classes.values()))
            best_canon = None
            for perm in itertools.permutations(range(3)):
                for neg in range(8):
                    mapped = []
                    for blk in raw_blocks:
                        mblk = []
                        for v3 in blk:
                            nv = 0
                            for j in range(3):
                                b = ((v3 >> perm[j]) & 1) ^ ((neg >> j) & 1)
                                nv |= b << j
                            mblk.append(nv)
                        mapped.append(tuple(sorted(mblk)))
                    cand_p = tuple(sorted(mapped))
                    if best_canon is None or cand_p < best_canon:
                        best_canon = cand_p
            assert best_canon is not None
            # Reject trivial partitions that simply drop an input bit
            is_trivial_drop = False
            for bit in range(3):
                sh = 1 << bit
                if all(all((v ^ sh) in blk for v in blk) for blk in best_canon):
                    is_trivial_drop = True
                    break
            if is_trivial_drop:
                continue
            if best_canon not in seen_in_task:
                seen_in_task.add(best_canon)
                part_counts[best_canon] += 1
                part_examples.setdefault(best_canon, []).append(str(task.task_id))

    ranked = sorted(part_counts.keys(), key=lambda p: (part_counts[p], -len(p)), reverse=True)
    results: List[Dict[str, object]] = []
    pairings_4 = [((0, 1), (0, 2)), ((0, 1), (0, 3)), ((0, 2), (0, 3))]
    pairings_3 = [((0,), (1,)), ((0,), (2,)), ((1,), (2,))]

    for part in ranked[:max_partitions]:
        pairings = pairings_4 if len(part) == 4 else pairings_3
        best_circ = None
        best_tts = None
        for p0, p1 in pairings:
            tt0 = 0
            tt1 = 0
            for ci in p0:
                for v3 in part[ci]:
                    tt0 |= 1 << v3
            for ci in p1:
                for v3 in part[ci]:
                    tt1 |= 1 << v3
            if tt0 in (0, 0xFF) or tt1 in (0, 0xFF) or tt0 == tt1 or (tt0 ^ 0xFF) == tt1:
                continue
            cd, _ = _davio_synthesize(3, (tt0, tt1), [0, 1, 2], use_greedy_var=True)
            cand_c = cd
            opt = sat_exact_synthesize(
                n_inputs=3, targets=(tt0, tt1), basis="XAG",
                min_gates=2, max_gates=min(cd.gate_count() - 1, 5),
                meter=meter, phase=phase,
            )
            if opt is not None and opt.gate_count() < cand_c.gate_count():
                cand_c = opt
            if best_circ is None or cand_c.gate_count() < best_circ.gate_count():
                best_circ = cand_c
                best_tts = (tt0, tt1)
        if best_circ is not None and best_tts is not None:
            m = Macro.from_circuit(f"ac3_{best_circ.sha256()[:8]}", best_circ, origin="ac_partition_miner")
            results.append({
                "count": int(part_counts[part]),
                "tasks": part_examples[part][:5],
                "partition": [list(b) for b in part],
                "macro": m,
                "gates": best_circ.gate_count(),
                "truth_tables_hex": [hex(t) for t in best_tts],
            })
    return results


def prune_artifact_on_val(
    artifact: Artifact,
    dev_val_tasks: Sequence[object],
    budget: int = 8000,
    seed: int = 0,
    meter: object | None = None,
    phase: str = "dev_val_prune",
) -> Tuple[Artifact, int]:
    """Greedy leave-one-out pruning strictly on internal `dev_val_tasks` (ZERO holdout access!).

    Drops any macro whose removal leaves `dev_val` total gates <= current best (strictly
    eliminates dead-weight / dev-train-memorized macros and beam-contention clutter!).
    """
    from comp_sprint.synth_base import synthesize_with_artifact

    if not dev_val_tasks or len(artifact.macros) <= 1:
        val_sum = sum(
            synthesize_with_artifact(t.n_inputs, t.targets, artifact=artifact, budget=budget, seed=seed, meter=meter, phase=phase).gate_count()
            for t in dev_val_tasks
        )
        return artifact, val_sum

    def eval_val(art: Artifact) -> int:
        return sum(
            synthesize_with_artifact(t.n_inputs, t.targets, artifact=art, budget=budget, seed=seed, meter=meter, phase=phase).gate_count()
            for t in dev_val_tasks
        )

    cur = artifact
    best_sum = eval_val(cur)

    # One greedy backward pass from end to front (preserves higher-priority core macros on ties)
    i = len(cur.macros) - 1
    while i >= 0 and len(cur.macros) > 1:
        sub_macros = cur.macros[:i] + cur.macros[i + 1:]
        cand = Artifact(
            arm=cur.arm, generation=cur.generation, macros=sub_macros,
            parent_sha256=cur.parent_sha256, rewrites=cur.rewrites, strategy=cur.strategy,
        )
        sc = eval_val(cand)
        if sc <= best_sum:
            cur = cand
            best_sum = sc
        i -= 1
    return cur, best_sum


def mine_deterministic_artifact(
    dev_train_tasks: Sequence[object],
    dev_train_circuits: Sequence[XAGCircuit],
    dev_val_tasks: Sequence[object] = (),
    max_macros: int = 20,
    max_rewrites: int = 8,
    generation: int = 1,
    parent_sha256: str | None = None,
    meter: object | None = None,
    phase: str = "A3_sleep_mine",
) -> Artifact:
    """Upgraded Arm A3 (ZERO-LLM-LEARN) producing a full verified `(L, T, S)` artifact:
      1. Black-box Ashenhurst-Curtis 3->2 cofactor partition mining on `dev_train_tasks`.
      2. Savings-weighted 3..4-input NPN4 cut mining (`csize >= 3`, scored by exact SAT gain).
      3. Deterministic verified algebraic bridge rewrite rules `T_det`.
      4. Internal `dev_val` utility pruning to drop dead-weight macros.
    """
    from comp_sprint.synth_base import _enumerate_cuts, _eval_cut_tt

    selected_macros: List[Macro] = []
    seen_sigs = set()

    def add_macro(m: Macro) -> bool:
        sig = (m.n_inputs, tuple(sorted(min(t, t ^ full_mask(m.n_inputs)) for t in m.truth_tables)))
        if sig in seen_sigs or len(selected_macros) >= max_macros:
            return False
        seen_sigs.add(sig)
        selected_macros.append(m)
        return True

    # 1. Black-box Ashenhurst-Curtis 3->2 partitions (top 6 recurring cells on dev_train)
    ac_parts = extract_dev_cofactor_partitions(dev_train_tasks, max_partitions=8, meter=meter, phase=phase)
    for item in ac_parts:
        m = item["macro"]
        if len(m.gates) < 2:
            continue
        add_macro(Macro(
            name=m.name, n_inputs=m.n_inputs, gates=m.gates, outputs=m.outputs,
            truth_tables=m.truth_tables, sha256=m.sha256, origin="zero_llm_ac_miner",
        ))
        if len(selected_macros) >= 6:
            break

    # 2. Savings-weighted 3..4-input NPN4 single-output cut mining (csize >= 3!)
    npn_cone_hits: Counter[int] = Counter()
    npn_max_cone: Dict[int, int] = {}

    def cone_size(circ: XAGCircuit, root_nid: int, leaves: Tuple[int, ...]) -> int:
        lset = set(leaves)
        seen = set()
        stack = [root_nid]
        n_in = circ.n_inputs
        while stack:
            u = stack.pop()
            if u in seen or u in lset or u < n_in:
                continue
            seen.add(u)
            g = circ.gates[u - n_in]
            stack.append(g.left)
            stack.append(g.right)
        return len(seen)

    for circ in dev_train_circuits:
        cuts = _enumerate_cuts(circ, max_k=4, max_cuts_per_node=20)
        n_in = circ.n_inputs
        seen_c_in_circ: Dict[int, int] = {}
        for idx in range(circ.gate_count()):
            nid = n_in + idx
            for leaves in cuts.get(nid, ()):
                if not (3 <= len(leaves) <= 4):
                    continue
                csize = cone_size(circ, nid, leaves)
                if csize < 3:
                    continue
                tt4 = _eval_cut_tt(circ, nid, leaves)
                if tt4 is None:
                    continue
                c = npn4_canonical(tt4)
                if c in (0x0000, 0x00FF, 0x000F, 0x0FF0):
                    continue
                if csize > seen_c_in_circ.get(c, 0):
                    seen_c_in_circ[c] = csize
        for c, csize in seen_c_in_circ.items():
            npn_cone_hits[c] += csize
            if csize > npn_max_cone.get(c, 0):
                npn_max_cone[c] = csize

    top_npn_cands = [c for c, _ in npn_cone_hits.most_common(28)]
    scored_npn: List[Tuple[float, int, XAGCircuit]] = []
    for canon_tt in top_npn_cands:
        opt = sat_exact_synthesize(
            n_inputs=4, targets=(canon_tt,), basis="XAG",
            min_gates=2, max_gates=6, meter=meter, phase=phase,
        )
        if opt is None:
            continue
        est_saving = max(0, npn_max_cone[canon_tt] - opt.gate_count())
        score = npn_cone_hits[canon_tt] * (1.0 + 2.0 * est_saving) / max(1, opt.gate_count())
        scored_npn.append((score, -opt.gate_count(), opt))
    scored_npn.sort(key=lambda x: (x[0], x[1]), reverse=True)

    for _sc, _neg_g, opt in scored_npn:
        if len(selected_macros) >= max_macros:
            break
        tt = opt.truth_tables()[0]
        add_macro(Macro.from_circuit(f"det_npn_{tt:04x}", opt, origin="zero_llm_miner"))

    # 3. Deterministic verified algebraic bridge rewrite rules `T_det`
    from comp_sprint.llm_proposer import compile_exprs_to_xag
    raw_det_bridges = [
        ("det_xor_dist_and", 3, ["(x0 & x1) ^ (x0 & x2)"], ["x0 & (x1 ^ x2)"]),
        ("det_or_to_and_xor", 2, ["x0 | x1"], ["(x0 ^ x1) ^ (x0 & x1)"]),
        ("det_and_or_bridge", 3, ["(x0 & x1) | x2"], ["((x0 & x1) & ~x2) ^ x2"]),
        ("det_mux_xor_form", 3, ["(x0 & x1) | (~x0 & x2)"], ["x2 ^ (x0 & (x1 ^ x2))"]),
        ("det_maj_xor_form", 3, ["(x0 & x1) | (x0 & x2) | (x1 & x2)"], ["(x0 & x1) ^ (x2 & (x0 ^ x1))"]),
    ]
    det_rewrites: List[RewriteRule] = []
    for rname, nin, l_e, r_e in raw_det_bridges:
        if len(det_rewrites) >= max_rewrites:
            break
        try:
            lc = compile_exprs_to_xag(nin, l_e)
            rc = compile_exprs_to_xag(nin, r_e)
            if rc.gate_count() <= lc.gate_count() and lc.sha256() != rc.sha256():
                det_rewrites.append(RewriteRule.from_circuits(rname, lc, rc, origin="zero_llm_miner"))
        except Exception:
            continue

    strat = SearchStrategy(
        enable_linear_precond=True,
        enable_bijective_factor=True,
        enable_bridge_rewrites=True,
        cut_priority="deep_first",
        max_factor_depth=6,
    )
    art = Artifact(
        arm="A3_ZERO_LLM",
        generation=generation,
        macros=tuple(selected_macros),
        parent_sha256=parent_sha256,
        rewrites=tuple(det_rewrites),
        strategy=strat,
    )
    if dev_val_tasks:
        art, _ = prune_artifact_on_val(art, dev_val_tasks, budget=12000, seed=0, meter=meter, phase=f"{phase}_prune")
    return art


def build_sham_matched_artifact(
    reference: Artifact,
    seed: int = 99991,
    compress_exact: bool = True,
    meter: object | None = None,
    phase: str = "A5_sham_build",
) -> Artifact:
    """Arm A5 (SHAM-MATCHED) for full `(L, T, S)` artifacts:
      - Keeps `reference.strategy` VERBATIM so `A4 > A5_SHAM` isolates learned `(L, T)`
        abstractions strictly beyond search-strategy heuristics!
      - Replaces `reference.macros` & `reference.rewrites` with size/arity-matched,
        SAT-compressed verified random task-irrelevant macros/rewrites.
    """
    base_sham = build_sham_matched_library(
        reference, seed=seed, compress_exact=compress_exact, meter=meter, phase=phase
    )
    rng = random.Random(seed + 777)
    sham_rewrites: List[RewriteRule] = []
    if reference.rewrites:
        from comp_sprint.npn import enumerate_npn4_classes
        from comp_sprint.synth_base import _davio_synthesize
        all_npns = sorted(
            c for c in enumerate_npn4_classes().keys()
            if c not in (0x0000, 0x00FF, 0x000F, 0x0FF0)
        )
        rng.shuffle(all_npns)
        for cand_c in all_npns:
            if len(sham_rewrites) >= len(reference.rewrites):
                break
            cd, _ = _davio_synthesize(4, (cand_c,), [0, 1, 2, 3], use_greedy_var=False)
            opt = sat_exact_synthesize(
                n_inputs=4, targets=(cand_c,), basis="XAG",
                min_gates=2, max_gates=min(cd.gate_count(), 6), meter=meter, phase=phase,
            )
            if opt is not None and opt.gate_count() <= cd.gate_count() and opt.sha256() != cd.sha256():
                try:
                    sham_rewrites.append(
                        RewriteRule.from_circuits(f"sham_rw_{cand_c:04x}", cd, opt, origin="sham_matched")
                    )
                except ValueError:
                    continue

    return Artifact(
        arm="A5_SHAM",
        generation=reference.generation,
        macros=base_sham.macros,
        parent_sha256=None,
        rewrites=tuple(sham_rewrites),
        strategy=reference.strategy,
    )
