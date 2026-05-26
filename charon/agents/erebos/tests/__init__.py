"""Erebos generator-plugin test suite.

Per pivot/erebos_design_philosophy_dna_2026-05-26.md P3 (TDD-first):
every generator plugin has a test file at test_g<NN>_<name>.py
covering input handling, transformation correctness, output schema,
falsification route validity, applicability gate.

Run with:
    pytest charon/agents/erebos/tests/
"""
