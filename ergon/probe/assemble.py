"""Packet assembler for `F-prom-retrieved` and `F-prom-whole` (Techne, supplier contract).

Contract: `stations/M1_STATUS.md` §7b · spec `pivot/SPEC_METABOLIZATION_PROBE_2026-08-12.md`
§4.4 (packet spec), R6 (honest assembly), R14 (provenance firewall) · prereg
`pivot/PREREG_METABOLIZATION_PROBE_v1.md` §4.2 (rep-1 rule), §4.3 (D-tagging), §4.4 (cutoff
vector), §4.5 (verdict redaction, token ceiling).

Four things in this module are load-bearing and fail loud rather than warn:

  * VERDICT REDACTION (prereg §4.5, adopted from Hephaestus review M1 and strengthened).
    Every verdict token is stripped from rendered D0/D1 packets — not just the terminal one,
    because traces restate their conclusion mid-stream. The strip uses the extractor's own
    frozen regex (`extract._VERDICT_TOKEN`) so redactor and scorer cannot drift apart:
    anything the scorer would read as a verdict is exactly what the redactor removes.
    Over-stripping is accepted and stated — that error direction can only SHRINK D0/D1 Δ.

  * REP-1 ENFORCEMENT (prereg §4.2, from review C1). Only the rep-1 pre-pass record may be
    rendered. Enforced by `rep == 1` mechanically, at load AND again at assembly, because an
    assembler free to choose between reps could select on a trace property correlated with
    correctness — a selection effect on exactly the axis the probe measures.

  * R14 PROVENANCE FIREWALL. Delegated to `schema.assert_packet_provenance` (already written
    and tested by Ergon); this module supplies the cutoff vector and re-stamps it into every
    header. Wall-clock is unusable (M3 CMOS reset), so ledger append-order is the honest clock.

  * APOLLO WALL QUARANTINE (`apollo/wall_corpus/MANIFEST.md` §1). `answer_content`,
    `ablation_applied` and `failure_class` are quarantined; only `wall_id`, `wall_signature`
    and `oracle_diagnosis` may ship. Validator-enforced on Apollo's side; asserted again here
    so a packet cannot carry them even if a caller passes a raw record.

R6 posture, stated once: this assembler ships what the substrate actually recorded — null
`kill_pattern`s, absent `kill_vector`s, transport-failure scraps, thin one-line classes. Where
a stratum has nothing, the packet says so in a SPARSITY stanza and the caller gets a census
saying so too. There is no hand-enrichment and no filtering on any property correlated with
quality or correctness. The only exclusions are TYPE-based and named: gold-derived records
(R14), rep-2 records (§4.2), quarantined Apollo fields (MANIFEST §1), and — as a flagged
judgement call the owner may overrule — infrastructure-transport scraps (see
`INCLUDE_TRANSPORT_FAILURES`).
"""
from __future__ import annotations

import dataclasses
import gzip
import hashlib
import json
import pathlib
import re
import sqlite3
from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator, Optional, Sequence

from .extract import _VERDICT_TOKEN  # the frozen regex — reused, never re-declared
from .schema import FirewallViolation, assert_packet_provenance

# --------------------------------------------------------------------------- frozen constants

ASSEMBLY_VERSION = "techne-assemble/v1.0.0"

#: prereg §4.5, literal.
REDACTION_PLACEHOLDER = "[VERDICT-REDACTED]"

#: prereg §4.5. F-prom-retrieved ceiling; other packeted arms match per task within ±5%.
RETRIEVED_TOKEN_CEILING = 8_000

#: prereg §4.5. F-prom-whole is capped at solver context minus this fraction.
WHOLE_CONTEXT_HEADROOM = 0.20

#: prereg §2 — the frozen seed. Used only for deterministic ordering tie-breaks, never for
#: quality-correlated selection.
PREREG_SEED = 20260813

#: prereg §4.3, fixed mechanism tags for D2.
MECHANISM_TAGS = (
    "exact-large-integer-arithmetic",
    "divisor-or-factor-search",
    "gcd-computation",
    "modular-reduction",
    "square-detection",
    "magnitude-comparison",
    "closed-form-formula-application",
)

#: prereg §4.3, obstruction classes for D3.
OBSTRUCTION_CLASSES = (
    "asserted-equality-without-executing-computation",
    "surface-plausible-arithmetically-false",
    "near-miss-margin-below-threshold",
)

#: prereg §4.3 — the probe's seven domains mapped onto mechanism tags. Fixed here, by
#: construction, so D2 selection is never a post-hoc judgement.
DOMAIN_MECHANISM_TAGS: dict[str, tuple[str, ...]] = {
    "ood_primality": ("divisor-or-factor-search", "exact-large-integer-arithmetic"),
    "ood_coprime": ("gcd-computation", "divisor-or-factor-search"),
    "ood_divisibility": ("divisor-or-factor-search", "modular-reduction"),
    "ood_perfect_square": ("square-detection", "exact-large-integer-arithmetic"),
    "ood_summation": ("closed-form-formula-application", "exact-large-integer-arithmetic"),
    "ood_modular": ("modular-reduction", "exact-large-integer-arithmetic"),
    "ood_inequality": ("magnitude-comparison", "exact-large-integer-arithmetic"),
}

#: Apollo `wall_corpus/MANIFEST.md` §1 — validator-enforced on Apollo's side, re-asserted here.
WALL_SHIPPABLE = ("wall_id", "wall_signature", "oracle_diagnosis")
WALL_QUARANTINED = ("answer_content", "ablation_applied", "failure_class", "provenance",
                    "separability")

#: Forge-ledger `reason` prefixes that denote a TRANSPORT/infrastructure outcome rather than a
#: mathematical or validation obstruction. Excluding these is a TYPE-based rule (parallel to
#: R14's gold-derived exclusion), NOT a quality filter — but it IS a judgement call, so it is
#: a flag, the census reports both ways, and the decision is the owner's (R12).
TRANSPORT_FAILURE_REASONS = ("api_call_failed",)
INCLUDE_TRANSPORT_FAILURES = False

# --------------------------------------------------------------------------- token accounting

#: A frozen, dependency-free, deterministic counter. `tiktoken` is not installed on M1 and a
#: HF tokenizer would make packet size depend on a downloaded artifact, so the ceiling is
#: enforced against THIS function everywhere. What matters for the ±5% per-task arm matching
#: is that every arm is measured by the SAME function — the same argument that makes the
#: redactor reuse the extractor's regex. Drift against real API `prompt_tokens` is measurable
#: after the fact (ProbeRecord carries both `packet_tokens` and `prompt_tokens`) and is a
#: reportable diagnostic, not a silent assumption.
TOKEN_COUNT_METHOD = "frozen-regex-approx/v1 (word|number|punct pieces, chars/4 floor)"

_TOKEN_PIECE = re.compile(r"[A-Za-z]+|\d|[^\sA-Za-z\d]")


def count_tokens(text: str) -> int:
    """Deterministic, conservative token estimate. Same input -> same output, forever."""
    pieces = len(_TOKEN_PIECE.findall(text))
    return max(pieces, -(-len(text) // 4))


# --------------------------------------------------------------------------- redaction


def redact_verdict_tokens(text: str) -> str:
    """Strip EVERY verdict token, replacing each with the prereg's literal placeholder.

    prereg §4.5, adopted-and-strengthened from Hephaestus review M1. Deliberately applied to
    the whole rendered packet rather than a terminal token: reasoning traces routinely restate
    their conclusion mid-stream ("...so they share a factor, therefore False"), and a
    terminal-only strip leaves that intact. Uses the extractor's own frozen regex.
    """
    return _VERDICT_TOKEN.sub(REDACTION_PLACEHOLDER, text)


def leaks_verdict(text: str) -> bool:
    """True if any token the scorer would read as a verdict survives. Redactor/scorer parity."""
    return bool(_VERDICT_TOKEN.search(text))


# --------------------------------------------------------------------------- residue records


@dataclass(frozen=True)
class ResidueRecord:
    """One residue item eligible for a packet. `ledger_id`/`seq` are the R14 clock."""

    ledger_id: str
    seq: int
    source: str  # probe_prepass | theseus_corpus | hephaestus_forge | signature_index
    record_id: str
    body: str  # the rendered residue text, pre-redaction
    derives_from_gold: bool = False
    uid: Optional[str] = None
    domain: Optional[str] = None
    rep: Optional[int] = None
    mechanism_tags: tuple[str, ...] = ()
    obstruction_class: Optional[str] = None
    null_fields: tuple[str, ...] = ()  # fields the substrate did NOT record (R6)
    sampling: str = "full-scan"

    def provenance_triple(self) -> tuple[str, int, bool]:
        return (self.ledger_id, self.seq, self.derives_from_gold)

    def render(self) -> str:
        head = f"[{self.source}:{self.record_id} {self.ledger_id}#{self.seq}]"
        lines = [head, self.body.rstrip()]
        if self.null_fields:
            lines.append(f"  (not recorded: {', '.join(self.null_fields)})")
        return "\n".join(lines)


# --------------------------------------------------------------------------- loaders


def _jsonl_lines(path: pathlib.Path) -> Iterator[tuple[int, dict[str, Any]]]:
    """Yield (1-based line index, record). Line index IS the append-order clock for a JSONL
    ledger — wall-clock is unusable (R14), and an append-only file's order is its sequence."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:  # type: ignore[operator]
        for i, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield i, json.loads(line)
            except json.JSONDecodeError:
                continue


def load_prepass(path: pathlib.Path, *, ledger_id: str = "probe_prepass") -> list[ResidueRecord]:
    """D0/D1 source. REP-1 ONLY, enforced mechanically (prereg §4.2, review C1).

    The pre-pass ledger does not exist until the pre-pass runs; an absent file yields an empty
    pool, and the caller's census then reports the stratum as unsupplied rather than inventing
    residue for it.
    """
    if not path.exists():
        return []
    out: list[ResidueRecord] = []
    for seq, d in _jsonl_lines(path):
        if int(d.get("rep", -1)) != 1:
            continue  # rep-2 exists for the contamination screen only; never packet-eligible
        if bool(d.get("derives_from_gold", False)):
            continue  # type-based exclusion, belt-and-braces before the firewall sees it
        for forbidden in ("gold", "gold_bool", "correct", "grader_output"):
            if forbidden in d:
                raise FirewallViolation(
                    f"pre-pass record {d.get('uid')!r} carries {forbidden!r}; "
                    "gold/correctness must not enter the residue record (prereg §4.2)"
                )
        trace = str(d.get("attempt_text") or d.get("trace") or "").strip()
        null_fields = tuple(f for f in ("attempt_text", "diagnosis") if not d.get(f))
        body = trace if trace else "(no attempt text recorded)"
        if d.get("diagnosis"):
            body += f"\n  diagnosis: {d['diagnosis']}"
        out.append(
            ResidueRecord(
                ledger_id=str(d.get("ledger_id", ledger_id)),
                seq=int(d.get("seq", seq)),
                source="probe_prepass",
                record_id=str(d.get("record_id") or d.get("uid") or seq),
                body=body,
                uid=d.get("uid"),
                domain=d.get("domain"),
                rep=1,
                mechanism_tags=DOMAIN_MECHANISM_TAGS.get(str(d.get("domain")), ()),
                null_fields=null_fields,
            )
        )
    return out


def _obstruction_for_theseus(rec: dict[str, Any]) -> Optional[str]:
    """Map a REJECTED Theseus record onto a prereg §4.3 obstruction class, by construction."""
    kind = str(rec.get("claim_kind") or "")
    kp = str(rec.get("kill_pattern") or "")
    if kind in ("invariant_equality", "functional_identity", "closure_under_operation"):
        return "asserted-equality-without-executing-computation"
    if "below_threshold" in kp or "margin" in kp:
        return "near-miss-margin-below-threshold"
    if kind in ("statistical_correlation", "distribution_match", "ratio_invariance"):
        return "surface-plausible-arithmetically-false"
    return None


def load_theseus_rejected(
    batch_path: pathlib.Path,
    *,
    claim_kinds: Optional[Sequence[str]] = None,
    max_records: Optional[int] = None,
    sampling: str = "full-scan",
) -> list[ResidueRecord]:
    """D3 source: Theseus REJECTED corpus records. One batch file = one ledger; the line index
    is its append order. `kill_pattern` nulls ship as nulls (R6)."""
    out: list[ResidueRecord] = []
    ledger_id = batch_path.name.split(".")[0]
    for seq, d in _jsonl_lines(batch_path):
        if str(d.get("verdict")) != "REJECTED":
            continue
        if claim_kinds and str(d.get("claim_kind")) not in claim_kinds:
            continue
        null_fields = tuple(
            f for f in ("kill_pattern", "kill_vector", "step_trace", "precision_dps", "method")
            if d.get(f) in (None, "", [])
        )
        body_lines = [f"  claim: {d.get('canonical_claim_text', '(not recorded)')}"]
        body_lines.append(f"  kind: {d.get('claim_kind', '(not recorded)')}")
        body_lines.append(f"  kill_pattern: {d.get('kill_pattern') or '(null)'}")
        if d.get("method"):
            body_lines.append(f"  method: {d['method']}")
        if d.get("step_trace"):
            body_lines.append(f"  trace: {d['step_trace']}")
        out.append(
            ResidueRecord(
                ledger_id=str(d.get("batch_id") or ledger_id),
                seq=seq,
                source="theseus_corpus",
                record_id=str(d.get("record_id", seq))[:16],
                body="\n".join(body_lines),
                domain=str(d.get("generator_id") or "theseus"),
                obstruction_class=_obstruction_for_theseus(d),
                null_fields=null_fields,
                sampling=sampling,
            )
        )
        if max_records and len(out) >= max_records:
            break
    return out


def load_forge_scraps(
    path: pathlib.Path,
    *,
    include_transport_failures: bool = INCLUDE_TRANSPORT_FAILURES,
    ledger_id: str = "hephaestus_forge",
) -> list[ResidueRecord]:
    """D3 source: forge-ledger scraps with failure reasons (Hephaestus, committed a3e9bbee).

    Line index is the append clock. Transport failures are excluded by TYPE by default and the
    exclusion is reported; see `INCLUDE_TRANSPORT_FAILURES`.
    """
    if not path.exists():
        return []
    out: list[ResidueRecord] = []
    for seq, d in _jsonl_lines(path):
        if str(d.get("status")) != "scrap":
            continue
        reason = str(d.get("reason") or "")
        is_transport = any(reason.startswith(p) for p in TRANSPORT_FAILURE_REASONS)
        if is_transport and not include_transport_failures:
            continue
        null_fields = tuple(f for f in ("reason",) if not d.get(f))
        body = (
            f"  combination: {d.get('key', '(not recorded)')}\n"
            f"  failure_reason: {reason or '(null)'}\n"
            f"  accuracy: {d.get('accuracy')} calibration: {d.get('calibration')}"
        )
        obstruction = (
            "near-miss-margin-below-threshold"
            if reason.startswith("trap_battery_failed")
            else "asserted-equality-without-executing-computation"
            if reason.startswith("validation:")
            else None
        )
        out.append(
            ResidueRecord(
                ledger_id=ledger_id,
                seq=seq,
                source="hephaestus_forge",
                record_id=hashlib.sha256(str(d.get("key", seq)).encode()).hexdigest()[:12],
                body=body,
                domain="forge",
                obstruction_class=obstruction,
                null_fields=null_fields,
            )
        )
    return out


def load_signature_classes(
    path: pathlib.Path,
    *,
    verdict_classes: Sequence[str] = ("KILL",),
    claim_kinds: Optional[Sequence[str]] = None,
    ledger_id: str = "signature_index",
) -> list[ResidueRecord]:
    """D3 source / F-prom-whole prefix: `signature_index` shape-classes.

    `rowid` is the table's insertion order and therefore the honest append clock; the stored
    `first_seen_at` / `last_seen_at` are wall-clock and unusable under R14.

    NOTE (R6, reported not resolved): this table's `verdict_class` vocabulary is
    KILL/CONFIRM/UNVERIFIED/INCONCLUSIVE — there is no `REJECTED` class here, though prereg
    §4.3 names "Theseus `invariant_equality` REJECTED records" as a D3 source. REJECTED lives
    in the corpus batch records (`load_theseus_rejected`); this index is the shape-class view.
    Both are shipped, labelled by source, and the discrepancy is filed for the owner.
    """
    if not path.exists():
        return []
    out: list[ResidueRecord] = []
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        sql = (
            "SELECT rowid, signature, generator_id, verdict_class, claim_kind, seen_count "
            "FROM signatures WHERE verdict_class IN (%s)"
            % ",".join("?" * len(verdict_classes))
        )
        params: list[Any] = list(verdict_classes)
        if claim_kinds:
            sql += " AND claim_kind IN (%s)" % ",".join("?" * len(claim_kinds))
            params += list(claim_kinds)
        sql += " ORDER BY rowid"
        for rowid, sig, gen, vclass, kind, seen in con.execute(sql, params):
            out.append(
                ResidueRecord(
                    ledger_id=ledger_id,
                    seq=int(rowid),
                    source="signature_index",
                    record_id=str(rowid),
                    body=(
                        f"  signature: {sig}\n"
                        f"  class: {vclass}  kind: {kind}  generator: {gen}  seen: {seen}"
                    ),
                    domain=str(gen),
                    obstruction_class=_obstruction_for_theseus({"claim_kind": kind}),
                )
            )
    finally:
        con.close()
    return out


def load_wall_oracles(corpus_path: pathlib.Path) -> list[dict[str, str]]:
    """Apollo Tier-A walls, F-oracle-shippable fields ONLY (`MANIFEST.md` §1).

    Quarantined fields are dropped here and asserted absent at render time, so a caller cannot
    ship them by passing a raw record.
    """
    if not corpus_path.exists():
        return []
    out = []
    for _seq, d in _jsonl_lines(corpus_path):
        out.append({k: str(d.get(k, "")) for k in WALL_SHIPPABLE})
    return out


def assert_wall_quarantine(rendered: str, raw_records: Iterable[dict[str, Any]]) -> None:
    """Fail loud if any quarantined Apollo value reached a rendered packet (MANIFEST §1)."""
    for rec in raw_records:
        for qfield in WALL_QUARANTINED:
            val = rec.get(qfield)
            if val in (None, "", {}, []):
                continue
            needle = json.dumps(val) if isinstance(val, (dict, list)) else str(val)
            if needle and needle in rendered:
                raise FirewallViolation(
                    f"quarantined Apollo field {qfield!r} reached the rendered packet "
                    f"(wall {rec.get('wall_id')!r}); MANIFEST §1 permits only {WALL_SHIPPABLE}"
                )


# --------------------------------------------------------------------------- packets


@dataclass
class SparsityReport:
    """R6: what the substrate did NOT record, shipped inside the packet."""

    records_shipped: int
    null_field_counts: dict[str, int] = field(default_factory=dict)
    strata_unsupplied: tuple[str, ...] = ()
    excluded_transport_failures: int = 0

    def render(self) -> str:
        lines = ["SPARSITY (what the substrate did not record — shipped as measured):"]
        if not self.records_shipped:
            lines.append("  no residue exists at this distance for this task.")
        for f, n in sorted(self.null_field_counts.items()):
            pct = 100.0 * n / max(self.records_shipped, 1)
            lines.append(f"  {f}: absent in {n}/{self.records_shipped} records ({pct:.1f}%)")
        for s in self.strata_unsupplied:
            lines.append(f"  {s}: NOT-RUN-FOR-LACK-OF-RESIDUE (no eligible records)")
        if self.excluded_transport_failures:
            lines.append(
                f"  excluded by type: {self.excluded_transport_failures} transport-failure "
                "scraps (infrastructure outcome, no mathematical obstruction recorded)"
            )
        return "\n".join(lines)


@dataclass
class Packet:
    header: dict[str, Any]
    body: str

    @property
    def text(self) -> str:
        return (
            "=== PROMETHEUS RESIDUE PACKET ===\n"
            + json.dumps(self.header, sort_keys=True, ensure_ascii=False, indent=1)
            + "\n=== RESIDUE ===\n"
            + self.body
        )

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def _order(records: Sequence[ResidueRecord]) -> list[ResidueRecord]:
    """Deterministic, quality-blind ordering: ledger then append-order then record id."""
    return sorted(records, key=lambda r: (r.ledger_id, r.seq, r.record_id))


def select_residue(
    records: Sequence[ResidueRecord],
    *,
    stratum: str,
    target_uid: Optional[str] = None,
    target_domain: Optional[str] = None,
    generator_of: Optional[dict[str, str]] = None,
) -> list[ResidueRecord]:
    """D-tagging by construction (prereg §4.3). No post-hoc judgement, no quality signal."""
    gen = generator_of or {}
    if stratum == "D0":
        out = [r for r in records if r.source == "probe_prepass" and r.uid == target_uid]
    elif stratum == "D1":
        out = [
            r for r in records
            if r.source == "probe_prepass"
            and r.uid != target_uid
            and r.domain == target_domain
            and gen.get(str(r.uid), r.domain or "") == gen.get(str(target_uid), target_domain or "")
        ]
    elif stratum == "D2":
        tags = set(DOMAIN_MECHANISM_TAGS.get(str(target_domain), ()))
        out = [
            r for r in records
            if r.domain != target_domain and tags.intersection(r.mechanism_tags)
        ]
    elif stratum == "D3":
        out = [
            r for r in records
            if r.source in ("theseus_corpus", "hephaestus_forge", "signature_index")
            and r.obstruction_class is not None
        ]
    else:
        raise ValueError(f"unknown stratum {stratum!r}")
    return _order(out)


def assemble_retrieved(
    *,
    task_uid: str,
    stratum: str,
    records: Sequence[ResidueRecord],
    tau: dict[str, int],
    ceiling: int = RETRIEVED_TOKEN_CEILING,
    excluded_transport_failures: int = 0,
    sampling_note: str = "full-scan",
) -> Packet:
    """Assemble one `F-prom-retrieved` packet. Deterministic, stamped, firewalled, redacted.

    Order of operations is deliberate: firewall -> render -> redact -> count -> truncate ->
    re-verify. Redaction happens BEFORE the token count so the ceiling is enforced against the
    text the solver actually sees.
    """
    if stratum not in ("D0", "D1", "D2", "D3"):
        raise ValueError(f"unknown stratum {stratum!r}")

    chosen = _order(records)

    # rep-1 re-assertion (prereg §4.2) — the loader enforces it, and so does assembly.
    for r in chosen:
        if r.source == "probe_prepass" and r.rep != 1:
            raise FirewallViolation(
                f"packet would ship rep={r.rep} record {r.record_id!r}; only rep-1 pre-pass "
                "records are packet-eligible (prereg §4.2)"
            )

    # R14 — fail loud before anything is rendered.
    assert_packet_provenance([r.provenance_triple() for r in chosen], tau)

    redact = stratum in ("D0", "D1")

    null_counts: dict[str, int] = {}
    for r in chosen:
        for f in r.null_fields:
            null_counts[f] = null_counts.get(f, 0) + 1

    def build(recs: Sequence[ResidueRecord]) -> tuple[str, str, int]:
        sparsity = SparsityReport(
            records_shipped=len(recs),
            null_field_counts={
                f: sum(1 for r in recs if f in r.null_fields) for f in sorted(null_counts)
            },
            strata_unsupplied=() if recs else (stratum,),
            excluded_transport_failures=excluded_transport_failures,
        )
        parts = [r.render() for r in recs] or ["(no residue recorded at this distance)"]
        body = "\n\n".join(parts) + "\n\n" + sparsity.render()
        if redact:
            body = redact_verdict_tokens(body)
        return body, sparsity.render(), count_tokens(body)

    body, _sparsity_text, tokens = build(chosen)
    truncated = 0
    while tokens > ceiling and chosen:
        chosen = chosen[:-1]  # drop from the deterministic tail; never quality-ranked
        truncated += 1
        body, _sparsity_text, tokens = build(chosen)

    header = {
        "assembly_version": ASSEMBLY_VERSION,
        "arm": "F-prom-retrieved",
        "task_uid": task_uid,
        "d_stratum": stratum,
        "source_record_ids": [f"{r.ledger_id}#{r.seq}" for r in chosen],
        "source_counts": {
            s: sum(1 for r in chosen if r.source == s) for s in sorted({r.source for r in chosen})
        },
        "tau_provenance": dict(sorted(tau.items())),
        "token_count": tokens,
        "token_count_method": TOKEN_COUNT_METHOD,
        "token_ceiling": ceiling,
        "records_truncated_to_fit": truncated,
        "verdict_redaction_applied": redact,
        "redaction_regex": _VERDICT_TOKEN.pattern,
        "sampling": sampling_note,
        "prereg": "PREREG_METABOLIZATION_PROBE_v1 §4.3/§4.4/§4.5",
    }

    packet = Packet(header=header, body=body)

    # Post-condition: for D0/D1 nothing the scorer would read as a verdict may survive.
    if redact and leaks_verdict(packet.body):
        raise FirewallViolation(
            "verdict token survived redaction in a D0/D1 packet — redactor/scorer drift "
            "(prereg §4.5); this must never be shipped"
        )
    return packet


def assemble_whole(
    *,
    task_uid: str,
    stratum: str,
    prefix_records: Sequence[ResidueRecord],
    records: Sequence[ResidueRecord],
    tau: dict[str, int],
    solver_context_tokens: int,
    excluded_transport_failures: int = 0,
    sampling_note: str = "full-scan",
) -> Packet:
    """`F-prom-whole` — the existence arm (prereg §5.3).

    Capped at `solver_context - 20%`. The `signature_index` block is emitted FIRST, in
    cacheable-prefix position, so a long-context solver pays for it once per solver rather
    than once per task.
    """
    cap = int(solver_context_tokens * (1.0 - WHOLE_CONTEXT_HEADROOM))
    prefix = _order(prefix_records)
    body_records = _order(records)

    assert_packet_provenance(
        [r.provenance_triple() for r in list(prefix) + list(body_records)], tau
    )

    redact = stratum in ("D0", "D1")
    prefix_text = "=== SIGNATURE INDEX (cacheable prefix) ===\n" + (
        "\n".join(r.render() for r in prefix) or "(no signature classes available)"
    )

    def build(recs: Sequence[ResidueRecord]) -> tuple[str, int]:
        sparsity = SparsityReport(
            records_shipped=len(recs) + len(prefix),
            null_field_counts={},
            strata_unsupplied=() if (recs or prefix) else (stratum,),
            excluded_transport_failures=excluded_transport_failures,
        )
        tail = "\n\n".join(r.render() for r in recs) or "(no residue recorded at this distance)"
        text = prefix_text + "\n\n=== RESIDUE ===\n" + tail + "\n\n" + sparsity.render()
        if redact:
            text = redact_verdict_tokens(text)
        return text, count_tokens(text)

    body, tokens = build(body_records)
    truncated = 0
    while tokens > cap and body_records:
        body_records = body_records[:-1]
        truncated += 1
        body, tokens = build(body_records)

    header = {
        "assembly_version": ASSEMBLY_VERSION,
        "arm": "F-prom-whole",
        "task_uid": task_uid,
        "d_stratum": stratum,
        "prefix_record_ids": [f"{r.ledger_id}#{r.seq}" for r in prefix],
        "source_record_ids": [f"{r.ledger_id}#{r.seq}" for r in body_records],
        "tau_provenance": dict(sorted(tau.items())),
        "token_count": tokens,
        "token_count_method": TOKEN_COUNT_METHOD,
        "token_cap": cap,
        "solver_context_tokens": solver_context_tokens,
        "records_truncated_to_fit": truncated,
        "verdict_redaction_applied": redact,
        "redaction_regex": _VERDICT_TOKEN.pattern,
        "cacheable_prefix": True,
        "sampling": sampling_note,
        "prereg": "PREREG_METABOLIZATION_PROBE_v1 §4.5/§5.3",
    }
    packet = Packet(header=header, body=body)
    if redact and leaks_verdict(packet.body):
        raise FirewallViolation("verdict token survived redaction in F-prom-whole (prereg §4.5)")
    return packet


def assemble_oracle(
    *, task_uid: str, walls: Sequence[dict[str, Any]], raw_records: Sequence[dict[str, Any]] = ()
) -> Packet:
    """`F-oracle` for Tier-A walls. Ships only MANIFEST §1 shippable fields, asserts quarantine."""
    lines = []
    for w in walls:
        for k in WALL_SHIPPABLE:
            lines.append(f"  {k}: {w.get(k, '(not recorded)')}")
        lines.append("")
    body = "\n".join(lines).rstrip() or "(no walls supplied)"
    assert_wall_quarantine(body, raw_records or walls)
    header = {
        "assembly_version": ASSEMBLY_VERSION,
        "arm": "F-oracle",
        "task_uid": task_uid,
        "shippable_fields": list(WALL_SHIPPABLE),
        "quarantined_fields": list(WALL_QUARANTINED),
        "token_count": count_tokens(body),
        "token_count_method": TOKEN_COUNT_METHOD,
        "source": "apollo/wall_corpus/MANIFEST.md §1",
    }
    return Packet(header=header, body=body)


def tau_from_records(records: Iterable[ResidueRecord]) -> dict[str, int]:
    """Build a cutoff vector covering exactly the ledgers present, at their max observed seq.

    Convenience for native (pre-probe) residue whose entire extent precedes every target
    attempt. It is NOT a substitute for a task-specific τ(T) where the pre-pass ledger is
    involved — there the cutoff must be the target's own attempt boundary.
    """
    tau: dict[str, int] = {}
    for r in records:
        tau[r.ledger_id] = max(tau.get(r.ledger_id, 0), r.seq)
    return tau
