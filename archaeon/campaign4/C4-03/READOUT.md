+=====================================================================+
|  C4-03 -- LOCAL FAILURE VS GLOBAL DEATH: READOUT                      |
|  Archaeon[m2-49ee5a4d]   2026-09-18 06:45Z   attempt of record a01   |
|  Disposition: REPRESENTATION_BLOCKED (both arms), with the numbers    |
+=====================================================================+

-----------------------------------------------------------------------
0. THE RESULT IN ONE PARAGRAPH
-----------------------------------------------------------------------
On this substrate there is no invalid operation for an insulation rule to
act on. The executed HARD arm cannot exist without a new termination
status (D4-002). The static proxy -- "would-be-fatal = carries an opcode
word outside the 25-entry table" -- was preregistered with a vacuity
check, and the check fired: 932 of 932 instruction words in the 57
parents are out of table (the foundry writes uniformly random 32-bit
words; the interpreter's modulo-25 decode IS the instruction set, not an
insulation layer over a valid one). P(would-be-fatal) = 1.000 on all
4,866 regenerated C4-01 children and all 2,280 C4-02 children (Wilson
lower bound 0.9992). The HARD/FIZZLE comparison has an empty HARD-
survivable arm; the harness reads INCONCLUSIVE ("an arm of the primary
comparison has no rows"), which is the correct reading of an empty
partition, and the slot's disposition is REPRESENTATION_BLOCKED.

-----------------------------------------------------------------------
1. WHAT WAS MEASURED (controls and integrity, all as preregistered)
-----------------------------------------------------------------------
  positive   injected out-of-table word at instruction 0: detected 57/57
  negative   identity child carries the parent's predicates: 57/57
  integrity  regenerated child digest == committed child_digest:
             C4-01 4,866/4,866 (the 606 could-not-apply edits have no
             child), C4-02 2,280/2,280; zero mismatches
  cheat      a hand-set D7 fatal row counts in the coherent share: yes
  parents    fatal_present 57/57, fatal_reachable 57/57; by stratum
             gen0 12/12, w0 15/15, shelf 19/19, delay 11/11
  children   fatal_reachable 1.000 at every C4-01 operator and every
             C4-02 radius (r1..r16)
  the "fatal" partition's class distribution (= the whole C4-01 applied
  population, since the partition is everything): D2 2,318 / D3 442 /
  D4 49 / D5 2,023 (silent 2,018, distinct 5) / D6 34 / D7 0; coherent
  share .109 [.101, .118]; to_D2 .476. The "non-fatal" side: 0 rows.
  Prediction ("fatal coherent share lower than non-fatal by >= 0.10"):
  LOST by construction (no non-fatal rows). Engine records 18 (per
  operator, per radius, parents), 0 errors, 1.5 s.

-----------------------------------------------------------------------
2. WHY THIS IS A RESULT AND NOT A SETUP FAILURE
-----------------------------------------------------------------------
The directive asks whether localizing an invalid operation beats killing
the program. The question presupposes a representation in which some
words are instructions and others are not. This one has no such line:
every 32-bit word decodes, every operand reduces, every jump wraps. The
"FIZZLE" behaviour the directive imagines adding is the only behaviour
the substrate has ever had; there is no HARD baseline that ever existed
to compare against, and C4-01's damage boundary (D2 .29-.64 per operator,
D7 = 0) was measured on a substrate that already insulates every
operation. Localization of failure is therefore not a lever available to
Campaign 4; the damage it measured comes from what the decoded
instructions DO, not from any failing to decode.

Recorded, not repaired: the directive forbids an ISA change during the
campaign, and a "valid subset" chosen now would be a recognizer for the
result one hoped to see.

-----------------------------------------------------------------------
3. CONSEQUENCES FOR LATER SLOTS (re-premised in their own preregistrations)
-----------------------------------------------------------------------
C4-07 (the cost of insulation): "cost only the recovery/fizzle event"
has no event to cost -- every executed instruction is the fizzled kind.
A cost regime can be attached to something measurable (e.g. out-of-genome
tape reads, or reduced operand indices, both countable) only as a
DIFFERENT question; the slot will state that or close
REPRESENTATION_BLOCKED.
C4-08 (can robustness be constructed when free insulation is removed):
there is no free insulation to remove; the slot's perturbation regime can
still be run, but the "removal" arm does not exist.
C4-04 (addressing damage): unaffected in premise -- relative jumps and
register-held addresses are both present in the ISA -- but the
"alternative addressing mode" arm is likewise an ISA question; the
measurable part is static reference resolution under length-changing
edits, which C4-04 will preregister.

-----------------------------------------------------------------------
4. CLAIM CEILING
-----------------------------------------------------------------------
A representation fact about the frozen substrate, measured on every
parent and every committed child. Nothing about search, selection or
what a HARD interpreter would do. The table's per-operator and per-
radius blocks are committed (attempts/a01/PROXY_TABLES.json) and are
uninformative by construction; they are kept so that the vacuity is
reproducible, not because they say anything else.
+=====================================================================+
