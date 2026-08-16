"""F-null — the identity control arm, and R7's two verification layers.

Spec `pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md` v2.0-FINAL §2 and **R7**; prereg
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` §5.1. Charon's contract (spec §4.1, prereg §7 step 5).

ARM ROLE. F-null is *mismatched* residue — the wrong problem's records, carrying the same
surface statistics. It answers: **does the identity of the residue matter, or would any
residue-shaped text do?** `Δ_carry = F-prom-retrieved − F-null` is the probe's single primary
endpoint (R15), so F-null is the arm the whole experiment rests on. If F-null is
distinguishable, the solver can condition on arm identity and the endpoint is meaningless.

TWO DESIGN COMMITMENTS, both load-bearing:

1. **F-null renders through Techne's assembler, not a renderer of mine.** `assemble_retrieved`
   supplies the header, the R14 firewall, the stratum-keyed verdict redaction, the ceiling and
   the truncation rule. A second renderer would differ in whitespace, key order, or stanza
   wording, and the blinded classifier would win on formatting alone. This is the same argument
   that makes the redactor import the extractor's own regex object: one implementation, no drift.
   A consequence, stated rather than hidden: **the rendered F-null packet carries the same header
   text as F-prom, including the `arm` field.** Arm identity lives in the result object, never in
   the packet — an identity control that announces itself is not a control.

2. **Redaction is inherited, never re-decided.** Because F-null goes through the same assembler
   with the same stratum, D0/D1 F-null gets every verdict token stripped exactly as D0/D1 F-prom
   does, and D2/D3 F-null is left unredacted exactly as D2/D3 F-prom is. Had F-null been redacted
   on a different rule, `[VERDICT-REDACTED]` density would itself have become the distinguishing
   surface feature the classifier is there to catch.

R7 LAYER (a) — twelve marginal-balance checks. The eleven preregistered dimensions, plus one
**declared twelfth**: verdict-token polarity. The D3 pool is 590/620 `holds=False` and zero
`holds=True` (`E3`, 2026-08-16), so a polarity mismatch would hand F-prom a base-rate prime that
F-null lacks — on a task set that is 50/50 by construction. Matching is expected by construction
since both arms draw the same corpus; it is verified rather than assumed. Tolerances are
Charon's to set under R7 and are declared in `TOLERANCES` below.

R7 LAYER (b) — the blinded classifier, `classifier_auc`. A simple model on surface features must
score **≤55%**. Per spec §7, two failed rebuilds ⇒ the experiment as designed is not runnable and
we say so.

— Charon, 2026-08-16.
"""

from __future__ import annotations

import math
import random
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence

from ergon.probe.assemble import (
    RETRIEVED_TOKEN_CEILING,
    ResidueRecord,
    assemble_retrieved,
    count_tokens,
)
from ergon.probe.extract import _VERDICT_TOKEN

ARM = "F-null"
VERSION = "f-null-v1.0"
CLASSIFIER_CEILING = 0.55  # spec R7(b) / §7
MAX_REBUILDS = 2  # spec §7: two rebuilds then INADMISSIBLE

_WORD = re.compile(r"[A-Za-z_]+")
_NUMERIC = re.compile(r"\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
_OBJECT_FAMILY = re.compile(r"\b([a-z_]+):")
_KILL_FAMILY = re.compile(r"^([a-z]\d+)_")
#: `kill_pattern` is not a `ResidueRecord` field — it lives inside the rendered body. Parsing it
#: from the body is also the honest choice: the body is what the solver sees, so it is the
#: surface the balance test is supposed to be about.
_KILL_PATTERN_FIELD = re.compile(r"kill_pattern:\s*(\S+)")


def _kill_pattern_of(r: ResidueRecord) -> Optional[str]:
    m = _KILL_PATTERN_FIELD.search(r.body or "")
    return m.group(1) if m else None


# --------------------------------------------------------------------------- marginals


#: R7(a) tolerances. Charon's to set ("each within preregistered tolerance; Charon owns both").
#: `rel` = relative tolerance on a scalar; `pp` = percentage points; `tvd` = total variation
#: distance between two categorical distributions.
TOLERANCES: dict[str, tuple[str, float]] = {
    "token_count": ("rel", 0.05),  # same ±5% the arms are matched on (prereg §4.5)
    "records_per_packet": ("rel", 0.0),  # exact
    "field_null_rates": ("pp", 5.0),  # per field
    "signature_count": ("rel", 0.10),  # distinct kill_pattern values
    "kill_label_distribution": ("tvd", 0.10),
    "numerical_token_density": ("rel", 0.10),
    "object_family_frequency": ("tvd", 0.15),
    "provenance_window_shape": ("rel", 0.10),  # ledger spread + normalized seq position
    "payload_length": ("rel", 0.10),  # mean chars per record
    "vocabulary_diversity": ("rel", 0.10),  # type-token ratio
    "source_type_distribution": ("tvd", 0.05),
    "verdict_polarity": ("pp", 5.0),  # DECLARED TWELFTH — see module docstring
}


def _tvd(a: Counter, b: Counter) -> float:
    """Total variation distance between two categorical distributions."""
    na, nb = sum(a.values()) or 1, sum(b.values()) or 1
    keys = set(a) | set(b)
    return 0.5 * sum(abs(a[k] / na - b[k] / nb) for k in keys)


def _rel(a: float, b: float) -> float:
    """Symmetric relative difference; 0.0 when both are 0."""
    denom = max(abs(a), abs(b))
    return 0.0 if denom == 0 else abs(a - b) / denom


def _kill_family(kill_pattern: Optional[str]) -> str:
    if not kill_pattern:
        return "<null>"
    m = _KILL_FAMILY.match(kill_pattern)
    return m.group(1) if m else kill_pattern.split("_")[0]


@dataclass
class Marginals:
    """The twelve R7(a) dimensions, computed from records plus their rendered packet."""

    token_count: int
    records_per_packet: int
    field_null_rates: dict[str, float]
    signature_count: int
    kill_label_distribution: Counter
    numerical_token_density: float
    object_family_frequency: Counter
    provenance_window_shape: tuple[float, float]
    payload_length: float
    vocabulary_diversity: float
    source_type_distribution: Counter
    verdict_polarity: float


def measure(records: Sequence[ResidueRecord], packet_text: str) -> Marginals:
    """Compute all twelve marginals. Packet-level dimensions read the rendered text, so they
    measure what the solver actually sees (including redaction, headers and sparsity stanza)."""
    n = max(len(records), 1)
    bodies = [r.body or "" for r in records]
    joined = "\n".join(bodies)

    words = _WORD.findall(packet_text)
    numerics = _NUMERIC.findall(packet_text)
    verdicts = [m.group(1).lower() for m in _VERDICT_TOKEN.finditer(packet_text)]

    null_counts: Counter = Counter()
    for r in records:
        for f in r.null_fields:
            null_counts[f] += 1

    seqs = [r.seq for r in records] or [0]
    ledgers = {r.ledger_id for r in records}
    span = max(seqs) - min(seqs)
    provenance = (len(ledgers) / n, float(span) / max(max(seqs), 1))

    return Marginals(
        token_count=count_tokens(packet_text),
        records_per_packet=len(records),
        field_null_rates={f: 100.0 * c / n for f, c in null_counts.items()},
        signature_count=len({k for k in map(_kill_pattern_of, records) if k}),
        kill_label_distribution=Counter(_kill_family(_kill_pattern_of(r)) for r in records),
        numerical_token_density=len(numerics) / max(len(words) + len(numerics), 1),
        object_family_frequency=Counter(_OBJECT_FAMILY.findall(joined)),
        provenance_window_shape=provenance,
        payload_length=sum(len(b) for b in bodies) / n,
        vocabulary_diversity=len(set(w.lower() for w in words)) / max(len(words), 1),
        source_type_distribution=Counter(r.source for r in records),
        verdict_polarity=(verdicts.count("false") / len(verdicts)) if verdicts else 0.0,
    )


@dataclass
class BalanceCheck:
    dimension: str
    kind: str
    observed: float
    tolerance: float
    passed: bool

    def line(self) -> str:
        flag = "PASS" if self.passed else "FAIL"
        return f"  {flag}  {self.dimension:<28} {self.kind}={self.observed:.4f} (tol {self.tolerance})"


@dataclass
class BalanceReport:
    checks: list[BalanceCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failures(self) -> list[str]:
        return [c.dimension for c in self.checks if not c.passed]

    def render(self) -> str:
        head = f"R7(a) marginal balance — {'PASS' if self.passed else 'FAIL'} "
        head += f"({sum(c.passed for c in self.checks)}/{len(self.checks)} dimensions)"
        return "\n".join([head, *(c.line() for c in self.checks)])


def divergences(prom: Marginals, null: Marginals) -> dict[str, float]:
    """The twelve raw divergence statistics, without any pass/fail judgement."""
    out: dict[str, float] = {}
    rep = BalanceReport()

    def add(dim: str, observed: float) -> None:
        out[dim] = observed

    add("token_count", _rel(prom.token_count, null.token_count))
    add("records_per_packet", _rel(prom.records_per_packet, null.records_per_packet))

    fields = set(prom.field_null_rates) | set(null.field_null_rates)
    worst = max(
        (abs(prom.field_null_rates.get(f, 0.0) - null.field_null_rates.get(f, 0.0)) for f in fields),
        default=0.0,
    )
    add("field_null_rates", worst)

    add("signature_count", _rel(prom.signature_count, null.signature_count))
    add("kill_label_distribution", _tvd(prom.kill_label_distribution, null.kill_label_distribution))
    add("numerical_token_density", _rel(prom.numerical_token_density, null.numerical_token_density))
    add("object_family_frequency", _tvd(prom.object_family_frequency, null.object_family_frequency))
    add(
        "provenance_window_shape",
        max(
            _rel(prom.provenance_window_shape[0], null.provenance_window_shape[0]),
            _rel(prom.provenance_window_shape[1], null.provenance_window_shape[1]),
        ),
    )
    add("payload_length", _rel(prom.payload_length, null.payload_length))
    add("vocabulary_diversity", _rel(prom.vocabulary_diversity, null.vocabulary_diversity))
    add("source_type_distribution", _tvd(prom.source_type_distribution, null.source_type_distribution))
    add("verdict_polarity", 100.0 * abs(prom.verdict_polarity - null.verdict_polarity))
    return out


def check_balance(
    prom: Marginals,
    null: Marginals,
    calibrated: Optional[dict[str, float]] = None,
) -> BalanceReport:
    """R7 layer (a): the twelve dimensions against their tolerances.

    Two tolerance regimes, and the difference matters:

    - **Absolute** (`TOLERANCES`) — hand-set constants. Correct for a *matched* construction,
      where the two arms are supposed to be near-identical and any gap is a construction defect.
    - **Calibrated** (`calibrate_tolerances`) — the 95th percentile of the same divergence
      statistic computed between two disjoint draws from ONE pool. Required for an
      *exchangeable* construction, where the arms are identically distributed by construction
      and every observed gap is sampling noise.

    Build #2 exposed why this distinction is not pedantry: with 25 records over eight-plus kill
    families, two draws from one pool differ by TVD ≈ 0.44 as a matter of course, so the
    hand-set 0.10 tolerance was **below the noise floor** — it was testing whether two samples
    from one distribution look identical, which they never do. A balance test has to be
    calibrated against the divergence a same-distribution pair actually produces, or it is
    measuring the sample size rather than the construction. Same principle as requiring a null
    that perturbs the axis the statistic varies on.
    """
    rep = BalanceReport()
    for dim, observed in divergences(prom, null).items():
        kind, absolute = TOLERANCES[dim]
        tol = absolute if calibrated is None else max(calibrated.get(dim, absolute), absolute)
        rep.checks.append(BalanceCheck(dim, kind, observed, tol, observed <= tol + 1e-12))
    return rep


@dataclass
class BalanceCalibration:
    """The same-distribution reference for R7 layer (a)."""

    thresholds: dict[str, float]
    family_failure_rate: float  # P(at least one of the twelve exceeds its own threshold)
    reps: int
    percentile: float
    seed: int


def calibrate_tolerances(
    pool: Sequence[ResidueRecord],
    *,
    n_records: int,
    tau: dict[str, int],
    stratum: str = "D3",
    seed: int = 0,
    reps: int = 200,
    percentile: float = 95.0,
) -> BalanceCalibration:
    """The same-distribution reference band for every dimension.

    Draws `reps` pairs of disjoint uniform samples from one pool, renders both through the
    production assembler, and returns the `percentile`-th percentile of each divergence
    statistic. That is the divergence two identically-distributed packets actually produce at
    this sample size — the honest floor below which a tolerance is measuring noise.

    Deterministic in `seed`. The resulting numbers are frozen into the R7 report so the
    calibration is auditable rather than re-derived at read time.
    """
    ordered = sorted(pool, key=lambda r: (r.ledger_id, r.seq, r.record_id))
    rng = random.Random(seed)
    collected: dict[str, list[float]] = {}
    for i in range(reps):
        picked = rng.sample(ordered, min(2 * n_records, len(ordered)))
        a, b = picked[:n_records], picked[n_records:]
        pa = assemble_retrieved(task_uid=f"CAL-{i}", stratum=stratum, records=a, tau=tau)
        pb = assemble_retrieved(task_uid=f"CAL-{i}", stratum=stratum, records=b, tau=tau)
        for dim, v in divergences(measure(a, pa.text), measure(b, pb.text)).items():
            collected.setdefault(dim, []).append(v)

    out: dict[str, float] = {}
    for dim, vals in collected.items():
        ordered_vals = sorted(vals)
        idx = min(len(ordered_vals) - 1, int(math.ceil(percentile / 100.0 * len(ordered_vals))) - 1)
        out[dim] = ordered_vals[max(idx, 0)]

    # Family-wise rate: with twelve dimensions each at p95, a large minority of
    # SAME-DISTRIBUTION pairs exceed at least one threshold. Requiring all twelve to pass is a
    # multiple-comparison error, so the gate compares observed failure RATE against this
    # calibrated rate rather than demanding a clean sweep.
    n = len(next(iter(collected.values()))) if collected else 0
    family_failures = sum(
        1 for i in range(n)
        if any(collected[dim][i] > out[dim] + 1e-12 for dim in collected)
    )
    return BalanceCalibration(
        thresholds=out,
        family_failure_rate=(family_failures / n) if n else 0.0,
        reps=reps, percentile=percentile, seed=seed,
    )


# --------------------------------------------------------------------------- selection


def _bucket(r: ResidueRecord) -> tuple:
    """Tightest categorical key: source, the FULL kill pattern, obstruction class, and the
    field-null pattern (R6's warts are part of the surface and must be reproduced).

    Build #1 keyed on the kill *family* (`a1`, `f4`, …) rather than the full pattern, and
    `signature_count` — distinct kill patterns per packet — failed in 11/40 pairs as a result.
    The full pattern is the surface the solver reads, so it is the surface to match on."""
    return (r.source, _kill_pattern_of(r), r.obstruction_class, tuple(sorted(r.null_fields)))


def _loose_bucket(r: ResidueRecord) -> tuple:
    """Fallback key when the tight bucket is exhausted."""
    return (r.source, _kill_family(_kill_pattern_of(r)), r.obstruction_class)


def _surface_key(r: ResidueRecord, max_seq: int) -> tuple[float, float, float]:
    """The three continuous quantities a categorical match does NOT pin down."""
    body = r.body or ""
    return (float(len(body)), float(sum(c.isdigit() for c in body)), r.seq / max(max_seq, 1))


#: Which construction each stratum uses, and why. THIS IS THE CENTRAL DESIGN DECISION OF F-NULL.
#:
#: `matched` — F-prom is TASK-LINKED at this stratum (D0 = the task's own pre-pass record, D1 =
#:   its siblings, D2 = mechanism-tag neighbours). A task-linked draw is a *biased* subsample of
#:   the corpus, so an unmatched control would differ in distribution and the classifier would
#:   find it. Bucket + surface matching is required, and earns its cost.
#:
#: `exchangeable` — F-prom is NOT task-linked at D3: `assemble.select_residue(stratum="D3")`
#:   takes no target argument, so F-prom-D3 is itself a draw from the whole eligible pool. When
#:   both arms can be drawn uniformly from ONE pool, exchangeability is exact by construction and
#:   strictly dominates any matching heuristic.
#:
#: This was learned the hard way and the failures are on the record (`charon/probe/
#: R7_CONSTRUCTION_2026-08-16.md`). Build #0 matched categorically and drifted on token and digit
#: counts (classifier 0.575). Build #1 added nearest-neighbour surface matching and got *worse*
#: (0.662), because nearest-matching against a finite pool is regression to the mean: F-null
#: could not reach F-prom's tail draws, so the control came out systematically less extreme.
#: **A matching heuristic can manufacture the very signature it is meant to remove.** Where
#: exchangeability is available, take it.
STRATEGY_BY_STRATUM: dict[str, str] = {
    "D0": "matched",
    "D1": "matched",
    "D2": "matched",
    "D3": "exchangeable",
}


def select_mismatched(
    prom_records: Sequence[ResidueRecord],
    pool: Sequence[ResidueRecord],
    *,
    seed: int,
    exclude_uids: Iterable[str] = (),
    strategy: str = "matched",
) -> list[ResidueRecord]:
    """Pick a disjoint set of records for F-null, by the stratum's strategy.

    Disjointness is enforced on `record_id`, and additionally on `uid` for any task-linked
    residue: F-null must be the WRONG problem's residue, so nothing sharing the target's uid may
    enter. Both strategies are seeded and quality-blind — records are never ranked by anything
    but surface similarity, so the control cannot be accidentally built from the good half of
    the corpus.
    """
    used = {r.record_id for r in prom_records}
    banned = set(exclude_uids)
    available = [
        r for r in pool
        if r.record_id not in used and not (r.uid is not None and str(r.uid) in banned)
    ]
    if not available:
        return []

    if strategy == "exchangeable":
        # Both arms are uniform draws from one pool, so they are identically distributed BY
        # CONSTRUCTION — a guarantee no matching heuristic can equal. See STRATEGY_BY_STRATUM.
        ordered = sorted(available, key=lambda r: (r.ledger_id, r.seq, r.record_id))
        k = min(len(prom_records), len(ordered))
        return random.Random(seed).sample(ordered, k)

    max_seq = max((r.seq for r in available), default=1)
    # Deterministic base order; the seed only breaks ties among equally-good candidates, so the
    # draw stays quality-blind — records are never ranked by anything but surface similarity.
    available.sort(key=lambda r: (r.ledger_id, r.seq, r.record_id))
    random.Random(seed).shuffle(available)

    # Scales for the surface distance, from the pool itself, so the three terms are commensurate.
    keys = [_surface_key(r, max_seq) for r in available]
    scales = [max((abs(k[i]) for k in keys), default=1.0) or 1.0 for i in range(3)]

    def distance(a: ResidueRecord, b: ResidueRecord) -> float:
        ka, kb = _surface_key(a, max_seq), _surface_key(b, max_seq)
        return sum(abs(ka[i] - kb[i]) / scales[i] for i in range(3))

    remaining = list(available)
    chosen: list[ResidueRecord] = []
    for want in prom_records:
        # Progressively looser candidate sets; within each, the nearest on the continuous
        # surface. Build #1 matched categorically and let length, digit count and provenance
        # drift — each individually inside its per-pair tolerance, but all biased the same way,
        # which is what the blinded classifier found at 0.575.
        for candidates in (
            [r for r in remaining if _bucket(r) == _bucket(want)],
            [r for r in remaining if _loose_bucket(r) == _loose_bucket(want)],
            remaining,
        ):
            if candidates:
                pick = min(candidates, key=lambda r: distance(r, want))
                remaining.remove(pick)
                chosen.append(pick)
                break

    return chosen


@dataclass
class NullPacket:
    packet: object  # assemble.Packet — rendered by Techne's assembler, not by this module
    records: list[ResidueRecord]
    balance: BalanceReport
    seed: int
    version: str = VERSION

    @property
    def text(self) -> str:
        return self.packet.text  # type: ignore[attr-defined]

    @property
    def admissible(self) -> bool:
        return self.balance.passed


def build_f_null(
    *,
    task_uid: str,
    stratum: str,
    prom_records: Sequence[ResidueRecord],
    prom_packet_text: str,
    pool: Sequence[ResidueRecord],
    tau: dict[str, int],
    seed: int,
    exclude_uids: Iterable[str] = (),
    ceiling: int = RETRIEVED_TOKEN_CEILING,
    excluded_transport_failures: int = 0,
    sampling_note: str = "full-scan",
    strategy: Optional[str] = None,
    calibrated: Optional[dict[str, float]] = None,
) -> NullPacket:
    """Build one F-null packet for `task_uid`, matched to that task's F-prom packet.

    Rendering is delegated to `assemble_retrieved`, so the firewall, the stratum-keyed redaction,
    the ceiling and every header field are the same code path F-prom takes.
    """
    strategy = strategy or STRATEGY_BY_STRATUM.get(stratum, "matched")
    records = select_mismatched(
        prom_records, pool, seed=seed, exclude_uids=exclude_uids, strategy=strategy
    )
    packet = assemble_retrieved(
        task_uid=task_uid,
        stratum=stratum,
        records=records,
        tau=tau,
        ceiling=ceiling,
        excluded_transport_failures=excluded_transport_failures,
        sampling_note=sampling_note,
    )
    kept = {rid for rid in packet.header["source_record_ids"]}
    shipped = [r for r in records if f"{r.ledger_id}#{r.seq}" in kept]
    balance = check_balance(
        measure(prom_records, prom_packet_text), measure(shipped, packet.text), calibrated
    )
    return NullPacket(packet=packet, records=shipped, balance=balance, seed=seed)


# --------------------------------------------------------------------------- R7 layer (b)


#: Surface features only — nothing semantic. If a model can separate the arms on these, the
#: packets differ in a way a solver could also condition on.
def surface_features(text: str) -> list[float]:
    words = _WORD.findall(text)
    numerics = _NUMERIC.findall(text)
    lower = [w.lower() for w in words]
    chars = len(text) or 1
    nw = len(words) or 1
    return [
        float(count_tokens(text)),
        float(chars),
        float(nw),
        len(numerics) / nw,
        len(set(lower)) / nw,
        sum(len(w) for w in words) / nw,
        text.count("\n") / chars * 1000,
        sum(c.isdigit() for c in text) / chars,
        sum(c in ".,;:|()[]{}" for c in text) / chars,
        sum(c.isupper() for c in text) / chars,
        float(len(_VERDICT_TOKEN.findall(text))),
        float(text.count("(not recorded:")),
        float(text.count("_")) / chars * 1000,
        float(len(set(_OBJECT_FAMILY.findall(text)))),
    ]


@dataclass
class ClassifierReport:
    score: float
    ceiling: float
    n_prom: int
    n_null: int
    folds: int
    passed: bool
    note: str = ""

    def render(self) -> str:
        flag = "PASS" if self.passed else "FAIL"
        return (
            f"R7(b) blinded classifier — {flag}  balanced accuracy {self.score:.3f} "
            f"(ceiling {self.ceiling:.2f}, n={self.n_prom}+{self.n_null}, {self.folds}-fold)"
            + (f"\n  {self.note}" if self.note else "")
        )


def classifier_auc(
    prom_texts: Sequence[str],
    null_texts: Sequence[str],
    *,
    seed: int = 0,
    folds: int = 5,
) -> ClassifierReport:
    """R7 layer (b). Cross-validated balanced accuracy of a simple model on surface features.

    Balanced accuracy, not raw accuracy: with unequal arm counts a majority-class predictor
    scores above 50% on raw accuracy and would pass a 55% ceiling while being no evidence at all.
    A logistic regression on standardized surface features is the "simple model" R7 asks for —
    strong enough that a real formatting tell will be found, simple enough that beating chance
    means a genuine linear separation rather than a memorized fold.
    """
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X = np.array([surface_features(t) for t in (*prom_texts, *null_texts)], dtype=float)
    y = np.array([1] * len(prom_texts) + [0] * len(null_texts))
    n_min = int(min(np.bincount(y)))
    if n_min < 2:
        return ClassifierReport(0.5, CLASSIFIER_CEILING, len(prom_texts), len(null_texts), 0,
                                True, "insufficient samples; test not evidential")

    k = max(2, min(folds, n_min))
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed))
    cv = StratifiedKFold(n_splits=k, shuffle=True, random_state=seed)
    score = float(cross_val_score(model, X, y, cv=cv, scoring="balanced_accuracy").mean())
    return ClassifierReport(
        score, CLASSIFIER_CEILING, len(prom_texts), len(null_texts), k, score <= CLASSIFIER_CEILING
    )


def r7_verdict(
    balance: Iterable[BalanceReport],
    classifier: ClassifierReport,
    rebuilds: int,
    calibration: Optional[BalanceCalibration] = None,
) -> str:
    """The R7 gate, as spec §7 defines it — and only as it defines it.

    Spec §7's kill condition is specific: *"R7 classifier beats 55% after two F-null rebuilds ⇒
    experiment as designed not runnable."* It is keyed on the **classifier**. A layer-(a) miss is
    a balance defect to be fixed, not the experiment's death, and conflating the two would let a
    tolerance I set myself declare the program unrunnable.

    Layer (a) is judged on the observed family-wise failure RATE against the calibrated
    same-distribution rate, never on a clean sweep of all twelve dimensions.
    """
    reports = list(balance)
    observed_rate = (sum(not b.passed for b in reports) / len(reports)) if reports else 0.0
    layer_a = (
        all(b.passed for b in reports) if calibration is None
        else observed_rate <= calibration.family_failure_rate + 1e-12
    )
    if not classifier.passed and rebuilds >= MAX_REBUILDS:
        return "INADMISSIBLE-EXPERIMENT-AS-DESIGNED-NOT-RUNNABLE"
    if not classifier.passed:
        return "R7-FAIL-CLASSIFIER-REBUILD-REQUIRED"
    if not layer_a:
        return "R7-FAIL-BALANCE-REBUILD-REQUIRED"
    return "R7-PASS"


__all__ = [
    "ARM", "VERSION", "CLASSIFIER_CEILING", "MAX_REBUILDS", "TOLERANCES",
    "Marginals", "measure", "BalanceReport", "check_balance",
    "select_mismatched", "NullPacket", "build_f_null", "STRATEGY_BY_STRATUM",
    "divergences", "calibrate_tolerances", "BalanceCalibration",
    "surface_features", "ClassifierReport", "classifier_auc", "r7_verdict",
]
