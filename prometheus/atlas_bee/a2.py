"""A2 -- mixture superadditivity vs solo-transplant additive prediction (source: NPE cw01-e05).

Source (Atlas nestor.cw01/cw01-2026-09-17:cw01-e05, NULL): a mixture of organisms was tested for SUPERADDITIVITY
against a solo-transplant additive prediction (mixture == sum of solos); 2/4 clear null (mixtures were additive, no
superadditivity), with an ablation identifying load-bearing members.

BEE instantiation: world.integer.v1 with n_players=K shares its registers and yield window across players, so a
mixture genuinely interacts (players write the shared registers and split the yield). A mixture is K elites in a
K-player world; the additive prediction is the sum of each elite's SOLO charge (alone in a 1-player world). The
ablation replaces one member with an inert constant player and measures the drop (load-bearing members).
"""
from __future__ import annotations

import pathlib
import statistics
from typing import Dict, List

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.backends.local import execute, lower
from prometheus.toolbox.contracts import PlayerSpec
from prometheus.toolbox import search as SR
from prometheus.toolbox.ref.players import constant_player
from prometheus.atlas_bee.harness import Adaptation
from prometheus.atlas_bee.manifest import Manifest

WORLD = dict(world_seed=8, start_charge=30, yield_amt=12, yield_width=16384)
HORIZON = 26
K = 3
N, GENERATIONS, KEEP = 16, 8, 6
TRAIN = {"base": 1, "n_seeds": 6}
EVAL = {"base": 4000, "n_seeds": 16}


def _spec_of(p) -> PlayerSpec:
    if isinstance(p, PlayerSpec):
        return p
    return PlayerSpec(p["representation"], p["payload"], p.get("initial_state", {}), frozenset(p.get("requires", ())), p.get("meta", {}))


class A2(Adaptation):
    id = "a2"
    source = {"atlas_key": "nestor.cw01/cw01-2026-09-17:cw01-e05", "disposition": "NULL",
              "original": "mixture superadditivity vs solo-transplant additive prediction; 2/4 clear null; load-bearing members"}

    def manifest(self) -> Manifest:
        m = Manifest(self.id, self.source["atlas_key"])
        m.add("mixture", "a mixture of organisms sharing a world", "K elites in world.integer.v1(n_players=K)", "ANALOGOUS",
              "the integer world shares registers and the yield window across players, so a mixture interacts (writes "
              "the shared state, splits the yield) rather than merely co-existing")
        m.add("solo transplant / additive prediction", "each member alone; predicted mixture = sum of solos",
              "each elite in a 1-player world; additive prediction = sum of solo charges", "IDENTICAL",
              "the additive baseline is the sum of the members' solo charges")
        m.add("superadditivity", "mixture beats the sum of solos", "mixture total charge / sum of solo charges", "ANALOGOUS",
              "ratio > 1 is superadditive, ~1 additive (null), < 1 subadditive (interference)")
        m.add("load-bearing members / ablation", "remove a member, measure the drop",
              "replace one member with an inert constant player; measure the mixture's total-charge drop", "ANALOGOUS",
              "an inert member is the ablation; the drop is that member's contribution")
        m.add("organisms", "the source's mixture members", "top-K elites of a 1-player search on the world", "ANALOGOUS",
              "matured by BEE's own search; distinct members")
        m.add("objective", "the source's performance metric", "total charge summed over the mixture's slots (world_summary)",
              "ANALOGOUS", "performance is the resource the mixture accumulates")
        m.add("scientific-conclusion layer", "e05's disposition (NULL)", "-", "OMITTED", "BEE authors no conclusion")
        return m

    def prereg_body(self) -> Dict:
        return {
            "question": "Is a mixture of K organisms SUPERADDITIVE (mixture total charge > sum of the members' solo "
                        "charges), or additive (null, as e05)? Which members are load-bearing under ablation?",
            "world": "world.integer.v1(%s), n_players=1 (solo) and %d (mixture)" % (WORLD, K),
            "organisms": "top-%d elites of a 1-player statemachine.v1 search" % K,
            "objective": "total charge summed over slots (world_summary)",
            "observations": ["solo charge per member", "mixture total charge", "superadditivity ratio = mixture / sum(solos)",
                             "ablation drop per member (member replaced by an inert constant)"],
            "controls": ["solo transplant (additive prediction)", "inert-member ablation (load-bearing test)"],
            "seeds": {"train": TRAIN, "eval": EVAL}, "budgets": {"search": {"n": N, "generations": GENERATIONS}, "K": K, "horizon": HORIZON},
            "stopping_rules": "fixed budget; a ratio ~1 is the NULL result e05 reported, not a failure",
            "decision_criteria": {
                "PHENOMENON_PRESERVED": "ratio ~1 (mixture additive: null, as e05)",
                "PHENOMENON_CHANGED": "ratio > 1.1 (superadditive) or < 0.9 (subadditive/interference) -- BEE shows a mixture effect e05 did not",
            },
        }

    # ---- execution --------------------------------------------------------------------------------------------
    def _elites(self, workdir: pathlib.Path, reg) -> List[PlayerSpec]:
        t = Experiment(family="a2_solo_ev", world=ref("world.integer.v1", n_players=1, **WORLD), substrate=ref("substrate.flat.v1"),
                       players=[], objective=ref("objective.charge.v1"), observers=[ref("observer.trace.v1")],
                       seed_policy=dict(TRAIN), budget={"episodes": 1, "horizon": HORIZON})
        sd = workdir / "solo_evolve"
        SR.evolve(t, ref("selector.truncation.v1", keep=KEEP, n=N, representation="statemachine.v1"),
                  generations=GENERATIONS, workdir=sd, seed=3, registry=reg)
        rows = [r for r in SR.load_rows(sd / "archive.jsonl") if r["kind"] == "elite" and isinstance(r.get("objective"), (int, float))]
        rows.sort(key=lambda r: r["objective"], reverse=True)
        return [_spec_of(r["player"]) for r in rows[:K]]

    def _total_charge(self, players: List, n_players: int, tag: str, workdir: pathlib.Path, reg) -> float:
        e = Experiment(family="a2_%s" % tag, world=ref("world.integer.v1", n_players=n_players, **WORLD),
                       substrate=ref("substrate.flat.v1"), players=[p.manifest() for p in players],
                       objective=ref("objective.charge.v1"), observers=[ref("observer.trace.v1")],
                       seed_policy=dict(EVAL), budget={"episodes": 1, "horizon": HORIZON})
        f = workdir / ("%s.jsonl" % tag)
        execute(lower(e, reg).job, f, reg)
        prim = [r for r in read_all(f) if r["arm"] == "primary"]
        totals = [sum(r["science"]["world_summary"]["charge"]) for r in prim if r["science"].get("world_summary")]
        return statistics.mean(totals) if totals else None

    def run(self, workdir: pathlib.Path, reg=None) -> Dict:
        reg = reg or default_registry()
        workdir = pathlib.Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
        elites = self._elites(workdir, reg)
        solo = [self._total_charge([e], 1, "solo%d" % i, workdir, reg) for i, e in enumerate(elites)]
        mixture = self._total_charge(elites, K, "mixture", workdir, reg)
        inert = constant_player([0, 0])
        ablation = []
        for i in range(len(elites)):
            members = [(inert if j == i else e) for j, e in enumerate(elites)]
            ablation.append(self._total_charge(members, K, "abl%d" % i, workdir, reg))
        return {"observed": {"solo": solo, "solo_sum": sum(s for s in solo if isinstance(s, (int, float))),
                             "mixture": mixture, "ablation": ablation}, "receipt_files": [],
                "notes": ["mixture interacts through the integer world's shared registers and yield split"]}

    def compare(self, observed: Dict) -> Dict:
        solo, solo_sum, mix, abl = observed["solo"], observed["solo_sum"], observed["mixture"], observed["ablation"]
        ratio = (mix / solo_sum) if (isinstance(mix, (int, float)) and solo_sum) else None
        drops = [None if not isinstance(a, (int, float)) or not isinstance(mix, (int, float)) else round(mix - a, 2) for a in abl]
        load_bearing = [i for i, dr in enumerate(drops) if isinstance(dr, (int, float)) and dr > 0.05 * (abs(mix) or 1)]
        new_phenomena = []
        if ratio is None:
            verdict = "INSTRUMENT_FAILURE"; headline = "missing mixture or solo sum"
        elif 0.9 <= ratio <= 1.1:
            verdict = "PHENOMENON_PRESERVED"; headline = "mixture is additive (ratio %.2f): NULL, as e05 -- no superadditivity" % ratio
        elif ratio > 1.1:
            verdict = "PHENOMENON_CHANGED"; headline = "mixture is SUPERADDITIVE (ratio %.2f): BEE shows a positive mixture effect e05 did not" % ratio
            new_phenomena.append("K organisms sharing the integer world's registers and yield produce more total charge than "
                                 "the sum of their solos -- superadditivity from shared-state interaction")
        else:
            verdict = "PHENOMENON_CHANGED"; headline = "mixture is SUBADDITIVE (ratio %.2f): the members interfere (contest the shared yield)" % ratio
            new_phenomena.append("mixing the solo elites LOSES total charge vs their solos -- they contest the shared yield window "
                                 "(a mixture cost e05's additive-null did not expose)")
        differences = {
            "scientific": [headline, "solo=%s sum=%.2f mixture=%s; ablation drops=%s; load-bearing members=%s" % (
                [round(s, 2) if isinstance(s, (int, float)) else s for s in solo], solo_sum,
                round(mix, 2) if isinstance(mix, (int, float)) else mix, drops, load_bearing)],
            "representational": ["mixture interaction is via the integer world's SHARED registers + split yield; the source's "
                                 "mixture medium may differ (ANALOGOUS)"],
            "executor": ["BEE local scalar execution; deterministic (fixed seeds)"],
            "resource": ["K=%d, population=%d, generations=%d, eval_seeds=%d" % (K, N, GENERATIONS, EVAL["n_seeds"])],
            "measurement": ["total charge summed over slots, meaned over eval seeds; ablation = one member replaced by an inert constant"],
        }
        return {"verdict": verdict, "ratio": ratio, "ablation_drops": drops, "load_bearing_members": load_bearing,
                "differences": differences, "new_phenomena": new_phenomena, "summary": headline}
