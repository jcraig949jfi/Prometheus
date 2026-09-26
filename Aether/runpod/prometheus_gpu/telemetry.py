"""Telemetry: what a run reports about itself while it is running.

One JSON object per line, appended to $PROMETHEUS_TELEMETRY_PATH. The
format is deliberately boring, because the qualities that matter here are
not expressive power:

  APPEND-ONLY, one record per line, flushed. A run that dies mid-flight
  leaves everything up to the last flush readable. A single JSON document
  written at the end leaves NOTHING when the pod is lost, which is
  exactly the case telemetry exists for.

  TWO CLOCKS on every record. `t_utc` answers "when", `t_elapsed_s`
  answers "how far in". Wall clock alone is not enough: the controller
  and the pod keep different clocks, and placing a progress curve against
  a cost curve needs an origin the pod itself agrees with.

  THE MODULE'S OWN VOCABULARY for everything else. The platform reserves
  a handful of key names and imposes nothing further. Aether counts
  site-ticks; another seat counts candidates or evaluations. A platform
  that forced one seat's denominator on every other seat would only be
  measuring its own history.

Reserved keys: kind, t_utc, t_elapsed_s, run_id, seq, units, message,
level. Every other key belongs to the module.

A truncated final line is expected, not corrupt: `read_jsonl` drops an
unparseable LAST line and refuses an unparseable earlier one, because a
bad record in the middle means something worse than a lost tail.
"""

import json
import time

SCHEMA = "prometheus-gpu/telemetry/1"

RESERVED = ("kind", "t_utc", "t_elapsed_s", "run_id", "seq", "units",
            "message", "level")

# `kind` is open, but these have agreed meanings so that generic tooling
# can summarise any module's run without knowing what it computes.
KINDS = {
    "start": "the workload began; may carry the module's plan",
    "progress": "periodic heartbeat with a `units` count so far",
    "event": "something discrete and notable happened",
    "warning": "degraded but continuing",
    "error": "a failure the module chose to report before exiting",
    "end": "the workload finished; carries final `units` and `status`",
}

LEVELS = ("debug", "info", "warning", "error")


class TelemetryError(ValueError):
    """A telemetry record that generic tooling could not trust."""


def _utc(when=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ",
                         time.gmtime(when if when is not None else time.time()))


def record(kind, origin, run_id=None, seq=None, **fields):
    """Build a record. `origin` is the run's monotonic start."""
    rec = {"kind": str(kind),
           "t_utc": _utc(),
           "t_elapsed_s": round(max(0.0, time.monotonic() - origin), 3)}
    if run_id is not None:
        rec["run_id"] = run_id
    if seq is not None:
        rec["seq"] = int(seq)
    for key, value in fields.items():
        rec[key] = value
    validate_record(rec)
    return rec


def validate_record(rec):
    """Raise unless a record carries what generic tooling depends on."""
    if not isinstance(rec, dict):
        raise TelemetryError("a telemetry record must be a JSON object")
    if not rec.get("kind"):
        raise TelemetryError("record needs a `kind`")
    if not isinstance(rec["kind"], str):
        raise TelemetryError("`kind` must be a string")
    if "t_utc" not in rec:
        raise TelemetryError("record needs `t_utc`; a record without a clock "
                             "cannot be placed against the cost curve")
    if "t_elapsed_s" not in rec:
        raise TelemetryError(
            "record needs `t_elapsed_s`; wall clock alone is not enough, "
            "because the pod and the controller keep different clocks")
    if not isinstance(rec["t_elapsed_s"], (int, float)):
        raise TelemetryError("`t_elapsed_s` must be a number")
    if rec["t_elapsed_s"] < 0:
        raise TelemetryError("`t_elapsed_s` must not be negative")
    if "units" in rec and not isinstance(rec["units"], (int, float)):
        raise TelemetryError("`units` must be a number: it is a count")
    if "level" in rec and rec["level"] not in LEVELS:
        raise TelemetryError("`level` must be one of %s" % (LEVELS,))
    if "seq" in rec and not isinstance(rec["seq"], int):
        raise TelemetryError("`seq` must be an integer")
    return True


class Writer(object):
    """Append-only telemetry sink. Flushes every record, on purpose."""

    def __init__(self, path, run_id=None, origin=None):
        self.path = path
        self.run_id = run_id
        self.origin = time.monotonic() if origin is None else origin
        self._seq = 0

    def emit(self, kind, **fields):
        self._seq += 1
        rec = record(kind, self.origin, run_id=self.run_id, seq=self._seq,
                     **fields)
        with open(self.path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
            fh.flush()
        return rec


def read_jsonl(path_or_text, is_text=False):
    """Parse telemetry, tolerating ONE truncated final line.

    A run killed mid-write leaves a partial last line; that is normal and
    the tail is dropped. An unparseable line anywhere EARLIER means
    interleaved or corrupted writes, which is a different and worse
    problem, so it raises instead of being quietly skipped.
    """
    if is_text:
        text = path_or_text
    else:
        with open(path_or_text, "r", encoding="utf-8") as fh:
            text = fh.read()
    lines = [ln for ln in text.split("\n") if ln.strip()]
    out = []
    for index, line in enumerate(lines):
        try:
            out.append(json.loads(line))
        except ValueError:
            if index == len(lines) - 1:
                break          # truncated tail: expected
            raise TelemetryError(
                "telemetry line %d is not valid JSON, and it is not the last "
                "line; a bad record in the middle means interleaved writes"
                % (index + 1,))
    return out


def summarise(records):
    """Reduce any module's telemetry to a shape generic tooling can use."""
    if not records:
        return {"records": 0, "complete": False,
                "note": "no telemetry; the workload may never have started"}
    kinds = {}
    for rec in records:
        key = rec.get("kind", "?")
        kinds[key] = kinds.get(key, 0) + 1
    unit_recs = [r for r in records if isinstance(r.get("units"), (int, float))]
    elapsed = [r["t_elapsed_s"] for r in records
               if isinstance(r.get("t_elapsed_s"), (int, float))]
    ends = [r for r in records if r.get("kind") == "end"]
    summary = {
        "records": len(records),
        "kinds": kinds,
        "first_utc": records[0].get("t_utc"),
        "last_utc": records[-1].get("t_utc"),
        "elapsed_s": round(max(elapsed), 3) if elapsed else None,
        "units_final": unit_recs[-1]["units"] if unit_recs else None,
        "errors": kinds.get("error", 0),
        "warnings": kinds.get("warning", 0),
        # `complete` means the MODULE said it finished. That is not the
        # same as the pod having exited, and not the same as success.
        "complete": bool(ends),
        "module_status": ends[-1].get("status") if ends else None,
    }
    if summary["units_final"] and summary["elapsed_s"]:
        summary["units_per_s"] = round(
            summary["units_final"] / summary["elapsed_s"], 4)
    # The largest gap says where a run stalled; a mean rate hides it.
    if len(elapsed) > 2:
        gaps = [b - a for a, b in zip(elapsed, elapsed[1:])]
        summary["max_gap_s"] = round(max(gaps), 3)
    return summary


def validate_file(path):
    """(records, summary), or raise. Used by `cli validate-telemetry`."""
    records = read_jsonl(path)
    for rec in records:
        validate_record(rec)
    return records, summarise(records)
