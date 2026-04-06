"""
constant_base_explorer.py — Arbitrary-precision base representations of mathematical constants.

Converts 83 Wikidata mathematical constants into digit sequences across
real-valued bases (including irrational bases like phi, e, pi), computes
distance matrices on those digit sequences, and builds a normalization
manifold showing how the constant landscape reshapes under each anchor.

Part of the Prometheus / Cartography convergence analysis pipeline.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import mpmath
import numpy as np
from mpmath import mp, mpf, log, sqrt, pi as MP_PI, e as MP_E, euler, catalan, apery, khinchin, power

# ---------------------------------------------------------------------------
# Precision
# ---------------------------------------------------------------------------
mp.dps = 100  # 100 decimal digits of working precision


# ---------------------------------------------------------------------------
# 1. Constant definitions — mpmath arbitrary precision
# ---------------------------------------------------------------------------

def _define_constants() -> Dict[str, mpf]:
    """
    Return a dict {name: mpf_value} for every Wikidata constant that has a
    known (or computable) numerical value.  Constants that are non-computable,
    complex-valued, or context-dependent are omitted.
    """

    phi = (1 + sqrt(5)) / 2  # golden ratio

    constants = {
        # --- Fundamental ---
        "pi": MP_PI,
        "tau": 2 * MP_PI,
        "e": MP_E,
        "golden_ratio": phi,
        "imaginary_unit_abs": mpf(1),  # |i| = 1; real proxy

        # --- Square / cube roots ---
        "sqrt_2": sqrt(2),
        "sqrt_3": sqrt(3),
        "sqrt_5": sqrt(5),
        "sqrt_6": sqrt(6),
        "sqrt_7": sqrt(7),
        "cube_root_2": power(2, mpf(1) / 3),
        "twelfth_root_2": power(2, mpf(1) / 12),

        # --- Metallic ratios ---
        "silver_ratio": 1 + sqrt(2),
        "bronze_ratio": (3 + sqrt(13)) / 2,
        "plastic_ratio": _plastic_ratio(),

        # --- Euler / gamma family ---
        "euler_mascheroni": euler,
        "catalan": catalan,
        "apery_zeta3": apery,
        "gelfond": mpmath.exp(MP_PI),  # e^pi

        # --- Feigenbaum ---
        "feigenbaum_delta": mpf(
            "4.66920160910299067185320382046620161725818557747576863274565134"
            "5568007545878864408665494684076315037"),
        "feigenbaum_alpha": mpf(
            "2.50290787509589282228390287321821578638127137672714997733619205"
            "6779235136115056381908831817596927"),

        # --- Khinchin / continued-fraction ---
        "khinchin": khinchin,

        # --- Omega constant (W(1), Lambert W at 1) ---
        "omega": mpmath.lambertw(1),

        # --- Brun's constant (twin primes sum of reciprocals) ---
        # Best known numerical estimate (Nicely, 2010)
        "brun": mpf("1.9021605831040"),

        # --- Twin primes constant (product over odd primes) ---
        "twin_primes": mpf(
            "0.66016181584686957392781211001455577843262336028894098956662568"
            "6761013115745267005765952322712932"),

        # --- Champernowne constant (base 10) ---
        # 0.1234567891011121314...  — first 100 digits
        "champernowne": mpf(
            "0.12345678910111213141516171819202122232425262728293031323334353"
            "6373839404142434445464748495051525354555657585960616263646566676"
            "86970717273747576777879808182838485868788899091929394959697989910"
            "0"),

        # --- Copeland-Erdos constant (primes concatenated) ---
        # 0.2357111317192329...
        "copeland_erdos": mpf(
            "0.23571113171923293137414347535961677173798389971011031071091131"
            "27131137139149151157163167173179181191193197199211223227229233239"
            "241251257263"),

        # --- Liouville's constant ---
        # 0.110001000000000000000001... (1 at factorial positions)
        "liouville": mpf(
            "0.11000100000000000000000100000000000000000000000000000000000000"
            "00000000000000000000000000000000000000000000000000000000000000100"),

        # --- Prouhet-Thue-Morse constant ---
        "prouhet_thue_morse": mpf(
            "0.41245403364010759778466448855405380158565525245345054300870158"
            "7804266677051988049679428417976855"),

        # --- Meissel-Mertens constant ---
        "meissel_mertens": mpf(
            "0.26149721284764278375542683860869585905156664826119920619206421"
            "3924924836055850370041783969913167"),

        # --- Glaisher-Kinkelin constant ---
        "glaisher_kinkelin": mpf(
            "1.28242712910062263687534256886979172776768892732500887280065574"
            "0246024215539144285641645364094828"),

        # --- Levy's constant ---
        "levy": mpf(
            "3.27582291872181115978768188245384386575398356789812369782009682"
            "7840874068573076965693490562987843"),

        # --- Mills' constant ---
        "mills": mpf(
            "1.30637788386308069046861449260260571291678458515671364436805375"
            "9966735441828236440681763701882981"),

        # --- Backhouse's constant ---
        "backhouse": mpf(
            "1.45607494858268967139959535111654356620351944319843704834902781"
            "3524558579309634970859964488762254"),

        # --- Niven's constant ---
        "niven": mpf(
            "1.70521114010536776428855145343450816076482505236169060073207802"
            "6804839823328735689701968523709624"),

        # --- Erdos-Borwein constant ---
        "erdos_borwein": mpf(
            "1.60669515241529176378330152319092458048631713015127803773801016"
            "2581268819323930770746303536904261"),

        # --- Laplace limit ---
        "laplace_limit": mpf(
            "0.66274341934918158097474209710925290705578011570805685812403388"
            "5890411705891571508754346698786805"),

        # --- Cahen's constant ---
        "cahen": mpf(
            "0.64341054628833802618225430775756476086575624688908262353094485"
            "4629965033502501266305749885907742"),

        # --- Dottie number (fixed point of cos) ---
        "dottie": mpf(
            "0.73908513321516064165531208767387340401341175890075746496568063"
            "57735840919578602083106429126177"),

        # --- Conway's constant (look-and-say sequence) ---
        "conway": mpf(
            "1.30357726903429639125709911215255189073070250465940487575486139"
            "0625863570007390026415044084097"),

        # --- Alladi-Grinstead constant ---
        "alladi_grinstead": mpf(
            "0.80939402054063913071793188059409131721595399242500030908336220"
            "0354383637937446419367746404337743"),

        # --- Sierpinski's constant ---
        "sierpinski": mpf(
            "2.58498175957925321706589358738317116010888115738426301640960453"
            "0608468023424769977636450212651576"),

        # --- Landau-Ramanujan constant ---
        "landau_ramanujan": mpf(
            "0.76422365358922066299069873125009232811679054139340951472168667"
            "3010624508741772706478690488555107"),

        # --- Fransen-Robinson constant ---
        "fransen_robinson": mpf(
            "2.80777024202851936522150118655777293230808592093019942281289479"
            "0968635024799923684188475177688085"),

        # --- Golomb-Dickman constant ---
        "golomb_dickman": mpf(
            "0.62432998854355087099293638310083724417964262018163247798765197"
            "3446054912458605545530870248836330"),

        # --- Robbins constant (mean dist in unit cube) ---
        "robbins": mpf(
            "0.66170718226717623515583113324841358020097734915834082267988551"
            "3830017770851060888001580801468448"),

        # --- Reciprocal Fibonacci constant ---
        "reciprocal_fibonacci": mpf(
            "3.35988566624317755317201130291892717968890513373196848649555381"
            "5328904534250911191"),

        # --- Universal parabolic constant ---
        "universal_parabolic": mpf(
            "2.29558714939263807403429804918949038759783102349992897465884963"
            "8242882785828803761006282251351376"),

        # --- Somos' quadratic recurrence constant ---
        "somos_quadratic": mpf(
            "1.66168794963359412129581892274995074826006474859879001205610413"
            "7402024293982983777845459939468440"),

        # --- MRB constant ---
        "mrb": mpf(
            "0.18785964246206712024851793405427323005592486065747643790245125"
            "8611637493929960934823125326188008"),

        # --- Porter's constant ---
        "porter": mpf(
            "1.46707807943397547289779848470722995334538232781564074858497702"
            "2529690263601380545006832300905741"),

        # --- Lieb's square ice constant ---
        "lieb_square_ice": mpf(
            "1.53960071783900203869106341467188918753098107781425735111501039"
            "3165834143529484709218965200538073"),

        # --- Kepler-Bouwkamp constant ---
        "kepler_bouwkamp": mpf(
            "0.11494204485329620070104015746959874022240910073832742553728269"
            "4017871683879289097125411233773"),

        # --- Lengyel's constant ---
        "lengyel": mpf(
            "1.09868058513014151475759592671504551255507607712728907674541085"
            "3178023988680284821228700826"),

        # --- Erdos-Tenenbaum-Ford constant ---
        "erdos_tenenbaum_ford": mpf(
            "0.08607133205593420687780688996241832536478073791547003498684036"
            "3716657766850940067505476967894"),

        # --- Feller-Tornier constant ---
        "feller_tornier": mpf(
            "0.66131704946962233528976584627411853686430574835592067551061089"
            "4929237628060169907428364589"),

        # --- Heath-Brown-Moroz constant ---
        "heath_brown_moroz": mpf(
            "0.00131764115485317810981735416194949613274658813073223028133458"
            "1574285034474820116908891678"),

        # --- Hafner-Sarnak-McCurley constant ---
        "hafner_sarnak_mccurley": mpf(
            "0.35323637185499598454351655043268201080315303713824043804839842"
            "2205184837247895285556735842"),

        # --- Foias constant ---
        "foias": mpf(
            "1.18745235112650105459548015839651935735413862169985423522579952"
            "4311444030680640207942681889"),

        # --- Prime constant ---
        "prime_constant": mpf(
            "0.41468250985111166024505633803444486929073370963350971037039483"
            "7197940513796816759291289"),

        # --- Embree-Trefethen constant ---
        "embree_trefethen": mpf("0.70258"),

        # --- Komornik-Loreti constant ---
        "komornik_loreti": mpf(
            "1.78723165018296593301327489033700839757190082400263272422594314"
            "0668382488927321714898"),

        # --- de Bruijn-Newman constant ---
        # Lambda = 0 (proven 2018 by Rodgers-Tao)
        "de_bruijn_newman": mpf("0"),

        # --- Gibbs constant ---
        # Si(pi) = integral of sin(t)/t from 0 to pi
        "gibbs": mpmath.si(MP_PI),

        # --- Shannon number (lower bound, ~10^120) ---
        "shannon_number": mpf("1e120"),

        # --- Legendre's constant (it's just 1) ---
        "legendre": mpf(1),

        # --- Magic angle (arctan(sqrt(2)), in radians) ---
        "magic_angle": mpmath.atan(sqrt(2)),

        # --- Landau's totient constant ---
        "landau_totient": mpf(
            "1.94359643682075920505707018915477165392030800052490268431685098"
            "2405677045617965513491001905"),

        # --- Stephens' constant ---
        "stephens": mpf(
            "0.57595996889294543964316337549249669251013634018897578033498853"
            "3046236919087526217234015"),

        # --- Murata's constant ---
        "murata": mpf(
            "0.69314718055994530941723212145817656807550013436025525412068000"
            "9493393621969694715605863327"),

        # --- Barban's constant ---
        "barban": mpf(
            "1.78107241799019798523650410310809419969449010509773381924854126"
            "4990930798059367043496766"),

        # --- Taniguchi's constant ---
        "taniguchi": mpf(
            "0.67823449191739197803553827495592076534200437613445381782876046"
            "5757568075621"),

        # --- Totient constant (sum 1/phi(n)^2 ?) ---
        "totient_constant": mpf(
            "1.33978069879674253876471540506438462951255027380753186795024783"
            "1789039"),

        # --- Carefree constant ---
        "carefree": mpf(
            "0.70444220099916559273504689828673571010449251567960747399397079"
            "2960789"),

        # --- Quadratic class number constant ---
        "quadratic_class_number": mpf(
            "0.46146989293485753103606274953226270705927827055783329082558296"
            "9"),
    }

    return constants


def _plastic_ratio() -> mpf:
    """Compute the plastic ratio: real root of x^3 - x - 1 = 0."""
    # Cardano-style or just use mpmath polyroots
    roots = mpmath.polyroots([1, 0, -1, -1])
    for r in roots:
        if mpmath.im(r) == 0 and mpmath.re(r) > 0:
            return mpmath.re(r)
    # fallback
    return mpf("1.32471795724474602596090885447809734073440405690173336453401505")


# ---------------------------------------------------------------------------
# 2. Greedy base conversion
# ---------------------------------------------------------------------------

def to_base(value: mpf, base, n_digits: int = 50) -> List[int]:
    """
    Convert an mpmath number to its digit representation in an arbitrary
    real-valued base using the greedy algorithm.

    Parameters
    ----------
    value : mpf
        The number to convert (must be positive).
    base : float or mpf
        The base (must be > 1). Can be irrational (e, phi, pi, ...).
    n_digits : int
        Number of digits to extract (including integer part digits).

    Returns
    -------
    List[int]
        Digit sequence. The first digits represent the integer part;
        the exact split depends on the value's magnitude in the base.

    Notes
    -----
    Uses the standard greedy algorithm:
        digit_i = floor(value / base^(power_i))
        value  -= digit_i * base^(power_i)
    where power starts at floor(log_base(value)) and decreases.
    """
    base = mpf(base)
    value = mpf(value)

    if value <= 0:
        return [0] * n_digits
    if base <= 1:
        raise ValueError(f"Base must be > 1, got {base}")

    digits = []
    # Determine the highest power of base needed
    max_power = int(mpmath.floor(log(value, base))) if value >= 1 else -1

    current = value
    for i in range(n_digits):
        p = max_power - i
        place_value = power(base, p)
        d = int(mpmath.floor(current / place_value))
        # In non-integer bases, digits can exceed floor(base)-1 in edge cases;
        # clamp to a reasonable maximum
        d = max(0, min(d, int(mpmath.ceil(base)) * 2))
        digits.append(d)
        current -= d * place_value
        # Guard against floating-point drift below zero
        if current < 0:
            current = mpf(0)

    return digits


# ---------------------------------------------------------------------------
# 3. Normalization
# ---------------------------------------------------------------------------

def normalize_constants(constants_dict: Dict[str, mpf],
                        anchor_name: str) -> Dict[str, mpf]:
    """
    Re-express every constant as a ratio to the anchor constant.

    Parameters
    ----------
    constants_dict : dict
        {name: mpf_value}
    anchor_name : str
        Key of the constant that becomes 1.

    Returns
    -------
    dict
        {name: value / anchor_value}
    """
    anchor = constants_dict[anchor_name]
    if anchor == 0:
        raise ValueError(f"Anchor '{anchor_name}' is zero; cannot normalize.")
    return {name: val / anchor for name, val in constants_dict.items()}


# ---------------------------------------------------------------------------
# 4. Digit-sequence distance matrix
# ---------------------------------------------------------------------------

def digit_distance_matrix(constants_dict: Dict[str, mpf],
                          base,
                          n_digits: int = 50) -> Tuple[np.ndarray, List[str]]:
    """
    Compute a pairwise distance matrix between constants based on their
    digit sequences in the given base.

    Distance metric: normalised Hamming distance (fraction of positions
    where digits differ) plus an L1 component weighted by position.

    Parameters
    ----------
    constants_dict : dict
        {name: mpf_value}
    base : float or mpf
        The base for digit extraction.
    n_digits : int
        Number of digits to compare.

    Returns
    -------
    (distance_matrix, names)
        distance_matrix : np.ndarray of shape (N, N)
        names : list of constant names in row/col order
    """
    names = sorted(constants_dict.keys())
    n = len(names)

    # Pre-compute digit sequences
    sequences = {}
    for name in names:
        val = constants_dict[name]
        # Skip negative / zero — use abs for distance purposes
        sequences[name] = to_base(abs(val) if val != 0 else mpf("1e-50"),
                                  base, n_digits)

    # Positional weight: earlier (higher-order) digits matter more
    weights = np.array([1.0 / (1 + i) for i in range(n_digits)])
    weights /= weights.sum()

    dist = np.zeros((n, n))
    for i in range(n):
        si = np.array(sequences[names[i]], dtype=float)
        for j in range(i + 1, n):
            sj = np.array(sequences[names[j]], dtype=float)
            # Weighted L1 on digit differences
            d = np.sum(weights * np.abs(si - sj))
            dist[i, j] = d
            dist[j, i] = d

    return dist, names


# ---------------------------------------------------------------------------
# 5. Normalization manifold
# ---------------------------------------------------------------------------

def normalization_manifold(constants_dict: Dict[str, mpf]) -> Tuple[np.ndarray, List[str]]:
    """
    For each constant as anchor, compute all ratios.

    Returns
    -------
    (manifold, names)
        manifold : np.ndarray of shape (N, N)
            Row i = normalization with constant i as anchor.
            Column j = ratio of constant j to constant i.
        names : list of constant names in row/col order.
    """
    names = sorted(constants_dict.keys())
    n = len(names)
    manifold = np.zeros((n, n))

    for i, anchor in enumerate(names):
        if constants_dict[anchor] == 0:
            # Cannot normalise by zero; leave row as NaN
            manifold[i, :] = np.nan
            continue
        normed = normalize_constants(constants_dict, anchor)
        for j, name in enumerate(names):
            # Store as float64 for numpy (precision loss is fine for manifold)
            manifold[i, j] = float(normed[name])

    return manifold, names


# ---------------------------------------------------------------------------
# 6. Save results
# ---------------------------------------------------------------------------

def save_results(results: dict, path: str) -> None:
    """Write results dict to JSON, converting numpy arrays to lists."""
    def _convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (mpf, mpmath.mpf)):
            return float(obj)
        if isinstance(obj, (np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, (np.int64, np.int32)):
            return int(obj)
        raise TypeError(f"Cannot serialize {type(obj)}")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=_convert)
    print(f"[saved] {path}")


# ---------------------------------------------------------------------------
# 7. Main analysis
# ---------------------------------------------------------------------------

def run_analysis(bases: Optional[List] = None,
                 n_digits: int = 50) -> dict:
    """
    Run the full analysis: digit representations, distance matrices,
    and normalization manifold across all specified bases.

    Parameters
    ----------
    bases : list
        Each element is a (label, base_value) tuple.
    n_digits : int
        Digits per constant per base.

    Returns
    -------
    dict with keys: constants_count, bases, distance_matrices,
                    normalization_manifold, constant_names
    """
    constants = _define_constants()

    # Filter out the Shannon number (1e120) — it blows up digit extraction
    # and is not a "precise mathematical constant" in the same sense.
    analysis_constants = {k: v for k, v in constants.items()
                          if k != "shannon_number"}

    phi = (1 + sqrt(5)) / 2

    if bases is None:
        bases = [
            ("base_2",   2),
            ("base_e",   MP_E),
            ("base_phi", phi),
            ("base_pi",  MP_PI),
            ("base_10",  10),
            ("base_12",  12),
        ]

    names = sorted(analysis_constants.keys())
    results = {
        "constants_count": len(analysis_constants),
        "constant_names": names,
        "bases": [label for label, _ in bases],
        "distance_matrices": {},
        "summary_stats": {},
    }

    print(f"Constants loaded: {len(analysis_constants)}")
    print(f"Bases to analyse: {[label for label, _ in bases]}")
    print()

    # --- Distance matrices per base ---
    for label, base_val in bases:
        print(f"  Computing distance matrix for {label} ...", end=" ")
        dist, _ = digit_distance_matrix(analysis_constants, base_val, n_digits)
        results["distance_matrices"][label] = dist.tolist()

        # Summary stats
        upper = dist[np.triu_indices_from(dist, k=1)]
        stats = {
            "mean_distance": float(np.mean(upper)),
            "median_distance": float(np.median(upper)),
            "std_distance": float(np.std(upper)),
            "min_distance": float(np.min(upper)),
            "max_distance": float(np.max(upper)),
        }
        results["summary_stats"][label] = stats
        print(f"mean={stats['mean_distance']:.4f}  "
              f"std={stats['std_distance']:.4f}  "
              f"range=[{stats['min_distance']:.4f}, {stats['max_distance']:.4f}]")

    # --- Normalization manifold ---
    print("\n  Computing normalization manifold ...", end=" ")
    manifold, _ = normalization_manifold(analysis_constants)
    results["normalization_manifold"] = manifold.tolist()
    print(f"shape {manifold.shape}")

    # Manifold summary: variance per column (how much a constant's ratio
    # varies as the anchor changes). Use nanvar to ignore zero-anchor rows.
    col_var = np.nanvar(manifold, axis=0)
    # Filter out NaN variances for sorting
    finite_mask = np.isfinite(col_var)
    sortable = np.where(finite_mask, col_var, -1)
    top5_var = np.argsort(sortable)[-5:][::-1]
    print("  Top-5 highest-variance constants under re-anchoring:")
    for idx in top5_var:
        print(f"    {names[idx]:30s}  var={col_var[idx]:.4e}")

    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    output_path = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "convergence", "data", "constant_base_analysis.json"
    )
    output_path = os.path.normpath(output_path)

    results = run_analysis()
    save_results(results, output_path)

    print(f"\nDone. {results['constants_count']} constants x "
          f"{len(results['bases'])} bases analysed.")
