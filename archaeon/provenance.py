"""Archaeological provenance: the record that makes a proposal re-derivable.

Every proposal must answer, from its stored ``source_evidence`` alone:

  * Which PEW/SFE records triggered it?      -> triggering_rows[].anchors
  * Which detector fired?                    -> detector, detector_version
  * What values crossed the threshold?       -> values / thresholds
  * What candidates were considered?         -> candidates_considered[]
  * Why was this one selected?               -> selection{rule, score, terms}
  * Signal-driven or exploration-driven?     -> mode, and source_reason
  * What seed was involved?                  -> exploration.seed + seed_inputs
  * Against WHICH corpus?                    -> corpus{hash, window, source}
  * Under WHICH rules?                       -> config_fingerprint,
                                                thresholds_version

The last two matter as much as the rest. A proposal whose corpus and threshold
set are not pinned cannot be re-derived, only re-guessed.

**No interpretation is stored.** The record says what was measured and what was
crossed. It never says what the pattern means, and the eligibility census is
carried alongside so that "nothing fired" can never be read without "here is
how much of the corpus could have fired at all".
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from . import config as cfg
from .detectors.base import Signal
from .rank import Candidate

PROVENANCE_SCHEMA = "archaeon.provenance.v0"

# Sanity bound: a proposal carrying tens of thousands of rows is unreadable and
# would make the jsonb column the dominant cost of the queue. Truncation is
# RECORDED, never silent, and the corpus hash still pins the full input.
MAX_TRIGGERING_ROWS = 128
MAX_CANDIDATES_RECORDED = 64


def _corpus_block(corpus) -> Dict[str, Any]:
    return {
        "hash": corpus.corpus_hash(),
        "chart": corpus.chart.name,
        "source": corpus.source_ref,
        "window": dict(corpus.window),
        "rows": len(corpus.rows),
        "coordinate_scales": corpus.coord_scales(),
    }


def _rules_block(config: cfg.ArchaeonConfig) -> Dict[str, Any]:
    return {
        "config_fingerprint": config.fingerprint(),
        "thresholds_version": cfg.THRESHOLDS_VERSION,
        "rank_weights": dict(config.rank_weights),
    }


def signal_provenance(*, corpus, config: cfg.ArchaeonConfig,
                      chosen: Candidate,
                      all_candidates: Sequence[Candidate],
                      census: Dict[str, Any]) -> Dict[str, Any]:
    """Provenance for a weak-signal-driven proposal."""
    sig = chosen.primary
    rows = list(sig.evidence_rows)
    truncated = len(rows) > MAX_TRIGGERING_ROWS

    considered = [c.to_json() for c in all_candidates[:MAX_CANDIDATES_RECORDED]]

    return {
        "schema": PROVENANCE_SCHEMA,
        "mode": "weak_signal",
        "corpus": _corpus_block(corpus),
        "rules": _rules_block(config),

        "detector": sig.detector,
        "detector_version": sig.detector_version,
        "intent": sig.intent,
        "co_firing_detectors": chosen.detectors,
        "signal_id": sig.signal_id(),

        # What crossed, and what it had to cross.
        "values_at_threshold": dict(sig.values),
        "thresholds_applied": dict(sig.thresholds),
        "support_n": sig.support_n,
        "regions": list(sig.regions),
        "players": list(sig.players),
        "target_coords_normalized": dict(sig.target_coords),

        # Which fossils triggered it.
        "triggering_rows": rows[:MAX_TRIGGERING_ROWS],
        "triggering_rows_total": len(rows),
        "triggering_rows_truncated": truncated,

        # What else was on the table and why this one won.
        "candidates_considered": considered,
        "candidates_considered_total": len(all_candidates),
        "candidates_truncated": len(all_candidates) > MAX_CANDIDATES_RECORDED,
        "selection": {
            "rule": ("highest score = intent weight + effect term + support "
                     "term; ties broken by (intent rank, detector order, "
                     "signal_id, target_key). Fully deterministic."),
            "score": chosen.score,
            "score_terms": dict(chosen.score_terms),
            "target_key": chosen.target_key,
        },

        # Always carried, so a reader never sees firing without eligibility.
        "eligibility_census": census,

        # The standing disclaimer, stored in the row rather than assumed.
        "authority": ("PROBE TRIGGER ONLY. A detector firing means this region "
                      "may be worth interrogating again. It does not assert "
                      "that any phenomenon exists, and no field of this record "
                      "may be read as a scientific conclusion."),
    }


def exploration_provenance(*, corpus, config: cfg.ArchaeonConfig,
                           selection: Dict[str, Any],
                           census: Dict[str, Any]) -> Dict[str, Any]:
    """Provenance for an exploration-driven proposal."""
    return {
        "schema": PROVENANCE_SCHEMA,
        "mode": "exploration",
        "corpus": _corpus_block(corpus),
        "rules": _rules_block(config),

        "detector": None,
        "intent": "COVERAGE",

        "exploration": dict(selection),
        "seed": selection.get("seed"),
        "seed_inputs": selection.get("seed_inputs"),
        "candidate_set_hash": selection.get("candidate_set_hash"),

        "selection": {
            "rule": ("coverage-biased: never-sampled legal cells preferred, "
                     "else cells at or below the undersampled quantile; one "
                     "chosen by a PRNG seeded from (corpus_hash, utc_day). "
                     "Re-derivable from seed + candidate_set_hash."),
            "pool_kind": selection.get("pool_kind"),
            "candidate_count": selection.get("candidate_count"),
        },

        "eligibility_census": census,

        "authority": ("DELIBERATE EXPLORATION. No detector fired on this "
                      "corpus. That is a reason to sample under-covered space, "
                      "and it is NOT a finding: it does not mean the corpus is "
                      "uninteresting, that a lineage is finished, or that any "
                      "hypothesis has been settled. See the eligibility census "
                      "for how much of the corpus could have fired at all."),
    }
