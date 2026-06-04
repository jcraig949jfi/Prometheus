"""Arachne swarm — the population that evolves crawlers independently.

Fitness is James's three factors: (1) don't die, (2) expand connectivity,
(3) branch near death. The population is the organism; lineage is a tree of
life. The fabric persists fully on disk (fabric/edges.jsonl), so stopping and
restarting the loop never loses woven structure — Aporia can adjust a crawler's
ruleset between restarts.

CLI:
  python -m agents.arachne.swarm --once
  python -m agents.arachne.swarm --loop --interval 5 --max-ticks 200
  python -m agents.arachne.swarm status
  python -m agents.arachne.swarm revive --landscape mathlib
  python -m agents.arachne.swarm tweak --id mathlib-0-1 --novelty-floor 0.7
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

_THIS = Path(__file__).resolve()
REPO = _THIS.parents[2]
for p in (REPO, REPO / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from agents.arachne.fabric import Fabric
from agents.arachne.crawler import Crawler, Ruleset
from agents.arachne.landscapes import build_landscapes
from agents.arachne.join import JoinWeaver
from agents.arachne.operational import OperationalJoiner

AGENT_DIR = _THIS.parent
STATE_DIR = AGENT_DIR / "state"
FABRIC_DIR = AGENT_DIR / "fabric"
STATE_DIR.mkdir(parents=True, exist_ok=True)
POP_FILE = STATE_DIR / "population.json"
SWARM_STATE = STATE_DIR / "swarm_state.json"
LINEAGE_LOG = STATE_DIR / "lineage.jsonl"
OVERRIDES = STATE_DIR / "overrides.json"

POP_CAP = 12
POP_HARD_CAP = 16          # floor revivals may exceed POP_CAP up to here
BRANCH_FITNESS = 0.6
BRANCH_PATIENCE = 4
BRANCH_COOLDOWN = 10
JOIN_EVERY = 3             # run the rosetta cross-landscape weaver every N ticks

# The five founding rulesets (James's 5 crawlers).
def founding_rulesets() -> list[Ruleset]:
    return [
        Ruleset(landscape="mathlib", max_neighbors=8, novelty_floor=0.92, seed=101),
        Ruleset(landscape="lmfdb",   max_neighbors=6, novelty_floor=0.85, seed=202),
        Ruleset(landscape="algolib", max_neighbors=8, novelty_floor=0.90, seed=303),
        Ruleset(landscape="oeis",    max_neighbors=6, novelty_floor=0.80, seed=404),
        # feral: minimal-rule generalist, hops landscapes — the "fewer rules" test
        Ruleset(landscape="feral",   max_neighbors=12, novelty_floor=0.97, hop=True,
                frontier_mode="random", seed=505),
    ]


class Swarm:
    def __init__(self):
        self.landscapes = build_landscapes()
        self.fabric = Fabric(FABRIC_DIR)
        self.weaver = JoinWeaver(oeis_adapter=self.landscapes.get("oeis"))
        self.opjoiner = OperationalJoiner(oeis_adapter=self.landscapes.get("oeis"))
        self.crawlers: list[Crawler] = []
        self.graveyard: list[dict] = []
        self.tick = 0
        self._id_counter = 0
        self._low_streak: dict[str, int] = {}
        self._branch_cooldown: dict[str, int] = {}

    # -- lifecycle ------------------------------------------------------------
    def _new_id(self, landscape: str, gen: int) -> str:
        self._id_counter += 1
        return f"{landscape}-{gen}-{self._id_counter}"

    def _feral_landscape(self) -> str:
        # feral needs a concrete starting landscape (it hops thereafter)
        return next(iter(self.landscapes), "mathlib")

    def seed_population(self) -> None:
        for rs in founding_rulesets():
            ls = rs.landscape
            if ls == "feral":
                if not self.landscapes:
                    continue
                rs.landscape = self._feral_landscape()
            elif ls not in self.landscapes:
                # landscape unreachable — spawn anyway; it will starve and its
                # child can mutate to a live landscape (evolution escaping death)
                pass
            cid = self._new_id(ls if ls != "feral" else "feral", 0)
            self.crawlers.append(Crawler(cid, rs))

    def _lineage(self, event: str, **kw) -> None:
        rec = {"at": datetime.now(timezone.utc).isoformat(), "event": event,
               "tick": self.tick, **kw}
        with LINEAGE_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def _branch(self, parent: Crawler) -> None:
        import random
        rng = random.Random(parent.rng.randint(1, 10_000_000))
        child_rs = parent.ruleset.mutate(rng)
        # Near-death branching should EXPLORE NEW LINKAGES (James's factor 3), not
        # re-enter the cliff. 70% of the time the child escapes to the
        # least-populated live landscape — this load-balances away from a
        # struggling landscape that would otherwise monopolize reproduction
        # (its low fitness is exactly what triggers branching).
        if self.landscapes and rng.random() < 0.70:
            counts = {n: 0 for n in self.landscapes}
            for c in self.crawlers:
                if c.alive and c.ruleset.landscape in counts:
                    counts[c.ruleset.landscape] += 1
            target = min(counts, key=lambda n: (counts[n], rng.random()))
            child_rs.landscape = target
            child_rs.hop = False
        cid = self._new_id(child_rs.landscape, parent.generation + 1)
        child = Crawler(cid, child_rs, parent=parent.id, generation=parent.generation + 1)
        self.crawlers.append(child)
        self._branch_cooldown[parent.id] = BRANCH_COOLDOWN
        self._lineage("branch", parent=parent.id, child=cid,
                      parent_fitness=round(parent.fitness(), 3),
                      child_ruleset=child.snapshot()["ruleset"])

    # -- one tick over the whole population -----------------------------------
    def step_all(self) -> dict:
        self.tick += 1
        self._apply_overrides()
        per = []
        for c in list(self.crawlers):
            if not c.alive:
                continue
            r = c.step(self.fabric, self.landscapes)
            per.append({"id": c.id, **{k: r.get(k) for k in
                        ("action", "landscape", "new_edges", "looping", "fitness")}})
            # decrement cooldown
            if self._branch_cooldown.get(c.id, 0) > 0:
                self._branch_cooldown[c.id] -= 1
            # branch-near-death tracking
            if c.alive and c.fitness() < BRANCH_FITNESS:
                self._low_streak[c.id] = self._low_streak.get(c.id, 0) + 1
            else:
                self._low_streak[c.id] = 0
            if (c.alive and self._low_streak.get(c.id, 0) >= BRANCH_PATIENCE
                    and self._alive_count() < POP_CAP
                    and self._branch_cooldown.get(c.id, 0) == 0):
                self._branch(c)
                self._low_streak[c.id] = 0

        # reap the dead
        for c in list(self.crawlers):
            if not c.alive:
                snap = c.snapshot()
                self.graveyard.append(snap)
                self._lineage("death", id=c.id, reason=c.death_reason,
                              total_edges=c.total_edges, generation=c.generation)
                self.crawlers.remove(c)

        # per-landscape population floor: no landscape may go extinct. This is
        # the fix for the monoculture collapse — connectivity-fitness alone drives
        # the population onto the highest-fanout landscape (oeis) and the rest die.
        for ls in self.landscapes:
            if self._alive_count() >= POP_HARD_CAP:
                break
            if not any(c.alive and c.ruleset.landscape == ls for c in self.crawlers):
                rs = next((r for r in founding_rulesets() if r.landscape == ls), None)
                rs = Ruleset(**rs.__dict__) if rs else Ruleset(landscape=ls)
                cid = self._new_id(ls, 0)
                self.crawlers.append(Crawler(cid, rs))
                self._lineage("floor_revive", id=cid, landscape=ls)

        # extinction resilience
        if self._alive_count() == 0:
            self._lineage("extinction_respawn")
            self.seed_population()

        # rosetta cross-landscape join — weave the separate webs into one tapestry
        join_delta = None
        if self.tick % JOIN_EVERY == 0:
            import random as _r
            join_delta = self.weaver.weave(self.fabric, _r.Random(self.tick), max_edges=40)
            if join_delta["new_edges"]:
                self._lineage("rosetta_weave", new_edges=join_delta["new_edges"])
        # operational join — computation-grounded edges (finite, runs until exhausted)
        if self.tick % 5 == 0 and not self.opjoiner.exhausted():
            import random as _r
            od = self.opjoiner.weave(self.fabric, _r.Random(self.tick + 7), batch=4)
            if od.get("new_edges"):
                self._lineage("operational_weave", new_edges=od["new_edges"],
                              matched=self.opjoiner.matched)

        self._write_state()
        self.save_population()
        return {"tick": self.tick, "alive": self._alive_count(),
                "fabric": self.fabric.stats(), "per": per,
                "join": join_delta}

    def _alive_count(self) -> int:
        return sum(1 for c in self.crawlers if c.alive)

    # -- Aporia-in-the-loop overrides -----------------------------------------
    def _apply_overrides(self) -> None:
        """Read state/overrides.json if present: {revive:[landscapes],
        kill:[ids], set:{id:{knob:val}}}. Applied then cleared."""
        if not OVERRIDES.exists():
            return
        try:
            ov = json.loads(OVERRIDES.read_text(encoding="utf-8"))
        except Exception:
            return
        for ls in ov.get("revive", []):
            rs = next((r for r in founding_rulesets() if r.landscape == ls), None)
            if rs is None:
                rs = Ruleset(landscape=ls)
            if ls == "feral" and self.landscapes:
                rs.landscape = self._feral_landscape()
                rs.hop = True
            cid = self._new_id(rs.landscape, 0)
            self.crawlers.append(Crawler(cid, rs))
            self._lineage("revive", id=cid, landscape=ls, by="aporia")
        kill = set(ov.get("kill", []))
        for c in self.crawlers:
            if c.id in kill:
                c.alive = False
                c.death_reason = "aporia_kill"
        for cid, knobs in ov.get("set", {}).items():
            c = next((x for x in self.crawlers if x.id == cid), None)
            if c:
                for k, v in knobs.items():
                    if hasattr(c.ruleset, k):
                        setattr(c.ruleset, k, v)
                self._lineage("tweak", id=cid, knobs=knobs, by="aporia")
        try:
            OVERRIDES.unlink()
        except Exception:
            pass

    # -- persistence ----------------------------------------------------------
    def _write_state(self) -> None:
        state = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "tick": self.tick,
            "landscapes_available": list(self.landscapes.keys()),
            "alive": self._alive_count(),
            "fabric": self.fabric.stats(),
            "crawlers": [c.snapshot() for c in self.crawlers],
            "rosetta": self.weaver.snapshot(),
            "operational": self.opjoiner.snapshot(),
            "graveyard_size": len(self.graveyard),
            "recent_dead": self.graveyard[-6:],
        }
        tmp = SWARM_STATE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tmp.replace(SWARM_STATE)

    def save_population(self) -> None:
        pop = {
            "tick": self.tick, "id_counter": self._id_counter,
            "crawlers": [{"id": c.id, "parent": c.parent, "generation": c.generation,
                          "total_edges": c.total_edges, "alive": c.alive,
                          "ruleset": asdict(c.ruleset)} for c in self.crawlers],
        }
        tmp = POP_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(pop, indent=2), encoding="utf-8")
        tmp.replace(POP_FILE)

    def load_population(self) -> bool:
        if not POP_FILE.exists():
            return False
        try:
            pop = json.loads(POP_FILE.read_text(encoding="utf-8"))
        except Exception:
            return False
        self.tick = pop.get("tick", 0)
        self._id_counter = pop.get("id_counter", 0)
        self.crawlers = []
        for c in pop.get("crawlers", []):
            if not c.get("alive", True):
                continue
            rs = Ruleset(**c["ruleset"])
            cr = Crawler(c["id"], rs, parent=c.get("parent"), generation=c.get("generation", 0))
            cr.total_edges = c.get("total_edges", 0)
            self.crawlers.append(cr)
        return bool(self.crawlers)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Arachne crawler swarm")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    pr = sub.add_parser("revive"); pr.add_argument("--landscape", required=True)
    pt = sub.add_parser("tweak")
    pt.add_argument("--id", required=True); pt.add_argument("--novelty-floor", type=float)
    pt.add_argument("--max-neighbors", type=int)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", action="store_true")
    ap.add_argument("--interval", type=float, default=5.0)
    ap.add_argument("--max-ticks", type=int, default=0)
    ap.add_argument("--fresh", action="store_true", help="ignore saved population")
    args = ap.parse_args()

    if args.cmd == "status":
        if SWARM_STATE.exists():
            print(SWARM_STATE.read_text(encoding="utf-8"))
        else:
            print("no swarm_state yet")
        return 0
    if args.cmd == "revive":
        ov = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
        ov.setdefault("revive", []).append(args.landscape)
        OVERRIDES.write_text(json.dumps(ov), encoding="utf-8")
        print(f"queued revive: {args.landscape}")
        return 0
    if args.cmd == "tweak":
        ov = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
        knobs = {}
        if args.novelty_floor is not None: knobs["novelty_floor"] = args.novelty_floor
        if args.max_neighbors is not None: knobs["max_neighbors"] = args.max_neighbors
        ov.setdefault("set", {})[args.id] = knobs
        OVERRIDES.write_text(json.dumps(ov), encoding="utf-8")
        print(f"queued tweak {args.id}: {knobs}")
        return 0

    sw = Swarm()
    if not sw.landscapes:
        print("FATAL: no landscapes available (check mathlib4 clone / PGPASSWORD / sympy)")
        return 2
    if args.fresh or not sw.load_population():
        sw.seed_population()
    print(f"landscapes: {list(sw.landscapes.keys())} | crawlers: {len(sw.crawlers)}")

    if args.loop:
        n = 0
        while True:
            r = sw.step_all()
            print(f"tick {r['tick']:4d} alive={r['alive']} "
                  f"fabric={r['fabric']['edges']}e/{r['fabric']['nodes']}n")
            n += 1
            if args.max_ticks and n >= args.max_ticks:
                break
            time.sleep(max(0.0, args.interval))
    else:
        r = sw.step_all()
        print(json.dumps(r, indent=2)[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
