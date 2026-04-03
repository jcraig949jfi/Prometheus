#!/usr/bin/env python3
"""Test suite for Gauge-Bandit Active Inference Scorer"""

from gauge_bandit_active_inference import ReasoningTool


def test_numeric_comparison():
    """Test numeric comparison parsing"""
    tool = ReasoningTool()
    result = tool.evaluate('Is 9.11 greater than 9.9?', ['Yes', 'No'])
    print(f"Numeric comparison: {result[0]['candidate']} (score: {result[0]['score']:.3f})")
    assert result[0]['candidate'] == 'No', "Should recognize 9.11 < 9.9"


def test_bat_and_ball():
    """Test algebraic reasoning (bat-and-ball problem)"""
    tool = ReasoningTool()
    result = tool.evaluate(
        'A bat and ball cost 1.10 in total. The bat costs 1.00 more than the ball. How much does the ball cost?',
        ['0.05', '0.10', '0.50']
    )
    print(f"Bat and ball: {result[0]['candidate']} (score: {result[0]['score']:.3f})")
    assert result[0]['candidate'] == '0.05', "Should solve algebraic equation"


def test_presupposition_detection():
    """Test epistemic honesty on presupposition questions"""
    tool = ReasoningTool()
    conf = tool.confidence('Have you stopped cheating on tests?', 'Yes')
    print(f"Presupposition confidence: {conf:.3f}")
    assert conf < 0.3, "Should be uncertain about presupposition questions"


def test_ambiguous_pronoun():
    """Test detection of pronoun ambiguity"""
    tool = ReasoningTool()
    conf = tool.confidence('John told Bill he was wrong. Who was wrong?', 'John')
    print(f"Pronoun ambiguity confidence: {conf:.3f}")
    assert conf < 0.3, "Should recognize pronoun ambiguity"


def test_all_but_n():
    """Test all-but-N pattern"""
    tool = ReasoningTool()
    result = tool.evaluate(
        'There are 10 apples. All but 3 are red. How many are red?',
        ['3', '7', '10']
    )
    print(f"All-but-N: {result[0]['candidate']} (score: {result[0]['score']:.3f})")


def test_transitivity():
    """Test transitive reasoning"""
    tool = ReasoningTool()
    result = tool.evaluate(
        'Alice is taller than Bob. Bob is taller than Carol. Is Alice taller than Carol?',
        ['Yes', 'No', 'Cannot determine']
    )
    print(f"Transitivity: {result[0]['candidate']} (score: {result[0]['score']:.3f})")


def test_structural_invariance():
    """Test that gauge theory maintains invariance across rephrasings"""
    tool = ReasoningTool()

    # Same logical structure, different wording
    prompt1 = 'If it rains, the ground gets wet. The ground is not wet. Did it rain?'
    prompt2 = 'When precipitation occurs, the surface becomes moist. The surface is dry. Was there precipitation?'

    result1 = tool.evaluate(prompt1, ['Yes', 'No'])
    result2 = tool.evaluate(prompt2, ['Yes', 'No'])

    print(f"Modus tollens v1: {result1[0]['candidate']} (score: {result1[0]['score']:.3f})")
    print(f"Modus tollens v2: {result2[0]['candidate']} (score: {result2[0]['score']:.3f})")

    # Scores should be close even if not identical (gauge invariance is approximate)
    score_diff = abs(result1[0]['score'] - result2[0]['score'])
    print(f"Score difference: {score_diff:.3f}")
    assert score_diff < 0.2, "Scores should be similar for structurally equivalent questions"


if __name__ == '__main__':
    print("Running GBAIS Test Suite\n" + "="*50)
    
    test_numeric_comparison()
    test_bat_and_ball()
    test_presupposition_detection()
    test_ambiguous_pronoun()
    test_all_but_n()
    test_transitivity()
    test_structural_invariance()
    
    print("\n" + "="*50)
    print("All tests passed!")
