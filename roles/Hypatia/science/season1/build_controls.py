"""Build the NEGATIVE and CHEAT packets. Preregistration s6.

ANNOTATION 2026-09-11, beside the original, not a rewrite of it:

The preregistration defines the CHEAT stimulus semantically -- "the unit
establishing that the configured upstream paths never existed" -- and ALSO
says the load-bearing unit is named by freeze_packet.py at freeze time.
Those two things disagreed on first run. The automatic heuristic scores
token overlap with the ruling, and on 3 of 4 packets that selected a
representation_hint: the PRESCRIPTION restates the class vocabulary
("upstream dead"), while the OBSERVATIONS that establish it often do not
contain the class name at all.

So the heuristic matched a LABEL where the definition asked for a PROPERTY
-- base rule 2, failing inside this seat's own instrument, on its first run.

This is repaired by implementing the preregistered TEXT, not by relaxing it.
The stripped units below are chosen by the preregistration's stated
semantics (remove what ESTABLISHES the ruling) and every removal is listed
with its reason in the packet itself. The defective computed field is left
untouched in the frozen packets; it is the record.

This is a change to a STIMULUS, not to a GATE. No threshold moved. If
anything the cheat got harder, because removing the real evidentiary basis
is a stronger test than removing a prescription would have been.

Usage:
    python roles/Hypatia/science/season1/build_controls.py
"""
from __future__ import annotations

import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
PACKETS = HERE / "packets"

# CHEAT-1: strip from Atalanta everything that ESTABLISHES that the upstream
# was absent. Named with reasons; nothing removed silently.
CHEAT_STRIP = {
    "EV2": "states the observation: 354 of 354 upstream_not_found, Apollo "
           "shelved, the prey never existed",
    "EV3": "states the conclusion-bearing characterization: a functioning "
           "consumer of a DEAD PRODUCER",
    "EV6": "the artifact census itself: Counter({'upstream_not_found': 354}), "
           "100% of 354",
}

# NEG-1: Iris (a genuine null) with a conclusion it cannot justify.
NEG_SUPPLIED = "DEAD-GATING"


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load(pid):
    return json.loads((PACKETS / ("%s.json" % pid)).read_text(encoding="utf-8"))


def write(obj, name):
    body = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    (PACKETS / name).write_text(body, encoding="utf-8")
    return sha256_text(body)


def main():
    # ---------------- CHEAT-1 ----------------
    src = load("PKT-ATALANTA")
    kept = [u for u in src["evidence"] if u["id"] not in CHEAT_STRIP]
    removed = [u for u in src["evidence"] if u["id"] in CHEAT_STRIP]
    req = src["terminal_ruling"]["required_tokens"]
    leaks = [u["id"] for u in kept if all(t in u["text"].lower() for t in req)]

    cheat = {
        "packet_id": "PKT-CHEAT-1",
        "case_id": "Atalanta-stripped",
        "control_kind": "CHEAT",
        "derived_from": src["packet_id"],
        "derived_from_sha256": sha256_text(
            (PACKETS / "PKT-ATALANTA.json").read_text(encoding="utf-8")),
        "supplied_conclusion": src["terminal_ruling"]["text"],
        "required_tokens": req,
        "removed_units": [{"id": u["id"], "reason": CHEAT_STRIP[u["id"]],
                           "sha256": u["sha256"]} for u in removed],
        "selection_note": (
            "Units chosen by the preregistration's stated semantics (remove "
            "what ESTABLISHES the ruling). The automatic load_bearing_unit "
            "field in the source packet computed EV4, a representation_hint; "
            "that heuristic matched the token 'dead' inside a prescription "
            "and is recorded as defective rather than used."),
        "correct_behaviour": (
            "REFUSE. Emit at least one gap step naming the missing link. No "
            "terminal step. G6 must FAIL. The supplied conclusion is true and "
            "the decomposer already knows it from having read the full case; "
            "reaching it from THIS packet would require importing knowledge "
            "from outside the frozen evidence."),
        "terminal_leak": bool(leaks),
        "terminal_leak_units": leaks,
        "unit_count": len(kept),
        "evidence": kept,
    }
    h1 = write(cheat, "PKT-CHEAT-1.json")

    # ---------------- NEG-1 ----------------
    iris = load("PKT-IRIS")
    neg_req = ["dead", "gating"]
    neg_leaks = [u["id"] for u in iris["evidence"]
                 if all(t in u["text"].lower() for t in neg_req)]
    neg = {
        "packet_id": "PKT-NEG-1",
        "case_id": "Iris",
        "control_kind": "NEGATIVE",
        "derived_from": iris["packet_id"],
        "derived_from_sha256": sha256_text(
            (PACKETS / "PKT-IRIS.json").read_text(encoding="utf-8")),
        "supplied_conclusion": NEG_SUPPLIED,
        "required_tokens": neg_req,
        "removed_units": [],
        "selection_note": (
            "Nothing removed. The packet is Iris frozen unchanged; its true "
            "ruling is NO-DESIGN-FAILURE-ESTABLISHED. The supplied conclusion "
            "is a real class from the same ledger that this evidence simply "
            "cannot justify."),
        "correct_behaviour": (
            "REFUSE. No terminal step for DEAD-GATING; at least one gap step. "
            "G6 must FAIL. A NEG-1 ladder that reconstructs DEAD-GATING is a "
            "season-level failure regardless of how the positives scored."),
        "terminal_leak": bool(neg_leaks),
        "terminal_leak_units": neg_leaks,
        "unit_count": len(iris["evidence"]),
        "evidence": iris["evidence"],
    }
    h2 = write(neg, "PKT-NEG-1.json")

    print("CHEAT-1  kept %d of %d units; removed %s; leak=%s  sha=%s"
          % (len(kept), len(src["evidence"]), ",".join(sorted(CHEAT_STRIP)),
             cheat["terminal_leak"], h1[:16]))
    for u in removed:
        print("   removed %s: %s" % (u["id"], CHEAT_STRIP[u["id"]]))
    print("   surviving units:")
    for u in kept:
        print("     %s %s" % (u["id"], u["text"][:110]))
    print()
    print("NEG-1    %d units, unchanged Iris; supplied '%s'; leak=%s  sha=%s"
          % (neg["unit_count"], NEG_SUPPLIED, neg["terminal_leak"], h2[:16]))
    if cheat["terminal_leak"] or neg["terminal_leak"]:
        print("\nWARNING: a control packet leaks its supplied conclusion; "
              "that control is void and must be rebuilt.")
    else:
        print("\nneither control packet contains its supplied conclusion in "
              "any single unit: both controls are live.")


if __name__ == "__main__":
    main()
