"""The WSE world: one event-stream grammar; every W-coordinate is a knob setting.

An EPISODE is a list of ticks; each tick is the list of uint32 words the organism finds on
input channel 0. Some ticks carry an expected answer (the first word the organism writes on
output channel 0 that tick). Nothing here knows what a register, a tape or a persistence
policy is: the world emits words and expects words.

Kind codes are the world's fixed syntax. Every IDENTITY (tag, value, operator parameter,
node id, order of arrival, which stream is asked) is drawn fresh per episode from the seed.

    PUT    [1, tag, v]                  s_tag := s_tag (op_tag) v    (first v initialises)
           [1, tag, p_1..p_n]           when `expensive` = n: v = sum(p_i) mod 2^32
    ASK    [2, tag]                     expect s_tag
    ASKX   [3, tag, y, p_1..p_n]        expect s_tag (op_tag) y; when the stream is
                                        expensive its LAST put's n pieces are re-supplied
                                        so that recomputation is POSSIBLE (reading n words)
                                        and storage is not the only route (D=1 in W6)
    ASK2   [4, tagA, tagB, c]           expect combine_c(s_A, s_B), c in 0..3 (ADD XOR SUB OR)
    ASKO   [5, v0]                      expect the LAST value put to the stream whose FIRST
                                        value was v0 (streams share a state value, so a
                                        value-only store cannot answer)
    SETOP  [6, tag, a, b, c]            op_tag(s, v) = (a*s + b*v + c) mod 2^32
    DEF    [7, node, a, b, c, x, y]     node := (a*val(x) + b*val(y) + c) mod 2^32
    NOISE  [8, r1, r2]                  never referenced
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Tuple

from proteus.foundry.prng import SplitMix64, seed_from

MASK32 = 0xFFFFFFFF
K_PUT, K_ASK, K_ASKX, K_ASK2, K_ASKO, K_SETOP, K_DEF, K_NOISE, K_RETIRE = 1, 2, 3, 4, 5, 6, 7, 8, 9
GRAMMAR_VERSION = "wse.event_grammar.v0.1"
DEFAULT_OP = (1, 1, 0)      # ADD


def combine(c: int, x: int, y: int) -> int:
    c %= 4
    if c == 0:
        return (x + y) & MASK32
    if c == 1:
        return x ^ y
    if c == 2:
        return (x - y) & MASK32
    return x | y


def apply_op(op: Tuple[int, int, int], s: int, v: int) -> int:
    a, b, c = op
    return (a * s + b * v + c) & MASK32


@dataclass(frozen=True)
class WorldSpec:
    """Every knob of directive VI, independently settable. `name` is a label only."""
    name: str = "W0"
    K: int = 1                       # simultaneously live streams
    D: int = 1                       # events (PUTs) per stream
    interleave: str = "sequential"   # sequential | random
    delay: int = 0                   # NOISE-only ticks between the last PUT and the asks
    ask_mode: str = "all"            # all | one
    ask_kind: str = "ASK"            # ASK | ASKX | ASK2 | ASKO
    ask_timing: str = "end"          # end | interleaved
    fanout: int = 1                  # ASKX consumers per stream
    expensive: int = 0               # pieces per PUT (0 = plain value)
    op_mode: str = "fixed"           # fixed | per_stream
    topology: str = "streams"        # streams | dag
    n_defs: int = 0                  # DEF nodes when topology = dag
    noise_rate: float = 0.0          # probability of NOISE words appended to a tick
    value_bits: int = 8
    # ---- v0.2 stream-world knobs (topology = "stream"; DESIGN_v0.2 s1)
    Kd: int = 0                      # distractor entities (never asked)
    retire_rate: float = 0.0         # P(a tracked tag is RETIREd after its last PUT)
    delays: tuple = ()               # per-tag ask delay drawn from this set (random timing)
    interfere: bool = False          # distractor tags share the top 12 bits of tracked tags
    vocab: str = "train"             # train: tags in [1,2^15); heldout: [2^15, 2^16)
    recycle: bool = False            # v0.3: after RETIRE the tag gets D NEW PUTs; ASK expects the new fold only

    def world_id(self) -> str:
        return hashlib.sha256(json.dumps({"grammar": GRAMMAR_VERSION, **asdict(self)},
                                         sort_keys=True).encode()).hexdigest()[:16]

    def knobs(self) -> dict:
        return asdict(self)


@dataclass
class Episode:
    ticks: List[List[int]]
    expected: Dict[int, int]                 # tick index -> expected first output word
    intervention_tick: int                   # the tick BEFORE which an intervention applies
    meta: dict = field(default_factory=dict)

    def n_asks(self) -> int:
        return len(self.expected)


def _distinct(rng: SplitMix64, n: int, lo: int, hi: int) -> List[int]:
    out: List[int] = []
    seen = set()
    while len(out) < n:
        x = rng.randint(lo, hi - 1)
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _shuffle(rng: SplitMix64, xs: list) -> list:
    xs = list(xs)
    for i in range(len(xs) - 1, 0, -1):
        j = rng.randbelow(i + 1)
        xs[i], xs[j] = xs[j], xs[i]
    return xs


def _noise(rng: SplitMix64) -> List[int]:
    return [K_NOISE, rng.next_u32(), rng.next_u32()]


def make_episode(spec: WorldSpec, rng: SplitMix64) -> Episode:
    if spec.topology == "dag":
        return _make_dag_episode(spec, rng)
    if spec.topology == "stream":
        return _make_ssf_episode(spec, rng)
    for _ in range(64):
        ep = _make_stream_episode(spec, rng)
        if ep is not None:
            return ep
    raise RuntimeError("could not construct a well-posed episode in 64 draws")


def _make_stream_episode(spec: WorldSpec, rng: SplitMix64):
    K, D = spec.K, spec.D
    vmax = 1 << spec.value_bits
    tags = _distinct(rng, K, 1, 1 << 16)
    ops = {t: DEFAULT_OP for t in tags}
    if spec.op_mode == "per_stream":
        ops = {t: (rng.randint(1, 7), rng.randint(1, 7), rng.randint(0, vmax - 1)) for t in tags}

    # per-stream PUT payloads: pieces[t][d] is the word list after [PUT, tag]; value = sum
    pieces: Dict[int, List[List[int]]] = {}
    for t in tags:
        n = max(1, spec.expensive)
        pieces[t] = [[rng.randint(0, vmax - 1) for _ in range(n)] for _ in range(D)]
    if spec.ask_kind == "ASKO":
        # W8: streams share a final state (ADD op, permuted values) but differ in origin/last.
        if not (spec.op_mode == "fixed" and spec.expensive == 0 and D >= 2 and K >= 2):
            raise ValueError("ASKO needs fixed op, no pieces, D>=2, K>=2")
        base = pieces[tags[0]]
        for t in tags[1:]:
            perm = _shuffle(rng, base)
            tries = 0
            while (perm[0] == base[0] or perm[-1] == base[-1]) and tries < 16:
                perm = _shuffle(rng, base); tries += 1
            if perm[0] == base[0] or perm[-1] == base[-1]:
                return None
            pieces[t] = perm
        firsts = [pieces[t][0][0] for t in tags]
        if len(set(firsts)) != K:
            return None
    values = {t: [sum(p) & MASK32 for p in pieces[t]] for t in tags}

    state: Dict[int, int] = {}
    for t in tags:
        s = values[t][0]
        for v in values[t][1:]:
            s = apply_op(ops[t], s, v)
        state[t] = s

    put_events: List[Tuple[int, List[int]]] = [(t, [K_PUT, t] + list(p)) for t in tags for p in pieces[t]]
    order = list(range(len(put_events)))
    if spec.interleave == "random":
        remaining = {t: [i for i, (tt, _) in enumerate(put_events) if tt == t] for t in tags}
        order = []
        while any(remaining.values()):
            live = [t for t in tags if remaining[t]]
            t = live[rng.randbelow(len(live))]
            order.append(remaining[t].pop(0))

    ticks: List[List[int]] = []
    expected: Dict[int, int] = {}
    if spec.op_mode == "per_stream":
        for t in _shuffle(rng, tags):
            a, b, c = ops[t]
            ticks.append([K_SETOP, t, a, b, c])
    last_put_tick: Dict[int, int] = {}
    for i in order:
        t, words = put_events[i]
        ticks.append(list(words))
        last_put_tick[t] = len(ticks) - 1

    asked = list(tags) if spec.ask_mode == "all" else [tags[rng.randbelow(K)]]
    asked = _shuffle(rng, asked)
    ask_events: List[Tuple[int, List[int], int]] = []
    for t in asked:
        if spec.ask_kind == "ASK":
            ask_events.append((t, [K_ASK, t], state[t]))
        elif spec.ask_kind == "ASKX":
            for _ in range(spec.fanout):
                y = rng.randint(0, vmax - 1)
                words = [K_ASKX, t, y]
                if spec.expensive > 0:
                    words = words + list(pieces[t][-1])
                ask_events.append((t, words, apply_op(ops[t], state[t], y)))
        elif spec.ask_kind == "ASK2":
            others = [u for u in tags if u != t]
            u = others[rng.randbelow(len(others))]
            c = rng.randbelow(4)
            ask_events.append((t, [K_ASK2, t, u, c], combine(c, state[t], state[u])))
        elif spec.ask_kind == "ASKO":
            ask_events.append((t, [K_ASKO, values[t][0]], values[t][-1]))
        else:
            raise ValueError(spec.ask_kind)

    if spec.ask_timing == "end":
        for _ in range(spec.delay):
            ticks.append(_noise(rng))
        for t, words, exp in ask_events:
            ticks.append(words)
            expected[len(ticks) - 1] = exp
    else:
        # interleaved: each ask lands at a random tick strictly after its stream's last PUT,
        # possibly before other streams finish (W4 conditions)
        n_base = len(ticks) + spec.delay
        inserts = sorted(((rng.randint(last_put_tick[t] + 1, n_base), words, exp)
                          for t, words, exp in ask_events), key=lambda z: z[0])
        out: List[List[int]] = []
        exp_out: Dict[int, int] = {}
        j = 0
        for i in range(n_base + 1):
            while j < len(inserts) and inserts[j][0] == i:
                out.append(inserts[j][1]); exp_out[len(out) - 1] = inserts[j][2]; j += 1
            if i < len(ticks):
                out.append(ticks[i])
            elif i < n_base:
                out.append(_noise(rng))
        ticks, expected = out, exp_out

    if spec.noise_rate > 0:
        for tk in ticks:
            if rng.unit() < spec.noise_rate:
                tk.extend(_noise(rng))

    itick = last_put_tick[asked[0]] + 1
    # which asks depend only on state completed BEFORE the intervention tick: the attainable
    # ceiling of any erase-type intervention (asks whose stream finishes later are re-stored)
    done = {}
    for t, words, exp in ask_events:
        deps = [t] if spec.ask_kind != "ASK2" else [t, words[2]]
        done[tuple(words)] = all(last_put_tick[u] < itick for u in deps)
    ask_done = {ti: done.get(tuple(w), False) for ti, w in enumerate(ticks) if ti in expected}
    return Episode(ticks=ticks, expected=expected, intervention_tick=itick,
                   meta={"tags": tags, "asked": asked, "K": K, "D": D, "ask_done": ask_done})


def _make_dag_episode(spec: WorldSpec, rng: SplitMix64) -> Episode:
    """W10: K input nodes by PUT, n_defs DEF nodes over earlier nodes, one ASK of a random
    DEF node. Arrival order is shuffled so some DEFs reference nodes not yet seen."""
    vmax = 1 << spec.value_bits
    K, n_defs = spec.K, spec.n_defs
    ids = _distinct(rng, K + n_defs, 1, 1 << 16)
    inputs, defs = ids[:K], ids[K:]
    val: Dict[int, int] = {t: rng.randint(0, vmax - 1) for t in inputs}
    def_rows = []
    known = list(inputs)
    for node in defs:
        x = known[rng.randbelow(len(known))]
        y = known[rng.randbelow(len(known))]
        a, b, c = rng.randint(1, 3), rng.randint(1, 3), rng.randint(0, vmax - 1)
        val[node] = (a * val[x] + b * val[y] + c) & MASK32
        def_rows.append([K_DEF, node, a, b, c, x, y])
        known.append(node)
    events = _shuffle(rng, [[K_PUT, t, val[t]] for t in inputs] + def_rows)
    ticks = [list(e) for e in events]
    for _ in range(spec.delay):
        ticks.append(_noise(rng))
    target = defs[rng.randbelow(len(defs))] if defs else inputs[rng.randbelow(len(inputs))]
    ticks.append([K_ASK, target])
    expected = {len(ticks) - 1: val[target]}
    if spec.noise_rate > 0:
        for tk in ticks:
            if rng.unit() < spec.noise_rate:
                tk.extend(_noise(rng))
    return Episode(ticks=ticks, expected=expected, intervention_tick=len(events),
                   meta={"inputs": inputs, "defs": defs, "target": target,
                         "ask_done": {len(ticks) - 1: True}})


def _make_ssf_episode(spec: WorldSpec, rng: SplitMix64) -> Episode:
    """DESIGN_v0.2 s1: K tracked + Kd distractor entities, D PUTs each (replace or add),
    optional RETIRE of tracked tags, per-tag random ask delay, interference, vocab range."""
    K, Kd, D = spec.K, spec.Kd, spec.D
    vmax = 1 << spec.value_bits
    lo, hi = (1, 1 << 15) if spec.vocab == "train" else (1 << 15, 1 << 16)
    tracked = _distinct(rng, K, lo, hi)
    used = set(tracked)
    distract: List[int] = []
    if spec.interfere:
        while len(distract) < Kd:
            base = tracked[rng.randbelow(K)] & ~0xF
            cand = base | rng.randbelow(16)
            if cand not in used and lo <= cand < hi:
                used.add(cand); distract.append(cand)
    else:
        while len(distract) < Kd:
            cand = rng.randint(lo, hi - 1)
            if cand not in used:
                used.add(cand); distract.append(cand)
    replace = spec.op_mode == "replace"
    per_tag: Dict[int, List[List[int]]] = {}
    state: Dict[int, int] = {}
    for t in tracked + distract:
        evs = []
        s = None
        for _ in range(D):
            v = rng.randint(0, vmax - 1)
            evs.append([K_PUT, t, v])
            s = v if (s is None or replace) else (s + v) & MASK32
        if t in tracked and spec.retire_rate > 0 and rng.unit() < spec.retire_rate:
            evs.append([K_RETIRE, t])
            s = 0
            if spec.recycle:
                s = None
                for _ in range(D):
                    v = rng.randint(0, vmax - 1)
                    evs.append([K_PUT, t, v])
                    s = v if (s is None or replace) else (s + v) & MASK32
        per_tag[t] = evs
        state[t] = s
    remaining = {t: list(v) for t, v in per_tag.items()}
    order_tags = tracked + distract
    ticks: List[List[int]] = []
    last_tick: Dict[int, int] = {}
    while any(remaining.values()):
        live = [t for t in order_tags if remaining[t]]
        t = live[rng.randbelow(len(live))]
        ticks.append(list(remaining[t].pop(0)))
        last_tick[t] = len(ticks) - 1
    delays = list(spec.delays) or [1]
    asks = []
    asked = _shuffle(rng, list(tracked))
    for t in asked:
        d = delays[rng.randbelow(len(delays))]
        if spec.ask_kind == "ASK2":
            others = [u for u in tracked if u != t]
            u = others[rng.randbelow(len(others))]
            c = rng.randbelow(4)
            pos = max(last_tick[t], last_tick[u]) + d
            asks.append((pos, [K_ASK2, t, u, c], combine(c, state[t], state[u]), [t, u]))
        else:
            asks.append((last_tick[t] + d, [K_ASK, t], state[t], [t]))
    n_base = max(len(ticks), max(a[0] for a in asks))
    asks.sort(key=lambda z: z[0])
    out: List[List[int]] = []
    expected: Dict[int, int] = {}
    ask_done: Dict[int, bool] = {}
    itick_ref = last_tick[asked[0]] + 1
    itick = None
    j = 0
    for i in range(n_base + 1):
        if i == itick_ref:
            itick = len(out)
        while j < len(asks) and asks[j][0] == i:
            out.append(asks[j][1]); expected[len(out) - 1] = asks[j][2]
            ask_done[len(out) - 1] = all(last_tick[u] < itick_ref for u in asks[j][3]); j += 1
        if i < len(ticks):
            out.append(ticks[i])
        elif i < n_base:
            out.append(_noise(rng))
    while j < len(asks):
        out.append(asks[j][1]); expected[len(out) - 1] = asks[j][2]; ask_done[len(out) - 1] = True; j += 1
    if itick is None:
        itick = len(out) - 1
    if spec.noise_rate > 0:
        for tk in out:
            if rng.unit() < spec.noise_rate:
                tk.extend(_noise(rng))
    retired = sorted(ti for ti, w in enumerate(out) if ti in expected and w[0] == K_ASK
                     and any(e[0] == K_RETIRE and e[1] == w[1] for e in per_tag[w[1]]))
    return Episode(ticks=out, expected=expected, intervention_tick=itick,
                   meta={"tags": tracked, "distract": distract, "asked": asked, "K": K, "D": D,
                         "ask_done": ask_done, "retired_asks": retired})


def null_scores(episodes: List[Episode], max_lag: int = 3) -> Dict[str, float]:
    """Payload-reading nulls computed by the harness (DESIGN_v0.2 s3): CONST0; ECHO of word
    position j of tick t-k for k in 0..max_lag (max over j reported per k); ECHO_FIRST (word j
    of tick 0). A world where any of these is high leaks its answer."""
    tot = 0
    const0 = 0
    first: Dict[int, int] = {}
    echo: Dict[Tuple[int, int], int] = {}
    for ep in episodes:
        for ti, exp in ep.expected.items():
            tot += 1
            const0 += 1 if exp == 0 else 0
            for j, w in enumerate(ep.ticks[0][:8]):
                first[j] = first.get(j, 0) + (1 if w == exp else 0)
            for k in range(0, max_lag + 1):
                if ti - k < 0:
                    continue
                for j, w in enumerate(ep.ticks[ti - k][:8]):
                    echo[(k, j)] = echo.get((k, j), 0) + (1 if w == exp else 0)
    n = max(1, tot)
    out = {"CONST0": const0 / n, "ECHO_FIRST": max(first.values(), default=0) / n}
    for k in range(0, max_lag + 1):
        out["ECHO_PREV_%d" % k] = max((v for (kk, _), v in echo.items() if kk == k), default=0) / n
    return out


def episodes_for(spec: WorldSpec, campaign_seed: int, family: str, index: int, n: int) -> List[Episode]:
    """n episodes from the (campaign_seed, world, family, index) stream; families separate
    training, held-out and intervention draws so no held-out episode is ever a training one."""
    root = SplitMix64(seed_from("wse.episodes.v0", campaign_seed, spec.world_id(), family, index))
    return [make_episode(spec, root.derive("episode", i)) for i in range(n)]


def erase_ceiling(episodes: List[Episode]) -> float:
    """Share of asks whose every dependency was complete before the intervention tick: the
    largest reward drop an erase-type intervention could produce on a fully state-dependent
    solver. Reported beside every intervention vector (attainable range before the gate)."""
    tot = done = 0
    for ep in episodes:
        for ti in ep.expected:
            tot += 1
            done += 1 if ep.meta.get("ask_done", {}).get(ti, False) else 0
    return done / max(1, tot)


def with_knobs(spec: WorldSpec, **changes) -> WorldSpec:
    d = asdict(spec)
    d.update(changes)
    return WorldSpec(**d)
