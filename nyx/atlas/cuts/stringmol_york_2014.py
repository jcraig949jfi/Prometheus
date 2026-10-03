"""Cut: stringmol-york-2014 -- artificial chemistry of self-copying strings that bind and execute one another (Hickinbotham et al., Stringmol). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: src/stringPM.cpp 358-427, 660-686, 1680-2003; src/agent.cpp 314-435, 588-612; src/alignment.cpp 38-123, 214-426; src/opcodes.cpp 61-302, 451-545, 1009-1152.
NOT read: spatial variant, setup, main and trial types, comass variants, OpcodeAdjacent, the blosum format. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('stringmol-york-2014', mode="ANCESTRY_AWARE",
        inspected=['src/stringPM.cpp 358-427, 660-686, 1680-2003', 'src/agent.cpp 314-435, 588-612', 'src/alignment.cpp 38-123, 214-426', 'src/opcodes.cpp 61-302, 451-545, 1009-1152'],
        evidence=[('SOURCE_READ', 'vault:stringmol-york-2014/upstream/tree/src/alignment.cpp:42-49'), ('SOURCE_READ', 'vault:stringmol-york-2014/upstream/tree/src/opcodes.cpp:61-302'), ('SOURCE_READ', 'vault:stringmol-york-2014/upstream/tree/src/opcodes.cpp:1009-1123'), ('SOURCE_READ', 'vault:stringmol-york-2014/upstream/tree/src/stringPM.cpp:358-427')],
        note="no fitness: strings meet stochastically, bind with a probability set by a Smith-Waterman alignment of one with the other's complement, execute each other's code at an energy cost, cleave products and decay [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('binding_probability_from_a_capped_smith_waterman_score_of_complementary_strings', human_name='encounter and bind (stringPM.cpp 660-686, 1740-1790; alignment.cpp 38-53)', status='ACCEPTED',
    mechanism="an unbound string meets a partner with probability 1 - (1 - area ratio)^n; the pair aligns one string's complement against the other; l = the shorter matched span, bind probability 0 if l <= 2 else min(score, l - 1.124) / (l - 1.124) (commented 'BRUTAL HACK'); binding costs one energy unit; the later-matching string becomes the active one",
    input='two strings', output='bound or not', state='a per-species-pair alignment cache', failure_landscape='by reading: the cache list is passed by value, so its head update is lost when the list is empty; a second alignment is computed and discarded',
    evidence_ref='vault:stringmol-york-2014/upstream/tree/src/alignment.cpp:42-49', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='encounter and bind (stringPM.cpp 660-686, 1740-1790; alignment.cpp 38-53)', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'DECISION', 'stochasticity': 'SEEDED_RANDOM'})

o1 = c.organ('template_addressed_copy_with_indels_and_adjacent_substitutions_executed_at_unit_energy_cost', human_name='execute loop and opcodes (stringPM.cpp 1806-1894; opcodes.cpp 61-302, 451-545)', status='ACCEPTED',
    mechanism='opcodes search ($, deterministic best alignment of the complemented template), move, copy (=, with indel probability indelrate and substitution to an adjacent opcode at subrate), increment, toggle, if-label (success probability (score/len)^len), cleave and terminate; every executed op costs one energy unit',
    input='the bound pair', output='a modified string, possibly a product', state='four pointers', failure_landscape="by reading: '}' falls through into default; a deletion advances the instruction pointer instead of the read pointer; a fixed 128-byte memset on a variable buffer",
    evidence_ref='vault:stringmol-york-2014/upstream/tree/src/opcodes.cpp:61-302', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='execute loop and opcodes (stringPM.cpp 1806-1894; opcodes.cpp 61-302, 451-545)', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SEQUENCE', 'stochasticity': 'SEEDED_RANDOM'})

o2 = c.organ('cleave_releasing_the_tail_as_a_new_molecule', human_name='OpcodeCleave (opcodes.cpp 1009-1123)', status='ACCEPTED',
    mechanism='the string from the active flow pointer to the end becomes a new agent and the parent is truncated; zero-length parents are destroyed',
    input='a bound pair', output='a product molecule', state='UNKNOWN', failure_landscape='by reading: the agent counter is never advanced here (pointer incremented instead of count) and the next-list head is passed by value, so a product can be lost when that list is empty',
    evidence_ref='vault:stringmol-york-2014/upstream/tree/src/opcodes.cpp:1009-1123', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='OpcodeCleave (opcodes.cpp 1009-1123)', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SEQUENCE', 'stochasticity': 'DETERMINISTIC'})

o3 = c.organ('constant_decay_and_a_finite_energy_budget', human_name='decay and energy gate (agent.cpp 588-612; stringPM.cpp 358-427, 1958-1997)', status='ACCEPTED',
    mechanism='each selected agent first decays with probability decayrate (default 1/65^2), freeing its partner; no reaction happens without energy; default mutation rates indel 3.06e-8, substitution 1e-5',
    input='UNKNOWN', output='UNKNOWN', state='energy', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:stringmol-york-2014/upstream/tree/src/stringPM.cpp:358-427', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='decay and energy gate (agent.cpp 588-612; stringPM.cpp 358-427, 1958-1997)', coverage={'stochasticity': 'SEEDED_RANDOM', 'resource_dependence': 'SHARED_RESOURCE'})

c.reject('the rest of the body: spatial variant, setup, main and trial types, comass variants, OpcodeAdjacent, the blosum format', reason='OTHER', evidence='NOT READ; residue')
c.reject("'stringmol-york-2014' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('a_string_persists_only_by_being_copied_faster_than_it_decays_under_a_finite_energy_supply', condition='constant decay; every executed operation consumes energy; encounters are random', world_rewards='strings that bind well and copy themselves accurately', world_punishes='strings that are not copied',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: artificial chemistry of self-copying strings that bind and execute one another (Hickinbotham et al., Stringmol)')

c.residue('LARGE_RESIDUE', ['not read: spatial variant, setup, main and trial types, comass variants, OpcodeAdjacent, the blosum format', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
