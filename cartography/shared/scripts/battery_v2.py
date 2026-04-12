#!/usr/bin/env python3
"""
Battery V2: F15-F24b + F25-F27 — Extended falsification battery.

F15: Log-Normal Calibration Test
F16: Equivalence Test (TOST)
F17: Confound Sensitivity Analysis
F18: Subset Stability Test
F19: Generative Replay
F20: Representation Invariance
F21: Trend Robustness
F22: Representation Alignment
F23: Latent Confound Discovery
F24: Variance Decomposition (eta²)
F24b: Metric Consistency (tail localization)
F25: Transportability Gate (leave-one-group-out OOS R²)
F26: Benjamini-Hochberg FDR Correction
F27: Domain Consequence Checker (tautology lookup)

Added 2026-04-12 after council review (ChatGPT×2, Gemini, Claude, DeepSeek, Grok, Perplexity).
"""

import numpy as np
from scipy import stats


class BatteryV2:
    """F15-F18: Extended battery tests."""

    def __init__(self, rng_seed=42):
        self.rng = np.random.default_rng(rng_seed)

    def F15_log_normal_calibration(self, values, domain_is_multiplicative=False):
        """Test if M4/M2^2 is explained by log-normality.

        Returns: (verdict, result_dict)
        Verdicts: DEVIATES_FROM_LOGNORMAL, CONSISTENT_WITH_LOGNORMAL,
                  PASS_THEORETICAL, INSUFFICIENT_DATA
        """
        v = np.array(values, dtype=float)
        v = v[v > 0]
        if len(v) < 50:
            return "INSUFFICIENT_DATA", {}

        lv = np.log(v)
        sigma_sq = np.var(lv)
        expected = (np.exp(4 * sigma_sq) + 2 * np.exp(3 * sigma_sq)) / \
                   (np.exp(2 * sigma_sq) + 1) ** 2

        vn = v / np.mean(v)
        m2 = np.mean(vn ** 2)
        m4 = np.mean(vn ** 4)
        observed = m4 / m2 ** 2

        boots = []
        for _ in range(500):
            s = self.rng.choice(v, len(v), replace=True)
            sn = s / np.mean(s)
            sm2 = np.mean(sn ** 2)
            sm4 = np.mean(sn ** 4)
            boots.append(sm4 / sm2 ** 2)
        lo, hi = np.percentile(boots, [2.5, 97.5])

        matches_ln = lo <= expected <= hi

        result = {
            "observed": observed,
            "expected_lognormal": expected,
            "bootstrap_CI": (lo, hi),
            "matches_lognormal": matches_ln,
            "sigma_sq": sigma_sq,
        }

        if matches_ln:
            verdict = "PASS_THEORETICAL" if domain_is_multiplicative else "CONSISTENT_WITH_LOGNORMAL"
        else:
            verdict = "DEVIATES_FROM_LOGNORMAL"

        return verdict, result

    def F16_equivalence_test(self, values, predicted, margin=0.10, n_bootstrap=1000):
        """TOST equivalence test for predicted value match.

        Returns: (verdict, result_dict)
        Verdicts: EQUIVALENT, SIGNIFICANTLY_DIFFERENT, INCONCLUSIVE, INSUFFICIENT_DATA
        """
        v = np.array(values, dtype=float)
        v = v[v > 0]
        if len(v) < 30:
            return "INSUFFICIENT_DATA", {}

        boots = []
        for _ in range(n_bootstrap):
            s = self.rng.choice(v, len(v), replace=True)
            sn = s / np.mean(s)
            m2 = np.mean(sn ** 2)
            m4 = np.mean(sn ** 4)
            boots.append(m4 / m2 ** 2)

        boots = np.array(boots)
        lo90, hi90 = np.percentile(boots, [5, 95])
        lower = predicted * (1 - margin)
        upper = predicted * (1 + margin)

        se = np.std(boots)
        denom = margin * predicted
        req_n = int(2 * ((1.645 + 0.842) * se / denom) ** 2) if denom > 0 else 999999

        result = {
            "mean": np.mean(boots),
            "CI_90": (lo90, hi90),
            "equivalence_bounds": (lower, upper),
            "required_n": req_n,
            "actual_n": len(v),
        }

        if len(v) < req_n:
            verdict = "INCONCLUSIVE"
        elif lo90 > lower and hi90 < upper:
            verdict = "EQUIVALENT"
        elif hi90 < lower or lo90 > upper:
            verdict = "SIGNIFICANTLY_DIFFERENT"
        else:
            verdict = "INCONCLUSIVE"

        return verdict, result

    def F17_confound_sensitivity(self, values, group_labels, confound_values, n_strata=4):
        """Automated confound sensitivity analysis for enrichment.

        Returns: (verdict, result_dict)
        Verdicts: CONFOUND_ROBUST, CONFOUND_SENSITIVE, CONFOUND_DOMINATED, INSUFFICIENT_DATA
        """
        values = np.array(values, dtype=float)
        confound_values = np.array(confound_values, dtype=float)

        groups = {}
        for v, g in zip(values, group_labels):
            groups.setdefault(g, []).append(v)

        within, across = [], []
        all_vals = values.copy()
        for g, vals in groups.items():
            vals_arr = np.array(vals)
            if len(vals_arr) >= 5:
                for _ in range(min(50, len(vals_arr))):
                    i, j = self.rng.choice(len(vals_arr), 2, replace=False)
                    within.append(abs(vals_arr[i] - vals_arr[j]))
        for _ in range(len(within)):
            i, j = self.rng.choice(len(all_vals), 2, replace=False)
            across.append(abs(all_vals[i] - all_vals[j]))

        if not within or not across:
            return "INSUFFICIENT_DATA", {}

        orig_enrichment = np.mean(across) / np.mean(within)

        strata_edges = np.percentile(confound_values, np.linspace(0, 100, n_strata + 1))
        strata_enrichments = []

        for s in range(n_strata):
            mask = (confound_values >= strata_edges[s]) & (confound_values < strata_edges[s + 1] + 1e-10)
            stratum_groups = {}
            for v, g, m in zip(values, group_labels, mask):
                if m:
                    stratum_groups.setdefault(g, []).append(v)

            sw, sa = [], []
            stratum_vals = values[mask]
            for g, vals in stratum_groups.items():
                vals_arr = np.array(vals)
                if len(vals_arr) >= 3:
                    for _ in range(min(20, len(vals_arr))):
                        i, j = self.rng.choice(len(vals_arr), 2, replace=False)
                        sw.append(abs(vals_arr[i] - vals_arr[j]))
            for _ in range(len(sw)):
                if len(stratum_vals) >= 2:
                    i, j = self.rng.choice(len(stratum_vals), 2, replace=False)
                    sa.append(abs(stratum_vals[i] - stratum_vals[j]))

            if sw and sa and np.mean(sw) > 0:
                strata_enrichments.append(np.mean(sa) / np.mean(sw))

        if not strata_enrichments:
            return "INSUFFICIENT_DATA", {}

        conditional = np.mean(strata_enrichments)
        sensitivity = abs(orig_enrichment - conditional) / orig_enrichment if orig_enrichment > 0 else 0

        result = {
            "original_enrichment": orig_enrichment,
            "conditional_enrichment": conditional,
            "sensitivity": sensitivity,
            "strata_enrichments": strata_enrichments,
        }

        if sensitivity < 0.3:
            verdict = "CONFOUND_ROBUST"
        elif sensitivity < 0.5:
            verdict = "CONFOUND_SENSITIVE"
        else:
            verdict = "CONFOUND_DOMINATED"

        return verdict, result

    def F18_subset_stability(self, values, statistic_fn, n_splits=100, fraction=0.8,
                              expected_cv=None):
        """Test stability of a statistic across random subsets.

        Now context-aware: compares observed CV to expected CV (if provided)
        or to a null CV estimated from bootstrap of the full sample.

        Returns: (verdict, result_dict)
        Verdicts: STABLE, MODERATE, UNSTABLE, INSUFFICIENT_DATA
        """
        values = np.array(values, dtype=float)
        values = values[values > 0]
        if len(values) < 50:
            return "INSUFFICIENT_DATA", {}

        stats_list = []
        for _ in range(n_splits):
            idx = self.rng.choice(len(values), int(len(values) * fraction), replace=False)
            stats_list.append(statistic_fn(values[idx]))

        stats_arr = np.array(stats_list)
        mean_val = np.mean(stats_arr)
        cv = np.std(stats_arr) / abs(mean_val) if abs(mean_val) > 0 else float("inf")

        # Estimate null CV if not provided: bootstrap the full sample
        # to get the expected sampling variability
        if expected_cv is None:
            null_stats = []
            for _ in range(min(n_splits, 50)):
                idx = self.rng.choice(len(values), len(values), replace=True)
                null_stats.append(statistic_fn(values[idx]))
            null_arr = np.array(null_stats)
            null_mean = np.mean(null_arr)
            expected_cv = np.std(null_arr) / abs(null_mean) if abs(null_mean) > 0 else 1.0

        # CV ratio: observed / expected
        cv_ratio = cv / expected_cv if expected_cv > 0 else float("inf")

        result = {
            "mean": mean_val,
            "std": np.std(stats_arr),
            "cv": cv,
            "expected_cv": expected_cv,
            "cv_ratio": cv_ratio,
            "range": (float(np.min(stats_arr)), float(np.max(stats_arr))),
        }

        # Context-aware verdict: compare to expected, not absolute threshold
        if cv_ratio < 1.5:
            verdict = "STABLE"
        elif cv_ratio < 3.0:
            verdict = "MODERATE"
        else:
            verdict = "UNSTABLE"

        return verdict, result

    def F21_trend_robustness(self, X, Y, index=None):
        """Test whether correlation survives detrending (Tier B: structural).

        If correlation is significant raw but vanishes after removing
        a linear trend, the signal is a trend confound.

        Returns: (verdict, result_dict)
        Verdicts: ROBUST, TREND_CONFOUND, HIDDEN_STRUCTURE, NULL
        """
        from scipy import stats as sp_stats
        X = np.array(X, dtype=float)
        Y = np.array(Y, dtype=float)
        n = min(len(X), len(Y))
        X, Y = X[:n], Y[:n]

        if index is None:
            index = np.arange(n, dtype=float)
        else:
            index = np.array(index, dtype=float)[:n]

        # Raw correlation
        r_raw, p_raw = sp_stats.pearsonr(X, Y)
        raw_sig = p_raw < 0.05

        # Detrend: remove linear trend on index
        X_coef = np.polyfit(index, X, 1)
        Y_coef = np.polyfit(index, Y, 1)
        X_res = X - np.polyval(X_coef, index)
        Y_res = Y - np.polyval(Y_coef, index)
        r_detrend, p_detrend = sp_stats.pearsonr(X_res, Y_res)
        detrend_sig = p_detrend < 0.05

        # Also: first differences
        dX = np.diff(X)
        dY = np.diff(Y)
        r_diff, p_diff = sp_stats.pearsonr(dX, dY)
        diff_sig = p_diff < 0.05

        result = {
            "r_raw": r_raw, "p_raw": p_raw,
            "r_detrended": r_detrend, "p_detrended": p_detrend,
            "r_differenced": r_diff, "p_differenced": p_diff,
            "trend_slope_X": X_coef[0], "trend_slope_Y": Y_coef[0],
        }

        if raw_sig and not detrend_sig:
            verdict = "TREND_CONFOUND"
        elif raw_sig and detrend_sig:
            verdict = "ROBUST"
        elif not raw_sig and detrend_sig:
            verdict = "HIDDEN_STRUCTURE"
        else:
            verdict = "NULL"

        return verdict, result

    def F19_generative_replay(self, real_values, synthetic_generator, statistic_fn,
                               n_replays=100):
        """Test whether a statistic is explained by a proposed generative model.

        synthetic_generator: callable(n) -> array of n synthetic values
        statistic_fn: callable(array) -> scalar

        Returns: (verdict, result_dict)
        Verdicts: MODEL_MATCHES, MODEL_PARTIAL, MODEL_FAILS, INSUFFICIENT_DATA
        """
        real_values = np.array(real_values, dtype=float)
        real_values = real_values[real_values > 0]
        if len(real_values) < 50:
            return "INSUFFICIENT_DATA", {}

        real_stat = statistic_fn(real_values)

        syn_stats = []
        for _ in range(n_replays):
            syn_data = np.array(synthetic_generator(len(real_values)), dtype=float)
            syn_data = syn_data[syn_data > 0]
            if len(syn_data) > 10:
                syn_stats.append(statistic_fn(syn_data))

        if len(syn_stats) < 10:
            return "INSUFFICIENT_DATA", {}

        syn_stats = np.array(syn_stats)
        syn_mean = np.mean(syn_stats)
        syn_std = np.std(syn_stats)
        z = (real_stat - syn_mean) / syn_std if syn_std > 0 else float("inf")

        from scipy.stats import ks_2samp
        best_syn = np.array(synthetic_generator(len(real_values)), dtype=float)
        best_syn = best_syn[best_syn > 0]
        ks_stat, ks_p = ks_2samp(real_values, best_syn) if len(best_syn) > 10 else (1.0, 0.0)

        # Variance ratio check: if synthetic model is too noisy to reject, flag it
        variance_ratio = syn_std / abs(real_stat) if abs(real_stat) > 0 else float("inf")

        result = {
            "real_statistic": real_stat, "synthetic_mean": syn_mean,
            "synthetic_std": syn_std, "z_score": z,
            "ks_statistic": ks_stat, "ks_pvalue": ks_p,
            "variance_ratio": variance_ratio,
        }

        if variance_ratio > 10:
            verdict = "MODEL_MISSPECIFIED"
        elif abs(z) < 2.0 and ks_p > 0.05:
            verdict = "MODEL_MATCHES"
        elif abs(z) < 3.0:
            verdict = "MODEL_PARTIAL"
        else:
            verdict = "MODEL_FAILS"

        return verdict, result

    def F20_representation_invariance(self, values, statistic_fn, transforms=None):
        """Test whether a statistic survives representation changes.

        Returns: (verdict, result_dict)
        Verdicts: INVARIANT, WEAKLY_DEPENDENT, REPRESENTATION_DEPENDENT, INSUFFICIENT_DATA
        """
        values = np.array(values, dtype=float)
        values = values[values > 0]
        if len(values) < 50:
            return "INSUFFICIENT_DATA", {}

        if transforms is None:
            transforms = [
                ("raw", lambda v: v),
                ("log", lambda v: np.log(v[v > 0])),
                ("rank", lambda v: np.argsort(np.argsort(v)).astype(float)),
                ("z-score", lambda v: (v - np.mean(v)) / np.std(v) if np.std(v) > 0 else v),
                ("sqrt", lambda v: np.sqrt(v[v >= 0])),
            ]

        results_by_transform = {}
        for name, transform in transforms:
            try:
                transformed = transform(values)
                transformed = np.array(transformed, dtype=float)
                transformed = transformed[np.isfinite(transformed)]
                if len(transformed) > 10:
                    results_by_transform[name] = statistic_fn(transformed)
            except Exception:
                pass

        if len(results_by_transform) < 3:
            return "INSUFFICIENT_DATA", {}

        stat_values = np.array(list(results_by_transform.values()))
        cv = np.std(stat_values) / abs(np.mean(stat_values)) if abs(np.mean(stat_values)) > 0 else float("inf")

        result = {"by_transform": results_by_transform, "cv_across_transforms": cv}

        if cv < 0.1:
            verdict = "INVARIANT"
        elif cv < 0.3:
            verdict = "WEAKLY_DEPENDENT"
        else:
            verdict = "REPRESENTATION_DEPENDENT"

        return verdict, result

    def F22_representation_alignment(self, X, Y):
        """Determine the correct representation by comparing residual quality.

        For each candidate transform, fits a linear model and evaluates:
        - Residual normality (Shapiro-Wilk)
        - Homoscedasticity (Breusch-Pagan proxy: correlation of |residuals| with fitted)
        - Cross-validated R² stability (std across 5 folds)

        The representation with the best residual behavior is the "natural" one.

        Returns: (verdict, result_dict)
        Verdicts: ALIGNED (one representation clearly best),
                  AMBIGUOUS (multiple equally good),
                  MISSPECIFIED (none produce clean residuals)
        """
        from scipy import stats as sp_stats
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import cross_val_score

        X = np.array(X, dtype=float)
        Y = np.array(Y, dtype=float)
        n = min(len(X), len(Y))
        X, Y = X[:n], Y[:n]

        # Each transform has an ordering_preserving flag for the complexity penalty
        transforms = [
            ("raw", lambda v: v, True),        # identity preserves ordering
            ("log", lambda v: np.log(v[v > 0]) if np.all(v > 0) else None, True),  # monotone
            ("sqrt", lambda v: np.sqrt(v[v >= 0]) if np.all(v >= 0) else None, True),  # monotone
        ]

        scores = {}
        for name, tfn, ordering_safe in transforms:
            try:
                Xt = tfn(X)
                Yt = tfn(Y)
                if Xt is None or Yt is None:
                    continue
                if len(Xt) < 30 or len(Yt) < 30:
                    continue

                lr = LinearRegression()
                lr.fit(Xt.reshape(-1, 1), Yt)
                resid = Yt - lr.predict(Xt.reshape(-1, 1))

                # Residual normality
                w_stat, w_p = sp_stats.shapiro(resid[:min(500, len(resid))])

                # Homoscedasticity proxy: |correlation of |resid| with fitted|
                fitted = lr.predict(Xt.reshape(-1, 1))
                hetero_r = abs(sp_stats.spearmanr(fitted, np.abs(resid))[0])

                # CV R² stability
                cv_scores = cross_val_score(
                    LinearRegression(), Xt.reshape(-1, 1), Yt, cv=5, scoring="r2"
                )
                cv_std = np.std(cv_scores)

                # Complexity penalty: penalize transforms that destroy ordering
                # or introduce non-monotonicity (refinement from frontier review)
                ordering_penalty = 0.0
                if not ordering_safe:
                    # Check if transform destroyed rank-order correlation
                    from scipy.stats import spearmanr as _spr
                    rho, _ = _spr(np.arange(len(Xt)), Xt)
                    if abs(rho) < 0.5:  # ordering destroyed
                        ordering_penalty = 0.2

                # Combined score (higher = better residuals)
                # Normality: higher W = better (range 0-1)
                # Homoscedasticity: lower hetero_r = better
                # CV stability: lower cv_std = better
                # Ordering penalty: penalizes ordering-destroying transforms
                score = w_stat - hetero_r - cv_std - ordering_penalty

                scores[name] = {
                    "shapiro_W": w_stat,
                    "shapiro_p": w_p,
                    "heteroscedasticity": hetero_r,
                    "cv_r2_mean": np.mean(cv_scores),
                    "cv_r2_std": cv_std,
                    "combined_score": score,
                    "r_squared": lr.score(Xt.reshape(-1, 1), Yt),
                }
            except Exception:
                pass

        if len(scores) < 2:
            return "INSUFFICIENT_DATA", {}

        # Find best representation
        best_name = max(scores, key=lambda k: scores[k]["combined_score"])
        best_score = scores[best_name]["combined_score"]

        # Check separation: is best clearly better than second-best?
        sorted_scores = sorted(scores.items(), key=lambda x: -x[1]["combined_score"])
        if len(sorted_scores) >= 2:
            gap = sorted_scores[0][1]["combined_score"] - sorted_scores[1][1]["combined_score"]
        else:
            gap = 0

        # Check if ANY representation has good residuals
        any_normal = any(s["shapiro_p"] > 0.05 for s in scores.values())

        result = {
            "scores": scores,
            "best_representation": best_name,
            "best_score": best_score,
            "gap_to_second": gap,
        }

        if not any_normal:
            verdict = "MISSPECIFIED"
        elif gap > 0.1:
            verdict = "ALIGNED"
        else:
            verdict = "AMBIGUOUS"

        return verdict, result

    def F23_latent_confound_discovery(self, X, Y, max_k=4, n_runs=10):
        """Detect latent confounding via effect-reduction-first logic.

        Step 1: Check Gate 4 (effect reduction) FIRST — is delta_r positive
                and significant? If not → NO_CONFOUND immediately.
        Step 2: If Gate 4 passes, validate with Gates 1-3 (stability,
                separation, predictive relevance).
        Step 3 (v2): Multi-method agreement — require k-means AND hierarchical
                AND GMM to agree on confound detection.

        This prevents hallucinated confounds from stable-but-irrelevant clusters.

        Returns: (verdict, result_dict)
        Verdicts: LATENT_CONFOUND, POSSIBLE_CONFOUND, NO_CONFOUND, INSUFFICIENT_DATA
        """
        from scipy import stats as sp_stats
        from sklearn.cluster import KMeans, AgglomerativeClustering
        from sklearn.metrics import adjusted_rand_score, silhouette_score
        try:
            from sklearn.mixture import GaussianMixture
            HAS_GMM = True
        except ImportError:
            HAS_GMM = False

        X = np.array(X, dtype=float).ravel()
        Y = np.array(Y, dtype=float).ravel()
        n = min(len(X), len(Y))
        X, Y = X[:n], Y[:n]
        if n < 100:
            return "INSUFFICIENT_DATA", {}

        r_global, _ = sp_stats.pearsonr(X, Y)
        features = np.column_stack([X, Y])
        best_result = None
        best_delta = -999

        for k in range(2, max_k + 1):
            # Cluster n_runs times for stability measurement
            all_labels = []
            for seed in range(n_runs):
                km = KMeans(n_clusters=k, random_state=seed, n_init=5)
                all_labels.append(km.fit_predict(features))

            labels = all_labels[0]

            # === GATE 4 FIRST: Effect reduction ===
            within_rs = [sp_stats.pearsonr(X[labels == c], Y[labels == c])[0]
                         for c in range(k) if np.sum(labels == c) >= 20]
            mean_within = np.mean(within_rs) if within_rs else r_global
            delta_r = abs(r_global) - abs(mean_within)

            # Permutation test on delta_r: shuffle labels, recompute
            perm_deltas = []
            for _ in range(200):
                perm_labels = self.rng.permutation(labels)
                perm_within = [sp_stats.pearsonr(X[perm_labels == c], Y[perm_labels == c])[0]
                               for c in range(k) if np.sum(perm_labels == c) >= 20]
                if perm_within:
                    perm_delta = abs(r_global) - abs(np.mean(perm_within))
                    perm_deltas.append(perm_delta)
            p_delta = np.mean(np.array(perm_deltas) >= delta_r) if perm_deltas else 1.0

            gate4 = delta_r > 0.15 and p_delta < 0.05

            # If Gate 4 fails → skip validation, this k is not a confound
            if not gate4:
                res = {"k": k, "delta_r": delta_r, "p_delta": p_delta,
                       "gate4": False, "r_global": r_global, "r_within": mean_within,
                       "gates_passed": 0}
                if delta_r > best_delta:
                    best_delta = delta_r
                    best_result = res
                continue

            # === Gate 4 passed — now validate with Gates 1-3 ===

            # Gate 1: Stability
            aris = [adjusted_rand_score(all_labels[i], all_labels[j])
                    for i in range(len(all_labels))
                    for j in range(i + 1, len(all_labels))]
            mean_ari = np.mean(aris)
            gate1 = mean_ari > 0.7

            # Gate 2: Separation
            sil = silhouette_score(features, labels) if len(set(labels)) > 1 else 0
            gate2 = sil > 0.2

            # Gate 3: Predictive relevance
            cluster_means = [np.mean(Y[labels == c]) for c in range(k)]
            ss_b = sum(np.sum(labels == c) * (cluster_means[c] - np.mean(Y)) ** 2
                       for c in range(k))
            ss_t = np.sum((Y - np.mean(Y)) ** 2)
            r2 = ss_b / ss_t if ss_t > 0 else 0
            gate3 = r2 > 0.05

            # Gate 5 (v2): Multi-method agreement
            # Require k-means AND at least one of {hierarchical, GMM} to agree
            method_agrees = 1  # k-means already ran
            try:
                hc = AgglomerativeClustering(n_clusters=k)
                hc_labels = hc.fit_predict(features)
                hc_ari = adjusted_rand_score(labels, hc_labels)
                if hc_ari > 0.5:
                    method_agrees += 1
            except Exception:
                pass
            if HAS_GMM:
                try:
                    gmm = GaussianMixture(n_components=k, random_state=self.rng.integers(1000))
                    gmm_labels = gmm.fit_predict(features)
                    gmm_ari = adjusted_rand_score(labels, gmm_labels)
                    if gmm_ari > 0.5:
                        method_agrees += 1
                except Exception:
                    pass
            gate5 = method_agrees >= 2  # at least 2 methods agree

            validation_gates = sum([gate1, gate2, gate3, gate5])
            res = {"k": k, "delta_r": delta_r, "p_delta": p_delta,
                   "stability": mean_ari, "silhouette": sil, "r2_cluster": r2,
                   "r_global": r_global, "r_within": mean_within,
                   "gate4": True, "g1": gate1, "g2": gate2, "g3": gate3,
                   "g5_multi_method": gate5, "methods_agreeing": method_agrees,
                   "gates_passed": validation_gates + 1}  # +1 for gate4

            if delta_r > best_delta:
                best_delta = delta_r
                best_result = res

        if best_result is None:
            return "INSUFFICIENT_DATA", {}

        if not best_result.get("gate4", False):
            return "NO_CONFOUND", best_result

        validation = best_result.get("gates_passed", 1) - 1  # subtract gate4
        if validation >= 4:  # all 4 validation gates (stability + separation + relevance + multi-method)
            return "LATENT_CONFOUND", best_result
        elif validation >= 2:
            return "POSSIBLE_CONFOUND", best_result
        elif validation >= 1:
            return "WEAK_CONFOUND", best_result
        else:
            return "NO_CONFOUND", best_result

    def F24_permutation_null(self, values, group_labels, n_perms=500):
        """Compute permutation-null distribution of eta² for calibration.

        Returns: dict with real_eta, null_mean, null_p99, p_value, z_score.
        """
        values = np.array(values, dtype=float)
        labels = np.array(group_labels)

        # Real eta²
        def _eta(vals, labs):
            groups = {}
            for v, l in zip(vals, labs):
                groups.setdefault(l, []).append(v)
            valid = {k: np.array(v) for k, v in groups.items() if len(v) >= 5}
            if len(valid) < 2:
                return float("nan")
            all_v = np.concatenate(list(valid.values()))
            gm = np.mean(all_v)
            ss_t = np.sum((all_v - gm) ** 2)
            ss_b = sum(len(v) * (np.mean(v) - gm) ** 2 for v in valid.values())
            return ss_b / ss_t if ss_t > 0 else 0

        real_eta = _eta(values, labels)
        null_etas = []
        for _ in range(n_perms):
            shuffled = labels.copy()
            self.rng.shuffle(shuffled)
            null_etas.append(_eta(values, shuffled))

        null_etas = np.array([e for e in null_etas if not np.isnan(e)])
        if len(null_etas) == 0:
            return {"real_eta": real_eta, "null_mean": 0, "null_p99": 0,
                    "p_value": 1.0, "z_score": 0}

        null_mean = np.mean(null_etas)
        null_std = np.std(null_etas)
        null_p99 = np.percentile(null_etas, 99)
        p_value = (np.sum(null_etas >= real_eta) + 1) / (len(null_etas) + 1)
        z_score = (real_eta - null_mean) / null_std if null_std > 0 else 0

        return {"real_eta": real_eta, "null_mean": null_mean,
                "null_p99": null_p99, "p_value": p_value, "z_score": z_score}

    def F24_variance_decomposition(self, values, group_labels,
                                     permutation_calibrate=False, n_perms=500):
        """Classify effect size via eta-squared (ANOVA variance decomposition).

        When permutation_calibrate=True, verdicts are based on the permutation
        null distribution instead of fixed Cohen thresholds. This corrects for
        the group-count inflation that makes random data look significant with
        many groups.

        Returns: (verdict, result_dict)
        Verdicts: STRONG_EFFECT, MODERATE_EFFECT, SMALL_EFFECT,
                  WEAK_EFFECT, NEGLIGIBLE_EFFECT, INSUFFICIENT_DATA
                  (with permutation: adds PERM_SIGNIFICANT / PERM_NOT_SIGNIFICANT)
        """
        from collections import Counter

        values = np.array(values, dtype=float)
        labels = np.array(group_labels)

        if len(values) < 30:
            return "INSUFFICIENT_DATA", {}

        # Group means and counts
        groups = {}
        for v, l in zip(values, labels):
            groups.setdefault(l, []).append(v)

        # Need at least 2 groups with >= 5 members
        valid_groups = {k: np.array(v) for k, v in groups.items() if len(v) >= 5}
        if len(valid_groups) < 2:
            return "INSUFFICIENT_DATA", {}

        # Flatten to valid only
        all_vals = np.concatenate(list(valid_groups.values()))
        grand_mean = np.mean(all_vals)
        n_total = len(all_vals)
        k_groups = len(valid_groups)

        ss_total = np.sum((all_vals - grand_mean) ** 2)
        ss_between = sum(
            len(v) * (np.mean(v) - grand_mean) ** 2
            for v in valid_groups.values()
        )
        ss_within = ss_total - ss_between

        eta_sq = ss_between / ss_total if ss_total > 0 else 0

        # F-statistic
        df_between = k_groups - 1
        df_within = n_total - k_groups
        ms_between = ss_between / df_between if df_between > 0 else 0
        ms_within = ss_within / df_within if df_within > 0 else 1
        f_stat = ms_between / ms_within if ms_within > 0 else 0

        # Per-group stats
        group_stats = {}
        for label, vals in valid_groups.items():
            group_stats[str(label)] = {
                "n": len(vals),
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)),
                "cv": float(np.std(vals) / abs(np.mean(vals))) if np.mean(vals) != 0 else float("inf"),
            }

        result = {
            "eta_squared": eta_sq,
            "f_statistic": f_stat,
            "ss_between": ss_between,
            "ss_within": ss_within,
            "ss_total": ss_total,
            "n_groups": k_groups,
            "n_total": n_total,
            "group_stats": group_stats,
        }

        # Fixed-threshold verdict (Cohen's conventions)
        if eta_sq < 0.01:
            verdict = "NEGLIGIBLE_EFFECT"
        elif eta_sq < 0.06:
            verdict = "SMALL_EFFECT"
        elif eta_sq < 0.14:
            verdict = "MODERATE_EFFECT"
        else:
            verdict = "STRONG_EFFECT"

        # Permutation-calibrated verdict (overrides if requested)
        if permutation_calibrate:
            perm = self.F24_permutation_null(values, group_labels, n_perms)
            result["permutation_null"] = perm
            if perm["p_value"] < 0.001 and perm["z_score"] > 3:
                result["perm_verdict"] = "PERM_SIGNIFICANT"
                # Excess eta² over null
                result["excess_eta"] = eta_sq - perm["null_mean"]
            else:
                result["perm_verdict"] = "PERM_NOT_SIGNIFICANT"
                verdict = "PERM_NOT_SIGNIFICANT"

        return verdict, result

    def F24b_metric_consistency(self, values, group_labels, statistic_fn=None):
        """Cross-metric sanity check: flag TAIL_DRIVEN effects.

        Compares the M4/M2² contrast between groups against the
        eta² effect size. When M4/M2² shows a big ratio but eta²
        is small, the effect is driven by tail differences, not
        bulk separation.

        Returns: (verdict, result_dict)
        Verdicts: CONSISTENT, TAIL_DRIVEN, INSUFFICIENT_DATA
        """
        values = np.array(values, dtype=float)
        labels = np.array(group_labels)

        groups = {}
        for v, l in zip(values, labels):
            groups.setdefault(l, []).append(v)

        valid_groups = {k: np.array(v) for k, v in groups.items() if len(v) >= 20}
        if len(valid_groups) < 2:
            return "INSUFFICIENT_DATA", {}

        # M4/M2² per group
        def _m4m2(arr):
            arr = arr[np.isfinite(arr) & (arr > 0)]
            if len(arr) < 10:
                return float("nan")
            vn = arr / np.mean(arr)
            m2 = np.mean(vn ** 2)
            m4 = np.mean(vn ** 4)
            return m4 / m2 ** 2 if m2 > 0 else float("nan")

        m4m2_vals = {str(k): _m4m2(v) for k, v in valid_groups.items()}
        m4m2_finite = [v for v in m4m2_vals.values() if np.isfinite(v)]

        if len(m4m2_finite) < 2:
            return "INSUFFICIENT_DATA", {}

        m4m2_ratio = max(m4m2_finite) / min(m4m2_finite) if min(m4m2_finite) > 0 else float("inf")

        # Eta² from F24
        eta_verdict, eta_result = self.F24_variance_decomposition(values, labels)
        eta_sq = eta_result.get("eta_squared", 0)

        # Median difference (robust, non-tail measure)
        medians = {str(k): float(np.median(v)) for k, v in valid_groups.items()}
        median_vals = list(medians.values())
        median_range_ratio = max(median_vals) / min(median_vals) if min(median_vals) > 0 else float("inf")

        # IQR overlap
        iqrs = {}
        for k, v in valid_groups.items():
            q25, q75 = np.percentile(v, [25, 75])
            iqrs[str(k)] = (q25, q75)

        result = {
            "m4m2_by_group": m4m2_vals,
            "m4m2_ratio": m4m2_ratio,
            "eta_squared": eta_sq,
            "medians": medians,
            "median_range_ratio": median_range_ratio,
            "iqrs": iqrs,
        }

        # Tail localization: what % of total deviation comes from top 10%?
        all_vals = np.concatenate(list(valid_groups.values()))
        grand_mean = np.mean(all_vals)
        threshold_90 = np.percentile(all_vals, 90)

        tail_contribution = 0.0
        if np.sum(all_vals >= threshold_90) > 10:
            tail_frac_by_group = {}
            for k, v in valid_groups.items():
                tail_frac_by_group[str(k)] = float(np.mean(v >= threshold_90))
            result["tail_frac_by_group"] = tail_frac_by_group

            # What fraction of total squared deviation comes from top 10% of values?
            total_dev = np.sum((all_vals - grand_mean) ** 2)
            tail_vals = all_vals[all_vals >= threshold_90]
            tail_dev = np.sum((tail_vals - grand_mean) ** 2)
            tail_contribution = tail_dev / total_dev if total_dev > 0 else 0
            result["tail_contribution"] = tail_contribution

        # Classification
        if m4m2_ratio > 1.5 and eta_sq < 0.06:
            if tail_contribution > 0.5:
                verdict = "EXTREME_TAIL_DRIVEN"
            else:
                verdict = "TAIL_DRIVEN"
        elif m4m2_ratio > 1.5 and eta_sq >= 0.06:
            verdict = "CONSISTENT"
        else:
            verdict = "CONSISTENT"

        return verdict, result

    # ================================================================
    # F25-F27: Council-recommended additions (2026-04-12)
    # ================================================================

    def F25_transportability(self, values, primary_labels, secondary_labels,
                              min_test_n=10, min_group_n=3):
        """Test whether a categorical mapping transfers across context partitions.

        Trains group means on all partitions except one, predicts held-out.
        Repeated for each secondary partition.

        Returns: (verdict, result_dict)
        Verdicts: UNIVERSAL (OOS R² > 0.15 weighted),
                  WEAKLY_TRANSFERABLE (OOS R² > 0),
                  CONTEXT_DEPENDENT (OOS R² ~ 0),
                  CONDITIONAL (OOS R² < 0, strong within-context)
                  INSUFFICIENT_DATA
        """
        from collections import defaultdict

        values = np.array(values, dtype=float)
        n = len(values)
        sec_groups = sorted(set(secondary_labels))

        if len(sec_groups) < 2:
            return "INSUFFICIENT_DATA", {}

        oos_results = []
        for held_out in sec_groups:
            test_mask = np.array([s == held_out for s in secondary_labels])
            train_mask = ~test_mask
            n_test = int(np.sum(test_mask))
            if n_test < min_test_n:
                continue

            # Learn primary group means from training set
            train_groups = defaultdict(list)
            for i in range(n):
                if train_mask[i]:
                    train_groups[primary_labels[i]].append(values[i])
            train_means = {k: np.mean(v) for k, v in train_groups.items()
                           if len(v) >= min_group_n}
            grand_mean = np.mean(values[train_mask])

            # Predict test set
            test_vals = values[test_mask]
            test_primary = [primary_labels[i] for i in range(n) if test_mask[i]]
            predicted = np.array([train_means.get(p, grand_mean) for p in test_primary])

            ss_total = np.sum((test_vals - np.mean(test_vals)) ** 2)
            ss_resid = np.sum((test_vals - predicted) ** 2)
            r2_oos = 1 - ss_resid / ss_total if ss_total > 0 else 0

            oos_results.append({
                "held_out": str(held_out), "n_test": n_test, "r2_oos": r2_oos
            })

        if not oos_results:
            return "INSUFFICIENT_DATA", {}

        weighted_oos = (sum(r["r2_oos"] * r["n_test"] for r in oos_results) /
                        sum(r["n_test"] for r in oos_results))
        mean_oos = np.mean([r["r2_oos"] for r in oos_results])

        result = {
            "per_group": oos_results,
            "weighted_oos_r2": weighted_oos,
            "mean_oos_r2": mean_oos,
            "n_groups_tested": len(oos_results),
        }

        if weighted_oos > 0.15:
            verdict = "UNIVERSAL"
        elif weighted_oos > 0.0:
            verdict = "WEAKLY_TRANSFERABLE"
        elif weighted_oos > -1.0:
            verdict = "CONTEXT_DEPENDENT"
        else:
            verdict = "CONDITIONAL"

        return verdict, result

    def F25b_model_transportability(self, values, primary_labels, secondary_labels,
                                      min_test_n=10):
        """Model-based transportability: distinguishes UNIVERSAL vs CONDITIONAL vs WEAK.

        Trains two models on all contexts except one:
          Model A: main effects only (one-hot primary → outcome)
          Model B: main + interaction (one-hot primary×secondary → outcome)

        Then predicts held-out context.

        Decision table:
          A transfers, B transfers  → UNIVERSAL
          A fails, B transfers      → CONDITIONAL (true interaction)
          A fails, B fails          → WEAK_NOISY (estimation noise, not structure)

        This fixes the F25 bug where small-group noise mimics conditionality.
        """
        from collections import defaultdict

        values = np.array(values, dtype=float)
        n = len(values)
        sec_groups = sorted(set(secondary_labels))

        if len(sec_groups) < 2:
            return "INSUFFICIENT_DATA", {}

        # Build one-hot encoders
        pri_cats = sorted(set(primary_labels))
        sec_cats = sorted(set(secondary_labels))

        def encode_main(pri_labels, n_rows):
            mat = np.zeros((n_rows, max(len(pri_cats) - 1, 1)))
            for i, l in enumerate(pri_labels):
                idx = pri_cats.index(l) if l in pri_cats else -1
                if idx > 0 and idx - 1 < mat.shape[1]:
                    mat[i, idx - 1] = 1
            return mat

        def encode_interaction(pri_labels, sec_labels, n_rows):
            """One-hot for each (primary, secondary) cell."""
            cells = sorted(set(zip(pri_cats, sec_cats)))
            # Use cell indicators for populated cells only
            cell_list = sorted(set(zip(primary_labels, secondary_labels)))
            if len(cell_list) < 3:
                return None
            mat = np.zeros((n_rows, max(len(cell_list) - 1, 1)))
            for i in range(n_rows):
                cell = (pri_labels[i], sec_labels[i])
                if cell in cell_list:
                    idx = cell_list.index(cell)
                    if idx > 0 and idx - 1 < mat.shape[1]:
                        mat[i, idx - 1] = 1
            return mat

        oos_a = []  # main-effects-only OOS R²
        oos_b = []  # interaction OOS R²

        for held_out in sec_groups:
            test_mask = np.array([s == held_out for s in secondary_labels])
            train_mask = ~test_mask
            n_test = int(np.sum(test_mask))
            n_train = int(np.sum(train_mask))
            if n_test < min_test_n or n_train < 30:
                continue

            y_train = values[train_mask]
            y_test = values[test_mask]
            pri_train = [primary_labels[i] for i in range(n) if train_mask[i]]
            pri_test = [primary_labels[i] for i in range(n) if test_mask[i]]
            sec_train = [secondary_labels[i] for i in range(n) if train_mask[i]]
            sec_test = [secondary_labels[i] for i in range(n) if test_mask[i]]

            ss_total = np.sum((y_test - np.mean(y_test))**2)
            if ss_total == 0:
                continue

            # Model A: main effects only
            X_a_train = np.column_stack([np.ones(n_train), encode_main(pri_train, n_train)])
            X_a_test = np.column_stack([np.ones(n_test), encode_main(pri_test, n_test)])
            try:
                beta_a = np.linalg.lstsq(X_a_train, y_train, rcond=None)[0]
                pred_a = X_a_test @ beta_a
                r2_a = 1 - np.sum((y_test - pred_a)**2) / ss_total
            except:
                r2_a = float("nan")

            # Model B: cell means (full interaction)
            cell_means = defaultdict(list)
            for i in range(n_train):
                cell_means[(pri_train[i], sec_train[i])].append(y_train[i])
            # For prediction, use cell mean if available, else primary mean, else grand mean
            pri_means_train = defaultdict(list)
            for i in range(n_train):
                pri_means_train[pri_train[i]].append(y_train[i])
            pri_means = {k: np.mean(v) for k, v in pri_means_train.items()}
            grand_mean = np.mean(y_train)

            pred_b = []
            for i in range(n_test):
                cell = (pri_test[i], sec_test[i])
                if cell in cell_means and len(cell_means[cell]) >= 2:
                    pred_b.append(np.mean(cell_means[cell]))
                elif pri_test[i] in pri_means:
                    pred_b.append(pri_means[pri_test[i]])
                else:
                    pred_b.append(grand_mean)
            pred_b = np.array(pred_b)
            r2_b = 1 - np.sum((y_test - pred_b)**2) / ss_total

            oos_a.append({"held_out": str(held_out), "n": n_test, "r2_a": r2_a, "r2_b": r2_b})

        if not oos_a:
            return "INSUFFICIENT_DATA", {}

        # Weighted averages
        total_n = sum(r["n"] for r in oos_a)
        w_r2_a = sum(r["r2_a"] * r["n"] for r in oos_a if np.isfinite(r["r2_a"])) / total_n
        w_r2_b = sum(r["r2_b"] * r["n"] for r in oos_a) / total_n

        result = {
            "per_group": oos_a,
            "weighted_r2_main": w_r2_a,
            "weighted_r2_interaction": w_r2_b,
            "n_groups_tested": len(oos_a),
        }

        # Decision table
        a_transfers = w_r2_a > 0.05
        b_transfers = w_r2_b > 0.05

        if a_transfers:
            verdict = "UNIVERSAL"
        elif not a_transfers and b_transfers:
            verdict = "CONDITIONAL"
        else:
            verdict = "WEAK_NOISY"

        return verdict, result

    def F25c_shrinkage_transportability(self, values, primary_labels, secondary_labels,
                                          min_test_n=10, shrinkage_k=10):
        """Shrinkage-based transportability: fixes F25b's small-group noise problem.

        Instead of raw group means (noisy for small groups) or one-hot OLS (breaks
        with many groups), uses James-Stein-style shrinkage:
            cell_estimate = (n * cell_mean + k * grand_mean) / (n + k)

        Small cells (n << k) → pulled toward grand mean (conservative)
        Large cells (n >> k) → keep their specific estimate (precise)

        Decision table same as F25b:
            Main transfers → UNIVERSAL
            Main fails, interaction transfers → CONDITIONAL
            Both fail → WEAK_NOISY
        """
        from collections import defaultdict

        values = np.array(values, dtype=float)
        n = len(values)
        sec_groups = sorted(set(secondary_labels))
        k = shrinkage_k

        if len(sec_groups) < 2:
            return "INSUFFICIENT_DATA", {}

        oos_results = []
        for held_out in sec_groups:
            test_mask = np.array([s == held_out for s in secondary_labels])
            train_mask = ~test_mask
            n_test = int(np.sum(test_mask))
            n_train = int(np.sum(train_mask))
            if n_test < min_test_n or n_train < 30:
                continue

            y_train = values[train_mask]
            y_test = values[test_mask]
            pri_train = [primary_labels[i] for i in range(n) if train_mask[i]]
            pri_test = [primary_labels[i] for i in range(n) if test_mask[i]]
            sec_train = [secondary_labels[i] for i in range(n) if train_mask[i]]

            grand_mean = np.mean(y_train)
            ss_total = np.sum((y_test - np.mean(y_test))**2)
            if ss_total == 0:
                continue

            # Model A: shrinkage on primary group means
            pri_groups = defaultdict(list)
            for i in range(n_train):
                pri_groups[pri_train[i]].append(y_train[i])
            pri_means = {g: (len(v) * np.mean(v) + k * grand_mean) / (len(v) + k)
                         for g, v in pri_groups.items()}

            pred_a = np.array([pri_means.get(p, grand_mean) for p in pri_test])
            r2_a = 1 - np.sum((y_test - pred_a)**2) / ss_total

            # Model B: shrinkage on (primary, secondary) cell means toward primary means
            cell_groups = defaultdict(list)
            for i in range(n_train):
                cell_groups[(pri_train[i], sec_train[i])].append(y_train[i])

            pred_b = []
            for i in range(n_test):
                p = pri_test[i]
                cell = (p, held_out)
                pri_mean = pri_means.get(p, grand_mean)
                if cell in cell_groups and len(cell_groups[cell]) >= 2:
                    cell_n = len(cell_groups[cell])
                    cell_mean = np.mean(cell_groups[cell])
                    pred_b.append((cell_n * cell_mean + k * pri_mean) / (cell_n + k))
                else:
                    pred_b.append(pri_mean)
            pred_b = np.array(pred_b)
            r2_b = 1 - np.sum((y_test - pred_b)**2) / ss_total

            oos_results.append({"held_out": str(held_out), "n": n_test,
                                "r2_main": r2_a, "r2_interaction": r2_b})

        if not oos_results:
            return "INSUFFICIENT_DATA", {}

        total_n = sum(r["n"] for r in oos_results)
        w_r2_a = sum(r["r2_main"] * r["n"] for r in oos_results) / total_n
        w_r2_b = sum(r["r2_interaction"] * r["n"] for r in oos_results) / total_n

        result = {
            "per_group": oos_results,
            "weighted_r2_main": w_r2_a,
            "weighted_r2_interaction": w_r2_b,
            "n_groups_tested": len(oos_results),
            "shrinkage_k": k,
        }

        a_transfers = w_r2_a > 0.05
        b_transfers = w_r2_b > 0.05

        if a_transfers:
            verdict = "UNIVERSAL"
        elif not a_transfers and b_transfers:
            verdict = "CONDITIONAL"
        else:
            verdict = "WEAK_NOISY"

        return verdict, result

    def F26_fdr_correction(self, p_values, alpha=0.05):
        """Benjamini-Hochberg FDR correction across multiple hypotheses.

        Returns: (verdict, result_dict) with adjusted p-values and
        which hypotheses survive the correction.

        Verdicts: PASSES_FDR, FAILS_FDR
        """
        p_arr = np.array(p_values, dtype=float)
        n_tests = len(p_arr)
        if n_tests == 0:
            return "INSUFFICIENT_DATA", {}

        # BH procedure
        sorted_idx = np.argsort(p_arr)
        sorted_p = p_arr[sorted_idx]
        thresholds = np.arange(1, n_tests + 1) / n_tests * alpha

        # Find largest k where p_(k) <= k/m * alpha
        rejected = sorted_p <= thresholds
        if np.any(rejected):
            max_k = np.max(np.where(rejected)[0])
            reject_mask = np.zeros(n_tests, dtype=bool)
            reject_mask[sorted_idx[:max_k + 1]] = True
        else:
            reject_mask = np.zeros(n_tests, dtype=bool)

        # Adjusted p-values (step-up)
        adjusted_p = np.minimum(1, sorted_p * n_tests / np.arange(1, n_tests + 1))
        for i in range(n_tests - 2, -1, -1):
            adjusted_p[i] = min(adjusted_p[i], adjusted_p[i + 1])
        adj_p_unsorted = np.empty(n_tests)
        adj_p_unsorted[sorted_idx] = adjusted_p

        result = {
            "n_tests": n_tests,
            "n_rejected": int(np.sum(reject_mask)),
            "alpha": alpha,
            "adjusted_p_values": adj_p_unsorted.tolist(),
            "reject_mask": reject_mask.tolist(),
        }

        verdict = "PASSES_FDR" if int(np.sum(reject_mask)) > 0 else "FAILS_FDR"
        return verdict, result

    # Known mathematical consequences that force specific outcomes.
    KNOWN_CONSEQUENCES = {
        ("E_6", "root_number"): "CM by Q(sqrt(-3)) forces root number +1 via parity conjecture",
        ("E_4", "root_number"): "CM structure likely forces root number +1",
        ("alexander_eval_neg1", "determinant"): "det = |Alexander(-1)| by definition",
        ("crossing_number", "jones_length"): "Jones span ~ 2*crossing for alternating knots (KMT theorem)",
        ("ec_conductor", "mf_level"): "Modularity theorem (Wiles 1995)",
        ("degree", "galois_group"): "Galois group is determined by degree (nesting, not prediction)",
        ("cm_flag", "root_number"): "CM curves have constrained functional equation signs",
    }

    def F27_consequence_check(self, grouping_var_name, outcome_var_name):
        """Check if a finding is a known mathematical consequence (tautology).

        Returns: (verdict, result_dict)
        Verdicts: TAUTOLOGY, NOT_TAUTOLOGY, PARTIAL_MATCH
        """
        key = (grouping_var_name.lower().strip(),
               outcome_var_name.lower().strip())

        if key in self.KNOWN_CONSEQUENCES:
            return "TAUTOLOGY", {
                "match": key,
                "explanation": self.KNOWN_CONSEQUENCES[key],
            }

        partial = []
        for (g, o), explanation in self.KNOWN_CONSEQUENCES.items():
            if (grouping_var_name.lower() in g or g in grouping_var_name.lower() or
                    outcome_var_name.lower() in o or o in outcome_var_name.lower()):
                partial.append({"match": (g, o), "explanation": explanation})

        if partial:
            return "PARTIAL_MATCH", {"partial_matches": partial}

        return "NOT_TAUTOLOGY", {}

    # ================================================================
    # F29-F32: Cross-domain falsification (2026-04-12 council protocol)
    # ================================================================

    def F29_distributional_baseline(self, set_a, set_b, n_random=1000):
        """Test cross-domain integer overlap against distributional null.

        Computes enrichment = observed_overlap / expected_overlap_under_uniform.
        Also tests against Benford-like power-law distributed nulls.

        Verdicts: REAL (>2x), MARGINAL (1.5-2x), ARTIFACT (<1.5x)
        """
        set_a = set(int(x) for x in set_a if x > 0)
        set_b = set(int(x) for x in set_b if x > 0)
        if not set_a or not set_b:
            return "INSUFFICIENT_DATA", {}

        overlap = len(set_a & set_b)
        max_val = max(max(set_a), max(set_b))
        expected_uniform = len(set_a) * len(set_b) / max_val if max_val > 0 else 1

        # Power-law null: generate random sets with same size but log-uniform distribution
        null_overlaps = []
        for _ in range(n_random):
            fake_a = set(int(x) for x in np.exp(self.rng.uniform(0, np.log(max_val + 1), len(set_a))))
            fake_b = set(int(x) for x in np.exp(self.rng.uniform(0, np.log(max_val + 1), len(set_b))))
            null_overlaps.append(len(fake_a & fake_b))

        null_mean = np.mean(null_overlaps)
        null_std = np.std(null_overlaps)
        z = (overlap - null_mean) / null_std if null_std > 0 else 0

        enrichment_uniform = overlap / expected_uniform if expected_uniform > 0 else 0
        enrichment_powerlaw = overlap / null_mean if null_mean > 0 else 0

        result = {
            "overlap": overlap, "set_a_size": len(set_a), "set_b_size": len(set_b),
            "expected_uniform": expected_uniform, "enrichment_uniform": enrichment_uniform,
            "null_mean_powerlaw": null_mean, "enrichment_powerlaw": enrichment_powerlaw,
            "z_powerlaw": z,
        }

        if enrichment_powerlaw > 2.0 and z > 3:
            return "REAL", result
        elif enrichment_powerlaw > 1.5:
            return "MARGINAL", result
        else:
            return "ARTIFACT", result

    def F30_range_conditioned_enrichment(self, set_a, set_b, values_a=None, values_b=None):
        """Test overlap after restricting both sets to the same numeric range.

        If enrichment vanishes after range-matching, it was a range artifact.
        """
        set_a = set(int(x) for x in set_a if x > 0)
        set_b = set(int(x) for x in set_b if x > 0)
        if not set_a or not set_b:
            return "INSUFFICIENT_DATA", {}

        # Full overlap
        full_overlap = len(set_a & set_b)

        # Restrict both to shared range
        lo = max(min(set_a), min(set_b))
        hi = min(max(set_a), max(set_b))
        a_restricted = set(x for x in set_a if lo <= x <= hi)
        b_restricted = set(x for x in set_b if lo <= x <= hi)

        if not a_restricted or not b_restricted:
            return "INSUFFICIENT_DATA", {}

        restricted_overlap = len(a_restricted & b_restricted)
        range_size = hi - lo + 1
        expected = len(a_restricted) * len(b_restricted) / range_size if range_size > 0 else 1
        enrichment = restricted_overlap / expected if expected > 0 else 0

        result = {
            "full_overlap": full_overlap,
            "restricted_overlap": restricted_overlap,
            "range": (lo, hi),
            "a_restricted": len(a_restricted),
            "b_restricted": len(b_restricted),
            "expected_in_range": expected,
            "enrichment_in_range": enrichment,
        }

        if enrichment > 2.0:
            return "SURVIVES_RANGE", result
        elif enrichment > 1.5:
            return "MARGINAL", result
        else:
            return "RANGE_ARTIFACT", result

    def F31_prime_mediated_null(self, values_a, values_b, labels_a, labels_b,
                                  shared_primes):
        """Test if cross-domain correlation survives after conditioning on prime properties.

        For each shared prime, compare domain A's feature against domain B's feature.
        Then partial-correlate after removing: log(p), p mod 6, gap to nearest prime.
        """
        if len(shared_primes) < 10:
            return "INSUFFICIENT_DATA", {}

        shared = sorted(shared_primes)
        va = np.array([values_a.get(p, float("nan")) for p in shared])
        vb = np.array([values_b.get(p, float("nan")) for p in shared])
        primes = np.array(shared, dtype=float)

        mask = np.isfinite(va) & np.isfinite(vb)
        va, vb, primes = va[mask], vb[mask], primes[mask]
        if len(va) < 10:
            return "INSUFFICIENT_DATA", {}

        # Raw correlation
        r_raw = np.corrcoef(va, vb)[0, 1]

        # Partial after log(p) — removes size confound
        log_p = np.log(primes)
        X = np.column_stack([np.ones(len(primes)), log_p])
        beta_a = np.linalg.lstsq(X, va, rcond=None)[0]
        beta_b = np.linalg.lstsq(X, vb, rcond=None)[0]
        resid_a = va - X @ beta_a
        resid_b = vb - X @ beta_b
        r_partial = np.corrcoef(resid_a, resid_b)[0, 1]

        # Partial after log(p) + p mod 6
        p_mod6 = primes % 6
        X2 = np.column_stack([np.ones(len(primes)), log_p, p_mod6])
        beta_a2 = np.linalg.lstsq(X2, va, rcond=None)[0]
        beta_b2 = np.linalg.lstsq(X2, vb, rcond=None)[0]
        resid_a2 = va - X2 @ beta_a2
        resid_b2 = vb - X2 @ beta_b2
        r_partial2 = np.corrcoef(resid_a2, resid_b2)[0, 1]

        result = {
            "n_shared": len(va),
            "r_raw": r_raw,
            "r_partial_logp": r_partial,
            "r_partial_logp_mod6": r_partial2,
        }

        if abs(r_partial) < abs(r_raw) * 0.3:
            return "PRIME_MEDIATED", result
        elif abs(r_partial) > abs(r_raw) * 0.7:
            return "SURVIVES_CONDITIONING", result
        else:
            return "PARTIALLY_MEDIATED", result

    def F32_scaling_degeneracy(self, x_a, y_a, x_b, y_b, label_a="A", label_b="B"):
        """Test if two domain relationships share the same functional form trivially.

        Fits log, sqrt, linear, power to each. If both match the same generic
        class (e.g., both ~log), the match is a scaling degeneracy, not structure.
        """
        from scipy.stats import pearsonr

        forms = {
            "linear": lambda x: x,
            "log": lambda x: np.log(x[x > 0]),
            "sqrt": lambda x: np.sqrt(x[x >= 0]),
            "quadratic": lambda x: x**2,
        }

        def best_fit(x, y):
            x, y = np.array(x, dtype=float), np.array(y, dtype=float)
            mask = np.isfinite(x) & np.isfinite(y) & (x > 0)
            x, y = x[mask], y[mask]
            if len(x) < 10:
                return "unknown", 0

            best_r2 = -1
            best_form = "unknown"
            for name, fn in forms.items():
                try:
                    xt = fn(x)
                    if len(xt) < len(x):
                        xt = fn(x[:len(xt)])
                        y_t = y[:len(xt)]
                    else:
                        y_t = y
                    r, _ = pearsonr(xt, y_t)
                    if r**2 > best_r2:
                        best_r2 = r**2
                        best_form = name
                except:
                    pass
            return best_form, best_r2

        form_a, r2_a = best_fit(x_a, y_a)
        form_b, r2_b = best_fit(x_b, y_b)

        result = {
            "domain_a": {"form": form_a, "r2": r2_a, "label": label_a},
            "domain_b": {"form": form_b, "r2": r2_b, "label": label_b},
            "same_form": form_a == form_b,
        }

        if form_a == form_b and r2_a > 0.5 and r2_b > 0.5:
            return "SCALING_DEGENERACY", result
        else:
            return "DIFFERENT_FORMS", result

    # ================================================================
    # Primitive Tagging System (council recommendation)
    # ================================================================

    PRIMITIVE_TAGS = {
        # Maps finding patterns to operation primitives
        "BREAK_SYMMETRY": "Universal mapping fractures along context lines. The mapping exists but changes across strata.",
        "REDUCE": "Complex structure collapses to a simple invariant via closed-form formula.",
        "COMPOSE": "Two domains share structure through a common mathematical object.",
        "SYMMETRIZE": "A symmetry group constrains or organizes observables.",
        "LINEARIZE": "A nonlinear relationship is well-approximated by a log/power law.",
        "PARTITION": "A categorical variable creates meaningful subgroups in a continuous outcome.",
        "IDENTITY": "Deterministic mathematical relationship (tautology or theorem).",
        "SPECTRAL": "Structure visible in eigenvalue/spacing statistics.",
    }

    def tag_primitive(self, finding_dict):
        """Tag a finding with its structural primitive(s).

        finding_dict should contain:
            - eta2: float
            - has_interaction: bool (ANOVA interaction significant?)
            - rank_stable: bool (rank correlation > 0.3 across contexts?)
            - is_identity: bool (R² > 0.99 or known theorem?)
            - functional_form: str (linear/log/sqrt/power)
            - is_cross_domain: bool
            - involves_eigenvalues: bool

        Returns: list of (primitive, confidence) tuples
        """
        tags = []

        # Identity detection
        if finding_dict.get("is_identity"):
            tags.append(("IDENTITY", 1.0))
            return tags

        # Break symmetry: strong within-context + interaction detected
        if finding_dict.get("has_interaction") and not finding_dict.get("rank_stable", True):
            tags.append(("BREAK_SYMMETRY", 0.9))

        # Symmetrize: categorical grouping explains large variance
        eta = finding_dict.get("eta2", 0)
        if eta >= 0.14 and not finding_dict.get("has_interaction"):
            tags.append(("SYMMETRIZE", 0.8))

        # Partition: categorical grouping with moderate effect
        if 0.01 <= eta < 0.14:
            tags.append(("PARTITION", 0.6))

        # Linearize: best-fit is log or power
        form = finding_dict.get("functional_form", "")
        if form in ("log", "sqrt", "power"):
            tags.append(("LINEARIZE", 0.7))

        # Reduce: very high R² on a simple formula
        if eta >= 0.9 or finding_dict.get("r_squared", 0) >= 0.9:
            tags.append(("REDUCE", 0.8))

        # Spectral
        if finding_dict.get("involves_eigenvalues"):
            tags.append(("SPECTRAL", 0.7))

        # Compose: cross-domain with surviving enrichment
        if finding_dict.get("is_cross_domain") and eta >= 0.01:
            tags.append(("COMPOSE", 0.5))

        if not tags:
            tags.append(("PARTITION", 0.3))  # default

        return tags
