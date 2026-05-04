"""ergon.learner.promotion_ledger — substrate-symbol promotion log.

Per Iter 7 / Task #65. The Ergon engine produces predicate-discovery events
at substrate-PASS rate ~25% in the OBSTRUCTION corpus. Without a promotion
ledger, these discoveries vanish at trial end.

The ledger is the artifact other agents (Charon, Aporia, Harmonia) use to
see what Ergon has found. It is append-only JSONL with one record per
substrate-PASS event:

  - timestamp_iso (ISO 8601, with TZ)
  - trial_name (the trial module that produced this record)
  - seed (RNG seed)
  - episode (within-trial episode index)
  - genome_content_hash (the genome's deterministic hash)
  - operator_class (which mutation operator produced it)
  - predicate (dict, the genome interpreted as a predicate)
  - lift (predictive lift on the corpus)
  - match_size (how many records matched)
  - kernel_binding_name (which BindEvalKernelV2 binding routed it)
  - is_obstruction_exact / is_secondary_exact / is_obstruction_discriminator /
    is_secondary_discriminator — match-set classification

The ledger is per-trial: each trial run writes its own JSONL. A consumer
(e.g. Charon checking what Ergon has found this week) reads multiple
ledgers and merges by content_hash to dedupe.

Storage discipline: the ledger holds the predicate verbatim (not its
content_hash). This is the substrate-grade payload — readable without
needing the kernel.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class PromotionLedger:
    """Append-only JSONL ledger of substrate-PASS predicate-discovery events."""

    def __init__(self, path: Optional[Path] = None, trial_name: str = "unknown"):
        self.path = Path(path) if path is not None else None
        self.trial_name = trial_name
        self.records: List[Dict[str, Any]] = []
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        seed: int,
        episode: int,
        genome_content_hash: str,
        operator_class: str,
        predicate: Dict[str, Any],
        lift: float,
        match_size: int,
        kernel_binding_name: str,
        is_obstruction_exact: bool = False,
        is_secondary_exact: bool = False,
        is_obstruction_discriminator: bool = False,
        is_secondary_discriminator: bool = False,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Append one substrate-PASS record. Writes to disk if path set."""
        record = {
            "timestamp_iso": datetime.now(timezone.utc).isoformat(),
            "trial_name": self.trial_name,
            "seed": seed,
            "episode": episode,
            "genome_content_hash": genome_content_hash,
            "operator_class": operator_class,
            "predicate": dict(predicate),
            "lift": float(lift),
            "match_size": int(match_size),
            "kernel_binding_name": kernel_binding_name,
            "is_obstruction_exact": bool(is_obstruction_exact),
            "is_secondary_exact": bool(is_secondary_exact),
            "is_obstruction_discriminator": bool(is_obstruction_discriminator),
            "is_secondary_discriminator": bool(is_secondary_discriminator),
        }
        if extra:
            record["extra"] = extra
        self.records.append(record)
        if self.path is not None:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        return record

    def n_records(self) -> int:
        return len(self.records)

    def n_promoted_by_class(self) -> Dict[str, int]:
        """Distinct exact / discriminator / no-match counts."""
        counts = {
            "obstruction_exact": 0,
            "secondary_exact": 0,
            "obstruction_discriminator_only": 0,
            "secondary_discriminator_only": 0,
            "non_planted_substrate_pass": 0,
        }
        for r in self.records:
            if r["is_obstruction_exact"]:
                counts["obstruction_exact"] += 1
            elif r["is_secondary_exact"]:
                counts["secondary_exact"] += 1
            elif r["is_obstruction_discriminator"]:
                counts["obstruction_discriminator_only"] += 1
            elif r["is_secondary_discriminator"]:
                counts["secondary_discriminator_only"] += 1
            else:
                counts["non_planted_substrate_pass"] += 1
        return counts

    def unique_predicates(self) -> List[Dict[str, Any]]:
        """Distinct predicates seen (by content_hash dedupe)."""
        seen: Dict[str, Dict[str, Any]] = {}
        for r in self.records:
            ch = r["genome_content_hash"]
            if ch not in seen:
                seen[ch] = {
                    "content_hash": ch,
                    "predicate": r["predicate"],
                    "first_episode": r["episode"],
                    "first_seed": r["seed"],
                    "operator_class": r["operator_class"],
                    "lift": r["lift"],
                    "match_size": r["match_size"],
                    "n_occurrences": 1,
                }
            else:
                seen[ch]["n_occurrences"] += 1
        return list(seen.values())

    @classmethod
    def load_jsonl(cls, path: Path, trial_name: str = "loaded") -> "PromotionLedger":
        """Load a ledger from JSONL on disk."""
        ledger = cls(path=None, trial_name=trial_name)
        with Path(path).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    ledger.records.append(json.loads(line))
        return ledger
