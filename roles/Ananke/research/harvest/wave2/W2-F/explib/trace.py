"""(2) Causal difference tracing with a closure invariant (engine-agnostic).

Generalises H-INST pte_trace.diff_trace (harvest/H-INST) from PTE to any engine whose cross-node influence
has an enumerable channel. Two lockstep runs A and B share every exogenous random draw (common random
numbers, forced by construction in explib.lockstep) and differ by an input schedule and/or an intervention.
The engine (or the lockstep runner) reports, per tick t, unit u and node n:

  post[t,u,n]        node state differs after the engine step of tick t (before interventions)
  held[t,u,n]        node state differs at the END of tick t (after interventions of tick t)
  inp[t,u,n]         the exogenous input to node n at tick t differs (a LEAF)
  arr[t,u,n]         the content delivered to node n at the start of tick t differs (optional)
  edges[E,5]         difference-bearing transport edges (u, src, te, dst, ta), te < ta (optional)
  hook_node[t,u,n]   an intervention after tick t changed node n's state (a LEAF)
  hook_flight[t,u,n] an intervention changed content that arrives at node n at tick t (a LEAF)
  comp_post / comp_held  {component: [T,U,N] bool} (optional, for write authority)

THE CLOSURE INVARIANT (the engine's locality claim and the tracer's correctness in one check)
  C1 node closure     a node can only START to differ through a differing input or a differing arrival
                      (post & ~held[t-1] & ~inp & ~arr == 0), and can only change between post and held
                      through an intervention (held & ~post & ~hook_node == 0).
  C2 arrival closure  a delivery can only differ through a recorded edge or an intervention
                      (arr & ~edge_target & ~hook_flight == 0).
  C3 edge sources     every edge's source was itself active at its emission tick.
Each check is PASS / FAIL / NOT_VERIFIED (NOT_VERIFIED when the needed channel is not reported, unless the
record declares `local_only=True`, i.e. the engine has no transport at all).

SEMANTICS (must not be stretched): these are DIFFERENCE paths. Outside the cone means the quantity cannot
carry the A/B contrast (sound, given closure PASS). Inside the cone does NOT mean used (difference is not
use: W-S P3, W-T, W-Y Kp[0]); a carrier claim needs a paired intervention (explib.reach / explib.authority).
"""
from __future__ import annotations

import dataclasses
from typing import Optional

import numpy as np

from .outcomes import FAIL, NOT_VERIFIED, PASS, Check, worst

LOCAL, TRANSPORTED, BOTH, NO_DIFF = "LOCAL", "TRANSPORTED", "BOTH", "NO_DIFF"
EDGE_COLS = ("u", "src", "te", "dst", "ta")


def _b(x, shape=None):
    if x is None:
        return None
    a = np.asarray(x, dtype=bool)
    if shape is not None and a.shape != shape:
        raise ValueError(f"shape {a.shape} != {shape}")
    return a


@dataclasses.dataclass
class DiffRecord:
    held: np.ndarray
    inp: np.ndarray
    arr: Optional[np.ndarray] = None
    edges: Optional[np.ndarray] = None
    post: Optional[np.ndarray] = None
    hook_node: Optional[np.ndarray] = None
    hook_flight: Optional[np.ndarray] = None
    comp_post: Optional[dict] = None
    comp_held: Optional[dict] = None
    local_only: bool = False
    meta: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        self.held = _b(self.held)
        T, U, N = self.held.shape
        sh = (T, U, N)
        self.inp = _b(self.inp, sh)
        self.post = self.held.copy() if self.post is None else _b(self.post, sh)
        self.arr = _b(self.arr, sh)
        self.hook_node = np.zeros(sh, bool) if self.hook_node is None else _b(self.hook_node, sh)
        self.hook_flight = np.zeros(sh, bool) if self.hook_flight is None else _b(self.hook_flight, sh)
        if self.edges is not None:
            e = np.asarray(self.edges, dtype=np.int64).reshape(-1, 5)
            if len(e) and not (e[:, 2] < e[:, 4]).all():
                raise ValueError("every edge needs te < ta")
            self.edges = e
        self._L = self._X = None

    # ------------------------------------------------------------------ shapes and derived masks
    @property
    def shape(self):
        return self.held.shape

    def pre(self) -> np.ndarray:
        """pre[t] = held[t-1]: the node entered tick t already differing."""
        p = np.zeros_like(self.held)
        p[1:] = self.held[:-1]
        return p

    def edge_target(self) -> Optional[np.ndarray]:
        if self.edges is None:
            return None
        T, U, N = self.shape
        m = np.zeros((T, U, N), bool)
        e = self.edges[self.edges[:, 4] < T]
        m[e[:, 4], e[:, 0], e[:, 3]] = True
        return m

    def arr_eff(self) -> np.ndarray:
        """Differing deliveries: the observed `arr` if reported, else edge targets, else none."""
        if self.arr is not None:
            return self.arr
        et = self.edge_target()
        if et is not None:
            return et | self.hook_flight
        return self.hook_flight.copy()

    def node(self) -> np.ndarray:
        """Node (t,u,n) is ACTIVE when it enters t differing, receives a differing delivery, or a differing input."""
        return self.pre() | self.arr_eff() | self.inp

    # ------------------------------------------------------------------ closure invariant
    def closure(self) -> dict:
        pre = self.pre()
        transport_known = self.arr is not None or self.edges is not None or self.local_only
        arr = self.arr_eff()
        start = self.post & ~pre
        un_node = start & ~self.inp & ~arr
        un_hook = self.held & ~self.post & ~self.hook_node
        n_node, n_hook = int(un_node.sum()), int(un_hook.sum())
        checks = []
        if n_node or n_hook:
            checks.append(Check("C1_node_closure", FAIL, {"unexplained_start": n_node, "unexplained_hook": n_hook,
                                                          "first": _first(un_node | un_hook)}))
        elif transport_known:
            checks.append(Check("C1_node_closure", PASS, {"unexplained_start": 0, "unexplained_hook": 0}))
        else:
            checks.append(Check("C1_node_closure", NOT_VERIFIED, "no arrival/edge channel reported"))
        if self.local_only:
            n_arr = int(self.arr.sum()) if self.arr is not None else 0
            n_e = 0 if self.edges is None else len(self.edges)
            checks.append(Check("C2_arrival_closure", FAIL if (n_arr or n_e) else PASS,
                                {"declared_local_only": True, "arrivals": n_arr, "edges": n_e}))
        elif self.arr is not None and self.edges is not None:
            un_arr = self.arr & ~self.edge_target() & ~self.hook_flight
            k = int(un_arr.sum())
            checks.append(Check("C2_arrival_closure", FAIL if k else PASS,
                                {"unexplained_arrival": k, "first": _first(un_arr)}))
        else:
            checks.append(Check("C2_arrival_closure", NOT_VERIFIED, "needs both arr and edges"))
        if self.edges is not None and len(self.edges):
            act = self.node() | self.post
            e = self.edges
            ok = act[e[:, 2], e[:, 0], e[:, 1]]
            k = int((~ok).sum())
            checks.append(Check("C3_edge_sources", FAIL if k else PASS, {"orphan_edges": k}))
        elif self.edges is not None or self.local_only:
            checks.append(Check("C3_edge_sources", PASS, {"orphan_edges": 0, "edges": 0}))
        else:
            checks.append(Check("C3_edge_sources", NOT_VERIFIED, "no edges reported"))
        return {"outcome": worst(checks), "checks": [c.as_dict() for c in checks]}

    # ------------------------------------------------------------------ LOCAL / TRANSPORTED path flags
    def paths(self):
        """Forward DP. L[t,u,n]: an edge-free difference path from an input or node-hook leaf reaches (t,n).
        X[t,u,n]: a difference path crossing >= 1 transport delivery reaches (t,n). Without edges, any
        differing delivery counts as transported (the source stays unresolved; meta['edge_resolved']=False)."""
        if self._L is not None:
            return self._L, self._X
        T, U, N = self.shape
        pre = self.pre()
        L = np.zeros((T, U, N), bool)
        X = np.zeros((T, U, N), bool)
        by_ta = {}
        if self.edges is not None:
            for row in self.edges:
                by_ta.setdefault(int(row[4]), []).append(row)
        arr_obs = self.arr_eff()
        Ls = np.zeros((U, N), bool)
        Xs = np.zeros((U, N), bool)
        for t in range(T):
            L[t] = self.inp[t] | (pre[t] & Ls)
            x = (pre[t] & Xs) | (arr_obs[t] & self.hook_flight[t])
            if self.edges is None:
                x |= arr_obs[t]
            else:
                for row in by_ta.get(t, ()):
                    u, v, te, d = int(row[0]), int(row[1]), int(row[2]), int(row[3])
                    if L[te, u, v] or X[te, u, v]:
                        x[u, d] = True
            X[t] = x
            held = self.held[t]
            Ls = held & (L[t] | self.hook_node[t])
            Xs = held & X[t]
        self._L, self._X = L, X
        self.meta["edge_resolved"] = self.edges is not None
        return L, X

    def path_class(self, t: int, u: int, n: int) -> str:
        L, X = self.paths()
        l, x = bool(L[t, u, n]), bool(X[t, u, n])
        return BOTH if (l and x) else LOCAL if l else TRANSPORTED if x else NO_DIFF

    # ------------------------------------------------------------------ difference cones
    def cone(self, u: int, n: int, t: int) -> dict:
        """Backward difference cone of node (t, n) in unit u.
        -> {'nodes': {(t,n)}, 'edges': {(src,te,dst,ta)}, 'leaves': {(kind,t,n)}}; kinds ENV, HOOK_NODE,
        HOOK_FLIGHT, UNRESOLVED_ARRIVAL (a differing delivery with no recorded edge)."""
        pre = self.pre()
        arr = self.arr_eff()
        node = self.node()
        eb = {}
        if self.edges is not None:
            for row in self.edges[self.edges[:, 0] == u]:
                eb.setdefault((int(row[3]), int(row[4])), []).append((int(row[1]), int(row[2])))
        nodes, edges, leaves = set(), set(), set()
        stack = [(t, n)] if node[t, u, n] else []
        while stack:
            tt, nn = stack.pop()
            if (tt, nn) in nodes:
                continue
            nodes.add((tt, nn))
            if self.inp[tt, u, nn]:
                leaves.add(("ENV", tt, nn))
            if pre[tt, u, nn]:
                if self.hook_node[tt - 1, u, nn]:
                    leaves.add(("HOOK_NODE", tt - 1, nn))
                if self.post[tt - 1, u, nn]:
                    stack.append((tt - 1, nn))
            if arr[tt, u, nn]:
                if self.hook_flight[tt, u, nn]:
                    leaves.add(("HOOK_FLIGHT", tt, nn))
                srcs = eb.get((nn, tt), ())
                if not srcs and not self.hook_flight[tt, u, nn]:
                    leaves.add(("UNRESOLVED_ARRIVAL", tt, nn))
                for v, te in srcs:
                    edges.add((v, te, nn, tt))
                    stack.append((te, v))
        return {"nodes": nodes, "edges": edges, "leaves": leaves}

    @staticmethod
    def cone_cut(cone: dict, tau: int) -> dict:
        """Where the cone's difference lives at the end of tick tau: nodes HELD into tau+1, and edges IN
        FLIGHT (emitted at <= tau, arriving > tau)."""
        held = {n for (t, n) in cone["nodes"] if t == tau + 1 and (tau, n) in cone["nodes"]}
        flight = {e for e in cone["edges"] if e[1] <= tau < e[3]}
        return {"held": held, "flight": flight}

    def first_touch(self, u: int, n: int, t0: int, t1: int) -> int:
        """First tick in (t0, t1] at which node n of unit u is active; -1 if none."""
        node = self.node()
        ts = np.nonzero(node[t0 + 1:t1 + 1, u, n])[0]
        return int(t0 + 1 + ts[0]) if len(ts) else -1

    # ------------------------------------------------------------------ dynamic write authority
    def component_causes(self) -> dict:
        """For every event where component c STARTS to differ at (t,u,n), the input class that could have
        written it: SENSED (differing input), TRANSPORTED (differing delivery), CARRIED (another component of
        the node already differed), HOOK (an intervention wrote it). '+'-joined when several apply;
        UNEXPLAINED when none (a closure failure at component level)."""
        if self.comp_post is None or self.comp_held is None:
            return {"outcome": NOT_VERIFIED, "causes": {}}
        pre = self.pre()
        arr = self.arr_eff()
        out = {}
        for c in self.comp_post:
            cp = _b(self.comp_post[c], self.shape)
            ch = _b(self.comp_held[c], self.shape)
            prev = np.zeros_like(ch)
            prev[1:] = ch[:-1]
            new = cp & ~prev
            d = {}
            for t, u, n in zip(*np.nonzero(new)):
                ks = [k for k, f in (("SENSED", self.inp[t, u, n]), ("TRANSPORTED", arr[t, u, n]),
                                     ("CARRIED", pre[t, u, n])) if f]
                key = "+".join(ks) or "UNEXPLAINED"
                d[key] = d.get(key, 0) + 1
            hk = int((ch & ~cp).sum())
            if hk:
                d["HOOK"] = hk
            if d:
                out[c] = d
        bad = sum(v.get("UNEXPLAINED", 0) for v in out.values())
        return {"outcome": FAIL if bad else PASS, "causes": out}


def _first(mask: np.ndarray):
    idx = np.argwhere(mask)
    return tuple(int(i) for i in idx[0]) if len(idx) else None
