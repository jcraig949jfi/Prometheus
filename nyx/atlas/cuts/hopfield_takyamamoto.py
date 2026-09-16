"""Cut: hopfield-takyamamoto (ancestry-aware, Stage A DEEP-by-size; SOURCE_READ network.py in full (the whole mechanism is 60 lines);
train.py / train_mnist.py skimmed (demo drivers: image binarisation, corruption, plotting)). A Hopfield network in numpy."""
from nyx.atlas.author import Cut

S = "vault:hopfield-takyamamoto/upstream/tree/network.py"
c = Cut("hopfield-takyamamoto", mode="ANCESTRY_AWARE", inspected=["network.py (all)", "train.py, train_mnist.py (skimmed)"], evidence=[("SOURCE_READ", S)],
        note="four mechanisms in sixty lines; the interesting anatomy is the stopping rule (energy unchanged after a sweep) and the mean-subtracted Hebb rule, both of which the human name 'Hopfield network' does not mention")

hb = c.organ("hebbian_outer_product_weights_from_mean_subtracted_patterns_with_zero_diagonal", human_name="train_weights", status="ACCEPTED",
    mechanism="rho = the mean activation over all patterns and neurons; W = sum over patterns of outer(t - rho, t - rho); the diagonal is zeroed; W is divided by the number of patterns; symmetric by construction",
    input="a list of +/-1 (or binary) vectors", output="W (N x N)", state="W", update="once (batch)", assumptions=["patterns are uncorrelated enough (record: capacity ~0.14 N); the mean subtraction is the author's deviation from the textbook rule"],
    fitness_value_in_ancestor="the only learning; capacity and spurious attractors are properties of this rule", evidence_ref=S + ":train_weights", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="train_weights",
    coverage={"input_topology": "SET", "output_topology": "MATRIX", "state_amount": "SUPERLINEAR", "memory": "SUMMARY_STATISTIC", "stochasticity": "DETERMINISTIC", "adaptation": "PARAMETER"})

sy = c.organ("synchronous_sign_threshold_update_of_all_units", human_name="_run (asyn=False): s = sign(W s - threshold)", status="ACCEPTED",
    mechanism="all units update at once from the previous state; up to num_iter sweeps", input="a state vector", output="a state vector", state="s", update="per sweep", assumptions=["sign(0) = 0 in numpy: a unit can be silenced (an implementation quirk of this body, not of the model)"],
    failure_landscape="UNKNOWN by run; by reading: synchronous updates can oscillate between two states (a known property of the parallel rule), which the stopping rule below would not detect as convergence -- it compares energy, and a 2-cycle has constant energy: the loop would return the first state of the cycle",
    evidence_ref=S + ":_run synchronous branch", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the asyn=False branch",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "update_topology": "PARALLEL_ROUNDS", "order_sensitivity": "INVARIANT", "failure_mode": "OSCILLATES"})

asy = c.organ("asynchronous_random_single_unit_updates_in_batches_of_100", human_name="_run (asyn=True)", status="ACCEPTED",
    mechanism="100 times: pick a random unit index and set it to sign(W[idx] . s - threshold); then check energy; up to num_iter such batches", input="a state vector", output="a state vector", state="s", update="per unit", assumptions=["100 random picks approximate a sweep (with N > 100 many units are untouched per batch)"],
    fitness_value_in_ancestor="the update order for which energy is non-increasing (Hopfield 1982)", evidence_ref=S + ":_run asynchronous branch", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the asyn=True branch",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SINGLE_STEP", "stochasticity": "ENVIRONMENT_RANDOM", "order_sensitivity": "SENSITIVE"})

en = c.organ("energy_function_as_the_stopping_rule", human_name="energy = -1/2 s W s + threshold . s; stop when unchanged", status="ACCEPTED",
    mechanism="after every sweep (or batch) compute the quadratic energy; if it equals the previous value exactly, return; else continue to num_iter", input="s, W", output="a scalar; a stop decision", state="e (last energy)", update="per sweep",
    assumptions=["equal energy means a fixed point (false for synchronous 2-cycles and for asynchronous batches that changed nothing by chance)"], evidence_ref=S + ":energy and the e == e_new tests", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="energy() + the two comparisons",
    coverage={"input_topology": "VECTOR", "output_topology": "DECISION", "state_amount": "CONSTANT", "memory": "LAST_VALUE"})

c.reject("plot_weights, tqdm progress, the image demos (train.py: skimage binarisation and corruption)", reason="OTHER", evidence="instruments and drivers; the corruption routine is the WORLD's noise, recorded as environment", note="train.py's np.random.seed(1) is the only seed; network.py's asynchronous branch is unseeded")
c.reject("'Hopfield network' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="learning and recall share only W; the two recall rules and the stopping rule are separately replaceable")

c.edge(hb, sy, "feeds"); c.edge(hb, asy, "feeds"); c.edge(sy, en, "feeds"); c.edge(asy, en, "feeds"); c.edge(en, sy, "gates", note="stop"); c.edge(en, asy, "gates"); c.edge(sy, asy, "competes")

c.pressure("a_corrupted_cue_must_recover_the_nearest_stored_pattern_with_no_index_and_no_search",
    condition="memories are addressed by content: a partial or noisy pattern must fall to the complete one by local dynamics alone", resource_or_constraint="N^2 weights for ~0.14 N patterns; no external comparison",
    failure_condition="convergence to a spurious attractor (record)", world_punishes="storing correlated or too many patterns; cues beyond the basin", world_rewards="a dynamics whose fixed points are the stored patterns and whose basins are wide",
    observable_consequence="recall accuracy vs corruption level and vs pattern count (the record's entry point)", vacuity_condition="one pattern", trivial_shortcuts="nearest-neighbour lookup over the stored list (exact, uses an index the pressure forbids)",
    cheat_control="a recaller given the stored list must recover every pattern within its Hamming basin; if the world does not distinguish it from Hebbian recall above capacity, capacity is not being tested", cost_class="CPU-scale", source_evidence="record pressure / failure; network.py", purpose="PURPOSE: associative memory (Hopfield 1982)")

c.ancestry("algorithm_from", "Hopfield 1982 (with a mean-subtraction variant of the Hebb rule)", note="from the code; the record's lineage not re-read")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["nothing ran here; the record's entry point (corruption level, pattern count past 0.14 N) is a ready Stage C experiment", "sign(0) = 0 and the 2-cycle blind spot of the energy stop are reading-level claims, unmeasured"],
          note="every line of network.py is accounted for")
c.save(state="DEEP")
