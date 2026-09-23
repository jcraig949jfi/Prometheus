"""T-P7: verification bundle integrity. LAUNCH BLOCKER.

The same bundle is executed four ways:

  1. treatment completes before control
  2. control completes before treatment
  3. killed after treatment, before control, then resumed
  4. killed after control, before treatment, then resumed

All four must produce byte-equivalent scientific content and identical verdicts, modulo
the fields named in bundles.VOLATILE_KEYS. This is the property the predecessor lacked:
its special flags read a mutable family slot at the moment a treatment completed, so a
flag existed or did not exist depending on which worker finished first and on whether a
restart had reshuffled the queue.

The kills are simulated honestly. The first arm is written, every in-memory object is
dropped, a FRESH BundleStore is constructed from the same directory, and the second arm
is added to whatever the store rebuilds from disk. Nothing survives the kill in memory,
so a resume that depended on in-process state would fail here.

Each execution stamps DIFFERENT volatile values - timestamps, wall clock, pid, host,
paths. If scrubbing were broken the four blobs would differ, so the exclusion list is
exercised rather than assumed.

NEGATIVE CONTROL. A test that cannot fail proves nothing, so the same comparison is run
against deliberately defective bundle implementations and must reject each one:

  order_dependent_state   arrival order leaks into scientific content
  adjudicates_incomplete  a verdict is returned before the bundle is complete
  conflicting_rerun       a re-run delivers different numbers and is accepted silently
  real_difference         a genuine measured difference is NOT detected

Run:  python tests/test_p7_bundles.py
Exit: 0 all checks pass, 1 otherwise.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import bundles  # noqa: E402


# ---------------------------------------------------------------- fixtures
def make_spec():
    """Rebuilt from scratch by every execution. Because the id is content-addressed, a
    restarted process finds its own bundle on disk without remembering anything."""
    base = {"world": "GRID", "environment": "STATIC", "representation": "Z8_32",
            "self_location": "PRIMITIVE", "copy_primitive": "BYTEWISE",
            "pressure": "NONE_IMPLICIT", "structure": "WELL_MIXED",
            "task_transform": "ADD1", "read_order": "ANSWER_BEFORE_READ",
            "bridge": "VALLEY", "seeding": "RANDOM", "mutation_operator": "BOTH",
            "mutation_locality": "LOCAL", "mutation_rate": "MID", "atlas_axis": "NONE"}
    treat = bundles.ArmSpec("treatment", "TREATMENT",
                            dict(base, reproduction="ENDOGENOUS_PARTIAL"), seed=1203, tier="L")
    ctrl = bundles.ArmSpec("control", "CONTROL",
                           dict(base, reproduction="EXTERNAL"), seed=1203, tier="L")
    return bundles.BundleSpec(hypothesis_id="H4", pair_seed=1203, arms=[treat, ctrl],
                              factor_deltas={"reproduction": ["ENDOGENOUS_PARTIAL", "EXTERNAL"]},
                              expected_cardinality=2)


# Measured content is fixed per arm. Volatile content varies per execution on purpose.
MEASURED = {
    "treatment": {"held_max_final": 1.0, "held_max_ever": 1.0,
                  "crossed_ever": True, "crossed_at_final": True,
                  "replication_events": 4, "max_causal_replication_depth": 3},
    "control": {"held_max_final": 0.0, "held_max_ever": 0.125,
                "crossed_ever": False, "crossed_at_final": False,
                "replication_events": 0, "max_causal_replication_depth": 0},
}


def arm_result(arm, execution):
    """Same science every time; different wall clock, pid, host and paths each time."""
    r = dict(MEASURED[arm])
    r.update({"ts": "2026-09-22 1%d:00:00" % execution,
              "wall_s": 100.0 + execution,
              "pid": 4000 + execution,
              "host": "worker-%d" % execution,
              "path": "/tmp/exec%d/%s" % (execution, arm)})
    return r


# ---------------------------------------------------------------- executions
def _fresh_store(root):
    return bundles.BundleStore(root)


def exec_in_order(root, order, execution, state_cls, kill_after_first):
    """Add arms in `order`. If kill_after_first, drop everything and reopen from disk."""
    store = _fresh_store(root)
    spec = make_spec()
    st = store.open(spec)
    if not isinstance(st, state_cls):
        st = state_cls(spec, st.results)
    st.add_result(order[0], arm_result(order[0], execution))
    store.put(st)

    if kill_after_first:
        # THE KILL. Nothing below may reach for anything above.
        del store, st, spec
        store = _fresh_store(root)           # fresh object, same directory
        spec = make_spec()                   # recomputed, not remembered
        st = store.open(spec)                # rebuilt from disk alone
        if not isinstance(st, state_cls):
            st = state_cls(spec, st.results)

    st.add_result(order[1], arm_result(order[1], execution))
    store.put(st)
    return store.open(spec) if state_cls is bundles.BundleState else st


EXECUTIONS = (
    ("treatment first", ("treatment", "control"), False),
    ("control first", ("control", "treatment"), False),
    ("kill after treatment", ("treatment", "control"), True),
    ("kill after control", ("control", "treatment"), True),
)


def run_four(tmp, state_cls=bundles.BundleState, content_fn=bundles.content_bytes):
    rows = []
    for i, (label, order, kill) in enumerate(EXECUTIONS, start=1):
        root = pathlib.Path(tmp) / ("exec%d" % i)
        st = exec_in_order(root, order, i, state_cls, kill)
        adj = st.adjudicate()
        rows.append({"label": label, "blob": content_fn(st), "verdict": adj["verdict"],
                     "complete": st.is_complete()})
    return rows


def four_way_agrees(rows):
    blobs = {r["blob"] for r in rows}
    verds = {r["verdict"] for r in rows}
    return len(blobs) == 1 and len(verds) == 1, blobs, verds


# ---------------------------------------------------------------- defect injections
class OrderDependentState(bundles.BundleState):
    """DEFECT: arrival order leaks into the scientific content.

    `seq` is deliberately NOT in VOLATILE_KEYS. The exclusion list cannot be the only
    defence, because a future field nobody thought to exclude would slip through it. The
    four-way byte comparison is the defence that does not depend on anticipating the
    field, and this injection is what proves the comparison is live.
    """

    def add_result(self, arm_name, result):
        r = dict(result)
        r["seq"] = len(self.results)
        return bundles.BundleState.add_result(self, arm_name, r)


class AdjudicatesIncompleteState(bundles.BundleState):
    """DEFECT: the predecessor's behaviour. Evaluate against whatever has landed."""

    def adjudicate(self, rule=None):
        if not self.is_complete():
            present = {a.name: self.results[a.name] for a in self.spec.arms
                       if a.name in self.results}
            if any(self.spec.arm(n).role == "TREATMENT" for n in present):
                return {"bundle_id": self.spec.bundle_id,
                        "hypothesis_id": self.spec.hypothesis_id,
                        "verdict": "ADMISSIBLE",
                        "why": "evaluated against whatever had completed so far",
                        "numbers": {}}
        return bundles.BundleState.adjudicate(self, rule)


class SilentOverwriteState(bundles.BundleState):
    """DEFECT: a re-run delivering different numbers overwrites instead of raising."""

    def add_result(self, arm_name, result):
        self.results[arm_name] = bundles._scrub(result)
        return True


# ---------------------------------------------------------------- checks
def check_baseline(tmp, out):
    rows = run_four(pathlib.Path(tmp) / "baseline")
    ok, blobs, verds = four_way_agrees(rows)
    out("baseline four executions", ok,
        "verdict %s across all four, %d distinct blob(s)"
        % (sorted(verds)[0] if verds else "?", len(blobs)))
    for r in rows:
        out("  %-22s" % r["label"], r["complete"] and r["verdict"] != bundles.VERDICT_INCOMPLETE,
            "complete=%s verdict=%s" % (r["complete"], r["verdict"]))
    return ok


def check_incomplete_refuses(out):
    spec = make_spec()
    st = bundles.BundleState(spec)
    st.add_result("treatment", arm_result("treatment", 9))
    adj = st.adjudicate()
    ok = adj["verdict"] == bundles.VERDICT_INCOMPLETE and adj["missing_arms"] == ["control"]
    out("incomplete bundle refuses", ok,
        "verdict=%s missing=%s" % (adj["verdict"], adj.get("missing_arms")))
    return ok


def check_idempotent_readd(out):
    spec = make_spec()
    st = bundles.BundleState(spec)
    st.add_result("treatment", arm_result("treatment", 1))
    added = st.add_result("treatment", arm_result("treatment", 7))   # different volatiles only
    ok = added is False and len(st.results) == 1
    out("identical re-run is idempotent", ok,
        "second add returned %r, %d result(s) stored" % (added, len(st.results)))
    return ok


def check_conflicting_raises(out):
    spec = make_spec()
    st = bundles.BundleState(spec)
    st.add_result("treatment", arm_result("treatment", 1))
    bad = dict(arm_result("treatment", 1), held_max_final=0.25)
    try:
        st.add_result("treatment", bad)
        ok, detail = False, "accepted a conflicting result silently"
    except bundles.BundleError as e:
        ok, detail = True, str(e)[:58]
    out("conflicting re-run raises", ok, detail)
    return ok


def check_unknown_arm_raises(out):
    spec = make_spec()
    st = bundles.BundleState(spec)
    try:
        st.add_result("not_an_arm", arm_result("treatment", 1))
        ok, detail = False, "accepted an undeclared arm"
    except bundles.BundleError as e:
        ok, detail = True, str(e)[:58]
    out("undeclared arm raises", ok, detail)
    return ok


def check_id_is_content_addressed(out):
    a, b = make_spec(), make_spec()
    ok_same = a.bundle_id == b.bundle_id
    arms = list(reversed(list(a.arms)))
    c = bundles.BundleSpec(a.hypothesis_id, a.pair_seed, arms, a.factor_deltas, 2)
    ok_order = c.bundle_id == a.bundle_id
    d = bundles.BundleSpec(a.hypothesis_id, 9999, list(a.arms), a.factor_deltas, 2)
    ok_diff = d.bundle_id != a.bundle_id
    ok = ok_same and ok_order and ok_diff
    out("bundle_id content-addressed", ok,
        "stable=%s order-invariant=%s seed-sensitive=%s" % (ok_same, ok_order, ok_diff))
    return ok


def check_spec_immutable(out):
    spec = make_spec()
    try:
        spec.pair_seed = 7
        ok, detail = False, "BundleSpec accepted an attribute assignment"
    except bundles.BundleError as e:
        ok, detail = True, str(e)[:58]
    out("spec is immutable", ok, detail)
    return ok


def check_cardinality_mismatch_raises(out):
    spec = make_spec()
    try:
        bundles.BundleSpec(spec.hypothesis_id, spec.pair_seed, list(spec.arms),
                           spec.factor_deltas, expected_cardinality=3)
        ok, detail = False, "accepted a cardinality its arm list contradicts"
    except bundles.BundleError as e:
        ok, detail = True, str(e)[:58]
    out("cardinality mismatch raises", ok, detail)
    return ok


def check_atomic_write(tmp, out):
    root = pathlib.Path(tmp) / "atomic"
    store = bundles.BundleStore(root)
    spec = make_spec()
    st = store.open(spec)
    st.add_result("treatment", arm_result("treatment", 1))
    store.put(st)
    st.add_result("control", arm_result("control", 1))
    store.put(st)
    leftovers = sorted(p.name for p in root.glob("*.tmp"))
    files = sorted(p.name for p in root.glob("*.json"))
    reloaded = bundles.BundleStore(root).get(spec.bundle_id)
    ok = (not leftovers and files == ["%s.json" % spec.bundle_id]
          and reloaded is not None and reloaded.is_complete())
    out("atomic write leaves no temp", ok,
        "%d json, %d tmp, reload complete=%s"
        % (len(files), len(leftovers), reloaded is not None and reloaded.is_complete()))
    return ok


# ---------------------------------------------------------------- negative control
def neg_order_dependent(tmp):
    rows = run_four(pathlib.Path(tmp) / "neg_order", state_cls=OrderDependentState)
    ok, blobs, _ = four_way_agrees(rows)
    return (not ok), "%d distinct blobs (order leaked into content)" % len(blobs)


def neg_adjudicates_incomplete(tmp):
    spec = make_spec()
    st = AdjudicatesIncompleteState(spec)
    st.add_result("treatment", arm_result("treatment", 1))
    adj = st.adjudicate()
    leaked = adj["verdict"] != bundles.VERDICT_INCOMPLETE
    return leaked, "incomplete bundle returned verdict %r" % adj["verdict"]


def neg_silent_overwrite(tmp):
    spec = make_spec()
    st = SilentOverwriteState(spec)
    st.add_result("treatment", arm_result("treatment", 1))
    st.add_result("treatment", dict(arm_result("treatment", 1), held_max_final=0.25))
    changed = (st.results["treatment"]["held_max_final"] == 0.25)
    return changed, "conflicting re-run silently overwrote held_max_final"


def neg_real_difference(tmp):
    """A genuine measured difference MUST break byte equality, or the comparison is
    vacuous and would pass on anything."""
    root = pathlib.Path(tmp) / "neg_real"
    a = exec_in_order(root / "a", ("treatment", "control"), 1, bundles.BundleState, False)
    saved = dict(MEASURED["control"])
    try:
        MEASURED["control"]["held_max_final"] = 0.99
        b = exec_in_order(root / "b", ("treatment", "control"), 1, bundles.BundleState, False)
    finally:
        MEASURED["control"].clear()
        MEASURED["control"].update(saved)
    differs = bundles.content_bytes(a) != bundles.content_bytes(b)
    return differs, "a real numeric change broke byte equality as it must"


NEGATIVE = {
    "order_dependent_state": neg_order_dependent,
    "adjudicates_incomplete": neg_adjudicates_incomplete,
    "conflicting_rerun": neg_silent_overwrite,
    "real_difference_detected": neg_real_difference,
}


# ---------------------------------------------------------------- main
def main():
    tmp = tempfile.mkdtemp(prefix="p7bundles_")
    results = []

    def out(name, ok, detail):
        results.append(ok)
        print("%-4s %-30s %s" % ("PASS" if ok else "FAIL", name, detail))

    try:
        print("T-P7  verification bundle integrity")
        print("-" * 96)
        check_baseline(tmp, out)
        check_incomplete_refuses(out)
        check_idempotent_readd(out)
        check_conflicting_raises(out)
        check_unknown_arm_raises(out)
        check_id_is_content_addressed(out)
        check_spec_immutable(out)
        check_cardinality_mismatch_raises(out)
        check_atomic_write(tmp, out)

        print()
        print("negative control: each injected defect must be CAUGHT")
        print("-" * 96)
        for name, fn in NEGATIVE.items():
            caught, detail = fn(tmp)
            results.append(caught)
            print("%-4s %-30s %s" % ("PASS" if caught else "FAIL", name,
                                     detail if caught else "NOT CAUGHT: " + detail))

        print("-" * 96)
        print("VOLATILE_KEYS (%d): %s" % (len(bundles.VOLATILE_KEYS),
                                          ", ".join(sorted(bundles.VOLATILE_KEYS))))
        ok = all(results)
        print("T-P7: %s  (%d checks, %d failed)"
              % ("PASS" if ok else "FAIL", len(results), sum(1 for r in results if not r)))
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
