"""Controls for adapters/_common.evidence_envelope (court charter, TOOL ADMISSIBILITY).

"A future agent should find it difficult to accidentally use an inadmissible instrument
as evidence."  These cases are that difficulty, measured.  stdlib only.

    python engine/necropolis/workshop/tests/test_evidence_stamp.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS.parents[2]))
from engine.necropolis.workshop.adapters import _common as C  # noqa: E402

results = []


def case(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f"  -- {detail}" if detail else ""))


def refused(tool_id):
    try:
        C.evidence_envelope(tool_id, [], {"x": 1})
        return None
    except C.InadmissibleInstrument as e:
        return str(e)


# refusals: the named instruments of the charter
for tid, why in (("NT-001", "grading oracle UNTRUSTED"), ("NT-010", "Pollux statistic UNTRUSTED: executes, still refused"),
                 ("NT-090", "BROKEN"), ("NT-091", "HISTORICAL_ONLY"), ("NT-057", "NEEDS_VALIDATION adapter"),
                 ("NT-017", "NEEDS_DEPENDENCY"), ("NT-999", "unregistered")):
    msg = refused(tid)
    case(f"{tid} refused as evidence ({why})", msg is not None, (msg or "")[:100])

# author-tests-only rows: every one refused
rows = [json.loads(l) for l in (WS / "TOOLS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
author_only = [r["tool_id"] for r in rows if r["admissibility"]["controlled"] == "AUTHOR_ONLY"]
case(f"all {len(author_only)} author-tests-only rows refused as evidence", all(refused(t) for t in author_only))

# admissible rows stamp, and the stamp carries what the charter requires
env = C.evidence_envelope("NT-047", [WS / "TOOLS.jsonl"], {"x": 1})
st = env["instrument"]
need = ("tool_id", "source_commit", "necropolis_status", "admissibility", "controls_artifact_sha256", "registry_sha256", "original_scientific_logic")
case("NT-047 stamps with tool id / version / status / ladder / control fingerprint", all(st.get(k) is not None for k in need) and env["purpose"] == "EVIDENCE",
     ", ".join(k for k in need if st.get(k) is None))
env48 = C.evidence_envelope("NT-048", [], {"x": 1})
o48 = env48["instrument"]["original_scientific_logic"]
case("adapter stamp names the original scientific logic it invokes (NT-048 -> pollux daemon)", "charon/agents/pollux/daemon.py" in o48, o48[:90])
adapters = [r["tool_id"] for r in rows if r["layer"] == "NECROPOLIS_ADAPTER"]
undeclared = [t for t in adapters if C.instrument_stamp(t)["original_scientific_logic"] in (None, "UNDECLARED")]
case(f"all {len(adapters)} adapter rows declare ORIGINAL SCIENTIFIC LOGIC", not undeclared, str(undeclared))

# READY_WITH_CAVEAT: stamps, but the caveat travels with the output and the class is not plain EVIDENCE
env = C.evidence_envelope("NT-049", [], {"x": 1})
case("NT-049 (READY_WITH_CAVEAT) stamps as EVIDENCE_WITH_CAVEAT with caveat text",
     env["instrument"]["admissibility"]["admissible_as"] == "EVIDENCE_WITH_CAVEAT" and bool(env["instrument"]["caveat"]))

# diagnostic purpose never lies about admissibility
env = C.evidence_envelope("NT-010", [], {"x": 1}, purpose="DIAGNOSTIC")
case("NT-010 as DIAGNOSTIC stamps NOT_ADMISSIBLE visibly", env["purpose"] == "DIAGNOSTIC" and env["instrument"]["admissibility"]["admissible_as"] == "NOT_ADMISSIBLE")

# legacy envelope is marked unstamped
env = C.result_envelope("anything", [], {"x": 1})
case("legacy result_envelope is marked DIAGNOSTIC/unstamped", env["purpose"] == "DIAGNOSTIC" and "unstamped" in env)

# a registry that lies (status READY but ladder blocked) is caught at stamp time, not trusted
import copy, tempfile, os
bad = copy.deepcopy(next(r for r in rows if r["tool_id"] == "NT-047"))
bad["admissibility"]["admissible"] = False; bad["admissibility"]["blocked_by"] = "CONTROLLED"; bad["admissibility"]["admissible_as"] = "NOT_ADMISSIBLE"
orig = C.tool_record
C.tool_record = lambda tid: bad
case("status READY with a blocked ladder is still refused (ladder, not status string, decides)", refused("NT-047") is not None)
C.tool_record = orig

n = len(results)
print(f"\n{sum(results)}/{n} evidence-stamp cases behave as required")
sys.exit(0 if all(results) else 1)
