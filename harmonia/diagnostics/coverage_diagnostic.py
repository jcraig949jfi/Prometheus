"""coverage_diagnostic.py — reusable hypothesis-class COVERAGE meta-instrument.

Generalizes the EC void-miner coverage audit
(harmonia/experiments/hypothesis_class_coverage_audit.py +
roles/Harmonia/AUDIT_20260622_instrument_monoculture.md) into an
import-and-call diagnostic that any instrument can be passed through.

DOCTRINE (program reassessment, 2026-06-22):
    "No '0 novel results' may be called terrain exhaustion (B1) until
     hypothesis-class coverage is measured."
A low-coverage instrument's "0 novel" is a B2 (expressiveness-ceiling) result
— a statement about the shadow the ruler casts, not the terrain. The separator
between B1 and B2 is a COVERAGE MEASURE on the hypothesis class:

    perfect in-class recall + ZERO out-of-class possibility + a NARROW class
        => B2_CEILING   (fixable by widening the class along named axes)
    high in-class recall + a BROAD class (little structural left out)
        => B1_EXHAUSTED (terrain is genuinely flat)
    a PROOF that the whole class is degenerate / dead
        => B1_EXHAUSTED_BY_PROOF (terrain dead, but for a structural reason,
           not because we searched it out)
    in-class laws MISSED (recall < 1 inside the class)
        => MIXED / INCONCLUSIVE (search insufficiency, not a clean ceiling)

The robust signal is the SHAPE (perfect-in + zero-out = ceiling), not the exact
coverage percentage — curated target lists are illustrative (stated honestly in
every report). [feedback_distinguish_B1_B2, feedback_failure_signature_doctrine]

Run (EC regression + self-test):
    PYTHONPATH=. PYTHONIOENCODING=utf-8 python harmonia/diagnostics/coverage_diagnostic.py
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Blocking-axis enum — the SHAPE of the ceiling (why an out-of-class target is
# unreachable). Generalized from the EC audit's six axes; IN_CLASS is the
# in-class sentinel. Instruments may extend the vocabulary, but a target's axis
# must be one of these for the histogram to be comparable across instruments.
# ---------------------------------------------------------------------------
AXES = (
    "IN_CLASS",        # expressible: inside the instrument's hypothesis class
    "UNARY",           # property of ONE element, not a relation between two
    "ARITY_GE_3",      # relates 3+ elements simultaneously
    "REAL_VALUED",     # involves a non-integer / continuous quantity
    "RELATION_OOV",    # the relation/operator is not in the instrument's set
    "CROSS_OBJECT",    # relates DIFFERENT objects (the pairing is identity-only)
    "DISTRIBUTIONAL",  # a statement about a SEQUENCE / distribution, not scalars
    "COMPOSITIONAL",   # requires composing primitives the instrument can't chain
    "PROOF_DEAD",      # the class is provably degenerate (B1-by-proof marker)
    "OTHER",           # escape hatch; state the reason in the note
)


@dataclass
class Target:
    """One known/surveyed structural fact in the instrument's domain.

    axis == "IN_CLASS"  -> expressible by the instrument.
    found               -> the instrument actually surfaced it (only meaningful
                           when in_class; an out-of-class target can never be
                           found, by construction).
    note                -> auditable justification for the axis assignment.
    """
    name: str
    axis: str
    found: bool = False
    note: str = ""

    @property
    def in_class(self) -> bool:
        return self.axis == "IN_CLASS"


@dataclass
class HypothesisClassSpec:
    """The measured hypothesis class of an instrument.

    class_size: total number of distinguishable claims the instrument can emit
                (computed from the real vocabulary — operators/relations/
                invariants or rungs/primitives). Use 0 if the class is a fixed
                finite catalog whose size IS the vocabulary count.
    breadth: a coarse 'narrow' | 'broad' judgement on the SHAPE of the class
             (not its raw size). A 10k-cell class of a single fixed claim shape
             is NARROW; a class spanning many shapes/arities is BROAD. This
             distinguishes B2 (narrow + ceiling) from B1 (broad + exhausted).
    proof_dead: True if a theorem proves the whole class degenerate (a3 cross-
                product under the product-measure theorem). Forces B1-by-proof.
    """
    instrument_name: str
    vocabulary: Dict[str, List[str]]          # named axes of the class -> members
    class_size: int
    claim_shape: str                          # human description of the one shape
    breadth: str = "narrow"                   # "narrow" | "broad"
    proof_dead: bool = False
    proof_note: str = ""
    notes: str = ""

    def __post_init__(self):
        assert self.breadth in ("narrow", "broad"), self.breadth


@dataclass
class CoverageReport:
    instrument: str
    class_size: int
    claim_shape: str
    breadth: str
    n_targets: int
    n_in_class: int
    n_in_class_found: int
    n_out_of_class: int
    in_class_recall: Optional[float]          # found / in_class (None if 0 in-class)
    expressible_fraction: float               # in_class / total
    out_of_class_fraction: float
    ceiling_axes: Dict[str, int]              # axis histogram over out-of-class
    verdict: str
    verdict_reason: str
    proof_dead: bool
    per_target: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Core diagnostic
# ---------------------------------------------------------------------------
def coverage(spec: HypothesisClassSpec, targets: List[Target]) -> CoverageReport:
    """Measure hypothesis-class coverage and assign a typed B1/B2 verdict.

    spec    : the measured hypothesis class (vocabulary + size + breadth).
    targets : curated list of known structural facts in the domain, each tagged
              with the blocking axis (IN_CLASS or a reason it is out of class).

    Returns a CoverageReport. The verdict separates:
        B2_CEILING               narrow class, perfect in-class recall, zero
                                 out-of-class -> instrument-bound, widen the
                                 class along the dominant ceiling axes.
        B1_EXHAUSTED             broad class, high in-class recall, little
                                 structural left unexpressed -> terrain flat.
        B1_EXHAUSTED_BY_PROOF    spec.proof_dead -> a theorem kills the class.
        MIXED_INCONCLUSIVE       in-class laws MISSED (recall < 1) -> search
                                 insufficiency confounds the ceiling read; or
                                 the signal is genuinely ambiguous.
    """
    for t in targets:
        assert t.axis in AXES, f"unknown axis {t.axis!r} for {t.name!r}"
        if t.found:
            assert t.in_class, f"out-of-class target {t.name!r} marked found"

    n = len(targets)
    in_class = [t for t in targets if t.in_class]
    out_class = [t for t in targets if not t.in_class]
    n_in = len(in_class)
    n_out = len(out_class)
    n_found = sum(t.found for t in in_class)
    recall = (n_found / n_in) if n_in else None
    expr_frac = n_in / n if n else 0.0
    out_frac = n_out / n if n else 0.0
    axes_hist = dict(Counter(t.axis for t in out_class).most_common())

    verdict, reason = _verdict(spec, n_in, n_found, recall, expr_frac, axes_hist)

    return CoverageReport(
        instrument=spec.instrument_name,
        class_size=spec.class_size,
        claim_shape=spec.claim_shape,
        breadth=spec.breadth,
        n_targets=n,
        n_in_class=n_in,
        n_in_class_found=n_found,
        n_out_of_class=n_out,
        in_class_recall=recall,
        expressible_fraction=round(expr_frac, 3),
        out_of_class_fraction=round(out_frac, 3),
        ceiling_axes=axes_hist,
        verdict=verdict,
        verdict_reason=reason,
        proof_dead=spec.proof_dead,
        per_target=[{**asdict(t), "in_class": t.in_class} for t in targets],
    )


def _verdict(spec, n_in, n_found, recall, expr_frac, axes_hist) -> Tuple[str, str]:
    # 1. Proof-dead class: terrain is dead, but BY THEOREM, not by search.
    if spec.proof_dead:
        return ("B1_EXHAUSTED_BY_PROOF",
                "the hypothesis class is provably degenerate "
                f"({spec.proof_note}); '0 novel' here is a structural certainty, "
                "not an instrument shadow — widening THIS class cannot help, the "
                "class itself must be abandoned for a non-degenerate pairing.")

    # 2. In-class laws MISSED -> search insufficiency confounds the read.
    if n_in > 0 and recall is not None and recall < 1.0:
        return ("MIXED_INCONCLUSIVE",
                f"in-class recall {recall:.0%} ({n_found}/{n_in}) < 1: the "
                "instrument misses laws it COULD express, so '0 novel' is "
                "confounded by search insufficiency — neither a clean ceiling "
                "(B2) nor clean exhaustion (B1). Fix search before reading "
                "coverage.")

    # 3. No in-class targets at all -> can't certify recall -> inconclusive.
    if n_in == 0:
        return ("MIXED_INCONCLUSIVE",
                "zero surveyed targets fall inside the class; coverage is "
                f"{expr_frac:.0%} and the instrument expresses none of the "
                "curated structure — strongly ceiling-shaped, but with no "
                "in-class recall to certify the instrument even works. Add an "
                "in-class target or widen the survey.")

    # From here: perfect in-class recall (recall == 1.0, n_found == n_in > 0).
    out_dominates = expr_frac < 0.5
    if spec.breadth == "narrow" and out_dominates:
        top = ", ".join(f"{a}:{k}" for a, k in axes_hist.items()) or "none"
        return ("B2_CEILING",
                f"perfect in-class recall ({n_found}/{n_in}) and zero of the "
                f"{sum(axes_hist.values())} out-of-class targets reachable, on a "
                f"NARROW class expressing only {expr_frac:.0%} of surveyed "
                f"structure. Signature of a ceiling, not flat terrain. Dominant "
                f"blocking axes: [{top}] — widening along these (not adding more "
                "in-class vocabulary) is the fix.")

    if spec.breadth == "broad" and expr_frac >= 0.5:
        return ("B1_EXHAUSTED",
                f"perfect in-class recall ({n_found}/{n_in}) on a BROAD class "
                f"covering {expr_frac:.0%} of surveyed structure with little "
                "left out-of-class. '0 novel' is most consistent with a flat "
                "terrain, not an instrument shadow.")

    # Mixed signals (narrow but high coverage, or broad but low coverage).
    return ("MIXED_INCONCLUSIVE",
            f"perfect in-class recall but breadth={spec.breadth!r} and "
            f"coverage={expr_frac:.0%} send conflicting signals (narrow classes "
            "should be low-coverage, broad classes high). Re-examine the breadth "
            "call or the target survey before assigning B1/B2.")


# ---------------------------------------------------------------------------
# Pretty-printer (shared by every instrument runner)
# ---------------------------------------------------------------------------
def render(report: CoverageReport) -> str:
    L = []
    L.append("=" * 74)
    L.append(f"COVERAGE DIAGNOSTIC — {report.instrument}")
    L.append("=" * 74)
    L.append(f"  claim shape : {report.claim_shape}")
    L.append(f"  class size  : {report.class_size}   breadth: {report.breadth}"
             + ("   [PROOF-DEAD]" if report.proof_dead else ""))
    rec = "n/a" if report.in_class_recall is None else f"{report.in_class_recall:.0%}"
    L.append(f"  targets surveyed ......... {report.n_targets}")
    L.append(f"  EXPRESSIBLE in class ..... {report.n_in_class}/{report.n_targets}"
             f" = {report.expressible_fraction:.0%}")
    L.append(f"    in-class recall (found). {report.n_in_class_found}/{report.n_in_class}"
             f" = {rec}")
    L.append(f"  OUT OF CLASS ............. {report.n_out_of_class}/{report.n_targets}"
             f" = {report.out_of_class_fraction:.0%}")
    if report.ceiling_axes:
        L.append("  ceiling axes (out-of-class):")
        for a, k in report.ceiling_axes.items():
            L.append(f"    {a:16s} {k}")
    L.append("  per-target:")
    for t in report.per_target:
        mark = ("FOUND" if t["found"]
                else "in-class, not surfaced" if t["in_class"]
                else t["axis"])
        L.append(f"    [{mark:>22s}] {t['name']}")
    L.append("")
    L.append(f"  VERDICT: {report.verdict}")
    L.append(f"  {report.verdict_reason}")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# EC regression case — refactored to use the reusable diagnostic. Reproducing
# the 25% / B2_CEILING result here is the regression check for this module.
# ---------------------------------------------------------------------------
def ec_spec_and_targets() -> Tuple[HypothesisClassSpec, List[Target]]:
    """Rebuild the EC void-miner case from the live instrument vocabulary."""
    import sys
    from pathlib import Path
    repo = Path(__file__).resolve().parents[2]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from theseus.generators.a3_functional_identity import OPERATORS
    from theseus.generators.a1_catalog_cross_product import RELATIONS

    # The 9 integer invariants the EC-rich diagonal sweep actually mined.
    EC_RICH_INVARIANTS = (
        "rank", "conductor", "tamagawa_product", "torsion",
        "sha_an", "num_bad_primes", "cm", "signD", "conductor_radical",
    )
    n_ops, n_rel, n_inv = len(OPERATORS), len(RELATIONS), len(EC_RICH_INVARIANTS)
    n_pairs = n_inv * (n_inv - 1)                  # ordered diagonal pairs i != j
    class_size = n_ops * n_ops * n_pairs * n_rel   # 6*6*72*4 = 10368

    spec = HypothesisClassSpec(
        instrument_name="EC void-miner (a3/EC-rich diagonal)",
        vocabulary={
            "operators": list(OPERATORS.keys()),
            "relations": list(RELATIONS),
            "invariants": list(EC_RICH_INVARIANTS),
        },
        class_size=class_size,
        claim_shape="rel(f(inv_i(O)), g(inv_j(O))) — pairwise, integer-valued, "
                    "scalar relation in 4, same-object diagonal",
        breadth="narrow",
        notes="all invariants integer; all relations scalar; pairwise; same object",
    )

    # 16 surveyed known EC laws (hand-curated; illustrative, not canonical —
    # the robust signal is the SHAPE). Mirrors the original audit table.
    targets = [
        Target("Lorenzini 2011: |E(Q)_tors| divides prod(c_p)", "IN_CLASS",
               found=True, note="torsion divides tamagawa_product; FOUND"),
        Target("Shared prime support: rad(N)|N and N==rad(N) mod 2", "IN_CLASS",
               found=True, note="conductor_radical vs conductor; FOUND"),
        Target("BSD rank equality: ord_{s=1} L == rank", "IN_CLASS", found=False,
               note="analytic_rank==rank IS in-class but analytic_rank not mined"),
        Target("Parity conjecture: rank == (1-root_number)/2 mod 2", "IN_CLASS",
               found=False, note="in-class but root_number not a mined invariant"),
        Target("Mazur 1977: |E(Q)_tors| in {1..10,12}", "UNARY",
               note="bound on ONE invariant; injectable (T1b), not discoverable"),
        Target("|Sha| is a perfect square", "UNARY",
               note="property of sha_an alone; needs a unary-property miner"),
        Target("Modularity: E/Q from a weight-2 newform", "CROSS_OBJECT",
               note="correspondence to an object of another category"),
        Target("Sato-Tate equidistribution of a_p", "DISTRIBUTIONAL",
               note="law about the sequence (a_p) and a real limiting measure"),
        Target("Ogg's formula: f_p = ord_p(Delta)+1-m_p", "ARITY_GE_3",
               note="three per-prime quantities; arity 3, per-prime"),
        Target("Szpiro/abc: log|Delta| <= (6+eps) log N", "RELATION_OOV",
               note="multiplicative/asymptotic bound; not abs_diff_le_3"),
        Target("BSD formula (full)", "REAL_VALUED",
               note="regulator, period, L-value derivative are real-valued"),
        Target("Conductor is isogeny-invariant", "CROSS_OBJECT",
               note="equality across an isogeny ORBIT of distinct curves"),
        Target("Root number = product of local root numbers", "DISTRIBUTIONAL",
               note="product over a per-prime family"),
        Target("Torsion injects into E(F_p) (good reduction)", "CROSS_OBJECT",
               note="relates E(Q)_tors to reduction E(F_p) — different object"),
        Target("Kodaira/Tate reduction types per bad prime", "RELATION_OOV",
               note="categorical per-prime classification; no scalar relation"),
        Target("Conductor-discriminant prime-support equality", "RELATION_OOV",
               note="set-equality of prime supports; Delta not mined"),
    ]
    return spec, targets


def _selftest():
    spec, targets = ec_spec_and_targets()
    rep = coverage(spec, targets)
    print(render(rep))
    # Regression assertions: must reproduce the 25% / B2 result.
    assert rep.class_size == 10368, rep.class_size
    assert rep.n_in_class == 4 and rep.n_targets == 16, (rep.n_in_class, rep.n_targets)
    assert abs(rep.expressible_fraction - 0.25) < 1e-9, rep.expressible_fraction
    assert rep.n_in_class_found == 2, rep.n_in_class_found
    # recall is 2/4 = 0.5 -> by the strict separator this is MIXED, NOT B2,
    # because two IN-CLASS laws (BSD rank eq, parity) were never offered an
    # invariant. The original audit reported B2 by treating "in-class but no
    # invariant" as out-of-the-CATALOG. Reconcile by measuring coverage of the
    # CATALOG class (invariants actually mined), where those two are out-of-class.
    assert rep.verdict == "MIXED_INCONCLUSIVE", rep.verdict
    print("\n[selftest] full-class read = MIXED (2 in-class laws lack a mined "
          "invariant). Catalog-class read below reproduces the audit's B2:\n")
    rep2 = coverage(*ec_catalog_spec_and_targets())
    print(render(rep2))
    assert rep2.verdict == "B2_CEILING", rep2.verdict
    assert rep2.n_in_class == 2 and rep2.n_in_class_found == 2
    assert abs(rep2.expressible_fraction - 2 / 16) < 1e-9
    print("\n[selftest] PASS — EC catalog-class reproduces perfect-in/zero-out "
          "B2_CEILING; full-class read honestly flags the 2 un-offered in-class "
          "laws as MIXED (a STRICTER read than the original prose).")


def ec_catalog_spec_and_targets() -> Tuple[HypothesisClassSpec, List[Target]]:
    """The EC class as the miner ACTUALLY ran it: 9 mined invariants only, so
    'expressible' means 'an invariant exists for it'. This is the class the
    original audit's 25% (4/16 expressible, 2 with an invariant) measured; here
    we measure the CATALOG class where the 2 un-offered in-class laws are out of
    class (axis RELATION_OOV: their invariant — analytic_rank/root_number — is
    not in the mined vocabulary), reproducing perfect-in/zero-out B2."""
    spec, targets = ec_spec_and_targets()
    spec.instrument_name = "EC void-miner (catalog class: 9 mined invariants)"
    spec.claim_shape += "  [invariant must be one of the 9 actually mined]"
    out = []
    for t in targets:
        if t.name.startswith("BSD rank equality") or t.name.startswith("Parity"):
            out.append(Target(t.name, "RELATION_OOV", found=False,
                              note="in-class in shape, but the needed invariant "
                                   "(analytic_rank/root_number) was never mined"))
        else:
            out.append(t)
    return spec, out


if __name__ == "__main__":
    _selftest()
