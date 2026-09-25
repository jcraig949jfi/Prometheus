"""AETH-02 H1-H4: zero-dollar falsification tests of the interpretation.

Each is written as a test that can FAIL. The report's mechanistic reading
is that persistence in `aeth01.v1` is uncontested residue rather than
anything functional; if these disagree, the reading is what changes.

  H1  persistent edges are non-contest residue and are NOT repaired
  H2  stationary statistics predict the edge and contest structure
      without invoking a structure-forming process
  H3  cycle enrichment for state-changing edges is a structural
      consequence of who can be on a cycle at all
  H4  removing perturbation removes about the predicted share of
      template-field change, immediately

All run on CPU at a lattice small enough to be free. §0 is the control
that makes that legitimate: the small lattice has to reproduce the
2048² stationary statistics before anything measured on it is quoted.

Nothing here alters `aeth01.v1`. The lesion in H1 edits lattice state
between ticks, exactly as an external intervention would; the kernel is
unmodified and the semantics id is untouched.
"""

import argparse
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_AETHER = os.path.dirname(_HERE)
for _p in (_AETHER, os.path.join(_AETHER, "test", "reference")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gpu_aeth01 as K                                   # noqa: E402
from observatory import aeth01_graph as G                # noqa: E402
from observatory import aeth01_observatory as OBS        # noqa: E402
from observatory import aeth01_run as R                  # noqa: E402

FIELDS = ("opcode", "arg0", "arg1", "payload", "energy")
TEMPLATE = ("opcode", "arg0", "arg1", "payload")

# B_balanced, exactly as the trajectories ran it.
B_BALANCED = dict(write_cost=1, maintenance_cost=1,
                  replenish_numer=int(round(0.125 * (1 << 32))),
                  replenish_amount=8)
B_SEED0 = 0x5C011701
B_RNG0 = 0xA37E01
MUT_NUMER = int(round(0.1 * (1 << 32)))

# Measured on the 2048^2 trajectories, from the committed evidence via
# `aeth02_reduce`. The small-lattice control in §0 is checked against
# these; they are observations, not targets to tune toward.
REFERENCE_2048 = {
    "write_density": 0.422507, "activity_density": 0.191052,
    "starved_density": 0.231455, "change_rate": 0.184610,
    "energy_gini": 0.587116, "entropy_opcode_bits": 5.5992,
    "edge_fraction": 788606 / (2048.0 * 2048.0 * 5),
    "state_changing": 0.270794, "same_uncontested": 0.722505,
    # From the 2048^2 fan-in histogram (opcode field, final sample):
    # 3,386 slots with 2 contenders + 18 with 3, over 198,562 edges.
    "contested_of_edges": (3386 + 18) / 198562.0,
    "ge64_opcode": 0.06964,
}


def params(seed=B_SEED0, mut_numer=MUT_NUMER):
    out = dict(B_BALANCED)
    out.update(seed=seed, mut_numer=mut_numer)
    return out


def step(fields, tick, par, watch=True):
    """One tick. Returns (fields, observer) with the observer or None."""
    observer = [] if watch else None
    out = K.gpu_step(H=fields[0].shape[0], W=fields[0].shape[1], tick=tick,
                     opcode=fields[0], arg0=fields[1], arg1=fields[2],
                     payload=fields[3], energy=fields[4],
                     observer=observer, **par)
    return list(out[:5]), observer


def run(n, ticks, seed=B_SEED0, rng_seed=B_RNG0, mut_numer=MUT_NUMER,
        fields=None, start_tick=1, track_runs=True, sample_every=0,
        progress=None):
    """Advance a world, tracking edge run-lengths. Returns a dict."""
    par = params(seed, mut_numer)
    if fields is None:
        fields, _recipe = R.build_initial("sparse_soup", n, n, rng_seed,
                                          write_density=0.50)
        fields = [f.copy() for f in fields]
    runs = G.new_runlengths(np, n, n) if track_runs else None
    samples, observer = [], None
    for offset in range(ticks):
        tick = start_tick + offset
        before = [f.copy() for f in fields] if sample_every else None
        fields, observer = step(fields, tick, par)
        if runs is not None:
            G.update_runlengths(np, runs, observer)
        if sample_every and (offset + 1) % sample_every == 0:
            samples.append(measure(np, before, fields, observer, runs, tick,
                                   par["write_cost"]))
        if progress and (offset + 1) % progress == 0:
            print("    tick %d/%d" % (offset + 1, ticks), file=sys.stderr)
    return {"fields": fields, "runs": runs, "observer": observer,
            "samples": samples, "tick": start_tick + ticks - 1, "params": par}


def measure(xp, before, after, observer, runs, tick, write_cost):
    """The subset of the observatory this module quotes."""
    out = {"tick": tick}
    out.update(OBS.cheap_counters(xp, after, write_cost))
    rate, per_field = OBS.change_rate(xp, before, after)
    out["change_rate"] = rate
    out["change_rate_by_field"] = per_field
    out["energy_gini"] = OBS.gini_from_counts(OBS.histogram256(xp, after[4]))
    out["entropy_opcode_bits"] = OBS.entropy_bits(
        OBS.histogram256(xp, after[0]))
    classes = G.edge_classes(xp, observer, before, after)
    total = sum(classes[f]["edges"] for f in FIELDS)
    n = after[0].size
    out["edges_total"] = total
    out["edge_fraction"] = total / float(n * 5)
    out["classes"] = classes
    for cls in G.CLASSES:
        out[cls.lower()] = sum(classes[f][cls] for f in FIELDS) / float(total)
    # The same-value contested classes are NOT the contested share: the
    # classification breaks out contest only for same-value edges, so
    # every contested edge that DID change state is missing from them.
    # The true share comes from the observer's own contender counts.
    out["same_value_contested_of_edges"] = (
        out["same_value_contested_alternative_change"]
        + out["same_value_contested_no_alternative_change"])
    contested = present = 0
    for entry in observer:
        winner, contenders, _differ = G.unpack(entry)
        live = winner != G.NO_WINNER
        present += int(live.sum())
        contested += int((live & (contenders >= 2)).sum())
    out["contested_edges"] = contested
    out["contested_of_edges"] = contested / float(present) if present else 0.0
    if runs is not None:
        out["ge64_opcode"] = float(
            (runs["run"][0] >= 64).sum()) / max(1, int((runs["run"][0] >= 1).sum()))
    return out


# ---------------------------------------------------------------- §0 control

def control_small_lattice_matches(n=256, ticks=2500, seed=B_SEED0,
                                  rng_seed=B_RNG0, tol=0.05):
    """Does the cheap lattice reproduce the 2048² stationary state?

    Everything below is measured at `n`. If `n` does not reproduce the
    statistics the report quotes, nothing measured at `n` may be used to
    argue about them, and this returns `passed: False` rather than
    letting four falsifiers rest on an unchecked proxy.
    """
    result = run(n, ticks, seed=seed, rng_seed=rng_seed,
                 sample_every=max(1, ticks // 5))
    last = result["samples"][-1]
    rows = {}
    for key, reference in REFERENCE_2048.items():
        got = last.get(key)
        if got is None:
            continue
        rel = abs(got - reference) / abs(reference) if reference else None
        rows[key] = {"reference_2048": reference, "observed": got,
                     "relative_error": rel, "within_tol": rel is not None
                     and rel <= tol}
    return {"n": n, "ticks": ticks, "tolerance": tol,
            "comparison": rows,
            "passed": all(r["within_tol"] for r in rows.values()),
            "state": result}


# ------------------------------------------------------------------ H1

def h1b_frozen_neighbourhoods(n=256, warmup=2500, window=64, seed=B_SEED0,
                              rng_seed=B_RNG0, field=0):
    """Are persistent edges inside locally static configurations?

    Measures, over `window` ticks after stationarity, the fraction of
    sites whose four template fields never change ("frozen"), and then
    compares frozen-ness and neighbourhood activity for the targets and
    sources of PERSISTENT edges against those of SHORT-run edges.

    PREDICTION, if H1's zero-occupancy result is explained by local
    stasis: persistent-edge targets and sources are far more likely to be
    frozen than short-run ones, and their neighbourhoods contain fewer
    active writers.

    This is an observation, not a falsifier: it explains an H1 result
    rather than testing a preregistered claim, and it is labelled that way
    in the closing report.
    """
    base = run(n, warmup, seed=seed, rng_seed=rng_seed)
    winner = G.unpack(base["observer"][field])[0]
    run_len = base["runs"]["run"][field]
    present = winner != G.NO_WINNER
    persistent = present & (run_len >= 64)
    short = present & (run_len >= 1) & (run_len <= 8)

    start = [f.copy() for f in base["fields"]]
    fields = [f.copy() for f in base["fields"]]
    par = params(seed)
    changed_any = np.zeros((n, n), dtype=bool)
    for offset in range(window):
        fields, _obs = step(fields, base["tick"] + 1 + offset, par,
                            watch=False)
    for idx in range(4):
        changed_any |= (fields[idx] != start[idx])
    frozen = ~changed_any

    # Neighbourhood activity: how many of the four neighbours are active
    # writers right now. A frozen site should have few.
    active = (start[0] == K.WRITE_OPCODE) & (
        start[4].astype(np.int64) >= par["write_cost"])
    neighbours = np.zeros((n, n), dtype=np.uint8)
    for dr, dc in G.SLOT_OFFSETS:
        neighbours += np.roll(active, (dr, dc), axis=(0, 1)).astype(np.uint8)

    offsets = np.array(G.SLOT_OFFSETS, dtype=np.int64)

    def describe(mask, label):
        targets = np.argwhere(mask)
        if not len(targets):
            return {"label": label, "n": 0}
        slots = winner[mask]
        srcs = (targets + offsets[slots]) % n
        return {
            "label": label,
            "n": int(len(targets)),
            "target_frozen": float(frozen[mask].mean()),
            "source_frozen": float(frozen[srcs[:, 0], srcs[:, 1]].mean()),
            "target_active_neighbours": float(neighbours[mask].mean()),
            "source_active_neighbours": float(
                neighbours[srcs[:, 0], srcs[:, 1]].mean()),
        }

    return {
        "n": n, "warmup": warmup, "window": window,
        "frozen_fraction_all_sites": float(frozen.mean()),
        "mean_active_neighbours_all_sites": float(neighbours.mean()),
        "persistent": describe(persistent, "run >= 64"),
        "short": describe(short, "run <= 8"),
    }


def h1_repair(n=256, warmup=2500, follow=500, k=400, seed=B_SEED0,
              rng_seed=B_RNG0, lesion_seed=0x11A2,
              field=0):
    """H1: persistent edges are residue, and nothing repairs them.

    PROTOCOL. Run to stationarity tracking run-lengths. Take the edges of
    one field and split them by run length into PERSISTENT (>= 64) and
    SHORT (<= 8). From the same snapshot, fork three arms:

      ARM_P     re-aim the SOURCE of each sampled persistent edge
      ARM_S     re-aim the SOURCE of each sampled short edge
      ARM_SHAM  sample persistent edges, change nothing

    The lesion adds 1 to the source's `arg0`, which rotates its target
    direction by one and leaves it active. That is the minimal edit that
    removes the edge without removing the writer, so a difference between
    arms cannot be explained by having disabled a site.

    MEASURED, at several horizons: the fraction of lesioned edges whose
    ORIGINAL source is again writing that target ("recurrence"), and the
    fraction of those targets receiving any edge at all ("occupancy").

    PREDICTION under H1: recurrence in ARM_P does not exceed ARM_S. If a
    persistent edge is a maintained structure, ARM_P recurs faster.
    FALSIFIED IF: ARM_P recurrence materially exceeds ARM_S.
    """
    base = run(n, warmup, seed=seed, rng_seed=rng_seed)
    runs, observer = base["runs"], base["observer"]
    winner = G.unpack(observer[field])[0]
    run_len = runs["run"][field]
    present = winner != G.NO_WINNER

    rng = np.random.default_rng(lesion_seed)
    persistent = np.argwhere(present & (run_len >= 64))
    short = np.argwhere(present & (run_len >= 1) & (run_len <= 8))
    k = int(min(k, len(persistent), len(short)))
    if k < 20:
        raise RuntimeError("too few edges to compare: %d persistent, %d short"
                           % (len(persistent), len(short)))
    pick_p = persistent[rng.choice(len(persistent), k, replace=False)]
    pick_s = short[rng.choice(len(short), k, replace=False)]

    def sources(targets):
        slots = winner[targets[:, 0], targets[:, 1]]
        offs = np.array(G.SLOT_OFFSETS, dtype=np.int64)[slots]
        return ((targets + offs) % n)

    src_p, src_s = sources(pick_p), sources(pick_s)
    horizons = sorted({1, 10, 50, 100, min(follow, 250), follow})
    arms = {}
    for name, targets, srcs, lesion in (("ARM_P", pick_p, src_p, True),
                                        ("ARM_S", pick_s, src_s, True),
                                        ("ARM_SHAM", pick_p, src_p, False)):
        fields = [f.copy() for f in base["fields"]]
        if lesion:
            fields[1][srcs[:, 0], srcs[:, 1]] = (
                fields[1][srcs[:, 0], srcs[:, 1]] + np.uint8(1))
        par = params(seed)
        track = {h: None for h in horizons}
        for offset in range(follow):
            tick = base["tick"] + 1 + offset
            fields, obs = step(fields, tick, par)
            step_no = offset + 1
            if step_no in track:
                w = G.unpack(obs[field])[0]
                got = w[targets[:, 0], targets[:, 1]]
                offs = np.array(G.SLOT_OFFSETS, dtype=np.int64)
                recurred = np.zeros(len(targets), dtype=bool)
                live = got != G.NO_WINNER
                if live.any():
                    back = (targets[live] + offs[got[live]]) % n
                    recurred[live] = np.all(back == srcs[live], axis=1)
                track[step_no] = {
                    "recurrence": float(recurred.mean()),
                    "occupancy": float(live.mean())}
        arms[name] = {"k": k, "horizons": track}

    verdict = {}
    for h in horizons:
        p = arms["ARM_P"]["horizons"][h]["recurrence"]
        s = arms["ARM_S"]["horizons"][h]["recurrence"]
        verdict[h] = {"ARM_P": p, "ARM_S": s, "excess": p - s}
    final = verdict[max(horizons)]
    return {"n": n, "warmup": warmup, "follow": follow, "k": k,
            "field": FIELDS[field], "arms": arms, "by_horizon": verdict,
            "excess_final": final["excess"],
            # A repaired structure would recur MORE than the short-run
            # control. "Not falsified" here means it does not.
            "falsified": final["excess"] > 0.05}


# ------------------------------------------------------------------ H2

def h2_independence(sample):
    """H2: independent stationary statistics predict the edge structure.

    Each active site aims at one of 4 directions and one of 5 fields, so
    under independence a given (site, field) slot is targeted by a given
    neighbour with probability p = activity_density / 20, and has

        P(>=1 contender) = 1 - (1-p)^4
        P(exactly 1)     = 4p(1-p)^3

    Persistence needs a further step: an edge recurs next tick if its
    source keeps its opcode, direction and target field, and no second
    contender appears. Estimating each from the measured per-field change
    rates gives a per-tick recurrence s, and P(run >= 64) = s^63.

    FALSIFIED IF: the predicted edge fraction or contested share is out by
    more than a factor of two, or -- more interestingly -- if the
    persistence prediction is right, since a correct independent
    prediction of the persistent cohort would mean no correlated
    stability is involved at all.
    """
    p = sample["activity_density"] / 20.0
    at_least_one = 1.0 - (1.0 - p) ** 4
    exactly_one = 4.0 * p * (1.0 - p) ** 3
    contested = (at_least_one - exactly_one) / at_least_one if at_least_one \
        else None

    rates = sample.get("change_rate_by_field") or {}
    keep_op = 1.0 - rates.get("opcode", 0.0)
    keep_a0 = 1.0 - rates.get("arg0", 0.0)
    keep_a1 = 1.0 - rates.get("arg1", 0.0)
    # A changed arg0 lands back on the same direction 1 time in 4, and a
    # changed arg1 on the same field 1 time in 5. Not crediting that would
    # understate the independent prediction and make the test easier.
    keep_dir = keep_a0 + (1.0 - keep_a0) / 4.0
    keep_field = keep_a1 + (1.0 - keep_a1) / 5.0
    no_new_rival = 1.0 - (at_least_one - exactly_one)
    s = keep_op * keep_dir * keep_field * no_new_rival
    predicted_ge64 = s ** 63

    observed_edges = sample["edge_fraction"]
    # The share of edges with two or more contenders, counted by the
    # kernel. Not the same-value contested classes: see `measure`.
    observed_contested = sample["contested_of_edges"]
    observed_ge64 = sample.get("ge64_opcode")

    def ratio(pred, obs):
        return None if not obs else pred / obs

    out = {
        "p_per_neighbour": p,
        "predicted_edge_fraction": at_least_one,
        "observed_edge_fraction": observed_edges,
        "edge_ratio": ratio(at_least_one, observed_edges),
        "predicted_contested_share": contested,
        "observed_contested_share": observed_contested,
        "contested_ratio": ratio(contested, observed_contested),
        "per_tick_recurrence": s,
        "predicted_ge64": predicted_ge64,
        "observed_ge64": observed_ge64,
        "ge64_ratio": ratio(predicted_ge64, observed_ge64),
    }
    out["edges_predicted_well"] = (out["edge_ratio"] is not None
                                   and 0.5 <= out["edge_ratio"] <= 2.0)
    out["contested_predicted_well"] = (out["contested_ratio"] is not None
                                       and 0.5 <= out["contested_ratio"] <= 2.0)
    out["persistence_predicted_well"] = (out["ge64_ratio"] is not None
                                         and 0.5 <= out["ge64_ratio"] <= 2.0)
    # H2 as stated claims the stationary statistics suffice. It fails if
    # the instantaneous structure is mispredicted, and it is INCOMPLETE if
    # the instantaneous structure is right but persistence is not.
    out["falsified"] = not (out["edges_predicted_well"]
                            and out["contested_predicted_well"])
    out["incomplete"] = (not out["falsified"]
                         and not out["persistence_predicted_well"])
    return out


# ------------------------------------------------------------------ H3

def enrichment_for(observer, before, after, restrict, fields):
    """State-changing share over `fields`, optionally restricted by target."""
    classes = G.edge_classes(np, observer, before, after, restrict=restrict)
    total = sum(classes[f]["edges"] for f in fields)
    if not total:
        return None, 0
    changing = sum(classes[f]["STATE_CHANGING"] for f in fields)
    return changing / float(total), total


def h3_cycle_enrichment(state, field_pool=FIELDS, rewire_seed=0x3C1,
                        rewirings=8):
    """H3: cycle enrichment is structural, not selection.

    A node can only be on a cycle if it has an outgoing edge, i.e. if it
    is an active writer. That is a constraint on the TARGET of the edges
    being counted, so before attributing anything to cycles we ask what
    conditioning on "target is a writer" alone already buys.

    Two controls:
      WRITER   edges whose target has out-degree 1 but is NOT on a cycle
      REWIRED  each edge's target reassigned uniformly among its source's
               four neighbours, preserving per-field edge counts and each
               edge's own class label, then cycles recomputed

    FALSIFIED IF: neither control reproduces the enrichment, i.e. cycle
    membership carries information beyond the writer constraint and beyond
    degree structure.
    """
    observer = state["observer"]
    before, after = state["before"], state["fields"]
    n = after[0].shape[0]
    nxt = G.realized_map(np, observer, n, n)
    mask, cycle_nodes, _steps = G.cycle_node_mask(np, nxt)
    on_cycle = mask.reshape(n, n).astype(bool)
    has_out = (nxt >= 0).reshape(n, n)

    def enrichment(restrict):
        classes = G.edge_classes(np, observer, before, after, restrict=restrict)
        total = sum(classes[f]["edges"] for f in field_pool)
        if not total:
            return None, 0
        changing = sum(classes[f]["STATE_CHANGING"] for f in field_pool)
        return changing / float(total), total

    overall, n_all = enrichment(None)
    cycle_rate, n_cycle = enrichment(on_cycle)
    writer_only = has_out & (~on_cycle)
    writer_rate, n_writer = enrichment(writer_only)
    nonwriter_rate, n_non = enrichment(~has_out)

    # Per field, because the pooled number cannot tell a constraint that
    # bites on one field from an effect spread across all five.
    per_field = {}
    for name in FIELDS:
        one = (name,)
        base, base_n = enrichment_for(observer, before, after, None, one)
        cyc, cyc_n = enrichment_for(observer, before, after, on_cycle, one)
        wri, wri_n = enrichment_for(observer, before, after, writer_only, one)
        per_field[name] = {
            "overall": base, "on_cycle": cyc, "writer_not_cycle": wri,
            "edges": base_n, "edges_on_cycle": cyc_n,
            "cycle_enrichment": (cyc / base) if base else None,
            "writer_enrichment": (wri / base) if base else None,
        }

    rng = np.random.default_rng(rewire_seed)
    rewired = []
    rows = np.arange(n, dtype=np.int64).reshape(n, 1)
    cols = np.arange(n, dtype=np.int64).reshape(1, n)
    offsets = np.array(G.SLOT_OFFSETS, dtype=np.int64)
    for _ in range(rewirings):
        null = np.full(n * n, -1, dtype=np.int64)
        live = np.argwhere((nxt >= 0).reshape(n, n))
        slots = rng.integers(0, 4, size=len(live))
        tgt = (live + offsets[slots]) % n
        null[live[:, 0] * n + live[:, 1]] = tgt[:, 0] * n + tgt[:, 1]
        nmask, ncount, _ = G.cycle_node_mask(np, null)
        rewired.append(ncount)

    return {
        "per_field": per_field,
        "n": n, "cycle_nodes": cycle_nodes,
        "mapped_nodes": int((nxt >= 0).sum()),
        "cycle_share": cycle_nodes / max(1, int((nxt >= 0).sum())),
        "state_changing": {
            "overall": overall, "on_cycle": cycle_rate,
            "writer_not_cycle": writer_rate, "not_a_writer": nonwriter_rate},
        "edges": {"all": n_all, "on_cycle": n_cycle,
                  "writer_not_cycle": n_writer, "not_a_writer": n_non},
        "cycle_enrichment": (cycle_rate / overall) if overall else None,
        "writer_enrichment": (writer_rate / overall) if overall else None,
        "rewired_cycle_nodes": {
            "mean": float(np.mean(rewired)), "min": int(min(rewired)),
            "max": int(max(rewired)), "trials": rewirings},
        # The writer constraint explains it if conditioning on "target is
        # a writer, but off-cycle" already reproduces most of the lift.
        "explained_by_writer_constraint": (
            writer_rate is not None and cycle_rate is not None
            and overall is not None
            and abs(writer_rate - cycle_rate) / (cycle_rate - overall) < 0.5
            if cycle_rate and overall and cycle_rate != overall else None),
    }


# ------------------------------------------------------------------ H4

def h4_perturbation(n=256, warmup=2500, follow=400, seed=B_SEED0,
                    rng_seed=B_RNG0, predicted_drop=0.38):
    """H4: perturbation supplies ~38% of template-field change.

    From a shared stationary snapshot, fork a control that keeps
    `mut_numer` and a treatment at `mut_numer = 0`. `aeth01.v1` is not
    modified: the perturbation rate is a run parameter.

    PREDICTION: the template change rate drops by about `predicted_drop`
    in the FIRST tick after the switch -- the redundant-channel share --
    and then keeps falling as redundant channels stop being re-randomised.
    Energy dynamics, which have no perturbation term, are unaffected.

    FALSIFIED IF: the immediate drop is not within a factor of 1.5 of the
    prediction, or if energy change moves materially.
    """
    base = run(n, warmup, seed=seed, rng_seed=rng_seed, track_runs=False)
    horizons = sorted({1, 2, 5, 10, 50, 100, follow})
    arms = {}
    for name, mut in (("CONTROL", MUT_NUMER), ("NO_PERTURBATION", 0)):
        fields = [f.copy() for f in base["fields"]]
        par = params(seed, mut)
        series = {}
        for offset in range(follow):
            tick = base["tick"] + 1 + offset
            prev = [f.copy() for f in fields]
            fields, _obs = step(fields, tick, par, watch=False)
            step_no = offset + 1
            if step_no in horizons:
                _rate, per_field = OBS.change_rate(np, prev, fields)
                series[step_no] = {
                    "template": sum(per_field[f] for f in TEMPLATE) / 4.0,
                    "energy": per_field["energy"]}
        arms[name] = series
    drops = {}
    for h in horizons:
        c = arms["CONTROL"][h]["template"]
        t = arms["NO_PERTURBATION"][h]["template"]
        drops[h] = {"control": c, "treated": t,
                    "drop": (c - t) / c if c else None}
    immediate = drops[1]["drop"]
    energy_shift = abs(arms["NO_PERTURBATION"][1]["energy"]
                       - arms["CONTROL"][1]["energy"])
    return {
        "n": n, "warmup": warmup, "follow": follow,
        "predicted_immediate_drop": predicted_drop,
        "observed_immediate_drop": immediate,
        "ratio": immediate / predicted_drop if predicted_drop else None,
        "by_horizon": drops,
        "energy_change_shift_at_tick1": energy_shift,
        "falsified": not (predicted_drop / 1.5 <= immediate
                          <= predicted_drop * 1.5)
        or energy_shift > 0.01,
    }


# ------------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("which", choices=["control", "h1", "h1b", "h2", "h3",
                                      "h4", "all"])
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--warmup", type=int, default=2500)
    ap.add_argument("--follow", type=int, default=400)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    results = {}
    if args.which in ("control", "h2", "h3", "all"):
        print("[control] %d^2 for %d ticks…" % (args.n, args.warmup),
              file=sys.stderr)
        ctl = control_small_lattice_matches(args.n, args.warmup)
        state = ctl.pop("state")
        results["control"] = ctl
        print("[control] passed=%s" % ctl["passed"], file=sys.stderr)
    if args.which in ("h2", "all"):
        results["h2"] = h2_independence(state["samples"][-1])
        print("[h2] falsified=%s incomplete=%s"
              % (results["h2"]["falsified"], results["h2"]["incomplete"]),
              file=sys.stderr)
    if args.which in ("h3", "all"):
        prev = [f.copy() for f in state["fields"]]
        fields, obs = step(state["fields"], state["tick"] + 1, state["params"])
        results["h3"] = h3_cycle_enrichment(
            {"observer": obs, "before": prev, "fields": fields})
        print("[h3] cycle_enrichment=%.3f writer_enrichment=%.3f"
              % (results["h3"]["cycle_enrichment"],
                 results["h3"]["writer_enrichment"]), file=sys.stderr)
    if args.which in ("h1", "all"):
        print("[h1] lesion experiment…", file=sys.stderr)
        results["h1"] = h1_repair(args.n, args.warmup, args.follow)
        print("[h1] excess=%+.4f falsified=%s"
              % (results["h1"]["excess_final"], results["h1"]["falsified"]),
              file=sys.stderr)
    if args.which in ("h1b", "all"):
        print("[h1b] frozen-neighbourhood probe…", file=sys.stderr)
        results["h1b"] = h1b_frozen_neighbourhoods(args.n, args.warmup)
        f = results["h1b"]
        print("[h1b] frozen sites %.4f; persistent targets frozen %.4f vs "
              "short %.4f" % (f["frozen_fraction_all_sites"],
                              f["persistent"]["target_frozen"],
                              f["short"]["target_frozen"]), file=sys.stderr)
    if args.which in ("h4", "all"):
        print("[h4] perturbation ablation…", file=sys.stderr)
        results["h4"] = h4_perturbation(args.n, args.warmup, args.follow)
        print("[h4] immediate drop %.4f (predicted %.2f) falsified=%s"
              % (results["h4"]["observed_immediate_drop"],
                 results["h4"]["predicted_immediate_drop"],
                 results["h4"]["falsified"]), file=sys.stderr)

    text = json.dumps(results, indent=2, sort_keys=True, default=float)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
        print("wrote %s" % args.out, file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
