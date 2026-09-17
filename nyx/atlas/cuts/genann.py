"""Cut: genann (Lewis Van Winkle's minimal feed-forward net in one C file; ancestry-aware, Stage A DEEP-by-size: genann.c 417 lines;
SOURCE_READ on M3; fourteenth of the 2026-09-17 NOT_CUT order). Read in full: genann.c (init, run, train, activations, I/O).
Skimmed: genann.h, test.c, the examples. Nothing ran (C; not on M3). The record files it under 'connectionist / perceptron /
backpropagation' with era pre1980 -- the era is the algorithm's, not the code's (2016-18).
"""
from nyx.atlas.author import Cut

G = "vault:genann/upstream/tree/genann.c"
c = Cut("genann", mode="ANCESTRY_AWARE", inspected=["genann.c (all)", "genann.h, test.c, example*.c (skimmed)"], evidence=[("SOURCE_READ", G), ("SOURCE_READ", "vault:genann/upstream/tree/genann.h")],
        note="backpropagation with nothing else: one weight array laid out layer by layer with a bias weight first, a forward pass that walks it once, and a training step that computes deltas backward and applies plain SGD per example -- no momentum, no batching, no regularisation")

layout = c.organ("single_contiguous_weight_array_with_bias_as_a_minus_one_input_and_layer_offsets_computed_on_the_fly", human_name="genann_init / the weight, output, delta arrays; the -1.0 bias term in genann_run", status="ACCEPTED",
    mechanism="one malloc holds the struct, all weights (inputs+1 per hidden neuron in layer 1, hidden+1 per neuron after), all neuron outputs and all deltas; the bias is implemented as an extra weight multiplied by a constant -1.0 at the head of every neuron's dot product; every routine locates a layer by arithmetic on (inputs, hidden, hidden_layers, outputs)",
    input="the four size parameters", output="an allocated network with random weights in [-0.5, 0.5)", state="weights, outputs, deltas", update="weights per training step",
    assumptions=["all hidden layers have the same width; a fully connected topology; doubles"], fitness_value_in_ancestor="cache-friendly, copyable with memcpy (genann_copy), serialisable as a list of numbers", failure_landscape="by reading: the size checks refuse absurd dimensions; no other guard",
    evidence_ref=G + ":genann_init, genann_copy, genann_run (the *w++ * -1.0 lines)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="genann_init and the array pointers",
    coverage={"input_topology": "SCALAR", "output_topology": "MATRIX", "state_amount": "SUPERLINEAR", "state_persistence": "PERSISTENT", "stochasticity": "SEEDED_RANDOM", "representation_sensitivity": "SENSITIVE"})

fwd = c.organ("forward_pass_as_one_walk_over_the_weight_array_with_a_pluggable_activation", human_name="genann_run; genann_act_sigmoid / _cached (4096-entry lookup) / linear / threshold / tanh / relu", status="ACCEPTED",
    mechanism="copy the inputs into the output array; for each neuron of each layer compute bias plus the dot product with the previous layer's outputs, apply the layer's activation function pointer, store; the default sigmoid is a 4096-entry table over [-15, 15] built once (with clamping outside), so the forward pass avoids exp()",
    input="an input vector", output="the output layer's values (a pointer into the network's own buffer)", state="the output array (overwritten per call)", update="per call",
    assumptions=["the lookup's quantisation (30/4096 per step) is below the training noise; assert(!isnan) is the only numerical check"], fitness_value_in_ancestor="a forward pass with no allocation and no transcendental calls", failure_landscape="by reading: the cached sigmoid is not smooth, so its derivative used in training is the analytic y(1-y) of the QUANTISED output, a small mismatch",
    evidence_ref=G + ":genann_run, genann_act_*, genann_init_sigmoid_lookup", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="genann_run and the activation functions",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP"})

bp = c.organ("backpropagation_with_per_example_sgd_and_the_derivative_taken_from_the_stored_output", human_name="genann_train; genann_act_derivative", status="ACCEPTED",
    mechanism="run forward; output deltas = (target - output) x f'(output) (or just the difference for a linear output); hidden deltas layer by layer backward = f'(output) x sum over the next layer of (its delta x the weight from this neuron), with the weight index computed from the layout; then every weight += learning_rate x delta x input-to-that-weight, bias weight with input -1; "
              "the derivative is computed from the stored activation value (y(1-y), 1-y^2, step for relu), so the forward outputs must still be in the buffer",
    input="one (input, target) pair; a learning rate", output="updated weights in place", state="the delta array", update="per example", assumptions=["squared error (the delta form assumes it); one example at a time; the caller loops over epochs and shuffles if it wants"],
    fitness_value_in_ancestor="the whole learning rule in ~90 lines; every index is derived from the layout, no matrices", failure_landscape="by reading: no gradient clipping; a large learning rate diverges; relu with the threshold derivative can die (zero gradient) and nothing revives it",
    human_prior="Rumelhart, Hinton & Williams 1986 backpropagation in its most literal form; the author's stated goal is minimalism", evidence_ref=G + ":genann_train, genann_act_derivative", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="genann_train",
    coverage={"input_topology": "VECTOR", "output_topology": "MATRIX", "state_amount": "LINEAR_IN_INPUT", "feedback": "CLOSED_LOOP", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "adaptation": "PARAMETER", "failure_mode": "DIVERGES"})

c.reject("genann_read / genann_write (text serialisation), genann_free, the examples and the minctest harness", reason="GENERIC_LANGUAGE_MECHANICS", evidence=G + ":genann_read, genann_write; test.c", note="test.c is a ready oracle (XOR etc.) for a Stage C run on a host with a C compiler")
c.reject("'neural network' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="layout, forward pass and learning rule are separately replaceable; the vault's hopfield and minisom bodies share the first two and not the third")

c.edge(layout, fwd, "feeds"); c.edge(fwd, bp, "feeds", note="stored outputs are the derivative's input"); c.edge(bp, layout, "updates")

c.pressure("a_fixed_parametric_map_must_reduce_error_on_examples_presented_one_at_a_time_using_only_a_local_error_signal_per_parameter",
    condition="an organism holds parameters; the world shows one (input, target) at a time and scores the output; the organism may change each parameter only by a quantity computed from signals available at that parameter",
    resource_or_constraint="one pass per example; parameters fixed in number", failure_condition="error does not fall, or falls then diverges", world_punishes="global updates (not local) and updates that need the whole dataset",
    world_rewards="a chain rule that delivers a local error to every parameter", observable_consequence="training error vs examples seen on XOR and on a noisy regression, across learning rates", vacuity_condition="a linearly separable target (a perceptron suffices) or a lookup-table-sized world",
    trivial_shortcuts="memorising examples; a world that reveals the target function", cheat_control="an organism given the target function's parameters must show zero error immediately; the ancestor at a learning rate 100x too high must diverge: the world must show both",
    cost_class="CPU-scale", source_evidence="genann.c genann_train; record tags backpropagation / learning", purpose="PURPOSE: minimal feed-forward neural network training (Van Winkle, genann)")

c.ancestry("algorithm_from", "Rumelhart, Hinton & Williams 1986 (backpropagation); the multilayer perceptron", note="from the code and the record; the record's pre1980 era is the algorithm's ancestry, not the body's date")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["nothing ran; test.c holds XOR/AND/OR training checks that would be the Stage C oracle", "the cached-sigmoid derivative mismatch is a reading-level claim"], note="every function in genann.c is an organ or rejected")
c.save(state="DEEP")
