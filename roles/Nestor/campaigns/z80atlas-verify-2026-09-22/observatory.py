"""The observatory: every run written so the campaign can be re-analysed by someone else.

ATLAS INGESTS FAMILIES, NOT RECEIPTS. A FAMILY is one cell of the grammar - one point in
factor space. A RUN is that family at one seed, one tier, one attempt. INDEX.jsonl carries
one flat row per run with the full factor vector, the derived tags, the provenance of the
scheduler's decision and the headline signals, so the index alone supports the campaign
map; the per-run directory carries everything needed to go deeper without re-running.

WRITTEN PER RUN
  CONFIG.json      the frozen cell, seed, tier, grammar hash, parent run, control role
  RESULT.json      the aggregated summary, anticheat flags, signals, timings
  series.jsonl.gz  the telemetry series (one object per sampled epoch)
  lineage.jsonl.gz parent pointers, birth epochs, copy fidelity, reproductive span
  specimens.json.gz organisms kept: the best, the reproducers, and anything the
                   serendipity triggers caught, with genome bytes AND disassembly

DISK IS A RESOURCE, SO IT IS BUDGETED. The observatory tracks its own bytes. Over budget
it degrades in a declared order - lineage tails first, then series resolution - and writes
the degradation into the run's record, because a silently truncated record would be a
measurement artefact disguised as data.
"""
from __future__ import annotations

import gzip
import json
import pathlib
import time

SCHEMA_VERSION = "z80atlas.observatory.v1"


class Observatory:
    def __init__(self, root, disk_budget_gb=60.0):
        self.root = pathlib.Path(root)
        self.runs_dir = self.root / "runs"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "INDEX.jsonl"
        self.specimen_path = self.root / "SPECIMENS.jsonl"
        self.bytes_written = 0
        self.disk_budget = disk_budget_gb * (1 << 30)
        self.degraded = 0
        self._write_manifest()

    # ------------------------------------------------------------------ manifest
    def _write_manifest(self):
        p = self.root / "INGEST_MANIFEST.json"
        if p.exists():
            return
        man = {
            "schema_version": SCHEMA_VERSION,
            "family": "cell_id: sha256 prefix of the factor vector. One family = one point in the grammar.",
            "run_id": "<cell_id>-s<seed>-t<tier>-a<attempt>",
            "index_row": {
                "run_id": "unique run identifier", "family": "cell_id",
                "cell": "the full factor vector (one key per grammar factor)",
                "derived": "computed tags: endogenous, spontaneity_test, constant_kind, has_task, moat, seeded_instrument",
                "seed": "integer seed", "tier": "S|M|L compute tier",
                "role": "EXPERIMENT | CONTROL | VERIFY | INTERVENTION",
                "control_of": "run_id this run is the matched control of, if any",
                "control_axis": "the single factor flipped to make this control",
                "parent_run": "run_id this run was promoted from, if any",
                "reason": "why the scheduler allocated this run",
                "stage": "EARLY | MIDDLE | LATE",
                "signals": "mechanical promotion signals (see scheduler.SIGNALS)",
                "interest": "scalar the producer was updated with",
                "flags": "anticheat flags, with severity",
                "voided": "true if a critical flag means this run cannot support a reproduction claim",
                "summary": "headline aggregates",
                "paths": "relative paths to the per-run artefacts",
                "wall_s": "seconds of wall clock",
            },
            "note": "Rows are append-only. A run is never rewritten; a rerun is a new run_id with parent_run set.",
        }
        p.write_text(json.dumps(man, indent=1), encoding="ascii")

    # ------------------------------------------------------------------ writing
    def _gz(self, path, rows):
        data = ("\n".join(json.dumps(r, ensure_ascii=True, default=str) for r in rows)).encode()
        with gzip.open(path, "wb", compresslevel=6) as fh:
            fh.write(data)
        self.bytes_written += path.stat().st_size
        return path.stat().st_size

    def over_budget(self):
        return self.bytes_written >= self.disk_budget

    def write_run(self, run_id, family, config, result, series, lineage, specimens):
        d = self.runs_dir / family / run_id
        d.mkdir(parents=True, exist_ok=True)
        degrade = self.over_budget()
        # P-1. Degradation must never silently invalidate a causal ancestry claim. A run
        # that declares lineage_complete keeps its full lineage even under disk pressure;
        # if it is thinned anyway the flag is cleared, so the adjudicator sees an
        # incomplete record rather than a complete-looking truncated one.
        keep_lineage = bool(result.get("lineage_complete"))
        if degrade:
            self.degraded += 1
            if not keep_lineage:
                lineage = lineage[-50:]
            series = series[::4] if len(series) > 24 else series
            specimens = specimens[:2]
            result = dict(result)
            result["observatory_degraded"] = "disk budget reached: lineage tail and series thinned"
        (d / "CONFIG.json").write_text(json.dumps(config, indent=1, ensure_ascii=True), encoding="ascii")
        (d / "RESULT.json").write_text(json.dumps(result, indent=1, ensure_ascii=True, default=str), encoding="ascii")
        self.bytes_written += (d / "CONFIG.json").stat().st_size + (d / "RESULT.json").stat().st_size
        if series:
            self._gz(d / "series.jsonl.gz", series)
        if lineage:
            # Records are already tagged dicts: {"kind": "birth"|"migration", ...}.
            self._gz(d / "lineage.jsonl.gz", list(lineage))
        if specimens:
            self._gz(d / "specimens.json.gz", specimens)
        return {"dir": str(d.relative_to(self.root)), "degraded": degrade}

    def append_index(self, row):
        with self.index_path.open("a", encoding="ascii") as fh:
            fh.write(json.dumps(row, ensure_ascii=True, default=str) + "\n")

    def append_specimen(self, row):
        """Serendipity capture: an organism preserved because something changed sharply,
        not because it won. Weird failures are kept on exactly the same terms."""
        row = dict(row)
        row["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with self.specimen_path.open("a", encoding="ascii") as fh:
            fh.write(json.dumps(row, ensure_ascii=True, default=str) + "\n")

    def stats(self):
        return {"bytes_written": self.bytes_written,
                "gb_written": round(self.bytes_written / (1 << 30), 3),
                "disk_budget_gb": round(self.disk_budget / (1 << 30), 1),
                "degraded_runs": self.degraded}


# ---------------------------------------------------------------- serendipity triggers
# Each trigger is a named comparison against the run's own earlier telemetry or against
# the campaign's running medians. They archive; they never score.
TRIGGERS = (
    "exec_length_jump", "write_topology_shift", "self_overwrite_onset", "copy_direction_flip",
    "conditional_halting", "interaction_asymmetry", "mutation_sensitivity_shift",
    "reproductive_compression", "spatial_expansion", "migration_behaviour",
    "task_repro_overlap", "phenotype_diversity_jump", "lineage_lifetime_jump",
    "periodicity", "persistent_internal_state", "cross_environment_behaviour",
)


def serendipity(series, summary):
    """Which triggers fired for this run. Pure function of the record."""
    fired = []
    if len(series) < 4:
        return fired
    a, b = series[:max(2, len(series) // 4)], series[-max(2, len(series) // 4):]

    def m(rows, k):
        vals = [r.get(k) for r in rows if isinstance(r.get(k), (int, float))]
        return sum(vals) / len(vals) if vals else None

    def jump(k, rel=0.5, absolute=None):
        x, y = m(a, k), m(b, k)
        if x is None or y is None:
            return None
        if absolute is not None and abs(y - x) >= absolute:
            return {"from": round(x, 4), "to": round(y, 4)}
        if x > 0 and abs(y - x) / max(x, 1e-9) >= rel:
            return {"from": round(x, 4), "to": round(y, 4)}
        return None

    for key, trig in (("len_mean", "exec_length_jump"), ("span_mean", "reproductive_compression"),
                      ("uniq", "phenotype_diversity_jump"), ("age_mean", "lineage_lifetime_jump"),
                      ("dom_share", "write_topology_shift")):
        j = jump(key)
        if j:
            fired.append({"trigger": trig, "metric": key, **j})
    if summary.get("entropy_drop") and summary["entropy_drop"] >= 0.75:
        fired.append({"trigger": "write_topology_shift", "metric": "entropy",
                      "from": summary.get("entropy_initial"), "to": summary.get("entropy_final")})
    if summary.get("replicated"):
        fired.append({"trigger": "self_overwrite_onset", "metric": "first_replicator",
                      "epoch": (summary.get("first_replicator") or {}).get("epoch")})
    if summary.get("crossed"):
        fired.append({"trigger": "task_repro_overlap", "metric": "first_cross",
                      "epoch": (summary.get("first_cross") or {}).get("epoch")})
    if summary.get("migrations", 0) > 0 and summary.get("niche_occupancy"):
        occ = summary["niche_occupancy"]
        if occ and max(occ) > 0 and min(occ) == 0:
            fired.append({"trigger": "migration_behaviour", "metric": "niche_occupancy", "occ": occ})
    if summary.get("reads_at_answer_of_best", -1) == 0 and summary.get("comp_max", 0) > 0.6:
        fired.append({"trigger": "conditional_halting", "metric": "answers_without_reading",
                      "comp_max": summary.get("comp_max")})
    return fired
