"""Tests for clio_extractor (Clio v0.2)."""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import clio_extractor  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_PAPER = {
    "id": 42,
    "title": "On the Mahler measure of Lehmer polynomials with totally real roots",
    "abstract": (
        "We prove a new lower bound for the Mahler measure of non-cyclotomic "
        "polynomials with totally real roots, improving the Schinzel-Zassenhaus "
        "constant in the totally-real case from 1.17 to 1.21. The result is "
        "constructive: we exhibit an explicit family realizing the bound."
    ),
    "authors": ["Jane Smith", "Bob Jones"],
    "arxiv_categories": ["math.NT"],
    "url": "http://arxiv.org/abs/2605.99999",
    "external_id": "2605.99999v1",
}


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def test_prompt_includes_title_and_abstract():
    prompt = clio_extractor.build_extraction_prompt(SAMPLE_PAPER)
    assert "Mahler measure" in prompt
    assert "Schinzel-Zassenhaus" in prompt
    assert "Jane Smith" in prompt
    assert "math.NT" in prompt


def test_prompt_handles_missing_fields():
    minimal = {"title": None, "abstract": None}
    prompt = clio_extractor.build_extraction_prompt(minimal)
    assert "untitled" in prompt.lower() or "title:" in prompt.lower()
    assert "no abstract" in prompt.lower() or "abstract:" in prompt.lower()


def test_prompt_caps_authors_to_5():
    paper = dict(SAMPLE_PAPER, authors=["A"] * 12)
    prompt = clio_extractor.build_extraction_prompt(paper)
    # comma-joined; with 5 entries we get 4 commas
    assert prompt.count(", A") <= 5


def test_prompt_mentions_paradigm_legend():
    prompt = clio_extractor.build_extraction_prompt(SAMPLE_PAPER)
    assert "P15" in prompt  # tensor decomposition code in legend
    assert "P22" in prompt  # polynomial method on signed graphs


# ---------------------------------------------------------------------------
# Response parsing — happy path
# ---------------------------------------------------------------------------

def _wrap(claims_list):
    return json.dumps({"claims": claims_list})


def test_parse_well_formed_json():
    text = _wrap([
        {
            "claim_text": "The Mahler measure has minimum 1.21 in the totally-real case.",
            "claim_type": "theorem",
            "paradigm_hint": "P12",
            "open_problem_hint": "Schinzel-Zassenhaus conjecture",
            "falsifiable": True,
            "confidence": 0.85,
        }
    ])
    claims = clio_extractor.parse_extraction_response(text)
    assert len(claims) == 1
    c = claims[0]
    assert "Mahler measure" in c["claim_text"]
    assert c["claim_type"] == "theorem"
    assert c["paradigm_hint"] == "P12"
    assert c["falsifiable"] is True
    assert c["confidence"] == 0.85


def test_parse_empty_claims_list():
    assert clio_extractor.parse_extraction_response('{"claims": []}') == []


# ---------------------------------------------------------------------------
# Response parsing — defensive
# ---------------------------------------------------------------------------

def test_parse_strips_markdown_fence():
    text = '```json\n' + _wrap([{"claim_text": "X is Y."}]) + '\n```'
    claims = clio_extractor.parse_extraction_response(text)
    assert len(claims) == 1
    assert claims[0]["claim_text"] == "X is Y."


def test_parse_extracts_json_block_from_preamble():
    text = (
        "Here are the claims I extracted:\n\n"
        + _wrap([{"claim_text": "The claim.", "claim_type": "theorem"}])
        + "\n\nLet me know if you need more."
    )
    claims = clio_extractor.parse_extraction_response(text)
    assert len(claims) == 1


def test_parse_invalid_claim_type_normalizes_to_none():
    text = _wrap([{"claim_text": "X", "claim_type": "NotARealType"}])
    claims = clio_extractor.parse_extraction_response(text)
    assert len(claims) == 1
    assert claims[0]["claim_type"] is None


def test_parse_invalid_paradigm_hint_normalizes_to_none():
    text = _wrap([{"claim_text": "X", "paradigm_hint": "garbage"}])
    claims = clio_extractor.parse_extraction_response(text)
    assert claims[0]["paradigm_hint"] is None


def test_parse_clamps_confidence_to_range():
    text = _wrap([
        {"claim_text": "A", "confidence": 1.7},
        {"claim_text": "B", "confidence": -0.4},
    ])
    claims = clio_extractor.parse_extraction_response(text)
    assert claims[0]["confidence"] == 1.0
    assert claims[1]["confidence"] == 0.0


def test_parse_skips_claim_missing_text():
    text = _wrap([
        {"claim_type": "theorem"},  # no claim_text
        {"claim_text": "Valid claim."},
    ])
    claims = clio_extractor.parse_extraction_response(text)
    assert len(claims) == 1
    assert claims[0]["claim_text"] == "Valid claim."


def test_parse_caps_at_3_claims():
    text = _wrap([{"claim_text": f"Claim {i}."} for i in range(10)])
    claims = clio_extractor.parse_extraction_response(text)
    assert len(claims) == 3


def test_parse_garbage_returns_empty():
    assert clio_extractor.parse_extraction_response("") == []
    assert clio_extractor.parse_extraction_response("no json here at all") == []
    assert clio_extractor.parse_extraction_response('{"unrelated": "object"}') == []
    assert clio_extractor.parse_extraction_response("null") == []


def test_parse_does_not_raise_on_any_input():
    # Property-style: extractor must never crash regardless of LLM output
    inputs = [None, "", "abc", "{", "}", "{}", "null", "[]", 12345, b"bytes",
              '{"claims": "not-a-list"}', '{"claims": [null, 42, "str"]}']
    for inp in inputs:
        try:
            result = clio_extractor.parse_extraction_response(inp)
        except Exception as e:
            pytest.fail(f"parse raised on input {inp!r}: {e}")
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# extract_claims_for_paper — DI smoke test
# ---------------------------------------------------------------------------

def test_extract_claims_for_paper_with_mock_llm():
    fake_response = _wrap([
        {
            "claim_text": "Mahler measure lower bound improves to 1.21.",
            "claim_type": "theorem",
            "falsifiable": True,
            "confidence": 0.9,
        }
    ])
    captured_prompt = {}

    def mock_llm(prompt, system="", **kw):
        captured_prompt["prompt"] = prompt
        captured_prompt["system"] = system
        return fake_response

    claims, raw = clio_extractor.extract_claims_for_paper(SAMPLE_PAPER, llm_fn=mock_llm)
    assert raw == fake_response
    assert len(claims) == 1
    assert "1.21" in claims[0]["claim_text"]
    assert "Mahler measure" in captured_prompt["prompt"]
    assert "claim-stack" in captured_prompt["system"].lower()


# ---------------------------------------------------------------------------
# run_extraction_batch — end-to-end with all deps mocked
# ---------------------------------------------------------------------------

def test_run_extraction_batch_writes_each_claim():
    papers = [
        dict(SAMPLE_PAPER, id=1),
        dict(SAMPLE_PAPER, id=2, title="Other paper"),
    ]
    written = []

    def fake_reader(limit):
        return papers

    def fake_writer(**kw):
        written.append(kw)
        return len(written)  # fake extraction_id

    def fake_llm(prompt, system="", **kw):
        return _wrap([
            {"claim_text": "Claim A.", "claim_type": "theorem", "confidence": 0.8},
            {"claim_text": "Claim B.", "claim_type": "conjecture", "confidence": 0.6},
        ])

    stats = clio_extractor.run_extraction_batch(
        batch_size=10,
        llm_fn=fake_llm,
        paper_reader=fake_reader,
        writer=fake_writer,
    )
    assert stats["papers_processed"] == 2
    assert stats["claims_extracted"] == 4
    assert len(written) == 4
    # Verify writer received expected fields
    assert all("claim_text" in w for w in written)
    assert all("paper_id" in w for w in written)
    assert all("claim_index" in w for w in written)
    # claim_index should be 0,1 within each paper
    by_paper = {}
    for w in written:
        by_paper.setdefault(w["paper_id"], []).append(w["claim_index"])
    for indices in by_paper.values():
        assert sorted(indices) == [0, 1]


def test_run_extraction_batch_handles_paper_failure():
    papers = [dict(SAMPLE_PAPER, id=1), dict(SAMPLE_PAPER, id=2)]

    def fake_reader(limit):
        return papers

    def fake_writer(**kw):
        return 1

    calls = [0]

    def fake_llm(prompt, system="", **kw):
        calls[0] += 1
        if calls[0] == 1:
            raise RuntimeError("LLM down")
        return _wrap([{"claim_text": "OK."}])

    stats = clio_extractor.run_extraction_batch(
        batch_size=10, llm_fn=fake_llm,
        paper_reader=fake_reader, writer=fake_writer,
    )
    assert stats["papers_failed"] == 1
    assert stats["papers_processed"] == 1
    assert stats["claims_extracted"] == 1


def test_run_extraction_batch_with_no_papers():
    stats = clio_extractor.run_extraction_batch(
        batch_size=10,
        llm_fn=lambda *a, **kw: "{}",
        paper_reader=lambda limit: [],
        writer=lambda **kw: None,
    )
    assert stats["papers_processed"] == 0
    assert stats["claims_extracted"] == 0


def test_run_extraction_batch_skips_paper_with_no_claims():
    papers = [dict(SAMPLE_PAPER, id=1)]
    written = []

    def fake_reader(limit):
        return papers

    def fake_writer(**kw):
        written.append(kw)
        return 1

    def fake_llm(prompt, system="", **kw):
        return '{"claims": []}'

    stats = clio_extractor.run_extraction_batch(
        batch_size=10, llm_fn=fake_llm,
        paper_reader=fake_reader, writer=fake_writer,
    )
    assert stats["papers_processed"] == 1
    assert stats["claims_extracted"] == 0
    assert written == []
