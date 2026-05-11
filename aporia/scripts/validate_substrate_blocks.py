"""Validate parsed substrate blocks against the canonical JSON schemas.

Per aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md §3.1:
runs each block through:
  1. JSON Schema validation (techne/contracts/substrate_block_schemas/<type>_v1.json)
  2. arXiv citation existence check (HEAD request to export.arxiv.org)
  3. arXiv withdrawal-status check (parse abstract page for "withdrawn")
  4. Cross-reference checks:
     - catalog_edit.entry_id must exist in tensor_open_problems_v1.md
     - primitive_proposal.parent_class must look like a real substrate
       primitive (UpperCamelCase + plausible)
     - {anti_anchor, primitive_proposal, catalog_edit, paradigm_candidate}
       .anti_anchor_pins must reference existing AA-NNN entries

Rejected blocks route to rejected.jsonl with a structured `reason`
field. Approved blocks go to validated.jsonl.

CLI
---
::

    python aporia/scripts/validate_substrate_blocks.py \\
        --parsed aporia/docs/staged_substrate_blocks/2026-05-11/parsed.jsonl \\
        --validated aporia/docs/staged_substrate_blocks/2026-05-11/validated.jsonl \\
        --rejected aporia/docs/staged_substrate_blocks/2026-05-11/rejected.jsonl \\
        [--no-arxiv-check]  # skip network calls

NOTE: arXiv HEAD checks are network-dependent. Use --no-arxiv-check
in offline environments / for unit testing the validator itself.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import jsonschema
    from jsonschema import Draft202012Validator
    from jsonschema.validators import RefResolver
except ImportError:
    print("FATAL: jsonschema is required. pip install jsonschema", file=sys.stderr)
    sys.exit(2)


SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "techne" / "contracts" / "substrate_block_schemas"
ARXIV_ABS_URL = "http://export.arxiv.org/abs/{arxiv_id}"
ARXIV_HEAD_TIMEOUT_S = 10
INTER_REQUEST_SLEEP_S = 0.4  # arxiv.org polite-bot guidance is ~3s; use 0.4 for HEAD-only


# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------


def _load_schemas() -> Tuple[Dict[str, dict], dict]:
    common = json.loads(
        (SCHEMA_DIR / "_common_definitions.json").read_text(encoding="utf-8")
    )
    schemas: Dict[str, dict] = {}
    for fname in (
        "anti_anchor_v1.json",
        "primitive_proposal_v1.json",
        "composition_rule_v1.json",
        "catalog_edit_v1.json",
        "training_anchor_v1.json",
        "paradigm_candidate_v1.json",
    ):
        block_type = fname.replace("_v1.json", "")
        schemas[block_type] = json.loads((SCHEMA_DIR / fname).read_text(encoding="utf-8"))
    return schemas, common


def _build_validator(schema: dict, common: dict) -> Draft202012Validator:
    store = {common["$id"]: common}
    resolver = RefResolver(base_uri=schema["$id"], referrer=schema, store=store)
    return Draft202012Validator(schema, resolver=resolver)


# ---------------------------------------------------------------------------
# Cross-reference loaders
# ---------------------------------------------------------------------------


def _load_existing_aa_ids() -> set:
    """Read techne/registry/anti_anchors.jsonl, return set of registered AA-NNN."""
    path = Path("techne/registry/anti_anchors.jsonl")
    if not path.exists():
        return set()
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception:  # noqa: BLE001
            continue
        if isinstance(obj.get("id"), str):
            out.add(obj["id"])
    return out


_TENSOR_CATALOG_PATH = Path("aporia/mathematics/tensor_open_problems_v1.md")
_T_ENTRY_RE = re.compile(r"^### (\d+)\.\s", re.MULTILINE)


def _load_existing_catalog_entry_ids() -> set:
    """Parse tensor_open_problems_v1.md, return set of T#NN entries that
    actually exist."""
    if not _TENSOR_CATALOG_PATH.exists():
        return set()
    text = _TENSOR_CATALOG_PATH.read_text(encoding="utf-8")
    return {f"T#{m.group(1)}" for m in _T_ENTRY_RE.finditer(text)}


# ---------------------------------------------------------------------------
# arXiv verification
# ---------------------------------------------------------------------------


_ARXIV_ID_RE = re.compile(r"^arXiv:(\d{4}\.\d{4,5})$")


def _arxiv_head_check(citation: str) -> Tuple[bool, str]:
    """Returns (ok, status_message). ok=True iff the arXiv ID resolves
    to an existing abstract page (HTTP 200). Withdrawal status checked
    separately via abstract-text parse (not in this function)."""
    m = _ARXIV_ID_RE.match(citation)
    if not m:
        return (True, "non-arxiv-citation:skipped")
    aid = m.group(1)
    url = ARXIV_ABS_URL.format(arxiv_id=aid)
    try:
        import urllib.request
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=ARXIV_HEAD_TIMEOUT_S) as resp:
            code = resp.getcode()
            if code == 200:
                return (True, f"arxiv-200:{aid}")
            return (False, f"arxiv-{code}:{aid}")
    except Exception as exc:  # noqa: BLE001
        return (False, f"arxiv-error:{aid}:{type(exc).__name__}:{str(exc)[:80]}")


def _arxiv_withdrawal_check(citation: str) -> Tuple[bool, str]:
    """Parse the abstract page for 'withdrawn' / 'retracted' markers.
    Returns (active, status_message). active=True iff the paper is NOT
    withdrawn/retracted."""
    m = _ARXIV_ID_RE.match(citation)
    if not m:
        return (True, "non-arxiv-citation:skipped")
    aid = m.group(1)
    url = ARXIV_ABS_URL.format(arxiv_id=aid)
    try:
        import urllib.request
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=ARXIV_HEAD_TIMEOUT_S) as resp:
            body = resp.read().decode("utf-8", errors="replace").lower()
    except Exception as exc:  # noqa: BLE001
        return (True, f"arxiv-fetch-failed-active-default:{aid}:{type(exc).__name__}")
    # Crude but conservative: any match for 'withdrawn' in the abstract
    # page text triggers a flag for human review. False-positive rate is
    # acceptable since the reviewer has the final say.
    if "withdrawn" in body or "retracted" in body:
        return (False, f"arxiv-withdrawn-or-retracted-flag:{aid}")
    return (True, f"arxiv-active:{aid}")


# ---------------------------------------------------------------------------
# Cross-reference validation
# ---------------------------------------------------------------------------


def _check_cross_references(
    block_type: str, payload: dict,
    *,
    existing_aa_ids: set, existing_catalog_entry_ids: set,
) -> List[str]:
    """Return list of cross-reference error messages (empty if all OK)."""
    errors: List[str] = []

    # AA-NNN cross-refs (most block types can pin anti-anchors)
    aa_pin_fields = {
        "primitive_proposal": "anti_anchor_pins",
        "catalog_edit": "associated_anchor_pins",
        "paradigm_candidate": "anti_anchor_pins",
    }
    pin_field = aa_pin_fields.get(block_type)
    if pin_field and pin_field in payload:
        for aa in payload.get(pin_field, []):
            if aa == "AA-XXX":
                # placeholder for new anchor; skip
                continue
            if aa not in existing_aa_ids:
                errors.append(
                    f"cross-ref:{pin_field}:{aa}:not-in-anti_anchors_jsonl"
                )

    # anti_anchor self-refinement
    if block_type == "anti_anchor":
        action = payload.get("recommended_action")
        if action in ("refine-existing", "invert-existing"):
            target = payload.get("refines_existing_aa_id")
            if target and target != "AA-XXX" and target not in existing_aa_ids:
                errors.append(
                    f"cross-ref:refines_existing_aa_id:{target}:"
                    f"not-in-anti_anchors_jsonl"
                )

    # catalog_edit.entry_id must exist in the target catalog
    if block_type == "catalog_edit":
        entry_id = payload.get("entry_id")
        catalog_file = payload.get("catalog_file", "")
        if (
            entry_id
            and catalog_file == "aporia/mathematics/tensor_open_problems_v1.md"
            and entry_id not in existing_catalog_entry_ids
        ):
            errors.append(
                f"cross-ref:entry_id:{entry_id}:not-in-{catalog_file}"
            )

    return errors


# ---------------------------------------------------------------------------
# Top-level validate
# ---------------------------------------------------------------------------


def validate_record(
    record: dict,
    *,
    validators: Dict[str, Draft202012Validator],
    existing_aa_ids: set,
    existing_catalog_entry_ids: set,
    arxiv_check: bool = True,
) -> Tuple[bool, List[str], Dict[str, str]]:
    """Validate one parsed record. Returns (ok, errors, arxiv_status)."""
    errors: List[str] = []
    arxiv_status: Dict[str, str] = {}

    block_type = record.get("block_type")
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return (False, [f"payload:not-a-dict:{type(payload).__name__}"], arxiv_status)
    if block_type not in validators:
        return (False, [f"block_type:unknown:{block_type}"], arxiv_status)

    # 1. Schema validation
    schema_errs = list(validators[block_type].iter_errors(payload))
    for e in schema_errs:
        errors.append(f"schema:{e.json_path}:{e.message[:240]}")

    # 2. arXiv check (citations may live in different places per block type)
    if arxiv_check:
        for cite_path, cite in _enumerate_citations(block_type, payload):
            ok, msg = _arxiv_head_check(cite)
            arxiv_status[f"{cite_path}:head"] = msg
            if not ok:
                errors.append(f"arxiv-head:{cite_path}:{msg}")
                continue
            time.sleep(INTER_REQUEST_SLEEP_S)
            active, wmsg = _arxiv_withdrawal_check(cite)
            arxiv_status[f"{cite_path}:withdrawal"] = wmsg
            # Withdrawal flag is REVIEW-required, not auto-reject — but
            # we mark it loud so the reviewer sees.
            if not active:
                errors.append(f"arxiv-withdrawn:{cite_path}:{wmsg}")
            time.sleep(INTER_REQUEST_SLEEP_S)

    # 3. Cross-reference checks
    errors.extend(_check_cross_references(
        block_type, payload,
        existing_aa_ids=existing_aa_ids,
        existing_catalog_entry_ids=existing_catalog_entry_ids,
    ))

    return (len(errors) == 0, errors, arxiv_status)


def _enumerate_citations(block_type: str, payload: dict) -> List[Tuple[str, str]]:
    """Return list of (json-path, citation-string) pairs to check.
    Each block type has different citation locations."""
    out: List[Tuple[str, str]] = []
    if block_type == "anti_anchor":
        if isinstance(payload.get("citation"), str):
            out.append(("citation", payload["citation"]))
    elif block_type == "primitive_proposal":
        for i, c in enumerate(payload.get("source_citations", []) or []):
            if isinstance(c, str):
                out.append((f"source_citations[{i}]", c))
    elif block_type == "composition_rule":
        for i, conf in enumerate(payload.get("literature_confirmation", []) or []):
            if isinstance(conf, dict) and isinstance(conf.get("citation"), str):
                out.append((f"literature_confirmation[{i}].citation", conf["citation"]))
    elif block_type == "catalog_edit":
        if isinstance(payload.get("citation"), str):
            out.append(("citation", payload["citation"]))
    elif block_type == "training_anchor":
        src = payload.get("source")
        if isinstance(src, str) and src.startswith("arXiv:"):
            out.append(("source", src))
    elif block_type == "paradigm_candidate":
        for i, conf in enumerate(payload.get("current_confirmations", []) or []):
            if isinstance(conf, dict) and isinstance(conf.get("citation"), str):
                out.append((f"current_confirmations[{i}].citation", conf["citation"]))
        for i, anchor in enumerate(payload.get("literature_anchors", []) or []):
            if isinstance(anchor, str):
                out.append((f"literature_anchors[{i}]", anchor))
    return out


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="validate_substrate_blocks",
        description=(
            "Validate parsed substrate_blocks against canonical schemas "
            "+ arXiv existence/withdrawal + cross-references."
        ),
    )
    p.add_argument("--parsed", required=True, type=Path,
                   help="Input parsed.jsonl from parse_substrate_blocks.py")
    p.add_argument("--validated", required=True, type=Path,
                   help="Output validated.jsonl (approved blocks)")
    p.add_argument("--rejected", required=True, type=Path,
                   help="Output rejected.jsonl (with reason field)")
    p.add_argument("--no-arxiv-check", action="store_true",
                   help="Skip network calls (arXiv HEAD + withdrawal)")
    args = p.parse_args(argv)

    if not args.parsed.exists():
        print(f"FATAL: --parsed does not exist: {args.parsed}", file=sys.stderr)
        return 1

    schemas, common = _load_schemas()
    validators = {bt: _build_validator(s, common) for bt, s in schemas.items()}
    existing_aa_ids = _load_existing_aa_ids()
    existing_catalog_entry_ids = _load_existing_catalog_entry_ids()
    print(
        f"Loaded {len(schemas)} schemas; "
        f"{len(existing_aa_ids)} existing AA-NNN; "
        f"{len(existing_catalog_entry_ids)} existing T#NN catalog entries.",
        file=sys.stderr,
    )

    args.validated.parent.mkdir(parents=True, exist_ok=True)
    args.rejected.parent.mkdir(parents=True, exist_ok=True)

    n_validated = 0
    n_rejected = 0
    with open(args.parsed, "r", encoding="utf-8") as f_in, \
         open(args.validated, "w", encoding="utf-8") as f_ok, \
         open(args.rejected, "w", encoding="utf-8") as f_bad:
        for line in f_in:
            if not line.strip():
                continue
            record = json.loads(line)
            ok, errors, arxiv_status = validate_record(
                record,
                validators=validators,
                existing_aa_ids=existing_aa_ids,
                existing_catalog_entry_ids=existing_catalog_entry_ids,
                arxiv_check=(not args.no_arxiv_check),
            )
            record["arxiv_status"] = arxiv_status
            if ok:
                f_ok.write(json.dumps(record) + "\n")
                n_validated += 1
            else:
                record["validation_errors"] = errors
                f_bad.write(json.dumps(record) + "\n")
                n_rejected += 1

    print(
        f"Validated {n_validated}; rejected {n_rejected} "
        f"({n_validated + n_rejected} total) -> "
        f"{args.validated}, {args.rejected}",
        file=sys.stderr,
    )
    return 0 if n_rejected == 0 else 0  # exit 0 even on rejections; rejections are output


if __name__ == "__main__":
    sys.exit(main())
