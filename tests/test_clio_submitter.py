"""Tests for clio_submitter (Clio v0.3)."""
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

import clio_submitter  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures — fake Sigma kernel
# ---------------------------------------------------------------------------

@dataclass
class _FakeClaim:
    id: str
    target_name: str
    hypothesis: str


class FakeKernel:
    """Records every CLAIM call for assertion."""

    def __init__(self):
        self.claims_made: list[dict] = []
        self._counter = 0

    def CLAIM(self, **kw):
        self._counter += 1
        cid = f"claim_fake_{self._counter:06d}"
        self.claims_made.append(kw)
        return _FakeClaim(id=cid, target_name=kw["target_name"], hypothesis=kw["hypothesis"])


class FailingKernel:
    """Always raises on CLAIM."""
    def CLAIM(self, **kw):
        raise RuntimeError("simulated kernel failure")


SAMPLE_EXTRACTION = {
    "id": 17,
    "paper_id": 42,
    "claim_index": 0,
    "claim_text": "The Mahler measure has minimum 1.21 in the totally-real case.",
    "claim_type": "theorem",
    "paradigm_hint": "P12",
    "open_problem_hint": "Schinzel-Zassenhaus conjecture",
    "falsifiable": True,
    "confidence": 0.85,
    "paper_external_id": "2605.99999v1",
    "paper_title": "On the Mahler measure of Lehmer polynomials",
    "paper_url": "http://arxiv.org/abs/2605.99999v1",
    "paper_abstract": "We prove a new lower bound...",
}


# ---------------------------------------------------------------------------
# kill_path_for — pure function
# ---------------------------------------------------------------------------

def test_kill_path_for_theorem():
    kp = clio_submitter.kill_path_for("theorem")
    assert "counterexample" in kp or "proof" in kp


def test_kill_path_for_conjecture():
    assert "counterexample" in clio_submitter.kill_path_for("conjecture")


def test_kill_path_for_empirical():
    assert "replicate" in clio_submitter.kill_path_for("empirical")


def test_kill_path_for_unknown_falls_back():
    assert clio_submitter.kill_path_for("not-a-type") == clio_submitter.DEFAULT_KILL_PATH
    assert clio_submitter.kill_path_for(None) == clio_submitter.DEFAULT_KILL_PATH
    assert clio_submitter.kill_path_for("") == clio_submitter.DEFAULT_KILL_PATH


def test_kill_path_is_case_insensitive():
    assert clio_submitter.kill_path_for("Theorem") == clio_submitter.kill_path_for("theorem")
    assert clio_submitter.kill_path_for("THEOREM ") == clio_submitter.kill_path_for("theorem")


def test_kill_path_always_returns_string():
    for ct in [None, "theorem", "conjecture", "empirical", "construction",
               "erratum", "counterexample", "unknown", "", "   "]:
        kp = clio_submitter.kill_path_for(ct)
        assert isinstance(kp, str)
        assert len(kp) > 0


# ---------------------------------------------------------------------------
# build_claim_args — pure function
# ---------------------------------------------------------------------------

def test_build_claim_args_required_fields():
    args = clio_submitter.build_claim_args(SAMPLE_EXTRACTION)
    assert "target_name" in args
    assert "hypothesis" in args
    assert "evidence" in args
    assert "kill_path" in args


def test_build_claim_args_target_uses_arxiv_id():
    args = clio_submitter.build_claim_args(SAMPLE_EXTRACTION)
    assert args["target_name"].startswith("arxiv:")
    assert "2605.99999v1" in args["target_name"]


def test_build_claim_args_target_falls_back_to_title():
    ext = dict(SAMPLE_EXTRACTION, paper_external_id="")
    args = clio_submitter.build_claim_args(ext)
    assert args["target_name"] != ""
    assert "Mahler" in args["target_name"]


def test_build_claim_args_target_falls_back_to_paper_id():
    ext = dict(SAMPLE_EXTRACTION, paper_external_id=None, paper_title=None)
    args = clio_submitter.build_claim_args(ext)
    assert "42" in args["target_name"]


def test_build_claim_args_hypothesis_is_claim_text():
    args = clio_submitter.build_claim_args(SAMPLE_EXTRACTION)
    assert args["hypothesis"] == SAMPLE_EXTRACTION["claim_text"]


def test_build_claim_args_kill_path_matches_claim_type():
    args = clio_submitter.build_claim_args(SAMPLE_EXTRACTION)
    assert args["kill_path"] == clio_submitter.kill_path_for("theorem")


def test_build_claim_args_kill_path_must_be_string():
    """Sigma kernel raises if kill_path is not a string. build_claim_args
    must always emit a string."""
    args = clio_submitter.build_claim_args(SAMPLE_EXTRACTION)
    assert isinstance(args["kill_path"], str)
    # Also true with no claim_type
    ext = dict(SAMPLE_EXTRACTION, claim_type=None)
    args = clio_submitter.build_claim_args(ext)
    assert isinstance(args["kill_path"], str)


def test_build_claim_args_prefers_llm_kill_path_suggestion():
    """v0.5: when LLM provided a paper-aware kill_path, use it over template."""
    custom_kp = "expose flaw in the proof of Lemma 3.2 or invalidate the totally-real assumption"
    ext = dict(SAMPLE_EXTRACTION, kill_path_suggestion=custom_kp)
    args = clio_submitter.build_claim_args(ext)
    assert args["kill_path"] == custom_kp
    assert args["evidence"]["kill_path_source"] == "llm"


def test_build_claim_args_falls_back_to_template_when_no_llm_kp():
    """Missing kill_path_suggestion -> claim_type template."""
    ext = dict(SAMPLE_EXTRACTION)
    ext.pop("kill_path_suggestion", None)
    args = clio_submitter.build_claim_args(ext)
    assert args["kill_path"] == clio_submitter.kill_path_for("theorem")
    assert args["evidence"]["kill_path_source"] == "template"


def test_build_claim_args_falls_back_when_llm_kp_empty_string():
    ext = dict(SAMPLE_EXTRACTION, kill_path_suggestion="   ")
    args = clio_submitter.build_claim_args(ext)
    assert args["evidence"]["kill_path_source"] == "template"


def test_build_claim_args_falls_back_when_llm_kp_none():
    ext = dict(SAMPLE_EXTRACTION, kill_path_suggestion=None)
    args = clio_submitter.build_claim_args(ext)
    assert args["evidence"]["kill_path_source"] == "template"


def test_build_claim_args_llm_kp_for_theorem_avoids_template_counterexample_trap():
    """The canary case: theorem with LLM kill_path that does NOT include
    'counterexample' overrides the template (which does include it)."""
    proof_aware_kp = "expose a gap in the published proof"
    ext = dict(SAMPLE_EXTRACTION, claim_type="theorem", kill_path_suggestion=proof_aware_kp)
    args = clio_submitter.build_claim_args(ext)
    assert "counterexample" not in args["kill_path"].lower()
    assert "proof" in args["kill_path"].lower()


def test_build_claim_args_evidence_carries_paper_metadata():
    args = clio_submitter.build_claim_args(SAMPLE_EXTRACTION)
    ev = args["evidence"]
    assert ev["source_paper_external_id"] == "2605.99999v1"
    assert ev["clio_paper_id"] == 42
    assert ev["clio_extraction_id"] == 17
    assert ev["claim_type"] == "theorem"
    assert ev["paradigm_hint"] == "P12"
    assert ev["extractor_confidence"] == 0.85


def test_build_claim_args_truncates_abstract():
    long_abstract = "X" * 5000
    ext = dict(SAMPLE_EXTRACTION, paper_abstract=long_abstract)
    args = clio_submitter.build_claim_args(ext)
    assert len(args["evidence"]["abstract_excerpt"]) <= 500


def test_build_claim_args_raises_on_empty_claim_text():
    ext = dict(SAMPLE_EXTRACTION, claim_text="")
    with pytest.raises(ValueError, match="empty claim_text"):
        clio_submitter.build_claim_args(ext)


# ---------------------------------------------------------------------------
# submit_extraction — DI kernel
# ---------------------------------------------------------------------------

def test_submit_extraction_returns_claim_id():
    k = FakeKernel()
    cid = clio_submitter.submit_extraction(SAMPLE_EXTRACTION, k)
    assert isinstance(cid, str)
    assert cid.startswith("claim_fake_")
    assert len(k.claims_made) == 1


def test_submit_extraction_passes_correct_args_to_kernel():
    k = FakeKernel()
    clio_submitter.submit_extraction(SAMPLE_EXTRACTION, k)
    call = k.claims_made[0]
    assert call["target_name"].startswith("arxiv:")
    assert call["hypothesis"] == SAMPLE_EXTRACTION["claim_text"]
    assert "counterexample" in call["kill_path"] or "proof" in call["kill_path"]
    assert call["evidence"]["clio_extraction_id"] == 17


def test_submit_extraction_sets_default_tier_when_kernel_has_tier():
    k = FakeKernel()
    clio_submitter.submit_extraction(SAMPLE_EXTRACTION, k)
    call = k.claims_made[0]
    if clio_submitter.Tier is not None:
        assert call.get("target_tier") == clio_submitter.Tier.Conjecture


# ---------------------------------------------------------------------------
# run_submission_batch — end-to-end with DI
# ---------------------------------------------------------------------------

def test_run_submission_batch_marks_success():
    k = FakeKernel()
    extractions = [
        dict(SAMPLE_EXTRACTION, id=1),
        dict(SAMPLE_EXTRACTION, id=2, claim_text="Another claim."),
    ]
    marked: list[tuple[int, str]] = []
    errored: list[tuple[int, str]] = []

    def reader(limit):
        return extractions

    def on_success(eid, claim_id):
        marked.append((eid, claim_id))
        return True

    def on_error(eid, err):
        errored.append((eid, err))
        return True

    stats = clio_submitter.run_submission_batch(
        batch_size=10, kernel=k,
        reader=reader, on_success=on_success, on_error=on_error,
    )
    assert stats["submitted"] == 2
    assert stats["failed"] == 0
    assert len(marked) == 2
    assert marked[0][0] == 1
    assert marked[1][0] == 2
    assert all(cid.startswith("claim_fake_") for _, cid in marked)
    assert errored == []


def test_run_submission_batch_records_kernel_failure():
    k = FailingKernel()
    extractions = [dict(SAMPLE_EXTRACTION, id=1)]
    marked = []
    errored = []

    stats = clio_submitter.run_submission_batch(
        batch_size=10, kernel=k,
        reader=lambda limit: extractions,
        on_success=lambda eid, cid: marked.append((eid, cid)),
        on_error=lambda eid, err: errored.append((eid, err)),
    )
    assert stats["submitted"] == 0
    assert stats["failed"] == 1
    assert len(errored) == 1
    assert "simulated kernel failure" in errored[0][1]
    assert marked == []


def test_run_submission_batch_empty_input():
    stats = clio_submitter.run_submission_batch(
        batch_size=10, kernel=FakeKernel(),
        reader=lambda limit: [],
        on_success=lambda *a, **kw: None,
        on_error=lambda *a, **kw: None,
    )
    assert stats["submitted"] == 0
    assert stats["failed"] == 0


def test_run_submission_batch_continues_after_failure():
    """One failing extraction must not block subsequent ones."""
    call_count = [0]

    class FlakyKernel:
        def CLAIM(self, **kw):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("transient")
            return _FakeClaim(id=f"ok_{call_count[0]}", target_name=kw["target_name"], hypothesis=kw["hypothesis"])

    extractions = [
        dict(SAMPLE_EXTRACTION, id=1),
        dict(SAMPLE_EXTRACTION, id=2),
        dict(SAMPLE_EXTRACTION, id=3),
    ]
    stats = clio_submitter.run_submission_batch(
        batch_size=10, kernel=FlakyKernel(),
        reader=lambda limit: extractions,
        on_success=lambda eid, cid: None,
        on_error=lambda eid, err: None,
    )
    assert stats["submitted"] == 2
    assert stats["failed"] == 1


# ---------------------------------------------------------------------------
# Real SigmaKernel — sqlite backend smoke
# ---------------------------------------------------------------------------

def test_real_sigma_sqlite_kernel_accepts_clio_args(tmp_path):
    """Build a real SigmaKernel(sqlite) and submit one Clio-shaped extraction.

    Verifies that build_claim_args produces something the actual kernel accepts.
    Skipped if sigma_kernel is unavailable.
    """
    if not clio_submitter.HAS_SIGMA:
        pytest.skip("sigma_kernel unavailable")
    db = tmp_path / "sigma_test.db"
    k = clio_submitter.build_kernel(backend="sqlite", db_path=str(db))
    cid = clio_submitter.submit_extraction(SAMPLE_EXTRACTION, k)
    assert isinstance(cid, str)
    assert cid.startswith("claim_")
    # Verify the claim exists in the kernel's storage
    row = k.conn.execute(
        "SELECT id, target_name, hypothesis, kill_path FROM claims WHERE id=?",
        (cid,),
    ).fetchone()
    assert row is not None
    assert row[1].startswith("arxiv:")
    assert "Mahler measure" in row[2]
    assert isinstance(row[3], str) and len(row[3]) > 0
