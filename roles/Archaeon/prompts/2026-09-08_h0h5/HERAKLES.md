HERAKLES — H0-H5: TWO NEW CA KINDS, H2 AND H5 ALPHAS (from the operator,
2026-09-08)

Read first: roles/Archaeon/prompts/2026-09-08_h0h5/DESIGN_H0_H5_v0.1.md
(sections 4 C2/C3, 5 H2, 5 H5). Preserve herakles/evca exactly as it is:
radius-3 density classification and its conventions are a finished,
qualified library. Everything below is a SEPARATELY NAMED kind. Starts
now; nothing waits on the loader.

H2 ALPHA — ca_stream_v1 (streaming kind on the radius-3 library)
1. Explicit order per step: inject at declared ports -> exactly one CA
   step -> readout. Reset before every independent stream. 31-cell ring
   first; one binary input port; horizon 8. Bit order, boundary, radius as
   the existing library; declare the readout class (capacity-limited
   linear over the current lattice; no undeclared input history) and its
   fitting budget.
2. Frozen complete 256-stream Boolean catalogue for delayed recall and
   adjacent-bit temporal XOR; hand-computed temporal fixtures; warm-up
   masks for delayed targets. Training/development/confirmation partitions
   (proposed 64/64/128) with confirmation labels inaccessible to rule
   search and readout fitting.
3. Known shift-register / logic components as INSTRUMENT-POSITIVE controls
   proving the task instrument and composition interface can pass; a
   readout-only / direct-input baseline with equalised readout budget.
4. Record readout capacity, training, extraction and execution costs.
   Never attribute readout-only computation to the substrate.
Alpha claim boundary: contract + fixtures + one actual CA run; NO
discovered-component claim. Rule search, matched interventions, export and
frozen reuse are beta.

H5 ALPHA — eca_rule_eval_v1 (separate radius-1 elementary CA)
5. index = 4*left + 2*center + right; output = (rule_number >> index) & 1;
   periodic ring. Hand-derived checks for rules 0, 255, 204, 170, 240, 90.
   Do NOT reuse the radius-3 hex decoder under a new number.
6. Assay: 7-cell rings, all 128 initial configurations, fixed 8-step
   horizon; teacher-rule/trajectory tasks deduplicated by observable
   behaviour (equivalence classes retained). Archaeon supplies the
   12-bit-genome decoders producer-side; your evaluator consumes only the
   resolved rule number.

Keep the three evidence stages apart in every report: bounded computation;
causal contribution under matched interventions; frozen reuse.

REPORT: the brief's iteration receipt JSON with real identifiers; exact
commands; expected vs observed; tests not run marked.
