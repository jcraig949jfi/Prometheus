# Should C2 or SI01 exist next? (Block O)

Currency: 2026-09-27, after C1b and the 2026-09-27 spikes. Neither is
launched or authorized. This is a recommendation with evidence.

## What the new evidence changes

1. PTE mechanisms are heterogeneous inside a C1 label. The four RELAY
   "routed relays" carry the bit at mid-transit in the channel (3) or in
   site state (1). MAJ cells use the channel (2), sites (1), or BOTH
   JOINTLY (4781b0a1). C1's family-level labels hide carrier diversity.
   The carrier-swap instrument resolves it in minutes per cell.
2. In-flight "memory" is a TUNED ECHO (M2): it holds a bit for the one
   trained interval and is at chance at gap >= 12. It forgets by
   construction.
3. "Self-modification" (M3) is a one-time configuration bootstrap. It is
   possibly an artefact of random rule initialization (T-M3-1).
4. Temporal instruments must show reach (the D-A lesson), and mechanism
   instruments should be carrier swaps, not kill/drop thresholds.

## C2 ("weather": three load axes inside the habitable zone)

Motivation: WEAKENED as designed. C2 was framed as a phase map of
"organised communication" under traffic, concurrency and conflict, with
labels from ablation fingerprints. After C1b, the most informative
unit is not a label per cell but a CARRIER per cell. A C2 run now would
measure accuracy boundaries without knowing which carrier each champion
uses. A boundary could then be a carrier SWITCH, not a competence limit,
and the design has no way to tell.
Cheaper experiment that answers more: the T-INS-1 carrier table over all
C1 SIGNAL cells, then ONE carrier-resolved load axis (traffic density)
on champions of known carrier. That asks "which carrier survives load?",
a sharper question than C2's.
Recommendation: DO NOT run C2 as designed. Re-derive it after T-INS-1 as
"carrier phase map under one load axis" (C2'). Premature until the
carrier instrument is a tested assay.

## SI01 (selective destruction of expired distinctions)

Motivation: the C1b result makes it LESS attractive on HOLD. The
objections O1 (recency confound) and O2 (forced overwrite) now have a
concrete PTE instance. M2's echo forgets automatically after one round
trip, so an expired cue is gone by timing, not by relevance. On M2-type
carriers SI01 would read SELECTIVE_SURVIVAL (E MERGED) for a trivial
reason: the carrier has a single tuned delay. The #612 mapping would
label it correctly only if the prereg first separates "gone because the
delay elapsed" from "gone because it stopped mattering". Crossed,
interleaved schedules with variable gaps are the only design that does
that, and they would simply kill M2-type champions (T-M2-2: they are
interval-tuned).
Better lens: the distributed carrier (4781b0a1) and the site-latched
relays are more interesting specimens for "what survives when", because
their bit lives in several places at once. A cheaper question first:
does any PTE carrier ever retain an expired distinction at all? Run the
single-cue-twin PRESENT/MERGED census (lens, minutes) across the carrier
table.
Recommendation: DO NOT build SI01 on HOLD/M2. If the operator still
wants the Selective-Irreversibility attack in PTE, the cheap census above
decides whether PTE has any non-trivial retention to study. If none, PTE
is the wrong lens for SI, and Cosmos's persistence/causal-utility
machinery is the better home.

## Is another PTE campaign premature?

Yes, for any campaign that labels mechanisms. First: T-INS-1 (carrier
assay as a tested instrument), T-TA-1 (reach), T-M2-2 (interval tuning).
All three are CPU-scale and hours each, with no campaign.

## HITL
The operator decides whether C2' or an SI census is wanted at all. That
is strategic. Nothing else here needs a decision.
