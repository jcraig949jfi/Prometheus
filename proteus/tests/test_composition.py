"""Contract tests for segment / composition / exact-ablation identity.

Every test here is a property another component may rely on. Where a property is CONDITIONAL, the
test asserts the condition is reported rather than asserting the happy answer.
"""
from __future__ import annotations

import json
import os
import unittest

from proteus.compose.segments import (COMPOSITION_SCHEMA, NOP_ALIASES, CompositionError, ablate,
                                      ablation_report, activation_evidence, compose,
                                      composition_id, decompose, segment_from_instructions,
                                      segment_id)
from proteus.foundry.affordances import N_OPCODES
from proteus.foundry.identity import RUNTIME_HASH, hash_obj
from proteus.foundry.vm import validate_manifest

IW = 4
A_WORDS = [7, 1, 2, 3, 16, 0, 1, 2]
B_WORDS = [23, 0, 1, 0, 1, 0, 0, 0]
ENV = {"n_regs": 4, "tape_words": 64, "code_writable": False,
       "persist": "none", "tick_budget": 64, "out_cap": 4}
HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(os.path.dirname(HERE), "compose", "GOLDEN_VECTORS.json")


def _A():
    return segment_from_instructions(A_WORDS)


def _B():
    return segment_from_instructions(B_WORDS)


class SegmentIdentity(unittest.TestCase):
    def test_identity_is_content_only(self):
        self.assertEqual(segment_id(_A()), segment_id(segment_from_instructions(list(A_WORDS))))

    def test_label_does_not_change_identity(self):
        plain = _A()
        labelled = segment_from_instructions(list(A_WORDS), label="anything at all")
        self.assertEqual(segment_id(plain), segment_id(labelled))

    def test_partial_instruction_is_refused(self):
        with self.assertRaises(CompositionError):
            segment_from_instructions([7, 1, 2])

    def test_empty_segment_is_refused(self):
        with self.assertRaises(CompositionError):
            segment_from_instructions([])


class CompositionIdentity(unittest.TestCase):
    def test_compose_emits_a_valid_manifest(self):
        c = compose([("A", _A()), ("B", _B())], ENV)
        validate_manifest(c["manifest"])
        self.assertEqual(c["manifest"]["genome"], A_WORDS + B_WORDS)

    def test_order_is_part_of_identity(self):
        ab = compose([("A", _A()), ("B", _B())], ENV)
        ba = compose([("B", _B()), ("A", _A())], ENV)
        self.assertNotEqual(ab["composition_id"], ba["composition_id"])
        self.assertNotEqual(hash_obj(ab["manifest"]), hash_obj(ba["manifest"]))

    def test_decompose_round_trips_exactly(self):
        c = compose([("A", _A()), ("B", _B())], ENV)
        got = dict(decompose(c))
        self.assertEqual(segment_id(got["A"]), segment_id(_A()))
        self.assertEqual(segment_id(got["B"]), segment_id(_B()))

    def test_duplicate_component_names_refused(self):
        with self.assertRaises(CompositionError):
            compose([("A", _A()), ("A", _B())], ENV)

    def test_unknown_glue_refused(self):
        with self.assertRaises(CompositionError):
            compose([("A", _A())], ENV, glue="dataflow.v1")

    def test_envelope_is_closed(self):
        bad = dict(ENV)
        bad["phenotype"] = "clever"
        with self.assertRaises(CompositionError):
            compose([("A", _A())], bad)

    def test_composition_id_and_organism_id_are_distinct_identities(self):
        c = compose([("A", _A()), ("B", _B())], ENV)
        self.assertNotEqual(c["composition_id"], hash_obj(c["manifest"]))

    def test_composition_id_is_stable_under_recompute(self):
        c = compose([("A", _A()), ("B", _B())], ENV)
        self.assertEqual(composition_id(c), c["composition_id"])


class ExactAblation(unittest.TestCase):
    def test_ablation_touches_only_the_declared_range(self):
        c = compose([("A", _A()), ("B", _B())], ENV)
        rep = ablation_report(c, "A")
        s = rep["structural"]
        self.assertEqual(s["changes_outside_declared_range"], 0)
        self.assertEqual(s["changes_to_operand_words"], 0)
        self.assertTrue(s["other_components_byte_identical"])
        self.assertTrue(s["length_preserved"])
        self.assertTrue(s["offsets_preserved"])
        self.assertTrue(s["envelope_preserved"])

    def test_ablation_changes_exactly_one_word_per_instruction(self):
        c = compose([("A", _A()), ("B", _B())], ENV)
        rep = ablation_report(c, "A")
        self.assertEqual(rep["structural"]["words_changed"],
                         rep["structural"]["instructions_in_component"])

    def test_all_nop_aliases_decode_to_nop(self):
        for w in NOP_ALIASES:
            self.assertEqual(w % N_OPCODES, 0)

    def test_non_nop_null_word_is_refused(self):
        c = compose([("A", _A())], ENV)
        with self.assertRaises(CompositionError):
            ablate(c, "A", null_word=7)

    def test_ablating_an_unknown_component_is_refused(self):
        c = compose([("A", _A())], ENV)
        with self.assertRaises(CompositionError):
            ablate(c, "Z")

    def test_ablation_records_its_parent(self):
        c = compose([("A", _A()), ("B", _B())], ENV)
        ab = ablate(c, "A")
        self.assertEqual(ab["ablated"]["parent_composition_id"], c["composition_id"])
        self.assertEqual(ab["ablated"]["component"], "A")

    def test_verdict_is_one_of_the_declared_three(self):
        c = compose([("A", _A()), ("B", _B())], ENV)
        self.assertIn(ablation_report(c, "A")["verdict"],
                      ("EXACT", "CONFOUNDED_BY_DATA_CHANNEL", "STRUCTURALLY_INEXACT"))

    def test_data_channel_confound_is_detected_when_present(self):
        """A constructed organism that READS its own opcode word must not certify EXACT.

        LDC r1,<addr of A's opcode word>; LD r2,r1; OUT r2,ch0  -- then A. The reader reports the
        word it finds at A's opcode address, so NOP-aliasing A changes the emitted value and the
        alias differential must catch it. This is the gate firing, not passing.
        """
        # The reader is 3 instructions = 12 words, so A's first opcode word is at tape index 12.
        #
        # OPERAND POSITION, THE HARD WAY. affordances.py's module docstring says "`c` is ... a
        # signed 32-bit immediate for LDC". The runtime disagrees: vm.py op==3 executes
        # `regs[a] = bw & MASK32`, i.e. the immediate is read from operand slot b (word ip+2).
        # The TABLE row is right ("a,imm"); the prose above it is wrong. Writing this genome from
        # the prose produces a silently different program -- it loads 0, reads tape[0], and the
        # confound this test exists to catch does not occur. Encoded from the RUNTIME below.
        reader = segment_from_instructions([
            3, 1, 12, 0,       # LDC r1 = 12  (immediate in slot b; word index of A's opcode)
            5, 2, 1, 0,        # LD  r2 = tape[r1]
            23, 2, 0, 0,       # OUT r2 -> channel 0
        ])
        target = segment_from_instructions([9, 1, 1, 1, 1, 0, 0, 0])   # MUL ; HALT
        env = dict(ENV)
        c = compose([("R", reader), ("A", target)], env)
        rep = ablation_report(c, "A")
        self.assertEqual(rep["verdict"], "CONFOUNDED_BY_DATA_CHANNEL")
        self.assertFalse(rep["alias_differential"]["invariant"])
        self.assertGreater(rep["alias_differential"]["distinct_transcripts"], 1)
        # and it is confounded for the DATA reason, not a structural one
        self.assertEqual(rep["structural"]["changes_outside_declared_range"], 0)
        self.assertTrue(rep["structural"]["other_components_byte_identical"])


class Activation(unittest.TestCase):
    def test_unreachable_component_is_not_activated(self):
        """A component behind an unconditional HALT never executes."""
        halt = segment_from_instructions([1, 0, 0, 0])          # HALT
        never = segment_from_instructions([7, 1, 2, 3])          # ADD, unreachable
        c = compose([("H", halt), ("NEVER", never)], ENV)
        self.assertEqual(activation_evidence(c, "NEVER")["verdict"], "NOT_ACTIVATED")

    def test_reachable_component_is_activated(self):
        c = compose([("A", _A()), ("B", _B())], ENV)
        self.assertEqual(activation_evidence(c, "A")["verdict"], "ACTIVATED")

    def test_nop_only_component_is_indeterminate_not_guessed(self):
        nops = segment_from_instructions([0, 0, 0, 0])
        c = compose([("N", nops), ("B", _B())], ENV)
        self.assertEqual(activation_evidence(c, "N")["verdict"],
                         "INDETERMINATE_COMPONENT_IS_ALREADY_NOP_CLASS")


class GoldenVectors(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(GOLDEN):
            self.skipTest("GOLDEN_VECTORS.json not emitted")
        self.doc = json.load(open(GOLDEN, encoding="utf-8"))

    def test_every_vector_self_verifies(self):
        import hashlib
        for v in self.doc["vectors"]:
            got = hashlib.sha256(v["canonical_bytes_utf8"].encode("utf-8")).hexdigest()
            self.assertEqual(got, v["sha256_hex"], v["name"])

    def test_recorded_identities_still_hold(self):
        ids = self.doc["identities"]
        self.assertEqual(segment_id(_A()), ids["segment_id_A"])
        self.assertEqual(segment_id(_B()), ids["segment_id_B"])
        ab = compose([("A", _A()), ("B", _B())], ENV)
        self.assertEqual(ab["composition_id"], ids["composition_id_AB"])
        self.assertEqual(hash_obj(ab["manifest"]), ids["organism_id_AB"])

    def test_interpretation_identity_is_published(self):
        ii = self.doc["interpretation_identity"]
        self.assertEqual(ii["runtime_hash"], RUNTIME_HASH)
        self.assertIn("affordance_hash", ii)

    def test_schema_is_the_declared_one(self):
        self.assertEqual(self.doc["composition_documents"]["AB"]["schema_version"],
                         COMPOSITION_SCHEMA)


class RuntimeUntouched(unittest.TestCase):
    def test_compose_package_is_not_part_of_the_runtime_identity(self):
        """Adding this package must not have changed any specimen's interpretation."""
        from proteus.foundry.identity import RUNTIME_SOURCE_FILES
        self.assertEqual(RUNTIME_SOURCE_FILES, ("affordances.py", "vm.py"))
        self.assertNotIn("composition.py", RUNTIME_SOURCE_FILES)


if __name__ == "__main__":
    unittest.main()
