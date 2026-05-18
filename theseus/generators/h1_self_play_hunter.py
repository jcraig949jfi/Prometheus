"""H1 — self-play proposer-vs-hunter (AlphaZero pattern).

Reads SHADOW_CATALOG survivors from the corpus and tries to find
counter-examples by varying objects. Each emission is either:

  hunter_success=True  → REJECTED — counter-example found; the survivor
                                    was a coincidence, not a relation.
                                    Hunter killed the proposer.
  hunter_success=False → SHADOW_CATALOG — no counter-example found in
                                          N tries; survivor is robust.

Both outcomes are informationally dense. The PAIR (survivor record +
hunter record) is naturally contrastive training data — exactly the
shape Ergon's Learner needs (positive + negative pairs over the same
relation).

Pulls from frontier "self-play" (AlphaZero, Mukhoty et al. NeurIPS 2023):
proposer-hunter games generate training data without external labels
or LLM tokens. Substrate-native by construction.
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from theseus.config import CORPUS_DIR, KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.corpus_reader import CorpusReader
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus
from theseus.generators.a1_catalog_cross_product import (
    A1CatalogCrossProductGenerator,
    _load_catalog,
    _get_int,
    _label,
    _evaluate_relation,
)


DEFAULT_HUNT_BUDGET = 30  # attempts per survivor before declaring robust
DEFAULT_SURVIVOR_BUFFER = 2000


class H1SelfPlayHunterGenerator(Generator):
    generator_id = "h1"
    claim_kind = ClaimKind.KILL_NEIGHBORHOOD.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 20,
        corpus_dir: Optional[Path] = None,
        hunt_budget: int = DEFAULT_HUNT_BUDGET,
        survivor_buffer: int = DEFAULT_SURVIVOR_BUFFER,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._corpus_dir = corpus_dir if corpus_dir is not None else CORPUS_DIR
        self._reader = CorpusReader(self._corpus_dir)
        self._hunt_budget = hunt_budget
        self._survivor_buffer = survivor_buffer
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._survivors: List[TheseusRecord] = []
        self._loaded = False
        # Bootstrap A1 to seed survivors if corpus is empty
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":h1seed", seed=seed + 600
        )

    def description(self) -> str:
        return (
            f"h1: self-play proposer-vs-hunter on corpus survivors "
            f"(hunt_budget={self._hunt_budget}, "
            f"survivor_buffer={self._survivor_buffer})"
        )

    def _load_survivors(self) -> None:
        if self._loaded:
            return
        needed = ("relation", "object_a", "object_b", "value_a",
                  "value_b", "invariant_a", "invariant_b")
        try:
            for r in self._reader.iter_survivors(
                max_records=self._survivor_buffer,
                require_payload_keys=list(needed),
            ):
                self._survivors.append(r)
        except Exception:
            pass
        self._loaded = True

    def _bootstrap_survivor(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            r = self._seed_gen.next()
            if r is None:
                return None
            if r.verdict != Verdict.SHADOW_CATALOG.value:
                continue
            p = r.claim_payload
            if all(
                k in p for k in
                ("relation", "object_a", "object_b", "value_a",
                 "value_b", "invariant_a", "invariant_b")
            ):
                return r
        return None

    def _try_hunt(
        self, survivor: TheseusRecord
    ) -> Optional[dict]:
        """Try to find a counter-example to survivor's claim.

        Returns a dict describing the counter-example, or None if no
        counter-example found in `hunt_budget` attempts.
        """
        p = survivor.claim_payload
        rel = p["relation"]
        for _ in range(self._hunt_budget):
            if self._rng.random() < 0.5:
                new_obj = self._rng.choice(self._knots)
                new_label = _label(new_obj, "knot")
                a_val = _get_int(new_obj, p["invariant_a"])
                b_val = p["value_b"]
                object_a = new_label
                object_b = p["object_b"]
                varied = "a"
            else:
                new_obj = self._rng.choice(self._ecs)
                new_label = _label(new_obj, "ec")
                a_val = p["value_a"]
                b_val = _get_int(new_obj, p["invariant_b"])
                object_a = p["object_a"]
                object_b = new_label
                varied = "b"
            if a_val is None or b_val is None:
                continue
            holds = _evaluate_relation(a_val, b_val, rel)
            if not holds:
                return {
                    "varied_side": varied,
                    "object_a": object_a,
                    "object_b": object_b,
                    "value_a": a_val,
                    "value_b": b_val,
                }
        return None

    def next(self) -> Optional[TheseusRecord]:
        if not self._loaded:
            self._load_survivors()

        for _ in range(15):
            if self._survivors:
                survivor = self._rng.choice(self._survivors)
            else:
                survivor = self._bootstrap_survivor()
                if survivor is None:
                    return None

            p = survivor.claim_payload
            hunt_result = self._try_hunt(survivor)
            self.attempts += 1

            if hunt_result is not None:
                # Hunter found counter-example: survivor was coincidence
                canonical = (
                    f"H1_HUNT_KILL[parent={survivor.record_id[:8]}] "
                    f"survivor: {p['invariant_a']}({p['object_a']})={p['value_a']} "
                    f"{p['relation']} {p['invariant_b']}({p['object_b']})={p['value_b']} "
                    f"counter: vary_{hunt_result['varied_side']} → "
                    f"{p['invariant_a']}({hunt_result['object_a']})={hunt_result['value_a']} "
                    f"NOT-{p['relation']} {p['invariant_b']}({hunt_result['object_b']})={hunt_result['value_b']}"
                )
                payload = {
                    "parent_record_id": survivor.record_id,
                    "parent_relation": p["relation"],
                    "invariant_a": p["invariant_a"],
                    "invariant_b": p["invariant_b"],
                    "parent_object_a": p["object_a"],
                    "parent_object_b": p["object_b"],
                    "parent_value_a": p["value_a"],
                    "parent_value_b": p["value_b"],
                    "hunter_varied_side": hunt_result["varied_side"],
                    "hunter_object_a": hunt_result["object_a"],
                    "hunter_object_b": hunt_result["object_b"],
                    "hunter_value_a": hunt_result["value_a"],
                    "hunter_value_b": hunt_result["value_b"],
                    "hunter_success": True,
                    "hunt_budget": self._hunt_budget,
                }
                verdict = Verdict.REJECTED.value
                kill_pattern = "h1_hunter_found_counterexample"
            else:
                # Hunter exhausted budget: survivor is robust
                canonical = (
                    f"H1_HUNT_ROBUST[parent={survivor.record_id[:8]}] "
                    f"{p['invariant_a']}({p['object_a']})={p['value_a']} "
                    f"{p['relation']} {p['invariant_b']}({p['object_b']})={p['value_b']} "
                    f"survived {self._hunt_budget} object-perturbations"
                )
                payload = {
                    "parent_record_id": survivor.record_id,
                    "parent_relation": p["relation"],
                    "invariant_a": p["invariant_a"],
                    "invariant_b": p["invariant_b"],
                    "parent_object_a": p["object_a"],
                    "parent_object_b": p["object_b"],
                    "parent_value_a": p["value_a"],
                    "parent_value_b": p["value_b"],
                    "hunter_success": False,
                    "hunt_budget": self._hunt_budget,
                }
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None

            record_id = TheseusRecord.compute_record_id(
                canonical_claim_text=canonical,
                generator_id=self.generator_id,
            )
            r = TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload=payload,
                canonical_claim_text=canonical,
                verdict=verdict,
                kill_pattern=kill_pattern,
                parent_record_id=survivor.record_id,
                method="exact",
                convergence_status="exact",
                extras={"role": "self_play_contrastive_pair"},
            )
            self.emitted.append(record_id)
            return r

        return None

    def add_parent(self, record: TheseusRecord) -> None:
        """Accept SHADOW_CATALOG records from same-batch peers."""
        if record.verdict != Verdict.SHADOW_CATALOG.value:
            return
        p = record.claim_payload
        needed = ("relation", "object_a", "object_b", "value_a",
                  "value_b", "invariant_a", "invariant_b")
        if all(k in p for k in needed):
            self._survivors.append(record)
            # Cap buffer growth
            if len(self._survivors) > self._survivor_buffer * 2:
                self._survivors = self._survivors[-self._survivor_buffer:]
