"""Cut: python-control (ancestry-aware, Stage A COARSE; SOURCE_READ control/statefbk.py lqr 258-404 (grepped, tail read), mateqn.py care
452-600 (grepped), function indexes of statefbk / mateqn / timeresp / iosys / nlsys; module list). A 17k-line control-systems toolbox
whose numerical core (the Riccati solve, integration, Schur) is DELEGATED to scipy / slycot -- an important negative anatomy."""
from nyx.atlas.author import Cut

S = "vault:python-control/upstream/tree/control/"
c = Cut("python-control", mode="ANCESTRY_AWARE", inspected=["statefbk.py (lqr, place*, ctrb/obsv/gram indexes)", "mateqn.py (care/dare/lyap, method dispatch)", "timeresp.py, iosys.py, nlsys.py (indexes)", "module list"],
        evidence=[("SOURCE_READ", S + "statefbk.py"), ("SOURCE_READ", S + "mateqn.py")],
        note="the record's entry point (LQR) is a thin organ over an external Riccati solver; the body's own machinery is representation (state-space / transfer-function / frequency-response objects), interconnection, and analysis wrappers -- most of the 17k lines are argument processing")

lq = c.organ("quadratic_cost_gain_from_a_riccati_solution_with_optional_integrator_augmentation", human_name="control.lqr / dlqr", status="ACCEPTED",
    mechanism="parse (sys | A, B), Q, R, [N]; if integral_action is given, augment A with integrator rows [A 0; C 0] and B with zero rows; call care(A, B, Q, R, N) for X (the Riccati solution), L (closed-loop eigenvalues) and G = R^-1 (B^T X + N^T); return K = G, S = X, E = L",
    input="A, B, Q, R, [N], [integral_action]", output="K, S, E", state="none", update="none", assumptions=["(A, B) stabilisable, (A, Q^1/2) detectable -- checked, if at all, by the solver below"],
    fitness_value_in_ancestor="the record's entry point; the trade-off Q vs R is the knob", evidence_ref=S + "statefbk.py:258-404", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="lqr / dlqr",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "stochasticity": "DETERMINISTIC"})

ric = c.organ("riccati_and_lyapunov_solvers_dispatched_to_slycot_or_scipy_with_shape_checking", parent=lq, human_name="mateqn.care / dare / lyap / dlyap", status="ACCEPTED",
    mechanism="validate shapes and symmetry; choose method (slycot's SB02MD / SB03MD if importable, else scipy.linalg.solve_continuous_are / a Schur-based lyapunov path at 380-381); for the generalised equation (S, E) the same two backends; return X, closed-loop eigenvalues, and the gain",
    input="A, B, Q, R, [S, E]", output="X, L, G", state="none", update="none", dependencies=["scipy.linalg.solve_continuous_are / schur", "slycot (optional)"],
    fitness_value_in_ancestor="the numerical core; NOT in the body", evidence_ref=S + "mateqn.py:84-246,452-733", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="mateqn.py",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE"})

pl = c.organ("pole_placement_by_ackermann_or_varga", human_name="place / place_varga / place_acker", status="CANDIDATE",
    mechanism="place_acker: K = [0 ... 1] ctrb(A, B)^-1 p(A) (Ackermann's formula, SISO); place_varga: slycot SB01BD (robust placement); place: scipy.signal.place_poles (by index and names; bodies not read)", input="A, B, desired poles", output="K", state="none",
    evidence_ref=S + "statefbk.py:47-257 (index)", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the place* functions",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE"})

rep = c.organ("three_interconvertible_system_representations_with_a_common_timebase", human_name="StateSpace (statesp.py), TransferFunction (xferfcn.py), FrequencyResponseData (frdata.py); lti.py / iosys.py", status="ACCEPTED",
    mechanism="a system is (A, B, C, D) matrices, or a rational-function matrix, or sampled frequency data; conversions between them (ss2tf, tf2ss via canonical forms), a discrete/continuous timebase dt carried on every object and checked when systems are combined (common_timebase), and signal naming (iosys keyword processing) -- read at index level",
    input="matrices / polynomials / data", output="system objects", state="the object", update="none", evidence_ref=S + "iosys.py:783-1364 (index); statesp.py, xferfcn.py (sizes)", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="statesp.py + xferfcn.py + frdata.py + lti.py + iosys.py",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "CONSTANT", "representation_sensitivity": "INVARIANT"})

ic = c.organ("block_diagram_interconnection_by_signal_name_matching", human_name="bdalg.py (series, parallel, feedback), interconnect (nlsys / iosys)", status="CANDIDATE",
    mechanism="systems are combined by matching named inputs to named outputs into one larger state-space or nonlinear system; feedback closes a loop with a sign (by module name and the record's closed-loop example; bodies not read)", input="systems + connections", output="one system", state="none",
    evidence_ref=S + "bdalg.py (name); nlsys.py:1346 nlsys", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="bdalg.py + interconnect",
    coverage={"input_topology": "GRAPH", "output_topology": "MATRIX"})

sim = c.organ("time_response_by_discretisation_or_ode_integration_with_a_result_object", human_name="timeresp.forced_response / step_response; nlsys.input_output_response", status="ACCEPTED",
    mechanism="for linear systems: discretise (or use the exact matrix exponential per step) and iterate x_{k+1} = A_d x_k + B_d u_k; for nonlinear systems: scipy.integrate.solve_ivp over the update function with inputs interpolated; results are returned as a TimeResponseData object with time / outputs / states / inputs and plotting (read at index level: 280-760 is the result class, 920 forced_response, 1474 input_output_response)",
    input="a system, a time vector, inputs, initial state", output="trajectories", state="none", update="per step", dependencies=["scipy.integrate.solve_ivp", "scipy.signal (cont2discrete)"],
    evidence_ref=S + "timeresp.py:280-760,920-1534; nlsys.py:1474", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="timeresp.py + nlsys.input_output_response",
    coverage={"input_topology": "MIXED", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SWEEP"})

c.reject("the numerical core (Riccati, Lyapunov, Schur, ODE integration, pole placement)", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY", evidence=S + "mateqn.py:18,380,532,539,578; timeresp/nlsys via scipy -- every heavy computation is a call into scipy or slycot", note="NEGATIVE ANATOMY: the fossil is a representation-and-wrapper layer; its machinery is elsewhere")
c.reject("frequency-domain analysis and plotting (freqplot, nichols, margins, pzmap, rlocus, sisotool, ctrlplot, timeplot, phaseplot)", reason="OTHER", evidence="by module name: analysis and plots of the representations; read-only", note="instruments")
c.reject("optimal.py (MPC / trajectory optimisation), flatsys/, stochsys.py (Kalman / LQE), robust.py (H-inf), modelsimp.py, descfcn.py, passivity.py", reason="OTHER", evidence="NOT READ; module names only", note="UNKNOWN; stochsys (Kalman) would be an R-candidate against tinyekf / simple-kalman / filterpy elsewhere in the vault")
c.reject("config.py, exception.py, matlab/ compatibility layer, tests/, bench/", reason="GENERIC_LANGUAGE_MECHANICS", evidence="by name")

c.edge(rep, lq, "feeds"); c.edge(lq, ric, "feeds"); c.edge(ric, lq, "feeds", note="X, L, G"); c.edge(lq, ic, "feeds", note="K closes the loop"); c.edge(ic, sim, "feeds"); c.edge(rep, sim, "feeds"); c.edge(pl, lq, "competes", note="two gain designs")

c.pressure("coupled_multivariable_dynamics_must_be_driven_to_rest_with_bounded_effort",
    condition="several states influence each other; the actuator has a cost; a gain that is too aggressive saturates or destabilises, too timid leaves error", resource_or_constraint="control effort (R) vs state error (Q)",
    failure_condition="divergence / a crash (record)", world_punishes="gains chosen by hand per loop; ignoring coupling", world_rewards="a gain from a quadratic cost solved over the whole coupled model",
    observable_consequence="the closed-loop trajectory to the origin under Q/R variations and disturbances (the record's entry point)", vacuity_condition="a scalar stable plant", trivial_shortcuts="a huge gain (fast, saturates; the world must bound effort)",
    cheat_control="a controller given the disturbance in advance must beat LQR on the cost; if the world's cost cannot separate them, effort or error is not being charged", cost_class="CPU-scale", source_evidence="record pressure / failure; lqr", purpose="PURPOSE: control system design and analysis (a MATLAB Control Toolbox clone)")
c.pressure("one_plant_must_be_expressed_in_whichever_form_the_analysis_needs",
    condition="design methods want state space; classical analysis wants transfer functions; measurements come as frequency data; conversions must agree and carry the sample time", resource_or_constraint="numerical conditioning of conversions",
    failure_condition="a conversion that silently changes the system (ill-conditioned tf2ss)", world_punishes="one representation", world_rewards="interconvertible objects with a shared timebase check",
    observable_consequence="round-trip ss -> tf -> ss agreement", vacuity_condition="one method", trivial_shortcuts="none",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="the three representation modules; common_timebase", purpose="PURPOSE: same")

c.residue("LARGE_RESIDUE", ["the representation classes, interconnection and simulation read at index level only", "optimal / flatsys / stochsys / robust unread", "nothing ran here; Techne's 2-state LQR harness is on M1", "the body's own numerics are nearly nil -- the atlas records the wrapper shapes and points at scipy/slycot as the true bodies"],
          note="LQR and the Riccati dispatch are read; the fossil's identity as a wrapper layer is the finding")
c.save(state="COARSE")
