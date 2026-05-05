"""prometheus_math.kill_vector_learner — Day 4 of the 5-day kill-space pivot.

Builds a *plain regression* learner that maps ``(region_meta, operator) ->
kill_vector`` and asks the empirical question: **is the gradient field even
learnable from the existing ledger?**

Context
-------
Day 1-3 just shipped:
  * Day 1-2: per-region archaeology — region carries 2.4x more kill-pattern
    information than operator (verdict B: region-specific).
  * Day 3: KillVector representation integrated, with backfill helper from
    legacy categorical kill_pattern strings.

ChatGPT's framing for Day 4:
  - input  = (state aka region_meta, operator)
  - output = predicted kill_vector
  - learner = plain regression (no RL, no neural net)
  - if MAE on held-out is meaningfully better than predicting the global
    mean, the substrate has a learnable gradient field.

Day 5 (next) uses this learner for greedy navigation: choose the operator
that minimises predicted ‖k‖.

Architecture
------------
For each of the 12 kill_vector components (out_of_band, reciprocity,
irreducibility, catalog:*, F1_permutation_null, F6_base_rate,
F9_simpler_explanation, F11_cross_validation), we train two small models:

  * a logistic regression for ``triggered`` (binary)
  * a linear regression for ``margin`` (only when margin is recoverable
    from the legacy data; predict NaN-as-NaN otherwise)

Total: 12 components x 2 sub-models = 24 small sklearn-style models.

Why not a neural net?
  - **Interpretability**: each model's coefficients say which (region,
    operator) feature shifts the kill probability.
  - **Data scale**: the existing ledger has ~315k aggregated kills, but
    only ~6 distinct regions x ~13 distinct operators x 7 falsifiers.
    The expanded per-record dataset is large, but the *cell count* is
    tiny — a neural net would memorize the table.
  - **Sparseness**: per-region archaeology already showed many region x
    operator cells empty. Linear models degrade gracefully; a NN would
    overfit the dense cells.

Baselines
---------
The learner is compared against four baselines:

  1. Mean baseline: predict the global mean kill_vector.
  2. Region baseline: predict the per-region mean.
  3. Operator baseline: predict the per-operator mean.
  4. Region x operator baseline: predict the per-(region, operator) cell
     mean. This is the upper bound for "no learning, just look up the
     table." A learner that beats this has captured generalisation.

Verdict dispatch
----------------
  * **A: learner beats region x operator cell-mean baseline** — substrate
    has a learnable gradient field beyond table lookup; Day 5 navigation
    is well-founded.
  * **B: learner matches but does not beat cell-mean** — no
    generalisation beyond memorisation; Day 5 navigation is just lookup;
    need denser data / new operators to find generalisable signal.
  * **C: learner underperforms cell-mean** — bug or fundamental
    representation issue; investigate before Day 5.

Honest framing: this is a small learner on noisy categorical data;
positive result is a substrate signal, not mathematical capability.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    mean_absolute_error,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

from prometheus_math.gradient_archaeology import (
    PER_FILE_METADATA,
    PROMETHEUS_MATH_DIR,
    _extract_kill_pattern_aggregate,
    _extract_region_kill_records,
    _region_id,
    _strip_arm_prefix,
    load_all_sources,
)
from prometheus_math.kill_vector import (
    KillComponent,
    KillVector,
    kill_vector_from_legacy,
)


# ---------------------------------------------------------------------------
# The canonical 12 falsifier components the learner predicts.
# ---------------------------------------------------------------------------
#
# These are the names emitted by ``kill_vector_from_pipeline_output``. The
# legacy ledger uses ``upstream:*`` strings instead of F1/F6/F9/F11 because
# old four_counts pilots tagged kills at the env-reward level (before the
# pipeline even saw them). The legacy-pattern -> falsifier_name map below
# captures the semantics: an "upstream:functional" reward is the env's
# explicit signal that F-checks were never reached because the env
# already classified the candidate; we map it to the Phase-0 ladder
# component (out_of_band) by default, since these candidates didn't make
# it past band-filtering. Where the legacy pattern more directly implies
# a specific F-check kill (e.g. "F6_kill:..."), the existing
# ``kill_vector.kill_vector_from_legacy()`` already routes correctly.

CANONICAL_COMPONENTS: Tuple[str, ...] = (
    "out_of_band",
    "reciprocity",
    "irreducibility",
    "catalog:Mossinghoff",
    "catalog:lehmer_literature",
    "catalog:LMFDB",
    "catalog:OEIS",
    "catalog:arXiv",
    "F1_permutation_null",
    "F6_base_rate",
    "F9_simpler_explanation",
    "F11_cross_validation",
)


# Map a legacy "upstream:*" kill_pattern string to the canonical
# falsifier_name + a recoverable margin (or None). All upstream:* labels
# come from the env's reward_label, which means the candidate never
# reached the F-check ladder; we attribute these to ``out_of_band`` since
# that's the Phase-0 gate they failed.
LEGACY_UPSTREAM_TO_COMPONENT: Dict[str, str] = {
    "upstream:cyclotomic_or_large": "out_of_band",
    "upstream:large_m": "out_of_band",
    "upstream:cyclotomic": "F9_simpler_explanation",
    "upstream:functional": "out_of_band",
    "upstream:low_m": "out_of_band",
    "upstream:salem_cluster": "out_of_band",
    "upstream:shaped_continuous": "out_of_band",
    "upstream:non_finite": "out_of_band",
    "upstream:unknown": "out_of_band",
}


def _canonical_component_for_legacy_kp(kp: str) -> Optional[str]:
    """Map a legacy kill_pattern string to one of CANONICAL_COMPONENTS.

    Returns None if the pattern doesn't match any canonical component
    (the record is dropped from the dataset, with a count in the
    diagnostic).
    """
    if not kp:
        return None
    if kp in LEGACY_UPSTREAM_TO_COMPONENT:
        return LEGACY_UPSTREAM_TO_COMPONENT[kp]
    if kp.startswith("upstream:"):
        return "out_of_band"
    if kp.startswith("out_of_band"):
        return "out_of_band"
    if kp.startswith("reciprocity"):
        return "reciprocity"
    if kp.startswith("reducible"):
        return "irreducibility"
    if kp.startswith("known_in_catalog"):
        for cat in ("Mossinghoff", "lehmer_literature", "LMFDB", "OEIS", "arXiv"):
            if cat in kp:
                return f"catalog:{cat}"
        return "catalog:Mossinghoff"
    if kp.startswith("F1_kill"):
        return "F1_permutation_null"
    if kp.startswith("F6_kill"):
        return "F6_base_rate"
    if kp.startswith("F9_kill"):
        return "F9_simpler_explanation"
    if kp.startswith("F11_kill"):
        return "F11_cross_validation"
    return None


# ---------------------------------------------------------------------------
# Dataset construction
# ---------------------------------------------------------------------------


@dataclass
class LearnerRecord:
    """One (features, kill_vector) pair for the learner.

    ``features`` is the input vector: region encoding + operator one-hot.
    ``y_triggered[i]`` and ``y_margin[i]`` are the i-th component's
    triggered flag (0/1) and margin (NaN if not recoverable).
    """

    region: str
    operator: str
    region_meta: Dict[str, Any]
    y_triggered: np.ndarray         # shape (n_components,), float in {0, 1}
    y_margin: np.ndarray            # shape (n_components,), float w/ NaN
    weight: float = 1.0             # for aggregated rows; default 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region": self.region,
            "operator": self.operator,
            "region_meta": dict(self.region_meta),
            "y_triggered": self.y_triggered.tolist(),
            "y_margin": [None if math.isnan(x) else float(x)
                         for x in self.y_margin.tolist()],
            "weight": float(self.weight),
        }


@dataclass
class Dataset:
    """The full tabular dataset assembled from the pilot ledger.

    Records are individual kill events (one record per "this candidate
    was killed by component X" line). The legacy ledger gives us aggregate
    counts per (region, operator, kill_pattern); we expand each count
    into ``count`` individual records — same triggered vector for each.

    Sparseness is honest: for any region x operator x component cell with
    zero kills, we have NO triggered=False record (the legacy ledger
    doesn't tell us how many candidates *passed* component X for this
    operator x region). We label this caveat in the dataset diagnostic.
    """

    records: List[LearnerRecord]
    component_names: Tuple[str, ...]
    region_to_idx: Dict[str, int]
    operator_to_idx: Dict[str, int]
    region_meta_keys: Tuple[str, ...] = ("degree", "alphabet_width", "reward_shape", "env")

    @property
    def n(self) -> int:
        return len(self.records)

    @property
    def n_components(self) -> int:
        return len(self.component_names)

    def coverage_matrix(self) -> Dict[Tuple[str, str], int]:
        """Region x operator -> count of records."""
        c: Counter = Counter()
        for r in self.records:
            c[(r.region, r.operator)] += int(round(r.weight))
        return dict(c)

    def stats(self) -> Dict[str, Any]:
        """Diagnostic stats for the dataset."""
        cov = self.coverage_matrix()
        return {
            "n_records": self.n,
            "n_components": self.n_components,
            "n_regions": len(self.region_to_idx),
            "n_operators": len(self.operator_to_idx),
            "coverage_matrix_shape": (len(self.region_to_idx),
                                      len(self.operator_to_idx)),
            "n_nonempty_cells": len(cov),
            "sparseness": (
                1.0 - len(cov)
                / max(1, len(self.region_to_idx) * len(self.operator_to_idx))
            ),
            "per_region_records": dict(Counter(r.region for r in self.records)),
            "per_operator_records": dict(
                Counter(r.operator for r in self.records)
            ),
        }


def _aggregated_to_records(
    region_kill_records: Sequence[Dict[str, Any]],
    *,
    expand_to_individual: bool = True,
    max_per_cell: int = 5000,
) -> List[LearnerRecord]:
    """Convert (region, operator, kill_pattern, count) aggregates into
    LearnerRecord(s).

    Each input row gives us ``count`` individual events with the same
    triggered vector (one component True, others False). The "False for
    others" assumption is conservative: the legacy ledger only logs the
    **first-failing** kill, so a candidate that survived components 1-5
    and was killed by component 6 has 0..5 = False, 6 = True; we mark
    components 7..N as False too (they were never tested, but for the
    learner that's the closest honest signal: "this kill_pattern was the
    routed-to component").

    Parameters
    ----------
    expand_to_individual : bool
        If True, expand each ``count`` into ``count`` individual
        LearnerRecord rows (with weight=1). If False, emit ONE row with
        weight=count. Default True (sklearn handles weighted rows but
        per-region split + classifier behaviour is cleaner with expanded
        rows for small datasets).
    max_per_cell : int
        Cap the number of expanded rows per (region, operator,
        kill_pattern) to avoid blowup on the largest cells (caps
        cyclotomic_or_large at ~130k -> 5k). The cap is applied
        per-cell, with the original count preserved as the weight on
        each row.
    """
    records: List[LearnerRecord] = []
    n_components = len(CANONICAL_COMPONENTS)
    name_to_idx = {n: i for i, n in enumerate(CANONICAL_COMPONENTS)}

    for r in region_kill_records:
        kp = r["kill_pattern"]
        comp = _canonical_component_for_legacy_kp(kp)
        if comp is None:
            continue
        idx = name_to_idx.get(comp)
        if idx is None:
            continue
        count = max(0, int(r["count"]))
        if count == 0:
            continue
        # Legacy ledger gives only the kill outcome for one component;
        # mark that component's triggered=True, all others False.
        # (The "all-others False" is conservative — see docstring.)
        y_trig = np.zeros(n_components, dtype=float)
        y_trig[idx] = 1.0
        y_marg = np.full(n_components, np.nan, dtype=float)

        # Recover margin where possible from the legacy pattern alone.
        if comp == "out_of_band":
            # We don't have M values in the aggregated ledger, so margin
            # stays NaN.
            pass

        # Reconstruct region_meta from PER_FILE_METADATA via region id.
        meta = {}
        if r.get("file") in PER_FILE_METADATA:
            meta = dict(PER_FILE_METADATA[r["file"]])

        if expand_to_individual:
            n_to_emit = min(count, max_per_cell)
            for _ in range(n_to_emit):
                records.append(LearnerRecord(
                    region=r["region"],
                    operator=r["operator"],
                    region_meta=meta,
                    y_triggered=y_trig.copy(),
                    y_margin=y_marg.copy(),
                    weight=float(count) / float(n_to_emit),
                ))
        else:
            records.append(LearnerRecord(
                region=r["region"],
                operator=r["operator"],
                region_meta=meta,
                y_triggered=y_trig.copy(),
                y_margin=y_marg.copy(),
                weight=float(count),
            ))

    return records


def build_dataset(
    base_dir: str = PROMETHEUS_MATH_DIR,
    *,
    expand_to_individual: bool = True,
    max_per_cell: int = 5000,
) -> Dataset:
    """End-to-end: load pilot JSONs, backfill via kill_vector_from_legacy,
    expand into per-component LearnerRecord rows.
    """
    sources = load_all_sources(base_dir)
    region_records = _extract_region_kill_records(sources)
    learner_records = _aggregated_to_records(
        region_records,
        expand_to_individual=expand_to_individual,
        max_per_cell=max_per_cell,
    )

    # Index regions and operators stably (sorted for reproducibility).
    regions = sorted({r.region for r in learner_records})
    operators = sorted({r.operator for r in learner_records})

    return Dataset(
        records=learner_records,
        component_names=CANONICAL_COMPONENTS,
        region_to_idx={r: i for i, r in enumerate(regions)},
        operator_to_idx={o: i for i, o in enumerate(operators)},
    )


# ---------------------------------------------------------------------------
# Feature extraction
# ---------------------------------------------------------------------------


def _build_feature_matrix(
    records: Sequence[LearnerRecord],
    *,
    region_encoder: Optional[OneHotEncoder] = None,
    operator_encoder: Optional[OneHotEncoder] = None,
) -> Tuple[np.ndarray, OneHotEncoder, OneHotEncoder]:
    """One-hot encode region + operator + (degree, alphabet_width,
    reward_shape, env) into a dense feature matrix.

    If encoders are supplied (test/eval pass), they are used. Otherwise,
    new encoders are fit on the supplied records (training pass).
    """
    if not records:
        return (np.zeros((0, 0), dtype=float), None, None)

    region_arr = np.array([[r.region] for r in records], dtype=object)
    operator_arr = np.array([[r.operator] for r in records], dtype=object)

    if region_encoder is None:
        region_encoder = OneHotEncoder(
            sparse_output=False, handle_unknown="ignore"
        )
        region_encoder.fit(region_arr)
    if operator_encoder is None:
        operator_encoder = OneHotEncoder(
            sparse_output=False, handle_unknown="ignore"
        )
        operator_encoder.fit(operator_arr)

    region_oh = region_encoder.transform(region_arr)
    operator_oh = operator_encoder.transform(operator_arr)

    # Region meta numeric features: degree, alphabet_width
    def _num(meta: Dict[str, Any], key: str, default: float = 0.0) -> float:
        v = meta.get(key, default)
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    deg = np.array([[_num(r.region_meta, "degree", 10.0)] for r in records],
                   dtype=float)
    width = np.array([[_num(r.region_meta, "alphabet_width", 5.0)]
                      for r in records], dtype=float)

    # Reward-shape one-hot (binary: step vs shaped)
    shape_one = np.array(
        [[1.0 if r.region_meta.get("reward_shape") == "shaped" else 0.0]
         for r in records],
        dtype=float,
    )

    X = np.hstack([region_oh, operator_oh, deg, width, shape_one])
    return X, region_encoder, operator_encoder


# ---------------------------------------------------------------------------
# Train / val / test split (stratified by region)
# ---------------------------------------------------------------------------


def stratified_split(
    dataset: Dataset,
    *,
    test_size: float = 0.20,
    val_size: float = 0.10,
    random_state: int = 42,
) -> Tuple[List[int], List[int], List[int]]:
    """Stratified split by region. Returns (train_idx, val_idx, test_idx).

    Each region's records are split independently with the same
    proportions, so every region is represented in train/val/test.
    Regions with too few records (<4) go entirely into train (no
    validation possible there).
    """
    rng = np.random.RandomState(random_state)
    by_region: Dict[str, List[int]] = defaultdict(list)
    for i, r in enumerate(dataset.records):
        by_region[r.region].append(i)

    train_idx: List[int] = []
    val_idx: List[int] = []
    test_idx: List[int] = []

    for region, idxs in sorted(by_region.items()):
        n = len(idxs)
        idxs_shuffled = list(idxs)
        rng.shuffle(idxs_shuffled)
        if n < 4:
            train_idx.extend(idxs_shuffled)
            continue
        n_test = max(1, int(round(n * test_size)))
        n_val = max(1, int(round(n * val_size))) if n >= 10 else 0
        n_train = n - n_test - n_val
        if n_train <= 0:
            n_train = max(1, n - n_test)
            n_val = max(0, n - n_test - n_train)

        test_idx.extend(idxs_shuffled[:n_test])
        val_idx.extend(idxs_shuffled[n_test:n_test + n_val])
        train_idx.extend(idxs_shuffled[n_test + n_val:])

    return train_idx, val_idx, test_idx


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------


@dataclass
class Baselines:
    """Four baselines: mean / region / operator / region_x_operator."""

    global_mean_trig: np.ndarray   # shape (n_components,)
    per_region_trig: Dict[str, np.ndarray]
    per_operator_trig: Dict[str, np.ndarray]
    per_cell_trig: Dict[Tuple[str, str], np.ndarray]
    n_components: int

    @classmethod
    def fit(
        cls,
        train_records: Sequence[LearnerRecord],
        n_components: int,
    ) -> "Baselines":
        if not train_records:
            return cls(
                global_mean_trig=np.zeros(n_components, dtype=float),
                per_region_trig={},
                per_operator_trig={},
                per_cell_trig={},
                n_components=n_components,
            )
        ys = np.stack([r.y_triggered for r in train_records])
        ws = np.array([r.weight for r in train_records], dtype=float)
        gw = ws.sum()
        global_mean = (ys * ws[:, None]).sum(axis=0) / max(gw, 1e-12)

        # Per-region
        by_region_y: Dict[str, List[np.ndarray]] = defaultdict(list)
        by_region_w: Dict[str, List[float]] = defaultdict(list)
        by_op_y: Dict[str, List[np.ndarray]] = defaultdict(list)
        by_op_w: Dict[str, List[float]] = defaultdict(list)
        by_cell_y: Dict[Tuple[str, str], List[np.ndarray]] = defaultdict(list)
        by_cell_w: Dict[Tuple[str, str], List[float]] = defaultdict(list)

        for r in train_records:
            by_region_y[r.region].append(r.y_triggered)
            by_region_w[r.region].append(r.weight)
            by_op_y[r.operator].append(r.y_triggered)
            by_op_w[r.operator].append(r.weight)
            by_cell_y[(r.region, r.operator)].append(r.y_triggered)
            by_cell_w[(r.region, r.operator)].append(r.weight)

        def _wmean(ys: List[np.ndarray], ws: List[float]) -> np.ndarray:
            ya = np.stack(ys)
            wa = np.asarray(ws, dtype=float)
            tot = wa.sum()
            return (ya * wa[:, None]).sum(axis=0) / max(tot, 1e-12)

        per_region = {k: _wmean(v, by_region_w[k]) for k, v in by_region_y.items()}
        per_op = {k: _wmean(v, by_op_w[k]) for k, v in by_op_y.items()}
        per_cell = {k: _wmean(v, by_cell_w[k]) for k, v in by_cell_y.items()}

        return cls(
            global_mean_trig=global_mean,
            per_region_trig=per_region,
            per_operator_trig=per_op,
            per_cell_trig=per_cell,
            n_components=n_components,
        )

    def predict(self, records: Sequence[LearnerRecord], *, kind: str) -> np.ndarray:
        """Return shape (n, n_components) predictions for ``records``.

        ``kind`` is one of {"global", "region", "operator", "cell"}.
        Falls back through the hierarchy when a key is missing in
        train: cell -> region+operator -> region -> operator -> global.
        """
        out = np.zeros((len(records), self.n_components), dtype=float)
        for i, r in enumerate(records):
            if kind == "global":
                out[i] = self.global_mean_trig
            elif kind == "region":
                out[i] = self.per_region_trig.get(r.region, self.global_mean_trig)
            elif kind == "operator":
                out[i] = self.per_operator_trig.get(
                    r.operator, self.global_mean_trig
                )
            elif kind == "cell":
                v = self.per_cell_trig.get((r.region, r.operator))
                if v is None:
                    v = self.per_region_trig.get(r.region)
                if v is None:
                    v = self.per_operator_trig.get(r.operator)
                if v is None:
                    v = self.global_mean_trig
                out[i] = v
            else:
                raise ValueError(f"unknown baseline kind {kind!r}")
        # Clip floating-point roundoff (weighted mean can produce
        # 1.0000000000000002 when all weights agree on triggered=1).
        np.clip(out, 0.0, 1.0, out=out)
        return out


# ---------------------------------------------------------------------------
# The learner: per-component logistic + linear regression
# ---------------------------------------------------------------------------


@dataclass
class Learner:
    """Per-component logistic + linear regression bundle."""

    triggered_models: List[Optional[LogisticRegression]]
    margin_models: List[Optional[LinearRegression]]
    region_encoder: OneHotEncoder
    operator_encoder: OneHotEncoder
    component_names: Tuple[str, ...]
    train_global_mean_trig: np.ndarray  # fallback for degenerate components

    @classmethod
    def fit(
        cls,
        train_records: Sequence[LearnerRecord],
        component_names: Tuple[str, ...] = CANONICAL_COMPONENTS,
        *,
        random_state: int = 42,
    ) -> "Learner":
        n_components = len(component_names)
        X, region_enc, operator_enc = _build_feature_matrix(train_records)
        Y_trig = np.stack([r.y_triggered for r in train_records])
        Y_marg = np.stack([r.y_margin for r in train_records])
        W = np.array([r.weight for r in train_records], dtype=float)
        global_mean_trig = (
            (Y_trig * W[:, None]).sum(axis=0) / max(W.sum(), 1e-12)
        )

        triggered_models: List[Optional[LogisticRegression]] = []
        margin_models: List[Optional[LinearRegression]] = []

        for j in range(n_components):
            yj = Y_trig[:, j]
            uniq = np.unique(yj)
            if len(uniq) < 2:
                # Degenerate: all 0s or all 1s -> no logistic possible.
                triggered_models.append(None)
            else:
                clf = LogisticRegression(
                    max_iter=2000,
                    random_state=random_state,
                    solver="liblinear",
                )
                clf.fit(X, yj, sample_weight=W)
                triggered_models.append(clf)

            mj = Y_marg[:, j]
            mask = ~np.isnan(mj)
            if mask.sum() < 5:
                margin_models.append(None)
            else:
                Xj = X[mask]
                wj = W[mask]
                yjm = mj[mask]
                lr = LinearRegression()
                lr.fit(Xj, yjm, sample_weight=wj)
                margin_models.append(lr)

        return cls(
            triggered_models=triggered_models,
            margin_models=margin_models,
            region_encoder=region_enc,
            operator_encoder=operator_enc,
            component_names=component_names,
            train_global_mean_trig=global_mean_trig,
        )

    def predict_proba(self, records: Sequence[LearnerRecord]) -> np.ndarray:
        """Probability of triggered=True per component. Shape (n, K)."""
        if not records:
            return np.zeros((0, len(self.component_names)), dtype=float)
        X, _, _ = _build_feature_matrix(
            records,
            region_encoder=self.region_encoder,
            operator_encoder=self.operator_encoder,
        )
        out = np.zeros((len(records), len(self.component_names)), dtype=float)
        for j, m in enumerate(self.triggered_models):
            if m is None:
                # All training records had identical triggered for this
                # component; predict the train mean.
                out[:, j] = float(self.train_global_mean_trig[j])
            else:
                # liblinear gives binary [P(0), P(1)]; take col 1
                p = m.predict_proba(X)
                if p.shape[1] == 1:
                    # only one class seen in train (shouldn't happen given
                    # uniq check, but defensive)
                    out[:, j] = m.classes_[0]
                else:
                    out[:, j] = p[:, list(m.classes_).index(1.0)]
        return out

    def predict_margin(self, records: Sequence[LearnerRecord]) -> np.ndarray:
        """Margin prediction per component. Shape (n, K). NaN where no
        margin model could be fit."""
        if not records:
            return np.zeros((0, len(self.component_names)), dtype=float)
        X, _, _ = _build_feature_matrix(
            records,
            region_encoder=self.region_encoder,
            operator_encoder=self.operator_encoder,
        )
        out = np.full((len(records), len(self.component_names)),
                      np.nan, dtype=float)
        for j, m in enumerate(self.margin_models):
            if m is None:
                continue
            out[:, j] = m.predict(X)
        return out

    def predict_kill_vector(
        self, records: Sequence[LearnerRecord]
    ) -> np.ndarray:
        """Combined predicted (n, K) triggered-prob vector for L2 norm
        computations downstream. Equivalent to predict_proba; the margin
        layer is reported separately."""
        return self.predict_proba(records)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def _safe_brier(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return float("nan")
    return float(brier_score_loss(y_true, np.clip(y_pred, 0.0, 1.0)))


def _safe_auc(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return float("nan")
    if len(np.unique(y_true)) < 2:
        return float("nan")
    try:
        return float(roc_auc_score(y_true, y_pred))
    except Exception:
        return float("nan")


def _accuracy(y_true: np.ndarray, y_pred_prob: np.ndarray) -> float:
    if len(y_true) == 0:
        return float("nan")
    pred = (y_pred_prob >= 0.5).astype(float)
    return float(np.mean(pred == y_true))


def per_component_metrics(
    records: Sequence[LearnerRecord],
    pred_trig: np.ndarray,
    component_names: Tuple[str, ...],
) -> Dict[str, Dict[str, float]]:
    """For each component, compute classification metrics on the held-out
    set."""
    Y = np.stack([r.y_triggered for r in records]) if records else np.zeros(
        (0, len(component_names))
    )
    out: Dict[str, Dict[str, float]] = {}
    for j, name in enumerate(component_names):
        yj = Y[:, j] if Y.size else np.zeros(0)
        pj = pred_trig[:, j] if pred_trig.size else np.zeros(0)
        out[name] = {
            "accuracy": _accuracy(yj, pj),
            "auc": _safe_auc(yj, pj),
            "brier": _safe_brier(yj, pj),
            "n_positive": int((yj == 1.0).sum()),
            "n_total": int(len(yj)),
        }
    return out


def overall_kill_vector_mae(
    records: Sequence[LearnerRecord],
    pred_trig: np.ndarray,
) -> float:
    """Per-record L1 norm averaged over records: MAE of the predicted
    triggered vector. Lower = better."""
    if not records:
        return float("nan")
    Y = np.stack([r.y_triggered for r in records])
    return float(np.mean(np.abs(Y - pred_trig)))


def operator_chart_recovery(
    records: Sequence[LearnerRecord],
    pred_trig: np.ndarray,
) -> Dict[str, Dict[str, Any]]:
    """For each operator in the held-out set, compute:
      * empirical_E[k|operator] from y_triggered
      * model_E[k|operator] from pred_trig
      * L1 distance per component

    This is the killer question (per ChatGPT): does the model recover
    the operator coordinate chart?
    """
    by_op_y: Dict[str, List[np.ndarray]] = defaultdict(list)
    by_op_p: Dict[str, List[np.ndarray]] = defaultdict(list)
    for i, r in enumerate(records):
        by_op_y[r.operator].append(r.y_triggered)
        by_op_p[r.operator].append(pred_trig[i])

    out: Dict[str, Dict[str, Any]] = {}
    for op, ys in by_op_y.items():
        Y = np.stack(ys)
        P = np.stack(by_op_p[op])
        emp = Y.mean(axis=0)
        mod = P.mean(axis=0)
        out[op] = {
            "n": len(ys),
            "empirical_mean": emp.tolist(),
            "model_mean": mod.tolist(),
            "l1_distance": float(np.abs(emp - mod).sum()),
        }
    return out


# ---------------------------------------------------------------------------
# End-to-end pipeline
# ---------------------------------------------------------------------------


@dataclass
class LearnerEvalResult:
    """The full learner-vs-baselines comparison."""

    dataset_stats: Dict[str, Any]
    n_train: int
    n_val: int
    n_test: int
    component_names: Tuple[str, ...]
    learner_metrics: Dict[str, Dict[str, float]]
    learner_kv_mae: float
    baseline_metrics: Dict[str, Dict[str, Dict[str, float]]]  # kind -> comp -> metric
    baseline_kv_mae: Dict[str, float]
    operator_chart_recovery: Dict[str, Dict[str, Any]]
    per_region_metrics: Dict[str, Dict[str, float]]
    verdict: str
    rationale: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "dataset_stats": self.dataset_stats,
            "n_train": self.n_train,
            "n_val": self.n_val,
            "n_test": self.n_test,
            "component_names": list(self.component_names),
            "learner_metrics": self.learner_metrics,
            "learner_kv_mae": self.learner_kv_mae,
            "baseline_metrics": self.baseline_metrics,
            "baseline_kv_mae": self.baseline_kv_mae,
            "operator_chart_recovery": self.operator_chart_recovery,
            "per_region_metrics": self.per_region_metrics,
            "verdict": self.verdict,
            "rationale": self.rationale,
        }


def _per_region_breakdown(
    test_records: Sequence[LearnerRecord],
    pred_trig: np.ndarray,
) -> Dict[str, Dict[str, float]]:
    by_region_idx: Dict[str, List[int]] = defaultdict(list)
    for i, r in enumerate(test_records):
        by_region_idx[r.region].append(i)
    out: Dict[str, Dict[str, float]] = {}
    for region, idxs in by_region_idx.items():
        if not idxs:
            continue
        Y = np.stack([test_records[i].y_triggered for i in idxs])
        P = pred_trig[idxs]
        out[region] = {
            "n": float(len(idxs)),
            "kv_mae": float(np.mean(np.abs(Y - P))),
            "macro_accuracy": float(
                np.mean(((P >= 0.5).astype(float) == Y).astype(float))
            ),
        }
    return out


def _verdict_from_mae(
    learner_mae: float,
    cell_baseline_mae: float,
    region_baseline_mae: float,
) -> Tuple[str, str]:
    """Apply the A/B/C verdict dispatch."""
    eps = 0.005
    if not math.isfinite(learner_mae) or not math.isfinite(cell_baseline_mae):
        return "C_REPRESENTATION_ISSUE", (
            f"Non-finite MAE (learner={learner_mae}, cell={cell_baseline_mae})"
            " — investigate before Day 5."
        )
    if learner_mae < cell_baseline_mae - eps:
        return "A_BEATS_CELL_MEAN", (
            f"Learner MAE {learner_mae:.4f} beats region x operator cell-mean"
            f" baseline {cell_baseline_mae:.4f} by {cell_baseline_mae - learner_mae:.4f}."
            " Substrate has a learnable gradient field beyond table lookup;"
            " Day 5 navigation is well-founded."
        )
    if learner_mae > cell_baseline_mae + eps:
        return "C_UNDERPERFORMS_CELL_MEAN", (
            f"Learner MAE {learner_mae:.4f} is worse than cell-mean"
            f" baseline {cell_baseline_mae:.4f}. Possible bug or"
            " representation mismatch — investigate."
        )
    return "B_MATCHES_CELL_MEAN", (
        f"Learner MAE {learner_mae:.4f} ≈ cell-mean baseline"
        f" {cell_baseline_mae:.4f} (within {eps}). No generalization beyond"
        " memorization; Day 5 navigation is just lookup. Need denser data"
        " or new operators to find generalisable signal."
    )


def run_learner(
    base_dir: str = PROMETHEUS_MATH_DIR,
    *,
    test_size: float = 0.20,
    val_size: float = 0.10,
    random_state: int = 42,
    expand_to_individual: bool = True,
    max_per_cell: int = 5000,
) -> LearnerEvalResult:
    """End-to-end: load -> backfill -> split -> train -> eval -> report."""
    dataset = build_dataset(
        base_dir,
        expand_to_individual=expand_to_individual,
        max_per_cell=max_per_cell,
    )
    if dataset.n == 0:
        empty_metrics = {
            n: {"accuracy": float("nan"), "auc": float("nan"),
                "brier": float("nan"), "n_positive": 0, "n_total": 0}
            for n in CANONICAL_COMPONENTS
        }
        return LearnerEvalResult(
            dataset_stats=dataset.stats(),
            n_train=0, n_val=0, n_test=0,
            component_names=CANONICAL_COMPONENTS,
            learner_metrics=empty_metrics,
            learner_kv_mae=float("nan"),
            baseline_metrics={},
            baseline_kv_mae={},
            operator_chart_recovery={},
            per_region_metrics={},
            verdict="C_REPRESENTATION_ISSUE",
            rationale="Empty dataset.",
        )

    train_idx, val_idx, test_idx = stratified_split(
        dataset, test_size=test_size, val_size=val_size,
        random_state=random_state,
    )
    train_records = [dataset.records[i] for i in train_idx]
    test_records = [dataset.records[i] for i in test_idx]

    learner = Learner.fit(train_records, random_state=random_state)
    baselines = Baselines.fit(train_records, dataset.n_components)

    pred_learner = learner.predict_proba(test_records)
    pred_global = baselines.predict(test_records, kind="global")
    pred_region = baselines.predict(test_records, kind="region")
    pred_operator = baselines.predict(test_records, kind="operator")
    pred_cell = baselines.predict(test_records, kind="cell")

    learner_metrics = per_component_metrics(
        test_records, pred_learner, CANONICAL_COMPONENTS
    )
    baseline_metrics = {
        "global": per_component_metrics(
            test_records, pred_global, CANONICAL_COMPONENTS
        ),
        "region": per_component_metrics(
            test_records, pred_region, CANONICAL_COMPONENTS
        ),
        "operator": per_component_metrics(
            test_records, pred_operator, CANONICAL_COMPONENTS
        ),
        "cell": per_component_metrics(
            test_records, pred_cell, CANONICAL_COMPONENTS
        ),
    }
    learner_kv_mae = overall_kill_vector_mae(test_records, pred_learner)
    baseline_kv_mae = {
        "global": overall_kill_vector_mae(test_records, pred_global),
        "region": overall_kill_vector_mae(test_records, pred_region),
        "operator": overall_kill_vector_mae(test_records, pred_operator),
        "cell": overall_kill_vector_mae(test_records, pred_cell),
    }
    chart_recov = operator_chart_recovery(test_records, pred_learner)
    per_region = _per_region_breakdown(test_records, pred_learner)

    verdict, rationale = _verdict_from_mae(
        learner_kv_mae, baseline_kv_mae["cell"], baseline_kv_mae["region"]
    )

    return LearnerEvalResult(
        dataset_stats=dataset.stats(),
        n_train=len(train_idx),
        n_val=len(val_idx),
        n_test=len(test_idx),
        component_names=CANONICAL_COMPONENTS,
        learner_metrics=learner_metrics,
        learner_kv_mae=learner_kv_mae,
        baseline_metrics=baseline_metrics,
        baseline_kv_mae=baseline_kv_mae,
        operator_chart_recovery=chart_recov,
        per_region_metrics=per_region,
        verdict=verdict,
        rationale=rationale,
    )


def render_report(res: LearnerEvalResult) -> str:
    """Render the human-readable Markdown report."""
    parts: List[str] = []
    parts.append("# Kill Vector Learner — Day 4 Results")
    parts.append("")
    parts.append("Empirical test of \"is the gradient field even learnable")
    parts.append("from the existing ledger?\"")
    parts.append("")
    parts.append("Plain regression (no RL, no neural net): for each of the")
    parts.append(f"{len(res.component_names)} kill_vector components, train one")
    parts.append("logistic regression for `triggered` and one linear regression")
    parts.append("for `margin`. Compare against four baselines — the strongest")
    parts.append("(region x operator cell-mean) is the upper bound for")
    parts.append("\"no learning, just look up the table.\"")
    parts.append("")
    parts.append("## Setup")
    parts.append("")
    parts.append("- Inputs: region encoding (degree, alphabet_width,")
    parts.append("  reward_shape, env) + operator one-hot")
    parts.append(f"- Targets: {len(res.component_names)} kill_vector components")
    parts.append("  -- (triggered: bool, margin: float | None)")
    parts.append("- Stratified split by region, random seed = 42")
    parts.append("")

    parts.append("## Dataset")
    parts.append("")
    s = res.dataset_stats
    parts.append(f"- Records: **{s.get('n_records', 0):,}**")
    parts.append(f"- Components: **{s.get('n_components', 0)}**")
    parts.append(f"- Regions: **{s.get('n_regions', 0)}**")
    parts.append(f"- Operators: **{s.get('n_operators', 0)}**")
    rows, cols = s.get("coverage_matrix_shape", (0, 0))
    parts.append(f"- Coverage matrix: **{rows} regions x {cols} operators**")
    parts.append(
        f"- Non-empty cells: **{s.get('n_nonempty_cells', 0)}**"
        f" / **{rows * cols}**"
        f" (sparseness = {s.get('sparseness', 0):.1%})"
    )
    parts.append("")
    parts.append(f"- Train: {res.n_train:,}")
    parts.append(f"- Val: {res.n_val:,}")
    parts.append(f"- Test: {res.n_test:,}")
    parts.append("")

    parts.append("## Per-region records")
    parts.append("")
    per_reg = s.get("per_region_records", {})
    for region, n in sorted(per_reg.items(), key=lambda kv: -kv[1]):
        parts.append(f"- `{region}`: {n:,}")
    parts.append("")

    parts.append("## Per-operator records")
    parts.append("")
    per_op = s.get("per_operator_records", {})
    for op, n in sorted(per_op.items(), key=lambda kv: -kv[1]):
        parts.append(f"- `{op}`: {n:,}")
    parts.append("")

    parts.append("## Held-out kill_vector MAE (lower is better)")
    parts.append("")
    parts.append(f"- **Learner**: {res.learner_kv_mae:.4f}")
    for kind, mae in res.baseline_kv_mae.items():
        parts.append(f"- Baseline ({kind}): {mae:.4f}")
    parts.append("")

    parts.append("## Per-component metrics (test set)")
    parts.append("")
    parts.append("| Component | Learner Acc | Learner AUC | Cell Acc | Cell AUC | Region Acc | n_pos / n_total |")
    parts.append("|---|---|---|---|---|---|---|")
    for name in res.component_names:
        L = res.learner_metrics.get(name, {})
        C = res.baseline_metrics.get("cell", {}).get(name, {})
        R = res.baseline_metrics.get("region", {}).get(name, {})
        parts.append(
            "| `{name}` | {la:.3f} | {lau:.3f} | {ca:.3f} | {cau:.3f}"
            " | {ra:.3f} | {np}/{nt} |".format(
                name=name,
                la=L.get("accuracy", float("nan")),
                lau=L.get("auc", float("nan")),
                ca=C.get("accuracy", float("nan")),
                cau=C.get("auc", float("nan")),
                ra=R.get("accuracy", float("nan")),
                np=L.get("n_positive", 0),
                nt=L.get("n_total", 0),
            )
        )
    parts.append("")

    parts.append("## Per-region performance")
    parts.append("")
    parts.append("| Region | n | KV MAE | Macro Acc |")
    parts.append("|---|---|---|---|")
    for region, m in sorted(
        res.per_region_metrics.items(), key=lambda kv: -kv[1]["n"]
    ):
        parts.append(
            f"| `{region}` | {int(m['n']):,} | {m['kv_mae']:.4f}"
            f" | {m['macro_accuracy']:.3f} |"
        )
    parts.append("")

    parts.append("## Operator coordinate chart recovery")
    parts.append("")
    parts.append("Per ChatGPT: does the learner reproduce the empirical")
    parts.append("E[k|operator] over held-out data?")
    parts.append("")
    parts.append("| Operator | n | L1 (empirical, model) |")
    parts.append("|---|---|---|")
    for op, m in sorted(
        res.operator_chart_recovery.items(), key=lambda kv: -kv[1]["n"]
    ):
        parts.append(f"| `{op}` | {m['n']:,} | {m['l1_distance']:.4f} |")
    parts.append("")

    parts.append("## Verdict")
    parts.append("")
    parts.append(f"**{res.verdict}**")
    parts.append("")
    parts.append(res.rationale)
    parts.append("")
    parts.append("## Honest framing")
    parts.append("")
    parts.append(
        "This is a small learner on noisy categorical data. A positive"
        " result is a *substrate* signal (the ledger has learnable"
        " (region, operator) -> kill structure), not mathematical"
        " capability. The Lehmer brute-force PROMOTE rate remains 0;"
        " every kill in this dataset is a near-miss in the kill-space"
        " geometry, not a ground-truth target."
    )
    parts.append("")
    parts.append(
        "Crucially, the legacy ledger only logs the *first-failing*"
        " kill, so triggered=False for non-firing components is a"
        " conservative conditional rather than a measured outcome."
        " Margin recovery from aggregated counts is impossible (we"
        " never persisted margins for the upstream:* labels), so the"
        " margin-side of the learner is empty for legacy data; only"
        " freshly captured kill_vectors will populate it."
    )
    parts.append("")
    return "\n".join(parts)


def write_report(
    res: LearnerEvalResult,
    *,
    json_path: Optional[str] = None,
    md_path: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Persist the result. Both paths optional; returns the actual paths
    written (None if not requested)."""
    j_out: Optional[str] = None
    m_out: Optional[str] = None
    if json_path is not None:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(res.as_dict(), f, indent=2, sort_keys=True)
        j_out = json_path
    if md_path is not None:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(render_report(res))
        m_out = md_path
    return j_out, m_out


__all__ = [
    "CANONICAL_COMPONENTS",
    "LEGACY_UPSTREAM_TO_COMPONENT",
    "Baselines",
    "Dataset",
    "Learner",
    "LearnerEvalResult",
    "LearnerRecord",
    "build_dataset",
    "operator_chart_recovery",
    "overall_kill_vector_mae",
    "per_component_metrics",
    "render_report",
    "run_learner",
    "stratified_split",
    "write_report",
]
