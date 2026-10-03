"""Cut: sferes2-mouret-2014 -- C++ evolutionary computation framework (Mouret and Doncieux, sferes2). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: sferes/ea/dom_sort.hpp 46-225; sferes/fit/fitness.hpp 112-117, 166-191; sferes/ea/crowd.hpp 94-173; sferes/ea/nsga2.hpp 59-118, 164-262; sferes/ea/rank_simple.hpp 47-93; sferes/gen/evo_float.hpp 84-141; sferes/ea/cmaes.hpp 50-119; sferes/ea/ea.hpp 198-236, 338-343.
NOT read: cmaes.cpp, eps_moea, modifiers (novelty, diversity), SBX in full, eval/MPI/stat. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('sferes2-mouret-2014', mode="ANCESTRY_AWARE",
        inspected=['sferes/ea/dom_sort.hpp 46-225', 'sferes/fit/fitness.hpp 112-117, 166-191', 'sferes/ea/crowd.hpp 94-173', 'sferes/ea/nsga2.hpp 59-118, 164-262', 'sferes/ea/rank_simple.hpp 47-93', 'sferes/gen/evo_float.hpp 84-141', 'sferes/ea/cmaes.hpp 50-119', 'sferes/ea/ea.hpp 198-236, 338-343'],
        evidence=[('SOURCE_READ', 'vault:sferes2-mouret-2014/upstream/tree/sferes/ea/crowd.hpp:140-155'), ('SOURCE_READ', 'vault:sferes2-mouret-2014/upstream/tree/sferes/ea/nsga2.hpp:207-247'), ('SOURCE_READ', 'vault:sferes2-mouret-2014/upstream/tree/sferes/ea/rank_simple.hpp:51-93'), ('SOURCE_READ', 'vault:sferes2-mouret-2014/upstream/tree/sferes/gen/evo_float.hpp:84-141')],
        note="NSGA-II (maximising) with Deb's non-dominated sort, crowding distance and dominance tournaments; a deprecated rank selection; polynomial mutation; a CMA-ES wrapper [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('nsga2_survivor_selection_by_pareto_fronts_then_crowding_at_the_cut', human_name='_fill_nondominated_sort and crowding (nsga2.hpp 164-194; crowd.hpp 94-157; dom_sort.hpp 92-164)', status='ACCEPTED',
    mechanism="parents and children are merged; Deb's O(n^2) sort peels fronts (dominance is MAXIMISATION); whole fronts fill the next population while they fit; the cut front is sorted by crowding distance (ends 1e14, interior sum of normalised neighbour gaps) and truncated",
    input='merged population', output='next population', state='ranks and crowding', failure_landscape='by reading: the Crowd template parameter of GenericNsga2 is not used by _rank_crowd, which hard-codes the default crowding',
    evidence_ref='vault:sferes2-mouret-2014/upstream/tree/sferes/ea/crowd.hpp:140-155', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='_fill_nondominated_sort and crowding (nsga2.hpp 164-194; crowd.hpp 94-157; dom_sort.hpp 92-164)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC'})

o1 = c.organ('binary_tournament_preferring_dominance_then_crowding_then_a_coin', human_name='mating selection (nsga2.hpp 207-247)', status='ACCEPTED',
    mechanism='two random permutations feed four tournaments per four slots; the winner dominates, else has the larger crowding distance, else a coin decides; rank-based selection is commented out; population size must be a multiple of 4',
    input='the population', output='parents', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:sferes2-mouret-2014/upstream/tree/sferes/ea/nsga2.hpp:207-247', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='mating selection (nsga2.hpp 207-247)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

o2 = c.organ('deprecated_rank_selection_with_a_log_biased_index', human_name='RankSimple (rank_simple.hpp 51-93)', status='CANDIDATE',
    mechanism='after a partial sort keeps keep_rate*size, parents are drawn at index size - facteur*log(rand*kappa + 1) with kappa = coeff^(nb_keep+1) - 1; the header marks it DEPRECATED',
    input='UNKNOWN', output='UNKNOWN', state='UNKNOWN', failure_landscape='by reading (intent unclear): the index lands in the lower part of the sorted population, including slots the same loop overwrites, and can equal size',
    evidence_ref='vault:sferes2-mouret-2014/upstream/tree/sferes/ea/rank_simple.hpp:51-93', confidence='MEDIUM', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='RankSimple (rank_simple.hpp 51-93)', coverage={'stochasticity': 'SEEDED_RANDOM'})

o3 = c.organ('polynomial_mutation_and_cma_es_wrapper_on_unit_interval_genes', human_name='evo_float.hpp 84-141; cmaes.hpp 50-119', status='CANDIDATE',
    mechanism='each gene mutates with probability mutation_rate by the polynomial delta and is put back into [0,1]; the CMA-ES wrapper negates fitness (CMA minimises) and writes samples into the genotype without clamping',
    input='UNKNOWN', output='UNKNOWN', state='UNKNOWN', failure_landscape='by reading: CMA samples can leave [0,1]; the range is asserted only in debug builds',
    evidence_ref='vault:sferes2-mouret-2014/upstream/tree/sferes/gen/evo_float.hpp:84-141', confidence='MEDIUM', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='evo_float.hpp 84-141; cmaes.hpp 50-119', coverage={'stochasticity': 'SEEDED_RANDOM'})

c.reject('the rest of the body: cmaes.cpp, eps_moea, modifiers (novelty, diversity), SBX in full, eval/MPI/stat', reason='OTHER', evidence='NOT READ; residue')
c.reject("'sferes2-mouret-2014' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('solutions_are_kept_by_pareto_rank_with_spread_preferred_at_the_boundary', condition='mu+lambda elitism on Pareto fronts', world_rewards='non-dominated and well-spread solutions', world_punishes='dominated, crowded solutions',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: C++ evolutionary computation framework (Mouret and Doncieux, sferes2)')

c.residue('LARGE_RESIDUE', ['not read: cmaes.cpp, eps_moea, modifiers (novelty, diversity), SBX in full, eval/MPI/stat', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
