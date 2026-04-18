"""bsd_sha_paradox.py — Harmonia worker U_D.

Investigate the mechanism behind the "small L correlates with small Sha"
paradox observed by worker T4 (commit cbe7b623).

Background
----------
T4 (rank0_low_tail_characterization) found that rank-0 curves at conductor
decade [10^5, 10^6) with  leading_term < 0.25 * M_1(decade)  are DEPLETED
in non-trivial Sha:
    sha=4  enrichment 0.47x,
    sha=9  enrichment 0.25x,
    sha=25 enrichment 0.22x.
Naive BSD reading (rank-0):
    L(1,E) = Omega_real * prod_p c_p * #Sha / #E(Q)_tors^2.
Large Sha should PUSH L up, not down — yet large Sha is MISSING from
the low-L tail.

Resolution
----------
If #Sha is small when L is small, then either
    (i) the numerator   Omega_real * prod_p c_p  is small, or
    (ii) the denominator #E(Q)_tors^2 is large.
Rank-0 regulator is identically 1 (empty product), so it cannot carry
variation.

We have `leading_term = L(1,E)` (EC L-function, rank-0) in
prometheus_fire.zeros.object_zeros, and `torsion`, `sha` in
lmfdb.public.ec_curvedata.  LMFDB does NOT store Omega_real or prod_p c_p
in our mirror.  BUT we can INVERT the BSD formula to obtain the
"analytic BSD geometric factor"
    A := Omega_real * prod_p c_p = L(1,E) * #tors^2 / #Sha
and decompose log L additively:
    log L = log A  +  log Sha  -  2 log tors.
Then for the low-tail cohort we measure which term dominates the
depression of log L relative to the bulk.

Headlines
---------
BSD_TAUTOLOGY_NO_PARADOX  — Sha's depletion is a conditioning tautology:
    conditioning L on "small" drags Sha down along with A.
TORSION_EXPLAINS_LOW_L    — the low-tail cohort has systematically large
    torsion; the -2 log tors term drives most of the depression.
PERIOD_EXPLAINS_LOW_L     — the low-tail cohort has systematically small
    Omega_real * prod_p c_p (i.e. log A is strongly negative).
MIXED_PATTERN             — roughly equal contributions.

Method
------
1. Pull rank-0 leading_term at decade [1e5, 1e6) (same join as T4).
2. Define low-tail = L < 0.25 * M_1(decade).
3. Join arithmetic fields: torsion, sha, torsion_structure, sha_primes.
4. Compute A = L * tors^2 / sha per curve.
5. Decompose log L = log A + log Sha - 2 log tors and report:
   - mean and median of each term in low-tail and bulk
   - share-of-depression = (mean_bulk - mean_lowtail) contribution per
     term to (mean_bulk(log L) - mean_lowtail(log L)).
6. Core tautology check: stratify low-tail by sha value. For each
   stratum, fit log A distribution. If conditioning on small L forces
   A small even within sha=1 (where sha can't vary), the restriction
   is a geometric-factor effect.  If instead the only way to achieve
   small L is to also have small sha (i.e. sha=1 is over-represented
   tautologically), then the T4 finding is BSD_TAUTOLOGY_NO_PARADOX.
7. Quantitative separability: build a null where sha is resampled
   independently of A, tors; recompute the low-tail sha enrichment
   ratios.  If they approximately match observed, the "depletion of
   large sha in low-L" is pure conditioning.

Output
------
cartography/docs/bsd_sha_paradox_investigation_results.json
"""
from __future__ import annotations

import ast
import json
import math
from collections import Counter
from datetime import datetime, timezone

import numpy as np
import psycopg2
from psycopg2.extras import execute_values

PF = dict(host="192.168.1.176", port=5432, dbname="prometheus_fire",
          user="postgres", password="prometheus", connect_timeout=10)
LM = dict(host="192.168.1.176", port=5432, dbname="lmfdb",
          user="postgres", password="prometheus", connect_timeout=10)

DECADE_LO = 100_000
DECADE_HI = 1_000_000
TAIL_THRESHOLD = 0.25
RNG_SEED = 2026_04_17


# ---------------------------------------------------------------------------

def load_rank0_leading_terms() -> dict:
    out = {}
    with psycopg2.connect(**PF) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT lmfdb_label, conductor, leading_term
            FROM zeros.object_zeros
            WHERE object_type = 'elliptic_curve'
              AND analytic_rank = 0
              AND conductor >= %s AND conductor < %s
              AND leading_term IS NOT NULL
              AND leading_term > 0
            """,
            (DECADE_LO, DECADE_HI),
        )
        for lbl, cond, lt in cur.fetchall():
            out[lbl] = (int(cond), float(lt))
    return out


def load_arithmetic(labels: list[str]) -> dict:
    COLS = ("lmfdb_label, torsion, sha, torsion_structure, sha_primes, "
            "cm, num_bad_primes, semistable")
    out = {}
    chunk = 5000
    with psycopg2.connect(**LM) as conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS _tmp_bsd_labels")
        cur.execute("CREATE TEMP TABLE _tmp_bsd_labels (lmfdb_label text PRIMARY KEY)")
        for i in range(0, len(labels), chunk):
            execute_values(
                cur,
                "INSERT INTO _tmp_bsd_labels (lmfdb_label) VALUES %s ON CONFLICT DO NOTHING",
                [(l,) for l in labels[i:i + chunk]],
                page_size=2000,
            )
        cur.execute(
            f"SELECT {COLS} FROM public.ec_curvedata "
            "WHERE lmfdb_label IN (SELECT lmfdb_label FROM _tmp_bsd_labels)"
        )
        for row in cur.fetchall():
            lbl, tor, sha, tstruct, sprimes, cm, nbp, ss = row
            out[lbl] = {
                "torsion": _int_or_none(tor),
                "sha": _int_or_none(sha),
                "torsion_structure": _list_of_int(tstruct),
                "sha_primes": _list_of_int(sprimes),
                "cm": _int_or_none(cm),
                "num_bad_primes": _int_or_none(nbp),
                "semistable": _bool_or_none(ss),
            }
    return out


def _int_or_none(s):
    if s is None or s == "":
        return None
    try:
        return int(s)
    except Exception:
        return None


def _bool_or_none(s):
    if s in (None, ""):
        return None
    if s in ("t", "true", "True", "TRUE"):
        return True
    if s in ("f", "false", "False", "FALSE"):
        return False
    return None


def _list_of_int(s):
    if s is None or s == "":
        return []
    try:
        v = ast.literal_eval(s)
        if isinstance(v, (list, tuple)):
            return [int(x) for x in v]
    except Exception:
        pass
    return []


# ---------------------------------------------------------------------------
# Summary helpers

def summarize(arr: np.ndarray) -> dict:
    if arr.size == 0:
        return {"n": 0}
    return {
        "n": int(arr.size),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "q05": float(np.quantile(arr, 0.05)),
        "q25": float(np.quantile(arr, 0.25)),
        "q75": float(np.quantile(arr, 0.75)),
        "q95": float(np.quantile(arr, 0.95)),
    }


def distribution(vals, keys=None, n=None) -> dict:
    c = Counter(vals)
    total = n if n is not None else sum(c.values())
    if keys is None:
        keys = sorted(c.keys(), key=lambda k: (k is None, k))
    out = {}
    for k in keys:
        cc = int(c.get(k, 0))
        out[str(k)] = {"count": cc, "share": cc / total if total > 0 else 0.0}
    return out


# ---------------------------------------------------------------------------

def main():
    started = datetime.now(timezone.utc).isoformat()
    print(f"[{started}] Loading rank-0 leading_term at decade [{DECADE_LO}, {DECADE_HI})")

    zeros = load_rank0_leading_terms()
    labels = list(zeros.keys())
    n0 = len(labels)
    lts = np.asarray([zeros[l][1] for l in labels], dtype=float)
    m1 = float(lts.mean())
    threshold = TAIL_THRESHOLD * m1
    print(f"  n rank-0 zeros: {n0}")
    print(f"  M_1 = {m1:.6f}   threshold = {threshold:.6f}")

    print("Joining lmfdb.public.ec_curvedata ...")
    arith = load_arithmetic(labels)
    print(f"  arithmetic joined: {len(arith)}")

    # Build parallel arrays over the joined intersection
    lbl_arr = []
    L_arr = []
    tor_arr = []
    sha_arr = []
    cm_arr = []
    nbp_arr = []
    ss_arr = []
    for l in labels:
        a = arith.get(l)
        if a is None:
            continue
        if a["torsion"] is None or a["sha"] is None:
            continue
        if a["torsion"] <= 0 or a["sha"] <= 0:
            continue
        lbl_arr.append(l)
        L_arr.append(zeros[l][1])
        tor_arr.append(a["torsion"])
        sha_arr.append(a["sha"])
        cm_arr.append(a["cm"] if a["cm"] is not None else 0)
        nbp_arr.append(a["num_bad_primes"] if a["num_bad_primes"] is not None else -1)
        ss_arr.append(a["semistable"])

    L = np.asarray(L_arr, dtype=float)
    tor = np.asarray(tor_arr, dtype=int)
    sha = np.asarray(sha_arr, dtype=int)
    cm_np = np.asarray(cm_arr, dtype=int)
    n = L.size
    print(f"  fully-joined rows: {n}")

    # Decompose  log L = log A + log sha - 2 log tors
    logL = np.log(L)
    logSha = np.log(sha.astype(float))
    logTor2 = 2.0 * np.log(tor.astype(float))
    logA = logL + logTor2 - logSha  # = log(Omega_real * prod_p c_p)

    low = L < threshold
    n_low = int(low.sum())
    n_bulk = n - n_low
    print(f"  low-tail rows: {n_low} / {n}  ({100 * n_low / n:.2f}%)")

    # ----- 1. Distribution summaries on logL, logA, logSha, -2 logTor
    summary = {
        "logL":     {"low": summarize(logL[low]),     "bulk": summarize(logL[~low])},
        "logA":     {"low": summarize(logA[low]),     "bulk": summarize(logA[~low])},
        "logSha":   {"low": summarize(logSha[low]),   "bulk": summarize(logSha[~low])},
        "neg2logTor": {"low": summarize(-logTor2[low]), "bulk": summarize(-logTor2[~low])},
    }

    # ----- 2. Share-of-depression decomposition
    # mean(logL) = mean(logA) + mean(logSha) - mean(2 log tor)
    # Deltas:
    d_logL = float(np.mean(logL[low]) - np.mean(logL[~low]))       # negative
    d_logA = float(np.mean(logA[low]) - np.mean(logA[~low]))
    d_logSha = float(np.mean(logSha[low]) - np.mean(logSha[~low])) # most negative
    d_neg2tor = float(np.mean(-logTor2[low]) - np.mean(-logTor2[~low]))
    # exact identity: d_logL = d_logA + d_logSha + d_neg2tor
    share = {
        "delta_mean_logL":       d_logL,
        "delta_mean_logA":       d_logA,
        "delta_mean_logSha":     d_logSha,
        "delta_mean_neg2logTor": d_neg2tor,
        "sum_of_parts":          d_logA + d_logSha + d_neg2tor,
        "share_A":       d_logA / d_logL   if d_logL != 0 else None,
        "share_Sha":     d_logSha / d_logL if d_logL != 0 else None,
        "share_neg2Tor": d_neg2tor / d_logL if d_logL != 0 else None,
    }

    # ----- 3. Distribution of sha and torsion across cohorts
    sha_dist = {
        "low":  distribution([int(x) for x in sha[low]], n=n_low),
        "bulk": distribution([int(x) for x in sha[~low]], n=n_bulk),
    }
    tor_dist = {
        "low":  distribution([int(x) for x in tor[low]], n=n_low),
        "bulk": distribution([int(x) for x in tor[~low]], n=n_bulk),
    }

    # enrichment = low_share / bulk_share
    def enrichment(low_d, bulk_d):
        keys = sorted(set(low_d) | set(bulk_d), key=lambda k: int(k))
        out = {}
        for k in keys:
            ls = low_d.get(k, {}).get("share", 0.0)
            bs = bulk_d.get(k, {}).get("share", 0.0)
            out[k] = {
                "low_share": ls,
                "bulk_share": bs,
                "enrichment": (ls / bs) if bs > 0 else None,
            }
        return out

    sha_enrich = enrichment(sha_dist["low"], sha_dist["bulk"])
    tor_enrich = enrichment(tor_dist["low"], tor_dist["bulk"])

    # ----- 4. Core tautology test: within sha=1 stratum, is the geometric
    # factor A also strongly depressed?  If yes, the low-L phenomenon lives
    # mostly in A (and conditioning on small L drags sha toward 1 simply
    # because large sha would multiply L up past the threshold).
    strata = {}
    for s_val in [1, 4, 9, 16, 25]:
        mask_s = sha == s_val
        if mask_s.sum() < 50:
            continue
        low_s = low & mask_s
        bulk_s = (~low) & mask_s
        strata[str(s_val)] = {
            "n_total": int(mask_s.sum()),
            "n_low": int(low_s.sum()),
            "low_share": float(low_s.sum() / mask_s.sum()),
            "logL_low":  summarize(logL[low_s]),
            "logL_bulk": summarize(logL[bulk_s]),
            "logA_low":  summarize(logA[low_s]),
            "logA_bulk": summarize(logA[bulk_s]),
            "tor_low":  summarize(tor[low_s].astype(float)),
            "tor_bulk": summarize(tor[bulk_s].astype(float)),
        }

    # ----- 5. Counterfactual null: "if sha were independent of (A, tor),
    # what would the low-tail sha enrichment look like?"  We construct a
    # synthetic cohort by keeping logA and tor fixed but resampling sha
    # from the marginal distribution of sha over the bulk, independently
    # per curve.  Then we recompute a synthetic L = exp(logA + log sha' -
    # 2 log tor), pick the bottom TAIL_THRESHOLD*M_1 cohort, and compute
    # sha enrichment ratios.
    rng = np.random.default_rng(RNG_SEED)
    # Marginal sha distribution from the FULL cohort (used as prior)
    sha_values, sha_counts = np.unique(sha, return_counts=True)
    sha_probs = sha_counts / sha_counts.sum()
    n_trials = 10
    null_sha_enrich = {str(int(v)): [] for v in sha_values}
    null_n_low_list = []
    for trial in range(n_trials):
        sha_synth = rng.choice(sha_values, size=n, replace=True, p=sha_probs)
        logL_synth = logA + np.log(sha_synth.astype(float)) - logTor2
        L_synth = np.exp(logL_synth)
        # Use matched threshold: for fairness, use the SAME fraction (not
        # the same numeric threshold) so the cohort sizes line up.  We
        # recompute the threshold at the quantile corresponding to
        # TAIL_THRESHOLD * M_1 in the original cohort.
        orig_frac = n_low / n
        thr_synth = float(np.quantile(L_synth, orig_frac))
        low_synth = L_synth < thr_synth
        n_low_synth = int(low_synth.sum())
        null_n_low_list.append(n_low_synth)
        # Compute sha enrichments on synthetic cohort
        for v in sha_values:
            mv = sha_synth == v
            total_v = int(mv.sum())
            low_v = int((low_synth & mv).sum())
            low_share = low_v / n_low_synth if n_low_synth else 0.0
            bulk_share = (total_v - low_v) / (n - n_low_synth) if (n - n_low_synth) else 0.0
            enr = (low_share / bulk_share) if bulk_share > 0 else None
            null_sha_enrich[str(int(v))].append(enr)
    # Aggregate null enrichment per sha value
    null_sha_enrich_agg = {}
    for k, vals in null_sha_enrich.items():
        clean = [x for x in vals if x is not None]
        null_sha_enrich_agg[k] = {
            "mean_enrichment": float(np.mean(clean)) if clean else None,
            "std_enrichment":  float(np.std(clean, ddof=1)) if len(clean) > 1 else None,
            "n_trials_used":   len(clean),
        }

    # Observed vs null side-by-side
    # But there's a subtle point: the null keeps (logA, tor) the same, so
    # the LOGL correlation structure with (A, tor) is unchanged.  Only
    # sha is shuffled.  If the observed sha enrichment matches the null
    # sha enrichment closely, the "sha depletion in low-L" is a pure
    # structural/ conditioning consequence of BSD (given the marginal
    # sha distribution and the observed joint (A, tor) distribution).

    # Quantify sha-A coupling in the bulk population (non-low-L).
    bulk_mask = ~low
    la_bulk = logA[bulk_mask]
    ls_bulk = logSha[bulk_mask]
    lt_bulk_logT = logTor2[bulk_mask]
    # Pearson correlation coefficients (numpy corrcoef).
    corr_bulk_logSha_logA = float(np.corrcoef(la_bulk, ls_bulk)[0, 1])
    corr_bulk_logTor_logA = float(np.corrcoef(la_bulk, lt_bulk_logT)[0, 1])
    corr_bulk_logTor_logSha = float(np.corrcoef(ls_bulk, lt_bulk_logT)[0, 1])
    # Full-cohort correlations.
    corr_all_logSha_logA = float(np.corrcoef(logA, logSha)[0, 1])
    corr_all_logTor_logA = float(np.corrcoef(logA, logTor2)[0, 1])
    corr_all_logTor_logSha = float(np.corrcoef(logSha, logTor2)[0, 1])
    # Mean logA as a function of sha value (to exhibit the sha-A coupling
    # directly; we expect monotone decreasing in sha).
    mean_logA_by_sha = {}
    for sv in sorted(set(int(x) for x in sha)):
        mask_sv = sha == sv
        if mask_sv.sum() < 20:
            continue
        mean_logA_by_sha[str(sv)] = {
            "n": int(mask_sv.sum()),
            "mean_logA": float(np.mean(logA[mask_sv])),
            "median_logA": float(np.median(logA[mask_sv])),
        }

    coupling = {
        "pearson_corr_bulk_logSha_logA":   corr_bulk_logSha_logA,
        "pearson_corr_bulk_log2Tor_logA":  corr_bulk_logTor_logA,
        "pearson_corr_bulk_log2Tor_logSha": corr_bulk_logTor_logSha,
        "pearson_corr_all_logSha_logA":    corr_all_logSha_logA,
        "pearson_corr_all_log2Tor_logA":   corr_all_logTor_logA,
        "pearson_corr_all_log2Tor_logSha": corr_all_logTor_logSha,
        "mean_logA_by_sha_value":          mean_logA_by_sha,
        "interpretation": (
            "Expect corr(logSha, logA) < 0 in the bulk if large-Sha curves "
            "have systematically small Omega*prod c_p; such anticorrelation "
            "moderates the BSD-conditioning depletion of sha in the low-L "
            "tail."
        ),
    }

    comparison = {}
    for k in ["1", "4", "9", "16", "25"]:
        obs = sha_enrich.get(k)
        null = null_sha_enrich_agg.get(k)
        comparison[k] = {
            "observed_enrichment": obs["enrichment"] if obs else None,
            "null_enrichment_mean": null["mean_enrichment"] if null else None,
            "null_enrichment_std":  null["std_enrichment"] if null else None,
        }

    # ----- 6. Verdict logic
    share_A   = share["share_A"]      or 0.0
    share_Sha = share["share_Sha"]    or 0.0
    share_Tor = share["share_neg2Tor"] or 0.0

    # Check whether the null reproduces the observed sha depletion.
    # Ratio observed/null for sha=4, 9, 25 (the three T4 reported).
    null_match = []
    for k in ["4", "9", "25"]:
        o = comparison[k]["observed_enrichment"]
        n_ = comparison[k]["null_enrichment_mean"]
        if o is not None and n_ is not None and n_ != 0:
            null_match.append(o / n_)
    null_match_mean = float(np.mean(null_match)) if null_match else None

    tautology = null_match_mean is not None and 0.7 <= null_match_mean <= 1.4

    # What drives the observed -log L shift?
    SHARE_DOMINANT = 0.5
    dominant = None
    if share_A >= SHARE_DOMINANT and share_Sha < 0.35 and share_Tor < 0.35:
        dominant = "A"
    elif share_Sha >= SHARE_DOMINANT:
        dominant = "Sha"
    elif share_Tor >= SHARE_DOMINANT:
        dominant = "Tor"
    else:
        dominant = "mixed"

    # The null_match ratio > 1 means OBSERVED sha enrichment is LARGER than
    # independent-sha null predicts — i.e., large sha is LESS depleted than
    # independence would give.  This indicates sha-A are anticorrelated in
    # the bulk, which buffers large-sha curves into the low-L tail.
    if tautology and dominant == "A":
        verdict_label = "BSD_TAUTOLOGY_NO_PARADOX"
        verdict_note = (
            "Share of the log-L depression carried by log(Omega*prod c_p) "
            "dominates, and when sha is reshuffled independently of (A, tor) "
            "the resulting low-tail sha enrichment ratios match the observed "
            "values within [0.7, 1.4]x. Conclusion: conditioning on small L "
            "AUTOMATICALLY depletes large sha because large sha multiplies L "
            "upward; there is no additional mechanism."
        )
    elif dominant == "Tor":
        verdict_label = "TORSION_EXPLAINS_LOW_L"
        verdict_note = (
            "log-L depression is dominated by the -2 log(#tors) term: low-tail "
            "cohort has systematically large torsion; denominator dominates."
        )
    elif dominant == "A" and null_match_mean is not None and null_match_mean > 1.4:
        verdict_label = "PERIOD_EXPLAINS_LOW_L"
        verdict_note = (
            "log-L depression is dominated by log A = log(Omega_real * prod c_p); "
            "share_A = {:.2f} vs share_Sha = {:.2f} vs share_neg2Tor = {:.2f}. "
            "The independent-sha null OVER-depletes large sha relative to "
            "observed (null_match = {:.2f}x, i.e., observed enrichment for "
            "sha>=4 is {:.1f}x higher than independence would predict); "
            "therefore sha and A are NEGATIVELY correlated in the bulk — "
            "large-Sha curves tend to have small Omega*prod c_p. T4's 'small "
            "L correlates with small Sha' is NOT a pure BSD conditioning "
            "tautology but is almost entirely carried by the A factor; the "
            "Sha depletion in the low tail is real but weaker than "
            "independence would predict (sha-A anticorrelation buffers it). "
            "Mechanism: the low-L tail is a SMALL-PERIOD / SMALL-TAMAGAWA "
            "sub-family; its sha distribution is pulled toward sha=1 both by "
            "the direct conditioning pressure and by the sha-A coupling."
        ).format(share_A, share_Sha, share_Tor, null_match_mean, null_match_mean)
    elif dominant == "A":
        verdict_label = "PERIOD_EXPLAINS_LOW_L"
        verdict_note = (
            "log-L depression dominated by log(Omega * prod c_p) "
            "(share_A = {:.2f}). Independent-sha null does NOT reproduce the "
            "observed sha depletion pattern."
        ).format(share_A)
    else:
        verdict_label = "MIXED_PATTERN"
        verdict_note = (
            "No single term carries >= 50% of the log-L depression; low-L "
            "arises from combined small Omega*prod c_p AND large torsion "
            "with partial sha covariation."
        )

    finished = datetime.now(timezone.utc).isoformat()
    out = {
        "task": "bsd_sha_paradox_investigation",
        "worker": "Harmonia_U_D",
        "started": started,
        "finished": finished,
        "config": {
            "decade_lo": DECADE_LO,
            "decade_hi": DECADE_HI,
            "tail_threshold_fraction_of_M1": TAIL_THRESHOLD,
            "rng_seed": RNG_SEED,
            "n_null_trials": n_trials,
        },
        "cohort": {
            "n_rank0_with_leading_term": n0,
            "M_1": m1,
            "threshold_leading_term": threshold,
            "n_joined_arithmetic": len(arith),
            "n_fully_joined_nonzero_tors_sha": n,
            "n_low_tail": n_low,
            "low_tail_fraction": n_low / n,
        },
        "decomposition_log_L": {
            "identity": "log L = log(Omega_real * prod c_p) + log Sha - 2 log #E(Q)_tors",
            "summary_per_term": summary,
            "share_of_depression_low_vs_bulk": share,
            "interpretation": (
                "share_X = [mean(X|low) - mean(X|bulk)] / [mean(logL|low) - mean(logL|bulk)]. "
                "X in {logA, logSha, -2 logTor}; shares sum to 1 by the BSD identity."
            ),
        },
        "sha_distribution": {
            "low": sha_dist["low"],
            "bulk": sha_dist["bulk"],
            "enrichment_per_value": sha_enrich,
        },
        "torsion_distribution": {
            "low": tor_dist["low"],
            "bulk": tor_dist["bulk"],
            "enrichment_per_value": tor_enrich,
        },
        "per_sha_strata": strata,
        "arithmetic_coupling": coupling,
        "independent_sha_null": {
            "description": (
                "Resample sha i.i.d. from the marginal sha distribution, "
                "keeping (log A, tor) fixed; recompute synthetic L and "
                "low-tail by matched fraction; observe synthetic sha "
                "enrichments. If they match observed, sha's depletion "
                "is a BSD conditioning tautology."
            ),
            "n_trials": n_trials,
            "low_tail_size_per_trial": null_n_low_list,
            "null_enrichment_per_sha_value": null_sha_enrich_agg,
            "observed_vs_null_comparison": comparison,
            "ratio_observed_to_null_for_sha_in_{4,9,25}": null_match,
            "ratio_observed_to_null_mean": null_match_mean,
            "tautology_band_0_7_to_1_4_match": tautology,
        },
        "verdict": {
            "label": verdict_label,
            "note": verdict_note,
            "shares": {
                "A":      share_A,
                "Sha":    share_Sha,
                "neg2Tor": share_Tor,
            },
            "dominant_term": dominant,
            "null_match_mean": null_match_mean,
        },
        "methodology_notes": [
            "BSD identity is exact for rank-0; regulator = 1 identically.",
            "Omega_real and prod_p c_p are not stored in LMFDB mirror; "
            "log A is derived from L, tors, sha via the BSD identity.",
            "This decomposition is tautological AS AN IDENTITY. The "
            "non-trivial question is which term's VARIATION drives the "
            "low-tail depression, which is testable.",
            "The independent-sha null is the cleanest way to distinguish "
            "BSD conditioning from a joint sha-A mechanism.",
        ],
    }

    out_path = "D:/Prometheus/cartography/docs/bsd_sha_paradox_investigation_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[{finished}] wrote {out_path}")
    print(f"VERDICT: {verdict_label}")
    print(f"  share_A      = {share_A:.3f}")
    print(f"  share_Sha    = {share_Sha:.3f}")
    print(f"  share_neg2Tor = {share_Tor:.3f}")
    print(f"  observed/null sha enrichment ratio (mean over sha in 4,9,25): "
          f"{null_match_mean}")
    print("Observed vs null sha enrichment:")
    for k, d in comparison.items():
        print(f"  sha={k}: obs={d['observed_enrichment']}  "
              f"null={d['null_enrichment_mean']}")


if __name__ == "__main__":
    main()
