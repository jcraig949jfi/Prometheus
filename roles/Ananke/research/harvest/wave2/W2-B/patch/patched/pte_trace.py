"""H-INST draft: exact causal-trace primitives for PTE (no engine edits).

Three primitives, all built on prometheus.ananke.engine.World by subclass or
lockstep composition; physics is never modified.

1. diff_trace      LOCKSTEP TWIN DIFFERENCE TRACER (causal-edge tracer).
                   Two batches A and B with identical world seeds step in
                   lockstep. B may differ by schedule (single-cue twins),
                   between-tick hooks, or (without edges) Controls. Per tick,
                   per world, per site: which state components differ, which
                   arrivals / sense inputs / emissions differ, and every
                   DIFFERENCE-BEARING PACKET EDGE (world, emitter v, emit tick
                   te) -> (recipient u, arrival tick ta), recovered exactly by
                   re-running the engine's own World._emit per differing
                   emitter into scratch mailboxes.
                   Derived: LOCAL vs TRANSPORTED path flags for every
                   (tick, site) node, the backward difference cone of any
                   readout, a cone cut at tick tau (held vs in flight), and
                   the component-infection causes (dynamic write authority).
                   Closure invariant: with identical Controls, a site can only
                   start to differ through a differing arrival, a differing
                   sense input or a hook; a mailbox entry can only start to
                   differ through a recorded edge or a hook. Both counters must
                   be 0 (engine locality + tracer correctness in one check).

2. reach_certificate  per-world INTERVENTION REACH: did a between-tick hook
                   (a) change state at all (APPLIED), (b) reach the readout
                   site by the readout tick (TOUCHED), (c) change the readout
                   value (OUTPUT)? Verdicts UNAPPLIED / NOT_REACHED /
                   ABSORBED / REACHED_OUTPUT, with LOCAL / TRANSPORTED path.
                   Complements lens.verify_reach, whose applied count is a
                   batch digest over all state at all ticks (see REPORT).

3. ProvenanceWorld EXACT FIRST-HOP PROVENANCE TAGS for traffic addressed to a
                   recipient set, keyed by (emitter group, emission epoch),
                   carried from flight into the INBOX (Acc_sum/Acc_cnt) with
                   the engine's drop / aloha / wake-clear / reset / flush
                   rules. Invariant: tags sum exactly to Msum/Mcnt and
                   Acc_sum/Acc_cnt at the recipients. provenance_swap /
                   provenance_follow exchange chosen provenance keys between
                   mirror partners (W-V TagWorld generalised: any group map,
                   emission epochs, inbox included).

Semantics are DIFFERENCE semantics: a difference path is necessary for a
quantity to carry the twin contrast, not sufficient for it to be USED. The
cone is a sound upper bound on carriers, never a carrier verdict.
CPU, eager stepping only (no CUDA graph).
"""
from __future__ import annotations

import bisect
import dataclasses
import pathlib
import sys

import numpy as np
import torch

_REPO = pathlib.Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from prometheus.ananke import envs  # noqa: E402
from prometheus.ananke.engine import Controls, Schedule, World  # noqa: E402

I32, I64 = torch.int32, torch.int64
COMP_BITS = {"S": 1, "inbox": 2, "Kp": 4, "r": 8, "w": 16, "E": 32}
LOCAL, TRANSPORTED, BOTH, NO_DIFF = "LOCAL", "TRANSPORTED", "BOTH", "NO_DIFF"


# ---------------------------------------------------------------- helpers
def mirrored_ws(seeds):
    return [seeds[m - (m % 2)] for m in range(len(seeds))]


def genome_batch(genome: np.ndarray, M: int) -> np.ndarray:
    g = np.asarray(genome)
    if g.ndim == 2:
        g = g[None]
    return np.repeat(g[None], M, axis=0)


def single_cue_schedule(ep: envs.Episode, env: envs.EnvSpec, trial: int) -> Schedule:
    """Copy of ep.schedule with trial `trial`'s cue ticks negated in every
    world (every sensor column). Distractors and other trials unchanged."""
    s = ep.schedule
    sv = s.sense_val.clone()
    t0 = trial * env.period()
    sv[t0:t0 + env.cue_len] = -sv[t0:t0 + env.cue_len]
    return Schedule(s.sense_idx.clone(), sv, s.read_idx.clone())


def site_diff_mask(a: World, b: World) -> torch.Tensor:
    """[B, N] uint8 bitmask of differing site components (COMP_BITS)."""
    m = (a.S != b.S).any(-1).to(I32) * 1
    m |= ((a.Acc_sum != b.Acc_sum).flatten(2).any(-1) | (a.Acc_cnt != b.Acc_cnt).any(-1)).to(I32) * 2
    m |= (a.Kp != b.Kp).any(-1).to(I32) * 4
    m |= (a.r != b.r).to(I32) * 8
    if a.R:
        m |= (a.w != b.w).any(-1).to(I32) * 16
    m |= (a.E != b.E).to(I32) * 32
    return m.to(torch.uint8)


def flight_diff(a: World, b: World) -> torch.Tensor:
    """[LM, B, N] bool: mailbox entry (slot, world, recipient) differs (any channel/component)."""
    return (a.Msum != b.Msum).any(-1).any(-1) | (a.Mcnt != b.Mcnt).any(-1)


def sense_at(w: World, t: int) -> torch.Tensor:
    """The SENSE register value each site receives at tick t (engine step 2)."""
    if t >= w.Tsch:
        return torch.zeros(w.B, w.N, dtype=I32, device=w.dev)
    return torch.zeros(w.B, w.N, dtype=I32, device=w.dev).scatter_add_(1, w.sch_idx, w.sch_val[t])


def _site_snapshot(w: World):
    return {n: getattr(w, n).clone() for n in ("S", "Acc_sum", "Acc_cnt", "Kp", "r", "w", "E")}


def _site_changed(w: World, snap) -> torch.Tensor:
    ch = torch.zeros(w.B, w.N, dtype=torch.bool, device=w.dev)
    for n, v in snap.items():
        x = getattr(w, n)
        d = x != v
        while d.dim() > 2:
            d = d.any(-1)
        ch |= d
    return ch


def _emit_scratch(w: World, want, chan, pay, te: int):
    """Re-run the engine's own World._emit for tick te into scratch mailboxes.
    World state, stats and t_dev are restored; returns (Msum, Mcnt) scratch."""
    real = (w.Msum, w.Mcnt)
    st = {k: v.clone() for k, v in w.stats.items()}
    tsave = w.t_dev.clone()
    s, c = torch.zeros_like(w.Msum), torch.zeros_like(w.Mcnt)
    try:
        w.Msum, w.Mcnt = s, c
        w.t_dev.fill_(te)
        World._emit(w, want, chan, pay)
    finally:
        w.Msum, w.Mcnt = real
        w.t_dev.copy_(tsave)
        for k, v in st.items():
            w.stats[k].copy_(v)
    return s, c


def _ctrl_equal(a: Controls, b: Controls) -> bool:
    da, db = dataclasses.asdict(a), dataclasses.asdict(b)
    ma, mb = da.pop("reset_state_mask"), db.pop("reset_state_mask")
    if da != db:
        return False
    if ma is None and mb is None:
        return True
    if ma is None or mb is None:
        return False
    return bool(np.array_equal(np.asarray(ma), np.asarray(mb)))


# ------------------------------------------------------------ 1 diff_trace
@dataclasses.dataclass
class DiffTrace:
    T: int
    LM: int
    site_post: np.ndarray      # [T, B, N] uint8: component diff after step t (before hook)
    site_hook: np.ndarray      # [T, B, N] uint8: component diff after step t AND hooks of t
    hook_site: np.ndarray      # [T, B, N] bool: a hook at t changed B's site arrays there
    hook_arr: np.ndarray       # [T+LM, B, N] bool: a hook changed B's mail arriving at (ta, u)
    arr: np.ndarray            # [T, B, N] bool: mail arriving at start of t differs
    sense: np.ndarray          # [T, B, N] bool: SENSE input at t differs
    emit: np.ndarray           # [T, B, N] bool: emitter's copies differ (fire/chan/payload/route)
    edges: np.ndarray          # [E, 6] int64: b, v, te, u, ta, chan-any(-1)
    traceA: np.ndarray         # [T, B, A] S0 at read sites
    traceB: np.ndarray
    unexplained_site: int
    unexplained_flight: int
    edges_exact: bool
    L: np.ndarray = None       # [T, B, N] bool: node has an edge-free difference path from a leaf
    X: np.ndarray = None       # [T, B, N] bool: node has a difference path crossing >= 1 packet edge

    # -- derived -------------------------------------------------------
    def pre(self) -> np.ndarray:
        p = np.zeros_like(self.arr)
        p[1:] = self.site_hook[:-1] != 0
        return p

    def node(self) -> np.ndarray:
        return self.pre() | self.arr | self.sense

    def _paths(self):
        """Forward DP of the LOCAL (L) / TRANSPORTED (X) flags."""
        T, B, N = self.arr.shape
        pre = self.pre()
        L = np.zeros((T, B, N), bool)
        X = np.zeros((T, B, N), bool)
        by_ta = {}
        for row in self.edges:
            by_ta.setdefault(int(row[4]), []).append(row)
        Ls = np.zeros((B, N), bool)          # state-level flags after tick t-1 (+hooks)
        Xs = np.zeros((B, N), bool)
        for t in range(T):
            L[t] = self.sense[t] | (pre[t] & Ls)
            x = (pre[t] & Xs) | (self.arr[t] & self.hook_arr[t])
            for row in by_ta.get(t, ()):
                b, v, te, u = int(row[0]), int(row[1]), int(row[2]), int(row[3])
                if L[te, b, v] or X[te, b, v]:
                    x[b, u] = True
            X[t] = x
            held = self.site_hook[t] != 0
            Ls = held & (L[t] | self.hook_site[t])
            Xs = held & X[t]
        self.L, self.X = L, X

    def path_class(self, t: int, b: int, u: int) -> str:
        if self.L is None:
            self._paths()
        l, x = bool(self.L[t, b, u]), bool(self.X[t, b, u])
        return BOTH if (l and x) else LOCAL if l else TRANSPORTED if x else NO_DIFF

    def readout_table(self, ep: envs.Episode, trial: int) -> dict:
        """Per world: output diff at trial's readout, path class, first tick the
        readout site's node became active in (cue onset, readout]."""
        B = self.arr.shape[1]
        rt = ep.ro_tick[:, trial]
        slot = ep.ro_slot[:, trial]
        ridx = ep.schedule.read_idx.numpy()
        out, cls = [], []
        for b in range(B):
            a = int(ridx[b, slot[b]])
            out.append(bool(self.traceA[rt[b], b, slot[b]] != self.traceB[rt[b], b, slot[b]]))
            cls.append(self.path_class(int(rt[b]), b, a))
        return {"output_diff": np.array(out), "path": np.array(cls)}

    def cone(self, b: int, u: int, t: int) -> dict:
        """Backward difference cone of node (t, u) in world b.
        -> {'nodes': set((t,u)), 'edges': set((v,te,u,ta)), 'leaves': set(kind,t,u)}"""
        pre = self.pre()
        eb = {}
        for row in self.edges[self.edges[:, 0] == b]:
            eb.setdefault((int(row[3]), int(row[4])), []).append((int(row[1]), int(row[2])))
        nodes, edges, leaves = set(), set(), set()
        node = self.node()
        stack = [(t, u)] if node[t, b, u] else []
        while stack:
            tt, uu = stack.pop()
            if (tt, uu) in nodes:
                continue
            nodes.add((tt, uu))
            if self.sense[tt, b, uu]:
                leaves.add(("ENV", tt, uu))
            if pre[tt, b, uu]:
                if self.hook_site[tt - 1, b, uu]:
                    leaves.add(("HOOK_SITE", tt - 1, uu))
                if self.site_post[tt - 1, b, uu] != 0:
                    stack.append((tt - 1, uu))
            if self.arr[tt, b, uu]:
                if self.hook_arr[tt, b, uu]:
                    leaves.add(("HOOK_FLIGHT", tt, uu))
                for v, te in eb.get((uu, tt), ()):
                    edges.add((v, te, uu, tt))
                    stack.append((te, v))
        return {"nodes": nodes, "edges": edges, "leaves": leaves}

    @staticmethod
    def cone_cut(cone: dict, tau: int) -> dict:
        """Where the cone's difference lives at the end of tick tau: sites whose
        HELD state continues into tick tau+1 on the cone, and edges IN FLIGHT
        (emitted at <= tau, arriving > tau)."""
        held = {u for (t, u) in cone["nodes"] if t == tau + 1 and (tau, u) in cone["nodes"]}
        flight = {e for e in cone["edges"] if e[1] <= tau < e[3]}
        return {"held": held, "flight": flight}

    def component_causes(self) -> dict:
        """Dynamic write authority: for every event where component c STARTS to
        differ at (t, b, u), the input class that could have written it:
        SENSED / TRANSPORTED (differing arrival) / CARRIED (another component of
        the same site already differed) / HOOK (a hook wrote it) / UNEXPLAINED.
        Multiple classes can apply to one event (reported as a '+'-joined key)."""
        pre = self.pre()
        out = {c: {} for c in COMP_BITS}
        T = self.arr.shape[0]
        for t in range(T):
            prev = self.site_hook[t - 1] if t else np.zeros_like(self.site_hook[0])
            for c, bit in COMP_BITS.items():
                new = ((self.site_post[t] & bit) != 0) & ((prev & bit) == 0)
                hk = ((self.site_hook[t] & bit) != 0) & ((self.site_post[t] & bit) == 0)
                for b, u in zip(*np.nonzero(new)):
                    ks = [k for k, f in (("SENSED", self.sense[t, b, u]), ("TRANSPORTED", self.arr[t, b, u]),
                                         ("CARRIED", pre[t, b, u])) if f]
                    key = "+".join(ks) or "UNEXPLAINED"
                    out[c][key] = out[c].get(key, 0) + 1
                n_h = int(hk.sum())
                if n_h:
                    out[c]["HOOK"] = out[c].get("HOOK", 0) + n_h
        return {c: v for c, v in out.items() if v}


def diff_trace(ph, genome, sch_a: Schedule, sch_b: Schedule, ws, T: int, hooks_b=None, ctrl_a=None,
               ctrl_b=None, device="cpu", edges=True, _fault_edge_tick=0) -> DiffTrace:
    """Lockstep twin tracer. hooks_b {tick: fn(world) | [fn]} run on B AFTER tick.
    `_fault_edge_tick` shifts the tick used to recompute edges (fault injection
    for the must-fail closure test only; never set it in real use)."""
    ctrl_a, ctrl_b = ctrl_a or Controls(), ctrl_b or Controls()
    same_ctrl = _ctrl_equal(ctrl_a, ctrl_b)
    M = len(ws)
    g = genome_batch(genome, M)
    A = World(ph, g, ws, device=device, ctrl=ctrl_a, schedule=sch_a)
    Bw = World(ph, g, ws, device=device, ctrl=ctrl_b, schedule=sch_b)
    LM, N = A.LM, A.N
    exact = bool(edges and same_ctrl and not ("w" in ctrl_a.reset_parts and ctrl_a.reset_state_at))
    hooks_b = hooks_b or {}
    route_by_w = ph.topology != "global" and ph.dest_mode != "all" and A.R > 0
    site_post = np.zeros((T, M, N), np.uint8)
    site_hook = np.zeros((T, M, N), np.uint8)
    hook_site = np.zeros((T, M, N), bool)
    hook_arr = np.zeros((T + LM, M, N), bool)
    arr = np.zeros((T, M, N), bool)
    sense = np.zeros((T, M, N), bool)
    emit = np.zeros((T, M, N), bool)
    E = []
    un_site = un_flight = 0
    prev_fd = torch.zeros(LM, M, N, dtype=torch.bool)
    prev_sd = torch.zeros(M, N, dtype=torch.bool)
    flush_ticks = set(ctrl_a.flush_inflight_at) | set(ctrl_b.flush_inflight_at)
    for t in range(T):
        slot = t % LM
        arr[t] = prev_fd[slot].numpy()
        sd_in = (sense_at(A, t) != sense_at(Bw, t))
        sense[t] = sd_in.numpy()
        A.step()
        Bw.step()
        sp = site_diff_mask(A, Bw)
        site_post[t] = sp.numpy()
        new_site = (sp != 0) & ~prev_sd & ~torch.as_tensor(arr[t]) & ~sd_in
        if same_ctrl:
            un_site += int(new_site.sum())
        # --- emission differences and exact edges (before hooks: post-step w is the emission w)
        ea, eb_ = A.last_emit, Bw.last_emit
        ed = (ea != eb_) | ((ea & eb_) & ((A.last_chan != Bw.last_chan) | (A.last_pay != Bw.last_pay).any(-1)))
        if route_by_w:
            ed |= (ea | eb_) & (A.w != Bw.w).any(-1)
        emit[t] = ed.numpy()
        fd = flight_diff(A, Bw)
        targets = torch.zeros(LM, M, N, dtype=torch.bool)
        if exact and ed.any() and t not in flush_ticks:
            te = t + _fault_edge_tick
            idx = ed.nonzero(as_tuple=False)
            rank = torch.zeros(M, dtype=I64)
            ranks = []
            for bb, _v in idx.tolist():
                ranks.append(int(rank[bb]))
                rank[bb] += 1
            ranks = torch.tensor(ranks, dtype=I64)
            for k in range(int(rank.max())):
                sel = idx[ranks == k]
                mk = torch.zeros(M, N, dtype=torch.bool)
                mk[sel[:, 0], sel[:, 1]] = True
                sa, ca = _emit_scratch(A, A.last_emit & mk, A.last_chan, A.last_pay, te)
                sb, cb = _emit_scratch(Bw, Bw.last_emit & mk, Bw.last_chan, Bw.last_pay, te)
                dd = (sa != sb).any(-1) | (ca != cb)                 # [LM, M, N, C]
                dslot = dd.any(-1)
                targets |= dslot
                v_of_b = torch.full((M,), -1, dtype=I64)
                v_of_b[sel[:, 0]] = sel[:, 1]
                for s_, b_, u_ in dslot.nonzero(as_tuple=False).tolist():
                    ta = t + 1 + ((s_ - (t + 1)) % LM)
                    E.append((b_, int(v_of_b[b_]), t, u_, ta, -1))
        if exact:
            new_f = fd & ~prev_fd
            new_f[slot] = False
            un_flight += int((new_f & ~targets).sum())
        # --- hooks on B
        fns = hooks_b.get(t, ())
        fns = fns if isinstance(fns, (list, tuple)) else [fns]
        if fns:
            snap = _site_snapshot(Bw)
            ms, mc = Bw.Msum.clone(), Bw.Mcnt.clone()
            for fn in fns:
                fn(Bw)
            hook_site[t] = _site_changed(Bw, snap).numpy()
            fch = ((Bw.Msum != ms).any(-1).any(-1) | (Bw.Mcnt != mc).any(-1))   # [LM, M, N]
            for s_, b_, u_ in fch.nonzero(as_tuple=False).tolist():
                ta = t + 1 + ((s_ - (t + 1)) % LM)
                if ta < T + LM:
                    hook_arr[ta, b_, u_] = True
            sp = site_diff_mask(A, Bw)
            fd = flight_diff(A, Bw)
        site_hook[t] = sp.numpy()
        prev_sd = sp != 0
        prev_fd = fd
    ed_arr = np.array(E, dtype=np.int64).reshape(-1, 6)
    return DiffTrace(T, LM, site_post, site_hook, hook_site, hook_arr, arr, sense, emit, ed_arr,
                     A.trace.cpu().numpy(), Bw.trace.cpu().numpy(), un_site, un_flight, exact)


def twin_trace(ph, genome, env: envs.EnvSpec, seeds, trial: int, T: int | None = None, device="cpu",
               **kw) -> tuple[DiffTrace, envs.Episode]:
    """Single-cue twins: B = A with trial `trial`'s cue negated. Runs to the
    trial's readout (+1) unless T is given."""
    ep = envs.build(ph, env, seeds)
    ws = mirrored_ws(seeds)
    T = T or int(ep.ro_tick[:, trial].max()) + 1
    dt = diff_trace(ph, genome, ep.schedule, single_cue_schedule(ep, env, trial), ws, T, device=device, **kw)
    return dt, ep


# ------------------------------------------------------ 2 reach certificate
UNAPPLIED, NOT_REACHED, ABSORBED, REACHED_OUTPUT = "UNAPPLIED", "NOT_REACHED", "ABSORBED", "REACHED_OUTPUT"


def reach_certificate(ph, genome, env: envs.EnvSpec, seeds, hooks: dict, trial: int, device="cpu",
                      ctrl=None) -> dict:
    """Per-world reach of a between-tick intervention to trial `trial`'s readout.
    A = normal, B = normal + hooks (same seeds, same schedule, same Controls).
    Only hooks at ticks < the trial's readout tick can matter; the trace runs
    to the readout. Returns fractions over worlds and a batch verdict:
      UNAPPLIED       no world's state changed
      NOT_REACHED     changed, but in no world did the difference reach the
                      readout site's state or mail by the readout tick
      ABSORBED        the readout site was touched in some world, the readout
                      value changed in none (an informative null candidate)
      REACHED_OUTPUT  the readout value changed in >= 1 world
    'path' counts LOCAL / TRANSPORTED / BOTH over worlds with an output change.
    W2-B additions (keys added; the batch verdict above is unchanged except for the window):
      * touches count only inside the trial's own window [cue onset, readout] (a hook in an earlier trial
        whose difference died before this trial's cue no longer makes the trial ABSORBED);
      * 'decision' = fraction of worlds whose scored decision sign(S0) in {-1,0,+1} changed
        (the value-level 'output' also counts magnitude-only changes);
      * 'per_world' verdicts and 'absorbed' = fraction of worlds that are admissible nulls (touched,
        decision unchanged); a batch null is admissible only for that fraction of worlds."""
    ep = envs.build(ph, env, seeds)
    ws = mirrored_ws(seeds)
    rt = ep.ro_tick[:, trial]
    T = int(rt.max()) + 1
    ctrl = ctrl or Controls()
    dt = diff_trace(ph, genome, ep.schedule, ep.schedule, ws, T, hooks_b=hooks, ctrl_a=ctrl, ctrl_b=ctrl,
                    device=device)
    node = dt.node()
    M = len(seeds)
    ridx = ep.schedule.read_idx.numpy()
    applied = dt.hook_site.any((0, 2)) | dt.hook_arr.any((0, 2))
    t_on = trial * env.period()                       # the trial's cue onset: its window starts here
    hook_ticks = [t for t in hooks if t < T]
    t_h = max(min(hook_ticks), t_on) if hook_ticks else T
    touched = np.zeros(M, bool)
    first = np.full(M, -1)
    rt_tab = dt.readout_table(ep, trial)
    for b in range(M):
        a = int(ridx[b, ep.ro_slot[b, trial]])
        ts = np.nonzero(node[t_h + 1:int(rt[b]) + 1, b, a])[0] if t_h < T else []
        # hook directly on the readout site's state also counts (LOCAL touch), inside the window only
        direct = dt.hook_site[t_h:int(rt[b]), b, a].any() if t_h < T else False
        if len(ts) or direct:
            touched[b] = True
            first[b] = (t_h + 1 + int(ts[0])) if len(ts) else t_h
    out = rt_tab["output_diff"]
    if not applied.any():
        v = UNAPPLIED
    elif out.any():
        v = REACHED_OUTPUT
    elif touched.any():
        v = ABSORBED
    else:
        v = NOT_REACHED
    paths = {}
    for p in rt_tab["path"][out]:
        paths[p] = paths.get(p, 0) + 1
    sl = ep.ro_slot[np.arange(M), trial]
    dec = np.sign(dt.traceA[rt, np.arange(M), sl]) != np.sign(dt.traceB[rt, np.arange(M), sl])
    per_world = np.where(~applied, UNAPPLIED, np.where(dec, "REACHED_DECISION", np.where(
        out, "REACHED_VALUE_ONLY", np.where(touched, ABSORBED, NOT_REACHED))))
    return {"verdict": v, "applied": float(applied.mean()), "touched": float(touched.mean()),
            "output": float(out.mean()), "decision": float(dec.mean()),
            "absorbed": float((touched & ~dec).mean()), "per_world": per_world.tolist(),
            "first_touch_lag": (first - rt)[touched].tolist(),
            "path": paths, "unexplained_site": dt.unexplained_site,
            "unexplained_flight": dt.unexplained_flight, "trace": dt}


# ------------------------------------------------------- 3 ProvenanceWorld
class ProvenanceWorld(World):
    """Normal physics + exact first-hop provenance tags for mail addressed to
    `recipients` [B, A] (default: read_idx), keyed by (group, epoch):
    key = group + n_groups * epoch, group = groups[b, emitter], epoch =
    bisect_right(epoch_bounds, emit tick). Flight tags Fsum [LM,B,A,K,C,P],
    Fcnt [LM,B,A,K,C]; inbox tags Isum [B,A,K,C,P], Icnt [B,A,K,C].
    Supported delivery rules: collision none / aloha, drop_packets_at,
    flush_inflight_at, reset_state_at with 'inbox', wake-clear. Not supported
    (raises): saturate, distractor_chan. Group ids outside [0, n_groups) are
    silently untracked, which check() then exposes as a mismatch."""

    def __init__(self, ph, genomes, ws, *, groups, n_groups: int, epoch_bounds=(), recipients=None, **kw):
        kw.setdefault("device", "cpu")           # World defaults to cuda; this draft is CPU-only
        super().__init__(ph, genomes, ws, **kw)
        if ph.cap > 0 and ph.collision == "saturate":
            raise NotImplementedError("saturate is not linear in the tags")
        if self.ctrl.distractor_chan >= 0:
            raise NotImplementedError("distractor traffic has no emitter")
        B, dev = self.B, self.dev
        C, P = ph.channels, ph.payload_width
        self.groups = torch.as_tensor(groups, dtype=I64, device=dev)
        assert self.groups.shape == (B, self.N)
        self.G = int(n_groups)
        self.bounds = list(epoch_bounds)
        self.K = self.G * (len(self.bounds) + 1)
        rec = self.read_idx if recipients is None else torch.as_tensor(recipients, dtype=I64, device=dev)
        for b in range(B):
            assert len(set(rec[b].tolist())) == rec.shape[1], "recipients must be unique per world"
        self.rec = rec
        self._bi = torch.arange(B, device=dev)[:, None]
        Aq = rec.shape[1]
        self.Fsum = torch.zeros(self.LM, B, Aq, self.K, C, P, dtype=I32, device=dev)
        self.Fcnt = torch.zeros(self.LM, B, Aq, self.K, C, dtype=I32, device=dev)
        self.Isum = torch.zeros(B, Aq, self.K, C, P, dtype=I32, device=dev)
        self.Icnt = torch.zeros(B, Aq, self.K, C, dtype=I32, device=dev)
        self.clamp_hits = 0

    def state_arrays(self):          # tags are never part of the world's state or digest
        return World.state_arrays(self)

    def _tick(self):
        ph, ctrl = self.ph, self.ctrl
        t = int(self.t_dev)
        slot = t % self.LM
        fs, fc = self.Fsum[slot].clone(), self.Fcnt[slot].clone()
        dropped = bool(ctrl.drop_packets_at) and t in set(ctrl.drop_packets_at)
        if dropped:
            fs.zero_()
            fc.zero_()
        if ph.cap > 0 and ph.collision == "aloha":
            tot = self.Mcnt[slot][self._bi, self.rec].sum(-1) * (0 if dropped else 1)   # [B, A]
            over = tot > ph.cap
            fs.masked_fill_(over[..., None, None, None], 0)
            fc.masked_fill_(over[..., None, None], 0)
        self.Isum.add_(fs)
        self.Icnt.add_(fc)
        self.Fsum[slot] = 0
        self.Fcnt[slot] = 0
        super()._tick()
        aw = self.last_awake[self._bi, self.rec]                                      # [B, A]
        self.Isum.masked_fill_(aw[..., None, None, None], 0)
        self.Icnt.masked_fill_(aw[..., None, None], 0)
        if ctrl.reset_state_at and "inbox" in ctrl.reset_parts and t in set(ctrl.reset_state_at):
            hit = self._reset_mask[self._bi, self.rec]
            self.Isum.masked_fill_(hit[..., None, None, None], 0)
            self.Icnt.masked_fill_(hit[..., None, None], 0)
        if ctrl.flush_inflight_at and t in set(ctrl.flush_inflight_at):
            self.Fsum.zero_()
            self.Fcnt.zero_()
        if (self.Acc_sum[self._bi, self.rec].abs() >= 2 ** 20).any():
            self.clamp_hits += 1

    def _emit(self, want, chan, pay):
        super()._emit(want, chan, pay)
        te = int(self.t_dev)
        e = bisect.bisect_right(self.bounds, te)
        real = (self.Msum, self.Mcnt)
        st = {k: v.clone() for k, v in self.stats.items()}
        s, c = torch.zeros_like(self.Msum), torch.zeros_like(self.Mcnt)
        try:
            for gi in range(self.G):
                m = self.groups == gi
                if not (want & m).any():
                    continue
                s.zero_()
                c.zero_()
                self.Msum, self.Mcnt = s, c
                World._emit(self, want & m, chan, pay)
                k = gi + self.G * e
                self.Fsum[:, :, :, k] += s[:, self._bi, self.rec]
                self.Fcnt[:, :, :, k] += c[:, self._bi, self.rec]
        finally:
            self.Msum, self.Mcnt = real
            for kk, v in st.items():
                self.stats[kk].copy_(v)

    def check(self) -> dict:
        """Max |tags summed over keys - real arrays| at the recipients. All 0 = exact."""
        bi, rec = self._bi, self.rec
        return {
            "flight_sum": int((self.Fsum.sum(3) - self.Msum[:, bi, rec]).abs().max()),
            "flight_cnt": int((self.Fcnt.sum(3) - self.Mcnt[:, bi, rec]).abs().max()),
            "inbox_sum": int((self.Isum.sum(2) - self.Acc_sum[bi, rec]).abs().max()),
            "inbox_cnt": int((self.Icnt.sum(2) - self.Acc_cnt[bi, rec]).abs().max()),
        }

    def tags(self) -> dict:
        return {"Fsum": self.Fsum.clone(), "Fcnt": self.Fcnt.clone(), "Isum": self.Isum.clone(),
                "Icnt": self.Icnt.clone(), "rec": self.rec.clone()}


def provenance_swap(dst: World, tags: dict, keys) -> None:
    """Every world b receives, at the tagged recipients, its mirror partner's
    contribution from provenance `keys` in place of its own (flight + inbox).
    Exact because PTE mail superposes by SUM. Other keys are untouched."""
    idx = torch.as_tensor(list(keys), dtype=I64, device=dst.dev)
    if idx.numel() == 0:
        return
    p = torch.arange(dst.B, device=dst.dev) ^ 1
    bi = torch.arange(dst.B, device=dst.dev)[:, None]
    rec = tags["rec"]
    fs, fc = tags["Fsum"].index_select(3, idx).sum(3), tags["Fcnt"].index_select(3, idx).sum(3)
    is_, ic = tags["Isum"].index_select(2, idx).sum(2), tags["Icnt"].index_select(2, idx).sum(2)
    dst.Msum[:, bi, rec] = dst.Msum[:, bi, rec] + (fs[:, p] - fs).to(I32)
    dst.Mcnt[:, bi, rec] = dst.Mcnt[:, bi, rec] + (fc[:, p] - fc).to(I32)
    dst.Acc_sum[bi, rec] = dst.Acc_sum[bi, rec] + (is_[p] - is_).to(I32)
    dst.Acc_cnt[bi, rec] = dst.Acc_cnt[bi, rec] + (ic[p] - ic).to(I32)


def provenance_follow(ph, genome, env: envs.EnvSpec, seeds, trial: int, tick: int, groups, n_groups: int,
                      keysets: dict, epoch_bounds=(), device="cpu") -> dict:
    """Fork after tick `tick`, apply provenance_swap(keys) per arm, run to
    trial's readout. Returns per arm: follow (fraction of worlds, among pairs
    where both partners are normal-correct, whose answer becomes the partner's),
    identical (readout bit-identical to normal in every world), and the
    base-run invariant check."""
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    ws = mirrored_ws(seeds)
    g = genome_batch(genome, M)
    base = ProvenanceWorld(ph, g, ws, device=device, schedule=ep.schedule, groups=groups, n_groups=n_groups,
                           epoch_bounds=epoch_bounds)
    rt = ep.ro_tick[:, trial]
    assert tick < int(rt.min()), "fork tick must precede the readout"
    for _ in range(tick + 1):
        base.step()
    chk = base.check()
    tags = base.tags()
    snap = {n: v.clone() for n, v in World.state_arrays(base).items()}

    def fork(keys):
        w = World(ph, g, ws, device=device, schedule=ep.schedule)
        for n, v in snap.items():
            getattr(w, n).copy_(v)
        w.t = base.t
        w.t_dev.fill_(base.t)
        if keys is not None:
            provenance_swap(w, tags, keys)
        for _ in range(tick + 1, int(rt.max()) + 1):
            w.step()
        tr = w.trace.cpu().numpy()
        return tr[rt, np.arange(M), ep.ro_slot[:, trial]].astype(np.int64)

    s_norm = fork(None)
    y = ep.y[:, trial]
    corr = np.sign(s_norm) == y
    ok = corr & corr[np.arange(M) ^ 1]
    out = {"check": chk, "eligible": int(ok.sum())}
    for name, keys in keysets.items():
        s = fork(keys)
        follow = np.sign(s) == np.sign(s_norm[np.arange(M) ^ 1])
        out[name] = {"follow": float(follow[ok].mean()) if ok.any() else float("nan"),
                     "identical": bool(np.array_equal(s, s_norm))}
    return out
