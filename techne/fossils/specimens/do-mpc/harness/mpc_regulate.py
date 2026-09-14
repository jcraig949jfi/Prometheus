import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
sys.path.insert(0, "examples/oscillating_masses_discrete")
import do_mpc
from template_model import template_model
from template_mpc import template_mpc
from template_simulator import template_simulator
model = template_model(); mpc = template_mpc(model, silence_solver=True); simulator = template_simulator(model)
estimator = do_mpc.estimator.StateFeedback(model)
np.random.seed(99); e = np.ones([model.n_x, 1]); x0 = np.random.uniform(-3 * e, 3 * e)
mpc.x0 = x0; simulator.x0 = x0; estimator.x0 = x0; mpc.set_initial_guess()
n0 = float(np.linalg.norm(x0)); norms = []; us = []
for k in range(40):
    u0 = mpc.make_step(x0); y = simulator.make_step(u0); x0 = estimator.make_step(y)
    if k == 20:   # DISTURBANCE: kick the plant state (the behavioral entry point)
        x0 = x0 + 2.0 * (np.random.rand(*x0.shape) - 0.5); simulator.x0 = x0; mpc.x0 = x0; estimator.x0 = x0
    norms.append(float(np.linalg.norm(x0))); us.append(float(np.asarray(u0).ravel()[0]))
print("n_x=%d n_u=%d |x0|=%.3f" % (model.n_x, model.n_u, n0))
print("|x| per step:", " ".join("%.2f" % v for v in norms))
print("u  per step:", " ".join("%+.2f" % v for v in us))
print("before kick (step 19): |x|/|x0| = %.3f ; right after kick (step 20): %.3f ; end (step 39): %.3f" % (norms[19] / n0, norms[20] / n0, norms[39] / n0))
ok = norms[39] / n0 < 0.10 and norms[20] > norms[19] and norms[39] < norms[20]   # regulated to <10% by the end, kick visible, recovered after it
print("RESULT", "OK" if ok else "FAIL")
