"""Cut: padasip-1.2.2 (ancestry-aware, Stage A COARSE; SOURCE_READ filters/base_filter.py (grepped structure), the learning_rule of all
16 filter classes, package layout; preprocess/ and detection/ by file name only; ann/ unread). One loop, sixteen update rules."""
from nyx.atlas.author import Cut

S = "vault:padasip-1.2.2/upstream/tree/padasip-1.2.2/padasip/"
c = Cut("padasip-1.2.2", mode="ANCESTRY_AWARE", inspected=["filters/base_filter.py", "filters/*.py learning_rule methods (16)", "package layout"],
        evidence=[("SOURCE_READ", S + "filters/base_filter.py"), ("SOURCE_READ", S + "filters/lms.py"), ("SOURCE_READ", S + "filters/rls.py"), ("SOURCE_READ", S + "filters/vslms_benveniste.py"), ("SOURCE_READ", S + "filters/ap.py")],
        note="the sixteen 'filters' are ONE loop with a pluggable update; the update rules decompose into four orthogonal modifications of the LMS gradient (normalisation, error shaping, step adaptation, second-order correction), which is the cut below")

lp = c.organ("predict_error_update_loop_over_a_regressor_stream", human_name="AdaptiveFilter.run / adapt", status="ACCEPTED",
    mechanism="for each sample k: y = w . x[k]; e = d[k] - y; w += learning_rule(e, x[k]); w_history[k] = w before the update; init_weights draws random or zeros or takes a vector",
    input="d (targets), x (regressor rows)", output="y, e, w_history", state="w (n taps), mu", update="per sample", assumptions=["a linear-in-parameters model w . x"],
    evidence_ref=S + "filters/base_filter.py:7-129", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="AdaptiveFilter (base_filter.py 1-130)",
    coverage={"input_topology": "STREAM", "output_topology": "STREAM", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "feedback": "CLOSED_LOOP", "update_topology": "SINGLE_STEP", "order_sensitivity": "SENSITIVE", "memory": "LAST_VALUE"})

g = c.organ("gradient_step_mu_times_error_times_input", parent=lp, human_name="LMS", status="ACCEPTED",
    mechanism="dw = mu * e * x: the instantaneous gradient of e^2 with a fixed step", input="e, x", output="dw", state="none", update="none", evidence_ref=S + "filters/lms.py:160-164", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="FilterLMS.learning_rule",
    fitness_value_in_ancestor="the base every other rule modifies", failure_landscape="UNKNOWN by run; record: mu too large diverges, too small cannot track",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "adaptation": "PARAMETER"})

nz = c.organ("step_normalised_by_instantaneous_input_power", parent=g, human_name="NLMS / NSSLMS / GNGD's nu", status="ACCEPTED",
    mechanism="mu_eff = mu / (eps + x . x): the step shrinks when the regressor is large so the update's effect on e is bounded independent of input scale; eps guards zero input (GNGD adapts eps itself)",
    input="x", output="a step scale", state="none (GNGD: eps)", update="none", evidence_ref=S + "filters/nlms.py:160-164; nsslms.py:96-100; gngd.py:85-94", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the / (eps + dot(x, x)) factor",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "NONE", "representation_sensitivity": "INVARIANT"})

sh = c.organ("error_shaping_nonlinearity_replacing_e_in_the_gradient", parent=g, human_name="sign-sign (SSLMS), LMF (e^3), LLNCOSH (tanh), GMCC (exp-abs kernel)", status="ACCEPTED",
    mechanism="the factor e in dw is replaced by f(e): sign(e) (and sign(x)) for SSLMS/NSSLMS, e^3 for LMF, tanh(lambda e) for LLNCOSH, lambda alpha exp(-lambda |e|^alpha) |e|^(alpha-1) sign(e) for GMCC; each is the gradient of a different loss (absolute, quartic, log-cosh, generalised correntropy)",
    input="e", output="f(e)", state="none", update="none", assumptions=["the loss chosen matches the noise (heavy tails favour bounded f; light tails favour steeper f)"],
    evidence_ref=S + "filters/sslms.py:99-103; lmf.py:95-99; llncosh.py:90-94; gmcc.py:78-84", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the e-dependent factor of each rule",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "uncertainty": "POINT"})

va = c.organ("step_size_adapted_from_the_correlation_of_successive_errors_and_inputs", parent=g, human_name="VSLMS (Mathews, Benveniste, Ang), GNGD's eps", status="ACCEPTED",
    mechanism="Mathews: mu += ro * e * last_e * (last_x . x) -- successive errors of the same sign on correlated inputs mean the step is too small; Benveniste: the same with a filtered gradient direction fi carried across steps (fi = (I - mu x x^T) fi + e x); GNGD adapts the regulariser eps by the same product; all keep (last_e, last_mu, last_x) as state",
    input="e, x, last_e, last_x", output="mu (and the update)", state="last_e, last_mu, last_x, (last_fi)", update="per sample", assumptions=["ro small; the correlation is a proxy for misadjustment"],
    fitness_value_in_ancestor="removes the fixed-mu dilemma the record names", evidence_ref=S + "filters/vslms_mathews.py:91-97; vslms_benveniste.py:92-100; gngd.py:85-94", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the mu-updating lines",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "memory": "LAST_VALUE", "adaptation": "PARAMETER", "feedback": "CLOSED_LOOP"})

rl = c.organ("recursive_inverse_correlation_matrix_with_forgetting", parent=lp, human_name="RLS", status="ACCEPTED",
    mechanism="R (the running inverse of the input autocorrelation) is updated by the matrix inversion lemma: R = (R - R x x^T R / (mu + x^T R x)) / mu with mu the forgetting factor; dw = R x e -- a second-order (Newton-like) step whose direction whitens the input",
    input="x, e", output="dw", state="R (n x n)", update="per sample", assumptions=["mu (forgetting) in (0, 1]; R initialised to a scaled identity"],
    fitness_value_in_ancestor="convergence independent of the input's eigenvalue spread, at n^2 cost", evidence_ref=S + "filters/rls.py:179-186", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="FilterRLS.learning_rule",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "SUPERLINEAR", "memory": "SUMMARY_STATISTIC", "resource_dependence": "COMPUTE"})

ap = c.organ("affine_projection_solving_over_a_window_of_recent_regressors", parent=lp, human_name="AP (affine projection)", status="ACCEPTED",
    mechanism="keep the last `order` regressors X and targets; e_mem = d_mem - X^T w; dw = mu * X (X^T X + eps I)^-1 e_mem -- the smallest weight change that zeroes the last `order` errors; a separate run/adapt because the memory must be shifted per sample",
    input="x, d", output="dw", state="x_mem (n x order), d_mem", update="per sample", evidence_ref=S + "filters/ap.py:133-170", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="FilterAP",
    coverage={"input_topology": "MATRIX", "output_topology": "VECTOR", "state_amount": "CONSTANT", "memory": "WINDOW", "resource_dependence": "COMPUTE"})

oc = c.organ("online_centering_by_running_means_of_input_and_target", parent=lp, human_name="OCNLMS", status="CANDIDATE",
    mechanism="a memory of recent x and d yields means m_x, m_d; the filter predicts on (x - m_x) and adds m_d; the update is NLMS on the centred data (read from the first lines of the rule only)", input="x, d", output="dw", state="the memory", update="per sample",
    evidence_ref=S + "filters/ocnlms.py:97-110", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="FilterOCNLMS",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "memory": "WINDOW"})

pp = c.organ("regressor_from_a_delay_line_of_a_scalar_history", human_name="preprocess.input_from_history", status="CANDIDATE",
    mechanism="turns a scalar sequence into rows of the last n values so the filter above can act as an FIR model (by file name and the record's 'identify a 4-tap FIR plant'; not read)", input="a sequence", output="a matrix", state="none", update="none",
    evidence_ref=S + "preprocess/input_from_history.py (name only)", evidence_grade="METADATA", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="preprocess/",
    coverage={"input_topology": "SEQUENCE", "output_topology": "MATRIX"})

dt = c.organ("novelty_detection_from_the_magnitude_of_weight_changes", human_name="detection.ELBND / LE / ESE", status="CANDIDATE",
    mechanism="consumers of w_history: a novelty score per sample from how much the weights moved (error and learning-based novelty detection by name; not read)", input="w_history, e", output="a score per sample", state="none",
    evidence_ref=S + "detection/elbnd.py, le.py, ese.py (names only)", evidence_grade="METADATA", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="detection/",
    coverage={"input_topology": "MATRIX", "output_topology": "SEQUENCE"})

c.reject("sixteen filters as sixteen organs", reason="OTHER", evidence="every learning_rule is mu * f(e) * g(x) with at most three lines of state; the rules differ along four axes (normalisation, error shaping, step adaptation, second-order direction) which are the organs above", note="the human package presents a taxonomy of names; the executable difference is a product of four switches")
c.reject("w_history / pretrained_run", reason="OTHER", evidence=S + "filters/base_filter.py:68-90,123-125 -- recording and a train/test split", note="instruments")
c.reject("ann/ (neural network module)", reason="OTHER", evidence="NOT READ; UNKNOWN, not rejected on merit")
c.reject("preprocess.standardize / pca / lda", reason="GENERIC_LANGUAGE_MECHANICS", evidence="by name: numpy conveniences around the filters", note="weak: names only")

c.edge(pp, lp, "feeds"); c.edge(lp, g, "feeds", note="e, x"); c.edge(nz, g, "transforms"); c.edge(sh, g, "transforms"); c.edge(va, g, "updates", note="mu"); c.edge(rl, lp, "feeds", note="alternative dw"); c.edge(ap, lp, "feeds", note="alternative dw"); c.edge(lp, dt, "feeds", note="w_history")
c.edge(g, rl, "competes"); c.edge(g, ap, "competes")

c.pressure("an_unknown_and_drifting_linear_plant_must_be_tracked_from_noisy_samples_with_one_update_per_sample",
    condition="the mapping from regressor to target is unknown and changes over time; each sample arrives once; the estimate must move enough to follow and little enough not to chase noise", resource_or_constraint="one pass; O(n) or O(n^2) per sample; a step-size constant chosen blind",
    failure_condition="divergence (step too large) or lag (step too small) -- the record's failure condition", world_punishes="a fixed step for a non-stationary plant", world_rewards="a step that reads the input scale and the recent error correlation",
    observable_consequence="tap error vs time across a plant switch (the record's entry point)", vacuity_condition="a stationary plant with unlimited samples (any small step wins)", trivial_shortcuts="batch least squares on all data (correct, not online; the world must forbid revisiting)",
    cheat_control="a filter told the plant's switch times and true taps must show zero error after each switch; if the world scores it equal to LMS at a mu near the stability bound, tracking is not being measured", cost_class="CPU-scale", source_evidence="record pressure / failure condition; vslms_*.py", purpose="PURPOSE: system identification, echo cancellation, equalisation")
c.pressure("the_noise_on_the_target_is_heavy_tailed",
    condition="occasional huge errors (impulsive noise) dominate a squared-error gradient and throw the weights", resource_or_constraint="no knowledge of which samples are outliers",
    failure_condition="weights jump on each impulse", world_punishes="linear-in-e updates", world_rewards="bounded error nonlinearities (sign, tanh, correntropy kernels)",
    observable_consequence="tap error under Gaussian vs impulsive noise for LMS vs SSLMS/LLNCOSH/GMCC", vacuity_condition="Gaussian noise (LMS is optimal)", trivial_shortcuts="clip the error (a crude f(e); the world should allow it)",
    cheat_control="a filter told which samples are impulses and skipping them must beat every f(e); if not, the world's noise is not impulsive", cost_class="CPU-scale", source_evidence="sslms.py, llncosh.py, gmcc.py", purpose="PURPOSE: same")
c.pressure("the_input_is_coloured_so_gradient_descent_crawls_along_the_small_eigen_directions",
    condition="regressor components are correlated; the error surface is a narrow valley; a first-order step converges at the rate of the smallest eigenvalue", resource_or_constraint="per-sample compute (O(n) vs O(n^2))",
    failure_condition="slow convergence on coloured input", world_punishes="first-order steps", world_rewards="whitening (RLS) or projection onto recent inputs (AP), paid in compute",
    observable_consequence="convergence time vs input eigenvalue spread for LMS vs RLS vs AP", vacuity_condition="white input", trivial_shortcuts="pre-whiten offline (needs the statistics the pressure hides)",
    cheat_control="a filter given the true autocorrelation must converge in ~n steps; if the world cannot separate it from LMS, the input is white", cost_class="CPU-scale", source_evidence="rls.py, ap.py", purpose="PURPOSE: same")

c.residue("PARTIALLY_EXPLAINED", ["preprocess/, detection/, ann/ characterised by names only (METADATA grade)", "OCNLMS memory handling read in part", "Ang's VSLMS variant not read (assumed the Mathews family)", "nothing ran; Techne's 4-tap plant harness is on M1"],
          note="the filter family is fully accounted for by one loop and four rule modifications plus two second-order alternatives")
c.save(state="COARSE")
