"""failure_primitives.py — Proposal D: the cross-agent failure-primitive atlas
(machine layer). v0, thin registry per 00_SEQUENCING_AND_HANDOFF.md §3.

The agent-level analogue of Erebos's claim-level `_kill_pattern_registry.py`:
type the failure SHAPE, make it queryable, make the voids visible. Each entry
is a FailurePrimitive whose `signature` is a detectable predicate — never a
verdict-line. An entry that reduces to "agent X failed" is rejected at
registration (see `_admission_check`).

Doctrine bindings:
- feedback_failure_signature_doctrine: report failure SHAPES, not verdicts.
- SHADOWS_ON_WALL: 1 anchor = shadow; 2 = surviving candidate; >=3 across
  INDEPENDENT lineages = coordinate-invariant. Lineage-sharing anchors count
  as ONE observation (the same shadow cast twice).
- Proposal D §4 falsifiers: a detector that never fires on agents that didn't
  author it demotes the entry to cautionary_tale.

Human layer: harmonia/memory/architecture/failure_primitive_atlas.md.
`validate_atlas()` cross-checks the MD against this registry (validator
ships with the doc, per feedback_validators_ship_with_docs).
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
ATLAS_MD = REPO_ROOT / "harmonia" / "memory" / "architecture" / "failure_primitive_atlas.md"


# ----------------------------------------------------------------------------
# Schema
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class AnchorCase:
    """One concrete observed instance of the failure shape.

    lineage: the code/authorship lineage the observation came through.
    Two anchors with the same lineage are ONE independent observation —
    this is what makes coordinate_invariant ruthless (Proposal D §5 Q1).
    """
    agent: str
    artifact: str            # repo path or doc reference, absolute or repo-relative
    date: str                # YYYY-MM-DD of the observation
    lineage: str             # e.g. "erebos-layer2", "theseus-gen", "polyhymnia-scour"
    note: str = ""
    escrow: bool = False     # detector fired but cause attribution owed; an
                             # escrowed anchor NEVER counts toward invariance


@dataclass(frozen=True)
class DetectorResult:
    fired: bool
    headline: str
    evidence: dict = field(default_factory=dict)


@dataclass
class FailurePrimitive:
    id: str                                  # FP-NNN
    name: str
    signature: str                           # detectable predicate, stated as a SHAPE
    detector: Optional[Callable]             # callable -> DetectorResult, or None
    detector_kind: str                       # "live" | "stub" | "demoted:cautionary_tale"
    anchor_cases: tuple                      # tuple[AnchorCase]
    mitigation: str                          # what stopped it where it was stopped ("" ok)
    void_flag: tuple                         # agents detector SHOULD run against but hasn't
    independence_status: str                 # "proven" | "refuted" | "pending"
    independence_note: str = ""
    notes: str = ""

    @property
    def independent_anchor_count(self) -> int:
        return len({a.lineage for a in self.anchor_cases if not a.escrow})

    @property
    def coordinate_invariant(self) -> bool:
        """>=3 anchors across DISTINCT lineages, with independence audited.
        'pending' never qualifies — unproven independence is a shared-prior
        risk, not an invariant."""
        return (self.independent_anchor_count >= 3
                and self.independence_status == "proven")

    @property
    def tier(self) -> str:
        n = self.independent_anchor_count
        if self.coordinate_invariant:
            return "coordinate_invariant"
        if n >= 2:
            return "surviving_candidate"
        return "shadow"


_VERDICT_LINE = re.compile(
    r"^\s*\w[\w\s-]*\s+(passed|failed|succeeded|broke)\b[.\s]*$", re.IGNORECASE)


def _admission_check(fp: FailurePrimitive) -> None:
    """Reject entries that violate the failure-signature doctrine."""
    if not fp.signature.strip():
        raise ValueError(f"{fp.id}: empty signature")
    if _VERDICT_LINE.match(fp.signature):
        raise ValueError(
            f"{fp.id}: signature is a verdict-line, not a detectable shape: "
            f"{fp.signature!r}")
    if fp.detector is None and fp.detector_kind == "live":
        raise ValueError(f"{fp.id}: detector_kind='live' but detector is None")
    if not fp.anchor_cases:
        raise ValueError(f"{fp.id}: at least one concrete anchor case required")
    if fp.detector_kind not in ("live", "stub", "demoted:cautionary_tale"):
        raise ValueError(f"{fp.id}: bad detector_kind {fp.detector_kind!r}")


# ----------------------------------------------------------------------------
# FP-001 detector — baseline costume
# ----------------------------------------------------------------------------
def detect_baseline_costume(claim, rows, *, key_fn, label_fn,
                            signature_fn=None, **kw) -> DetectorResult:
    """Does the structural claim tie a cheap baseline? Delegates to the frozen
    Proposal A primitive (harmonia.primitives.baseline_costume.costume_check).
    Fires iff verdict is COSTUME_OF:<baseline>."""
    from harmonia.primitives.baseline_costume import costume_check
    v = costume_check(claim, rows, key_fn=key_fn, label_fn=label_fn,
                      signature_fn=signature_fn, **kw)
    return DetectorResult(
        fired=v.verdict.startswith("COSTUME_OF"),
        headline=v.headline,
        evidence={"verdict": v.verdict,
                  "strongest_tie": v.strongest_tie,
                  "z_vs_null": v.z_vs_null,
                  "per_baseline_agreement":
                      v.diagnostics.get("per_baseline_agreement", {})},
    )


# ----------------------------------------------------------------------------
# FP-002 detector — opaque-kill black hole
# ----------------------------------------------------------------------------
def detect_opaque_kill_blackhole(
    kill_patterns: Sequence[str],
    *,
    top1_share_threshold: float = 0.30,
    min_records: int = 1000,
    payload_variation: Optional[Callable[[str], bool]] = None,
) -> DetectorResult:
    """A single kill-label absorbing >= top1_share_threshold of a >= min_records
    ledger is an information-loss hole: that fraction of kill volume emits no
    direction (h2: one label, 44% of 200K). Optionally, payload_variation(top1)
    -> True means the dominant label's records DO carry varying witness fields,
    which downgrades the hole (the label is coarse but the payload is not).

    Input is just the kill-label column — works on any agent's ledger.
    """
    n = len(kill_patterns)
    if n == 0:
        return DetectorResult(False, "empty ledger; nothing to scan", {"n": 0})
    counts = Counter(kill_patterns)
    top1, top1_n = counts.most_common(1)[0]
    top1_share = top1_n / n
    # Normalized Shannon entropy of the label distribution (0 = one label).
    if len(counts) > 1:
        h = -sum((c / n) * math.log(c / n) for c in counts.values())
        h_norm = h / math.log(len(counts))
    else:
        h_norm = 0.0
    fired = n >= min_records and top1_share >= top1_share_threshold
    downgraded = False
    if fired and payload_variation is not None and payload_variation(top1):
        fired, downgraded = False, True
    return DetectorResult(
        fired=fired,
        headline=(f"top-1 label '{top1}' absorbs {top1_share:.1%} of {n} kills "
                  f"(entropy_norm={h_norm:.2f})"
                  + ("; DOWNGRADED: payload under top-1 varies" if downgraded
                     else "")),
        evidence={"n": n, "n_labels": len(counts), "top1": top1,
                  "top1_share": round(top1_share, 4),
                  "entropy_norm": round(h_norm, 4),
                  "threshold": top1_share_threshold,
                  "payload_downgrade": downgraded},
    )


# ----------------------------------------------------------------------------
# FP-003 detector — bounded-menu wall
# ----------------------------------------------------------------------------
def detect_bounded_menu_wall(
    promotions_per_batch: Sequence[int],
    *,
    menu_fingerprints: Optional[Sequence[str]] = None,
    min_streak: int = 30,
) -> DetectorResult:
    """>= min_streak consecutive zero-promotion batches at the ledger tail,
    while the candidate-generation menu stayed FIXED, is a structural ceiling —
    not a tuning failure (Techne: 90 batches; Polyhymnia: saturated single
    scour, 84% null ticks). menu_fingerprints (one per batch, any hashable
    repr of the menu) lets the detector distinguish wall (menu constant over
    the streak) from churn (menu changed and still nothing promoted — a
    different, worse shape). Without fingerprints the menu is assumed fixed
    and the result says so.

    INPUT CONTRACT (learned from the 2026-06-10 Apollo audit): `promotions`
    must be HONEST promotions — events where the substrate accepted something
    strictly better. For capacity-bound archives (MAP-Elites), cell-fill
    counts saturate by design; pass within-cell fitness improvements instead,
    or the detector false-positives on benign saturation-at-capacity. The
    caller owns this distinction; the result cannot detect it from the series.
    """
    n = len(promotions_per_batch)
    if n == 0:
        return DetectorResult(False, "empty batch ledger", {"n_batches": 0})
    streak = 0
    for p in reversed(promotions_per_batch):
        if p == 0:
            streak += 1
        else:
            break
    menu_constant = True
    menu_known = menu_fingerprints is not None
    if menu_known and streak > 0:
        tail = list(menu_fingerprints)[-streak:]
        menu_constant = len(set(tail)) == 1
    fired = streak >= min_streak and menu_constant
    return DetectorResult(
        fired=fired,
        headline=(f"tail zero-promotion streak={streak}/{n} batches "
                  f"(min_streak={min_streak}); menu "
                  + ("constant" if menu_constant else "CHANGED during streak")
                  + ("" if menu_known else " (assumed fixed; no fingerprints)")),
        evidence={"streak": streak, "n_batches": n, "min_streak": min_streak,
                  "menu_constant": menu_constant, "menu_known": menu_known},
    )


# ----------------------------------------------------------------------------
# FP-004 detector — degenerate-field flatline
# (graduated from the 2026-06-10 generative hunt; 4 code-disjoint anchors)
# ----------------------------------------------------------------------------
def detect_degenerate_field_flatline(
    records: Sequence[dict],
    field: str,
    *,
    min_records: int = 20,
    writer_events: Optional[int] = None,
    missing=object(),
) -> DetectorResult:
    """A field the design declares as VARYING is degenerate across the whole
    ledger (single value / never populated / pinned at a bound) despite live
    upstream writers — so every downstream metric or structure verdict computed
    on it is algebraically forced and gets read as a domain finding.

    Generalizes a retraction Harmonia already paid for: a correlation matrix
    over single-component (rank-1-forced) kill vectors
    (reaudit_killvector_rank1_2026-05-27); Apollo's `llm_alive=0` population
    despite 9,089 LLM-mutation events; a health composite computed on a
    dead channel (Polyhymnia); identical depth-2 confidence signatures across
    77% of hubs (Noesis).

    Fires iff the ledger is non-trivially sized AND the field has <=1 distinct
    populated value. If `writer_events` is given and exceeds the field's
    populated count, that is the smoking gun (writers fired; field stayed flat)
    and is surfaced in the evidence.
    """
    n = len(records)
    if n < min_records:
        return DetectorResult(
            False, f"only {n} records (< min_records={min_records}); no verdict",
            {"n": n, "field": field, "insufficient_volume": True})
    vals = [r.get(field, missing) for r in records]
    populated = [v for v in vals if v is not missing and v is not None]
    distinct = len(set(populated))
    pop_frac = len(populated) / n
    top_val, top_share = None, 0.0
    if populated:
        c = Counter(populated)
        top_val, top_n = c.most_common(1)[0]
        top_share = top_n / len(populated)
    degenerate = distinct <= 1
    writers_contradict = (writer_events is not None
                          and writer_events > len(populated))
    return DetectorResult(
        fired=degenerate,
        headline=(f"field '{field}': {distinct} distinct value(s) over {n} records "
                  f"(populated {pop_frac:.0%}"
                  + (f", top='{top_val}' {top_share:.0%}" if populated else "")
                  + ")"
                  + (f"; but {writer_events} writer events fired -> FLATLINE"
                     if writers_contradict else "")),
        evidence={"n": n, "field": field, "distinct": distinct,
                  "populated_fraction": round(pop_frac, 4),
                  "top_value": top_val, "top_share": round(top_share, 4),
                  "writer_events": writer_events,
                  "writers_contradict": writers_contradict},
    )


# ----------------------------------------------------------------------------
# The registry — seeds FP-001/002/003 per the handoff §3; FP-004 from the hunt
# ----------------------------------------------------------------------------
REGISTRY: dict = {}


def register(fp: FailurePrimitive) -> FailurePrimitive:
    _admission_check(fp)
    if fp.id in REGISTRY:
        raise ValueError(f"duplicate id {fp.id}")
    REGISTRY[fp.id] = fp
    return fp


register(FailurePrimitive(
    id="FP-001",
    name="baseline_costume",
    signature=("A structural claim derived from rows R ties (>=90% agreement on "
               ">=5 shared keys) a cheap baseline computable from R's marginals "
               "or co-occurrence counts — the 'found structure' is the baseline "
               "wearing a hat."),
    detector=detect_baseline_costume,
    detector_kind="live",
    anchor_cases=(
        AnchorCase("erebos", "pivot/sprint1/phase3/PHASE3_0_SMOKE_VERDICT_2026-05-30.md",
                   "2026-05-30", "erebos-layer2",
                   "ITER-56: 9.8-sigma 'motif structure' == per-plugin majority counter"),
        AnchorCase("theseus", "pivot/kill_topography_findings_2026-05-29.md",
                   "2026-05-29", "theseus-gen",
                   "Finding 1: kill concentration == catalog volume (volume mimicry)"),
    ),
    mitigation=("Gate every structure claim through baseline_costume.costume_check "
                "before promotion (Proposal A; shipped 2026-06-10)."),
    void_flag=("theseus-a3-voids (Proposal B gate, pending)",
               "theseus-h2-subclasses (Proposal E §3.3, pending)",
               "apollo-branch-c-archive-keying",
               "icarus-lens-attribution"),
    independence_status="proven",
    independence_note=("Erebos Layer 2 (charon/agents/erebos, kill-ledger motifs) and "
                       "Theseus kill-topography (theseus/, generator corpus) share no "
                       "scour/scoring code; the shape recurred across distinct "
                       "pipelines. 2 independent anchors -> surviving_candidate; "
                       "third anchor expected from a3/h2 checks."),
    notes=("Additional SAME-lineage instance (adds zero independence, recorded for "
           "completeness): Theseus calibration-v2 sweep's apparent 18.5% F2 signal "
           "was two layers of the generators' own construction (mutation "
           "inheritance + selection/transform) — an instrument reading its own "
           "construction, killed by v3's independent null "
           "(pivot/calibration_v3_VERDICT_2026-06-03.md). Lineage theseus-gen, "
           "same as the kill-topography anchor."),
))

register(FailurePrimitive(
    id="FP-002",
    name="opaque_kill_black_hole",
    signature=("One kill-label absorbs >=30% of a >=1000-record ledger with no "
               "varying witness payload beneath it: that volume confirms failures "
               "happened but emits zero direction (gradient destroyed)."),
    detector=detect_opaque_kill_blackhole,
    detector_kind="live",
    anchor_cases=(
        AnchorCase("theseus", "pivot/kill_topography_findings_2026-05-29.md",
                   "2026-05-29", "theseus-gen",
                   "Finding 3: h2_method_triangulated_reject = 43.68% of 200K kills, "
                   "zero internal differentiation"),
    ),
    mitigation=("h2 refactor landed (structured kill patterns with agreement-class + "
                "witness pair + method tag); historical backfill = Proposal E, "
                "Harmonia C."),
    void_flag=("apollo-kill-logs", "icarus-kill-clusters",
               "charon-plugin-ledger", "ergon-shadow-archive"),
    independence_status="pending",
    independence_note="Single anchor (shadow tier). Cross-agent scans queued in void_flag.",
))

register(FailurePrimitive(
    id="FP-003",
    name="bounded_menu_wall",
    signature=("A fixed candidate-generation menu produces a >=30-batch tail of "
               "consecutive zero promotions under honest scoring: a structural "
               "ceiling of the menu, not a search/tuning failure. Deepening the "
               "menu in-place does not break it; menu growth or lineage branching "
               "does."),
    detector=detect_bounded_menu_wall,
    detector_kind="live",
    anchor_cases=(
        AnchorCase("theseus-substrate (Techne-operated)",
                   "roles/Techne/SUBSTRATE_FIRE_LOG_2026-05-21.md",
                   "2026-05-29", "theseus-techne-loop",
                   "Fires #142-#236: 92 consecutive 0-promoted after the Fire #141 "
                   "honest-scoring fix; fixed claim space (one hardcoded relation "
                   "tuple x one catalog pair) over a region calibration v3 proved "
                   "empty. Cause subclass: region_empty. Autopsy: "
                   "pivot/calibration_v3_VERDICT_2026-06-03.md. NOTE: 'Techne' and "
                   "'Theseus' walls are ONE observation — Techne is the operator "
                   "role of the Theseus substrate, one fire ledger."),
        AnchorCase("polyhymnia", "aporia/meta/triage_report_2026-06-03.md",
                   "2026-06-03", "polyhymnia-scour-aporia-shell",
                   "280 ticks / 236 null (84.3%): single scour saturated its source "
                   "(2415 tesserae, mtime-cached *.py walk); adaptation menu = 5 "
                   "no-op stubs + 1 real item that cannot help; absorbing "
                   "approval-gate state (163 dup tickets). Cause subclass: "
                   "source_saturated. Primary: aporia/meta/queue/aporia_inbox.jsonl "
                   "ticket T-2026-06-03-aporia-polyhymnia-verdict; commit 824a668b."),
        AnchorCase("apollo", "harmonia/experiments/fp_void_audits_20260610.json",
                   "2026-06-10", "apollo-blackboard-evolve",
                   "DETECTOR-FIRED (this atlas's first cross-agent firing): Branch C "
                   "r1 49/49 and r2 480/480 gens with zero best_acc improvement "
                   "under fixed op menu, search alive (mutation_viability=1.0, "
                   "llm_used>0). ESCROW RESOLVED 2026-06-15 (Harmonia E) -> cause "
                   "subclass = expressiveness_ceiling, NOT Goodhart. Apollo's own "
                   "2026-06-10 artifacts (apollo/pivot/r2_run1_findings_2026-06-10.md "
                   "+ apollo/pivot/cross_tier_falsification_result_2026-06-10.json) "
                   "attribute the plateau to a type-bridge gap: the op menu cannot "
                   "EXPRESS a cross-tier organism (no op reads derived_facts -> writes "
                   "relations/ordered), so the better organism is outside the search "
                   "space, not unfound. NOT Goodhart: best_acc stayed honestly flat at "
                   "0.42 (no proxy inflated while quality stalled). Confirmed by the "
                   "FP-003 mitigation itself: deepening the menu in-place made it WORSE "
                   "(dup-op clones 0.42->0.27) but growing the menu by ONE bridge op "
                   "(relations_from_facts) made the cross-tier organism expressible -> "
                   "0.42->1.0, unique_solver=true, all single-tier controls <=0.3. "
                   "This is FP-003's predicted escape ('menu growth breaks it; "
                   "deepening in-place does not'). 3rd proven-independent lineage. "
                   "EXECUTING-LENS CONFIRMED 2026-06-15: detector re-run live on the "
                   "real 481-gen ledger (not the stored verdict) FIRES under the "
                   "honest-promotion contract (streak 481/481, menu constant, search "
                   "alive: mutation_viability=1.0, llm_used>0 in 462/481 gens). "
                   "Repro: harmonia/experiments/fp003_apollo_executing_confirm_20260615.py."),
    ),
    mitigation=("Menu-growth / lineage mechanism (Arachne population layer): the "
                "substrate is the lineage, not the single agent "
                "(math_crawlers_epiphany_2026-06-04 §2). Prior art: Erebos ITER-43 "
                "consecutive_zero_growth_run (charon/agents/erebos/_rank_expansion.py) "
                "was independently built as a detector for this exact pattern."),
    void_flag=("ergon-operator-menu", "aporia-attempt-menu",
               "icarus-proposal-menu (adaptation strategies)"),
    independence_status="proven",
    independence_note=(
        "STAGE-2 RULING (2026-06-10, Harmonia E; full audit in session journal): "
        "anchors 1 and 2 are code-disjoint at the failure-relevant path — "
        "Polyhymnia's daemon shell descends from the Aporia agents-swarm template "
        "(Hypatia/Atalanta/Pheme/Talos), not Techne/Theseus; tensor framework "
        "standalone; zero cross-imports; the scour does not even walk techne/. "
        "Promotion machinery shares no symbols (Generator/run_batch/training_weight "
        "vs Scour/run_tick/integrate). Mechanical causes differ (region_empty vs "
        "source_saturated) — heterogeneous causes converging on the same observable "
        "shape STRENGTHENS shape-level invariance. KNOWN RESIDUAL CONTAMINATION: "
        "feedback_gen_30_wall (James's C# gen-30 stall) PREDATES both walls and is "
        "hard-coded in agents/_shared/self_improving.py's docstring, which "
        "Polyhymnia runs; both post-mortems were written by authors who knew the "
        "predicted shape. The diagnosis LANGUAGE is therefore contaminated; the "
        "ruling rests on the mechanical event series (promotion counters, null-tick "
        "counters), which fired independently of narrative. "
        "STAGE-3 RULING (2026-06-15, Harmonia E): the escrowed Apollo anchor is "
        "DE-ESCROWED as a 3rd proven-independent lineage -> FP-003 promotes "
        "surviving_candidate -> COORDINATE_INVARIANT. Audit path (LOCAL, not the "
        "4-probe Workflow the first two anchors got — the Apollo independence is "
        "structural and unambiguous, so a Workflow would be confirmatory not "
        "load-bearing): (1) code-disjointness verified by import analysis — "
        "apollo/src/blackboard_evolve.py imports only blackboard/dataflow_fitness/"
        "blackboard_ops{,_v2,_r2}; it does NOT import the agents/_shared/"
        "self_improving.py mixin that contaminated Polyhymnia, nor theseus/, nor any "
        "Aporia shell. Separate MAP-Elites substrate, distinct founding (Branch C "
        "blackboard prototype). (2) Distinct mechanism: expressiveness_ceiling, a "
        "third subclass alongside region_empty/source_saturated. (3) Narrative-"
        "independence: Apollo's diagnosis is in its OWN type-bridge vocabulary (no "
        "reference to 'FP-003'/'bounded_menu_wall'); the load-bearing evidence is the "
        "event series (best_acc flat 0.42 over 481 gens; the bridge-op experiment "
        "0.42->1.0), narrative-independent on the same standard applied to anchors "
        "1-2. SHARPEST OPEN CRITIQUE (logged, not fatal): Theseus's region_empty is a "
        "TRUTHFUL wall (region genuinely empty -> correct STOP) while Apollo's "
        "expressiveness_ceiling is an ARTIFACT wall (a better organism exists outside "
        "the menu -> correct GROW) — opposite remedies under one observable. Per the "
        "heterogeneous-causes doctrine this strengthens shape-invariance and makes "
        "the detector a triage instrument ('menu wall: now diagnose STOP-vs-GROW'); a "
        "subclass-discriminator probe is owed when spend resets to confirm the "
        "detector cannot be made to over-lump."),
    notes=("Cause-subclass taxonomy (preserves the gradient per "
           "feedback_failure_signature_doctrine): region_empty (menu fully "
           "expresses a genuinely empty region — Theseus; Techne's own log calls "
           "this 'correct refusal', the lumping caveat is acknowledged), "
           "source_saturated (menu exhausted its source — Polyhymnia), "
           "expressiveness_ceiling (menu cannot express anything better than seed; "
           "the better organism is outside the search space — Apollo, CONFIRMED "
           "2026-06-15 via the bridge-op falsification), cause_unattributed. The "
           "detector detects the SHAPE; the subclass is post-detection diagnosis, "
           "and it routes the remedy: region_empty/source_saturated -> STOP (the "
           "wall is truthful); expressiveness_ceiling -> GROW the menu (the wall is "
           "an artifact of an incomplete vocabulary)."),
))

register(FailurePrimitive(
    id="FP-004",
    name="degenerate_field_flatline",
    signature=("A field/channel/coordinate the design declares as VARYING is "
               "degenerate across the whole ledger (<=1 distinct populated value / "
               "never populated / pinned at a bound) despite live upstream writers; "
               "every downstream metric or structure verdict computed on it is "
               "algebraically forced and gets read as a domain finding."),
    detector=detect_degenerate_field_flatline,
    detector_kind="live",
    anchor_cases=(
        AnchorCase("harmonia", "harmonia/memory/architecture/reaudit_killvector_rank1_2026-05-27.md",
                   "2026-05-27", "harmonia",
                   "A correlation matrix over single-component kill vectors is "
                   "algebraically forced to rank-1; the 'rank-1 basis' was an "
                   "instrumentation artifact (all 24k vectors 1-component). Harmonia "
                   "PAID for this retraction — FP-004 generalizes it."),
        AnchorCase("apollo", "harmonia/experiments/hunt_raw_20260610.json",
                   "2026-05-22", "apollo",
                   "9,089 LLM-tagged mutation events but llm_alive in the population "
                   "was 0; every 'LLM lineage' metric computed on it was forced. "
                   "Source: pivot/apollo_investigation_2026-05-22.md."),
        AnchorCase("noesis", "journal/2026-03-31-aletheia-overnight.md",
                   "2026-03-31", "noesis",
                   "182 of 236 hubs (77%) share identical depth-2 confidence "
                   "signatures — a degenerate annotation read as hub structure."),
        AnchorCase("polyhymnia", "harmonia/experiments/hunt_raw_20260610.json",
                   "2026-06-03", "polyhymnia-scour-aporia-shell",
                   "Health composite computed on a dead channel (dead_channel_"
                   "composite): diversity/novelty pinned at 0 feed a 'health' "
                   "verdict. Source: aporia polyhymnia diagnosis."),
    ),
    mitigation=("Per-declared-varying-field entropy/cardinality audit BEFORE any "
                "analysis that consumes the field; second leg: confirm downstream "
                "metric changes under an intervention with a known large upstream "
                "effect (bit-identical metric = flatline). Detector shipped 2026-06-10."),
    void_flag=("ergon-tensor-fields", "icarus-trace-dict-fields",
               "charon-plugin-scorecard-fields", "theseus-record-fields"),
    independence_status="pending",
    independence_note=(
        "GRADUATED from the generative hunt (4 anchors the dedup judge marked "
        "across apollo/harmonia/noesis/polyhymnia). PRIMA-FACIE code-disjoint — "
        "four different top-level codebases, four mechanically distinct instruments "
        "(population counter / correlation-matrix rank / confidence-signature hash / "
        "health composite). But a rigorous FP-003-style lineage audit was NOT run "
        "(blocked by the Anthropic spend limit 2026-06-10), so status stays "
        "'pending' and the tier is held at surviving_candidate, not "
        "coordinate_invariant, until that audit lands. Honest: the detector firing "
        "on Harmonia's OWN paid-for rank-1 retraction is the calibration that earns "
        "trust in the novel anchors."),
    notes=("First shape graduated from the Stage-3 hunt to a live detector — the "
           "anti-taxonomy-theater proof that the atlas grows by detectors that "
           "fire, not prose. Full candidate shelf (89 other shapes, mostly "
           "unaudited shadows): "
           "harmonia/memory/architecture/fp_candidate_shelf_20260610.md."),
))


# ----------------------------------------------------------------------------
# Query API
# ----------------------------------------------------------------------------
def get(fp_id: str) -> FailurePrimitive:
    return REGISTRY[fp_id]


def all_ids() -> list:
    return sorted(REGISTRY.keys())


def coordinate_invariants() -> list:
    return [fp for fp in REGISTRY.values() if fp.coordinate_invariant]


def void_report() -> list:
    """The Mendeleev gaps: (fp_id, target) cells where a detector should run
    but never has. Highest-value audits to schedule next."""
    out = []
    for fp in REGISTRY.values():
        for target in fp.void_flag:
            out.append({"fp": fp.id, "name": fp.name, "target": target,
                        "detector_kind": fp.detector_kind, "tier": fp.tier})
    return out


def validate_atlas(md_path: Path = ATLAS_MD) -> list:
    """Cross-check the human-layer MD against this registry. Returns a list of
    discrepancy strings (empty = clean). Checks: every registry FP appears in
    the MD; every anchor artifact path that looks repo-relative exists; MD
    mentions no FP-NNN id absent from the registry."""
    problems = []
    if not md_path.exists():
        return [f"atlas MD missing: {md_path}"]
    text = md_path.read_text(encoding="utf-8")
    md_ids = set(re.findall(r"\bFP-\d{3}\b", text))
    for fp_id in REGISTRY:
        if fp_id not in md_ids:
            problems.append(f"{fp_id} registered but absent from MD")
    for md_id in md_ids:
        if md_id not in REGISTRY:
            problems.append(f"{md_id} in MD but not registered")
    for fp in REGISTRY.values():
        for a in fp.anchor_cases:
            p = REPO_ROOT / a.artifact
            if not p.exists():
                problems.append(f"{fp.id} anchor artifact missing: {a.artifact}")
    return problems


# ----------------------------------------------------------------------------
# Self-test
# ----------------------------------------------------------------------------
def _selftest() -> None:
    # FP-002 fires on an h2-shaped ledger, not on a differentiated one.
    flat = ["h2_flat"] * 870 + [f"kp_{i % 40}" for i in range(1130)]
    r = detect_opaque_kill_blackhole(flat, min_records=1000)
    assert r.fired and r.evidence["top1"] == "h2_flat", r.headline
    spread = [f"kp_{i % 40}" for i in range(2000)]
    r2 = detect_opaque_kill_blackhole(spread, min_records=1000)
    assert not r2.fired, r2.headline
    # payload-variation downgrade path
    r2b = detect_opaque_kill_blackhole(flat, min_records=1000,
                                       payload_variation=lambda top: True)
    assert not r2b.fired and r2b.evidence["payload_downgrade"], r2b.headline

    # FP-003 fires on a 90-batch tail wall, not on active promotion or churn.
    wall = [3, 1, 2] + [0] * 90
    r3 = detect_bounded_menu_wall(wall, menu_fingerprints=["m1"] * 93)
    assert r3.fired, r3.headline
    alive = [3, 1, 2] + [0] * 10 + [1] + [0] * 5
    r4 = detect_bounded_menu_wall(alive)
    assert not r4.fired, r4.headline
    churn = [3] + [0] * 92
    r5 = detect_bounded_menu_wall(
        churn, menu_fingerprints=["m1"] * 50 + ["m2"] * 43)
    assert not r5.fired and not r5.evidence["menu_constant"], r5.headline

    # FP-001 delegates to the frozen costume_check (fires on a majority-map claim).
    rows = [{"k": f"p{i % 5}", "lbl": f"kp_{i % 5}" if i % 4 else "kp_x",
             "sig": f"s{i}"} for i in range(200)]
    from harmonia.primitives.baseline_costume import marginal_majority
    claim = marginal_majority(rows, key_fn=lambda r: r["k"],
                              label_fn=lambda r: r["lbl"])
    r6 = detect_baseline_costume(claim, rows, key_fn=lambda r: r["k"],
                                 label_fn=lambda r: r["lbl"])
    assert r6.fired, r6.headline

    # FP-004 fires on a flatlined declared-varying field; not on a real one.
    dead = [{"gen": i, "llm_alive": 0, "acc": (i % 7) / 7.0} for i in range(50)]
    r7 = detect_degenerate_field_flatline(dead, "llm_alive", writer_events=9089)
    assert r7.fired and r7.evidence["writers_contradict"], r7.headline
    r8 = detect_degenerate_field_flatline(dead, "acc")
    assert not r8.fired, r8.headline  # acc genuinely varies
    r9 = detect_degenerate_field_flatline(dead[:5], "llm_alive")
    assert not r9.fired and r9.evidence["insufficient_volume"], r9.headline

    # Admission: verdict-line signatures are rejected.
    try:
        register(FailurePrimitive(
            id="FP-999", name="bad", signature="Apollo failed.",
            detector=None, detector_kind="stub",
            anchor_cases=(AnchorCase("x", "y", "2026-01-01", "z"),),
            mitigation="", void_flag=(), independence_status="pending"))
        raise AssertionError("verdict-line signature was admitted")
    except ValueError:
        pass

    # Tier logic: ruthlessness about lineage.
    fp3 = get("FP-003")
    # STAGE-3 (2026-06-15): Apollo anchor de-escrowed as 3rd independent lineage.
    assert fp3.coordinate_invariant, "FP-003 must qualify after Stage-3 de-escrow"
    assert fp3.independent_anchor_count == 3, fp3.independent_anchor_count
    # The escrowed-anchor guard still works: re-escrowing Apollo drops it to 2.
    assert sum(1 for a in fp3.anchor_cases if a.escrow) == 0, "no escrowed anchors remain"
    assert get("FP-001").tier == "surviving_candidate"

    inv = validate_atlas()
    print("failure_primitives v0 self-test PASS;",
          f"{len(REGISTRY)} FPs, {len(void_report())} void cells,",
          f"atlas validation: {'CLEAN' if not inv else inv}")


if __name__ == "__main__":
    _selftest()
