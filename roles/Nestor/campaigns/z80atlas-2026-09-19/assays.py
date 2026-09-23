"""Post-run assays: the Atlas axes, applied to what a run actually produced.

These are MEASUREMENTS on preserved organisms and on the run's own series. They never
change a run and never feed back into it; the scheduler attaches their output to the
record. Keeping them post-run is what lets the same axis be applied to any cell of the
grammar without multiplying the physics.

RULER PROVENANCE IS RECORDED, because this campaign has already paid for the alternative.
The damage ruler here is QUALIFIED SCATTERED BERNOULLI: each byte inside the program's own
length is hit independently with probability f, so the expected dose scales with length
instead of being a fixed count. A fixed-count ruler hits short genomes harder and
manufactures a length-robustness coordinate out of nothing - four of seven claims in an
earlier campaign turned out to be that ruler rather than the organisms.
"""
from __future__ import annotations

import random

import tasks
import z8

DOSES = (0.02, 0.05, 0.10, 0.20)
DRAWS = 6
LOAD_K = (1, 2, 4, 8)

RULER = {
    "damage": "qualified scattered Bernoulli(f) over the program's own bytes; dose scales with length",
    "draws": DRAWS, "doses": DOSES,
    "load": "k accumulated point mutations using the campaign's operand/opcode perturbation model",
    "why_not_fixed_count": "a fixed-count ruler is a harsher dose for a short genome and manufactures a length coordinate",
}


def _perturb(g, i, is_op, rng):
    g = bytearray(g)
    if is_op:
        g[i] = rng.randrange(256)
    else:
        u = rng.random()
        if u < 0.45:
            g[i] = (g[i] + rng.randint(-8, 8)) & 0xFF
        elif u < 0.90:
            g[i] ^= 1 << rng.randrange(8)
        else:
            g[i] = rng.randrange(256)
    return bytes(g)


def _damage(g, f, rng):
    """Scattered Bernoulli damage over the program's own bytes."""
    opcodes = set(a for a, _ in z8.dis(g))
    out = bytearray(g)
    hit = 0
    for i in range(len(out)):
        if rng.random() < f:
            out = bytearray(_perturb(bytes(out), i, i in opcodes, rng))
            hit += 1
    return bytes(out), hit


def damage_cliff(specimens, spec, seed, n=3):
    rng = random.Random(seed ^ 0xDA3A9E)
    rows = []
    for sp in specimens[:n]:
        g = bytes.fromhex(sp["genome_hex"])
        base = tasks.competence(g, spec, seed=seed, held_seed=seed + 1)["held"]
        curve = []
        for f in DOSES:
            losses, hits = [], []
            for d in range(DRAWS):
                dg, h = _damage(g, f, rng)
                c = tasks.competence(dg, spec, seed=seed, held_seed=seed + 1)["held"]
                losses.append(base - c)
                hits.append(h)
            curve.append({"f": f, "mean_bytes_hit": round(sum(hits) / len(hits), 2),
                          "mean_loss": round(sum(losses) / len(losses), 4),
                          "share_lethal": round(sum(1 for l in losses if base > 0 and l >= base * 0.9)
                                                / len(losses), 3)})
        rows.append({"hash": sp["hash"], "len": sp["len"], "base_held": round(base, 4), "curve": curve})
    return {"ruler": RULER, "rows": rows}


def deleterious_load(specimens, spec, seed, n=3):
    rng = random.Random(seed ^ 0x10AD)
    rows = []
    for sp in specimens[:n]:
        g0 = bytes.fromhex(sp["genome_hex"])
        base = tasks.competence(g0, spec, seed=seed, held_seed=seed + 1)["held"]
        curve = []
        for k in LOAD_K:
            vals = []
            for _ in range(DRAWS):
                g = g0
                opcodes = set(a for a, _ in z8.dis(g))
                for _j in range(k):
                    i = rng.randrange(len(g))
                    g = _perturb(g, i, i in opcodes, rng)
                vals.append(tasks.competence(g, spec, seed=seed, held_seed=seed + 1)["held"])
            curve.append({"k": k, "mean_held": round(sum(vals) / len(vals), 4),
                          "share_dead": round(sum(1 for v in vals if v <= 0.05) / len(vals), 3)})
        rows.append({"hash": sp["hash"], "len": sp["len"], "base_held": round(base, 4), "curve": curve})
    return {"ruler": RULER, "rows": rows}


def residue_transport(specimens, cell, seed, n=3):
    """Score preserved organisms under task variants they never evolved against.

    This is the campaign's cross-environment readout: machinery that only ever works on
    the exact task it evolved against is local; machinery that carries is transferable.
    """
    variants = {}
    base_cell = dict(cell)
    for tr in ("XOR1", "ADD1", "XOR15", "XOR5A"):
        for ro in tasks.READ_ORDERS:
            c = dict(base_cell)
            c["task_transform"], c["read_order"] = tr, ro
            variants["%s|%s" % (tr, ro)] = tasks.spec_from_cell(c, n_episodes=16)
    rows = []
    for sp in specimens[:n]:
        g = bytes.fromhex(sp["genome_hex"])
        rows.append({"hash": sp["hash"], "len": sp["len"],
                     "scores": {k: round(tasks.competence(g, s, seed=seed, held_seed=seed + 1)["held"], 4)
                                for k, s in variants.items()}})
    return {"home": "%s|%s" % (cell["task_transform"], cell["read_order"]), "rows": rows}


def length_robustness(specimens, spec, seed, f=0.10):
    rng = random.Random(seed ^ 0x1E2)
    pts = []
    for sp in specimens[:8]:
        g = bytes.fromhex(sp["genome_hex"])
        base = tasks.competence(g, spec, seed=seed, held_seed=seed + 1)["held"]
        losses = []
        for _ in range(DRAWS):
            dg, _h = _damage(g, f, rng)
            losses.append(base - tasks.competence(dg, spec, seed=seed, held_seed=seed + 1)["held"])
        pts.append({"len": sp["len"], "base_held": round(base, 4),
                    "mean_loss": round(sum(losses) / len(losses), 4)})
    r = None
    if len(pts) >= 4:
        xs = [p["len"] for p in pts]
        ys = [p["mean_loss"] for p in pts]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in ys)
        r = round(sxy / ((sxx * syy) ** 0.5), 4) if sxx > 0 and syy > 0 else None
    return {"ruler": RULER, "dose": f, "points": pts, "pearson_len_vs_loss": r,
            "note": "length varies only as much as the run made it vary; a null r with no length "
                    "spread is an absence of contrast, not an absence of effect"}


def _series(series, key):
    return [(r.get("e"), r.get(key)) for r in series if isinstance(r.get(key), (int, float))]


def stasis_escape(series, key="comp_max", tol=0.02):
    xs = _series(series, key)
    if len(xs) < 6:
        return {"n_points": len(xs), "longest_plateau": None}
    best = cur = 1
    start = xs[0][0]
    best_start = start
    for i in range(1, len(xs)):
        if abs(xs[i][1] - xs[i - 1][1]) <= tol:
            cur += 1
            if cur > best:
                best, best_start = cur, start
        else:
            cur = 1
            start = xs[i][0]
    end_val = xs[-1][1]
    plateau_val = max(v for _e, v in xs[:max(2, len(xs) // 2)])
    return {"key": key, "n_points": len(xs), "longest_plateau_points": best,
            "plateau_started_epoch": best_start, "escaped": bool(end_val > plateau_val + 0.1),
            "final": end_val, "plateau_level": plateau_val}


def transitions(series, keys=("comp_max", "len_mean", "uniq", "dom_share", "span_mean", "entropy")):
    """Largest single-step changes per metric: a mechanical historical-transition detector."""
    out = {}
    for k in keys:
        xs = _series(series, k)
        if len(xs) < 4:
            continue
        deltas = [(abs(xs[i][1] - xs[i - 1][1]), xs[i][0], xs[i - 1][1], xs[i][1])
                  for i in range(1, len(xs))]
        deltas.sort(key=lambda t: -t[0])
        d, e, a, b = deltas[0]
        spread = max(v for _e, v in xs) - min(v for _e, v in xs)
        out[k] = {"max_step": round(d, 4), "at_epoch": e, "from": round(a, 4), "to": round(b, 4),
                  "share_of_range": round(d / spread, 3) if spread > 0 else None}
    return out


def run_assays(cell, summary, series, specimens, seed):
    """Dispatch on the cell's declared axis. NONE means nothing is measured, not that
    something was measured and found empty."""
    axis = cell["atlas_axis"]
    if axis == "NONE" or not specimens:
        return {"axis": axis, "ran": False}
    spec = tasks.spec_from_cell(cell, n_episodes=16)
    try:
        if axis == "DAMAGE_CLIFF":
            return {"axis": axis, "ran": True, "damage_cliff": damage_cliff(specimens, spec, seed)}
        if axis == "DELETERIOUS_LOAD":
            return {"axis": axis, "ran": True, "deleterious_load": deleterious_load(specimens, spec, seed)}
        if axis == "RESIDUE_TRANSPORT":
            return {"axis": axis, "ran": True, "residue_transport": residue_transport(specimens, cell, seed)}
        if axis == "LENGTH_ROBUSTNESS":
            return {"axis": axis, "ran": True, "length_robustness": length_robustness(specimens, spec, seed)}
        if axis == "STASIS_ESCAPE":
            return {"axis": axis, "ran": True, "stasis": stasis_escape(series),
                    "stasis_len": stasis_escape(series, key="len_mean")}
        if axis == "TRANSITION_DETECTOR":
            return {"axis": axis, "ran": True, "transitions": transitions(series)}
        if axis == "RECOMBINATION":
            return {"axis": axis, "ran": True,
                    "in_run": {"fid_mean_final": summary.get("fid_mean_final"),
                               "span_mean_final": summary.get("span_mean_final"),
                               "births_endogenous": summary.get("births_endogenous"),
                               "uniq_final": summary.get("uniq_final"),
                               "note": "the splice operator ran inside the world; these are its birth statistics"}}
    except Exception as e:                                        # noqa: BLE001
        return {"axis": axis, "ran": False, "error": "%s: %s" % (type(e).__name__, e)}
    return {"axis": axis, "ran": False}
