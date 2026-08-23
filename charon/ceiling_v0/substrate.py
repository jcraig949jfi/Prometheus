"""The evolving cognitive substrate: machine-readable artifacts + a deterministic
predictor built from them.

RESTORED 2026-08-22 after the working-tree loss (see RECOVERY.md).

Nothing in here understands the universe. Rules are accepted or destroyed by the
environment (`test_rule`), never by a model's opinion.

Soundness note: memo entries are keyed by the canonical form produced by the rule
set active when they were written, so each records the ids of the rules that
produced its key. If a rule is later demoted by re-testing, every memo entry that
depended on it is purged. Without this the store silently accumulates facts that
were only true under a claim now known false.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Sequence, Set, Tuple

from universe import Interaction, Session

MAX_NOTE_CHARS = 800
MAX_OPS = 24


@dataclass
class Rule:
    rid: str
    lhs: List[str]
    rhs: List[str]
    kind: str                 # 'reduce' | 'order'
    proposer: str             # 'llm' | 'random' | 'injected' | 'c4' | 'synthetic'
    round_proposed: int
    passes: int = 0
    fails: int = 0
    status: str = "active"    # 'active' | 'rejected'
    uses: int = 0
    source_ops: List[str] = field(default_factory=list)
    surprise_linked: bool = False

    def key(self) -> str:
        return " ".join(self.lhs) + " => " + " ".join(self.rhs)


@dataclass
class Op:
    oid: str
    expansion: List[str]
    round_defined: int
    uses: int = 0


class ArtifactStore:
    """Everything P2 is allowed to carry across an amnesia boundary."""

    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.ops: Dict[str, Op] = {}
        self.memo: Dict[str, Dict] = {}   # key -> {"sym","rules","src"}
        self.note: str = ""
        self.sym_counts: Dict[str, int] = {}
        self.counters: Dict[str, int] = {
            "proposed": 0, "accepted": 0, "rejected": 0,
            "retests": 0, "demoted": 0, "surprises": 0,
            "memo_purged": 0, "ops_defined": 0,
            # a system that is never wrong because it never commits is not the
            # same as one that is never wrong because it is right
            "probes_seen": 0, "probes_ignorant": 0,
            "probes_committed": 0, "probes_wrong": 0,
        }
        self._next_rule = 0
        self._next_op = 0

    # ---------------------------------------------------------------- ops
    def define_op(self, expansion: Sequence[str], rnd: int) -> Optional[str]:
        if len(self.ops) >= MAX_OPS:
            return None
        try:
            prims = self.expand(list(expansion))
        except ValueError:
            return None
        if not prims or len(prims) > 12:
            return None
        for oid, op in self.ops.items():
            try:
                if self.expand(op.expansion) == prims:
                    return oid
            except ValueError:
                continue
        self._next_op += 1
        oid = f"OP_{self._next_op:03d}"
        self.ops[oid] = Op(oid, list(expansion), rnd)
        self.counters["ops_defined"] += 1
        return oid

    def expand(self, seq: Sequence[str], _depth: int = 0) -> List[str]:
        """Resolve OP references to primitives. Provenance is total: every
        derived operator reconstructs from primitives or it is invalid."""
        if _depth > 8:
            raise ValueError("op expansion too deep")
        out: List[str] = []
        for tok in seq:
            tok = tok.strip()
            if not tok:
                continue
            if tok.startswith("OP_"):
                if tok not in self.ops:
                    raise ValueError(f"unknown op {tok}")
                out.extend(self.expand(self.ops[tok].expansion, _depth + 1))
            elif tok.startswith("A") and tok[1:].isdigit():
                out.append(tok)
            else:
                raise ValueError(f"bad token {tok!r}")
        return out

    # ---------------------------------------------------------------- rules
    def active_rules(self) -> List[Rule]:
        return [r for r in self.rules.values() if r.status == "active"]

    def add_rule(self, lhs: List[str], rhs: List[str], kind: str,
                 proposer: str, rnd: int,
                 source_ops: Optional[List[str]] = None) -> Rule:
        self._next_rule += 1
        r = Rule(f"R_{self._next_rule:04d}", list(lhs), list(rhs), kind,
                 proposer, rnd, source_ops=list(source_ops or []))
        self.rules[r.rid] = r
        return r

    def has_rule(self, lhs: Sequence[str], rhs: Sequence[str]) -> bool:
        k = " ".join(lhs) + " => " + " ".join(rhs)
        return any(r.key() == k for r in self.rules.values())

    def demote(self, rid: str) -> None:
        r = self.rules.get(rid)
        if r is None or r.status != "active":
            return
        r.status = "rejected"
        self.counters["demoted"] += 1
        self.purge_memo_for_rules({rid})

    def purge_memo_for_rules(self, rids: Set[str]) -> int:
        dead = [k for k, v in self.memo.items() if set(v["rules"]) & rids]
        for k in dead:
            del self.memo[k]
        self.counters["memo_purged"] += len(dead)
        return len(dead)

    # ---------------------------------------------------------------- memo
    @staticmethod
    def memo_key(tag: str, word: Sequence[str]) -> str:
        return f"{tag}|{' '.join(word)}"

    def remember(self, tag: str, canonical: Sequence[str], symbol: str,
                 rule_ids: Sequence[str], src: str = "probe") -> None:
        """`src` records WHAT CAUSED this observation to be paid for, so the
        analysis can separate gain from the model being RIGHT from gain from the
        probe a wrong guess happened to trigger."""
        self.memo[self.memo_key(tag, canonical)] = {
            "sym": symbol, "rules": sorted(set(rule_ids)), "src": src
        }

    # ---------------------------------------------------------------- io
    def majority(self) -> str:
        """Most frequent readout this store has observed. Derived only from own
        probes -- never from the evaluator."""
        if not self.sym_counts:
            return "q0"
        return max(sorted(self.sym_counts), key=lambda s: self.sym_counts[s])

    def to_json(self) -> str:
        return json.dumps({
            "rules": [asdict(r) for r in self.rules.values()],
            "ops": [asdict(o) for o in self.ops.values()],
            "memo": self.memo,
            "note": self.note,
            "sym_counts": self.sym_counts,
            "counters": self.counters,
            "_next_rule": self._next_rule,
            "_next_op": self._next_op,
        }, sort_keys=True)

    @classmethod
    def from_json(cls, blob: str) -> "ArtifactStore":
        d = json.loads(blob)
        s = cls()
        for rd in d["rules"]:
            s.rules[rd["rid"]] = Rule(**rd)
        for od in d["ops"]:
            s.ops[od["oid"]] = Op(**od)
        s.memo = {k: dict(v) for k, v in d["memo"].items()}
        s.note = d["note"]
        s.sym_counts = dict(d.get("sym_counts", {}))
        s.counters = dict(d["counters"])
        s._next_rule = d["_next_rule"]
        s._next_op = d["_next_op"]
        return s

    def clone(self) -> "ArtifactStore":
        return ArtifactStore.from_json(self.to_json())

    def size_bytes(self) -> int:
        return len(self.to_json().encode())


# ---------------------------------------------------------------------------
#  Normalisation — pure deterministic code, no model involved
# ---------------------------------------------------------------------------


def classify(lhs: Sequence[str], rhs: Sequence[str]) -> Optional[str]:
    """Admissible only if it strictly decreases (length, lex). That alone
    guarantees the rewriting terminates."""
    if len(lhs) == 0:
        return None
    if len(lhs) > len(rhs):
        return "reduce"
    if len(lhs) == len(rhs) and list(rhs) < list(lhs):
        return "order"
    return None


def normalize(word: Sequence[str], rules: Sequence[Rule],
              max_steps: int = 600, tally: bool = False
              ) -> Tuple[List[str], List[str]]:
    """Greedy (length, lex)-decreasing rewriting to a fixpoint.
    Returns (canonical_word, ids_of_rules_that_fired)."""
    cur = list(word)
    active = [r for r in rules if r.status == "active"]
    banks = ([r for r in active if r.kind == "reduce"],
             [r for r in active if r.kind == "order"])
    fired: List[str] = []
    for _ in range(max_steps):
        hit = None
        for bank in banks:
            for r in bank:
                n = len(r.lhs)
                if n == 0 or n > len(cur):
                    continue
                for i in range(len(cur) - n + 1):
                    if cur[i:i + n] == r.lhs:
                        hit = (r, i, n)
                        break
                if hit:
                    break
            if hit:
                break
        if not hit:
            break
        r, i, n = hit
        cur = cur[:i] + list(r.rhs) + cur[i + n:]
        fired.append(r.rid)
        if tally:
            r.uses += 1
    return cur, fired


class SubstratePredictor:
    """Deterministic, non-LLM readout of the artifact store."""

    def __init__(self, store: ArtifactStore, fallback: Optional[str] = None):
        self.store = store
        self.fallback = fallback or store.majority()

    def predict(self, tag: str, word: Sequence[str], tally: bool = False
                ) -> Tuple[str, bool]:
        canon, _ = normalize(word, list(self.store.rules.values()), tally=tally)
        entry = self.store.memo.get(ArtifactStore.memo_key(tag, canon))
        if entry is not None:
            return entry["sym"], True
        return self.fallback, False

    def predict_all(self, queries, tally: bool = False) -> Tuple[List[str], float]:
        preds, hits = [], 0
        for q in queries:
            p, hit = self.predict(q.tag, q.word, tally=tally)
            preds.append(p)
            hits += int(hit)
        return preds, hits / max(1, len(queries))


# ---------------------------------------------------------------------------
#  Harvest / surprise
# ---------------------------------------------------------------------------


def harvest(store: ArtifactStore, inter: Interaction,
            src: str = "probe") -> int:
    """Every prefix of an executed sequence is an observed fact. Memoise each
    under its current canonical form. Costs no interactions -- the data was
    already paid for."""
    rules = list(store.rules.values())
    added = 0
    for sym in inter.readout:
        store.sym_counts[sym] = store.sym_counts.get(sym, 0) + 1
    for i in range(len(inter.word) + 1):
        canon, fired = normalize(inter.word[:i], rules)
        store.remember(inter.tag, canon, inter.readout[i], fired, src)
        added += 1
    return added


def detect_surprise(store: ArtifactStore, tag: str, word: Sequence[str],
                    observed_final: str) -> bool:
    """Records IGNORANCE (no prediction available) separately from ERROR
    (prediction available and wrong). Measured S is 0.00 everywhere, which reads
    as "never wrong" until you notice the store almost never commits: every rule
    passed environmental testing and every memo entry is a directly observed
    fact, so it is only ever ignorant. A purely conservative epistemic policy
    cannot generate the error signal the metabolisation story depends on."""
    pred = SubstratePredictor(store)
    sym, hit = pred.predict(tag, word)
    store.counters["probes_seen"] += 1
    if not hit:
        store.counters["probes_ignorant"] += 1
        return False
    store.counters["probes_committed"] += 1
    if sym != observed_final:
        store.counters["probes_wrong"] += 1
        store.counters["surprises"] += 1
        return True
    return False


# ---------------------------------------------------------------------------
#  The stupid verifier — the environment decides, nothing else
# ---------------------------------------------------------------------------


def test_rule(session: Session, lhs: Sequence[str], rhs: Sequence[str],
              rng: random.Random, n_contexts: int = 3
              ) -> Tuple[Optional[bool], int]:
    """Myhill-Nerode style equivalence probe: compare `tag . lhs . suffix`
    against `tag . rhs . suffix` over several contexts. The verifier has no idea
    what the claim means. Costs 2 interactions per context, charged to the same
    budget every arm spends."""
    uni = session.universe
    maxlen = uni.spec.max_word_len
    if not (1 <= len(lhs) <= maxlen) or len(rhs) > maxlen:
        return None, 0
    spent = 0
    checked = 0
    for _ in range(n_contexts):
        room = maxlen - max(len(lhs), len(rhs))
        if room < 0:
            return None, spent
        lo = 1 if len(rhs) == 0 else 0     # an empty rhs must still be runnable
        if room < lo:
            return None, spent
        suffix = [rng.choice(uni.actions)
                  for _ in range(rng.randint(lo, min(2, room)))]
        tag = rng.choice(uni.tags)
        if session.remaining < 2:
            break
        ok_l, a = session.try_run(tag, list(lhs) + suffix, source="ruletest")
        ok_r, b = session.try_run(tag, list(rhs) + suffix, source="ruletest")
        spent += 2
        if not ok_l or not ok_r:
            break
        checked += 1
        if a[-1] != b[-1]:
            return False, spent
    if checked == 0:
        return None, spent
    return True, spent


def submit_rule(store: ArtifactStore, session: Session, lhs: Sequence[str],
                rhs: Sequence[str], proposer: str, rnd: int, rng: random.Random,
                source_ops: Optional[List[str]] = None,
                surprise_linked: bool = False, n_contexts: int = 3):
    """Propose -> environment tests -> store keeps or destroys."""
    kind = classify(lhs, rhs)
    if kind is None or store.has_rule(lhs, rhs):
        return None, None, 0
    verdict, spent = test_rule(session, lhs, rhs, rng, n_contexts)
    if verdict is None:
        return None, None, spent
    store.counters["proposed"] += 1
    r = store.add_rule(lhs, rhs, kind, proposer, rnd, source_ops)
    r.surprise_linked = surprise_linked
    if verdict:
        r.passes += 1
        store.counters["accepted"] += 1
    else:
        r.fails += 1
        r.status = "rejected"
        store.counters["rejected"] += 1
    return r, verdict, spent


def retest_active_rules(store: ArtifactStore, session: Session,
                        rng: random.Random, max_rules: int = 4,
                        n_contexts: int = 2) -> int:
    """Environmental selection over time. A rule that fails now is demoted and
    its memo dependents purged. This is what removes injected wrong artifacts."""
    cands = sorted(store.active_rules(), key=lambda r: (r.passes, r.rid))
    spent = 0
    for r in cands[:max_rules]:
        if session.remaining < 4:
            break
        verdict, s = test_rule(session, r.lhs, r.rhs, rng, n_contexts)
        spent += s
        store.counters["retests"] += 1
        if verdict is True:
            r.passes += 1
        elif verdict is False:
            r.fails += 1
            store.demote(r.rid)
    return spent
