"""Shared plumbing for the six adaptations (directive Phases 4-6).

An Adaptation declares a translation manifest and a preregistration; the harness FREEZES the prereg (canonical JSON
+ sha256) and writes it BEFORE any result exists, runs the adaptation natively in BEE, replays every receipts file
it produced (divergences are data), and hands the observed result to the adaptation's own comparison. A repair is a
new descendant adaptation id, never an edit of a frozen prereg.

Phase-6 comparison verdicts (one per adaptation, plus per-signal detail):
  PHENOMENON_PRESERVED  the source phenomenon appears in BEE with the same sign/shape
  PHENOMENON_CHANGED    it appears but differs in magnitude/shape
  PHENOMENON_INVERTED   it appears with the opposite sign
  PHENOMENON_ABSENT     it does not appear where the source reported it
  NEW_PHENOMENON        BEE exposes something the source did not report
  NOT_COMPARABLE        the source outcome and the BEE outcome are not on the same axis
  NOT_REPRESENTABLE     the source question could not be posed in BEE at all
  INSTRUMENT_FAILURE    the BEE run failed as an instrument (invalid receipts, control not MET)
The comparison also SEPARATES five difference kinds: scientific / representational / executor / resource / measurement.
"""
from __future__ import annotations

import pathlib
from typing import Callable, Dict, List, Optional

from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.ir import Experiment
from prometheus.toolbox.backends.local import execute, lower, replay_file
from prometheus.toolbox import search as SR
from prometheus.atlas_bee.freeze import freeze, verify
from prometheus.atlas_bee.manifest import Manifest

VERDICTS = ("PHENOMENON_PRESERVED", "PHENOMENON_CHANGED", "PHENOMENON_INVERTED", "PHENOMENON_ABSENT",
            "NEW_PHENOMENON", "NOT_COMPARABLE", "NOT_REPRESENTABLE", "INSTRUMENT_FAILURE")
DIFF_KINDS = ("scientific", "representational", "executor", "resource", "measurement")

PACKET = pathlib.Path(__file__).resolve().parents[2] / "roles" / "Bellerophon" / "atlas_bee"


class Adaptation:
    """Base class. A concrete adaptation sets id/source and implements manifest(), prereg_body() and run()."""
    id: str = ""
    source: Dict = {}

    def manifest(self) -> Manifest:
        raise NotImplementedError

    def prereg_body(self) -> Dict:
        """The design-only fields: question, world, organisms, initial_state, interventions, objective,
        observations, controls, seeds, budgets, stopping_rules, invariants, decision_criteria. NO results."""
        raise NotImplementedError

    def run(self, workdir: pathlib.Path, reg) -> Dict:
        """Execute natively in BEE. Return {'observed': {...}, 'receipt_files': [paths], 'notes': [...]}. """
        raise NotImplementedError

    def compare(self, observed: Dict) -> Dict:
        """Return {'verdict': one of VERDICTS, 'signals': [{name, verdict, ...}], 'differences': {kind: [...]},
        'new_phenomena': [...], 'summary': str}."""
        raise NotImplementedError

    # ---- harness services -------------------------------------------------------------------------------------
    def prereg(self) -> Dict:
        m = self.manifest()
        body = dict(self.prereg_body())
        body["manifest"] = m.to_dict()
        body["adaptation_id"] = self.id
        body["source_experiment"] = self.source.get("atlas_key")
        body["source_disposition"] = self.source.get("disposition")
        return body

    def freeze_record(self) -> Dict:
        return freeze(self.prereg())


def run_experiment(exp: Experiment, path: pathlib.Path, reg=None):
    reg = reg or default_registry()
    return execute(lower(exp, reg).job, path, reg)


def replay_all(receipt_files: List[pathlib.Path], reg=None) -> List[Dict]:
    reg = reg or default_registry()
    out = []
    for p in receipt_files:
        p = pathlib.Path(p)
        rp = p.with_name(p.stem + "_replay.jsonl")
        try:
            r = replay_file(p, rp, reg)
            out.append({"file": p.name, "runs_compared": r.get("runs_compared"), "divergent": r.get("divergent"),
                        "kernel_hash_equal": r.get("kernel_hash_equal"), "status": r.get("status")})
        except ValueError as e:                                  # a file with no replayable SUMMARY is recorded, not hidden
            out.append({"file": p.name, "status": "NO_SUMMARY", "detail": str(e)[:160]})
    return out


def freeze_and_write(ad: Adaptation) -> Dict:
    """Phase 4: write PREREG_<id>.json (the frozen record) into the packet dir, before any run. Returns the record."""
    rec = ad.freeze_record()
    assert verify(rec)
    PACKET.mkdir(parents=True, exist_ok=True)
    import json
    (PACKET / ("PREREG_%s.json" % ad.id)).write_text(json.dumps(rec, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    return rec
