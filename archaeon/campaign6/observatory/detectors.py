"""The eleven detectors (DETECTORS_v0.1.md), v0-profile implementations. Each is a pure function of a
Subject and a Context and returns a detector verdict (archaeon.c6.detector.v1): FIRE / QUIET /
UNABLE with score, threshold, evidence. UNABLE is returned whenever an input the definition needs
is absent; it is never silently QUIET. Thresholds come from the frozen table passed in the
Context; the code never chooses one.

Subject: {organism_id, manifest, pair=(t0, ext), parent: Subject|None, generation}
Context: thresholds (dict name -> value), spread, library (list of pairs), population (list of
Subjects), ancestors(subject, depth) -> list[Subject], siblings(subject) -> list[Subject],
probe(subject) -> {env: reward} | None, home_reward(subject) -> float|None, band, regime_events
(list of lt), replay_D(subject) -> {reproduced: bool}|None, ablation(subject) -> list[{node,
delta, dormant_in_ancestors}]|None, world_state -> {persistent: bool, resources: int,
persisted_reads(subject) -> int}.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

from proteus.foundry.grammar import static_reachable

from ..c6base import DETECTORS
from ..schemas import detector_verdict
from .fingerprint import fp_distance
from archaeon.campaign6.substrate import struct_distance_any as struct_distance


class Subject:
    __slots__ = ("organism_id", "manifest", "pair", "parent", "generation", "meta")

    def __init__(self, organism_id, manifest, pair, parent=None, generation=0, meta=None):
        self.organism_id, self.manifest, self.pair, self.parent, self.generation = organism_id, manifest, pair, parent, generation
        self.meta = meta or {}


class Context:
    def __init__(self, thresholds: Dict[str, float], spread: Dict[str, float], *, library=None, population=None, ancestors=None, siblings=None,
                 probe=None, home_reward=None, band=1 / 16, regime_events=None, replay_D=None, ablation=None, world_state=None, pop_median_drop=None):
        self.thresholds, self.spread = thresholds, spread
        self.library = library or []
        self.population = population or []
        self.ancestors = ancestors or (lambda s, depth: [])
        self.siblings = siblings or (lambda s: [])
        self.probe = probe or (lambda s: None)
        self.home_reward = home_reward or (lambda s: None)
        self.band = band
        self.regime_events = regime_events or []
        self.replay_D = replay_D or (lambda s: None)
        self.ablation = ablation or (lambda s: None)
        self.world_state = world_state or {"persistent": False, "resources": 1, "persisted_reads": (lambda s: 0)}
        self.pop_median_drop = pop_median_drop or (lambda s, lt: None)

    def t(self, name: str) -> Optional[float]:
        return self.thresholds.get(name)


def _v(name, outcome, score, thr, evidence, subj: Subject):
    return detector_verdict(name, outcome, score, thr, {**evidence, "subject": {"organism_id": subj.organism_id, "generation": subj.generation}})


# 1 ------------------------------------------------------------------------------------------------
def behavioral_novelty(s: Subject, c: Context) -> dict:
    name = "behavioral_novelty"; thr = c.t(name)
    pool = [x.pair for x in c.ancestors(s, 8)] + [x.pair for x in c.siblings(s)] + [x.pair for x in c.population if x.organism_id != s.organism_id] + list(c.library)
    if not pool or thr is None:
        return _v(name, "UNABLE", None, thr, {"reason": "empty comparison pool" if not pool else "no threshold"}, s)
    d = min(fp_distance(s.pair, p, c.spread) for p in pool)
    return _v(name, "FIRE" if d > thr else "QUIET", d, thr, {"nearest_distance": d, "pool_n": len(pool)}, s)


# 2 ------------------------------------------------------------------------------------------------
def lineage_discontinuity(s: Subject, c: Context) -> dict:
    name = "lineage_discontinuity"; thr = c.t(name); s_max = c.thresholds.get("lineage_discontinuity.struct_max", 0.25)
    if s.parent is None or thr is None:
        return _v(name, "UNABLE", None, thr, {"reason": "no parent"}, s)
    sd = struct_distance(s.manifest, s.parent.manifest)
    if sd > s_max:
        return _v(name, "QUIET", None, thr, {"reason": "structural edit not small", "struct_distance": sd, "struct_max": s_max}, s)
    d = fp_distance(s.pair, s.parent.pair, c.spread)
    return _v(name, "FIRE" if d > thr else "QUIET", d, thr, {"behaviour_distance": d, "struct_distance": sd}, s)


# 3 ------------------------------------------------------------------------------------------------
def unexpected_transfer(s: Subject, c: Context) -> dict:
    name = "unexpected_transfer"; thr = c.t(name)
    pr = c.probe(s); home = c.home_reward(s)
    if not pr or home is None or s.parent is None:
        return _v(name, "UNABLE", None, thr, {"reason": "no probe worlds or no parent"}, s)
    ppr = c.probe(s.parent); phome = c.home_reward(s.parent)
    if not ppr or phome is None:
        return _v(name, "UNABLE", None, thr, {"reason": "parent has no probe readings"}, s)
    floor = c.thresholds.get("unexpected_transfer.floor", 3 / 16)
    gains = {e: round(pr[e] - ppr.get(e, 0.0), 4) for e in pr}
    # a transfer = a gain of at least a band on a world the lineage never saw AND competence there (the C4 floor), home unmoved
    eligible = {e: g for e, g in gains.items() if g >= c.band and pr[e] >= floor}
    best = max(gains.values()) if gains else 0.0
    home_moved = abs(home - phome) > c.band
    fire = bool(eligible) and not home_moved
    return _v(name, "FIRE" if fire else "QUIET", best, c.band, {"gains": gains, "eligible": eligible, "floor": floor, "home_delta": round(home - phome, 4), "home_moved": home_moved}, s)


# 4 ------------------------------------------------------------------------------------------------
def structural_reuse(s: Subject, c: Context) -> dict:
    """v0 profile: a 4-word instruction block that appears >= 2 times with every copy statically reachable."""
    name = "structural_reuse"; thr = c.t(name) or 2
    if "genome" not in s.manifest:
        # graph profile: a node kind+params signature executed at >= 2 sites is reuse only when the meter says both ran; until the
        # per-node execution counts are read from the fingerprint, report UNABLE (C6_GEOMETRY stage owns this detector)
        return _v(name, "UNABLE", None, thr, {"reason": "graph profile: component reuse needs node execution counts (C6_GEOMETRY stage)"}, s)
    g = s.manifest["genome"]; n = len(g) // 4
    if n < 2:
        return _v(name, "UNABLE", None, thr, {"reason": "genome too short"}, s)
    reach = static_reachable(g, s.manifest["tape_words"])
    blocks = {}
    for i in range(n):
        blocks.setdefault(tuple(g[i * 4:i * 4 + 4]), []).append(i)
    reused = [(b, idx) for b, idx in blocks.items() if len(idx) >= 2 and all(i in reach for i in idx) and b[0] % 25 not in (0,)]
    k = max((len(idx) for _, idx in reused), default=0)
    return _v(name, "FIRE" if k >= thr else "QUIET", k, thr, {"reused_blocks": len(reused), "max_copies": k}, s)


# 5 ------------------------------------------------------------------------------------------------
def environmental_modification(s: Subject, c: Context) -> dict:
    name = "environmental_modification"; thr = c.t(name)
    if not c.world_state.get("persistent") or thr is None:
        return _v(name, "UNABLE", None, thr, {"reason": "world has no persistent state"}, s)
    k = c.world_state["persisted_reads"](s)
    return _v(name, "FIRE" if k > thr else "QUIET", k, thr, {"persisted_and_read": k}, s)


# 6 ------------------------------------------------------------------------------------------------
def niche_divergence(s: Subject, c: Context) -> dict:
    name = "niche_divergence"; thr = c.t(name)
    if c.world_state.get("resources", 1) < 2 or len(c.population) < 2 or thr is None:
        return _v(name, "UNABLE", None, thr, {"reason": "fewer than two resource types or one lineage"}, s)
    mine = set(s.pair[1]["resources_touched"]) | set(s.pair[1]["env_dependencies"])
    js = []
    for x in c.population:
        if x.organism_id == s.organism_id:
            continue
        other = set(x.pair[1]["resources_touched"]) | set(x.pair[1]["env_dependencies"])
        js.append(len(mine & other) / max(1, len(mine | other)))
    jmin = min(js) if js else 1.0
    return _v(name, "FIRE" if jmin < thr else "QUIET", jmin, thr, {"min_jaccard": jmin}, s)


# 7 ------------------------------------------------------------------------------------------------
def regime_persistence(s: Subject, c: Context) -> dict:
    name = "regime_persistence"; thr = c.t(name)
    if not c.regime_events:
        return _v(name, "UNABLE", None, thr, {"reason": "no regime change yet"}, s)
    lt = max(e for e in c.regime_events if e <= s.generation) if any(e <= s.generation for e in c.regime_events) else None
    if lt is None or s.parent is None:
        return _v(name, "UNABLE", None, thr, {"reason": "no regime change before this subject"}, s)
    home, phome = c.home_reward(s), c.home_reward(s.parent)
    drop = c.pop_median_drop(s, lt)
    if home is None or phome is None or drop is None:
        return _v(name, "UNABLE", None, thr, {"reason": "no rewards around the regime change"}, s)
    fire = abs(home - phome) <= c.band and drop >= c.band
    return _v(name, "FIRE" if fire else "QUIET", drop, c.band, {"lineage_delta": round(home - phome, 4), "population_median_drop": drop, "regime_lt": lt}, s)


# 8 ------------------------------------------------------------------------------------------------
def unexplained_gain(s: Subject, c: Context) -> dict:
    name = "unexplained_gain"; thr = c.t(name); s_max = c.thresholds.get("unexplained_gain.struct_max", 0.25)
    if s.parent is None:
        return _v(name, "UNABLE", None, thr, {"reason": "no parent"}, s)
    home, phome = c.home_reward(s), c.home_reward(s.parent)
    if home is None or phome is None:
        return _v(name, "UNABLE", None, thr, {"reason": "no rewards"}, s)
    gain = home - phome
    if gain < c.band or struct_distance(s.manifest, s.parent.manifest) > s_max:
        return _v(name, "QUIET", gain, c.band, {"gain": round(gain, 4), "reason": "no small-edit gain"}, s)
    rd = c.replay_D(s)
    if rd is None:
        return _v(name, "UNABLE", gain, c.band, {"reason": "mutation rollback (replay D) not yet run", "gain": round(gain, 4)}, s)
    return _v(name, "FIRE" if rd.get("reproduced") else "QUIET", gain, c.band, {"gain": round(gain, 4), "rollback_reproduced_gain": rd.get("reproduced")}, s)


# 9 ------------------------------------------------------------------------------------------------
def unexpected_causal_dependence(s: Subject, c: Context) -> dict:
    name = "unexpected_causal_dependence"; thr = c.t(name)
    ab = c.ablation(s)
    if ab is None:
        return _v(name, "UNABLE", None, thr, {"reason": "no ablation set"}, s)
    hits = [x for x in ab if x.get("dormant_in_ancestors") and abs(x.get("delta", 0.0)) >= c.band]
    return _v(name, "FIRE" if hits else "QUIET", len(hits), c.band, {"dormant_causal_nodes": [x.get("node") for x in hits][:8], "ablated": len(ab)}, s)


# 10 -----------------------------------------------------------------------------------------------
def detector_disagreement(verdicts: List[dict], s: Subject, c: Context) -> dict:
    name = "detector_disagreement"
    able = [v for v in verdicts if v["outcome"] != "UNABLE" and v["detector"] not in ("detector_disagreement", "classifier_failure")]
    fired = [v["detector"] for v in able if v["outcome"] == "FIRE"]; quiet = [v["detector"] for v in able if v["outcome"] == "QUIET"]
    fire = len(fired) >= 1 and len(quiet) >= 2
    return _v(name, "FIRE" if fire else "QUIET", len(fired), 1, {"fired": fired, "quiet": quiet, "able": len(able)}, s)


# 11 -----------------------------------------------------------------------------------------------
def classifier_failure(verdicts: List[dict], s: Subject, c: Context, classification: Optional[str] = None) -> dict:
    name = "classifier_failure"
    core = [v for v in verdicts if v["detector"] not in ("detector_disagreement", "classifier_failure")]
    unable = [v["detector"] for v in core if v["outcome"] == "UNABLE"]; fired = [v["detector"] for v in core if v["outcome"] == "FIRE"]
    none_of_the_above = classification is not None and classification in ("NONE_OF_THE_ABOVE", "UNKNOWN_MECHANISM")
    blind = len(unable) >= 3 and len(fired) >= 1
    fire = none_of_the_above or blind
    return _v(name, "FIRE" if fire else "QUIET", len(unable), 3, {"unable": unable, "fired": fired, "classification": classification, "blind": blind}, s)


IN_LOOP = {"behavioral_novelty": behavioral_novelty, "lineage_discontinuity": lineage_discontinuity, "unexpected_transfer": unexpected_transfer,
           "structural_reuse": structural_reuse, "environmental_modification": environmental_modification, "niche_divergence": niche_divergence,
           "regime_persistence": regime_persistence, "unexplained_gain": unexplained_gain, "unexpected_causal_dependence": unexpected_causal_dependence}
assert set(IN_LOOP) | {"detector_disagreement", "classifier_failure"} == set(DETECTORS)


def run_all(s: Subject, c: Context, classification: Optional[str] = None) -> List[dict]:
    vs = [fn(s, c) for fn in IN_LOOP.values()]
    vs.append(detector_disagreement(vs, s, c))
    vs.append(classifier_failure(vs, s, c, classification))
    return vs
