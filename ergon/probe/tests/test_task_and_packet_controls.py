"""The non-LLM controls, as gates rather than scripts.

A control that lives in a script only runs when someone remembers to run it. These are the
invariants that currently HOLD — so they become regression gates and cannot silently break —
plus one xfail recording a real, filed defect rather than hiding it.

Every check here is a computation over the manifest and the rendered prompts. No API calls.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def manifest_rows():
    import ergon.probe.campaign as C
    return C.manifest()


@pytest.fixture(scope="module")
def arms(manifest_rows):
    import ergon.probe.campaign as C
    gold = {r["uid"]: r["gold_int"] for r in manifest_rows}
    try:
        return C.Arms(manifest_rows, gold)
    except Exception as e:                      # no prepass pool on a fresh clone
        pytest.skip(f"no residue pool available: {type(e).__name__}")


# ------------------------------------------------------------------ task-level controls

def test_task_family_is_well_posed(manifest_rows):
    """A deterministic program must recover gold from the PROMPT TEXT at 1.0000.

    If this fails, no LLM number computed on this manifest means anything — the gold is wrong,
    or the prompt does not determine the answer.
    """
    from ergon.probe.task_controls import deterministic_solver
    res = deterministic_solver(manifest_rows)
    assert res["agreement"] == 1.0, f"gold not reproducible: {res['disagreements']}"


def test_uid_index_does_not_predict_the_answer(manifest_rows):
    """The v1 defect was a manifest whose index predicted the answer at 0.921. Verified here
    INDEPENDENTLY of the generator's own decorrelation guard — a guard checked only by the
    code that implements it is not checked."""
    from ergon.probe.task_controls import uid_decorrelation
    res = uid_decorrelation(manifest_rows)
    assert res["abs_r_under_0_1"], f"uid index correlates with gold: r={res['pearson_r']}"


def test_surface_shortcut_floor_is_recorded_not_assumed(manifest_rows):
    """The attainable-WITHOUT-REASONING floor must stay measured and visible.

    This does not gate on a value — a family may legitimately have a high heuristic floor. It
    gates on the floor being computable and materially above chance being NOTICED, because the
    band's headroom argument is reasoned against chance and the real floor is higher.
    See ergon/probe/FINDING_heuristic_floor_2026-08-24.md.
    """
    from ergon.probe.task_controls import surface_shortcuts
    res = surface_shortcuts(manifest_rows)
    best = max(v["cv_accuracy"] for v in res["features"].values())
    assert best > res["chance_majority_class"], "no surface feature beats chance at all — " \
                                                "suspicious; the control may be broken"
    # the measured floor on this family; if it moves a lot, the finding needs restating
    assert best > 0.45, f"heuristic floor dropped to {best}; re-read the heuristic-floor finding"


# ------------------------------------------------------------------ packet-level invariants

def test_every_arm_prompt_ends_with_the_f0_base(manifest_rows, arms):
    """DECIDABLE. F0 carries no packet, so F0's prompt IS the base. A single differing byte is
    a channel by which an arm can be identified, and no classifier-at-chance result rules it
    out. This is the C1 renderer fix, held as a gate rather than a memory."""
    from ergon.probe.packet_invariants import base_identical
    uids = [r["uid"] for r in manifest_rows[:25]]
    for uid in uids:
        prompts = {a: arms.prompt(a, uid)
                   for a in ("F0", "F-null", "F-generic", "F-prom-retrieved")}
        ok, diffs = base_identical(prompts)
        assert ok, f"{uid}: arm base differs from F0 — {list(diffs)}"


def test_no_verbatim_gold_in_non_oracle_payloads(manifest_rows, arms):
    from ergon.probe.packet_invariants import gold_substring_scan
    gold = {r["uid"]: r["gold_int"] for r in manifest_rows}
    for r in manifest_rows[:25]:
        uid = r["uid"]
        prompts = {a: arms.prompt(a, uid)
                   for a in ("F0", "F-null", "F-generic", "F-prom-retrieved")}
        ok, hits = gold_substring_scan(prompts, gold[uid])
        assert ok, f"{uid}: gold asserted in a non-oracle payload — {hits}"


def test_every_residue_arm_is_generated_by_the_one_template(manifest_rows, arms):
    """STRUCTURAL, not heuristic: every residue-carrying arm's packet must match the single
    template exactly, so shape cannot identify the arm BY CONSTRUCTION.

    This replaces two weaker checks. Per-task envelope equality was too strict (a redacted
    sequence number made 21/200 packets differ). Framing-multiset equality was subtly wrong —
    the abstraction erased words but preserved LIST LENGTH, so a one-item census looked
    shape-different from a five-item one though both came from the same frame. Matching the
    template directly needs no abstraction at all.

    Closes the defect previously carried here as a strict xfail: F-generic was a prose
    paragraph while F-null/F-prom were bracketed records. All six now render through
    packet_render.render.
    """
    from ergon.probe.packet_render import matches_template
    from ergon.probe.packet_invariants import payload_of
    residue_arms = ("F-null", "F-prom-retrieved", "F-generic",
                    "F-hint", "F-null+hint", "F-prom+hint")
    pools = set()
    for r in manifest_rows[:40]:
        uid = r["uid"]
        base = arms.prompt("F0", uid)
        for a in residue_arms:
            payload = payload_of(arms.prompt(a, uid), base)
            # THE STRIP IS GONE. It used to remove a "shared lead line" from F-null and
            # F-prom before matching. The line was not shared -- it was on those two arms and
            # not the other four, a 400/400 arm label -- and deleting it here is precisely why
            # three checks passed over it for a day. The lead line now lives in TEMPLATE, so
            # the full payload matches with nothing removed. Never re-introduce a per-arm
            # exemption in a check whose job is to prove the arms are indistinguishable.
            ok, slots = matches_template(payload)
            assert ok, f"{uid}/{a}: packet was NOT produced by the shared template"
            pools.add(slots["slug"].split("-")[0])
    assert len(pools) == 1, f"the slug pool token differs by arm — a readable label: {pools}"
    # NOT SUFFICIENT, and the gap is recorded here because it cost a day: splitting the slug on
    # "-" and keeping [0] discards the INDEX, which is where the +40000/+50000/+60000/+70000
    # per-arm bands lived. The digits are checked at population scope by
    # `packet_invariants.slug_bands_not_separable`, gate-fired in test_packet_leak_gate_fire.py.
    # A per-task test cannot see a band: one index per arm has nothing to be separable from.


def test_the_factorial_cells_exist_and_differ_only_in_content(manifest_rows, arms):
    """The 2x2 the redesign ruling requires: residue absent/present x method-hint
    absent/present. The ruling rejected subtraction ("+.08 - +.05 = +.03 is not a justified
    decomposition"), so the cells must be jointly runnable and shape-matched, not differenced.
    """
    from ergon.probe.packet_render import matches_template
    from ergon.probe.packet_invariants import payload_of
    uid = manifest_rows[0]["uid"]
    base = arms.prompt("F0", uid)
    cells = {"residue-,hint-": "F-generic", "residue-,hint+": "F-hint",
             "residue+,hint-": "F-prom-retrieved", "residue+,hint+": "F-prom+hint"}
    items = {}
    for name, arm in cells.items():
        payload = payload_of(arms.prompt(arm, uid), base)   # no per-arm strip; see above
        ok, slots = matches_template(payload)
        assert ok, f"{name} ({arm}) is not template-generated"
        items[name] = slots["items"]
    assert items["residue-,hint+"] != items["residue-,hint-"], "the hint cell carries no hint"
    assert items["residue+,hint+"] != items["residue+,hint-"], "hint absent from residue+hint"
    from ergon.probe.campaign import HINT_ITEMS
    assert HINT_ITEMS[0] in items["residue+,hint+"], "the saturated hint is not fully supplied"
