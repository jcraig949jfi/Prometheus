"""G-R8 (round 8 BUILD, builder G): the frozen round-8 world set -- stratum L (w13 genome-space neighbours in
bands L1/L2/L3) and stratum B (fresh background seeds) -- plus the measure-then-size screen plan.

Authoritative rule: LAUNCH_R8.md s6 (L-band, ruling R13), s7 (stratum B), s8 (sizing, ruling R11); SWARM_R8 s5.

A world is expand(de_novo(GRAMMAR_VERSION, gen_seed)); it is NOT a parameter vector. Stratum L perturbs w13 in
GENOME space through the public wforge API mutate(parent, op, op_seed), which returns a frozen DESCENDANT whose
mutation history is interpreted at expansion time, so the descendant genome alone reproduces the world. wforge is
a READ-ONLY production seat: this module only imports it.

  L1  exactly one op from SINGLE_AXIS                                       (size-preserving, single-axis)
  L2  two SINGLE_AXIS ops, OR one labelled STRUCTURAL op
  L3  three SINGLE_AXIS ops, OR two ops at least one of which is a labelled STRUCTURAL op

Templates are the ORDERED op tuples each band admits (mutation order matters at expansion). Draw i of a band uses
template i % len(templates) and draws one op_seed per op from that band's PCG64 stream: PCG64(20260924).jumped(k)
for band k (L1 = 0, so L1 is the plain 20260924 stream). Draws only ever APPEND as capacity grows, so a smaller
manifest is an exact prefix of a larger one.

MECHANISM-LEVEL DEDUP (mandatory, R13). Silent mutations are real: PARAM_PERTURB op_seed 4 and BUDGET_MUTATE
op_seeds 2-4 give a new world_id with w13's mechanism; every INTERFACE_MUTATE op_seed gives the same mechanism.
The key is Mechanics.manifest_hash() of the expansion. The walk is base w13, then L1, L2, L3, B: a mechanism
already held by an earlier band stays there; within a band the lowest op_seed tuple (then lowest draw index) is the
representative. Every discarded draw is RECORDED in `duplicates` -- residue, not waste. Nothing else is dropped:
an entry whose chain contains a step that did not change the mechanism stays in its band and carries
`silent_steps`.

SIZING (R11). No stratum N exists here. screen_order() fixes the order before any outcome (L1 first, stratified
by template; then B/L2/L3 interleaved, each permuted by PCG64(20260923)). size_next() admits the next prefix from
MEASURED whole-world costs against the remaining CPU; before any measurement it admits only the bootstrap block
(one L1 world per L1 template -- a quantity of the rule, not a planning constant). Every world it cannot afford
gets a WHY_NOT_RUN record carrying the projection.

Generation and screening are separately gated (ADAPT-6): build_manifest()/freeze_manifest() import no bus, fabric
or screen code and cost seconds.
"""
from __future__ import annotations

import hashlib
import json
import math
import pathlib
import sys
from dataclasses import asdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
_WF = ROOT / "SerendipityFoundry" / "worldfoundry"
if str(_WF) not in sys.path:
    sys.path.insert(0, str(_WF))

from wforge.genome import MutationOp, WorldGenome, de_novo, mutate  # noqa: E402
from wforge.world import expand  # noqa: E402

SCHEMA = "nestor.world_set_r8.v1"
GRAMMAR_VERSION = "wforge-grammar-0.1"
BASE_GEN_SEED = 13
BASE_WORLD_ID = "Wf250db380cb2afd3"

SINGLE_AXIS = ("PARAM_PERTURB", "REWIRE", "PRIMITIVE_INSERT", "PRIMITIVE_DELETE")
STRUCTURAL = ("BUDGET_MUTATE", "INTERFACE_MUTATE")
ALL_OPS = SINGLE_AXIS + STRUCTURAL

OP_SEED_STREAM = 20260924          # LAUNCH_R8 s5.2: L-band mutation op seeds
SCREEN_ORDER_SEED = 20260923       # LAUNCH_R8 s5.2: screen order permutation
STRATUM_B_GEN_SEED0 = 900000       # LAUNCH_R8 s7: gen_seed 900000 + i
CONSUMED_GEN_SEEDS = range(1, 38)  # LAUNCH_R8 s5.1: the R16 grid
OP_SEED_LO, OP_SEED_HI = 1, 1 << 31

BANDS = ("L1", "L2", "L3")
TEMPLATES = {
    "L1": [(a,) for a in SINGLE_AXIS],
    "L2": [(a, b) for a in SINGLE_AXIS for b in SINGLE_AXIS] + [(s,) for s in STRUCTURAL],
    "L3": ([(a, b, c) for a in SINGLE_AXIS for b in SINGLE_AXIS for c in SINGLE_AXIS]
           + [(a, b) for a in ALL_OPS for b in ALL_OPS if a in STRUCTURAL or b in STRUCTURAL]),
}

# MANIFEST capacity: how many draws are generated and frozen per stratum. This sizes the preregistered manifest,
# NOT the screen -- screening is sized by size_next() from measured cost, and every unscreened world carries
# WHY_NOT_RUN. Whole template cycles, so each template is equally represented in the frozen draws.
CAPACITY = {"L1": 16 * len(TEMPLATES["L1"]), "L2": 4 * len(TEMPLATES["L2"]),
            "L3": 1 * len(TEMPLATES["L3"]), "B": 64}

MECH_FIELDS = ("horizon", "n_slots", "act_width", "n_regs", "regime_period", "stoch_rate", "delay", "act_targets",
               "act_cost", "step_cost", "yield_reg", "yield_lo", "yield_hi", "yield_amt", "start_charge",
               "obs_regs", "obs_perm", "corrupt_rate", "obs_delay", "horizon_class")


def rule(capacity: dict | None = None) -> dict:
    """The frozen band rule as data; its sha256 is stamped on the manifest."""
    return {"schema": SCHEMA, "grammar_version": GRAMMAR_VERSION, "base_gen_seed": BASE_GEN_SEED,
            "base_world_id": BASE_WORLD_ID, "single_axis": list(SINGLE_AXIS), "structural": list(STRUCTURAL),
            "templates": {b: [list(t) for t in TEMPLATES[b]] for b in BANDS},
            "op_seed_stream": {"bit_generator": "PCG64", "seed": OP_SEED_STREAM, "band_substream": "jumped(k)",
                               "band_k": {b: k for k, b in enumerate(BANDS)},
                               "draw": f"integers({OP_SEED_LO}, {OP_SEED_HI}) one per op in template order"},
            "stratum_b": {"gen_seed0": STRATUM_B_GEN_SEED0, "draw": "gen_seed0 + i"},
            "dedup": {"key": "wforge.world.Mechanics.manifest_hash()", "walk": ["BASE", *BANDS, "B"],
                      "representative": "earliest band; within band lowest op_seed tuple, then lowest draw_index"},
            "screen_order_seed": SCREEN_ORDER_SEED,
            "capacity": dict(capacity or CAPACITY)}


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def base_genome() -> WorldGenome:
    return de_novo(GRAMMAR_VERSION, BASE_GEN_SEED)


def mechanism(mech) -> dict:
    d = {k: getattr(mech, k) for k in MECH_FIELDS}
    d["lin_ops"] = [list(op) for op in mech.lin_ops]
    d["T"], d["S"], d["W"] = mech.horizon, mech.n_slots, mech.act_width
    d["n"] = d["T"] * d["S"] * d["W"]
    return d


def summary(mech) -> dict:
    """The fields a reader checks first (LAUNCH_R8 s6 base line), from the expansion."""
    return {"T": mech.horizon, "S": mech.n_slots, "W": mech.act_width, "n": mech.horizon * mech.n_slots * mech.act_width,
            "n_regs": mech.n_regs, "lin_ops": len(mech.lin_ops), "corrupt_rate": mech.corrupt_rate,
            "obs_delay": mech.obs_delay, "horizon_class": mech.horizon_class, "act_targets": list(mech.act_targets),
            "yield_reg": mech.yield_reg, "yield_amt": mech.yield_amt, "start_charge": mech.start_charge}


def band_rng(band: str) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(OP_SEED_STREAM).jumped(BANDS.index(band)))


def chain(ops: tuple, op_seeds: tuple) -> list[WorldGenome]:
    """[w13, after op 1, ..., after op k] -- the lineage, built by the public mutate() only."""
    gs = [base_genome()]
    for op, s in zip(ops, op_seeds):
        gs.append(mutate(gs[-1], op, int(s)))
    return gs


def genome_from_payload(p: dict) -> WorldGenome:
    """Rebuild a genome from its canonical payload ALONE (no band, no draw index)."""
    return WorldGenome(grammar_version=p["grammar_version"], generation_seed=p["generation_seed"],
                       parent_ids=tuple(p["parent_ids"]),
                       mutation_history=tuple(MutationOp(**m) for m in p["mutation_history"]))


def _diff(base: dict, m: dict) -> list[str]:
    return sorted(k for k in m if m[k] != base[k])


def _label(ops) -> str:
    st = [o for o in ops if o in STRUCTURAL]
    return f"STRUCTURAL({'+'.join(st)})" if st else "SINGLE_AXIS"


def l_draws(band: str, n: int) -> list[dict]:
    """The first n draws of an L band, before dedup."""
    rng, tpl, out = band_rng(band), TEMPLATES[band], []
    for i in range(n):
        ops = tpl[i % len(tpl)]
        seeds = tuple(int(x) for x in rng.integers(OP_SEED_LO, OP_SEED_HI, size=len(ops)))
        gs = chain(ops, seeds)
        mechs = [expand(g) for g in gs]
        hashes = [m.manifest_hash() for m in mechs]
        base_m, m = mechanism(mechs[0]), mechanism(mechs[-1])
        out.append({"stratum": "L", "band": band, "draw_index": i, "ops": list(ops), "op_seeds": list(seeds),
                    "structural_ops": [o for o in ops if o in STRUCTURAL], "label": _label(ops),
                    "silent_steps": [k + 1 for k in range(len(ops)) if hashes[k + 1] == hashes[k]],
                    "lineage": [g.world_id for g in gs], "world_id": gs[-1].world_id,
                    "genome": gs[-1].payload(), "mech_hash": hashes[-1], "summary": summary(mechs[-1]),
                    "changed_vs_base": _diff(base_m, m), "size_preserving": m["n"] == base_m["n"]})
    return out


def b_draws(n: int) -> list[dict]:
    out = []
    for i in range(n):
        g = de_novo(GRAMMAR_VERSION, STRATUM_B_GEN_SEED0 + i)
        mech = expand(g)
        out.append({"stratum": "B", "band": "B", "draw_index": i, "gen_seed": g.generation_seed, "ops": [],
                    "op_seeds": [], "structural_ops": [], "label": "BACKGROUND", "silent_steps": [],
                    "lineage": [g.world_id], "world_id": g.world_id, "genome": g.payload(),
                    "mech_hash": mech.manifest_hash(), "summary": summary(mech)})
    return out


def dedup(draws_by_band: dict) -> tuple[list[dict], list[dict]]:
    """-> (kept, duplicates). Walk BASE, L1, L2, L3, B; one representative per expanded mechanism."""
    bg = base_genome()
    owner = {expand(bg).manifest_hash(): {"band": "BASE", "world_id": bg.world_id}}
    kept, dups = [], []
    for band in (*BANDS, "B"):
        draws = draws_by_band.get(band, [])
        key = (lambda d: (d["gen_seed"], d["draw_index"])) if band == "B" else (lambda d: (tuple(d["op_seeds"]), d["draw_index"]))
        reps = {}
        for d in sorted(draws, key=key):
            h = d["mech_hash"]
            if h not in owner and h not in reps:
                reps[h] = d
        for d in draws:
            h = d["mech_hash"]
            rep = owner.get(h) or ({"band": band, "world_id": reps[h]["world_id"]} if reps[h] is not d else None)
            if rep is None:
                kept.append(d)
                continue
            dups.append({**d, "duplicate_of": rep["world_id"], "duplicate_of_band": rep["band"],
                         "reason": "SILENT_MUTATION_EQUALS_BASE" if rep["band"] == "BASE" else "MECHANISM_IDENTICAL"})
        for h, d in reps.items():
            owner[h] = {"band": band, "world_id": d["world_id"]}
    return kept, dups


def _file_sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_manifest(capacity: dict | None = None) -> dict:
    """The deterministic manifest body (no timestamps; byte-reproducible)."""
    cap = dict(capacity or CAPACITY)
    draws = {b: l_draws(b, cap[b]) for b in BANDS}
    draws["B"] = b_draws(cap["B"])
    kept, dups = dedup(draws)
    bg = base_genome()
    body = {"schema": SCHEMA, "rule": rule(cap), "rule_sha256": _sha(rule(cap)),
            "wforge_sha256": {f: _file_sha(_WF / "wforge" / f) for f in ("genome.py", "world.py")},
            "base": {"world_id": bg.world_id, "genome": bg.payload(), "mech_hash": expand(bg).manifest_hash(),
                     "summary": summary(expand(bg))},
            "entries": kept, "duplicates": dups,
            "counts": {b: {"drawn": len(draws[b]), "kept": sum(e["band"] == b for e in kept),
                           "duplicates": sum(e["band"] == b for e in dups)} for b in (*BANDS, "B")}}
    body["screen_order"] = screen_order(body)
    return body


def screen_order(body: dict) -> list[str]:
    """Fixed before any outcome. L1 first, permuted within each template and interleaved (any prefix of k*|T| holds k
    per template); then B, L2, L3 each permuted and interleaved round-robin. All permutations from PCG64(20260923)."""
    rng = np.random.Generator(np.random.PCG64(SCREEN_ORDER_SEED))
    ents = body["entries"]

    def perm(xs):
        return [xs[i] for i in rng.permutation(len(xs))] if xs else []

    def interleave(cols):
        out, cols = [], [list(c) for c in cols]
        while any(cols):
            for c in cols:
                if c:
                    out.append(c.pop(0))
        return out

    l1 = interleave([perm([e["world_id"] for e in ents if e["band"] == "L1" and tuple(e["ops"]) == t])
                     for t in TEMPLATES["L1"]])
    rest = interleave([perm([e["world_id"] for e in ents if e["band"] == b]) for b in ("B", "L2", "L3")])
    return l1 + rest


def bootstrap_n() -> int:
    return len(TEMPLATES["L1"])


def size_next(order: list[str], measured_cpu_s: dict, in_flight: list[str], remaining_cpu_s: float) -> dict:
    """MEASURE-THEN-SIZE (R11). measured_cpu_s: world_id -> CPU-s of a COMPLETED screen of that world. Admits the next
    worlds of `order` that the remaining CPU affords at the mean measured cost per world; in-flight worlds are
    reserved at that same mean. With no measurement, admits only the bootstrap block. Every unaffordable world in
    `order` gets WHY_NOT_RUN with the projection. Re-call after each completion: the estimate is re-measured."""
    done = set(measured_cpu_s)
    pending = [w for w in order if w not in done and w not in set(in_flight)]
    if not measured_cpu_s:
        n_boot = max(0, bootstrap_n() - len(in_flight))
        return {"status": "BOOTSTRAP", "estimator": None, "est_cpu_s_per_world": None, "n_measured": 0,
                "remaining_cpu_s": remaining_cpu_s, "admit": pending[:n_boot], "why_not_run": []}
    est = sum(measured_cpu_s.values()) / len(measured_cpu_s)
    free = remaining_cpu_s - est * len(in_flight)
    n = max(0, math.floor(free / est)) if est > 0 else len(pending)
    admit, cut = pending[:n], pending[n:]
    proj = {"estimator": "MEAN_MEASURED_CPU_S_PER_COMPLETED_WORLD", "est_cpu_s_per_world": est,
            "n_measured": len(measured_cpu_s), "remaining_cpu_s": remaining_cpu_s, "in_flight": len(in_flight),
            "free_cpu_s_after_in_flight": free, "affordable_n": n}
    why = [{"record": "WHY_NOT_RUN", "world_id": w, "reason": "PROJECTED_CPU_EXCEEDS_REMAINING",
            "order_position": order.index(w), "projection": {**proj, "cpu_s_needed_through_this_world":
                                                             est * (len(in_flight) + n + k + 1)}}
           for k, w in enumerate(cut)]
    return {"status": "SIZED", **proj, "admit": admit, "why_not_run": why}


def freeze_manifest(path: str | pathlib.Path, capacity: dict | None = None, frozen_at_utc: str = "",
                    git_head: str = "") -> dict:
    """Write the manifest ONCE. Refuses to overwrite: a frozen set is never regenerated in place."""
    path = pathlib.Path(path)
    if path.exists():
        raise FileExistsError(f"MANIFEST_ALREADY_FROZEN: {path}")
    body = build_manifest(capacity)
    doc = {"body": body, "body_sha256": _sha(body), "frozen_at_utc": frozen_at_utc, "git_head": git_head}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, sort_keys=True, indent=1) + "\n", encoding="ascii")
    return doc


def verify_manifest(path: str | pathlib.Path) -> list[str]:
    """-> list of problems (empty = verified). Regenerates from the stamped capacity and rebuilds every genome from
    its payload alone."""
    doc = json.loads(pathlib.Path(path).read_text(encoding="ascii"))
    body, bad = doc["body"], []
    if _sha(body) != doc["body_sha256"]:
        bad.append("BODY_SHA_MISMATCH")
    if json.dumps(build_manifest(body["rule"]["capacity"]), sort_keys=True) != json.dumps(body, sort_keys=True):
        bad.append("REGENERATION_DIFFERS")
    for e in body["entries"] + body["duplicates"]:
        g = genome_from_payload(e["genome"])
        if g.world_id != e["world_id"] or expand(g).manifest_hash() != e["mech_hash"]:
            bad.append(f"GENOME_DOES_NOT_REPRODUCE:{e['world_id']}")
    return bad


if __name__ == "__main__":
    b = build_manifest()
    print(json.dumps({"counts": b["counts"], "rule_sha256": b["rule_sha256"], "n_order": len(b["screen_order"])}))
