"""The NAMED boolean3 population: hand-built controls and the interface artifact.

THE FROZEN USE_A REGISTRY IS NOT TOUCHED. `proteus/integration/PLAYER_REGISTRY.json` keeps its 64
specimens, its registry_id and every organism_id exactly as fossilised. New candidates live under
a separate interface name, `proteus.boolean3.v0`, in their own artifact. Old specimens are never
redefined; they simply are not members of this population.

THE CONTROLS ARE HAND-BUILT, NOT COMPILED. That is deliberate: if they came out of
`compile_boolean` they would test the compiler against itself. Written by hand, they are an
INDEPENDENT check that the input channel really does deliver three distinguishable bits, and the
tests compare them against the compiler's output for the same functions.

    ID0 / ID1 / ID2   positive controls: output equals input j, so output changes with input j
    BLIND             negative control: emits a constant and never executes IN at all

A player receives only its declared channels. Nothing here hands a candidate the task oracle, a
truth table, or the final evaluation set.
"""
from __future__ import annotations

from proteus.eval.boolean import (INTERFACE_VERSION, N_INPUTS, N_REGS, OUT_CAP, R_CHANNEL,
                                  TAPE_WORDS, TICK_BUDGET)

# declared opcodes, repeated here so a hand-built program does not import the compiler's intent
HALT, LDC, XOR, IN, OUT = 1, 3, 12, 21, 23


def _manifest(genome):
    return {"schema_version": "proteus.player_manifest.v0", "n_regs": N_REGS,
            "tape_words": TAPE_WORDS, "genome": list(genome), "code_writable": False,
            "persist": "none", "tick_budget": TICK_BUDGET, "out_cap": OUT_CAP}


def _identity(j):
    """Read all three inputs in order, emit the j-th. r15 is 0 and selects channel 0."""
    g = []
    for i in range(N_INPUTS):
        g += [IN, i, R_CHANNEL, 0]
    g += [OUT, j, R_CHANNEL, 0]
    g += [HALT, 0, 0, 0]
    return _manifest(g)


ID0 = _identity(0)
ID1 = _identity(1)
ID2 = _identity(2)

#: Negative control. Emits 1 always. It never executes IN, so no input can reach the output.
BLIND = _manifest([LDC, 0, 1, 0,
                   OUT, 0, R_CHANNEL, 0,
                   HALT, 0, 0, 0])

POSITIVE_CONTROLS = {"ID0": (ID0, 0), "ID1": (ID1, 1), "ID2": (ID2, 2)}
NEGATIVE_CONTROLS = {"BLIND": BLIND}


def population():
    """The named population as data. Roles are declared; nothing is scored or ranked."""
    from proteus.eval.identity import (FAMILY_PROGRAM, REPR_PLAYER_MANIFEST_V0,
                                       artifact_manifest, organism_ref)
    members = []
    for name, (man, j) in sorted(POSITIVE_CONTROLS.items()):
        art = artifact_manifest(FAMILY_PROGRAM, man, REPR_PLAYER_MANIFEST_V0, "proteus.vm.v0.4")
        members.append({"name": name, "role": "positive_control",
                        "sensitive_to_input": j, "manifest": man,
                        "organism_ref": organism_ref(art)})
    for name, man in sorted(NEGATIVE_CONTROLS.items()):
        art = artifact_manifest(FAMILY_PROGRAM, man, REPR_PLAYER_MANIFEST_V0, "proteus.vm.v0.4")
        members.append({"name": name, "role": "negative_control",
                        "sensitive_to_input": None, "manifest": man,
                        "organism_ref": organism_ref(art)})
    return {
        "schema_version": "proteus.boolean3_population.v1",
        "interface_version": INTERFACE_VERSION,
        "n_inputs": N_INPUTS,
        "channel_contract": {
            "inputs": "ONE channel carrying exactly 3 values in {0,1}, input 0 first",
            "n_out": 1,
            "output": "one value in {0,1} on channel 0",
            "reads": "IN consumes the channel in order; cursors are tick-scoped",
        },
        "members": members,
        "frozen_registry_untouched": "proteus/integration/PLAYER_REGISTRY.json",
        "claim_boundary": ("Controls establish that the CHANNEL can carry three distinguishable "
                           "bits. They are not evidence that any frozen specimen is an agent, "
                           "and no specimen from the USE_A registry is a member of this "
                           "population."),
    }
