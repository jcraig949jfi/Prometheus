"""Composition enumeration driver (gen_10).

Enumerates all type-valid ordered pairs (outer ∘ inner) from the
promoted symbol registry, scores them, and emits the top-N as Agora
tasks.

Idempotence: tasks are keyed by a deterministic composition-id derived
from (outer_ref, inner_ref). Re-running the driver should be
idempotent — existing tasks are not re-enqueued if the task_id already
exists in `agora:work_tasks`.

Usage:
    PYTHONPATH=. python -m harmonia.composers.enumerate
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

os.environ.setdefault("AGORA_REDIS_HOST", "192.168.1.176")
os.environ.setdefault("AGORA_REDIS_PASSWORD", "prometheus")

import redis

from agora.symbols import all_symbols, get_latest_version
from agora.symbols.resolve import resolve
from agora.tensor import dims
from agora.helpers import seed_task, canonical_instance_name

from harmonia.composers.validator import validate
from harmonia.composers.scorer import score_composition


def _get_redis():
    host = os.environ.get("AGORA_REDIS_HOST", "192.168.1.176")
    password = os.environ.get("AGORA_REDIS_PASSWORD", "prometheus")
    return redis.Redis(host=host, password=password, decode_responses=True)


def _load_symbol_meta(name: str, version: int) -> dict:
    """Get a symbol's frontmatter via agora.symbols.resolve.

    Returns a dict with at least {name, type, version, precision?,
    references?}.
    """
    sym = resolve(name, version=version)
    # resolve() returns the full symbol record (parsed frontmatter +
    # sections). We only need the frontmatter-level keys.
    meta = {
        "name": sym.get("name", name),
        "type": sym.get("type", "unknown"),
        "version": sym.get("version", version),
        "precision": sym.get("precision"),
        "references": sym.get("references", []),
    }
    return meta


def _tensor_zero_cells() -> int:
    """Return the current count of zero-valued (F,P) tensor cells."""
    d = dims()
    total = int(d.get("features", 0)) * int(d.get("projections", 0))
    nonzero = int(d.get("nonzero_cells", 0))
    return max(total - nonzero, 0)


def enumerate_compositions(
    symbols: Optional[list[str]] = None,
    r: Optional[redis.Redis] = None,
) -> list[dict]:
    """Produce the full scored composition list.

    Returns a list of dicts with validator verdict and, if valid, score
    components. Sorted by score descending.
    """
    if r is None:
        r = _get_redis()
    if symbols is None:
        symbols = sorted(all_symbols())

    metas = {s: _load_symbol_meta(s, get_latest_version(s)) for s in symbols}

    zero_cells = _tensor_zero_cells()

    compositions = []
    retired = []
    for outer in symbols:
        for inner in symbols:
            v = validate(metas[outer], metas[inner])
            if not v["valid"]:
                retired.append({**v, "score": 0.0})
                continue
            sc = score_composition(metas[outer], metas[inner],
                                   tensor_zero_cells=zero_cells, r=r)
            compositions.append({**v, **sc})

    compositions.sort(key=lambda c: -c["score"])
    return compositions, retired


def _composition_task_id(outer_ref: str, inner_ref: str) -> str:
    """Deterministic task id for idempotent seeding."""
    safe = lambda s: s.replace("@", "_").replace("[", "_").replace("]", "_").replace(":", "_")
    return f"composition_{safe(outer_ref)}_X_{safe(inner_ref)}"


def seed_top_n_tasks(
    compositions: list[dict],
    n: int = 10,
    priority_base: float = -0.6,
    posted_by: str = "Harmonia_M2_sessionA",
) -> list[dict]:
    """Seed top-N compositions onto Agora. Idempotent: if a task_id
    already exists, skip. Priority scales with rank."""
    r = _get_redis()
    worker = canonical_instance_name(posted_by)
    seeded = []
    skipped = []
    for i, comp in enumerate(compositions[:n]):
        task_id = _composition_task_id(comp["outer"], comp["inner"])
        if r.hexists("agora:work_tasks", task_id):
            skipped.append(task_id)
            continue
        # Priority: top-scored gets -0.6, rank-N gets -0.6 + 0.02*rank
        priority = priority_base + 0.02 * i
        goal = (
            f"Execute composition {comp['outer']} ∘ {comp['inner']} "
            f"(score={comp['score']:.3f}, rank {i+1}). Run the outer "
            f"against the inner; land any new (F,P) cells in the tensor."
        )
        acceptance = [
            "composition runs end-to-end and produces a numeric result or structured output",
            "any (F,P) cells touched have their values updated per the verdict discipline",
            "Pattern 30 gate passes (or the composition aborts with 'Pattern 30 BLOCK')",
            "result recorded as SIGNATURE@v2 under null-family discipline when applicable",
        ]
        caveats = [
            "Pattern 30 gate applies to every composition producing a correlation. HONOR BLOCKs.",
            "type-compatibility verified by validator; if a rule mis-rejected, submit a rule exception — do NOT bypass.",
            f"scorer components — novelty={comp['novelty']:.1f}, "
            f"resolving_prior={comp['resolving_prior']}, "
            f"fanout={comp['stratification_fanout']:.1f}, "
            f"cost={comp['cost']:.1f}",
        ]
        seed_task(
            task_id=task_id,
            task_type="composition_run",
            spec="docs/prompts/gen_10_composition_enumeration.md",
            goal=goal,
            acceptance=acceptance,
            priority=priority,
            composes_with=["gen_10", "gen_02", "gen_06"],
            epistemic_caveats=caveats,
            required_qualification="harmonia_session",
            posted_by=worker,
            extra={
                "outer_ref": comp["outer"],
                "inner_ref": comp["inner"],
                "score": comp["score"],
                "score_components": {k: comp[k] for k in
                                     ("novelty", "resolving_prior",
                                      "stratification_fanout", "cost")},
            },
        )
        seeded.append(task_id)
    return {"seeded": seeded, "skipped_existing": skipped}


def write_queue_md(compositions: list[dict], out_path: Path,
                   retired: Optional[list[dict]] = None) -> None:
    """Write the human-readable composition_queue.md top-50 table."""
    lines = ["# Composition Queue — gen_10",
             "",
             "**Generated by** `harmonia/composers/enumerate.py`",
             f"**Symbols inspected:** {len({c['outer'] for c in compositions} | {c['inner'] for c in compositions})}",
             f"**Valid compositions enumerated:** {len(compositions)}",
             f"**Rejected by validator:** {len(retired) if retired else 0}",
             "",
             "## Scorer",
             "",
             "```",
             "score = (novelty + resolving_prior + 0.5 * stratification_fanout) / sqrt(cost)",
             "```",
             "",
             "## Top-50 (by score)",
             "",
             "| Rank | Composition | Score | novelty | resolving_prior | fanout | cost | Types |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |",
             ]
    for i, c in enumerate(compositions[:50]):
        lines.append(
            f"| {i+1} | `{c['outer']} ∘ {c['inner']}` | {c['score']:.3f} | "
            f"{c['novelty']:.1f} | {c['resolving_prior']} | "
            f"{c['stratification_fanout']:.1f} | {c['cost']:.1f} | "
            f"{c['outer_type']} ∘ {c['inner_type']} |"
        )
    if retired:
        lines += ["", "## Rejected by validator (sample)", "",
                  "| Composition | Reason |",
                  "| --- | --- |"]
        for r in retired[:30]:
            outer = r.get('outer')
            inner = r.get('inner')
            lines.append(
                f"| `{outer} ∘ {inner}` ({r.get('outer_type')} ∘ {r.get('inner_type')}) | {r['reason']} |"
            )
    lines += ["",
              "## Epistemic discipline",
              "",
              "- Top-scored ≠ top-interesting. Scorer is a heuristic. Conductor picks.",
              "- Pattern 30 gate applies to every correlation-producing composition. HONOR BLOCKs.",
              "- Type-compatibility is a hard constraint. File rule exceptions rather than bypass.",
              "- Retired compositions that consistently return noise after ≥ 3 tries get deprioritized.",
              "",
              "## Composes with",
              "",
              "- gen_01 Map-Elites (when live) — selects from this queue by behavior novelty.",
              "- gen_02 null-family — every new null spawns N new compositions.",
              "- gen_06 pattern auto-sweeps — gates every composition result before tensor landing.",
              ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    compositions, retired = enumerate_compositions()
    print(f"Symbols enumerated: {len(sorted({c['outer'] for c in compositions} | {c['inner'] for c in compositions}))}")
    print(f"Valid compositions: {len(compositions)}")
    print(f"Rejected by validator: {len(retired)}")
    print()
    print("Top 10:")
    for i, c in enumerate(compositions[:10]):
        print(f"  {i+1:2d}. {c['outer']:18s} ∘ {c['inner']:18s}  score={c['score']:6.3f}  "
              f"(nov={c['novelty']:5.1f}, rp={c['resolving_prior']}, "
              f"fo={c['stratification_fanout']:.1f}, cost={c['cost']:.1f})")

    out_path = Path("harmonia/memory/composition_queue.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_queue_md(compositions, out_path, retired)
    print(f"Wrote {out_path}")

    # Also dump JSON for machine consumers
    json_path = Path("harmonia/memory/composition_queue.json")
    json_path.write_text(json.dumps({
        "compositions": compositions,
        "retired": retired,
    }, indent=2), encoding="utf-8")
    print(f"Wrote {json_path}")

    # Seed top-10
    result = seed_top_n_tasks(compositions, n=10)
    print(f"Seeded {len(result['seeded'])} composition tasks "
          f"(skipped {len(result['skipped_existing'])} already-existing).")
    return compositions, retired, result


if __name__ == "__main__":
    main()
