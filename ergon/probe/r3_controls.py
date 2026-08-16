"""R3 control battery — the instrumentation gates that make arm results admissible.

Owner: Harmonia B (meter integrity; spec §4.1, prereg §7 step 8).
Contract: spec R3 (both controls demonstrated BEFORE any arm), R4 (headroom), prereg §4.5
(the adjudicated verdict-strip leakage check), spec §4.2 Tier A exit criteria.

FOUR CONTROLS, each with a pass/fail print:

  A — payload consumption      F-answer >> F0, else the pipeline/solver cannot consume a
                               packet at all and arm results are inadmissible.
  B — cheat control            content-REDACTED, format-intact packets must NOT beat F0.
                               If they do, the packet FORMAT leaks and the spec is rebuilt.
  C — verdict-strip leakage    100 stripped D0 packets, problem text redacted, one solver:
                               gold recovery not significantly above 0.50 AND point <= 0.60.
                               Two failures => D0/D1 excluded (prereg §4.5). probe_prepass
                               does not exist yet -> ARMED-AWAITING-PREPASS; the decision
                               procedure and the packet-side static gate run TODAY against
                               synthetic fixtures.
  D — R4 headroom              smallest difficulty level L with strongest-solver cold F0 in
                               [0.35, 0.60]; measured ceiling (= F-answer accuracy, the
                               instrument's own demonstrated top) minus F0 >= 25pp.

QUANTIFICATION OF "F-answer >> F0" (spec left it open; meter-integrity fixes it here,
recorded in COSIGN_HARMONIA_B_2026-08-16.md):
    PASS iff  (F-answer - F0) >= +25pp  AND  McNemar exact p < 0.01 on paired tasks.
CHEAT-CONTROL FAIL RULE:
    FAIL iff  p < 0.05  AND  delta >= +5pp   (significant AND at the probe's own practical
    floor). Measured operating characteristics at N=400 over 40 fixture seeds: clean-world
    false-alarm 5%, power 100% at a +15pp leak, 85% at +10pp. A sub-5pp format effect sits
    inside the probe's declared practically-inert zone, and the PRIMARY endpoint
    (F-prom vs F-null) is format-matched on both sides, so a residual micro-leak cancels
    there by construction. First version of this rule was an OR — the calibration suite
    itself caught it firing on a clean world (seed 20260816, delta=+11pp noise, p=.028),
    which is the calibration doctrine below doing its job.

CALIBRATION DOCTRINE (harmonia lesson 2026-08-12: a control needs its own positive
control — ladder_liveness_audit vs ladder_leakage_audit): every control here is exercised
in BOTH directions against synthetic worlds before its live verdict means anything:
a clean world where it must PASS and a planted-defect world where it must FAIL. A control
whose calibration fails is INVALID and its live verdict is inadmissible, not merely
suspect. `--fixtures` runs the full calibration suite with zero API spend.

LIVE-RUN HYGIENE: control runs are results files whose run_id starts with "R3-". This
module REFUSES to evaluate rows outside that namespace, and substantive analysis keys on
run_id, so control rows can never be pooled into an arm comparison. Cheat packets run
under arm="F-prom-retrieved" INSIDE an R3-CHEAT run file (ARMS is frozen; the namespace,
not the arm label, is the isolation).

Run:
    cd D:\\prometheus
    PYTHONPATH=. PYTHONIOENCODING=utf-8 python -m ergon.probe.r3_controls --fixtures
    PYTHONPATH=. ... python -m ergon.probe.r3_controls --live <results.jsonl>   (Tier A)
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence

from .assemble import (
    Packet,
    ResidueRecord,
    assemble_retrieved,
    leaks_verdict,
    redact_verdict_tokens,
)
from .schema import ProbeRecord

WALL_CORPUS = pathlib.Path("apollo/wall_corpus/corpus.jsonl")

# Thresholds — fixed here, cited in the co-sign note, changed nowhere else.
A_MIN_DELTA_PP = 25.0
A_MAX_P = 0.01
B_MAX_DELTA_PP = 5.0
B_SIG_P = 0.05
# The cheat batch must be big enough that its noise floor sits WELL below the +5pp
# practical floor it polices (sd ~ 3.3pp at N=400 vs ~5pp at N=200, where calibration
# measured a 20% clean-world false-alarm rate). Redacted packets on a free-tier solver
# are cheap; statistical validity is not.
B_MIN_N = 400
C_N = 100
C_MAX_P = 0.05          # prereg §4.5: pass requires p > 0.05 (one-sided, above-chance)
C_MAX_POINT = 0.60      # prereg §4.5: AND point estimate <= 0.60
C_MAX_FAILURES = 2      # two failures => D0/D1 excluded from the run
D_BAND = (0.35, 0.60)   # prereg §3 cold-F0 band, strongest solver
D_MIN_HEADROOM_PP = 25.0  # spec R4


# ------------------------------------------------------------------ exact statistics (stdlib)


def exact_binom_p_upper(k: int, n: int, p0: float = 0.5) -> float:
    """One-sided exact binomial P(X >= k | n, p0). The leakage check's test (prereg §4.5:
    'not significantly ABOVE chance' — the one-sided upper tail is the preregistered
    direction; below-chance recovery is not leakage)."""
    if n <= 0:
        return 1.0
    return sum(math.comb(n, i) * p0 ** i * (1 - p0) ** (n - i) for i in range(k, n + 1))


def mcnemar_exact_p(n01: int, n10: int) -> float:
    """Two-sided exact McNemar on discordant pairs (binomial, p=0.5)."""
    n = n01 + n10
    if n == 0:
        return 1.0
    k = min(n01, n10)
    tail = sum(math.comb(n, i) * 0.5 ** n for i in range(0, k + 1))
    return min(1.0, 2.0 * tail)


# ------------------------------------------------------------------ result plumbing


@dataclass
class ControlResult:
    name: str
    verdict: str                    # PASS | FAIL | INVALID | ARMED-AWAITING-PREPASS
    detail: str
    numbers: Dict[str, float] = field(default_factory=dict)

    def line(self) -> str:
        nums = "  ".join(f"{k}={v:.4g}" for k, v in self.numbers.items())
        return f"[{self.verdict:^24s}] {self.name}\n    {self.detail}\n    {nums}".rstrip()


def _task_success(rows: Sequence[ProbeRecord], arm: str) -> Dict[str, float]:
    """Per-task mean success for one arm (parse failure scores 0 — prereg §1 guard)."""
    acc: Dict[str, List[float]] = defaultdict(list)
    for r in rows:
        if r.arm != arm or r.status != "ok":
            continue
        acc[r.task_uid].append(1.0 if r.correct else 0.0)
    return {uid: sum(v) / len(v) for uid, v in acc.items() if v}


def _paired(a: Dict[str, float], b: Dict[str, float]):
    """(delta_pp, n01, n10, n_pairs) over the task intersection. Discordance at the
    task-mean level: a>b / a<b (exactly McNemar when one solver, conservative when more)."""
    uids = sorted(set(a) & set(b))
    if not uids:
        return 0.0, 0, 0, 0
    delta = sum(a[u] - b[u] for u in uids) / len(uids) * 100.0
    n01 = sum(1 for u in uids if a[u] > b[u])
    n10 = sum(1 for u in uids if a[u] < b[u])
    return delta, n01, n10, len(uids)


def _guard_namespace(rows: Sequence[ProbeRecord]) -> None:
    bad = sorted({r.run_id for r in rows if not r.run_id.startswith(("R3-", "SYNTHETIC"))})
    if bad:
        raise ValueError(
            f"r3_controls refuses non-control run_ids {bad}; control runs live in the "
            "'R3-*' namespace so they can never be pooled into an arm comparison"
        )


# ------------------------------------------------------------------ Control A


def control_a_payload_consumption(rows: Sequence[ProbeRecord]) -> ControlResult:
    """F-answer >> F0, quantified. A solver that cannot exploit a packet literally
    containing the solution makes every arm result inadmissible (spec R3)."""
    fa, f0 = _task_success(rows, "F-answer"), _task_success(rows, "F0")
    delta, n01, n10, n = _paired(fa, f0)
    p = mcnemar_exact_p(n01, n10)
    ok = delta >= A_MIN_DELTA_PP and p < A_MAX_P and n > 0
    return ControlResult(
        "A payload-consumption (F-answer >> F0)",
        "PASS" if ok else "FAIL",
        f"need delta >= +{A_MIN_DELTA_PP:.0f}pp AND McNemar p < {A_MAX_P}; "
        f"paired on {n} tasks" if n else "no paired tasks — pipeline produced nothing",
        {"delta_pp": delta, "p": p, "n_pairs": n, "n01": n01, "n10": n10},
    )


# ------------------------------------------------------------------ Control B


_WORDNUM = None


def redact_content(packet_text: str) -> str:
    """Content-redacted, format-intact rendering of a packet (spec R3 cheat control).

    Every alphanumeric content token in the BODY becomes 'x' (words) / '0' (digits);
    line structure, punctuation, field labels' shape, lengths-in-tokens, and the packet
    frame survive. The header is kept verbatim: it is format/metadata, and whether
    format+metadata alone lift accuracy is exactly the cheat question.
    """
    global _WORDNUM
    import re
    if _WORDNUM is None:
        _WORDNUM = re.compile(r"[A-Za-z]+|\d")
    head, sep, body = packet_text.partition("=== RESIDUE ===")
    if not sep:  # not a framed packet — redact the whole text
        head, sep, body = "", "", packet_text
    body = _WORDNUM.sub(lambda m: "0" if m.group(0).isdigit() else "x", body)
    return head + sep + body


def control_b_cheat(rows: Sequence[ProbeRecord]) -> ControlResult:
    """Content-redacted packets must NOT beat F0. Rows: an R3-CHEAT run containing F0 rows
    and redacted-packet rows (arm='F-prom-retrieved' inside the R3-CHEAT namespace)."""
    cheat, f0 = _task_success(rows, "F-prom-retrieved"), _task_success(rows, "F0")
    delta, n01, n10, n = _paired(cheat, f0)
    p = mcnemar_exact_p(n01, n10)
    leaks = p < B_SIG_P and delta >= B_MAX_DELTA_PP
    return ControlResult(
        "B cheat control (redacted packet must NOT beat F0)",
        "FAIL" if leaks or n == 0 else "PASS",
        f"fail iff p < {B_SIG_P} AND delta >= +{B_MAX_DELTA_PP:.0f}pp; "
        f"paired on {n} tasks" if n else "no paired tasks — nothing was measured",
        {"delta_pp": delta, "p": p, "n_pairs": n},
    )


# ------------------------------------------------------------------ Control C


def leakage_decision(k_recovered: int, n: int = C_N) -> ControlResult:
    """The adjudicated verdict-strip leakage rule (prereg §4.5, quantified pass condition)."""
    p = exact_binom_p_upper(k_recovered, n)
    point = k_recovered / n if n else 1.0
    ok = p > C_MAX_P and point <= C_MAX_POINT
    return ControlResult(
        "C verdict-strip leakage (gold recovery from stripped D0 packets)",
        "PASS" if ok else "FAIL",
        f"pass iff exact-binomial p > {C_MAX_P} vs 0.50 AND point <= {C_MAX_POINT}; "
        f"{C_MAX_FAILURES} failures exclude D0/D1 from the run (prereg §4.5)",
        {"recovered": k_recovered, "n": n, "point": point, "p_upper": p},
    )


def packet_static_gate(packets: Iterable[Packet]) -> ControlResult:
    """Structural precondition for C: no rendered D0/D1 packet may carry a verdict token,
    verified INDEPENDENTLY of the assembler's own post-condition (meter checks meter)."""
    n = bad = 0
    for pk in packets:
        n += 1
        if leaks_verdict(pk.body):
            bad += 1
    return ControlResult(
        "C-static (independent re-verification: stripped packets carry no verdict token)",
        "PASS" if (n and not bad) else "FAIL",
        f"{bad}/{n} packets leak" if n else "no packets supplied",
        {"n_packets": n, "n_leaking": bad},
    )


# ------------------------------------------------------------------ Control D


def pick_level(cold_by_level: Dict[str, Dict[str, float]]) -> ControlResult:
    """Smallest L whose STRONGEST-solver cold F0 lies in the band (prereg §3)."""
    lo, hi = D_BAND
    for level in sorted(cold_by_level):
        strongest = max(cold_by_level[level].values())
        if lo <= strongest <= hi:
            return ControlResult(
                "D1 leveling (cold band, strongest solver)", "PASS",
                f"level {level} selected; strongest cold F0 in [{lo}, {hi}]",
                {"chosen_level_f0": strongest},
            )
    return ControlResult(
        "D1 leveling (cold band, strongest solver)", "FAIL",
        "no level satisfies the band -> HEADROOM-FAILURE; no residue verdict may be issued "
        "(spec §4.5 row 1)", {},
    )


def headroom_check(f0_acc: float, ceiling_acc: float) -> ControlResult:
    """R4: >= 25pp between strongest-solver F0 and the MEASURED instrument ceiling.
    The ceiling is F-answer accuracy — what a solver that knows the answer achieves
    through this pipeline — not an assumed 1.0 (parse failure eats real headroom)."""
    hr = (ceiling_acc - f0_acc) * 100.0
    return ControlResult(
        "D2 headroom (measured ceiling - F0 >= 25pp)",
        "PASS" if hr >= D_MIN_HEADROOM_PP else "FAIL",
        f"ceiling is MEASURED F-answer accuracy, not assumed 1.0",
        {"headroom_pp": hr, "f0": f0_acc, "ceiling": ceiling_acc},
    )


# ------------------------------------------------------------------ wall-corpus substrate


def wall_substrate_check(path: pathlib.Path = WALL_CORPUS) -> ControlResult:
    """Positive-control substrate integrity: Apollo's two unablated CTRL walls exist and the
    F-answer/F-oracle quarantine fields are present on every record (spec §4.2)."""
    if not path.exists():
        return ControlResult("W wall-corpus substrate", "FAIL", f"{path} missing", {})
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    ctrl = [r for r in rows if r.get("failure_class") == "control_none"]
    missing = [r.get("wall_id") for r in rows
               if not all(k in r for k in ("oracle_diagnosis", "answer_content", "wall_id"))]
    ok = len(ctrl) == 2 and not missing and len(rows) >= 20
    return ControlResult(
        "W wall-corpus substrate (2 unablated CTRL walls; quarantine fields present)",
        "PASS" if ok else "FAIL",
        f"walls={len(rows)} ctrl={[r.get('wall_id') for r in ctrl]} missing_fields={missing}",
        {"n_walls": len(rows), "n_ctrl": len(ctrl)},
    )


# ------------------------------------------------------------------ calibration (fixtures)


def _synth(planted: Dict[str, float], seed: int = 20260816, n_tasks: int = B_MIN_N):
    from .fixtures import synthetic_run
    return synthetic_run(n_tasks=n_tasks, planted=planted, seed=seed,
                         solvers=("fixture:solver",))


def _synthetic_d0_records(n: int, seed: int = 20260816) -> List[ResidueRecord]:
    """D0 residue whose traces are saturated with verdict tokens — the worst case the
    redactor must survive."""
    rng = random.Random(seed)
    out = []
    for i in range(n):
        truth = rng.random() < 0.5
        out.append(ResidueRecord(
            ledger_id="probe_prepass", seq=i + 1, source="probe_prepass",
            record_id=f"fix-{i:03d}", uid=f"task-{i:03d}", domain="ood_coprime", rep=1,
            body=(f"attempt: computed gcd, concluded the claim is {truth}. "
                  f"So the answer is {truth}; mid-trace restatement: {truth}."),
        ))
    return out


def run_calibration() -> List[ControlResult]:
    """Every control, both directions. A control that cannot FAIL is not a control."""
    out: List[ControlResult] = []

    # A and B are STATISTICAL controls, so a single-seed check would calibrate a coin
    # flip — and a 10-seed check nearly did the same (2 clean-world alarms in the first
    # 10 seeds read as a 20% size when the 40-seed measurement is 5%). Measure operating
    # characteristics over 40 seeds: clean world PASS >= 90% (size), planted defect
    # FAIL >= 90% (power).
    seeds = [20260816 + i for i in range(40)]

    def _rate(control, planted, want_pass: bool) -> float:
        hits = 0
        for s in seeds:
            v = control(_synth(planted, seed=s)).verdict
            hits += int(v == ("PASS" if want_pass else "FAIL"))
        return hits / len(seeds)

    # A — clean world (F-answer +50pp) must PASS; broken pipeline (+0) must FAIL.
    a_size = _rate(control_a_payload_consumption, {"F0": 0.0, "F-answer": 0.50}, True)
    a_power = _rate(control_a_payload_consumption, {"F0": 0.0, "F-answer": 0.0}, False)
    out.append(_cal("A", a_size, a_power))

    # B — honest redaction (cheat lift 0) must PASS; leaky format (+15pp) must FAIL.
    b_size = _rate(control_b_cheat, {"F0": 0.0, "F-prom-retrieved": 0.0}, True)
    b_power = _rate(control_b_cheat, {"F0": 0.0, "F-prom-retrieved": 0.15}, False)
    out.append(_cal("B", b_size, b_power))

    # C statistics — 50/100 recoveries must PASS; 66/100 must FAIL (p ~ 8e-4);
    # 61/100 must FAIL on point>0.60 even before p; 58/100 must PASS (p ~ 0.067).
    c_ok = (leakage_decision(50).verdict == "PASS"
            and leakage_decision(58).verdict == "PASS"
            and leakage_decision(61).verdict == "FAIL"
            and leakage_decision(66).verdict == "FAIL")

    # C packet path — assembled D0 packets must survive the independent static gate,
    # and an UNREDACTED render of the same records must be caught as leaking.
    recs = _synthetic_d0_records(C_N)
    tau = {"probe_prepass": C_N + 1}
    pkts = [assemble_retrieved(task_uid=r.uid or "", stratum="D0", records=[r], tau=tau)
            for r in recs]
    static = packet_static_gate(pkts)
    raw_leaks = all(leaks_verdict(r.render()) for r in recs)
    redact_roundtrip = not leaks_verdict(redact_verdict_tokens(recs[0].render()))
    c_packet_ok = static.verdict == "PASS" and raw_leaks and redact_roundtrip
    out.append(ControlResult(
        "CALIBRATION C (decision rule + packet path, both directions)",
        "PASS" if (c_ok and c_packet_ok) else "FAIL",
        f"decision-vector ok={c_ok}; static gate on {len(pkts)} assembled packets="
        f"{static.verdict}; unredacted-render caught leaking={raw_leaks}; "
        f"redactor round-trip clean={redact_roundtrip}",
        {"n_packets": len(pkts)},
    ))

    # D — band selection both directions + headroom both directions.
    d_pick_ok = pick_level({"L0": {"s": 0.82}, "L1": {"s": 0.55}}).verdict == "PASS"
    d_pick_fail = pick_level({"L0": {"s": 0.82}, "L1": {"s": 0.20}}).verdict == "FAIL"
    d_hr_ok = headroom_check(0.45, 0.95).verdict == "PASS"
    d_hr_fail = headroom_check(0.55, 0.70).verdict == "FAIL"
    out.append(ControlResult(
        "CALIBRATION D (leveling + headroom, both directions)",
        "PASS" if all((d_pick_ok, d_pick_fail, d_hr_ok, d_hr_fail)) else "FAIL",
        f"pick_pass={d_pick_ok} pick_fail={d_pick_fail} hr_pass={d_hr_ok} hr_fail={d_hr_fail}",
        {},
    ))

    # W — the real wall corpus, structural.
    out.append(wall_substrate_check())
    return out


def _cal(name: str, clean_pass_rate: float, defect_fail_rate: float) -> ControlResult:
    ok = clean_pass_rate >= 0.9 and defect_fail_rate >= 0.9
    return ControlResult(
        f"CALIBRATION {name} (operating characteristics over 40 seeds)",
        "PASS" if ok else "FAIL",
        "clean world must PASS >= 90% (size); planted defect must FAIL >= 90% (power)",
        {"clean_pass_rate": clean_pass_rate, "defect_fail_rate": defect_fail_rate},
    )


# ------------------------------------------------------------------ CLI


def _load_rows(path: pathlib.Path) -> List[ProbeRecord]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            d.pop("schema_version", None)
            rows.append(ProbeRecord(**d))
    _guard_namespace(rows)
    return rows


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixtures", action="store_true",
                    help="run the calibration suite (both directions, zero API spend)")
    ap.add_argument("--live", type=pathlib.Path, default=None,
                    help="evaluate an R3-* results JSONL (controls A and B)")
    ap.add_argument("--leakage-recovered", type=int, default=None,
                    help="control C live: number of gold labels recovered out of --leakage-n")
    ap.add_argument("--leakage-n", type=int, default=C_N)
    args = ap.parse_args(argv)

    results: List[ControlResult] = []
    if args.fixtures or (not args.live and args.leakage_recovered is None):
        print("== R3 control battery — CALIBRATION (synthetic fixtures; test inputs, "
              "never evidence) ==")
        results = run_calibration()
        results.append(ControlResult(
            "C live status", "ARMED-AWAITING-PREPASS",
            "probe_prepass does not exist yet (prereg §4.2); the decision rule and packet "
            "path are calibrated above and the live batch runs with the other controls "
            "before any arm", {},
        ))
    if args.live:
        rows = _load_rows(args.live)
        print(f"== R3 control battery — LIVE ({args.live}, {len(rows)} rows) ==")
        results.append(control_a_payload_consumption(rows))
        results.append(control_b_cheat(rows))
    if args.leakage_recovered is not None:
        results.append(leakage_decision(args.leakage_recovered, args.leakage_n))

    hard_fail = False
    for r in results:
        print(r.line())
        if r.verdict == "FAIL":
            hard_fail = True
    print()
    if hard_fail:
        print("FAIL: at least one control failed. Arms are INADMISSIBLE until every "
              "control passes (spec R3/R4; prereg §8).")
        return 1
    print("PASS: all executed controls pass. (Controls marked ARMED-AWAITING-PREPASS "
          "still gate arms and must run live before the first arm.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
