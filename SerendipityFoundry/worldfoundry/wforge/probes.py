"""Reference probe battery -- calibration instruments, NOT aspirational players.

RED-TEAM NOTE (incorporated): this battery defines the null and the
discriminative band, and it is HUMAN-SHAPED. The production battery must be
extended with programs sampled from Proteus's own genotype distribution so that
'informative world' is not operationalized as 'legible to human archetypes'.
The v0 battery below is for the offline diversity demonstration only.
"""
from __future__ import annotations

from .world import XS64, stream


class Probe:
    name = "?"

    def reset(self, seed: int, act_width: int):
        self.act_width = act_width

    def act(self, obs, charge_hint=None):
        raise NotImplementedError


class Noop(Probe):
    name = "noop"

    def act(self, obs, charge_hint=None):
        return [0] * self.act_width


class ConstMax(Probe):
    name = "const_max"

    def act(self, obs, charge_hint=None):
        return [7] * self.act_width


class ConstOne(Probe):
    name = "const_one"

    def act(self, obs, charge_hint=None):
        return [1] * self.act_width


class RandomP(Probe):
    name = "random"

    def reset(self, seed: int, act_width: int):
        super().reset(seed, act_width)
        self.r = stream("probe-random", seed)

    def act(self, obs, charge_hint=None):
        return [self.r.below(8) for _ in range(self.act_width)]


class Cycler(Probe):
    name = "cycler"

    def reset(self, seed: int, act_width: int):
        super().reset(seed, act_width)
        self.t = 0

    def act(self, obs, charge_hint=None):
        self.t += 1
        v = (0, 7, 0, 3)[self.t % 4]
        return [v] * self.act_width


class Burst(Probe):
    name = "burst"

    def reset(self, seed: int, act_width: int):
        super().reset(seed, act_width)
        self.t = 0

    def act(self, obs, charge_hint=None):
        self.t += 1
        return ([7] if self.t % 8 == 0 else [0]) * self.act_width


class GreedyEcho(Probe):
    """1-step integer hill-climber: repeats last action if own-charge channel
    rose, else perturbs. Uses only the opaque obs vector -- no designer labels."""
    name = "greedy_echo"

    def reset(self, seed: int, act_width: int):
        super().reset(seed, act_width)
        self.r = stream("probe-greedy", seed)
        self.last_obs_sum = None
        self.last_act = [0] * act_width

    def act(self, obs, charge_hint=None):
        s = sum(obs)
        if self.last_obs_sum is not None and s >= self.last_obs_sum:
            a = self.last_act
        else:
            a = [self.r.below(8) for _ in range(self.act_width)]
        self.last_obs_sum = s
        self.last_act = a
        return a


BATTERY = [Noop, ConstOne, ConstMax, RandomP, Cycler, Burst, GreedyEcho]
