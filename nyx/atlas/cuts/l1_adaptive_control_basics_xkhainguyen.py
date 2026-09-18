"""Cut: l1-adaptive-control-basics-xkhainguyen (two MATLAB scripts, 209 lines; ancestry-aware, Stage A DEEP-by-size; SOURCE_READ on M3;
fifteenth of the 2026-09-17 NOT_CUT order). Read in full: MainL1_ODE1_v2.m and the diff to v1. Nothing ran (MATLAB not on M3).
"""
from nyx.atlas.author import Cut

M = "vault:l1-adaptive-control-basics-xkhainguyen/upstream/tree/MainL1_ODE1_v2.m"
c = Cut("l1-adaptive-control-basics-xkhainguyen", mode="ANCESTRY_AWARE", inspected=["MainL1_ODE1_v2.m (all); v1 by diff"], evidence=[("SOURCE_READ", M), ("SOURCE_READ", "vault:l1-adaptive-control-basics-xkhainguyen/upstream/tree/MainL1_ODE1_v1.m")],
        note="the L1 architecture for a first-order plant, in its piecewise-constant form: a predictor of the plant, an estimator that reads the prediction error and solves for the disturbance that would explain it, and a low-pass-filtered cancellation of that estimate; the four functions are the four organs")

pred = c.organ("state_predictor_run_in_parallel_with_the_plant_using_the_current_disturbance_estimate", human_name="predictor() (dx_hat = -am*x_hat + b*(u + sigma_hat))", status="ACCEPTED",
    mechanism="a copy of the reference model driven by the same control input plus the current estimate sigma_hat, integrated at the adaptation period Ts (not the plant's dt); its output is compared with the measured plant state",
    input="u, sigma_hat, x_hat", output="x_hat at the next adaptation sample", state="x_hat", update="per Ts", assumptions=["the plant is first-order with known am and b; the unknown enters as an additive matched disturbance"],
    fitness_value_in_ancestor="the estimator needs a prediction error, not a plant model inversion", failure_landscape="UNKNOWN by run", evidence_ref=M + ":predictor", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="predictor()",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "OPEN_LOOP", "stochasticity": "DETERMINISTIC", "temporal_horizon": "STEP"})

est = c.organ("piecewise_constant_adaptive_law_solving_the_discretised_error_dynamics_for_the_disturbance", human_name="estimator() (sigma_hat = -Phi(Ts)^-1 * exp(-am Ts) * x_tilde / b)", status="ACCEPTED",
    mechanism="at each sample the prediction error x_tilde = x_hat - x is mapped to the constant disturbance that, held over one period, would produce it under the error dynamics: Phi(Ts) = (1 - exp(-am Ts))/am, mu = exp(-am Ts) x_tilde, sigma_hat = -Phi^-1 mu / b; no gain to tune, no projection: the sampling period IS the adaptation gain",
    input="x_tilde, am, b, Ts", output="sigma_hat (held constant for Ts)", state="none", update="per Ts", assumptions=["the disturbance is constant over one sample period; fast sampling makes the estimate track fast disturbances"],
    fitness_value_in_ancestor="adaptation rate decoupled from robustness: make Ts small for estimation, filter the control for robustness", failure_landscape="by reading: the estimate is noisy at the sampling rate; it must be filtered before use",
    human_prior="the piecewise-constant law is the Hovakimyan/Cao L1 design (2010); the exact discretisation (Phi) is what distinguishes it from a gradient law", evidence_ref=M + ":estimator; params.Phi_Ts", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="estimator() and the Phi_Ts line",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "feedback": "CLOSED_LOOP", "stochasticity": "DETERMINISTIC", "hidden_state": "ESTIMATES", "adaptation": "PARAMETER", "temporal_horizon": "STEP"})

ctl = c.organ("low_pass_filtered_cancellation_of_the_estimate", human_name="controller() (u = kr r - sigma_hat, then a first-order filter with time constant tau)", status="ACCEPTED",
    mechanism="the raw control cancels the estimated disturbance and tracks the reference; it is then passed through a discrete first-order low-pass (u_f = (Ts/tau) u + (1 - Ts/tau) u_prev) so that only the part of the estimate within the filter bandwidth reaches the plant",
    input="sigma_hat, r", output="u_f", state="u_prev (a global)", update="per Ts", assumptions=["the filter bandwidth is the robustness knob; the fast estimator's noise is above it"],
    fitness_value_in_ancestor="the L1 separation: fast adaptation without high-gain feedback", failure_landscape="by reading: with tau small the filter passes estimator noise; with tau large the cancellation lags the disturbance", human_prior="the filter is the defining element of L1 vs MRAC",
    evidence_ref=M + ":controller", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="controller()",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC"})

plant = c.organ("first_order_plant_with_a_scripted_piecewise_disturbance", human_name="plant() (dx = -a x + b (u + d); d = three timed bursts incl. 500 Hz and 1 kHz sinusoids)", status="ACCEPTED",
    mechanism="Euler integration at dt = 1e-4 of a first-order plant with the same a and b the controller assumes; the disturbance d is a step (100 on 10-20 ms), a 500 Hz sinusoid of amplitude 500 on a 300 offset (40-50 ms), and a 1 kHz sinusoid minus 500 (70-80 ms)",
    input="u_f, t", output="x, d", state="x", update="per dt", assumptions=["the plant is the world here: the disturbance profile is the experiment's pressure, chosen to include frequencies above and below the filter bandwidth"],
    fitness_value_in_ancestor="the demo's whole claim rests on this profile", failure_landscape="UNKNOWN by run", evidence_ref=M + ":plant, step", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="plant() and step()",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "temporal_horizon": "STEP"})

c.reject("plotting and script boilerplate (clc/close/clear; the figures)", reason="GENERIC_LANGUAGE_MECHANICS", evidence=M + ":top and the plot block")
c.reject("'L1 adaptive control' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="predictor, estimator, filter and plant are four functions with one shared parameter struct; the architecture is their wiring")
c.reject("v1 as a separate specimen", reason="OTHER", evidence="v1 samples only the adaptive law at Ts and runs predictor and controller at dt; v2 samples all three at Ts (the diff); v2 is the body cut, v1 is preserved as the author's earlier wiring", note="the wiring difference is itself a reading-level finding: where the sample-and-hold sits changes the loop")

c.edge(plant, est, "feeds", note="x"); c.edge(pred, est, "feeds", note="x_hat"); c.edge(est, ctl, "feeds"); c.edge(ctl, plant, "feeds"); c.edge(ctl, pred, "feeds"); c.edge(est, pred, "feeds", note="sigma_hat")

c.pressure("a_plant_hit_by_disturbances_faster_than_the_controller_may_respond_must_be_regulated_without_high_gain",
    condition="an organism controls a first-order process with an additive unknown input containing components both below and above a bandwidth the organism is allowed to act at; it observes only the state",
    resource_or_constraint="a sampling period; a control bandwidth (filter); no plant inversion", failure_condition="tracking error under the fast components, or instability from feeding estimator noise into the plant", world_punishes="high-gain feedback (instability) and slow adaptation (error)",
    world_rewards="estimating fast and acting slow", observable_consequence="tracking error and control effort spectrum on the three-burst profile as Ts and tau are varied", vacuity_condition="a disturbance within the control bandwidth (a PI controller suffices)",
    trivial_shortcuts="a world that reveals d", cheat_control="a controller handed d must show zero error at any bandwidth; the same architecture with tau -> 0 (no filter) must show noise amplification: the world must show both",
    cost_class="CPU-scale", source_evidence="MainL1_ODE1_v2.m plant()/controller()/estimator()", purpose="PURPOSE: L1 adaptive control demonstration (Hovakimyan & Cao 2010 architecture)")

c.ancestry("algorithm_from", "Hovakimyan & Cao, L1 Adaptive Control Theory (2010): piecewise-constant adaptation law with a state predictor and a low-pass filtered control", note="from the record's domain and the code's structure; not verified against the book this pass")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["nothing ran (MATLAB); the scripts are ~100 lines and would port to numpy for a Stage C run on M3 in an hour -- a candidate for the M3-native world class"], note="every function is an organ or rejected")
c.save(state="DEEP")
