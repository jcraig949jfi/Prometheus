FUNCTIONAL CONTRACT (identical for every generation arm)

You are designing an executable dynamical MECHANISM (a "world" or substrate) in Python + numpy.

The task it lives in. Each episode presents a sequence of integer observations, one per time step:
  t = 0          a CUE symbol c in {0, 1, 2, 3}  (V = 4)
  t = 1 .. k     k DISTRACTOR symbols, each uniform in {4, 5, 6, 7}, independent of the cue
  t = k + 1      the QUERY symbol 8
The alphabet has 13 symbols (0..12; 9..12 never occur here). k varies between episodes of different experiments
(1 to 16). After the query step, an external linear or nonlinear decoder reads your mechanism's READOUT FEATURES and
tries to name the cue. The question is whether, and how, information about the cue survives the distractors and
is available at the readout.

Interface (batched: axis 0 of every array is the episode; E episodes run in parallel, E up to 4000):

    import numpy as np
    from prometheus.cosmos.c3.system import System
    from prometheus.cosmos.c3.task import Task, onehot      # onehot(int_array, n) -> (E, n) float

    class Mechanism(System):
        def __init__(self, task: Task): ...      # task.V == 4, task.k, task.n_symbols == 13; fix ALL knobs here
        def init(self, E) -> dict               # state: dict of numpy arrays, axis 0 = episode
        def noise(self, n, rng) -> dict         # all randomness for ONE step for n episodes, drawn from rng
        def step(self, state, obs_t, noise) -> dict   # obs_t: (E,) int array; return the NEW state dict
        def readout_features(self, state) -> np.ndarray   # (E, d) float: what the decoder sees after the query
        def full_state(self, state) -> np.ndarray         # (E, D) float: EVERYTHING that can influence the future

    def make(task):
        return Mechanism(task)

Rules:
- numpy only; no other imports beyond the three lines above. No file, network or clock access.
- All randomness comes from noise(n, rng); step must be a function of (state, obs_t, noise) only. Nothing that
  influences the future may live outside the state dict (e.g. on self).
- readout_features must be computed from the state only. Never pass the cue around the mechanism.
- step must cost <= ~10 ms for E = 4000 on one CPU core; state <= ~2000 floats per episode.
- No tuning against any evaluation: fix every parameter in __init__.

What to return: one Python code block that defines Mechanism and make exactly as above, followed by at most three
sentences describing the causal organisation you intended (what holds the cue, how it moves, what the readout sees).
