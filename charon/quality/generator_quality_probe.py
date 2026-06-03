"""Generator quality probe — first-pass quality triage for Ergon.

## Why this exists (Charon → Ergon handoff, 2026-06-03)

James is having Ergon collect + consume + quality-assess every generator /
swarm in the repo. This module hands Ergon the *quality criterion* so the
first pass uses the right metric.

The load-bearing lesson from the Erebos Phase 3.K audit (2026-06-03,
`pivot/sprint1/phase3/PHASE3_K_PAIR_AWARE_NULL_VERDICT_2026-06-03.md`):

> "Beats random" is NOT the bar. A generator's output has value a downstream
> Layer-2 navigator can exploit ONLY if it carries co-occurrence / conditional
> structure that beats a COUNTER baseline under a permutation null. Every
> Erebos Layer-2 signal claim collapsed when finally tested against that bar.

So the quality of a generator's ledger is not "does it produce lots of rows"
or "is its z-score-vs-shuffle high." It is: **does the ledger carry structure
a per-plugin/per-generator counter cannot already express?**

## The cheap first-pass funnel (what this probe computes)

Two cheap, schema-generic diagnostics triage most generators without the
expensive permutation null:

1. **kp concentration** — per generator, the share of the single most common
   kill_pattern. If ~1.0, the generator emits one dominant kp, so a per-
   generator counter reproduces it exactly. Counter-equivalent → LOW quality
   for a Layer-2 consumer (the structure is fully captured by counting).

2. **multi-emission rate** — fraction of linking-groups (rows sharing a
   `parent_record_id`, else `batch_id`) that contain >= 2 rows. If ~0, there
   is no co-occurrence structure at all, so NO Layer-2 primitive can exceed a
   counter by construction (there are no joint patterns to navigate).

A generator warrants the EXPENSIVE permutation-null test (the discriminator in
`charon/agents/erebos/sprint1/phase3/pair_aware_permutation_null.py`) ONLY if
it passes both cheap gates: kp-diverse AND has multi-emission structure. This
probe flags which generators clear the funnel so Ergon spends the null budget
where it can matter.

This is deliberately the cheap triage, not the full test. It is honest about
that: a `WARRANTS_NULL_TEST` verdict is "might have signal, run the null",
never "has signal."

## Usage

    python -m charon.quality.generator_quality_probe <ledger.jsonl> [...]

Or import `probe_ledger(path)` / `probe_rows(rows, source)` and consume the
`GeneratorQuality` dataclasses directly (Ergon's collection layer).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional


# A generator counts as "one dominant kp" (counter-equivalent) at/above this
# top-kp share. 0.90 mirrors the Phase 3 observation that the real ledger had
# one dominant kp per plugin, making the motif extractor == per-plugin counter.
KP_CONCENTRATION_CEILING = 0.90

# Below this multi-emission rate there is effectively no co-occurrence
# structure for any Layer-2 primitive to navigate.
MULTI_EMISSION_FLOOR = 0.02

# Candidate linking fields, in priority order. The first present + populated
# field is used to group co-occurring rows.
LINK_FIELDS = ("input_signature", "parent_record_id", "batch_id")

GENERATOR_FIELDS = ("generator_id", "plugin_id")
KP_FIELD_DEFAULT = "kill_pattern"


@dataclass(frozen=True)
class GeneratorQuality:
    generator_id: str
    n_rows: int
    n_distinct_kps: int
    top_kp: str
    top_kp_share: float
    verdict: str
    note: str


@dataclass(frozen=True)
class LedgerQuality:
    source: str
    n_rows: int
    link_field: Optional[str]
    n_link_groups: int
    n_multi_emission_groups: int
    multi_emission_rate: float
    per_generator: tuple[GeneratorQuality, ...]
    headline: str


def _generator_of(row: dict) -> Optional[str]:
    for f in GENERATOR_FIELDS:
        v = row.get(f)
        if v:
            return str(v)
    return None


def _pick_link_field(rows: list[dict]) -> Optional[str]:
    for f in LINK_FIELDS:
        if any(r.get(f) for r in rows):
            return f
    return None


def probe_rows(rows: list[dict], source: str = "<rows>",
               kp_field: str = KP_FIELD_DEFAULT) -> LedgerQuality:
    rows = [r for r in rows if isinstance(r, dict)]
    n_rows = len(rows)

    # --- per-generator kp concentration -------------------------------------
    kp_by_gen: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        gen = _generator_of(r)
        if gen is None:
            continue
        kp = r.get(kp_field) or "PROMOTED"
        kp_by_gen[gen][str(kp)] += 1

    per_gen: list[GeneratorQuality] = []
    for gen, kps in sorted(kp_by_gen.items()):
        total = sum(kps.values())
        top_kp, top_n = kps.most_common(1)[0]
        share = top_n / total if total else 0.0
        if len(kps) == 1 or share >= KP_CONCENTRATION_CEILING:
            verdict = "COUNTER_EQUIVALENT"
            note = (
                f"one dominant kp ({share:.0%}); a per-generator counter "
                f"reproduces this generator's output exactly. Low value for a "
                f"Layer-2 consumer."
            )
        else:
            verdict = "KP_DIVERSE"
            note = (
                f"{len(kps)} distinct kps, top share {share:.0%}; carries "
                f"conditional structure a counter may not fully capture."
            )
        per_gen.append(GeneratorQuality(
            generator_id=gen, n_rows=total, n_distinct_kps=len(kps),
            top_kp=str(top_kp), top_kp_share=round(share, 4),
            verdict=verdict, note=note,
        ))

    # --- multi-emission (co-occurrence) structure ---------------------------
    link_field = _pick_link_field(rows)
    n_groups = n_multi = 0
    if link_field is not None:
        groups: dict[str, int] = defaultdict(int)
        for r in rows:
            key = r.get(link_field)
            if key:
                groups[str(key)] += 1
        n_groups = len(groups)
        n_multi = sum(1 for c in groups.values() if c >= 2)
    multi_rate = (n_multi / n_groups) if n_groups else 0.0

    # --- ledger-level headline ----------------------------------------------
    kp_diverse = [g for g in per_gen if g.verdict == "KP_DIVERSE"]
    has_lateral = multi_rate >= MULTI_EMISSION_FLOOR
    if not per_gen:
        headline = "NO_GENERATOR_FIELD: rows lack generator_id/plugin_id; cannot triage by generator."
    elif not has_lateral:
        headline = (
            f"NO_COOCCURRENCE: multi-emission rate {multi_rate:.1%} (link="
            f"{link_field}). No joint structure exists; NO Layer-2 primitive "
            f"can exceed a counter on this ledger by construction. First-pass "
            f"quality = counter-grade at best."
        )
    elif not kp_diverse:
        headline = (
            f"ALL_COUNTER_EQUIVALENT: co-occurrence exists (multi-rate "
            f"{multi_rate:.1%}) but every generator emits one dominant kp. "
            f"Conditional recommendations collapse to marginals. Counter-grade."
        )
    else:
        names = ", ".join(g.generator_id for g in kp_diverse)
        headline = (
            f"WARRANTS_NULL_TEST: {len(kp_diverse)} kp-diverse generator(s) "
            f"[{names}] AND multi-emission rate {multi_rate:.1%}. This ledger "
            f"MIGHT carry signal beyond counters — run the permutation-null "
            f"discriminator before claiming it does."
        )

    return LedgerQuality(
        source=source, n_rows=n_rows, link_field=link_field,
        n_link_groups=n_groups, n_multi_emission_groups=n_multi,
        multi_emission_rate=round(multi_rate, 4),
        per_generator=tuple(per_gen), headline=headline,
    )


def probe_ledger(path: str | Path, kp_field: str = KP_FIELD_DEFAULT) -> LedgerQuality:
    p = Path(path)
    rows: list[dict] = []
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return probe_rows(rows, source=str(p), kp_field=kp_field)


def _print(q: LedgerQuality) -> None:
    print("=" * 72)
    print(f"GENERATOR QUALITY PROBE — {q.source}")
    print("=" * 72)
    print(q.headline)
    print()
    print(f"  n_rows               : {q.n_rows}")
    print(f"  link_field           : {q.link_field}")
    print(f"  link groups          : {q.n_link_groups}")
    print(f"  multi-emission groups: {q.n_multi_emission_groups} "
          f"({q.multi_emission_rate:.1%})")
    print()
    if q.per_generator:
        print("  per generator:")
        for g in q.per_generator:
            print(f"    {g.generator_id:24s} rows={g.n_rows:<5d} "
                  f"kps={g.n_distinct_kps:<3d} top={g.top_kp_share:.0%}  "
                  f"{g.verdict}")
            print(f"        top_kp={g.top_kp}")


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        print(__doc__)
        sys.exit(0)
    for pth in paths:
        _print(probe_ledger(pth))
        print()
