"""Reference observers and objectives. Observers MEASURE (directive s15): counts, sums, descriptors, with
their version in every receipt. Objectives EVALUATE a receipt-like dict into a value plus components;
they read and never write. Neither declares meaning.

  observer.trace.v1       per-player event counts by kind, yield/charge totals, actions total, ticks
  observer.descriptor.v1  a small integer behaviour descriptor: [abstain_rate_bucket, action_mag_bucket, yield_bucket]
  objective.yield_net.v1  value = sum(yield gained) - sum(penalty_weights[k] * accounting[k]); penalties declared
  objective.survival.v1   value = ticks alive summed over players
"""
from __future__ import annotations

from typing import Any, Dict, List

from prometheus.toolbox.contracts import EVENT_ID, EVENT_KINDS, Event


class TraceObserver:
    kind = "observer.trace.v1"
    version = "1"

    def __init__(self):
        self._by_kind: Dict[str, int] = {}
        self._yield: Dict[int, int] = {}
        self._actions: Dict[int, int] = {}
        self._abstain: Dict[int, int] = {}
        self._ticks = 0
        self._n_players = 0

    def manifest(self) -> dict:
        return {"kind": self.kind, "version": self.version}

    def begin(self, ctx: dict) -> None:
        self._n_players = ctx.get("n_players", 1)

    def on_tick(self, tick: int, observations: Dict[int, List[int]], actions: Dict[int, List[int]]) -> None:
        self._ticks = tick + 1
        for pid, a in actions.items():
            mag = sum(a)
            self._actions[pid] = self._actions.get(pid, 0) + mag
            if mag == 0:
                self._abstain[pid] = self._abstain.get(pid, 0) + 1

    def on_events(self, events: List[Event]) -> None:
        for (_, kind, pid, _, val) in events:
            name = EVENT_KINDS[kind] if 0 <= kind < len(EVENT_KINDS) else "UNKNOWN_%d" % kind     # C17: retain, never crash or drop
            self._by_kind[name] = self._by_kind.get(name, 0) + 1
            if kind == EVENT_ID["YIELD"]:
                self._yield[pid] = self._yield.get(pid, 0) + val

    def measure(self) -> Dict[str, Any]:
        return {"ticks": self._ticks, "events_by_kind": dict(sorted(self._by_kind.items())),
                "yield_by_player": {str(k): v for k, v in sorted(self._yield.items())},
                "actions_by_player": {str(k): v for k, v in sorted(self._actions.items())},
                "abstain_by_player": {str(k): v for k, v in sorted(self._abstain.items())},
                "yield_total": sum(self._yield.values()), "actions_total": sum(self._actions.values())}

    def describe(self) -> List[int]:
        return []

    # C37: observers that can be checkpointed expose snapshot/restore of their counters
    def snapshot(self) -> bytes:
        import json
        return json.dumps({"k": self._by_kind, "y": self._yield, "a": self._actions, "ab": self._abstain, "t": self._ticks, "n": self._n_players,
                           "ep": getattr(self, "_ep_yield", 0), "al": getattr(self, "_alive", 0), "s": getattr(self, "_series", [])}).encode()

    def restore(self, snapshot: bytes) -> None:
        import json
        d = json.loads(snapshot.decode())
        self._by_kind = d["k"]; self._yield = {int(k): v for k, v in d["y"].items()}; self._actions = {int(k): v for k, v in d["a"].items()}
        self._abstain = {int(k): v for k, v in d["ab"].items()}; self._ticks = d["t"]; self._n_players = d["n"]
        if hasattr(self, "_series"):
            self._ep_yield = d["ep"]; self._alive = d["al"]; self._series = [list(r) for r in d["s"]]


class DescriptorObserver(TraceObserver):
    """[abstain_rate_bucket 0-8, action_magnitude_bucket 0-7, yield_bucket 0-7]. The scales are PARAMETERS
    (C27: with the defaults the magnitude and yield buckets saturated at 7 on the integer world, collapsing a
    MAP-Elites archive to 4 cells); a designer calibrates them to the world's ranges."""
    kind = "observer.descriptor.v1"
    version = "2"

    def __init__(self, action_scale: int = 1, yield_scale: int = 8):
        super().__init__(); self.action_scale = max(1, int(action_scale)); self.yield_scale = max(1, int(yield_scale))

    def manifest(self) -> dict:
        return {"kind": self.kind, "version": self.version, "action_scale": self.action_scale, "yield_scale": self.yield_scale}

    def describe(self) -> List[int]:
        t = max(1, self._ticks); n = max(1, self._n_players)
        abst = sum(self._abstain.values()) * 8 // (t * n)
        mag = min(7, sum(self._actions.values()) // (t * n * self.action_scale))
        yb = min(7, sum(self._yield.values()) // self.yield_scale)
        return [abst, mag, yb]

    def measure(self) -> Dict[str, Any]:
        m = super().measure(); m["descriptor"] = self.describe(); return m


class YieldNetObjective:
    kind = "objective.yield_net.v1"
    version = "1"

    def __init__(self, penalties: Dict[str, float] | None = None):
        self.penalties = dict(penalties or {})

    def manifest(self) -> dict:
        return {"kind": self.kind, "version": self.version, "penalties": self.penalties}

    def evaluate(self, receipt: dict) -> Dict[str, Any]:
        sci = receipt.get("science", {}); acc = receipt.get("accounting", {})
        y = 0
        for obs in sci.get("observations", {}).values():
            y = max(y, int(obs.get("yield_total", 0)))
        pen = {k: w * float(acc.get(k, 0)) for k, w in self.penalties.items()}
        unknown = sorted(k for k in self.penalties if k not in acc)      # C49: a penalty on a key that never appears is reported, never a silent zero
        return {"value": y - sum(pen.values()), "components": {"yield_total": y, "penalties": pen, "unknown_penalty_keys": unknown}}


class MultiObjective:
    """objective.multi.v1 (C94): NAMED COMPONENTS, each an ordinary objective ref; value is {name: number|None}. The
    kernel assumes nothing scalar: split summaries report per-component means, search rows carry the dict and a
    selector ranks by a named component or refuses."""
    kind = "objective.multi.v1"
    version = "1"

    def __init__(self, components: Dict[str, dict] | None = None):
        if not components or not isinstance(components, dict):
            raise ValueError("objective.multi.v1 needs components={name: objective ref, ...}")
        self.components = {k: dict(v) for k, v in components.items()}

    def manifest(self) -> dict:
        return {"kind": self.kind, "version": self.version, "components": self.components}

    def evaluate(self, receipt: dict) -> Dict[str, Any]:
        from prometheus.toolbox.registry import default_registry
        reg = default_registry(); value = {}; parts = {}
        for name, r in self.components.items():
            obj = reg.make(r["kind"], **r.get("params", {}))
            res = obj.evaluate(receipt); value[name] = res.get("value"); parts[name] = dict(res, kind=obj.kind, version=getattr(obj, "version", None))
        return {"value": value, "components": parts}


class SurvivalObjective:
    kind = "objective.survival.v1"
    version = "1"

    def manifest(self) -> dict:
        return {"kind": self.kind, "version": self.version}

    def evaluate(self, receipt: dict) -> Dict[str, Any]:
        s = receipt.get("science", {}).get("world_summary", {})
        alive = s.get("alive", []); ticks = s.get("ticks", 0)
        return {"value": ticks * sum(1 for a in alive if a), "components": {"ticks": ticks, "alive": alive}}


# ------------------------------------------------------------------------------------------ series (U3)
LAST_MIRROR = None      # test hook: the last StateDevice a SeriesObserver mirrored into (so a test can destroy it)


class SeriesObserver(TraceObserver):
    """observer.series.v1: per tick [tick, actions_sum, yield_cumulative, alive_count] for the current episode.
    Declares `series`; `enabled=False` records a DISABLED series (distinct from EMPTY). `mirror_device`
    names a StateDevice kind to mirror records into during the run -- the mirror is a cache, never the copy
    of record (U3)."""
    kind = "observer.series.v1"
    version = "1"
    series = True

    def __init__(self, enabled: bool = True, mirror_device: str | None = None, per_player: bool = False):
        super().__init__()
        self.enabled = bool(enabled); self.mirror_device = mirror_device; self.per_player = bool(per_player)
        self._series: List[List[int]] = []
        self._alive = 0; self._alive_by: Dict[int, bool] = {}; self._ep_yield_by: Dict[int, int] = {}
        self._dev = None
        if mirror_device == "inprocess":
            from prometheus.toolbox import state as ST
            global LAST_MIRROR
            self._dev = ST.InProcessStateDevice(); LAST_MIRROR = self._dev

    def manifest(self) -> dict:
        return {"kind": self.kind, "version": self.version, "series": True, "enabled": self.enabled, "mirror_device": self.mirror_device,
                "per_player": self.per_player, "columns": self.series_columns()}

    def series_columns(self) -> List[str]:
        """C53: records self-describe. Aggregate columns first; with per_player, three columns per player follow."""
        cols = ["tick", "actions_sum", "yield_cum", "alive"]
        if self.per_player:
            for pid in range(self._n_players):
                cols += ["p%d_actions" % pid, "p%d_yield_cum" % pid, "p%d_alive" % pid]
        return cols

    def begin(self, ctx: dict) -> None:
        super().begin(ctx); self._series = []; self._alive = self._n_players; self._ep_yield = 0   # per-EPISODE counters (C21)
        self._alive_by = {pid: True for pid in range(self._n_players)}; self._ep_yield_by = {pid: 0 for pid in range(self._n_players)}
        if self._dev is not None:
            self._dev.end_scope("episode")

    def on_events(self, events: List[Event]) -> None:
        super().on_events(events)
        for (_, kind, pid, _, val) in events:
            if kind == EVENT_ID["ABSORBED"]:
                self._alive -= 1; self._alive_by[pid] = False
            elif kind == EVENT_ID["YIELD"]:
                self._ep_yield += val; self._ep_yield_by[pid] = self._ep_yield_by.get(pid, 0) + val

    def on_tick(self, tick: int, observations: Dict[int, List[int]], actions: Dict[int, List[int]]) -> None:
        super().on_tick(tick, observations, actions)
        if not self.enabled:
            return
        rec = [tick, sum(sum(a) for a in actions.values()), self._ep_yield, self._alive]     # col 2: yield within THIS episode
        if self.per_player:
            for pid in range(self._n_players):
                rec += [sum(actions.get(pid, [])), self._ep_yield_by.get(pid, 0), 1 if self._alive_by.get(pid, False) else 0]
        self._series.append(rec)
        if self._dev is not None:
            self._dev.advance(tick); self._dev.append("series", rec, scope="persistent")

    def series_episode(self) -> List[List[int]]:
        return list(self._series)


class SurvivalTicksObjective:
    """objective.survival.v2 (C96, playtest H): v1 (ticks x players alive at the end) is a STEP -- 0 for every player
    that dies before the horizon, whatever it survived, so it cannot rank a dying population (every elite of pt_h
    read life=0). v2 values the ticks the last episode lasted: the death tick when everyone died, the horizon
    otherwise; alive count is a component. v1 stays as it was (its receipts are what they are)."""
    kind = "objective.survival.v2"
    version = "2"

    def manifest(self) -> dict:
        return {"kind": self.kind, "version": self.version}

    def evaluate(self, receipt: dict) -> Dict[str, Any]:
        s = receipt.get("science", {}).get("world_summary", {})
        alive = s.get("alive", []); ticks = s.get("ticks", 0)
        return {"value": ticks, "components": {"ticks": ticks, "alive": alive, "n_alive": sum(1 for a in alive if a)}}


class SeriesGainObjective:
    """objective.series_gain.v1 (C13): yield reached in the LAST episode minus yield reached in the FIRST, read
    from observer.series.v1's records (column 2 = cumulative yield). The experience-to-competence shape.
    None -- never a fabricated 0 -- when the series is missing or disabled."""
    kind = "objective.series_gain.v1"
    version = "1"

    def manifest(self) -> dict:
        return {"kind": self.kind, "version": self.version, "reads": "observer.series.v1"}

    def evaluate(self, receipt: dict) -> Dict[str, Any]:
        s = (receipt.get("series") or {}).get("observer.series.v1")
        if s is None:
            return {"value": None, "components": {"reason": "SERIES_MISSING"}}
        if s["status"] == "DISABLED":
            return {"value": None, "components": {"reason": "SERIES_DISABLED"}}
        eps = (receipt.get("_series_episodes") or {}).get("observer.series.v1") or s.get("inline")
        if not eps or not eps[0] or not eps[-1]:
            return {"value": None, "components": {"reason": "SERIES_EMPTY", "episodes": len(eps or [])}}
        cols = s.get("columns") or ["tick", "actions_sum", "yield_cum", "alive"]
        if "yield_cum" not in cols:
            return {"value": None, "components": {"reason": "SERIES_HAS_NO_COLUMN:yield_cum", "columns": cols}}
        c = cols.index("yield_cum")                              # C53: by NAME, never by habit
        first, last = eps[0][-1][c], eps[-1][-1][c]
        return {"value": last - first, "components": {"column": "yield_cum", "first_episode_yield": first, "last_episode_yield": last, "episodes": len(eps),
                                                      "per_episode_yield": [ep[-1][c] if ep else None for ep in eps]}}
