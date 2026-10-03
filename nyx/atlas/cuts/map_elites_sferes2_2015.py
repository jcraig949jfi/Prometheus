"""Cut: map-elites-sferes2-2015 -- MAP-Elites (Mouret and Clune 2015), the authors' sferes2 module. Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: map_elites.hpp 77-199; fit_map.hpp 61-68; test_map_elites.cpp 73-105.
NOT read: stat_map*, binary_map, plotting, wscript, the test's fitness body. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('map-elites-sferes2-2015', mode="ANCESTRY_AWARE",
        inspected=['map_elites.hpp 77-199', 'fit_map.hpp 61-68', 'test_map_elites.cpp 73-105'],
        evidence=[('SOURCE_READ', 'vault:map-elites-sferes2-2015/upstream/tree/map_elites.hpp:154-161'), ('SOURCE_READ', 'vault:map-elites-sferes2-2015/upstream/tree/map_elites.hpp:150-172'), ('SOURCE_READ', 'vault:map-elites-sferes2-2015/upstream/tree/map_elites.hpp:89-116')],
        note="the reference MAP-Elites: descriptors rounded into a grid, an epsilon band with a centre-distance tie-break, uniform parents [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('descriptor_to_cell_by_rounding_against_the_full_grid_size', human_name='_add_to_archive binning (map_elites.hpp 154-161, 187-194)', status='ACCEPTED',
    mechanism='p = min(1, descriptor), cell = round(p * n) clamped to n - 1',
    input='a descriptor', output='a cell index', state='UNKNOWN', failure_landscape='by reading: rounding against n makes cell 0 half-width and the last cell about 1.5 cells wide; negative descriptors are caught only by an assert',
    evidence_ref='vault:map-elites-sferes2-2015/upstream/tree/map_elites.hpp:154-161', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='_add_to_archive binning (map_elites.hpp 154-161, 187-194)', coverage={'input_topology': 'VECTOR', 'output_topology': 'VECTOR', 'stochasticity': 'DETERMINISTIC'})

o1 = c.organ('replacement_by_epsilon_better_or_epsilon_tie_closer_to_the_cell_centre', human_name='_add_to_archive (map_elites.hpp 150-172, 175-185)', status='ACCEPTED',
    mechanism='a living candidate enters an empty cell, or replaces the elite if better by more than epsilon, or if within epsilon and closer to the cell centre; the parent is stored beside it',
    input='a candidate', output='inserted or not', state='one elite and its parent per cell', failure_landscape='by reading: with epsilon > 0 a slightly worse but more central solution replaces the elite; the centre grid uses n - 1 while binning uses n (the test sets epsilon 0)',
    evidence_ref='vault:map-elites-sferes2-2015/upstream/tree/map_elites.hpp:150-172', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='_add_to_archive (map_elites.hpp 150-172, 175-185)', coverage={'input_topology': 'VECTOR', 'output_topology': 'DECISION', 'stochasticity': 'DETERMINISTIC', 'memory': 'ARCHIVE'})

o2 = c.organ('uniform_parent_pairs_over_occupied_cells_two_children_each', human_name='epoch (map_elites.hpp 89-116)', status='ACCEPTED',
    mechanism='each generation rebuilds the population from occupied cells and, size times, draws two parents uniformly, crosses and mutates them and inserts both children with their parent',
    input='the archive', output='2*size offspring', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:map-elites-sferes2-2015/upstream/tree/map_elites.hpp:89-116', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='epoch (map_elites.hpp 89-116)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

c.reject("the rest of the body: stat_map*, binary_map, plotting, wscript, the test's fitness body", reason='OTHER', evidence='NOT READ; residue')
c.reject("'map-elites-sferes2-2015' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('solutions_compete_only_within_their_behaviour_cell_with_no_pressure_on_parent_choice', condition='a 128x128 behaviour grid in the test; one elite per cell', world_rewards='beating the cell elite by epsilon, or tying it closer to the centre', world_punishes='anything else',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose="PURPOSE: MAP-Elites (Mouret and Clune 2015), the authors' sferes2 module")

c.residue('LARGE_RESIDUE', ["not read: stat_map*, binary_map, plotting, wscript, the test's fitness body", 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
