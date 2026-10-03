"""Cut: pyribs-icaros-2020 -- quality-diversity optimisation library (pyribs; Fontaine and Nikolaidis CMA-ME / CMA-MAE). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: ribs/archives/_grid_archive.py 105-182, 362-410, 474-714, 770-848, 920-921; ribs/archives/_utils.py 76-93; ribs/emitters/_evolution_strategy_emitter.py 82-146, 183-265; ribs/emitters/rankers.py 136-203; ribs/emitters/opt/_cma_es.py 239-247, 275-299; ribs/schedulers/_scheduler.py 180-412; ribs/schedulers/_bandit_scheduler.py 205-297, 418-419.
NOT read: CVT and other archives, ArrayStore, other emitters, CMA-ES internals beyond the weights, other rankers. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('pyribs-icaros-2020', mode="ANCESTRY_AWARE",
        inspected=['ribs/archives/_grid_archive.py 105-182, 362-410, 474-714, 770-848, 920-921', 'ribs/archives/_utils.py 76-93', 'ribs/emitters/_evolution_strategy_emitter.py 82-146, 183-265', 'ribs/emitters/rankers.py 136-203', 'ribs/emitters/opt/_cma_es.py 239-247, 275-299', 'ribs/schedulers/_scheduler.py 180-412', 'ribs/schedulers/_bandit_scheduler.py 205-297, 418-419'],
        evidence=[('SOURCE_READ', 'vault:pyribs-icaros-2020/upstream/tree/ribs/archives/_grid_archive.py:634-638'), ('SOURCE_READ', 'vault:pyribs-icaros-2020/upstream/tree/ribs/archives/_grid_archive.py:509-515'), ('SOURCE_READ', 'vault:pyribs-icaros-2020/upstream/tree/ribs/emitters/_evolution_strategy_emitter.py:183-265'), ('SOURCE_READ', 'vault:pyribs-icaros-2020/upstream/tree/ribs/schedulers/_bandit_scheduler.py:274-280')],
        note="archives whose admission compares against a per-cell THRESHOLD that, with a learning rate below 1 (CMA-MAE), anneals toward the objectives seen, so the elite can be displaced by a worse solution [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('grid_archive_admission_against_a_per_cell_threshold', human_name='GridArchive.add / index_of (_grid_archive.py 362-410, 518-714)', status='ACCEPTED',
    mechanism='a measure is binned as ((dims*(m - lower) + 1e-6) / interval) clipped; a candidate is admitted iff objective > cell threshold (strict; empty cells take threshold_min, default -inf); status 2 new, 1 improved; within a batch argmax wins (first on ties) and statuses are computed against the pre-batch archive',
    input='a batch', output='statuses and an updated archive', state='per-cell threshold and elite', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:pyribs-icaros-2020/upstream/tree/ribs/archives/_grid_archive.py:634-638', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='GridArchive.add / index_of (_grid_archive.py 362-410, 518-714)', coverage={'input_topology': 'SET', 'output_topology': 'VECTOR', 'stochasticity': 'DETERMINISTIC', 'memory': 'ARCHIVE'})

o1 = c.organ('cma_mae_threshold_annealing_toward_the_mean_admitted_objective', human_name='threshold update (_grid_archive.py 474-516, 770-848)', status='ACCEPTED',
    mechanism='batch rule: ratio = (1 - lr)^k, new threshold = ratio*threshold + mean(objectives)*(1 - ratio) over the k admissible candidates of a cell; single rule threshold*(1 - lr) + objective*lr; lr = 1 (default) recovers MAP-Elites',
    input='admitted objectives', output='a new threshold', state='thresholds', failure_landscape="by reading: with lr < 1 a candidate between the threshold and the elite replaces the elite, so the archive's objective sum can fall",
    evidence_ref='vault:pyribs-icaros-2020/upstream/tree/ribs/archives/_grid_archive.py:509-515', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='threshold update (_grid_archive.py 474-516, 770-848)', coverage={'input_topology': 'VECTOR', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC', 'adaptation': 'PARAMETER'})

o2 = c.organ('evolution_strategy_emitter_ranking_by_status_then_improvement_with_filter_and_restart', human_name='EvolutionStrategyEmitter (82-146, 183-265); rankers 136-203; CMA-ES weights 239-247', status='ACCEPTED',
    mechanism="default ranker '2imp' sorts by (status, value) descending; with selection 'filter' only solutions that changed the archive are parents; CMA weights log(n+0.5) - log(i), normalised; restart from one uniformly sampled elite when CMA stops or nothing new was added",
    input='a scored batch', output='a new search distribution', state='CMA state', failure_landscape="by reading: an empty archive makes the restart's sample_elites raise",
    evidence_ref='vault:pyribs-icaros-2020/upstream/tree/ribs/emitters/_evolution_strategy_emitter.py:183-265', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='EvolutionStrategyEmitter (82-146, 183-265); rankers 136-203; CMA-ES weights 239-247', coverage={'input_topology': 'SET', 'output_topology': 'VECTOR', 'stochasticity': 'SEEDED_RANDOM', 'adaptation': 'PARAMETER'})

o3 = c.organ('bandit_scheduler_choosing_emitters_by_a_ucb1_variant', human_name='BanditScheduler (_bandit_scheduler.py 205-297, 418-419)', status='ACCEPTED',
    mechanism='ucb1 = success/selection + zeta*sqrt(log(sum of successes)/selection), zeta 0.05; never-selected emitters get inf; selection counts solutions emitted, success counts non-zero statuses; the plain Scheduler asks every emitter every iteration and does not choose',
    input='emitter statistics', output='the active emitters', state='counts', failure_landscape='by reading: the log uses total SUCCESSES (UCB1 uses total plays); all-zero successes give log(0) and NaN scores',
    evidence_ref='vault:pyribs-icaros-2020/upstream/tree/ribs/schedulers/_bandit_scheduler.py:274-280', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='BanditScheduler (_bandit_scheduler.py 205-297, 418-419)', coverage={'input_topology': 'VECTOR', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC'})

c.reject('the rest of the body: CVT and other archives, ArrayStore, other emitters, CMA-ES internals beyond the weights, other rankers', reason='OTHER', evidence='NOT READ; residue')
c.reject("'pyribs-icaros-2020' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('a_solution_is_kept_if_it_beats_its_cell_s_threshold_which_may_be_annealed_below_the_elite', condition='a behaviour grid; admission against a per-cell threshold; emitters rewarded for archive changes', world_rewards='new cells and improvements over the threshold', world_punishes="solutions below their cell's threshold",
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: quality-diversity optimisation library (pyribs; Fontaine and Nikolaidis CMA-ME / CMA-MAE)')

c.residue('LARGE_RESIDUE', ['not read: CVT and other archives, ArrayStore, other emitters, CMA-ES internals beyond the weights, other rankers', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
