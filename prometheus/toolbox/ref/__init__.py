"""Reference implementations and their registry rows. `install(registry)` registers every reference
component with its capabilities, route and provenance; rows start PROVISIONAL and become ADMITTED
only through admission.admit() on a host (the state is per process; the durable record is the
admission receipt the caller writes).
"""
from __future__ import annotations

from prometheus.toolbox.registry import ComponentRecord, Registry

PROV = {"author": "Bellerophon", "design": "roles/Bellerophon/WORLDS_KERNEL_DESIGN_v0.2.md"}


def install(reg: Registry) -> Registry:
    from prometheus.toolbox.ref import worlds as W, substrates as S, observers as O, controls as Cn, players as P
    reg.register(ComponentRecord("world.integer.v1", "world", W.IntegerWorld, W.IntegerWorld.capabilities, reference_of="world.integer",
                                 route="write", provenance=dict(PROV, source="prometheus/toolbox/ref/worlds.py"), license="repository"))
    try:
        W._wforge()
        reg.register(ComponentRecord("world.wforge.encounter.v0", "world", W.WforgeEncounterWorld, W.WforgeEncounterWorld.capabilities,
                                     route="wrap", provenance=dict(PROV, source="SerendipityFoundry/worldfoundry/wforge/world.py", owner="Ludus"), license="repository"))
    except Exception as exc:                                    # noqa: BLE001  absent machinery is an absent row, recorded
        reg.register(ComponentRecord("world.wforge.encounter.v0", "world", W.WforgeEncounterWorld, frozenset(), route="wrap",
                                     provenance=dict(PROV, source="SerendipityFoundry/worldfoundry/wforge/world.py"), state="UNAVAILABLE",
                                     admission={"failed": "import: %s" % str(exc)[:120]}))
    try:
        W._c6()
        reg.register(ComponentRecord("world.c6.composed.v1", "world", W.C6ComposedWorld, W.C6ComposedWorld.capabilities, route="wrap",
                                     provenance=dict(PROV, source="archaeon/campaign6/worlds/runtime.py", owner="Archaeon"), license="repository"))
    except Exception as exc:                                    # noqa: BLE001
        reg.register(ComponentRecord("world.c6.composed.v1", "world", W.C6ComposedWorld, frozenset(), route="wrap",
                                     provenance=dict(PROV, source="archaeon/campaign6/worlds/runtime.py"), state="UNAVAILABLE",
                                     admission={"failed": "import: %s" % str(exc)[:120]}))
    from prometheus.toolbox.ref.worlds_grid import GridWorld
    reg.register(ComponentRecord("world.grid.v1", "world", GridWorld, GridWorld.capabilities, reference_of="world.grid", route="write",
                                 provenance=dict(PROV, source="prometheus/toolbox/ref/worlds_grid.py"), license="repository"))
    reg.register(ComponentRecord("substrate.flat.v1", "substrate", S.FlatInProcessSubstrate, S.FlatInProcessSubstrate.capabilities,
                                 reference_of="substrate.flat", route="write", provenance=dict(PROV, source="prometheus/toolbox/ref/substrates.py"), license="repository"))
    reg.register(ComponentRecord("substrate.kv.v1", "substrate", S.KVSubstrate, S.KVSubstrate.capabilities, route="write",
                                 provenance=dict(PROV, source="prometheus/toolbox/ref/substrates.py"), license="repository"))
    reg.register(ComponentRecord("substrate.stream.v1", "substrate", S.StreamSubstrate, S.StreamSubstrate.capabilities, route="write",
                                 provenance=dict(PROV, source="prometheus/toolbox/ref/substrates.py"), license="repository"))
    reg.register(ComponentRecord("substrate.mailbox.v1", "substrate", S.MailboxSubstrate, S.MailboxSubstrate.capabilities, route="write",
                                 provenance=dict(PROV, source="prometheus/toolbox/ref/substrates.py"), license="repository"))
    reg.register(ComponentRecord("rewrite.v1", "representation", P.random_rewrite_system, frozenset({"core.player.v1"}), route="write",
                                 provenance=dict(PROV, source="prometheus/toolbox/ref/players.py"), license="repository"))
    reg.register(ComponentRecord("statemachine.v2", "representation", P.random_statemachine_v2, frozenset({"core.player.v1"}), route="write",
                                 provenance=dict(PROV, source="prometheus/toolbox/ref/players.py"), license="repository"))
    reg.register(ComponentRecord("statemachine.v1", "representation", P.random_statemachine, frozenset({"core.player.v1"}), reference_of="statemachine",
                                 route="write", provenance=dict(PROV, source="prometheus/toolbox/ref/players.py"), license="repository"))
    reg.register(ComponentRecord("constant.v1", "representation", P.constant_player, frozenset({"core.player.v1"}), route="write",
                                 provenance=dict(PROV, source="prometheus/toolbox/ref/players.py"), license="repository"))
    reg.register(ComponentRecord("proteus.tape.v0", "representation", P.random_proteus_player, frozenset({"core.player.v1"}), route="wrap",
                                 provenance=dict(PROV, source="proteus/foundry/vm.py", owner="Proteus"), license="repository",
                                 state="PROVISIONAL" if P.proteus_available() else "UNAVAILABLE",
                                 admission={} if P.proteus_available() else {"failed": "proteus.foundry.vm not importable"}))
    reg.register(ComponentRecord("observer.trace.v1", "observer", O.TraceObserver, frozenset({"ext.events.v1"}), route="write", provenance=PROV, license="repository"))
    reg.register(ComponentRecord("observer.descriptor.v1", "observer", O.DescriptorObserver, frozenset({"ext.events.v1"}), route="write", provenance=PROV, license="repository"))
    reg.register(ComponentRecord("observer.series.v1", "observer", O.SeriesObserver, frozenset({"ext.events.v1"}), route="write", provenance=PROV, license="repository"))
    reg.register(ComponentRecord("objective.yield_net.v1", "objective", O.YieldNetObjective, frozenset(), route="write", provenance=PROV, license="repository"))
    reg.register(ComponentRecord("objective.survival.v1", "objective", O.SurvivalObjective, frozenset(), route="write", provenance=PROV, license="repository"))
    reg.register(ComponentRecord("objective.series_gain.v1", "objective", O.SeriesGainObjective, frozenset(), route="write", provenance=PROV, license="repository"))
    for kind, cls in Cn.ALL.items():
        reg.register(ComponentRecord(kind, "control", cls, frozenset(), route="write", provenance=PROV, license="repository"))
    from prometheus.toolbox.ref import transforms as T
    for kind, cls in T.ALL.items():
        reg.register(ComponentRecord(kind, "transform", cls, frozenset(), route="write", provenance=PROV, license="repository"))
    from prometheus.toolbox import search as SR
    reg.register(ComponentRecord("selector.truncation.v1", "selector", SR.TruncationSelector, frozenset(), route="write", provenance=PROV, license="repository"))
    reg.register(ComponentRecord("selector.map_elites.v1", "selector", SR.MapElitesSelector, frozenset(), route="write", provenance=PROV, license="repository"))
    return reg
