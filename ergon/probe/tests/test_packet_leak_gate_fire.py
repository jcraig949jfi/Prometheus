"""GATE-FIRE for the packet-leak checks: constructed worlds where each check MUST fail.

WHY THIS FILE EXISTS. On 2026-08-25 the packet layer was found carrying two perfect arm labels
at once -- a lead line present on 2 of 6 arms (400/400 separating) and a per-arm numeric slug
band (+40000/+50000/+60000/+70000, 200/200 separating). Three checks were live at the time and
all three passed. That is the whole lesson: the checks had never been shown capable of failing.

So, under the generalized gate-fire rule -- *every measurement needs a constructed world where
its headline conclusion is known in advance, preferably the conclusion the experimenter least
wants* -- each check below is handed a packet set carrying the exact defect it claims to catch,
and must name it. The pattern is `test_block_pinning.py`'s: do not assert the property holds,
construct the violation and prove the check detects it.

The conclusion I least want is "the packets leak and P2 cannot run." Every test here is built
to produce it, so a green suite means the checks can still say it.

None of this calls an LLM. Every fixture is a literal string.
"""
import pytest

from ergon.probe.packet_render import MODAL_SPARSITY, render, synthetic_slug
from ergon.probe.packet_invariants import (
    payload_of, slug_bands_not_separable, slug_pool_shared, sparsity_arm_invariant,
    template_conformance,
)

CARRYING = ("F-null", "F-prom-retrieved", "F-generic")
BASE = "How many primes are in the following list?\n(1) 91 (2) 97\n"


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


def _clean_prompts(task="task-0"):
    """A leak-free packet set: every arm through one renderer, indices in the real range."""
    prompts = {"F0": BASE}
    for i, arm in enumerate(CARRYING):
        slug = synthetic_slug("M30", (arm, task), 200)
        prompts[arm] = render(slug, [f"method-{i}", "sqrt-bound"]) + "\n\n" + BASE
    return prompts


# --------------------------------------------------------------------------------------
# NEGATIVE CONTROL FIRST. A check that fails on everything detects nothing; without this,
# every positive below is satisfied by a function that returns False unconditionally.
# --------------------------------------------------------------------------------------

def test_negative_control_clean_packets_pass_every_check():
    """Note the population: the band check is fed 60 tasks, not one. On a single task each arm
    contributes one index and two singletons are trivially "separable", so an n=1 negative
    control would fail for a reason that has nothing to do with leakage. Getting this wrong
    once is what made it worth writing down -- see the n=1 test below, which pins the fact.
    """
    per_task = []
    for t in range(60):
        prompts = _clean_prompts(f"task-{t}")
        ok, bad, slots = template_conformance(prompts, CARRYING)
        assert ok, f"clean packets rejected -- the check is not discriminating: {bad}"
        assert len(slots) == len(CARRYING)
        assert slug_pool_shared(slots)[0]
        assert sparsity_arm_invariant(slots)[0]
        per_task.append(slots)
    assert slug_bands_not_separable(per_task)[0]


# --------------------------------------------------------------------------------------
# DEFECT 1 -- the lead line. The historical instance, reproduced exactly.
# --------------------------------------------------------------------------------------

def test_a_caller_prepended_lead_line_is_detected():
    """The exact 2026-08-25 defect: campaign.py prefixed "A prior attempt record:\\n" onto
    F-null and F-prom only. The check that was supposed to catch it instead STRIPPED the line
    before matching, with the comment "shared lead line" -- it was on two arms of six.
    """
    prompts = _clean_prompts()
    prompts["F-null"] = "A prior attempt record:\n" + prompts["F-null"]

    ok, bad, _ = template_conformance(prompts, CARRYING)
    assert not ok, "a lead line on ONE arm passed template conformance -- the 08-25 defect"
    assert "F-null" in bad, f"detected a defect but named the wrong arm: {list(bad)}"
    assert "F-generic" not in bad, "flagged a clean arm; the check is not localising"


def test_a_trailing_caller_suffix_is_detected_by_the_invariant_SET():
    """Prefixes are the instance that happened; the class is anything a caller can attach.
    Checking only the side that burned us last time is how instance 5 gets in.

    FOUND BY THIS TEST, and kept as written rather than papered over: `template_conformance`
    does NOT catch a trailing suffix. The sparsity slot is captured greedily to end-of-string
    (it has to be -- the real block is multi-line and varies per record), so anything appended
    is swallowed INTO that slot and the packet still conforms.

    The conformance check is therefore not sufficient alone, and tightening the sparsity
    pattern is the wrong fix: it would make a legitimate record variation look like a defect.
    What closes the class is the SLOT OBLIGATION -- a suffix that differs by arm makes the
    sparsity slot differ by arm, and INVARIANT 6c fails. A suffix identical across all arms is
    absorbed silently, and that is correct: an arm-invariant suffix is not an arm label.

    So the property "no caller-attached arm label" is carried by conformance AND 6c together,
    never by conformance alone. That is asserted here so the division cannot be forgotten.
    """
    prompts = _clean_prompts()
    prompts["F-generic"] = prompts["F-generic"] + "\n(generic advice set)"

    conforms, _, slots = template_conformance(prompts, CARRYING)
    assert conforms, ("if this ever starts failing the greedy-sparsity analysis above is "
                      "stale and the reasoning below must be re-derived, not re-asserted")
    assert "(generic advice set)" in slots["F-generic"]["sparsity"], "suffix went elsewhere"

    ok, diffs = sparsity_arm_invariant(slots)
    assert not ok, "a per-arm trailing suffix passed BOTH checks -- the class is open"
    assert "F-generic" in diffs


# --------------------------------------------------------------------------------------
# DEFECT 2 -- the numeric band. Invisible to every shape abstraction, by construction.
# --------------------------------------------------------------------------------------

def test_a_per_arm_numeric_slug_band_is_detected():
    """The +40000 band. No shape check could ever have caught this: `envelope_shape` and
    `framing_skeleton` both map digit runs to `#` in order to make shape comparable, so they
    delete precisely the bytes that carried the label.
    """
    per_task = []
    for i in range(20):
        per_task.append({
            "F-prom-retrieved": {"slug": f"nearmiss_mix-M30-{i:05d}", "items": "a",
                                 "sparsity": MODAL_SPARSITY},
            "F-generic": {"slug": f"nearmiss_mix-M30-{i + 40000:05d}", "items": "a",
                          "sparsity": MODAL_SPARSITY},
        })
    ok, detail = slug_bands_not_separable(per_task)
    assert not ok, "a disjoint per-arm index band passed -- the digit-label defect"
    assert "F-generic|F-prom-retrieved" in detail["separable_pairs"]


def test_overlapping_indices_are_not_flagged_as_a_band():
    """Arms SHOULD have different slug indices -- they identify different records. Only
    disjoint bands are a label. A check that demanded equality would forbid the design.
    """
    per_task = [{
        "F-prom-retrieved": {"slug": f"nearmiss_mix-M30-{i:05d}", "items": "a",
                             "sparsity": MODAL_SPARSITY},
        "F-generic": {"slug": f"nearmiss_mix-M30-{(i * 7 + 3) % 200:05d}", "items": "a",
                      "sparsity": MODAL_SPARSITY},
    } for i in range(20)]
    assert slug_bands_not_separable(per_task)[0]


def test_one_packet_cannot_reveal_a_band_which_is_why_this_check_is_population_scope():
    """Documents the scoping decision as a test rather than a docstring: given a single task,
    the +40000 offset is undetectable -- one value per arm, nothing to compare against. The
    band is a property of the distribution, so the check runs over the manifest.
    """
    single = [{
        "F-prom-retrieved": {"slug": "nearmiss_mix-M30-00007", "items": "a",
                             "sparsity": MODAL_SPARSITY},
        "F-generic": {"slug": "nearmiss_mix-M30-40007", "items": "a",
                      "sparsity": MODAL_SPARSITY},
    }]
    ok, _ = slug_bands_not_separable(single)
    assert not ok, ("with n=1 the two singletons are trivially separable, so this fires -- "
                    "harmless here, but it is why the honest read needs the population")


# --------------------------------------------------------------------------------------
# DEFECT 3 -- a label in words, and DEFECT 4 -- an arm editing the record it reports.
# --------------------------------------------------------------------------------------

def test_a_pool_token_naming_the_arm_is_detected():
    slots = {"F-generic": {"slug": "generic_pool-M30-00007", "items": "a",
                           "sparsity": MODAL_SPARSITY},
             "F-null": {"slug": "nearmiss_mix-M30-00007", "items": "a",
                        "sparsity": MODAL_SPARSITY}}
    ok, pools = slug_pool_shared(slots)
    assert not ok and set(pools.values()) == {"generic_pool", "nearmiss_mix"}


def test_an_arm_varying_the_sparsity_block_is_detected():
    slots = {"F-null": {"slug": "nearmiss_mix-M30-00007", "items": "a",
                        "sparsity": MODAL_SPARSITY},
             "F-prom-retrieved": {"slug": "nearmiss_mix-M30-00007", "items": "a",
                                  "sparsity": MODAL_SPARSITY + "\n  attempt_text: absent"}}
    assert not sparsity_arm_invariant(slots)[0]


def test_items_may_differ_freely_because_items_are_the_treatment():
    """The exemption, asserted. A check forbidding all cross-arm difference would forbid the
    factorial; naming which slot may differ is the entire content of the isomorphism claim.
    """
    prompts = {"F0": BASE}
    prompts["F-prom-retrieved"] = render("nearmiss_mix-M30-00007", ["trial-division"]) \
        + "\n\n" + BASE
    prompts["F-prom+hint"] = render("nearmiss_mix-M30-00031",
                                    ["trial-division", "divide-out-2-3-and-5-first",
                                     "use-last-digit-and-digit-sum"]) + "\n\n" + BASE
    arms = ("F-prom-retrieved", "F-prom+hint")
    ok, bad, slots = template_conformance(prompts, arms)
    assert ok, bad
    assert slots["F-prom-retrieved"]["items"] != slots["F-prom+hint"]["items"]
    assert slug_pool_shared(slots)[0] and sparsity_arm_invariant(slots)[0]


# --------------------------------------------------------------------------------------
# THE API GUARD -- make the defect unconstructible, not merely detectable.
# --------------------------------------------------------------------------------------

def test_synthetic_slug_refuses_a_caller_chosen_index_range():
    """The +40000 band was possible because the caller chose the integer. It no longer can:
    the index is hashed into a caller-declared span, so producing a disjoint band requires
    lying about the span rather than adding a number.
    """
    with pytest.raises(ValueError):
        synthetic_slug("M30", ("F-generic", "task-0"), 0)
    with pytest.raises(ValueError):
        synthetic_slug("M30", ("F-generic", "task-0"), None)
    with pytest.raises(ValueError):        # the older `generic_pool` defect, still guarded
        synthetic_slug("M30", ("F-generic", "task-0"), 200, pool="generic_pool")


def test_synthetic_slug_stays_inside_the_declared_span_and_is_deterministic():
    vals = {synthetic_slug("M30", ("F-generic", f"task-{i}"), 200) for i in range(200)}
    idxs = [int(v.rsplit("-", 1)[1]) for v in vals]
    assert all(0 <= i < 200 for i in idxs), "an index escaped the real task-id range"
    assert synthetic_slug("M30", ("F-hint", "task-9"), 200) == \
        synthetic_slug("M30", ("F-hint", "task-9"), 200), "slugs must be reproducible"


# --------------------------------------------------------------------------------------
# REGRESSION on the live manifest -- the defect is gone from the thing that ships.
# --------------------------------------------------------------------------------------

def test_live_arms_conform_with_no_stripping_and_no_band(manifest_rows, arms):
    """Supersedes the test that stripped the lead line before matching. The strip is the
    defect: this asserts on the payload EXACTLY as the solver would receive it.
    """
    residue_arms = ("F-null", "F-prom-retrieved", "F-generic",
                    "F-hint", "F-null+hint", "F-prom+hint")
    per_task = []
    for r in manifest_rows[:40]:
        uid = r["uid"]
        prompts = {a: arms.prompt(a, uid) for a in ("F0",) + residue_arms}
        ok, bad, slots = template_conformance(prompts, residue_arms)
        assert ok, f"{uid}: payload did not conform without stripping: {bad}"
        assert slug_pool_shared(slots)[0]
        assert sparsity_arm_invariant(slots)[0]
        per_task.append(slots)
    ok, detail = slug_bands_not_separable(per_task)
    assert ok, f"a per-arm slug band is live on the manifest: {detail['separable_pairs']}"


def test_every_live_arm_carries_the_lead_line_or_none_does(manifest_rows, arms):
    """The specific 400/400 asymmetry, pinned as its own regression. Stated as a partition so
    it cannot be satisfied by deleting the line from the template and forgetting one caller.
    """
    residue_arms = ("F-null", "F-prom-retrieved", "F-generic",
                    "F-hint", "F-null+hint", "F-prom+hint")
    for r in manifest_rows[:25]:
        uid = r["uid"]
        base = arms.prompt("F0", uid)
        has = {a: payload_of(arms.prompt(a, uid), base).startswith("A prior attempt record:")
               for a in residue_arms}
        assert len(set(has.values())) == 1, f"{uid}: lead line splits the arms: {has}"
