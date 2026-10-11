# NS-01 GENERATION PROTOCOL (frozen before any proposal is generated or evaluated)

Directive: roles/Cosmos/prompts/2026-10-11_operator_NS-01/DIRECTIVE_VERBATIM.md (main). Exploratory, visible-world
only. No holdout, no C4 confirmation data, no killed law revived. Every job under prometheus.cosmos.supervise.

## Object of generation
An executable MECHANISM satisfying prometheus/cosmos/ns01/CONTRACT.md (identical text for every arm): a System with
init / noise / step / readout_features / full_state and make(task), numpy only, knobs fixed. The audit
(FAILURE_ATLAS.json) found the operator's 14 candidates to be inference-procedure failures; they constrain the JUDGE
(tier P). Candidates are excluded on the 7 mechanism-level classes (tier M) and on equivalence to the 16 witnesses.

## Arms (8 proposals each; same contract; one fresh, tool-less agent conversation per LLM arm)
Each LLM arm is a separate subagent conversation whose only input is the text below; it is instructed to use NO
tools (no repository access; the archive cannot leak through files). Proposals are requested one at a time
(8 turns). The arms differ ONLY in what the generator is told:
- A UNCONSTRAINED: the contract. Turn 1: "Propose a new executable mechanism." Turns 2-8: "Propose another
  mechanism, causally different from your previous ones."
- B NEGATIVE PROMPT: the contract + the operator's challenge (directive s2, verbatim) + the 14 operator failure
  descriptions E01-E14 (verbatim) + the 7 tier-M mechanism failure descriptions (name + one sentence). Same turns.
- C BLIND / EXTERNAL EXCLUSION: the contract only. After each proposal Cosmos runs the exclusion engine and replies
  with ONE compact signal and nothing else: "REJECTED: known failure class <id>" or "REJECTED: equivalent to a known
  mechanism" or "REJECTED: degenerate" or "REJECTED: not executable" or "ACCEPTED". Then "Propose another mechanism."
  No witness, description or code is revealed.
- D GRAMMAR (non-LLM): prometheus/cosmos/ns01/grammar.py samples mechanisms from a symbolic grammar (seeded); after
  each proposal the same compact signal down-weights the primitives of a rejected proposal. Primitive choices are a
  documented bias (grammar.py docstring). Cosmos does not select among grammar outputs: the first 8 draws are the 8
  proposals.

## Evaluation of every proposal (identical; executable only)
1. Freeze: source sha256 recorded in CANDIDATES.jsonl BEFORE execution.
2. Compliance: imports, interface, a 3-step dry run, finiteness; else NONEXECUTABLE (counted, not repaired).
3. Signature (ns01/signature.py, fixed seeds) -> classify (frozen rules, FLOOR .10) + nearest witness distance.
4. Label (first match):
   NONEXECUTABLE | DEGENERATE (rule fired) | KNOWN_EQUIVALENCE (distance <= TAU .05 to a witness) |
   KNOWN_FAILURE (not viable and >= 1 tier-M rule fired) | VIABLE_KNOWN_STRUCTURE (viable, rules fired, e.g.
   linear-blind but usable) | VIABLE_DISTINCT (viable, no rule fired, distance > TAU from every witness) |
   DISTINCT_BEHAVIOR_UNEXPLAINED (not viable, no rule fired, distance > TAU).
5. Deeper investigation (preregistered information-value rule): every DISTINCT_BEHAVIOR_UNEXPLAINED and every
   VIABLE_DISTINCT candidate, in that order, gets: (a) fresh-seed signature, (b) the 4 disguise transforms, (c) the
   distance to all OTHER candidates. It is reproducibly distinct iff (a) and (b) stay > TAU from every witness and the
   label is unchanged. Only then is a NOVEL_FAILURE_CANDIDATE considered (directive s6: minimal witness, causal
   account, an intervention separating it from its nearest known class, a representation-change test).
   NOVEL_FAILURE_SUPPORTED additionally needs a planted minimal re-implementation written by Cosmos from the causal
   account that reproduces the signature. Unmodified originals are preserved; no candidate is repaired.
6. A novel class, if supported, is added to the archive only for NS-02 (not retroactively).

## Measurements per arm (raw, not collapsed)
Primary: number of reproducibly distinct mechanisms / failure classes per unit effort (generation wall time and
characters; execution CPU seconds). Secondary: fractions per label; signature diversity (mean pairwise distance
within arm; number of TAU-clusters); fraction matching tier-M classes, by class; re-encoding robustness.
P6 (atlas): 8 per arm -> exact counts only; no significance claims.

## Exclusion-engine qualification (before any candidate is evaluated)
Disguised witnesses (Permute, LinearEncode, Rescale, RenameState; a hand refactor of DelayLine; a parameter
variant): false rejection <= .10. Seven look-alike distinct pairs: false acceptance <= 1/7. If the engine fails,
the failure is reported and candidates are still evaluated with the failing component marked.

## Pre-registered ways all four arms might fail (directive s10), each with what would show it
- B anchors on the archive -> B's KNOWN_FAILURE/KNOWN_EQUIVALENCE fraction >= A's and B's proposals sit nearer the
  witnesses (median nearest-witness distance <= A's).
- C collapses on repeats -> within-C signature diversity <= A's; repeated rejections of the same class.
- D's grammar bias -> D's proposals cluster (few TAU-clusters) or are mostly DEGENERATE.
- Engine confuses implementation with physics -> disguise false rejections; look-alike false acceptances.
- Novelty pressure -> complicated nonsense -> rising NONEXECUTABLE / DEGENERATE in C over turns.
- The contract forces one architecture -> all arms' viable proposals land within TAU of register/delay witnesses.
- The 7 classes are too coarse to guide search -> C's signals mostly one class.
- The signature lacks power for new causal behaviour -> distinct-looking mechanisms (by code) sharing signatures.
