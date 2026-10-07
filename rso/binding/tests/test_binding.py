"""BX1-BX5 on synthetic rows. Each C-004 survivor shape that the binding must refuse has a case here at the
module level; slice001's G-INV fire cases (C-009-T011) pin the same shapes end to end."""
import unittest

from rso.binding import binding as X

L = "launch-A"
NODE = "rcpt:REG:PRESERVE:STANDARD"
RID = L + "/" + NODE
RECEIPT = b'{"node_id":"rcpt:REG:PRESERVE:STANDARD","world":{"variant":"STANDARD"}}'


def rows(**node_overrides):
    node = {"kind": "RUN", "run_id": RID, "parent_run_id": L, "launch_kind": "RECEIPT", "node_id": NODE,
            "status": "COMPLETED", "receipt_sha256": X.receipt_sha256(RECEIPT)}
    node.update(node_overrides)
    return [{"kind": "RUN", "run_id": L, "launch_kind": "TOP_LEVEL", "node_id": "G0", "status": "COMPLETED"},
            node, {"kind": "TERMINAL", "row_count": 2}]


class Binds(unittest.TestCase):
    def test_sound_row_binds(self):
        self.assertEqual(X.binding_reasons(NODE, RID, RECEIPT, rows(), L), [])

    def test_no_timestamp_is_read(self):
        r = rows(start_utc="2099-01-01T00:00:00Z", end_utc="1970-01-01T00:00:00Z")
        self.assertEqual(X.binding_reasons(NODE, RID, RECEIPT, r, L), [])


class Refuses(unittest.TestCase):
    def test_later_or_earlier_window_run_is_a_foreign_launch(self):
        # R2.BROKEN.LATER_WINDOW_RUN, R2 OVERLAP_RUN, S4.PROBE.STALE_RUN: another launch's run of the same node
        other = rows()
        other.insert(1, {"kind": "RUN", "run_id": "launch-B", "launch_kind": "TOP_LEVEL", "status": "COMPLETED"})
        other[2]["parent_run_id"] = "launch-B"
        self.assertIn(X.FOREIGN_LAUNCH, X.binding_reasons(NODE, RID, RECEIPT, other, L))

    def test_failed_row_is_refused(self):
        # R2 FAILED_ROW_CITED
        self.assertIn("BIND_STATUS:FAILED", X.binding_reasons(NODE, RID, RECEIPT, rows(status="FAILED"), L))

    def test_world_substitution_is_refused(self):
        # R2 edit Y1: the row is TWINWORLD's run; node id and digest both differ
        twin = b'{"node_id":"rcpt:REG:PRESERVE:TWINWORLD","world":{"variant":"TWINWORLD"}}'
        r = rows(node_id="rcpt:REG:PRESERVE:TWINWORLD", receipt_sha256=X.receipt_sha256(twin))
        why = X.binding_reasons(NODE, RID, RECEIPT, r, L)
        self.assertIn(X.NODE_MISMATCH, why)
        self.assertIn(X.DIGEST_MISMATCH, why)

    def test_digest_alone_catches_a_relabelled_row(self):
        # the node id is copied, the digest is another receipt's (observer/world/artifact borrow, S4 X3)
        self.assertEqual(X.binding_reasons(NODE, RID, RECEIPT, rows(receipt_sha256="0" * 64), L),
                         [X.DIGEST_MISMATCH])

    def test_receipt_edit_after_the_run_is_refused(self):
        self.assertEqual(X.binding_reasons(NODE, RID, RECEIPT + b" ", rows(), L), [X.DIGEST_MISMATCH])

    def test_missing_digest(self):
        self.assertIn(X.DIGEST_MISSING, X.binding_reasons(NODE, RID, RECEIPT, rows(receipt_sha256=None), L))

    def test_no_row_and_ambiguous_row(self):
        self.assertEqual(X.binding_reasons(NODE, "nope", RECEIPT, rows(), L), [X.NO_ROW])
        r = rows()
        r.insert(2, dict(r[1]))
        self.assertEqual(X.binding_reasons(NODE, RID, RECEIPT, r, L), [X.AMBIGUOUS_ROW])

    def test_launch_must_be_anchored_present_and_completed(self):
        self.assertIn(X.LAUNCH_UNANCHORED, X.binding_reasons(NODE, RID, RECEIPT, rows(), None))
        r = rows()
        r[0]["status"] = "FAILED"
        self.assertIn("BIND_LAUNCH_NOT_COMPLETED:FAILED", X.binding_reasons(NODE, RID, RECEIPT, r, L))
        self.assertIn(X.LAUNCH_MISSING, X.binding_reasons(NODE, RID, RECEIPT, rows()[1:], L))

    def test_top_level_row_cannot_stand_for_a_node_run(self):
        self.assertIn(X.NOT_A_NODE_RUN, X.binding_reasons(NODE, L, RECEIPT, rows(), L))


class Provenance(unittest.TestCase):
    def test_other_launch_rows_are_not_own_rows(self):
        r = rows()
        r.insert(2, dict(r[1], run_id="launch-B/" + NODE, parent_run_id="launch-B"))
        self.assertEqual([x["run_id"] for x in X.own_launch_rows(r, L)], [RID])

    def test_receipt_sha256_takes_bytes_only(self):
        with self.assertRaises(TypeError):
            X.receipt_sha256("text")


class Siblings(unittest.TestCase):
    """C-009-T031 R2, CONTRACT.md s7 BX5b at the module level (opaque node ids)."""

    def _sibling(self, **over):
        r = rows()
        s = dict(r[1], run_id=RID + "#2", receipt_sha256=X.receipt_sha256(b"another receipt"))
        s.update(over)
        r.insert(2, s)
        return r

    def test_second_completed_execution_is_unreported(self):
        self.assertEqual(X.sibling_reasons(NODE, RID, self._sibling(), L), [X.SIBLING_UNREPORTED])
        self.assertEqual(X.unreported_siblings(NODE, RID, self._sibling(), L), [RID + "#2"])

    def test_sound_row_has_no_sibling(self):
        self.assertEqual(X.sibling_reasons(NODE, RID, rows(), L), [])

    def test_failed_interrupted_refused_attempts_are_provenance(self):
        for status in ("FAILED", "INTERRUPTED", "REFUSED"):
            self.assertEqual(X.sibling_reasons(NODE, RID, self._sibling(status=status), L), [], status)

    def test_other_launch_and_other_node_are_not_siblings(self):
        self.assertEqual(X.sibling_reasons(NODE, RID, self._sibling(parent_run_id="launch-B"), L), [])
        self.assertEqual(X.sibling_reasons(NODE, RID, self._sibling(node_id="rcpt:other"), L), [])
        self.assertEqual(X.sibling_reasons(NODE, RID, self._sibling(launch_kind="MUTATION_CHILD"), L), [])


class B1Pins(unittest.TestCase):
    """C-009-T031 R1 at the module level: the B1 shapes E2 / E3 survived (no module test pinned them)."""

    def test_e2_launch_row_must_be_top_level(self):
        r = rows()
        r[0]["launch_kind"] = "RECEIPT"                     # the 'launch' is a node execution row
        self.assertEqual(X.launch_reasons(r, L), [X.LAUNCH_MISSING])
        self.assertIn(X.LAUNCH_MISSING, X.binding_reasons(NODE, RID, RECEIPT, r, L))

    def test_e3_mutation_child_is_not_a_node_run(self):
        self.assertEqual(X.binding_reasons(NODE, RID, RECEIPT, rows(launch_kind="MUTATION_CHILD"), L),
                         [X.NOT_A_NODE_RUN])

    def test_e4_missing_digest_alone(self):
        self.assertEqual(X.binding_reasons(NODE, RID, RECEIPT, rows(receipt_sha256=None), L), [X.DIGEST_MISSING])


if __name__ == "__main__":
    unittest.main()
