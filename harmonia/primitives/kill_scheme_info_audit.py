"""kill_scheme_info_audit.py — the information-recovery auditor for kill-label
schemes (Proposal E generalization; Harmonia C, 2026-06-10).

THE LAW THIS INSTRUMENT OPERATIONALIZES (h2 anchor case, validated 2026-06-10;
full evidence: harmonia/proposals/2026-06-09/E_RESULTS_2026-06-10.md):

  1. TRANSMISSION — a kill label transmits information about anything beyond
     the record itself only through its CLAIM-COORDINATE content (what was
     tested). Components derived from the stochastic evaluation PATH (which
     methods voted, R-squared values, margins) add label entropy but carry
     exactly zero information about an independent re-evaluation, conditional
     on the coordinates:  I(path_component ; Y_fresh | coords) = 0
     whenever evaluations are independent given coordinates.
  2. AVAILABILITY — the information available per record, I(coords; Y_fresh),
     is a property of the generator's MECHANISM, not its labeling. A label
     refactor cannot raise it (data-processing inequality); it can only stop
     withholding it.
  3. ACCUMULATION — a ledger's total predictive value about fresh evaluations
     saturates at sum_cells H(Y_fresh | cell). Volume beyond saturation
     re-measures known cells (kill-topography Finding 1, mechanized).

  Scope condition: clause 1 requires evaluations independent given the
  coordinates. Generators whose evaluation consumes accumulated corpus state
  (e.g. theseus d4) sit OUTSIDE the law; the BEYOND_COORDINATE_SIGNAL verdict
  below is the detector for that boundary (or for hidden coordinates).

Verdicts emitted per label component:
  COORDINATE_BEARING      — deterministic function of the claim coordinates;
                            transmits territory location. Keep.
  PATH_DECORATION         — varies given coordinates, adds no conditional
                            information (within permutation null). Repaint.
  BEYOND_COORDINATE_SIGNAL— conditional information above null: either the
                            independence premise is violated (state coupling)
                            or the coordinate set is incomplete. Investigate;
                            do not celebrate as signal until the mechanism
                            is named.

Companion primitives: baseline_costume.costume_check (Proposal A) gates the
same schemes from the imposter side; failure_primitives FP-002 detects the
flat-label special case. This instrument covers the case FP-002 is blind to:
a label distribution with HEALTHY entropy whose variation is all path noise
(theseus d3: hundreds of distinct labels, zero coordinate content).

Self-test: python harmonia/primitives/kill_scheme_info_audit.py
"""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

# Pre-registered thresholds (h2_info_recovery_prereg.md Q1) — change only with
# a version bump and a note in the E_RESULTS lineage.
COSMETIC_TOP1 = 0.90
DIFFERENTIATED_TOP1 = 0.75
DEFAULT_N_PERMS = 200


# ----------------------------------------------------------------------------
# Information helpers (plug-in, bits)
# ----------------------------------------------------------------------------
def entropy_bits(counter: Counter) -> float:
    tot = sum(counter.values())
    if tot == 0:
        return 0.0
    return -sum((c / tot) * math.log2(c / tot) for c in counter.values() if c)


def mi_bits(xs, ys) -> float:
    joint = Counter(zip(xs, ys))
    tot = sum(joint.values())
    if tot == 0:
        return 0.0
    px, py = Counter(xs), Counter(ys)
    mi = 0.0
    for (x, y), c in joint.items():
        mi += (c / tot) * math.log2(c * tot / (px[x] * py[y]))
    return mi


def cond_mi_bits(xs, ys, zs) -> float:
    by_z = defaultdict(lambda: ([], []))
    for x, y, z in zip(xs, ys, zs):
        by_z[z][0].append(x)
        by_z[z][1].append(y)
    n = len(xs)
    return sum((len(gx) / n) * mi_bits(gx, gy) for gx, gy in by_z.values())


def perm_null95(xs, ys, zs=None, n_perms=DEFAULT_N_PERMS, seed=0) -> float:
    """95th percentile of (C)MI under shuffling of xs."""
    rng = random.Random(seed)
    xs = list(xs)
    vals = []
    for _ in range(n_perms):
        rng.shuffle(xs)
        vals.append(mi_bits(xs, ys) if zs is None else cond_mi_bits(xs, ys, zs))
    vals.sort()
    return vals[int(0.95 * len(vals))] if vals else 0.0


# ----------------------------------------------------------------------------
# Result types
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class ComponentReport:
    name: str
    n_distinct: int
    top1_share: float
    H_bits: float
    H_given_coords_bits: float
    verdict: str                       # COORDINATE_BEARING | PATH_DECORATION |
    #                                    BEYOND_COORDINATE_SIGNAL | NO_FRESH_EVAL
    I_comp_Y_bits: Optional[float] = None
    I_comp_Y_given_coords_bits: Optional[float] = None
    cmi_null95: Optional[float] = None


@dataclass(frozen=True)
class KillSchemeAudit:
    n_rows: int
    concentration_verdict: str         # COSMETIC | DIFFERENTIATED | AMBIGUOUS
    label_top1_share: float
    label_H_bits: float
    coords_H_bits: float
    components: tuple                  # tuple[ComponentReport]
    I_coords_Y_bits: Optional[float] = None
    I_coords_Y_null95: Optional[float] = None
    I_label_Y_bits: Optional[float] = None
    I_label_Y_given_coords_bits: Optional[float] = None
    I_label_Y_given_coords_null95: Optional[float] = None
    ledger_saturation_bits: Optional[float] = None
    headline: str = ""
    notes: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------
# The auditor
# ----------------------------------------------------------------------------
def audit_kill_label_scheme(
    rows: list,
    *,
    label_fn: Callable,
    coord_fn: Callable,
    component_fns: Optional[dict] = None,
    fresh_eval_fn: Optional[Callable] = None,
    n_perms: int = DEFAULT_N_PERMS,
    seed: int = 0,
) -> KillSchemeAudit:
    """Audit a kill-label scheme for information recovery vs repaint.

    rows           — kill records (any type the accessor callables accept).
    label_fn       — row -> full label.
    coord_fn       — row -> hashable claim coordinates (what was tested,
                     fixed before evaluation). The auditor is only as honest
                     as this argument: hiding a real coordinate here converts
                     genuine signal into BEYOND_COORDINATE_SIGNAL, and
                     including a path value here launders noise into
                     COORDINATE_BEARING. Derive it from the generator's code,
                     not from the label.
    component_fns  — {name: row -> value} label-component decomposition.
    fresh_eval_fn  — row -> outcome of an INDEPENDENT re-evaluation of the
                     same coordinates (fresh seeds). Without it the audit is
                     structural only (entropy decomposition, no MI verdicts).
    """
    labels = [label_fn(r) for r in rows]
    coords = [coord_fn(r) for r in rows]
    n = len(rows)
    lc = Counter(labels)
    label_top1 = (lc.most_common(1)[0][1] / n) if n else 0.0
    label_H = entropy_bits(lc)
    coords_H = entropy_bits(Counter(coords))

    if label_top1 >= COSMETIC_TOP1:
        conc = "COSMETIC"
    elif label_top1 <= DIFFERENTIATED_TOP1:
        conc = "DIFFERENTIATED"
    else:
        conc = "AMBIGUOUS"

    ys = [fresh_eval_fn(r) for r in rows] if fresh_eval_fn else None

    i_coords_y = i_coords_null = i_label_y = i_label_cmi = label_cmi_null = None
    saturation = None
    if ys is not None:
        i_coords_y = mi_bits(coords, ys)
        i_coords_null = perm_null95(coords, ys, n_perms=n_perms, seed=seed)
        i_label_y = mi_bits(labels, ys)
        i_label_cmi = cond_mi_bits(labels, ys, coords)
        label_cmi_null = perm_null95(labels, ys, zs=coords,
                                     n_perms=n_perms, seed=seed + 1)
        by_cell = defaultdict(Counter)
        for c, y in zip(coords, ys):
            by_cell[c][y] += 1
        saturation = sum(entropy_bits(cnt) for cnt in by_cell.values())

    comps = []
    for name, fn in (component_fns or {}).items():
        vals = [fn(r) for r in rows]
        vc = Counter(vals)
        h = entropy_bits(vc)
        h_given = cond_mi_bits(vals, vals, coords)  # H(comp|coords) via I(X;X|Z)
        i_y = cmi = null95 = None
        if ys is not None:
            i_y = mi_bits(vals, ys)
            cmi = cond_mi_bits(vals, ys, coords)
            null95 = perm_null95(vals, ys, zs=coords,
                                 n_perms=n_perms, seed=seed + hash(name) % 997)
            if h_given < 1e-9 or h < 1e-9:
                verdict = "COORDINATE_BEARING"
            elif cmi > null95:
                verdict = "BEYOND_COORDINATE_SIGNAL"
            else:
                verdict = "PATH_DECORATION"
        else:
            verdict = ("COORDINATE_BEARING" if h_given < 1e-9 or h < 1e-9
                       else "NO_FRESH_EVAL")
        comps.append(ComponentReport(
            name=name, n_distinct=len(vc),
            top1_share=(vc.most_common(1)[0][1] / n) if n else 0.0,
            H_bits=h, H_given_coords_bits=h_given, verdict=verdict,
            I_comp_Y_bits=i_y, I_comp_Y_given_coords_bits=cmi,
            cmi_null95=null95))

    decorations = [c.name for c in comps if c.verdict == "PATH_DECORATION"]
    beyond = [c.name for c in comps if c.verdict == "BEYOND_COORDINATE_SIGNAL"]
    headline = (
        f"{conc} label distribution (top-1 {label_top1:.1%}); "
        f"coords carry {f'{i_coords_y:.4f}' if i_coords_y is not None else '?'} "
        f"bits about fresh evaluation"
        + (f"; saturation bound {saturation:.2f} bits" if saturation is not None
           else "")
        + (f"; PATH DECORATION: {decorations}" if decorations else "")
        + (f"; INVESTIGATE (beyond-coordinate signal): {beyond}" if beyond else "")
    )
    return KillSchemeAudit(
        n_rows=n, concentration_verdict=conc, label_top1_share=label_top1,
        label_H_bits=label_H, coords_H_bits=coords_H, components=tuple(comps),
        I_coords_Y_bits=i_coords_y, I_coords_Y_null95=i_coords_null,
        I_label_Y_bits=i_label_y, I_label_Y_given_coords_bits=i_label_cmi,
        I_label_Y_given_coords_null95=label_cmi_null,
        ledger_saturation_bits=saturation, headline=headline,
    )


# ----------------------------------------------------------------------------
# Self-test: three synthetic mechanisms exercise all three verdicts.
# ----------------------------------------------------------------------------
def _selftest() -> None:
    rng = random.Random(20260610)

    # 1. Deterministic mechanism, coordinate-bearing label (a3-like):
    #    outcome is a fixed function of the cell; label = cell.
    cells = [f"cell_{i % 12}" for i in range(1200)]
    rows1 = [{"cell": c, "y": hash(c) % 2} for c in cells]
    a1 = audit_kill_label_scheme(
        rows1, label_fn=lambda r: r["cell"], coord_fn=lambda r: r["cell"],
        component_fns={"cell": lambda r: r["cell"]},
        fresh_eval_fn=lambda r: hash(r["cell"]) % 2, n_perms=60)
    assert a1.components[0].verdict == "COORDINATE_BEARING", a1.headline
    assert a1.I_coords_Y_bits > 0.5, a1.headline           # near H(Y)
    assert a1.ledger_saturation_bits < 1e-9, a1.headline   # deterministic cells

    # 2. Null mechanism, path-decorated label (h2-like): outcome iid coin
    #    regardless of cell; label decorated with the draw.
    rows2 = [{"cell": f"cell_{i % 12}", "draw": rng.random() < 0.5}
             for i in range(1200)]
    a2 = audit_kill_label_scheme(
        rows2,
        label_fn=lambda r: f"{r['cell']}_{'hi' if r['draw'] else 'lo'}",
        coord_fn=lambda r: r["cell"],
        component_fns={"draw_tag": lambda r: "hi" if r["draw"] else "lo"},
        fresh_eval_fn=lambda r: rng.random() < 0.5, n_perms=60)
    assert a2.components[0].verdict == "PATH_DECORATION", a2.headline
    assert a2.I_coords_Y_bits < 0.05, a2.headline           # nothing available

    # 3. State-coupled mechanism (d4-like): fresh outcome correlated with the
    #    record's own path value (premise violation) -> must be flagged.
    rows3 = []
    for i in range(1200):
        hidden = rng.random() < 0.5
        rows3.append({"cell": f"cell_{i % 12}", "hidden": hidden})
    a3 = audit_kill_label_scheme(
        rows3,
        label_fn=lambda r: f"{r['cell']}_{'A' if r['hidden'] else 'B'}",
        coord_fn=lambda r: r["cell"],
        component_fns={"state_tag": lambda r: "A" if r["hidden"] else "B"},
        # "fresh" eval that secretly reads the record's state -> coupling
        fresh_eval_fn=lambda r: r["hidden"] ^ (rng.random() < 0.05),
        n_perms=60)
    assert a3.components[0].verdict == "BEYOND_COORDINATE_SIGNAL", a3.headline

    print("kill_scheme_info_audit self-test PASS")
    print("  [det+coord]  ", a1.headline)
    print("  [null+path]  ", a2.headline)
    print("  [state-coupled]", a3.headline)


if __name__ == "__main__":
    _selftest()
