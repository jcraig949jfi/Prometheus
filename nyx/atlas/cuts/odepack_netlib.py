"""Cut: odepack-netlib (ancestry-aware, Stage A COARSE-by-breadth, first of the 2026-09-17 NOT_CUT order; SOURCE_READ on M3).
Read in full: opkda1.f DSTODE (630-1127, the one-step core), DCFODE (47-174), DPREPJ (283-476), DSOLSY (477-567),
DEWSET/DVNORM (1128-1210), DINTDY (175-282); opkdmain.f DLSODE executable blocks B-G (1243-1660: options, initial step,
step budget, error returns). Read in part: opkda1.f DSTODA (3803-4436) for the automatic method switch only (3947-4227).
NOT read: DLSODES/DLSODPK/DLSODKR/DLSODI/DLSOIBT/DLSODIS drivers and their sparse / Krylov / implicit cores (opkda1.f
1211-3802, 5175-10136), the root finder DRCHEK/DROOTS, opkda2.f (LINPACK + error message machinery). Nothing ran.

The record's behavioural entry point (switch MF between Adams and BDF on one problem; vary MXSTEP) is a ready SCOUT.
"""
from nyx.atlas.author import Cut

A1 = "vault:odepack-netlib/upstream/opkda1.f"
MAIN = "vault:odepack-netlib/upstream/opkdmain.f"
c = Cut("odepack-netlib", mode="ANCESTRY_AWARE",
        inspected=["opkda1.f: DSTODE, DCFODE, DPREPJ, DSOLSY, DEWSET, DVNORM, DINTDY (all); DSTODA (switch section only)",
                   "opkdmain.f: DLSODE blocks B-G (all); the DLSODE prologue skimmed for MXSTEP/ISTATE semantics"],
        evidence=[("SOURCE_READ", A1 + ":630-1127"), ("SOURCE_READ", A1 + ":47-567"), ("SOURCE_READ", A1 + ":1128-1210"),
                  ("SOURCE_READ", A1 + ":175-282"), ("SOURCE_READ", MAIN + ":1243-1660"), ("SOURCE_READ", A1 + ":3947-4227")],
        note="the famous names (LSODE, Gear's method, BDF) sit above a small set of mechanisms that are each replaceable: "
             "a scaled-derivative history array, a predictor that is pure addition, a corrector with a self-measured convergence "
             "rate, a weighted-RMS error test, a three-candidate step/order chooser with hysteresis and hold-off, a Jacobian "
             "refresh policy keyed to how far the iteration matrix has drifted, and a failure ladder with escalating retreats")

yh = c.organ("nordsieck_history_array_of_scaled_derivatives", human_name="the YH array (Nordsieck form)", status="ACCEPTED",
    mechanism="state is kept as YH(i,j+1) = h^j y_i^(j) / j! for j = 0..NQ, i.e. the solution and its scaled Taylor coefficients at the current point, one column per order; "
              "a change of step size h -> rh*h is a column-wise rescale by rh^j (DSTODE 175-180); a change of order adds or drops a column; the array is also what the interpolant reads",
    input="the accepted correction ACOR and the coefficients EL(j) after a successful step", output="the current state for every consumer (predictor, error test, order change, interpolation, restart)",
    state="N x (MAXORD+1) doubles", update="per accepted step (470: YH(i,j) += EL(j)*ACOR(i)); rescaled on every h change",
    assumptions=["the scaled derivatives are meaningful, i.e. the solution is smooth enough at the current order; the failure ladder (KFLAG <= -3) says explicitly when it stops trusting them"],
    fitness_value_in_ancestor="one representation serves prediction, correction, error control, order change, step change and dense output; nothing is recomputed from past solution values",
    failure_landscape="by reading: after repeated error-test failures the accumulated derivatives are assumed wrong and the array is truncated to order 1 with a fresh f evaluation (640-650); no measurement",
    human_prior="Nordsieck (1962) representation chosen over storing past y values (the multistep textbook form); the choice is what makes step changes cheap",
    evidence_ref=A1 + ":630-1127 (YH usage; rescale 175-180; update 470; truncate 640-650)", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="every YH read/write in DSTODE; the LYH slice of RWORK in the driver",
    coverage={"input_topology": "VECTOR", "output_topology": "MATRIX", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "memory": "WINDOW",
              "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP", "representation_sensitivity": "SENSITIVE", "temporal_horizon": "WINDOW"})

pred = c.organ("predictor_by_pascal_triangle_summation_in_place", human_name="predict (200-215)", status="ACCEPTED",
    mechanism="advance the history array to TN+H by NQ passes of in-place column additions YH1(I) += YH1(I+NYH) from the highest order down: multiplication by the Pascal-triangle matrix with no multiplications; "
              "the same loop with subtraction (440-445, 510-515) is the exact retraction used on failure",
    input="YH at TN", output="predicted YH at TN+H (first column = predicted y)", state="none beyond YH", update="once per attempted step",
    assumptions=["the Taylor form of YH (the organ above); exactness of the retraction relies on the additions being reversible in floating point only approximately (not measured)"],
    fitness_value_in_ancestor="the predictor costs ~N*NQ additions and no function evaluations", failure_landscape="UNKNOWN by run",
    evidence_ref=A1 + ":200-215 (predict), 440-445 and 510-515 (retract)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN",
    source_boundary="loops 210/215 and their inverses",
    coverage={"input_topology": "MATRIX", "output_topology": "MATRIX", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "order_sensitivity": "SENSITIVE", "recovery": "ROLLS_BACK"})

corr = c.organ("corrector_iteration_with_self_measured_convergence_rate", human_name="corrector loop 220-410 (functional or chord/Newton)", status="ACCEPTED",
    mechanism="up to MAXCOR=3 iterations of either functional iteration (MITER=0: y <- y0 + el(1)*(h f(y) - yh2)) or the chord method (solve P dy = h f - (yh2 + acor) with P = I - h*el0*J held fixed); "
              "after each iteration the weighted norm DEL of the correction is taken and CRATE = max(0.2*CRATE, DEL/DELP) estimates the contraction rate; the stopping test is DEL*min(1, 1.5*CRATE) <= TESCO(2,NQ)*CONIT, "
              "i.e. the iteration is declared converged when its PREDICTED remaining error is below the local error test scale, not when the last correction is tiny; divergence (DEL > 2*DELP at M >= 2) aborts early",
    input="predicted YH, the iteration matrix P (if chord), f", output="the accumulated correction ACOR and the corrected y, or a convergence failure", state="CRATE (persists across steps, reset to 0.7 when P is refreshed), DELP",
    update="per corrector iteration",
    assumptions=["contraction is roughly geometric so one ratio predicts the tail", "for the chord method P may be stale (it is deliberately reused; see the refresh policy organ)"],
    fitness_value_in_ancestor="the convergence test is calibrated to the error test, so no iterations are spent beyond what the step can use; CRATE lets a slow iteration stop early and trigger a matrix refresh instead of burning MAXCOR",
    failure_landscape="by reading: with MITER=0 on a stiff problem the iteration diverges for any step larger than ~1/|lambda| and the ladder shrinks h until the budget is exhausted (the record's failure)",
    human_prior="MAXCOR=3 and the 0.2/1.5 constants are Hindmarsh's tuning; not derived",
    evidence_ref=A1 + ":220-410", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="labels 220-410",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "memory": "LAST_VALUE",
              "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP", "failure_mode": "DIVERGES", "hidden_state": "ESTIMATES"})

err = c.organ("weighted_rms_local_error_test", human_name="DEWSET + DVNORM + the DSM <= 1 test (450)", status="ACCEPTED",
    mechanism="error weights EWT(i) = RTOL*|y_i| + ATOL(i) are recomputed from the current y before every step (driver 250-260) and inverted; every norm in the integrator is the RMS of v_i/EWT_i (DVNORM); "
              "the local error estimate is the norm of the accumulated correction divided by TESCO(2,NQ) (a method constant), and the step is accepted iff that is <= 1",
    input="y, RTOL, ATOL, ACOR", output="EWT vector; the scalar DSM; accept/reject", state="EWT (per step)", update="per step",
    assumptions=["a mixed relative/absolute tolerance is the right notion of close; components with EWT <= 0 are an illegal input (driver 510, ISTATE=-6)"],
    fitness_value_in_ancestor="one scalar drives every decision (convergence, acceptance, step and order choice), and it is dimensionless so the same constants serve every problem",
    failure_landscape="by reading: TOLSF = uround * ||y||_EWT > 1 means the tolerance is below machine precision; the driver returns ISTATE=-2 (520) rather than loop",
    evidence_ref=A1 + ":1128-1210 and 450; " + MAIN + ":250-280, 520", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="DEWSET, DVNORM, label 450, driver 250-280",
    coverage={"input_topology": "VECTOR", "output_topology": "DECISION", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "uncertainty": "POINT", "representation_sensitivity": "SENSITIVE"})

sel = c.organ("step_and_order_selection_by_three_candidate_ratios_with_hysteresis_and_holdoff", human_name="520-630 (RHDN / RHSM / RHUP)", status="ACCEPTED",
    mechanism="after a step (success or failure) three step-size multipliers are computed from error estimates at orders NQ-1, NQ, NQ+1: RH = 1/(c * D^(1/(q+1)) + tiny) with c = 1.3, 1.2, 1.4; "
              "the largest wins; a change is made only if RH >= 1.1 (else IALTH=3: do not look again for 3 steps); after any change IALTH = NQ+1 steps of hold-off; RMAX caps the increase at 10 (1e4 on the first step, 2 after a failure); "
              "on failure RHUP=0 (never raise order) and after two failures RH <= 0.2; the order-up estimate needs the previous step's correction, which is saved into the spare column only when IALTH=1",
    input="DSM, ACOR, YH(:,L), the saved previous correction, KFLAG", output="new H, new NQ (NQ-1, NQ, NQ+1)", state="IALTH (hold-off counter), RMAX, the spare YH column", update="per step",
    assumptions=["the local error scales as h^(q+1) (the exponent in each ratio)", "changing h or q costs a rescale and destabilises the estimates, hence the hold-off"],
    fitness_value_in_ancestor="the step and order track the solution's smoothness without a fixed schedule; the hysteresis (1.1) and hold-off (IALTH) stop the controller chattering",
    failure_landscape="by reading: the constants 1.3/1.2/1.4 bias toward keeping or lowering order; an order increase is only ever tried from a clean step (RHUP=0 on failure)",
    human_prior="the safety factors and the 1.1 threshold are tuning; the asymmetric bias against order increase is a design choice recorded in the code, not in the prologue",
    evidence_ref=A1 + ":520-630 and 100-125 (same formula on a MAXORD change)", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="labels 520-630",
    coverage={"input_topology": "MIXED", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "memory": "LAST_VALUE",
              "stochasticity": "DETERMINISTIC", "adaptation": "PARAMETER", "failure_mode": "OSCILLATES", "temporal_horizon": "STEP"})

jref = c.organ("jacobian_refresh_policy_keyed_to_iteration_matrix_drift", human_name="IPUP / RC / CCMAX / MSBP / JCUR (200, 220-250, 410)", status="ACCEPTED",
    mechanism="the iteration matrix P = I - h*el0*J is NOT rebuilt every step: RC tracks the ratio of the current h*el0 to the one P was built with; P is rebuilt when |RC-1| > CCMAX=0.3, or every MSBP=20 steps, or when the corrector "
              "fails to converge with a stale P (JCUR=0 -> refresh and retry the same step before reducing h); refreshing resets CRATE to 0.7",
    input="h, el0, NST, corrector outcome", output="a rebuild decision (IPUP=MITER) or reuse", state="RC, NSLP (step of last build), JCUR", update="per step and per convergence failure",
    assumptions=["J changes slowly along the solution; a wrong P only slows the chord iteration, it does not change the fixed point"],
    fitness_value_in_ancestor="the expensive operation (N function evaluations or a user Jacobian plus an LU) is amortised over ~20 steps; a convergence failure is first blamed on staleness, then on the step",
    failure_landscape="UNKNOWN by run", human_prior="CCMAX=0.3, MSBP=20 are tuning constants set in the driver (opkdmain.f 110-118)",
    evidence_ref=A1 + ":200, 220-250, 410; " + MAIN + ":1380-1390 (CCMAX, MAXCOR, MSBP, MXNCF constants)", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="the IPUP/RC/NSLP/JCUR variables and their tests",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "LAST_VALUE", "stochasticity": "DETERMINISTIC",
              "update_topology": "EVENT_DRIVEN", "resource_dependence": "COMPUTE", "adaptation": "NONE"})

pmat = c.organ("iteration_matrix_construction_strategies_by_MITER", human_name="DPREPJ / DSOLSY (MITER 1-5)", status="ACCEPTED",
    mechanism="five ways to build and apply P = I - h*el0*J behind one interface: 1 user dense Jacobian; 2 finite-difference dense (N extra f calls, increment R = max(sqrt(uround)*|y_j|, r0/EWT_j) with r0 = 1000*|h|*uround*N*||f||); "
              "3 a DIAGONAL approximation from ONE extra f call along the predicted correction direction (a diagonal Jacobian-vector estimate; the solve is a vector divide, rescaled when h*el0 changes without a rebuild, DSOLSY 300-390); "
              "4 user banded; 5 finite-difference banded (MBAND extra f calls, columns grouped by band); dense/banded go through LINPACK LU (DGEFA/DGBFA) and back-solve",
    input="y, f, h*el0, (JAC), band widths", output="P factored in WM, or IERPJ", state="WM (the factored matrix; for MITER=3 the diagonal and the h*el0 it was built at)", update="on refresh",
    assumptions=["for MITER=3 the diagonal approximation is only good when J is nearly diagonal in the EWT scaling; the code cannot tell and the corrector rate (CRATE) is the only signal"],
    fitness_value_in_ancestor="cost/accuracy of the Newton matrix is a user choice orthogonal to the integrator (DSTODE is independent of MITER, prologue)", failure_landscape="UNKNOWN by run",
    evidence_ref=A1 + ":283-567", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="DPREPJ + DSOLSY",
    coverage={"input_topology": "VECTOR", "output_topology": "MATRIX", "state_amount": "SUPERLINEAR", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "resource_dependence": "COMPUTE",
              "uncertainty": "POINT"})

lad = c.organ("failure_escalation_ladder_with_bounded_retreats", human_name="410-445, 500-515, 640-680; driver 500-560", status="ACCEPTED",
    mechanism="convergence failure: refresh P if stale, else retract, RMAX=2, h*0.25, count NCF; at MXNCF=10 or h=HMIN -> KFLAG=-2. error-test failure: retract, KFLAG-1, choose h at order NQ or NQ-1 with RHUP=0; "
              "after 2 failures h <= 0.2*h; after 3 the history is distrusted: order -> 1, f re-evaluated, h*0.1, IALTH=5; at 10 failures or h=HMIN -> KFLAG=-1. driver: MXSTEP (default 500) steps per call -> ISTATE=-1 with the partial solution returned; "
              "T+H == T in floating point -> a warning up to MXHNIL=10 times, then silence, integration continues",
    input="KFLAG history, NCF, h, HMIN", output="a retry with a smaller h and/or lower order, or a typed failure return with the state as of the last good step", state="KFLAG, NCF, RMAX, NHNIL, NST-NSLAST", update="per failure",
    assumptions=["the last accepted state is always recoverable (retraction is exact enough); failures are local, so shrinking h is the right first move"],
    fitness_value_in_ancestor="every failure is typed (-1 budget, -2 precision, -4 error test, -5 corrector, -6 weights) and returns the solution as far as it got with the offending component (IWORK(16)) named; nothing is silently wrong",
    failure_landscape="the record's own: a non-stiff method on a stiff problem exhausts MXSTEP (ISTATE=-1) rather than diverging; the ladder makes the failure cheap and legible",
    human_prior="the retreat factors 0.25 / 0.2 / 0.1 and the counts 10 / 10 / 500 are tuning",
    evidence_ref=A1 + ":410-445, 500-515, 640-680; " + MAIN + ":1494, 1580-1660", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the labelled failure paths",
    coverage={"input_topology": "EVENT", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN",
              "failure_mode": "STALLS", "recovery": "DEGRADES_GRACEFULLY", "resource_dependence": "COMPUTE"})

h0 = c.organ("initial_step_size_from_tolerance_and_first_derivative_norm", human_name="Block C, H0 (opkdmain.f 1423-1443)", status="ACCEPTED",
    mechanism="if the user gives no H0: TOL = max(RTOL, ATOL/|y|) clipped to [100*uround, 1e-3]; H0 = 1/sqrt(1/(TOL*W0^2) + TOL*||f||_EWT^2) with W0 = max(|T|,|TOUT|); capped by |TOUT-T| and HMAX; then RMAX=1e4 lets the first accepted step grow fast",
    input="y0, f(y0), tolerances, T, TOUT", output="H0", state="none", update="once per problem",
    assumptions=["a first step that is too small is cheap to recover from (RMAX=1e4 on the first step), so the heuristic errs small"],
    fitness_value_in_ancestor="removes a user parameter; the two terms balance a time-scale bound and a derivative bound", failure_landscape="UNKNOWN by run",
    evidence_ref=MAIN + ":1423-1443", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="Block C from label 100 to 190",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "temporal_horizon": "INSTANT"})

cf = c.organ("method_coefficient_generator_from_polynomial_recurrences", human_name="DCFODE (Adams to order 12, BDF to order 5)", status="ACCEPTED",
    mechanism="the integration coefficients EL(1..q+1) and the three test constants TESCO(1..3,q) for every order are generated at run time from the coefficients of the product polynomial (x+1)(x+2)...(x+q-1) built by an integer-like recurrence; "
              "Adams: integrate the polynomial (PINT, XPIN); BDF: normalise by PC(2); the maximum orders (12, 5) are hard limits of the tables",
    input="METH", output="ELCO(13,12), TESCO(3,12)", state="none (recomputed on a method change)", update="on method change",
    assumptions=["BDF above order 5 is unstable (the human record's reason for MXORDS=5); the table size encodes that prior"],
    fitness_value_in_ancestor="no stored tables; the same code serves two method families", failure_landscape="UNKNOWN by run", human_prior="the two families and their order caps",
    evidence_ref=A1 + ":47-174", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="DCFODE",
    coverage={"input_topology": "SCALAR", "output_topology": "MATRIX", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE"})

interp = c.organ("dense_output_by_evaluating_the_history_polynomial", human_name="DINTDY", status="ACCEPTED",
    mechanism="the k-th derivative at any T in [TN-HU, TN] is read off the history array by a Horner-like sum over the columns with s = (T-TN)/H and falling-factorial coefficients; no extra f calls; T outside the last step is refused (IFLAG)",
    input="T, k, YH", output="y^(k)(T)", state="none", update="on demand",
    assumptions=["the history polynomial is accurate over the last step only"], fitness_value_in_ancestor="output at user times decoupled from the step sequence (ITASK=1 interpolates rather than stepping to TOUT)",
    failure_landscape="UNKNOWN by run", evidence_ref=A1 + ":175-282", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="DINTDY",
    coverage={"input_topology": "MATRIX", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "temporal_horizon": "STEP"})

sw = c.organ("automatic_stiffness_switch_from_corrector_rate_lipschitz_estimate", human_name="DSTODA method switch (DLSODA), read in part", status="CANDIDATE",
    mechanism="(DLSODA only) after each converged corrector the contraction rate is turned into a local Lipschitz-constant estimate PDEST = max(PDEST, RATE/|h*el(1)|); every ICOUNT steps the code computes the step the OTHER family could take "
              "(a stability-bounded step for Adams, SM1(NQ)/PDH; an error-bounded step for BDF) and switches only if the other family's step is at least RATIO=5 times larger; a switch resets order and rescales YH",
    input="corrector rate, h, NQ, DSM", output="METH (1 Adams / 2 BDF), MITER", state="PDEST, PDLAST, ICOUNT, IRFLAG", update="per step; decision every ICOUNT steps",
    assumptions=["the corrector's contraction rate is a usable proxy for the spectral radius of h*J (a stiffness detector with no eigenvalue computation)"],
    fitness_value_in_ancestor="removes the user's MF choice -- the record's failure mode (wrong family for the problem) is what this organ exists to prevent",
    failure_landscape="UNKNOWN by run; by reading the RATIO=5 hysteresis prevents flapping but delays the switch", human_prior="RATIO=5, ICOUNT=20 tuning",
    evidence_ref=A1 + ":3947-3954, 4008-4016, 4109-4123, 4174-4227 (read); the rest of DSTODA not read", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="the /DLSA01/ common block variables and the switch section of DSTODA; CANDIDATE because only part of the routine was read",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "memory": "SUMMARY_STATISTIC",
              "stochasticity": "DETERMINISTIC", "adaptation": "POLICY", "hidden_state": "ESTIMATES"})

c.reject("LINPACK DGEFA/DGESL/DGBFA/DGBSL (LU factor and solve) and DUMACH (unit roundoff), opkda2.f", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY", evidence="opkda2.f is the LINPACK/BLAS subset plus XERRWD; called, not part of the integrator's anatomy")
c.reject("XERRWD / XSETF / XSETUN message machinery", reason="OTHER", evidence="instrument: prints the typed failure; the typing itself is the ladder organ", note="an instrument, not a mechanism")
c.reject("DSRCOM/DSRCMA (save/restore of the COMMON block for interrupt/restart)", reason="GENERIC_LANGUAGE_MECHANICS", evidence=A1 + ":568-629; a workaround for Fortran COMMON, no behaviour")
c.reject("Gear's method / BDF / LSODE as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the family choice is one integer (METH) into DCFODE; every other mechanism is shared by both families")
c.reject("the sibling drivers DLSODES/DLSODA/DLSODAR/DLSODPK/DLSODKR/DLSODI/DLSOIBT/DLSODIS and their cores", reason="OTHER", evidence="NOT READ this pass (opkda1.f 1211-3802, 5175-10136; opkdmain.f 1757-16587); residue, not a rejection on the merits", note="a second pass on the sparse (DPRJS/DSOLSS) and Krylov (DSPIOM/DSPIGMR) cores is where new anatomy is most likely")

c.edge(yh, pred, "feeds"); c.edge(pred, corr, "feeds"); c.edge(pmat, corr, "feeds"); c.edge(jref, pmat, "triggers"); c.edge(corr, jref, "triggers", note="a stale-P convergence failure forces a rebuild")
c.edge(corr, err, "feeds"); c.edge(err, sel, "gates"); c.edge(err, lad, "triggers"); c.edge(corr, lad, "triggers"); c.edge(sel, yh, "updates", note="rescale on h change; add/drop a column on order change")
c.edge(lad, yh, "restores"); c.edge(lad, sel, "gates", note="RHUP=0 and RH<=0.2 after failures"); c.edge(cf, corr, "feeds"); c.edge(cf, sel, "feeds"); c.edge(yh, interp, "feeds"); c.edge(h0, yh, "feeds", note="first column scaling")
c.edge(corr, sw, "feeds", note="DLSODA only"); c.edge(sw, cf, "selects", note="DLSODA only"); c.edge(jref, corr, "updates", note="CRATE reset to 0.7 on rebuild")

c.pressure("dynamics_with_widely_separated_time_scales_under_a_finite_step_budget_and_an_accuracy_tolerance",
    condition="the world's state evolves under a rule whose fastest mode decays 10^6-10^10 times faster than the slow behaviour of interest; the organism must report the slow behaviour to a stated tolerance within a bounded number of evaluations of the rule",
    resource_or_constraint="a step/evaluation budget (the ancestor's MXSTEP=500 per call) and a tolerance; the rule's derivative is available but its Jacobian is expensive",
    failure_condition="budget exhausted before the horizon (the ancestor's ISTATE=-1) or a reported answer outside tolerance", world_punishes="taking steps at the fast time scale; reporting an answer that drifts from the slow solution",
    world_rewards="an organism whose step is bounded by the slow behaviour, not by the fast mode's stability limit", observable_consequence="evaluations used vs tolerance achieved on the same problem across stiffness ratios (the record's Robertson-type entry point)",
    vacuity_condition="a problem with one time scale, or a budget so large that the fast scale can be resolved", trivial_shortcuts="a fixed tiny step with an unlimited budget; reading the analytic slow manifold if the world exposes it; a lookup of the answer",
    cheat_control="an organism handed the exact solution must be scored as passing the tolerance at zero evaluations, and a fixed-step explicit organism must be scored as exhausting the budget at stiffness ratio 10^6: if the world cannot separate those two the pressure is not present",
    cost_class="CPU-scale", source_evidence="record human_failure_condition; DLSODE 1494/500; DSTODE 410-445", purpose="PURPOSE: stiff ODE integration (Hindmarsh)")

c.pressure("an_expensive_model_of_the_local_dynamics_must_be_reused_across_steps_and_refreshed_only_when_it_has_drifted",
    condition="an organism may build a local linear model of the world's rule at a cost of N evaluations, and each step's inner solve is cheap given the model; the model decays in usefulness as the state moves",
    resource_or_constraint="evaluation budget; the model's cost is N times a step's cost", failure_condition="rebuilding every step (budget) or never rebuilding (inner iteration diverges)",
    world_punishes="both extremes", world_rewards="a refresh policy that reads its own convergence behaviour", observable_consequence="rebuilds per 100 steps vs inner-iteration failures per 100 steps",
    vacuity_condition="the model is free, or the rule is linear so the model never drifts", trivial_shortcuts="a fixed rebuild period tuned to the test problem",
    cheat_control="an organism given a free exact model must show zero inner failures and zero rebuild cost; a policy that rebuilds every step must be scored as spending N-fold budget: the world must price the rebuild or the pressure is absent",
    cost_class="CPU-scale", source_evidence="DSTODE 200-250, 410; driver constants CCMAX/MSBP", purpose="PURPOSE: amortised Newton matrix (chord method)")

c.pressure("a_controller_of_its_own_resolution_must_not_chatter",
    condition="an organism chooses its own step/resolution from an error signal it computes; changes are costly (rescaling, invalidated estimates) and the error signal is noisy at the step scale",
    resource_or_constraint="each change costs a rescale and a hold-off during which estimates are unreliable", failure_condition="oscillating resolution (step up, fail, step down, ...) that wastes the budget",
    world_punishes="a high change count per accepted step", world_rewards="hysteresis and hold-off that still track real changes in the solution's smoothness",
    observable_consequence="changes per accepted step and rejected steps per accepted step on a problem whose smoothness varies (a known transient)", vacuity_condition="a constant-smoothness problem where one step size is right throughout",
    trivial_shortcuts="never change the step (fails the tracking half); change only downward", cheat_control="a controller fed the exact optimal step sequence must score zero rejections; a controller with hysteresis disabled must show more changes on the same problem: if the world cannot see the difference it is not measuring chatter",
    cost_class="CPU-scale", source_evidence="DSTODE 520-630 (the 1.1 threshold, IALTH, RMAX)", purpose="PURPOSE: adaptive step/order control (Gear/Hindmarsh)")

c.ancestry("algorithm_from", "Gear (1971) DIFSUB; Hindmarsh GEAR (1974) -> LSODE (1983); the Nordsieck (1962) representation", note="from the prologues (revision history 791129) and the record's lineage; not independently verified this pass")
c.residue("PARTIALLY_EXPLAINED", ["the sparse-Jacobian core (DPRJS/DSOLSS with the Yale sparse package), the Krylov cores (DSPIOM/DSPIGMR/DPCG), the implicit-form cores (DSTODI, DAINVG) and the root finder (DRCHEK/DROOTS) were not read: ~7,500 of 10,136 lines of opkda1.f",
                                   "the DLSODA switch was read for its decision rule only; its rescaling and order reset on switch were not traced",
                                   "no constant (MAXCOR, CCMAX, MSBP, 1.1, 0.2, RATIO=5) was tested; every tuning claim is SOURCE_READ"],
          note="the DLSODE path is accounted for line by line; the body is one integrator with many front ends and this cut covers the common core plus one front end")
c.save(state="COARSE")
