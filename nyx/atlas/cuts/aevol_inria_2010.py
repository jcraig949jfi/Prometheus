"""Cut: aevol-inria-2010 -- in silico experimental evolution of bacterial-like genomes (Knibbe, Beslon et al., aevol). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: src/libaevol/biochemistry/Promoter.cpp 35-473; src/libaevol/macros.h 105-180; src/libaevol/population/Individual.cpp 580-852; src/libaevol/phenotype/fuzzy/Vector_Fuzzy.cpp 183-338; src/libaevol/io/parameters/ParamValues.h 76-120; src/libaevol/biochemistry/mutations/mutators/DnaMutator.cpp 35-377; src/libaevol/population/selection/Selection_Asexual.cpp 33-103.
NOT read: transcription and translation search, translate_protein, the default fuzzy flavour, sexual selection, mutation application. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('aevol-inria-2010', mode="ANCESTRY_AWARE",
        inspected=['src/libaevol/biochemistry/Promoter.cpp 35-473', 'src/libaevol/macros.h 105-180', 'src/libaevol/population/Individual.cpp 580-852', 'src/libaevol/phenotype/fuzzy/Vector_Fuzzy.cpp 183-338', 'src/libaevol/io/parameters/ParamValues.h 76-120', 'src/libaevol/biochemistry/mutations/mutators/DnaMutator.cpp 35-377', 'src/libaevol/population/selection/Selection_Asexual.cpp 33-103'],
        evidence=[('SOURCE_READ', 'vault:aevol-inria-2010/upstream/tree/src/libaevol/biochemistry/Promoter.cpp:35-473'), ('SOURCE_READ', 'vault:aevol-inria-2010/upstream/tree/src/libaevol/population/Individual.cpp:580-852'), ('SOURCE_READ', 'vault:aevol-inria-2010/upstream/tree/src/libaevol/population/Individual.cpp:764-778'), ('SOURCE_READ', 'vault:aevol-inria-2010/upstream/tree/src/libaevol/biochemistry/mutations/mutators/DnaMutator.cpp:338-368'), ('SOURCE_READ', 'vault:aevol-inria-2010/upstream/tree/src/libaevol/population/selection/Selection_Asexual.cpp:33-103')],
        note="a circular genome is read for promoters (Hamming distance to a consensus), transcribed and translated into proteins that become fuzzy-set triangles; the summed phenotype is compared with a target and fitness falls exponentially with the gap [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('promoter_found_within_hamming_distance_of_a_consensus_with_expression_falling_with_distance', human_name='Promoter.cpp 35-473; macros.h 105-180', status='ACCEPTED',
    mechanism='a promoter exists where the 22-base window is within PROM_MAX_DIFF (4 in base 2) of the consensus, with circular wrap; its basal expression is 1 - distance / (max + 1)',
    input='the genome', output='promoters with expression', state='the promoter list', failure_landscape="by reading: the lagging-strand variants test macro names that differ from the leading strand's",
    evidence_ref='vault:aevol-inria-2010/upstream/tree/src/libaevol/biochemistry/Promoter.cpp:35-473', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='Promoter.cpp 35-473; macros.h 105-180', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC'})

o1 = c.organ('proteins_as_fuzzy_triangles_summed_by_activators_and_inhibitors_into_a_phenotype', human_name='Individual.cpp 580-852; Vector_Fuzzy.cpp 183-338', status='ACCEPTED',
    mechanism="codon classes decode (Gray code) to a triangle's mode m, half-width w (scaled by w_max 0.0333) and height h times expression; non-functional if any is zero; activators and inhibitors are summed separately and clipped, then combined and clipped at 0",
    input='proteins', output='a fuzzy phenotype', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:aevol-inria-2010/upstream/tree/src/libaevol/population/Individual.cpp:580-852', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='Individual.cpp 580-852; Vector_Fuzzy.cpp 183-338', coverage={'input_topology': 'SET', 'output_topology': 'VECTOR', 'stochasticity': 'DETERMINISTIC'})

o2 = c.organ('fitness_exponential_in_the_area_between_phenotype_and_target', human_name='compute_metabolic_error / compute_fitness (Individual.cpp 764-778)', status='ACCEPTED',
    mechanism='the metabolic error is the geometric area of phenotype minus target; fitness = exp(-1000 * error), or 0 for a flat phenotype',
    input='a phenotype', output='fitness', state='UNKNOWN', failure_landscape='by reading: the trapezoid area takes fabs of the signed mean, so segments whose difference changes sign are under-counted',
    evidence_ref='vault:aevol-inria-2010/upstream/tree/src/libaevol/population/Individual.cpp:764-778', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='compute_metabolic_error / compute_fitness (Individual.cpp 764-778)', coverage={'input_topology': 'VECTOR', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC'})

o3 = c.organ('mutation_urn_of_rearrangements_then_local_events_with_binomial_counts', human_name='DnaMutator.cpp 35-377', status='ACCEPTED',
    mechanism='per type, Binomial(genome length, rate) events (defaults 1e-5 for point, small indels up to 6, duplication, deletion, translocation, inversion) are drawn from an urn, rearrangements first; events crossing genome-size bounds are dropped',
    input='a genome', output='mutation events', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:aevol-inria-2010/upstream/tree/src/libaevol/biochemistry/mutations/mutators/DnaMutator.cpp:338-368', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='DnaMutator.cpp 35-377', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SEQUENCE', 'stochasticity': 'SEEDED_RANDOM', 'adaptation': 'STRUCTURE'})

o4 = c.organ('local_fitness_proportional_selection_in_a_toroidal_patch', human_name='Selection_Asexual.cpp 33-103', status='ACCEPTED',
    mechanism="by default each cell's offspring comes from a roulette over the 3x3 toroidal neighbourhood; global multinomial, fittest and no-selection are alternatives",
    input='neighbour fitness', output='a parent', state='UNKNOWN', failure_landscape='by reading: an even patch size writes past the end of the neighbour vector',
    evidence_ref='vault:aevol-inria-2010/upstream/tree/src/libaevol/population/selection/Selection_Asexual.cpp:33-103', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='Selection_Asexual.cpp 33-103', coverage={'input_topology': 'MATRIX', 'output_topology': 'SCALAR', 'stochasticity': 'SEEDED_RANDOM', 'competition': 'CONTENDS'})

c.reject('the rest of the body: transcription and translation search, translate_protein, the default fuzzy flavour, sexual selection, mutation application', reason='OTHER', evidence='NOT READ; residue')
c.reject("'aevol-inria-2010' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('a_genome_must_express_proteins_whose_summed_fuzzy_phenotype_matches_a_target_under_exponentially_harsh_selection_applied_locally', condition='fitness exp(-1000 * gap) applied by local roulette', world_rewards='phenotypes close to the target', world_punishes='even small phenotype gaps',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: in silico experimental evolution of bacterial-like genomes (Knibbe, Beslon et al., aevol)')

c.residue('LARGE_RESIDUE', ['not read: transcription and translation search, translate_protein, the default fuzzy flavour, sexual selection, mutation application', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
