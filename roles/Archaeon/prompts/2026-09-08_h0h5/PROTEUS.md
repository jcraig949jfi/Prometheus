PROTEUS — H0-H5: THE H1 BOOLEAN SUBSTRATE (from the operator, 2026-09-08)

Read first: roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md
(sections 4 C2/C3, 5 H1, 5 H0). You own program semantics, runtime and
affordance identity, and the executable input/output contract. Your B1
library is the base. Starts now; nothing here waits on the loader.

DELIVER
1. A bounded typed Boolean grammar: 3-input tasks first; primitives
   input, constants, NOT, AND, OR, XOR; compiled to a DECLARED subset of
   the VM's semantics. Compile/evaluate parity against an INDEPENDENT
   truth-table evaluator over all 8 inputs. If the current input channel
   cannot express this subset, record the exact failing positive control
   and implement an explicit NEW player interface; never redefine old
   specimens.
2. Input-sensitive positive controls: hand-built programs whose output
   changes with each input; a deliberately input-blind program as the
   negative control.
3. New candidates use a NAMED population/interface; the frozen USE_A
   specimen registry is not mutated. Candidate players receive only their
   declared channels; the task oracle may be owned by the executor but no
   hidden task implementation or final evaluation set reaches the player.
4. Preserve the ordering that defines the first witness and the distinction
   between budget exhaustion and mismatch (your B1 contract). A witness
   pack is INPUT DATA to the target run, never transferred target truth:
   labels are always recomputed by the target oracle.
5. Fixtures: reset, type, budget, output-cap, and an independent-oracle
   parity fixture. State the exact finite correctness scope (which task
   sizes are exhaustively verified).
6. Expose `genome_read` (any load touching a genome address) in results, as
   already asked for D-16.

THEN, with Vivarium: cegis_boolean_v1 -- the within-task CEGIS loop lives
inside the kind (candidate policy/version, source pack, oracle interface,
case ordering, seed streams, max candidates, oracle/op caps, trace bound,
termination all sealed). `no witness` alone is never `solved`; solved
requires complete coverage of the declared finite verification scope.

NOT ASKED: breeding, mutation of specimens, LLM proposers.

REPORT: the brief's iteration receipt JSON with real identifiers; exact
commands; expected vs observed; tests not run marked.
