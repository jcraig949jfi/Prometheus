"""Phase 3.0 — Real-residue smoke test (ITER-56).

Per the 2026-05-30 frontier review verdict: before spending the
~10-iteration BSD-loader + daemon-wire + replay path, run one
brutal real-data check on the substrate's primitives. If Layer 2
cannot beat shuffled labels AND counter baselines on real residue,
pause infrastructure expansion.

## Three baselines, not one

The pre-Sprint-1 protocol compared substrate vs random / shuffle
baselines only. Per [[feedback-counter-baseline-discriminator]],
the discriminating question is whether Layer 2 produces decisions
a typed-row + counter + rule-router baseline cannot. This harness
compares against:

  1. SUBSTRATE       — motifs / tensor / null-space on real rows
  2. SHUFFLED        — same primitives on shuffled-label real rows
  3. COUNTER BASELINE — typed event schema + counters + rules,
                        no Layer-2 primitives at all

## Three honest verdicts possible

  PASS:           substrate beats both shuffled AND counter baselines
                  on at least one actionable signal -> proceed to S1
  FAIL:           substrate ties or loses to counter baseline ->
                  pause BSD work; inspect seam sufficiency
  INCONCLUSIVE:   real data too sparse / pending to discriminate ->
                  not a verdict; substrate must produce richer
                  Layer-1 verdicts before this gate can run

## Real-data shape (inspected 2026-05-30)

  570 total rows: 215 Erebos-emitted + 355 Stygian-attack
  Erebos rows: generator_id='erebos', claim_kind encodes gNN_*,
    kp encodes erebos_gNN_*_pending (= awaiting Stygian verdict)
  Stygian rows: 347 of 355 are stygian_battery_attack with
    kp in {stygian_hecate_meta_test_not_yet_implemented,
           stygian_no_loader_registered}
  -- mostly infrastructure-pending, not Layer-1 verdicts

  This sparsity is itself a finding: the substrate doesn't yet
  HAVE rich Layer-1 verdicts to navigate. Layer 2's value claim
  is conditional on Layer 1 producing the kind of failures the
  doctrine envisions.
"""
from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from charon.agents.erebos._kill_tensor import (
    AXIS_DOMAIN,
    AXIS_INVARIANT,
    AXIS_KP,
    AXIS_PLUGIN,
    KillTensor,
)
from charon.agents.erebos._motif_extraction import (
    extract_plugin_domain_kp_motifs,
    extract_plugin_kp_motifs,
)
from charon.agents.erebos._null_space import find_voids


REAL_LEDGER_PATHS = [
    Path("charon/agents/erebos/state/kill_ledger.jsonl"),
    Path("charon/agents/stygian/state/kill_ledger.jsonl"),
]
# Phase 3.B enrichment file (separate from production state).
# When present, included automatically -- the smoke re-runs over
# combined production + enriched residue.
ENRICHED_LEDGER_PATH = Path(
    "charon/agents/erebos/state/kill_ledger_enriched.jsonl"
)
SEED = 1031
MIN_REAL_ROWS = 100   # protocol minimum
MOTIF_MIN_COUNT = 3
N_SHUFFLE_TRIALS = 20  # null distribution depth


@dataclass(frozen=True)
class SmokeResult:
    n_real_rows: int
    n_substrate_motifs: int
    n_substrate_voids: int
    substrate_motif_concentration: float    # gini-like; higher = more structured
    shuffled_motif_concentration_mean: float
    shuffled_motif_concentration_std: float
    substrate_vs_shuffled_z: float          # (substrate - shuffled_mean) / shuffled_std
    counter_baseline_top_kp_per_plugin: dict
    substrate_routing_differs_from_counter: int  # count of plugins where Layer 2 differs
    actionable_routing_deltas: int
    verdict: str
    headline: str
    notes: str = ""
    diagnostics: dict = field(default_factory=dict)


def _normalize_row(row: dict) -> Optional[dict]:
    """Convert real ledger row to the canonical shape Layer 2 primitives expect.

    Real rows have generator_id at agent level (erebos / stygian) and
    encode the actual plugin in claim_kind (e.g. 'erebos_g02_contrast_claim').
    Normalize to:
      plugin_id        = extracted from claim_kind (or stygian batter)
      kill_pattern     = direct
      domain           = mahler / analytic / unknown from claim_payload.problem_id
      input_signature  = parent_record_id (or sigma_claim_id, or composed_id)
      row_id           = record_id
    """
    if not isinstance(row, dict):
        return None
    ck = row.get("claim_kind", "")
    # Extract g<NN>_<name> from claim_kind if present
    plugin_id = None
    m = re.search(r"_(g\d+_[a-z_]+?)_(claim|attack)", ck)
    if m:
        plugin_id = m.group(1)
    elif ck.startswith("stygian_"):
        plugin_id = "stygian_battery"
    elif ck:
        plugin_id = ck
    else:
        return None

    cp = row.get("claim_payload") or {}
    pid = cp.get("problem_id", "") if isinstance(cp, dict) else ""
    if isinstance(pid, str) and pid.startswith("BL-C"):
        domain = "mahler"
    elif isinstance(pid, str) and pid.startswith("BL-A"):
        domain = "analytic"
    else:
        domain = "unknown"

    input_signature = (
        row.get("parent_record_id")
        or row.get("sigma_claim_id")
        or row.get("composed_id")
        or row.get("record_id")
    )

    return {
        "row_id": row.get("record_id"),
        "plugin_id": plugin_id,
        "kill_pattern": row.get("kill_pattern"),
        "domain": domain,
        "input_signature": input_signature,
    }


def _load_real_rows(include_enriched: bool = True) -> list[dict]:
    paths = list(REAL_LEDGER_PATHS)
    if include_enriched and ENRICHED_LEDGER_PATH.exists():
        paths.append(ENRICHED_LEDGER_PATH)
    rows: list[dict] = []
    for p in paths:
        if not p.exists():
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    continue
                norm = _normalize_row(raw)
                if norm is not None and norm["plugin_id"]:
                    rows.append(norm)
    return rows


def _motif_concentration(motifs: list) -> float:
    """Concentration measure: top-3 motif counts divided by total
    in-motif rows. Higher = more concentrated structure (fewer
    motifs carry most weight); lower = flatter distribution.
    Bounded in [0, 1]; ~1/k for uniform over k motifs.
    """
    if not motifs:
        return 0.0
    counts = sorted((m.count for m in motifs), reverse=True)
    top_k = sum(counts[:3])
    total = sum(counts)
    return top_k / total if total > 0 else 0.0


def _run_substrate(rows: list[dict]) -> tuple[int, int, float]:
    """Run motif extraction + null-space on rows; return (n_motifs,
    n_voids, concentration)."""
    motif_result = extract_plugin_kp_motifs(rows, min_count=MOTIF_MIN_COUNT)
    motifs = list(motif_result.motifs)

    tensor = KillTensor.from_ledger_rows(rows)
    void_result = find_voids(
        tensor,
        fix_axes=(AXIS_PLUGIN, AXIS_DOMAIN, AXIS_INVARIANT),
        min_score=0.5,
    )
    n_voids = len(void_result.voids)
    concentration = _motif_concentration(motifs)
    return len(motifs), n_voids, concentration


def _shuffle_labels(rows: list[dict], rng: random.Random) -> list[dict]:
    kps = [r["kill_pattern"] for r in rows]
    rng.shuffle(kps)
    return [{**r, "kill_pattern": k} for r, k in zip(rows, kps)]


def _counter_baseline_recommendations(rows: list[dict]) -> dict[str, str]:
    """Q2's counter baseline: per-plugin majority kp.
    Returns {plugin_id: most_common_kp}."""
    by_plugin: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        kp = r.get("kill_pattern") or "PROMOTED"
        by_plugin[r["plugin_id"]][kp] += 1
    return {
        pid: counts.most_common(1)[0][0] for pid, counts in by_plugin.items()
    }


def _substrate_routing_recommendations(rows: list[dict]) -> dict[str, str]:
    """The substrate's routing: per-plugin, recommend the kp from
    the highest-count motif that includes this plugin. If motifs
    perfectly track per-plugin majority, this equals the counter
    baseline; if motifs differ, substrate has a different opinion."""
    motif_result = extract_plugin_kp_motifs(rows, min_count=MOTIF_MIN_COUNT)
    # For each plugin, find its highest-count motif
    by_plugin: dict[str, tuple[int, str]] = {}
    for m in motif_result.motifs:
        plugin, kp = m.key
        prev = by_plugin.get(plugin, (0, ""))
        if m.count > prev[0]:
            by_plugin[plugin] = (m.count, kp)
    return {pid: kp for pid, (_, kp) in by_plugin.items()}


def run_phase3_smoke() -> SmokeResult:
    rows = _load_real_rows()
    n_real = len(rows)

    if n_real < MIN_REAL_ROWS:
        return SmokeResult(
            n_real_rows=n_real,
            n_substrate_motifs=0,
            n_substrate_voids=0,
            substrate_motif_concentration=0.0,
            shuffled_motif_concentration_mean=0.0,
            shuffled_motif_concentration_std=0.0,
            substrate_vs_shuffled_z=0.0,
            counter_baseline_top_kp_per_plugin={},
            substrate_routing_differs_from_counter=0,
            actionable_routing_deltas=0,
            verdict="INCONCLUSIVE",
            headline=(
                f"INCONCLUSIVE: only {n_real} real rows available; "
                f"need >= {MIN_REAL_ROWS}. Substrate hasn't yet "
                f"produced enough Layer-1 verdicts to navigate."
            ),
            notes=(
                "Real data is sparse. This is itself a finding -- "
                "see [[feedback-instrument-vs-architectural-pass]]: "
                "Layer 2's value claim is conditional on Layer 1 "
                "producing the kind of failures the doctrine envisions."
            ),
        )

    # SUBSTRATE: run primitives on real rows
    n_motifs, n_voids, concentration = _run_substrate(rows)

    # SHUFFLED baseline: null distribution
    rng = random.Random(SEED)
    shuffled_concentrations = []
    for _ in range(N_SHUFFLE_TRIALS):
        s_rows = _shuffle_labels(rows, rng)
        _, _, s_conc = _run_substrate(s_rows)
        shuffled_concentrations.append(s_conc)
    s_mean = sum(shuffled_concentrations) / len(shuffled_concentrations)
    s_var = sum((s - s_mean) ** 2 for s in shuffled_concentrations) / len(shuffled_concentrations)
    s_std = s_var ** 0.5
    z = (concentration - s_mean) / s_std if s_std > 0 else 0.0

    # COUNTER baseline: per-plugin majority kp (no motifs, no tensor)
    counter_recs = _counter_baseline_recommendations(rows)
    substrate_recs = _substrate_routing_recommendations(rows)

    n_differ = 0
    n_actionable_deltas = 0
    for pid in set(counter_recs) | set(substrate_recs):
        c = counter_recs.get(pid)
        s = substrate_recs.get(pid)
        if c != s:
            n_differ += 1
            # "Actionable" means substrate's pick is not None/PROMOTED
            # AND differs from counter's pick. PROMOTED -> PROMOTED is
            # not actionable; substantive kp differences are.
            if s and s != "PROMOTED" and c != s:
                n_actionable_deltas += 1

    # Verdict logic per the 2026-05-30 review protocol
    if z >= 2.0 and n_actionable_deltas >= 1:
        verdict = "PASS"
        headline = (
            f"PASS: substrate's motif concentration is "
            f"{z:.2f} sigma above shuffled mean AND produces "
            f"{n_actionable_deltas} actionable routing delta(s) "
            f"vs counter baseline. Proceed to S1."
        )
    elif z >= 2.0 and n_actionable_deltas == 0:
        verdict = "FAIL"
        headline = (
            f"FAIL: substrate beats shuffled labels (z={z:.2f}) "
            f"but produces ZERO actionable routing deltas vs "
            f"counter baseline. Pause BSD work; the substrate "
            f"detects structure counters already see."
        )
    elif z < 2.0:
        verdict = "FAIL"
        headline = (
            f"FAIL: substrate motif concentration z={z:.2f} does "
            f"not significantly exceed shuffled baseline. Real "
            f"residue lacks the structure the substrate's "
            f"primitives were calibrated for."
        )
    else:
        verdict = "INCONCLUSIVE"
        headline = "INCONCLUSIVE"

    return SmokeResult(
        n_real_rows=n_real,
        n_substrate_motifs=n_motifs,
        n_substrate_voids=n_voids,
        substrate_motif_concentration=concentration,
        shuffled_motif_concentration_mean=s_mean,
        shuffled_motif_concentration_std=s_std,
        substrate_vs_shuffled_z=z,
        counter_baseline_top_kp_per_plugin=counter_recs,
        substrate_routing_differs_from_counter=n_differ,
        actionable_routing_deltas=n_actionable_deltas,
        verdict=verdict,
        headline=headline,
        notes=(
            f"3-baseline comparison per 2026-05-30 review. "
            f"N_real_rows={n_real}; N_shuffle_trials={N_SHUFFLE_TRIALS}; "
            f"seed={SEED}. Substrate motif concentration "
            f"{concentration:.4f} vs shuffled "
            f"{s_mean:.4f} +/- {s_std:.4f} -> z={z:.2f}. "
            f"Substrate routing differs from counters on "
            f"{n_differ}/{len(counter_recs)} plugins; "
            f"{n_actionable_deltas} actionable (non-PROMOTED, "
            f"substantive disagreement)."
        ),
        diagnostics={
            "shuffled_concentrations": shuffled_concentrations,
            "n_distinct_plugins": len(counter_recs),
            "n_distinct_kps_real": len({r.get("kill_pattern") for r in rows}),
        },
    )


if __name__ == "__main__":
    result = run_phase3_smoke()
    print("=" * 70)
    print("Phase 3.0 -- Real-residue smoke test verdict")
    print("=" * 70)
    print(result.headline)
    print()
    print("Notes:", result.notes)
    print()
    print(f"  Real rows                  : {result.n_real_rows}")
    print(f"  Substrate motifs           : {result.n_substrate_motifs}")
    print(f"  Substrate voids            : {result.n_substrate_voids}")
    print(f"  Substrate concentration    : {result.substrate_motif_concentration:.4f}")
    print(f"  Shuffled mean (+/- std)    : {result.shuffled_motif_concentration_mean:.4f}"
          f" (+/- {result.shuffled_motif_concentration_std:.4f})")
    print(f"  z-score                    : {result.substrate_vs_shuffled_z:.4f}")
    print(f"  Plugins where Layer 2 != counter : {result.substrate_routing_differs_from_counter}")
    print(f"  Actionable routing deltas  : {result.actionable_routing_deltas}")
    print()
    print(f"VERDICT: {result.verdict}")
