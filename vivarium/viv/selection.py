"""E6 -- make the candidate set class-A in the SUBSTRATE, not only the queue.

Harmonia S15 found seven of eight selection mechanisms are class B:
information-theoretically absent from the substrate, because only the survivor
is ever submitted. Vivarium's queue already fixes that on its own side -- the
whole candidate set is registered before selection and the unchosen are
cancelled, never deleted -- but SFE sees one experiment and cannot tell a
best-of-twenty from the only one anybody tried.

SFE has the container for this: a `selection` family, whose members carry roles
`selected` and `alternative`, and whose own findings include

    SELECTION_WITHOUT_ALTERNATIVES
      "a selected member with no recorded alternatives: the selection is
       asserted but not visible"

which is exactly the accusation this module exists to answer.

THE ALTERNATIVES ARE REGISTERED, NOT INVENTED. A cancelled candidate has no
SFE object, so it cannot be a member of anything. It is therefore registered as
an experiment with `commit=False`, which SFE defines as a PLAN: no budget
debited, prospective window still open, non-executable. That is precisely what
a candidate that was proposed and not chosen IS, and it is the only shape in
the engine that says so without claiming an execution that never happened.

WHAT THIS IS NOT. It does not run the alternatives, does not score them, and
does not say why one was chosen -- the selection RULE is Archaeon's and lives
in `source_evidence`. This records only that the alternatives existed, were
registered before the survivor ran, and were not executed.

The family manifest is sealed by SFE at creation and declares the full set by
queue id and spec_hash, so even the alternatives' identities are fixed at the
moment the family is created rather than asserted afterwards.
"""
from __future__ import annotations

from typing import Optional

#: SFE family kind and member roles. Its vocabulary, not ours.
FAMILY_KIND = "selection"
ROLE_SELECTED = "selected"
ROLE_ALTERNATIVE = "alternative"


class SelectionBindError(RuntimeError):
    """The selection family could not be recorded. Never fatal to a run."""


def bind(client, *, candidate_set_id: str, members: list, selected_row,
         selected_exp_id: str, world_id: str, log=lambda *_a: None) -> dict:
    """Create the selection family and record who was chosen over whom.

    `members` is every queue row sharing the candidate_set_id, selected one
    included. `selected_exp_id` is the experiment that actually ran.

    Returns a record of what was bound. Raises SelectionBindError on failure;
    the caller decides what that means, and for a completed run it means the
    binding is missing, not that the science is."""
    alternatives = [m for m in members
                    if str(m["experiment_id"]) != str(
                        selected_row["experiment_id"])]

    manifest = {
        # SFE reads `planned_members` and compares it to what was recorded --
        # counting, not judgement. Declaring the full set here is what makes a
        # later divergence visible instead of invisible.
        "planned_members": len(members),
        "candidate_set_id": candidate_set_id,
        "selection_recorded_by": "vivarium",
        "candidates": [
            {"queue_experiment_id": str(m["experiment_id"]),
             "spec_hash": m["spec_hash"],
             "queue_status": m["status"],
             "role": (ROLE_SELECTED
                      if str(m["experiment_id"])
                      == str(selected_row["experiment_id"])
                      else ROLE_ALTERNATIVE)}
            for m in members],
        "note": ("The alternatives are registered as UNCOMMITTED experiments: "
                 "SFE plans, no budget debited, never executed. That is what a "
                 "candidate proposed and not chosen is. Vivarium records that "
                 "they existed and were not run; it does not record why the "
                 "survivor won -- the selection rule is the producer's and "
                 "lives in source_evidence."),
    }

    try:
        # EngineClient.family() returns the whole family DICT, not the id.
        # Found live on 2026-09-06: the dict went into the members URL and the
        # binding failed with "URL can't contain control characters".
        created = client.family(FAMILY_KIND, manifest=manifest,
                                name="cs:" + candidate_set_id)
        family_id = (created.get("family_id")
                     if isinstance(created, dict) else created)
        if not isinstance(family_id, str) or not family_id:
            raise SelectionBindError(
                "the engine returned no usable family_id: %r" % (created,))
    except SelectionBindError:
        raise
    except Exception as exc:                        # noqa: BLE001
        raise SelectionBindError("could not create the selection family: %s"
                                 % exc) from exc

    bound = {"family_id": family_id, "candidate_set_id": candidate_set_id,
             "planned_members": len(members), "selected": None,
             "alternatives": [], "errors": []}

    try:
        client.family_member(family_id, "experiment", selected_exp_id,
                             role=ROLE_SELECTED)
        bound["selected"] = {"exp_id": selected_exp_id,
                             "queue_experiment_id":
                                 str(selected_row["experiment_id"])}
    except Exception as exc:                        # noqa: BLE001
        raise SelectionBindError("could not record the selected member: %s"
                                 % exc) from exc

    for alt in alternatives:
        try:
            # commit=False: a PLAN. No budget, non-executable, and honest --
            # this candidate really was proposed and really was not run.
            reg = client.experiment(world_id, alt["experiment_spec"],
                                    commit=False, enqueue=False,
                                    kind=(alt["experiment_spec"].get("work")
                                          or {}).get("kind", "experiment"))
            client.family_member(family_id, "experiment", reg["exp_id"],
                                 role=ROLE_ALTERNATIVE)
            bound["alternatives"].append(
                {"exp_id": reg["exp_id"],
                 "queue_experiment_id": str(alt["experiment_id"]),
                 "queue_status": alt["status"],
                 "spec_hash": alt["spec_hash"]})
        except Exception as exc:                    # noqa: BLE001
            # One unrecordable alternative must not cost the others, and it
            # must not be silent: an incomplete binding is a weaker claim than
            # a complete one and has to say so.
            bound["errors"].append({"queue_experiment_id":
                                    str(alt["experiment_id"]),
                                    "error": str(exc)[:300]})
            log("[viv] selection: alternative %s could not be recorded: %s"
                % (alt["experiment_id"], str(exc)[:200]))

    bound["alternatives_recorded"] = len(bound["alternatives"])
    bound["alternatives_expected"] = len(alternatives)
    bound["complete"] = (not bound["errors"]
                         and bound["alternatives_recorded"]
                         == bound["alternatives_expected"])
    bound["selection_visible"] = (bound["selected"] is not None
                                  and bound["alternatives_recorded"] >= 1)
    return bound
