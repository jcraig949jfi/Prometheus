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
            ps = {k: v["series_hash"] for k, v in (primary.get("series") or {}).items()}
            as_ = {k: v["series_hash"] for k, v in (arm.get("series") or {}).items()}
            seq = ps == as_
            return _met(eq and seq, {"class": rc, "equal": eq, "series_equal": seq})
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


def _coverage(primary: dict, arm: dict) -> list:
    return list(arm.get("provenance", {}).get("transformed_players", []))


def _indeterminate_if_uncovered(arm: dict, detail: dict) -> dict | None:
    cov = _coverage(None, arm)
    if not cov:
        return {"outcome": "INDETERMINATE", "detail": dict(detail, transformed_players=[], note="control could not act on any player (no transform accepts these representations)")}
    return None


class _TransformControl:
    """A control whose arm applies one registered Transform to every player it accepts (C5, 2026-09-19):
    the arm's provenance records `transformed_players`; an arm that transformed nobody is INDETERMINATE."""
    transform = ""

    def arm(self, exp, rng_seed: int):
        from prometheus.toolbox.ref.transforms import transform_players
        from prometheus.toolbox.registry import default_registry
        e = copy.deepcopy(exp)
        e.players, done = transform_players(default_registry(), self.transform, exp.players, rng_seed)
        e.provenance = dict(e.provenance, control=self.kind, transformed_players=done)
        return e


class ShamControl(_TransformControl):
    kind = "sham"
    transform = "transform.shuffle.v1"

    def manifest(self) -> dict:
        return {"kind": "control.sham.v1", "transform": self.transform, "mechanism": "structure destroyed, cost preserved"}

    def expectation(self, primary: dict, arm: dict) -> dict:
        a = primary["accounting"].get("params"); b = arm["accounting"].get("params")
        detail = {"primary_params": a, "arm_params": b, "transformed_players": _coverage(primary, arm)}
        return _indeterminate_if_uncovered(arm, detail) or _met(a == b, detail)


class ScratchControl(_TransformControl):
    kind = "scratch"
    transform = "transform.fresh.v1"

    def manifest(self) -> dict:
        return {"kind": "control.scratch.v1", "transform": self.transform}

    def expectation(self, primary: dict, arm: dict) -> dict:
        detail = {"arm_status": arm["status"], "transformed_players": _coverage(primary, arm)}
        return _indeterminate_if_uncovered(arm, detail) or _met(arm["status"] == "COMPLETED", detail)


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
