"""Cut: neat-python-codereclaimers-2008 -- NeuroEvolution of Augmenting Topologies (Stanley and Miikkulainen 2002), pure-Python implementation. Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 2 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: neat/genome.py 315-396, 621-702; neat/genes.py 75-184; neat/species.py 65-170; neat/stagnation.py 33-99; neat/reproduction.py 66-176, 178-332; neat/population.py 98-156; examples/xor/config-feedforward.
NOT read: structural mutations (436-620), innovation.py, attributes.py, config.py, networks, checkpointing, parallel. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('neat-python-codereclaimers-2008', mode="ANCESTRY_AWARE",
        inspected=['neat/genome.py 315-396, 621-702', 'neat/genes.py 75-184', 'neat/species.py 65-170', 'neat/stagnation.py 33-99', 'neat/reproduction.py 66-176, 178-332', 'neat/population.py 98-156', 'examples/xor/config-feedforward'],
        evidence=[('SOURCE_READ', 'vault:neat-python-codereclaimers-2008/upstream/tree/neat/genome.py:621-702'), ('SOURCE_READ', 'vault:neat-python-codereclaimers-2008/upstream/tree/neat/species.py:71-170'), ('SOURCE_READ', 'vault:neat-python-codereclaimers-2008/upstream/tree/neat/stagnation.py:33-99'), ('SOURCE_READ', 'vault:neat-python-codereclaimers-2008/upstream/tree/neat/reproduction.py:234-244'), ('SOURCE_READ', 'vault:neat-python-codereclaimers-2008/upstream/tree/neat/genome.py:328-335')],
        note="speciation by a compatibility distance, stagnation culling, smoothed min-max-normalised offspring allocation and innovation-aligned crossover; several defaults differ from the 2002 paper [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 2 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('compatibility_distance_over_innovation_aligned_node_and_connection_genes', human_name='distance (genome.py 621-702; genes.py 153-184)', status='ACCEPTED',
    mechanism='node part (sum of homologous gene distances + c_disjoint * disjoint) / max nodes; connection part (sum of homologous distances + c_disjoint * disjoint + c_excess * excess) / max connections, genes matched by innovation number; gene distance sums |weight difference| and an enable penalty times c_weight',
    input='two genomes', output='a distance', state='UNKNOWN', failure_landscape="by reading: the weight term is a SUM over matching genes divided by N, not the paper's mean weight difference",
    evidence_ref='vault:neat-python-codereclaimers-2008/upstream/tree/neat/genome.py:621-702', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='distance (genome.py 621-702; genes.py 153-184)', coverage={'input_topology': 'GRAPH', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC'})

o1 = c.organ('speciation_by_closest_representative_then_threshold_assignment', human_name='SpeciesSet.speciate (species.py 71-170)', status='ACCEPTED',
    mechanism='each species takes as representative the genome closest to its old one (no threshold); the rest join the nearest representative within compatibility_threshold (strict) or found a species; an optional controller moves the threshold toward a target species count',
    input='the population', output='species', state='representatives', failure_landscape='by reading: an existing species always survives speciation, however far its closest genome is',
    evidence_ref='vault:neat-python-codereclaimers-2008/upstream/tree/neat/species.py:71-170', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='SpeciesSet.speciate (species.py 71-170)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC'})

o2 = c.organ('stagnation_culling_with_species_elitism', human_name='DefaultStagnation (stagnation.py 33-99)', status='ACCEPTED',
    mechanism='a species is stagnant when it has not beaten its own historical best (by default the mean of its members) for max_stagnation generations (default 15); stagnant species are removed worst-first except the protected top species_elitism (default 0)',
    input='species histories', output='species to remove', state='history', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:neat-python-codereclaimers-2008/upstream/tree/neat/stagnation.py:33-99', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='DefaultStagnation (stagnation.py 33-99)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC', 'memory': 'WINDOW'})

o3 = c.organ('offspring_allocation_by_min_max_normalised_species_mean_moved_halfway_toward_target', human_name='reproduce (reproduction.py 66-176, 178-332)', status='ACCEPTED',
    mechanism="adjusted fitness = (species mean - global min) / max(1.0, global range); a species' size moves halfway toward its share and is forced to sum to the population size; within a species the top survival_threshold (0.2, at least 2) are uniform parents, plus elitism (default 0)",
    input='species and fitness', output='next generation', state='UNKNOWN', failure_landscape='by reading: the max(1.0, range) floor flattens allocation when fitness spreads are below 1; interspecies crossover > 0 can draw from already-emptied species',
    evidence_ref='vault:neat-python-codereclaimers-2008/upstream/tree/neat/reproduction.py:234-244', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='reproduce (reproduction.py 66-176, 178-332)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

o4 = c.organ('crossover_aligning_genes_by_innovation_with_disjoint_genes_from_the_fitter_parent', human_name='configure_crossover (genome.py 315-396)', status='ACCEPTED',
    mechanism='matching genes take each attribute 50/50 from either parent; disjoint and excess genes come only from the fitter parent, and on equal fitness genome2 is treated as fitter; feed-forward children skip genes that would create a cycle',
    input='two genomes', output='a child genome', state='UNKNOWN', failure_landscape='by reading: equal fitness does not inherit disjoint genes from both parents (the 2002 paper does)',
    evidence_ref='vault:neat-python-codereclaimers-2008/upstream/tree/neat/genome.py:328-335', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='configure_crossover (genome.py 315-396)', coverage={'input_topology': 'GRAPH', 'output_topology': 'GRAPH', 'stochasticity': 'SEEDED_RANDOM'})

c.reject('the rest of the body: structural mutations (436-620), innovation.py, attributes.py, config.py, networks, checkpointing, parallel', reason='OTHER', evidence='NOT READ; residue')
c.reject("'neat-python-codereclaimers-2008' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('new_topologies_are_shielded_by_speciation_while_species_compete_for_offspring_by_normalised_mean_fitness', condition='species compete for a fixed population; stagnant species are culled', world_rewards='species whose mean fitness rises', world_punishes='species that stagnate for 15 generations',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: NeuroEvolution of Augmenting Topologies (Stanley and Miikkulainen 2002), pure-Python implementation')

c.residue('LARGE_RESIDUE', ['not read: structural mutations (436-620), innovation.py, attributes.py, config.py, networks, checkpointing, parallel', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
