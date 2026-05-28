"""N1 — active-disagreement generator (real, Stage 14).

Emits META-CLAIMS about verifier disagreement:

    On synthetic input S, verifier V1 emits verdict V1(S),
    verifier V2 emits verdict V2(S), and V1(S) ≠ V2(S).

Real implementation (Stage 14): generates a small synthetic
workload of (knot, EC) pairs drawn from real catalogs. For each
pair, computes a parity-equality claim and routes it through TWO
DIFFERENT verifier implementations:

- V1 ("strict_parity"): exact arithmetic equality of (a mod 2) and
  (b mod 2).
- V2 ("threshold_proxy"): the value-proximity proxy that older
  generators use — `abs_diff_le_K` for some K. When values are
  large but share parity, abs_diff_le_K with small K disagrees
  with strict parity.

The generator emits ONE record per pair where the two verifiers
disagree, recording both verdicts.

This is real meta-substrate data: records about substrate
behavior, derivable from real catalog content.

Plan: pivot/techne_5gen_plan_2026-05-27.md
"""
from __future__ import annotations

import gzip
import json
import random
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple

from theseus.config import KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
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


# Verifier implementations
# ------------------------

def verifier_strict_parity(a: int, b: int) -> str:
    """Strict modular equality: same parity → SHADOW_CATALOG, else REJECTED."""
    if a % 2 == b % 2:
        return "SHADOW_CATALOG"
    return "REJECTED"


def verifier_threshold_proxy(a: int, b: int, K: int = 3) -> str:
    """Threshold proxy: |a-b| ≤ K → SHADOW_CATALOG, else REJECTED.

    This is the 'F4_FRONT' style verifier used by f4_frontier_pursuit
    when it emits abs_diff_le_K claims. For large-magnitude values that
    share parity, this verifier disagrees with strict parity.
    """
    if abs(a - b) <= K:
        return "SHADOW_CATALOG"
    return "REJECTED"


def verifier_modular_3(a: int, b: int) -> str:
    """A third verifier: mod-3 equivalence.

    Used to find pairs where mod-2 and mod-3 verdicts disagree, which
    reveals where a generator's choice of modulus matters.
    """
    if a % 3 == b % 3:
        return "SHADOW_CATALOG"
    return "REJECTED"


VERIFIER_PAIRS: List[Tuple[str, callable, str, callable, str]] = [
    (
        "exact_parity_vs_threshold_K3",
        verifier_strict_parity,
        "exact_parity",
        lambda a, b: verifier_threshold_proxy(a, b, K=3),
        "abs_diff_le_3",
    ),
    (
        "exact_parity_vs_threshold_K10",
        verifier_strict_parity,
        "exact_parity",
        lambda a, b: verifier_threshold_proxy(a, b, K=10),
        "abs_diff_le_10",
    ),
    (
        "exact_parity_vs_mod_3",
        verifier_strict_parity,
        "exact_parity",
        verifier_modular_3,
        "mod_3_equivalence",
    ),
]


class N1ActiveDisagreementGenerator(Generator):
    generator_id = "n1"
    claim_kind = ClaimKind.VERIFIER_DISAGREEMENT.value
    status = GeneratorStatus.ACTIVE
    role = GeneratorRole.DISCOVERY

    # Cap synthetic workload to bound runtime while still producing
    # enough disagreements to be useful.
    MAX_PAIRS_TESTED = 600

    def __init__(self, batch_id: str, seed: int = 1337) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        try:
            self._knots = _load_catalog(KNOTS_DB_PATH)
        except Exception:
            self._knots = []
        try:
            self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        except Exception:
            self._ecs = []
        self._pending_disagreements: List[Dict[str, Any]] = []
        self._cursor = 0
        self._workload_built = False

    def description(self) -> str:
        return (
            f"n1: active-disagreement (real) — replays synthetic "
            f"(knot, EC) workload through {len(VERIFIER_PAIRS)} verifier "
            f"pairs; emits when V1 ≠ V2"
        )

    def _build_workload(self) -> None:
        """One-shot: sample N (knot, EC) pairs, run both verifiers,
        accumulate disagreements."""
        self._workload_built = True
        if not self._knots or not self._ecs:
            return

        # Build candidate value pairs from real catalog entries.
        knot_values: List[Tuple[str, str, int]] = []
        for k in self._knots:
            name = k.get("name", "?")
            for attr in ("determinant", "signature", "three_genus",
                         "crossing_number"):
                v = k.get(attr)
                if isinstance(v, int):
                    knot_values.append((f"knot:{name}.{attr}", attr, v))

        ec_values: List[Tuple[str, str, int]] = []
        for ec in self._ecs:
            base = ec.get("base") or {}
            rich = ec.get("rich") or {}
            label = base.get("label") or base.get("cremona_label") or "?"
            for attr, src in (
                ("conductor", base), ("rank", base),
                ("torsion", rich), ("tamagawa_product", rich),
            ):
                v = src.get(attr)
                if isinstance(v, int):
                    ec_values.append((f"ec:{label}.{attr}", attr, v))

        if not knot_values or not ec_values:
            return

        # Sample MAX_PAIRS_TESTED random pairs and test each through
        # every verifier pair.
        seen: set = set()
        for _ in range(self.MAX_PAIRS_TESTED):
            k_label, k_attr, k_val = self._rng.choice(knot_values)
            e_label, e_attr, e_val = self._rng.choice(ec_values)
            pair_key = (k_label, e_label)
            if pair_key in seen:
                continue
            seen.add(pair_key)

            for pair_id, v1_fn, v1_name, v2_fn, v2_name in VERIFIER_PAIRS:
                try:
                    v1 = v1_fn(k_val, e_val)
                    v2 = v2_fn(k_val, e_val)
                except Exception:
                    continue
                if v1 == v2:
                    continue
                # Disagreement found — queue for emission.
                self._pending_disagreements.append({
                    "pair_id": pair_id,
                    "verifier_a": v1_name,
                    "verdict_a": v1,
                    "verifier_b": v2_name,
                    "verdict_b": v2,
                    "subject_left_label": k_label,
                    "subject_left_value": k_val,
                    "subject_right_label": e_label,
                    "subject_right_value": e_val,
                    "subject_record_hash": self._subject_hash(
                        k_label, e_label, k_val, e_val
                    ),
                })

    @staticmethod
    def _subject_hash(k_label: str, e_label: str, k_val: int, e_val: int) -> str:
        import hashlib
        h = hashlib.sha256()
        h.update(f"{k_label}|{e_label}|{k_val}|{e_val}".encode("utf-8"))
        return h.hexdigest()[:16]

    def next(self) -> Optional[TheseusRecord]:
        if not self._workload_built:
            self._build_workload()
        if self._cursor >= len(self._pending_disagreements):
            return None
        d = self._pending_disagreements[self._cursor]
        self._cursor += 1
        self.attempts += 1

        canonical = (
            f"N1_DISAGREE[{d['pair_id']}] "
            f"{d['verifier_a']}={d['verdict_a']} vs "
            f"{d['verifier_b']}={d['verdict_b']} on "
            f"<{d['subject_left_label']}={d['subject_left_value']} | "
            f"{d['subject_right_label']}={d['subject_right_value']}>"
        )
        record_id = TheseusRecord.compute_record_id(canonical, self.generator_id)
        self.emitted.append(record_id)

        return TheseusRecord(
            record_id=record_id,
            generator_id=self.generator_id,
            batch_id=self.batch_id,
            emitted_at=datetime.now(timezone.utc).isoformat(),
            claim_kind=self.claim_kind,
            claim_payload={
                "pair_id": d["pair_id"],
                "verifier_a": d["verifier_a"],
                "verdict_a": d["verdict_a"],
                "verifier_b": d["verifier_b"],
                "verdict_b": d["verdict_b"],
                "subject_left_label": d["subject_left_label"],
                "subject_left_value": d["subject_left_value"],
                "subject_right_label": d["subject_right_label"],
                "subject_right_value": d["subject_right_value"],
                "subject_record_hash": d["subject_record_hash"],
                "disagreement_axis": d["pair_id"],
                "logical_form": "verifier_disagreement_meta_claim",
            },
            canonical_claim_text=canonical,
            verdict=Verdict.UNVERIFIED.value,
        )
