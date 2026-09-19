"""Reference controls (directive s16): experimental OBJECTS that travel with the Experiment. Each control
produces an ARM (a variant Experiment) and a mechanical EXPECTATION over (primary receipt, arm receipt)
pairs. Expectations are about the INSTRUMENT (did the measurement channel see what it must see), never
about the science; a NOT_MET outcome marks the run CONTROL_NOT_MET in its receipt and is a result.

  control.replay.v1       same experiment, same seeds  -> trace hashes equal (BIT) or within tolerance (SEMANTIC)
  control.cheat.v1        world dynamics silently skipped (world param _cheat_skip_dynamics) -> every trace differs
  control.negative.v1     every player replaced by the abstaining constant player -> actions_total == 0, objective computed
  control.positive.v1     every player replaced by the maximal constant player -> actions_total > 0 and trace != negative's would
                          (checked against the primary: the world must respond to actions: trace differs)
  control.sham.v1         statemachine tables shuffled with identical shape -> cost (params) equal to primary
  control.scratch.v1      fresh random players of the same representation/shape, different seed -> ran, cost recorded
  control.permutation.v1  observation channels permuted (kernel wrapper) -> ran; trace equal iff players ignore obs
"""
from __future__ import annotations

import copy
from typing import Any, Dict

from prometheus.toolbox.ref import players as P
from prometheus.toolbox.ref.worlds import stream


def _met(ok: bool, detail: Any) -> dict:
    return {"outcome": "MET" if ok else "NOT_MET", "detail": detail}


class ReplayControl:
    kind = "replay"

    def manifest(self) -> dict:
        return {"kind": "control.replay.v1"}

    def arm(self, exp, rng_seed: int):
        e = copy.deepcopy(exp); e.provenance = dict(e.provenance, control="replay"); return e

    def expectation(self, primary: dict, arm: dict) -> dict:
        rc = primary.get("replay_class")
        if rc == "BIT":
            eq = primary["trace_hashes"] == arm["trace_hashes"]
            return _met(eq, {"class": rc, "equal": eq})
        return {"outcome": "INDETERMINATE", "detail": {"class": rc, "note": "semantic replay needs a declared tolerance; none in Phase 1"}}


class CheatControl:
    kind = "cheat"

    def manifest(self) -> dict:
        return {"kind": "control.cheat.v1", "mechanism": "world_params._cheat_skip_dynamics=True"}

    def arm(self, exp, rng_seed: int):
        e = copy.deepcopy(exp)
        e.world = {"kind": e.world["kind"], "params": dict(e.world.get("params", {}), _cheat_skip_dynamics=True)}
        e.provenance = dict(e.provenance, control="cheat")
        return e

    def expectation(self, primary: dict, arm: dict) -> dict:
        differs = [a != b for a, b in zip(primary["trace_hashes"], arm["trace_hashes"])]
        return _met(bool(differs) and all(differs), {"episodes_differing": sum(differs), "episodes": len(differs)})


class NegativeControl:
    kind = "negative"

    def manifest(self) -> dict:
        return {"kind": "control.negative.v1", "player": "constant.v1 abstain"}

    def arm(self, exp, rng_seed: int):
        e = copy.deepcopy(exp)
        e.players = [P.constant_player([0, 0], meta={"control": "negative", "replaces": p.get("meta", {}).get("seed")}).manifest() for p in exp.players]
        e.provenance = dict(e.provenance, control="negative")
        return e

    def expectation(self, primary: dict, arm: dict) -> dict:
        obs = arm["science"].get("observations", {})
        acts = sum(int(o.get("actions_total", 0)) for o in obs.values())
        has_obj = "objective" in arm["science"]
        return _met(acts == 0 and has_obj, {"arm_actions_total": acts, "objective_recorded": has_obj})


class PositiveControl:
    kind = "positive"

    def manifest(self) -> dict:
        return {"kind": "control.positive.v1", "player": "constant.v1 maximal"}

    def arm(self, exp, rng_seed: int):
        e = copy.deepcopy(exp)
        e.players = [P.constant_player([7, 7], meta={"control": "positive"}).manifest() for _ in exp.players]
        e.provenance = dict(e.provenance, control="positive")
        return e

    def expectation(self, primary: dict, arm: dict) -> dict:
        obs = arm["science"].get("observations", {})
        acts = sum(int(o.get("actions_total", 0)) for o in obs.values())
        differs = primary["trace_hashes"] != arm["trace_hashes"]
        return _met(acts > 0 and differs, {"arm_actions_total": acts, "trace_differs_from_primary": differs})


class ShamControl:
    kind = "sham"

    def manifest(self) -> dict:
        return {"kind": "control.sham.v1", "mechanism": "statemachine table rows permuted; shape and parameter count preserved"}

    def arm(self, exp, rng_seed: int):
        e = copy.deepcopy(exp); s = stream("sham", rng_seed)
        for p in e.players:
            if p["representation"] == "statemachine.v1":
                table = p["payload"]["table"]
                flat = [cell for row in table for cell in row]
                for i in range(len(flat) - 1, 0, -1):
                    j = s.below(i + 1); flat[i], flat[j] = flat[j], flat[i]
                nb = p["payload"]["n_buckets"]
                p["payload"]["table"] = [flat[i * nb:(i + 1) * nb] for i in range(p["payload"]["n_states"])]
                p["meta"] = dict(p.get("meta", {}), control="sham")
        e.provenance = dict(e.provenance, control="sham")
        return e

    def expectation(self, primary: dict, arm: dict) -> dict:
        a = primary["accounting"].get("params"); b = arm["accounting"].get("params")
        return _met(a == b, {"primary_params": a, "arm_params": b})


class ScratchControl:
    kind = "scratch"

    def manifest(self) -> dict:
        return {"kind": "control.scratch.v1"}

    def arm(self, exp, rng_seed: int):
        e = copy.deepcopy(exp)
        new = []
        for i, p in enumerate(exp.players):
            if p["representation"] == "statemachine.v1":
                pl = p["payload"]
                new.append(P.random_statemachine(rng_seed * 1009 + i, pl["n_states"], pl["n_buckets"], pl["width"], pl["act_range"], meta={"control": "scratch"}).manifest())
            else:
                new.append(p)
        e.players = new; e.provenance = dict(e.provenance, control="scratch")
        return e

    def expectation(self, primary: dict, arm: dict) -> dict:
        return _met(arm["status"] == "COMPLETED", {"arm_status": arm["status"]})


class PermutationControl:
    kind = "permutation"

    def manifest(self) -> dict:
        return {"kind": "control.permutation.v1", "mechanism": "wrappers.observation_permute"}

    def arm(self, exp, rng_seed: int):
        e = copy.deepcopy(exp)
        e.interventions = list(e.interventions) + [{"name": "control.permutation", "world_params": {}, "wrappers": {"observation_permute": rng_seed}}]
        e.provenance = dict(e.provenance, control="permutation")
        return e

    def expectation(self, primary: dict, arm: dict) -> dict:
        return _met(arm["status"] == "COMPLETED", {"trace_equal_to_primary": primary["trace_hashes"] == arm["trace_hashes"]})


ALL = {"control.replay.v1": ReplayControl, "control.cheat.v1": CheatControl, "control.negative.v1": NegativeControl,
       "control.positive.v1": PositiveControl, "control.sham.v1": ShamControl, "control.scratch.v1": ScratchControl,
       "control.permutation.v1": PermutationControl}
