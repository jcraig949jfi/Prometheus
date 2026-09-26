"""Reduce an AETH-02 trajectory log to the tables a report quotes.

    python -m Aether.observatory.aeth02_reduce <circuitry.log>
    python Aether/observatory/aeth02_reduce.py <circuitry.log> --json

Every number in `AETH-01/NATIVE_CIRCUITRY_01_2026-09-24.md` comes from
here, run against the committed evidence. A report whose numbers cannot
be regenerated from committed bytes is a report nobody can check, so this
is the reduction, not a scratch script that happened to produce it once.

The log is line-oriented: control lines carry no prefix, telemetry lines
are `AETH02 ` followed by one JSON object. Cadence matters when reading a
sample: bulk and graph metrics ride the 250-tick sample cadence, cycle
metrics the 500-tick graph cadence, compression and the state digest the
5,000-tick deep cadence. A metric absent from a sample was not measured
there, which is not the same as zero.
"""

import argparse
import base64
import io
import json
import struct
import sys
import zlib

PREFIX = "AETH02 "
FIELDS = ("opcode", "arg0", "arg1", "payload", "energy")
TEMPLATE = ("opcode", "arg0", "arg1", "payload")
CLASSES = ("STATE_CHANGING", "SAME_VALUE_UNCONTESTED",
           "SAME_VALUE_CONTESTED_ALTERNATIVE_CHANGE",
           "SAME_VALUE_CONTESTED_NO_ALTERNATIVE_CHANGE")
# Copy-coupled single-bit perturbation probability, mut_numer / 2^32.
MUT_PROB = 429496730 / 2.0 ** 32
WINDOW_COLS = 9
WINDOW_ROW = "<%di" % WINDOW_COLS


def load(path):
    """(records, control_lines). A bad telemetry line is reported, not hidden."""
    records, control, bad = [], [], []
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for number, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if line.startswith(PREFIX):
                try:
                    records.append(json.loads(line[len(PREFIX):]))
                except ValueError:
                    bad.append(number)
            elif line.strip():
                control.append(line)
    if bad:
        raise ValueError("unparseable telemetry on lines %s" % bad[:10])
    return records, control


def by_phase(records, kind="sample"):
    out = {}
    for rec in records:
        if rec.get("kind") == kind:
            out.setdefault(rec["phase"], []).append(rec)
    for value in out.values():
        value.sort(key=lambda s: s["tick"])
    return out


def pooled_classes(sample, fields=FIELDS, key="edge_classes"):
    """Class counts summed over `fields`, or None if not measured here."""
    table = sample.get(key)
    if not table:
        return None
    total = sum(table[f]["edges"] for f in fields)
    counts = {}
    for cls in CLASSES:
        values = [table[f].get(cls) for f in fields]
        counts[cls] = None if any(v is None for v in values) else sum(values)
    return total, counts


def immortal_fraction(samples, field, min_tick=5000):
    """(f, count, mortal_mean): the unbroken share, by least squares.

    If a fraction f of present edges has been continuously present since
    tick 1 (run = T) and the rest turn over with mean run m, then
    run_mean(T) = f*T + (1-f)*m, so the SLOPE of run_mean against T
    estimates f and the intercept gives (1-f)*m. Fitted after the
    transient, because the relation only holds once the cohort size is
    stationary.
    """
    points = [(s["tick"], s["persistence"][field]["run_mean"],
               s["persistence"][field]["edges_present"])
              for s in samples
              if s["tick"] >= min_tick and s.get("persistence")]
    if len(points) < 3:
        return None
    n = len(points)
    sx = sum(t for t, _m, _e in points)
    sy = sum(m for _t, m, _e in points)
    sxx = sum(t * t for t, _m, _e in points)
    sxy = sum(t * m for t, m, _e in points)
    denom = n * sxx - sx * sx
    if not denom:
        return None
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    present = points[-1][2]
    mortal = intercept / (1.0 - slope) if slope < 1.0 else None
    return slope, slope * present, mortal


def redundancy(sample):
    """(p_same, perturbation_share_of_change) over the template fields.

    The classifier scores an edge by its REALISED outcome, so a same-value
    proposal that perturbation flipped is counted as state-changing. With
    q the perturbation probability and p_s the share of landed writes
    proposing an identical value,

        SAME_VALUE = p_s (1 - q)        CHANGING = (1 - p_s) + p_s q

    This is arithmetic on the measured classification plus the known rate,
    not an independent measurement. Its one assumption is that the
    perturbation draw is independent of whether the proposal differed,
    which is true by construction in the kernel.
    """
    pooled = pooled_classes(sample, TEMPLATE)
    if not pooled:
        return None
    total, counts = pooled
    same = sum(counts[c] for c in CLASSES if c != "STATE_CHANGING"
               and counts[c] is not None)
    changing = counts["STATE_CHANGING"]
    if not total or changing is None:
        return None
    p_same = (same / total) / (1.0 - MUT_PROB)
    from_perturbation = p_same * MUT_PROB
    return p_same, from_perturbation / (changing / total)


def window_rows(window):
    """Decode one window's sampled edges into dicts."""
    packed = window["packed"]
    raw = base64.b64decode(packed["b64"])
    try:
        raw = zlib.decompress(raw)
    except zlib.error:
        pass
    size = struct.calcsize(WINDOW_ROW)
    kept = packed["kept"]
    if len(raw) != size * kept:
        raise ValueError("window payload is %d bytes, expected %d for %d rows"
                         % (len(raw), size * kept, kept))
    cols = packed["cols"]
    return [dict(zip(cols, struct.unpack_from(WINDOW_ROW, raw, i * size)))
            for i in range(kept)]


def contest_free_persistence(window, threshold=64):
    """(n_persistent, n_contested_among_them, control_contested_rate).

    The control is every sampled edge in the same window, which is the
    comparison that matters: whether persistence and contest co-occur at
    all, not whether contests are rare in general.
    """
    rows = window_rows(window)
    if not rows:
        return None
    persistent = [r for r in rows if r.get("run", 0) >= threshold]
    contested = sum(1 for r in persistent if r.get("contenders", 0) >= 2)
    base = sum(1 for r in rows if r.get("contenders", 0) >= 2) / float(len(rows))
    return len(persistent), contested, base


def summarise(path):
    records, control = load(path)
    samples = by_phase(records)
    ends = {r["phase"]: r for r in records if r.get("kind") == "phase_end"}
    starts = {r["phase"]: r for r in records if r.get("kind") == "phase_start"}
    windows = [r for r in records if r.get("kind") == "window"]

    out = {"control_lines": control, "phases": {}, "windows": []}
    outdegrees = set()
    for rec in records:
        value = rec.get("partial_function_max_outdegree")
        if value is not None:
            outdegrees.add(value)
    out["max_outdegree_observed"] = sorted(outdegrees)

    for phase, series in sorted(samples.items()):
        last = series[-1]
        pooled = pooled_classes(last)
        entry = {
            "name": starts[phase]["name"] if phase in starts else None,
            "seed": starts[phase]["params"]["seed"] if phase in starts else None,
            "init_digest": (starts[phase]["recipe"]["initial_state_digest"]
                            if phase in starts else None),
            "samples": len(series),
            "last_tick": last["tick"],
            "completed": phase in ends,
            "stationary": {k: last.get(k) for k in
                           ("write_density", "activity_density",
                            "starved_density", "change_rate",
                            "entropy_opcode_bits", "energy_gini",
                            "energy_total", "autocorr_opcode",
                            "autocorr_energy", "edges_total")},
            "classes_pooled": None,
            "persistence": {},
            "unbroken": {},
        }
        if pooled:
            total, counts = pooled
            entry["classes_pooled"] = {
                "edges": total,
                "fractions": {c: (counts[c] / total if counts[c] is not None
                                  else None) for c in CLASSES}}
        for field in FIELDS:
            data = last["persistence"][field]
            entry["persistence"][field] = {
                "edges_present": data["edges_present"],
                "run_max": data["run_max"], "run_mean": data["run_mean"],
                "ge16_fraction": data["run_ge_16"] / data["edges_present"],
                "ge64_fraction": data["run_ge_64"] / data["edges_present"]}
            fit = immortal_fraction(series, field)
            if fit:
                entry["unbroken"][field] = {
                    "fraction": fit[0], "count": fit[1], "turnover_mean": fit[2]}
        red = redundancy(last)
        if red:
            entry["redundant_proposal_fraction"] = red[0]
            entry["perturbation_share_of_change"] = red[1]
        cycles = [s for s in series if s.get("cycle_nodes") is not None]
        if cycles:
            retention = [s["cycle_retention"] for s in cycles
                         if s.get("cycle_retention") is not None]
            entry["cycles"] = {
                "measurements": len(cycles),
                "nodes_last": cycles[-1]["cycle_nodes"],
                "mapped_last": cycles[-1]["mapped_nodes"],
                "share_last": (cycles[-1]["cycle_nodes"]
                               / cycles[-1]["mapped_nodes"]),
                "retention_mean": (sum(retention) / len(retention)
                                   if retention else None),
                "retention_zero_count": sum(1 for r in retention if r == 0)}
        if phase in ends:
            end = ends[phase]
            entry["cost"] = {k: end[k] for k in
                             ("phase_usd", "wall_seconds", "sites_per_sec",
                              "usd_per_1e9_site_ticks")}
            entry["final_digest"] = end["final_state_digest"]
        out["phases"][phase] = entry

    for window in windows:
        if window["tick"] <= 1:
            continue
        result = contest_free_persistence(window)
        if not result:
            continue
        n_pers, contested, base = result
        out["windows"].append(
            {"phase": window["phase"], "tick": window["tick"],
             "label": window["label"], "persistent": n_pers,
             "persistent_contested": contested, "control_contested": base})
    return out


def render(summary):
    lines = ["AETH-02 REDUCTION",
             "  control lines: %s" % "; ".join(summary["control_lines"]),
             "  max out-degree observed: %s" % summary["max_outdegree_observed"]]
    for phase, entry in sorted(summary["phases"].items()):
        lines.append("")
        lines.append("PHASE %d %s  seed=%s  %d samples to tick %d%s"
                     % (phase, entry["name"], entry["seed"], entry["samples"],
                        entry["last_tick"],
                        "" if entry["completed"] else "  TRUNCATED"))
        st = entry["stationary"]
        lines.append("  stationary  write=%.6f active=%.6f starved=%.6f "
                     "change=%.6f" % (st["write_density"],
                                      st["activity_density"],
                                      st["starved_density"], st["change_rate"]))
        lines.append("              H_op=%.4f gini=%.6f ac_op=%.6f ac_E=%.6f"
                     % (st["entropy_opcode_bits"], st["energy_gini"],
                        st["autocorr_opcode"], st["autocorr_energy"]))
        cp = entry["classes_pooled"]
        if cp:
            lines.append("  edges %d  %s" % (
                cp["edges"], "  ".join(
                    "%s=%.4f%%" % (c.replace("SAME_VALUE_", "SV_"),
                                   100.0 * cp["fractions"][c])
                    for c in CLASSES if cp["fractions"][c] is not None)))
        if "redundant_proposal_fraction" in entry:
            lines.append("  redundant proposals %.4f of landed template writes;"
                         " perturbation supplies %.2f%% of all change"
                         % (entry["redundant_proposal_fraction"],
                            100.0 * entry["perturbation_share_of_change"]))
        for field in FIELDS:
            p = entry["persistence"][field]
            u = entry["unbroken"].get(field)
            lines.append("  %-8s present=%7d run_max=%6d mean=%8.2f "
                         "ge64=%6.3f%%%s"
                         % (field, p["edges_present"], p["run_max"],
                            p["run_mean"], 100.0 * p["ge64_fraction"],
                            "" if not u else
                            "  unbroken=%.5f (n=%.0f) turnover_mean=%.1f"
                            % (u["fraction"], u["count"], u["turnover_mean"])))
        if "cycles" in entry:
            c = entry["cycles"]
            lines.append("  cycles %d nodes of %d mapped (%.4f%%); retention "
                         "mean %.4f over %d measurements, zero on %d"
                         % (c["nodes_last"], c["mapped_last"],
                            100.0 * c["share_last"], c["retention_mean"],
                            c["measurements"], c["retention_zero_count"]))
        if "cost" in entry:
            c = entry["cost"]
            lines.append("  cost $%.5f over %.1f s; %.4e site-ticks/s; "
                         "$%.6f per 1e9" % (c["phase_usd"], c["wall_seconds"],
                                            c["sites_per_sec"],
                                            c["usd_per_1e9_site_ticks"]))
    if summary["windows"]:
        lines.append("")
        lines.append("WINDOWS: persistence against contest")
        total_p = total_c = 0
        for w in summary["windows"]:
            total_p += w["persistent"]
            total_c += w["persistent_contested"]
            lines.append("  ph%d t%-6d %-9s n=%3d contested=%d "
                         "control_rate=%.4f"
                         % (w["phase"], w["tick"], w["label"],
                            w["persistent"], w["persistent_contested"],
                            w["control_contested"]))
        lines.append("  pooled: %d of %d persistent edges were contested"
                     % (total_c, total_p))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("log")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    summary = summarise(args.log)
    if args.json:
        json.dump(summary, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        print(render(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
