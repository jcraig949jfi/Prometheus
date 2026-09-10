VIVARIUM AND PROTEUS — TRACK A, PART 2: cegis_boolean_v1 AND THE H0
INPUTS (from the operator, 2026-09-10)

Read: CHIMERA_BRIEF_2026-09-10.md §3 Track A items 5-8; design v0.1 §5 H1
and H0, §4 C3. Vivarium owns the kind contract; Proteus owns the semantics
(boolean3 substrate, 790fb4803; B1 library). Archaeon issues the arms and
supplies the failure packs; Harmonia owns the analysis.

DELIVER
5. cegis_boolean_v1: the bounded within-task CEGIS loop lives INSIDE the
   kind. Sealed inputs: candidate policy/version (fixed seeded enumeration
   over the declared grammar: input, constants, NOT, AND, OR, XOR), the
   source pack slot (a failure_input_set artifact through the loader, or
   EXPLICITLY empty), oracle interface, case ordering, seed streams, max
   candidates, oracle/op caps, trace bound, termination policy. Exhaustive
   verification over all 8 inputs; Boolean NOT compiled as XOR x, ONE;
   solved requires full coverage; no-witness alone is never solved;
   budget exhaustion is its own status. The generic runner stays blind.
6. The H0 inputs on the SAME kind: the declared source-failure input
   contract, and an explicit optional component-library slot whose EMPTY
   value is a declared input (not a hidden alternative). One solver
   runtime for all four cells. A small deterministic extractor for
   repeated typed subtrees may produce the instrument library; hand-built
   library fixtures are instrument controls and are labelled so.
7. H1 alpha (Archaeon issues three arms as a human-issued comparison
   family): fresh CEGIS; the same plus random-compatible source inputs; the
   same plus relevant source inputs. Every retrieved input is re-labelled
   by the TARGET oracle; the fresh arm gets an equal fresh-probe allowance;
   ordered witnesses, shortfalls, exhaustion and every assigned task are
   preserved. Eight inputs may saturate; an alpha tie is a finding about
   the scope, not a reason to retune anything.
8. H0 alpha (Archaeon issues four cells): neither / failures only /
   library only / both. Establishes correct exchange and measurement; no
   synergy claim; G = S11 - S00 and I = S11 - S10 - S01 + S00 are analyses
   under Harmonia's rules, not outcome rules.

Proteus specifically: input-sensitive positive controls and the compile/
evaluate parity fixture travel with the kind; the frozen USE_A registry
stays untouched; candidates receive only their declared channel.

REPORT: the brief's iteration receipt JSON with real identifiers; exact
commands; assigned / attempted / solved / exhausted / invalid /
infrastructure-failure counts per arm; tests not run marked.
