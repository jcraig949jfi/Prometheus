# Campaign 5 -- local campaign decisions (operator offline ~10 h; "make your own calls")

Format: D5-### | when (UTC) | decision | evidence | alternative rejected |
revisit-if. Each decision states SCIENTIFIC DISCRETION or DETERMINISTIC.
Vocabulary in prose follows archaeon/campaign4/DISPOSITION_C4-REH-1.md s6.
The directive is verbatim at roles/Archaeon/prompts/2026-09-18_campaign5/.

D5-001 | 2026-09-18 14:05 | EXECUTION PATH AND IDENTITY: the campaign harness
path (campaign-3 Experiment parametrized: archaeon/campaign5/c5base.py),
local evaluation, every world / experiment / observation written to the
engine under a NEW client cmp5-archaeon (self-registered by the Engine
wrapper on first use; credential written beside c5base.py, gitignored, never
moved), campaign seed 20260922, ledger prefix L5. NOT Vivarium's
wse_evaluate_v1: it is a working day away (#426) and wraps the OLD evaluator,
which Phase B cannot use at all. Recorded as the directive requires; no
scientific reason to wait was invented. | Directive HARD RULES; Vivarium
#426; D4-001. | Alternative: reuse cmp4-archaeon (rows distinguishable by
seed only) -- rejected: one identity per campaign is the C1-C4 convention. |
Revisit when the kind exists and Phase A is over. DETERMINISTIC.

D5-002 | 2026-09-18 14:05 | THREE QUESTIONS PUT TO THE OPERATOR IN CHAT before
they went offline, each with the default that applies on silence: (1) LANE --
Archaeon authors the Phase-B interpreter, generator and grammar variant under
archaeon/campaign5/ as a campaign-scoped representation, Proteus's frozen VM
untouched, handed to Proteus for adoption after (default yes); (2) FAIL
semantics -- the first fault kills the whole evaluation (reward 0 on every
episode), the maximal HARD (default); (3) STOP authority -- if Phase A returns
OLD_SUBSTRATE_EXHAUSTED and C5-03 returns REPRESENTATION_FAILURE, the
campaign ends there with a report (default). Any answer received is appended
here beside the default it replaces. | Operator preface: "I'll answer
questions now before you start". | -- | Revisit on the operator's word.
SCIENTIFIC DISCRETION (defaults chosen by the lead).

D5-003 | 2026-09-18 14:05 | C5-01 RESOLUTION: 6 walkers per competent parent (C4-05
had 4), depth 64, archives 0/16/32/48/64; 282 walkers per depth gives a
Wilson half-width of about .02 at rates near .05, the smallest effect the
branches use (.02). Walkers 1-4 reproduce C4-05's walks byte-for-byte for the
first 16 steps (same seeds) and that is checked. PRESERVE rule: continued-
gradient branch AND yield per evaluation at depth 64 >= 2 x a random single
edit's (.0012/evaluation). | C5-01/DESIGN.md. | Alternative: 4 walkers
(half-width .03, cannot resolve a 2-point difference). | Revisit never in C5.
SCIENTIFIC thresholds, DETERMINISTIC application.

D5-004 | 2026-09-18 14:30 | C5-01 read: MIXED (r16 .050, r32 .064, r48 .078, r64
.082; gaps .014/.018 below the .02 step; yield per evaluation .00127 -> .00082
below the .0012 single-edit comparator); PRESERVE_NEUTRAL_MECHANISM = NO under
the preregistered rule. Replication of C4-05 3,648/3,648 steps. | C5-01
DEEPWALK_TABLES.json. | -- | Not revisited in C5. DETERMINISTIC.

D5-005 | 2026-09-18 14:35 | C5-02 WORLD SET, frozen from the screen receipt
archaeon/campaign5/WORLD_SCREEN_2026-09-18.json (rule fixed in code before any
candidate was scored: eligible iff best held-out over all 57 parents in
[3/16, .70)): W2_K2d1 (.510), W2_K2_rand (.542), W3_K3 (.382), W4_K4 (.302) --
four distinct structures, 27-45 parents above the floor on each, headroom
.36-.60 to the summit. W2_K2 (.625, eligible) is excluded because C4-06/08
selected on it for 100 generations from these lineages (not a fresh headroom
test); the remaining eligible worlds are held in reserve. Pre-solved worlds
(W0, W1_d4..d16, noise, interleaved, 8-bit delay) are listed in the receipt as
ineligible; two ask kinds failed the generator's own constraints (recorded).
| WORLD_SCREEN_2026-09-18.json. | Alternative: reuse C4-09's worlds --
rejected (three pre-solved). | Revisit never in C5. DETERMINISTIC (rule) +
SCIENTIFIC DISCRETION (the four picked among nine eligible, before any C5-02
row).

D5-006 | 2026-09-18 14:23 | C5-02 control arm length: G_c = ceil(T_lateral / (4 x N)) per
seed from the lateral arm's measured total evaluations; lateral runs first. Recorded
in the prereg by the runner. | c5_02.py. | -- | -- . DETERMINISTIC.

D5-007 | 2026-09-18 14:28 | REPRESENTATION B boundary = the ENCODING only: opcode word
defined iff < 25; register field the opcode reads defined iff < n_regs; addresses from
register contents and jump offsets stay modulo tape; immediates 32-bit; unread fields
cannot fault. FAIL = the whole evaluation (D5-002 default 2); FIZZLE = skip + count.
Grammar B = v0.4 with in-range redraws; operand_perturbation unchanged (the crossing
operator, measured: 9.3% of children cross overall, all through it). | C5-03/DESIGN.md,
repb/. | Alternative: fault on out-of-range ADDRESSES too -- rejected (values, not
encodings; would make LD/ST from computed addresses almost always fatal). SCIENTIFIC
DISCRETION.

D5-008 | 2026-09-18 14:31 | C5-03 a01 FAILED under its own text (F3 count-TVD raw-vs-
injected2 .42; F6 volatile timings; 2 engine 422s on the outcome word). POST-HOC
AMENDMENT for a02, labelled as such: F3's third pair on distinct fault SITES at the
same .50 threshold; F6 strips wall_s/cpu_s (harness defect, C4-01 precedent); outcome
word FALSIFIED. a01 is preserved and both statistics are reported. This is the
campaign's one departure from "no post-hoc movement": it changes a STATISTIC that
measured the wrong quantity (repeat executions of one site), not a threshold, and the
populations were already separated by F2 (static, TVD 1.0) and F5 (sites, 100%). The
operator may overrule; then C5-03 = REPRESENTATION_FAILURE and Phase B is void.
| C5-03/attempts/a01/QUALIFICATION.json. | Alternative: stop Phase B on a01 -- rejected
as an instrument-bookkeeping stop, not a scientific one; flagged in the report.
SCIENTIFIC DISCRETION (the operator's to revisit).

D5-009 | 2026-09-18 14:33 | PHASE A DECISION: OLD_SUBSTRATE_EXHAUSTED. C5-01 did not
meet the PRESERVE_NEUTRAL rule (MIXED; yield per evaluation below a single edit's);
C5-02 returned class A (takeover without improvement: 0/24 world x seed cells improved
at equal total compute; rescued share >= .5 on three worlds; the elite sits at the
starting parent on most cells). Neither mechanism is preserved; Phase B proceeds on
representation B with the OLD substrate's parents transcoded (F1) as the starting
class and with no Phase-A mechanism carried. | C5-01/READOUT.md, C5-02/READOUT.md. |
Alternative: PRESERVE_MECHANISM on the C5-01 probability gradient alone -- rejected,
the rule required efficiency and was written before the run. | Revisit never in C5.
DETERMINISTIC (rules fixed in D5-003 and C5-02/DESIGN.md).

D5-010 | 2026-09-18 14:41 | C5-05 bins DT/DF read BEFORE the unchanged C4-01 classifier;
crossing = static invalidity of the child's genome; thresholds T1-T6 fixed in
C5-05/DESIGN.md; arm R must replicate C4-01 a02 digest for digest. Result: 5,586/5,586;
T1/T2 pass on both grammars; T3 prediction lost (D6 lower by a tenth of a band);
T4 recovered-competent .46 / .42 among executed-crossing children (C5-06 owns the
reading); D7 = 0 everywhere. | C5-05/attempts/a01/GEOMETRY_B.json. | -- | Not
revisited. DETERMINISTIC.

D5-011 | 2026-09-18 14:47 | C5-06..C5-10 PREREGISTERED. Timing, from file times: C5-10/RULE.md
14:36Z (before C5-04 and C5-05 ran); C5-08 14:43Z, C5-09 14:44Z, C5-06 14:45Z (before
C5-05's summary was read at 14:47Z); C5-07/DESIGN.md and C5-10/DESIGN.md 14:47Z -- the
same minute the C5-05 summary was read, so C5-07's cost thresholds (K1 1.10x, K2 the
band, .50 share) were chosen with C5-05's T4 (.46 recovered) in view, and before C5-06
(its input) ran; C5-10/DESIGN.md adds nothing to RULE.md. All committed at 14:49Z: C5-06 matched classes RECOVERY /
BOTH_LIVE / INSULATION_LOSS / BOTH_DIE with held-out replication (3 rng seeds, >= 2/3)
and the fixed gate for C5-07 (>= 10 replicated recoveries AND Wilson lower bound
> .01 of executed-crossing children; degenerate parents excluded); C5-07 costs K1-K3
(conditional); C5-08 M1-M4 with dead-code ablation and length bins; C5-09 four arms
(OLD_v04, OLD_B, B_FAIL, B_FIZZLE) at identical compute with WON/LOST/TIED cells and
the +4 net rule; C5-10 reads RULE.md verbatim. | archaeon/campaign5/C5-0[6-9]/DESIGN.md,
C5-10/RULE.md. | -- | Not revisited. SCIENTIFIC thresholds, DETERMINISTIC application.

D5-012 | 2026-09-18 14:58 | READINGS RECORDED AS THE RULES GAVE THEM: C5-06 REAL_LOCAL_RECOVERY
(229 replicated recoveries, Wilson lower .140 > .01; loss 154 < recovery -> "merely
changed how programs die" = NO); C5-07 INSULATION_CHEAP (K1 median 1.00, K2 +.023, K3
.044); C5-08 MIXED (M1 failed: dead-code ablation moves R_old by .026, one bin over the
band; M2/M3/M4 hold) -- C4-07's "neutrality + length" is corrected to LENGTH + behavioural
neutrality, not unreachable code; the numbers of C4-07 stand. Harness decl readings
(UNDERPOWERED on C5-04/C5-07, WEAK_POSITIVE on C5-03/C5-06) are the machine's mechanical
labels beside the preregistered readings, as with C4-08 (D4-012). | C5-06/07/08
READOUT.md. | -- | Not revisited. DETERMINISTIC.

D5-013 | 2026-09-18 15:03 | C5-09 a01 INSTRUMENT_INVALID BY ITS OWN KILL RULE: the determinism
control compared the whole run record including wall_s (volatile) and read False; every
scientific number is on file (NO_GAIN: nets OLD_B 0 / B_FAIL +1 / B_FIZZLE +1; 96 cells
and not one first held-out gain in any arm). Harness defect -> a02 with the control
comparing wall_s-stripped records and the re-run saved; a01 preserved; a02's numbers
must equal a01's (checked in the readout). C5-10 a01 (NO_CONDITION_SELECTED on a01's
numbers) is preserved and C5-10 re-runs on a02. | C5-09/attempts/a01/REACH.json. | -- |
Not revisited. DETERMINISTIC (the kill rule as written).

D5-014 | 2026-09-18 15:08 | FINAL DISPOSITION: BOUNDARY_CREATED_NO_DISCOVERY_GAIN. Phase A
OLD_SUBSTRATE_EXHAUSTED (D5-009). Phase B: representation B qualified (C5-03 a02, under
D5-008); the boundary is real and countable (C5-05 T1/T2), it does not merely change how
programs die (C5-06: 229 replicated recoveries > 154 losses), recovery is cheap for the
survivor (C5-07), robustness is length not dead code (C5-08), and none of it moves
discovery at equal compute (C5-09 a02 NO_GAIN, nets 0/+1/+1, no first held-out gain in
96 cells; C5-10 a02 NO_CONDITION_SELECTED). The directive's question is answered: the
boundary created a region of bounded variation (parent plus a hole, displacement .015)
from which evolution does NOT discover more efficiently. The campaign stops here as the
branches say. The C5-03 amendment is the operator's to overrule (then REPRESENTATION_
FAILURE governs Phase B and Phase A's disposition stands alone). | CAMPAIGN_REPORT.md,
REVIEW_PACKET_CAMPAIGN5_2026-09-18.md. | Alternative dispositions considered:
NO_CONDITION_SELECTED alone (rejected: it names one slot, not the campaign);
BOUNDARY_CREATED_DISCOVERY_GAIN (rejected: the rule was not met). | Not revisited.
DETERMINISTIC (every branch fixed before its run).

D5-015 | 2026-09-18 15:25 | OPERATOR RULING (verbatim at roles/Archaeon/prompts/2026-09-18_
campaign5/03_OPERATOR_RULING_CLOSURE.md): BOUNDARY_CREATED_NO_DISCOVERY_GAIN ACCEPTED; no
further Campaign-5 slots; Phase A independently sufficient to retire the old substrate/
grammar search direction; C5-10 NO_CONDITION_SELECTED informative. C5-03 bookkeeping as
ruled: a01 = PREREGISTRATION_FAILED -- STATISTIC_MISSPECIFIED; D5-008 = protocol
amendment; a02 = evidence under the amended protocol. Fact determined: a02 re-executed
a01's population seed (1) and evaluation seed (3) on a deterministic evaluator, so it
REUSED outcome-bearing data -> a02's qualification is EXPLORATORY / POST-HOC. Phase B is
not void; the campaign conclusion does not depend on C5-03. C4-07's mechanism reading
superseded (archaeon/campaign4/SUPERSESSION_2026-09-18.md); its numbers stand. The three
D5-002 defaults RATIFIED. Representation B RETAINED as a qualified experimental
instrument, NOT promoted to the platform VM; artifacts handed to Proteus; adoption waits
for a capability the current representation cannot reach. Next work must alter the
searchable program structure / grammar of useful behaviours, not fault-boundary tuning.
| the ruling. | -- | Final. OPERATOR AUTHORITY.
