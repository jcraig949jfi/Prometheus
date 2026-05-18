"""D4 — boundary-crossing pair generator.

Reads SHADOW_CATALOG ("PASS") and REJECTED ("KILL") records from the
corpus with the same (relation, invariant_a, invariant_b) signature.
Finds minimum-distance pairs in the (value_a, value_b) space — pairs
that BRACKET the relation boundary.

Each emission is a (PASS, KILL) pair record naming the boundary location:
"PASS at (a=A, b=B) and KILL at (a=A', b=B') with euclidean distance ε."

D4's value: each emission pins the boundary at a specific location with
quantified narrowness. Pairs with very small ε (within 1-2 integer units)
are the substrate's sharpest boundary surfaces. Pairs with larger ε are
weaker boundary information.

Frontier-aligned with active learning at boundaries: instead of sampling
uniformly, target the (PASS, KILL) pairs that minimize ε.
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from theseus.config import CORPUS_DIR
from theseus.emit.corpus_reader import CorpusReader
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.generators.base import Generator, GeneratorStatus
from theseus.generators.a1_catalog_cross_product import (
    A1CatalogCrossProductGenerator,
)


DEFAULT_PAIR_BUFFER = 1000
TIGHT_BOUNDARY_EPS = 2.0  # euclidean distance threshold for "tight" pairs


class D4BoundaryCrossingGenerator(Generator):
    generator_id = "d4"
    claim_kind = ClaimKind.KILL_NEIGHBORHOOD.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 130,
        corpus_dir: Optional[Path] = None,
        buffer_size: int = DEFAULT_PAIR_BUFFER,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._corpus_dir = corpus_dir if corpus_dir is not None else CORPUS_DIR
        self._reader = CorpusReader(self._corpus_dir)
        self._buffer = buffer_size
        # Group records by (relation, invariant_a, invariant_b)
        self._passes: Dict[Tuple[str, str, str], List[TheseusRecord]] = defaultdict(list)
        self._kills: Dict[Tuple[str, str, str], List[TheseusRecord]] = defaultdict(list)
        self._loaded = False
        # Bootstrap A1
        self._seed_gen = A1CatalogCrossProductGenerator(
            batch_id=batch_id + ":d4seed", seed=seed + 1000
        )

    def description(self) -> str:
        return (
            f"d4: PASS/KILL boundary-crossing pairs from corpus "
            f"(group by (relation, inv_a, inv_b); tight if eps ≤ {TIGHT_BOUNDARY_EPS})"
        )

    def _record_signature(self, r: TheseusRecord) -> Optional[Tuple[str, str, str]]:
        p = r.claim_payload
        if not all(k in p for k in ("relation", "invariant_a", "invariant_b")):
            return None
        return (p["relation"], p["invariant_a"], p["invariant_b"])

    def add_parent(self, record: TheseusRecord) -> None:
        """Accept SHADOW_CATALOG or REJECTED A1-shaped records from same batch.

        Requires full A1-shape payload (relation, invariant_a/b, object_a/b,
        value_a/b) so next() can build the boundary record without KeyError.
        D1/H1 records that carry value_a/b but use different object-key
        names (parent_object, etc) are filtered out here.
        """
        sig = self._record_signature(record)
        if sig is None:
            return
        p = record.claim_payload
        needed = ("value_a", "value_b", "object_a", "object_b")
        if not all(k in p for k in needed):
            return
        # Bug fix (Fire #8): touch only the dict we appended to.
        # Previously `for d in (self._passes, self._kills): len(d[sig])`
        # used defaultdict access to create empty lists in the other dict,
        # which then survived the matched_sigs filter and caused
        # IndexError('Cannot choose from an empty sequence') downstream.
        if record.verdict == Verdict.SHADOW_CATALOG.value:
            self._passes[sig].append(record)
            if len(self._passes[sig]) > self._buffer:
                self._passes[sig] = self._passes[sig][-self._buffer:]
        elif record.verdict == Verdict.REJECTED.value:
            self._kills[sig].append(record)
            if len(self._kills[sig]) > self._buffer:
                self._kills[sig] = self._kills[sig][-self._buffer:]

    def _load_corpus(self) -> None:
        if self._loaded:
            return
        needed = ("value_a", "value_b", "object_a", "object_b")
        try:
            for r in self._reader.iter_records():
                sig = self._record_signature(r)
                if sig is None:
                    continue
                p = r.claim_payload
                if not all(k in p for k in needed):
                    continue
                if r.verdict == Verdict.SHADOW_CATALOG.value:
                    self._passes[sig].append(r)
                elif r.verdict == Verdict.REJECTED.value:
                    self._kills[sig].append(r)
                if sum(len(v) for v in self._passes.values()) > self._buffer:
                    break
        except Exception:
            pass
        self._loaded = True

    def _bootstrap(self) -> bool:
        """Run A1 internally to seed at least one PASS+KILL pair in some sig."""
        needed = ("value_a", "value_b", "object_a", "object_b")
        for _ in range(50):
            r = self._seed_gen.next()
            if r is None:
                return False
            sig = self._record_signature(r)
            if sig is None:
                continue
            p = r.claim_payload
            if not all(k in p for k in needed):
                continue
            if r.verdict == Verdict.SHADOW_CATALOG.value:
                self._passes[sig].append(r)
            elif r.verdict == Verdict.REJECTED.value:
                self._kills[sig].append(r)
            # Stop once we have at least one matched signature
            for s in self._passes:
                if self._kills.get(s):
                    return True
        return any(self._kills.get(s) for s in self._passes)

    def next(self) -> Optional[TheseusRecord]:
        if not self._loaded:
            self._load_corpus()
        # Find signatures with both non-empty PASS and KILL lists.
        # (Belt-and-braces: explicit truthy check on both, even though
        # the cap-growth fix should prevent empty lists from existing.)
        matched_sigs = [
            s for s in self._passes
            if self._passes[s] and self._kills.get(s)
        ]
        if not matched_sigs:
            if not self._bootstrap():
                return None
            matched_sigs = [s for s in self._passes if self._kills.get(s)]
            if not matched_sigs:
                return None

        for _ in range(15):
            sig = self._rng.choice(matched_sigs)
            pass_rec = self._rng.choice(self._passes[sig])
            kill_rec = self._rng.choice(self._kills[sig])

            pp = pass_rec.claim_payload
            kp = kill_rec.claim_payload
            dx = float(kp["value_a"]) - float(pp["value_a"])
            dy = float(kp["value_b"]) - float(pp["value_b"])
            eps = math.sqrt(dx * dx + dy * dy)

            tight = eps <= TIGHT_BOUNDARY_EPS
            verdict = (
                Verdict.SHADOW_CATALOG.value if tight
                else Verdict.REJECTED.value
            )
            kill_pattern = (
                None if tight
                else f"d4_loose_boundary_eps{eps:.2f}>{TIGHT_BOUNDARY_EPS}"
            )

            relation, inv_a, inv_b = sig
            canonical = (
                f"D4_BOUND[{relation}, {inv_a}, {inv_b}] "
                f"PASS at ({pp['object_a']}={pp['value_a']}, "
                f"{pp['object_b']}={pp['value_b']}) | "
                f"KILL at ({kp['object_a']}={kp['value_a']}, "
                f"{kp['object_b']}={kp['value_b']}) | "
                f"ε={eps:.2f} | tight={tight}"
            )
            payload = {
                "relation": relation,
                "invariant_a": inv_a,
                "invariant_b": inv_b,
                "pass_record_id": pass_rec.record_id,
                "kill_record_id": kill_rec.record_id,
                "pass_object_a": pp["object_a"],
                "pass_value_a": pp["value_a"],
                "pass_object_b": pp["object_b"],
                "pass_value_b": pp["value_b"],
                "kill_object_a": kp["object_a"],
                "kill_value_a": kp["value_a"],
                "kill_object_b": kp["object_b"],
                "kill_value_b": kp["value_b"],
                "epsilon": eps,
                "tight_boundary": tight,
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
                method="exact",
                convergence_status="exact",
                extras={"role": "boundary_pair_locator"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
