"""Typed result records for the Metabolization Probe (spec R9) + the two firewalls.

Two things in this module are load-bearing and must fail loud rather than warn:

  * the SYNTHETIC FIREWALL — a record generated as a test fixture can never reach a results
    file. Fixtures exist to validate the analysis code against a planted effect; if one leaked
    into results we would be measuring our own generator.
  * the R14 PROVENANCE FIREWALL — a packet may contain only residue that precedes the target
    task's held-out attempt. Enforced from ledger ordering via a cutoff vector, never from
    wall-clock (M3's CMOS reset makes clock-derived times untrustworthy).
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field, asdict
from typing import Any, Iterable, Iterator, Optional

# Canonical arm names (spec §2). F-shuffle is OUT of v1 (prereg §5.2).
ARMS = (
    "F0",
    "F-null",
    "F-generic",
    "F-prom-retrieved",
    "F-prom-whole",
    "F-oracle",
    "F-answer",
)
# Arms that carry a packet; F0 by definition does not.
PACKETED_ARMS = tuple(a for a in ARMS if a != "F0")
# Instrumentation control — never enters a substantive comparison (spec R3).
INSTRUMENTATION_ONLY = ("F-answer",)

D_STRATA = ("D0", "D1", "D2", "D3")

STATUSES = ("ok", "timeout", "http_error", "transport_error")


class FirewallViolation(RuntimeError):
    """Raised when a synthetic record or an out-of-provenance packet is about to be used."""


@dataclass
class ProbeRecord:
    """One task x arm x attempt observation."""

    run_id: str
    task_uid: str
    domain: str
    d_stratum: str
    arm: str
    solver: str  # host + model_id, the pinning unit (prereg §1)
    attempt: int
    status: str
    gold_bool: Optional[bool] = None
    parsed_verdict: Optional[bool] = None
    raw_response: str = ""
    extract_flags: list[str] = field(default_factory=list)
    latency_s: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    packet_sha256: Optional[str] = None
    packet_tokens: Optional[int] = None
    # R14: the cutoff vector this packet was assembled against, {ledger_id: max_seq}
    tau_provenance: dict[str, int] = field(default_factory=dict)
    executor: str = ""
    host: str = ""
    ts_utc: str = ""
    synthetic: bool = False

    def __post_init__(self) -> None:
        if self.arm not in ARMS:
            raise ValueError(f"unknown arm {self.arm!r}; expected one of {ARMS}")
        if self.d_stratum not in D_STRATA:
            raise ValueError(f"unknown stratum {self.d_stratum!r}; expected one of {D_STRATA}")
        if self.status not in STATUSES:
            raise ValueError(f"unknown status {self.status!r}; expected one of {STATUSES}")

    @property
    def correct(self) -> Optional[bool]:
        """None when no verdict could be parsed — scored as incorrect, counted separately."""
        if self.parsed_verdict is None or self.gold_bool is None:
            return None
        return self.parsed_verdict == self.gold_bool

    @property
    def scored(self) -> bool:
        """Prereg §1: an unparseable or failed response counts as INCORRECT, never as missing."""
        return bool(self.correct)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def assert_no_synthetic(records: Iterable[ProbeRecord]) -> None:
    """The synthetic firewall. Structural, not a matter of discipline."""
    bad = [r for r in records if r.synthetic]
    if bad:
        raise FirewallViolation(
            f"{len(bad)} synthetic record(s) reached a results path "
            f"(first: run={bad[0].run_id} task={bad[0].task_uid} arm={bad[0].arm}). "
            "Fixtures validate the analysis; they are never evidence."
        )


def assert_packet_provenance(
    packet_records: Iterable[tuple[str, int, bool]],
    tau: dict[str, int],
) -> None:
    """R14 firewall.

    `packet_records` is (ledger_id, seq, derives_from_gold) per residue record in the packet.
    `tau` is the cutoff vector {ledger_id: max_seq_at_cutoff} frozen into the packet header.

    Three conditions, all fatal:
      1. every record's ledger is registered in the cutoff vector
      2. every record's seq precedes the cutoff for its own ledger
      3. no record derives from the target's gold outcome (excluded by TYPE, not by time)
    """
    for ledger, seq, from_gold in packet_records:
        if ledger not in tau:
            raise FirewallViolation(
                f"packet cites unregistered ledger {ledger!r}; cutoff vector covers {sorted(tau)}"
            )
        if seq > tau[ledger]:
            raise FirewallViolation(
                f"packet cites {ledger}:{seq} at or after cutoff {ledger}:{tau[ledger]} — "
                "this would smuggle later knowledge of the target into the packet"
            )
        if from_gold:
            raise FirewallViolation(
                f"packet cites gold-derived record {ledger}:{seq}; "
                "gold-derived records are excluded by type"
            )


def write_results(path: pathlib.Path, records: list[ProbeRecord]) -> int:
    """The only sanctioned way to persist results. Runs the synthetic firewall first."""
    assert_no_synthetic(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
    return len(records)


def read_records(path: pathlib.Path) -> list[ProbeRecord]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(ProbeRecord(**json.loads(line)))
    return out


def iter_records(paths: Iterable[pathlib.Path]) -> Iterator[ProbeRecord]:
    for p in paths:
        yield from read_records(p)
