"""Kairos claim lint -- the design-adequacy findings the SFE engine refuses to compute.

The engine compares hashes, counts units and checks containment; it never
judges nulls, effect sizes, gates, power, controls or whether a kill had
company (SCIENTIFIC_PROVENANCE.md s1, s10). This module reads a CLAIM PACKET
-- the claim, its cited analysis, its family census and the family's
executed experiments, assembled by a reader from the ledger -- and emits
Kairos findings over exactly that refused territory. It is a predicate set,
not a model: the same packet always yields the same findings, and no
finding is a verdict. Kairos proposes; the owner, Harmonia, Charon or the
operator decides.

Declaration convention (Kairos v0). The engine stores an analysis `spec` as
freeform JSON. Kairos reads these optional keys inside it:

    spec.null                {"family": str, "perturbs": str}
    spec.effect_size         {"estimator": str, "value": num, "se": num}
    spec.gate                {"threshold": num, "attainable_range": [lo, hi],
                              "eligible_count": int}
    spec.controls            {"negative": ref, "positive": ref, "cheat": ref}
                             (a ref is a non-empty string: an exp id, a
                              fixture path or a receipt anchor)
    spec.alternatives_considered   [str, ...]
    spec.perturbation_axes   [str, ...]   (see roles/Kairos/science/FAILURE_SURFACE_v0.md)

An ABSENT key is UNDECLARED -- reported as such, never treated as false
(the engine's own rule for replication dimensions). A PRESENT key whose
value does not carry the property is the case this lint exists for: the
label is there and the property is not (base role: verify the property,
never the label). The cheat fixture in roles/Kairos/science/fixtures/ is exactly that.

Severity: ATTACK (the claim as recorded cannot be defended on this axis),
NOTE (worth a sentence in the packet), UNDECLARED (the indeterminate
branch: nothing was asserted either way).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[3]   # roles/Kairos/science -> repo root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LINT_VERSION = "kairos.claim_lint.v0"

ATTACK, NOTE, UNDECLARED = "ATTACK", "NOTE", "UNDECLARED"

POSITIVE_STATUSES = frozenset({"SUPPORTED", "SUCCESSFUL_NEGATIVE"})
# Engine findings on a completion or fork that make an outcome a fact about
# the apparatus rather than the hypothesis (Necropolis LAW N14).
INSTRUMENT_FINDINGS = frozenset({"CONFIG_DIVERGENCE", "NO_EXECUTION_ATTESTATION",
                                 "NO_EFFECTIVE_INTERVENTION", "INTERVENTION_NOT_APPLIED",
                                 "PARTIALLY_INERT_INTERVENTION"})


def _finding(code: str, severity: str, message: str, **where: Any) -> Dict[str, Any]:
    f = {"code": code, "severity": severity, "message": message}
    f.update(where)
    return f


def _is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _ref_ok(x: Any) -> bool:
    return isinstance(x, str) and bool(x.strip())


def _spec(packet: Dict[str, Any]) -> Dict[str, Any]:
    a = packet.get("analysis") or {}
    s = a.get("spec")
    return s if isinstance(s, dict) else {}


def _status(packet: Dict[str, Any]) -> str:
    return str((packet.get("claim") or {}).get("status") or "")


# ---- individual predicates ------------------------------------------------

def check_null(packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if _status(packet) not in POSITIVE_STATUSES:
        return out
    null = _spec(packet).get("null", None)
    if null is None:
        out.append(_finding("K_NULL_UNDECLARED", UNDECLARED,
                            "a positive claim declares no null model; nothing was asserted "
                            "about what the statistic looks like when the effect is absent",
                            path="analysis.spec.null"))
        return out
    if not isinstance(null, dict) or not _ref_ok(null.get("family")):
        out.append(_finding("K_NULL_EMPTY", ATTACK,
                            "spec.null is present but names no null family: the label is there, "
                            "the property is not", path="analysis.spec.null"))
        return out
    if not _ref_ok(null.get("perturbs")):
        out.append(_finding("K_NULL_AXIS_UNSTATED", ATTACK,
                            "the null does not say which axis it perturbs; a null that does not "
                            "perturb the axis the statistic varies on is degenerate",
                            path="analysis.spec.null.perturbs"))
    return out


def check_effect_size(packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if _status(packet) not in POSITIVE_STATUSES:
        return out
    es = _spec(packet).get("effect_size", None)
    if es is None:
        out.append(_finding("K_EFFECT_SIZE_UNDECLARED", UNDECLARED,
                            "a positive claim declares no effect size", path="analysis.spec.effect_size"))
        return out
    if not isinstance(es, dict) or not _is_num(es.get("value")):
        out.append(_finding("K_EFFECT_SIZE_NO_VALUE", ATTACK,
                            "spec.effect_size carries no numeric value", path="analysis.spec.effect_size.value"))
        return out
    if not _is_num(es.get("se")):
        out.append(_finding("K_EFFECT_SIZE_NO_SE", ATTACK,
                            "an effect size without its standard error cannot be read against any gate",
                            path="analysis.spec.effect_size.se"))
    return out


def check_gate(packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    spec = _spec(packet)
    gate = spec.get("gate", None)
    if gate is None:
        if _status(packet) in POSITIVE_STATUSES:
            out.append(_finding("K_GATE_UNDECLARED", UNDECLARED,
                                "no gate is declared; the claim's status was reached without a "
                                "preregistered line", path="analysis.spec.gate"))
        return out
    if not isinstance(gate, dict) or not _is_num(gate.get("threshold")):
        out.append(_finding("K_GATE_NO_THRESHOLD", ATTACK,
                            "spec.gate is present but carries no numeric threshold", path="analysis.spec.gate.threshold"))
        return out
    thr = gate["threshold"]
    rng = gate.get("attainable_range")
    if not (isinstance(rng, (list, tuple)) and len(rng) == 2 and all(_is_num(v) for v in rng)):
        out.append(_finding("K_GATE_WITHOUT_ATTAINABLE_RANGE", ATTACK,
                            "the gate has no attainable range; it cannot be shown that the gate "
                            "could fire on any input", path="analysis.spec.gate.attainable_range"))
    else:
        lo, hi = min(rng), max(rng)
        if thr < lo or thr > hi:
            out.append(_finding("K_GATE_UNREACHABLE", ATTACK,
                                "threshold {} lies outside the attainable range [{}, {}]: the gate "
                                "could not fire on any input, so 'nothing fired' is not a null "
                                "reading".format(thr, lo, hi), path="analysis.spec.gate.threshold"))
    ec = gate.get("eligible_count")
    if ec is None:
        out.append(_finding("K_ELIGIBLE_COUNT_MISSING", ATTACK,
                            "no eligible count: 'nothing fired' and 'nothing could have fired' "
                            "cannot be told apart", path="analysis.spec.gate.eligible_count"))
    elif not (isinstance(ec, int) and not isinstance(ec, bool)):
        out.append(_finding("K_ELIGIBLE_COUNT_NOT_INTEGER", ATTACK,
                            "eligible_count is not an integer", path="analysis.spec.gate.eligible_count"))
    elif ec == 0 and _status(packet) != "INCONCLUSIVE":
        out.append(_finding("K_ELIGIBLE_COUNT_ZERO", ATTACK,
                            "eligible_count is 0 and the claim is not INCONCLUSIVE: no row was "
                            "eligible to move the decision", path="analysis.spec.gate.eligible_count"))
    es = spec.get("effect_size")
    if isinstance(es, dict) and _is_num(es.get("value")) and _is_num(es.get("se")) and es["se"] > 0:
        if abs(es["value"] - thr) < es["se"]:
            out.append(_finding("K_GATE_INSIDE_SE", ATTACK,
                                "|value - threshold| = {:.6g} is smaller than the SE {:.6g}: a line "
                                "closer to the observation than its own error is not a gate".format(
                                    abs(es["value"] - thr), es["se"]),
                                path="analysis.spec.gate.threshold"))
    return out


def check_controls(packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if _status(packet) not in POSITIVE_STATUSES:
        return out
    ctl = _spec(packet).get("controls", None)
    if ctl is None:
        out.append(_finding("K_CONTROLS_UNDECLARED", UNDECLARED,
                            "no controls are declared", path="analysis.spec.controls"))
        return out
    if not isinstance(ctl, dict):
        out.append(_finding("K_CONTROLS_MALFORMED", ATTACK, "spec.controls is not an object",
                            path="analysis.spec.controls"))
        return out
    for name, sev, why in (("positive", ATTACK, "the channel has not been shown to detect real signal"),
                           ("cheat", ATTACK, "the channel has not been shown able to observe the thing "
                                             "it claims to measure (success deliberately injected)"),
                           ("negative", NOTE, "welcome but not a substitute for the positive and cheat controls")):
        v = ctl.get(name, None)
        if v is None:
            out.append(_finding("K_CONTROL_MISSING_" + name.upper(), sev,
                                "no {} control: {}".format(name, why), path="analysis.spec.controls." + name))
        elif not _ref_ok(v):
            out.append(_finding("K_CONTROL_EMPTY_" + name.upper(), ATTACK,
                                "the {} control is declared but points at nothing (no exp id, fixture "
                                "or receipt): a label, not a control".format(name),
                                path="analysis.spec.controls." + name))
    return out


def check_conclusion_vs_observation(packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if _status(packet) not in POSITIVE_STATUSES:
        return out
    a = (packet.get("analysis") or {}).get("analysis") or {}
    vn, dn = a.get("verified_n"), a.get("declared_n")
    if _is_num(vn) and vn <= 1:
        out.append(_finding("K_SINGLE_UNIT_SUPPORT", ATTACK,
                            "the claim is positive on verified_n = {} unit(s) under '{}'".format(
                                vn, a.get("unit_of_analysis")), path="analysis.analysis.verified_n"))
    if _is_num(vn) and _is_num(dn) and vn < dn:
        out.append(_finding("K_CONCLUSION_EXCEEDS_VERIFIED_N", ATTACK,
                            "declared_n {} but the engine verified {}; the conclusion rests on units "
                            "the ledger could not resolve".format(dn, vn), path="analysis.analysis.verified_n"))
    alts = _spec(packet).get("alternatives_considered", None)
    if alts is None:
        out.append(_finding("K_ALTERNATIVES_UNDECLARED", UNDECLARED,
                            "no alternative explanations are recorded as considered",
                            path="analysis.spec.alternatives_considered"))
    elif not (isinstance(alts, list) and any(_ref_ok(x) for x in alts)):
        out.append(_finding("K_ALTERNATIVES_EMPTY", ATTACK,
                            "alternatives_considered is present and names nothing",
                            path="analysis.spec.alternatives_considered"))
    td = (packet.get("claim") or {}).get("transport_domain")
    axes = _spec(packet).get("perturbation_axes", None)
    if isinstance(td, list) and td and not (isinstance(axes, list) and axes):
        out.append(_finding("K_TRANSPORT_WITHOUT_SURFACE", ATTACK,
                            "the claim asserts transport to {} domain(s) but no perturbation axis was "
                            "mapped: a parameter-local result presented as universal".format(len(td)),
                            path="claim.transport_domain"))
    return out


def check_kill_geometry(packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Single-experiment lineage death, and kills that are instrument facts."""
    out: List[Dict[str, Any]] = []
    exps = packet.get("experiments") or []
    executed = [e for e in exps if isinstance(e, dict) and e.get("outcome") in ("FALSIFIED", "SURVIVED", "INCONCLUSIVE")]
    killed = [e for e in executed if e.get("outcome") == "FALSIFIED"]
    for e in killed:
        eng = set(e.get("engine_findings") or [])
        hit = sorted(eng & INSTRUMENT_FINDINGS)
        if hit:
            out.append(_finding("K_KILL_ON_INSTRUMENT_FINDING", ATTACK,
                                "experiment {} is FALSIFIED while the engine recorded {}: the outcome is "
                                "a fact about the apparatus until an apparatus control clears it "
                                "(Necropolis LAW N14)".format(e.get("exp_id"), hit),
                                exp_id=e.get("exp_id"), engine_findings=hit))
        if e.get("measurement_at_range_edge") is True:
            out.append(_finding("K_MEASUREMENT_FAILURE_AS_KILL", ATTACK,
                                "experiment {} is FALSIFIED with its statistic pinned at the measurement's "
                                "declared range edge: UNMEASURABLE, not a kill".format(e.get("exp_id")),
                                exp_id=e.get("exp_id")))
    if killed and len(executed) == 1:
        out.append(_finding("K_SINGLE_EXPERIMENT_TERMINAL", ATTACK,
                            "one executed experiment, FALSIFIED, and no neighbour in the family: a kill "
                            "without geometry (roles/Kairos/science/FAILURE_SURFACE_v0.md)", exp_id=killed[0].get("exp_id")))
    elif killed and not (_spec(packet).get("perturbation_axes")
                         or ((packet.get("family") or {}).get("manifest") or {}).get("kairos_surface")):
        out.append(_finding("K_KILL_WITHOUT_AXES", NOTE,
                            "{} FALSIFIED among {} executed, but no perturbation axes are declared; the "
                            "neighbours cannot be read as a surface".format(len(killed), len(executed))))
    return out


CHECKS = (check_null, check_effect_size, check_gate, check_controls,
          check_conclusion_vs_observation, check_kill_geometry)


def lint(packet: Dict[str, Any]) -> Dict[str, Any]:
    """Run every predicate; return findings with counts by severity. Never a verdict."""
    findings: List[Dict[str, Any]] = []
    for chk in CHECKS:
        findings.extend(chk(packet))
    findings.sort(key=lambda f: (f["severity"] != ATTACK, f["severity"] != NOTE, f["code"]))
    counts = {ATTACK: 0, NOTE: 0, UNDECLARED: 0}
    for f in findings:
        counts[f["severity"]] += 1
    return {"lint": LINT_VERSION,
            "claim_id": (packet.get("claim") or {}).get("claim_id"),
            "status": _status(packet) or None,
            "findings": findings,
            "counts": counts,
            "attack_surface": sorted({f["code"] for f in findings if f["severity"] == ATTACK})}


def lint_files(paths: Iterable[Path]) -> List[Dict[str, Any]]:
    return [lint(json.loads(Path(p).read_text(encoding="utf-8"))) for p in paths]


def main(argv: Optional[List[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: python roles/Kairos/science/claim_lint.py <claim_packet.json> [...]", file=sys.stderr)
        return 2
    results = lint_files(Path(a) for a in args)
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    from archaeon.workspace import assert_not_canonical  # noqa: E402
    assert_not_canonical("run the Kairos claim lint", allow_override=False)
    raise SystemExit(main())
