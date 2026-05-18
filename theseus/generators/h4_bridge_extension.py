"""H4 — bridge-extension generator (multi-invariant categorical test).

Given a SHADOW_CATALOG parent claim `i(knot:K) RELATION j(ec:E)`,
proposes 3 NEW ec_invariants (not the parent's j) and tests whether
the same relation holds with the new invariant: `i(knot:K) RELATION
new_j(ec:E)` for each.

If multiple extensions hold → the bridge has CATEGORICAL STRUCTURE
(it's not a coincidence on a single invariant pair). If only the
parent's pair held → the bridge is isolated / coincidental.

Distinguished from C3 (single-slide retest): H4 emits a SINGLE record
that summarizes 3 simultaneous extension tests. This is the
multi-arrow categorical reasoning pattern — a record's verdict
captures bridge connectivity rather than per-arrow truth.

Verdict mapping:
- SHADOW_CATALOG if ≥2 of 3 extensions hold (bridge has structure)
- INCONCLUSIVE if exactly 1 extension holds
- REJECTED if 0 extensions hold (parent was isolated)
"""
from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import List, Optional

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
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
    _evaluate_relation,
    EC_INTEGER_INVARIANTS,
)


N_EXTENSIONS = 3


class H4BridgeExtensionGenerator(Generator):
    generator_id = "h4"
    claim_kind = ClaimKind.BRIDGE_EXTENSION.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 220,
        parents: Optional[List[TheseusRecord]] = None,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._parents: List[TheseusRecord] = list(parents) if parents else []
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":h4seed", seed=seed + 1100
        )

    def description(self) -> str:
        return (
            f"h4: bridge-extension multi-invariant test "
            f"({N_EXTENSIONS} new ec_invariants per parent)"
        )

    def add_parent(self, record: TheseusRecord) -> None:
        if record.verdict != Verdict.SHADOW_CATALOG.value:
            return
        p = record.claim_payload
        needed = ("relation", "object_a", "object_b",
                  "value_a", "value_b", "invariant_a", "invariant_b")
        if all(k in p for k in needed):
            self._parents.append(record)

    def _bootstrap_parent(self) -> Optional[TheseusRecord]:
        for _ in range(30):
            r = self._seed_gen.next()
            if r is None:
                return None
            if r.verdict == Verdict.SHADOW_CATALOG.value:
                return r
        return None

    def _find_ec(self, label: str):
        return next(
            (e for e in self._ecs if e.get("base", {}).get("label") == label),
            None,
        )

    def next(self) -> Optional[TheseusRecord]:
        for _ in range(20):
            if self._parents:
                parent = self._rng.choice(self._parents)
            else:
                parent = self._bootstrap_parent()
                if parent is None:
                    return None

            p = parent.claim_payload
            ec_obj = self._find_ec(p["object_b"])
            if ec_obj is None:
                self.attempts += 1
                continue

            # Pick N_EXTENSIONS new ec_invariants different from parent's
            candidates = [i for i in EC_INTEGER_INVARIANTS if i != p["invariant_b"]]
            if len(candidates) < N_EXTENSIONS:
                self.attempts += 1
                continue
            new_invs = self._rng.sample(candidates, N_EXTENSIONS)

            extensions: List[dict] = []
            for new_inv in new_invs:
                new_b = _get_int(ec_obj, new_inv)
                if new_b is None:
                    extensions.append({
                        "ec_invariant": new_inv,
                        "value": None,
                        "holds": None,
                    })
                    continue
                holds = _evaluate_relation(p["value_a"], new_b, p["relation"])
                extensions.append({
                    "ec_invariant": new_inv,
                    "value": new_b,
                    "holds": holds,
                })

            valid_extensions = [
                e for e in extensions if e["holds"] is not None
            ]
            if not valid_extensions:
                self.attempts += 1
                continue

            n_holding = sum(1 for e in valid_extensions if e["holds"])

            if n_holding >= 2:
                verdict = Verdict.SHADOW_CATALOG.value
                kill_pattern = None
            elif n_holding == 1:
                verdict = Verdict.INCONCLUSIVE.value
                kill_pattern = None
            else:
                verdict = Verdict.REJECTED.value
                kill_pattern = "h4_bridge_isolated_no_extensions_hold"

            ext_summary = ", ".join(
                f"{e['ec_invariant']}={'✓' if e['holds'] else '✗'}"
                for e in valid_extensions
            )
            canonical = (
                f"H4_BRIDGE[parent={parent.record_id[:8]}] "
                f"{p['invariant_a']}(knot:{p['object_a']}) {p['relation']} "
                f"?(ec:{p['object_b']}) | parent_{p['invariant_b']}=✓ + "
                f"{ext_summary} | extensions_hold={n_holding}/{len(valid_extensions)}"
            )
            payload = {
                "parent_record_id": parent.record_id,
                "relation": p["relation"],
                "knot_invariant": p["invariant_a"],
                "knot_object": p["object_a"],
                "knot_value": p["value_a"],
                "ec_object": p["object_b"],
                "parent_ec_invariant": p["invariant_b"],
                "parent_ec_value": p["value_b"],
                "extensions": extensions,
                "n_holding": n_holding,
                "n_tested": len(valid_extensions),
            }
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
                parent_record_id=parent.record_id,
                method="exact",
                convergence_status="exact",
                extras={"role": "multi_arrow_bridge_connectivity"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
