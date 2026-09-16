"""Cut: minisom (ancestry-aware, Stage A COARSE; SOURCE_READ minisom.py 26-69, 220-300 (constructor), 401-610, 627-790, 875-1010;
the numba fast path 82-219 / 786-874 and the unittest class 1055+ skimmed). Kohonen self-organising map, single file, numpy."""
from nyx.atlas.author import Cut

S = "vault:minisom/upstream/tree/minisom.py"
c = Cut("minisom", mode="ANCESTRY_AWARE", inspected=["minisom.py (1564 lines; the class body read, numba duplicate and tests skimmed)"],
        evidence=[("SOURCE_READ", S)], note="a single class whose train loop is four mechanisms in a fixed order; Techne's harness runs it (RUNNABLE_CONTAINER) so Stage C is open")

win = c.organ("winner_by_argmin_distance_over_the_lattice", human_name="best matching unit (BMU) / competitive selection", status="ACCEPTED",
    human_interpretation="the neuron whose weight vector is closest to the input wins",
    mechanism="compute a distance (euclidean by default; cosine, manhattan, chebyshev, or a user callable) from x to every weight vector on the x*y lattice into activation_map, then argmin -> (i, j); nothing else in the file reads activation_map",
    input="one sample x (input_len,)", output="lattice coordinates (i, j)", state="none (activation_map is scratch)", update="none", assumptions=["the distance is the right notion of similarity for the data"],
    fitness_value_in_ancestor="the competition that makes the map a quantiser", evidence_ref=S + ":423-431,496-508,522-526", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="_activate + winner + the four _*_distance functions", coverage={"input_topology": "VECTOR", "output_topology": "DECISION", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "competition": "ARBITRATES"})

nb = c.organ("lattice_neighbourhood_kernel_around_the_winner", human_name="neighbourhood function (gaussian / mexican hat / bubble / triangle) on a rectangular or hexagonal grid", status="ACCEPTED",
    human_interpretation="neighbours of the winner on the GRID (not in input space) are pulled too; this is what makes the map topology-preserving",
    mechanism="precomputed grid coordinate arrays _xx, _yy (hexagonal: odd rows offset, meshgrid at construction); given the winner c and radius sigma return a (x, y) matrix of weights: gaussian exp(-d^2/2sigma^2) as an outer product of per-axis factors, mexican hat (gaussian times (1-d^2/sigma^2)), bubble (1 inside radius else 0), triangle (linear to 0 at sigma)",
    input="winner (i, j), sigma", output="an (x, y) matrix of coupling weights", state="_xx, _yy (constant after construction)", update="none", assumptions=["grid distance, not weight distance, defines who learns together"],
    fitness_value_in_ancestor="ordering: without it the map is plain competitive learning / k-means-like (record: 'fails to organise')", evidence_ref=S + ":465-495,220-300 (topology setup)", confidence="HIGH",
    portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="neighborhood = one of _gaussian/_mexican_hat/_bubble/_triangle plus the coordinate arrays",
    coverage={"input_topology": "SCALAR", "output_topology": "MATRIX", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "SENSITIVE"})

dc = c.organ("time_indexed_decay_of_step_and_radius", human_name="learning-rate and sigma schedule (five decay laws)", status="ACCEPTED",
    mechanism="eta(t) and sigma(t) are pure functions of (initial, t, max_iter): inverse_decay_to_zero (C/(C+t), C=max_iter/100), linear_decay_to_zero, inverse_decay_to_one, linear_decay_to_one, asymptotic_decay (1/(1+t/(max_iter/2))); chosen by name at construction; t is the iteration or, with use_epochs, the epoch index",
    input="t, max_iter", output="eta, sigma", state="none", update="none", assumptions=["the total budget max_iter is known in advance (every law is normalised by it)"],
    fitness_value_in_ancestor="a wide early radius orders the map, a narrow late radius refines it; the record names the schedule as the failure locus", failure_landscape="UNKNOWN by run; by reading: sigma decaying below ~1 leaves neighbours uncoupled; a budget too short leaves the map twisted (record)",
    evidence_ref=S + ":433-463,670-676", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the five _*_decay_* methods",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "NONE", "temporal_horizon": "EPISODE", "adaptation": "PARAMETER"})

up = c.organ("online_pull_of_weights_toward_the_sample_scaled_by_kernel", human_name="Kohonen update rule w += eta * h(c, sigma) * (x - w)", status="ACCEPTED",
    mechanism="one sample at a time: every weight vector moves toward x by the fraction eta * neighbourhood weight of its grid cell (einsum over the lattice)",
    input="x, winner, eta, sigma", output="mutated weights (x, y, input_len)", state="the codebook _weights", update="per sample", assumptions=["small steps; the sample order matters (see sequencing)"],
    fitness_value_in_ancestor="the only place the codebook changes in online training", evidence_ref=S + ":528-551", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="update()",
    coverage={"input_topology": "VECTOR", "output_topology": "MATRIX", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "update_topology": "SINGLE_STEP", "order_sensitivity": "SENSITIVE", "memory": "SUMMARY_STATISTIC"})

bt = c.organ("batch_kernel_weighted_mean_replacement", human_name="batch SOM (Kohonen 2013)", status="ACCEPTED",
    mechanism="per iteration: accumulate numerator += h(bmu(sample), sigma) * sample and denominator += h over ALL samples with the weights frozen, then w = (1 - lr) * w + lr * numerator/denominator for cells with denominator > 0 (untouched cells keep their weights)",
    input="the whole data matrix, sigma(t), lr(t)", output="mutated weights", state="_weights; per-iteration accumulators", update="once per pass over the data", assumptions=["order-invariant by construction", "cells no sample reaches never move"],
    fitness_value_in_ancestor="an alternative to the online rule; the record does not say which Techne's harness used", evidence_ref=S + ":724-785", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="train_batch_offline (the numba variant 786-874 is a duplicate)",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "CONSTANT", "update_topology": "SWEEP", "order_sensitivity": "INVARIANT", "memory": "SUMMARY_STATISTIC"})

sq = c.organ("sample_sequencing_with_optional_winner_override", human_name="train() loop: sequential / shuffled / epoch order; fixed_points", status="ACCEPTED",
    mechanism="_build_iteration_indexes yields sample indices: arange(n) % len(data) or tiled epochs, optionally shuffled by the seeded RandomState; train() walks them, computes the winner (or takes the caller's fixed (i, j) for that sample index), and calls update with the decay index t (iteration or epoch)",
    input="data, num_iteration, random_order, use_epochs, fixed_points", output="a sequence of (sample, winner, t) events", state="the RandomState", update="none", assumptions=["reusing samples cyclically is harmless"],
    fitness_value_in_ancestor="fixed_points is a supervised anchor: a sample can be pinned to a cell (semi-supervised SOM)", evidence_ref=S + ":26-48,627-689", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="_build_iteration_indexes + train + train_random + train_batch",
    coverage={"input_topology": "MATRIX", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "stochasticity": "SEEDED_RANDOM", "order_sensitivity": "SENSITIVE"})

ini = c.organ("codebook_initialisation_random_or_pca_plane", human_name="random_weights_init / pca_weights_init", status="ACCEPTED",
    mechanism="random: each cell takes a random data sample; pca: eigh of the data covariance, the lattice is laid on the plane of the top two eigenvectors around the data mean (linspace -1..1 per axis); the constructor otherwise draws uniform random weights normalised per cell",
    input="data", output="initial _weights", state="_weights", update="once", assumptions=["pca: >= 2 features and a 2-D lattice"], fitness_value_in_ancestor="the code claims pca init converges faster and is deterministic (571-576); not measured here",
    evidence_ref=S + ":561-609,280-300", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two *_init methods + constructor weight draw",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "CONSTANT", "stochasticity": "SEEDED_RANDOM"})

c.reject("quantization_error / topographic_error / distance_map (U-matrix) / activation_response / win_map / labels_map", reason="OTHER",
         evidence=S + ":875-1054 -- read-only functions of the trained weights and data; none feeds back into training", note="INSTRUMENTS, not machinery (the NYX-42 schema question again); they are the observables Stage C will use")
c.reject("numba batch fast path (_batch_offline_iteration_numba, train_batch_offline_fast)", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + ":82-219,786-874 -- the same algorithm as batch_kernel_weighted_mean_replacement compiled; behaviourally a duplicate by intent, not verified")
c.reject("'self-organising map' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the train loop is winner -> kernel -> decay -> update; each is a separately selectable method (constructor arguments choose the distance, the kernel, the two decay laws, the topology)")
c.reject("verbose progress printing (_wrap_index__in_verbose)", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + ":50-68")

c.edge(sq, win, "feeds"); c.edge(win, nb, "feeds", note="winner centres the kernel"); c.edge(dc, nb, "updates", note="sigma(t)"); c.edge(dc, up, "updates", note="eta(t)")
c.edge(nb, up, "transforms", note="kernel scales the pull per cell"); c.edge(sq, up, "schedules"); c.edge(ini, up, "stores", note="initial codebook the pulls act on")
c.edge(nb, bt, "transforms"); c.edge(dc, bt, "updates"); c.edge(win, bt, "feeds"); c.edge(sq, win, "gates", note="fixed_points bypass the winner")

c.pressure("a_bounded_lattice_must_represent_an_unlabelled_distribution",
    condition="data arrive as vectors with no labels and no target; a fixed small set of prototypes must cover them so that similar inputs land on nearby prototypes", resource_or_constraint="x*y prototypes, far fewer than samples; no supervisory signal",
    failure_condition="prototypes collapse onto one region (dead cells) or the grid folds (twisted map)", world_punishes="high reconstruction distance; neighbours on the grid that are far in input space", world_rewards="low quantisation error AND low topographic error together",
    observable_consequence="quantization_error and topographic_error (the fossil's own instruments)", vacuity_condition="as many prototypes as samples (each sample gets its own cell)", trivial_shortcuts="k-means minimises quantisation error alone; a world that rewards only that does not need the lattice",
    cheat_control="a codebook built from the true cluster centres with a random grid assignment must score well on quantisation and badly on topography; if the world cannot tell it from a trained map, it is not measuring organisation", cost_class="CPU-scale", source_evidence="record human_environmental_pressure / failure condition; minisom.py 949-1009", purpose="PURPOSE: visualise / cluster high-dimensional data on a 2-D sheet")
c.pressure("no_signal_says_when_ordering_is_done_so_a_fixed_budget_is_split_by_a_clock",
    condition="the process has two regimes (coarse ordering, fine convergence) and no observable tells it which one it is in; the only control is a decay schedule against a budget known in advance", resource_or_constraint="max_iter fixed before training",
    failure_condition="too fast a decay freezes a twisted map; too slow a decay never converges", world_punishes="schedules mismatched to the data's structure", world_rewards="a schedule (or a self-measured proxy) that spends the budget on ordering first",
    observable_consequence="final topographic error as a function of the decay law", vacuity_condition="a budget so large that any decay works", trivial_shortcuts="run forever; a world must charge for iterations",
    cheat_control="a run given the ordering/convergence boundary as an oracle must beat every fixed schedule; otherwise the world's reward does not depend on the schedule", cost_class="CPU-scale", source_evidence="minisom.py 433-463; record behavioral_entry_point", purpose="PURPOSE: same")

c.ancestry("algorithm_from", "Kohonen 1982 / Kohonen 2013 (batch)", note="named in the code's own docstring 724-727; Techne's record ancestry not re-read here")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["nothing ran; Techne's harness (clustered 2-D points, quantisation error drops) is a Stage C candidate with the kernel radius and decay law as ablation targets", "hexagonal vs rectangular topology is a coordinate change inside the kernel organ; whether it changes measured behaviour is UNKNOWN"],
          note="seven mechanisms account for every line of train / train_batch_offline / update")
c.save(state="COARSE")
