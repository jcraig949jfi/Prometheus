"""Reusable automated checks distilled from the NPE historical error autopsy (W2-5).

Every check returns a :class:`CheckResult` with one of three outcome families:

* ``OK``           -- the defect signature was looked for and not found;
* a DEFECT verdict -- the named defect signature was found (check-specific name);
* ``NOT_VERIFIED`` -- the check could not look (missing fields, no shared seeds, no
  planted positive supplied ...). NOT_VERIFIED is never a pass.

Stdlib only. No world runs: every check takes rows, callables or bytes supplied by
the caller. See ../REPORT.md for the defect classes and the incidents behind them.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

OK = "OK"
NOT_VERIFIED = "NOT_VERIFIED"


@dataclass
class CheckResult:
    check: str
    verdict: str
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)
    findings: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.verdict == OK

    @property
    def defect(self) -> bool:
        return self.verdict not in (OK, NOT_VERIFIED)

    def __str__(self) -> str:  # pragma: no cover - convenience
        return "[%s] %s: %s" % (self.check, self.verdict, self.reason)


__all__ = ["CheckResult", "OK", "NOT_VERIFIED"]
