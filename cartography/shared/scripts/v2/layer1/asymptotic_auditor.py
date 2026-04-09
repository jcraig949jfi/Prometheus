"""Asymptotic auditor: compare extended OEIS sequences against short-run growth rates."""

import argparse
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit
from scipy.special import gammaln

# Paths
REPO = Path(__file__).resolve().parents[5]  # F:/Prometheus
NEW_TERMS_DIR = REPO / "cartography" / "oeis" / "data" / "new_terms"
STRIPPED_FILE = REPO / "cartography" / "oeis" / "data" / "stripped_new.txt"
OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"

# Constant matcher
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # shared/scripts
from constant_matcher import identify_constant

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ---------------------------------------------------------------------------
# OEIS stripped-data loader (lazy, cached)
# ---------------------------------------------------------------------------
_stripped_cache = None

def _load_stripped():
    global _stripped_cache
    if _stripped_cache is not None:
        return _stripped_cache
    _stripped_cache = {}
    if not STRIPPED_FILE.exists():
        return _stripped_cache
    with open(STRIPPED_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) < 2:
                continue
            seq_id = parts[0].strip(",")
            vals = parts[1].strip().rstrip(",").split(",")
            try:
                _stripped_cache[seq_id] = [int(v) for v in vals if v.strip()]
            except ValueError:
                continue
    return _stripped_cache


# ---------------------------------------------------------------------------
# Sequence loading
# ---------------------------------------------------------------------------

def load_sequence(seq_file: Path) -> dict:
    """Load a sequence file and return metadata + full term list."""
    with open(seq_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    seq_id = data["seq_id"]
    known_count = data.get("known_terms", 0)

    # Try to get original terms from stripped data
    stripped = _load_stripped()
    original = stripped.get(seq_id, [])

    # Parse new terms
    new_terms = {}
    for key, val in data.get("new_terms", {}).items():
        # key like "a(29)"
        idx = int(key.split("(")[1].rstrip(")"))
        new_terms[idx] = int(val)

    # Build full sequence: original terms + new terms
    if original:
        full = list(original)
        max_orig_idx = len(original) - 1
        for idx in sorted(new_terms.keys()):
            if idx > max_orig_idx:
                # Fill gaps if any
                while len(full) <= idx:
                    if len(full) in new_terms:
                        full.append(new_terms[len(full)])
                    else:
                        full.append(None)
    else:
        # No original data; use new_terms only
        if not new_terms:
            return {"seq_id": seq_id, "name": data.get("name", ""), "terms": [], "known_count": known_count}
        min_idx = min(new_terms.keys())
        max_idx = max(new_terms.keys())
        full = []
        for i in range(min_idx, max_idx + 1):
            full.append(new_terms.get(i))

    # Filter None values, keep only valid terms
    terms = [t for t in full if t is not None]
    return {
        "seq_id": seq_id,
        "name": data.get("name", ""),
        "terms": terms,
        "known_count": known_count,
    }


# ---------------------------------------------------------------------------
# Growth rate computation
# ---------------------------------------------------------------------------

def compute_ratios(terms: list) -> np.ndarray:
    """Compute consecutive ratios a(n+1)/a(n), skipping zeros."""
    ratios = []
    for i in range(len(terms) - 1):
        if terms[i] != 0 and terms[i + 1] != 0:
            # Handle sign: use absolute values for growth rate
            r = abs(terms[i + 1]) / abs(terms[i])
            if np.isfinite(r) and r > 0:
                ratios.append(r)
    return np.array(ratios) if ratios else np.array([])


def growth_rates(terms: list, window: int = 15):
    """Return (short_rate, long_rate, delta_pct) or None if insufficient data."""
    ratios = compute_ratios(terms)
    if len(ratios) < 2 * window:
        # Not enough data; use halves
        if len(ratios) < 6:
            return None
        half = len(ratios) // 2
        short = np.median(ratios[:half])
        long_ = np.median(ratios[half:])
    else:
        short = np.median(ratios[:window])
        long_ = np.median(ratios[-window:])

    if short == 0 or not np.isfinite(short) or not np.isfinite(long_):
        return None

    delta_pct = abs(short - long_) / abs(short)
    return short, long_, delta_pct


# ---------------------------------------------------------------------------
# Model fitting
# ---------------------------------------------------------------------------

def _safe_log(terms):
    """Log of absolute values, replacing zeros with NaN."""
    arr = np.array([abs(t) if t != 0 else np.nan for t in terms], dtype=float)
    with np.errstate(invalid="ignore"):
        return np.log(arr)


def fit_polynomial(x, y_log, deg):
    """Fit log(a(n)) ~ polynomial in n. Returns (coeffs, aic, bic)."""
    mask = np.isfinite(y_log)
    if mask.sum() < deg + 2:
        return None, np.inf, np.inf
    xm, ym = x[mask], y_log[mask]
    try:
        coeffs = np.polyfit(xm, ym, deg)
        predicted = np.polyval(coeffs, xm)
        residuals = ym - predicted
        n = len(ym)
        k = deg + 1
        ss = np.sum(residuals**2)
        if ss <= 0:
            ss = 1e-30
        ll = -n / 2 * (np.log(2 * np.pi * ss / n) + 1)
        aic = 2 * k - 2 * ll
        bic = k * np.log(n) - 2 * ll
        return coeffs, aic, bic
    except Exception:
        return None, np.inf, np.inf


def fit_exponential(x, y_log):
    """Fit log(a(n)) ~ a + b*n (pure exponential). Returns (a, b, aic, bic)."""
    mask = np.isfinite(y_log)
    if mask.sum() < 4:
        return None, None, np.inf, np.inf
    xm, ym = x[mask], y_log[mask]
    try:
        coeffs = np.polyfit(xm, ym, 1)
        predicted = np.polyval(coeffs, xm)
        residuals = ym - predicted
        n = len(ym)
        k = 2
        ss = np.sum(residuals**2)
        if ss <= 0:
            ss = 1e-30
        ll = -n / 2 * (np.log(2 * np.pi * ss / n) + 1)
        aic = 2 * k - 2 * ll
        bic = k * np.log(n) - 2 * ll
        return coeffs[1], coeffs[0], aic, bic  # slope=b, intercept=a
    except Exception:
        return None, None, np.inf, np.inf


def fit_mixed(x, y_log):
    """Fit log(a(n)) ~ a + b*n + c*log(n) (polynomial * exponential)."""
    mask = np.isfinite(y_log)
    if mask.sum() < 6:
        return None, np.inf, np.inf
    xm, ym = x[mask], y_log[mask]
    # Avoid log(0)
    xm_safe = np.where(xm > 0, xm, 1)
    log_xm = np.log(xm_safe)
    A = np.column_stack([np.ones_like(xm), xm, log_xm])
    try:
        coeffs, res, _, _ = np.linalg.lstsq(A, ym, rcond=None)
        predicted = A @ coeffs
        residuals = ym - predicted
        n = len(ym)
        k = 3
        ss = np.sum(residuals**2)
        if ss <= 0:
            ss = 1e-30
        ll = -n / 2 * (np.log(2 * np.pi * ss / n) + 1)
        aic = 2 * k - 2 * ll
        bic = k * np.log(n) - 2 * ll
        return coeffs, aic, bic
    except Exception:
        return None, np.inf, np.inf


def best_model(terms: list):
    """Fit all models, return (model_name, growth_rate, aic, bic, params)."""
    if len(terms) < 6:
        return None

    x = np.arange(len(terms), dtype=float)
    y_log = _safe_log(terms)

    results = []

    # Exponential
    b, a, aic_e, bic_e = fit_exponential(x, y_log)
    if b is not None:
        results.append(("exponential", np.exp(b), aic_e, bic_e, {"a": a, "b": b}))

    # Polynomials (degree 2-5) in log space
    for deg in range(2, 6):
        coeffs, aic_p, bic_p = fit_polynomial(x, y_log, deg)
        if coeffs is not None:
            # Growth rate from leading coefficient
            results.append((f"poly_log_d{deg}", None, aic_p, bic_p, {"coeffs": coeffs.tolist()}))

    # Mixed
    coeffs_m, aic_m, bic_m = fit_mixed(x, y_log)
    if coeffs_m is not None:
        results.append(("mixed", np.exp(coeffs_m[1]) if len(coeffs_m) > 1 else None, aic_m, bic_m, {"coeffs": coeffs_m.tolist()}))

    if not results:
        return None

    # Pick by BIC
    results.sort(key=lambda r: r[3])
    return results[0]


def best_model_window(terms: list, start: int, end: int):
    """Fit best model to a sub-window of the sequence."""
    sub = terms[start:end]
    if len(sub) < 6:
        return None
    return best_model(sub)


# ---------------------------------------------------------------------------
# Deviation analysis
# ---------------------------------------------------------------------------

def deviation_analysis(terms: list, short_rate: float):
    """Compute deviation sequence and check ratios against constants."""
    if short_rate <= 0 or short_rate == 1.0 or len(terms) < 10:
        return None

    # Predict from short-run exponential: a(n) ~ a(0) * short_rate^n
    a0 = abs(terms[0]) if terms[0] != 0 else 1
    predicted = [a0 * (short_rate ** i) for i in range(len(terms))]
    deviations = [terms[i] - predicted[i] for i in range(len(terms))]

    # Compute ratios of consecutive deviations
    dev_ratios = []
    for i in range(len(deviations) - 1):
        if deviations[i] != 0 and abs(deviations[i]) > 1:
            r = deviations[i + 1] / deviations[i]
            if np.isfinite(r) and 0.01 < abs(r) < 100:
                dev_ratios.append(r)

    if not dev_ratios:
        return None

    # Check median ratio against known constants
    med_ratio = float(np.median(dev_ratios))
    matches = identify_constant(abs(med_ratio), tolerance=1e-4, use_ries=False)

    if matches:
        top = matches[0]
        return {
            "deviation_ratio": med_ratio,
            "constant_name": top.name,
            "constant_value": top.matched_value,
            "residual": top.residual,
            "confidence": top.confidence,
        }
    return None


# ---------------------------------------------------------------------------
# Audit one sequence
# ---------------------------------------------------------------------------

def audit_sequence(seq_data: dict) -> dict:
    """Audit a single sequence. Returns result dict or None."""
    seq_id = seq_data["seq_id"]
    terms = seq_data["terms"]

    if len(terms) < 6:
        return None

    # Check for non-growing sequences
    if all(t == terms[0] for t in terms):
        return None

    gr = growth_rates(terms)
    if gr is None:
        return None

    short_rate, long_rate, delta_pct = gr

    # Skip sequences with growth rate ~1 (bounded/polynomial in raw terms)
    if short_rate < 1.001 and long_rate < 1.001:
        return None

    flagged = delta_pct > 0.02

    result = {
        "seq_id": seq_id,
        "name": seq_data["name"],
        "n_terms": len(terms),
        "known_count": seq_data["known_count"],
        "short_rate": round(float(short_rate), 6),
        "long_rate": round(float(long_rate), 6),
        "delta_pct": round(float(delta_pct * 100), 4),
        "flagged": flagged,
    }

    status = "FLAGGED" if flagged else "OK"
    print(f"Auditing {seq_id}... short={short_rate:.3f} long={long_rate:.3f} delta={delta_pct*100:.1f}% -- {status}")

    if flagged:
        # Full model fitting
        model = best_model(terms)
        if model:
            name, rate, aic, bic, params = model
            result["best_model"] = name
            result["best_model_aic"] = round(float(aic), 2)
            result["best_model_bic"] = round(float(bic), 2)
            if rate is not None:
                result["model_growth_rate"] = round(float(rate), 8)

        # Check for regime change: different best model for first half vs second half
        half = len(terms) // 2
        m_short = best_model(terms[:max(half, 6)])
        m_long = best_model(terms[half:])
        if m_short and m_long and m_short[0] != m_long[0]:
            result["regime_change"] = True
            result["short_model"] = m_short[0]
            result["long_model"] = m_long[0]
        else:
            result["regime_change"] = False

        # Deviation analysis / constant matching
        cm = deviation_analysis(terms, short_rate)
        if cm:
            result["constant_match"] = cm

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Asymptotic auditor for extended OEIS sequences")
    parser.add_argument("--seq", type=str, default=None, help="Audit a single sequence (e.g., A148700)")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.seq:
        seq_file = NEW_TERMS_DIR / f"{args.seq}.json"
        if not seq_file.exists():
            print(f"File not found: {seq_file}")
            sys.exit(1)
        files = [seq_file]
    else:
        files = sorted(NEW_TERMS_DIR.glob("*.json"))

    print(f"Asymptotic Auditor: {len(files)} sequences to audit")
    print(f"Loading OEIS stripped data...")
    _load_stripped()
    print(f"Loaded {len(_stripped_cache)} sequences from stripped data")
    print()

    all_results = []
    n_flagged = 0
    n_regime = 0
    n_constant = 0
    n_skipped = 0

    for seq_file in files:
        try:
            seq_data = load_sequence(seq_file)
        except Exception as e:
            print(f"Error loading {seq_file.name}: {e}")
            n_skipped += 1
            continue

        result = audit_sequence(seq_data)
        if result is None:
            n_skipped += 1
            continue

        all_results.append(result)
        if result["flagged"]:
            n_flagged += 1
            if result.get("regime_change"):
                n_regime += 1
            if result.get("constant_match"):
                n_constant += 1

    # Write outputs
    dev_path = OUTPUT_DIR / "asymptotic_deviations.jsonl"
    regime_path = OUTPUT_DIR / "regime_changes.jsonl"

    class _Enc(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, np.bool_):
                return bool(o)
            if isinstance(o, np.integer):
                return int(o)
            if isinstance(o, np.floating):
                return float(o)
            return super().default(o)

    with open(dev_path, "w", encoding="utf-8") as f:
        for r in all_results:
            f.write(json.dumps(r, ensure_ascii=False, cls=_Enc) + "\n")

    with open(regime_path, "w", encoding="utf-8") as f:
        for r in all_results:
            if r.get("regime_change"):
                f.write(json.dumps(r, ensure_ascii=False, cls=_Enc) + "\n")

    print()
    print("=" * 60)
    print(f"SUMMARY")
    print(f"  Audited:          {len(all_results)}")
    print(f"  Skipped:          {n_skipped}")
    print(f"  Flagged (>2%):    {n_flagged}")
    print(f"  Regime changes:   {n_regime}")
    print(f"  Constant matches: {n_constant}")
    print(f"  Output:           {dev_path}")
    print(f"  Regime changes:   {regime_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
