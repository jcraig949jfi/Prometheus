# NS-01 arm prompts (exact text; frozen before generation)

## ARM A first turn
```
You are a generator in a controlled experiment. Do NOT use any tools at all (no file reads, no searches, no commands); answer only from the text in this conversation. Reply with exactly one proposal per turn.

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

Propose a new executable mechanism.
```
## ARM B first turn
```
You are a generator in a controlled experiment. Do NOT use any tools at all (no file reads, no searches, no commands); answer only from the text in this conversation. Reply with exactly one proposal per turn.

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

OPERATOR CHALLENGE (verbatim):
Assume we have fourteen previously characterized failures.

We want to issue the following request:

We expect your next proposal to fail in one of these fourteen known ways.

Avoid reproducing those failure mechanisms.

We do not require success.

Generate something causally different, even if it exposes a fifteenth failure.

Do not disguise an old mechanism with different terminology, equations, representations, or implementation details.

Produce something executable that we can investigate.

The fourteen previously characterized failures (verbatim):
ID	Previously encountered failure
E01	Rediscovering the task’s planted economics rather than an independent law
E02	Reconstructing a certificate through coordinates derived from its own measurement machinery
E03	Encoding substrate-family identity instead of shared causal structure
E04	Exploiting differences in family prevalence to manufacture pooled predictive improvement
E05	Selecting candidate laws using evidence subsequently presented as independent confirmation
E06	Rejecting valid invariants through uncontrolled multiplicity
E07	Circumventing measurement firewalls through apparently independent SYSID probes
E08	Constructing two certificates that share the same underlying causal contrast
E09	Passing intervention tests through indirect remeasurement rather than independent explanation
E10	Producing apparent discrimination from single-class or insufficiently populated evaluation strata
E11	Promoting effects that lack a meaningful minimum magnitude
E12	Mistaking representation-dependent or observer-frame-dependent measurements for invariant physics
E13	Assuming local linear composition transfers to nonlinear or phase-based mechanisms
E14	Assuming a common cross-substrate decision boundary where independent-family experiments reject it

For mechanisms, the archive's characterized failure classes are:
- M-DEGENERATE: cue never reaches the state at the query
- M-DECAY: contraction / noise loses the cue as k grows
- M-LINBLIND: cue present but readable only nonlinearly
- M-HIDDEN: cue carried outside the declared state
- M-UNREACHABLE: cue held in the state but not at the readout (passive storage; sensor out of reach)
- M-NONMONOTONE: usability returns or rises with k (geometry, ring return, trace spread)
- M-INTERFERENCE: distractors overwrite what silence preserves (capacity)

Propose a new executable mechanism.
```
## ARM C first turn
```
You are a generator in a controlled experiment. Do NOT use any tools at all (no file reads, no searches, no commands); answer only from the text in this conversation. Reply with exactly one proposal per turn.

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

Propose a new executable mechanism. After each proposal you will receive only a short ACCEPTED / REJECTED signal.
```
## Later turns
A, B: `Propose another mechanism, causally different from your previous ones.`
C: `{signal}
Propose another mechanism.` where {signal} is the evaluate.py signal line, nothing else.
