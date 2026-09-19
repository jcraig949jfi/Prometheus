"""Reference transforms (directive s17; built in C5 after playtest A showed controls silently skipping players
they did not understand). A Transform declares the object kinds it ACCEPTS ("player.<representation>") and
apply(obj, seed) returns a new object of the same kind. Controls look transforms up by representation and
record which players they could transform; a control that transformed nothing reports INDETERMINATE.

  transform.shuffle.v1   structure-destroying, cost-preserving (the SHAM): statemachine.v1 table cells
                         permuted with shape kept; proteus.tape.v0 genome words permuted with length kept;
                         constant.v1 NOT accepted (there is no structure to destroy).
  transform.fresh.v1     the SCRATCH: a new random player of the same representation and shape from a new seed.
  transform.relabel.v1   statemachine.v1: states renumbered by a seeded permutation (behaviour-preserving:
                         the fingerprint must not change) -- the metamorphic transform.
"""
from __future__ import annotations

import copy
from typing import Any

from prometheus.toolbox.contracts import PlayerSpec
from prometheus.toolbox.ref import players as P
from prometheus.toolbox.ref.worlds import stream


def _shuffle(lst: list, s) -> list:
    out = list(lst)
    for i in range(len(out) - 1, 0, -1):
        j = s.below(i + 1); out[i], out[j] = out[j], out[i]
    return out


def _spec(p: dict | PlayerSpec) -> PlayerSpec:
    if isinstance(p, PlayerSpec):
        return p
    return PlayerSpec(p["representation"], copy.deepcopy(p["payload"]), dict(p.get("initial_state", {})), frozenset(p.get("requires", ())), dict(p.get("meta", {})))


SM = ("statemachine.v1", "statemachine.v2")


class ShuffleTransform:
    kind = "transform.shuffle.v1"
    accepts = frozenset({"player.statemachine.v1", "player.statemachine.v2", "player.proteus.tape.v0", "player.rewrite.v1"})

    def manifest(self) -> dict:
        return {"kind": self.kind, "accepts": sorted(self.accepts)}

    def apply(self, obj: Any, rng_seed: int) -> PlayerSpec:
        spec = _spec(obj); s = stream("shuffle", rng_seed, spec.representation)
        pl = copy.deepcopy(spec.payload)
        if spec.representation in SM:
            flat = _shuffle([cell for row in pl["table"] for cell in row], s); nb = pl["n_buckets"]
            pl["table"] = [flat[i * nb:(i + 1) * nb] for i in range(pl["n_states"])]
        elif spec.representation == "proteus.tape.v0":
            pl["manifest"] = dict(pl["manifest"], genome=_shuffle(list(pl["manifest"]["genome"]), s))
        elif spec.representation == "rewrite.v1":
            flat = _shuffle([x for rule in pl["rules"] for side in rule for x in side], s)
            pl["rules"] = [[flat[i:i + 2], flat[i + 2:i + 4]] for i in range(0, len(flat), 4)]; pl["tape"] = _shuffle(list(pl["tape"]), s)
        else:
            raise TypeError("%s does not accept %s" % (self.kind, spec.representation))
        return PlayerSpec(spec.representation, pl, spec.initial_state, spec.requires, dict(spec.meta, transform=self.kind, transform_seed=rng_seed))


class FreshTransform:
    kind = "transform.fresh.v1"
    accepts = frozenset({"player.statemachine.v1", "player.statemachine.v2", "player.proteus.tape.v0", "player.rewrite.v1"})

    def manifest(self) -> dict:
        return {"kind": self.kind, "accepts": sorted(self.accepts)}

    def apply(self, obj: Any, rng_seed: int) -> PlayerSpec:
        spec = _spec(obj)
        if spec.representation == "statemachine.v1":
            pl = spec.payload
            return P.random_statemachine(rng_seed, pl["n_states"], pl["n_buckets"], pl["width"], pl["act_range"], meta={"transform": self.kind})
        if spec.representation == "statemachine.v2":
            pl = spec.payload
            return P.random_statemachine_v2(rng_seed, pl["n_states"], pl["n_buckets"], pl["width"], pl["act_range"], pl["mem_range"], meta={"transform": self.kind})
        if spec.representation == "proteus.tape.v0":
            return P.random_proteus_player(rng_seed, meta={"transform": self.kind})
        if spec.representation == "rewrite.v1":
            pl = spec.payload
            return P.random_rewrite_system(rng_seed, len(pl["rules"]), pl["alphabet"], len(pl["tape"]), meta={"transform": self.kind})
        raise TypeError("%s does not accept %s" % (self.kind, spec.representation))


class RelabelTransform:
    kind = "transform.relabel.v1"
    accepts = frozenset({"player.statemachine.v1", "player.statemachine.v2"})

    def manifest(self) -> dict:
        return {"kind": self.kind, "accepts": sorted(self.accepts)}

    def apply(self, obj: Any, rng_seed: int) -> PlayerSpec:
        spec = _spec(obj)
        if spec.representation not in SM:
            raise TypeError("%s does not accept %s" % (self.kind, spec.representation))
        pl = copy.deepcopy(spec.payload); n = pl["n_states"]; s = stream("relabel", rng_seed)
        perm = _shuffle(list(range(n)), s)                  # old state i -> new label perm[i]
        table = [None] * n
        for i, row in enumerate(pl["table"]):
            table[perm[i]] = [[perm[cell[0]]] + list(cell[1:]) for cell in row]     # cell = [next, acts] (v1) or [next, acts, mem_write] (v2)
        pl["table"] = table
        init = dict(spec.initial_state); init["state"] = perm[int(init.get("state", 0))]
        return PlayerSpec(spec.representation, pl, init, spec.requires, dict(spec.meta, transform=self.kind, transform_seed=rng_seed))


class PointMutationTransform:
    """transform.point_mutation.v1 (C26): change exactly ONE table cell of a state machine (next state, one action
    value, or -- for v2 -- the memory write). The search operator; shape and cost preserved."""
    kind = "transform.point_mutation.v1"
    accepts = frozenset({"player.statemachine.v1", "player.statemachine.v2"})

    def manifest(self) -> dict:
        return {"kind": self.kind, "accepts": sorted(self.accepts)}

    def apply(self, obj: Any, rng_seed: int) -> PlayerSpec:
        spec = _spec(obj)
        if spec.representation not in SM:
            raise TypeError("%s does not accept %s" % (self.kind, spec.representation))
        pl = copy.deepcopy(spec.payload); s = stream("point_mutation", rng_seed)
        i = s.below(pl["n_states"]); j = s.below(pl["n_buckets"]); cell = pl["table"][i][j]
        field = s.below(3 if spec.representation == "statemachine.v2" else 2)
        if field == 0:
            cell[0] = (cell[0] + 1 + s.below(max(1, pl["n_states"] - 1))) % pl["n_states"]
        elif field == 1:
            k = s.below(len(cell[1])); cell[1][k] = (cell[1][k] + 1 + s.below(max(1, pl["act_range"] - 1))) % pl["act_range"]
        else:
            cell[2] = -1 if cell[2] >= 0 and s.below(4) == 0 else s.below(pl["mem_range"])
        parent_fp = spec.meta.get("fingerprint")
        return PlayerSpec(spec.representation, pl, spec.initial_state, spec.requires,
                          dict(spec.meta, transform=self.kind, transform_seed=rng_seed, parent=parent_fp))


ALL = {"transform.shuffle.v1": ShuffleTransform, "transform.fresh.v1": FreshTransform, "transform.relabel.v1": RelabelTransform,
       "transform.point_mutation.v1": PointMutationTransform}


def transform_players(registry, kind: str, players: list, rng_seed: int) -> tuple:
    """Apply a registered transform to every player it accepts. -> (new player manifests, transformed indices)."""
    t = registry.make(kind); out = []; done = []
    for i, p in enumerate(players):
        if "player." + p["representation"] in t.accepts:
            m = t.apply(p, rng_seed * 1009 + i).manifest()
            for k in ("substrate",):                      # C35: keys the PlayerSpec does not model travel with the player
                if k in p:
                    m[k] = p[k]
            out.append(m); done.append(i)
        else:
            out.append(p)
    return out, done
