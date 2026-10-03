"""Cut: poet-enhanced-2020 (Uber AI Enhanced POET, Wang, Rawal, Lehman, Gao, Clune, Stanley 2020; uber-research/poet @ 8669a17e,
branch master). Ancestry-aware, NARROW per the operator's 2026-09-18 refinery directive s2 ("extract exactly two mechanisms
first: environment discard / minimal-criterion boundary; PATA-EC recomputation over world x contemporary population") and
the 2026-10-03 directive's queue. Read on M3 by Nyx (no reader agent): poet_distributed/novelty.py 1-44 (all),
poet_distributed/stats.py 1-47 (all), poet_distributed/es.py 580-624 (update_pata_ec, evaluate_transfer) and the imports
16-23, poet_distributed/poet_algo.py 160-361 (transfer, health check, pass_dedup, pass_mc, get_new_env, get_child_list,
adjust_envs_niches, remove_oldest, optimize). NOT read: the ES optimiser body (es.py 1-579), the Box2D bipedal-walker
niche, the CPPN terrain generator (niches/box2d/cppn.py), reproduce_ops.py, the logger, master.py.

Nothing ran here (Box2D and fiber workers absent on M3). Unlike poet-original's novelty.py, PATA-EC is NOT standalone: it
needs every agent evaluated on every environment, so its runnable core is the representation layer (stats.py ranks and
novelty.py distance), both numpy-only.

BY READING, the most consequential fact in the body: update_pata_ec defines cap_score(score, lower, upper) and calls it as
cap_score(self.evaluate_theta(...)) with ONE argument (es.py:597 and :600). In Python that raises TypeError on the first
score, so as pinned PATA-EC cannot be computed, and the first environment reproduction that reaches poet_algo.py:296
should fail. The lower/upper bounds it was meant to clip to (mc_lower, mc_upper) are passed in and never used. This is
a prediction from reading, carried as row I1 of packet MECH-POET-PATA-EC-001; it has not been executed.
"""
from nyx.atlas.author import Cut

T = "vault:poet-enhanced-2020/upstream/tree/poet_distributed/"
NOV, ST, ES, PA = T + "novelty.py", T + "stats.py", T + "es.py", T + "poet_algo.py"

c = Cut("poet-enhanced-2020", mode="ANCESTRY_AWARE",
        inspected=["poet_distributed/novelty.py 1-44", "poet_distributed/stats.py 1-47", "poet_distributed/es.py 16-23, 580-624",
                   "poet_distributed/poet_algo.py 160-361"],
        evidence=[("SOURCE_READ", NOV + ":18-44"), ("SOURCE_READ", ST + ":9-24"), ("SOURCE_READ", ES + ":586-602"),
                  ("SOURCE_READ", PA + ":237-241"), ("SOURCE_READ", PA + ":261-280"), ("SOURCE_READ", PA + ":282-336")],
        note="Enhanced POET replaces the original's hand-built 5-number environment descriptor with PATA-EC: an environment is "
             "described by HOW THE CURRENT AND ARCHIVED AGENTS RANK ON IT. Its novelty is the mean distance from that rank vector "
             "to the k=5 nearest rank vectors of the existing environments, all computed over the same agent set. The descriptor "
             "is therefore RELATIONAL: an environment's phenotype is defined by the population it is measured against, and "
             "changes when the population changes even if the environment does not -- the property the operator's basis-"
             "population ablation targets. Admission keeps the original's two-sided minimal criterion but applies it to the "
             "best transferred agent, and counts ANNECS when the archive's agents also pass. As pinned, the PATA-EC capping step "
             "calls a 3-argument function with 1 argument (see the docstring).")

pata = c.organ("pata_ec_environment_phenotype_as_centered_ranks_of_every_agent_s_capped_score_on_it",
    human_name="Optimizer.update_pata_ec (es.py 586-602) + compute_ranks / compute_centered_ranks (stats.py 9-24)", status="ACCEPTED",
    mechanism="for one environment, every archived and every active agent is evaluated on it; each score is meant to be clipped "
              "to [mc_lower, mc_upper]; the vector of scores is replaced by its centered ranks, rank/(n-1) - 0.5 in [-0.5, 0.5], "
              "with ranks from argsort. The environment's phenotype is that rank vector over the CURRENT agent set, recomputed "
              "for every environment (active, archived and candidate) at each reproduction step (poet_algo.py 295-299)",
    input="an environment; all agents' parameters", output="an n-vector of centered ranks", state="pata_ec stored on the optimizer",
    update="once per reproduction step, for every environment",
    assumptions=["two environments are similar if they order the agents the same way", "only the ORDER of agents' scores matters, not their magnitude"],
    fitness_value_in_ancestor="a domain-general environment descriptor that needs no hand-chosen features; it measures what an environment demands of agents",
    failure_landscape="by reading: (1) cap_score(score, lower, upper) is called with one argument (597, 600): TypeError, so as pinned "
                      "the vector cannot be computed; (2) the clipping, had it run, maps every agent below mc_lower to one value, and "
                      "argsort then ranks those ties in some fixed order, so an environment that every agent fails gets a non-zero "
                      "rank vector, identical to that of an environment every agent solves; (3) with a single agent, n - 1 = 0 and the "
                      "centered rank is 0/0; (4) the vector's meaning changes whenever an agent is added or archived",
    human_prior="Wang et al. 2020, 'Enhanced POET' (PATA-EC: Performance of All Transferred Agents - Environment Characterization)",
    evidence_ref=ES + ":586-602; " + ST + ":9-24", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="update_pata_ec and the two rank functions",
    coverage={"input_topology": "MATRIX", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_EPISODE",
              "stochasticity": "DETERMINISTIC", "order_sensitivity": "SENSITIVE", "representation_sensitivity": "SENSITIVE"})

nov = c.organ("novelty_as_mean_distance_to_the_k_nearest_environment_rank_vectors_over_the_same_agent_basis",
    human_name="compute_novelty_vs_archive + euclidean_distance (novelty.py 18-44)", status="ACCEPTED",
    mechanism="the candidate's PATA-EC is recomputed over the current agent set, its Euclidean distance to the PATA-EC of every archived "
              "and active environment is taken (with a ragged-length branch that pads the shorter vector with its last element), and "
              "the mean of the k = 5 smallest is the novelty score; candidates that passed the minimal criterion are sorted by it, "
              "highest first",
    input="the candidate's and the population's rank vectors", output="a scalar novelty", state="none",
    update="per candidate", assumptions=["k nearest in rank-vector space is a usable novelty measure"],
    fitness_value_in_ancestor="the order in which candidate environments are offered for admission",
    failure_landscape="by reading: argsort()[:k] returns fewer than k when fewer than k environments exist (the regime change Harmonia "
                      "verified in poet-original's estimator, #1063); because every vector is recomputed on the same basis the ragged "
                      "branch should be dead in normal operation",
    human_prior="k-nearest-neighbour novelty (Lehman and Stanley 2011), applied to a relational descriptor",
    evidence_ref=NOV + ":18-44", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="novelty.py, all of it",
    coverage={"input_topology": "SET", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "memory": "ARCHIVE"})

mc = c.organ("admission_by_minimal_criterion_on_the_best_transferred_agent_and_annecs_when_the_archive_also_passes",
    human_name="get_child_list + adjust_envs_niches + pass_mc + remove_oldest (poet_algo.py 237-241, 261-336)", status="ACCEPTED",
    mechanism="a reproducing environment (its agent has self-evaluated at least repro_threshold) is mutated (CPPN terrain); a child is a "
              "candidate if not a duplicate and if the PARENT's agent scores inside [mc_lower, mc_upper] on it; candidates are ordered "
              "by PATA-EC novelty; each is then given the BEST of every active agent and its one-step proposal (targeted transfer) and "
              "admitted if that best score is inside the band; at most max_admitted per step; ANNECS is incremented when the best "
              "ARCHIVED agent also passes the band; over max_num_envs the oldest active environments are archived (FIFO)",
    input="reproducing environments; all agents", output="admitted environments; ANNECS count", state="registry, archive, ANNECS",
    update="every adjust_interval * steps_before_transfer iterations",
    assumptions=["an environment is worth adding if some current agent finds it neither impossible nor trivial"],
    fitness_value_in_ancestor="a curriculum of stepping-stone environments; ANNECS as the open-endedness measure",
    failure_landscape="by reading: the PATA-EC refresh at 295-299 runs BEFORE the children are scored, so the cap_score defect fires "
                      "on the first reproduction step that has any candidate parent; the ANNECS increment counts environments solved "
                      "by the archive's agents within the band, i.e. it rewards environments that are NOT novel to the archive",
    human_prior="the original POET minimal criterion (Wang et al. 2019) plus Enhanced POET's targeted transfer and ANNECS",
    evidence_ref=PA + ":237-241, 261-336", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="the four poet_algo.py methods",
    coverage={"input_topology": "SET", "output_topology": "DECISION", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT",
              "stochasticity": "SEEDED_RANDOM", "memory": "ARCHIVE", "competition": "CONTENDS"})

c.edge(pata, nov, "feeds", note="novelty is computed on PATA-EC vectors (novelty.py 32-37)")
c.edge(nov, mc, "selects", note="candidates sorted by novelty before admission (poet_algo.py 278-279)")
c.edge(mc, pata, "updates", note="admitting or archiving an environment changes the agent basis of every PATA-EC")

c.reject("the ES optimiser (es.py 1-579), the transfer machinery beyond evaluate_transfer, the CPPN terrain generator and its mutation, "
         "the Box2D bipedal walker, the logger, master.py", reason="OTHER", evidence="NOT READ; residue",
         note="the directive asked for exactly two mechanisms first")
c.reject("'Enhanced POET' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="descriptor, novelty and admission are separable functions")

c.pressure("an_environment_is_admitted_for_being_neither_impossible_nor_trivial_for_the_best_current_agent_and_novel_in_how_it_ranks_the_agents",
    condition="environments are proposed by mutation; their novelty is measured by how differently they order the current and archived agents; admission requires the best transferred agent to score inside a band",
    resource_or_constraint="a cap on active environments (oldest archived first)", failure_condition="no candidate passes the band; or every candidate orders the agents like an existing environment",
    world_punishes="environments that rank agents like existing ones; impossible or trivial environments", world_rewards="environments that re-order the agent population",
    observable_consequence="novelty ordering of fixed candidate environments under two agent bases (the basis-population ablation)",
    vacuity_condition="a single agent (the rank vector is 0/0) or all agents tied on every environment",
    trivial_shortcuts="an environment on which agents tie: clipped ties receive an arbitrary but fixed rank order",
    cheat_control="hold every environment fixed and permute the order in which agents are stored: if novelty changes, the descriptor reads storage order, not behaviour",
    cost_class="cluster-scale for the full algorithm; the representation layer is microseconds", source_evidence="the three organs above",
    purpose="PURPOSE: open-ended co-evolution of environments and agents (Wang et al. 2020)")

c.ancestry("derived_from", "poet-original-2019 (uber-research/poet original_poet @ 0b40743d): the same loop with the hand-built 5-number descriptor replaced by PATA-EC and with targeted transfer and ANNECS added",
           note="from the code read in both bodies")
c.residue("LARGE_RESIDUE", ["the ES optimiser and transfer bookkeeping unread", "the CPPN terrain generator unread", "nothing ran (Box2D, fiber absent)",
                            "whether any released run used a corrected cap_score is unknown: the pin's code raises TypeError by reading"],
          note="NARROW cut, two mechanisms plus the descriptor they share")
c.save(state="COARSE")
