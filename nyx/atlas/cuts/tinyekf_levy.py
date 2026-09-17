"""Cut: tinyekf-levy (Levy's TinyEKF, a header-only extended Kalman filter for microcontrollers; ancestry-aware, Stage A DEEP; SOURCE_READ on
M3; position 73 of the 2026-09-17 NOT_CUT order). Read: src/tinyekf.h in full at structure level (328 lines: the static matrix helpers,
the Cholesky inverse, ekf_initialize, ekf_predict, ekf_update and its three steps). NOT read: the GPS and sensor-fusion examples, the
Python package, the attic. Nothing ran (C; no compiler on M3; the Python package in python/ would be an M3 world if it is pure).
"""
from nyx.atlas.author import Cut

H = "vault:tinyekf-levy/upstream/tree/src/tinyekf.h"
c = Cut("tinyekf-levy", mode="ANCESTRY_AWARE", inspected=["src/tinyekf.h 1-328"], evidence=[("SOURCE_READ", H + ":1-328")],
        note="the extended Kalman filter with every decision made for a small fixed-point-free microcontroller: state and measurement sizes are compile-time constants (EKF_N, EKF_M) so every matrix is a stack array; the caller supplies the nonlinear prediction and its Jacobian (fx, F) and the measurement prediction and its Jacobian (hx, H), so the filter itself is only the covariance algebra; the innovation covariance is inverted by a Cholesky decomposition that reports failure, so a non-positive-definite S aborts the update instead of corrupting the state")

pred = c.organ("prediction_as_caller_supplied_state_and_jacobian_with_the_covariance_propagated_by_f_p_f_transpose_plus_q_on_stack_arrays", human_name="ekf_predict (184-200): memcpy(x, fx); FP = F P; Ft = F^T; P = FP Ft + Q; the _mulmat / _transpose / _addmat helpers (10-70)", status="ACCEPTED",
    mechanism="the caller evaluates the nonlinear transition f at the current state and its Jacobian F outside the filter and passes both in; the filter copies the predicted state and propagates the covariance with two matrix products and an addition of the process noise, all in fixed-size arrays sized by the compile-time constants",
    input="fx, F, Q", output="x, P", state="x, P", update="per time step", assumptions=["the linearisation around the current estimate is the caller's responsibility; keeping the filter ignorant of the model makes it a library of one struct and two functions"],
    fitness_value_in_ancestor="an EKF that fits an Arduino: no heap, no dynamic sizes, no model code inside", failure_landscape="by reading: no symmetrisation of P after the update; round-off can make P asymmetric over many steps in single precision (the _float_t switch exists to choose double)", human_prior="Kalman 1960; the EKF of the Apollo era (Schmidt), the record's lineage", evidence_ref=H + ":184-200", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="ekf_predict",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP"})

upd = c.organ("update_with_the_gain_from_a_cholesky_inverse_of_the_innovation_covariance_that_aborts_the_update_when_the_factorisation_fails", human_name="ekf_update (215-300): G = P H^T (H P H^T + R)^{-1} via invert() -> _cholsl (116-160, returns nonzero on a non-positive pivot); x += G (z - hx); ekf_update_step3 (199-206): P = (I - G H) P", status="ACCEPTED",
    mechanism="the innovation covariance S = H P H^T + R is inverted by Cholesky decomposition (choldc1) followed by forward and backward substitution; a non-positive diagonal during the decomposition returns an error and the update returns false, leaving x and P as predicted; otherwise the gain is P H^T S^-1, the state is corrected by the gain times the innovation z - hx (with hx supplied by the caller from its measurement model), and the covariance is reduced by the Joseph-less form (I - G H) P",
    input="z, hx, H, R", output="x, P, a success flag", state="x, P", update="per measurement", assumptions=["S is symmetric positive definite whenever the model and noises are sane; a Cholesky failure is a better signal of a bad measurement or model than a NaN in the state"],
    fitness_value_in_ancestor="the standard EKF update with a cheap, explicit sanity gate", failure_landscape="by reading: (I - G H) P is numerically less stable than the Joseph form; no innovation gating beyond the factorisation check", human_prior="the standard EKF equations; Cholesky inversion from Numerical Recipes (the attic's origin per the comments)", evidence_ref=H + ":116-160, 199-300", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="ekf_update, invert, _cholsl",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "feedback": "CLOSED_LOOP", "stochasticity": "DETERMINISTIC", "failure_mode": "DEGRADES", "recovery": "DEGRADES_GRACEFULLY"})

c.reject("the matrix helpers (_mulmat, _mulvec, _transpose, _addmat, _negate, _addeye, _addvec, _sub: naive triple loops)", reason="BELOW_MEANINGFUL_GRAIN", evidence=H + ":10-160", note="substrate; the Cholesky routines are counted in the update organ")
c.reject("the GPS and sensor-fusion examples, the Python package (python/tinyekf, altitude_fuser.py, mousetracker.py), the attic", reason="OTHER", evidence="NOT READ; residue", note="the GPS example ships data and a reference output: a Stage C oracle")
c.reject("'Kalman filter' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="prediction and update are separable and the model is outside the body; the atlas's simple-kalman (not a Kalman filter) and particles/kalman.py are the recurrence set")

c.edge(pred, upd, "feeds"); c.edge(upd, pred, "feeds", note="the corrected state")

c.pressure("a_nonlinear_state_must_be_tracked_from_noisy_sensors_on_a_processor_with_no_heap_and_little_arithmetic_where_a_single_bad_measurement_must_not_corrupt_the_estimate",
    condition="an organism fuses sensors into a state estimate on a microcontroller; the dynamics and measurements are nonlinear; memory is static; occasional measurements are inconsistent (a corrupt GPS fix); the score is estimate error and the absence of divergence", resource_or_constraint="stack arrays sized at compile time; no heap",
    failure_condition="divergence after a bad measurement, or memory that grows with the problem", world_punishes="an update that inverts S without checking; dynamic allocation", world_rewards="fixed-size arrays and an abort on a failed factorisation",
    observable_consequence="position error on the GPS example's data with a corrupted fix injected, for the update with and without the Cholesky abort; peak stack use", vacuity_condition="a linear model with consistent measurements", trivial_shortcuts="a desktop EKF with the Joseph form and gating (which costs what the target lacks)",
    cheat_control="an organism given the true trajectory must show zero error; the update without the abort must diverge on the injected fix; with the abort it must skip the fix and continue: the world must show all three",
    cost_class="CPU-scale", source_evidence="tinyekf.h ekf_update and _cholsl; the examples' data", purpose="PURPOSE: embedded state estimation (Levy 2015-)")

c.ancestry("reimplementation_of", "the extended Kalman filter (Schmidt 1960s after Kalman 1960); Cholesky inversion after Numerical Recipes", note="from the header and the record")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["examples and the Python package unread", "nothing ran"], note="a 328-line header fully accounted for")
c.save(state="DEEP")
