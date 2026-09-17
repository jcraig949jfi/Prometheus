"""Cut: particles-chopin-0.4 (Chopin's `particles` library; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; ninth of the
2026-09-17 NOT_CUT order). Read: core.py 1-80 (docstring), 108-200 (FeynmanKac abstract class: function list), 296-415 (SMC:
weights, particle generation, reweight, resample_move, SQMC variant, summaries, the iterator step); resampling.py 166-190 (ESS),
464-540 (scheme registry, inverse CDF, ordered uniforms), 600-710 (stratified, systematic, residual, SSP, killing, idiotic).
NOT read: state_space_models.py, smc_samplers.py, mcmc.py, smoothing.py, distributions.py, kalman.py, collectors.py, nested.py,
the QMC/Hilbert modules, multinomial* bodies. Nothing ran.
"""
from nyx.atlas.author import Cut

C = "vault:particles-chopin-0.4/upstream/tree/particles-0.4/particles/core.py"
R = "vault:particles-chopin-0.4/upstream/tree/particles-0.4/particles/resampling.py"
c = Cut("particles-chopin-0.4", mode="ANCESTRY_AWARE", inspected=["core.py 1-200 (docstring, FeynmanKac interface), 296-415 (SMC step)", "resampling.py 166-190, 464-540, 600-710"],
        evidence=[("SOURCE_READ", C + ":296-415"), ("SOURCE_READ", C + ":108-200"), ("SOURCE_READ", R + ":464-540"), ("SOURCE_READ", R + ":600-710"), ("SOURCE_READ", R + ":166-190")],
        note="a particle filter reduced to its loop: propose, weight, decide whether to resample, resample by one of several schemes that differ only in how the ordered uniforms are drawn, "
             "and accumulate a likelihood from the mean weight; the model is an interface of three functions (M0, M, logG) and the loop never looks inside it")

fk = c.organ("model_as_an_interface_of_initial_kernel_transition_kernel_and_log_potential", human_name="class FeynmanKac (M0, M, logG; optional Gamma0/Gamma for QMC, logeta for APF, done, time_to_resample)", status="ACCEPTED",
    mechanism="the algorithm calls only M0(N) to draw initial particles, M(t, xp) to move each particle from its ancestor, and logG(t, xp, x) to compute a log-weight increment; a model may also supply a stopping rule (done), its own resampling trigger (time_to_resample), an auxiliary weight (logeta) and inverse-CDF forms (Gamma0/Gamma) for quasi-Monte Carlo",
    input="a subclass supplying those methods", output="a runnable filter for any such model (state-space bootstrap/guided/auxiliary, tempering, IBIS are all instances per the docstring)", state="none in the interface", update="n/a",
    assumptions=["every sequential Monte Carlo problem is a Feynman-Kac model (the book's thesis); the model can vectorise M and logG over N particles"], fitness_value_in_ancestor="one loop for many algorithms; the model owns the stopping rule and the resampling trigger, so the loop is generic",
    failure_landscape="UNKNOWN by run", human_prior="the Feynman-Kac abstraction (Del Moral 2004; Chopin & Papaspiliopoulos 2020)", evidence_ref=C + ":108-200", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="class FeynmanKac",
    coverage={"input_topology": "MIXED", "output_topology": "MIXED", "state_amount": "NONE", "stochasticity": "SEEDED_RANDOM", "representation_sensitivity": "INVARIANT"})

loop = c.organ("propose_weight_resample_loop_as_an_iterator_with_history_and_summaries_as_side_channels", human_name="SMC.__next__ / reweight_particles / resample_move / run (core.py 315-415)", status="ACCEPTED",
    mechanism="step t: if t=0 draw N particles from M0, else (compute APF auxiliary weights if the model is APF) ask the model whether to resample; if yes draw ancestor indices A from the aux weights by the chosen scheme, set Xp = X[A] and reset the weights (to uniform, or to the APF correction), else A = identity; move X = M(t, Xp); add logG to the log-weights; compute summaries; t += 1; the object is a Python iterator so a caller can step, inspect X/W/A, and continue",
    input="a FeynmanKac model, N, a scheme name, flags (qmc, store_history, collectors)", output="X, W, A per step; logLt; optional history", state="X, Xp, A, wgts, t, logLt, rs_flag", update="per step",
    assumptions=["N is fixed (resampling always draws N even for waste-free variants, per the comment)", "the weights object handles log-space normalisation"],
    fitness_value_in_ancestor="the loop is inspectable at every step (iterator) and the same loop serves QMC by swapping one method", failure_landscape="UNKNOWN by run; by reading: weight degeneracy between resampling steps is left to the model's trigger",
    evidence_ref=C + ":315-415", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the SMC methods listed",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_EPISODE", "memory": "LAST_VALUE", "stochasticity": "SEEDED_RANDOM", "update_topology": "SINGLE_STEP", "temporal_horizon": "STEP"})

ess = c.organ("effective_sample_size_from_log_weights_as_the_degeneracy_measure", human_name="essl (resampling.py 166-190); used by the model's time_to_resample", status="ACCEPTED",
    mechanism="ESS = (sum w)^2 / sum w^2 with w = exp(lw - max lw) (max-subtracted for stability); in [1, N]; N for uniform weights, 1 when one weight dominates; the model's default trigger compares it with a fraction of N (not read here: the default lives in the model classes)",
    input="log-weights", output="a scalar in [1, N]", state="none", update="per step",
    assumptions=["ESS approximates the number of 'useful' particles; a threshold on it is the standard adaptive trigger (Kong, Liu & Wong 1994)"], fitness_value_in_ancestor="resampling only when degeneracy warrants it: fewer resampling steps, lower variance",
    failure_landscape="UNKNOWN by run", evidence_ref=R + ":166-190", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="essl",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "uncertainty": "SAMPLE"})

icdf = c.organ("resampling_as_inverse_cdf_over_ordered_uniforms_with_the_scheme_being_how_the_uniforms_are_drawn", human_name="inverse_cdf, uniform_spacings, stratified, systematic, multinomial (resampling.py 485-612)", status="ACCEPTED",
    mechanism="all the classical schemes share one O(N+M) pass: walk the cumulative weights once with M SORTED uniforms and emit the index at which each uniform falls; multinomial draws the M sorted uniforms as normalised exponential spacings (O(M) instead of sort), stratified draws one uniform per stratum ((u_m + m)/M), systematic uses a single uniform for all strata ((u + m)/M)",
    input="normalised weights W, M sorted uniforms", output="ancestor indices A", state="none", update="per resampling step",
    assumptions=["the schemes differ in variance, not in expectation: systematic has the lowest variance and is the default in practice; all keep E[#offspring of n] = M W_n"], fitness_value_in_ancestor="one jit-compiled kernel; the scheme is a choice of a uniform vector",
    failure_landscape="by reading: systematic resampling is not consistent in the sense of Gerber et al. 2019 (the SSP docstring's motivation); the shared inverse_cdf is O(N+M) but sequential (a numba loop)", human_prior="the unification of schemes as 'ordered uniforms + inverse CDF' (Chopin's book)",
    evidence_ref=R + ":485-612", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="inverse_cdf and the three thin wrappers",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "SEEDED_RANDOM", "update_topology": "SWEEP", "order_sensitivity": "SENSITIVE"})

ssp = c.organ("srinivasan_sampling_process_pairwise_transfer_of_fractional_offspring_mass", human_name="ssp (resampling.py 632-680)", status="ACCEPTED",
    mechanism="each particle starts with floor(M W_n) children and a fractional remainder xi_n; walk the particles with two live indices i, j: transfer mass between xi_i and xi_j by the largest amount that keeps both in [0,1], choosing the direction at random with probability proportional to the transfer sizes; whichever hits an integer (0 or 1) is settled (1 -> one more child) and replaced by the next particle; a round-off guard adds the missing child at the end; every particle gets floor or ceil of M W_n children",
    input="W, M", output="offspring counts, expanded to indices", state="xi (remainders), nr_children", update="per resampling step",
    assumptions=["a resampling scheme should be both low-variance (offspring k or k+1) and consistent; the reference is Gerber, Chopin & Whiteley 2019"], fitness_value_in_ancestor="the properties of systematic resampling plus a consistency guarantee",
    failure_landscape="by reading: floating round-off can lose a particle; the code checks the count and asks for a bug report if it is still wrong -- an explicit self-check", human_prior="a 2019 scheme; the only one here with a theorem attached in the docstring",
    evidence_ref=R + ":632-680", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="ssp",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "SEEDED_RANDOM", "update_topology": "SWEEP", "order_sensitivity": "SENSITIVE"})

kill = c.organ("killing_resampling_keeping_each_particle_with_probability_proportional_to_its_weight_over_the_max", human_name="killing (resampling.py 681-700)", status="ACCEPTED",
    mechanism="each particle survives in place with probability W_n / max W; the killed ones are replaced by multinomial draws from W; requires M = N; keeps the surviving particles' positions fixed (useful when particle identity matters, e.g. for genealogies or parallel hardware)",
    input="W", output="A with fixed points for survivors", state="none", update="per resampling step", assumptions=["a particle at the max weight is never killed; the acceptance is a rejection sampler against the max"],
    fitness_value_in_ancestor="in-place resampling (the docstring notes it is 'not described in the book')", failure_landscape="UNKNOWN by run; by reading: high variance when one weight dominates (nearly all killed)",
    evidence_ref=R + ":681-700", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="killing",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "SEEDED_RANDOM", "update_topology": "PARALLEL_ROUNDS", "order_sensitivity": "INVARIANT"})

ll = c.organ("log_likelihood_accumulated_from_the_log_mean_weight_with_a_correction_when_not_resampling", human_name="compute_summaries (core.py 351-368)", status="ACCEPTED",
    mechanism="loglt = log mean weight at t if resampling happened (or t = 0), else the DIFFERENCE of log mean weights between t and t-1 (because the weights were not reset); logLt accumulates; summaries and history are collected after, so collectors can read the history",
    input="the weights object", output="loglt, logLt", state="log_mean_w, logLt", update="per step", assumptions=["the standard unbiased likelihood estimator of SMC (Del Moral); the correction handles the no-resample steps"],
    fitness_value_in_ancestor="the marginal likelihood comes free from the filter; what makes SMC usable inside PMCMC and model comparison", failure_landscape="UNKNOWN by run",
    evidence_ref=C + ":351-368", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="compute_summaries",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC"})

sqmc = c.organ("sequential_quasi_monte_carlo_by_hilbert_sorting_particles_and_resampling_with_a_sobol_point_set", human_name="resample_move_qmc (core.py 339-350)", status="CANDIDATE",
    mechanism="always resample; draw an (N, d+1) Sobol point set; sort particles along a Hilbert curve; use the first coordinate (sorted) with inverse_cdf over the Hilbert-ordered weights to pick ancestors; feed the remaining coordinates to the model's inverse-CDF move Gamma(t, xp, v)",
    input="X, W, a Sobol generator, the model's Gamma", output="X, A", state="h_order", update="per step", assumptions=["the model exposes its transition as an inverse CDF of a uniform (Gamma); the Hilbert sort makes the ancestor selection a one-dimensional quasi-random operation"],
    fitness_value_in_ancestor="faster-than-Monte-Carlo convergence (Gerber & Chopin 2015) with the same loop", failure_landscape="UNKNOWN; the hilbert and rqmc modules were not read", evidence_ref=C + ":339-350", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="resample_move_qmc; CANDIDATE because its two dependencies were not read",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "SEEDED_RANDOM", "order_sensitivity": "SENSITIVE"})

c.reject("multiSMC (parallel runs), _picklable_f, utils.timer, __str__ / verbose printing, collectors and history storage", reason="GENERIC_LANGUAGE_MECHANICS", evidence=C + ":351-368 (hist/summaries hooks), 415-518", note="orchestration and instruments; the collectors are the natural Stage C readout")
c.reject("the model library (state_space_models, smc_samplers, mcmc, smoothing, distributions, kalman, nested)", reason="OTHER", evidence="NOT READ (about 6,000 lines); residue", note="smc_samplers (tempering, IBIS, waste-free) is where the loop is stressed hardest")
c.reject("'particle filter' / 'SMC' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the loop, the trigger, the schemes and the likelihood estimator are separately replaceable; the library itself exposes each as a parameter")
c.reject("'idiotic' resampling (all particles from one draw)", reason="DUPLICATES_A_CONTROL", evidence=R + ":701-708 'For testing only. DO NOT USE.'", note="the body ships its own negative control; noted for Stage C, not an organ")

c.edge(fk, loop, "feeds"); c.edge(loop, ess, "feeds", note="via the model's trigger"); c.edge(ess, loop, "gates", note="rs_flag"); c.edge(loop, icdf, "selects", note="scheme by name"); c.edge(icdf, loop, "feeds", note="A"); c.edge(ssp, icdf, "competes"); c.edge(kill, icdf, "competes")
c.edge(loop, ll, "feeds"); c.edge(sqmc, loop, "competes", note="qmc flag replaces resample_move"); c.edge(sqmc, icdf, "feeds", note="reuses inverse_cdf")

c.pressure("a_population_must_track_a_hidden_moving_state_from_noisy_observations_when_weights_degenerate_geometrically",
    condition="the world has a hidden state evolving by a known stochastic rule and emits noisy observations; a population of N guesses is scored each step by observation likelihood; without intervention one guess's weight comes to dominate within a few steps",
    resource_or_constraint="N; per-step evaluations of the rule and the likelihood; variance of the estimate", failure_condition="collapse to one lineage (estimate variance explodes) or resampling every step (unnecessary noise)",
    world_punishes="both", world_rewards="a population that duplicates the plausible and discards the implausible only when degeneracy is measured", observable_consequence="tracking error and likelihood-estimate variance vs N and vs the resampling trigger threshold",
    vacuity_condition="a linear-Gaussian world (the Kalman filter is exact; kalman.py is in the body as the oracle) or observations so uninformative that weights stay uniform", trivial_shortcuts="a world that reveals the hidden state; N so large that degeneracy never bites within the horizon",
    cheat_control="an organism given the hidden state must track with zero error at N=1; the ancestor with the trigger set to never-resample must collapse within a known number of steps on a standard model: the world must show both or the degeneracy pressure is absent",
    cost_class="CPU-scale", source_evidence="core.py 315-415; resampling.py 166-190; record domain hidden-state/filtering/resampling", purpose="PURPOSE: sequential Monte Carlo / particle filtering (Chopin & Papaspiliopoulos 2020)")

c.pressure("duplication_of_a_population_by_weight_must_be_low_variance_and_unbiased_at_the_same_time",
    condition="N items with weights must be replaced by N items drawn so each item's expected copy count is N times its weight; the variance of the copy counts is the cost", resource_or_constraint="O(N) time; randomness",
    failure_condition="bias (wrong expectation) or high variance (multinomial)", world_punishes="both; and schemes that need O(N log N)", world_rewards="ordered-uniform schemes where each count is floor or ceil of its expectation",
    observable_consequence="copy-count variance across schemes on the same weight vector; downstream estimator variance", vacuity_condition="uniform weights", trivial_shortcuts="deterministic rounding (biased)",
    cheat_control="a scheme that returns the exact expected counts (impossible unless integer) is the ceiling; the 'idiotic' scheme in the body (all copies of one draw) is the floor: the world must rank the real schemes strictly between them",
    cost_class="CPU-scale", source_evidence="resampling.py 485-680", purpose="PURPOSE: resampling schemes (Kitagawa 1996; Gerber, Chopin & Whiteley 2019)")

c.ancestry("algorithm_from", "Gordon, Salmond & Smith 1993 (bootstrap filter); Del Moral 2004 (Feynman-Kac); Chopin & Papaspiliopoulos 2020 (the book this library accompanies)", note="from the docstrings; the record's lineage not re-read")
c.residue("PARTIALLY_EXPLAINED", ["the model library and the QMC/Hilbert machinery were not read (sqmc is CANDIDATE)", "the default resampling trigger (ESS < N/2 by convention) lives in the model classes, not read; the cut names the measure, not the threshold", "nothing ran; kalman.py in the body is the exact oracle for a Stage C world"],
          note="the loop and the resampling schemes are accounted for; the vault's filterpy-labbe and simple-kalman fossils are recurrence candidates against kalman.py")
c.save(state="COARSE")
