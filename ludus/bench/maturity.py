"""Circuit maturity ledger — evidence CLASS, never evidence count.

The failure this blocks: a circuit accumulates worlds, the count is quoted as
support, and nobody notices that every one of those worlds was visible while the
circuit was being written or adjusted. "Twenty-one-world support" can mean twenty-
one independent tests or zero, and the number alone cannot tell you which.

So support is never a single number here. It is four separate counts:

    DEVELOPMENT   worlds visible when the circuit was invented
    REPAIR        worlds whose results caused the circuit to be modified
    THRESHOLD     worlds used to set any constant or scope boundary
    PROSPECTIVE   worlds where a prediction was registered BEFORE they existed
    UNTOUCHED     worlds that are none of the above AND expose the circuit's axis

and promotion depends on the CLASS of evidence, not the size of any count.

Ladder, ascending. Each rung requires something the previous one cannot supply:

    PROPOSED             an observed pattern
    EXECUTABLE           mechanically defined; runs without a human in the loop
    IDENTIFIABLE         current measurements distinguish it from its alternatives
    ABLATION_SUPPORTED   an intervention moves behaviour as predicted
    CROSS_WORLD          survives prospectively in more than one untouched world
    PARTNER_ROBUST       survives substitution of its partner on the other axis
    COMPOSITIONAL        participates predictably in combinations
    TRANSFER_SUPPORTED   prior acquisition measurably reduces learning cost elsewhere
    RETIRED              failed

`promote()` refuses any jump that is justified only by more worlds at the same
class. That refusal is the whole point of the file.
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / "ludus" / "atlas"
PATH = ATLAS / "circuit_maturity.json"

LADDER = ["PROPOSED", "EXECUTABLE", "IDENTIFIABLE", "ABLATION_SUPPORTED",
          "CROSS_WORLD", "PARTNER_ROBUST", "COMPOSITIONAL", "TRANSFER_SUPPORTED"]

#: What each rung REQUIRES. Deliberately not satisfiable by adding worlds.
REQUIREMENT = {
    "EXECUTABLE": "a mechanical definition that runs with no human judgement",
    "IDENTIFIABLE": "no other registered circuit produces an identical signature "
                    "across the admissible design",
    "ABLATION_SUPPORTED": "a world property was intervened on and behaviour moved "
                          "in the direction predicted BEFORE the intervention",
    "CROSS_WORLD": ">=2 UNTOUCHED worlds with a prediction registered before they "
                   "existed; development and repair worlds do not count",
    "PARTNER_ROBUST": "measured value survives substituting the partner on the "
                      "other axis; partner_spread below a stated bound",
    "COMPOSITIONAL": "behaviour in combination is predicted from components, "
                     "prospectively",
    "TRANSFER_SUPPORTED": "prior acquisition measurably lowers the COST of "
                          "reaching a competence threshold in a new world",
}


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load() -> dict:
    if PATH.exists():
        return json.loads(PATH.read_text(encoding="utf-8"))
    return {"ladder": LADDER, "requirements": REQUIREMENT, "circuits": {}}


def save(m):
    ATLAS.mkdir(parents=True, exist_ok=True)
    m["updated_utc"] = _now()
    PATH.write_text(json.dumps(m, indent=2), encoding="utf-8")


def register(rid, state="PROPOSED", **counts):
    m = load()
    e = m["circuits"].setdefault(rid, {"circuit_id": rid, "state": state,
                                       "history": []})
    e.update({k: v for k, v in counts.items()})
    e["state"] = state
    e.setdefault("history", []).append({"state": state, "when": _now()})
    save(m)
    return e


#: Structural requirements per rung. Evidence must be a dict carrying these keys
#: with values that pass the stated check. A PROSE justification is never enough.
GATE = {
    "IDENTIFIABLE": (["identical_signature_pairs"],
                     lambda ev: ev.get("identical_signature_pairs") == []),
    "ABLATION_SUPPORTED": (["intervened_property", "predicted_direction",
                            "observed_direction", "registered_before"],
                           lambda ev: (ev.get("registered_before") is True and
                                       ev.get("predicted_direction") ==
                                       ev.get("observed_direction"))),
    "CROSS_WORLD": (["prospective_untouched_worlds", "predictions_registered_before"],
                    lambda ev: (ev.get("predictions_registered_before") is True and
                                len(ev.get("prospective_untouched_worlds", [])) >= 2)),
    "PARTNER_ROBUST": (["max_partner_spread", "bound", "partners_tested"],
                       lambda ev: (ev.get("max_partner_spread") is not None and
                                   ev["max_partner_spread"] <= ev.get("bound", 0.05)
                                   and len(ev.get("partners_tested", [])) >= 3)),
    "COMPOSITIONAL": (["composition", "predicted_before", "prediction_error"],
                      lambda ev: (ev.get("predicted_before") is True and
                                  ev.get("prediction_error", 1.0) <= 0.05)),
    "TRANSFER_SUPPORTED": (["cost_with_prior", "cost_without_prior",
                            "registered_before"],
                           lambda ev: (ev.get("registered_before") is True and
                                       ev.get("cost_with_prior", 1e9) <
                                       ev.get("cost_without_prior", 0))),
    "EXECUTABLE": ([], lambda ev: True),
}


def promote(rid, to_state, evidence):
    """Structural gate. Prose is not evidence.

    The FIRST version of this guard tested `"world count" in str(evidence)` and was
    defeated by its own first test case: the string "support from 21 worlds" does
    not contain "world count", so it promoted r0003 on exactly the reasoning the
    file exists to forbid. A textual guard is a guard against a phrasing, not
    against an argument. Each rung now names the FIELDS its evidence must carry
    and a predicate those fields must satisfy.
    """
    m = load()
    e = m["circuits"].get(rid)
    if not e:
        raise KeyError(rid)
    if to_state not in LADDER:
        raise ValueError(f"{to_state} is not a rung")
    if LADDER.index(to_state) <= LADDER.index(e["state"]):
        raise ValueError("not a promotion")
    if not isinstance(evidence, dict):
        raise TypeError(
            f"evidence for {to_state} must be a dict carrying "
            f"{GATE.get(to_state, ([], None))[0]}; prose is not evidence")
    fields, check = GATE.get(to_state, ([], lambda ev: False))
    missing = [f for f in fields if f not in evidence]
    if missing:
        raise ValueError(f"promotion to {to_state} is missing required evidence "
                         f"fields {missing}. Requirement: {REQUIREMENT[to_state]}")
    if not check(evidence):
        raise ValueError(f"evidence supplied does not satisfy {to_state}: "
                         f"{REQUIREMENT[to_state]}")
    e["state"] = to_state
    e["history"].append({"state": to_state, "evidence": evidence, "when": _now()})
    save(m)
    return e


# ==========================================================================
# The honest seeding, including the parts that read badly
# ==========================================================================

SEED = {
  "r0003": dict(
    state="ABLATION_SUPPORTED",
    development_worlds=["FLIP7", "MARTIAN_DICE"],
    repair_worlds=[],
    threshold_worlds=[],
    prospective_worlds=["INCAN_GOLD", "CANT_STOP"],
    untouched_worlds=["INCAN_GOLD", "CANT_STOP"],
    note="Prediction registered in CYCLE_002 §8.1 before either prospective world "
         "existed; both returned 1.0000 and survived re-pairing. That is CROSS_WORLD "
         "evidence on its face. It is NOT promoted past ABLATION_SUPPORTED because "
         "PARTNER_ROBUST fails outright: the same circuit reads 0.0000 and 1.0000 in "
         "one FOUNDRY world depending only on its partner. A circuit cannot be "
         "credited as cross-world while its value is not yet a function of the world.",
    blocked_at="PARTNER_ROBUST",
    blocking_evidence="partner spread of 1.0000 in FOUNDRY[gate=1,k=3,cap=4]"),

  "r0011": dict(
    state="EXECUTABLE",
    development_worlds=["MARTIAN_DICE"],
    repair_worlds=[],
    threshold_worlds=[],
    prospective_worlds=[],
    untouched_worlds=["CANT_STOP"],
    note="CONTAMINATION FLAG: written from the seat's own 'option preservation' "
         "vocabulary, not from data. Worst circuit in Martian Dice (0.2501, below "
         "the null circuit) and best in Can't Stop (0.9389). No prediction was ever "
         "registered for it, so its Can't Stop result is retrospective and cannot "
         "raise its rung.",
    blocked_at="IDENTIFIABLE",
    blocking_evidence="sign reverses between two worlds sharing an interface; no "
                      "registered prediction distinguishes the two cases in advance"),

  "r0012": dict(
    state="EXECUTABLE",
    development_worlds=["MARTIAN_DICE"],
    repair_worlds=[],
    threshold_worlds=[],
    prospective_worlds=["FOR_SALE (unbuilt)"],
    untouched_worlds=["CANT_STOP"],
    note="Registered kill condition was MIS-SPECIFIED -- it named a reversal "
         "outside push-your-luck, and the reversal happened inside it. Replaced, "
         "not reinterpreted.",
    blocked_at="IDENTIFIABLE",
    blocking_evidence="kill condition replaced after the fact; the replacement has "
                      "not yet faced an untouched world"),

  "r0015": dict(
    state="EXECUTABLE",
    development_worlds=["FLIP7", "MARTIAN_DICE"],
    repair_worlds=[], threshold_worlds=[], prospective_worlds=[],
    untouched_worlds=["INCAN_GOLD", "CANT_STOP"],
    note="Standing COLLISION RISK with r0003. Until a world separates them, one of "
         "the two may be a redundant name.",
    blocked_at="IDENTIFIABLE",
    blocking_evidence="unresolved collision with r0003"),

  "r0007": dict(
    state="EXECUTABLE",
    development_worlds=["FLIP7"], repair_worlds=[], threshold_worlds=[],
    prospective_worlds=[], untouched_worlds=["INCAN_GOLD", "MARTIAN_DICE", "CANT_STOP"],
    note="Pot-blind control. Reads the risk and ignores the stake; retained to show "
         "whether the stake matters. Controls are never promoted.",
    blocked_at="n/a", blocking_evidence="control, not a candidate"),

  "r0010": dict(
    state="EXECUTABLE",
    development_worlds=["MARTIAN_DICE"], repair_worlds=[], threshold_worlds=[],
    prospective_worlds=[], untouched_worlds=["CANT_STOP"],
    note="Baseline.", blocked_at="n/a", blocking_evidence="baseline, not a candidate"),

  "r0014": dict(
    state="EXECUTABLE",
    development_worlds=["MARTIAN_DICE"], repair_worlds=[], threshold_worlds=[],
    prospective_worlds=[], untouched_worlds=["CANT_STOP"],
    note="CONTAMINATION FLAG: same 'spend capacity only when it pays' origin as "
         "r0011.",
    blocked_at="IDENTIFIABLE", blocking_evidence="no registered prediction"),
}


def seed():
    for rid, kw in SEED.items():
        register(rid, **kw)
    return load()


def report() -> str:
    m = seed()
    lines = ["# Circuit maturity", "",
             "Support is four separate counts. A larger count at the same evidence",
             "class is never grounds for promotion.", ""]
    for rid, e in sorted(m["circuits"].items()):
        lines.append(f"## {rid} — **{e['state']}**")
        lines.append(f"- development: {e.get('development_worlds') or '—'}")
        lines.append(f"- repair: {e.get('repair_worlds') or '—'}"
                     f" | threshold: {e.get('threshold_worlds') or '—'}")
        lines.append(f"- prospective: {e.get('prospective_worlds') or '—'}")
        lines.append(f"- untouched: {e.get('untouched_worlds') or '—'}")
        if e.get("blocked_at") and e["blocked_at"] != "n/a":
            lines.append(f"- **blocked at {e['blocked_at']}**: {e.get('blocking_evidence')}")
        lines.append(f"- {e.get('note','')}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    txt = report()
    (ATLAS / "CIRCUIT_MATURITY.md").write_text(txt, encoding="utf-8")
    print(txt)
