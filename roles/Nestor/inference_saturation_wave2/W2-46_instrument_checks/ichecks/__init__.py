"""W2-46 instrument checks: reusable checks for the Wave-2 instrument-failure classes (a)-(h).

Same contract as W2-5's ``checks`` package (copied, not imported, so this folder is self-contained):

* ``OK``           -- the defect signature was looked for and not found (a PASS);
* a DEFECT verdict -- the named signature was found (a FAIL; check-specific name);
* ``NOT_VERIFIED`` -- the check could not look. NOT_VERIFIED is never a pass.

Stdlib only. No world runs. Static checks parse source with ``ast`` and never import or execute the
scanned code; record checks read JSON the caller supplies.
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

    @property
    def outcome(self) -> str:
        """PASS / FAIL / NOT_VERIFIED, the three-outcome reading."""
        return "PASS" if self.ok else "NOT_VERIFIED" if self.verdict == NOT_VERIFIED else "FAIL"

    def __str__(self) -> str:  # pragma: no cover - convenience
        return "[%s] %s: %s" % (self.check, self.verdict, self.reason)


__all__ = ["CheckResult", "OK", "NOT_VERIFIED"]
