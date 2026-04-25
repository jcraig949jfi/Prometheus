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
