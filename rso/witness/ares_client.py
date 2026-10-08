"""Ares witness adapter: a client of rso.binding (C-009-T013). PLUMBING ONLY.

Selection: rso/witness/SELECTION.md (Ares, world W15; W4 reference). Design: rso/witness/DESIGN_DRAFT.md.
Gate (SELECTION.md): no subject evolution, no witness predicate on Ares output, and no accuracy or retention number
for any arm or control until the witness preregistration is frozen. Accordingly the episode runner returns actions
and the world-side oracle only -- never rewards or fitness -- and the predicate functions below are COUNT functions
with no thresholds (the ruler, its statistic and its band are Argus's, C-009-T014).

What this module provides:
  - the seven arms of DESIGN_DRAFT s4 as wrappers, none of which edits ares/:
      S       the subject, correct resets
      S-NOPL  the subject with every plasticity rate zeroed (allowed-channel ablation)
      S-LEAK  the subject under LeakyResetRuntime: an episode reset that zeroes activations but does NOT restore the
              live plastic W1 from the genome (the delayed-leak construction across native boundary B2)
      POS     a hand-wired plastic carrier (positive control for the ruler)
      RECUR   a hand-wired activation self-loop carrier (channel control: an activation carrier meets W15's interrupts)
      NULL    the subject with plasticity disabled as in S-NOPL AND reset_each_step (AMENDMENT_v1.0.1)
      SHUF    the subject in W15 "shuffled" mode (cue decoupled from the regime: calibration world)
  - run_episodes: ares.search.rollout's episode loop reproduced step for step (a test pins equal actions), with an
    optional observer called after every step and an injectable runtime so state can persist across episodes;
  - canonical, float-free receipts per (arm, predicate) node and one node-execution row each, bound by rso.binding
    (BX2/BX3). Node ids are opaque strings built and parsed only here (BX6).
Python >= 3.8; numpy.
"""
import hashlib
import json
import os

import numpy as np

from ares import search as AR
from ares import substrate as S
from rso.binding import binding as B
from rso.slice001 import adapter as SA
from rso.slice001 import receipt as R

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCHEMA = "rso.witness.ares_receipt.v0"
WORLD = "W15"
REFERENCE_WORLD = "W4"
ARMS = ("S", "S-NOPL", "S-LEAK", "POS", "RECUR", "NULL", "SHUF")
CODE_PATHS = ("ares/substrate.py", "ares/worlds.py", "ares/search.py", "rso/witness/ares_client.py")
OBSERVER_ID = "rso.witness.ares_client.run_episodes"


# --------------------------------------------------------------------------------------------------------
# Arms

class LeakyResetRuntime(S.Runtime):
    """S-LEAK: the episode reset zeroes activations but leaves the live plastic W1 as the last episode left it."""

    def reset(self):
        self.v[:] = 0.0


def _with_cfg(pop, **changes):
    q = pop.copy()
    d = pop.cfg.to_dict()
    d.update(changes)
    q.cfg = S.Config(**d)
    return q


def pos_carrier(cfg=None):
    """Hand-wired plastic carrier: hidden node h reads the cue (obs ch1) and has a plastic edge from the constant
    channel (obs ch5), so during the cue W1[h, 5] moves with the cue's sign and re-drives h after an interrupt.
    Outputs read h with opposite signs (the wiring of ares/tests/test_carriers.py)."""
    cfg = cfg or S.Config()
    pop = S.Population(cfg, 1)
    n, h = cfg.n, S.OBS_DIM
    pop.alive[0, h] = True
    pop.op[0, h] = S.OPS.index("ADD")
    pop.W1[0, h, 1] = 1.0
    pop.R[0, h, 5] = 0.5                       # the plastic edge (constant channel -> h)
    pop.op[0, n - 2] = S.OPS.index("ADD"); pop.W1[0, n - 2, h] = -1.0
    pop.op[0, n - 1] = S.OPS.index("ADD"); pop.W1[0, n - 1, h] = 1.0
    return pop


def recur_carrier(cfg=None):
    """Hand-wired activation self-loop carrier (as ares/tests/test_carriers.py recur_carrier)."""
    cfg = cfg or S.Config()
    pop = S.Population(cfg, 1)
    n, h = cfg.n, S.OBS_DIM
    pop.alive[0, h] = True
    pop.op[0, h] = S.OPS.index("TANH")
    pop.W1[0, h, 1] = 3.0
    pop.W1[0, h, h] = 3.0                      # the activation carrier edge
    pop.op[0, n - 2] = S.OPS.index("ADD"); pop.W1[0, n - 2, h] = -1.0
    pop.op[0, n - 1] = S.OPS.index("ADD"); pop.W1[0, n - 1, h] = 1.0
    return pop


def arm(name, subject):
    """(population, world mode, runtime class) for one arm. The subject population is never modified."""
    if name == "S":
        return subject, "present", S.Runtime
    if name == "S-NOPL":
        q = subject.copy()
        q.R[:] = 0.0
        return q, "present", S.Runtime
    if name == "S-LEAK":
        return subject, "present", LeakyResetRuntime
    if name == "POS":
        return pos_carrier(subject.cfg), "present", S.Runtime
    if name == "RECUR":
        return recur_carrier(subject.cfg), "present", S.Runtime
    if name == "NULL":
        # AMENDMENT_v1.0.1 (W1 B8): plasticity disabled exactly as S-NOPL, on a copy, AND reset_each_step --
        # no carry by construction (activations zeroed every step, no plastic write)
        q = _with_cfg(subject, reset_each_step=True)
        q.R[:] = 0.0
        return q, "present", S.Runtime
    if name == "SHUF":
        return subject, "shuffled", S.Runtime
    raise ValueError("unknown arm %r; registered: %s" % (name, ", ".join(ARMS)))


# --------------------------------------------------------------------------------------------------------
# Episode runner (observer) -- actions and oracle only

def world(name=WORLD, mode="present"):
    return AR.make_world(name, mode)


def run_episodes(pop, w, seeds, runtime=None, runtime_cls=S.Runtime, observer=None):
    """ares.search.rollout's loop, step for step, returning actions (E, T, P) int8, the world's regime r and shown
    cue per episode, and its interrupt steps. No reward, fitness or accuracy is returned. `runtime` lets state
    persist across calls (S-LEAK across B2); observer(t, runtime) runs after every step and must not write."""
    rt = runtime if runtime is not None else runtime_cls(pop)
    P = pop.P
    noise_sd = float(getattr(w, "state_noise_sd", 0.0))
    acts, regs, shown, rsteps = [], [], [], []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        nrng = np.random.default_rng(sd ^ 0x5EED)
        rt.reset()
        obs = w.reset(rng, P)
        resets = set(getattr(w, "reset_steps", ()))
        a_ep = np.zeros((w.T, P), dtype=np.int8)
        for t in range(w.T):
            a = rt.step(obs)
            obs, _reward_discarded, _alive, _info = w.step(a)
            if noise_sd > 0:
                rt.v[:, S.OBS_DIM:] += nrng.normal(0, noise_sd, size=(P, rt.v.shape[1] - S.OBS_DIM)).astype(np.float32)
            if t in resets:
                rt.v[:, S.OBS_DIM:] = 0.0
            a_ep[t] = a
            if observer is not None:
                observer(t, rt)
        acts.append(a_ep)
        regs.append(int(getattr(w, "r", -1)))
        shown.append(int(getattr(w, "shown", -1)))
        rsteps.append(sorted(int(x) for x in resets))
    return {"actions": np.stack(acts), "regimes": np.array(regs, dtype=np.int8),
            "shown": np.array(shown, dtype=np.int8), "reset_steps": rsteps}


# --------------------------------------------------------------------------------------------------------
# Receipts and binding rows

def genome_digest(pop, p=0):
    """sha256 of the organism's genome in a fixed JSON form (floats as Python repr; the digest, not the floats,
    enters the receipt)."""
    g = json.dumps(pop.genome(p), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(g.encode("utf-8")).hexdigest()


def _artifact(role, data):
    return {"role": role, "sha256": hashlib.sha256(data).hexdigest(), "length": len(data)}


def node_id(subject_digest, arm_name, predicate, world_name):
    return "ares:%s:%s:%s:%s" % (subject_digest[:16], arm_name, predicate, world_name)


def _array_artifact(role, arr):
    """(listing, bytes) for a numpy array; dtype and shape recorded so the evaluator can decode the bytes."""
    arr = np.ascontiguousarray(arr)
    data = arr.tobytes()
    a = _artifact(role, data)
    a["dtype"] = str(arr.dtype)
    a["shape"] = [int(x) for x in arr.shape]
    return a, data


def _json_artifact(role, obj):
    data = json.dumps(obj).encode("ascii")
    a = _artifact(role, data)
    a["dtype"] = "json"
    a["shape"] = [len(obj)]
    return a, data


def _groups(seeds, k, predicate):
    seeds = [int(s) for s in seeds]
    if not seeds or len(seeds) % k:
        raise ValueError("%s expects a flat list of %d-tuples of seeds, got %d seed(s)" % (predicate, k, len(seeds)))
    return [tuple(seeds[i:i + k]) for i in range(0, len(seeds), k)]


def _recording_observer(store):
    def observe(t, rt):
        store.append((t, rt.v.copy(), rt.W1.copy()))
    return observe


def node_execution(launch, arm_name, predicate, subject, seeds):
    """Run one node by its predicate's pattern (PREREGISTRATION s4, s5, s7). Returns (arm population, mode, outputs,
    oracle), outputs and oracle as [(listing, bytes)]. Patterns:
      P-OBS    the episode run twice on fresh runtimes, with a recording observer and without one
      P-ERASE  seeds = flat (pre_a, pre_b, probe) triples; [pre_a, probe] and [pre_b, probe] on fresh runtimes;
               the probe episode's actions per triple (ERASE_PROBES.md s1)
      P-PRES   seeds = flat (warmup, seed) pairs; [warmup, seed] on one runtime vs [seed] on a fresh instance
      other    (P-RET, P-CAL, P-CHAN, and any reported arm) one episode run over the seeds
    No count, accuracy or decision is computed here: the evaluator recomputes from the bytes."""
    pop, mode, rt_cls = arm(arm_name, subject)
    wn = launch.world_name
    if predicate == "P-OBS":
        recorded = []
        rec_run = run_episodes(pop, world(wn, mode), seeds, runtime_cls=rt_cls, observer=_recording_observer(recorded))
        plain = run_episodes(pop, world(wn, mode), seeds, runtime_cls=rt_cls)
        outputs = [_array_artifact("trace:actions_record", rec_run["actions"]),
                   _array_artifact("trace:actions_norecord", plain["actions"])]
        oracle = [_array_artifact("oracle:regimes", plain["regimes"]),
                  _json_artifact("oracle:reset_steps", plain["reset_steps"])]
    elif predicate == "P-ERASE":
        triples = _groups(seeds, 3, predicate)
        after_a = np.stack([_probe_actions(pop, rt_cls, [a, p], mode, wn) for a, b, p in triples])
        after_b = np.stack([_probe_actions(pop, rt_cls, [b, p], mode, wn) for a, b, p in triples])
        regs = np.array([[regime_of(s, wn, mode) for s in t] for t in triples], dtype=np.int8)
        outputs = [_array_artifact("trace:probe_after_a", after_a), _array_artifact("trace:probe_after_b", after_b)]
        oracle = [_array_artifact("oracle:regimes", regs)]
    elif predicate == "P-PRES":
        pairs = _groups(seeds, 2, predicate)
        warm = np.stack([_probe_actions(pop, rt_cls, [w, s], mode, wn) for w, s in pairs])
        fresh = np.stack([_probe_actions(pop, rt_cls, [s], mode, wn) for w, s in pairs])
        regs = np.array([[regime_of(x, wn, mode) for x in pr] for pr in pairs], dtype=np.int8)
        outputs = [_array_artifact("trace:pres_warm", warm), _array_artifact("trace:pres_fresh", fresh)]
        oracle = [_array_artifact("oracle:regimes", regs)]
    else:
        out = run_episodes(pop, world(wn, mode), seeds, runtime_cls=rt_cls)
        outputs = [_array_artifact("trace:actions", out["actions"])]
        oracle = [_array_artifact("oracle:regimes", out["regimes"]),
                  _json_artifact("oracle:reset_steps", out["reset_steps"])]
    return pop, mode, outputs, oracle


def receipt_dict(launch, arm_name, predicate, subject, seeds):
    """(receipt dict, {sha256: bytes}) for one node: the driver's preferred producer seam (run_witness
    node_artifacts). Every byte string the evaluator reads is named in outputs / oracle with role, sha256, length,
    dtype and shape (PREREGISTRATION s7)."""
    pop, mode, outputs, oracle = node_execution(launch, arm_name, predicate, subject, seeds)
    sd = genome_digest(subject)
    rec = {
        "schema": SCHEMA,
        "node_id": node_id(sd, arm_name, predicate, launch.world_name),
        "subject": {"runtime": "ares", "genome_sha256": sd, "arm_genome_sha256": genome_digest(pop)},
        "arm": arm_name,
        "predicate": predicate,
        "world": {"name": launch.world_name, "mode": mode},
        "seeds": [int(s) for s in seeds],
        "observer": OBSERVER_ID,
        "outputs": [a for a, _ in outputs],
        "oracle": [a for a, _ in oracle],
        "execution": {"status": B.COMPLETED},
        "code": [SA.file_code_ref(p, launch.code_commit, launch.root) for p in CODE_PATHS],
    }
    arts = {}
    for a, data in outputs + oracle:
        arts[a["sha256"]] = data
    return rec, arts


def receipt_bytes(rec):
    """Canonical, float-free bytes (receipt.canonical_bytes refuses floats)."""
    return R.canonical_bytes(rec)


class Launch:
    """One top-level launch: its node executions and the inventory rows that bind them (BX1, BX2)."""

    def __init__(self, launch_run_id, code_commit, world_name=WORLD, root=REPO_ROOT):
        self.launch_run_id = launch_run_id
        self.code_commit = code_commit
        self.world_name = world_name
        self.root = root
        self._rows = []

    def produce(self, arm_name, predicate, subject, seeds):
        """Run one node, build its receipt, record its row. Returns (node_id, run_id, receipt canonical bytes)."""
        rec, _arts = receipt_dict(self, arm_name, predicate, subject, seeds)
        data = receipt_bytes(rec)
        run_id = "%s/%s" % (self.launch_run_id, rec["node_id"])
        self._rows.append({"kind": B.RUN, "run_id": run_id, "parent_run_id": self.launch_run_id,
                           "launch_kind": B.RECEIPT, "node_id": rec["node_id"], "status": B.COMPLETED,
                           "receipt_sha256": B.receipt_sha256(data)})
        return rec["node_id"], run_id, data

    def rows(self):
        top = {"kind": B.RUN, "run_id": self.launch_run_id, "launch_kind": B.TOP_LEVEL, "node_id": "G0",
               "status": B.COMPLETED}
        return [top] + list(self._rows) + [{"kind": "TERMINAL", "row_count": 1 + len(self._rows)}]


# --------------------------------------------------------------------------------------------------------
# Predicate COUNT functions (no thresholds; unit-tested on synthetic arrays only before preregistration)

def post_interrupt_counts(actions, regimes, reset_steps, good=lambda r: r + 1):
    """Per organism: (correct, total) over the steps after each episode's last interrupt; correct = the action the
    regime rewards (W4/W15: action r + 1)."""
    E, T, P = actions.shape
    correct = np.zeros(P, dtype=np.int64)
    total = np.zeros(P, dtype=np.int64)
    for e in range(E):
        start = (max(reset_steps[e]) + 1) if reset_steps[e] else 0
        seg = actions[e, start:T, :]
        correct += (seg == good(int(regimes[e]))).sum(axis=0)
        total += seg.shape[0]
    return correct, total


def paired_carryover_diffs(actions_after_a, actions_after_b):
    """P-ERASE across B2 (deterministic, paired): the same probe episode run after two different preceding
    episodes; the number of (step, organism) positions whose actions differ. 0 means no carry-over observed."""
    return int(np.count_nonzero(np.asarray(actions_after_a) != np.asarray(actions_after_b)))


def actions_equal(a, b):
    """P-OBS plumbing: identical action traces with and without the observer."""
    return bool(np.array_equal(np.asarray(a), np.asarray(b)))


# --------------------------------------------------------------------------------------------------------
# C-009-T018: P-ERASE probe set and P-PRES seed set (rso/witness/ERASE_PROBES.md). Deterministic seed scans below
# the witness seed floor (PREREG_DRAFT s3: witness seeds >= 900000) and above balanced_seeds_for's scan range.

ERASE_START = 800_000
ERASE_N_PROBES = 64            # 32 probes with r = 0, 32 with r = 1
PRES_START = 850_000
PRES_N_SEEDS = 32              # 16 with r = 0, 16 with r = 1, each with its own warm-up episode
WITNESS_SEED_FLOOR = 900_000


def regime_of(seed, name=WORLD, mode="present"):
    """The world-side regime r an episode seed draws (oracle only; no organism is run)."""
    w = world(name, mode)
    w.reset(np.random.default_rng(seed), 1)
    return int(w.r)


def _scan(start, stop, wanted, exclude):
    """Seeds from `start` upward, skipping `exclude`, taken in order as each requested regime slot opens.
    `wanted` is a list of regimes; returns one seed per entry, in that order."""
    out, s, pending = [], start, list(wanted)
    by_r = {0: [], 1: []}
    while pending:
        if s >= stop:
            raise ValueError("seed range exhausted before the set was complete")
        if s not in exclude:
            by_r[regime_of(s)].append(s)
            while pending and by_r[pending[0]]:
                out.append(by_r[pending.pop(0)].pop(0))
        s += 1
    return out


def erase_probe_set(n=ERASE_N_PROBES, start=ERASE_START, exclude=()):
    """[(pre_a, pre_b, probe)]: pre_a draws r = 0, pre_b draws r = 1, probe alternates r = 0 / r = 1. Each seed is
    used once. P-ERASE runs [pre_a, probe] and [pre_b, probe] on fresh runtimes and compares the probe episode."""
    wanted = []
    for i in range(n):
        wanted += [0, 1, i % 2]
    seeds = _scan(start, PRES_START, wanted, set(exclude))
    return [tuple(seeds[3 * i:3 * i + 3]) for i in range(n)]


def pres_seed_set(n=PRES_N_SEEDS, start=PRES_START, exclude=()):
    """[(warmup, seed)]: P-PRES runs [warmup, seed] on one runtime and [seed] on a fresh instance of the same genome;
    the seed episode's actions must be identical. Seeds alternate r = 0 / r = 1; warm-ups take the opposite r."""
    wanted = []
    for i in range(n):
        wanted += [1 - i % 2, i % 2]
    seeds = _scan(start, WITNESS_SEED_FLOOR, wanted, set(exclude))
    return [tuple(seeds[2 * i:2 * i + 2]) for i in range(n)]


def _probe_actions(pop, rt_cls, seq, mode="present", world_name=WORLD):
    rt = rt_cls(pop)
    return run_episodes(pop, world(world_name, mode), seq, runtime=rt)["actions"][-1]


def p_erase_count(pop, rt_cls, probes, mode="present"):
    """Total differing (step, organism) actions in the probe episode between its two preceding conditions, summed
    over the probe set. A count, not a decision; ERASE_PROBES.md registers the gate on it."""
    return sum(paired_carryover_diffs(_probe_actions(pop, rt_cls, [a, p], mode), _probe_actions(pop, rt_cls, [b, p], mode))
               for a, b, p in probes)


def p_pres_diffs(pop, rt_cls, pairs, mode="present"):
    """Total differing actions on each seed episode between 'after a warm-up and a reset' and 'fresh instance'."""
    return sum(paired_carryover_diffs(_probe_actions(pop, rt_cls, [w, s], mode), _probe_actions(pop, rt_cls, [s], mode))
               for w, s in pairs)
