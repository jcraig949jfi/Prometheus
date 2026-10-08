"""Tests for the witness evaluator (C-010-T012), on SYNTHETIC bundles built here.

No registered subject, arm or seed list is run or read (PREREGISTRATION s10 gate): the organisms are fake action
arrays with known counts, written in the driver's bundle layout (run_witness.py: receipts/, artifacts/<sha256>,
inventory.json, run.json, MANIFEST.json) with the producer's artifact listings (ares_client: role, sha256, length,
dtype, shape). The world's oracle (r, interrupt steps) is real: W15 resets only, no organism. Expected classes come
from PREREGISTRATION s5-s6 and RULER.md, never from the evaluator's output.
"""
import copy
import hashlib
import json
import os
import random
import shutil
import tempfile
import unittest

import numpy as np

from rso.witness import ruler as RUL
from rso.binding import binding as B
from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.witness import ares_client as AC
from rso.witness import evaluate as WE
from rso.witness import ruler as RU
from rso.witness.challenge.W1 import cases as C

D4, D15 = "4" * 64, "f" * 64          # synthetic subject genome digests (S4 primary, S15 secondary)
LAUNCH = "w-test-launch"
REGISTERED_AT, FIRST_CHECK, LATE = "2026-10-07T00:00:00Z", "2026-10-07T01:00:00Z", "2026-10-07T02:00:00Z"
N = RU.N_EPISODES
T = 40

_SEEDS = {}


def witness_seeds():
    """2048 seeds >= 900000, balanced on the world's r (1024 each), in order: a synthetic stand-in for the
    registered list (same generator shape, not the registered list)."""
    if "w" not in _SEEDS:
        w = AC.world("W15", "present")
        out, c = [], {0: 0, 1: 0}
        s = 900000
        while len(out) < N:
            w.reset(np.random.default_rng(s), 1)
            if c[w.r] < N // 2:
                out.append(s)
                c[w.r] += 1
            s += 1
        _SEEDS["w"] = out
    return list(_SEEDS["w"])


def oracle(seeds, mode="present"):
    w = AC.world("W15", mode)
    regs, steps = [], []
    for s in seeds:
        w.reset(np.random.default_rng(s), 1)
        regs.append(int(w.r))
        steps.append(sorted(int(x) for x in w.reset_steps))
    return regs, steps


def episode_actions(decisions, steps):
    """(E, T, 1) int8: every step after the episode's last interrupt answers `decision`; earlier steps abstain."""
    a = np.zeros((len(decisions), T, 1), dtype=np.int8)
    for e, (d, st) in enumerate(zip(decisions, steps)):
        a[e, max(st) + 1:, 0] = d
    return a


def policy(p, seed=0):
    """Correct (r + 1) with probability p, otherwise the other action."""
    rng = random.Random(seed)
    return lambda r: r + 1 if rng.random() < p else 2 - r


def const(d):
    return lambda r: d


def exact_correct(k):
    """Correct on the first k episodes, wrong after (deterministic counts)."""
    state = {"i": 0}

    def f(r):
        state["i"] += 1
        return r + 1 if state["i"] <= k else 2 - r
    return f


class Spec(object):
    """What the synthetic bundle contains. Every field is the test's own knob; defaults give two qualified subjects:
    S4 POSITIVE (P-CHAN PASS), S15 NEGATIVE."""

    def __init__(self, **kw):
        self.ret = {D4: policy(0.65, 1), D15: const(1)}
        self.nopl = {D4: const(1), D15: const(1)}
        self.null, self.shuf, self.pos = const(1), const(1), policy(0.9, 2)
        self.obs_differs = {D4: False, D15: False}
        self.pres_differs = {D4: False, D15: False}
        self.erase_differs = {D4: False, D15: False}
        self.leak_differs = {D4: True, D15: True}
        self.nopl_seeds = None            # a different seed order for S-NOPL (pairing violation)
        for k, v in kw.items():
            setattr(self, k, v)


def _listing(role, data, dtype, shape):
    return {"role": role, "sha256": hashlib.sha256(data).hexdigest(), "length": len(data), "dtype": dtype,
            "shape": shape}


def _array(role, arr):
    arr = np.ascontiguousarray(arr)
    data = arr.tobytes()
    return _listing(role, data, str(arr.dtype), [int(x) for x in arr.shape]), data


def _json(role, obj):
    data = json.dumps(obj).encode("ascii")
    return _listing(role, data, "json", [len(obj)]), data


def _receipt(digest, arm, predicate, seeds, mode, outputs, oracle_):
    return {"schema": AC.SCHEMA, "node_id": AC.node_id(digest, arm, predicate, "W15"),
            "subject": {"runtime": "ares", "genome_sha256": digest, "arm_genome_sha256": digest},
            "arm": arm, "predicate": predicate, "world": {"name": "W15", "mode": mode},
            "seeds": [int(s) for s in seeds], "observer": AC.OBSERVER_ID,
            "outputs": [a for a, _ in outputs], "oracle": [a for a, _ in oracle_],
            "execution": {"status": "COMPLETED"}, "code": []}


def _ret_node(digest, arm, predicate, decide, seeds, mode="present"):
    regs, steps = oracle(seeds, mode)
    acts = episode_actions([decide(r) for r in regs], steps)
    outs = [_array("trace:actions", acts)]
    orc = [_array("oracle:regimes", np.array(regs, dtype=np.int8)), _json("oracle:reset_steps", steps)]
    return _receipt(digest, arm, predicate, seeds, mode, outs, orc), outs + orc


def _pair_node(digest, arm, predicate, roles, n, differs):
    """P-PRES (k = 2: warmup, seed) or P-ERASE (k = 3: pre_a, pre_b, probe) on the registered SHAPE (W1 cases'
    generators, non-registered ranges), with the world's regimes per seed group as its oracle."""
    k = 3 if predicate == "P-ERASE" else 2
    groups = C.erase_like() if k == 3 else C.pres_like()
    assert len(groups) == n
    seeds = C.flat(groups)
    a = np.ones((n, T), dtype=np.int8)
    b = a.copy()
    if differs:
        b[n // 2, T - 1] = 2
    regs, _ = oracle(seeds)
    outs = [_array(roles[0], a), _array(roles[1], b)]
    orc = [_array("oracle:regimes", np.array(regs, dtype=np.int8).reshape(n, k))]
    return _receipt(digest, arm, predicate, seeds, "present", outs, orc), outs + orc


def _obs_node(digest, differs):
    seeds = witness_seeds()          # P-OBS on EVERY witness seed (PREREGISTRATION s5; C-010-T033 integration)
    a = np.ones((len(seeds), T, 1), dtype=np.int8)
    b = a.copy()
    if differs:
        b[1, 3, 0] = 2
    regs, steps = oracle(seeds)
    outs = [_array("trace:actions_record", a), _array("trace:actions_norecord", b)]
    orc = [_array("oracle:regimes", np.array(regs, dtype=np.int8)), _json("oracle:reset_steps", steps)]
    return _receipt(digest, "S", "P-OBS", seeds, "present", outs, orc), outs + orc


def plan(spec):
    """[(receipt dict, [(listing, bytes)])] for the full registered node set."""
    seeds = witness_seeds()
    nodes = []
    for d in (D4, D15):
        nodes.append(_ret_node(d, "S", "P-RET", spec.ret[d], seeds))
        nodes.append(_ret_node(d, "S-NOPL", "P-CHAN", spec.nopl[d], spec.nopl_seeds or seeds))
        nodes.append(_obs_node(d, spec.obs_differs[d]))
        nodes.append(_pair_node(d, "S", "P-PRES", ("trace:pres_warm", "trace:pres_fresh"), len(C.pres_like()),
                                spec.pres_differs[d]))
        nodes.append(_pair_node(d, "S", "P-ERASE", ("trace:probe_after_a", "trace:probe_after_b"), len(C.erase_like()),
                                spec.erase_differs[d]))
        nodes.append(_pair_node(d, "S-LEAK", "P-ERASE", ("trace:probe_after_a", "trace:probe_after_b"),
                                len(C.erase_like()), spec.leak_differs[d]))
    nodes.append(_ret_node(D4, "NULL", "P-CAL", spec.null, seeds))
    nodes.append(_ret_node(D4, "SHUF", "P-CAL", spec.shuf, seeds, mode="shuffled"))
    nodes.append(_ret_node(D4, "POS", "P-CAL", spec.pos, seeds))
    return nodes


def write_bundle(root, nodes, rows_edit=None):
    """The driver's layout. rows_edit(rows) may rewrite the inventory rows before they are written."""
    os.makedirs(os.path.join(root, "receipts"))
    os.makedirs(os.path.join(root, "artifacts"))
    rows = [{"kind": "RUN", "run_id": LAUNCH, "launch_kind": "TOP_LEVEL", "node_id": "WITNESS:test",
             "status": "COMPLETED", "cpu_us": 0, "artifact_bytes": 0}]
    man_nodes = []
    for i, (rec, arts) in enumerate(nodes):
        data = R.canonical_bytes(rec)
        fname = "receipts/R%03d.json" % i
        with open(os.path.join(root, fname), "wb") as f:
            f.write(data)
        for listing, b in arts:
            p = os.path.join(root, "artifacts", listing["sha256"])
            if not os.path.exists(p):
                with open(p, "wb") as f:
                    f.write(b)
        run_id = "%s/%s" % (LAUNCH, rec["node_id"])
        rows.append({"kind": "RUN", "run_id": run_id, "parent_run_id": LAUNCH, "launch_kind": "RECEIPT",
                     "node_id": rec["node_id"], "status": "COMPLETED", "receipt_sha256": B.receipt_sha256(data),
                     "cpu_us": 1, "artifact_bytes": len(data)})
        man_nodes.append({"node_id": rec["node_id"], "run_id": run_id, "arm": rec["arm"],
                          "predicate": rec["predicate"], "subject_sha256": rec["subject"]["genome_sha256"],
                          "receipt_file": fname, "artifacts": [l for l, _ in arts]})
    if rows_edit:
        rows = rows_edit(rows)
    rows = rows + [{"kind": "TERMINAL", "row_count": len(rows)}]
    inv = R.canonical_bytes({"schema": "rso.witness.inventory.v0", "rows": rows})
    man = R.canonical_bytes({"schema": "rso.witness.manifest.v0", "launch_run_id": LAUNCH, "label": "test",
                             "world": "W15", "code_commit": "0" * 40, "nodes": man_nodes, "subjects": []})
    for name, data in (("inventory.json", inv), ("run.json", R.canonical_bytes({"run_id": LAUNCH})),
                       ("MANIFEST.json", man)):
        with open(os.path.join(root, name), "wb") as f:
            f.write(data)
    return man, inv


def keeper(man, inv, at=REGISTERED_AT, skip=()):
    rows = []
    if "EVIDENCE_MANIFEST" not in skip:
        rows.append({"record_kind": "EVIDENCE_MANIFEST", "blob_sha256": hashlib.sha256(man).hexdigest(),
                     "registered_at_utc": at, "repo_path": "MANIFEST.json", "row_id": 1})
    if "RUN_INVENTORY" not in skip:
        rows.append({"record_kind": "RUN_INVENTORY", "blob_sha256": hashlib.sha256(inv).hexdigest(),
                     "registered_at_utc": at, "repo_path": "inventory.json", "row_id": 2})
    return EV.FixtureStore(rows)


SUBJECTS = {"S4": D4, "S15": D15}


def seed_lists(witness=None):
    """The registered seed lists the evaluator requires (make_configs SEED_LISTS.json "seeds"), test stand-ins."""
    return {"witness": witness or witness_seeds(), "erase": C.flat(C.erase_like()), "pres": C.flat(C.pres_like())}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="rso-witness-eval-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_eval(self, spec=None, nodes=None, rows_edit=None, store=None, after_write=None, **kw):
        nodes = nodes if nodes is not None else plan(spec or Spec())
        root = os.path.join(self.tmp, "bundle")
        man, inv = write_bundle(root, nodes, rows_edit)
        if after_write:
            after_write(root)
        store = store if store is not None else keeper(man, inv)
        kw.setdefault("seed_lists", seed_lists())
        return WE.evaluate([root], store, FIRST_CHECK, SUBJECTS, primary="S4", **kw)

    def classes(self, res):
        return {k: v["class"] for k, v in res["subjects"].items()}


class TestClasses(Base):
    def test_positive_and_negative(self):
        res = self.run_eval()
        self.assertEqual(self.classes(res), {"S4": "POSITIVE", "S15": "NEGATIVE"})
        s4 = res["subjects"]["S4"]
        self.assertEqual((s4["P-RET"]["value"], s4["P-CHAN"]["value"]), ("POSITIVE", "PASS"))
        self.assertEqual(res["P-CAL"]["value"], "PASS")

    def test_positive_channel_unidentified(self):
        res = self.run_eval(Spec(nopl={D4: policy(0.65, 1), D15: const(1)}))
        self.assertEqual(self.classes(res)["S4"], "POSITIVE (channel unidentified)")
        self.assertEqual(res["subjects"]["S4"]["P-CHAN"]["witness"]["why"], "NOPL_NOT_NEGATIVE")

    def test_indeterminate_and_not_shown_are_detection_unqualified(self):
        res = self.run_eval(Spec(ret={D4: exact_correct(1075), D15: policy(0.35, 3)}))
        self.assertEqual(self.classes(res), {"S4": "DETECTION_UNQUALIFIED", "S15": "DETECTION_UNQUALIFIED"})
        self.assertEqual(res["subjects"]["S4"]["P-RET"]["value"], "INDETERMINATE")
        self.assertEqual(res["subjects"]["S15"]["P-RET"]["value"], "NOT_SHOWN")

    def test_result_is_canonical_and_deterministic(self):
        a = R.canonical_bytes(self.run_eval())
        shutil.rmtree(self.tmp)
        os.makedirs(self.tmp)
        self.assertEqual(R.canonical_bytes(self.run_eval()), a)


class TestGateFailures(Base):
    def _du(self, res, subject="S4"):
        """The subject is DETECTION_UNQUALIFIED; returns its reasons joined, for substring checks."""
        self.assertEqual(res["subjects"][subject]["class"], "DETECTION_UNQUALIFIED")
        return " | ".join(res["subjects"][subject]["why"])

    def test_p_cal_fail_unqualifies_every_subject(self):
        res = self.run_eval(Spec(null=policy(0.6, 4)))
        self.assertEqual(res["P-CAL"]["value"], "FAIL")
        self.assertIn("P-CAL FAIL", self._du(res, "S4"))
        self.assertIn("P-CAL FAIL", self._du(res, "S15"))

    def test_p_obs_fail(self):
        self.assertIn("P-OBS FAIL", self._du(self.run_eval(Spec(obs_differs={D4: True, D15: False}))))

    def test_p_pres_fail(self):
        self.assertIn("P-PRES FAIL", self._du(self.run_eval(Spec(pres_differs={D4: True, D15: False}))))

    def test_p_erase_subject_carries_over(self):
        self.assertIn("P-ERASE FAIL", self._du(self.run_eval(Spec(erase_differs={D4: True, D15: False}))))

    def test_p_erase_leak_not_exhibited(self):
        self.assertIn("P-ERASE DETECTION_UNQUALIFIED",
                      self._du(self.run_eval(Spec(leak_differs={D4: False, D15: True}))))

    def test_p_chan_unpaired_seeds_refused(self):
        # T031 (ADJUDICATION_W1 R2): S-NOPL must run the registered witness list exactly, so an unpaired (reordered)
        # list is now an unregistered node -> UNQUALIFIED, before the T012 SEEDS_NOT_PAIRED gate is reached.
        res = self.run_eval(Spec(nopl_seeds=list(reversed(witness_seeds()))))
        why = " ".join(res["subjects"]["S4"]["why"])
        self.assertIn("SEEDS_NOT_REGISTERED", why)
        self.assertIn("P-CHAN", why)
        self.assertEqual(self.classes(res)["S4"], "UNQUALIFIED")


class TestRefusals(Base):
    def _refused(self, res, code):
        self.assertEqual(self.classes(res), {"S4": "UNQUALIFIED", "S15": "UNQUALIFIED"})
        self.assertTrue(any(code in w for w in res["bundles"][0]["refused"]), res["bundles"][0]["refused"])

    def test_p_flat_nested_parent(self):
        def nest(rows):
            rows[2]["parent_run_id"] = rows[1]["run_id"]
            return rows
        self._refused(self.run_eval(rows_edit=nest), "P-FLAT")

    def test_p_flat_digestless_completed_row(self):
        def strip(rows):
            del rows[3]["receipt_sha256"]
            return rows
        self._refused(self.run_eval(rows_edit=strip), "P-FLAT")

    def test_p_flat_duplicate_node(self):
        def dup(rows):
            return rows + [dict(rows[1], run_id=rows[1]["run_id"] + "#2")]
        self._refused(self.run_eval(rows_edit=dup), "P-FLAT")

    def test_p_flat_other_launch_rows_are_refused_as_frozen(self):
        # PREREGISTRATION s5 as frozen: EVERY RECEIPT row's parent is the anchored launch. An inventory that also
        # holds another launch's rows (ledger.inventory() over a shared store) is refused. Escalation C-010-T012_1
        # asks the coordinator whether T020 uses one ledger store per launch or the rule is read per launch.
        def other_launch(rows):
            return rows + [{"kind": "RUN", "run_id": "w-other", "launch_kind": "TOP_LEVEL", "node_id": "WITNESS:o",
                            "status": "COMPLETED"},
                           dict(rows[1], run_id="w-other/x", parent_run_id="w-other", node_id="x")]
        self._refused(self.run_eval(rows_edit=other_launch), "P-FLAT:NESTED_OR_FOREIGN_PARENT:w-other/x")

    def test_receipt_digest_mismatch(self):
        def edit(root):
            p = os.path.join(root, "receipts", "R000.json")
            data = open(p, "rb").read()
            open(p, "wb").write(data.replace(b'"P-RET"', b'"P-REX"'))
        self._refused(self.run_eval(after_write=edit), "BIND_DIGEST_MISMATCH")

    def test_artifact_bytes_tampered(self):
        def tamper(root):
            d = os.path.join(root, "artifacts")
            name = sorted(os.listdir(d))[0]
            data = bytearray(open(os.path.join(d, name), "rb").read())
            data[0] ^= 1
            open(os.path.join(d, name), "wb").write(bytes(data))
        self._refused(self.run_eval(after_write=tamper), "ARTIFACT_MISMATCH")

    def test_oracle_counterfeit_is_refused(self):
        # A producer that flips the regimes it reports (and re-hashes consistently) cannot move the ruler: the
        # evaluator recomputes r from the seeds through the world alone.
        nodes = plan(Spec())
        rec, arts = nodes[0]
        regs = np.frombuffer(arts[1][1], dtype=np.int8) ^ 1
        new = _array("oracle:regimes", regs.astype(np.int8))
        rec = copy.deepcopy(rec)
        rec["oracle"][0] = new[0]
        nodes[0] = (rec, [arts[0], new, arts[2]])
        self._refused(self.run_eval(nodes=nodes), "ORACLE_MISMATCH")

    def test_custody_unqualified(self):
        def no_inventory(man, inv):
            return keeper(man, inv, skip=("RUN_INVENTORY",))
        root = os.path.join(self.tmp, "b")
        man, inv = write_bundle(root, plan(Spec()))
        res = WE.evaluate([root], no_inventory(man, inv), FIRST_CHECK, SUBJECTS, primary="S4", seed_lists=seed_lists())
        self.assertEqual(self.classes(res), {"S4": "UNQUALIFIED", "S15": "UNQUALIFIED"})
        self.assertIn("KEEPER_ROW_MISSING:RUN_INVENTORY", res["bundles"][0]["custody"]["why"])
        res = WE.evaluate([root], keeper(man, inv, at=LATE), FIRST_CHECK, SUBJECTS, primary="S4",
                          seed_lists=seed_lists())
        self.assertIn("REGISTERED_AFTER_CHECK", res["bundles"][0]["custody"]["why"])

    def test_missing_node_is_evidence_missing(self):
        nodes = [n for n in plan(Spec()) if not (n[0]["arm"] == "S-LEAK" and n[0]["subject"]["genome_sha256"] == D15)]
        res = self.run_eval(nodes=nodes)
        self.assertEqual(self.classes(res)["S15"], "UNQUALIFIED")
        self.assertTrue(any("EVIDENCE_MISSING" in w for w in res["subjects"]["S15"]["why"]))
        self.assertEqual(self.classes(res)["S4"], "POSITIVE")


class TestTrustNothing(Base):
    def test_producer_claims_are_ignored(self):
        # A receipt carrying its own verdict (bound by the digest, so it binds) changes nothing.
        nodes = plan(Spec())
        rec = copy.deepcopy(nodes[6][0])                     # S15 P-RET (NEGATIVE)
        self.assertEqual((rec["subject"]["genome_sha256"], rec["predicate"]), (D15, "P-RET"))
        rec["claimed"] = {"P-RET": "POSITIVE", "correct": 2048}
        nodes[6] = (rec, nodes[6][1])
        self.assertEqual(self.classes(self.run_eval(nodes=nodes))["S15"], "NEGATIVE")

    def test_registered_seed_list_is_enforced(self):
        res = self.run_eval(seed_lists=seed_lists(list(reversed(witness_seeds()))))
        self.assertEqual(self.classes(res), {"S4": "UNQUALIFIED", "S15": "UNQUALIFIED"})
        self.assertTrue(any("SEEDS_NOT_REGISTERED" in w for w in res["subjects"]["S4"]["why"]))

    def test_population_of_more_than_one_organism_is_refused(self):
        nodes = plan(Spec())
        rec, arts = nodes[0]
        acts = np.frombuffer(arts[0][1], dtype=np.int8).reshape(N, T, 1)
        two = _array("trace:actions", np.concatenate([acts, acts], axis=2))
        rec = copy.deepcopy(rec)
        rec["outputs"][0] = two[0]
        nodes[0] = (rec, [two, arts[1], arts[2]])
        res = self.run_eval(nodes=nodes)
        self.assertEqual(self.classes(res)["S4"], "UNQUALIFIED")
        self.assertTrue(any("SHAPE" in w for w in res["subjects"]["S4"]["why"]))


# --------------------------------------------------------------------------------------------------------
# C-010-T031: the one repair round after the W1 challenge (rso/witness/ADJUDICATION_W1.md R1-R4, R6 pins). The
# broken / sound shapes are the reviewer's committed builders (rso/witness/challenge/W1/cases.py); expected
# verdicts are the reviewer's expected.json.

W1_LISTS = None


def w1_lists():
    global W1_LISTS
    if W1_LISTS is None:
        W1_LISTS = {"witness": C.witness_like(), "erase": C.flat(C.erase_like()), "pres": C.flat(C.pres_like())}
    return W1_LISTS


def w1_eval(roots, store, subjects=None):
    return WE.evaluate(roots, store, C.FIRST_CHECK, subjects or C.SUBJECTS, "S4", seed_lists=w1_lists())


class TestW1Repairs(Base):
    def _dir(self, name):
        d = os.path.join(self.tmp, name)
        os.makedirs(d)
        return d

    def test_r1_b1_duplicate_node_across_bundles(self):
        b = C.build_b1(self._dir("b1"))
        xy = w1_eval([b["X"], b["Y"]], b["store"])
        yx = w1_eval([b["Y"], b["X"]], b["store"])
        self.assertEqual(xy["subjects"]["S4"]["class"], "UNQUALIFIED")
        self.assertTrue(any("EVIDENCE_DUPLICATE" in w for w in xy["subjects"]["S4"]["why"]), xy["subjects"]["S4"]["why"])
        self.assertEqual(xy["subjects"], yx["subjects"])                      # order-independent
        self.assertEqual(xy["P-CAL"], yx["P-CAL"])

    def test_r1_result_names_the_launch_of_each_node(self):
        res = self.run_eval()
        sup = res["supplied_by"]
        self.assertEqual(set(sup.values()), {LAUNCH})
        self.assertIn(AC.node_id(D4, "S", "P-RET", "W15"), sup)

    def test_r2_b2_p_cal_on_an_unregistered_list(self):
        b = C.build_b2(self._dir("b2"))
        res = w1_eval(b["roots"], b["store"])
        self.assertEqual(res["P-CAL"]["value"], "BLOCKED")
        self.assertIn("SEEDS_NOT_REGISTERED", res["P-CAL"]["reason"])
        self.assertEqual({k: v["class"] for k, v in res["subjects"].items()}, {"S4": "UNQUALIFIED", "S15": "UNQUALIFIED"})

    def test_r2_seed_lists_are_required(self):
        root = os.path.join(self.tmp, "b")
        man, inv = write_bundle(root, plan(Spec()))
        with self.assertRaises(TypeError):
            WE.evaluate([root], keeper(man, inv), FIRST_CHECK, SUBJECTS, primary="S4")
        with self.assertRaises(ValueError):
            WE.evaluate([root], keeper(man, inv), FIRST_CHECK, SUBJECTS, primary="S4", seed_lists={"witness": []})
        with self.assertRaises(SystemExit):
            WE.main([root, "--subjects", "S4=" + D4, "--first-check", FIRST_CHECK])

    def test_r2_every_node_on_its_registered_list(self):
        lists = seed_lists()
        lists["erase"] = list(reversed(lists["erase"]))
        res = self.run_eval(seed_lists=lists)
        for name in ("S4", "S15"):
            self.assertEqual(res["subjects"][name]["class"], "UNQUALIFIED")
            self.assertTrue(any("SEEDS_NOT_REGISTERED" in w and "P-ERASE" in w for w in res["subjects"][name]["why"]))

    def test_r3_b3_same_regime_triples(self):
        b = C.build_b3(self._dir("b3"))
        res = w1_eval(b["roots"], b["store"])
        self.assertEqual(res["subjects"]["S4"]["class"], "UNQUALIFIED")
        self.assertTrue(any("ERASE_SHAPE" in w or "SEEDS_NOT_REGISTERED" in w for w in res["subjects"]["S4"]["why"]))

    def test_r3_erase_shape_on_the_registered_list(self):
        # Even when the registered list itself is malformed (pre_b r = 0), the shape check refuses (R3 is not R2).
        same = C.erase_like(C.ERASE_SAME_START, same_regime=True)
        nodes = plan(Spec())
        for i, (rec, arts) in enumerate(nodes):
            if rec["predicate"] == "P-ERASE":
                n = len(same)
                a = np.ones((n, T), dtype=np.int8)
                b = a.copy()
                if rec["arm"] == "S-LEAK":
                    b[0, 0] = 2
                regs, _ = oracle(C.flat(same))
                outs = [_array("trace:probe_after_a", a), _array("trace:probe_after_b", b)]
                orc = [_array("oracle:regimes", np.array(regs, dtype=np.int8).reshape(n, 3))]
                nodes[i] = (_receipt(rec["subject"]["genome_sha256"], rec["arm"], "P-ERASE", C.flat(same), "present",
                                     outs, orc), outs + orc)
        lists = seed_lists()
        lists["erase"] = C.flat(same)
        res = self.run_eval(nodes=nodes, seed_lists=lists)
        self.assertTrue(any("ERASE_SHAPE" in w for w in res["subjects"]["S4"]["why"]), res["subjects"]["S4"]["why"])

    def test_r3_pres_warmup_must_be_opposite(self):
        groups = C.pres_like()
        bad = [(g[1], g[1] + 0) for g in groups[:1]] + groups[1:]           # first pair: warm-up = the seed itself
        nodes = plan(Spec())
        for i, (rec, arts) in enumerate(nodes):
            if rec["predicate"] == "P-PRES":
                n = len(bad)
                a = np.ones((n, T), dtype=np.int8)
                regs, _ = oracle(C.flat(bad))
                outs = [_array("trace:pres_warm", a), _array("trace:pres_fresh", a.copy())]
                orc = [_array("oracle:regimes", np.array(regs, dtype=np.int8).reshape(n, 2))]
                nodes[i] = (_receipt(rec["subject"]["genome_sha256"], "S", "P-PRES", C.flat(bad), "present", outs, orc),
                            outs + orc)
        lists = seed_lists()
        lists["pres"] = C.flat(bad)
        res = self.run_eval(nodes=nodes, seed_lists=lists)
        self.assertTrue(any("PRES_SHAPE" in w for w in res["subjects"]["S4"]["why"]), res["subjects"]["S4"]["why"])

    def test_r4_b5_node_id_fields_disagree(self):
        b = C.build_b5(self._dir("b5"))
        res = w1_eval(b["roots"], b["store"])
        self.assertEqual(res["subjects"]["S4"]["class"], "UNQUALIFIED")
        self.assertTrue(any("NODE_ID_FIELDS" in w for w in res["bundles"][0]["refused"]), res["bundles"][0]["refused"])

    def test_r6_s3_decided_after_the_last_interrupt(self):
        # W1.S3 (sound): correct answers only in (first interrupt, last interrupt], abstain after the last: NEGATIVE.
        # Integration (C-010-T033): P-OBS must run on EVERY witness seed, and the reviewer's frozen S3 builder runs it on
        # a prefix, so the full evaluation refuses the bundle before P-RET; the window rule E1 lives in episodes(), so
        # it is pinned here on the bundle's S/P-RET node directly.
        b = C.build_s3(self._dir("s3"))
        nodes = {}
        for r in b["roots"]:
            nodes.update(WE.check_bundle(r, b["store"], C.FIRST_CHECK)["nodes"])
        ret = [n for nid, n in nodes.items() if n["receipt"]["arm"] == "S" and n["receipt"]["predicate"] == "P-RET"
               and n["receipt"]["subject"]["genome_sha256"] == C.SUBJECTS["S4"]]
        self.assertEqual(len(ret), 1)
        out = RUL.p_ret(WE.episodes(ret[0]))
        self.assertEqual((out["value"], out["successes"], out["wrong"]), ("NEGATIVE", 0, 0))

    def test_r6_e3_run_unreported_with_a_reregistered_manifest(self):
        root = os.path.join(self.tmp, "b")
        man, inv = write_bundle(root, plan(Spec()))
        doc = json.loads(man.decode("utf-8"))
        dropped = doc["nodes"].pop(0)
        man2 = R.canonical_bytes(doc)
        with open(os.path.join(root, "MANIFEST.json"), "wb") as f:
            f.write(man2)
        res = WE.evaluate([root], keeper(man2, inv), FIRST_CHECK, SUBJECTS, primary="S4", seed_lists=seed_lists())
        self.assertTrue(any(w.startswith("RUN_UNREPORTED:") and dropped["node_id"] in w
                            for w in res["bundles"][0]["refused"]), res["bundles"][0]["refused"])

    def test_r6_e5_erase_oracle_counterfeit(self):
        nodes = plan(Spec())
        i = next(k for k, (rec, _a) in enumerate(nodes) if rec["predicate"] == "P-ERASE" and rec["arm"] == "S")
        rec, arts = nodes[i]
        regs = np.frombuffer(arts[2][1], dtype=np.int8).reshape(-1, 3).copy()
        regs[:, 1] = 0                                                       # claims pre_b drew r = 0
        new = _array("oracle:regimes", regs)
        rec = copy.deepcopy(rec)
        rec["oracle"][0] = new[0]
        nodes[i] = (rec, [arts[0], arts[1], new])
        res = self.run_eval(nodes=nodes)
        self.assertTrue(any("ORACLE_MISMATCH" in w for w in res["bundles"][0]["refused"]), res["bundles"][0]["refused"])


if __name__ == "__main__":
    unittest.main()
