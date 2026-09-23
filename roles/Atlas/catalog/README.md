# Ecosystem catalogue (world x organism x evolutionary pressure)

Currency: 2026-09-19 (catalog/1; generated from atlas.ecosystem on M1 -- regenerate, do not hand-edit counts).
Operator request: roles/Atlas/prompts/2026-09-19_alife_survey/. Record schema: SCHEMA.md.
Source of truth: ECOSYSTEMS.jsonl (one line per system; loaded by `python -m atlas harvest catalog`).

Six surveyor passes (open-endedness/curricula, digital evolution/chemistry, CA/self-organisation,
embodied/ecology, LLM-era/program evolution, frameworks/lists) were merged and de-duplicated
(393 records -> 352 external systems) and joined by 4 rows for Prometheus's own engines
(origin=prometheus) so one matrix covers both. Pointers only: nothing was downloaded.

## Totals

    ecosystems (external / prometheus)           352 / 4
    references (all / VERIFIED)                  834 / 642
    code repositories (all / VERIFIED)           327 / 315
    papers (all / VERIFIED)                      344 / 225
    declared relative links                      904
    systems with Prometheus coverage already     22

url_status is the surveyor's: VERIFIED = fetched/API-resolved; SEARCH_RESULT = seen in search; UNVERIFIED = from memory.

## By survey cluster

    llm_era_and_program_evolution                70
    open_endedness_curricula                     66
    cellular_and_continuous_self_organization    58
    digital_evolution_and_chemistry              53
    embodied_morphology_and_ecosystems           52
    discovered_via_list                          40
    frameworks_suites_and_lists                  38
    source_list                                  16
    prometheus_internal                          4

## Densest world x organism cells (external; Prometheus rows shown separately)

    text_or_code x llm_program                25  openelm, evoprompting, funsearch, llmatic, stop, discopop, reevo, aflow, adas, llamea, llm4ad, llm-sr, llm-gp, funsearch-jonppe, codeevolve, asi-arch,
    discrete_grid x policy                    22  project-origin, minigrid-babyai, neural-mmo, pcgrl, paired, amigo, dcd, robust-plr, accel, dsage, clutr, powderworld, diplr, minimax-jax, shed, xland-
    program_memory x machine_code             17  darwin-1961, core-war, coreworld, tierra, psoup, core-war-evolvers, network-tierra, cosmos, amoeba, physis, microgp-corewar, mactierra, salis, bff-com
    discrete_grid x ca_pattern                17  von-neumann-universal-constructor, codd-ca, langton-loops, byl-loop, chou-reggia-emergent-replicators, evoloop, larger-than-life, golly, sexyloop, gol
    discrete_grid x neural_net                16  ackley-littman-al, geb, evolvio, minimal-criterion-coevolution, growing-nca, self-classifying-mnist-nca, 3d-artefacts-nca, self-organising-textures-nc
    game_env x policy                         14  asymmetric-self-play, unity-ml-agents-mapoca, procgen, psro-open-ended-games, go-explore, pettingzoo, plr, minihack, jumanji, samplr, omni, jaxmarl, m
    physics_3d x policy                       14  openai-es, multiagent-competition, goal-gan, robosumo, hide-and-seek-autocurricula, smp-shared-modular-policies, xland-oel, brax, transform2act, metam
    physics_3d x morphology_plus_controller   13  karl-sims-evolved-virtual-creatures, golem-lipson-pollack, 3d-virtual-creature-evolution, nslc-virtual-creatures, novelty-search-local-competition, le
    continuous_field x kernel_params          12  imgep-lenia, holmes, leniax, flow-lenia, yuca-glaberish, lenia-large-scale-oee, leniabreeder, sensorimotor-lenia, flow-lenia-ai-scientist, asal-plus-p
    chemistry x reaction_rules                 9  scl-autopoiesis, autocatalytic-polymer-model, autogen-kampis, arms, squirm3, fraglets, hutton-membrane-cells, organic-builder, simsoup
    continuous_field x ca_pattern              7  gray-scott-pearson, ready, smoothlife, lenia, lenia-expanded-universe, asymptotic-lenia, glaberish
    discrete_grid x machine_code               6  avida, evolve-4, avida-ed, avida-origin-of-life, evita, nanopond
    physics_2d x neural_net                    6  polyworld, creatures, nolfi-floreano-predator-prey, novelty-search, minimal-criteria-novelty-search, keiwan-evolution
    text_or_code x llm_agent                   6  ai-scientist, godel-agent, hgm, dgm, ai-scientist-v2, sica
    particles x ca_pattern                     5  primordial-particle-systems, particle-life-clusters, particle-life-hunar, particle-lenia, particle-life-mohr
    game_env x llm_agent                       4  generative-agents, voyager, project-sid, intelligent-go-explore
    procedural_terrain x neural_net            4  poet, enhanced-poet, atep, llm-poet

    Prometheus:
    graph x policy                                NPE GraphWorld rounds r1-r8 (Nestor swarm)
    program_memory x machine_code                 SFE campaigns (Archaeon C1-C6 on the Serendipity Foundry Engine)
    program_memory x other:graph_organism         DEEP FRONTIER lineages (Archaeon scheduler)
    program_memory x other:tree_or_tape_genome      NPE CW01 campaign and loop (Nestor)

## Pressure kinds (external)

    explicit_fitness                             145
    implicit_replication                         92
    resource_competition                         68
    coevolution                                  34
    novelty                                      32
    human_or_model_judgment                      30
    curriculum_regret                            26
    quality_diversity                            25
    predator_prey                                21
    other:none                                   14
    environment_coevolution                      12
    minimal_criterion                            9
    other:learning_progress                      5
    other:lexicase                               3

## Useful queries

    -- systems in a cell, newest first, with verified code
    SELECT e.ecosystem_id, e.year_first, r.ref_uri FROM atlas.ecosystem e JOIN atlas.ecosystem_reference r USING (ecosystem_id)
    WHERE e.world_kind='continuous_field' AND r.kind='code' AND r.url_status='VERIFIED' ORDER BY e.year_first DESC;
    -- everything Prometheus already holds, with the path
    SELECT ecosystem_id, internal_coverage FROM atlas.ecosystem WHERE internal_coverage IS NOT NULL;
    -- a system's relatives (variants, parents, reimplementations)
    SELECT dst_key FROM atlas.edge WHERE relation='RELATED_TO' AND src_key='poet';

## Limits

- One label per axis per system; hybrids are flattened (the verbatim record keeps the nuance).
- Surveyor coverage is broad, not exhaustive; the source lists (cluster source_list) enumerate more.
- Earlier internal lists are wider but unverified: herakles/HERAKLES_HISTORICAL_COLLIDER_V0/A_FIELD_MAP.md
  (152 families, mostly from model memory) and aporia/docs/frontier_campaign_69/software_inventory.jsonl (463 entries).
- Candidate new ecosystems and experiments built on this: roles/Atlas/proposals/2026-09-19_cross_ecosystem/.
