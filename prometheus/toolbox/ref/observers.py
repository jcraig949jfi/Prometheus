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


class DescriptorObserver(TraceObserver):
    kind = "observer.descriptor.v1"
    version = "1"

    def describe(self) -> List[int]:
        t = max(1, self._ticks); n = max(1, self._n_players)
        abst = sum(self._abstain.values()) * 8 // (t * n)
        mag = min(7, sum(self._actions.values()) // (t * n))
        yb = min(7, sum(self._yield.values()) // 8)
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
        return {"value": y - sum(pen.values()), "components": {"yield_total": y, "penalties": pen}}


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

    def __init__(self, enabled: bool = True, mirror_device: str | None = None):
        super().__init__()
        self.enabled = bool(enabled); self.mirror_device = mirror_device
        self._series: List[List[int]] = []
        self._alive = 0
        self._dev = None
        if mirror_device == "inprocess":
            from prometheus.toolbox import state as ST
            global LAST_MIRROR
            self._dev = ST.InProcessStateDevice(); LAST_MIRROR = self._dev

    def manifest(self) -> dict:
        return {"kind": self.kind, "version": self.version, "series": True, "enabled": self.enabled, "mirror_device": self.mirror_device}

    def begin(self, ctx: dict) -> None:
        super().begin(ctx); self._series = []; self._alive = self._n_players
        if self._dev is not None:
            self._dev.end_scope("episode")

    def on_events(self, events: List[Event]) -> None:
        super().on_events(events)
        for (_, kind, _, _, _) in events:
            if kind == EVENT_ID["ABSORBED"]:
                self._alive -= 1

    def on_tick(self, tick: int, observations: Dict[int, List[int]], actions: Dict[int, List[int]]) -> None:
        super().on_tick(tick, observations, actions)
        if not self.enabled:
            return
        rec = [tick, sum(sum(a) for a in actions.values()), sum(self._yield.values()), self._alive]
        self._series.append(rec)
        if self._dev is not None:
            self._dev.advance(tick); self._dev.append("series", rec, scope="persistent")

    def series_episode(self) -> List[List[int]]:
        return list(self._series)
