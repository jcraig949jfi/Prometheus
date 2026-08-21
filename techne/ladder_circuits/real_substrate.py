"""REAL SUBSTRATE — cycle 024's composition instruments pointed at a live Prometheus pipeline.

**READ-ONLY AUDIT.** Nothing in `ergon/` is modified, on the same footing as the harmonia R12
grader (HITL #57). Findings are reported; the owning role decides.

**Pipeline chosen: `ergon/probe` packet assembly.** Picked over the discovery pipeline and
harmonia's grading chain because it is the only candidate with (a) explicit sequential stages —
firewall, order, render, redact, count, truncate, re-verify — matching the chain shape cycle 024
built for, (b) a live ledger written the same day, and (c) an existing correctness property
(the verdict firewall) that supplies a real truth function rather than an invented one.

Two things came out of it, and the first is not about the instruments at all.

## Finding A — a live seam defect, found before the instruments were even applied

`campaign.py` writes `p1_prepass.jsonl` with records keyed `key: [rep, uid]`, and reads the same
file two ways: its own `best()` indexes `key` correctly, while `load_prepass()` filters on a
TOP-LEVEL `rep` field that the writer never emits. Measured on the live ledger: **330 records on
disk, 0 in the pool.** The F-prom-retrieved arm then assembles a 58-token packet whose body is
`"(no residue recorded at this distance)"` and whose sparsity report declares the stratum
UNSUPPLIED.

So the pipeline reports *the substrate recorded nothing* when the truth is *the loader could not
read the ledger*. That is claim v13's shape — absence is indistinguishable from unreadability,
and the system reports the benign one — arriving unprompted in production code.

`_audit_load_prepass` below reads the same file the way `best()` does. It exists to make the
finding reproducible, **not** as a proposed fix.

## Finding B — what did NOT transfer, which is the honest answer to the cycle's question

The information profile needs COLLISIONS to say anything. Real records render to unique strings,
so every stage's fibres are singletons, so `deficit = H(T | P) = 0` by construction at every
stage and the seam can never be located. On real data the instrument reports a clean chain no
matter what the chain does.

That is the R0 result from cycle 022 at production scale: an injective projection can never be
aliased, so a clean aliasing reading from one is uninformative rather than good.

**The repair is to stop measuring against identity and measure against the CONSUMER'S
equivalence.** For this pipeline the consumer is the scorer, and the property it cares about is
binary: does the packet leak a verdict. Under that truth function the profile becomes informative
immediately — and it inverts, which is the interesting part. See `redaction_profile`.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from ergon.probe.assemble import (
    ResidueRecord, count_tokens, leaks_verdict, redact_all_answer_forms,
)
from prometheus_math.partition import (
    conditional_entropy, entropy, induced_partition, information_profile, is_refinement_chain,
)

__all__ = ["CAMPAIGN_LEDGER", "raw_rows", "loader_drop_rate", "_audit_load_prepass",
           "assembly_trace", "redaction_profile", "RedactionReport"]

CAMPAIGN_LEDGER = pathlib.Path("ergon/probe/ledgers/campaign/p1_prepass.jsonl")


def raw_rows(path: pathlib.Path = CAMPAIGN_LEDGER) -> List[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def _audit_load_prepass(path: pathlib.Path = CAMPAIGN_LEDGER) -> List[ResidueRecord]:
    """Read the campaign ledger the way `campaign.best()` does — `key = [rep, uid]`.

    **This is an audit shim, not a fix.** It exists so the drop-rate finding is reproducible and
    so the instruments have real records to run on. Which of the two readers is wrong is
    Ergon's call, not mine: the writer could gain a top-level `rep`, or the loader could learn
    the key form, and those have different consequences for the other five call sites of
    `load_prepass`.
    """
    out: List[ResidueRecord] = []
    for seq, d in enumerate(raw_rows(path)):
        key = d.get("key")
        rep = key[0] if isinstance(key, list) and key else d.get("rep", -1)
        if int(rep) != 1:
            continue
        if bool(d.get("derives_from_gold", False)):
            continue
        trace = str(d.get("attempt_text") or "").strip()
        out.append(ResidueRecord(
            ledger_id="p1_prepass",
            seq=seq,
            source="probe_prepass",
            record_id=str(key[1]) if isinstance(key, list) and len(key) > 1 else str(seq),
            body=trace or "(no attempt text recorded)",
            uid=str(key[1]) if isinstance(key, list) and len(key) > 1 else None,
            domain=d.get("domain"),
            rep=1,
            null_fields=tuple(f for f in ("attempt_text",) if not d.get(f)),
        ))
    return out


def loader_drop_rate(path: pathlib.Path = CAMPAIGN_LEDGER) -> Tuple[int, int, int]:
    """(rows on disk, records the shipping loader accepts, records the audit shim accepts)."""
    from ergon.probe.assemble import load_prepass
    return len(raw_rows(path)), len(load_prepass(path)), len(_audit_load_prepass(path))


# --------------------------------------------------------------------------------------------
# The real assembly chain, as cycle-024 stages.

def assembly_trace(record: ResidueRecord) -> List[str]:
    """The states a single record passes through: raw body -> rendered -> redacted.

    Truncation is a packet-level stage rather than a record-level one, so it is not in this
    trace; the chain measured here is the part that acts on each record.
    """
    rendered = record.render()
    return [record.body, rendered, redact_all_answer_forms(rendered)]


@dataclass
class RedactionReport:
    """The profile against BOTH truth functions the pipeline cares about.

    A redaction stage is the first chain I have measured where **rising deficit is the product,
    not the damage**. The firewall's whole job is to destroy information about one quantity while
    preserving another, so correctness is a pair of opposite requirements:

        deficit against the LEAKED quantity must RISE to its full entropy   (verdict destroyed)
        deficit against the USEFUL quantity must STAY at zero               (trace preserved)

    Cycle 024's `ChainReport` assumes deficit is damage and calls any rise a seam. On this
    pipeline that verdict is exactly backwards, which is the clearest thing real data has said
    about the instruments.
    """

    n_records: int
    leak_profile: List[Tuple[float, float]]
    trace_profile: List[Tuple[float, float]]
    leak_entropy: float
    stage_names: Tuple[str, ...] = ("render", "redact")

    @property
    def verdict_destroyed(self) -> bool:
        """Did redaction take the leak deficit to its ceiling?"""
        return self.leak_profile[-1][0] >= self.leak_entropy - 1e-9

    @property
    def trace_preserved(self) -> bool:
        """Did it leave the useful channel intact?"""
        return self.trace_profile[-1][0] < 1e-9

    @property
    def firewall_sound(self) -> bool:
        return self.verdict_destroyed and self.trace_preserved


def redaction_profile(records: Sequence[ResidueRecord],
                      limit: int = 120) -> RedactionReport:
    """Measure the real chain against the consumer's equivalence rather than against identity.

    `leaks_verdict` is the scorer's own predicate and is binary, so its fibres genuinely collide
    — which is exactly what the identity-based profile lacked.
    """
    recs = list(records)[:limit]
    traces = [assembly_trace(r) for r in recs]
    n = len(recs)
    depth = len(traces[0])
    stages = [induced_partition(list(range(n)), lambda i, k=k: traces[i][k])
              for k in range(depth)]
    leak_truth = induced_partition(list(range(n)),
                                   lambda i: leaks_verdict(traces[i][0]))
    # "Useful channel": the record's own identity, which the packet must still carry.
    trace_truth = induced_partition(list(range(n)), lambda i: recs[i].record_id)
    return RedactionReport(
        n_records=n,
        leak_profile=information_profile(stages, leak_truth, n),
        trace_profile=information_profile(stages, trace_truth, n),
        leak_entropy=entropy(leak_truth, n),
    )


# =============================================================================================
# Cycle 026 — the SELECTION stages, which is what the instruments were actually built for.
#
# Cycle 025 pointed the composition instruments at render/redact (intra-record content
# transforms) and they saw nothing. `select_residue` -> `_order*` -> truncate are inter-record
# operations, so this is the scope statement's decisive test.
# =============================================================================================

from ergon.probe.assemble import _order, _order_per_task_stratified  # noqa: E402


def truncated_head(chosen: Sequence[ResidueRecord], ceiling: int = 8000) -> Tuple[str, ...]:
    """The record ids that survive the packet's token ceiling, in order.

    Mirrors `assemble_retrieved`'s truncation: drop from the deterministic tail until the body
    fits. Reproduced here rather than called because the assembler truncates a rendered body and
    this audit needs the surviving RECORD SET.
    """
    out: List[str] = []
    total = 0
    for r in chosen:
        t = count_tokens(r.render())
        if total + t > ceiling:
            break
        out.append(r.record_id)
        total += t
    return tuple(out)


@dataclass
class OrderingReport:
    """Deficit of the shipped packet with respect to the TARGET TASK it was built for.

    A packet that is identical for every task carries zero information about its task, so its
    deficit equals the task entropy — the maximum available. That is the constant-packet defect
    Charon measured, expressed as a number the instruments produce.
    """

    n_tasks: int
    task_entropy: float
    plain_deficit: float
    stratified_deficit: float
    plain_distinct_heads: int
    stratified_distinct_heads: int
    plain_pool_coverage: int
    stratified_pool_coverage: int
    pool_size: int

    @property
    def plain_is_constant(self) -> bool:
        return self.plain_distinct_heads == 1

    @property
    def instruments_transferred(self) -> bool:
        """The scope test: does the measurement separate the known-bad ordering from the fix?"""
        return self.plain_deficit > self.stratified_deficit + 1e-9


def ordering_profile(pool: Sequence[ResidueRecord], n_tasks: int = 24,
                     ceiling: int = 8000) -> OrderingReport:
    """Measure both orderings against the target-task truth function."""
    uids = [r.uid for r in pool][:n_tasks]
    plain = {u: truncated_head(_order(list(pool)), ceiling) for u in uids}
    strat = {u: truncated_head(_order_per_task_stratified(list(pool), target_uid=u), ceiling)
             for u in uids}

    n = len(uids)
    task_truth = induced_partition(uids, lambda u: u)
    plain_part = induced_partition(uids, lambda u: plain[u])
    strat_part = induced_partition(uids, lambda u: strat[u])

    cov = lambda d: len({rid for h in d.values() for rid in h})
    return OrderingReport(
        n_tasks=n,
        task_entropy=entropy(task_truth, n),
        plain_deficit=conditional_entropy(task_truth, plain_part, n),
        stratified_deficit=conditional_entropy(task_truth, strat_part, n),
        plain_distinct_heads=len(set(plain.values())),
        stratified_distinct_heads=len(set(strat.values())),
        plain_pool_coverage=cov(plain),
        stratified_pool_coverage=cov(strat),
        pool_size=len(pool),
    )
