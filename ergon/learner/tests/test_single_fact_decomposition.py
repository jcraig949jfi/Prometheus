"""Tests for E007 — single-fact-decomposition prompt protocol."""
from __future__ import annotations

import pytest

from ergon.learner.inference.single_fact_decomposition import (
    DecompositionResult,
    answer_with_decomposition,
    assemble_answers,
    decompose_question,
    is_multi_part,
)


# ---------------------------------------------------------------------------
# is_multi_part heuristic
# ---------------------------------------------------------------------------


def test_is_multi_part_single_question():
    assert not is_multi_part("What is the chromatic number of the Petersen graph?")


def test_is_multi_part_enumeration_letters():
    q = "For the Petersen graph, state: (a) its chromatic number, (b) its girth."
    assert is_multi_part(q)


def test_is_multi_part_enumeration_roman():
    q = "Compute (i) the genus of the trefoil, (ii) its determinant."
    assert is_multi_part(q)


def test_is_multi_part_enumeration_numeric():
    q = "Provide (1) the prime gap bound, (2) the year proven."
    assert is_multi_part(q)


def test_is_multi_part_conjoined_question_words():
    q = "What is the genus of the trefoil and what is its Alexander polynomial?"
    assert is_multi_part(q)


def test_is_multi_part_ordinal_prefixes():
    q = "First state the Bochner-Riesz proven range; second discuss n>=3 status."
    assert is_multi_part(q)


def test_is_multi_part_empty_string():
    assert not is_multi_part("")


def test_is_multi_part_whitespace_only():
    assert not is_multi_part("   \n  \t  ")


def test_is_multi_part_single_and_in_noun_phrase():
    q = "What is the relationship between primes and twin primes?"
    assert not is_multi_part(q)


# ---------------------------------------------------------------------------
# decompose_question
# ---------------------------------------------------------------------------


def test_decompose_single_part_returns_unchanged():
    q = "What is the chromatic number of the Petersen graph?"
    assert decompose_question(q) == [q]


def test_decompose_two_part_letters_petersen():
    """Canonical paired test from Charon Fire-006 P-029."""
    q = "For the Petersen graph, state: (a) its chromatic number, (b) its girth."
    subs = decompose_question(q)
    assert len(subs) == 2
    for s in subs:
        assert "Petersen" in s
    assert "chromatic number" in subs[0]
    assert "girth" in subs[1]


def test_decompose_three_part_roman():
    q = "Compute (i) the genus, (ii) the determinant, (iii) the Alexander polynomial of the trefoil."
    subs = decompose_question(q)
    assert len(subs) == 3
    assert "genus" in subs[0]
    assert "determinant" in subs[1]
    assert "Alexander polynomial" in subs[2]


def test_decompose_conjoined_question():
    q = "What is the genus of the trefoil and what is its Alexander polynomial?"
    subs = decompose_question(q)
    assert len(subs) == 2
    assert "genus" in subs[0].lower()
    assert "alexander polynomial" in subs[1].lower()


def test_decompose_subqueries_end_with_punctuation():
    q = "State (a) the chromatic, (b) the girth."
    for s in decompose_question(q):
        assert s.endswith("?") or s.endswith(".")


def test_decompose_empty_returns_input_unchanged():
    assert decompose_question("") == [""]


def test_decompose_handles_trailing_labeled_instruction_correctly():
    """Regression: 'labeled (a) and (b)' trailing instruction was generating
    spurious 3rd subquery 'For X, state: and?' Fixed by short-body + label-
    dedup filter."""
    q = "For the Petersen graph, state: (a) its chromatic number, (b) its girth. Reply concisely with two integers labeled (a) and (b)."
    subs = decompose_question(q)
    # MUST be exactly 2 subqueries despite 4 enumeration-marker matches
    assert len(subs) == 2, (
        f"trailing 'labeled (a) and (b)' should not create extra subqueries; "
        f"got {len(subs)}: {subs}"
    )
    assert "chromatic number" in subs[0]
    assert "girth" in subs[1]
    # No "and?" subquery
    for s in subs:
        assert s.strip().lower() not in ("and?", "or?", "and", "or")


def test_decompose_dedupe_repeated_labels():
    """Repeated `(a)` (e.g., from 'option (a) is the chromatic, option (a)
    is also...') should not generate two subqueries for the same label."""
    q = "Compute (a) the chromatic number, (b) the girth. Use convention (a) before (b)."
    subs = decompose_question(q)
    assert len(subs) == 2  # 2 unique labels, not 4


# ---------------------------------------------------------------------------
# assemble_answers
# ---------------------------------------------------------------------------


def test_assemble_single_answer_returns_unwrapped():
    out = assemble_answers(["q?"], ["the answer"])
    assert out == "the answer"


def test_assemble_two_answers_with_letters():
    out = assemble_answers(["q1?", "q2?"], ["3", "5"])
    assert "(a) 3" in out and "(b) 5" in out


def test_assemble_length_mismatch_raises():
    with pytest.raises(ValueError, match="different lengths"):
        assemble_answers(["q1?", "q2?"], ["only one"])


# ---------------------------------------------------------------------------
# answer_with_decomposition (the main wrapper)
# ---------------------------------------------------------------------------


def test_answer_with_decomposition_single_part():
    calls = []
    def fn(q):
        calls.append(q)
        return "STUB"
    q = "What is the chromatic number of the Petersen graph?"
    res = answer_with_decomposition(q, fn, decomposition_on=True)
    assert isinstance(res, DecompositionResult)
    assert res.is_multi_part is False
    assert res.n_model_calls == 1
    assert calls == [q]


def test_answer_with_decomposition_multi_part_on():
    calls = []
    def fn(q):
        calls.append(q)
        return "STUB"
    q = "For Petersen, state: (a) chromatic, (b) girth."
    res = answer_with_decomposition(q, fn, decomposition_on=True)
    assert res.is_multi_part is True
    assert res.n_model_calls == 2
    assert len(calls) == 2
    assert res.metadata["path"] == "decomposed"


def test_answer_with_decomposition_off_passes_through():
    """Acceptance #4: ablation OFF passes full question unchanged."""
    calls = []
    def fn(q):
        calls.append(q)
        return "STUB"
    q = "For Petersen, state: (a) chromatic, (b) girth."
    res = answer_with_decomposition(q, fn, decomposition_on=False)
    assert res.decomposition_on is False
    assert res.n_model_calls == 1
    assert calls == [q]
    assert res.metadata["path"] == "passthrough"


def test_answer_with_decomposition_per_subquery_answers_recorded():
    def fn(q):
        return f"ANSWER_FOR<{q[:30]}>"
    q = "Compute (a) genus, (b) determinant of trefoil."
    res = answer_with_decomposition(q, fn, decomposition_on=True)
    assert len(res.per_subquery_answers) == 2
    assert all(a.startswith("ANSWER_FOR<") for a in res.per_subquery_answers)


def test_answer_with_decomposition_telemetry_complete():
    res = answer_with_decomposition(
        "What is the chromatic of Petersen and its girth?",
        lambda q: "X",
        decomposition_on=True,
    )
    assert res.answer
    assert res.decomposition_on is True
    assert isinstance(res.is_multi_part, bool)
    assert isinstance(res.subqueries, list)
    assert isinstance(res.per_subquery_answers, list)
    assert isinstance(res.n_model_calls, int)
    assert isinstance(res.metadata, dict)


# ---------------------------------------------------------------------------
# Contract-check: existing eval API surface unchanged
# ---------------------------------------------------------------------------


def test_no_contract_change_to_evaluate_model():
    """Acceptance #7: NO contract change to Learner public API."""
    import inspect
    from ergon.pipeline_d.eval import evaluate_model, evaluate_model_with_label_mask

    sig = inspect.signature(evaluate_model)
    expected = {"model", "eval_dataset", "tokenizer", "candidate_labels",
                "max_new_tokens", "log_predictions"}
    assert set(sig.parameters.keys()) == expected

    sig2 = inspect.signature(evaluate_model_with_label_mask)
    expected2 = {"model", "eval_dataset", "tokenizer", "candidate_labels",
                 "log_predictions"}
    assert set(sig2.parameters.keys()) == expected2


def test_module_imports_cleanly():
    """Smoke: import has no side effects (no model load)."""
    import ergon.learner.inference.single_fact_decomposition as sfd
    for name in ("is_multi_part", "decompose_question", "assemble_answers",
                 "answer_with_decomposition", "DecompositionResult"):
        assert hasattr(sfd, name), f"missing public API: {name}"
