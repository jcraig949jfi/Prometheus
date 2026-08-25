"""GATE-FIRE for the block-B leg and the preregistered merge rule.

The conclusion I least want, in order:
  1. "block B's collection wrote into block A's pinned ledgers" -- silent contamination of the
     population whose entire purpose is immutability;
  2. "the blocks disagree, so pooling is forbidden" -- the merge rule's clause with teeth, and
     the one a driver wanting its own floor met would be most tempted to soften.

So both are constructed here and both must be reported. Nothing below calls an LLM: the lane is
replaced by a stub, because a scoping test that needs the network is a test that will be skipped
on the day it matters.
"""
import json
import pathlib

import pytest

from ergon.probe import blocks


# ---------------------------------------------------------------- the containment hazard

def _snapshot(d):
    """Every file under `d` with its bytes. Not mtimes -- an idempotent rewrite is harmless,
    a byte change is not, and mtime would flag the first and miss nothing."""
    return {p.relative_to(d).as_posix(): p.read_bytes()
            for p in d.rglob("*") if p.is_file()}


def _live_ledgers():
    import ergon.probe.campaign as C
    return pathlib.Path(C.DIR).parent


def test_block_A_ledgers_are_untouched_by_a_block_B_collection(monkeypatch, tmp_path):
    """THE DANGEROUS ONE. `repointed` mutates module globals; a mistake writes block B's rows
    into block A's pinned ledgers. This does not assert the scoping works -- it snapshots
    block A's directory, drives a write against a stubbed lane, and proves not one byte moved.
    """
    import ergon.probe.campaign as C

    real_a = pathlib.Path(C.DIR)
    before = _snapshot(real_a)
    assert before, "block A's ledger directory is empty; this test would prove nothing"

    sent = []

    def _stub(*a, **k):
        sent.append(1)
        raise AssertionError("the lane must not be called by this test")

    monkeypatch.setattr(C, "call", _stub)
    monkeypatch.setattr(C, "DIR", tmp_path / "campaign")     # sandbox, as the dry-run does
    (tmp_path / "campaign").mkdir()

    with blocks.repointed("B") as d:
        C.log(event="gate_fire_probe", note="this row must land in block B's dir, not A's")
        assert C.DIR == d

    assert _snapshot(real_a) == before, "a block-B write reached block A's pinned ledgers"
    assert not sent


def test_a_sandboxed_driver_sandboxes_its_block_B_leg_too(monkeypatch, tmp_path):
    """THE DEFECT THIS FILE MISSED THE FIRST TIME, now pinned.

    `block_dir` originally returned a repo-absolute path, so a caller that had already
    re-pointed `campaign.DIR` into a sandbox got its block-B leg silently redirected back to
    the LIVE tree. The dry-run test does exactly that, and wrote 142 synthetic
    `executor: dryrun / host: TESTHOST` rows into the real block B prepass ledger before this
    was caught. Nothing was spent and nothing was lost -- the directory was untracked -- but a
    later scheduled firing would have computed block B's band read over invented rows.

    The original gate-fire suite proved block A was safe and never asked whether block B was.
    A containment test scoped to one of two directories is a containment test with a hole in
    it, which is the same shape as the packet-leak defect from earlier the same day: the check
    was pointed at the place the previous failure happened.
    """
    import ergon.probe.campaign as C

    live_blockb = _live_ledgers() / "campaign_blockB"
    existed = live_blockb.exists()
    before = _snapshot(live_blockb) if existed else None

    monkeypatch.setattr(C, "DIR", tmp_path / "campaign")
    (tmp_path / "campaign").mkdir()

    with blocks.repointed("B") as d:
        assert tmp_path in d.parents, f"block B escaped the sandbox to {d}"
        C.log(event="sandbox_probe")
        assert (d / "campaign_log.jsonl").exists()

    if existed:
        assert _snapshot(live_blockb) == before, "the sandboxed run wrote to the live block B"
    else:
        assert not live_blockb.exists(), (
            "a sandboxed run CREATED the live block B ledger directory -- the exact defect "
            "this test exists for")


def test_the_second_family_ledger_is_sandboxed_with_the_rest(monkeypatch, tmp_path):
    """Same hole, other path: a sandboxed run must not read or append to the live drip ledger,
    or a test's screen would be computed against production second-family rows.
    """
    import ergon.probe.campaign as C
    monkeypatch.setattr(C, "DIR", tmp_path / "campaign")
    (tmp_path / "campaign").mkdir()
    with blocks.repointed("B"):
        sf = pathlib.Path(C.SECOND_FAMILY_LEDGER)
        assert not sf.is_absolute() or tmp_path in sf.parents, \
            f"second-family ledger escaped the sandbox: {sf}"


def test_repointing_is_restored_even_when_the_body_raises(monkeypatch, tmp_path):
    """A collection that dies mid-flight must not leave the module pointed at block B: the
    next caller is `campaign._campaign()`, which would then write block A's rows into block
    B's directory -- the same contamination, in the other direction.
    """
    import ergon.probe.campaign as C
    # Sandboxed: `repointed` mkdirs its target, and this test has no business creating a
    # directory in the live ledger tree just to prove a restore works.
    monkeypatch.setattr(C, "DIR", tmp_path / "campaign")
    (tmp_path / "campaign").mkdir()
    before_dir, before_sf = C.DIR, C.SECOND_FAMILY_LEDGER
    with pytest.raises(RuntimeError):
        with blocks.repointed("B"):
            assert C.DIR != before_dir
            raise RuntimeError("boom")
    assert C.DIR == before_dir and C.SECOND_FAMILY_LEDGER == before_sf


def test_the_two_blocks_use_different_second_family_ledgers():
    """Block B's second-family rows must not append to block A's drip ledger: the
    cross-family screen intersects per block, and a shared ledger would silently screen block
    A against block B's rows.
    """
    assert (blocks.spec("A")["second_family_ledger"]
            != blocks.spec("B")["second_family_ledger"])


# ---------------------------------------------------------------- the identity of a block

def test_a_tampered_block_manifest_is_refused_ON_THE_SHA_PATH(monkeypatch, tmp_path):
    """A pin that cannot fail is not a pin. One trailing space on one row of 220 must refuse.

    The assertion names the SHA path specifically. An earlier version accepted "sha OR absent"
    in the message, which would have passed if the fixture simply pointed at a missing file --
    i.e. it could have been green while the sha comparison was never executed at all. An
    "either" assertion on an error message is a test that does not know what it proved.
    """
    rows = blocks.load("B")
    rows[7] = dict(rows[7], prompt=rows[7]["prompt"] + " ")     # one trailing space, 1 of 220
    tampered = tmp_path / "tampered.jsonl"
    tampered.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    assert tampered.exists(), "the fixture must exist, or this tests the absent-file path"

    # `ROOT / <absolute path>` yields the absolute path, so the loader reads the fixture.
    monkeypatch.setitem(blocks.BLOCKS["B"], "manifest", str(tampered))
    with pytest.raises(SystemExit) as e:
        blocks.load("B")
    msg = str(e.value)
    assert "REFUSED" in msg and "sha" in msg, msg
    assert blocks.spec("B")["sha16"] in msg, "the refusal must name the expected sha"


def test_the_row_count_is_checked_too(monkeypatch, tmp_path):
    """Dropping a row changes the sha, so this is belt-and-braces -- but the count is the
    check whose failure message a human can act on, and a silently short block is how a
    pooled n gets quietly smaller than the number reported beside it.
    """
    rows = blocks.load("B")[:-1]
    short = tmp_path / "short.jsonl"
    short.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    monkeypatch.setitem(blocks.BLOCKS["B"], "manifest", str(short))
    with pytest.raises(SystemExit) as e:
        blocks.load("B")
    assert "REFUSED" in str(e.value)


def test_a_uid_outside_the_namespace_is_refused(monkeypatch):
    """The namespaces are what make the blocks poolable without double counting. A block B
    row wearing a block A uid would be counted in both."""
    monkeypatch.setitem(blocks.BLOCKS["B"], "uid_prefix", "nearmiss_mix-M30-")
    with pytest.raises(SystemExit) as e:
        blocks.load("B")
    assert "namespace" in str(e.value)


def test_the_live_blocks_are_disjoint_in_uid_and_in_task_text():
    """Disjoint uids alone would not stop the same TASK appearing in both blocks under two
    names, which would double count it in the pooled read."""
    a, b = blocks.load("A"), blocks.load("B")
    assert not ({r["uid"] for r in a} & {r["uid"] for r in b})
    assert not ({r["prompt"] for r in a} & {r["prompt"] for r in b})


# ---------------------------------------------------------------- the merge rule

def _read(point, lo, hi, n):
    return {"tier_b_cross_family_screen":
            {"point_estimate": point, "n": n, "manifest_interval_95": [lo, hi]}}


def test_non_overlapping_intervals_FORBID_pooling():
    """The clause with teeth, and the conclusion the driver least wants: block B exists to
    meet a power floor, and this rule can refuse to let it. Constructed so the refusal is
    proven to fire rather than assumed.
    """
    m = blocks.merge_reading(_read(0.47, 0.40, 0.54, 194),
                             _read(0.68, 0.61, 0.75, 210))
    assert m["pooling"] == "FORBIDDEN"
    assert m["n_pooled"] is None
    assert "DISAGREEMENT IS THE FINDING" in m["reason"]
    assert m["block_A"] and m["block_B"], "both blocks must still be reported (§1)"


def test_touching_intervals_are_treated_as_overlapping():
    """A boundary case decided explicitly rather than by whichever comparison got typed:
    intervals that share an endpoint are NOT evidence of disagreement.
    """
    m = blocks.merge_reading(_read(0.47, 0.40, 0.54, 194), _read(0.60, 0.54, 0.66, 210))
    assert m["pooling"] == "PERMITTED"


def test_overlapping_intervals_permit_pooling_and_the_pooled_n_is_the_sum():
    m = blocks.merge_reading(_read(0.4742, 0.4040, 0.5445, 194),
                             _read(0.5000, 0.4300, 0.5700, 210))
    assert m["pooling"] == "PERMITTED"
    assert m["n_pooled"] == 404
    # n-weighted mean, which is accuracy over the disjoint union
    assert m["pooled_point_estimate"] == pytest.approx(
        (0.4742 * 194 + 0.5000 * 210) / 404, abs=5e-5)


def test_a_missing_second_family_leg_blocks_pooling_rather_than_falling_back():
    """HB-R1: the single-family number is not a weaker version of the cross-family one, it is
    the statistic the rule disqualifies. A block without a second-family leg must contribute
    NOTHING, not a substituted single-family figure.
    """
    m = blocks.merge_reading(_read(0.4742, 0.4040, 0.5445, 194),
                             {"tier_b_cross_family_screen": None,
                              "point_estimate": 0.51,
                              "point_estimate_post_screen_SINGLE_FAMILY": 0.49})
    assert m["pooling"] == "UNAVAILABLE"
    assert m["n_pooled"] is None
    assert "B" in m["reason"]


def test_pooled_n_alone_cannot_satisfy_the_floor_without_the_rule_being_consulted():
    """Guards the shape of the R13 check: 194 + 210 = 404 clears the floor of 300, but only
    when pooling is PERMITTED. A driver that read `n_pooled` without reading `pooling` would
    clear its own floor on two blocks that disagree -- which is the exact move the merge rule
    was written to prevent.
    """
    m = blocks.merge_reading(_read(0.47, 0.40, 0.54, 194), _read(0.68, 0.61, 0.75, 210))
    assert m["pooling"] == "FORBIDDEN"
    assert m.get("n_pooled") is None, ("n_pooled must be None when pooling is forbidden, so a "
                                       "careless reader gets a TypeError, not a passing floor")


# ---------------------------------------------------------------- registry / drip agreement

def test_the_drip_and_the_registry_agree_on_every_block_ledger_name():
    """Two files naming the same ledger by two constructions is how they come to disagree.

    `blocks.BLOCKS[b]["second_family_ledger"]` is what the campaign's cross-family screen
    READS; `drip_coldband.block_work(b)[2]` is the prefix the drip WRITES. If those drift, the
    drip collects block B's second family into a file the screen never opens, the screen stays
    UNAVAILABLE forever, and the campaign halts every firing while a ledger quietly fills up.
    Nothing would raise -- which is why it is asserted rather than assumed.
    """
    import ergon.probe.drip_coldband as D
    from ergon.probe.drip_coldband import _slug
    for b in D.BLOCK_ORDER:
        _, _, prefix = D.block_work(b)
        written = f"{prefix}{_slug('nvidia:nemotron-super-49b-v1')}.jsonl"
        read = pathlib.Path(blocks.spec(b)["second_family_ledger"]).name
        assert written == read, (
            f"block {b}: the drip writes {written!r} but the screen reads {read!r}")


def test_block_A_drip_ledger_name_is_unchanged_by_the_block_refactor():
    """Block A already holds 400 collected second-family rows under its original name. A
    prefix accidentally applied to block A would orphan them and silently re-collect.
    """
    import ergon.probe.drip_coldband as D
    _, _, prefix = D.block_work("A")
    assert prefix == "", "block A must keep its original, unprefixed ledger name"
    live = D.DRIP_DIR / f"{D._slug('nvidia:nemotron-super-49b-v1')}.jsonl"
    assert live.exists(), "block A's collected second-family ledger is missing"


def test_each_block_drips_its_own_rows_and_only_its_own():
    import ergon.probe.drip_coldband as D
    ga, wa, _ = D.block_work("A")
    gb, wb, _ = D.block_work("B")
    assert len(wa) == 2 * len(ga) and len(wb) == 2 * len(gb)
    assert not (set(ga) & set(gb)), "the two blocks' drip work sets share a uid"
