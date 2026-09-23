"""Cut: poet-original-2019 (Uber AI POET, Paired Open-Ended Trailblazer, Wang/Lehman/Clune/Stanley 2019; branch
original_poet; ancestry-aware, NARROW per the operator's 2026-09-18 refinery directive s2 and continued under the
2026-09-19b directive s2 "continue the POET cuts concurrently ... prefer completing at least one POET mechanism through
an independent ruling"). Read on M3: poet_distributed/poet_algo.py (pass_dedup/pass_mc 257-268, get_child_list 287-305,
adjust_envs_niches 307-341, remove_oldest 343-352, add_optimizer 151-170, delete_optimizer 171-178) and
poet_distributed/novelty.py 18-62 (the whole file). NOT read: es.py (the ES optimiser and its fiber workers), the
Box2D niches, model.py, reproduce_ops mutation operators, stats, logger.

Nothing ran against the full algorithm here (it needs Box2D + fiber/ipyparallel workers, absent on M3). novelty.py
DOES import and run standalone on M3 with numpy alone -- verified 2026-09-19 -- so the novelty organ is the
M3-RUNNABLE mechanism and is the one carried to a prediction packet.

Why POET now: it tests whether mechanism archaeology generalises beyond Lenia-shaped phenomena. POET's claim is
open-endedness through paired environment/agent co-evolution; the machinery that actually decides what survives is
three small, separable pieces of bookkeeping, and two of them contain defects visible only by reading.
"""
from nyx.atlas.author import Cut

A = "vault:poet-original-2019/upstream/tree/poet_distributed/poet_algo.py"
N = "vault:poet-original-2019/upstream/tree/poet_distributed/novelty.py"

c = Cut("poet-original-2019", mode="ANCESTRY_AWARE",
        inspected=["poet_distributed/poet_algo.py 151-178, 257-352", "poet_distributed/novelty.py 1-62"],
        evidence=[("SOURCE_READ", A + ":257-268"), ("SOURCE_READ", A + ":287-305"), ("SOURCE_READ", A + ":307-352"),
                  ("SOURCE_READ", A + ":151-178"), ("SOURCE_READ", N + ":18-62")],
        note="POET co-evolves a population of environments with a population of agents, and is presented as an "
             "open-ended process. The selection actually applied to environments is three separable pieces of "
             "bookkeeping: a two-sided MINIMAL CRITERION band that admits only environments the current agents find "
             "neither impossible nor trivial; a capacity rule that discards the OLDEST active environments (not the "
             "worst, not the least novel); and a novelty estimator over a hand-built 5-number environment descriptor. "
             "Reading them together exposes an asymmetry the paper does not foreground: the ACTIVE population is a "
             "FIFO window, while the NOVELTY ARCHIVE is never pruned, so novelty is always measured against every "
             "environment ever created, including ones long deleted.")

mc = c.organ("admission_only_of_environments_on_which_the_current_agent_scores_inside_a_two_sided_band_neither_unsolvable_nor_already_solved",
    human_name="pass_mc (poet_algo.py:264-268): if score < mc_lower or score > mc_upper: return False",
    status="ACCEPTED",
    mechanism="a candidate environment is evaluated with an EXISTING agent's parameters and admitted only if the "
              "resulting score falls inside [mc_lower, mc_upper]. Below the band the environment is unsolvable by the "
              "current population and carries no gradient; above it the environment is already solved and carries no "
              "challenge. The test is applied TWICE on different thetas: once in get_child_list with the PARENT's "
              "theta (poet_algo.py:296-299), and again in adjust_envs_niches after a targeted transfer picks the best "
              "theta over the whole population (poet_algo.py:330-333). So admission is relative to the population's "
              "current competence, not to any absolute property of the environment: the same environment can be "
              "rejected early and admitted later, which is what makes the curriculum move",
    input="a candidate environment configuration and an agent parameter vector", output="admit / reject",
    state="none in the test itself; the thresholds mc_lower and mc_upper are fixed run arguments",
    update="per candidate, at each environment-adjustment step",
    assumptions=["a scalar episode return is an adequate proxy for 'too hard' and 'too easy'",
                 "the band's two fixed thresholds remain meaningful as agent competence grows over the run"],
    fitness_value_in_ancestor="the goldilocks filter that keeps the environment population inside the agents' zone of "
                              "proximal development; POET's central selective device",
    failure_landscape="by reading: the band is FIXED while competence RISES, so the admissible region drifts toward "
                      "harder environments only as fast as the score scale allows; an environment whose difficulty is "
                      "not monotone in the score cannot be placed by this test; and because admission uses the best "
                      "transferred theta, a strong generalist agent can make genuinely novel environments look "
                      "'already solved' and get them rejected",
    human_prior="Wang, Lehman, Clune, Stanley 2019 (POET); the minimal-criterion idea from Brant & Stanley 2017 (MCC)",
    evidence_ref=A + ":264-268", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="pass_mc and its two call sites",
    coverage={"input_topology": "MIXED", "output_topology": "DECISION", "state_amount": "NONE",
              "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE", "uncertainty": "POINT"})

fifo = c.organ("capacity_enforced_by_deleting_the_oldest_active_environments_while_the_novelty_archive_is_never_pruned",
    human_name="remove_oldest (poet_algo.py:343-352) against add_optimizer/delete_optimizer (151-178)",
    status="ACCEPTED",
    mechanism="when the active population exceeds max_num_envs, POET computes num_removals and deletes that many "
              "environments taken from the FRONT of env_registry (an OrderedDict in insertion order) -- that is, the "
              "OLDEST, chosen with no reference to their score, their novelty, their productivity as transfer sources, "
              "or whether any agent still needs them. add_optimizer inserts each new environment into BOTH "
              "env_registry (active) and env_archive (novelty memory); delete_optimizer pops from optimizers and "
              "env_registry ONLY and never touches env_archive. The active population is therefore a FIFO sliding "
              "window over the environment lineage, while the novelty archive grows monotonically forever",
    input="the active environment registry and the capacity max_num_envs", output="the set of environments deleted",
    state="env_registry (bounded, FIFO) and env_archive (unbounded, append-only)", update="per adjustment step when over capacity",
    assumptions=["age is an acceptable proxy for exhaustedness -- that an older environment has already given what it had",
                 "nothing downstream needs a deleted environment, although the novelty archive still scores against it"],
    fitness_value_in_ancestor="a fixed compute budget: the number of concurrently optimised niches is what POET can afford",
    failure_landscape="by reading: a productive environment is discarded purely for being early, and a just-admitted "
                      "unproductive one survives; the retained set is determined by insertion order, so the population's "
                      "composition under capacity pressure is a function of ARRIVAL TIME rather than of value. Combined "
                      "with the unpruned archive, deleted environments keep suppressing the novelty of their own region "
                      "forever, so the search is pushed away from neighbourhoods it has abandoned and can no longer exploit",
    human_prior="POET's population cap; the archive/population split is standard in novelty search (Lehman & Stanley 2011)",
    evidence_ref=A + ":343-352", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="remove_oldest plus the registry/archive asymmetry in add_optimizer and delete_optimizer",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT",
              "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP"})

nov = c.organ("novelty_as_the_mean_distance_to_the_k_nearest_members_of_an_unpruned_archive_over_a_five_number_hand_built_environment_descriptor",
    human_name="compute_novelty_vs_archive + euclidean_distance + env2array (novelty.py:18-62)",
    status="ACCEPTED",
    mechanism="each environment is reduced to five numbers by env2array -- ground_roughness, pit_gap[0], pit_gap[1], "
              "stump_height[0], stump_height[1], with ZERO substituted whenever a list is empty -- then the candidate's "
              "distance to every archive member is computed and the mean of the k SMALLEST distances is returned as "
              "novelty (k=5 at the call site). The child list is sorted by this score, high to low, so it sets the "
              "order in which candidates are tried for admission. TWO defects are visible by reading: (1) "
              "compute_novelty_vs_archive calls euclidean_distance with normalize=False HARDCODED, so the norm vector "
              "[8,8,8,3,3] that exists in the function is never applied and roughness/pit features (range ~0-8) "
              "dominate stump features (range ~0-3) in every distance; (2) argsort()[:k] silently returns FEWER than k "
              "when the archive is smaller than k, so early in a run 'novelty' is the mean distance to the WHOLE "
              "archive (a global dispersion measure) and later it is the mean distance to the 5 nearest (a local "
              "density measure) -- the estimator changes what it measures as the run proceeds, with no discontinuity "
              "flagged anywhere",
    input="the unpruned env_archive and a candidate environment configuration", output="a scalar novelty score",
    state="the archive, which only ever grows", update="per candidate in get_child_list",
    assumptions=["five hand-chosen terrain numbers capture the environment differences that matter",
                 "an empty pit_gap/stump_height list is equivalent to a zero-valued one",
                 "the k-nearest mean is comparable across archive sizes"],
    fitness_value_in_ancestor="ordering candidate environments so the most different are tried for admission first",
    failure_landscape="by reading: novelty DEFLATES as the archive densifies, and the deflation is partly an artefact "
                      "of the estimator changing character at archive size k; unnormalised features mean a small "
                      "roughness change outweighs a large stump change; the zero-substitution makes 'no pit' and 'a pit "
                      "of width 0' identical, so a structural absence and a degenerate presence are the same point",
    human_prior="novelty search (Lehman & Stanley 2011); the descriptor is POET's own",
    evidence_ref=N + ":18-62", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="novelty.py in full (env2array, euclidean_distance, compute_novelty_vs_archive)",
    coverage={"input_topology": "SET", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT",
              "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE", "uncertainty": "POINT"})

c.reject("the ES optimiser (es.py), its fiber/ipyparallel workers, the Box2D bipedal-walker niches, model.py, the "
         "CPPN/reproduce_ops mutation operators, stats and logging",
         reason="OTHER", evidence="NOT READ; residue",
         note="the agent-side half of the pairing is a standard ES and is not what the operator's question is about; "
              "the environment-side selection is")
c.reject("'open-endedness' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY",
         evidence="the minimal criterion, the capacity discard and the novelty estimator are separable and have "
                  "different failure modes; POET's open-endedness claim is a property asserted of their composition")
c.reject("the n>m branch of euclidean_distance (novelty.py:44-50)", reason="OTHER",
         evidence=N + ":44-50",
         note="DEAD CODE for this descriptor: env2array always returns length 5, so n == m always and the "
              "ragged-length branch never executes. A latent generality that never fires; recorded, not cut")

c.edge(nov, mc, "feeds", note="novelty orders the child list; the minimal criterion decides admission from that order")
c.edge(fifo, nov, "feeds", note="deletion never prunes the archive novelty is measured against")

c.pressure("an_open_ended_environment_generator_must_keep_producing_challenges_its_agents_can_just_barely_learn_while_bounded_compute_forces_it_to_discard_environments_and_a_never_pruned_memory_keeps_penalising_the_regions_it_discarded",
    condition="a population of environments is co-evolved with a population of agents under a fixed niche budget; "
              "candidates are ordered by novelty against an archive that is never pruned and admitted only if a "
              "transferred agent scores inside a fixed two-sided band; when the budget is exceeded the oldest active "
              "environments are deleted",
    resource_or_constraint="max_num_envs concurrent niches; a fixed evaluation budget per adjustment step",
    failure_condition="for the open-endedness claim: the process stalls because the admissible band, measured against "
                      "a rising competence, and the deflating novelty estimator together stop admitting anything new",
    world_punishes="discarding environments by age while continuing to score novelty against them forever",
    world_rewards="generating environments that are different in the five descriptor numbers AND solvable-but-not-solved "
                  "by some current agent",
    observable_consequence="the admitted-environment rate over run time; the novelty score of admitted candidates as a "
                           "function of archive size; whether the deleted regions continue to suppress candidates near them",
    vacuity_condition="an environment space too small for the descriptor to separate, or a capacity never reached",
    trivial_shortcuts="mutating only the dominant unnormalised features (roughness, pit gaps) to score novelty cheaply "
                      "while leaving the stump features -- and the actual difficulty -- untouched",
    cheat_control="a candidate that differs ONLY in stump_height must score lower novelty than an equally-sized "
                  "difference in ground_roughness if the unnormalised-dominance reading is right; and an archive of "
                  "fewer than k members must yield the whole-archive mean rather than a k-nearest mean",
    cost_class="cluster-scale for the full algorithm; the novelty organ alone is milliseconds",
    source_evidence=N + ":18-62; " + A + ":264-268, 287-305, 343-352",
    purpose="PURPOSE: paired open-ended environment/agent co-evolution (Uber AI 2019)")

c.ancestry("superseded_by", "poet-enhanced-2020",
           note="Enhanced POET (branch master) replaces the hand-built 5-number descriptor and this novelty estimator "
                "with CPPN-generated environments and PATA-EC, and adds ANNECS; from the Techne record")
c.ancestry("algorithm_from", "minimal criterion coevolution (Brant & Stanley 2017); novelty search (Lehman & Stanley 2011)",
           note="from the source and the paper")
c.residue("PARTIALLY_EXPLAINED",
          ["the ES half (es.py) and the Box2D niches unread -- the agent side of the pairing",
           "the mutation operators in reproduce_ops.py unread, so what 'a child environment' can be is not characterised",
           "the full algorithm did not run on M3 (Box2D + fiber workers absent); only novelty.py is executable here",
           "PATA-EC and ANNECS live in poet-enhanced-2020 and are a separate cut"],
          note="three mechanisms located and bound to the fossil's lines; the novelty organ is M3-RUNNABLE and is the "
               "one carried to a prediction packet, per the directive's preference for one POET mechanism completed "
               "through an independent ruling over several new cuts")
c.save(state="COARSE")
