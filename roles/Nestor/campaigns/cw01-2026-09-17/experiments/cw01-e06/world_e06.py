"""cw01-e06 — representation ecology: two substrates, one blind task, shared world.

The task is REPRESENTATION-BLIND. Scoring reads outputs only; nothing in scoring or
selection branches on the substrate label. Every difference between TREE and TAPE is a
mechanical consequence of the form:

  TREE  compact; subtree-replacement mutation is NON-LOCAL and disruptive; implicit
        intermediates cost nothing; recombines with TREE partners.
  TAPE  longer for the same function; single-instruction mutation is LOCAL and
        incrementally improvable; explicit registers are maintained at cost;
        recombines with TAPE partners.

ONE PRICE LIST applies to whatever structure a substrate actually has. TREE pays
nothing for registers because it has none - mechanical, not a discount. TREE is cheaper
but brittle; TAPE is costlier but hill-climbs. Neither is destined to dominate, which is
what makes this an ecology experiment rather than a benchmark.

SUBSTRATE vs LABEL. The genome carries `substrate` (mechanics) and `label`
(bookkeeping) separately, and recombination compatibility keys on LABEL. In treatment
label == substrate. In control A two labels sit on ONE substrate, so the identical
assortative dynamics run with no representational difference - the noise floor for beta.

CW01-D046: roots are discovered by walking up for a marker, never by counting parents.
"""
from __future__ import annotations

import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    """Minimal walk-up to find lib/, then let repopath do the real work.

    This is the one place a walk-up is hand-written, because lib/repopath.py cannot be
    imported before lib/ is on the path. It looks for the MARKER, not a fixed depth.
    """
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
import repopath as RP          # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
REPO = RP.find_root(HERE)

NEUTRAL_GENES = ("neutral_a", "neutral_b")
CLIP = 1e4


def _c(x):
    return float(max(-CLIP, min(CLIP, x)))


OPS = {
    "add": lambda a, b: _c(a + b),
    "sub": lambda a, b: _c(a - b),
    "mul": lambda a, b: _c(a * b),
    "min": lambda a, b: _c(min(a, b)),
    "max": lambda a, b: _c(max(a, b)),
    "gate": lambda a, b: _c(b if a > 0 else 0.0),
}
OPNAMES = tuple(sorted(OPS))


# ------------------------------------------------------------- latent facts

def _make_graph(r, n_inputs, n_nodes, reuse):
    """A substrate-neutral OPERATION GRAPH: nodes with explicit dependencies.

    CW01-D055 / operator constraint 1. The previous version was a straight-line
    instruction list indexed by position - that is TAPE semantics with a TREE compiler,
    and it handed one substrate the canonical form for free. A dependency graph has no
    privileged linearisation: both substrates receive the same semantic object and each
    pays its OWN mechanical realisation cost. TAPE holds a shared node in a register;
    TREE must DUPLICATE the whole sub-graph beneath it.

    `reuse` targets the fraction of nodes consumed more than once (fan-out > 1), which
    is a property of the ENVIRONMENT, not of any representation.
    """
    nodes, consumers = [], [0] * (n_inputs + 4 * n_nodes)

    def add(op, i, j):
        consumers[i] += 1
        consumers[j] += 1
        nodes.append((op, i, j))

    for k in range(n_nodes):
        avail = n_inputs + k

        def pick():
            # CW01-D056, symptom 1. The previous version drew reuse candidates from
            # range(avail), which is dominated by INPUTS early on, so the entire knob
            # was spent re-picking leaves. Re-using an input shares no computation -
            # TREE duplicates a leaf at cost 1 - which is why measured fan-out stayed
            # pinned near 0.12 for every requested band. Reuse now applies to PRODUCED
            # nodes only, so the knob raises sharing of computation.
            produced = [t for t in range(n_inputs, avail) if consumers[t] >= 1]
            if produced and r.random() < reuse:
                return int(produced[int(r.integers(0, len(produced)))])
            return int(r.integers(0, avail))

        add(OPNAMES[int(r.integers(0, len(OPNAMES)))], pick(), pick())

    # CW01-D056, symptom 2 - same mechanism. `output` was hardcoded to the last node,
    # so nothing guaranteed its cone reached the rest of the graph. Concentrating picks
    # orphaned later nodes into dead sub-structure, which is why tree_expansion_cost
    # FELL (11/9/7/5) as reuse rose and why band 0.75 collapsed to 4 distinct outputs.
    # Fold every unconsumed produced node into one output: no sub-structure can be
    # dead, and shared nodes are genuinely duplicated under TREE expansion.
    def loose():
        return [t for t in range(n_inputs, n_inputs + len(nodes)) if consumers[t] == 0]

    pend = loose()
    while len(pend) > 1:
        add(OPNAMES[int(r.integers(0, len(OPNAMES)))], pend[0], pend[1])
        pend = loose()
    return {"nodes": nodes, "n_inputs": n_inputs, "output": n_inputs + len(nodes) - 1}


def graph_eval(g, x):
    """Memoised evaluation over the dependency graph. Each node computed ONCE.

    Deliberately not a sequential scan and not a tree expansion - neither substrate's
    execution model is privileged by the canonical evaluator.
    """
    memo = {}

    def val(t):
        if t < g["n_inputs"]:
            return x[t]
        if t in memo:
            return memo[t]
        op, i, j = g["nodes"][t - g["n_inputs"]]
        memo[t] = OPS[op](val(i), val(j))
        return memo[t]

    return val(g["output"])


def graph_fanout_reuse(g):
    """MEASURED reuse: fraction of produced nodes consumed more than once."""
    cons = {}
    for _op, i, j in g["nodes"]:
        for t in (i, j):
            cons[t] = cons.get(t, 0) + 1
    produced = range(g["n_inputs"], g["n_inputs"] + len(g["nodes"]))
    multi = sum(1 for t in produced if cons.get(t, 0) > 1)
    return multi / max(1, len(g["nodes"]))


def tree_expansion_cost(g):
    """Nodes a TREE needs: shared sub-graphs must be DUPLICATED. TAPE pays len(nodes).

    This is the mechanical quantity that should drive comparative advantage, and it is
    reported so the advantage can be checked rather than assumed (the assumption that
    TREE was 'compact' was false - CW01-D055)."""
    memo = {}

    def cost(t):
        if t < g["n_inputs"]:
            return 1
        if t in memo:
            return memo[t]
        _op, i, j = g["nodes"][t - g["n_inputs"]]
        memo[t] = 1 + cost(i) + cost(j)
        return memo[t]

    return cost(g["output"])


def legacy_tree_target(cfg, mkseed):
    """THE PRE-FIX WORLD, retained deliberately as an adversarial FIXTURE.

    This is the depth-3 expression tree generator whose substrate leak caused CW01-D054.
    It is kept so the Q16 mutual-invasibility gate can be shown REFUSING it. A gate that
    has only ever admitted the world it was written alongside is not evidence; the
    broken world is the positive control for the gate's ability to refuse.
    """
    r = np.random.Generator(np.random.PCG64(mkseed(cfg["attempt_id"], "target", 0)))
    n = cfg["task"]["n_inputs"]

    def grow(d):
        if d == 0 or r.random() < 0.25:
            return ("in", int(r.integers(0, n)))
        return (OPNAMES[int(r.integers(0, len(OPNAMES)))], grow(d - 1), grow(d - 1))

    return grow(3)


def target_eval(t, x):
    """Evaluate either canonical form: operation graph, or the legacy tree fixture."""
    return graph_eval(t, x) if isinstance(t, dict) and "nodes" in t else tree_eval(t, x)


def attempt_target(cfg, mkseed):
    """The hidden functions. Drawn ONCE per attempt_id (CW01-D029/D037).

    CW01-D054, and the error was mine. The first version generated the target as a
    depth-3 EXPRESSION TREE - that is, in ONE substrate's native form. Scoring was
    representation-blind, but the WORLD was not: a tree target is trivially expressible
    by TREE and awkward for TAPE. That manufactured a +0.2365 intrinsic gap and left
    TREE's WORST per-capita fitness (0.345) above TAPE's BEST (0.289) at every
    frequency - the curves never crossed, so there was no mutual invasibility and
    coexistence was impossible rather than merely unlikely. Requirement 1 was satisfied
    literally, in the reward function, and violated in the target GENERATOR.

    Targets are now straight-line DAGs spanning a REUSE spectrum. Low reuse is a tree,
    which TREE expresses compactly. High reuse references intermediates repeatedly,
    which TAPE holds in registers and TREE must DUPLICATE. Neither substrate is native
    to the family as a whole, and the spectrum supplies the two-sided comparative
    advantage that mutual invasibility requires.

    Returns a LIST of targets; the call interface is otherwise unchanged.
    """
    t = cfg["task"]
    r = np.random.Generator(np.random.PCG64(mkseed(cfg["attempt_id"], "target", 0)))
    lo, hi = t["input_domain"]
    out = []
    for band in t["reuse_bands"]:
        g, ys = None, set()
        for _try in range(int(t.get("max_generator_tries", 40))):
            g = _make_graph(r, t["n_inputs"], int(t["n_nodes"]), float(band))
            # NON-DEGENERACY. The previous generator emitted a CONSTANT target at
            # reuse=0.50 (1 distinct output over 400 draws), which makes solve-rates
            # meaningless. A target must actually vary over its own input domain.
            ys = set()
            for _ in range(int(t.get("degeneracy_probe", 64))):
                x = [float(v) for v in r.integers(lo, hi + 1, size=t["n_inputs"])]
                ys.add(round(graph_eval(g, x), 6))
            if len(ys) >= int(t.get("min_distinct_outputs", 8)):
                break
        out.append({"reuse_target": float(band),
                    "reuse_measured": graph_fanout_reuse(g),
                    "tree_cost": tree_expansion_cost(g),      # TREE must duplicate shared sub-graphs
                    "tape_cost": len(g["nodes"]),             # TAPE holds them in registers
                    "distinct_outputs": len(ys),
                    "degenerate": len(ys) < int(t.get("min_distinct_outputs", 8)),
                    "graph": g})
    return out


def make_items(cfg, rng, target):
    """PER EPISODE: inputs drawn fresh; the target STRUCTURE is attempt-stable.

    Each item is drawn from one of the reuse bands, so a single episode spans the whole
    comparative-advantage axis rather than one substrate's home ground.
    """
    t = cfg["task"]
    lo, hi = t["input_domain"]
    targets = target if isinstance(target, list) else [target]
    out = []
    for _ in range(t["items_per_episode"]):
        tt = targets[int(rng.integers(0, len(targets)))]
        x = [float(v) for v in rng.integers(lo, hi + 1, size=t["n_inputs"])]
        core = tt["graph"] if (isinstance(tt, dict) and "graph" in tt) else tt
        out.append((x, target_eval(core, x)))
    return out


def items_for_band(cfg, rng, band_target, n=None):
    """Items drawn from ONE reuse band, for measuring Delta(r) = F_TREE - F_TAPE.

    Operator constraint 2: the precondition is not that a TREE-friendly world and a
    TAPE-friendly world both exist somewhere, but that ONE substrate-neutral generator
    yields regions where Delta(r) > 0 and regions where Delta(r) < 0.
    """
    t = cfg["task"]
    lo, hi = t["input_domain"]
    core = band_target["graph"] if "graph" in band_target else band_target
    n = int(n or t["items_per_episode"])
    items = []
    for _ in range(n):
        x = [float(v) for v in rng.integers(lo, hi + 1, size=t["n_inputs"])]
        items.append((x, target_eval(core, x)))
    return items


def invasion_analysis(cfg, mkseed, aid, gens_resident=40, gens_invade=20,
                      n_org=96, invader_frac=0.10, target=None):
    """Q16 PRECONDITION, done properly: invade an EVOLVED RESIDENT at equilibrium.

    CW01-D055. The generation-zero version of this test (below, retained for contrast)
    was MIS-AIMED. It measured standing fitness in a RANDOM population, but TREE's only
    plausible advantage is dynamic - subtree crossover transplants an intact functional
    unit where one-point tape crossover disrupts register plumbing - and a dynamic
    advantage cannot appear before any evolution has happened. A gen-0 test would report
    'not invasible' even in a world where coexistence genuinely emerges.

    The ecological criterion is mutual invasibility of a RESIDENT AT EQUILIBRIUM: evolve
    each substrate alone, then introduce the other rare and measure whether it grows.
    Both directions must succeed for coexistence to be reachable.
    """
    # `target` is INJECTABLE so this gate can be aimed at the legacy tree fixture and
    # shown REFUSING the pre-fix world. A gate that has only ever admitted the world it
    # was written alongside is not evidence (CW01-D055, operator action 3). Note the
    # local is named `tgt`: the previous body reassigned `target` inside the loop and
    # would have silently clobbered an injected one.
    tgt = target if target is not None else attempt_target(cfg, mkseed)
    out = {}
    for resident, invader in (("TREE", "TAPE"), ("TAPE", "TREE")):
        res_arm = "solo_tree" if resident == "TREE" else "solo_tape"
        inv_arm = "solo_tree" if invader == "TREE" else "solo_tape"
        res = evolve(cfg, res_arm, gens_resident, n_org, mkseed, aid,
                     freq_first=1.0, target=tgt)
        inv = evolve(cfg, inv_arm, gens_resident, n_org, mkseed, aid + "|inv",
                     freq_first=1.0, target=tgt)

        k = max(1, int(round(invader_frac * n_org)))
        r = np.random.Generator(np.random.PCG64(mkseed(aid, "invade|%s" % invader, 0)))
        pop = [dict(g, label=resident) for g in res["final_pop"][:n_org - k]]
        pop += [dict(g, label=invader) for g in inv["final_pop"][:k]]

        f0 = k / float(n_org)
        traj = [f0]
        cross_ok = bool(cfg["arms"]["mixed_assortative"].get("cross_substrate_recombination", False))
        for gen in range(gens_invade):
            srng = np.random.Generator(np.random.PCG64(mkseed(aid, "invstream|%s|%d" % (invader, gen), 0)))
            items = make_items(cfg, srng, target)
            pop, _ev, _a, _s = generation(pop, cfg, items, cross_ok, r,
                                          cfg["ecology"]["elite_fraction"])
            traj.append(sum(1 for g in pop if g["label"] == invader) / float(len(pop)))
        grew = traj[-1] > f0
        out["%s_into_%s" % (invader, resident)] = {
            "seeded": f0, "final": traj[-1], "trajectory": traj, "invaded": bool(grew)}

    a = out["TAPE_into_TREE"]["invaded"]
    b = out["TREE_into_TAPE"]["invaded"]
    return {"directions": out, "mutually_invasible": bool(a and b),
            "verdict": ("MUTUALLY INVASIBLE against evolved residents - coexistence reachable"
                        if (a and b) else
                        "NOT mutually invasible (%s into TREE: %s, %s into TAPE: %s)"
                        % ("TAPE", a, "TREE", b))}


def mutual_invasibility(cfg, mkseed, aid, arm="mixed_assortative", n_org=96, reps=6):
    """GENERATION-ZERO standing fitness. RETAINED FOR CONTRAST ONLY - see D055.

    This was promoted as the Q16 precondition in D054 and is MIS-AIMED: it measures a
    random population, so it can only ever see STATIC advantage. Use invasion_analysis
    for the actual precondition. Kept because the contrast between the two is itself
    evidence about whether a substrate's advantage is static or dynamic.
    """
    target = attempt_target(cfg, mkseed)
    labs = _labels(cfg, arm)
    curve = {lab: {} for lab in labs}
    for f0 in (0.10, 0.90):
        for rep in range(reps):
            r = np.random.Generator(np.random.PCG64(mkseed(aid, "mi|%0.2f" % f0, rep)))
            pop = initial_population(cfg, arm, r, n_org, f0)
            srng = np.random.Generator(np.random.PCG64(mkseed(aid, "mi_items", rep)))
            ev = evaluate_population(pop, cfg, make_items(cfg, srng, target))
            for lab in labs:
                v = [e["fitness"] for g, e in zip(pop, ev) if g["label"] == lab]
                if v:
                    curve[lab].setdefault(f0, []).append(float(np.mean(v)))
    m = {lab: {f: float(np.mean(v)) for f, v in d.items()} for lab, d in curve.items()}
    a, b = labs[0], labs[1] if len(labs) > 1 else labs[0]
    a_rare = m[a].get(0.10, float("nan")) > m[b].get(0.10, float("nan"))
    b_rare = m[b].get(0.90, float("nan")) > m[a].get(0.90, float("nan"))
    return {"curves": m, "a": a, "b": b,
            "a_invades_when_rare": bool(a_rare), "b_invades_when_rare": bool(b_rare),
            "mutually_invasible": bool(a_rare and b_rare),
            "verdict": ("MUTUALLY INVASIBLE - coexistence is reachable" if (a_rare and b_rare)
                        else "NOT mutually invasible - coexistence is IMPOSSIBLE, not merely unlikely")}


# ---------------------------------------------------------------- substrates

def tree_eval(node, x):
    if node[0] == "in":
        return x[node[1]]
    return OPS[node[0]](tree_eval(node[1], x), tree_eval(node[2], x))


def tree_nodes(node):
    return 1 if node[0] == "in" else 1 + tree_nodes(node[1]) + tree_nodes(node[2])


def random_tree(r, n_inputs, depth):
    if depth == 0 or r.random() < 0.3:
        return ("in", int(r.integers(0, n_inputs)))
    return (OPNAMES[int(r.integers(0, len(OPNAMES)))],
            random_tree(r, n_inputs, depth - 1), random_tree(r, n_inputs, depth - 1))


def tape_eval(prog, x, n_reg):
    reg = [0.0] * n_reg
    for i in range(min(len(x), n_reg)):
        reg[i] = x[i]
    for op, dst, s1, s2 in prog:
        reg[dst] = OPS[op](reg[s1], reg[s2])
    return reg[0]


def random_tape(r, cfg):
    s = cfg["substrates"]["TAPE"]
    n = int(r.integers(4, s["max_instructions"] + 1))
    return [(OPNAMES[int(r.integers(0, len(OPNAMES)))],
             int(r.integers(0, s["n_registers"])),
             int(r.integers(0, s["n_registers"])),
             int(r.integers(0, s["n_registers"]))) for _ in range(n)]


def live_registers(prog):
    return len({d for _, d, _, _ in prog})


# ------------------------------------------------------------------- genome

def seed_genome(cfg, r, substrate, label):
    body = (random_tree(r, cfg["task"]["n_inputs"], 3) if substrate == "TREE"
            else random_tape(r, cfg))
    return {"substrate": substrate, "label": label, "body": body,
            "neutral_a": float(r.uniform(0, 1)), "neutral_b": float(r.uniform(0, 1)),
            "lineage": int(r.integers(0, 1 << 30))}


def structural_units(g):
    return tree_nodes(g["body"]) if g["substrate"] == "TREE" else len(g["body"])


def registers_used(g):
    return 0 if g["substrate"] == "TREE" else live_registers(g["body"])


def evaluate(g, cfg, items):
    """Score from OUTPUTS ONLY. Nothing here reads g['substrate'] or g['label']."""
    err = 0.0
    for x, y in items:
        out = (tree_eval(g["body"], x) if g["substrate"] == "TREE"
               else tape_eval(g["body"], x, cfg["substrates"]["TAPE"]["n_registers"]))
        err += abs(out - y)
    mae = err / max(1, len(items))
    score = 1.0 / (1.0 + mae)
    p = cfg["prices"]
    cost = (structural_units(g) * p["per_structural_unit"]
            + registers_used(g) * p["per_live_register"]
            + len(items) * p["per_item_attempted"])
    return {"score": score, "mean_abs_error": mae, "cost": cost,
            "fitness": score - cost, "structural_units": structural_units(g),
            "live_registers": registers_used(g), "items_attempted": len(items)}


# --------------------------------------------------------------- variation

def mutate(g, cfg, r):
    """TREE: subtree replacement (non-local). TAPE: one instruction field (local)."""
    h = dict(g)
    if g["substrate"] == "TREE":
        nodes = tree_nodes(g["body"])
        k = int(r.integers(0, nodes))

        def rep(node, i):
            if i[0] == k:
                i[0] += 1
                return random_tree(r, cfg["task"]["n_inputs"], 2)
            i[0] += 1
            if node[0] == "in":
                return node
            return (node[0], rep(node[1], i), rep(node[2], i))

        body = rep(g["body"], [0])
        if tree_nodes(body) > cfg["substrates"]["TREE"]["max_nodes"]:
            body = g["body"]
        h["body"] = body
    else:
        prog = list(g["body"])
        if prog:
            i = int(r.integers(0, len(prog)))
            op, dst, s1, s2 = prog[i]
            nreg = cfg["substrates"]["TAPE"]["n_registers"]
            f = int(r.integers(0, 4))
            if f == 0:
                op = OPNAMES[int(r.integers(0, len(OPNAMES)))]
            elif f == 1:
                dst = int(r.integers(0, nreg))
            elif f == 2:
                s1 = int(r.integers(0, nreg))
            else:
                s2 = int(r.integers(0, nreg))
            prog[i] = (op, dst, s1, s2)
        h["body"] = prog
    h["neutral_a"] = float(np.clip(g["neutral_a"] + r.normal(0, 0.05), 0, 1))
    h["neutral_b"] = float(np.clip(g["neutral_b"] + r.normal(0, 0.05), 0, 1))
    return h


def compatible(a, b, cross_ok):
    """Assortative by LABEL. Neutralisation waives it while labels remain."""
    return True if cross_ok else (a["label"] == b["label"])


def recombine(a, b, cfg, r):
    h = dict(a)
    if a["substrate"] == "TREE" and b["substrate"] == "TREE":
        nodes = tree_nodes(b["body"])
        k = int(r.integers(0, nodes))

        def pick(node, i):
            if i[0] == k:
                i[0] += 1
                return node
            i[0] += 1
            if node[0] == "in":
                return None
            return pick(node[1], i) or pick(node[2], i)

        donor = pick(b["body"], [0]) or b["body"]
        na = tree_nodes(a["body"])
        j = int(r.integers(0, na))

        def put(node, i):
            if i[0] == j:
                i[0] += 1
                return donor
            i[0] += 1
            if node[0] == "in":
                return node
            return (node[0], put(node[1], i), put(node[2], i))

        body = put(a["body"], [0])
        h["body"] = body if tree_nodes(body) <= cfg["substrates"]["TREE"]["max_nodes"] else a["body"]
    elif a["substrate"] == "TAPE" and b["substrate"] == "TAPE":
        pa, pb = list(a["body"]), list(b["body"])
        if pa and pb:
            ca = int(r.integers(1, len(pa) + 1))
            cb = int(r.integers(0, len(pb)))
            body = pa[:ca] + pb[cb:]
            h["body"] = body[:cfg["substrates"]["TAPE"]["max_instructions"]] or pa
    else:
        return None                      # no cross-substrate body operation exists
    return h


# ----------------------------------------------------------------- ecology

def arm_roles(cfg, arm):
    """(substrate, label) pairs. Control A puts TWO LABELS on ONE substrate."""
    subs = cfg["arms"][arm]["substrates"]
    if len(subs) == 1:
        return [(subs[0], subs[0])]
    if subs[0] == subs[1]:
        return [(subs[0], "L0"), (subs[1], "L1")]
    return [(s, s) for s in subs]


def initial_population(cfg, arm, r, n_org, freq_first):
    roles = arm_roles(cfg, arm)
    if len(roles) == 1:
        return [seed_genome(cfg, r, roles[0][0], roles[0][1]) for _ in range(n_org)]
    k = int(round(freq_first * n_org))
    pop = [seed_genome(cfg, r, roles[0][0], roles[0][1]) for _ in range(k)]
    pop += [seed_genome(cfg, r, roles[1][0], roles[1][1]) for _ in range(n_org - k)]
    return pop


def _labels(cfg, arm):
    return [lab for _, lab in arm_roles(cfg, arm)]


def solved_mask(g, cfg, items, tol):
    """Which items this organism solves, and its error. Keys on OUTPUTS ONLY."""
    n_reg = cfg["substrates"]["TAPE"]["n_registers"]
    mask, err = [], 0.0
    for x, y in items:
        v = (tree_eval(g["body"], x) if g["substrate"] == "TREE"
             else tape_eval(g["body"], x, n_reg))
        err += abs(v - y)
        mask.append(abs(v - y) <= tol)
    return mask, err / max(1, len(items))


def evaluate_population(pop, cfg, items):
    """Population-level scoring with RESOURCE SHARING.

    CW01-D052: with per-organism scoring this world was a fixation lottery - 18/18 runs
    fixed, 0/18 coexistence, and CONTROL A (two labels, ONE substrate, no
    representational difference) fixed 6/6. Fixation therefore carried no information
    about representation at all.

    The analytic cause: assortative recombination is a POSITIVE frequency-dependence
    mechanism. Rare means fewer compatible partners means worse means rarer. Alone it
    can only accelerate fixation and can never produce coexistence, so requirement 4
    (all five outcomes reachable) was unsatisfiable by construction.

    Each item is now a RESOURCE, and organisms that solve it SPLIT its value. This is
    representation-blind - it keys on WHICH ITEMS ARE SOLVED, never on who solved them -
    and it supplies the missing NEGATIVE frequency-dependence channel: a common strategy
    dilutes its own reward, so rare types gain. Coexistence becomes REACHABLE without
    being imposed, and fixation stays reachable if one substrate is simply better.
    """
    sh = cfg["sharing"]
    tol = sh["tolerance"]
    pairs = [solved_mask(g, cfg, items, tol) for g in pop]
    counts = [0] * len(items)
    for m, _ in pairs:
        for j, s in enumerate(m):
            if s:
                counts[j] += 1
    p = cfg["prices"]
    ev = []
    for g, (m, mae) in zip(pop, pairs):
        n_solved = sum(m)
        share = (sum(1.0 / counts[j] for j, s in enumerate(m) if s)
                 if sh.get("enabled", True) else float(n_solved))
        cost = (structural_units(g) * p["per_structural_unit"]
                + registers_used(g) * p["per_live_register"]
                + len(items) * p["per_item_attempted"])
        ev.append({"score": n_solved / max(1, len(items)), "shared_score": share,
                   "mean_abs_error": mae, "n_solved": n_solved, "cost": cost,
                   "fitness": share - cost, "structural_units": structural_units(g),
                   "live_registers": registers_used(g), "items_attempted": len(items)})
    return ev


def generation(pop, cfg, items, cross_ok, r, elite_frac):
    """One generation. RNG draws are made UNCONDITIONALLY so streams stay aligned
    across arms (CW01-D019/D021) - critical here, since the arm changes only whether a
    drawn partner is COMPATIBLE, never whether a draw happens.

    `elite_frac` is retained for signature stability but no longer selects: deterministic
    truncation over 24 elites let drift dominate and is why control A fixed 6/6 (D052).
    """
    ev = evaluate_population(pop, cfg, items)
    fit = np.array([e["fitness"] for e in ev])
    n = len(pop)
    k = max(2, int(cfg["ecology"].get("tournament_size", 3)))

    attempts = {lab: 0 for lab in {g["label"] for g in pop}}
    successes = {lab: 0 for lab in attempts}
    kids = []
    for i in range(n):
        cand = r.integers(0, n, size=k)                      # tournament: drawn ALWAYS
        a = pop[int(cand[int(np.argmax(fit[cand]))])]
        # ALL THREE draws happen in EVERY arm. A flag must never short-circuit a draw
        # (CW01-D019/D021); the arm changes only how the drawn values are USED.
        j = int(r.integers(0, n))            # partner index
        coin = r.random()                    # recombination coin
        rescue = r.random()                  # M3 rescue pick (ignored when not neutralised)
        b = pop[j]
        child = None
        if coin < cfg["ecology"]["recombination_rate"]:
            attempts[a["label"]] = attempts.get(a["label"], 0) + 1
            partner = b if (compatible(a, b, cross_ok)
                            and a["substrate"] == b["substrate"]) else None
            if partner is None and cross_ok:
                # M3 NEUTRALISATION. The hypothesised mechanism is that a RARE label
                # finds fewer compatible partners, so its recombination yield falls
                # with its own frequency. Neutralising it means partner availability
                # no longer depends on frequency - NOT inventing a cross-substrate
                # body operation, which does not exist. Labels are untouched.
                same = [g for g in pop if g["substrate"] == a["substrate"]]
                if same:
                    partner = same[min(int(rescue * len(same)), len(same) - 1)]
            if partner is not None:
                child = recombine(a, partner, cfg, r)
                if child is not None:
                    successes[a["label"]] = successes.get(a["label"], 0) + 1
        if child is None:
            child = dict(a)
        kids.append(mutate(child, cfg, r))
    return kids, ev, attempts, successes


def evolve(cfg, arm, generations, n_org, mkseed, aid, freq_first=0.5, target=None, n_eval=1):
    """Run one ecology. Returns per-generation TRAJECTORIES, never just endpoints."""
    if target is None:
        target = attempt_target(cfg, mkseed)
    cross_ok = bool(cfg["arms"][arm].get("cross_substrate_recombination", False))
    elite_frac = cfg["ecology"]["elite_fraction"]
    labels = _labels(cfg, arm)

    r = np.random.Generator(np.random.PCG64(mkseed(aid, "evo|" + arm, 0)))
    pop = initial_population(cfg, arm, r, n_org, freq_first)
    ancestors = {g["lineage"] for g in pop}

    hist, extinct = [], {lab: None for lab in labels}
    for gen in range(generations):
        srng = np.random.Generator(np.random.PCG64(mkseed(aid, "stream|%s|%d" % (arm, gen), 0)))
        items = make_items(cfg, srng, target)
        kids, ev, att, suc = generation(pop, cfg, items, cross_ok, r, elite_frac)

        rec = {"gen": gen}
        for lab in labels:
            idx = [i for i, g in enumerate(pop) if g["label"] == lab]
            f = len(idx) / float(len(pop))
            rec["freq_" + lab] = f
            rec["n_" + lab] = len(idx)
            for k in ("score", "fitness", "cost", "structural_units", "live_registers"):
                rec["%s_%s" % (k, lab)] = (float(np.mean([ev[i][k] for i in idx])) if idx else 0.0)
            rec["recomb_attempts_" + lab] = att.get(lab, 0)
            rec["recomb_successes_" + lab] = suc.get(lab, 0)
            rec["recomb_yield_" + lab] = (suc.get(lab, 0) / att[lab]) if att.get(lab) else 0.0
            rec["lineages_" + lab] = len({pop[i]["lineage"] for i in idx})
            if f == 0.0 and extinct[lab] is None:
                extinct[lab] = gen
        hist.append(rec)
        pop = kids

    surviving = {g["lineage"] for g in pop}
    return {"arm": arm, "attempt_id": aid, "freq_first": freq_first, "history": hist,
            "labels": labels, "extinction_generation": extinct,
            "ancestor_lineages": len(ancestors),
            "lineage_survival": len(ancestors & surviving) / max(1, len(ancestors)),
            "final_pop": pop, "target": target}


# ------------------------------------------------- ecological read-outs

def final_frequency(run, label):
    return run["history"][-1].get("freq_" + label, 0.0)


def growth_advantage(run, label, other):
    """Per-capita log growth of `label` relative to `other`, over the run.

    Uses frequency ODDS so the quantity is a genuine per-capita rate rather than a
    terminal abundance. Undefined odds (extinction) are clamped to the population's
    resolution rather than dropped, so a displaced label still contributes.
    """
    h, n = run["history"], float(len(run["history"][0].get("n_" + label, 0) or 1))
    res = 1.0 / max(2.0, sum(h[0].get("n_" + lab, 0) for lab in run["labels"]))

    def odds(rec):
        a = min(max(rec.get("freq_" + label, 0.0), res), 1 - res)
        b = min(max(rec.get("freq_" + other, 0.0), res), 1 - res)
        return a / b

    return float((math.log(odds(h[-1])) - math.log(odds(h[0]))) / max(1, len(h) - 1))


def invaded(run, label, other):
    """Did `label` increase from its seeded frequency? (invasion when rare)"""
    return final_frequency(run, label) > run["history"][0].get("freq_" + label, 0.0)


def displacement_generation(run, label):
    """Generation at which `label` was displaced, or None if it persisted."""
    return run["extinction_generation"].get(label)


def coexisting(run, eps=0.05):
    """Both labels still present above a resolution floor at the end."""
    return all(final_frequency(run, lab) > eps for lab in run["labels"])
