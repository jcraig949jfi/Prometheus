"""
Dissection Tensor — GPU-accelerated multi-dimensional signature space.

Architecture:
  1. ENCODE: Pack mathematical objects' dissection signatures into PyTorch
     tensors on GPU. Each object is a point in N-dimensional signature space.
  2. BATTERY: Encode falsification battery results (F1-F27) as additional
     dimensions — the truth boundary becomes geometry in the tensor.
  3. COMPRESS: TT-decomposition (TensorLy) reveals entangled dimensions
     and makes high-dimensional exploration tractable.
  4. EXPLORE: GPU-parallel sweeps for geometric intersections — submanifolds
     where objects from different domains converge.

Dissection strategies mapped to existing data:
  S1  (complex plane eval)  -> knot poly / EC a_p on unit circle grid
  S3  (mod-p fingerprint)  -> EC a_p, knot poly coeffs mod p
  S5  (spectral/FFT)       -> OEIS sequences, knot poly coefficients
  S7  (p-adic valuation)   -> EC conductor factorization, NF discriminant
  S9  (symmetry group)     -> Genus-2 ST groups, crystal space groups
  S10 (Galois group)       -> NF galois_label
  S12 (zeta-like density)  -> point count / divisibility density across domains
  S13 (discriminant)       -> NF disc_abs, EC conductor
  S22 (operadic structure) -> Fungrim formula type/module
  S24 (info-theoretic)     -> Shannon entropy of coefficients

Battery dimensions:
  F_eta2    -> variance decomposition effect size
  F_p       -> permutation null p-value
  F_z       -> z-score
  F_verdict -> categorical (KILLED=0, TENDENCY=1, CONSTRAINT=2, LAW=3, IDENTITY=4)

Machine: M1 (Skullport)
GPU: RTX 5060 Ti, 17GB VRAM
"""
import sys
import json
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

# TensorLy for decomposition
import tensorly as tl
from tensorly.decomposition import tensor_train

# Use PyTorch backend for TensorLy (GPU-native)
tl.set_backend('pytorch')

ROOT = Path(__file__).resolve().parents[3]
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ============================================================
# Data classes
# ============================================================
@dataclass
class MathObject:
    """A mathematical object with its multi-strategy signature."""
    obj_id: str
    domain: str          # 'EC', 'knot', 'NF', 'fungrim', 'genus2', 'OEIS', etc.
    label: str           # human-readable label
    signatures: dict     # strategy_name -> np.array or scalar
    battery: dict = field(default_factory=dict)  # test_id -> battery results
    raw: dict = field(default_factory=dict)      # original data for reference


# ============================================================
# Strategy extractors — compute signatures from raw data
# ============================================================
class StrategyExtractors:
    """Compute dissection signatures from raw mathematical objects."""

    @staticmethod
    def s1_complex(coefficients, n_points=8):
        """S1: Complex plane evaluation.
        Evaluate polynomial with given coefficients on n_points equally spaced
        points on the unit circle: e^{i*pi*k/4} for k=0..n_points-1.
        Returns: vector of magnitudes at each point (length n_points).
        """
        if not coefficients or len(coefficients) < 2:
            return np.full(n_points, np.nan)
        coeffs = np.array(coefficients, dtype=np.complex128)
        grid = np.exp(1j * np.pi * np.arange(n_points) / (n_points / 2))
        mags = np.zeros(n_points, dtype=np.float32)
        for i, z in enumerate(grid):
            # Evaluate polynomial: c0 + c1*z + c2*z^2 + ...
            val = np.polyval(coeffs[::-1], z)
            mags[i] = np.abs(val)
        # Log-scale to tame large magnitudes
        mags = np.log1p(mags).astype(np.float32)
        return mags

    @staticmethod
    def s12_zeta(values, mode="divisibility", primes=(2, 3, 5, 7)):
        """S12: Point count / zeta-like arithmetic density.
        Modes:
          'divisibility' — fraction of values divisible by each prime (OEIS, EC a_p)
          'conductor_mod' — conductor mod each prime (EC)
          'disc_mod' — discriminant mod each prime (NF)
        Returns: vector of length len(primes).
        """
        n_primes = len(primes)
        if values is None:
            return np.full(n_primes, np.nan)

        if mode == "divisibility":
            if not values or len(values) < 2:
                return np.full(n_primes, np.nan)
            n = len(values)
            sig = []
            for p in primes:
                count = sum(1 for v in values if int(v) % p == 0)
                sig.append(count / n)
            return np.array(sig, dtype=np.float32)

        elif mode == "conductor_mod":
            # values is a single integer (conductor)
            cond = abs(int(values))
            if cond == 0:
                return np.full(n_primes, np.nan)
            sig = [float((cond % p) / p) for p in primes]
            return np.array(sig, dtype=np.float32)

        elif mode == "disc_mod":
            # values is a single integer (discriminant)
            disc = abs(int(values))
            if disc == 0:
                return np.full(n_primes, np.nan)
            sig = [float((disc % p) / p) for p in primes]
            return np.array(sig, dtype=np.float32)

        return np.full(n_primes, np.nan)

    @staticmethod
    def s3_mod_p(coefficients, primes=(2, 3, 5, 7, 11, 13)):
        """S3: Modular arithmetic fingerprint.
        For polynomial coefficients, compute residue class coverage mod p.
        Returns: vector of length len(primes) with coverage fractions.
        """
        if not coefficients or len(coefficients) < 2:
            return np.full(len(primes), np.nan)
        sig = []
        for p in primes:
            residues = set(int(c) % p for c in coefficients if c != 0)
            sig.append(len(residues) / p)
        return np.array(sig, dtype=np.float32)

    @staticmethod
    def s5_spectral(values, n_features=8):
        """S5: Spectral decomposition.
        FFT of a sequence -> top-K power spectrum magnitudes.
        Returns: vector of length n_features.
        """
        if not values or len(values) < 4:
            return np.full(n_features, np.nan)
        arr = np.array(values, dtype=np.float64)
        # Normalize
        if np.std(arr) > 0:
            arr = (arr - np.mean(arr)) / np.std(arr)
        spectrum = np.abs(np.fft.rfft(arr))
        # Top-K magnitudes (skip DC component)
        if len(spectrum) > 1:
            spectrum = spectrum[1:]
        # Pad or truncate to n_features
        if len(spectrum) >= n_features:
            sig = np.sort(spectrum)[-n_features:][::-1]
        else:
            sig = np.zeros(n_features)
            sig[:len(spectrum)] = np.sort(spectrum)[::-1]
        return sig.astype(np.float32)

    @staticmethod
    def s7_padic(n, primes=(2, 3, 5, 7, 11)):
        """S7: p-adic valuation.
        For an integer n, compute v_p(n) for each prime p.
        Returns: vector of length len(primes).
        """
        if n is None or n == 0:
            return np.full(len(primes), np.nan)
        n = abs(int(n))
        sig = []
        for p in primes:
            v = 0
            m = n
            while m > 0 and m % p == 0:
                v += 1
                m //= p
            sig.append(v)
        return np.array(sig, dtype=np.float32)

    @staticmethod
    def s10_galois_hash(galois_label, max_dim=8):
        """S10: Galois group encoding.
        Encode Galois label (e.g., '4T3') as a feature vector.
        Returns: vector of length max_dim.
        """
        sig = np.zeros(max_dim, dtype=np.float32)
        if not galois_label:
            sig[:] = np.nan
            return sig
        # Parse nTk format
        parts = galois_label.replace('T', ' ').split()
        if len(parts) == 2:
            try:
                n, k = int(parts[0]), int(parts[1])
                sig[0] = n            # degree
                sig[1] = k            # transitive group index
                sig[2] = n * k        # combined
                sig[3] = np.log1p(n)  # log degree
            except ValueError:
                sig[:] = np.nan
        else:
            sig[:] = np.nan
        return sig

    @staticmethod
    def s13_discriminant(disc, conductor=None, max_dim=4):
        """S13: Discriminant/conductor signature.
        Returns: vector with log magnitude, sign, factorization features.
        """
        sig = np.zeros(max_dim, dtype=np.float32)
        if disc is None:
            sig[:] = np.nan
            return sig
        d = abs(int(disc))
        sig[0] = np.log1p(d)
        sig[1] = 1.0 if disc > 0 else -1.0
        sig[2] = len([i for i in range(2, min(d + 1, 100)) if d % i == 0])  # rough divisor count
        if conductor is not None:
            sig[3] = np.log1p(abs(int(conductor)))
        return sig

    @staticmethod
    def s24_entropy(coefficients):
        """S24: Information-theoretic signature.
        Shannon entropy + compression features of coefficient sequence.
        Returns: vector of length 4.
        """
        if not coefficients or len(coefficients) < 2:
            return np.full(4, np.nan)
        coefficients = np.array(coefficients, dtype=np.float64)
        arr = np.abs(coefficients) + 0.01
        p = arr / arr.sum()
        entropy = -np.sum(p * np.log2(p))
        # Additional features
        sig = np.array([
            entropy,
            np.log1p(float(len(coefficients))),   # length
            np.log1p(float(np.max(np.abs(coefficients)))),  # max magnitude
            float(np.std(coefficients) / (np.mean(np.abs(coefficients)) + 1e-8)),  # CV
        ], dtype=np.float32)
        return sig


# ============================================================
# Battery encoder — F1-F27 results as tensor dimensions
# ============================================================
class BatteryEncoder:
    """Encode falsification battery results as feature vectors."""

    VERDICT_MAP = {
        'KILLED': 0.0, 'SKIP': 0.0,
        'NEGLIGIBLE': 0.1, 'NEGLIGIBLE_EFFECT': 0.1,
        'TENDENCY': 0.3,
        'SMALL_EFFECT': 0.4,
        'CONSTRAINT': 0.5, 'MODERATE_EFFECT': 0.5,
        'CONDITIONAL': 0.7, 'CONDITIONAL_LAW': 0.7,
        'STRONG_EFFECT': 0.8,
        'LAW': 0.9, 'UNIVERSAL': 0.9,
        'IDENTITY': 1.0,
        'SURVIVES': 0.6,
        'ANALYZED': 0.5,
        'NOT_TAUTOLOGY': 0.7,
        'PARTIAL_MATCH': 0.4,
        'CONTEXT_DEPENDENT': 0.5,
        'CONSISTENT': 0.6,
        'EXTREME_TAIL_DRIVEN': 0.3,
    }

    @classmethod
    def encode(cls, battery_result, n_dims=8):
        """Encode a single test's battery results into a feature vector.

        Extracts: verdict_score, eta_squared, p_value, z_score,
                  m4m2, f25_verdict, f27_verdict, spearman_r
        """
        sig = np.full(n_dims, np.nan, dtype=np.float32)

        if not battery_result:
            return sig

        # Verdict -> score
        verdict = battery_result.get('verdict', '')
        sig[0] = cls.VERDICT_MAP.get(verdict, 0.5)

        # eta^2 from F24
        f24 = battery_result.get('f24', battery_result.get('f24_by_rank', {}))
        if isinstance(f24, dict):
            eta2 = f24.get('eta_squared')
            if eta2 is not None:
                sig[1] = float(eta2)

        # p-value
        p_val = battery_result.get('p')
        if p_val is not None:
            sig[2] = -np.log10(max(float(p_val), 1e-300))  # log-scale

        # z-score
        z = battery_result.get('z')
        if z is not None:
            sig[3] = float(z)

        # M4/M^2 from F24b
        f24b = battery_result.get('f24b', {})
        if isinstance(f24b, dict):
            m4m2 = f24b.get('m4m2_ratio')
            if m4m2 is not None and isinstance(m4m2, (int, float)):
                sig[4] = float(m4m2)

        # F25 transportability
        f25 = battery_result.get('f25', {})
        if isinstance(f25, dict):
            f25_v = f25.get('verdict', '')
            sig[5] = cls.VERDICT_MAP.get(f25_v, 0.5)

        # F27 consequence check
        f27 = battery_result.get('f27', {})
        if isinstance(f27, dict):
            f27_v = f27.get('verdict', '')
            sig[6] = cls.VERDICT_MAP.get(f27_v, 0.5)

        # Correlation (Spearman r)
        r = battery_result.get('spearman_r')
        if r is not None:
            sig[7] = float(r)

        return sig


# ============================================================
# Data loaders — extract MathObjects from existing datasets
# ============================================================
class DataLoaders:
    """Load mathematical objects from Prometheus datasets."""

    @staticmethod
    def load_knots(max_n=None):
        """Load knots with Alexander/Jones polynomial signatures."""
        path = ROOT / "cartography/knots/data/knots.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        objects = []
        ext = StrategyExtractors

        for k in data["knots"][:max_n]:
            obj = MathObject(
                obj_id=f"knot_{k['name']}",
                domain="knot",
                label=k["name"],
                signatures={},
                raw={"crossing_number": k.get("crossing_number", 0),
                     "determinant": k.get("determinant", 0)},
            )

            # S1: complex plane evaluation on Alexander polynomial
            ac = k.get("alex_coeffs", [])
            obj.signatures["s1_alex"] = ext.s1_complex(ac)

            # S1: complex plane evaluation on Jones polynomial
            jc = k.get("jones_coeffs", [])
            obj.signatures["s1_jones"] = ext.s1_complex(jc)

            # S3: mod-p on Alexander coefficients
            obj.signatures["s3_alex"] = ext.s3_mod_p(ac)

            # S3: mod-p on Jones coefficients
            obj.signatures["s3_jones"] = ext.s3_mod_p(jc)

            # S5: spectral on Alexander
            obj.signatures["s5_alex"] = ext.s5_spectral(ac)

            # S5: spectral on Jones
            obj.signatures["s5_jones"] = ext.s5_spectral(jc)

            # S7: p-adic valuation of determinant
            det = k.get("determinant")
            obj.signatures["s7_det"] = ext.s7_padic(det)

            # S13: determinant as discriminant analog
            obj.signatures["s13"] = ext.s13_discriminant(det)

            # S24: entropy of Alexander coefficients
            obj.signatures["s24_alex"] = ext.s24_entropy(ac)

            objects.append(obj)
        return objects

    @staticmethod
    def load_number_fields(max_n=None):
        """Load number fields with algebraic signatures."""
        path = ROOT / "cartography/number_fields/data/number_fields.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        objects = []
        ext = StrategyExtractors

        for f in data[:max_n]:
            try:
                disc = int(f["disc_abs"])
                obj = MathObject(
                    obj_id=f"nf_{f['label']}",
                    domain="NF",
                    label=f["label"],
                    signatures={},
                    raw={"degree": int(f["degree"]),
                         "class_number": int(f.get("class_number", 0)),
                         "regulator": float(f.get("regulator", 0))},
                )
                # S7: p-adic valuation of discriminant
                obj.signatures["s7_disc"] = ext.s7_padic(disc)

                # S10: Galois group
                obj.signatures["s10"] = ext.s10_galois_hash(f.get("galois_label"))

                # S12: zeta-like density from discriminant mod p
                obj.signatures["s12_nf"] = ext.s12_zeta(disc, mode="disc_mod")

                # S13: discriminant
                obj.signatures["s13"] = ext.s13_discriminant(
                    disc * (1 if f.get("disc_sign", "1") == "1" else -1)
                )

                # S24: class number / regulator as "coefficient" analog
                cn = int(f.get("class_number", 0))
                reg = float(f.get("regulator", 0))
                if cn > 0 and reg > 0:
                    obj.signatures["s24_arith"] = np.array([
                        np.log1p(cn), np.log1p(reg),
                        np.log1p(cn * reg / max(np.sqrt(disc), 1)),  # Brauer-Siegel
                        float(f["degree"]),
                    ], dtype=np.float32)
                else:
                    obj.signatures["s24_arith"] = np.full(4, np.nan)

                objects.append(obj)
            except (ValueError, TypeError):
                continue
        return objects

    @staticmethod
    def load_ec(max_n=None):
        """Load elliptic curves from DuckDB."""
        import duckdb
        con = duckdb.connect(str(ROOT / "charon/data/charon.duckdb"), read_only=True)
        df = con.execute(f"""
            SELECT lmfdb_label, conductor, rank, analytic_rank,
                   torsion, torsion_structure, aplist, bad_primes
            FROM elliptic_curves
            WHERE rank IS NOT NULL
            {"LIMIT " + str(max_n) if max_n else ""}
        """).fetchdf()
        con.close()

        objects = []
        ext = StrategyExtractors

        for _, row in df.iterrows():
            cond = int(row["conductor"])
            obj = MathObject(
                obj_id=f"ec_{row['lmfdb_label']}",
                domain="EC",
                label=row["lmfdb_label"],
                signatures={},
                raw={"conductor": cond, "rank": int(row["rank"]),
                     "torsion": int(row["torsion"]),
                     "analytic_rank": int(row["analytic_rank"])},
            )

            # S1: complex plane evaluation on a_p sequence (treated as polynomial coeffs)
            ap = row.get("aplist")
            if ap is not None and hasattr(ap, '__len__') and len(ap) >= 3:
                ap_list = [int(x) for x in ap[:50] if x is not None]
                obj.signatures["s1_ap"] = ext.s1_complex(ap_list)
                obj.signatures["s3_ap"] = ext.s3_mod_p(ap_list)
                obj.signatures["s5_ap"] = ext.s5_spectral(ap_list)
                obj.signatures["s24_ap"] = ext.s24_entropy(ap_list)
                # S12: divisibility density from a_p values
                obj.signatures["s12_ec"] = ext.s12_zeta(ap_list, mode="divisibility")
            else:
                obj.signatures["s1_ap"] = np.full(8, np.nan)
                obj.signatures["s3_ap"] = np.full(6, np.nan)
                obj.signatures["s5_ap"] = np.full(8, np.nan)
                obj.signatures["s24_ap"] = np.full(4, np.nan)
                obj.signatures["s12_ec"] = np.full(4, np.nan)

            # S7: p-adic valuation of conductor
            obj.signatures["s7_cond"] = ext.s7_padic(cond)

            # S13: conductor as discriminant
            obj.signatures["s13"] = ext.s13_discriminant(cond)

            objects.append(obj)
        return objects

    @staticmethod
    def load_oeis(max_n=20000):
        """Load OEIS sequences with spectral and attractor signatures."""
        path = ROOT / "cartography/oeis/data/stripped_new.txt"
        if not path.exists():
            print("  OEIS stripped_new.txt not found, skipping")
            return []

        objects = []
        ext = StrategyExtractors
        count = 0

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Format: A-number ,term1,term2,...
                idx = line.find(",")
                if idx < 0:
                    continue
                a_num = line[:idx].strip()
                terms_str = line[idx:].strip().strip(",")
                if not terms_str:
                    continue
                try:
                    terms = [int(t.strip()) for t in terms_str.split(",") if t.strip()]
                except ValueError:
                    continue

                if len(terms) < 10:
                    continue

                terms = terms[:100]  # cap

                obj = MathObject(
                    obj_id=f"oeis_{a_num}",
                    domain="OEIS",
                    label=a_num,
                    signatures={},
                    raw={"n_terms": len(terms), "first_term": terms[0]},
                )

                # S5: spectral
                obj.signatures["s5_oeis"] = ext.s5_spectral(terms)

                # S6: attractor (phase space) — (a(n), a(n+1)) statistics
                if len(terms) >= 20:
                    diffs = np.diff(terms[:50])
                    arr = np.array(terms[:50], dtype=float)
                    # Lyapunov-like: mean |log(|diff|)|
                    abs_diffs = np.abs(diffs).astype(float) + 1
                    lyap = np.mean(np.log(abs_diffs))
                    # Autocorrelation at lag 1
                    if np.std(arr) > 0:
                        ac1 = np.corrcoef(arr[:-1], arr[1:])[0, 1]
                    else:
                        ac1 = 0.0
                    obj.signatures["s6_oeis"] = np.array([
                        lyap,
                        ac1 if np.isfinite(ac1) else 0.0,
                        np.log1p(float(np.max(np.abs(np.array(terms[:50], dtype=float))))),
                        float(np.std(diffs) / (np.mean(np.abs(diffs)) + 1e-8)),
                    ], dtype=np.float32)
                else:
                    obj.signatures["s6_oeis"] = np.full(4, np.nan)

                # S3: mod-p on terms
                obj.signatures["s3_ap"] = ext.s3_mod_p(terms)

                # S12: zeta-like divisibility density
                obj.signatures["s12_oeis"] = ext.s12_zeta(terms, mode="divisibility")

                # S24: entropy
                obj.signatures["s24_oeis"] = ext.s24_entropy(terms)

                objects.append(obj)
                count += 1
                if count >= max_n:
                    break

        return objects

    @staticmethod
    def load_genus2(max_n=None):
        """Load genus-2 curves with symmetry and conductor signatures."""
        path = ROOT / "cartography/genus2/data/genus2_curves_full.json"
        if not path.exists():
            path = ROOT / "cartography/genus2/data/genus2_curves.json"
        if not path.exists():
            print("  genus-2 data not found, skipping")
            return []

        data = json.loads(path.read_text(encoding="utf-8"))
        curves = data if isinstance(data, list) else data.get("curves", data.get("data", []))
        objects = []
        ext = StrategyExtractors

        for c in curves[:max_n]:
            cond = c.get("conductor") or c.get("cond")
            if not cond:
                continue
            try:
                cond = int(cond)
            except (ValueError, TypeError):
                continue

            obj = MathObject(
                obj_id=f"g2_{c.get('label', c.get('lmfdb_label', str(cond)))}",
                domain="genus2",
                label=str(c.get("label", c.get("lmfdb_label", ""))),
                signatures={},
                raw={"conductor": cond,
                     "st_group": c.get("st_group", c.get("st_group_label", ""))},
            )

            # S7: p-adic valuation of conductor
            obj.signatures["s7_cond"] = ext.s7_padic(cond)

            # S13: conductor as discriminant
            disc = c.get("disc", c.get("abs_disc", cond))
            obj.signatures["s13"] = ext.s13_discriminant(disc, conductor=cond)

            # S9: Sato-Tate group as symmetry encoding
            st = c.get("st_group", c.get("st_group_label", ""))
            st_map = {"USp(4)": 0, "N(G_{3,3})": 1, "G_{3,3}": 2,
                      "N(U(1))": 3, "SU(2)": 4, "U(1)": 5,
                      "E_6": 6, "J(E_6)": 7, "E_4": 8, "J(E_4)": 9}
            obj.signatures["s9_st"] = np.array([
                st_map.get(st, -1),
                float(len(st)) / 10.0,  # name length as proxy
                1.0 if "N(" in st else 0.0,  # normalizer flag
                1.0 if "J(" in st else 0.0,  # J-flag
            ], dtype=np.float32)

            objects.append(obj)

        return objects

    @staticmethod
    def load_fungrim(max_n=None):
        """Load Fungrim formulas with operadic/symbolic signatures."""
        import ast
        path = ROOT / "cartography/fungrim/data/fungrim_index.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        objects = []

        for f in data["formulas"][:max_n]:
            nsym = int(f["n_symbols"])
            symbols = f.get("symbols", [])
            if isinstance(symbols, str):
                try:
                    symbols = ast.literal_eval(symbols)
                except:
                    symbols = []

            obj = MathObject(
                obj_id=f"fg_{f['id']}",
                domain="fungrim",
                label=f"{f['module']}/{f['id']}",
                signatures={},
                raw={"module": f["module"], "type": f["type"],
                     "n_symbols": nsym},
            )

            # S22: operadic — encode type and module as features
            type_map = {"equation": 0, "definition": 1, "domain": 2,
                        "table": 3, "identity": 4}
            obj.signatures["s22"] = np.array([
                type_map.get(f["type"], -1),
                nsym,
                len(symbols),
                hash(f["module"]) % 1000 / 1000.0,  # module hash
            ], dtype=np.float32)

            # S24: symbol frequency as entropy
            obj.signatures["s24_sym"] = np.array([
                np.log1p(nsym),
                1.0 if "Pi" in symbols else 0.0,
                1.0 if any("Zeta" in s for s in symbols) else 0.0,
                1.0 if "Infinity" in symbols else 0.0,
            ], dtype=np.float32)

            objects.append(obj)
        return objects


# ============================================================
# The Dissection Tensor
# ============================================================
class DissectionTensor:
    """GPU-resident multi-dimensional signature tensor.

    Packs mathematical objects from multiple domains into a dense
    tensor where each row is an object and columns are dissection
    strategy dimensions. NaN = strategy not applicable to this object.

    Dimensions:
      s1_alex[8], s1_jones[8], s1_ap[8]  = 24  (complex plane eval)
      s3_alex[6], s3_jones[6], s3_ap[6]  = 18  (mod-p fingerprints)
      s5_alex[8], s5_jones[8], s5_ap[8]  = 24  (spectral)
      s7_det[5], s7_disc[5], s7_cond[5]  = 15  (p-adic)
      s10[8]                              =  8  (Galois)
      s12_ec[4], s12_oeis[4], s12_nf[4]  = 12  (zeta-like density)
      s13[4]                              =  4  (discriminant)
      s22[4]                              =  4  (operadic)
      s24_alex[4], s24_arith[4],
        s24_ap[4], s24_sym[4]             = 16  (entropy)
      battery[8]                          =  8  (falsification)
      ---
      Total: ~145 dimensions
    """

    # Strategy name -> dimensionality
    STRATEGY_DIMS = {
        "s1_alex": 8, "s1_jones": 8, "s1_ap": 8,
        "s3_alex": 6, "s3_jones": 6, "s3_ap": 6,
        "s5_alex": 8, "s5_jones": 8, "s5_ap": 8, "s5_oeis": 8,
        "s6_oeis": 4,
        "s7_det": 5, "s7_disc": 5, "s7_cond": 5,
        "s9_st": 4,
        "s10": 8,
        "s12_ec": 4, "s12_oeis": 4, "s12_nf": 4,
        "s13": 4,
        "s22": 4,
        "s24_alex": 4, "s24_arith": 4, "s24_ap": 4, "s24_sym": 4,
        "s24_oeis": 4,
    }

    TOTAL_DIMS = sum(STRATEGY_DIMS.values())

    # Strategy groups — which strategies are "the same lens" across domains.
    # Cross-domain distance requires matches within at least 2 groups.
    STRATEGY_GROUPS = {
        "complex":   ["s1_alex", "s1_jones", "s1_ap"],
        "mod_p":     ["s3_alex", "s3_jones", "s3_ap"],
        "spectral":  ["s5_alex", "s5_jones", "s5_ap", "s5_oeis"],
        "padic":     ["s7_det", "s7_disc", "s7_cond"],
        "symmetry":  ["s9_st"],
        "galois":    ["s10"],
        "zeta":      ["s12_ec", "s12_oeis", "s12_nf"],
        "disc_cond": ["s13"],
        "operadic":  ["s22"],
        "entropy":   ["s24_alex", "s24_arith", "s24_ap", "s24_sym", "s24_oeis"],
        "attractor": ["s6_oeis"],
    }

    def __init__(self):
        self.objects = []
        self.domain_indices = defaultdict(list)  # domain -> [indices]
        self.tensor = None       # [N, D] on GPU
        self.mask = None         # [N, D] boolean — True where data exists
        self.labels = []         # obj_id list
        self.domains = []        # domain list
        self._strategy_slices = {}  # strategy_name -> (start, end) in dim axis
        self._group_slices = {}    # group_name -> (start, end) covering all strategies in group
        self.battery_index = {}    # test_id -> BatteryEncoder.encode() result
        self.battery_domains = {}  # test_id -> (domain_a, domain_b) the hypothesis spans

        # Build slice map
        offset = 0
        for name, dim in self.STRATEGY_DIMS.items():
            self._strategy_slices[name] = (offset, offset + dim)
            offset += dim

        # Build group slice map
        for group_name, strat_list in self.STRATEGY_GROUPS.items():
            starts = [self._strategy_slices[s][0] for s in strat_list if s in self._strategy_slices]
            ends = [self._strategy_slices[s][1] for s in strat_list if s in self._strategy_slices]
            if starts:
                self._group_slices[group_name] = (min(starts), max(ends))

    def add_objects(self, objects):
        """Add a list of MathObjects."""
        for obj in objects:
            idx = len(self.objects)
            self.objects.append(obj)
            self.domain_indices[obj.domain].append(idx)
            self.labels.append(obj.obj_id)
            self.domains.append(obj.domain)

    def add_battery_results(self, test_id, result_dict, domain_a=None, domain_b=None):
        """Register battery results as truth-boundary constraints.

        Battery results are NOT per-object dimensions. They are properties
        of hypotheses about relationships between domain pairs. Stored in
        a separate index and used as post-filters on intersections.
        """
        encoded = BatteryEncoder.encode(result_dict)
        self.battery_index[test_id] = {
            "encoded": encoded,
            "result": result_dict,
            "domains": (domain_a, domain_b),
        }

    def build(self):
        """Pack all objects into a GPU tensor."""
        N = len(self.objects)
        D = self.TOTAL_DIMS
        print(f"Building dissection tensor: {N} objects x {D} dimensions")

        # Allocate on CPU first (NaN-filled)
        data = np.full((N, D), np.nan, dtype=np.float32)

        for i, obj in enumerate(self.objects):
            # Fill each strategy slice
            for strat_name, sig in obj.signatures.items():
                if strat_name in self._strategy_slices:
                    start, end = self._strategy_slices[strat_name]
                    dim = end - start
                    if len(sig) == dim:
                        data[i, start:end] = sig
                    elif len(sig) > dim:
                        data[i, start:end] = sig[:dim]
                    else:
                        data[i, start:start + len(sig)] = sig

        # Create mask (True where we have data)
        mask = ~np.isnan(data)

        # Replace NaN with 0 for GPU operations (mask tracks validity)
        data_clean = np.nan_to_num(data, nan=0.0)

        # Move to GPU
        self.tensor = torch.tensor(data_clean, device=DEVICE, dtype=torch.float32)
        self.mask = torch.tensor(mask, device=DEVICE, dtype=torch.bool)

        # Stats
        fill_rate = mask.sum() / mask.size * 100
        print(f"  Tensor shape: {self.tensor.shape}")
        print(f"  Device: {self.tensor.device}")
        print(f"  Fill rate: {fill_rate:.1f}%")
        print(f"  Memory: {self.tensor.element_size() * self.tensor.nelement() / 1e6:.1f} MB")

        # Per-strategy fill rates
        for name, (start, end) in self._strategy_slices.items():
            strat_mask = mask[:, start:end]
            strat_fill = strat_mask.any(axis=1).sum() / N * 100
            print(f"    {name:12s}: {strat_fill:5.1f}% of objects have data")

        return self.tensor

    def normalize(self):
        """Per-dimension normalization (z-score where data exists)."""
        if self.tensor is None:
            raise ValueError("Call build() first")

        # Compute mean/std only over valid entries
        masked = self.tensor * self.mask.float()
        counts = self.mask.float().sum(dim=0).clamp(min=1)
        means = masked.sum(dim=0) / counts
        sq_diff = ((self.tensor - means) ** 2) * self.mask.float()
        stds = (sq_diff.sum(dim=0) / counts).sqrt().clamp(min=1e-8)

        # Normalize in-place
        self.tensor = ((self.tensor - means) / stds) * self.mask.float()
        print(f"Normalized: mean ~ 0, std ~ 1 per dimension")

    def get_strategy_slice(self, strategy_name):
        """Get tensor slice for a specific strategy."""
        start, end = self._strategy_slices[strategy_name]
        return self.tensor[:, start:end], self.mask[:, start:end]

    def get_domain_mask(self, domain):
        """Boolean mask for objects from a specific domain."""
        indices = self.domain_indices[domain]
        mask = torch.zeros(len(self.objects), device=DEVICE, dtype=torch.bool)
        mask[indices] = True
        return mask

    # ============================================================
    # GPU-accelerated exploration
    # ============================================================
    def cross_domain_distances(self, domain_a, domain_b,
                               strategies=None, min_shared_groups=1,
                               top_k=50):
        """Find closest pairs between two domains in signature space.

        Uses strategy-group-aware distance: only compares dimensions
        where both objects have data, and requires matches in at least
        min_shared_groups distinct strategy groups.

        Args:
            domain_a, domain_b: domain names (e.g., 'knot', 'EC')
            strategies: list of strategy names to use (None = all math strategies)
            min_shared_groups: minimum distinct strategy groups with shared data
            top_k: number of closest pairs to return

        Returns:
            list of (obj_a_id, obj_b_id, distance, n_shared_dims)
        """
        idx_a = torch.tensor(self.domain_indices[domain_a], device=DEVICE)
        idx_b = torch.tensor(self.domain_indices[domain_b], device=DEVICE)

        if len(idx_a) == 0 or len(idx_b) == 0:
            return []

        # Select strategy columns (exclude battery — it's a post-filter)
        if strategies:
            cols = []
            for s in strategies:
                if s in self._strategy_slices:
                    start, end = self._strategy_slices[s]
                    cols.extend(range(start, end))
            cols = torch.tensor(cols, device=DEVICE)
        else:
            cols = torch.arange(self.TOTAL_DIMS, device=DEVICE)

        # Extract sub-tensors
        t_a = self.tensor[idx_a][:, cols]  # [Na, d]
        t_b = self.tensor[idx_b][:, cols]  # [Nb, d]
        m_a = self.mask[idx_a][:, cols]
        m_b = self.mask[idx_b][:, cols]

        Na, Nb = len(idx_a), len(idx_b)

        # Batch pairwise distances to avoid OOM
        # Process in chunks of batch_size rows from domain A
        batch_size = max(1, min(2000, int(1e9 / (Nb * len(cols) * 4))))
        best_dists = torch.full((top_k,), float('inf'), device=DEVICE)
        best_indices = torch.zeros((top_k, 2), device=DEVICE, dtype=torch.long)

        for start in range(0, Na, batch_size):
            end = min(start + batch_size, Na)
            chunk_a = t_a[start:end]    # [chunk, d]
            chunk_ma = m_a[start:end]

            # Pairwise within chunk: [chunk, 1, d] - [1, Nb, d]
            diff = chunk_a.unsqueeze(1) - t_b.unsqueeze(0)
            shared_mask = chunk_ma.unsqueeze(1) & m_b.unsqueeze(0)

            sq_diff = (diff ** 2) * shared_mask.float()
            n_shared = shared_mask.float().sum(dim=2).clamp(min=1)
            dists = (sq_diff.sum(dim=2) / n_shared).sqrt()
            # Require minimum shared dimensions (at least 2 strategy groups)
            min_dims = max(5, min_shared_groups * 4)
            dists[n_shared < min_dims] = float('inf')

            # Find top-k in this chunk
            chunk_flat = dists.flatten()
            k_chunk = min(top_k, chunk_flat.numel())
            vals, flat_idx = torch.topk(chunk_flat, k_chunk, largest=False)

            # Convert flat indices to (i_a_local, i_b)
            i_a_local = flat_idx // Nb
            i_b_idx = flat_idx % Nb

            # Track n_shared for this chunk
            chunk_n_shared = n_shared  # [chunk, Nb]

            # Merge with running best
            for j in range(k_chunk):
                v = vals[j]
                if v < best_dists[-1]:
                    ia_local = i_a_local[j].item()
                    ib_local = i_b_idx[j].item()
                    best_dists[-1] = v
                    best_indices[-1, 0] = start + ia_local
                    best_indices[-1, 1] = ib_local
                    # Store n_shared in a separate tensor
                    if not hasattr(self, '_best_nshared'):
                        self._best_nshared = torch.zeros(top_k, device=DEVICE)
                    self._best_nshared[-1] = chunk_n_shared[ia_local, ib_local]
                    # Re-sort
                    order = best_dists.argsort()
                    best_dists = best_dists[order]
                    best_indices = best_indices[order]
                    self._best_nshared = self._best_nshared[order]

            del diff, shared_mask, sq_diff, dists, chunk_flat, chunk_n_shared
            torch.cuda.empty_cache()

        results = []
        for k_i in range(top_k):
            val = best_dists[k_i].item()
            if np.isinf(val):
                continue
            ia = best_indices[k_i, 0].item()
            ib = best_indices[k_i, 1].item()
            ns = int(self._best_nshared[k_i].item()) if hasattr(self, '_best_nshared') else 0
            obj_a = self.objects[idx_a[ia].item()]
            obj_b = self.objects[idx_b[ib].item()]
            results.append((obj_a.obj_id, obj_b.obj_id, float(val), ns))

        if hasattr(self, '_best_nshared'):
            del self._best_nshared

        return results

    def find_intersections(self, threshold=1.0, strategies=None,
                           min_shared_groups=2, top_k=100):
        """Find cross-domain intersections — object pairs from different
        domains that are close in signature space.

        Returns sorted list of (obj_a, obj_b, distance, n_shared_dims).
        """
        domains = list(self.domain_indices.keys())
        all_pairs = []

        for i, da in enumerate(domains):
            for db in domains[i + 1:]:
                pairs = self.cross_domain_distances(
                    da, db, strategies, min_shared_groups, top_k)
                all_pairs.extend(pairs)

        # Sort by distance, filter by threshold
        all_pairs.sort(key=lambda x: x[2])
        return [p for p in all_pairs if p[2] < threshold][:top_k]

    def tt_decompose(self, rank=5):
        """Tensor Train decomposition via TensorLy.

        Compresses the signature tensor and reveals which dimensions
        are entangled. Bond dimensions between TT cores indicate
        dimensional coupling strength.

        Returns: (tt_factors, bond_dimensions, reconstruction_error)
        """
        if self.tensor is None:
            raise ValueError("Call build() first")

        print(f"TT decomposition (rank={rank})...")

        # TensorLy TT on 2D is essentially SVD-based
        # Reshape into a higher-order tensor for meaningful TT:
        # Group dimensions by strategy for interpretable cores
        strategy_groups = []
        group_names = []
        for name, (start, end) in self._strategy_slices.items():
            strategy_groups.append(self.tensor[:, start:end])
            group_names.append(name)

        # Stack into [N, S1_dim, S2_dim, ...] — but strategies have
        # different dims, so we pad to max and reshape
        # For now, do TT on the flat [N, D] tensor
        t = self.tensor.cpu()  # TensorLy TT works on CPU
        tl_tensor = tl.tensor(t)

        try:
            tt = tensor_train(tl_tensor, rank=rank)
            # Reconstruction error
            reconstructed = tl.tt_to_tensor(tt)
            error = torch.norm(t - torch.tensor(reconstructed)) / torch.norm(t)

            # Bond dimensions
            bond_dims = [core.shape[-1] for core in tt[:-1]]

            print(f"  Cores: {len(tt)}")
            print(f"  Bond dimensions: {bond_dims}")
            print(f"  Reconstruction error: {error:.4f}")
            print(f"  Compression ratio: {t.numel() / sum(c.numel() for c in tt):.1f}x")

            return tt, bond_dims, float(error)
        except Exception as e:
            print(f"  TT decomposition failed: {e}")
            return None, None, None

    def tt_decompose_grouped(self, rank=5):
        """Strategy-grouped TT decomposition.

        Reshapes [N, D] into [N, G1, G2, ..., Gk] where Gi is a
        low-dimensional summary of strategy group i (mean + std across
        dims in that group). Then runs TT decomposition on the resulting
        higher-order tensor.

        Bond dimensions between adjacent strategy-group cores reveal
        which strategy pairs are ENTANGLED (high bond dim = strong
        coupling between those mathematical lenses).

        Returns: (tt_factors, bond_dims, group_names, entanglement_pairs)
        """
        if self.tensor is None:
            raise ValueError("Call build() first")

        group_names = list(self.STRATEGY_GROUPS.keys())
        n_groups = len(group_names)
        N = self.tensor.shape[0]

        print(f"\nStrategy-grouped TT decomposition (rank={rank})...")
        print(f"  Groups: {group_names}")

        # Build [N, n_groups, 2] features tensor on GPU:
        # For each group, compute (masked mean, masked std) across all dims
        group_features = torch.zeros(N, n_groups, 2, device=DEVICE)

        for gi, gname in enumerate(group_names):
            strat_list = self.STRATEGY_GROUPS[gname]
            cols = []
            for sname in strat_list:
                if sname in self._strategy_slices:
                    start, end = self._strategy_slices[sname]
                    cols.extend(range(start, end))
            if not cols:
                continue
            col_idx = torch.tensor(cols, device=DEVICE)
            group_vals = self.tensor[:, col_idx]       # [N, group_dim]
            group_mask = self.mask[:, col_idx].float()  # [N, group_dim]
            denom = group_mask.sum(dim=1).clamp(min=1)
            mean = (group_vals * group_mask).sum(dim=1) / denom
            sq_diff = ((group_vals - mean.unsqueeze(1)) ** 2) * group_mask
            std = (sq_diff.sum(dim=1) / denom).sqrt()
            group_features[:, gi, 0] = mean
            group_features[:, gi, 1] = std

        # Reshape into higher-order tensor: [N, 2, 2, ..., 2] (n_groups modes of size 2)
        # Build via successive outer products
        ho_tensor = group_features[:, 0, :]  # [N, 2]
        for gi in range(1, n_groups):
            # [N, 2, ..., 2] x [N, 2] -> [N, 2, ..., 2, 2]
            ho_tensor = ho_tensor.unsqueeze(-1) * group_features[:, gi, :].unsqueeze(1)
            target_shape = [N] + [2] * (gi + 1)
            ho_tensor = ho_tensor.reshape(target_shape)

        print(f"  Higher-order tensor shape: {list(ho_tensor.shape)}")
        print(f"  Modes: N={N}, " +
              ", ".join(f"{gname}=2" for gname in group_names))

        # TT decomposition via TensorLy (CPU)
        t_cpu = ho_tensor.cpu()
        tl_tensor = tl.tensor(t_cpu)

        try:
            tt = tensor_train(tl_tensor, rank=rank)

            # Reconstruction error
            reconstructed = tl.tt_to_tensor(tt)
            error = torch.norm(t_cpu - torch.tensor(reconstructed)) / torch.norm(t_cpu)

            # Bond dimensions between cores
            bond_dims = [core.shape[-1] for core in tt[:-1]]

            print(f"  Cores: {len(tt)}")
            print(f"  Core shapes: {[list(c.shape) for c in tt]}")
            print(f"  Bond dimensions: {bond_dims}")
            print(f"  Reconstruction error: {error:.4f}")

            # Identify entangled strategy pairs (high bond dim between adjacent cores)
            # Core 0 is N-mode, cores 1..k are strategy groups
            # Bond between core i and core i+1 connects group_names[i-1] to group_names[i]
            entanglement_pairs = []
            print(f"\n  Strategy entanglement (bond dimensions):")
            for bi in range(len(bond_dims)):
                if bi == 0:
                    left = "objects"
                else:
                    left = group_names[bi - 1]
                if bi < len(group_names):
                    right = group_names[bi]
                else:
                    right = "terminal"
                bd = bond_dims[bi]
                entanglement_pairs.append((left, right, bd))
                marker = " ***" if bd == rank else ""
                print(f"    {left:12s} <-> {right:12s}: bond_dim={bd}{marker}")

            # Sort by bond dim to show strongest couplings
            entanglement_pairs.sort(key=lambda x: x[2], reverse=True)
            print(f"\n  Strongest couplings (saturated bond = max entanglement):")
            for left, right, bd in entanglement_pairs[:5]:
                print(f"    {left} <-> {right}: {bd}")

            return tt, bond_dims, group_names, entanglement_pairs

        except Exception as e:
            print(f"  Grouped TT decomposition failed: {e}")
            return None, None, group_names, []

    def strategy_group_correlation(self):
        """Compute strategy-group correlation matrix on GPU.

        For each pair of strategy groups, compute the mean Pearson
        correlation across objects (using only objects that have data
        in both groups). This reveals which mathematical lenses
        co-vary across the entire object population.

        Returns: (corr_matrix, group_names)  -- corr_matrix is [G, G] numpy
        """
        if self.tensor is None:
            raise ValueError("Call build() first")

        group_names = list(self.STRATEGY_GROUPS.keys())
        n_groups = len(group_names)
        N = self.tensor.shape[0]

        print(f"\nStrategy-group correlation matrix ({n_groups}x{n_groups})...")

        # Compute group-level summary: masked mean per group per object
        group_means = torch.zeros(N, n_groups, device=DEVICE)
        group_valid = torch.zeros(N, n_groups, device=DEVICE, dtype=torch.bool)

        for gi, gname in enumerate(group_names):
            strat_list = self.STRATEGY_GROUPS[gname]
            cols = []
            for sname in strat_list:
                if sname in self._strategy_slices:
                    start, end = self._strategy_slices[sname]
                    cols.extend(range(start, end))
            if not cols:
                continue
            col_idx = torch.tensor(cols, device=DEVICE)
            group_vals = self.tensor[:, col_idx]
            group_mask = self.mask[:, col_idx].float()
            has_data = group_mask.sum(dim=1) > 0
            denom = group_mask.sum(dim=1).clamp(min=1)
            group_means[:, gi] = (group_vals * group_mask).sum(dim=1) / denom
            group_valid[:, gi] = has_data

        # Pearson correlation between all group pairs (GPU)
        corr_matrix = torch.zeros(n_groups, n_groups, device=DEVICE)

        for i in range(n_groups):
            for j in range(i, n_groups):
                # Mask: both groups have data
                shared = group_valid[:, i] & group_valid[:, j]
                n_shared = shared.sum().item()
                if n_shared < 10:
                    corr_matrix[i, j] = 0.0
                    corr_matrix[j, i] = 0.0
                    continue
                x = group_means[shared, i]
                y = group_means[shared, j]
                # Pearson r on GPU
                mx = x - x.mean()
                my = y - y.mean()
                num = (mx * my).sum()
                den = (mx.norm() * my.norm()).clamp(min=1e-12)
                r = (num / den).item()
                corr_matrix[i, j] = r
                corr_matrix[j, i] = r

        # Print correlation matrix
        print(f"\n  {'':14s} " + " ".join(f"{g:>10s}" for g in group_names))
        corr_np = corr_matrix.cpu().numpy()
        for i, gname in enumerate(group_names):
            row = " ".join(f"{corr_np[i, j]:10.3f}" for j in range(n_groups))
            print(f"  {gname:14s} {row}")

        # Highlight strongest off-diagonal correlations
        print(f"\n  Strongest cross-group correlations:")
        pairs = []
        for i in range(n_groups):
            for j in range(i + 1, n_groups):
                pairs.append((group_names[i], group_names[j], corr_np[i, j]))
        pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        for left, right, r in pairs[:10]:
            marker = " (strong)" if abs(r) > 0.3 else ""
            print(f"    {left:12s} <-> {right:12s}: r={r:+.3f}{marker}")

        return corr_np, group_names

    def summary(self):
        """Print tensor summary."""
        if self.tensor is None:
            print("Tensor not built yet. Call build() first.")
            return

        print(f"\n{'='*60}")
        print(f"DISSECTION TENSOR SUMMARY")
        print(f"{'='*60}")
        print(f"Objects: {len(self.objects)}")
        print(f"Dimensions: {self.TOTAL_DIMS}")
        print(f"Device: {self.tensor.device}")
        print(f"Memory: {self.tensor.element_size() * self.tensor.nelement() / 1e6:.1f} MB")
        print(f"\nDomains:")
        for domain, indices in sorted(self.domain_indices.items()):
            print(f"  {domain:12s}: {len(indices):6d} objects")
        print(f"\nStrategy dimensions:")
        for name, (start, end) in self._strategy_slices.items():
            dim = end - start
            strat_mask = self.mask[:, start:end]
            n_with_data = strat_mask.any(dim=1).sum().item()
            print(f"  {name:12s}: {dim:2d} dims, "
                  f"{n_with_data:6d}/{len(self.objects)} objects ({n_with_data/len(self.objects)*100:.0f}%)")


# ============================================================
# Main — build and explore
# ============================================================
def main():
    print(f"Device: {DEVICE}")
    if DEVICE.type == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    dt = DissectionTensor()

    # Load all domains
    print("\n--- Loading data ---")
    print("Loading knots...")
    dt.add_objects(DataLoaders.load_knots())

    print("Loading number fields...")
    dt.add_objects(DataLoaders.load_number_fields())

    print("Loading elliptic curves...")
    dt.add_objects(DataLoaders.load_ec())

    print("Loading Fungrim...")
    dt.add_objects(DataLoaders.load_fungrim())

    print("Loading OEIS sequences...")
    dt.add_objects(DataLoaders.load_oeis(max_n=20000))

    print("Loading genus-2 curves...")
    dt.add_objects(DataLoaders.load_genus2(max_n=10000))

    # Load battery results as truth-boundary index (NOT tensor dims)
    print("\nLoading battery results (truth-boundary index)...")
    v2_dir = ROOT / "cartography/shared/scripts/v2"
    for result_file in v2_dir.glob("r3_*_results.json"):
        data = json.loads(result_file.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for test_id, result in data.items():
                if isinstance(result, dict):
                    dt.add_battery_results(test_id, result)
    print(f"  {len(dt.battery_index)} battery results indexed")

    # Build tensor
    print("\n--- Building tensor ---")
    dt.build()
    dt.normalize()
    dt.summary()

    # Explore cross-domain distances (require at least 2 shared strategy groups)
    print(f"\n--- Cross-domain exploration (min 2 shared strategy groups) ---")
    domains = list(dt.domain_indices.keys())
    for i, da in enumerate(domains):
        for db in domains[i + 1:]:
            pairs = dt.cross_domain_distances(da, db, min_shared_groups=2, top_k=5)
            if pairs:
                print(f"\n{da} <-> {db} (top 5 closest):")
                for obj_a, obj_b, dist, n_shared in pairs:
                    print(f"  {obj_a:30s} <-> {obj_b:30s}  "
                          f"d={dist:.3f} ({n_shared} shared dims)")

    # Find intersections
    print(f"\n--- Intersections (threshold=1.5, min 2 groups) ---")
    intersections = dt.find_intersections(threshold=1.5, top_k=20)
    for obj_a, obj_b, dist, n_shared in intersections:
        da = obj_a.split("_")[0]
        db = obj_b.split("_")[0]
        print(f"  [{da}<->{db}] {obj_a:30s} <-> {obj_b:30s}  "
              f"d={dist:.3f} ({n_shared} shared dims)")

    # TT decomposition
    print(f"\n--- Tensor Train decomposition ---")
    tt, bonds, error = dt.tt_decompose(rank=5)

    # Strategy-grouped TT decomposition
    print(f"\n--- Strategy-grouped TT decomposition ---")
    gtt, gbonds, gnames, entanglement = dt.tt_decompose_grouped(rank=5)

    # Strategy-group correlation matrix
    print(f"\n--- Strategy-group correlation matrix ---")
    corr, corr_names = dt.strategy_group_correlation()

    # Save tensor for later use
    out_dir = ROOT / "cartography/convergence/data"
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save({
        "tensor": dt.tensor.cpu(),
        "mask": dt.mask.cpu(),
        "labels": dt.labels,
        "domains": dt.domains,
        "strategy_slices": dt._strategy_slices,
    }, out_dir / "dissection_tensor.pt")
    print(f"\nTensor saved to convergence/data/dissection_tensor.pt")

    return dt


if __name__ == "__main__":
    dt = main()
