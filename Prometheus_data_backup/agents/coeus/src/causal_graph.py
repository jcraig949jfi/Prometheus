"""
causal_graph.py — Build causal graph from Nous + Hephaestus data.

Uses NOTEARS for structure learning if causal-learn is available,
falls back to regularized regression for causal influence estimation.
LiNGAM runs on the continuous score dimensions.

The output is a CausalGraph object containing:
    - concept_influence: per-concept causal effect on each outcome
    - pair_synergy: interaction effects for concept pairs
    - score_dag: causal ordering among score dimensions
    - field_effects: per-field aggregate causal effects
"""

import json
import logging
from pathlib import Path

import numpy as np

log = logging.getLogger("coeus.causal")

# Optional imports — degrade gracefully
try:
    from causallearn.search.FCMBased import lingam as cl_lingam
    from causallearn.search.ScoreBased.GES import ges
    HAS_CAUSAL_LEARN = True
except ImportError:
    HAS_CAUSAL_LEARN = False
    log.info("causal-learn not installed; using regression fallback")

try:
    from causallearn.search.ConstraintBased.FCI import fci
    HAS_FCI = True
except ImportError:
    HAS_FCI = False

try:
    import lingam as lingam_pkg
    HAS_LINGAM = True
except ImportError:
    HAS_LINGAM = False
    log.info("lingam not installed; skipping LiNGAM analysis")

try:
    from dagma.nonlinear import DagmaMLP, DagmaNonlinear
    HAS_DAGMA = True
except ImportError:
    HAS_DAGMA = False


class CausalGraph:
    """Container for causal analysis results."""

    def __init__(self):
        self.concept_names = []        # all unique concept names
        self.concept_influence = {}    # concept -> {forge_effect, reasoning_effect, ...}
        self.pair_synergy = {}         # "A + B" -> synergy score
        self.score_dag = {}            # score_dim -> list of (parent_dim, weight)
        self.field_effects = {}        # field -> {forge_effect, ...}
        self.forge_rate_by_concept = {}  # concept -> forge success rate
        self.confounders = {}          # concept -> FCI confounder status
        self.interventional = {}       # concept -> {drop_probability, counterfactual}
        self.dagma_divergences = []    # list of {concept, type, linear, nonlinear, message}
        self.n_observations = 0
        self.n_forged = 0
        self.method = "none"

    def to_dict(self) -> dict:
        return {
            "concept_influence": self.concept_influence,
            "pair_synergy": dict(sorted(self.pair_synergy.items(),
                                        key=lambda x: abs(x[1]), reverse=True)[:50]),
            "score_dag": self.score_dag,
            "field_effects": self.field_effects,
            "forge_rate_by_concept": self.forge_rate_by_concept,
            "confounders": self.confounders,
            "interventional": self.interventional,
            "dagma_divergences": self.dagma_divergences,
            "n_observations": self.n_observations,
            "n_forged": self.n_forged,
            "method": self.method,
        }

    def save(self, path: Path):
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "CausalGraph":
        data = json.loads(path.read_text(encoding="utf-8"))
        g = cls()
        g.concept_influence = data.get("concept_influence", {})
        g.pair_synergy = data.get("pair_synergy", {})
        g.score_dag = data.get("score_dag", {})
        g.field_effects = data.get("field_effects", {})
        g.forge_rate_by_concept = data.get("forge_rate_by_concept", {})
        g.confounders = data.get("confounders", {})
        g.interventional = data.get("interventional", {})
        g.n_observations = data.get("n_observations", 0)
        g.n_forged = data.get("n_forged", 0)
        g.method = data.get("method", "loaded")
        return g


def _encode_dataset(nous_entries: list[dict], ledger: dict,
                    combo_key_fn) -> tuple[np.ndarray, list[str], list[str]]:
    """Encode Nous + ledger data into a numeric matrix for causal analysis.

    Returns:
        X: (n_samples, n_features) array
        feature_names: list of column names
        concept_names: list of all unique concepts
    """
    # Collect all unique concepts
    all_concepts = set()
    for entry in nous_entries:
        for name in entry.get("concept_names", []):
            all_concepts.add(name)
    concept_list = sorted(all_concepts)
    concept_idx = {c: i for i, c in enumerate(concept_list)}

    # Collect all unique fields
    all_fields = set()
    for entry in nous_entries:
        for field in entry.get("concept_fields", []):
            all_fields.add(field)
    field_list = sorted(all_fields)
    field_idx = {f: i for i, f in enumerate(field_list)}

    # Feature columns:
    # [concept_0..concept_N, field_0..field_M, reasoning, metacog, hypothesis, implement,
    #  composite, forge_attempted, forge_success, accuracy, calibration,
    #  margin_accuracy, margin_calibration]
    n_concepts = len(concept_list)
    n_fields = len(field_list)
    n_scores = 5  # reasoning, metacog, hypothesis, implement, composite
    n_outcomes = 6  # forge_attempted, forge_success, accuracy, calibration, margin_acc, margin_cal
    n_features = n_concepts + n_fields + n_scores + n_outcomes

    feature_names = (
        [f"concept:{c}" for c in concept_list]
        + [f"field:{f}" for f in field_list]
        + ["reasoning", "metacognition", "hypothesis_generation",
           "implementability", "composite_score"]
        + ["forge_attempted", "forge_success", "accuracy", "calibration",
           "margin_accuracy", "margin_calibration"]
    )

    X = np.zeros((len(nous_entries), n_features), dtype=np.float64)

    for row, entry in enumerate(nous_entries):
        # Concept indicators
        for name in entry.get("concept_names", []):
            X[row, concept_idx[name]] = 1.0

        # Field indicators
        for field in entry.get("concept_fields", []):
            X[row, n_concepts + field_idx[field]] = 1.0

        # Scores
        score = entry.get("score", {})
        ratings = score.get("ratings", {})
        col_base = n_concepts + n_fields
        X[row, col_base + 0] = (ratings.get("reasoning") or 0) / 10.0
        X[row, col_base + 1] = (ratings.get("metacognition") or 0) / 10.0
        X[row, col_base + 2] = (ratings.get("hypothesis_generation") or 0) / 10.0
        X[row, col_base + 3] = (ratings.get("implementability") or 0) / 10.0
        X[row, col_base + 4] = (score.get("composite_score") or 0) / 10.0

        # Outcomes from ledger
        key = combo_key_fn(entry)
        ledger_entry = ledger.get(key)
        outcome_base = col_base + n_scores
        if ledger_entry is not None:
            X[row, outcome_base + 0] = 1.0  # attempted
            X[row, outcome_base + 1] = 1.0 if ledger_entry.get("status") == "forged" else 0.0
            X[row, outcome_base + 2] = ledger_entry.get("accuracy", 0.0)
            X[row, outcome_base + 3] = ledger_entry.get("calibration", 0.0)
            # Margin over NCD baseline (what the tool adds beyond compression)
            X[row, outcome_base + 4] = ledger_entry.get("margin_accuracy", 0.0)
            X[row, outcome_base + 5] = ledger_entry.get("margin_calibration", 0.0)

    return X, feature_names, concept_list


def _regression_influence(X: np.ndarray, feature_names: list[str],
                          concept_names: list[str]) -> CausalGraph:
    """Estimate causal influence via L1-regularized logistic/linear regression.

    This is the fallback when causal-learn is not available. It's not true
    causal discovery but provides useful conditional associations.
    """
    from sklearn.linear_model import LogisticRegression, Lasso
    from sklearn.preprocessing import StandardScaler

    graph = CausalGraph()
    graph.concept_names = concept_names
    graph.method = "lasso_regression"

    n_concepts = len(concept_names)
    outcome_cols = {name: i for i, name in enumerate(feature_names)}

    # --- Concept influence on forge success ---
    forge_col = outcome_cols["forge_success"]
    attempted_col = outcome_cols["forge_attempted"]

    # Only use rows where forge was attempted
    attempted_mask = X[:, attempted_col] > 0.5
    if attempted_mask.sum() >= 10:
        X_attempted = X[attempted_mask]
        y_forge = X_attempted[:, forge_col]

        # Features: concept indicators + score dimensions
        score_cols = [outcome_cols[s] for s in
                      ["reasoning", "metacognition", "hypothesis_generation",
                       "implementability", "composite_score"]]
        feature_cols = list(range(n_concepts)) + score_cols
        X_feat = X_attempted[:, feature_cols]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_feat)

        if len(np.unique(y_forge)) >= 2:
            lr = LogisticRegression(penalty="l1", solver="liblinear", C=1.0, max_iter=1000)
            lr.fit(X_scaled, y_forge)
            coefs = lr.coef_[0]

            for i, concept in enumerate(concept_names):
                graph.concept_influence[concept] = {
                    "forge_effect": round(float(coefs[i]), 4),
                }

            # Score dimension effects
            score_names = ["reasoning", "metacognition", "hypothesis_generation",
                           "implementability", "composite_score"]
            for j, sname in enumerate(score_names):
                idx = n_concepts + j
                graph.score_dag[sname] = round(float(coefs[idx]), 4)

    # --- Concept influence on reasoning score (using all data) ---
    reasoning_col = outcome_cols["reasoning"]
    y_reasoning = X[:, reasoning_col]

    if y_reasoning.std() > 0.01:
        X_concepts = X[:, :n_concepts]
        lasso = Lasso(alpha=0.01, max_iter=5000)
        lasso.fit(X_concepts, y_reasoning)
        for i, concept in enumerate(concept_names):
            if concept not in graph.concept_influence:
                graph.concept_influence[concept] = {}
            graph.concept_influence[concept]["reasoning_effect"] = round(float(lasso.coef_[i]), 4)

    # --- Pair synergy (interaction terms for top concepts) ---
    # Only compute for concepts with non-zero influence
    active = [c for c, v in graph.concept_influence.items()
              if abs(v.get("forge_effect", 0)) > 0.01 or abs(v.get("reasoning_effect", 0)) > 0.01]

    if attempted_mask.sum() >= 10 and len(active) >= 2:
        for i, c1 in enumerate(active):
            for c2 in active[i+1:]:
                idx1 = concept_names.index(c1)
                idx2 = concept_names.index(c2)
                # Co-occurrence in attempted forges
                both = X_attempted[:, idx1] * X_attempted[:, idx2]
                if both.sum() >= 2:
                    # Synergy = forge rate when both present vs expected
                    rate_both = X_attempted[both > 0.5, forge_col].mean() if both.sum() > 0 else 0
                    rate_1 = X_attempted[X_attempted[:, idx1] > 0.5, forge_col].mean()
                    rate_2 = X_attempted[X_attempted[:, idx2] > 0.5, forge_col].mean()
                    expected = rate_1 * rate_2
                    synergy = rate_both - expected
                    if abs(synergy) > 0.01:
                        graph.pair_synergy[f"{c1} + {c2}"] = round(float(synergy), 4)

    # --- Field effects ---
    field_cols = [i for i, name in enumerate(feature_names) if name.startswith("field:")]
    if attempted_mask.sum() >= 10 and len(np.unique(X[attempted_mask, forge_col])) >= 2:
        X_fields = X[attempted_mask][:, field_cols]
        y_forge = X[attempted_mask, forge_col]
        if X_fields.shape[1] > 0:
            lasso_f = Lasso(alpha=0.01, max_iter=5000)
            lasso_f.fit(X_fields, y_forge)
            for j, fi in enumerate(field_cols):
                fname = feature_names[fi].replace("field:", "")
                if abs(lasso_f.coef_[j]) > 0.001:
                    graph.field_effects[fname] = round(float(lasso_f.coef_[j]), 4)

    # --- Forge rate by concept ---
    if attempted_mask.sum() > 0:
        X_attempted = X[attempted_mask]
        for i, concept in enumerate(concept_names):
            present = X_attempted[:, i] > 0.5
            if present.sum() > 0:
                rate = X_attempted[present, forge_col].mean()
                graph.forge_rate_by_concept[concept] = round(float(rate), 4)

    graph.n_observations = X.shape[0]
    graph.n_forged = int(X[:, outcome_cols["forge_success"]].sum())

    return graph


def _notears_analysis(X: np.ndarray, feature_names: list[str],
                      concept_names: list[str]) -> dict:
    """Run NOTEARS on the continuous score + outcome submatrix.

    Returns adjacency dict for the score DAG.
    """
    if not HAS_CAUSAL_LEARN:
        return {}

    # Extract only continuous columns (scores + outcomes)
    score_outcome_names = [
        "reasoning", "metacognition", "hypothesis_generation",
        "implementability", "composite_score",
        "forge_success", "accuracy", "calibration",
    ]
    col_indices = [i for i, name in enumerate(feature_names) if name in score_outcome_names]

    if len(col_indices) < 3:
        return {}

    X_sub = X[:, col_indices]
    # Remove rows with all zeros (non-attempted)
    mask = X_sub.sum(axis=1) > 0
    X_sub = X_sub[mask]

    if X_sub.shape[0] < 30:
        log.warning("Too few observations for NOTEARS (%d)", X_sub.shape[0])
        return {}

    try:
        record = ges(X_sub)
        adj = record['G'].graph  # adjacency matrix
        dag = {}
        names = [score_outcome_names[i] for i in range(len(col_indices))]
        for i, name in enumerate(names):
            parents = []
            for j in range(len(names)):
                if adj[j, i] != 0 and i != j:
                    parents.append((names[j], round(float(adj[j, i]), 4)))
            if parents:
                dag[name] = parents
        return dag
    except Exception as e:
        log.warning("NOTEARS/GES failed: %s", e)
        return {}


def _lingam_analysis(X: np.ndarray, feature_names: list[str]) -> dict:
    """Run LiNGAM on continuous score dimensions.

    Returns causal ordering dict.
    """
    if not HAS_LINGAM:
        return {}

    score_names = ["reasoning", "metacognition", "hypothesis_generation",
                   "implementability", "composite_score"]
    col_indices = [i for i, name in enumerate(feature_names) if name in score_names]

    X_sub = X[:, col_indices]
    mask = X_sub.sum(axis=1) > 0
    X_sub = X_sub[mask]

    if X_sub.shape[0] < 30:
        return {}

    try:
        model = lingam_pkg.DirectLiNGAM()
        model.fit(X_sub)
        ordering = {}
        names = [score_names[i] for i in range(len(col_indices))]
        causal_order = model.causal_order_
        for rank, idx in enumerate(causal_order):
            ordering[names[idx]] = {
                "causal_rank": rank,
                "adjacency": {names[j]: round(float(model.adjacency_matrix_[idx, j]), 4)
                              for j in range(len(names))
                              if abs(model.adjacency_matrix_[idx, j]) > 0.01 and j != idx},
            }
        return ordering
    except Exception as e:
        log.warning("LiNGAM failed: %s", e)
        return {}


def _fci_confounder_analysis(X: np.ndarray, feature_names: list[str],
                             concept_names: list[str]) -> dict:
    """Run FCI to detect latent confounders between concepts and forge success.

    Returns dict: concept_name -> confounder status string.
    """
    if not HAS_FCI:
        return {}

    n_concepts = len(concept_names)
    outcome_cols = {name: i for i, name in enumerate(feature_names)}
    forge_col = outcome_cols.get("forge_success")
    attempted_col = outcome_cols.get("forge_attempted")

    if forge_col is None or attempted_col is None:
        return {}

    # Only use attempted rows, and limit to top-20 most active concepts + outcome
    attempted_mask = X[:, attempted_col] > 0.5
    if attempted_mask.sum() < 30:
        log.warning("Too few attempted forges for FCI (%d)", attempted_mask.sum())
        return {}

    X_att = X[attempted_mask]

    # Find concepts with enough presence (at least 5 occurrences in attempted)
    active_concepts = []
    active_indices = []
    for i, name in enumerate(concept_names):
        if X_att[:, i].sum() >= 5:
            active_concepts.append(name)
            active_indices.append(i)

    if len(active_concepts) < 3:
        return {}

    # Limit to top 25 most frequent to keep FCI tractable
    freqs = [(X_att[:, i].sum(), i, name) for i, name in zip(active_indices, active_concepts)]
    freqs.sort(reverse=True)
    top = freqs[:25]
    sel_indices = [t[1] for t in top]
    sel_names = [t[2] for t in top]

    # Build submatrix: selected concepts + forge_success
    cols = sel_indices + [forge_col]
    X_sub = X_att[:, cols]
    col_names = sel_names + ["forge_success"]

    try:
        G, edges = fci(X_sub, independence_test_method="fisherz", alpha=0.05,
                        verbose=False)
        graph_matrix = G.graph
        outcome_idx = len(sel_names)  # last column

        results = {}
        for i, concept in enumerate(sel_names):
            edge_to = graph_matrix[i, outcome_idx]
            edge_from = graph_matrix[outcome_idx, i]

            # Bidirectional arrow (2,2) = latent confounder
            if edge_to == 2 and edge_from == 2:
                results[concept] = "confounded"
            # Direct cause (tail->arrow = 3,2)
            elif edge_to == 2 and edge_from == 3:
                results[concept] = "direct_cause"
            # Possibly directed (circle->arrow = 1,2)
            elif edge_to == 2 and edge_from == 1:
                results[concept] = "possible_cause"
            elif edge_to != 0 or edge_from != 0:
                results[concept] = "associated"

        log.info("FCI: %d concepts analyzed, %d direct causes, %d confounded",
                 len(sel_names),
                 sum(1 for v in results.values() if v == "direct_cause"),
                 sum(1 for v in results.values() if v == "confounded"))
        return results

    except Exception as e:
        log.warning("FCI failed: %s", e)
        return {}


def _dagma_analysis(X: np.ndarray, feature_names: list[str],
                    concept_names: list[str]) -> dict:
    """Run DAGMA (non-linear) to capture concept synergies that linear models miss.

    Returns dict: concept_name -> non-linear forge effect.
    Only runs when we have enough data (200+ attempted forges).
    """
    if not HAS_DAGMA:
        return {}

    n_concepts = len(concept_names)
    outcome_cols = {name: i for i, name in enumerate(feature_names)}
    forge_col = outcome_cols.get("forge_success")
    attempted_col = outcome_cols.get("forge_attempted")

    if forge_col is None or attempted_col is None:
        return {}

    attempted_mask = X[:, attempted_col] > 0.5
    if attempted_mask.sum() < 200:
        log.info("DAGMA needs 200+ attempts, have %d — skipping", int(attempted_mask.sum()))
        return {}

    X_att = X[attempted_mask]

    # Select top-20 most frequent concepts + forge_success
    freqs = [(X_att[:, i].sum(), i, name) for i, name in enumerate(concept_names)
             if X_att[:, i].sum() >= 10]
    freqs.sort(reverse=True)
    top = freqs[:20]
    sel_indices = [t[1] for t in top]
    sel_names = [t[2] for t in top]

    cols = sel_indices + [forge_col]
    X_sub = X_att[:, cols].astype(np.float64)
    num_nodes = X_sub.shape[1]

    try:
        import torch
        eq_model = DagmaMLP(dims=[num_nodes, 12, 1], bias=True)
        model = DagmaNonlinear(eq_model)
        W_est = model.fit(X_sub, lambda1=0.02, lambda2=0.005)

        outcome_idx = num_nodes - 1
        causal_weights = W_est[:, outcome_idx]

        results = {}
        for i, (idx, name) in enumerate(zip(sel_indices, sel_names)):
            weight = float(causal_weights[i])
            if abs(weight) > 0.05:
                results[name] = round(weight, 4)

        log.info("DAGMA: found %d non-linear effects", len(results))
        return dict(sorted(results.items(), key=lambda x: abs(x[1]), reverse=True))

    except Exception as e:
        log.warning("DAGMA failed: %s", e)
        return {}


def _compute_interventional(X: np.ndarray, feature_names: list[str],
                            concept_names: list[str]) -> dict:
    """Compute interventional estimates: P(forge | do(remove concept)).

    For each concept, estimates how much forge probability drops if we
    intervene to remove that concept from all triples. Uses simple
    conditional probability (observational proxy for do-calculus).

    Returns dict: concept -> {base_rate, rate_with, rate_without, drop}
    """
    outcome_cols = {name: i for i, name in enumerate(feature_names)}
    forge_col = outcome_cols.get("forge_success")
    attempted_col = outcome_cols.get("forge_attempted")

    if forge_col is None or attempted_col is None:
        return {}

    attempted_mask = X[:, attempted_col] > 0.5
    n_attempted = attempted_mask.sum()
    if n_attempted < 20:
        return {}

    X_att = X[attempted_mask]
    base_rate = X_att[:, forge_col].mean()

    results = {}
    for i, name in enumerate(concept_names):
        present = X_att[:, i] > 0.5
        n_with = present.sum()
        n_without = (~present).sum()

        if n_with < 3 or n_without < 3:
            continue

        rate_with = X_att[present, forge_col].mean()
        rate_without = X_att[~present, forge_col].mean()
        drop = rate_with - rate_without

        if abs(drop) > 0.01:
            results[name] = {
                "base_rate": round(float(base_rate), 4),
                "rate_with": round(float(rate_with), 4),
                "rate_without": round(float(rate_without), 4),
                "drop": round(float(drop), 4),
            }

    return results


def build_causal_graph(nous_entries: list[dict], ledger: dict,
                       combo_key_fn) -> CausalGraph:
    """Build the full causal graph from all available data.

    Args:
        nous_entries: list of Nous response dicts
        ledger: dict from load_ledger() (key -> entry)
        combo_key_fn: function to compute combo key from entry

    Returns:
        CausalGraph with all analysis results
    """
    log.info("Encoding dataset: %d entries, %d ledger records",
             len(nous_entries), len(ledger))

    X, feature_names, concept_names = _encode_dataset(
        nous_entries, ledger, combo_key_fn
    )

    log.info("Dataset shape: %s, %d features", X.shape, len(feature_names))

    # Primary analysis: regression-based influence
    graph = _regression_influence(X, feature_names, concept_names)

    # Enhanced: NOTEARS on score submatrix
    notears_dag = _notears_analysis(X, feature_names, concept_names)
    if notears_dag:
        graph.score_dag = notears_dag
        graph.method += "+notears"
        log.info("NOTEARS: found %d edges in score DAG", sum(len(v) for v in notears_dag.values()))

    # Enhanced: LiNGAM causal ordering
    lingam_result = _lingam_analysis(X, feature_names)
    if lingam_result:
        graph.score_dag_lingam = lingam_result
        graph.method += "+lingam"
        log.info("LiNGAM: found causal ordering for %d variables", len(lingam_result))

    # Enhanced: FCI latent confounder detection
    fci_result = _fci_confounder_analysis(X, feature_names, concept_names)
    if fci_result:
        graph.confounders = fci_result
        graph.method += "+fci"

    # Enhanced: DAGMA non-linear (only with enough data)
    dagma_result = _dagma_analysis(X, feature_names, concept_names)
    if dagma_result:
        divergences = []
        for concept, nl_weight in dagma_result.items():
            if concept in graph.concept_influence:
                linear_weight = graph.concept_influence[concept].get("forge_effect", 0)
                graph.concept_influence[concept]["nonlinear_effect"] = nl_weight

                # Divergence: linear and non-linear disagree on direction or magnitude
                if linear_weight != 0 and nl_weight != 0:
                    same_sign = (linear_weight > 0) == (nl_weight > 0)
                    ratio = abs(nl_weight / linear_weight) if linear_weight != 0 else float('inf')
                    if not same_sign:
                        divergences.append({
                            "concept": concept,
                            "type": "sign_flip",
                            "linear": round(linear_weight, 4),
                            "nonlinear": round(nl_weight, 4),
                            "message": f"{concept}: linear says {'positive' if linear_weight > 0 else 'negative'}, "
                                       f"DAGMA says {'positive' if nl_weight > 0 else 'negative'}"
                        })
                    elif ratio > 3.0 or ratio < 0.33:
                        divergences.append({
                            "concept": concept,
                            "type": "magnitude_shift",
                            "linear": round(linear_weight, 4),
                            "nonlinear": round(nl_weight, 4),
                            "ratio": round(ratio, 2),
                            "message": f"{concept}: DAGMA effect is {ratio:.1f}x the linear estimate"
                        })
            else:
                graph.concept_influence[concept] = {"nonlinear_effect": nl_weight}
                if abs(nl_weight) > 0.2:
                    divergences.append({
                        "concept": concept,
                        "type": "hidden_by_linear",
                        "linear": 0,
                        "nonlinear": round(nl_weight, 4),
                        "message": f"{concept}: invisible to linear model, DAGMA finds effect={nl_weight:.3f}"
                    })

        graph.dagma_divergences = divergences
        graph.method += "+dagma"

        if divergences:
            log.warning("DAGMA DIVERGENCE: %d concepts where non-linear contradicts linear:",
                        len(divergences))
            for d in divergences:
                log.warning("  %s", d["message"])
        else:
            log.info("DAGMA: no divergences from linear model (effects consistent)")

    # Interventional estimates (counterfactual probabilities)
    interventional = _compute_interventional(X, feature_names, concept_names)
    if interventional:
        graph.interventional = interventional
        log.info("Interventional: computed counterfactuals for %d concepts",
                 len(interventional))

    log.info("Causal graph built: method=%s, %d concept influences, %d synergies",
             graph.method, len(graph.concept_influence), len(graph.pair_synergy))

    return graph
