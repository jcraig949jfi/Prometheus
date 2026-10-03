"""Cut: mabe2-ofria-2019 -- Modular Agent-Based Evolver 2 (Ofria lab), C++20 framework composed by scripts. Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: source/select/SelectTournament.hpp 1-133; source/select/SelectElite.hpp 1-106; source/select/SelectRoulette.hpp 1-107; source/core/MABE.hpp 648-694, 768-826; source/core/MABEBase.hpp 127-145; source/placement/RandomReplacement.hpp 1-94; source/placement/MaxSizePlacement.hpp 1-103; source/orgs/BitsOrg.hpp 30-111; settings/NK.mabe 1-82.
NOT read: lexicase and fitness-sharing selectors, schedulers, evaluators, VirtualCPU and AvidaGP organisms, Population.hpp, Emplode, the Empirical submodule. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('mabe2-ofria-2019', mode="ANCESTRY_AWARE",
        inspected=['source/select/SelectTournament.hpp 1-133', 'source/select/SelectElite.hpp 1-106', 'source/select/SelectRoulette.hpp 1-107', 'source/core/MABE.hpp 648-694, 768-826', 'source/core/MABEBase.hpp 127-145', 'source/placement/RandomReplacement.hpp 1-94', 'source/placement/MaxSizePlacement.hpp 1-103', 'source/orgs/BitsOrg.hpp 30-111', 'settings/NK.mabe 1-82'],
        evidence=[('SOURCE_READ', 'vault:mabe2-ofria-2019/upstream/tree/source/select/SelectTournament.hpp:1-133'), ('SOURCE_READ', 'vault:mabe2-ofria-2019/upstream/tree/source/select/SelectElite.hpp:34-40'), ('SOURCE_READ', 'vault:mabe2-ofria-2019/upstream/tree/source/core/MABE.hpp:768-826'), ('SOURCE_READ', 'vault:mabe2-ofria-2019/upstream/tree/source/select/SelectRoulette.hpp:1-107')],
        note="selection, placement and mutation are separate modules composed by a script; the NK example is elite plus tournament(7) with generational replacement [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('tournament_selection_strict_best_of_t_random_draws', human_name='SelectTournament (1-133)', status='ACCEPTED',
    mechanism='for each birth draw t positions with replacement (default 7), redrawing empty cells, and replicate the strictly best (first drawn wins ties)',
    input='a population', output='births', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:mabe2-ofria-2019/upstream/tree/source/select/SelectTournament.hpp:1-133', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='SelectTournament (1-133)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

o1 = c.organ('elite_selection_with_a_top_count_that_the_loop_decrements_in_place', human_name='SelectElite (1-106)', status='ACCEPTED',
    mechanism='organisms are walked from the highest fitness, each replicated ceil(births / top_count--) times; top_count is the configured member variable',
    input='a population', output='births', state='top_count', failure_landscape='by reading: the loop decrements the member top_count, so after one call it is 0 and later calls replicate nothing (the NK script calls elite selection every update; whether the config is re-applied each update was not checked)',
    evidence_ref='vault:mabe2-ofria-2019/upstream/tree/source/select/SelectElite.hpp:34-40', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='SelectElite (1-106)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC'})

o2 = c.organ('birth_placement_modules_append_or_random_replacement_with_generational_swap', human_name='DoBirth / placement (MABE.hpp 648-694, 768-826; RandomReplacement; MaxSizePlacement)', status='ACCEPTED',
    mechanism="offspring are made mutated or cloned and placed by the population's placement module: append by default, random replacement of a position other than the parent's, or append up to a maximum then replace; REPLACE_WITH empties the target first, so the NK script is generational",
    input='offspring', output='positions', state='UNKNOWN', failure_landscape='by reading: random replacement spins forever in a size-1 population holding the parent; max_pop_size has no initialiser',
    evidence_ref='vault:mabe2-ofria-2019/upstream/tree/source/core/MABE.hpp:768-826', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='DoBirth / placement (MABE.hpp 648-694, 768-826; RandomReplacement; MaxSizePlacement)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

o3 = c.organ('roulette_selection_and_binomial_bit_flip_mutation', human_name='SelectRoulette (1-107); BitsOrg (30-111)', status='ACCEPTED',
    mechanism='roulette draws each birth from an index map of fitnesses (select and birth populations must differ); bit organisms toggle Binomial(mut_prob 0.01, N) distinct random bits',
    input='UNKNOWN', output='UNKNOWN', state='UNKNOWN', failure_landscape='by reading: negative or all-zero fitness is not guarded',
    evidence_ref='vault:mabe2-ofria-2019/upstream/tree/source/select/SelectRoulette.hpp:1-107', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='SelectRoulette (1-107); BitsOrg (30-111)', coverage={'stochasticity': 'SEEDED_RANDOM'})

c.reject('the rest of the body: lexicase and fitness-sharing selectors, schedulers, evaluators, VirtualCPU and AvidaGP organisms, Population.hpp, Emplode, the Empirical submodule', reason='OTHER', evidence='NOT READ; residue')
c.reject("'mabe2-ofria-2019' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('whatever_the_script_composes_truncation_local_rank_or_fitness_proportional_over_an_evaluator_trait', condition='modules are composed per experiment; the NK script uses elite plus tournament(7) with generational replacement', world_rewards='high trait values', world_punishes='low trait values',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: Modular Agent-Based Evolver 2 (Ofria lab), C++20 framework composed by scripts')

c.residue('LARGE_RESIDUE', ['not read: lexicase and fitness-sharing selectors, schedulers, evaluators, VirtualCPU and AvidaGP organisms, Population.hpp, Emplode, the Empirical submodule', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
