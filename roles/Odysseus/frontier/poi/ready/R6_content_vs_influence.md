# R6 -- Content vs influence: the taint/perturbation disagreement matrix (POI-015, POI-001)

Output path: roles/<your-seat>/poi_R6/ . Stdlib Python, laptop, 3-5 h.
Read 00_READ_FIRST.md.

## Question
In one BEE run (r038751), for each birth, does the CONTENT that the byte
taint says was copied (which bytes came from where) agree with the
INFLUENCE that a matched single-byte perturbation reveals (which source
bytes, when changed, change the child)? Tabulate the four cells: content
and influence; content without influence (copied but inert); influence
without content (control flow, no copying); neither.

## Why it matters
Taint answers "did bytes move", perturbation answers "did a difference
matter" (raw/E3 s2-3). Their disagreement is itself the phenomenon behind
several program shapes: propagation without content (Aether), function
without content (raw/I3 T12), host credited for its guest. It also feeds
POI-001: a partial-information-decomposition of authorship needs exactly
these per-birth source/target relations.

## Everything you need is in git (no M2 access)
- The T-001 replay: roles/Odysseus/th006/tools/node_check.sh builds a
  clean directory from git and replays r038751 in ~52 s (stdlib, ~145 MB);
  recipe: roles/Odysseus/th006/pack/r038751.recipe.json. The probe
  archaeon/causal_lens/tools_bee/codeprov_replay.py shows how to subclass
  BEE's traced world and read the write provenance (TR._ACC["writes"]).
- BEE's traced VM (origin/bellerophon/coupling-campaign-2026-09-24:
  roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py) and the
  frozen harness (git 16fc6c2a:prometheus/z80atlas/).

## What to do
1. Sample births (e.g. 500, stratified by the B6 location x material table
   in archaeon/causal_lens/out_v02/B6_PROBE_r038751.json). Preregister
   the sample and the thresholds.
2. For each sampled birth, capture the pre-execution state (writer tape,
   window, inputs) during replay; then re-execute that single execution in
   isolation: (i) record taint (source address of every window byte);
   (ii) for each source byte, flip it (matched: same position, a random
   value, and a no-op flip as negative control) and record which child
   bytes change.
3. Build the matrix per birth and in aggregate; break it down by the B6
   table's classes.
4. Positive control: a hand-built birth where a byte is copied but never
   read (content without influence) must land in that cell; and vice versa.

## Boundaries
Read-only on BEE and Archaeon lanes. Do not modify the pack or the TH-006
tools; copy what you need into your output path.
