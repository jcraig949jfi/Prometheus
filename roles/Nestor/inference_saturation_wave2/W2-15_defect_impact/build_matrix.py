"""W2-15: DEFECT x VERDICT impact matrix (read-only reasoning record).

python -B build_matrix.py -> matrix.json, matrix.md

Every NPE verdict (EXPERIMENT_GRAPH.jsonl closed rows + FINDINGS.md + dossiers A-E + frontier) is a row.
Columns are the defects. A cell is one of:
  NA           the defect's mechanism is not present in this experiment's cell / design / readout
  NONE         the mechanism is present but cannot change the verdict or its wording
  WORDING      the verdict stands; a sentence about it must change
  BIAS+ / BIAS- / BIAS?   the verdict's effect estimate is pushed up (+, toward the claim), down (-, toward
               the null) or in an undetermined direction; the label survives under the bias as far as we can show
  INVALIDATES  the verdict (or the named reading of it) cannot be supported while the defect stands
Cells not listed for a row are NA. Applicability rules (written before judging; see APPLIES):
  D1   cache keyed on genome only, crosses niches: cell has >1 niche whose task spec differs (COEVO_ENV x NICHES_*,
       or RESERVOIR's niche-0 modifier) AND the readout or the dynamics use comp/held.
       In QD/NOVELTY/EXEC_TIME pair-tape cells comp has NO dynamical role (D3: the pressure is inert; qd_map is read
       only by the unreachable reaper; COEVO env scoring draws a fixed number of RNG values), so D1 there reaches
       only comp/held readouts.
  H1C  the same cache in a single-niche cell: each genome scored once on one shared 6-episode draw (dossier B A1).
  D2   C9 H3 A == B (same cell_id, same seed): H3 and its descendants.
  D3   7 of 12 pressures byte-identical on the pair tape; TAPE_COST/PREDATION kill without replacement:
       claims that attribute anything to a pressure, to death, or to "selection" other than overwriting, on PAIR_TAPE.
  D4   Z8_SLOTTED ignores the operator (87% of OPERAND edits hit opcodes; ~7-8x effective supply vs Z8_64):
       any 7ae3-vs-ffa6 / SLOTTED-vs-other contrast, or a claim whose scope is a SLOTTED cell.
  D5   anticheat guards cannot fire: any "0 voided / anticheat clean" statement.
  D8   mutual acceptance -> false depth 2: depth endpoints, only where padding exists (genome shorter than its half).
  D9   relabel keeps stale age/comp/held/energy/slot_owner: readouts of newborn bookkeeping, PREDATION, gates on comp.
  VR   newborns keep the victim's registers (BACKLOG T-DC-2; D9 regs_kept=True): register-state claims in CARRIED worlds.
  AC   ATOMIC is a composite (keeps predecessor-accepted overwrites, causal or not; discards self-writes; N9: ~3/4 of
       its establishment gain is the fidelity clause): claims that read ATOMIC as "erosion removed" or as organismal.
  D24  RNG stream shifts (implant arms unpaired; any behavioural difference shifts later draws): paired reasoning.
  D10  C-A3 event clauses redundant, endpoint transient: C-A3 and descendants (X-MAT, XTG eligibility).
  D11  FAIR donor-profile truncation: X-A3-FAIR.
  D12  run_dd.screen index-keyed and re-drawn per checkpoint: experiments whose L2 label comes from run_dd.screen.
  XTG  D6/D7/D13/D14/D15 (X-TASK-GATE-only defects).
  W25  W2-5 sweep class at a cited line of this experiment's runner (RCF/LAC/SCP/SIM/PAD/RNG ...).
  W29  W2-9 statistical finding (FRAGILE / ARTIFACT-RISK / UNINFORMATIVE / donor clustering ...).
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

DEFECTS = ["D1", "H1C", "D2", "D3", "D4", "D5", "D8", "D9", "VR", "AC", "D24", "D10", "D11", "D12", "XTG", "W25", "W29"]

APPLIES = {
    "D1": "multi-niche cell with niche-dependent spec AND comp/held used (readout or dynamics)",
    "H1C": "single-niche cell, comp/held readout; one cached 6-episode draw per genome",
    "D2": "C9 H3 and descendants",
    "D3": "PAIR_TAPE claim attributing an effect to pressure, death, or non-overwrite selection",
    "D4": "7ae3-vs-ffa6 or SLOTTED-vs-other contrast, or SLOTTED-scoped claim",
    "D5": "claims of 0 voided / anticheat clean",
    "D8": "depth endpoint with padding possible",
    "D9": "newborn bookkeeping readouts, PREDATION, comp-gated pairing",
    "VR": "register-state claims in a CARRIED pair-tape world",
    "AC": "claims reading ATOMIC as erosion removal / organismal fidelity",
    "D24": "paired / same-background reasoning across arms",
    "D10": "C-A3 and descendants",
    "D11": "X-A3-FAIR",
    "D12": "L2 from run_dd.screen",
    "XTG": "X-TASK-GATE",
    "W25": "W2-5 sweep hit at this runner",
    "W29": "W2-9 statistical finding",
}

# (id, family, recorded verdict, cell/design note, {defect: (impact, justification)}, relabel or None, findings lines)
R = []


def row(eid, fam, verdict, cell, cells, relabel=None, lines=None):
    R.append({"id": eid, "family": fam, "verdict": verdict, "cell": cell, "cells": cells,
              "relabel": relabel, "findings_lines": lines or []})


# ---------------------------------------------------------------- 72-hour campaign and forensics
row("Z80A-72H / A-1", "72h", "1,031 ADMISSIBLE (NARROWED x3)", "observatory, all grammar cells; flags all PAIR_EXECUTION",
    {"D5": ("WORDING", "'23,471 runs, 0 voided' carries no information: RUNNER_BIRTH and IMMORTAL are unsatisfiable, so voided "
                       "is always False; the splice (Z80A-D05) passed anticheat as an invisible runner copy."),
     "D3": ("WORDING", "all 1,031 are pair-tape; any per-pressure breakdown of flags is realization noise for 7 aliased levels, and "
                       "TAPE_COST/PREDATION cells shrink without replacement (fewer organisms -> fewer flags)."),
     "D8": ("BIAS+", "72h genomes vary in length (indels) so padding exists; mutual acceptance can manufacture exactly depth 2. "
                     "Affects 'depth >= 2 in 120' (predecessor ancestry) only upward, i.e. in the direction of the existing narrowing."),
     "W25": ("NONE", "SCH/SIM already recorded (dossier C 5.1, E-11); nothing new.")},
    None, [15, "19-37"])
row("A-2 matched pairs", "72h", "HOLDS (pressure row EXTERNAL-scoped)", "metric d_held_max (packet.py:95), predecessor world with the same genome-keyed cache",
    {"D1": ("BIAS?", "held_max in COEVO_ENV x NICHES_* and RESERVOIR cells is read from a cache keyed on genome only, so a genome "
                     "carries its first niche's score; within a pair both arms share the contamination except when the axis is "
                     "environment/structure. Direction undetermined; the 4 printed rows are not environment/structure axes."),
     "H1C": ("BIAS?", "held_max is a population MAXIMUM over single cached held-out draws. EXPLICIT_FITNESS converges the population "
                      "(few distinct genomes, few draws) while NONE keeps many distinct genomes (many draws, higher max by chance): "
                      "this attenuates EXPLICIT>NONE; selection on cached comp inflates it only via comp/held correlation. Net sign unknown."),
     "D3": ("WORDING", "the scope note's reason should cite D3: on PAIR_TAPE 7 of 12 pressure levels are byte-identical, so pressure "
                       "contrasts there are realization noise, not weak effects.")},
    "HOLDS as recorded deltas of a cached single-draw metric", [43, 58, "60-64"])
row("A-4 / E-4 (H4 source)", "72h", "WITHDRAWN", "COEVO_ENV cell, frozen population",
    {"D1": ("NONE", "cross-niche cache only reinforces the withdrawal (held moved only with COEVO env redraws).")})
row("S1A funnels / S2-P11", "forensics", "HOLDS / INSTRUMENT", "FREE / OVERWRITE replays; P-11 spec", {})
row("S1C-P11-REASSAY / E-3", "forensics", "57 survive; max P-11 depth 2 (2 runs)", "72h pair cells, variable genome length",
    {"D8": ("BIAS+", "padding exists in 72h genomes; the 2 depth-2 survivors are exactly what a mutual acceptance manufactures. "
                     "Unverified either way; direction is toward further narrowing."),
     "D5": ("NONE", "")},
    "57 survive; 'max depth 2' unverified against D8", ["198-201"])

# ---------------------------------------------------------------- Cycle 9
row("C9-H1R", "C9", "COST_INTERACTION_ONLY (CONFIRM)", "H1: EXTERNAL, STATIC, WELL_MIXED (1 niche), EXPLICIT_FITNESS, tier S",
    {"D1": ("NA", "single niche, STATIC: no cross-niche spec."),
     "H1C": ("BIAS+", "I equals the ungated-VM mean, a cached single 6-episode draw under selection on that same cached score "
                      "(lucky-draw sweeps); the label hinges on that one mean (>= 0.15 / < 0.30). gated+VM = 0 is immune."),
     "W29": ("WORDING", "degenerate 2x2: FREE arms identical by construction (gate satisfied at entry), M = -I/2 always; "
                        "GATE_EFFECT alone unattainable. Only 'gated+VM = 0/60' discriminates.")},
    "COST_INTERACTION_ONLY -> DEGENERATE DESIGN (label ARTIFACT-RISK); robust fact: gated+VM recorded competence 0/60 (180/180 with transplant)",
    ["269-279"])
row("X-H1-TRANSPLANT", "C9", "SIGNAL", "H1 cell, 4 transforms",
    {"H1C": ("BIAS+", "same cached ungated level in every transform."),
     "W29": ("WORDING", "same degeneracy (FREE arms identical); 'gate+free cue harmless' is true by construction.")},
    None, ["274-276"])
row("X-H1-GRADIENT", "C9", "WEAK_SIGNAL (mechanism: guessers carry ungated competence)", "H1 cell",
    {"H1C": ("INVALIDATES", "the mechanism reading. An answer-before-read genome has expected score 0.5/episode, yet >85% ABR "
                            "populations hold mean training competence ~0.9 (dossier B U10): the recorded 'competence' of guessers is "
                            "luck-of-cache selected by EXPLICIT_FITNESS. 'Guessers carry the gradient' describes cached scores, not "
                            "task competence. The composition fact (no reader evolves) stands.")},
    "WEAK_SIGNAL (composition only); 'competence carried by guessers' -> 'cached scores carried by guessers'", ["276-279"])
row("C9-H2", "C9", "REPLICATION_EVENTS_WITHOUT_PROPAGATION; 7ae3 WEAK_SIGNAL", "16 panel pair cells (pressures QD/METABOLIC/EXEC_TIME/NONE/NOVELTY/COMPETITION)",
    {"D24": ("WORDING", "'random 0/16, in situ 0/16' is one null of 16 runs (already in the D24 errata, line not yet edited)."),
     "D3": ("WORDING", "every panel pressure is an aliased level: specimen cells differ effectively only in representation, "
                       "ops mask / self_location, copy primitive, mutation operator/locality/rate, atlas axis and tier."),
     "D8": ("NONE", "15/16 never reach depth 2; an upward artefact cannot create the null.")},
    None, ["280-282"])
row("C9-H3", "C9", "NOT_DEMONSTRATED", "RESERVOIR (4 niches), PAIR_TAPE, pressures EXEC_TIME_COST / NOVELTY, envs RESOURCE_LIMITED / NONSTATIONARY",
    {"D2": ("INVALIDATES", "A and B are the same simulation in 64/64 bundles (same cell_id and seed); the easy niche exists only in "
                           "scoring; C is unpaired from epoch 0 and is not a transport control."),
     "D1": ("INVALIDATES", "the only A-vs-B differences are scoring: n_cross_events differs in 15/64, crossed_ever 5/64, from "
                           "genome-keyed held crossing RESERVOIR niches."),
     "D3": ("INVALIDATES", "both H3 pressures are aliased on the pair tape, so no channel exists by which easy-niche competence "
                           "could be amplified or transported preferentially; the hypothesis was untestable in these cells."),
     "D9": ("BIAS?", "relabelled newborns carry the victim's comp/held until the next validation.")},
    "NOT_DEMONSTRATED -> INVALID / UNTESTABLE AS DESIGNED (withdraw the E-9 negative)", ["283-284"])
row("C9-H3-RULER", "C9", "INVALID (tournament)", "H3 bundles", {"D2": ("NONE", "already INVALID.")})
row("C9-H3-NULL / X-H3-FLOW", "C9", "CLEAN_NULL: NOT_COMPETENT (niche-0 held 0.000)", "a621: PAIR_TAPE, NOVELTY, NONSTATIONARY, RESERVOIR",
    {"D1": ("BIAS-", "per-niche mean held is read from the genome-keyed cache; a genome first validated in one of the 3 hard niches "
                     "carries that score into niche 0, pulling niche-0 held toward the hard value (toward NOT_COMPETENT)."),
     "D3": ("INVALIDATES", "the localization. NOVELTY is aliased to NONE on the pair tape: nothing selects for competence in any "
                           "niche, so 'the chain fails at its first link' is guaranteed by design, not located by measurement."),
     "D2": ("NONE", "the replay attaches to the frozen arms; A and B being identical is consistent with its own replay note."),
     "D9": ("BIAS?", "stale comp on relabelled newborns.")},
    "CLEAN_NULL -> UNINFORMATIVE (no selection channel; cached cross-niche held); 'transport works ~21%' stands (material tags)", ["58 graph"])
row("X-H3-EASIER", "C9", "CLEAN_NULL -> RETIRE_H3_STRUCTURAL", "a621 with niche 0 = XOR1",
    {"D3": ("WORDING", "retirement stands, but the reason is 'no task-coupled selection exists on the pair tape under NOVELTY', "
                       "not 'random pair-tape populations do not evolve competence at this scale'."),
     "D1": ("BIAS-", "niche-0 held cached cross-niche.")},
    "RETIRE stands; reason re-worded", ["graph row 58"])

# ---------------------------------------------------------------- c9x non-pair (FREE) physics
for eid, v in (("X-NONPAIR-SEARCH", "WEAK_SIGNAL"), ("X-NONPAIR-FIDELITY", "WEAK_SIGNAL"), ("X-SELFLOC-FREE", "CLEAN_NULL"),
               ("X-SELFLOC-SEEDED", "SIGNAL"), ("X-ERROR-THRESHOLD", "CLEAN_NULL"), ("X-ENERGY-INHERIT", "SIGNAL"),
               ("X-LOCAL-ALLOC", "WEAK_SIGNAL"), ("X-SPONTANEOUS", "CLEAN_NULL"), ("X-NEARMISS", "WEAK_SIGNAL"),
               ("X-DENSE-OPS", "INVALID"), ("X-DENSE-OPS-R", "SIGNAL"), ("X-DENSE-ABLATE", "SIGNAL")):
    row(eid, "c9x-FREE", v, "non-pair FREE physics, random grammar cells; readouts births/fidelity/depth", {})
row("C-SELFLOC", "c9x-FREE", "CONFIRMED", "FREE physics, implanted copier", {"W29": ("NONE", "ROBUST (power 0.97).")})
row("C-ENERGY", "c9x-FREE", "CONFIRMED", "FREE physics, energy pressures active (D3 is pair-tape only)",
    {"W29": ("WORDING", "effect ROBUST; mechanism ('cannot afford its copy') not separated from lowest-energy-first reaping of "
                        "zero-energy newborns (dossier B A3).")}, None, ["236-245"])
row("C-DENSE", "c9x-FREE", "CONFIRMED", "FREE permissive world",
    {"W29": ("WORDING", "ROBUST as 'certified replication occurs'; 5/13 cells have exactly 1 event; >= 2 events p = 0.0027 fails "
                        "both frozen bars, so not a heredity claim.")}, "CONFIRMED (replication occurs; not heredity)", ["247-257"])
row("C-ABLATE LOC", "c9x-FREE", "CONFIRMED", "FREE", {"W29": ("NONE", "ROBUST.")})
row("C-ABLATE SEARCH", "c9x-FREE", "CONFIRMED", "FREE",
    {"W29": ("WORDING", "FRAGILE: exactly the 10 up-cells needed; 10/40 single-cell deletions flip it; fails Holm at 0.01; "
                        "'necessary' = a 60% drop, not abolition.")}, "CONFIRMED-FRAGILE", ["258-260"])
row("C-ABLATE ENERGY_FOR_DEPTH", "c9x-FREE", "NOT_CONFIRMED", "FREE",
    {"W29": ("WORDING", "unattainable once FULL D2 = 3 (best possible p = 0.125): an eligibility failure, not evidence.")},
    "NOT_CONFIRMED -> INELIGIBLE", ["260-262"])

# ---------------------------------------------------------------- c9x pair tape (7ae3 cell unless noted)
row("X-H2-7AE3", "c9x-pair", "WEAK_SIGNAL", "7ae3 cell, splice on, BASE", {})
row("X-H2-TERMINATION", "c9x-pair", "WEAK_SIGNAL (12 OVERWRITTEN / 9 PROPAGATED / 3 DIED)", "7ae3 cell (QD, no death on the pair tape)",
    {"D3": ("WORDING", "nothing can die in this cell (QD aliased, no reaping, no replenishment); 'DIED' = 'replaced as an id' = "
                       "relabelled by another accepted overwrite. Read: 15/24 lost to overwrite, 9 propagated."),
     "D9": ("NONE", "fates keyed on oid; D8 latent.")}, None, ["287 (graph)"])
row("X-H2-NORECOMB", "c9x-pair", "WEAK_SIGNAL", "7ae3 cell", {})
row("C-NORECOMB", "c9x-pair", "NOT_CONFIRMED", "7ae3 + c2a8 cells",
    {"W29": ("WORDING", "power ~0.08 (pooling halved the effect); BASE arm 5/24 vs C-RUNAWAY BASE 4/150 (p = 0.003).")},
    "NOT_CONFIRMED -> UNDERPOWERED", ["288"])
row("X-PAIR-NORECOMB", "c9x-pair", "INVALID (downgraded)", "24 RECOMBINATION cells", {})
row("X-RUNAWAY", "c9x-pair", "SIGNAL (descriptive)", "7ae3 cell, BASE, splice off", {"D8": ("NONE", "64-byte implant fills its half: no padding.")})
row("C-RUNAWAY", "c9x-pair", "CONFIRMED", "7ae3 cell, BASE, splice off vs on",
    {"W29": ("WORDING", "FRAGILE: 7/150 is the minimum passing count; prior power 0.05-0.56; second try after C-NORECOMB; "
                        "claim-level x2 gives 0.0145 > 0.01."),
     "D8": ("NONE", "no padding; d >= 20 is not reachable by a one-step inflation.")}, "CONFIRMED-FRAGILE", ["286-296"])
row("X-RUNAWAY-TRANSPLANT", "c9x-pair", "CLEAN_NULL", "8 RECOMBINATION specimen cells", {"D3": ("NONE", "")})
for eid, v in (("X-STATE", "WEAK_SIGNAL"), ("X-SUFFICIENCY", "CLEAN_NULL"), ("X-POSITION", "INVALID (withdrawn)"),
               ("X-CRITICAL-MASS", "WEAK_SIGNAL"), ("X-DECAY", "WEAK_SIGNAL"), ("X-STALL", "SIGNAL"), ("X-STERILE", "CLEAN_NULL"),
               ("X-STALL-F0", "SIGNAL"), ("X-ROOT-AUDIT", "WEAK_SIGNAL"), ("X-ACQUIRE", "WEAK_SIGNAL"), ("X-CONTENT", "WEAK_SIGNAL"),
               ("X-CORE", "WEAK_SIGNAL"), ("X-CORE-TIME", "SIGNAL"), ("X-CERT-BREAK", "WEAK_SIGNAL")):
    row(eid, "c9x-pair", v, "7ae3 / foreign pair cells; genome- or P-11-based readouts", {})
row("C-CRITICAL-MASS", "c9x-pair", "CONFIRMED", "7ae3 cell, BASE, k=4 vs k=1",
    {"W29": ("NONE", "ROBUST for the weak stated claim."),
     "W25": ("WORDING", "its own two doses still reject independence (joint p = 0.014); the superadditivity retraction rests on "
                        "X-DOSE-CURVE alone.")}, None, ["303-307"])
row("X-DOSE-CURVE", "c9x-pair", "CLEAN_NULL ('founders are independent lottery tickets')", "7ae3 cell, k = 1,2,4,8",
    {"W25": ("BIAS-", "the LRT (p = 0.42) is on its own doses only; C-CRITICAL-MASS's k=1/k=4 data reject independence at "
                      "p = 0.014 and W2-1 finds the k=1 batches homogeneous. 'Independent' is not established; UNRESOLVED (W2-12).")},
    "CLEAN_NULL on its own doses; founder independence UNRESOLVED", ["308-310", "436-439"])
row("X-TICKET", "c9x-pair", "WEAK_SIGNAL", "7ae3 cell, BASE",
    {"D3": ("WORDING", "'causal lineage extinct' cannot mean death (no deaths in the cell): every label holder was overwritten "
                       "(N1/N2: side-0 LDIR hijack explains ~0.21 of the 0.28 epoch-1 loss).")}, None, ["311-314"])
row("X-ATOMIC", "c9x-pair", "SIGNAL", "7ae3 cell, ATOMIC vs BASE",
    {"AC": ("WORDING", "composite treatment: keeps predecessor-accepted overwrites (causal or not) and discards self-writes; N9 "
                       "attributes ~3/4 of the static establishment gain to the fidelity clause.")}, None, ["325-327"])
row("C-ATOMIC C1", "c9x-pair", "CONFIRMED", "7ae3 cell, ATOMIC vs BASE, 80+80",
    {"AC": ("WORDING", "'Tape-write erosion is what stops pair-tape heredity' -> 'the composite ATOMIC rule (keep only "
                       "predecessor-accepted overwrites, causal or not; discard all other writes including self-writes) "
                       "produces runaway'; N9: fidelity clause ~75%, self-write discard the rest."),
     "W29": ("NONE", "ROBUST (composite)."),
     "D8": ("NONE", "")}, None, ["328-331"])
row("C-ATOMIC C2", "c9x-pair", "NOT_CONFIRMED", "15 other panel cells",
    {"W29": ("WORDING", "only 2 of 15 specimens ever reached d >= 5; rule needed >= 4 favouring ATOMIC: ineligible."),
     "D3": ("NONE", "pressures inert, but C2 never attributed the null to pressure."),
     "D4": ("NONE", "pooled over cells.")}, "NOT_CONFIRMED -> INELIGIBLE", ["331-334"])
row("X-DONOR-RATE", "c9x-pair", "SIGNAL", "static P-11 assay in 16 panel cells", {"D3": ("NONE", "static assay.")})
row("X-DONOR-SWAP", "c9x-pair", "WEAK_SIGNAL", "7ae3 genome in 11 foreign cells, ATOMIC",
    {"D3": ("WORDING", "'competence is a property of genome x cell': on the pair tape pressure, environment, task and niche "
                       "structure are inert for copying, so 'cell' reduces to representation / ops mask (SELF) / copy primitive / "
                       "mutation factors."),
     "D4": ("BIAS?", "in-world runaway counts compare ffa6 and e160 (Z8_SLOTTED, ~8x opcode-hitting supply) with Z8_64 cells; "
                     "the static assay rates are unaffected."),
     "AC": ("NONE", "ATOMIC declared.")}, None, ["336-342"])
row("X-SWAP-ORIGIN", "c9x-pair", "CLEAN_NULL (labels corrected)", "9cba/e160/ffa6",
    {"D24": ("NONE", "already corrected (Part B 1/8 vs 0/8 uninformative).")})
row("X-ATOMIC-RANDOM", "c9x-pair", "SIGNAL", "7ae3 cell, genome vs random implant, ATOMIC",
    {"D24": ("NONE", "unpaired Fisher; audited (T-DEF-D24)."),
     "AC": ("NONE", "'descendants' already narrowed to label descent by X-CONTENT.")})
row("X-SWAP-ANCESTRY", "c9x-pair", "SIGNAL", "foreign cells, ATOMIC",
    {"AC": ("NONE", "spread through kept non-causal overwrites (dossier B A2) is already covered by 'lineage descent, not content'.")})
row("C-SWAP-ACQUIRE", "c9x-pair", "NOT_CONFIRMED", "9cba/e160, genome vs random, 240+240",
    {"W29": ("WORDING", "near-miss (p = 0.0018; minimum attainable 10 vs 0); flips at d >= 10 (11 vs 0, p = 4.3e-4); power 0.41."),
     "D24": ("NONE", "unpaired.")}, "NOT_CONFIRMED -> NEAR-MISS / UNDERPOWERED", ["363-365"])
row("C-CORE", "c9x-pair", "CONFIRMED", "7ae3 cell, ATOMIC, 64 seeds",
    {"W29": ("WORDING", "FRAGILE: 17/27 vs bar 16.2; one classification flip fails it; 'conserves SELF+LDIR' ROBUST, 'and little "
                        "else' FRAGILE."),
     "AC": ("NONE", "purifying-selection limit already recorded (Aporia #621).")}, "CONFIRMED-FRAGILE", ["376-381"])

# ---------------------------------------------------------------- W1
row("X-DONOR-DISCOVERY", "W1", "SIGNAL (1/96)", "7ae3 + ffa6 cells, ATOMIC, random populations",
    {"D12": ("NONE", "one L2 run; the screen's noise cannot move 1/96 across the <= 10% bar.")})
row("X-DD-DENSE-COPY", "W1", "SIGNAL (0/96 vs 49/96)", "7ae3 + ffa6",
    {"D12": ("BIAS?", "8/49 DENSE L2 runs rest on a best rate < 0.6 (W2-8); 41 vs 0 still SIGNAL."),
     "D4": ("WORDING", "per-cell 19/48 vs 30/48 is a SLOTTED-vs-Z8_64 contrast.")})
row("C-DENSE-COPY", "W1", "CONFIRMED (1/64 vs 39/64)", "7ae3 + ffa6, ATOMIC",
    {"D12": ("NONE", "checked here (d12_sensitivity.json): strict L2 >= 0.6: 36/64 vs 1/64 (p = 3.5e-13); >= 0.7: 35 vs 0."),
     "D4": ("WORDING", "secondary per-cell split (7ae3 14/32, ffa6 25/32) is operator-confounded."),
     "W29": ("NONE", "ROBUST.")}, None, ["443-451"])
row("X-DD-ESTABLISH", "W1", "SIGNAL", "7ae3 + ffa6, CARRIED",
    {"W25": ("BIAS?", "LAC: 8/23 'ESTABLISHED' first donors made 0 causal births (dossier D U1); SCP: run_de.competent is a "
                      "zero-context screen."),
     "VR": ("WORDING", "in-world, a newborn's first execution starts from the victim's registers, not its own.")})
row("X-DD-NOCOPY-CONTEXT", "W1", "WEAK_SIGNAL", "", {"VR": ("WORDING", "STATE/PARTNER labels: a newborn's carried state is the victim's.")})
row("X-DD-STATE-RESET", "W1", "CLEAN_NULL", "reset registers on genome change",
    {"VR": ("NONE", "this IS the victim-register test; its endpoint was establishment only (W2-1)."),
     "D12": ("BIAS?", "conditional on L2 from run_dd.screen.")})
row("X-DD-SELFSTATE", "W1", "WEAK_SIGNAL", "", {"VR": ("WORDING", "'the state its OWN execution leaves' is the static assay; in-world the first context is the victim's.")})
row("X-DD-STATELESS", "W1", "SIGNAL", "7ae3 + ffa6",
    {"D12": ("BIAS?", "runaway-given-L2 with L2 from the re-drawn screen."),
     "D4": ("WORDING", "7ae3 0.32->0.74 vs ffa6 0.43->0.98 is operator-confounded.")})
row("C-STATELESS", "W1", "NOT_CONFIRMED (p = 0.012)", "7ae3 + ffa6",
    {"D12": ("NONE", "checked: requiring L2 at >= 2 checkpoints gives p = 0.040; stays NOT_CONFIRMED."),
     "D4": ("WORDING", "'the effect sat entirely in ffa6' is a SLOTTED-vs-Z8_64 contrast; X-P2-BRIDGE later reversed the split.")},
    None, ["460-461"])
row("C-STATELESS-FFA6", "W1", "CONFIRMED (11/33 vs 34/42, p = 3.3e-5)", "ffa6 only (Z8_SLOTTED, NICHES_HIGH_MIG, COEVO_ENV), ATOMIC",
    {"D12": ("BIAS+", "flicker admissions are differential: 9 DENSE vs 4 STATELESS runs have L2 at exactly one checkpoint (0 and 1 "
                      "establish), inflating the DENSE denominator. L2 at >= 2 checkpoints: 11/24 vs 33/38, p = 7.6e-4 (passes "
                      "0.001); >= 3: p = 0.005 (fails). The unconditional endpoint 34/48 vs 11/48 (p = 2.3e-6, W2-9) is screen-free."),
     "D4": ("WORDING", "the confirmed scope is a SLOTTED-operator cell; the 7ae3-vs-ffa6 split that motivated the restriction is "
                       "operator-confounded (and was later withdrawn by X-P2-BRIDGE)."),
     "D1": ("NONE", "4 COEVO niches, but readouts are P-11 assays and depth; comp has no dynamical role under QD on the pair tape."),
     "W29": ("NONE", "ROBUST (unconditional p = 2.3e-6)."),
     "VR": ("NONE", "the 'persistence' reading is already withdrawn.")}, "CONFIRMED (prefer the unconditional endpoint)", ["453-462"])

# ---------------------------------------------------------------- P2
row("X-P2-ATTRIB", "P2", "SIGNAL", "static", {})
row("X-P2-SHAM", "P2", "CLEAN_NULL", "", {"D12": ("NONE", "0/96: screen noise cannot create donors at rate 0.")})
row("X-P2-PLANT", "P2", "SIGNAL (32/96)", "", {"D12": ("BIAS?", "L2 from re-drawn screen; bar 25/96."), "D4": ("WORDING", "per-cell 15/17.")})
row("X-P2-BRIDGE", "P2", "CLEAN_NULL (split reverses)", "C7 / C7S / C7N / CF bridge cells, implanted panel",
    {"D4": ("WORDING", "the axis reading 'mutation topology' is wrong: SLOTTED (C7S, CF) differs from Z8_64 by ~7x effective "
                       "supply and 87% opcode targeting (N14). The null on the split stands."),
     "D24": ("WORDING", "C7N vs C7 (10/32 vs 4/32) has no code mechanism (niches inert, N6/N7); migration draws unpair the runs."),
     "W25": ("WORDING", "LAC at run_br.py:159 (label lineage).")}, None, ["472-474", "484-489"])
row("X-P2-REGSTATE", "P2", "SIGNAL (ZERO_SPECIFIC)", "CF / C7, implanted 16-donor panel",
    {"W29": ("BIAS+", "panel admitted by a zero-state screen (as C-ZERO); ZERO > CONST partly built in."),
     "VR": ("WORDING", "CARRY arm's carried state includes victim registers.")})
row("C-ZERO-SPECIFIC", "P2", "CONFIRMED (26/48 vs 2/48)", "ffa6 cell (CF), fresh 16-donor panel screened from zeros",
    {"W29": ("BIAS+", "donor-clustered (ICC 0.44): donor-level sign p = 0.003 fails the frozen 0.001; and N11: 14/16 donors cannot "
                      "copy from 0x5A at all, so CONST 2/48 was forced by the screen. 'Zero is special' is mostly a statement about "
                      "the screen; N12: what zero supplies is mainly the HL pointer phase."),
     "D12": ("NONE", "panel screen re-run 16/16; admission noise is not arm-differential."),
     "VR": ("WORDING", "CARRY 6/48 is establishment from victim-carried registers."),
     "D4": ("WORDING", "scope is a SLOTTED-operator cell.")},
    "CONFIRMED at run level -> 'establishment in the world the donors were screened for' (ARTIFACT-RISK for 'zero is special')",
    ["466-471"])
row("X-P2-ENDOSTATE", "P2", "CLEAN_NULL", "", {"W25": ("NONE", "ruler (one-point self-state) defect already recorded.")})
row("X-P2-LINEAGE", "P2", "WEAK_SIGNAL", "", {"W25": ("NONE", "LAC already in dossier D U1.")})
row("X-P2-D0CHECK", "P2", "CLEAN_NULL", "", {})

# ---------------------------------------------------------------- ARC3
row("ARC3 accessibility delegate", "ARC3", "operator CORRECTED; carrier exposure SUGGESTIVE", "7ae3 / ffa6",
    {"D4": ("WORDING", "the delegate described SLOTTED correctly (opcode positions at offsets 1-3 mutate, frame shifts), but "
                       "FINDINGS condensed it to 'both use the OPERAND operator' and 'in ffa6 slot offsets 1-3 mutate': in effect ffa6 "
                       "has an opcode-randomizing operator (87% of edits)."),
     "D12": ("BIAS?", "neutral-walk pilot screens with run_dd.screen.")}, None, ["484-489"])
row("X-A3-FAIR", "ARC3", "SIGNAL ZERO_LITERAL (S_ZERO 0.867)", "7ae3 + ffa6, reset worlds",
    {"D11": ("WORDING", "first-donor profiles truncated to 20; full set: S_ZERO 0.833 (one run flips). Label unchanged."),
     "W25": ("NONE", "SCP at run_fair:94-95 (fixed entry states) is the declared ruler."),
     "VR": ("NONE", "")})
row("X-A3-FORENSIC-16000006", "ARC3", "KILLED as single change; distributed change real", "", {})
row("X-A3-ENDOSTATE-R", "ARC3", "WEAK_SIGNAL / CLEAN_NULL", "", {})
row("X-A3-SFLINEAGE", "ARC3", "SIGNAL (3/5 runs, 100% in L)", "C-A3's parent instrument",
    {"D10": ("BIAS+", "same 'last checkpoint with a state-free genome' reading as C-A3; persistence not required."),
     "W25": ("WORDING", "LAC (run_sfl:55-61,77-79): L is label descent through accepted replications, including non-P-11 edges; "
                        "X-MAT checked content only for C-A3's events, not these 5 runs.")})
row("X-A3-AUTOPSY", "ARC3", "SIGNAL (C3 = material)", "", {"W25": ("WORDING", "SIM/LAC (run_ap:94-106) MED.")})
row("C-A3-INTERNALIZE", "ARC3", "CONFIRMED (8 events, bar 4)", "7ae3 + ffa6, dense VM, ATOMIC, CARRIED, 72+72 runs",
    {"D10": ("BIAS+", "8 as coded -> 4 with state-free genomes at the final checkpoint (exactly the bar) -> 3 if they must be the "
                      "majority of competent genomes. The free_in_L clause is equivalent to the L_share clause; 4 events rest on "
                      "transient genomes (1, 1, 11, 7 genomes; 0 at final)."),
     "W29": ("WORDING", "FRAGILE: no control arm, no null calibration; the 20-seed state-free assay flickers."),
     "W25": ("BIAS?", "RCF: the replay control re-applies event() to stored JSON (cannot refuse); LAC: L follows labels, including "
                      "non-P-11 edges; SCP (N13): 'competent' is a zero-context screen in a CARRIED world, so the counts cover only "
                      "the zero-competent subset of the reproducing population."),
     "D4": ("WORDING", "per-cell 'ffa6 7, 7ae3 1' becomes 3 vs 1 at the final checkpoint (one-sided p ~ 0.31) and is "
                       "operator-confounded either way."),
     "D3": ("WORDING", "'native QD pressure' (XTG PREREG:31) is no pressure: the only selection is overwriting."),
     "VR": ("WORDING", "in the CARRIED world newborns start from the victim's registers."),
     "AC": ("WORDING", "N9: under ATOMIC the world's fidelity gate maintains copies; 'endogenous' refers to the register-setting "
                       "content, not to organismal copy fidelity."),
     "D1": ("NONE", "ffa6 multi-niche but readouts are assays; comp is dynamically inert.")},
    "CONFIRMED (as coded) -> CONFIRMED-FRAGILE: 4 persistent events = exactly the bar; 3 on a majority reading", ["524-531"])
row("X-A3-WITHDRAW", "ARC3", "CLEAN_NULL (speed)", "7ae3 + ffa6, ZERO scaffold withdrawn",
    {"W25": ("BIAS-", "PERSISTS is 12/12 in GRADUAL, ABRUPT and CONTROL_ZERO: the endpoint is at its ceiling, so a GRADUAL > "
                      "ABRUPT speed effect was undetectable (RCF). First drafted as INVALIDATES; downgraded by the adversarial pass: "
                      "the gradual-withdrawal hypothesis predicts ABRUPT collapse, and ABRUPT 12/12 contradicts that directly "
                      "(n = 12). LAC at run_wd:94-95,133-134."),
     "VR": ("WORDING", "the robustness rise after withdrawal is measured in a CARRIED world where newborns start from victim registers."),
     "D24": ("NONE", "arms identical to epoch 300, then unpaired; no paired test used.")},
    "CLEAN_NULL -> CEILING NULL: abrupt withdrawal did not reduce persistence (12/12); a speed effect was undetectable",
    ["533-553"])

# ---------------------------------------------------------------- frontier
row("X-MAT-INTERNALIZE", "frontier", "ENDOGENOUS (8/8 ENDOGENOUS_MATERIAL)", "replays of C-A3's 26 eligible runs",
    {"D10": ("WORDING", "inherits the transient endpoint: 4 of 8 endpoints are at epochs 1200-1900 with 1-11 organisms and 0 at "
                        "final. At the final checkpoint 4/4 are ENDOGENOUS (X 0.000-0.027): the verdict holds on 4."),
     "D4": ("WORDING", "MUT share 0.19-0.56 in the 7 ffa6 runs vs 0.045 in 7ae3: ffa6's 'endogenous' bytes are ~43% output of the "
                       "SLOTTED opcode-randomizing world operator. W2-9's MIXED-if-MUT-foreign alternative is entirely an ffa6 / D4 "
                       "phenomenon."),
     "W29": ("WORDING", "ARTIFACT-RISK: 7/8 endpoints at L_share 1.0 where X ~ 0 by structure; no planted-transplant control."),
     "W25": ("NONE", "PAD/LAC at run_xmi MED; the bit-identical replay gate is good practice.")},
    "ENDOGENOUS (MUT-neutral, 4 persistent + 4 transient; ARTIFACT-RISK, no positive control)", ["(absent from FINDINGS)"])
row("X-TASK-GATE", "frontier", "frozen, NOT RUN", "ffa6 + 7ae3, TASK_GATED pair tape",
    {"D1": ("INVALIDATES", "ffa6 is COEVO_ENV x 4 niches; cached competence crosses niches and is the gate input."),
     "XTG": ("INVALIDATES", "D6 reader filter uses the base cue index (ABR-niche readers never count); D15 a regime-blind echo "
                            "scores held 0.74 and counts competent 200/200; D14 Stage 0 never exercises the pair path or CD; "
                            "D13 INIT != sorting under ATOMIC; D7 revalidation is 100% cache hits."),
     "D9": ("BIAS?", "stale victim competence becomes the gate input for newborns."),
     "D3": ("WORDING", "TASK_GATED is one of the few non-aliased pressures, but the 'regime' eligibility (25/72) came from a "
                       "pressure-free world."),
     "W25": ("INVALIDATES", "RCF: CD = 0 by construction in Stage 0's EXTERNAL arms (confirmed in code by Nestor).")},
    "DO NOT DISPATCH AS FROZEN (errata filed)", [])


def counts():
    by = {d: {} for d in DEFECTS}
    for r in R:
        for d in DEFECTS:
            imp = r["cells"].get(d, ("NA", ""))[0]
            by[d][imp] = by[d].get(imp, 0) + 1
    return by


def md():
    L = ["| verdict | recorded | " + " | ".join(DEFECTS) + " |", "|" + "---|" * (len(DEFECTS) + 2)]
    short = {"NA": "", "NONE": "0", "WORDING": "W", "BIAS+": "B+", "BIAS-": "B-", "BIAS?": "B?", "INVALIDATES": "**INV**"}
    for r in R:
        L.append("| %s | %s | " % (r["id"], r["verdict"]) +
                 " | ".join(short[r["cells"].get(d, ("NA", ""))[0]] for d in DEFECTS) + " |")
    return "\n".join(L)


if __name__ == "__main__":
    out = {"defects": DEFECTS, "applies_rule": APPLIES, "rows": R, "counts_by_defect": counts(),
           "n_rows": len(R),
           "relabels": [{"id": r["id"], "from": r["verdict"], "to": r["relabel"]} for r in R if r["relabel"]],
           "invalidations": [{"id": r["id"], "defect": d, "why": r["cells"][d][1]} for r in R for d in r["cells"]
                             if r["cells"][d][0] == "INVALIDATES"]}
    (HERE / "matrix.json").write_text(json.dumps(out, indent=1))
    (HERE / "matrix.md").write_text(md() + "\n")
    print("rows", len(R))
    print(json.dumps(out["counts_by_defect"], indent=0))
    print("relabels", len(out["relabels"]), "invalidations", len(out["invalidations"]))
