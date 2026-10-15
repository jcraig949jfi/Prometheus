"""C-019-T021 compatibility layer over the FROZEN Crius interface (read-only steward; nothing under crius/ is edited).

Worlds are built from crius/configs/c1.json plus, where labelled, a substrate flag (config only) or an observation filter
applied OUTSIDE the engine by substituting `crius.player.TaskRun` with a subclass for the duration of a `with` block.
The engine's transition code (`world_c1._C1.apply_action`, `TaskRun.act`) is not overridden, only the label seen by the organism.
"""
import contextlib
import copy
import json
import os
import sys

from crius import env as crius_env, player as crius_player, vm

C1 = os.path.join("crius", "configs", "c1.json")
RUNGB_SUBSTRATE = {"typed_procedures": True, "psim": False, "version": "c2-typed-v1"}      # crius/configs/c2b.json substrate, verbatim
READS = {"organism": 0, "engine": 0}


class FilteredTaskRun(crius_env.TaskRun):
    """EXTERNAL_FILTER (a): the organism sees last_primitive == -1; transitions are the parent's, untouched.
    `full=True` also hides the attribute from the substrate runtime (only valid where calibration is OFF);
    `full=False` filters the observation dict only (the runtime still sees the label: W4)."""
    FULL = True

    @property
    def last_primitive(self):
        caller = sys._getframe(1).f_code.co_filename
        READS["engine" if os.path.basename(caller) in ("env.py", "vm.py") else "organism"] += 1
        return -1 if self.FULL else self._lp

    @last_primitive.setter
    def last_primitive(self, v):
        self._lp = v

    def observation(self):
        o = super().observation()
        o["last_primitive"] = -1
        return o


class FilteredObsOnly(FilteredTaskRun):
    FULL = False


class CountingTaskRun(crius_env.TaskRun):
    """Unfiltered, counts reads of last_primitive made by anything other than env.py / vm.py (i.e. by an organism)."""

    @property
    def last_primitive(self):
        caller = sys._getframe(1).f_code.co_filename
        READS["engine" if os.path.basename(caller) in ("env.py", "vm.py") else "organism"] += 1
        return self._lp

    @last_primitive.setter
    def last_primitive(self, v):
        self._lp = v


def load_cfg(world):
    with open(C1, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg = copy.deepcopy(cfg)
    if world in ("W3", "W4"):
        cfg["substrate"] = dict(RUNGB_SUBSTRATE)
    if world in ("W5b", "W5c"):
        cfg["substrate"] = {"typed_procedures": False, "psim": False, "version": "cf-nocal"}   # COUNTERFACTUAL_RUNTIME: calibration disabled
    return cfg


@contextlib.contextmanager
def world_context(world):
    """Install the world's TaskRun for the duration of the block."""
    cls = {"W1": CountingTaskRun, "W2": FilteredTaskRun, "W3": CountingTaskRun, "W4": FilteredObsOnly,
           "W5b": CountingTaskRun, "W5c": FilteredTaskRun}[world]
    old = crius_player.TaskRun
    crius_player.TaskRun = cls
    READS["organism"] = READS["engine"] = 0
    try:
        yield load_cfg(world)
    finally:
        crius_player.TaskRun = old
        vm.set_substrate({})
