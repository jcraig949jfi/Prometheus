"""Pipeline-D data loader (W3.3).

Converts schema-conformant records (W3.2 boundary-layer fixture +
W3.1 synthetic env) into a HuggingFace `Dataset` suitable for LoRA
fine-tuning of Qwen2.5-Math-1.5B-Instruct.

Per design doc §3 Pipeline-D framing: training input is a serialized
predicate + minimal corpus context; output is the predicted class
label (foldable to KillVector regression in v1.0). Records are
serialized as a single text field; the trainer (W3.6) treats the
class-label tail as the supervised target via causal-LM next-token
prediction.

Schema sources:
- 17-entry boundary-layer fixture (`pipeline_d/boundary_layer_fixture.py`,
  W3.2) emits the substrate-v2.2-aligned schema. Documented fields:
  poly_coefficients, mahler_measure_dps60, n_irreducible_factors,
  cyclotomic_factor_indices, non_cyclotomic_factor_present,
  catalog_match_type, class, class_post_fold, plus method_spec,
  stability_pass etc. (we extract a minimal serialization subset).
- Synthetic env (`ergon/diagnostic_c/synthetic_env.py`, W3.1) emits
  SyntheticRecord with poly_coefficients + height + nnz_free +
  mahler_proxy + label.

The serializer accepts both shapes via duck-typed field access and
falls back gracefully if a field is missing — the schema is still in
flight (W3.2 not yet landed at scaffold-time) so this loader is built
to consume the documented shape with tolerant defaults.
"""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from datasets import Dataset


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = (
    "Predicate: {coeffs} | Mahler: {mahler} | Factors: {n_factors} | Class: "
)


def _coerce_to_dict(record: Any) -> Dict[str, Any]:
    """Accept dataclass / Mapping / object-with-to_dict / dict."""
    if isinstance(record, Mapping):
        return dict(record)
    if hasattr(record, "to_dict") and callable(record.to_dict):
        return dict(record.to_dict())
    if is_dataclass(record):
        return asdict(record)
    if hasattr(record, "__dict__"):
        return dict(record.__dict__)
    raise TypeError(f"Cannot coerce record of type {type(record).__name__} to dict")


def _format_coeffs(coeffs: Sequence[int] | None) -> str:
    if coeffs is None:
        return "[]"
    # Compact integer list representation, no spaces.
    return "[" + ",".join(str(int(c)) for c in coeffs) + "]"


def _extract_mahler(rec: Dict[str, Any]) -> str:
    """Pick the best available Mahler-style field. Order:
    mahler_measure_dps60 (boundary-layer canonical) >
    mahler_measure_dps30 > mahler_measure_dps100 > mahler_proxy
    (synthetic env) > 0.0.
    """
    for k in ("mahler_measure_dps60", "mahler_measure_dps30",
              "mahler_measure_dps100", "mahler_proxy"):
        v = rec.get(k)
        if v is not None:
            return f"{float(v):.6f}"
    return "0.000000"


def _extract_n_factors(rec: Dict[str, Any]) -> str:
    """Boundary-layer record has n_irreducible_factors; synthetic env
    has nnz_free (number of nonzero free coefficients) which is the
    closest analog. Falls back to 0."""
    for k in ("n_irreducible_factors", "nnz_free"):
        v = rec.get(k)
        if v is not None:
            return str(int(v))
    return "0"


def _extract_label(rec: Dict[str, Any]) -> str:
    """Prefer 2-class fold (class_post_fold), then 4-class (class),
    then synthetic env's binary label. Always returns a string token."""
    for k in ("class_post_fold", "class", "label"):
        v = rec.get(k)
        if v is not None:
            return str(v)
    raise KeyError(
        f"Record has no class / class_post_fold / label field; got keys: "
        f"{sorted(rec.keys())}"
    )


def serialize_record(record: Any) -> Dict[str, str]:
    """Serialize one record into prompt + completion + full text.

    Returns a dict with three keys:
    - "prompt": the prefix the model sees (everything up to and
      including "Class: ")
    - "completion": the gold label string the model should produce
    - "text": prompt + completion (used by SFTTrainer's text field)
    """
    rec = _coerce_to_dict(record)
    coeffs = rec.get("poly_coefficients")
    prompt = PROMPT_TEMPLATE.format(
        coeffs=_format_coeffs(coeffs),
        mahler=_extract_mahler(rec),
        n_factors=_extract_n_factors(rec),
    )
    completion = _extract_label(rec)
    return {
        "prompt": prompt,
        "completion": completion,
        "text": prompt + completion,
    }


# ---------------------------------------------------------------------------
# Dataset construction
# ---------------------------------------------------------------------------


def load_dataset_for_training(
    records: Iterable[Any],
    tokenizer: Any,
    max_seq_length: int = 512,
) -> Dataset:
    """Build a HuggingFace `Dataset` from an iterable of records.

    Each row carries `text` (prompt + completion), `prompt`, `completion`,
    plus tokenized `input_ids` / `attention_mask` truncated to
    `max_seq_length`. The trainer (W3.6) consumes `text` directly via
    `SFTTrainer`; the explicit `input_ids` are convenient for the eval
    harness (W3.5) and for round-trip tests.
    """
    records_list = list(records)
    if not records_list:
        raise ValueError("Cannot build dataset from empty record list")
    rows = [serialize_record(r) for r in records_list]

    def _tokenize(batch: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        enc = tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_seq_length,
            padding=False,
        )
        return enc

    ds = Dataset.from_list(rows)
    ds = ds.map(_tokenize, batched=True, remove_columns=[])
    return ds


def train_eval_split(
    dataset: Dataset,
    eval_fraction: float = 0.2,
    seed: int = 42,
) -> Tuple[Dataset, Dataset]:
    """Reproducible 80/20 split (default). Uses HF Dataset's
    `train_test_split` with fixed seed for determinism."""
    if not 0.0 < eval_fraction < 1.0:
        raise ValueError(f"eval_fraction must be in (0, 1); got {eval_fraction}")
    if len(dataset) < 2:
        raise ValueError(
            f"Need >=2 records to split; got {len(dataset)}. "
            "Use the dataset directly without splitting."
        )
    splits = dataset.train_test_split(test_size=eval_fraction, seed=seed)
    return splits["train"], splits["test"]


# ---------------------------------------------------------------------------
# JSONL loader (for stub / disk-backed P5 NearMissCorpus per joint sprint S1)
# ---------------------------------------------------------------------------


def load_records_from_jsonl(path: str | Path) -> List[Dict[str, Any]]:
    """Read a JSONL file of records. Used when the P5 stub /
    boundary-layer fixture has been emitted to disk."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSONL not found: {p}")
    records: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSON at {p}:{i + 1}: {exc}") from exc
    return records


__all__ = [
    "PROMPT_TEMPLATE",
    "serialize_record",
    "load_dataset_for_training",
    "train_eval_split",
    "load_records_from_jsonl",
]
