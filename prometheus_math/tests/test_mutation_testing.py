"""Tests for prometheus_math.mutation_testing (T-2026-05-07-T014)."""
from __future__ import annotations

from pathlib import Path

import pytest

from prometheus_math.mutation_testing import (
    MUTATION_OPERATORS,
    BaselineReport,
    MutationProposal,
    MutationResult,
    MutationVerdict,
    apply_mutation_to_text,
    generate_baseline,
    propose_mutations,
    render_baseline_report,
    run_mutation_test,
)


# ---------------------------------------------------------------------------
# Operator-level enumerator tests
# ---------------------------------------------------------------------------


class TestComparisonFlipOperator:
    def test_flips_lt_to_gt(self):
        sites = list(MUTATION_OPERATORS["comparison_flip"]("if x < 5: pass"))
        ops = [(o, r) for _, o, r in sites]
        assert ("<", ">") in ops

    def test_flips_le_to_ge(self):
        sites = list(MUTATION_OPERATORS["comparison_flip"]("if x <= 5: pass"))
        ops = [(o, r) for _, o, r in sites]
        assert ("<=", ">=") in ops
        # Must NOT also yield single ``<`` (length-descending dedup)
        assert ("<", ">") not in ops

    def test_does_not_flip_arrow_in_signature(self):
        sites = list(MUTATION_OPERATORS["comparison_flip"]("def foo() -> int:"))
        # ``->`` should not produce a ``>`` flip
        for _, op, _ in sites:
            assert op != ">"

    def test_flips_eq_to_neq(self):
        sites = list(MUTATION_OPERATORS["comparison_flip"]("if a == b: pass"))
        ops = [(o, r) for _, o, r in sites]
        assert ("==", "!=") in ops

    def test_neq_yielded_only_once(self):
        """``!=`` should yield (!=, ==) but the inner == should NOT also fire."""
        sites = list(MUTATION_OPERATORS["comparison_flip"]("if a != b: pass"))
        ops = [(o, r) for _, o, r in sites]
        assert ("!=", "==") in ops
        # The == inside != is part of the same site
        eq_pos = [c for c, o, _ in sites if o == "=="]
        # Should be empty (== inside != was suppressed)
        assert eq_pos == [] or eq_pos[0] != 1


class TestBooleanLiteralOperator:
    def test_flips_true(self):
        sites = list(MUTATION_OPERATORS["boolean_not"]("flag = True"))
        ops = [(o, r) for _, o, r in sites]
        assert ("True", "False") in ops

    def test_flips_false(self):
        sites = list(MUTATION_OPERATORS["boolean_not"]("flag = False"))
        ops = [(o, r) for _, o, r in sites]
        assert ("False", "True") in ops

    def test_does_not_match_substring(self):
        sites = list(MUTATION_OPERATORS["boolean_not"]("Truelike = 1"))
        assert sites == []


class TestReturnConstantNoneOperator:
    def test_replaces_simple_return(self):
        sites = list(MUTATION_OPERATORS["return_constant_None"]("    return x + 1"))
        assert len(sites) == 1
        col, original, replacement = sites[0]
        assert original == "return x + 1"
        assert replacement == "return None"
        assert col == 4

    def test_does_not_double_mutate_return_none(self):
        sites = list(MUTATION_OPERATORS["return_constant_None"]("    return None"))
        assert sites == []

    def test_strips_trailing_comments(self):
        sites = list(MUTATION_OPERATORS["return_constant_None"]("    return x  # foo"))
        assert len(sites) == 1
        _, original, _ = sites[0]
        assert original == "return x"


class TestOffByOneIntOperator:
    def test_increments_small_int(self):
        sites = list(MUTATION_OPERATORS["off_by_one_int"]("threshold = 10"))
        ops = [(o, r) for _, o, r in sites]
        assert ("10", "11") in ops

    def test_skips_large_int(self):
        # |200| > 100 -> skipped
        sites = list(MUTATION_OPERATORS["off_by_one_int"]("seed = 200"))
        # No site at column matching the 200 should be emitted
        for _, o, _ in sites:
            assert o != "200"


# ---------------------------------------------------------------------------
# propose_mutations
# ---------------------------------------------------------------------------


class TestProposeMutations:
    def test_empty_file_yields_no_proposals(self, tmp_path: Path):
        f = tmp_path / "empty.py"
        f.write_text("", encoding="utf-8")
        assert propose_mutations(f) == []

    def test_skips_comment_lines(self, tmp_path: Path):
        f = tmp_path / "commented.py"
        f.write_text("# if True:\n", encoding="utf-8")
        proposals = propose_mutations(f)
        # Comment line should be filtered
        assert proposals == []

    def test_yields_per_operator_per_site(self, tmp_path: Path):
        f = tmp_path / "live.py"
        f.write_text(
            "def foo(x):\n"
            "    if x > 0:\n"
            "        return True\n"
            "    return False\n",
            encoding="utf-8",
        )
        proposals = propose_mutations(f)
        op_names = {p.operator_name for p in proposals}
        assert "comparison_flip" in op_names
        assert "boolean_not" in op_names
        assert "return_constant_None" in op_names

    def test_skips_docstring_block(self, tmp_path: Path):
        f = tmp_path / "docstring.py"
        f.write_text(
            '"""\n'
            "if 1 < 2: pass\n"
            '"""\n'
            "x = True\n",
            encoding="utf-8",
        )
        proposals = propose_mutations(f)
        # Only the True flip outside the docstring
        op_names = {p.operator_name for p in proposals}
        assert op_names == {"boolean_not"}


# ---------------------------------------------------------------------------
# apply_mutation_to_text
# ---------------------------------------------------------------------------


class TestApplyMutationToText:
    def test_applies_at_correct_position(self, tmp_path: Path):
        text = "if x > 5:\n    pass\n"
        # Build a proposal manually for column 5 (the >)
        prop = MutationProposal(
            file_path=tmp_path / "fake.py",
            line_no=1, column=5,
            operator_name="comparison_flip",
            original_text=">", mutated_text="<",
        )
        out = apply_mutation_to_text(text, prop)
        assert out == "if x < 5:\n    pass\n"

    def test_anchor_mismatch_raises(self, tmp_path: Path):
        text = "if x > 5:\n"
        prop = MutationProposal(
            file_path=tmp_path / "fake.py",
            line_no=1, column=5,
            operator_name="comparison_flip",
            original_text="<",  # WRONG; actual is >
            mutated_text=">",
        )
        with pytest.raises(ValueError, match="anchor mismatch"):
            apply_mutation_to_text(text, prop)

    def test_line_out_of_range_raises(self, tmp_path: Path):
        text = "x = 1\n"
        prop = MutationProposal(
            file_path=tmp_path / "fake.py",
            line_no=99, column=0,
            operator_name="boolean_not",
            original_text="True", mutated_text="False",
        )
        with pytest.raises(ValueError, match="line_no"):
            apply_mutation_to_text(text, prop)

    def test_preserves_eol_style(self, tmp_path: Path):
        text = "x = True\r\ny = False\r\n"
        prop = MutationProposal(
            file_path=tmp_path / "fake.py",
            line_no=1, column=4,
            operator_name="boolean_not",
            original_text="True", mutated_text="False",
        )
        out = apply_mutation_to_text(text, prop)
        # CRLF preserved
        assert "\r\n" in out
        assert out.startswith("x = False\r\n")


# ---------------------------------------------------------------------------
# End-to-end (run_mutation_test) using a no-op test command
# ---------------------------------------------------------------------------


class TestRunMutationTest:
    def test_passing_test_cmd_yields_survived(self, tmp_path: Path):
        f = tmp_path / "src.py"
        f.write_text("x = True\n", encoding="utf-8")
        prop = MutationProposal(
            file_path=f, line_no=1, column=4,
            operator_name="boolean_not",
            original_text="True", mutated_text="False",
        )
        # Use a shell command that always exits 0 (cross-platform: python -c pass)
        result = run_mutation_test(prop, 'python -c "pass"', timeout_s=30)
        assert result.verdict == MutationVerdict.SURVIVED
        # File restored to original
        assert f.read_text(encoding="utf-8") == "x = True\n"

    def test_failing_test_cmd_yields_killed(self, tmp_path: Path):
        f = tmp_path / "src.py"
        f.write_text("x = True\n", encoding="utf-8")
        prop = MutationProposal(
            file_path=f, line_no=1, column=4,
            operator_name="boolean_not",
            original_text="True", mutated_text="False",
        )
        result = run_mutation_test(prop, 'python -c "import sys; sys.exit(1)"', timeout_s=30)
        assert result.verdict == MutationVerdict.KILLED
        assert f.read_text(encoding="utf-8") == "x = True\n"

    def test_anchor_mismatch_yields_skipped_and_restores_file(self, tmp_path: Path):
        f = tmp_path / "src.py"
        f.write_text("x = 1\n", encoding="utf-8")
        prop = MutationProposal(
            file_path=f, line_no=1, column=4,
            operator_name="boolean_not",
            original_text="True", mutated_text="False",  # bogus anchor
        )
        result = run_mutation_test(prop, 'python -c "pass"', timeout_s=30)
        assert result.verdict == MutationVerdict.SKIPPED
        # File NOT mutated, so still original
        assert f.read_text(encoding="utf-8") == "x = 1\n"

    def test_missing_target_file_yields_errored(self, tmp_path: Path):
        prop = MutationProposal(
            file_path=tmp_path / "does_not_exist.py",
            line_no=1, column=0,
            operator_name="boolean_not",
            original_text="True", mutated_text="False",
        )
        result = run_mutation_test(prop, 'python -c "pass"', timeout_s=30)
        assert result.verdict == MutationVerdict.ERRORED


# ---------------------------------------------------------------------------
# Baseline integration
# ---------------------------------------------------------------------------


class TestGenerateBaseline:
    def test_baseline_aggregates_correctly(self, tmp_path: Path):
        f = tmp_path / "live.py"
        f.write_text("x = True\ny = False\n", encoding="utf-8")
        # Test command always passes -> all mutations survive
        report = generate_baseline(
            target_files=[f],
            test_cmd='python -c "pass"',
            operators=("boolean_not",),
            timeout_s=30,
        )
        assert report.n_killed == 0
        assert report.n_survived == 2
        assert report.mutation_score == 0.0
        assert len(report.survivors) == 2

    def test_max_mutations_caps_proposal_count(self, tmp_path: Path):
        f = tmp_path / "live.py"
        f.write_text("a = True\nb = True\nc = True\n", encoding="utf-8")
        report = generate_baseline(
            target_files=[f],
            test_cmd='python -c "pass"',
            operators=("boolean_not",),
            max_mutations=2,
            timeout_s=30,
        )
        assert report.n_proposals == 2


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


class TestRenderBaselineReport:
    def test_no_proposals_renders_no_proposals_message(self):
        empty = BaselineReport(
            target_files=("foo.py",), test_cmd="cmd",
            n_proposals=0, n_killed=0, n_survived=0,
            n_errored=0, n_skipped=0, mutation_score=0.0,
            survivors=(), elapsed_s=0.0,
        )
        md = render_baseline_report(empty)
        assert "Mutation Testing Baseline" in md
        assert "No mutations were proposed" in md

    def test_survivors_table_renders(self, tmp_path: Path):
        prop = MutationProposal(
            file_path=tmp_path / "live.py", line_no=3, column=4,
            operator_name="boolean_not",
            original_text="True", mutated_text="False",
        )
        result = MutationResult(
            proposal=prop, verdict=MutationVerdict.SURVIVED,
            elapsed_s=1.2,
        )
        report = BaselineReport(
            target_files=("live.py",), test_cmd="cmd",
            n_proposals=1, n_killed=0, n_survived=1,
            n_errored=0, n_skipped=0, mutation_score=0.0,
            survivors=(result,), elapsed_s=1.5,
        )
        md = render_baseline_report(report)
        assert "Top Surviving Mutations" in md
        assert "live.py:3" in md
        assert "True" in md and "False" in md

    def test_no_survivors_message_renders(self):
        report = BaselineReport(
            target_files=("foo.py",), test_cmd="cmd",
            n_proposals=5, n_killed=5, n_survived=0,
            n_errored=0, n_skipped=0, mutation_score=1.0,
            survivors=(), elapsed_s=10.0,
        )
        md = render_baseline_report(report)
        assert "No survivors" in md
