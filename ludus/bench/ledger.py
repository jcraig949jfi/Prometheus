"""The prospective circuit ledger — the guard against hindsight.

The failure mode this exists to prevent: a circuit is invented while staring at
two worlds, quietly redefined each time a third world breaks it, and eventually
written up as a durable abstraction that "held across five worlds". Every step of
that is locally reasonable and the end product is laundered nonsense.

So each circuit carries, from the moment it is registered:

    circuit_id          the ugly identifier; never renamed
    invented_on         worlds the seat was LOOKING AT when it wrote the circuit
    tuned_on            worlds whose numbers changed the circuit afterwards
    predicted_worlds    worlds where it is predicted to hold, named BEFORE they run
    predicted_direction what "holding" means, stated numerically
    kill_condition      the observation that would retire it, stated in advance
    first_failure       the first world that violated the prediction, and when
    split_history       ancestry when one circuit is split into two
    current_scope       the honest domain of the claim right now
    untouched_tests     worlds that were neither invented_on nor tuned_on

The ledger has teeth rather than being documentation: `evidence_worlds()` refuses
to count any world in `invented_on` or `tuned_on` as evidence for a circuit.
Charter v1 §33 says a type invented because it explains five games cannot treat
those five as independent confirmation. This makes that arithmetic, not a
resolution.

A circuit with zero untouched tests has a retention number and no evidence. The
ledger says so out loud rather than letting a mean-across-worlds hide it.
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / "ludus" / "atlas"
LEDGER_PATH = ATLAS / "circuit_ledger.json"

REQUIRED = ("circuit_id", "invented_on", "tuned_on", "predicted_worlds",
            "predicted_direction", "kill_condition", "first_failure",
            "split_history", "current_scope")


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ==========================================================================
# Seed entries. Written honestly, including the parts that are unflattering.
# ==========================================================================

SEED = {
    "r0003": {
        "circuit_id": "r0003",
        "english": "myopic one-step stopping rule",
        "definition": "STOP iff P(death | continue) * pot >= E[immediate gain | continue]",
        "axis": "STOP",
        "invented_on": ["FLIP7", "MARTIAN_DICE"],
        "tuned_on": [],
        "provenance_note": "NOT invented from the seat's own vocabulary. It is the "
                           "textbook one-step rule; it was written down because "
                           "Flip 7's exact DP table was already sitting there to "
                           "check it against, not because a concept suggested it.",
        "predicted_worlds": ["INCAN_GOLD", "CANT_STOP"],
        "predicted_direction": "retention >= 0.97 with a competent partner on the "
                               "SELECT axis; registered in CYCLE_002 §8.1 before "
                               "either world was built",
        "kill_condition": "retention materially below 0.97 in any world exposing a "
                          "total-loss STOP interface, with a competent SELECT partner",
        "first_failure": None,
        "split_history": [],
        "current_scope": "worlds with an accumulate-or-bank decision where death "
                         "forfeits the ENTIRE pot. Untested where loss is partial "
                         "- see BACKLOG item 2 (Coloretto), which was chosen to "
                         "attack exactly this precondition.",
    },
    "r0010": {
        "circuit_id": "r0010",
        "english": "greedy immediate pot",
        "definition": "take the option with the highest immediate pot",
        "axis": "SELECT",
        "invented_on": ["MARTIAN_DICE"],
        "tuned_on": [],
        "provenance_note": "the null-ish obvious baseline; no ontology in it",
        "predicted_worlds": [],
        "predicted_direction": "unregistered - this is a baseline, not a claim",
        "kill_condition": "n/a; retained as a floor",
        "first_failure": None,
        "split_history": [],
        "current_scope": "baseline only",
    },
    "r0011": {
        "circuit_id": "r0011",
        "english": "minimum consumption / capacity preservation",
        "definition": "take the option consuming least irreversible capacity",
        "axis": "SELECT",
        "invented_on": ["MARTIAN_DICE"],
        "tuned_on": [],
        "provenance_note": "CONTAMINATION FLAG. This circuit was NOT suggested by "
                           "data. It was written because charter v1 §23 talks about "
                           "'option preservation' and the seat reached for its own "
                           "vocabulary. It then scored 0.2501 in Martian Dice - "
                           "far below the null circuit r0013 at 0.7398. Recorded "
                           "because a concept-seeded circuit that FAILS is the "
                           "cheapest possible evidence about how much the seat's "
                           "vocabulary is worth.",
        "predicted_worlds": [],
        "predicted_direction": "unregistered before first run - a retrospective "
                               "number, and it must not be read as a test",
        "kill_condition": "already below the null circuit in its only world",
        "first_failure": "MARTIAN_DICE (retention 0.2501, below null r0013 0.7398)",
        "split_history": [],
        "current_scope": "NONE. Retained as a fossil per charter §42, not as a "
                         "candidate.",
    },
    "r0012": {
        "circuit_id": "r0012",
        "english": "one-ply lookahead select",
        "definition": "take the option whose single next draw has the best greedy "
                      "expected pot",
        "axis": "SELECT",
        "invented_on": ["MARTIAN_DICE"],
        "tuned_on": [],
        "provenance_note": "shallow-search baseline, not a concept",
        "predicted_worlds": ["FOR_SALE"],
        "predicted_direction": "retention >= 0.90 in For Sale, and r0011 stays near "
                               "the bottom. Registered in BACKLOG.md before For Sale "
                               "exists.",
        "kill_condition": "the ORDERING of SELECT circuits reverses outside "
                          "push-your-luck - that would mean SELECT circuits are "
                          "genre-mediated, not interface-mediated",
        "first_failure": None,
        "split_history": [],
        "current_scope": "push-your-luck worlds with a live SELECT axis. ONE family. "
                         "Surviving For Sale would be evidence, NOT a universal "
                         "circuit.",
    },
    "r0014": {
        "circuit_id": "r0014",
        "english": "pot gain per unit capacity",
        "definition": "maximise pot gain divided by capacity consumed",
        "axis": "SELECT",
        "invented_on": ["MARTIAN_DICE"],
        "tuned_on": [],
        "provenance_note": "CONTAMINATION FLAG. Same origin as r0011 - written from "
                           "the seat's own 'spend capacity only when it pays' "
                           "intuition, not from any observation.",
        "predicted_worlds": [],
        "predicted_direction": "unregistered before first run",
        "kill_condition": "fails to beat the null circuit r0013 in any world with a "
                          "live SELECT axis",
        "first_failure": None,
        "split_history": [],
        "current_scope": "provisional; one world, retrospective number",
    },
    "r0015": {
        "circuit_id": "r0015",
        "english": "two-ply myopic stopping",
        "definition": "stop iff continuing two draws under greedy play has negative "
                      "expected change",
        "axis": "STOP",
        "invented_on": ["FLIP7", "MARTIAN_DICE"],
        "tuned_on": [],
        "provenance_note": "depth variant of r0003, written to test whether depth "
                           "buys anything on the STOP axis",
        "predicted_worlds": [],
        "predicted_direction": "unregistered",
        "kill_condition": "COLLISION RISK: if r0015 never separates from r0003 in "
                          "any world, one of them is redundant and the bench must "
                          "hunt a world that separates them or retire one.",
        "first_failure": None,
        "split_history": [],
        "current_scope": "provisional",
    },
    "r0007": {
        "circuit_id": "r0007",
        "english": "survival-rate stopping",
        "definition": "stop once P(surviving one more draw) falls below 1/2",
        "axis": "STOP",
        "invented_on": ["FLIP7"],
        "tuned_on": [],
        "provenance_note": "pot-blind control: it reads the risk and ignores the "
                           "stake. Its whole job is to show whether the stake "
                           "matters.",
        "predicted_worlds": [],
        "predicted_direction": "predicted to underperform r0003 wherever pot varies",
        "kill_condition": "n/a; retained as a control",
        "first_failure": None,
        "split_history": [],
        "current_scope": "control only",
    },
}


def load() -> dict:
    if LEDGER_PATH.exists():
        return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    return {"schema": list(REQUIRED), "created_utc": _now(), "circuits": {}}


def save(led: dict) -> None:
    ATLAS.mkdir(parents=True, exist_ok=True)
    led["updated_utc"] = _now()
    LEDGER_PATH.write_text(json.dumps(led, indent=2), encoding="utf-8")


def seed() -> dict:
    led = load()
    for rid, entry in SEED.items():
        if rid not in led["circuits"]:
            entry = dict(entry)
            entry["registered_utc"] = _now()
            led["circuits"][rid] = entry
    save(led)
    return led


def evidence_worlds(led: dict, rid: str, all_worlds, axis_live=None) -> dict:
    """Split worlds into evidence and non-evidence. This is the teeth.

    Two subtractions, not one:

      1. A world used to invent or tune a circuit CANNOT confirm it. Charter v1
         §33, made arithmetic instead of a resolution.
      2. A world that does not expose the circuit's AXIS cannot test it either.
         The ledger's first run credited the SELECT circuit r0010 with "3
         untouched test worlds", two of which (Flip 7, Incan Gold) have no SELECT
         axis at all — every draw admits one option. Counting those as evidence
         is the same inflation this file exists to prevent, committed by the
         file itself on its first execution.

    `axis_live` maps world -> set of live axes. Omit it and every world counts as
    axis-eligible, which is the permissive reading and is flagged as such.
    """
    e = led["circuits"].get(rid)
    if not e:
        return {"untouched": [], "contaminated": list(all_worlds), "n_untouched": 0,
                "reason": "circuit not in ledger; treat all worlds as contaminated"}
    dirty = set(e.get("invented_on", [])) | set(e.get("tuned_on", []))
    axis = e.get("axis")
    eligible, ineligible = [], []
    for w in all_worlds:
        if axis_live is not None and axis and axis not in axis_live.get(w, set()):
            ineligible.append(w)
        else:
            eligible.append(w)
    untouched = [w for w in eligible if w not in dirty]
    return {"untouched": untouched,
            "contaminated": sorted(dirty & set(eligible)),
            "axis_ineligible": ineligible,
            "n_untouched": len(untouched),
            "axis_filter_applied": axis_live is not None}


def record_failure(rid: str, world: str, detail: str) -> None:
    """First failure is written once and never overwritten.

    Overwriting it is precisely how a circuit's history gets laundered: each new
    break replaces the last, and the record ends up showing only the most recent
    and most forgivable one.
    """
    led = load()
    e = led["circuits"].setdefault(rid, {"circuit_id": rid})
    if not e.get("first_failure"):
        e["first_failure"] = f"{world}: {detail} [{_now()}]"
    e.setdefault("subsequent_failures", []).append(f"{world}: {detail} [{_now()}]")
    save(led)


def record_split(parent: str, children: list, latent_distinction: str,
                 test_elsewhere: str) -> None:
    """Splits, not patches.

    A circuit that breaks in one world must NOT be special-cased for that world.
    The split has to name the latent distinction that forced it, and name where
    that distinction will be tested independently - otherwise the 'split' is a
    patch wearing a new identifier.
    """
    led = load()
    if not latent_distinction or not test_elsewhere:
        raise ValueError("a split requires BOTH the latent distinction that forced "
                         "it AND where that distinction will be tested elsewhere; "
                         "without those it is a patch, not a split")
    p = led["circuits"].setdefault(parent, {"circuit_id": parent})
    p.setdefault("split_history", []).append(
        {"into": children, "latent_distinction": latent_distinction,
         "will_be_tested_on": test_elsewhere, "when": _now()})
    p["current_scope"] = f"SUPERSEDED by {children} - retained as a fossil"
    for c in children:
        led["circuits"].setdefault(c, {
            "circuit_id": c, "split_history": [{"from": parent, "when": _now()}],
            "invented_on": p.get("invented_on", []) + p.get("tuned_on", []),
            "tuned_on": [], "predicted_worlds": [], "first_failure": None,
            "predicted_direction": "MUST BE REGISTERED BEFORE THE NEXT WORLD RUNS",
            "kill_condition": "MUST BE REGISTERED BEFORE THE NEXT WORLD RUNS",
            "current_scope": "new; inherits the parent's contamination"})
    save(led)


def report(all_worlds, axis_live=None) -> str:
    led = seed()
    lines = ["# Circuit ledger", "",
             "Worlds used to invent or tune a circuit are **not evidence for it**.",
             ""]
    for rid, e in sorted(led["circuits"].items()):
        ev = evidence_worlds(led, rid, all_worlds, axis_live)
        lines.append(f"## {rid} — {e.get('english','?')}  ({e.get('axis','?')})")
        lines.append(f"- definition: `{e.get('definition','?')}`")
        lines.append(f"- invented on: {e.get('invented_on') or '—'}"
                     f" | tuned on: {e.get('tuned_on') or '—'}")
        lines.append(f"- **untouched test worlds: {ev['n_untouched']}** "
                     f"{ev['untouched'] or '(none — NO INDEPENDENT EVIDENCE)'}")
        if ev.get("axis_ineligible"):
            lines.append(f"- cannot test it (no {e.get('axis')} axis): "
                         f"{ev['axis_ineligible']}")
        lines.append(f"- predicted: {e.get('predicted_direction','—')}")
        lines.append(f"- kill condition: {e.get('kill_condition','—')}")
        lines.append(f"- first failure: {e.get('first_failure') or 'none recorded'}")
        lines.append(f"- current scope: {e.get('current_scope','—')}")
        if e.get("provenance_note"):
            lines.append(f"- provenance: {e['provenance_note']}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    from ludus.bench.worlds import WORLD_BY_NAME
    import json as _j
    mx = ATLAS / "transfer_matrix.json"
    live = {}
    if mx.exists():
        for w, e in _j.loads(mx.read_text(encoding="utf-8"))["worlds"].items():
            ax = {"STOP"}
            if e.get("select_axis_is_live"):
                ax.add("SELECT")
            live[w] = ax
    txt = report(sorted(WORLD_BY_NAME), live or None)
    (ATLAS / "CIRCUIT_LEDGER.md").write_text(txt, encoding="utf-8")
    print(txt)
