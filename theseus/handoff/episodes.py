"""Episode composer — stitches related Theseus records into multi-phase
episodes that map onto Ergon's LearnerRecord schema.

Per Ergon's training_anchor_ingestion_spec.md §1.3, `episode_id` /
`episode_phase` are derived during ingestion; Tier-1 maps each anchor 1:1
to a single-phase episode. Fire #31 ships the next tier: walk the corpus,
identify parent→children chains, and emit records with proper episode
phase metadata so a single "claim" + its "falsify" / "promote" follow-ups
share an episode.

Phase mapping (generator_id → episode_phase):
  - A1, A2, A3, A4, A5, F2, F3, F4    → "claim"    (root cross-catalog claims)
  - B5, C1, C2, C3, C4, C5            → "claim"    (mutated/derived claims with own substrate verdict)
  - E1, E3                            → "claim"    (literature-mined claims)
  - D1, D2, D3, D4, H1, H2            → "falsify"  (kill-neighborhood / hunt / triangulation)
  - H4                                → "promote"  (bridge extension — categorical confirmation)
  - B1, B2, B3, B4, G4, G5            → "evaluate" (substrate self-tests + symmetry/scale evals)

Rationale: B1 (operator-rotation) and B2-B4 (composition/inverse/fixed-point)
are substrate self-tests of the operator algebra; G4 (reflection) + G5
(scale) test claim invariance under transforms. All four are
*evaluations* of structural properties, not new claims or falsifications.
This puts all 4 phases on the map, making 4-phase episodes possible
when a root's chain accumulates a claim + falsify + promote + evaluate
sibling — though current architecture doesn't link G/B-family records
to specific parents, so 4-phase requires post-hoc episode linking
(deferred to a later fire).

`episode_id` = sha256 of the chain root's record_id (stable across runs).
A chain root is a record with no `parent_record_id` (or whose parent isn't
in the corpus). Multi-step chains (C1 child of A1, H4 child of A1, etc.)
all inherit the root's episode_id.

`episode_completeness` summarizes how many distinct phase types the
episode covers. 4-phase episodes (claim + falsify + promote + evaluate)
are the high-value training subset Ergon should weight heaviest.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from theseus.config import CORPUS_DIR


# Generator-id → episode_phase mapping. The 4 phases match the
# EPISODE_PHASES enum referenced in Ergon's spec.
_GENERATOR_PHASE_MAP: Dict[str, str] = {
    # Root claim emitters + claim-shaped derivatives
    "a1": "claim", "a2": "claim", "a3": "claim", "a4": "claim", "a5": "claim",
    "f2": "claim", "f3": "claim", "f4": "claim",
    "b5": "claim",
    "c1": "claim", "c2": "claim", "c3": "claim", "c4": "claim", "c5": "claim",
    "e1": "claim", "e3": "claim",
    # Falsification attempts (a record passing here = survived a kill probe)
    "d1": "falsify", "d2": "falsify", "d3": "falsify", "d4": "falsify",
    "h1": "falsify", "h2": "falsify",
    # Promotion / categorical-confirmation
    "h4": "promote",
    # Evaluate — substrate self-tests + symmetry/scale-invariance evaluators
    "b1": "evaluate", "b2": "evaluate", "b3": "evaluate", "b4": "evaluate",
    "g4": "evaluate", "g5": "evaluate",
}


def classify_phase(generator_id: str) -> str:
    """Map a Theseus generator_id to one of {claim, falsify, promote, evaluate}.

    Default for unknown generators is "evaluate" (single-phase, lowest specificity)."""
    return _GENERATOR_PHASE_MAP.get(generator_id, "evaluate")


def _episode_id_for_root(root_record_id: str) -> str:
    """Stable, content-addressed episode_id derived from the chain root."""
    h = hashlib.sha256()
    h.update(b"episode|")
    h.update(root_record_id.encode("utf-8"))
    return h.hexdigest()


def _walk_corpus(corpus_dir: Path) -> Iterable[Dict[str, Any]]:
    """Stream records from all corpus jsonl files (skips .annotated.jsonl)."""
    if not corpus_dir.is_dir():
        return
    from theseus.emit.corpus_files import iter_batch_paths, open_batch
    for jf in iter_batch_paths(corpus_dir):
        try:
            with open_batch(jf) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            continue


def build_parent_child_index(
    corpus_dir: Path = CORPUS_DIR,
) -> Tuple[Dict[str, str], Dict[str, List[str]]]:
    """Return (record_id → parent_id, record_id → list of child_ids).

    Only includes records whose claim_payload's `parent_record_id` is also
    present in the corpus. Standalone records (no parent in corpus) become
    chain roots.
    """
    all_ids: set = set()
    parent_of: Dict[str, str] = {}
    for r in _walk_corpus(corpus_dir):
        rid = r.get("record_id")
        if not rid:
            continue
        all_ids.add(rid)
        # The parent reference can live in two places per Theseus's
        # current schemas: top-level `parent_record_id` or inside
        # claim_payload.
        parent = r.get("parent_record_id")
        if parent is None:
            p = r.get("claim_payload") or {}
            parent = p.get("parent_record_id")
        if parent:
            parent_of[rid] = parent
    # Only keep parent links that resolve into the corpus.
    parent_of = {rid: pid for rid, pid in parent_of.items() if pid in all_ids}
    children_of: Dict[str, List[str]] = defaultdict(list)
    for rid, pid in parent_of.items():
        children_of[pid].append(rid)
    return parent_of, dict(children_of)


def find_chain_root(record_id: str, parent_of: Dict[str, str]) -> str:
    """Walk parent pointers to the chain root. Cycle-safe (bounded depth)."""
    cur = record_id
    for _ in range(64):  # depth cap
        nxt = parent_of.get(cur)
        if nxt is None or nxt == cur:
            return cur
        cur = nxt
    return cur


def assign_episodes(
    corpus_dir: Path = CORPUS_DIR,
) -> Tuple[Dict[str, str], Dict[str, Dict[str, Any]]]:
    """Return:
      - record_id → episode_id (every record in the corpus)
      - episode_id → {
            root_record_id, phase_counts: {phase: n},
            n_records, completeness, distinct_phases
        }
    """
    parent_of, _children = build_parent_child_index(corpus_dir)
    record_to_episode: Dict[str, str] = {}
    episode_meta: Dict[str, Dict[str, Any]] = {}

    for r in _walk_corpus(corpus_dir):
        rid = r.get("record_id")
        if not rid:
            continue
        root = find_chain_root(rid, parent_of)
        ep_id = _episode_id_for_root(root)
        record_to_episode[rid] = ep_id
        gid = r.get("generator_id", "?")
        phase = classify_phase(gid)
        meta = episode_meta.setdefault(ep_id, {
            "episode_id": ep_id,
            "root_record_id": root,
            "phase_counts": {"claim": 0, "falsify": 0, "promote": 0, "evaluate": 0},
            "n_records": 0,
            "distinct_phases": set(),
        })
        meta["phase_counts"][phase] = meta["phase_counts"].get(phase, 0) + 1
        meta["n_records"] += 1
        meta["distinct_phases"].add(phase)

    # Finalize: completeness = number of distinct phases / 4 (claim/falsify/promote/evaluate)
    for ep_id, meta in episode_meta.items():
        n_phases = len(meta["distinct_phases"])
        meta["completeness"] = round(n_phases / 4.0, 3)
        meta["distinct_phases"] = sorted(meta["distinct_phases"])

    return record_to_episode, episode_meta


def episode_summary_stats(episode_meta: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate stats across all episodes for journaling / reporting."""
    by_completeness: Dict[float, int] = defaultdict(int)
    by_distinct_phases: Dict[int, int] = defaultdict(int)
    for meta in episode_meta.values():
        by_completeness[meta["completeness"]] += 1
        by_distinct_phases[len(meta["distinct_phases"])] += 1
    return {
        "n_episodes": len(episode_meta),
        "single_phase_episodes": by_distinct_phases.get(1, 0),
        "two_phase_episodes": by_distinct_phases.get(2, 0),
        "three_phase_episodes": by_distinct_phases.get(3, 0),
        "four_phase_episodes": by_distinct_phases.get(4, 0),
        "completeness_distribution": dict(by_completeness),
    }


def main() -> None:
    """CLI smoke: walk the corpus, print episode stats."""
    import argparse
    p = argparse.ArgumentParser(prog="theseus.handoff.episodes")
    p.add_argument("--corpus-dir", type=Path, default=CORPUS_DIR)
    args = p.parse_args()
    record_to_episode, episode_meta = assign_episodes(args.corpus_dir)
    stats = episode_summary_stats(episode_meta)
    print(f"Records assigned: {len(record_to_episode):,}")
    print(f"Episodes total:   {stats['n_episodes']:,}")
    print(f"  single-phase:   {stats['single_phase_episodes']:,}")
    print(f"  two-phase:      {stats['two_phase_episodes']:,}")
    print(f"  three-phase:    {stats['three_phase_episodes']:,}")
    print(f"  four-phase:     {stats['four_phase_episodes']:,}")


if __name__ == "__main__":
    main()
