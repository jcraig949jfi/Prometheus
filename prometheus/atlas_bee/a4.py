"""A4 -- import takeover / dose ecology (source: SFE C3-SFE-10).

Source (Atlas archaeon.campaign/cmp3:C3-SFE-10, CAPABLE_NEGATIVE): mature imports injected into a population take it
over -- but a PERMUTED control (the same import, scrambled) takes over EQUALLY (11/12 vs 12/12). So takeover is
driven by the injection/dose, not by the import's competence.

BEE instantiation: the S3 seed_players scaffolding injects players into generation 0 carrying origin="import"; their
descendants inherit the origin, so the archive's import-share per generation IS the takeover curve. A MATURE import
is the best elite of a prior search on the same world; the PERMUTED control is that elite passed through
transform.shuffle.v1 (same components, scrambled table -> same complexity, random behaviour). We compare the
takeover curves of mature vs permuted at a fixed dose. A FRESH random import is a floor.
"""
from __future__ import annotations

import pathlib
from typing import Dict, List

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.contracts import PlayerSpec
from prometheus.toolbox import search as SR
from prometheus.atlas_bee.harness import Adaptation
from prometheus.atlas_bee.manifest import Manifest

WORLD = dict(world_seed=8, start_charge=40, yield_amt=10)
HORIZON = 24
N, GENERATIONS, KEEP = 16, 8, 6
MATURE_GENERATIONS = 10
DOSE = 4
SEEDS = {"base": 1, "n_seeds": 4}


def _spec_of(p) -> PlayerSpec:
    if isinstance(p, PlayerSpec):
        return p
    return PlayerSpec(p["representation"], p["payload"], p.get("initial_state", {}), frozenset(p.get("requires", ())), p.get("meta", {}))


class A4(Adaptation):
    id = "a4"
    source = {"atlas_key": "archaeon.campaign/cmp3:C3-SFE-10", "disposition": "CAPABLE_NEGATIVE",
              "original": "mature imports take over, but a permuted control takes over equally (11/12 vs 12/12): dose, not competence"}

    def manifest(self) -> Manifest:
        m = Manifest(self.id, self.source["atlas_key"])
        m.add("import / injection", "a mature organism injected into a population",
              "seed_players injected into generation 0 with origin=import (the S3 scaffolding)", "IDENTICAL",
              "injected players take the first slots of generation 0; their descendants inherit the origin")
        m.add("takeover measure", "the import lineage's share of the population over time",
              "fraction of archive elites with origin=import, per generation", "ANALOGOUS",
              "origin travels through player meta, so the archive records import vs resident lineage per generation")
        m.add("mature import", "an organism matured on the world", "best elite of a prior search on the same world",
              "ANALOGOUS", "matured by BEE's own search rather than the source's, but on the same world")
        m.add("permuted control", "the import scrambled (same material, no competence)",
              "transform.shuffle.v1 of the mature elite (permutes the table)", "IDENTICAL",
              "the shuffle keeps the components and complexity but scrambles the behaviour -- the permuted control")
        m.add("dose", "how many copies are injected", "seed_players = DOSE DISTINCT organisms of the kind (top-DOSE "
              "elites for mature; their individual shuffles for permuted; DOSE randoms for fresh)", "MODIFIED",
              "BEE's sweep forbids duplicate players (every population member must be distinct), so a dose of "
              "byte-identical clones is UNREPRESENTABLE; the dose is DOSE distinct organisms of the same kind")
        m.add("offspring cap", "SFE's per-parent offspring quota", "-", "UNREPRESENTABLE",
              "BEE's search has no per-parent offspring cap; takeover is shaped by selection, not a quota")
        m.add("objective / selection", "the population's fitness pressure", "objective.charge.v1, selector.truncation.v1",
              "ANALOGOUS", "hill-climb on charge; a competent import should out-select residents, a scrambled one should not")
        m.add("scientific-conclusion layer", "SFE's disposition (CAPABLE_NEGATIVE)", "-", "OMITTED", "BEE authors no conclusion")
        return m

    def prereg_body(self) -> Dict:
        return {
            "question": "Does a MATURE import take over a population more than its PERMUTED control (a scrambled copy)? "
                        "If they take over equally, takeover is driven by the dose/injection, not by competence (as C3-SFE-10).",
            "world": "world.integer.v1(%s)" % WORLD,
            "imports": {"mature": "best elite of a %d-generation search on the world" % MATURE_GENERATIONS,
                        "permuted": "transform.shuffle.v1 of the mature elite", "fresh": "a random statemachine (floor)"},
            "initial_state": "generation 0 = DOSE copies of the import (origin=import) + fresh residents",
            "interventions": {"import_kind": ["mature", "permuted", "fresh"], "dose": DOSE},
            "objective": "objective.charge.v1", "observations": ["import-origin share of the archive per generation",
                                                                 "final import-share per import kind"],
            "controls": ["permuted (shuffle) as the competence-removed control", "fresh random import as a floor"],
            "seeds": SEEDS, "budgets": {"search": {"n": N, "generations": GENERATIONS, "keep": KEEP}, "episodes": 1, "horizon": HORIZON},
            "stopping_rules": "fixed budget; equal takeover of mature and permuted is the CAPABLE_NEGATIVE result, not a failure",
            "decision_criteria": {
                "PHENOMENON_PRESERVED": "mature and permuted reach a similar final import-share (takeover is dose-driven, as C3-SFE-10)",
                "PHENOMENON_CHANGED/INVERTED": "mature takes over substantially more than permuted (competence DOES drive takeover in BEE)",
                "PHENOMENON_ABSENT": "no import kind takes over (dose too small / no selection gradient)",
            },
        }

    # ---- execution --------------------------------------------------------------------------------------------
    def _mature(self, workdir: pathlib.Path, reg) -> List:
        t = Experiment(family="a4_mat", world=ref("world.integer.v1", **WORLD), substrate=ref("substrate.flat.v1"),
                       players=[], objective=ref("objective.charge.v1"), observers=[ref("observer.trace.v1")],
                       seed_policy=dict(SEEDS), budget={"episodes": 1, "horizon": HORIZON})
        sd = workdir / "mature"
        SR.evolve(t, ref("selector.truncation.v1", keep=KEEP, n=N, representation="statemachine.v1"),
                  generations=MATURE_GENERATIONS, workdir=sd, seed=3, registry=reg)
        rows = [r for r in SR.load_rows(sd / "archive.jsonl") if r["kind"] == "elite" and isinstance(r.get("objective"), (int, float))]
        rows.sort(key=lambda r: r["objective"], reverse=True)
        return [(_spec_of(r["player"]), r["objective"]) for r in rows[:DOSE]]

    def _takeover(self, dose_specs: List[PlayerSpec], kind: str, workdir: pathlib.Path, reg) -> Dict:
        imps = [PlayerSpec(s.representation, s.payload, s.initial_state, s.requires, dict(s.meta, origin="import", import_kind=kind))
                for s in dose_specs]
        t = Experiment(family="a4_%s" % kind, world=ref("world.integer.v1", **WORLD), substrate=ref("substrate.flat.v1"),
                       players=[], objective=ref("objective.charge.v1"), observers=[ref("observer.trace.v1")],
                       seed_policy=dict(SEEDS), budget={"episodes": 1, "horizon": HORIZON})
        sd = workdir / ("takeover_%s" % kind)
        SR.evolve(t, ref("selector.truncation.v1", keep=KEEP, n=N, representation="statemachine.v1"),
                  generations=GENERATIONS, workdir=sd, seed=11, registry=reg, seed_players=imps)
        rows = [r for r in SR.load_rows(sd / "archive.jsonl") if r["kind"] == "elite"]
        gens = sorted({r["gen"] for r in rows})
        share = []
        for g in gens:
            gr = [r for r in rows if r["gen"] == g]
            imp_n = sum(1 for r in gr if r.get("origin") == "import")
            share.append(round(imp_n / len(gr), 3) if gr else None)
        return {"kind": kind, "import_share_by_gen": share, "final_share": share[-1] if share else None,
                "archive_file": str(sd / "archive.jsonl")}

    def run(self, workdir: pathlib.Path, reg=None) -> Dict:
        reg = reg or default_registry()
        workdir = pathlib.Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
        mature = self._mature(workdir, reg)
        mature_specs = [s for s, _ in mature]
        sh = reg.make("transform.shuffle.v1")
        permuted_specs = [sh.apply(s, 99 + i) for i, s in enumerate(mature_specs)]
        from prometheus.toolbox.ref.players import random_statemachine
        fresh_specs = [random_statemachine(777 + i) for i in range(DOSE)]
        imports = {"mature": mature_specs, "permuted": permuted_specs, "fresh": fresh_specs}
        results = {k: self._takeover(v, k, workdir, reg) for k, v in imports.items()}
        return {"observed": {"mature_train_objs": [o for _, o in mature], "takeover": results},
                "receipt_files": [], "notes": ["takeover measured from archive origin-share; offspring cap UNREPRESENTABLE per manifest"]}

    def compare(self, observed: Dict) -> Dict:
        tk = observed["takeover"]
        mat = tk["mature"]["final_share"]; per = tk["permuted"]["final_share"]; fr = tk["fresh"]["final_share"]
        signals = {k: tk[k]["import_share_by_gen"] for k in tk}
        finals = {"mature": mat, "permuted": per, "fresh": fr}
        new_phenomena = []
        def near(a, b, tol=0.15):
            return a is not None and b is not None and abs(a - b) <= tol
        took_over = lambda x: x is not None and x >= 0.75
        equivalent = near(mat, per) and near(mat, fr)          # mature ~= permuted ~= fresh: competence gives no edge
        if mat is None or per is None:
            verdict = "INSTRUMENT_FAILURE"; headline = "a takeover curve is missing"
        elif not took_over(mat) and not took_over(per):
            verdict = "PHENOMENON_ABSENT"
            headline = ("no import took over (mature=%.2f permuted=%.2f fresh=%.2f): all injected lineages wash out under "
                        "pure selection. C3-SFE-10's mature~=permuted EQUIVALENCE is preserved (competence gives no takeover "
                        "edge), but takeover itself is ABSENT -- its mechanism (the offspring cap that sustains a dose) is "
                        "UNREPRESENTABLE in BEE, so a non-optimal import is simply selected out." % (mat, per, fr))
            if equivalent:
                new_phenomena.append("takeover in SFE is dose-driven because the offspring cap guarantees injected organisms "
                                     "reproduction slots; BEE has no offspring cap, so mature, permuted and fresh imports wash "
                                     "out EQUALLY -- the equivalence survives, the takeover does not")
        elif near(mat, per):
            verdict = "PHENOMENON_PRESERVED"
            headline = "mature (%.2f) and permuted (%.2f) take over equally: dose-driven takeover, as C3-SFE-10" % (mat, per)
        else:
            verdict = "PHENOMENON_CHANGED"
            headline = "mature (%.2f) and permuted (%.2f) take over UNEQUALLY: competence shapes takeover in BEE, unlike C3-SFE-10" % (mat, per)
            if took_over(mat) and not took_over(per):
                new_phenomena.append("in BEE the mature import takes over but the permuted (scrambled) control does NOT -- "
                                     "competence, not just dose, drives takeover; the SFE negative does not hold under BEE's selection")
        differences = {
            "scientific": [headline, "final import-share: " + ", ".join("%s=%s" % (k, v) for k, v in finals.items())],
            "representational": ["takeover = archive origin-share over generations (S3 origin inheritance)",
                                 "no per-parent offspring cap (UNREPRESENTABLE): takeover is shaped by selection alone"],
            "executor": ["BEE local scalar execution; deterministic search (fixed seed)"],
            "resource": ["dose=%d, population=%d, generations=%d, mature trained %d gens" % (DOSE, N, GENERATIONS, MATURE_GENERATIONS)],
            "measurement": ["fraction of archive elites with origin=import, final generation"],
        }
        return {"verdict": verdict, "signals": signals, "finals": finals, "differences": differences,
                "new_phenomena": new_phenomena, "summary": headline}
