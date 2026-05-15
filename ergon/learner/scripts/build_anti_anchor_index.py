"""Build Ergon's registry-aware anti_anchor index.

Reads `techne/registry/anti_anchors.jsonl` and emits an index at
`ergon/learner/corpus/anti_anchor_index/index.json` plus a manifest.

This is the Phase 0 minimum-viable "registry-aware corpus tagging
pipeline" per `T-2026-05-15-aporia-to-ergon-track2-unblocked-techne-
registered-aa014-aa015-aa016` (Track 2 unblocked). The index is the
input to a future Phase 1 tagging step that cross-references LearnerRecord
sidecars with applicable anti_anchors. That tagging step is on
`ergon/BACKLOG.md` as BL-E-NNN.

Today the script reads 16 registered anti_anchors (AA-001..AA-016) and
emits a single index plus per-AA detail files. No LearnerRecord mutation,
no decoy injection — per spec §1.4, decoy injection is corpus-assembly
time, not ingest time.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


_INDEX_SCHEMA_VERSION = "0.1.0"
_DEFAULT_REGISTRY_PATH = Path("techne/registry/anti_anchors.jsonl")
_DEFAULT_OUTPUT_DIR = Path("ergon/learner/corpus/anti_anchor_index")

_PROJECTED_FIELDS = (
    "id", "name", "false_form", "true_form", "citation",
    "verified_against_primary", "last_verified", "verification_source",
    "source_report",
)


def _project_entry(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Project registry entry to the fields the corpus consumer needs."""
    return {k: raw.get(k) for k in _PROJECTED_FIELDS}


def _read_registry(path: Path) -> List[Dict[str, Any]]:
    """Read all anti_anchor entries from the registry JSONL."""
    entries: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(
                    f"WARN: registry line {line_no} JSON parse failed: {e}",
                    file=sys.stderr,
                )
                continue
    return entries


def build_index(
    registry_path: Path,
    output_dir: Path,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Build the index. Returns a manifest dict.

    Idempotent on inputs: same registry contents → same output bytes.
    """
    if not registry_path.exists():
        raise FileNotFoundError(
            f"anti_anchor registry not found at {registry_path}",
        )

    entries = _read_registry(registry_path)
    if not entries:
        raise ValueError(
            f"registry at {registry_path} parsed to zero entries",
        )

    projected = [_project_entry(e) for e in entries]
    projected.sort(key=lambda d: d["id"])  # deterministic ordering by AA-ID

    ids_seen = set()
    duplicates: List[str] = []
    for p in projected:
        if p["id"] in ids_seen:
            duplicates.append(p["id"])
        ids_seen.add(p["id"])

    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / "index.json"
    manifest_path = output_dir / "manifest.json"
    details_dir = output_dir / "details"
    details_dir.mkdir(exist_ok=True)

    if index_path.exists() and not overwrite:
        raise FileExistsError(
            f"index already exists at {index_path}; pass --overwrite to "
            f"replace",
        )

    # Single-file index keyed by AA-ID.
    index = {
        "_schema_version": _INDEX_SCHEMA_VERSION,
        "registry_source": str(registry_path).replace("\\", "/"),
        "registry_entry_count": len(projected),
        "entries": {p["id"]: p for p in projected},
    }
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, sort_keys=True, ensure_ascii=False)

    # Per-AA detail files for downstream consumers that want one-file-
    # per-AA lookup (matches the staged_substrate_blocks/<date>/<type>.jsonl
    # convention).
    for p in projected:
        detail_path = details_dir / f"{p['id']}.json"
        with open(detail_path, "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2, sort_keys=True, ensure_ascii=False)

    manifest = {
        "_schema_version": _INDEX_SCHEMA_VERSION,
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "registry_source": str(registry_path).replace("\\", "/"),
        "registry_entry_count": len(projected),
        "registry_entry_ids": sorted(ids_seen),
        "duplicates_in_registry": sorted(duplicates),
        "output_dir": str(output_dir).replace("\\", "/"),
        "index_path": str(index_path).replace("\\", "/"),
        "details_dir": str(details_dir).replace("\\", "/"),
        "phase_0_scope_note": (
            "Index-only Phase 0 deliverable. Downstream tagging step "
            "(apply index to LearnerRecord sidecars; emit anti_anchor "
            "applicability per record) is on ergon/BACKLOG.md (Phase 1)."
        ),
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True, ensure_ascii=False)

    return manifest


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build Ergon's anti_anchor index from techne/registry/"
            "anti_anchors.jsonl. Index input for the Phase 1 tagging step."
        ),
    )
    parser.add_argument(
        "--registry", type=Path, default=_DEFAULT_REGISTRY_PATH,
        help="Path to anti_anchors registry JSONL.",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=_DEFAULT_OUTPUT_DIR,
        help="Destination directory for index + details.",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing index files.",
    )
    args = parser.parse_args(argv)

    try:
        manifest = build_index(
            args.registry, args.output_dir, args.overwrite,
        )
    except (FileNotFoundError, FileExistsError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print(f"Built index: {manifest['index_path']}")
    print(f"Registry entries indexed: {manifest['registry_entry_count']}")
    print(f"AA-IDs: {', '.join(manifest['registry_entry_ids'])}")
    if manifest["duplicates_in_registry"]:
        print(
            f"WARN: duplicates in registry: "
            f"{manifest['duplicates_in_registry']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
