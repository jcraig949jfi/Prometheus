"""C-010-T014 W1 challenge on FREEZE_W1: fixtures and hand-wired constructions (Pallas, Q3). DATA FILE: frozen at the
set commit; the drivers (run_cases.py, run_mutation.py) may be repaired afterwards, this file may not.

HARD GATE (TASK.json; PREREGISTRATION s10): nothing here runs a registered subject configuration, a registered arm
on a registered seed, or make_configs. Every seed is >= 5,000,000 (registered witness seeds scan upward from
900,000; P-ERASE / P-PRES seeds lie in [800,000, 900,000)). Organisms: synthetic action arrays with KNOWN
decisions (the evaluator's own test idiom), the test suite's hand-wired leak construction, the POS / RECUR
carriers, one random P = 1 population. Numeric outcomes of registered-arm constructions are never committed.

Bundle layout follows run_witness.py; receipts follow ares_client.receipt_dict. Oracles (r, interrupt steps) are
the real W15 world's, computed exactly as evaluate.world_oracle computes them.
"""
import hashlib
import json
import os
import random
import shutil

import numpy as np

from ares import substrate as S
from rso.binding import binding as B
from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.witness import ares_client as AC
from rso.witness import ruler as RU
from rso.witness.tests.test_ares_client import _leak_construction

T = 40
N = RU.N_EPISODES
DA, DB = "a" * 64, "b" * 64                  # synthetic digests: the "S4" / "S15" ROLES of evaluate.py, not the subjects
LAUNCH_X, LAUNCH_Y = "w1-launch-x", "w1-launch-y"
REG_AT, FIRST_CHECK = "2026-10-07T00:00:00Z", "2026-10-07T01:00:00Z"
SUBJECTS = {"S4": DA, "S15": DB}
WIT_START, WIT_ALT_START = 5000000, 5100000
ERASE_START, ERASE_SAME_START, PRES_START = 6000000, 6100000, 7000000
LEAK_GAIN = 3.5                              # below W_CLIP = 4.0; above the cue amplitude 1.0

_CACHE = {}


# --------------------------------------------------------------------------------------------------------
# Seeds (all >= 5,000,000; the registered generator's shapes, never its ranges)

def witness_like(start=WIT_START):
    """2048 seeds from `start` upward, alternating r = 0 / r = 1 (the registered s3 shape on a non-registered range)."""
    key = ("wit", start)
    if key not in _CACHE:
        _CACHE[key] = AC._scan(start, start + 1000000, [i % 2 for i in range(N)], set())
    return list(_CACHE[key])


def erase_like(start=ERASE_START, same_regime=False, n=AC.ERASE_N_PROBES):
    """[(pre_a, pre_b, probe)]: registered shape pre_a r = 0, pre_b r = 1 (ERASE_PROBES s1); same_regime makes
    pre_b draw r = 0 too (the deviation case B3)."""
    key = ("erase", start, same_regime, n)
    if key not in _CACHE:
        wanted = []
        for i in range(n):
            wanted += [0, 0 if same_regime else 1, i % 2]
        seeds = AC._scan(start, start + 1000000, wanted, set())
        _CACHE[key] = [tuple(seeds[3 * i:3 * i + 3]) for i in range(n)]
    return list(_CACHE[key])


def pres_like(start=PRES_START, n=AC.PRES_N_SEEDS):
    key = ("pres", start, n)
    if key not in _CACHE:
        wanted = []
        for i in range(n):
            wanted += [1 - i % 2, i % 2]
        seeds = AC._scan(start, start + 1000000, wanted, set())
        _CACHE[key] = [tuple(seeds[2 * i:2 * i + 2]) for i in range(n)]
    return list(_CACHE[key])


def flat(groups):
    return [s for g in groups for s in g]


def oracle(seeds, mode="present"):
    """(regimes, interrupt steps) per seed, exactly as evaluate.world_oracle: one world, reset per seed, P = 1."""
    w = AC.world("W15", mode)
    regs, steps = [], []
    for s in seeds:
        w.reset(np.random.default_rng(int(s)), 1)
        regs.append(int(w.r))
        steps.append(sorted(int(x) for x in w.reset_steps))
    return regs, steps


# --------------------------------------------------------------------------------------------------------
# Synthetic traces (E, T, 1) int8 with KNOWN decisions

def after_last(decisions, steps):
    """Every step after the episode's last interrupt answers `decision`; earlier steps abstain (test idiom)."""
    a = np.zeros((len(decisions), T, 1), dtype=np.int8)
    for e, (d, st) in enumerate(zip(decisions, steps)):
        a[e, max(st) + 1:, 0] = d
    return a


def pre_interrupt_only(regs, steps):
    """S2: the CORRECT answer at every step t <= the last interrupt (including the interrupt step, whose action is
    computed before the reset), abstain at every step after it. By RULER.md s1 the episode decision is NO_ANSWER."""
    a = np.zeros((len(regs), T, 1), dtype=np.int8)
    for e, (r, st) in enumerate(zip(regs, steps)):
        a[e, :max(st) + 1, 0] = r + 1
    return a


def mid_window(regs, steps):
    """S3: the CORRECT answer at every step in (first interrupt, last interrupt], abstain after the last. By the
    registered rule (after the LAST interrupt) the decision is NO_ANSWER; a ruler windowed on the FIRST interrupt
    would read it as correct."""
    a = np.zeros((len(regs), T, 1), dtype=np.int8)
    for e, (r, st) in enumerate(zip(regs, steps)):
        a[e, min(st) + 1:max(st) + 1, 0] = r + 1
    return a


def policy(p, seed=0):
    rng = random.Random(seed)

    def f(regs, steps):
        return after_last([r + 1 if rng.random() < p else 2 - r for r in regs], steps)
    return f


def const(d):
    return lambda regs, steps: after_last([d] * len(regs), steps)


def always_correct(regs, steps):
    return after_last([r + 1 for r in regs], steps)


# --------------------------------------------------------------------------------------------------------
# Receipts and bundles (driver layout; producer listings)

def _listing(role, data, dtype, shape):
    return {"role": role, "sha256": hashlib.sha256(data).hexdigest(), "length": len(data), "dtype": dtype,
            "shape": shape}


def array_artifact(role, arr):
    arr = np.ascontiguousarray(arr)
    data = arr.tobytes()
    return _listing(role, data, str(arr.dtype), [int(x) for x in arr.shape]), data


def json_artifact(role, obj):
    data = json.dumps(obj).encode("ascii")
    return _listing(role, data, "json", [len(obj)]), data


def receipt(digest, arm, predicate, seeds, mode, outputs, oracle_, node_id=None, genome_sha256=None):
    return {"schema": AC.SCHEMA, "node_id": node_id or AC.node_id(digest, arm, predicate, "W15"),
            "subject": {"runtime": "ares", "genome_sha256": genome_sha256 or digest, "arm_genome_sha256": digest},
            "arm": arm, "predicate": predicate, "world": {"name": "W15", "mode": mode},
            "seeds": [int(s) for s in seeds], "observer": AC.OBSERVER_ID,
            "outputs": [a for a, _ in outputs], "oracle": [a for a, _ in oracle_],
            "execution": {"status": "COMPLETED"}, "code": []}


def ret_node(digest, arm, predicate, trace_fn, seeds, mode="present", **kw):
    regs, steps = oracle(seeds, mode)
    acts = trace_fn(regs, steps)
    outs = [array_artifact("trace:actions", acts)]
    orc = [array_artifact("oracle:regimes", np.array(regs, dtype=np.int8)), json_artifact("oracle:reset_steps", steps)]
    return receipt(digest, arm, predicate, seeds, mode, outs, orc, **kw), outs + orc


def pair_node(digest, arm, predicate, roles, groups, a, b):
    """P-ERASE (k = 3) or P-PRES (k = 2) node from the two probe-episode arrays a, b of shape (n, T, 1)."""
    k = len(groups[0])
    seeds = flat(groups)
    regs, _ = oracle(seeds)
    outs = [array_artifact(roles[0], a), array_artifact(roles[1], b)]
    orc = [array_artifact("oracle:regimes", np.array(regs, dtype=np.int8).reshape(len(groups), k))]
    return receipt(digest, arm, predicate, seeds, "present", outs, orc), outs + orc


def pair_arrays(n, differs):
    a = np.ones((n, T, 1), dtype=np.int8)
    b = a.copy()
    if differs:
        b[n // 2, T - 1, 0] = 2
    return a, b


def obs_node(digest, seeds, differs=False):
    regs, steps = oracle(seeds)
    a = np.ones((len(seeds), T, 1), dtype=np.int8)
    b = a.copy()
    if differs:
        b[1, 3, 0] = 2
    outs = [array_artifact("trace:actions_record", a), array_artifact("trace:actions_norecord", b)]
    orc = [array_artifact("oracle:regimes", np.array(regs, dtype=np.int8)), json_artifact("oracle:reset_steps", steps)]
    return receipt(digest, "S", "P-OBS", seeds, "present", outs, orc), outs + orc


ERASE_ROLES = ("trace:probe_after_a", "trace:probe_after_b")
PRES_ROLES = ("trace:pres_warm", "trace:pres_fresh")


class Spec(object):
    """Knobs of a synthetic full node set. Defaults: DA POSITIVE (P-CHAN PASS), DB NEGATIVE, every gate PASS,
    the leak member fires."""

    def __init__(self, **kw):
        self.ret = {DA: policy(0.65, 1), DB: const(1)}
        self.nopl = {DA: const(1), DB: const(1)}
        self.null, self.shuf, self.pos = const(1), const(1), policy(0.9, 2)
        self.cal_seeds = None                 # P-CAL arms' seeds (default: the same list as P-RET)
        self.erase_override = {}              # digest -> {"S": (receipt, arts), "S-LEAK": (receipt, arts)}
        self.ret_override = {}                # digest -> (receipt, arts) replacing the S/P-RET node
        for k, v in kw.items():
            setattr(self, k, v)


def full_plan(spec, seeds=None):
    """[(receipt, [(listing, bytes)])] for the registered node map (evaluate.py SUBJECT_NODES + SHARED_NODES)."""
    seeds = seeds or witness_like()
    cal = spec.cal_seeds or seeds
    erase, pres = erase_like(), pres_like()
    nodes = []
    for d in (DA, DB):
        nodes.append(spec.ret_override.get(d) or ret_node(d, "S", "P-RET", spec.ret[d], seeds))
        nodes.append(ret_node(d, "S-NOPL", "P-CHAN", spec.nopl[d], seeds))
        nodes.append(obs_node(d, seeds[:8]))
        a, b = pair_arrays(len(pres), False)
        nodes.append(pair_node(d, "S", "P-PRES", PRES_ROLES, pres, a, b))
        ov = spec.erase_override.get(d, {})
        a, b = pair_arrays(len(erase), False)
        nodes.append(ov.get("S") or pair_node(d, "S", "P-ERASE", ERASE_ROLES, erase, a, b))
        a, b = pair_arrays(len(erase), True)
        nodes.append(ov.get("S-LEAK") or pair_node(d, "S-LEAK", "P-ERASE", ERASE_ROLES, erase, a, b))
    nodes.append(ret_node(DA, "NULL", "P-CAL", spec.null, cal))
    nodes.append(ret_node(DA, "SHUF", "P-CAL", spec.shuf, cal, mode="shuffled"))
    nodes.append(ret_node(DA, "POS", "P-CAL", spec.pos, cal))
    return nodes


def write_bundle(root, nodes, launch=LAUNCH_X, rows_edit=None, extra_files=None):
    """The driver's layout. Returns (manifest bytes, inventory bytes)."""
    os.makedirs(os.path.join(root, "receipts"))
    os.makedirs(os.path.join(root, "artifacts"))
    rows = [{"kind": "RUN", "run_id": launch, "launch_kind": "TOP_LEVEL", "node_id": "WITNESS:w1",
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
        run_id = "%s/%s" % (launch, rec["node_id"])
        rows.append({"kind": "RUN", "run_id": run_id, "parent_run_id": launch, "launch_kind": "RECEIPT",
                     "node_id": rec["node_id"], "status": "COMPLETED", "receipt_sha256": B.receipt_sha256(data),
                     "cpu_us": 1, "artifact_bytes": len(data)})
        man_nodes.append({"node_id": rec["node_id"], "run_id": run_id, "arm": rec["arm"],
                          "predicate": rec["predicate"], "subject_sha256": rec["subject"]["genome_sha256"],
                          "receipt_file": fname, "artifacts": [l for l, _ in arts]})
    if rows_edit:
        rows = rows_edit(rows)
    rows = rows + [{"kind": "TERMINAL", "row_count": len(rows)}]
    inv = R.canonical_bytes({"schema": "rso.witness.inventory.v0", "rows": rows})
    man = R.canonical_bytes({"schema": "rso.witness.manifest.v0", "launch_run_id": launch, "label": "w1",
                             "world": "W15", "code_commit": "0" * 40, "nodes": man_nodes, "subjects": []})
    for name, data in (("inventory.json", inv), ("run.json", R.canonical_bytes({"run_id": launch})),
                       ("MANIFEST.json", man)):
        with open(os.path.join(root, name), "wb") as f:
            f.write(data)
    for rel, data in (extra_files or {}).items():
        p = os.path.join(root, *rel.split("/"))
        d = os.path.dirname(p)
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(p, "wb") as f:
            f.write(data)
    return man, inv


def keeper(*pairs, **kw):
    """FixtureStore registering each (manifest bytes, inventory bytes) pair at REG_AT (or at=...)."""
    at = kw.get("at", REG_AT)
    rows, i = [], 0
    for man, inv in pairs:
        for kind, blob in (("EVIDENCE_MANIFEST", man), ("RUN_INVENTORY", inv)):
            i += 1
            rows.append({"record_kind": kind, "blob_sha256": hashlib.sha256(blob).hexdigest(),
                         "registered_at_utc": at, "repo_path": kind, "row_id": i})
    return EV.FixtureStore(rows)


def sha_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# --------------------------------------------------------------------------------------------------------
# Hand-wired constructions (runtimes); none edits ares/ or the witness modules

class SignLeakRuntime(S.Runtime):
    """B3: an episode reset that restores W1 from the genome PLUS a regime-quantised trace of what the last episode
    wrote: LEAK_GAIN x sign(live W1 - genome W1), per edge. Two preceding episodes of the SAME regime leave an
    identical start state (the probe cannot tell them apart: D = 0); preceding episodes of DIFFERENT regimes leave
    opposite starts (D > 0). A leak, by construction; it passes P-ERASE whenever the probe triples pair same-regime
    pre-episodes."""

    def reset(self):
        drift = np.sign(np.round(self.W1 - self.pop.W1, 3)).astype(np.float32)
        self.v[:] = 0.0
        self.W1[:] = np.clip(self.pop.W1 + LEAK_GAIN * drift, -S.W_CLIP, S.W_CLIP)


class TwoBackLeakRuntime(S.Runtime):
    """B4: the episode reset zeroes activations and starts the new episode from the live W1 the episode BEFORE LAST
    left (a one-slot delay line). Episode k sees episode k-2's W1 and never episode k-1's: every one-step probe
    ([pre, probe]; [warmup, seed] vs [seed]) starts from the genome and reports 0."""

    def __init__(self, pop):
        S.Runtime.__init__(self, pop)
        self._held = None

    def reset(self):
        prev_live = self.W1.copy()
        self.v[:] = 0.0
        self.W1[:] = self.pop.W1 if self._held is None else self._held
        self._held = prev_live


def probe_actions(pop, rt_cls, seq, mode="present"):
    """The LAST episode's actions (T, P) int8 of a fresh runtime of class rt_cls run over the episode sequence."""
    rt = rt_cls(pop)
    return AC.run_episodes(pop, AC.world("W15", mode), seq, runtime=rt)["actions"][-1]


def erase_arrays(pop, rt_cls, triples):
    """(after_a, after_b) of shape (n, T, 1): the probe episode after pre_a and after pre_b, per triple."""
    a = np.stack([probe_actions(pop, rt_cls, [x, p]) for x, _y, p in triples])
    b = np.stack([probe_actions(pop, rt_cls, [y, p]) for _x, y, p in triples])
    return a, b


def diffs(a, b):
    return int(np.count_nonzero(np.asarray(a) != np.asarray(b)))


# --------------------------------------------------------------------------------------------------------
# Case builders. Each returns what run_cases.py needs; none calls the evaluator.

def build_s2(root):
    nodes = full_plan(Spec(ret={DA: pre_interrupt_only, DB: const(1)}))
    man, inv = write_bundle(root, nodes)
    return {"roots": [root], "store": keeper((man, inv))}


def build_s3(root):
    nodes = full_plan(Spec(ret={DA: mid_window, DB: const(1)}))
    man, inv = write_bundle(root, nodes)
    return {"roots": [root], "store": keeper((man, inv))}


def build_b1(root):
    """Two COMPLETED bundles of two launches presenting the SAME node ids with different P-RET traces for DA
    (X: policy 0.65 -> POSITIVE; Y: const 1 -> NEGATIVE), both registered with the keeper."""
    rx, ry = os.path.join(root, "X"), os.path.join(root, "Y")
    mx, ix = write_bundle(rx, full_plan(Spec()), launch=LAUNCH_X)
    my, iy = write_bundle(ry, full_plan(Spec(ret={DA: const(1), DB: const(1)})), launch=LAUNCH_Y)
    return {"X": rx, "Y": ry, "store": keeper((mx, ix), (my, iy))}


def build_b2(root):
    """P-CAL arms (NULL, SHUF, POS) on a DIFFERENT balanced 2048 list than the P-RET / P-CHAN nodes."""
    alt = witness_like(WIT_ALT_START)
    nodes = full_plan(Spec(cal_seeds=alt))
    man, inv = write_bundle(root, nodes)
    return {"roots": [root], "store": keeper((man, inv)), "alt_seeds_sha256": hashlib.sha256(
        json.dumps(alt).encode()).hexdigest()}


def b3_arrays():
    """The two P-ERASE array pairs of B3 from the SignLeak construction over the POS carrier: X's on same-regime
    triples, X-LEAK's on registered-shape triples. Deterministic; a construction property, not an evaluator verdict."""
    key = "b3"
    if key not in _CACHE:
        pop = AC.pos_carrier()
        same, reg = erase_like(ERASE_SAME_START, same_regime=True), erase_like()
        _CACHE[key] = {"same": erase_arrays(pop, SignLeakRuntime, same), "reg": erase_arrays(pop, SignLeakRuntime, reg),
                       "same_triples": same, "reg_triples": reg}
    return _CACHE[key]


def build_b3(root):
    arr = b3_arrays()
    xs = pair_node(DA, "S", "P-ERASE", ERASE_ROLES, arr["same_triples"], *arr["same"])
    xl = pair_node(DA, "S-LEAK", "P-ERASE", ERASE_ROLES, arr["reg_triples"], *arr["reg"])
    nodes = full_plan(Spec(erase_override={DA: {"S": xs, "S-LEAK": xl}}))
    man, inv = write_bundle(root, nodes)
    return {"roots": [root], "store": keeper((man, inv)),
            "premise": {"D_same_regime": diffs(*arr["same"]), "D_registered_shape": diffs(*arr["reg"])}}


def build_b5(root):
    """DA's S/P-RET receipt whose FIELDS disagree with its node id: arm SHUF (traces and oracle in shuffled mode,
    so the oracle check passes under the arm's mode) and subject.genome_sha256 = DB; node_id says DA / S."""
    seeds = witness_like()
    fake = ret_node(DA, "SHUF", "P-RET", policy(0.65, 1), seeds, mode="shuffled",
                    node_id=AC.node_id(DA, "S", "P-RET", "W15"), genome_sha256=DB)
    nodes = full_plan(Spec(ret_override={DA: fake}))
    man, inv = write_bundle(root, nodes)
    return {"roots": [root], "store": keeper((man, inv))}


def build_b6(root):
    """A counterfeit P-RET trace for a REAL bundled genome: subjects/<sha16>.json holds the hand-wired leak
    construction's canonical genome; the S/P-RET node under its true digest carries an always-correct trace the
    organism never produced; every hash, row, manifest and keeper record is consistent."""
    from rso.witness import run_witness as RW
    pop = _leak_construction()
    gbytes = RW.genome_bytes(pop.genome(0))
    digest = hashlib.sha256(gbytes).hexdigest()
    seeds = witness_like()
    spec = Spec()
    spec.ret = {digest: always_correct, DB: const(1)}
    spec.nopl = {digest: const(1), DB: const(1)}
    nodes = []
    erase, pres = erase_like(), pres_like()
    for d in (digest, DB):
        nodes.append(ret_node(d, "S", "P-RET", spec.ret[d], seeds))
        nodes.append(ret_node(d, "S-NOPL", "P-CHAN", spec.nopl[d], seeds))
        nodes.append(obs_node(d, seeds[:8]))
        a, b = pair_arrays(len(pres), False)
        nodes.append(pair_node(d, "S", "P-PRES", PRES_ROLES, pres, a, b))
        a, b = pair_arrays(len(erase), False)
        nodes.append(pair_node(d, "S", "P-ERASE", ERASE_ROLES, erase, a, b))
        a, b = pair_arrays(len(erase), True)
        nodes.append(pair_node(d, "S-LEAK", "P-ERASE", ERASE_ROLES, erase, a, b))
    nodes.append(ret_node(digest, "NULL", "P-CAL", spec.null, seeds))
    nodes.append(ret_node(digest, "SHUF", "P-CAL", spec.shuf, seeds, mode="shuffled"))
    nodes.append(ret_node(digest, "POS", "P-CAL", spec.pos, seeds))
    man, inv = write_bundle(root, nodes, extra_files={"subjects/%s.json" % digest[:16]: gbytes})
    return {"roots": [root], "store": keeper((man, inv)), "subjects": {"S4": digest, "S15": DB},
            "genome_sha256": digest}


def two_back_demo():
    """B4 construction properties (no evaluator): the one-step probes of P-ERASE and P-PRES on the two-back leak,
    the same probes on the production LeakyResetRuntime (control: the probes DO fire on a one-back leak) and on
    S.Runtime (control: 0), and a direct three-episode carry test on the two-back leak and on S.Runtime."""
    pop = _leak_construction()
    erase, pres = erase_like(), pres_like()
    out = {}
    for name, cls in (("TwoBack", TwoBackLeakRuntime), ("LeakyReset", AC.LeakyResetRuntime), ("Runtime", S.Runtime)):
        out[name] = {"p_erase_count": AC.p_erase_count(pop, cls, erase), "p_pres_diffs": AC.p_pres_diffs(pop, cls, pres)}
    mid = witness_like()[0]
    for name, cls in (("TwoBack", TwoBackLeakRuntime), ("Runtime", S.Runtime)):
        carry = sum(diffs(probe_actions(pop, cls, [a, mid, p]), probe_actions(pop, cls, [b, mid, p]))
                    for a, b, p in erase[:16])
        out[name]["three_episode_carry"] = int(carry)
    return out


def null_arm_demo():
    """B8 construction properties: the NULL arm (reset_each_step) applied to the plastic POS carrier. Internal
    state and action EQUALITY only; no accuracy."""
    pop = AC.pos_carrier()
    seeds = witness_like()[:8]
    null_pop, null_mode, null_cls = AC.arm("NULL", pop)
    s_pop, s_mode, s_cls = AC.arm("S", pop)
    rt = null_cls(null_pop)
    AC.run_episodes(null_pop, AC.world("W15", null_mode), seeds[:1], runtime=rt)
    w1_written_under_null = bool(not np.array_equal(rt.W1, null_pop.W1))
    plastic_flag_under_null = bool(rt.plastic)
    null_acts = AC.run_episodes(null_pop, AC.world("W15", null_mode), seeds, runtime_cls=null_cls)["actions"]
    s_acts = AC.run_episodes(s_pop, AC.world("W15", s_mode), seeds, runtime_cls=s_cls)["actions"]
    nopl_pop, nopl_mode, nopl_cls = AC.arm("S-NOPL", pop)
    nopl_acts = AC.run_episodes(nopl_pop, AC.world("W15", nopl_mode), seeds, runtime_cls=nopl_cls)["actions"]
    _regs, steps = oracle(seeds)
    post = [slice(max(st) + 1, T) for st in steps]

    def post_diff(x, y):
        return int(sum(diffs(x[e, sl], y[e, sl]) for e, sl in enumerate(post)))
    return {"reset_each_step_set": bool(null_pop.cfg.reset_each_step), "plastic_flag_under_null": plastic_flag_under_null,
            "w1_written_under_null": w1_written_under_null,
            "null_vs_s_differing_actions_all_steps": diffs(null_acts, s_acts),
            "null_vs_s_differing_actions_after_last_interrupt": post_diff(null_acts, s_acts),
            "nopl_vs_s_differing_actions_after_last_interrupt": post_diff(nopl_acts, s_acts),
            "episodes": len(seeds)}


# --------------------------------------------------------------------------------------------------------
# S1: the real driver on hand-wired / random organisms, full registered node map, non-registered seeds

def driver_configs(root, p_obs_n=256):
    """Writes two canonical genome files (SA: the hand-wired leak construction; SB: a random P = 1 population) and
    the three launch configs make_configs would write, on this set's seeds. Returns (paths, digests)."""
    from rso.witness import run_witness as RW
    subs = {"SA": _leak_construction(), "SB": S.random_population(S.Config(), 1, np.random.default_rng(7))}
    cfgdir = os.path.join(root, "configs")
    os.makedirs(cfgdir)
    files, digests = {}, {}
    for name, pop in subs.items():
        data = RW.genome_bytes(pop.genome(0))
        files[name] = name + ".json"
        digests[name] = hashlib.sha256(data).hexdigest()
        RW._write(os.path.join(cfgdir, files[name]), data)
    wit, erase, pres = witness_like(), flat(erase_like()), flat(pres_like())
    nodes = {"CONTROLS": [{"subject": files["SA"], "arm": a, "predicate": p, "seeds": wit}
                          for a, p in (("POS", "P-CAL"), ("NULL", "P-CAL"), ("SHUF", "P-CAL"), ("RECUR", "REPORT"))]}
    for name in ("SA", "SB"):
        nodes[name] = [{"subject": files[name], "arm": a, "predicate": p, "seeds": sd} for a, p, sd in (
            ("S", "P-RET", wit), ("S-NOPL", "P-CHAN", wit), ("S", "P-OBS", wit[:p_obs_n]), ("S", "P-ERASE", erase),
            ("S-LEAK", "P-ERASE", erase), ("S", "P-PRES", pres))]
    paths = {}
    for label, entries in nodes.items():
        cfg = {"schema": RW.CONFIG_SCHEMA, "label": "W1-" + label, "world": "W15", "entries": entries}
        paths[label] = os.path.join(cfgdir, "config_%s.json" % label)
        RW._write(paths[label], (json.dumps(cfg, sort_keys=True, indent=1) + "\n").encode("ascii"))
    return paths, digests


def tamper_copies(bundle, dest):
    """B7: four tampered COPIES of a driver bundle. Returns {name: (root, store_override or None, note)}; the store
    override re-registers the tampered blob where the tamper is to the manifest / inventory itself."""
    out = {}

    def cp(name):
        d = os.path.join(dest, name)
        shutil.copytree(bundle, d)
        return d

    def rd(p):
        with open(p, "rb") as f:
            return f.read()

    def wr(p, data):
        with open(p, "wb") as f:
            f.write(data)
    # (a) two artifact files' contents swapped (names unchanged)
    d = cp("artifact_swap")
    arts = sorted(os.listdir(os.path.join(d, "artifacts")))
    pa, pb = [os.path.join(d, "artifacts", x) for x in arts[:2]]
    da, db = rd(pa), rd(pb)
    wr(pa, db)
    wr(pb, da)
    out["artifact_swap"] = (d, None, "artifacts %s and %s contents swapped" % (arts[0][:12], arts[1][:12]))
    # (b) manifest entry 0 points at node 1's receipt file; the tampered manifest IS re-registered
    d = cp("receipt_file_swap")
    man = json.loads(rd(os.path.join(d, "MANIFEST.json")))
    man["nodes"][0]["receipt_file"] = man["nodes"][1]["receipt_file"]
    mb = R.canonical_bytes(man)
    wr(os.path.join(d, "MANIFEST.json"), mb)
    ib = rd(os.path.join(d, "inventory.json"))
    out["receipt_file_swap"] = (d, keeper((mb, ib)),
                                "MANIFEST nodes[0].receipt_file := nodes[1].receipt_file; manifest re-registered")
    # (c) inventory row digest of the first node edited; the ORIGINAL inventory stays registered
    d = cp("inventory_digest_edit")
    inv = json.loads(rd(os.path.join(d, "inventory.json")))
    row = next(r for r in inv["rows"] if r.get("launch_kind") == "RECEIPT")
    row["receipt_sha256"] = ("0" if row["receipt_sha256"][0] != "0" else "1") + row["receipt_sha256"][1:]
    ib2 = R.canonical_bytes(inv)
    wr(os.path.join(d, "inventory.json"), ib2)
    out["inventory_digest_edit"] = (d, None,
                                    "inventory row receipt_sha256 of the first node edited; original inventory registered")
    # (c2) the same edit, tampered inventory re-registered
    d2 = cp("inventory_digest_edit_reregistered")
    wr(os.path.join(d2, "inventory.json"), ib2)
    mb2 = rd(os.path.join(d2, "MANIFEST.json"))
    out["inventory_digest_edit_reregistered"] = (d2, keeper((mb2, ib2)), "as (c), tampered inventory re-registered")
    return out


def redact(res):
    """Structure only: refusals, binding, custody, which gates were evaluated, that a class exists. Every numeric
    outcome field and every class value of a driver-produced bundle is dropped (TASK.json non-goals; dry_run
    practice)."""
    out = {"schema": res.get("schema"), "world": res.get("world"), "primary": res.get("primary"),
           "bundles": [{k: b.get(k) for k in ("bundle", "launch_run_id", "p_flat", "custody", "refused")}
                       for b in res.get("bundles", [])],
           "P-CAL": {"evaluated": res["P-CAL"]["value"] != "BLOCKED",
                     "blocked_reason": res["P-CAL"]["reason"] if res["P-CAL"]["value"] == "BLOCKED" else None},
           "subjects": {}}
    for name, sub in res.get("subjects", {}).items():
        out["subjects"][name] = {"gates_evaluated": sorted(k for k in sub if k.startswith("P-")),
                                 "has_class": "class" in sub, "class_is_unqualified": sub.get("class") == "UNQUALIFIED",
                                 "why_if_unqualified": sub.get("why") if sub.get("class") == "UNQUALIFIED" else None}
    return out
