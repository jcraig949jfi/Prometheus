"""Reference substrate.

  substrate.flat.v1   WRITE  the flat in-process machine: instantiates statemachine.v1, constant.v1 and (when
                             proteus imports) proteus.tape.v0; no workspace; raw cost accounting aggregated over
                             its instances. It offers players NO extension capabilities: a player that `requires`
                             ext.workspace.* cannot be instantiated here, and the negotiation says so.

A Substrate is the boundary that decides what a player can touch (directive s6, s12). Phase 2 adds
substrates that expose a StateDevice as workspace.kv / workspace.stream to the same representations.
"""
from __future__ import annotations

from typing import Dict, List

from prometheus.toolbox.contracts import PlayerSpec
from prometheus.toolbox.ref import players as P


class SubstrateError(ValueError):
    pass


class FlatInProcessSubstrate:
    kind = "substrate.flat.v1"
    capabilities = frozenset({"core.substrate.v1", "ext.cost.v1", "ext.reference.v1"})

    def __init__(self):
        reps = {"statemachine.v1", "constant.v1"}
        if P.proteus_available():
            reps.add("proteus.tape.v0")
        self.representations = frozenset(reps)
        self._instances: List[object] = []

    def manifest(self) -> dict:
        return {"kind": self.kind, "representations": sorted(self.representations), "capabilities": sorted(self.capabilities)}

    def instantiate(self, spec: PlayerSpec, seed: int):
        if spec.representation not in self.representations:
            raise SubstrateError("%s cannot instantiate %r" % (self.kind, spec.representation))
        unmet = set(spec.requires) - self.capabilities
        if unmet:
            raise SubstrateError("player requires %s which %s does not offer" % (sorted(unmet), self.kind))
        if spec.representation == "statemachine.v1":
            inst = P.StateMachineInstance(spec)
        elif spec.representation == "constant.v1":
            inst = P.ConstantInstance(spec)
        else:
            inst = P.ProteusTapeInstance(spec, seed)
        self._instances.append(inst)
        return inst

    def accounting(self) -> Dict[str, int]:
        tot: Dict[str, int] = {}
        for inst in self._instances:
            for k, v in inst.cost().items():
                tot[k] = tot.get(k, 0) + int(v)
        tot["instances"] = len(self._instances)
        return tot
