"""stall_check -- a stall is a MEASURED RATE over an explicit interval.

    "Any future claim that a process or worktree is 'stalled' must be based
     on measured progress over an explicit interval. A snapshot is not
     evidence of a stall."
                                                  (operator, 2026-09-11)

Origin, recorded because the rule was bought with two destroyed worktrees:
on 2026-09-11 this seat twice judged a `git worktree add` stalled because a
top-level entry count had not moved between two glances, and destroyed both
under WORKING_CONTRACT s7 (destroy, do not nurse). The third attempt looked
identical. Measured instead of judged, it was moving at about 75 files/s and
completed normally at 39,488 files. The repository had 22-24 concurrent git
processes from the fleet-wide adoption pass. Slow is not corrupt, and s7 is
for corrupt.

The operative asymmetry: STALLED is a destructive verdict and PROGRESSING is
not, so the predicate is deliberately biased against STALLED. It refuses to
rule (INDETERMINATE) whenever the observation cannot distinguish "not moving"
from "moving slower than this interval can see". Defaulting to STALLED under
ignorance is the exact 2026-09-11 error.

    from roles.Hypatia.science.stall_check import check_stall
    v = check_stall(lambda: count_files(path), interval_s=20.0, samples=3)
    if v.verdict == "STALLED": ...      # only now may s7 be invoked

Every verdict carries the interval, the sample count, the readings and the
measured rate, so a receipt quoting it can be audited without rerunning it.

Self-controls: python roles/Hypatia/science/stall_check.py --selftest
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Callable, List, Optional

PROGRESSING = "PROGRESSING"
STALLED = "STALLED"
INDETERMINATE = "INDETERMINATE"

MIN_SAMPLES = 2          # one reading is a snapshot and can never rule
MIN_INTERVAL_S = 5.0     # below this, "no change" is not informative


@dataclass
class StallVerdict:
    verdict: str
    reason: str
    readings: List[float] = field(default_factory=list)
    timestamps: List[float] = field(default_factory=list)
    interval_s: float = 0.0
    samples: int = 0
    rate_per_s: Optional[float] = None
    min_detectable_rate_per_s: Optional[float] = None

    def as_dict(self):
        return asdict(self)

    def __str__(self):
        r = "n/a" if self.rate_per_s is None else "%.4f/s" % self.rate_per_s
        return ("%s over %.1fs, %d samples, rate %s -- %s"
                % (self.verdict, self.interval_s, self.samples, r, self.reason))


def classify(readings, timestamps, min_unit=1.0):
    """Pure decision function. Separated so it can be tested without a clock."""
    n = len(readings)
    if n < MIN_SAMPLES:
        return StallVerdict(INDETERMINATE,
                            "a single reading is a snapshot; a stall is a rate, "
                            "not a value", list(readings), list(timestamps),
                            0.0, n)
    span = timestamps[-1] - timestamps[0]
    if span < MIN_INTERVAL_S:
        return StallVerdict(INDETERMINATE,
                            "interval %.2fs is below the %.1fs floor; 'no change' "
                            "over this long is not informative"
                            % (span, MIN_INTERVAL_S),
                            list(readings), list(timestamps), span, n)

    delta = readings[-1] - readings[0]
    rate = delta / span if span > 0 else 0.0
    min_detectable = min_unit / span

    if delta < 0:
        return StallVerdict(INDETERMINATE,
                            "the probe went backwards (%.3f); it is not monotone "
                            "and cannot be read as progress" % delta,
                            list(readings), list(timestamps), span, n, rate,
                            min_detectable)
    if delta > 0:
        return StallVerdict(PROGRESSING,
                            "advanced %.3f over %.1fs" % (delta, span),
                            list(readings), list(timestamps), span, n, rate,
                            min_detectable)

    # delta == 0. The only branch that may say STALLED, and it still must
    # show that the interval was long enough to have seen one unit of work.
    if span < (min_unit / min_detectable if min_detectable else 0):
        return StallVerdict(INDETERMINATE, "interval too short to resolve one unit",
                            list(readings), list(timestamps), span, n, 0.0,
                            min_detectable)
    return StallVerdict(STALLED,
                        "no change over %.1fs across %d samples; one unit would "
                        "have been visible at >= %.4f/s"
                        % (span, n, min_detectable),
                        list(readings), list(timestamps), span, n, 0.0,
                        min_detectable)


def check_stall(probe: Callable[[], float], interval_s: float = 20.0,
                samples: int = 3, min_unit: float = 1.0,
                _clock=time.monotonic, _sleep=time.sleep) -> StallVerdict:
    """Sample `probe` `samples` times across `interval_s` and rule."""
    # Do NOT silently upgrade a snapshot into a measurement. A caller who
    # asks for one reading gets one reading and an INDETERMINATE verdict --
    # refusing is the whole point of this predicate. (Caught by the
    # snapshot_cannot_rule self-control, 2026-09-11.)
    gap = interval_s / (samples - 1) if samples > 1 else 0.0
    readings, stamps = [], []
    for i in range(samples):
        readings.append(float(probe()))
        stamps.append(_clock())
        if i < samples - 1:
            _sleep(gap)
    return classify(readings, stamps, min_unit=min_unit)


# ---------------------------------------------------------------------------
def selftest():
    """Negative, positive and cheat controls. The cheat is the real one: the
    slow-but-live process that this seat destroyed twice."""
    results = {}

    class FakeClock:
        def __init__(self):
            self.t = 0.0

        def __call__(self):
            return self.t

        def sleep(self, d):
            self.t += d

    def run(probe, interval=20.0, samples=3, min_unit=1.0):
        c = FakeClock()
        return check_stall(probe, interval, samples, min_unit,
                           _clock=c, _sleep=c.sleep)

    # NEGATIVE: a genuinely dead process must be callable STALLED.
    v = run(lambda: 100.0)
    results["negative_detects_real_stall"] = (v.verdict == STALLED)

    # POSITIVE: a healthy fast process must read PROGRESSING.
    state = {"n": 0.0}

    def fast():
        state["n"] += 1500.0
        return state["n"]
    v = run(fast)
    results["positive_detects_progress"] = (v.verdict == PROGRESSING)

    # CHEAT: the 2026-09-11 case. Slow but live. Must NEVER read STALLED.
    slow = {"n": 31450.0}

    def creeping():
        slow["n"] += 1.0          # one unit per sample: barely moving
        return slow["n"]
    v = run(creeping)
    results["cheat_slow_but_live_not_called_stalled"] = (v.verdict != STALLED)
    results["cheat_verdict_was"] = v.verdict

    # SNAPSHOT: one reading can never rule. This is the invariant itself.
    v = run(lambda: 100.0, samples=1)
    results["snapshot_cannot_rule"] = (v.verdict == INDETERMINATE)

    # TOO-SHORT INTERVAL: refuses rather than defaulting to STALLED.
    v = run(lambda: 100.0, interval=1.0, samples=3)
    results["short_interval_refuses"] = (v.verdict == INDETERMINATE)

    # NON-MONOTONE: a probe that goes backwards is not progress evidence.
    seq = iter([500.0, 400.0, 300.0])
    v = run(lambda: next(seq))
    results["non_monotone_refuses"] = (v.verdict == INDETERMINATE)

    print("STALL_CHECK SELF-CONTROLS")
    for k, val in results.items():
        print("  %-44s %s" % (k, val))
    ok = all(v for k, v in results.items() if isinstance(v, bool))
    print("\n%s" % ("all self-controls pass" if ok else
                    "SELF-CONTROL FAILURE -- do not use this predicate"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(__doc__)
