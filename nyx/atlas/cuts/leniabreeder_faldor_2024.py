"""Cut: leniabreeder-faldor-2024 -- quality-diversity search over Lenia creatures (Faldor and Cully 2024, Leniabreeder). Techne batch 17 (#1190, a853fdf0b); ancestry-aware, Stage COARSE; SOURCE_READ on M3.
READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.
Read: common.py 9-45; main_me.py 51-119; main_aurora.py 78-129, 250-267; lenia/lenia.py 116-125, 162-184; qdax/core/containers/mapelites_repertoire.py 103-131, 212-320; qdax/core/emitters/mutation_operators.py 182-239; qdax/core/containers/unstructured_repertoire.py 37-128; qdax/core/aurora.py 52-81, 134-195.
NOT read: Lenia growth/kernels (lenia.py 1-115), patterns, the VAE, most of main_aurora.py, other qdax emitters, analysis. Nothing ran.
"""
from nyx.atlas.author import Cut

c = Cut('leniabreeder-faldor-2024', mode="ANCESTRY_AWARE",
        inspected=['common.py 9-45', 'main_me.py 51-119', 'main_aurora.py 78-129, 250-267', 'lenia/lenia.py 116-125, 162-184', 'qdax/core/containers/mapelites_repertoire.py 103-131, 212-320', 'qdax/core/emitters/mutation_operators.py 182-239', 'qdax/core/containers/unstructured_repertoire.py 37-128', 'qdax/core/aurora.py 52-81, 134-195'],
        evidence=[('SOURCE_READ', 'vault:leniabreeder-faldor-2024/upstream/tree/main_me.py:51-82'), ('SOURCE_READ', 'vault:leniabreeder-faldor-2024/upstream/tree/qdax/core/containers/mapelites_repertoire.py:285-292'), ('SOURCE_READ', 'vault:leniabreeder-faldor-2024/upstream/tree/qdax/core/emitters/mutation_operators.py:182-239'), ('SOURCE_READ', 'vault:leniabreeder-faldor-2024/upstream/tree/qdax/core/containers/unstructured_repertoire.py:37-128')],
        note="MAP-Elites (CVT) or AURORA over Lenia genotypes (kernel parameters plus a 32x32 initial pattern), with a viability filter that kills dying, border-touching or spreading creatures [READER-ASSISTED, 2026-10-03: a read-only reader agent (claude-opus-5-5, same family as Nyx) read the files below and returned line-cited notes; Nyx spot-checked 1 of the cited line ranges against the files (all matched) and wrote this cut. Nothing was run, imported or built (no bytecode written into the body). Stage A census 121 stays frozen; this body is cut under the operator's 2026-10-03 directive (item 4) and tracked with the other operator-directed bodies.]")

o0 = c.organ('viability_filter_killing_empty_full_or_spread_patterns_to_minus_infinity', human_name='fitness/descriptor parsing and kill rule (main_me.py 51-82; lenia.py 181-184)', status='ACCEPTED',
    mechanism='fitness is set to -inf if at any step a channel is everywhere below 0.1 (empty), the border mass exceeds 0.1 (full), or less than 0.9 of the mass lies in the central window (spread), or if fitness/descriptor is NaN; default fitness is negative angle variance, descriptors are mean mass and mean displacement',
    input='a rollout', output='fitness and descriptor', state='UNKNOWN', failure_landscape='by reading: linear_velocity ignores the metric operator and is the displacement between the last and the n_keep-th frame from the end',
    evidence_ref='vault:leniabreeder-faldor-2024/upstream/tree/main_me.py:51-82', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='fitness/descriptor parsing and kill rule (main_me.py 51-82; lenia.py 181-184)', coverage={'input_topology': 'SEQUENCE', 'output_topology': 'SCALAR', 'stochasticity': 'DETERMINISTIC'})

o1 = c.organ('cvt_map_elites_insertion_by_nearest_centroid_and_strict_improvement', human_name='MapElitesRepertoire.add (mapelites_repertoire.py 212-320)', status='ACCEPTED',
    mechanism='each candidate maps to its nearest CVT centroid; within a batch only the per-cell maximum survives; it replaces the incumbent iff strictly fitter; parents are uniform over occupied cells',
    input='a batch', output='an updated repertoire', state='1024 cells', failure_landscape='by reading: if every initial genotype is killed the repertoire is empty and parent sampling divides 0 by 0',
    evidence_ref='vault:leniabreeder-faldor-2024/upstream/tree/qdax/core/containers/mapelites_repertoire.py:285-292', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='MapElitesRepertoire.add (mapelites_repertoire.py 212-320)', coverage={'input_topology': 'SET', 'output_topology': 'SET', 'stochasticity': 'DETERMINISTIC', 'memory': 'ARCHIVE'})

o2 = c.organ('isoline_dd_variation_iso_noise_plus_line_noise_along_the_parent_difference', human_name='isoline (mutation_operators.py 182-239)', status='ACCEPTED',
    mechanism='x = (x1 + N(0, iso_sigma)) + (x2 - x1) * N(0, line_sigma), one line-noise draw per pair; defaults iso 0.005, line 0.05; the initial population is the seed pattern plus iso noise',
    input='two parents', output='a child', state='UNKNOWN', failure_landscape='UNKNOWN by run',
    evidence_ref='vault:leniabreeder-faldor-2024/upstream/tree/qdax/core/emitters/mutation_operators.py:182-239', confidence='HIGH', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='isoline (mutation_operators.py 182-239)', coverage={'input_topology': 'VECTOR', 'output_topology': 'VECTOR', 'stochasticity': 'SEEDED_RANDOM'})

o3 = c.organ('aurora_unstructured_archive_keeping_individuals_far_from_their_fitter_neighbours_in_a_learned_space', human_name='UnstructuredRepertoire (37-128); aurora.py 52-81', status='CANDIDATE',
    mechanism='archive plus offspring are ranked by the mean descriptor distance to their 3 nearest at-least-as-fit neighbours (+inf if none) and the top 1024 kept; descriptors are the mean VAE latent over the last frames, and after each update the VAE is retrained and every stored individual is re-described',
    input='UNKNOWN', output='UNKNOWN', state='the archive and the encoder', failure_landscape='UNKNOWN by run (the VAE and its training loop not read)',
    evidence_ref='vault:leniabreeder-faldor-2024/upstream/tree/qdax/core/containers/unstructured_repertoire.py:37-128', confidence='MEDIUM', portability='UNKNOWN', compatibility='UNKNOWN', utility='UNKNOWN',
    source_boundary='UnstructuredRepertoire (37-128); aurora.py 52-81', coverage={'stochasticity': 'SEEDED_RANDOM', 'representation_sensitivity': 'SENSITIVE'})

c.reject('the rest of the body: Lenia growth/kernels (lenia.py 1-115), patterns, the VAE, most of main_aurora.py, other qdax emitters, analysis', reason='OTHER', evidence='NOT READ; residue')
c.reject("'leniabreeder-faldor-2024' as one organ", reason='NAME_HAS_NO_EXECUTABLE_BOUNDARY', evidence='the mechanisms above are separable pieces of code')

c.pressure('a_lenia_creature_must_stay_alive_and_bounded_to_score_and_then_compete_only_within_its_behaviour_cell', condition='a viability filter kills dying or spreading creatures; survivors compete per descriptor cell (or by learned-space isolation)', world_rewards='bounded persistent creatures with low angular variance in empty cells', world_punishes='dying, border-touching or spreading patterns',
    cheat_control='UNKNOWN: not designed this pass', cost_class='UNKNOWN (nothing ran)', source_evidence='the organs above', purpose='PURPOSE: quality-diversity search over Lenia creatures (Faldor and Cully 2024, Leniabreeder)')

c.residue('LARGE_RESIDUE', ['not read: Lenia growth/kernels (lenia.py 1-115), patterns, the VAE, most of main_aurora.py, other qdax emitters, analysis', 'nothing ran', 'reader-assisted cut: line ranges spot-checked, not every line re-read by Nyx'],
          note='batch 17 first pass')
c.save(state='COARSE')
