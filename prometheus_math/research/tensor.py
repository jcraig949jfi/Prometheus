"""Cross-domain tensor builder for Harmonia (project #44 phase 1).

Harmonia's research thread builds and probes a *cross-domain tensor*: a
4-axis array indexed by ``(domain, object, phoneme, invariant)`` where
the entries are scalar statistics computed per (object, phoneme,
invariant) triple. The tensor is the primary substrate that all of the
"phoneme" experiments (Megethos, Tropos, Phasis, Eidos, ...) operate on
in ergon/, agora/, and charon/. Until now every research session
hand-rolled this tensor with one-off scripts. This module codifies the
construction.

This is the **phase 1** module: helpers to *build* the tensor. Phase 2
(distributional and identity-join scorers) is deferred — the building
block must stabilise first.

Vocabulary
----------
- **Domain**: a mathematical universe (elliptic curves, knots, number
  fields, modular forms, polytopes, genus-2 curves, ...). Each domain
  exposes a *fetch* callable returning a list of object records.
- **Phoneme**: an abstract structural axis Harmonia uses across domains
  (Megethos = magnitude / scale, Tropos = shape / asymmetry, Phasis =
  phase / oscillation, Eidos = form / categorical type, ...). Phonemes
  apply only to the domains where they make sense; ``applies_to_domains``
  carries that whitelist.
- **Invariant**: a numeric (or categorical encoded as numeric) statistic
  computed per object, parameterised by phoneme. Each invariant has a
  ``compute_fn(object_record, phoneme_name) -> float | NaN``.

Public API
----------
``DomainSpec``, ``PhonemeSpec``, ``InvariantSpec``
    Frozen dataclasses describing the three axes.
``canonical_phonemes()``
    Harmonia's standard 4-phoneme set (Megethos, Tropos, Phasis, Eidos).
``canonical_domains()``
    Stub specs for the six standard Harmonia domains (ec_q, nf_q,
    knot_table, modular_forms, polytope, genus_2). The fetch callables
    are placeholders — production code wires them to ``pm.databases.*``.
``build_tensor(domains, phonemes, invariants, n_per_domain=None,
               missing_value='nan')``
    Construct the 4-D dense tensor + boolean computed/finite mask + axes
    + meta. Returns a dict.
``compute_invariant(object_record, invariant_spec, phoneme_spec)``
    Single-cell computation: applies sentinel rules then dispatches to
    the invariant's ``compute_fn``. Returns NaN on any failure (and logs
    via ``logging``).
``tensor_to_dataframe(tensor)``
    Long-form DataFrame: one row per (domain, object_idx, phoneme,
    invariant, value, mask).
``tensor_save(tensor, path)`` / ``tensor_load(path)``
    Roundtripable .npz + json sidecar.

Tensor schema
-------------
``build_tensor`` returns a dict with::

    {
      "axes": {
          "domain":    [str, ...],   # length D
          "phoneme":   [str, ...],   # length P
          "invariant": [str, ...],   # length I
          # Per-domain per-object identifiers, shape (D, N):
          "object_id": np.ndarray of shape (D, N), dtype=object,
      },
      "data":  np.ndarray, shape (D, N, P, I), dtype=float64,
      "masks": np.ndarray, shape (D, N, P, I), dtype=bool,
      "meta":  {
          "timestamp": ISO-8601 string,
          "n_per_domain": int or None,
          "missing_value": float (NaN or sentinel),
          "domain_versions": {domain_name: version_str},
          "schema_version": "1",
      },
    }

Where ``N`` is the maximum object count across all domains; domains with
fewer objects are padded with NaN data and ``False`` mask values. The
``object_id`` axis carries either the primary id of each object or the
empty string for padded slots.

Design notes
------------
- Failures are NEVER fatal: any per-cell error becomes NaN with mask
  ``False`` and a single log line. The whole tensor still builds.
- Phonemes that don't apply to a domain (``applies_to_domains`` filter)
  produce all-NaN columns with mask ``False`` for that domain — they
  are visible in the tensor as "this phoneme was deliberately not
  measured for this domain", which is different from a compute failure.
  Both end up as ``mask=False`` in the data tensor; the distinction is
  recorded only in the per-cell log.
- The tensor is dense (not sparse). Harmonia's downstream operations
  rely on numpy indexing; sparse tensors would force a different API.
  At Harmonia's working scale (≤ 6 domains, ≤ 100 objects each, ≤ 10
  phonemes, ≤ 20 invariants → 1.2M float64 ≈ 10 MB) density is fine.

Author: Techne — project #44 phase 1 of techne/PROJECT_BACKLOG_1000.md.
Forged: 2026-04-25.
"""
from __future__ import annotations

import datetime as _dt
import json as _json
import logging as _logging
import os as _os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Sequence, Union

import numpy as np

try:
    import pandas as pd  # noqa: F401  (used in tensor_to_dataframe)
except Exception:  # pragma: no cover — pandas is a hard dependency in pm
    pd = None  # type: ignore

__all__ = [
    "DomainSpec",
    "PhonemeSpec",
    "InvariantSpec",
    "canonical_phonemes",
    "canonical_domains",
    "build_tensor",
    "compute_invariant",
    "tensor_to_dataframe",
    "tensor_save",
    "tensor_load",
    "SCHEMA_VERSION",
    # Phase 2 scorers (project #44 phase 2)
    "distributional_distance",
    "distributional_matrix",
    "identity_join",
    "cross_domain_correlation",
    "tensor_silent_islands",
    "tensor_phoneme_score",
    "tensor_anomaly_surface",
]

_log = _logging.getLogger(__name__)

SCHEMA_VERSION = "1"


# ---------------------------------------------------------------------------
# Specs
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DomainSpec:
    """Specification of a tensor domain axis entry.

    Attributes
    ----------
    name
        Short identifier (e.g. ``"ec_q"``, ``"knot_table"``).
    fetch_fn
        Callable ``() -> Sequence[dict]`` returning the domain's object
        records. Each record is an arbitrary dict; downstream invariant
        ``compute_fn`` callables are responsible for understanding it.
        ``fetch_fn`` may accept an optional ``n`` keyword for row-cap;
        ``build_tensor`` calls ``fetch_fn(n=n_per_domain)`` first and
        falls back to ``fetch_fn()`` if the keyword is rejected.
    n_objects
        Hint for typical row count (used only for documentation / capacity
        planning; not relied on by ``build_tensor``).
    primary_id_field
        Key in the object record carrying the canonical id (e.g.
        ``"lmfdb_label"`` for EC, ``"name"`` for knots). Optional; if the
        record lacks the field, the integer index is used as id.
    version
        Free-form string recorded in the tensor meta to enable
        reproducibility. Default ``"unspecified"``.
    """

    name: str
    fetch_fn: Callable[..., Sequence[dict]]
    n_objects: int = 0
    primary_id_field: Optional[str] = None
    version: str = "unspecified"


@dataclass(frozen=True)
class PhonemeSpec:
    """Specification of a phoneme axis entry.

    Attributes
    ----------
    name
        Short identifier (e.g. ``"Megethos"``, ``"Tropos"``).
    description
        One-line human description.
    applies_to_domains
        Whitelist of domain names this phoneme is meaningful for. The
        special value ``("*",)`` means "applies to all domains". Empty
        tuple = applies nowhere (sentinel; useful in tests).
    sentinel_value
        Float written into the tensor when the phoneme does not apply
        to a domain. Default ``float("nan")``.
    """

    name: str
    description: str
    applies_to_domains: tuple = ("*",)
    sentinel_value: float = float("nan")

    def applies_to(self, domain_name: str) -> bool:
        if not self.applies_to_domains:
            return False
        if "*" in self.applies_to_domains:
            return True
        return domain_name in self.applies_to_domains


@dataclass(frozen=True)
class InvariantSpec:
    """Specification of an invariant axis entry.

    Attributes
    ----------
    name
        Short identifier (e.g. ``"mean"``, ``"slope"``).
    kind
        Either ``"numeric"`` or ``"categorical"``. Categoricals must
        encode to a finite float (e.g. label-encoded class index).
    compute_fn
        Callable ``(object_record, phoneme_name) -> float`` returning
        the cell value. Must return ``float("nan")`` on missing data.
        Exceptions are caught by ``compute_invariant`` and converted to
        NaN with a log line.
    normalization
        Optional post-processing tag (``"none"``, ``"zscore"``,
        ``"log"``, ``"rank"``). ``build_tensor`` does NOT apply it
        automatically; downstream consumers may. Default ``"none"``.
    """

    name: str
    kind: str = "numeric"
    compute_fn: Optional[Callable[[Any, str], float]] = None
    normalization: str = "none"

    def __post_init__(self) -> None:
        if self.kind not in ("numeric", "categorical"):
            raise ValueError(
                f"InvariantSpec.kind must be 'numeric' or 'categorical', got "
                f"{self.kind!r}"
            )


# ---------------------------------------------------------------------------
# Canonical Harmonia sets (Megethos / silent-islands)
# ---------------------------------------------------------------------------


def canonical_phonemes() -> list:
    """Return Harmonia's canonical phoneme set.

    Notes
    -----
    The Megethos memory file (project_megethos.md) is the source for the
    primary phoneme name. Megethos was killed as a *universal* axis
    claim by the M1 battery, but it survives as the canonical magnitude
    axis name in tensor construction — its invariants still measure
    something real (database scale + arithmetic conditioning), they just
    don't transfer cross-domain. Tropos, Phasis, and Eidos are the three
    other canonical structural phonemes Harmonia uses.

    Returns
    -------
    list of PhonemeSpec
        The four canonical phonemes. Each has a non-empty
        ``applies_to_domains`` tuple.
    """
    return [
        PhonemeSpec(
            name="Megethos",
            description="Magnitude / scale axis (log-size of canonical invariants).",
            applies_to_domains=("*",),
        ),
        PhonemeSpec(
            name="Tropos",
            description="Shape / asymmetry axis (skew, kurtosis, gap-ratio mean).",
            applies_to_domains=("*",),
        ),
        PhonemeSpec(
            name="Phasis",
            description="Phase / oscillation axis (sign patterns, parity, root number).",
            applies_to_domains=("ec_q", "nf_q", "modular_forms", "genus_2"),
        ),
        PhonemeSpec(
            name="Eidos",
            description="Form / categorical type axis (CM, isogeny class, Galois type).",
            applies_to_domains=("ec_q", "nf_q", "modular_forms", "genus_2", "knot_table"),
        ),
    ]


def _placeholder_fetch(name: str) -> Callable[..., Sequence[dict]]:
    """Return a placeholder fetch_fn that raises a clear error.

    The canonical_domains() entries point at these placeholders so that
    callers see a helpful message ("wire this up to pm.databases.X")
    rather than a silent empty fetch.
    """

    def _fn(*args: Any, **kwargs: Any) -> Sequence[dict]:
        raise NotImplementedError(
            f"Domain {name!r} fetch_fn is a placeholder. Wire it to the "
            f"appropriate pm.databases.* wrapper before calling build_tensor."
        )

    return _fn


def canonical_domains() -> list:
    """Return Harmonia's canonical domain stubs.

    These are *specs* — each fetch_fn is a placeholder that raises
    NotImplementedError. Production callers should replace each spec's
    fetch_fn with a wired wrapper around ``pm.databases.lmfdb`` /
    ``pm.databases.knotinfo`` / ``pm.databases.oeis`` etc.

    Returns
    -------
    list of DomainSpec
        Six canonical domains: ec_q, nf_q, knot_table, modular_forms,
        polytope, genus_2.
    """
    return [
        DomainSpec(
            name="ec_q",
            fetch_fn=_placeholder_fetch("ec_q"),
            n_objects=2000,
            primary_id_field="lmfdb_label",
        ),
        DomainSpec(
            name="nf_q",
            fetch_fn=_placeholder_fetch("nf_q"),
            n_objects=1000,
            primary_id_field="label",
        ),
        DomainSpec(
            name="knot_table",
            fetch_fn=_placeholder_fetch("knot_table"),
            n_objects=100,
            primary_id_field="name",
        ),
        DomainSpec(
            name="modular_forms",
            fetch_fn=_placeholder_fetch("modular_forms"),
            n_objects=500,
            primary_id_field="label",
        ),
        DomainSpec(
            name="polytope",
            fetch_fn=_placeholder_fetch("polytope"),
            n_objects=100,
            primary_id_field="id",
        ),
        DomainSpec(
            name="genus_2",
            fetch_fn=_placeholder_fetch("genus_2"),
            n_objects=300,
            primary_id_field="lmfdb_label",
        ),
    ]


# ---------------------------------------------------------------------------
# Cell computation
# ---------------------------------------------------------------------------


def compute_invariant(
    object_record: Any,
    invariant_spec: InvariantSpec,
    phoneme_spec: PhonemeSpec,
) -> float:
    """Compute one tensor cell.

    Parameters
    ----------
    object_record
        The per-object dict from ``DomainSpec.fetch_fn``.
    invariant_spec
        The invariant whose ``compute_fn`` we dispatch to.
    phoneme_spec
        Passed through as the second arg to ``compute_fn`` so the
        invariant can branch on phoneme.

    Returns
    -------
    float
        Numeric value, or ``float("nan")`` on any failure (including
        missing ``compute_fn``).
    """
    if invariant_spec.compute_fn is None:
        return float("nan")
    try:
        v = invariant_spec.compute_fn(object_record, phoneme_spec.name)
    except Exception as exc:  # noqa: BLE001 — failures must not abort
        _log.debug(
            "compute_invariant: %s/%s -> NaN (%s: %s)",
            phoneme_spec.name,
            invariant_spec.name,
            type(exc).__name__,
            exc,
        )
        return float("nan")
    try:
        v = float(v)
    except (TypeError, ValueError):
        return float("nan")
    return v


# ---------------------------------------------------------------------------
# Tensor build
# ---------------------------------------------------------------------------


def _safe_fetch(spec: DomainSpec, n: Optional[int]) -> Sequence[dict]:
    """Call spec.fetch_fn with ``n=n`` if accepted, else without."""
    if n is not None:
        try:
            return list(spec.fetch_fn(n=n))
        except TypeError:
            pass
    return list(spec.fetch_fn())


def build_tensor(
    domains: Sequence[DomainSpec],
    phonemes: Sequence[PhonemeSpec],
    invariants: Sequence[InvariantSpec],
    n_per_domain: Optional[int] = None,
    missing_value: Union[str, float] = "nan",
) -> dict:
    """Build the cross-domain tensor.

    Parameters
    ----------
    domains
        Non-empty sequence of DomainSpec.
    phonemes
        Sequence of PhonemeSpec. Empty list is allowed (tensor will have
        zero phoneme axis length).
    invariants
        Non-empty sequence of InvariantSpec.
    n_per_domain
        Optional int: cap each domain's row count. If 0, the tensor's
        object axis has length 0 (still a valid 4-D array).
    missing_value
        Either ``"nan"`` (default) or a numeric sentinel written into
        the data array where computation didn't run.

    Returns
    -------
    dict
        See module docstring "Tensor schema" for the layout.

    Raises
    ------
    ValueError
        If ``domains`` is empty, ``invariants`` is empty, or
        ``n_per_domain`` is a negative int.
    """
    if not domains:
        raise ValueError("build_tensor: domains is empty")
    if not invariants:
        raise ValueError("build_tensor: invariants is empty")
    if n_per_domain is not None and n_per_domain < 0:
        raise ValueError(f"build_tensor: n_per_domain must be >= 0, got {n_per_domain}")

    # Resolve missing_value sentinel.
    if missing_value == "nan":
        sentinel = float("nan")
    else:
        try:
            sentinel = float(missing_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"missing_value must be 'nan' or numeric: {exc}") from exc

    D = len(domains)
    P = len(phonemes)
    I = len(invariants)

    # Step 1: fetch per-domain objects.
    domain_records: list = []
    domain_ids: list = []
    for spec in domains:
        records = _safe_fetch(spec, n_per_domain)
        if n_per_domain is not None:
            records = list(records)[: n_per_domain]
        ids = []
        for idx, rec in enumerate(records):
            if spec.primary_id_field and isinstance(rec, dict) and spec.primary_id_field in rec:
                ids.append(str(rec[spec.primary_id_field]))
            else:
                ids.append(str(idx))
        domain_records.append(records)
        domain_ids.append(ids)

    # Step 2: compute object axis length N (max across domains; 0 allowed).
    if n_per_domain is not None:
        N = n_per_domain
    else:
        N = max((len(r) for r in domain_records), default=0)

    # Step 3: allocate tensor + mask.
    data = np.full((D, N, P, I), sentinel, dtype=np.float64)
    masks = np.zeros((D, N, P, I), dtype=bool)
    object_ids = np.full((D, N), "", dtype=object)

    # Step 4: fill per (domain, object, phoneme, invariant).
    for di, (dspec, records, ids) in enumerate(zip(domains, domain_records, domain_ids)):
        for oi in range(min(len(records), N)):
            object_ids[di, oi] = ids[oi]
            rec = records[oi]
            for pi, pspec in enumerate(phonemes):
                if not pspec.applies_to(dspec.name):
                    # Sentinel for "phoneme deliberately not applied to
                    # this domain" — value is the phoneme's own sentinel
                    # (defaults to NaN so it's indistinguishable from a
                    # compute failure unless the user customises it).
                    for ii in range(I):
                        v = pspec.sentinel_value
                        if v != v:  # NaN
                            data[di, oi, pi, ii] = sentinel
                        else:
                            data[di, oi, pi, ii] = float(v)
                    # masks already False
                    continue
                for ii, ispec in enumerate(invariants):
                    v = compute_invariant(rec, ispec, pspec)
                    if v == v and np.isfinite(v):  # not NaN, not inf
                        data[di, oi, pi, ii] = v
                        masks[di, oi, pi, ii] = True
                    else:
                        data[di, oi, pi, ii] = sentinel
                        # mask stays False

    meta = {
        "timestamp": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "n_per_domain": n_per_domain,
        "missing_value": "nan" if sentinel != sentinel else float(sentinel),
        "domain_versions": {d.name: d.version for d in domains},
        "schema_version": SCHEMA_VERSION,
    }

    return {
        "axes": {
            "domain": [d.name for d in domains],
            "phoneme": [p.name for p in phonemes],
            "invariant": [i.name for i in invariants],
            "object_id": object_ids,
        },
        "data": data,
        "masks": masks,
        "meta": meta,
    }


# ---------------------------------------------------------------------------
# DataFrame export
# ---------------------------------------------------------------------------


def tensor_to_dataframe(tensor: dict):
    """Convert tensor dict to long-form DataFrame.

    Returns
    -------
    pandas.DataFrame
        Columns: ``domain, object_idx, object_id, phoneme, invariant,
        value, mask``. One row per cell.

    Raises
    ------
    ImportError
        If pandas is not available.
    """
    if pd is None:  # pragma: no cover
        raise ImportError("tensor_to_dataframe requires pandas")
    axes = tensor["axes"]
    data = tensor["data"]
    masks = tensor["masks"]
    object_ids = axes["object_id"]
    D, N, P, I = data.shape
    rows = []
    for di in range(D):
        dname = axes["domain"][di]
        for oi in range(N):
            oid = object_ids[di, oi] if N > 0 else ""
            for pi in range(P):
                pname = axes["phoneme"][pi]
                for ii in range(I):
                    iname = axes["invariant"][ii]
                    rows.append(
                        {
                            "domain": dname,
                            "object_idx": oi,
                            "object_id": oid,
                            "phoneme": pname,
                            "invariant": iname,
                            "value": float(data[di, oi, pi, ii]),
                            "mask": bool(masks[di, oi, pi, ii]),
                        }
                    )
    return pd.DataFrame(
        rows,
        columns=[
            "domain",
            "object_idx",
            "object_id",
            "phoneme",
            "invariant",
            "value",
            "mask",
        ],
    )


# ---------------------------------------------------------------------------
# Persistence: .npz + sidecar JSON
# ---------------------------------------------------------------------------


def tensor_save(tensor: dict, path: Union[str, Path]) -> None:
    """Save tensor to ``path.npz`` plus ``path.json`` sidecar.

    Parameters
    ----------
    tensor
        Output of :func:`build_tensor`.
    path
        Destination path. Extension may be ``.npz`` (replaced) or absent.

    Raises
    ------
    IOError
        If the parent directory doesn't exist.
    """
    path = Path(path)
    if path.suffix.lower() == ".npz":
        npz_path = path
    else:
        npz_path = path.with_suffix(".npz")
    sidecar_path = npz_path.with_suffix(".json")

    parent = npz_path.parent
    if str(parent) and not parent.exists():
        # Treat missing parent as IOError so callers get a clear failure
        # mode rather than a low-level FileNotFoundError.
        raise IOError(f"tensor_save: parent directory does not exist: {parent}")

    axes = tensor["axes"]
    np.savez(
        npz_path,
        data=tensor["data"],
        masks=tensor["masks"],
        object_id=axes["object_id"],
    )
    sidecar = {
        "domain": list(axes["domain"]),
        "phoneme": list(axes["phoneme"]),
        "invariant": list(axes["invariant"]),
        "meta": tensor["meta"],
    }
    with open(sidecar_path, "w", encoding="utf-8") as f:
        _json.dump(sidecar, f, indent=2, sort_keys=True, default=str)


# ---------------------------------------------------------------------------
# Phase 2: helper resolvers (axis lookups)
# ---------------------------------------------------------------------------


def _axis_index(tensor: dict, axis: str, name: str) -> int:
    """Resolve ``name`` to its integer index along ``axis``.

    Raises
    ------
    KeyError
        If ``name`` does not appear in ``tensor['axes'][axis]``. The error
        message lists the legal names for that axis.
    """
    names = tensor["axes"][axis]
    if name not in names:
        raise KeyError(
            f"{axis}={name!r} not found; legal {axis} names: {list(names)}"
        )
    return list(names).index(name)


def _domain_invariant_values(
    tensor: dict,
    domain: str,
    phoneme: str,
    invariant: str,
) -> np.ndarray:
    """Return finite, masked-True values for one (domain, phoneme, invariant) cell.

    Strips NaN and uses the mask to drop padded / failed cells. Returns
    a 1-D float array (possibly empty).
    """
    di = _axis_index(tensor, "domain", domain)
    pi = _axis_index(tensor, "phoneme", phoneme)
    ii = _axis_index(tensor, "invariant", invariant)
    data = tensor["data"][di, :, pi, ii]
    masks = tensor["masks"][di, :, pi, ii]
    valid = masks & np.isfinite(data)
    return np.asarray(data[valid], dtype=float)


# ---------------------------------------------------------------------------
# Phase 2: distributional distances
# ---------------------------------------------------------------------------


_DIST_METRICS = ("js", "ks", "wass", "mmd")


def _hist_probs(a: np.ndarray, b: np.ndarray, n_bins: int = 32):
    """Pair-binned probability histograms for js/mmd over a shared support.

    The support is ``[min(min(a), min(b)), max(max(a), max(b))]`` so that
    the two histograms live on the same axis. Returns ``(p, q)`` 1-D
    probability vectors that sum to 1 and are aligned bin-for-bin.
    """
    lo = float(min(a.min(), b.min()))
    hi = float(max(a.max(), b.max()))
    if hi <= lo:
        # degenerate (constant or near-constant) — return identical
        # one-bin histograms so JS = 0.
        return np.array([1.0]), np.array([1.0])
    edges = np.linspace(lo, hi, n_bins + 1)
    pa, _ = np.histogram(a, bins=edges)
    pb, _ = np.histogram(b, bins=edges)
    pa = pa.astype(float)
    pb = pb.astype(float)
    sa = pa.sum()
    sb = pb.sum()
    if sa > 0:
        pa /= sa
    if sb > 0:
        pb /= sb
    return pa, pb


def _mmd_rbf(a: np.ndarray, b: np.ndarray, sigma: Optional[float] = None) -> float:
    """RBF-kernel Maximum Mean Discrepancy (squared, biased estimator).

    MMD^2 = E[k(x,x')] + E[k(y,y')] - 2 E[k(x,y)] with
    ``k(u,v) = exp(-||u-v||^2 / (2 sigma^2))``. Uses the median heuristic
    for ``sigma`` when not supplied.
    """
    a = a.reshape(-1, 1)
    b = b.reshape(-1, 1)
    if sigma is None:
        # median heuristic on the pooled pairwise distances
        xy = np.concatenate([a, b], axis=0)
        diffs = xy[:, None, 0] - xy[None, :, 0]
        med = float(np.median(np.abs(diffs[diffs != 0]))) if np.any(diffs != 0) else 1.0
        sigma = max(med, 1e-12)

    def K(x, y):
        d = (x[:, None, 0] - y[None, :, 0]) ** 2
        return np.exp(-d / (2.0 * sigma * sigma))

    kxx = float(np.mean(K(a, a)))
    kyy = float(np.mean(K(b, b)))
    kxy = float(np.mean(K(a, b)))
    val = kxx + kyy - 2.0 * kxy
    # numerical zero floor (biased estimator can produce tiny negatives)
    return max(val, 0.0)


def distributional_distance(
    tensor: dict,
    domain_a: str,
    domain_b: str,
    phoneme: str,
    invariant: str,
    metric: str = "js",
) -> float:
    """Distance between two domains' invariant distributions.

    Parameters
    ----------
    tensor
        Output of :func:`build_tensor`.
    domain_a, domain_b
        Domain names (must be present in ``tensor['axes']['domain']``).
    phoneme, invariant
        The fixed (phoneme, invariant) cell whose distribution is
        compared across the two domains.
    metric
        One of:

        - ``'js'``: Jensen-Shannon distance on shared-support histograms
          (scipy.spatial.distance.jensenshannon).
        - ``'ks'``: Kolmogorov-Smirnov statistic (scipy.stats.ks_2samp).
        - ``'wass'``: Wasserstein-1 distance (scipy.stats.wasserstein_distance).
        - ``'mmd'``: RBF-kernel MMD^2, biased estimator with median
          bandwidth.

    Returns
    -------
    float
        Non-negative distance (0 = identical distributions). Returns
        NaN if either domain has zero finite values for the cell.

    Raises
    ------
    ValueError
        If ``metric`` is not in ``{'js','ks','wass','mmd'}``.
    KeyError
        If any of ``domain_a/domain_b/phoneme/invariant`` is unknown.
    """
    if metric not in _DIST_METRICS:
        raise ValueError(
            f"unknown metric {metric!r}; choose from {list(_DIST_METRICS)}"
        )

    a = _domain_invariant_values(tensor, domain_a, phoneme, invariant)
    b = _domain_invariant_values(tensor, domain_b, phoneme, invariant)
    if a.size == 0 or b.size == 0:
        return float("nan")
    if domain_a == domain_b:
        # Trivially zero by construction (same finite sample on both sides).
        return 0.0

    if metric == "js":
        from scipy.spatial.distance import jensenshannon

        p, q = _hist_probs(a, b)
        d = float(jensenshannon(p, q, base=2))
        return 0.0 if not np.isfinite(d) else d
    if metric == "ks":
        from scipy.stats import ks_2samp

        return float(ks_2samp(a, b).statistic)
    if metric == "wass":
        from scipy.stats import wasserstein_distance

        return float(wasserstein_distance(a, b))
    # mmd
    return float(_mmd_rbf(a, b))


def distributional_matrix(
    tensor: dict,
    phoneme: str,
    invariant: str,
    metric: str = "js",
) -> np.ndarray:
    """Pairwise distance matrix between all domains for one (phoneme, invariant).

    Parameters
    ----------
    tensor, phoneme, invariant, metric
        See :func:`distributional_distance`.

    Returns
    -------
    np.ndarray, shape (n_domain, n_domain)
        Symmetric, zero-diagonal. Off-diagonal NaN when either domain is
        empty for the cell.
    """
    domains = list(tensor["axes"]["domain"])
    n = len(domains)
    M = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d = distributional_distance(
                tensor, domains[i], domains[j], phoneme, invariant, metric=metric
            )
            M[i, j] = d
            M[j, i] = d
    return M


# ---------------------------------------------------------------------------
# Phase 2: identity_join
# ---------------------------------------------------------------------------


def identity_join(
    tensor: dict,
    key_invariant: str,
    value_invariants: Optional[Sequence[str]] = None,
):
    """Join records across domains that share a key invariant value.

    Treats one invariant as a "key" (e.g. an LMFDB-label hash, a
    discriminant, a torsion order) and finds records across domains
    where this key matches. The output is a wide-format DataFrame: one
    row per matched key, columns per (domain, value_invariant).

    Parameters
    ----------
    tensor
        Output of :func:`build_tensor`. The ``key_invariant`` MUST be
        a numeric invariant whose equality is meaningful.
    key_invariant
        Invariant name to use as the join key.
    value_invariants
        Optional list of invariant names to carry as columns. If
        ``None``, all non-key invariants are carried.

    Returns
    -------
    pandas.DataFrame
        Columns: ``key`` plus one ``{domain}__{invariant}`` column per
        (domain, value_invariant). One row per distinct key value that
        appears in 2+ domains (i.e. a real cross-domain join). May be
        empty if no key collides.

    Raises
    ------
    KeyError
        If ``key_invariant`` is not in ``tensor['axes']['invariant']``.
    ImportError
        If pandas is unavailable.
    """
    if pd is None:  # pragma: no cover
        raise ImportError("identity_join requires pandas")
    invariants = list(tensor["axes"]["invariant"])
    if key_invariant not in invariants:
        raise KeyError(
            f"key_invariant={key_invariant!r} not in invariants {invariants}"
        )
    if value_invariants is None:
        value_invariants = [iv for iv in invariants if iv != key_invariant]
    else:
        for iv in value_invariants:
            if iv not in invariants:
                raise KeyError(
                    f"value invariant {iv!r} not in invariants {invariants}"
                )

    domains = list(tensor["axes"]["domain"])
    phonemes = list(tensor["axes"]["phoneme"])
    data = tensor["data"]
    masks = tensor["masks"]
    key_ii = invariants.index(key_invariant)

    # Reduce key axis: a record "has key K" if ANY (phoneme, invariant=key)
    # cell is a finite K and mask True. We collapse phonemes by taking
    # the first finite value (keys are phoneme-independent in the
    # canonical Harmonia setup).
    rows = []  # list of (key_value, domain, value_dict)
    for di, dname in enumerate(domains):
        for oi in range(data.shape[1]):
            key_val = float("nan")
            for pi in range(len(phonemes)):
                if masks[di, oi, pi, key_ii] and np.isfinite(data[di, oi, pi, key_ii]):
                    key_val = float(data[di, oi, pi, key_ii])
                    break
            if not np.isfinite(key_val):
                continue
            value_dict = {}
            for iv in value_invariants:
                ii = invariants.index(iv)
                v = float("nan")
                for pi in range(len(phonemes)):
                    if masks[di, oi, pi, ii] and np.isfinite(data[di, oi, pi, ii]):
                        v = float(data[di, oi, pi, ii])
                        break
                value_dict[f"{dname}__{iv}"] = v
            rows.append((key_val, dname, value_dict))

    # Group by key, keep only keys appearing in 2+ domains.
    by_key: dict = {}
    for key_val, dname, vdict in rows:
        bucket = by_key.setdefault(key_val, {"domains": set(), "values": {}})
        bucket["domains"].add(dname)
        bucket["values"].update(vdict)

    cols = ["key"] + [f"{d}__{iv}" for d in domains for iv in value_invariants]
    out_rows = []
    for key_val, bucket in by_key.items():
        if len(bucket["domains"]) < 2:
            continue
        row = {"key": key_val}
        for c in cols[1:]:
            row[c] = bucket["values"].get(c, float("nan"))
        out_rows.append(row)
    return pd.DataFrame(out_rows, columns=cols)


# ---------------------------------------------------------------------------
# Phase 2: cross_domain_correlation
# ---------------------------------------------------------------------------


def cross_domain_correlation(
    tensor: dict,
    phoneme_a: str,
    invariant_a: str,
    phoneme_b: str,
    invariant_b: str,
    n_bootstrap: int = 1000,
    seed: int | None = None,
) -> dict:
    """Pearson correlation between two tensor cells across domains+objects.

    Flattens the two (phoneme, invariant) cells across all (domain,
    object) pairs and computes Pearson r between the surviving paired
    finite values. Bootstraps the CI via
    :func:`prometheus_math.research.bootstrap.bootstrap_correlation`.

    Parameters
    ----------
    tensor
        Output of :func:`build_tensor`.
    phoneme_a, invariant_a, phoneme_b, invariant_b
        The two cells to correlate. May share phoneme or invariant.
    n_bootstrap : int, default 1000
        Number of bootstrap resamples for the CI.
    seed : int or None
        Seed for the bootstrap.

    Returns
    -------
    dict
        ``{pearson_r, ci_lower, ci_upper, p_value, n_observations,
        phoneme_a, invariant_a, phoneme_b, invariant_b}``. ``pearson_r``
        is NaN with explicit warning when n_observations < 3 or either
        side is constant.
    """
    import warnings

    pi_a = _axis_index(tensor, "phoneme", phoneme_a)
    ii_a = _axis_index(tensor, "invariant", invariant_a)
    pi_b = _axis_index(tensor, "phoneme", phoneme_b)
    ii_b = _axis_index(tensor, "invariant", invariant_b)
    data = tensor["data"]
    masks = tensor["masks"]
    a = data[:, :, pi_a, ii_a].ravel()
    b = data[:, :, pi_b, ii_b].ravel()
    ma = masks[:, :, pi_a, ii_a].ravel()
    mb = masks[:, :, pi_b, ii_b].ravel()
    valid = ma & mb & np.isfinite(a) & np.isfinite(b)
    a = a[valid]
    b = b[valid]
    n = int(a.size)

    base = {
        "pearson_r": float("nan"),
        "ci_lower": float("nan"),
        "ci_upper": float("nan"),
        "p_value": float("nan"),
        "n_observations": n,
        "phoneme_a": phoneme_a,
        "invariant_a": invariant_a,
        "phoneme_b": phoneme_b,
        "invariant_b": invariant_b,
    }
    if n < 3:
        warnings.warn(
            f"cross_domain_correlation: n_observations={n} (<3); returning NaN",
            stacklevel=2,
        )
        return base
    if a.std() == 0 or b.std() == 0:
        warnings.warn(
            "cross_domain_correlation: one side is constant; r undefined",
            stacklevel=2,
        )
        return base

    from scipy.stats import pearsonr

    r, p = pearsonr(a, b)
    base["pearson_r"] = float(r)
    base["p_value"] = float(p)

    # Bootstrap CI
    try:
        from prometheus_math.research.bootstrap import bootstrap_correlation

        bc = bootstrap_correlation(a, b, n=int(n_bootstrap), seed=seed)
        base["ci_lower"] = float(bc["ci_lower"])
        base["ci_upper"] = float(bc["ci_upper"])
    except Exception:  # pragma: no cover — defensive
        base["ci_lower"] = float("nan")
        base["ci_upper"] = float("nan")
    return base


# ---------------------------------------------------------------------------
# Phase 2: tensor_silent_islands
# ---------------------------------------------------------------------------


def tensor_silent_islands(
    tensor: dict,
    threshold: float = 0.5,
    metric: str = "js",
    phoneme: Optional[str] = None,
    invariant: Optional[str] = None,
):
    """Identify domain-pairs whose distributions are nearly disjoint.

    Implements the "silent islands" finding from
    project_silent_islands.md: pairs (A, B) of domains whose
    distributional distance for a fixed (phoneme, invariant) is at or
    above ``threshold`` are silent — they speak different mathematical
    languages.

    Parameters
    ----------
    tensor
        Output of :func:`build_tensor`.
    threshold : float, default 0.5
        Pairs with ``distributional_matrix[i, j] >= threshold`` are
        flagged.
    metric : str, default 'js'
        Distance metric, see :func:`distributional_distance`.
    phoneme, invariant : str or None
        If both supplied, restricts attention to that single cell. If
        either is None, scans across all (phoneme, invariant) pairs and
        averages distance across them per domain-pair.

    Returns
    -------
    list of ((domain_a, domain_b), score)
        Sorted by descending score. Empty list when nothing is silent.
    """
    domains = list(tensor["axes"]["domain"])
    phonemes = list(tensor["axes"]["phoneme"])
    invariants = list(tensor["axes"]["invariant"])

    if phoneme is not None and invariant is not None:
        M = distributional_matrix(tensor, phoneme, invariant, metric=metric)
    else:
        # Average across all cells; ignore NaN.
        n = len(domains)
        accum = np.full((n, n), 0.0)
        cnt = np.zeros((n, n), dtype=int)
        for ph in phonemes:
            for iv in invariants:
                M = distributional_matrix(tensor, ph, iv, metric=metric)
                finite = np.isfinite(M)
                accum[finite] += M[finite]
                cnt[finite] += 1
        with np.errstate(invalid="ignore", divide="ignore"):
            M = np.where(cnt > 0, accum / np.maximum(cnt, 1), np.nan)

    out: list = []
    n = len(domains)
    for i in range(n):
        for j in range(i + 1, n):
            v = M[i, j]
            if np.isfinite(v) and v >= threshold:
                out.append(((domains[i], domains[j]), float(v)))
    out.sort(key=lambda x: -x[1])
    return out


# ---------------------------------------------------------------------------
# Phase 2: tensor_phoneme_score
# ---------------------------------------------------------------------------


def tensor_phoneme_score(tensor: dict, phoneme: str) -> dict:
    """Score how strongly a phoneme links domains.

    For the given phoneme, scans every invariant, computes inter-domain
    distributional matrix and pairwise correlations on the (domain,
    object) flattened series, and produces a summary.

    Parameters
    ----------
    tensor
        Output of :func:`build_tensor`.
    phoneme
        Phoneme name; must be in ``tensor['axes']['phoneme']``.

    Returns
    -------
    dict
        ``{
            'applicable_domains': list[str],
            'mean_correlation': float,
            'max_correlation': float,
            'min_distributional_distance': float,
            'summary': 'strong link' | 'partial' | 'weak'
        }``
    """
    pi = _axis_index(tensor, "phoneme", phoneme)
    domains = list(tensor["axes"]["domain"])
    invariants = list(tensor["axes"]["invariant"])
    data = tensor["data"]
    masks = tensor["masks"]

    applicable = []
    for di, d in enumerate(domains):
        if np.any(masks[di, :, pi, :]):
            applicable.append(d)

    # Pairwise correlations across invariants (within phoneme).
    corrs: list = []
    for ia in range(len(invariants)):
        for ib in range(ia + 1, len(invariants)):
            a = data[:, :, pi, ia].ravel()
            b = data[:, :, pi, ib].ravel()
            ma = masks[:, :, pi, ia].ravel()
            mb = masks[:, :, pi, ib].ravel()
            v = ma & mb & np.isfinite(a) & np.isfinite(b)
            if v.sum() < 3:
                continue
            aa = a[v]
            bb = b[v]
            if aa.std() == 0 or bb.std() == 0:
                continue
            corrs.append(float(np.corrcoef(aa, bb)[0, 1]))

    if corrs:
        mean_corr = float(np.mean(np.abs(corrs)))
        max_corr = float(np.max(np.abs(corrs)))
    else:
        mean_corr = float("nan")
        max_corr = float("nan")

    # Min distributional distance across (invariant, domain-pair).
    min_d = float("inf")
    for iv in invariants:
        try:
            M = distributional_matrix(tensor, phoneme, iv, metric="js")
        except Exception:
            continue
        # Off-diagonal only
        n = M.shape[0]
        for i in range(n):
            for j in range(i + 1, n):
                v = M[i, j]
                if np.isfinite(v) and v < min_d:
                    min_d = float(v)
    if min_d == float("inf"):
        min_d = float("nan")

    # Summary heuristic on mean |correlation|: monotone in mean_corr.
    if not np.isfinite(mean_corr):
        summary = "weak"
    elif mean_corr >= 0.5:
        summary = "strong link"
    elif mean_corr >= 0.2:
        summary = "partial"
    else:
        summary = "weak"

    return {
        "applicable_domains": applicable,
        "mean_correlation": mean_corr,
        "max_correlation": max_corr,
        "min_distributional_distance": min_d,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Phase 2: tensor_anomaly_surface
# ---------------------------------------------------------------------------


def tensor_anomaly_surface(
    tensor: dict,
    ensemble: str = "auto",
    p_threshold: float = 0.05,
    n_skip: int = 0,
) -> list:
    """Surface (phoneme, invariant) cells whose flattened values look anomalous.

    Composes :func:`build_tensor` output with
    :func:`prometheus_math.research.anomaly_surface.surface_anomalies`.
    For each (phoneme, invariant) cell, treats the flattened finite
    values across all (domain, object) as a pseudo-spectral series and
    runs the anomaly surface. Cells that fail KS against every canonical
    RMT class are returned.

    Parameters
    ----------
    tensor
        Output of :func:`build_tensor`.
    ensemble : 'auto'
        Reserved for future per-cell ensemble selection. Currently
        passed through to surface_anomalies as the canonical class set.
    p_threshold : float, default 0.05
        Surfaced when KS-p < threshold against ALL canonical classes.
    n_skip : int, default 0
        Forwarded to surface_anomalies.

    Returns
    -------
    list of dict
        Each anomalous cell carries
        ``{'phoneme', 'invariant', 'label', 'anomaly_score',
        'candidate_classes_failed', 'ks_pvalues', 'ratios_summary'}``.
    """
    from prometheus_math.research.anomaly_surface import surface_anomalies

    phonemes = list(tensor["axes"]["phoneme"])
    invariants = list(tensor["axes"]["invariant"])
    data = tensor["data"]
    masks = tensor["masks"]

    out: list = []
    records = []
    for pi, ph in enumerate(phonemes):
        for ii, iv in enumerate(invariants):
            a = data[:, :, pi, ii].ravel()
            m = masks[:, :, pi, ii].ravel()
            valid = m & np.isfinite(a)
            zeros = a[valid].astype(float)
            if zeros.size < 10:
                continue
            # surface_anomalies needs sorted "zeros" to compute ratios
            zeros = np.sort(zeros)
            records.append({
                "label": f"{ph}/{iv}",
                "zeros": zeros.tolist(),
                "phoneme": ph,
                "invariant": iv,
            })

    if not records:
        return out

    try:
        anomalies = surface_anomalies(
            family_query={},
            n_zeros=max(10, max(len(r["zeros"]) for r in records)),
            p_threshold=p_threshold,
            n_skip=n_skip,
            zeros_records=[{"label": r["label"], "zeros": r["zeros"]} for r in records],
        )
    except Exception:  # pragma: no cover — defensive
        return out

    label_to_meta = {r["label"]: (r["phoneme"], r["invariant"]) for r in records}
    for a in anomalies:
        ph, iv = label_to_meta.get(a.get("label"), (None, None))
        out.append({
            "phoneme": ph,
            "invariant": iv,
            "label": a.get("label"),
            "anomaly_score": a.get("anomaly_score"),
            "candidate_classes_failed": a.get("candidate_classes_failed"),
            "ks_pvalues": a.get("ks_pvalues"),
            "ratios_summary": a.get("ratios_summary"),
        })
    return out


def tensor_load(path: Union[str, Path]) -> dict:
    """Load tensor from ``path.npz`` + ``path.json`` sidecar.

    Parameters
    ----------
    path
        Path passed to :func:`tensor_save`.

    Returns
    -------
    dict
        Same shape as :func:`build_tensor` output.

    Raises
    ------
    IOError
        If either the .npz or the sidecar is missing.
    """
    path = Path(path)
    if path.suffix.lower() == ".npz":
        npz_path = path
    else:
        npz_path = path.with_suffix(".npz")
    sidecar_path = npz_path.with_suffix(".json")
    if not npz_path.exists():
        raise IOError(f"tensor_load: npz not found: {npz_path}")
    if not sidecar_path.exists():
        raise IOError(f"tensor_load: sidecar not found: {sidecar_path}")
    z = np.load(npz_path, allow_pickle=True)
    data = z["data"]
    masks = z["masks"]
    object_id = z["object_id"]
    with open(sidecar_path, "r", encoding="utf-8") as f:
        sidecar = _json.load(f)
    return {
        "axes": {
            "domain": list(sidecar["domain"]),
            "phoneme": list(sidecar["phoneme"]),
            "invariant": list(sidecar["invariant"]),
            "object_id": object_id,
        },
        "data": data,
        "masks": masks,
        "meta": dict(sidecar["meta"]),
    }
