"""Cut: qdax-airl-2022 -- quality-diversity algorithms in JAX (Lim, Chalumeau, Faldor et al., QDax 0.5.1). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: qdax/core/containers/mapelites_repertoire.py 55-137, 162-266, 364; qdax/core/emitters/repertoire_selectors/uniform_selector.py 38-54; qdax/core/emitters/standard_emitters.py 13-90; qdax/core/emitters/mutation_operators.py 175-226; qdax/core/emitters/cma_emitter.py 47-102, 169-357; qdax/core/containers/mome_repertoire.py 75-322; qdax/core/map_elites.py 148-195, 271-281.
NOT read: PGA-ME emitter, CMAES internals, polynomial operators, MultiEmitter, the CMA pool/opt/mega emitters, DNS repertoire, metrics, pareto_front.py. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('qdax-airl-2022', mode="ANCESTRY_AWARE",
        inspected=['qdax/core/containers/mapelites_repertoire.py 55-137, 162-266, 364', 'qdax/core/emitters/repertoire_selectors/uniform_selector.py 38-54', 'qdax/core/emitters/standard_emitters.py 13-90', 'qdax/core/emitters/mutation_operators.py 175-226', 'qdax/core/emitters/cma_emitter.py 47-102, 169-357', 'qdax/core/containers/mome_repertoire.py 75-322', 'qdax/core/map_elites.py 148-195, 271-281'],
        evidence=[('SOURCE_READ', 'vault:qdax-airl-2022/upstream/tree/qdax/core/containers/mapelites_repertoire.py:224-228'), ('SOURCE_READ', 'vault:qdax-airl-2022/upstream/tree/qdax/core/emitters/repertoire_selectors/uniform_selector.py:38-54'), ('SOURCE_READ', 'vault:qdax-airl-2022/upstream/tree/qdax/core/emitters/cma_emitter.py:169-357'), ('SOURCE_READ', 'vault:qdax-airl-2022/upstream/tree/qdax/core/containers/mome_repertoire.py:75-322')],
        note="the library behind leniabreeder: per-cell elitist repertoires, uniform parent choice, isoline variation, CMA-ME emitters and MOME Pareto cells; no CMA-MAE [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('grid_or_cvt_repertoire_with_batch_segment_max_and_strict_improvement', human_name='add / get_cells_indices (mapelites_repertoire.py 111-137, 173-266)', status='ACCEPTED',
    mechanism='descriptors map to the nearest centroid with no clipping; within a batch only the per-cell max survives (segment_max); a candidate replaces the incumbent iff strictly fitter; losers are redirected to an out-of-bounds index; empty cells hold -inf; CVT centroids are k-means++ on uniform samples',
    input='a batch', output='an updated repertoire', state='genotypes, fitness, descriptors per cell', failure_landscape='by reading: equal batch maxima in one cell both scatter to it, so the survivor is decided by JAX scatter semantics',
    evidence_ref='vault:qdax-airl-2022/upstream/tree/qdax/core/containers/mapelites_repertoire.py:224-228', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='add / get_cells_indices (mapelites_repertoire.py 111-137, 173-266)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC', 'memory': 'ARCHIVE'})

o1 = c.organ('parent_selection_uniform_over_occupied_cells', human_name='UniformSelector (uniform_selector.py 38-54)', status='ACCEPTED',
    mechanism='p = (1 - empty) / sum(1 - empty), where empty means fitness -inf; draws with replacement',
    input='the repertoire', output='parents', state='UNKNOWN', failure_landscape='by reading: an all-empty repertoire gives NaN probabilities; a genuine -inf score is indistinguishable from an empty cell',
    evidence_ref='vault:qdax-airl-2022/upstream/tree/qdax/core/emitters/repertoire_selectors/uniform_selector.py:38-54', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='UniformSelector (uniform_selector.py 38-54)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'SEEDED_RANDOM'})

o2 = c.organ('cma_me_emitter_ranking_new_cells_by_fitness_and_others_by_improvement_with_restart', human_name='cma_emitter.py 47-102, 169-357', status='ACCEPTED',
    mechanism='improvement = fitness - previous fitness of the cell (+inf for new cells); new cells are offset above all improvers and the batch sorted descending; restart when all improvements are negative after min_count, after max_count, or on a flat distribution, from one uniformly sampled elite; the code says it updates on the whole batch, unlike the paper',
    input='a scored batch', output='an updated search distribution', state='CMA state', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:qdax-airl-2022/upstream/tree/qdax/core/emitters/cma_emitter.py:169-357', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='cma_emitter.py 47-102, 169-357', coverage={'input_topology': 'SET', 'output_topology': 'VECTOR', 'stochasticity': 'SEEDED_RANDOM', 'adaptation': 'PARAMETER'})

o3 = c.organ('mome_cells_holding_a_capped_pareto_front', human_name='MOMERepertoire.add (mome_repertoire.py 75-322)', status='CANDIDATE',
    mechanism="candidates are inserted sequentially; each cell's front plus the candidate is re-filtered to its Pareto front and truncated to front_size",
    input='UNKNOWN', output='UNKNOWN', state='UNKNOWN', failure_landscape='by reading: a new non-dominated point that arrives when the front is full is cut off by the truncation; no crowding-based replacement',
    evidence_ref='vault:qdax-airl-2022/upstream/tree/qdax/core/containers/mome_repertoire.py:75-322', confidence='MEDIUM', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='MOMERepertoire.add (mome_repertoire.py 75-322)', coverage={'stochasticity': 'DETERMINISTIC', 'memory': 'ARCHIVE'})

c.reject('the rest of the body: PGA-ME emitter, CMAES internals, polynomial operators, MultiEmitter, the CMA pool/opt/mega emitters, DNS repertoire, metrics, pareto_front.py', reason='OTHER', evidence='NOT READ; residue')
c.reject("'qdax-airl-2022' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('solutions_compete_only_with_the_incumbent_of_their_behaviour_cell_while_parents_are_drawn_uniformly', condition='a fixed tessellation of behaviour space; one elite per cell; flat parent choice', world_rewards="being strictly better than the cell's incumbent, or filling a new cell", world_punishes='everything else (discarded)',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: quality-diversity algorithms in JAX (Lim, Chalumeau, Faldor et al., QDax 0.5.1)')

c.residue('LARGE_RESIDUE', ['not read: PGA-ME emitter, CMAES internals, polynomial operators, MultiEmitter, the CMA pool/opt/mega emitters, DNS repertoire, metrics, pareto_front.py', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
