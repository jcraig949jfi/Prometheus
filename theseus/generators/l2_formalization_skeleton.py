"""L2 — formalization-skeleton generator (REAL, Stage 31).

Generates Lean 4 lemma skeletons grounded in real catalog objects.
For each (template × object), substitutes catalog facts into the
skeleton's holes and emits the resulting skeleton.

Currently no autoformalization gate exists in-process — these
records are emitted UNVERIFIED for downstream Lean processing.
"""
from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import TheseusRecord, ClaimKind, Verdict
from theseus.generators.base import Generator, GeneratorStatus, GeneratorRole


def _load_catalog(path) -> List[dict]:
    p = str(path)
    if p.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    return data.get("entries", []) if isinstance(data, dict) else data


SKELETON_TEMPLATES = [
    {
        "id": "ec_torsion_size_lemma",
        "domain": "ec",
        "needs": ["label", "torsion"],
        "extractor": lambda o: ((o.get("base") or {}).get("label"), (o.get("rich") or {}).get("torsion")),
        "render": lambda label, t: (
            f"theorem ec_torsion_size_{label.replace('.', '_').replace('-', '_')} :\n"
            f"  ∃ E : EllipticCurve Q, E.label = \"{label}\" ∧ "
            f"Nat.card E.torsionSubgroup = {t} := by\n"
            f"  exact?  -- requires LMFDB lookup tactic"
        ),
        "tactics_hint": ["exact?"],
    },
    {
        "id": "knot_signature_lemma",
        "domain": "knot",
        "needs": ["name", "signature"],
        "extractor": lambda o: (o.get("name"), o.get("signature")),
        "render": lambda name, s: (
            f"theorem knot_signature_{name.replace('_', '_under_')} :\n"
            f"  Knot.signature (Knot.named \"{name}\") = {s} := by\n"
            f"  decide  -- computable invariant"
        ),
        "tactics_hint": ["decide"],
    },
    {
        "id": "ec_rank_at_least_lemma",
        "domain": "ec",
        "needs": ["label", "rank"],
        "extractor": lambda o: ((o.get("base") or {}).get("label"), (o.get("base") or {}).get("rank")),
        "render": lambda label, r: (
            f"theorem ec_rank_at_least_{label.replace('.', '_').replace('-', '_')} :\n"
            f"  ∀ E : EllipticCurve Q, E.label = \"{label}\" → "
            f"E.rank ≥ {r} := by\n"
            f"  intro E hE\n"
            f"  rw [hE]; exact?"
        ),
        "tactics_hint": ["intro", "rw", "exact?"],
    },
    {
        "id": "knot_determinant_lemma",
        "domain": "knot",
        "needs": ["name", "determinant"],
        "extractor": lambda o: (o.get("name"), o.get("determinant")),
        "render": lambda name, d: (
            f"theorem knot_determinant_{name.replace('_', '_under_')} :\n"
            f"  Knot.det (Knot.named \"{name}\") = {d} := by\n"
            f"  decide"
        ),
        "tactics_hint": ["decide"],
    },
]


class L2FormalizationSkeletonGenerator(Generator):
    generator_id = "l2"
    claim_kind = ClaimKind.FORMALIZATION_SKELETON.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    MAX_PER_TEMPLATE = 60

    def __init__(self, batch_id: str) -> None:
        super().__init__(batch_id)
        try:
            self._knots = _load_catalog(KNOTS_DB_PATH)
        except Exception:
            self._knots = []
        try:
            self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        except Exception:
            self._ecs = []
        self._queue: List[Dict[str, Any]] = []
        for tpl in SKELETON_TEMPLATES:
            catalog = self._knots if tpl["domain"] == "knot" else self._ecs
            for obj in catalog[: self.MAX_PER_TEMPLATE]:
                try:
                    vals = tpl["extractor"](obj)
                    if any(v is None for v in vals):
                        continue
                except Exception:
                    continue
                self._queue.append({"template": tpl, "obj": obj, "vals": vals})
        self._cursor = 0

    def description(self) -> str:
        return f"l2: formalization_skeleton (real) — {len(self._queue)} skeletons"

    def next(self) -> Optional[TheseusRecord]:
        if self._cursor >= len(self._queue):
            return None
        item = self._queue[self._cursor]
        self._cursor += 1
        self.attempts += 1
        tpl, obj, vals = item["template"], item["obj"], item["vals"]
        try:
            lean_code = tpl["render"](*vals)
        except Exception:
            return self.next()  # skip and continue
        canonical = f"L2_FORMSKELETON[{tpl['id']}] generated for {vals[0]}"
        record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
        self.emitted.append(record_id)
        return TheseusRecord(
            record_id=record_id,
            generator_id=self.generator_id,
            batch_id=self.batch_id,
            emitted_at=datetime.now(timezone.utc).isoformat(),
            claim_kind=self.claim_kind,
            claim_payload={
                "skeleton_id": tpl["id"],
                "lean_skeleton": lean_code,
                "tactics_hint": tpl["tactics_hint"],
                "catalog_object": vals[0],
                "logical_form": "formalization_skeleton",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
