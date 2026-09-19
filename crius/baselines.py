"""Reference Players (controls only; their mechanisms are never in the searched instruction set).

RANDOM        uniform action each step
HEURISTIC     greedy over hamming distance with prefix replay, 1- then 2-step lookahead
ENUMERATE     iterative deepening over op sequences using RESET (brute force)
ENUMERATE_VM  the same strategy as bytecode (the ARM-S search seed; no workspace use)
CACHE_REUSE   ENUMERATE plus a table of observed (op, context) -> delta in workspace
              cells, consulted by in-the-head planning before any probe
ADAPTIVE      CACHE_REUSE plus executable blocks: each solved sequence is recorded as
              a block keyed by (context, delta); blocks and pairs of blocks are tried
              before planning; a successful pair is composed into a new block

Every cross-task datum lives in the Workspace or BlockStore; instance
attributes carry nothing between tasks. Compute is charged one unit per
decision plus the stores' own costs.

CLI: python -m crius.baselines --config crius/configs/c0.json [--out DIR] [--seeds 101 102]
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import random
import time

from . import vm, world
from .env import TaskOver
from .player import PythonPlayer, VMPlayer

K = world.NUM_OPS
RESET = world.RESET_ACTION


def _delta(after, before):
    return tuple((a - b) % world.B for a, b in zip(after, before))


def _is_delta(v) -> bool:
    return isinstance(v, tuple) and len(v) == world.L and all(isinstance(e, int) for e in v)


class RandomPlayer(PythonPlayer):
    name = "RANDOM"

    def run(self, env, st):
        rng = random.Random("RANDOM:%d:%r:%r" % (env.task_index, env.start, env.target))
        while True:
            env.charge(1)
            env.act(rng.randrange(K))


class HeuristicPlayer(PythonPlayer):
    name = "HEURISTIC"
    MAX_PREFIX = 6

    def run(self, env, st):
        prefix = []
        target = env.target
        while len(prefix) < self.MAX_PREFIX:
            env.act(RESET)
            for op in prefix:
                env.act(op)
            base = world.hamming(env.current, target)
            best, best_d = None, base
            for op in range(K):
                env.charge(1)
                env.act(RESET)
                for p in prefix:
                    env.act(p)
                env.act(op)
                d = world.hamming(env.current, target)
                if d < best_d:
                    best, best_d = [op], d
            if best is None:
                for pair in itertools.product(range(K), repeat=2):
                    env.charge(1)
                    env.act(RESET)
                    for p in prefix:
                        env.act(p)
                    env.act(pair[0])
                    env.act(pair[1])
                    d = world.hamming(env.current, target)
                    if d < best_d:
                        best, best_d = list(pair), d
            if best is None:
                env.halt()
            prefix.extend(best)
        env.halt()


class EnumeratePlayer(PythonPlayer):
    name = "ENUMERATE"
    MAX_DEPTH = 4

    def run(self, env, st):
        for depth in range(1, self.MAX_DEPTH + 1):
            for seq in itertools.product(range(K), repeat=depth):
                env.charge(1)
                env.act(RESET)
                for op in seq:
                    env.act(op)
        env.halt()


class CacheReusePlayer(PythonPlayer):
    """Table in cells: 2*op+ctx -> delta tuple; 16+2*op+ctx -> conflict flag."""

    name = "CACHE_REUSE"
    MAX_PLAN_DEPTH = 4
    RECORD_BLOCKS = False

    # ---- the table
    def observe(self, ws, op, before, after):
        ctx = world.context(before)
        addr = 2 * op + ctx
        d = _delta(after, before)
        cur = ws.read(addr)
        if not _is_delta(cur):
            ws.write(addr, d)
        elif cur != d:
            ws.write(16 + addr, 1)

    def model(self, ws, op, x):
        ctx = world.context(x)
        addr = 2 * op + ctx
        if ws.read(16 + addr):
            return None
        d = ws.read(addr)
        if not _is_delta(d):
            return None
        return world.add(x, d)

    def plan(self, env, ws, start, target):
        """Iterative deepening in the head using the table. Returns a sequence or None."""
        for depth in range(1, self.MAX_PLAN_DEPTH + 1):
            found = self._dfs(env, ws, start, target, depth, [])
            if found is not None:
                return found
        return None

    def _dfs(self, env, ws, x, target, depth, path):
        if depth == 0:
            return list(path) if x == target else None
        for op in range(K):
            env.charge(1)
            y = self.model(ws, op, x)
            if y is None:
                continue
            path.append(op)
            r = self._dfs(env, ws, y, target, depth - 1, path)
            path.pop()
            if r is not None:
                return r
        return None

    # ---- acting with observation
    def apply(self, env, ws, op):
        before = env.current
        env.act(op)
        self.observe(ws, op, before, env.current)
        return env.current

    def run_sequence(self, env, ws, seq):
        env.act(RESET)
        for op in seq:
            self.apply(env, ws, op)
            if env.success:
                return True
        return False

    def enumerate_with_observation(self, env, ws):
        for depth in range(1, EnumeratePlayer.MAX_DEPTH + 1):
            for seq in itertools.product(range(K), repeat=depth):
                env.charge(1)
                if self.run_sequence(env, ws, seq):
                    return list(seq)
        return None

    def solved_by(self, env, st, seq):
        """Hook for ADAPTIVE; CACHE_REUSE records nothing executable."""

    def run(self, env, st):
        ws = st.ws
        start, target = env.start, env.target
        plan = self.plan(env, ws, start, target)
        if plan is not None:
            ok = self.run_sequence(env, ws, plan)
            if ok:
                self.solved_by(env, st, plan)
                return
        seq = self.enumerate_with_observation(env, ws)
        if seq is not None:
            self.solved_by(env, st, seq)
            return
        env.halt()


class AdaptivePlayer(CacheReusePlayer):
    """CACHE_REUSE plus executable blocks keyed by (context, delta) in local_state[0..2]."""

    name = "ADAPTIVE"

    def _needed(self, env):
        return world.context(env.start), _delta(env.target, env.start)

    def _key(self, blocks, bid):
        return blocks.state_get(bid, 0), blocks.state_get(bid, 1)

    def solved_by(self, env, st, seq):
        if len(seq) < 2 or len(st.blocks.blocks) >= st.blocks.max_blocks:
            return
        ctx, need = self._needed(env)
        for bid in st.blocks.ids():
            if self._key(st.blocks, bid) == (ctx, need):
                return
        ins = [(vm.OP["ACTI"], op, 0, 0) for op in seq]
        bid = st.blocks.create(ins, origin="record")
        if bid >= 0:
            st.blocks.state_set(bid, 0, ctx)
            st.blocks.state_set(bid, 1, need)
            st.blocks.state_set(bid, 2, len(seq))

    def _replay_observing(self, env, st, bid):
        """Invoke a block through the VM; observe the deltas of its actions afterwards."""
        traj0 = len(env.trajectory)
        before = env.current
        vm.invoke_block(bid, st)
        for a, after in env.trajectory[traj0:]:
            if a != RESET:
                self.observe(st.ws, a, before, after)
            before = after
        return env.success

    def run(self, env, st):
        ws, blocks = st.ws, st.blocks
        ctx, need = self._needed(env)
        keyed = []
        for bid in blocks.ids():
            env.charge(1)
            k = self._key(blocks, bid)
            if _is_delta(k[1]) and isinstance(k[0], int):
                keyed.append((bid, k[0], k[1]))
        # 1. a single stored block with the right key
        for bid, c, d in keyed:
            if (c, d) == (ctx, need):
                env.act(RESET)
                if self._replay_observing(env, st, bid):
                    return
        # 2. a pair of stored blocks whose deltas compose to the need
        for (ba, ca, da), (bb, cb, db) in itertools.permutations(keyed, 2):
            env.charge(1)
            if ca != ctx or world.add(da, db) != need:
                continue
            if (ctx + da[0]) % 2 != cb:
                continue
            env.act(RESET)
            self._replay_observing(env, st, ba)
            if env.success:
                return
            try:
                self._replay_observing(env, st, bb)
            except TaskOver:
                if not env.success:
                    raise
            if env.success:
                nid = blocks.compose(ba, bb)
                if nid >= 0:
                    blocks.state_set(nid, 0, ctx)
                    blocks.state_set(nid, 1, need)
                    blocks.state_set(nid, 2, blocks.length(nid))
                return
        # 3. plan over ops AND stored blocks as macro-operators (depth <= 3), execute, record
        plan = self._plan_with_blocks(env, ws, keyed, env.start, env.target)
        if plan is not None:
            env.act(RESET)
            for item in plan:
                if isinstance(item, tuple):
                    self._replay_observing(env, st, item[0])
                else:
                    self.apply(env, ws, item)
                if env.success:
                    seq = [a for a, _ in env.trajectory if a != RESET]
                    k = max(i for i, (a, _) in enumerate(env.trajectory) if a == RESET)
                    seq = [a for a, _ in env.trajectory[k + 1:]]
                    self.solved_by(env, st, seq)
                    return
        # 4. plan with the table alone, then enumerate
        super().run(env, st)

    def _plan_with_blocks(self, env, ws, keyed, start, target, max_depth=3):
        ops = list(range(K)) + [(bid, c, d) for bid, c, d in keyed]
        for depth in range(1, max_depth + 1):
            found = self._dfs_ext(env, ws, ops, start, target, depth, [])
            if found is not None:
                return found
        return None

    def _dfs_ext(self, env, ws, ops, x, target, depth, path):
        if depth == 0:
            return list(path) if x == target else None
        for item in ops:
            env.charge(1)
            if isinstance(item, tuple):
                bid, c, d = item
                if world.context(x) != c:
                    continue
                y = world.add(x, d)
            else:
                y = self.model(ws, item, x)
                if y is None:
                    continue
            path.append(item)
            r = self._dfs_ext(env, ws, ops, y, target, depth - 1, path)
            path.pop()
            if r is not None:
                return r
        return None


BASELINES = {
    "RANDOM": RandomPlayer,
    "HEURISTIC": HeuristicPlayer,
    "ENUMERATE": EnumeratePlayer,
    "CACHE_REUSE": CacheReusePlayer,
    "ADAPTIVE": AdaptivePlayer,
}


def make_baseline(name: str):
    if name == "ENUMERATE_VM":
        return VMPlayer(vm.enumerate_program(), name="ENUMERATE_VM")
    return BASELINES[name]()


ALL_NAMES = ("RANDOM", "HEURISTIC", "ENUMERATE", "ENUMERATE_VM", "CACHE_REUSE", "ADAPTIVE")


def main(argv=None):
    from . import receipts, streams
    from .evaluate import full_battery

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--seeds", type=int, nargs="*", default=None)
    ap.add_argument("--suite", default=None)
    ap.add_argument("--names", nargs="*", default=None)
    args = ap.parse_args(argv)
    cfg = receipts.load_config(args.config)
    c1 = streams.world_id(cfg) == "c1"
    if c1:
        from . import baselines_c1
    names = args.names or (list(baselines_c1.ALL_NAMES) if c1 else list(ALL_NAMES))
    maker = baselines_c1.make_baseline if c1 else make_baseline
    if args.suite is None:
        args.suite = "gate" if c1 else "search"
    seeds = args.seeds or (cfg["seeds"]["gate"] if c1 else cfg["seeds"]["search"])
    out = args.out or os.path.join("crius", "runs", "baselines_%s" % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    os.makedirs(out, exist_ok=True)
    meta = receipts.run_meta(cfg, args.config)
    rows = []
    for name in names:
        for seed in seeds:
            player = maker(name)
            tasks = streams.lifetime(cfg, seed, args.suite)
            t0 = time.time()
            bat = full_battery(player, tasks, cfg, seed=seed)
            dt = time.time() - t0
            rec = receipts.battery_receipt(meta, player, tasks, seed, args.suite, bat, wall_seconds=dt)
            path = os.path.join(out, "%s_seed%d.json" % (name, seed))
            receipts.write_json(path, rec)
            m = bat["ACCUMULATED"]["metrics"]
            rows.append((name, seed, m, bat, dt))
            print(receipts.one_line(name, seed, bat, dt))
    receipts.write_json(os.path.join(out, "RUN_META.json"), meta)
    print("receipts:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
