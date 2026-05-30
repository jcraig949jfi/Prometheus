"""Phase 3.A — Seam-sufficiency audit (ITER-57a).

Per `feedback_seam_sufficiency_audit`: doctrine's deepest exposed
assumption is that the seam preserves the decisive information from
Layer-1 failures. This audit tests that.

## Protocol

1. Load real ledger rows in chronological order.
2. For each row R_t, predict plugin(R_{t+1}) using two predictors:
   - SEAM-ONLY: features = (plugin_id, kill_pattern, domain) of R_t
   - RAW: features = seam fields PLUS (claim_payload-shape signature,
     batch_id, method, has_kill_vector)
3. Use per-feature-tuple majority predictor.
4. Chronological 70/30 train/test split.
5. Score = accuracy of next-plugin prediction.
6. Verdict:
   - raw_acc - seam_acc > 0.10 -> seam is INSUFFICIENT (raw exploits
     info seam dropped)
   - raw_acc - seam_acc <= 0.10 -> seam is sufficient under this test

## Honest framing

This is a NECESSARY but not SUFFICIENT test of seam sufficiency.
Raw might fail to beat seam even if the seam is lossy, because:
- our raw predictor is a simple per-tuple majority; a richer model
  could exploit raw better
- the next-plugin prediction task may not be what Layer 2 actually
  needs decisive info for
- the existing ledger may not exhibit the kind of failures where
  raw vs seam diverges

A clean "raw beats seam by >10 percentage points" is strong evidence
for INSUFFICIENT. A clean "raw ties seam" is weak evidence for
sufficient — could also be predictor weakness.

## Honest framing of the comparison itself

Raw is a strict superset of seam features. Raw's training accuracy
can only equal-or-beat seam. Test accuracy is where the comparison
is informative — raw might overfit to features (like batch_id or
claim_payload hashes) that don't generalize.

If raw HELPS on test, the gain is real. If raw HURTS on test
(overfitting), that's not evidence the seam is sufficient — it's
evidence our naive raw predictor was wrong, the seam-only baseline
is structurally similar.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


REAL_LEDGER_PATHS = [
    Path("charon/agents/erebos/state/kill_ledger.jsonl"),
    Path("charon/agents/stygian/state/kill_ledger.jsonl"),
]
TRAIN_FRACTION = 0.70
PASS_MARGIN = 0.10   # raw_acc - seam_acc > 0.10 -> seam insufficient


@dataclass(frozen=True)
class SeamAuditResult:
    n_rows_total: int
    n_train: int
    n_test: int
    seam_only_acc: float
    raw_acc: float
    raw_minus_seam: float
    verdict: str
    headline: str
    notes: str


def _extract_plugin(row: dict) -> Optional[str]:
    ck = row.get("claim_kind", "")
    m = re.search(r"_(g\d+_[a-z_]+?)_(claim|attack)", ck)
    if m:
        return m.group(1)
    if ck.startswith("stygian_"):
        return "stygian_battery"
    return ck or None


def _extract_domain(row: dict) -> str:
    cp = row.get("claim_payload") or {}
    if not isinstance(cp, dict):
        return "unknown"
    pid = cp.get("problem_id", "")
    if isinstance(pid, str) and pid.startswith("BL-C"):
        return "mahler"
    if isinstance(pid, str) and pid.startswith("BL-A"):
        return "analytic"
    return "unknown"


def _payload_signature(row: dict) -> str:
    """Hash of canonicalized claim_payload — strict superset of
    what the seam carries via problem_id alone."""
    cp = row.get("claim_payload") or {}
    if not isinstance(cp, dict):
        return "none"
    canon = json.dumps(cp, sort_keys=True, default=str)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:12]


def _load_chronological_rows() -> list[dict]:
    rows: list[dict] = []
    for p in REAL_LEDGER_PATHS:
        if not p.exists():
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    # Sort by emitted_at
    rows.sort(key=lambda r: r.get("emitted_at", ""))
    return rows


def _build_features(row: dict, *, raw: bool) -> tuple:
    plugin = _extract_plugin(row) or "?"
    kp = row.get("kill_pattern") or "PROMOTED"
    domain = _extract_domain(row)
    if not raw:
        return (plugin, kp, domain)
    # Raw adds three structural features the seam doesn't carry
    payload_sig = _payload_signature(row)
    method = row.get("method") or "none"
    has_kv = bool(row.get("kill_vector"))
    return (plugin, kp, domain, payload_sig, method, has_kv)


def _train_majority(
    pairs: list[tuple[tuple, str]],
) -> dict[tuple, str]:
    """For each feature tuple, return the majority next-plugin."""
    by_feat: dict[tuple, Counter] = defaultdict(Counter)
    for feat, next_plugin in pairs:
        by_feat[feat][next_plugin] += 1
    return {f: c.most_common(1)[0][0] for f, c in by_feat.items()}


def _predict(
    pairs: list[tuple[tuple, str]],
    predictor: dict[tuple, str],
    fallback: str,
) -> list[str]:
    return [predictor.get(feat, fallback) for feat, _ in pairs]


def _accuracy(predictions: list[str], truth: list[str]) -> float:
    if not truth:
        return 0.0
    n_correct = sum(1 for p, t in zip(predictions, truth) if p == t)
    return n_correct / len(truth)


def run_seam_audit() -> SeamAuditResult:
    rows = _load_chronological_rows()

    # Build chronological (features_t, plugin_{t+1}) training pairs
    seam_pairs: list[tuple[tuple, str]] = []
    raw_pairs: list[tuple[tuple, str]] = []
    for i in range(len(rows) - 1):
        next_plugin = _extract_plugin(rows[i + 1])
        if not next_plugin:
            continue
        seam_pairs.append((_build_features(rows[i], raw=False), next_plugin))
        raw_pairs.append((_build_features(rows[i], raw=True), next_plugin))

    n_total = len(seam_pairs)
    n_train = int(n_total * TRAIN_FRACTION)
    seam_train = seam_pairs[:n_train]
    seam_test = seam_pairs[n_train:]
    raw_train = raw_pairs[:n_train]
    raw_test = raw_pairs[n_train:]

    truth = [t for _, t in seam_test]

    # Global majority next-plugin as fallback for unseen features
    train_truth_counter = Counter(t for _, t in seam_train)
    global_majority = (
        train_truth_counter.most_common(1)[0][0]
        if train_truth_counter else "?"
    )

    seam_predictor = _train_majority(seam_train)
    seam_preds = _predict(seam_test, seam_predictor, global_majority)
    seam_acc = _accuracy(seam_preds, truth)

    raw_predictor = _train_majority(raw_train)
    raw_preds = _predict(raw_test, raw_predictor, global_majority)
    raw_acc = _accuracy(raw_preds, truth)

    delta = raw_acc - seam_acc

    if delta > PASS_MARGIN:
        verdict = "SEAM_INSUFFICIENT"
        headline = (
            f"SEAM INSUFFICIENT: raw predictor beats seam-only by "
            f"{delta:.4f} ({raw_acc:.4f} vs {seam_acc:.4f}). The "
            f"seam is dropping information the raw fields carry. "
            f"Expand the seam schema."
        )
    elif delta < -PASS_MARGIN:
        verdict = "RAW_OVERFITS"
        headline = (
            f"RAW OVERFITS: raw predictor LOSES to seam by "
            f"{-delta:.4f} on the test set. Not evidence the seam "
            f"is sufficient; evidence that our naive raw predictor "
            f"overfit. Inconclusive on seam sufficiency."
        )
    else:
        verdict = "SEAM_SUFFICIENT"
        headline = (
            f"SEAM SUFFICIENT (under this test): raw beats seam by "
            f"only {delta:.4f}, below the {PASS_MARGIN} margin. "
            f"Either the seam carries the decisive info, or this "
            f"test isn't strong enough to find what it's missing."
        )

    return SeamAuditResult(
        n_rows_total=n_total,
        n_train=n_train,
        n_test=len(seam_test),
        seam_only_acc=seam_acc,
        raw_acc=raw_acc,
        raw_minus_seam=delta,
        verdict=verdict,
        headline=headline,
        notes=(
            f"chronological 70/30 split; per-feature-tuple majority "
            f"predictor; fallback = global majority "
            f"({global_majority!r}); n_total_pairs={n_total}, "
            f"n_train={n_train}, n_test={len(seam_test)}; "
            f"raw features = seam + (payload_sha, method, has_kill_vector)"
        ),
    )


if __name__ == "__main__":
    r = run_seam_audit()
    print("=" * 70)
    print("Phase 3.A -- Seam-sufficiency audit verdict")
    print("=" * 70)
    print(r.headline)
    print()
    print(f"  n_train               : {r.n_train}")
    print(f"  n_test                : {r.n_test}")
    print(f"  seam-only accuracy    : {r.seam_only_acc:.4f}")
    print(f"  raw accuracy          : {r.raw_acc:.4f}")
    print(f"  raw - seam            : {r.raw_minus_seam:+.4f}")
    print(f"  pass margin           : {PASS_MARGIN}")
    print()
    print(f"VERDICT: {r.verdict}")
    print()
    print("Notes:", r.notes)
