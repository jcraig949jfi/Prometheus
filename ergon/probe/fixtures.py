"""Synthetic fixtures for validating the Metabolization Probe's analysis path.

These are TEST INPUTS, never evidence. Every record is stamped `synthetic=True`, and
`schema.write_results` refuses to persist one — so a fixture cannot become a result by
accident rather than by discipline.

Two generators:
  adversarial_responses()  — the response strings that break naive extractors, including the
                             real failure modes we have measured or been warned about
  synthetic_run()          — a full task x arm x solver run with a PLANTED effect, so the
                             analysis can be checked against a number we chose in advance
                             (the same positive-control logic the 2026-06-09 routing eval used)
"""
from __future__ import annotations

import hashlib
import random
from typing import Iterable

from .schema import ProbeRecord, ARMS

# (raw_response, expected_verdict, expected_flag_or_None) — the extractor's acceptance suite.
ADVERSARIAL: list[tuple[str, bool | None, str | None]] = [
    # observed live on NVIDIA during preflight
    ("**False** The claim is false because 8566 and 907 share no common factor.", False, None),
    ("True  \nThe prime factorization of 8566 is 2 x 4283.", True, None),
    # prompt echo — the trap that makes everything parse True
    ("Is this claim true? Answer True or False. False, gcd is 2.", False, None),
    # markdown noise
    ("### __True__ — because gcd(8566, 907) = 1.", True, None),
    # verdict only
    ("False", False, None),
    # empty / whitespace / null
    ("", None, "empty"),
    ("   \n  ", None, "empty"),
    (None, None, "null_response"),
    # refusal
    ("I can't help with that request.", None, "refusal"),
    # thinking leak (Claude Opus 5 thinking-disabled failure mode)
    ("<thinking>let me compute gcd</thinking> True. gcd is 1.", True, "thinking_leak"),
    # truncated inside an unterminated thinking block
    ("<thinking>computing gcd(8566, 907) step by", None, "thinking_leak"),
    # tool call written as prose — the turn 'succeeds' and the call never runs
    ('{"name": "calculator", "arguments": {"a": 8566}}', None, "tool_call_as_text"),
    ("<tool_call>gcd(8566,907)</tool_call>", None, "tool_call_as_text"),
    # no verdict at all
    ("The greatest common divisor is 1.", None, "no_verdict"),
    # both verdicts early
    ("True or false? I would say false here.", False, None),
    ("It is not true; the answer is false.", True, "conflict_early"),
    # cut off mid-word
    ("False. The number 8566 is divisi", False, "possibly_truncated"),
    # unicode / non-ascii (the encoding path that broke an earlier harness)
    ("Faux — non. False, gcd = 2. ≈ confirmed", False, None),
]


def adversarial_responses() -> list[tuple[str, bool | None, str | None]]:
    return list(ADVERSARIAL)


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def synthetic_run(
    n_tasks: int = 120,
    solvers: Iterable[str] = ("nvidia:nemotron-super-49b-v1.5", "nvidia:deepseek-v4-flash"),
    base_rate: float = 0.45,
    planted: dict[str, float] | None = None,
    seed: int = 20260814,
    parse_fail_by_arm: dict[str, float] | None = None,
    timeout_by_arm: dict[str, float] | None = None,
    arms: Iterable[str] = ARMS,
) -> list[ProbeRecord]:
    """A full run whose true per-arm lift over F0 is exactly `planted`.

    Task difficulty varies (so the pairing is doing real work), then each arm's success
    probability is the task's base rate plus that arm's planted lift.
    """
    planted = planted if planted is not None else {
        "F0": 0.0, "F-null": 0.005, "F-generic": 0.02, "F-prom-retrieved": 0.10,
        "F-prom-whole": 0.14, "F-oracle": 0.22, "F-answer": 0.50,
    }
    parse_fail_by_arm = parse_fail_by_arm or {}
    timeout_by_arm = timeout_by_arm or {}
    rng = random.Random(seed)
    solvers = list(solvers)
    arms = list(arms)
    strata = ("D0", "D1", "D2", "D3")

    records: list[ProbeRecord] = []
    for i in range(n_tasks):
        uid = f"synth-{i:04d}"
        difficulty = min(0.95, max(0.05, rng.gauss(base_rate, 0.18)))
        gold = rng.random() < 0.5
        stratum = strata[i % len(strata)]
        for arm in arms:
            p_ok = min(0.99, max(0.01, difficulty + planted.get(arm, 0.0)))
            for solver in solvers:
                status = "ok"
                verdict: bool | None
                if rng.random() < timeout_by_arm.get(arm, 0.0):
                    status, verdict = "timeout", None
                elif rng.random() < parse_fail_by_arm.get(arm, 0.0):
                    verdict = None
                else:
                    verdict = gold if rng.random() < p_ok else (not gold)
                records.append(ProbeRecord(
                    run_id="SYNTHETIC-FIXTURE",
                    task_uid=uid,
                    domain="ood_coprime",
                    d_stratum=stratum,
                    arm=arm,
                    solver=solver,
                    attempt=1,
                    status=status,
                    gold_bool=gold,
                    parsed_verdict=verdict,
                    raw_response="",
                    latency_s=round(rng.uniform(2.0, 25.0), 2),
                    packet_sha256=None if arm == "F0" else _sha(f"{uid}:{arm}"),
                    packet_tokens=None if arm == "F0" else 8000,
                    tau_provenance={"probe_prepass": 1000, "theseus": 5_000_000},
                    executor="fixture",
                    host="local",
                    ts_utc="2026-08-14T00:00:00+00:00",
                    synthetic=True,   # the firewall's hook
                ))
    return records
