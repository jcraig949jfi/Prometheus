"""Experiment registry for the NPE-48h window. Each experiment is declared HERE (question, arms, seeds, epochs,
classification rule) and committed BEFORE it runs; results land in runs/<EXP>/.

    python -B exp.py <EXP> [workers]
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fh  # noqa: E402

EXPS = {}


def declare(name, **kw):
    EXPS[name] = kw


# --------------------------------------------------------------------------- 1. X-LOSS-AUTOPSY + X-GATE-HARM
# One batch serves two declared nodes (shared runs).
# X-LOSS-AUTOPSY (EXPLORE, parent X-TASK-GATE-V2): what causal event destroys the transmitted task function while copying
#   stays intact? Read from the exact per-interaction ledger: loss classes (LOST_INPLACE / LOST_OVERWRITE /
#   LOST_COPY_ERR / LOST_COPY_MUT), transmission fidelity P(child comp | comp donor) for P-11 and LABEL births and for the
#   tape copy before the world's mutation, per-interaction and per-epoch hazards, loss byte positions vs the CT_UA map
#   (copier 0-6, task routine 7-49, padding 50-63), exposure of competent vs non-competent halves.
#   TG_REPLAY re-runs the six XTG-v2 production seeds (EQ-1: identical dynamics) for 400 epochs with the ledger.
# X-GATE-HARM (EXPLORE, parent X-TASK-GATE-V2): is the symmetric TG gate beneficial, neutral or harmful to competence?
#   Same CT_UA plant + backgrounds (paired seeds) under TG, SHUF (rate-matched, competence-blind), CONST p=0.15 (floor,
#   competence-blind), CONST p=1.0 (everyone interacts). Endpoint: competence persistence among ESTABLISHED runs
#   (depth >= 20): last epoch with CS > 0, CS AUC over the run, CS_peak; mechanism: per-interaction loss hazard of
#   competent halves vs exposure (interactions per competent half-epoch).
#   Classification (declared): HARMFUL if median last-epoch-CS>0 (established runs) of TG is < that of SHUF AND < CONST015
#   with TG's per-competent-half-epoch exposure higher; BENEFICIAL if TG's is > both; NEUTRAL otherwise.
#   All arms are expected to lose competence; the question is speed and why.
SEEDS_A = [44_000_000 + s for s in range(12)]
REPLAY = [43_000_000 + s for s in range(6)]
declare("X-LOSS-GATE",
        jobs=[("TG_REPLAY", s, dict(epochs=400)) for s in REPLAY]
        + [(arm, s, dict(epochs=1000, **cfg)) for s in SEEDS_A for arm, cfg in
           (("TG", {}), ("SHUF", dict(gate="SHUF")), ("C015", dict(gate="CONST", p_const=0.15)),
            ("C100", dict(gate="CONST", p_const=1.0)))])


# --------------------------------------------------------------------------- 2. X-DIR-QUAL
# X-DIR-QUAL (EXPLORE, parents X-GATE-HARM, X-LOSS-AUTOPSY): does selection on COPY DIRECTION (competence decides who runs
#   first = who copies onto whom) maintain a transmitted task function, at a FIXED, competence-blind interaction rate?
#   Single coordinate: order = DIR (higher-u organism on side 0, q = 1) vs RANDOM, at CONST p in {0.15, 1.0}; CT_UA plant.
#   Negatives under DIR at p = 0.15: CT_U (reads, does not use; u = 0 -> no ordering advantage) and COPY_ONLY.
#   p = 0.15 arms run 2000 epochs, p = 1.0 arms 300 epochs: both ~300 interactions per organism (X-LOSS-GATE showed
#   p = 1.0 costs ~10x per epoch). Seeds 44_100_000 + s (paired across arms within a plant).
#   Endpoint (persistence, not peak): among established runs, final CS >= 0.10 (MAINTAINED), and last epoch with CS > 0.
#   Classification (declared): SIGNAL if DIR maintains (final CS >= 0.10) in >= 50% of established CT_UA runs at some p
#   while its RANDOM partner at that p maintains in <= 1 run AND both negatives have final CS = 0 in all runs;
#   WEAK_SIGNAL if DIR's median last-CS>0 epoch exceeds RANDOM's by >= 2x at some p without maintenance;
#   CLEAN_NULL otherwise. INVALID if a negative arm ends with CS >= 0.10 in any run.
SEEDS_D = [44_100_000 + s for s in range(12)]
declare("X-DIR-QUAL",
        jobs=[(arm, s, dict(gate="CONST", p_const=p, order=o, epochs=ep)) for s in SEEDS_D
              for arm, p, o, ep in (("DIR015", 0.15, "DIR", 2000), ("RND015", 0.15, "RANDOM", 2000),
                                    ("DIR100", 1.0, "DIR", 300), ("RND100", 1.0, "RANDOM", 300))]
        + [(arm, s, dict(gate="CONST", p_const=0.15, order="DIR", plant=pl)) for s in SEEDS_D[:6]
           for arm, pl in (("NEG_CTU_DIR015", "CT_U"), ("NEG_COPY_DIR015", "COPY_ONLY"))])


CT_W = bytes.fromhex("ED327DEE405FE5DB0047DB00A847DB00FE00280678C625D3007678D3007679A4B8C83F4C602745135FECC26DAE628982C868A00D"
                     "767F86F5E75EB8C61DE6C7F9")      # W2-10 CT_W: copier + tasks.witness(FORCED_READ ADD37)


# --------------------------------------------------------------------------- 3. after X-DIR-QUAL
def ct_ua_add(v):
    """CT_UA with its ADD-37 operand (byte 31) replaced: a copier whose task routine is one constant away from use."""
    g = bytearray(fh.PLANTS["CT_UA"])
    assert g[31] == 0x25
    g[31] = v
    return bytes(g)


# C-DIR-MAINTAIN (CONFIRM, parent X-DIR-QUAL): FRESH seeds 44_200_000 + s, frozen protocol (this block at its commit).
#   Arms: DIR015 (CONST 0.15, order DIR, q 1) and RND015 (CONST 0.15, RANDOM), CT_UA plant, 12 seeds each, 2000 epochs;
#   negatives under DIR015: CT_U and COPY_ONLY, 6 seeds each.
#   Rule: CONFIRMED iff (established DIR015 runs with final CS >= 0.10) >= 0.75 x established DIR015 runs AND
#   (established RND015 runs with final CS >= 0.10) <= 1 AND no negative run has final CS >= 0.10. Otherwise NOT_CONFIRMED.
SEEDS_C = [44_200_000 + s for s in range(12)]
declare("C-DIR-MAINTAIN",
        jobs=[(arm, s, dict(gate="CONST", p_const=0.15, order=o)) for s in SEEDS_C
              for arm, o in (("DIR015", "DIR"), ("RND015", "RANDOM"))]
        + [(arm, s, dict(gate="CONST", p_const=0.15, order="DIR", plant=pl)) for s in SEEDS_C[:6]
           for arm, pl in (("NEG_CTU_DIR015", "CT_U"), ("NEG_COPY_DIR015", "COPY_ONLY"))])

# X-DIR-SURFACE (EXPLORE, parent X-DIR-QUAL): where is the maintenance boundary? Directional strength q (probability the
#   higher-u organism is put first) x total mutation k (mut_scale = copy_scale = k), CONST 0.15, 2000 epochs, CT_UA.
#   q in {0.1, 0.25, 0.5, 1.0} x k in {1, 4, 16} (the q = 1, k = 1 cell is X-DIR-QUAL's DIR015). 6 seeds 44_300_000 + s.
#   Readout per cell: established runs maintained (final CS >= 0.10), median final CS, median last-CS>0 epoch.
#   Prediction from F1 (declared): maintenance iff the directional win advantage per mixed interaction exceeds the
#   competence leak per interaction (~0.035 x k); expected boundary between q 0.1 and 0.25 at k 1, moving up with k.
#   Classification: SIGNAL if a monotone boundary exists (maintenance falls with k and rises with q in every row/column
#   with at least one maintained and one lost cell); CLEAN_NULL if every cell maintains or every cell loses.
SEEDS_S = [44_300_000 + s for s in range(6)]
declare("X-DIR-SURFACE",
        jobs=[("Q%03d_K%02d" % (int(q * 100), k), s,
               dict(gate="CONST", p_const=0.15, order="DIR", q_dir=q, mut_scale=k, copy_scale=k))
              for s in SEEDS_S for q in (0.1, 0.25, 0.5, 1.0) for k in (1, 4, 16) if not (q == 1.0 and k == 1)])

# X-REDISCOVER (EXPLORE, parent X-DIR-QUAL): can directional selection RE-DISCOVER lost function? Plant a copier whose
#   routine is d operand-steps from use (CT_UA with byte 31 = 0x24 d1, 0x00 d2, 0x40 d3, 0xD9 d4; all u = 0), under DIR
#   (q 1) vs RANDOM order, CONST 0.15, 2000 epochs, 6 seeds 44_400_000 + s. Readout: runs with any competence root
#   (MUT / *_CREATED), epoch of the first, runs with final CS >= 0.10, and whether the final competent genome equals
#   CT_UA (re-discovery of the same byte) or another solution.
#   Classification: SIGNAL if DIR reaches final CS >= 0.10 in >= 3/6 at some d >= 2 while RANDOM does in <= 1;
#   WEAK_SIGNAL if only d = 1 is rediscovered under DIR; CLEAN_NULL if no DIR run at d >= 1 ends competent.
SEEDS_R = [44_400_000 + s for s in range(6)]
declare("X-REDISCOVER",
        jobs=[("RD%d_%s" % (d, o), s, dict(gate="CONST", p_const=0.15, order=o, plant=ct_ua_add(v)))
              for s in SEEDS_R for d, v in ((1, 0x24), (2, 0x00), (3, 0x40), (4, 0xD9)) for o in ("DIR", "RANDOM")])

# X-RANDOM-DIR (EXPLORE, parent X-DIR-QUAL): from RANDOM populations (no plant), does DIR yield a copier regime and any
#   competence? DIR vs RANDOM at CONST 0.15, 12 seeds 44_500_000 + s, 2000 epochs. Readout: depth >= 20 runs, any
#   competence root, final CS. Expected (declared): copier regime rare, competence absent in both (the task needs a
#   ~30-byte conditional; no gradient under the use ruler). A null here bounds endogenous re-discovery from scratch.
SEEDS_X = [44_500_000 + s for s in range(12)]
declare("X-RANDOM-DIR",
        jobs=[(arm, s, dict(gate="CONST", p_const=0.15, order=o, plant=None)) for s in SEEDS_X
              for arm, o in (("RAND_DIR", "DIR"), ("RAND_RND", "RANDOM"))])


# X-DIR-LONG (EXPLORE, parent X-DIR-QUAL): over a longer horizon (8000 epochs at CONST 0.15 ~ 1200 interactions per
#   organism) under DIR, does the maintained architecture change beyond drift? X-DIR-QUAL mining (F4) found neutral
#   rewiring of the vestigial read-order detector (bytes 16-19) and re-use of the dead ABR branch's OUT (byte 29 offset).
#   Question: does task robustness rise ("flattest" selection), is the vestigial detector lost, does routine
#   conservation fall, and does anything fuse task and copier? k in {1, 4} (mut_scale = copy_scale = k), 6 seeds each,
#   44_600_000 + s. Readout from dom_series (dominant competent genome every 50 epochs): single-byte robustness over
#   time (arch.robustness), share of genomes whose bytes 16-19 differ from CT_UA, routine length to first HALT on the
#   regime-1 path, identity by region. Classification: SIGNAL if dominant-genome routine robustness at the end exceeds
#   CT_UA's (0.382) by >= 0.10 in >= 4/6 maintained runs at some k; WEAK_SIGNAL if by >= 0.05; CLEAN_NULL otherwise.
SEEDS_L = [44_600_000 + s for s in range(6)]
declare("X-DIR-LONG",
        jobs=[("LONG_K%02d" % k, s, dict(gate="CONST", p_const=0.15, order="DIR", mut_scale=k, copy_scale=k, epochs=8000))
              for s in SEEDS_L for k in (1, 4)])


# X-VETO (EXPLORE, orthogonal falsifier, parent C-DIR-MAINTAIN): is COPY PRIORITY specifically required, or does any
#   competence-coupled asymmetry of heredity maintain function? VETO = random order, but a pair whose first mover is
#   less competent than the second is skipped (defensive: competence protects from being overwritten; it never grants
#   the first move). CONST 0.15, 2000 epochs, CT_UA, 12 seeds 44_700_000 + s; arms VETO015, RND015, DIR015 (reference).
#   Negatives are omitted by construction (u = 0 for CT_U / COPY_ONLY lineages -> VETO never fires; identical to RND).
#   Classification: SIGNAL (any asymmetry suffices) if VETO maintains (final CS >= 0.10) in >= 75% of established runs
#   and RND in <= 1; WEAK_SIGNAL if VETO's median last-CS>0 epoch >= 2x RND's without maintenance; CLEAN_NULL otherwise
#   (copy priority specifically required).
SEEDS_V = [44_700_000 + s for s in range(12)]
declare("X-VETO",
        jobs=[(arm, s, dict(gate="CONST", p_const=0.15, order=o)) for s in SEEDS_V
              for arm, o in (("VETO015", "VETO"), ("RND015", "RANDOM"), ("DIR015", "DIR"))])


# X-ARCH-COMPETE (EXPLORE, parent C-DIR-MAINTAIN, F4): does selection on function also select the more ROBUST
#   implementation? Two fully competent architectures planted together under DIR: CT_UA (routine 32 bytes, single-byte
#   robustness 0.69) and CT_W (routine 24 bytes, robustness 0.75, copy keeps task 1.0). Both have u = 1, so DIR ties
#   them (random order between them); only their mutational leak differs. Plant slot is alternated by seed parity
#   (even: CT_UA at i = 0, CT_W at i = 1; odd: swapped). CONST 0.15, DIR, 2000 epochs, k in {1, 4}, 12 seeds
#   44_800_000 + s. Readout: final competent genomes assigned to the nearer construct (Hamming); CT_W-family share.
#   Classification: SIGNAL if the CT_W family holds > 0.5 of the final competent organisms in >= 75% of runs with final
#   competence at k = 4 AND in a majority at k = 1; WEAK_SIGNAL if only at k = 4; CLEAN_NULL if neither (no selection
#   among architectures beyond drift).
SEEDS_AC = [44_800_000 + s for s in range(12)]
declare("X-ARCH-COMPETE",
        jobs=[("AC_K%02d" % k, s, dict(gate="CONST", p_const=0.15, order="DIR", mut_scale=k, copy_scale=k,
                                       plant=("CT_UA" if s % 2 == 0 else CT_W),
                                       extra_plants=[CT_W if s % 2 == 0 else "CT_UA"]))
              for s in SEEDS_AC for k in (1, 4)])


# X-ONTAPE (EXPLORE, parent C-DIR-MAINTAIN): ENDOGENOUS ruler. Can function be maintained when copy priority is earned
#   from the organism's OWN on-tape answers (task episode fed to IN during the pair-tape execution in which copying
#   happens; first OUT scored; EWMA alpha 0.3, reset on conversion) instead of an offline scorer? No world-side
#   ruler is consulted. Known answers (OT-1): on-tape correctness CT_UA 0.99 (fresh copy 0.95), CT_U 0.54, COPY_ONLY 0.
#   Arms: ONTAPE (q 1) vs ONTAPE_RND (same inputs, random order), CT_UA, CONST 0.15, 2000 epochs, 12 seeds
#   44_900_000 + s; negatives under ONTAPE: CT_U and COPY_ONLY, 6 seeds. Readout: final CS by the frozen USE ruler
#   (offline, readout only), on-tape correctness counts, last-CS>0 epoch.
#   Classification: SIGNAL if ONTAPE maintains use-competence (final CS >= 0.10) in >= 75% of established runs and
#   ONTAPE_RND in <= 1; WEAK_SIGNAL if ONTAPE's median last-CS>0 >= 2x ONTAPE_RND's without maintenance; CLEAN_NULL
#   otherwise. INVALID if a negative arm ends with use-CS >= 0.10. Declared caveat: the on-tape ruler gives partial
#   credit (CT_U-like regime-blind answers score ~0.5), so it selects for answering, of which USE is the best form.
SEEDS_O = [44_900_000 + s for s in range(12)]
declare("X-ONTAPE",
        jobs=[(arm, s, dict(gate="CONST", p_const=0.15, order=o)) for s in SEEDS_O
              for arm, o in (("ONTAPE", "ONTAPE"), ("ONTAPE_RND", "ONTAPE_RND"))]
        + [(arm, s, dict(gate="CONST", p_const=0.15, order="ONTAPE", plant=pl)) for s in SEEDS_O[:6]
           for arm, pl in (("NEG_CTU_ONTAPE", "CT_U"), ("NEG_COPY_ONTAPE", "COPY_ONLY"))])


# X-DIR-7AE3 (EXPLORE, scope/generalization, parent C-DIR-MAINTAIN): does the direction-vs-rate result hold in another
#   world? The 7ae3 cell: same task (FORCED_READ ADD37), same ops (SELF, BLOCK copy, dense VM, ATOMIC runner), but
#   Z8_64 representation (unslotted; OPERAND mutation hits real operand bytes only, so opcodes are never mutated by the
#   world operator; copy errors still hit any byte) and WELL_MIXED structure. STATIC env, CONST 0.15, 2000 epochs,
#   CT_UA; DIR015 vs RND015, 12 seeds 45_000_000 + s; negatives under DIR: CT_U, COPY_ONLY, 6 seeds.
#   Classification: SIGNAL (generalizes) by X-DIR-QUAL's rule; CLEAN_NULL if DIR does not maintain; INVALID if
#   CT_UA does not establish in >= 4/12 under either order (instrument unreachable in this cell) or a negative ends
#   with CS >= 0.10.
SEEDS_7 = [45_000_000 + s for s in range(12)]
declare("X-DIR-7AE3",
        jobs=[(arm, s, dict(cell="7ae3", gate="CONST", p_const=0.15, order=o)) for s in SEEDS_7
              for arm, o in (("DIR015_7AE3", "DIR"), ("RND015_7AE3", "RANDOM"))]
        + [(arm, s, dict(cell="7ae3", gate="CONST", p_const=0.15, order="DIR", plant=pl)) for s in SEEDS_7[:6]
           for arm, pl in (("NEG_CTU_7AE3", "CT_U"), ("NEG_COPY_7AE3", "COPY_ONLY"))])


# X-REDISCOVER-SUPPLY (EXPLORE, parent X-REDISCOVER, weak-signal child): is re-discovery SUPPLY-limited? Same plants
#   (d = 1: 0x24; d = 2: 0x00), DIR, but CONST p = 1.0 for 2000 epochs (~2000 interactions per organism, ~7x the
#   mutational supply of X-REDISCOVER at the same per-interaction physics). 6 seeds 45_100_000 + s each.
#   Declared prediction (supply model): d = 1 creation in most runs and sweeps under DIR; d = 2 creation in roughly
#   half the runs (estimate ~0.6 two-step events per run at 7x supply).
#   Classification: SIGNAL (supply-limited, two-step reachable) if d = 2 ends competent in >= 2/6; WEAK_SIGNAL if d = 2
#   shows any creation root but no maintained run; CLEAN_NULL if no d = 2 creation (two-step blocked beyond supply).
SEEDS_RS = [45_100_000 + s for s in range(6)]
declare("X-REDISCOVER-SUPPLY",
        jobs=[("RS%d_DIR100" % d, s, dict(gate="CONST", p_const=1.0, order="DIR", plant=ct_ua_add(v)))
              for s in SEEDS_RS for d, v in ((1, 0x24), (2, 0x00))])


# C-ONTAPE-MAINTAIN (CONFIRM, parent X-ONTAPE): FRESH seeds 45_200_000 + s, protocol frozen at this block's commit.
#   ONTAPE vs ONTAPE_RND (CONST 0.15, 2000 epochs, CT_UA), 12 seeds each; negatives under ONTAPE: CT_U, COPY_ONLY,
#   6 seeds each. tape_readout on. Primary ruler: FUNCTION = TCS (share of live organisms with homotypic on-tape
#   cue-flip use >= 0.75), because selection in this world acts on in-context behavior (F8); the offline use CS is
#   reported beside it and decides nothing.
#   Rule: CONFIRMED iff (established ONTAPE runs with final TCS >= 0.10) >= 0.75 x established AND (established
#   ONTAPE_RND runs with final TCS >= 0.10) <= 1 AND no negative run has final TCS >= 0.10 or final CS >= 0.10.
SEEDS_CO = [45_200_000 + s for s in range(12)]
declare("C-ONTAPE-MAINTAIN",
        jobs=[(arm, s, dict(gate="CONST", p_const=0.15, order=o, tape_readout=True)) for s in SEEDS_CO
              for arm, o in (("ONTAPE", "ONTAPE"), ("ONTAPE_RND", "ONTAPE_RND"))]
        + [(arm, s, dict(gate="CONST", p_const=0.15, order="ONTAPE", plant=pl, tape_readout=True)) for s in SEEDS_CO[:6]
           for arm, pl in (("NEG_CTU_ONTAPE", "CT_U"), ("NEG_COPY_ONTAPE", "COPY_ONLY"))])

# X-ONTAPE-LONG (EXPLORE, parent X-ONTAPE): over 6000 epochs (~900 interactions per organism) under ONTAPE, does
#   function migrate from genome-contained (offline AND on-tape competent) to pair-distributed (tape-only) forms?
#   6 seeds 45_300_000 + s, CONST 0.15, CT_UA, tape_readout on (classes every 50 epochs).
#   Readout: tape_only share trajectory; runs where tape_only > 0.5 of live organisms at any snapshot; final TCS;
#   mechanisms of tape-only genomes (jump targets into the partner half).
#   Classification: SIGNAL if tape-only forms exceed 0.5 of the population in >= 2/6 runs with TCS maintained (>= 0.10);
#   WEAK_SIGNAL if tape-only forms appear (> 0.05 at some snapshot) in >= 3/6; CLEAN_NULL otherwise.
SEEDS_OL = [45_300_000 + s for s in range(6)]
declare("X-ONTAPE-LONG",
        jobs=[("ONTAPE_LONG", s, dict(gate="CONST", p_const=0.15, order="ONTAPE", tape_readout=True, epochs=6000))
              for s in SEEDS_OL])


if __name__ == "__main__":
    name = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    e = EXPS[name]
    fh.pool_run(name, e["jobs"], HERE / "runs" / name, w)
