"""
Constant Matcher — Inverse symbolic identification for numerical values.
=========================================================================
Given a floating-point number, identifies it as a known mathematical constant
or a simple algebraic combination of known constants.

Three identification strategies:
  1. Local database of 83+ mathematical constants with high-precision values
  2. Algebraic combinations (c1*c2, c1/c2, c1+c2, c1-c2, sqrt(c), c^2)
  3. RIES online inverse symbolic calculator (rate-limited)

Standalone usage:
  python constant_matcher.py 1.6180339
  python constant_matcher.py 2.718281828 --tolerance 1e-8
  python constant_matcher.py --batch 1.618033 2.718281 3.141592
"""

import json
import math
import ssl
import sys
import time
import urllib.request
import urllib.parse
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Optional, Union

# ---------------------------------------------------------------------------
# SSL workaround for Windows
# ---------------------------------------------------------------------------
try:
    import certifi
    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()
    _SSL_CTX.check_hostname = False
    _SSL_CTX.verify_mode = ssl.CERT_NONE

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[3]
CONVERGENCE_DATA = REPO / "cartography" / "convergence" / "data"
WIKIDATA_CONSTANTS = CONVERGENCE_DATA / "wikidata_math_constants.json"

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ConstantMatch:
    """A single match result from constant identification."""
    value: float                    # The queried value
    name: str                       # Human-readable name of the match
    expression: str                 # Symbolic expression (e.g., "pi/e")
    matched_value: float            # The exact value of the constant/expression
    residual: float                 # |value - matched_value|
    confidence: float               # 0.0 to 1.0 (higher = closer match)
    source: str                     # "local", "algebraic", or "ries"
    wikidata_qid: Optional[str] = None  # Wikidata QID if available

    def to_dict(self):
        return asdict(self)


# ---------------------------------------------------------------------------
# High-precision local constant database
# ---------------------------------------------------------------------------

# Core constants with at least 15 significant digits
LOCAL_CONSTANTS = {
    # Fundamental
    "pi":                       3.14159265358979323846,
    "e":                        2.71828182845904523536,
    "phi (golden ratio)":       1.61803398874989484820,
    "sqrt(2)":                  1.41421356237309504880,
    "sqrt(3)":                  1.73205080756887729353,
    "sqrt(5)":                  2.23606797749978969641,
    "sqrt(6)":                  2.44948974278317809820,
    "sqrt(7)":                  2.64575131106459059050,

    # Euler-Mascheroni and related
    "Euler-Mascheroni gamma":   0.57721566490153286061,
    "Catalan's constant":       0.91596559417721901505,
    "Apery's constant zeta(3)": 1.20205690315959428540,

    # Feigenbaum
    "Feigenbaum delta":         4.66920160910299067185,
    "Feigenbaum alpha":         2.50290787509589282228,

    # Khinchin
    "Khinchin's constant":      2.68545200106530644531,

    # Logarithms
    "ln(2)":                    0.69314718055994530942,
    "ln(3)":                    1.09861228866810969140,
    "ln(10)":                   2.30258509299404568402,
    "log10(2)":                 0.30102999566398119521,
    "log10(e)":                 0.43429448190325182765,
    "log2(10)":                 3.32192809488736234787,

    # Reciprocals and ratios
    "1/e":                      0.36787944117144232160,
    "1/pi":                     0.31830988618379067154,
    "pi/e":                     1.15572734979092171791,
    "e/pi":                     0.86525597943226508722,
    "pi/4":                     0.78539816339744830962,
    "pi/2":                     1.57079632679489661923,
    "pi/6":                     0.52359877559829887308,

    # Powers and products
    "phi^2":                    2.61803398874989484820,
    "2*pi (tau)":               6.28318530717958647692,
    "pi^2":                     9.86960440108935861883,
    "e^2":                      7.38905609893065022723,
    "e^pi":                     23.1406926327792690057,
    "pi^e":                     22.4591577183610454734,
    "2^(1/2)":                  1.41421356237309504880,  # same as sqrt(2)
    "2^(1/3)":                  1.25992104989487316477,
    "2^(1/12)":                 1.05946309435929526456,

    # Gelfond's constant and Gelfond-Schneider
    "e^pi (Gelfond)":          23.1406926327792690057,
    "2^sqrt(2) (Gelfond-Schneider)": 2.66514414269022518866,

    # Other well-known constants
    "omega constant":           0.56714329040978387300,
    "Dottie number":            0.73908513321516064166,
    "Meissel-Mertens":          0.26149721284764278376,
    "Bernstein's constant":     0.28016949902386913303,
    "Gauss-Kuzmin-Wirsing":     0.30366300289873265860,
    "Landau-Ramanujan":         0.76422365358922066299,
    "Brun's constant (twin)":   1.90216058310,  # less precision known
    "Glaisher-Kinkelin":        1.28242712910062263954,
    "Plastic ratio":            1.32471795724474602596,
    "Silver ratio":             2.41421356237309504880,
    "Bronze ratio":             3.30277563773199464655,

    # Reciprocal Fibonacci constant
    "reciprocal Fibonacci":     3.35988566624317755317,

    # Mill's constant
    "Mill's constant":          1.30637788386308069046,

    # Niven's constant
    "Niven's constant":         1.70521114010536776428,

    # Universal parabolic constant
    "universal parabolic":      2.29558714939263807404,

    # Sierpinski's constant
    "Sierpinski's constant":    2.58498175957925321706,

    # Levy's constant
    "Levy's constant":          3.27582291872181115978,

    # Backhouse's constant
    "Backhouse's constant":     1.45607494858268967140,

    # Conway's constant
    "Conway's constant":        1.30357726903429639126,

    # Somos quadratic recurrence
    "Somos quadratic":          1.66168794963359412129,

    # Erdos-Borwein
    "Erdos-Borwein":            1.60669515241529176378,

    # Laplace limit
    "Laplace limit":            0.66274341934918158097,

    # MRB constant
    "MRB constant":             0.18785964246206712024,

    # Prouhet-Thue-Morse
    "Prouhet-Thue-Morse":       0.41245403364010759778,

    # Copeland-Erdos
    "Copeland-Erdos":           0.23571113171923293137,

    # Champernowne
    "Champernowne C10":         0.12345678910111213141,

    # Liouville's constant
    "Liouville's constant":     0.11000100000000000000,

    # Golomb-Dickman
    "Golomb-Dickman":           0.62432998854355087100,

    # Cahen's constant
    "Cahen's constant":         0.64341054628833802618,

    # Fransen-Robinson
    "Fransen-Robinson":         2.80777024202851936522,

    # Kepler-Bouwkamp
    "Kepler-Bouwkamp":          0.11494204485329620070,

    # Porter's constant
    "Porter's constant":        1.46707807943397547289,

    # de Bruijn-Newman
    "de Bruijn-Newman":         0.0,  # Lambda >= 0, proven = 0

    # Foias constant
    "Foias constant":           1.18745235112650105460,

    # Lemniscate constant
    "lemniscate constant":      2.62205755429211981046,

    # Lehmer's totient constant (Heath-Brown-Moroz)
    "Heath-Brown-Moroz":        0.00131764115485317810,

    # Common small integers and fractions for completeness
    "1/2":                      0.5,
    "1/3":                      0.33333333333333333333,
    "2/3":                      0.66666666666666666667,
    "1/4":                      0.25,
    "3/4":                      0.75,
    "1/sqrt(2)":                0.70710678118654752440,
    "1/sqrt(2*pi)":             0.39894228040143267794,
    "sqrt(2*pi)":               2.50662827463100050242,
    "sqrt(pi)":                 1.77245385090551602730,
}

# Map names to Wikidata QIDs where known
_NAME_TO_QID = {
    "pi": "Q167",
    "e": "Q82435",
    "phi (golden ratio)": "Q41690",
    "sqrt(2)": "Q389813",
    "sqrt(3)": "Q1150815",
    "sqrt(5)": "Q2337529",
    "sqrt(6)": "Q111952608",
    "sqrt(7)": "Q111951213",
    "Euler-Mascheroni gamma": "Q273023",
    "Catalan's constant": "Q855282",
    "Apery's constant zeta(3)": "Q622682",
    "Feigenbaum delta": "Q120336524",
    "Feigenbaum alpha": "Q120336535",
    "Khinchin's constant": "Q2718188",
    "Glaisher-Kinkelin": "Q1782651",
    "Plastic ratio": "Q2345603",
    "Silver ratio": "Q2353128",
    "Bronze ratio": "Q11662816",
    "omega constant": "Q2291098",
    "Dottie number": "Q48996451",
    "Backhouse's constant": "Q4839668",
    "Conway's constant": "Q2994911",
    "reciprocal Fibonacci": "Q3772671",
    "Mill's constant": "Q1192957",
    "Niven's constant": "Q1113025",
    "universal parabolic": "Q7894145",
    "Sierpinski's constant": "Q461009",
    "Erdos-Borwein": "Q1349661",
    "Laplace limit": "Q2994928",
    "MRB constant": "Q6717435",
    "Copeland-Erdos": "Q931099",
    "Champernowne C10": "Q1061180",
    "Liouville's constant": "Q18030473",
    "Golomb-Dickman": "Q5580918",
    "Cahen's constant": "Q1025756",
    "Fransen-Robinson": "Q1445544",
    "Kepler-Bouwkamp": "Q6393212",
    "Porter's constant": "Q30692563",
    "Foias constant": "Q15634948",
    "Meissel-Mertens": "Q1918289",
    "Landau-Ramanujan": "Q2641368",
    "Brun's constant (twin)": "Q850251",
    "Heath-Brown-Moroz": "Q5693407",
    "2*pi (tau)": "Q2333151",
    "2^(1/3)": "Q56352464",
    "2^(1/12)": "Q4919430",
}

# ---------------------------------------------------------------------------
# Wikidata enrichment: load labels from the JSON sidecar
# ---------------------------------------------------------------------------
_wikidata_labels: dict = {}  # QID -> label


def _load_wikidata_labels():
    """Lazy-load Wikidata labels for richer output."""
    if _wikidata_labels:
        return
    if not WIKIDATA_CONSTANTS.exists():
        return
    try:
        with open(WIKIDATA_CONSTANTS, "r", encoding="utf-8") as f:
            for entry in json.load(f):
                qid = entry.get("qid", "")
                label = entry.get("label", qid)
                _wikidata_labels[qid] = label
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Confidence scoring
# ---------------------------------------------------------------------------

def _confidence(residual: float, tolerance: float) -> float:
    """
    Compute a confidence score in [0, 1].

    Score is 1.0 when residual=0, decays exponentially, reaches ~0.01
    at the tolerance boundary.
    """
    if tolerance <= 0:
        return 1.0 if residual == 0 else 0.0
    # -ln(0.01) ~ 4.605 => k such that exp(-k * tol / tol) ~ 0.01
    k = 4.605 / tolerance
    return math.exp(-k * residual)


# ---------------------------------------------------------------------------
# Core: identify against local constants
# ---------------------------------------------------------------------------

def _match_local(value: float, tolerance: float = 1e-6) -> List[ConstantMatch]:
    """Check value against all local constants."""
    _load_wikidata_labels()
    matches = []
    for name, cval in LOCAL_CONSTANTS.items():
        if cval == 0.0 and name == "de Bruijn-Newman":
            continue  # Skip trivial zero match
        residual = abs(value - cval)
        if residual <= tolerance:
            qid = _NAME_TO_QID.get(name)
            matches.append(ConstantMatch(
                value=value,
                name=_wikidata_labels.get(qid, name) if qid else name,
                expression=name,
                matched_value=cval,
                residual=residual,
                confidence=_confidence(residual, tolerance),
                source="local",
                wikidata_qid=qid,
            ))
    return matches


# ---------------------------------------------------------------------------
# Algebraic combinations
# ---------------------------------------------------------------------------

# Subset of "important" constants for pairwise combinations
# (using all 83 would be O(n^2) ~ 7000 pairs, still fast)
_COMBO_CONSTANTS = {
    k: v for k, v in LOCAL_CONSTANTS.items()
    if v != 0.0
}


def check_against_constants(
    value: float,
    tolerance: float = 1e-6,
) -> List[ConstantMatch]:
    """
    Check a number against ALL local constants and their simple algebraic
    combinations: c1*c2, c1/c2, c1+c2, c1-c2, sqrt(c), c^2 for all pairs.

    Returns matches sorted by confidence (descending).
    """
    _load_wikidata_labels()
    matches = []
    seen_expressions = set()

    def _add(name, expr, cval, src="algebraic"):
        if expr in seen_expressions:
            return
        residual = abs(value - cval)
        if residual <= tolerance:
            seen_expressions.add(expr)
            qid = _NAME_TO_QID.get(name)
            matches.append(ConstantMatch(
                value=value,
                name=name,
                expression=expr,
                matched_value=cval,
                residual=residual,
                confidence=_confidence(residual, tolerance),
                source=src,
                wikidata_qid=qid,
            ))

    # Direct matches
    for name, cval in LOCAL_CONSTANTS.items():
        if cval == 0.0 and name == "de Bruijn-Newman":
            continue
        _add(name, name, cval, src="local")

    # Unary operations: sqrt(c), c^2
    for name, cval in _COMBO_CONSTANTS.items():
        if cval > 0:
            _add(f"sqrt({name})", f"sqrt({name})", math.sqrt(cval))
        _add(f"({name})^2", f"({name})^2", cval * cval)

    # Pairwise operations
    names = list(_COMBO_CONSTANTS.keys())
    vals = list(_COMBO_CONSTANTS.values())
    n = len(names)
    for i in range(n):
        for j in range(i, n):
            n1, v1 = names[i], vals[i]
            n2, v2 = names[j], vals[j]

            _add(f"{n1} + {n2}", f"{n1} + {n2}", v1 + v2)
            _add(f"{n1} * {n2}", f"{n1} * {n2}", v1 * v2)

            if i != j:
                _add(f"{n1} - {n2}", f"{n1} - {n2}", v1 - v2)
                _add(f"{n2} - {n1}", f"{n2} - {n1}", v2 - v1)

            if v2 != 0:
                _add(f"{n1} / {n2}", f"{n1} / {n2}", v1 / v2)
            if v1 != 0 and i != j:
                _add(f"{n2} / {n1}", f"{n2} / {n1}", v2 / v1)

    matches.sort(key=lambda m: m.confidence, reverse=True)
    return matches


# ---------------------------------------------------------------------------
# RIES online lookup
# ---------------------------------------------------------------------------

_ries_last_call = 0.0
_RIES_MIN_INTERVAL = 2.0  # seconds between calls (rate limit)
_RIES_URL = "https://thomasahle.com/ries/"  # WASM-based, no REST API

# RIES is a WASM app with no public REST endpoint.  We query the original
# mrob.com CGI interface which does accept GET requests.
_RIES_CGI = "https://mrob.com/pub/ries/ries-cgi.html"


def _query_ries(value: float, timeout: float = 10.0) -> List[ConstantMatch]:
    """
    Query the RIES inverse symbolic calculator online.

    Since RIES is primarily a WASM/CLI tool without a clean REST API,
    we attempt to query mrob.com's CGI interface.  If that fails, we
    return an empty list gracefully.
    """
    global _ries_last_call

    # Rate limiting
    elapsed = time.time() - _ries_last_call
    if elapsed < _RIES_MIN_INTERVAL:
        time.sleep(_RIES_MIN_INTERVAL - elapsed)

    matches = []
    try:
        # mrob.com RIES CGI accepts: ?T=<value>
        url = f"https://mrob.com/pub/ries/ries-cgi.html?T={value}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Prometheus-ConstantMatcher/1.0",
        })
        _ries_last_call = time.time()
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Parse RIES output: lines like "  x = expression  (error)"
        # RIES CGI returns plain-text-ish results in <pre> blocks
        pre_match = re.search(r"<pre[^>]*>(.*?)</pre>", html, re.DOTALL | re.IGNORECASE)
        if not pre_match:
            # Try the whole body for plain text results
            text = re.sub(r"<[^>]+>", "", html)
        else:
            text = pre_match.group(1)

        # Look for lines with "x = ..." or "... = x"
        for line in text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("RIES"):
                continue
            # Typical RIES output:  "  x = sqrt(5+pi)   (3.456e-7)"
            eq_match = re.search(
                r"(x\s*=\s*(.+?)|(.+?)\s*=\s*x)\s*(?:\(([^)]+)\))?$",
                line
            )
            if eq_match:
                expr = (eq_match.group(2) or eq_match.group(3) or "").strip()
                err_str = eq_match.group(4)
                if expr:
                    try:
                        err = float(err_str) if err_str else 0.0
                    except (ValueError, TypeError):
                        err = 0.0
                    residual = abs(err) if err else 0.0
                    conf = max(0.0, 1.0 - residual * 1e6)  # heuristic
                    matches.append(ConstantMatch(
                        value=value,
                        name=f"RIES: {expr}",
                        expression=expr,
                        matched_value=value - residual,
                        residual=residual,
                        confidence=min(1.0, max(0.0, conf)),
                        source="ries",
                    ))
    except Exception as exc:
        # Graceful degradation: RIES is optional
        print(f"  [RIES] Query failed ({exc.__class__.__name__}): {exc}",
              file=sys.stderr)

    return matches


# ---------------------------------------------------------------------------
# Main identification function
# ---------------------------------------------------------------------------

def identify_constant(
    value: float,
    tolerance: float = 1e-6,
    use_ries: bool = True,
) -> List[ConstantMatch]:
    """
    Identify a numerical value as a known mathematical constant.

    Checks against:
      a) Local database of 83+ mathematical constants
      b) RIES online inverse symbolic calculator (rate-limited)
      c) Returns a list of matches with confidence scores

    Parameters
    ----------
    value : float
        The number to identify.
    tolerance : float
        Maximum absolute difference to consider a match (default 1e-6).
    use_ries : bool
        Whether to query RIES online (default True).

    Returns
    -------
    list[ConstantMatch]
        Matches sorted by confidence (highest first).
    """
    matches = _match_local(value, tolerance)

    # RIES lookup (only if no perfect local match found)
    if use_ries and not any(m.residual == 0.0 for m in matches):
        ries_matches = _query_ries(value)
        matches.extend(ries_matches)

    matches.sort(key=lambda m: m.confidence, reverse=True)
    return matches


# ---------------------------------------------------------------------------
# Batch identification
# ---------------------------------------------------------------------------

def batch_identify(
    values: List[float],
    tolerance: float = 1e-6,
    use_ries: bool = False,
    use_algebraic: bool = True,
) -> dict:
    """
    Identify multiple numerical values against known constants.

    Parameters
    ----------
    values : list[float]
        Numbers to identify (e.g., eigenvalues from a matrix).
    tolerance : float
        Maximum absolute difference for a match.
    use_ries : bool
        Whether to query RIES for unmatched values (default False
        for batch to avoid rate limiting).
    use_algebraic : bool
        Whether to check algebraic combinations (default True).

    Returns
    -------
    dict
        Mapping from each value to its list of ConstantMatch results.
        Values with no matches map to an empty list.
    """
    results = {}
    for v in values:
        if use_algebraic:
            matches = check_against_constants(v, tolerance)
        else:
            matches = _match_local(v, tolerance)

        # Optionally try RIES for unmatched values
        if use_ries and not matches:
            matches = _query_ries(v)

        results[v] = matches
    return results


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _format_match(m: ConstantMatch) -> str:
    """Format a single match for human-readable display."""
    qid_str = f"  [Wikidata: {m.wikidata_qid}]" if m.wikidata_qid else ""
    return (
        f"  {m.expression:<40s}  "
        f"= {m.matched_value:<22.15g}  "
        f"residual={m.residual:.2e}  "
        f"conf={m.confidence:.4f}  "
        f"({m.source}){qid_str}"
    )


def save_results(results: dict, output_path: Path):
    """Save batch results to a JSON file."""
    serializable = {}
    for val, matches in results.items():
        serializable[str(val)] = [m.to_dict() for m in matches]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)
    print(f"  Results saved to {output_path}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Identify mathematical constants from numerical values."
    )
    parser.add_argument(
        "values", nargs="*", type=float,
        help="One or more numerical values to identify."
    )
    parser.add_argument(
        "--batch", nargs="+", type=float, default=None,
        help="Batch mode: identify multiple values."
    )
    parser.add_argument(
        "--tolerance", "-t", type=float, default=1e-6,
        help="Match tolerance (default: 1e-6)."
    )
    parser.add_argument(
        "--algebraic", "-a", action="store_true", default=False,
        help="Include algebraic combinations (slower, more thorough)."
    )
    parser.add_argument(
        "--ries", action="store_true", default=False,
        help="Query RIES online (rate-limited)."
    )
    parser.add_argument(
        "--save", "-s", type=str, default=None,
        help="Save results to JSON file."
    )

    args = parser.parse_args()

    all_values = list(args.values or [])
    if args.batch:
        all_values.extend(args.batch)

    if not all_values:
        parser.print_help()
        sys.exit(1)

    for val in all_values:
        print(f"\n{'='*72}")
        print(f"  Identifying: {val}")
        print(f"{'='*72}")

        if args.algebraic:
            matches = check_against_constants(val, args.tolerance)
        else:
            matches = identify_constant(val, args.tolerance, use_ries=args.ries)

        if matches:
            print(f"  Found {len(matches)} match(es):\n")
            for m in matches[:20]:  # Show top 20
                print(_format_match(m))
            if len(matches) > 20:
                print(f"\n  ... and {len(matches) - 20} more.")
        else:
            print("  No matches found.")

    # Save if requested
    if args.save:
        results = {}
        for val in all_values:
            if args.algebraic:
                results[val] = check_against_constants(val, args.tolerance)
            else:
                results[val] = identify_constant(
                    val, args.tolerance, use_ries=args.ries
                )
        save_results(results, Path(args.save))


if __name__ == "__main__":
    main()
