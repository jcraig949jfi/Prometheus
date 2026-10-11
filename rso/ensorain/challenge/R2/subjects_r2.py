"""C-016-T042 re-check subjects (Pallas, Q3). Adversarial and semantic TAPE genomes against FREEZE_ENSORAIN v1.1.0.
Read-only against ensorain/ and every frozen file; nothing here is imported by the frozen assay.

R2 seeds: R2_RANGE = 16_360_001 .. 16_369_999, declared here, disjoint from every PREREGISTRATION s6 range
(subjects.our_ranges, incl. the confirmatory 16_330_001..16_340_000), from every WTP-05 registered range
(subjects.REGISTERED) and from the C-016-T040 challenge range (challenge/subjects_c.CH_RANGE). `conflicts()` must
return [] and cases_r2.py refuses to run otherwise. Scored cases use R2_0 + 0..199 (N_R2 = 200 lives); witnesses
R2_0 + 3000..; the draws check R2_0 + 4000... The confirmatory seeds are never used.

Physics the designs rest on (ensorain/wtp5/tape.py, pinned): the perturbed value is theta + sigma * e, antithetic,
NOT clipped (tape.py:320); the update is eta * sum_k z(r_k) e_k / (K sigma) with z the block's rewards standardised
(baseline-subtracted; zero when every episode's reward is equal: tape.py:345-349); the parameter is clipped to
[-1, 1] after the update only; working state is per episode (run_block allocates z (K, S, W): tape.py:171); ACT
reads lane 0 of its input and signs it (tape.py:280-281); every gate has weight 1 (worlds.py:289).
"""
import numpy as np

from ensorain.wtp5.tape import W, genome, node
from ensorain.wtp5.worlds import P0, P1, F2
from rso.ensorain import subjects as S
from rso.ensorain.challenge import subjects_c as C

R2_0 = 16_360_001
R2_RANGE = (R2_0, R2_0 + 9_999)
N_R2 = 200
WITNESS_OFF = 3000
DRAWS_OFF = 4000


def conflicts():
    """Every declared range (ours, WTP-05's, the T040 challenge) that overlaps the R2 range."""
    rs = S.REGISTERED + S.our_ranges() + [C.CH_RANGE]
    return [r for r in rs if R2_RANGE[0] <= r[1] and r[0] <= R2_RANGE[1]]


def _c(x):
    return np.full(W, float(x))


def walker(theta0=0.5, eta=0.024, sigma=0.01):
    """WK (BROKEN, inference; aimed at the repaired K1). Type-1 action s * theta with theta plastic and
    |theta| >> sigma, so the perturbation (sigma e, |e| < 4) never flips the decision and the ES gradient on theta is
    reward-UNCORRELATED noise; type-2 action a constant +1 (chance), so the block's rewards always have spread and the
    standardised gradient is never zero. theta is then a LAW-BLIND random walk with step eta * |grad| / (K sigma),
    |grad| ~ 8 (sum of 64 standardised rewards times unit normals): 0.024 * 8 / (64 * 0.01) = 0.3 per block.
    The frozen arm and the noise arm (eta 1e-9: step 1e-8) are the fixed +s policy: never revised."""
    n = [node("OBS"), node("CH", 0, i=P0), node("CH", 0, i=F2), node("CONST", v=_c(theta0), plastic=True),
         node("MUL", 1, 3), node("CONST", v=_c(1.0)), node("SEL", 2, 4, 5), node("ACT", 6)]
    return genome(n, S=1, eta=eta, sigma=sigma)


def ratchet(theta0=0.5, eta=0.024, sigma=0.01):
    """RT (PROBE, interpretation). The walker with type-2 = q (always correct): the reward spread exists only while
    type-1 is WRONG, so theta is frozen while it is right and walks while it is wrong -- a trial-and-error search that
    halts on success. It never moves without a switch. This is the reference graph (challenge/subjects_c.ref_like)
    at theta0 = 0.5, eta = 0.024, sigma = 0.01."""
    return C.ref_like(theta0, eta, sigma)


def ref_tiny(scale):
    """TN (SEMANTIC, instrument: the noise arm). The reference rescaled by `scale` with its readout amplified by
    1/scale: theta0 = 0.2 scale, sigma = 0.5 scale (theta/sigma = 0.4 as the reference), eta = scale^2 (the update
    eta grad / (K sigma) rescales exactly). Decision for decision it is the reference on the same draws, with two
    differences: the PLASTIC_BOUND clip at 1 is never reached (its parameter can run away), and ETA_NOISE = 1e-9 is
    ABSOLUTE: at scale 1e-5 its own eta is 1e-10 <= 1e-9, so assay.noise_matched leaves it unchanged and the noise
    arm IS the full arm (K1n ties on every seed); at scale 1e-4 (eta 1e-8) the noise arm learns at 1/10 of its rate."""
    A = 1.0 / scale
    n = [node("OBS"), node("CH", 0, i=P0), node("CH", 0, i=P1), node("CH", 0, i=F2),
         node("CONST", v=_c(0.2 * scale), plastic=True), node("MUL", 1, 4), node("CONST", v=_c(A)), node("MUL", 5, 6),
         node("SEL", 3, 7, 2), node("ACT", 8)]
    return genome(n, S=1, eta=scale ** 2, sigma=0.5 * scale)


def searched_dead():
    """FS (BROKEN, interpretation: family S from structure). memoryless_plus (+s through a non-plastic path) plus an
    UNCONNECTED plastic CONST and eta, sigma > 0: assay.family_s reads a non-empty declared key set and admits it to
    family S although nothing plastic reaches ACT."""
    g = S.memoryless(+1)
    g["nodes"].append(node("CONST", v=_c(0.0), plastic=True))
    g["eta"], g["sigma"] = 1.0, 0.5
    return g


SCORED = {"reference": S.reference, "jitter": C.jitter, "innate_max": C.innate_max, "learns_pre": C.learns_pre,
          "innate_zero": lambda: C.ref_like(0.0, 1.0, 0.5), "walker": walker, "ratchet": ratchet,
          "ref_tiny5": lambda: ref_tiny(1e-5), "ref_tiny4": lambda: ref_tiny(1e-4)}
