"""C-016-T040 challenge subjects (Pallas, Q3). Adversarial and semantic TAPE genomes built on the frozen reference's
node layout (rso/ensorain/subjects.py:53 -> ensorain/wtp5/planted.py:113-117). Read-only against ensorain/ and against
every frozen file: nothing here is imported by the frozen assay, and nothing here edits it.

Challenge seeds: CH_RANGE = 16_350_001 .. 16_359_999, declared here, disjoint from every range in PREREGISTRATION.md s6
(subjects.our_ranges) and from every WTP-05 registered range (subjects.REGISTERED). `conflicts()` must return [] and
cases.py refuses to run otherwise. Scored cases use CH0 + 0..199 (N_DEV = 200 lives, a development size: the frozen
development qualification used 400). Witnesses use CH0 + 5000.. . The confirmatory seeds 16_330_001..400 are never used.
"""
import numpy as np

from ensorain.wtp5.tape import W, genome, node
from ensorain.wtp5.worlds import P0, P1, F2
from rso.ensorain import subjects as S

CH0 = 16_350_001
CH_RANGE = (CH0, CH0 + 9_999)
N_DEV = 200
WITNESS_OFF = 5000


def conflicts():
    """Every declared range (ours and WTP-05's) that overlaps the challenge range."""
    return [r for r in S.REGISTERED + S.our_ranges() if CH_RANGE[0] <= r[1] and r[0] <= CH_RANGE[1]]


def _c(x):
    return np.full(W, float(x))


def ref_like(theta0, eta, sigma):
    """The reference graph (planted.py:115-116: act = theta * s on type 1, q on type 2) with the plastic CONST
    initialised at theta0 and the genome's eta, sigma set as given."""
    n = [node("OBS"), node("CH", 0, i=P0), node("CH", 0, i=P1), node("CH", 0, i=F2),
         node("CONST", v=_c(theta0), plastic=True)]
    n += [node("MUL", 1, 4), node("SEL", 3, 5, 2), node("ACT", 6)]
    return genome(n, S=1, eta=eta, sigma=sigma)


def jitter():
    """B1 (BROKEN, inference): a fixed PRE-switch prior (+0.1) plus perturbation noise and no learning. eta = 1e-9 keeps
    the perturbation on (tape.py:305 needs eta > 0) while the update (tape.py:349) moves theta by ~1e-8 per block. On a
    type-1 gate it acts +s with P(0.1 + 0.5 e > 0) = .58, before and after the switch alike. Its frozen arm is the
    deterministic +s policy (late accuracy 0)."""
    return ref_like(0.1, 1e-9, 0.5)


def innate_max():
    """B2 (SEMANTIC, interpretation): the reference with theta0 = +1.0 = PLASTIC_BOUND. Nothing can be learned before
    the switch (the pre-switch gradient points up into the clip); the whole pre-switch competence is innate."""
    return ref_like(1.0, 1.0, 0.5)


def learns_pre():
    """S5 (SOUND / semantic): the reference with theta0 = -0.1. It starts on the WRONG side of the pre-switch law and
    must learn the law in-life (block 0 acts +s only 42% of the time) before it can be revised at the switch. The honest
    exemplar of 'revise a lifetime-learned parameter'. Its frozen arm is the -s policy (pre accuracy 0)."""
    return ref_like(-0.1, 1.0, 0.5)


def nan_plastic():
    """P1 (PROBE, instrument): a plastic CONST holding NaN. assay.memory_check bounds a plastic value with
    `np.any(np.abs(ya) > PLASTIC_BOUND)`, which is False for NaN."""
    return ref_like(float("nan"), 1.0, 0.5)


def clock_hybrid(c=1.0, d=-0.25, eta=0.5, sigma=0.5):
    """P2 (PROBE, instrument + interpretation): the best law-blind TIMER I could design inside TAPE's physics, and the
    reason it is not one. One plastic parameter phi (init -1.0) is DRIVEN by the never-switching type-2 reward
    (act = s * sign(phi + c): the ES gradient pushes phi up while type-2 flips happen) and READ by the type-1 action
    (act = s * sign(d - phi): +s while phi < d, -s after). If phi crossed d at a fixed time the genome would pass G_PRE
    and the late window without ever reading the type-1 law. CHALLENGE_SET.md P2 argues it cannot: the type-1 readout
    receives a law-dependent gradient of the same scale as the drive, so phi stalls at (d - c) / 2 before the switch
    and crosses only after it. The no-switch probe (cases.py P2) tests exactly that."""
    n = [node("OBS"), node("CH", 0, i=P0), node("CH", 0, i=P1), node("CH", 0, i=F2),
         node("CONST", v=_c(-1.0), plastic=True),                                     # 4 phi
         node("CONST", v=_c(c)), node("ADD", 4, 5), node("MUL", 2, 6),                 # 5-7 type-2: s2 * (phi + c)
         node("CONST", v=_c(d)), node("CONST", v=_c(-1.0)), node("MUL", 4, 9), node("ADD", 8, 10),   # 8-11 d - phi
         node("MUL", 1, 11),                                                           # 12 type-1: s1 * (d - phi)
         node("SEL", 3, 12, 7), node("ACT", 13)]
    return genome(n, S=1, eta=eta, sigma=sigma)


SCORED = {"reference": S.reference, "jitter": jitter, "innate_max": innate_max, "learns_pre": learns_pre,
          "clock_hybrid": clock_hybrid}
