"""Cut: simple-kalman-denyssene (Arduino 'SimpleKalmanFilter', 82 lines; ancestry-aware, Stage A DEEP-by-size; SOURCE_READ on M3;
position 22 of the 2026-09-17 NOT_CUT order). Read in full: src/SimpleKalmanFilter.h, .cpp. Nothing ran.
"""
from nyx.atlas.author import Cut

S = "vault:simple-kalman-denyssene/upstream/tree/src/SimpleKalmanFilter.cpp"
c = Cut("simple-kalman-denyssene", mode="ANCESTRY_AWARE", inspected=["src/SimpleKalmanFilter.h, .cpp (all)"], evidence=[("SOURCE_READ", S), ("SOURCE_READ", "vault:simple-kalman-denyssene/upstream/tree/src/SimpleKalmanFilter.h")],
        note="one scalar recursion in five lines; the interesting anatomy is that its 'process noise' term is not the Kalman one: the estimate error grows with the size of the last correction, not with a fixed q per step")

g = c.organ("scalar_gain_as_estimate_error_over_estimate_plus_measurement_error", human_name="updateEstimate line 1: K = err_est / (err_est + err_meas)", status="ACCEPTED",
    mechanism="the gain is the ratio of the current estimate error to the sum of estimate and measurement errors; the estimate moves toward the measurement by K times the innovation; the estimate error shrinks by (1-K)",
    input="a scalar measurement; the two error magnitudes", output="the new estimate", state="_last_estimate, _err_estimate, _kalman_gain", update="per measurement",
    assumptions=["a random-walk state with no dynamics (no prediction step: the prior is the last estimate)", "errors are treated as magnitudes, not variances (no squares anywhere)"],
    fitness_value_in_ancestor="three multiplications and one division per sample on an 8-bit microcontroller", failure_landscape="by reading: with no process-noise growth the gain decays toward zero and the filter stops tracking; the next organ is the author's fix",
    evidence_ref=S + ":updateEstimate", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the first two statements of updateEstimate",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC", "hidden_state": "ESTIMATES", "uncertainty": "POINT"})

q = c.organ("estimate_error_re_inflated_by_the_magnitude_of_the_last_correction_times_q", human_name="updateEstimate line 3: err_est = (1-K) err_est + |last - current| * q", status="ACCEPTED",
    mechanism="after shrinking the estimate error by (1-K), the code ADDS q times the absolute change the update just made; a large correction (the signal is moving) inflates the error, which raises the next gain; a quiet signal lets the error and gain decay",
    input="the innovation just applied; q", output="the next estimate error", state="_err_estimate", update="per measurement",
    assumptions=["a big correction means the model was wrong, so trust the next measurement more: an adaptive heuristic standing in for a process-noise variance"],
    fitness_value_in_ancestor="tracks steps without a tuned process model; the whole reason the library is popular", failure_landscape="by reading: the error is driven by the FILTER'S OWN output change, so measurement noise that happens to move the estimate also inflates the error (a positive feedback that the true Kalman recursion does not have); no measurement",
    human_prior="the author's own device; the Kalman process noise Q is a constant added to the prior variance, not a term proportional to |innovation|", evidence_ref=S + ":updateEstimate (third statement)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the third statement",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "stochasticity": "DETERMINISTIC", "adaptation": "PARAMETER", "failure_mode": "OSCILLATES"})

c.reject("the setters and getters, the Arduino include", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + ":set*/get*")
c.reject("'Kalman filter' as the name of this body", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="no prediction step, no variances, an adaptive error term: it is a scalar exponential smoother with an innovation-driven gain; the vault's filterpy-labbe and particles/kalman.py hold the actual recursion (recurrence test by execution is the natural Stage C)", note="RECURRENCE candidate against kalman.py at R0 (name only) -- by reading the mechanisms DIFFER")

c.edge(g, q, "feeds"); c.edge(q, g, "feeds")

c.pressure("a_noisy_scalar_must_be_smoothed_by_a_microcontroller_with_no_model_of_how_fast_the_true_value_moves",
    condition="a sensor value with noise and occasional real steps; a few bytes of state and a few operations per sample; the organism is not told the process dynamics", resource_or_constraint="constant state; one division per sample",
    failure_condition="lag on steps or noise pass-through", world_punishes="both", world_rewards="a gain that rises when the signal moves and falls when it is quiet", observable_consequence="RMS error and step-response lag on a step-plus-noise signal, against a fixed-alpha smoother and against a true Kalman filter with known Q",
    vacuity_condition="a stationary signal (fixed alpha wins) or known dynamics", trivial_shortcuts="a world that reveals the true value",
    cheat_control="an organism given the true value must score zero error; the fixed-alpha smoother must show the lag/noise trade-off this filter claims to escape: the world must show both",
    cost_class="CPU-scale", source_evidence="SimpleKalmanFilter.cpp updateEstimate; record tags sensor-fusion / signal-reconstruction", purpose="PURPOSE: cheap scalar smoothing on Arduino (Sene 2017)")

c.ancestry("inspired_by", "the scalar Kalman filter (Kalman 1960) with the process-noise term replaced by an innovation-magnitude heuristic", note="the cut's reading; the record's lineage not re-read")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["nothing ran; 82 lines port to Python in minutes -- a candidate for an M3-native recurrence test against particles/kalman.py"], note="every line is accounted for")
c.save(state="DEEP")
