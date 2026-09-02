"""LATTICE TRANSDUCER (LT) benchmark family for D16-C.

State space GF(2)^8. A WORLD hides three independent parameters, each reached
through its own query channel:

  A  a_star : the unique nonzero linear functional preserved by the FREE ops
              g_1, g_3 (affine, hidden).      channel: TRANSITION(j in {1,3}, x)
  B  (P2,c2): the hidden PORTAL op g_2 = P2 x ^ c2 (does NOT preserve a_star).
                                              channel: TRANSITION(2, x)
  C  m_star : hidden admissibility mask; repair r (public effect e_r) is
              admissible iff m_star . e_r = 0. channel: ADMISSIBLE(r)

Every task answer is an exact function of the hidden parameters. Submission
is ONE-SHOT: a researcher answers only when its version space determines the
answer uniquely (else ABSTAIN). There is no plan-test oracle. The adjudicator
is exact enumeration. No sampling anywhere in truth.

Everything here is deterministic given seeds. Nothing here talks to the
engine; engine recording is a wrapper (see ecology.py).
"""
from __future__ import annotations
import hashlib, json, random
from dataclasses import dataclass, field
from typing import Optional

N = 8
MASK = (1 << N) - 1
FREE_OPS = (1, 3)
PORTAL = 2
N_REPAIRS = 64


def parity(v: int) -> int:
    return bin(v).count("1") & 1


def dot(a: int, b: int) -> int:
    return parity(a & b)


def mat_apply(rows: list[int], x: int) -> int:
    """rows[i] = i-th row of an 8x8 GF(2) matrix as a bitmask; y_i = row_i . x."""
    y = 0
    for i, r in enumerate(rows):
        if parity(r & x):
            y |= 1 << i
    return y


def mat_T(rows: list[int]) -> list[int]:
    cols = []
    for i in range(N):
        c = 0
        for k in range(N):
            if (rows[k] >> i) & 1:
                c |= 1 << k
        cols.append(c)
    return cols


def rank_gf2(vecs: list[int]) -> int:
    basis = []
    for v in vecs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def invertible(rows: list[int]) -> bool:
    return rank_gf2(rows) == N


def rand_invertible(rng: random.Random) -> list[int]:
    while True:
        rows = [rng.randrange(1, 1 << N) for _ in range(N)]
        if invertible(rows):
            return rows


def rand_invertible_fixing(rng: random.Random, a: int) -> list[int]:
    """Invertible P with P^T a = a, i.e. a . (P x) = a . x for all x.
    P^T a = XOR of rows k with a_k = 1 == a."""
    while True:
        rows = rand_invertible(rng)
        acc = 0
        for k in range(N):
            if (a >> k) & 1:
                acc ^= rows[k]
        if acc == a:
            return rows


@dataclass
class World:
    world_seed: int
    a_star: int
    P1: list[int]; c1: int
    P2: list[int]; c2: int
    P3: list[int]; c3: int
    m_star: int
    effects: list[int]            # public repair effects e_r, r = 0..63
    abc_x0: list[int]             # instance parameters for ABC tasks

    # ---- hidden dynamics (oracle side) ----------------------------------
    def op(self, j: int) -> tuple[list[int], int]:
        return {1: (self.P1, self.c1), 2: (self.P2, self.c2),
                3: (self.P3, self.c3)}[j]

    def transition(self, j: int, x: int) -> int:
        P, c = self.op(j)
        return mat_apply(P, x) ^ c

    def admissible(self, r: int) -> bool:
        return dot(self.m_star, self.effects[r]) == 0

    @property
    def R_adm(self) -> list[int]:
        return [r for r in range(N_REPAIRS) if self.admissible(r)]

    # ---- ground-truth answers ------------------------------------------
    def answers(self) -> dict:
        return answers_from_params(self.a_star, self.P2, self.c2, self.m_star,
                                   self.effects, self.abc_x0)

    def public(self) -> dict:
        return {"effects": self.effects, "abc_x0": self.abc_x0, "N": N}

    def fingerprint(self) -> str:
        blob = json.dumps({"a": self.a_star, "P1": self.P1, "c1": self.c1,
                           "P2": self.P2, "c2": self.c2, "P3": self.P3,
                           "c3": self.c3, "m": self.m_star,
                           "eff": self.effects, "x0": self.abc_x0}, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()


def answers_from_params(a: int, P2: list[int], c2: int, m: int,
                        effects: list[int], abc_x0: list[int]) -> dict:
    R_adm = [r for r in range(N_REPAIRS) if dot(m, effects[r]) == 0]
    P2T = mat_T(P2)
    u = mat_apply(P2T, a) ^ a          # x crosses under g_2 iff u.x ^ b == 1
    b = dot(a, c2)
    ans = {
        "A": a,
        "B": [list(P2), c2],
        "C": R_adm,
        "AB": [u, b],
        "AC": [r for r in R_adm if dot(a, effects[r]) == 1],
        "BC": [r for r in R_adm if mat_apply(P2, effects[r]) == effects[r]],
    }
    for k, x0 in enumerate(abc_x0):
        sols = []
        cx0 = dot(a, x0)
        g = mat_apply(P2, x0) ^ c2
        for r in R_adm:
            e = effects[r]
            if dot(a, g ^ e) != cx0:
                sols.append([r, "after"])
            if dot(a, mat_apply(P2, x0 ^ e) ^ c2) != cx0:
                sols.append([r, "before"])
        ans[f"ABC{k}"] = sols
    return ans


# BC ("admissible repairs commuting with g_2") was KILLED by the Phase 0 census:
# answer is [] in 88.5% of worlds (universal strategy) and B alone determines
# it 80% of the time. It stays computable for the record but is no task.
TASK_TYPES = ["A", "B", "C", "AB", "AC", "ABC0", "ABC1", "ABC2"]
INTERACTIVE = ["AB", "AC", "ABC0", "ABC1", "ABC2"]
KILLED_TASKS = ["BC"]
COMPONENTS_OF = {"A": {"A"}, "B": {"B"}, "C": {"C"}, "AB": {"A", "B"},
                 "AC": {"A", "C"}, "BC": {"B", "C"},
                 "ABC0": {"A", "B", "C"}, "ABC1": {"A", "B", "C"},
                 "ABC2": {"A", "B", "C"}}


def canon(v) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"))


def generate_world(world_seed: int) -> World:
    """Deterministic generator. Rejection-samples until the qualification
    predicates in census() hold structurally (uniqueness of a_star is verified
    by enumeration here, again in the census)."""
    rng = random.Random(("LT-world", world_seed).__repr__())
    while True:
        a = rng.randrange(1, 1 << N)
        m = rng.randrange(1, 1 << N)
        if m == a:
            continue
        P1 = rand_invertible_fixing(rng, a)
        P3 = rand_invertible_fixing(rng, a)
        while True:
            c1 = rng.randrange(0, 1 << N)
            if dot(a, c1) == 0:
                break
        while True:
            c3 = rng.randrange(0, 1 << N)
            if dot(a, c3) == 0:
                break
        P2 = rand_invertible(rng)
        c2 = rng.randrange(0, 1 << N)
        # portal must NOT preserve a_star (else order/crossing structure is vacuous)
        P2T = mat_T(P2)
        if mat_apply(P2T, a) == a and dot(a, c2) == 0:
            continue
        effects = rng.sample(range(1, 1 << N), N_REPAIRS)
        x0s = rng.sample(range(0, 1 << N), 3)
        w = World(world_seed, a, P1, c1, P2, c2, P3, c3, m, effects, x0s)
        if len(common_invariants(w)) != 1:
            continue
        return w


def common_invariants(w: World) -> list[int]:
    """All nonzero a with a.g_j(x) == a.x for all x and both free ops (exact)."""
    out = []
    for a in range(1, 1 << N):
        ok = True
        for j in FREE_OPS:
            for x in range(1 << N):
                if dot(a, w.transition(j, x)) != dot(a, x):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            out.append(a)
    return out


# ---------------------------------------------------------------------------
# Knowledge state: what a researcher (or synthesizer) has, and what it can
# derive. Purely a function of OBSERVATIONS (raw) plus optional adopted
# CLAIMS. Determinacy is exact (enumeration for A and C; linear span for B).
# ---------------------------------------------------------------------------

@dataclass
class Knowledge:
    effects: list[int]
    abc_x0: list[int]
    obs_free: list[tuple[int, int, int]] = field(default_factory=list)   # (j,x,y)
    obs_portal: list[tuple[int, int]] = field(default_factory=list)      # (x,y)
    obs_adm: list[tuple[int, bool]] = field(default_factory=list)        # (r,adm)
    family_A: Optional[set] = None    # representation restriction (None = all)
    adopted: dict = field(default_factory=dict)   # claims adopted blind

    # -- A ---------------------------------------------------------------
    def vs_A(self) -> list[int]:
        if "A" in self.adopted:
            return [self.adopted["A"]]
        cands = range(1, 1 << N) if self.family_A is None else sorted(self.family_A)
        out = []
        for a in cands:
            if all(dot(a, x ^ y) == 0 for (_, x, y) in self.obs_free):
                out.append(a)
        return out

    # -- C ---------------------------------------------------------------
    def vs_C(self) -> list[int]:
        if "C" in self.adopted:
            return [self.adopted["C"]]
        out = []
        for m in range(1, 1 << N):
            if all((dot(m, self.effects[r]) == 0) == adm for (r, adm) in self.obs_adm):
                out.append(m)
        return out

    # -- B: affine span over GF(2)^9 ------------------------------------
    def _portal_basis(self):
        """Reduced basis of the queried extended inputs (x,1) with attached
        outputs, so that any v in span yields the determined g_2-combination."""
        basis = []  # list of (vec9, out8)
        for (x, y) in self.obs_portal:
            v, o = x | (1 << N), y
            for (bv, bo) in basis:
                if v ^ bv < v:
                    v ^= bv; o ^= bo
            if v:
                basis.append((v, o))
                basis.sort(key=lambda t: -t[0])
        return basis

    def portal_value(self, v9: int) -> Optional[int]:
        """Determined value of W . v9 where W is the unknown extended [P2|c2]
        (v9 = (x,1) gives g_2(x); v9 = (x,0) gives P2 x). None if undetermined."""
        if "B" in self.adopted:
            P2, c2 = self.adopted["B"]
            x = v9 & MASK
            return mat_apply(P2, x) ^ (c2 if (v9 >> N) & 1 else 0)
        basis = self._portal_basis()
        o = 0
        v = v9
        for (bv, bo) in basis:
            if v ^ bv < v:
                v ^= bv; o ^= bo
        return o if v == 0 else None

    def portal_rank(self) -> int:
        if "B" in self.adopted:
            return N + 1
        return len(self._portal_basis())

    def portal_full(self) -> Optional[tuple[list[int], int]]:
        if self.portal_rank() < N + 1:
            return None
        c2 = self.portal_value(1 << N)
        cols = [self.portal_value(1 << i) for i in range(N)]  # P2 e_i
        rows = [0] * N
        for i, col in enumerate(cols):
            for k in range(N):
                if (col >> k) & 1:
                    rows[k] |= 1 << i
        return rows, c2

    # -- answers ---------------------------------------------------------
    def answer(self, task: str):
        """Exact answer if determined by the knowledge state, else None."""
        E, x0s = self.effects, self.abc_x0
        if task == "A":
            vs = self.vs_A(); return vs[0] if len(vs) == 1 else None
        if task == "C":
            vs = self.vs_C()
            if len(vs) != 1: return None
            m = vs[0]; return [r for r in range(N_REPAIRS) if dot(m, E[r]) == 0]
        if task == "B":
            f = self.portal_full(); return [f[0], f[1]] if f else None
        if task == "AB":
            vsA = self.vs_A()
            if not vsA or len(vsA) > 64: return None
            outs = set()
            for a in vsA:
                # u.x ^ b = a.(g2(x) ^ x); W-combination: sum of rows k in a
                # (u,b) = sum_{k in a} extended row k, determined iff rank == 9
                f = self.portal_full()
                if f is None: return None
                P2, c2 = f
                u = mat_apply(mat_T(P2), a) ^ a; b = dot(a, c2)
                outs.add(canon([u, b]))
            return json.loads(outs.pop()) if len(outs) == 1 else None
        if task == "AC":
            vsA, vsC = self.vs_A(), self.vs_C()
            if not vsA or not vsC or len(vsA) * len(vsC) > 4096: return None
            outs = set()
            for a in vsA:
                for m in vsC:
                    outs.add(canon([r for r in range(N_REPAIRS)
                                    if dot(m, E[r]) == 0 and dot(a, E[r]) == 1]))
                    if len(outs) > 1: return None
            return json.loads(outs.pop())
        if task == "BC":
            vsC = self.vs_C()
            if not vsC or len(vsC) > 256: return None
            outs = set()
            for m in vsC:
                res = []
                for r in range(N_REPAIRS):
                    if dot(m, E[r]) != 0: continue
                    pv = self.portal_value(E[r])       # P2 e_r (last coord 0)
                    if pv is None: return None
                    if pv == E[r]: res.append(r)
                outs.add(canon(res))
                if len(outs) > 1: return None
            return json.loads(outs.pop())
        if task.startswith("ABC"):
            k = int(task[3:]); x0 = x0s[k]
            vsA, vsC = self.vs_A(), self.vs_C()
            if not vsA or not vsC or len(vsA) * len(vsC) > 4096: return None
            g = self.portal_value(x0 | (1 << N))
            if g is None: return None
            outs = set()
            for a in vsA:
                cx0 = dot(a, x0)
                for m in vsC:
                    sols = []
                    for r in range(N_REPAIRS):
                        if dot(m, E[r]) != 0: continue
                        e = E[r]
                        if dot(a, g ^ e) != cx0: sols.append([r, "after"])
                        gb = self.portal_value((x0 ^ e) | (1 << N))
                        if gb is None: return None
                        if dot(a, gb) != cx0: sols.append([r, "before"])
                    outs.add(canon(sols))
                    if len(outs) > 1: return None
            return json.loads(outs.pop())
        raise ValueError(task)

    def determined(self) -> dict:
        return {t: (self.answer(t) is not None) for t in TASK_TYPES}

    def merge_obs(self, other: "Knowledge") -> None:
        self.obs_free = sorted(set(self.obs_free) | set(other.obs_free))
        self.obs_portal = sorted(set(self.obs_portal) | set(other.obs_portal))
        self.obs_adm = sorted(set(self.obs_adm) | set(other.obs_adm))


def adjudicate(world: World, task: str, submitted) -> str:
    """Exact adjudication. ABSTAIN / CORRECT / WRONG."""
    if submitted is None:
        return "ABSTAIN"
    truth = world.answers()[task]
    return "CORRECT" if canon(submitted) == canon(truth) else "WRONG"


# ---------------------------------------------------------------------------
# Deterministic researcher policy (version-space driven; diversity settings)
# ---------------------------------------------------------------------------

@dataclass
class Settings:
    seed: int = 0
    order: tuple = ("A", "B", "C")        # initial hypothesis order
    basis: Optional[list[int]] = None     # representation: family = wt(M a) <= 3
    heuristic: str = "random"             # random | maxsplit | basis
    diet: tuple = ("T1", "T2", "T3", "ADM")   # allowed query channels
    dsl_order: int = 0                    # enumeration order of repairs

    def key(self) -> str:
        return canon({"seed": self.seed, "order": list(self.order),
                      "basis": self.basis, "heur": self.heuristic,
                      "diet": list(self.diet), "dsl": self.dsl_order})


def sparse_family(basis: list[int], maxwt: int = 3) -> set:
    fam = set()
    for a in range(1, 1 << N):
        if bin(mat_apply(basis, a)).count("1") <= maxwt:
            fam.add(a)
    return fam


class Researcher:
    """One research lineage. `oracle(query) -> result` answers TRANSITION /
    ADMISSIBLE; `recorder` receives every epistemic act (hypothesis,
    prediction, experiment, observation, failure) so an engine wrapper can
    ledger it. Deterministic in (settings, world public data, oracle)."""

    def __init__(self, world_public: dict, settings: Settings, oracle, recorder,
                 budget: int):
        self.pub = world_public
        self.s = settings
        self.rng = random.Random(("LT-researcher", settings.key()).__repr__())
        self.oracle = oracle
        self.rec = recorder
        self.budget = budget
        self.spent = 0
        self.K = Knowledge(world_public["effects"], world_public["abc_x0"])
        if settings.basis is not None:
            self.K.family_A = sparse_family(settings.basis)
        self.failed = set()       # components abandoned (family exhausted)
        self.log = []             # (query, result, hypothesis, outcome)
        self.repair_order = list(range(N_REPAIRS))
        random.Random(("dsl", settings.dsl_order).__repr__()).shuffle(self.repair_order)

    # -- component status --------------------------------------------------
    def done(self, comp: str) -> bool:
        if comp == "A": return len(self.K.vs_A()) == 1
        if comp == "B": return self.K.portal_rank() == N + 1
        if comp == "C": return len(self.K.vs_C()) == 1
        raise ValueError(comp)

    def allowed(self, comp: str) -> bool:
        d = self.s.diet
        if comp == "A": return "T1" in d or "T3" in d
        if comp == "B": return "T2" in d
        if comp == "C": return "ADM" in d
        return False

    def next_component(self) -> Optional[str]:
        for c in self.s.order:
            if c in self.failed or not self.allowed(c): continue
            if not self.done(c): return c
        return None

    # -- query selection ---------------------------------------------------
    def pick_query(self, comp: str):
        if comp == "A":
            ops = [j for j in FREE_OPS if f"T{j}" in self.s.diet]
            j = ops[self.spent % len(ops)]
            if self.s.heuristic == "maxsplit":
                # choose x whose constraint direction is unknown: cannot be
                # predicted without P_j; fall back to random (documented)
                x = self.rng.randrange(0, 1 << N)
            else:
                x = self.rng.randrange(0, 1 << N)
            return ("TRANSITION", j, x)
        if comp == "B":
            if self.s.heuristic == "basis":
                queried = {x for (x, _) in self.K.obs_portal}
                for x in [0] + [1 << i for i in range(N)]:
                    if x not in queried: return ("TRANSITION", PORTAL, x)
            # random x not in span (guaranteed progress)
            for _ in range(64):
                x = self.rng.randrange(0, 1 << N)
                if self.K.portal_value(x | (1 << N)) is None:
                    return ("TRANSITION", PORTAL, x)
            return ("TRANSITION", PORTAL, self.rng.randrange(0, 1 << N))
        if comp == "C":
            vs = self.K.vs_C()
            E = self.pub["effects"]
            asked = {r for (r, _) in self.K.obs_adm}
            if self.s.heuristic == "maxsplit":
                best, bestgap = None, 10 ** 9
                for r in self.repair_order:
                    if r in asked: continue
                    k = sum(1 for m in vs if dot(m, E[r]) == 0)
                    gap = abs(2 * k - len(vs))
                    if gap < bestgap: best, bestgap = r, gap
                return ("ADMISSIBLE", best)
            for r in self.repair_order:
                if r not in asked:
                    # skip questions whose answer is already determined
                    ks = {dot(m, E[r]) for m in vs}
                    if len(ks) == 1: continue
                    return ("ADMISSIBLE", r)
            return ("ADMISSIBLE", self.repair_order[0])
        raise ValueError(comp)

    def leading_hypothesis(self, comp: str):
        if comp == "A":
            vs = self.K.vs_A(); return ("A", vs[0]) if vs else None
        if comp == "C":
            vs = self.K.vs_C(); return ("C", vs[0]) if vs else None
        if comp == "B":
            return ("B", "portal_affine_rank%d" % self.K.portal_rank())
        return None

    # -- main loop ---------------------------------------------------------
    def step(self) -> bool:
        comp = self.next_component()
        if comp is None or self.spent >= self.budget:
            return False
        hyp = self.leading_hypothesis(comp)
        if hyp is None:
            # family exhausted: a first-class failure, component abandoned
            self.failed.add(comp)
            self.rec("failure", {"component": comp, "type": "FAMILY_EXHAUSTED",
                                 "family": "sparse_wt3" if self.K.family_A else "all",
                                 "n_obs": len(self.K.obs_free)})
            return True
        q = self.pick_query(comp)
        # prospective prediction of the leading hypothesis
        if q[0] == "TRANSITION" and comp == "A":
            pred = {"kind": "invariant", "a": hyp[1], "j": q[1], "x": q[2],
                    "claim": "a.g_j(x) == a.x"}
        elif q[0] == "ADMISSIBLE":
            pred = {"kind": "admissible", "m": hyp[1], "r": q[1],
                    "claim": "adm(r) == (m.e_r == 0)",
                    "value": dot(hyp[1], self.pub["effects"][q[1]]) == 0}
        else:
            pred = {"kind": "portal", "rank": self.K.portal_rank(), "x": q[2],
                    "claim": "g2(x) not yet determined"}
        hid = self.rec("hypothesis", {"component": comp, "statement": canon(hyp)})
        pid = self.rec("prediction", {"hyp": hid, "content": pred})
        eid = self.rec("experiment", {"hyp": hid, "pred": pid, "spec": list(q)})
        res = self.oracle(q)
        self.spent += 1
        # evaluate prediction exactly
        if q[0] == "TRANSITION" and comp == "A":
            ok = dot(hyp[1], q[2] ^ res) == 0
            outcome = "SURVIVED" if ok else "FALSIFIED"
        elif q[0] == "ADMISSIBLE":
            outcome = "SURVIVED" if pred["value"] == res else "FALSIFIED"
        else:
            outcome = "INCONCLUSIVE"   # portal queries are measurements, not tests
        # record observation
        if q[0] == "TRANSITION":
            if q[1] == PORTAL: self.K.obs_portal.append((q[2], res))
            else: self.K.obs_free.append((q[1], q[2], res))
        else:
            self.K.obs_adm.append((q[1], res))
        self.rec("observation", {"exp": eid, "pred": pid, "outcome": outcome,
                                 "content": {"query": list(q), "result": res}})
        if outcome == "FALSIFIED":
            self.rec("failure", {"component": comp, "type": "HYPOTHESIS_FALSIFIED",
                                 "hypothesis": canon(hyp), "query": list(q),
                                 "result": res})
        self.log.append((q, res, hyp, outcome))
        return True

    def run(self) -> None:
        while self.step():
            pass

    # -- artifacts -----------------------------------------------------------
    def structured_artifacts(self) -> list[dict]:
        """Success claims for determined components; failure artifacts for
        abandoned components. Evidence = hashes of the supporting observations."""
        arts = []
        def ev(obs): return [hashlib.sha256(canon(o).encode()).hexdigest()[:16] for o in obs]
        if self.done("A"):
            arts.append({"info_kind": "success", "claim": "A", "a": self.K.vs_A()[0],
                         "evidence": ev(self.K.obs_free)})
        if self.done("B"):
            P2, c2 = self.K.portal_full()
            arts.append({"info_kind": "success", "claim": "B", "P2": P2, "c2": c2,
                         "evidence": ev(self.K.obs_portal)})
        if self.done("C"):
            arts.append({"info_kind": "success", "claim": "C", "m": self.K.vs_C()[0],
                         "evidence": ev(self.K.obs_adm)})
        for comp in sorted(self.failed):
            arts.append({"info_kind": "failure", "claim": comp,
                         "type": "FAMILY_EXHAUSTED",
                         "basis": self.s.basis, "evidence": ev(self.K.obs_free)})
        # hypothesis-level failures (falsified leading candidates)
        for (q, res, hyp, outcome) in self.log:
            if outcome == "FALSIFIED":
                arts.append({"info_kind": "failure", "type": "HYPOTHESIS_FALSIFIED",
                             "hypothesis": hyp, "query": list(q), "result": res})
        return arts

    def raw_artifact(self) -> dict:
        return {"info_kind": "observation",
                "obs_free": [list(o) for o in self.K.obs_free],
                "obs_portal": [list(o) for o in self.K.obs_portal],
                "obs_adm": [[r, bool(a)] for (r, a) in self.K.obs_adm]}


# ---------------------------------------------------------------------------
# Synthesizer: builds a Knowledge from artifacts under a recipient policy,
# optionally spends B_syn queries, answers tasks (abstain unless determined).
# ---------------------------------------------------------------------------

def knowledge_from_artifacts(pub: dict, artifacts: list[dict], policy: str,
                             oracle=None, verify_budget: int = 0, verify_k: int = 3) -> tuple[Knowledge, dict]:
    """policy: RAW (use observation artifacts only), BLIND (adopt success
    claims), VERIFY_K (adopt a claim only after k re-tests, power 1-2^-k; alias VERIFY_ONE),
    FALSIFIER_FIRST (a claim contradicted by any failure artifact's recorded
    observation is rejected; otherwise adopt)."""
    K = Knowledge(pub["effects"], pub["abc_x0"])
    used = {"adopted": [], "rejected": [], "verify_spent": 0, "obs_merged": 0}
    # observations from RAW artifacts always merge (they are facts about the world)
    for a in artifacts:
        if a.get("info_kind") == "observation":
            K.obs_free += [tuple(o) for o in a.get("obs_free", [])]
            K.obs_portal += [tuple(o) for o in a.get("obs_portal", [])]
            K.obs_adm += [(o[0], bool(o[1])) for o in a.get("obs_adm", [])]
            used["obs_merged"] += 1
    K.obs_free = sorted(set(K.obs_free)); K.obs_portal = sorted(set(K.obs_portal))
    K.obs_adm = sorted(set(K.obs_adm))
    if policy == "RAW":
        return K, used
    # failure artifacts carry observations too (query,result) -- also facts
    fal_obs = []
    for a in artifacts:
        if a.get("info_kind") == "failure" and a.get("type") == "HYPOTHESIS_FALSIFIED":
            fal_obs.append((a["query"], a["result"]))
    claims = [a for a in artifacts if a.get("info_kind") == "success"]
    # resolve claims per component; conflicts -> majority unless policy says otherwise
    for comp in ("A", "B", "C"):
        cs = [c for c in claims if c["claim"] == comp]
        if not cs: continue
        vals = {}
        for c in cs:
            v = c["a"] if comp == "A" else ([c["P2"], c["c2"]] if comp == "B" else c["m"])
            vals.setdefault(canon(v), []).append(c)
        cand = sorted(vals.items(), key=lambda kv: -len(kv[1]))
        chosen = None
        for key, cl in cand:
            v = json.loads(key)
            if policy == "FALSIFIER_FIRST":
                # reject if any recorded observation (from failures or raw) contradicts
                if _contradicted(comp, v, K, fal_obs, pub):
                    used["rejected"].append({"comp": comp, "value": v, "why": "falsifier"})
                    continue
            if policy in ("VERIFY_ONE", "VERIFY_K") and oracle is not None and used["verify_spent"] < verify_budget:
                # VERIFY_K: up to verify_k queries per candidate (power 1-2^-k); a
                # contradiction already on record rejects for free.
                # executing lens: a contradicting FAILURE record is re-run before
                # it is trusted; a record whose result does not replay is dropped
                # (fal_obs are client-asserted, forgeable).  Own/raw observations
                # are trusted as merged facts.
                bad = [fo for fo in fal_obs if _contradicted(comp, v, K, [fo], pub) and not _contradicted(comp, v, K, [], pub)]
                for (q, res) in bad:
                    if used["verify_spent"] >= verify_budget: break
                    real = oracle(tuple(q)); used["verify_spent"] += 1
                    if real != res:
                        fal_obs = [fo for fo in fal_obs if fo != (q, res)]
                        used["rejected"].append({"comp": comp, "value": v, "why": "forged_falsifier_dropped"})
                if _contradicted(comp, v, K, fal_obs, pub):
                    used["rejected"].append({"comp": comp, "value": v, "why": "already_contradicted"})
                    continue
                failed = False
                for q, expect in _decisive_tests(comp, v, pub, verify_k):
                    if used["verify_spent"] >= verify_budget: break
                    res = oracle(q); used["verify_spent"] += 1
                    if q[0] == "TRANSITION":
                        if q[1] == PORTAL: K.obs_portal.append((q[2], res))
                        else: K.obs_free.append((q[1], q[2], res))
                    else:
                        K.obs_adm.append((q[1], res))
                    if not expect(res):
                        failed = True; break
                if failed:
                    used["rejected"].append({"comp": comp, "value": v, "why": "verify_failed"})
                    continue
            chosen = v
            break
        if chosen is not None:
            K.adopted[comp] = chosen if comp != "B" else (chosen[0], chosen[1])
            used["adopted"].append({"comp": comp, "value": chosen, "n_sources": len(vals[canon(chosen)])})
    return K, used


def _contradicted(comp, v, K: Knowledge, fal_obs, pub) -> bool:
    E = pub["effects"]
    if comp == "A":
        for (j, x, y) in K.obs_free:
            if dot(v, x ^ y) != 0: return True
        for (q, res) in fal_obs:
            if q[0] == "TRANSITION" and q[1] in FREE_OPS and dot(v, q[2] ^ res) != 0: return True
    if comp == "C":
        for (r, adm) in K.obs_adm:
            if (dot(v, E[r]) == 0) != adm: return True
        for (q, res) in fal_obs:
            if q[0] == "ADMISSIBLE" and (dot(v, E[q[1]]) == 0) != res: return True
    if comp == "B":
        P2, c2 = v
        for (x, y) in K.obs_portal:
            if mat_apply(P2, x) ^ c2 != y: return True
        for (q, res) in fal_obs:
            if q[0] == "TRANSITION" and q[1] == PORTAL and mat_apply(P2, q[2]) ^ c2 != res: return True
    return False


def _decisive_tests(comp, v, pub, k: int):
    """k queries whose joint pass-probability for a WRONG candidate is <= 2^-k
    (A, C: a random x against a value that is not an invariant of the queried
    op passes with p=1/2; ops alternate so no wrong a survives by being an
    invariant of one free op -- only a* is invariant under both. B: a single
    random x rejects a wrong (P2,c2) with p >= 1-2^-8).  Phase 0 SD-002: the
    v1 single random query was NOT decisive (power 1/2)."""
    rng = random.Random(("verify", comp, canon(v)).__repr__())
    E = pub["effects"]; tests = []
    for i in range(k):
        if comp == "A":
            x = rng.randrange(0, 1 << N); j = FREE_OPS[i % 2]
            tests.append((("TRANSITION", j, x), (lambda y, v=v, x=x: dot(v, x ^ y) == 0)))
        elif comp == "C":
            r = rng.randrange(N_REPAIRS)
            tests.append((("ADMISSIBLE", r), (lambda adm, v=v, r=r: adm == (dot(v, E[r]) == 0))))
        else:
            P2, c2 = v; x = rng.randrange(0, 1 << N)
            tests.append((("TRANSITION", PORTAL, x), (lambda y, P2=P2, c2=c2, x=x: mat_apply(P2, x) ^ c2 == y)))
    return tests
