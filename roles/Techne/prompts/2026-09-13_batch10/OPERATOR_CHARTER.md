TECHNE — BATCH 10
TRUST THE VAULT BEFORE EXPANDING IT

Batch 09 accepted.

The important result is not merely that the vault grew 109 -> 117.

You demonstrated a new failure class:

SOURCE PRESENT != FOSSIL PRESERVED

Avida's failure was caused by an absent pinned submodule body.
The 109-census independently found the same preservation defect in
lru-cache-goldsborough.

That makes preservation closure part of the instrument.

Batch 10 is therefore NOT another breadth harvest.

Its purpose is:

MAKE THE VAULT'S CLAIMS TRUSTWORTHY,
THEN EXTRACT BEHAVIOR FROM LOSER/WINNER PAIRS.

Do not optimize specimen count.

P1 — FIX THE PIN-EVIDENCE INSTRUMENT

Batch 09 discovered that pin evidence actually lives in:

hashes.artifacts

while batch scripts overwrite:

source_origin

and thereby drop sha256 / commit_resolved information.

This defect caused the first census to report 59 unpinned fossils when
the true count was 18.

Fix the instrument at the source.

Preregister the intended semantics before changing it.

Add controls capable of detecting the exact failure that produced 59.

Regenerate the preservation census.

Report BEFORE and AFTER.

Do not silently replace the old erroneous result.
Preserve it as an instrument failure.

P2 — REMOVE HARVEST SHADOW CODE

harvest.py contains duplicate definitions of:

acquire
_shell
_clip
_expect_ok
verify

with the later definitions silently winning.

Treat this as instrument debt.

Determine whether the pairs are actually equivalent BEFORE deleting or
consolidating anything.

Diff behavior, not merely text.

If they differ, characterize the difference and determine which behavior
existing receipts were actually produced under.

Then establish ONE authoritative implementation of each operation.

Add a regression/control capable of detecting accidental duplicate
top-level definitions in this instrument in the future.

Do not opportunistically redesign harvest.py.

P3 — EVIDENCE-GATE THE LEGACY LOSERS

Batch 09 established:

21 / 117 non-ACTIVE specimens

but only:

6

are presently backed by the new evidence-gated disposition machinery.

The remaining 15 legacy tag-based cases have state UNKNOWN and are not
citation-backed.

Do not grandfather them.

For each legacy disposition:

find primary or authoritative evidence;
record what that evidence actually supports;
migrate only claims supported by evidence.

If the evidence does not support the old label:

CHANGE THE LABEL.

If sufficient evidence cannot be found:

UNKNOWN.

The objective is not to preserve the loser count.

The objective is to discover how much of the old loser count survives
evidentiary scrutiny.

Report:

LEGACY CLAIMS ENTERED
CLAIMS CONFIRMED
CLAIMS RECLASSIFIED
CLAIMS DEMOTED TO UNKNOWN

and the resulting evidence-backed loser fraction.

P4 — TURN SUPERSESSION INTO BEHAVIOR

Batch 09 acquired:

LINPACK vs LAPACK
EISPACK vs LAPACK

but the measurable behavioral core remains incomplete because
lapack-reference is SOURCE_ONLY.

Attempt to make the reference LAPACK specimen runnable without modifying
its preserved body.

If successful, construct the smallest controlled comparison that exposes
the pressure documented by the LAPACK Users' Guide:

same mathematical problem
different computational organization
measurable consequence

For LINPACK/LAPACK prioritize memory-access / blocking behavior rather than
a vanity wall-clock benchmark.

For EISPACK/LAPACK find the nearest equally defensible measurable pressure.

Preserve algorithmic and environmental confounds explicitly.

A result showing NO meaningful difference is valid.

Do not tune matrix sizes after observing the result merely to make LAPACK
win.

Preregister sizes/regimes or derive them mechanically.

The target artifact is not:

LAPACK faster.

It is:

documented supersession pressure
    ->
executable paired fossils
    ->
controlled behavioral coordinate.

P5 — ENVIRONMENTAL OBSOLESCENCE

Preserve Batch 09's MD5 specimen exactly.

It is unusually valuable:

identical source bytes
identical source sha256
builds in both worlds
runs in both worlds
exits 0 in both worlds
correct in one
wrong in the other

Do not patch the fossil.

Generalize the INSTRUMENT, not the specimen.

Ask whether the vault contains other fossils whose correctness depends on
environmental properties such as:

word width
signedness
endianness
integer overflow semantics
alignment
filesystem assumptions
clock representation
compiler behavior
protocol/environment assumptions

This is a bounded census first.

Do not manufacture examples.

If natural specimens exist, test them using preserved bodies and explicit
world changes.

If none exist, report NONE.

P6 — PRE-1970 DEPTH

Only after P1-P5 are landed or explicitly blocked:

resume historical acquisition with a strong bias toward PRE-1970
executable bodies.

Batch 09 made zero progress here.

Do not count ancestry.

A 1976 implementation of a 1971 translation of earlier work is still a
1976 body.

Prefer specimens where we can preserve BOTH:

the organism

and:

the world needed to execute it.

Especially valuable are loser/winner or ancestor/descendant pairs where
the historical pressure can eventually be measured.

Do not lower provenance standards merely to populate a decade.

TCP remains separate.

Do NOT start TECHNE-69b in this batch unless everything above closes
unexpectedly early and there is enough budget for a properly controlled
round.

P7 — PRESERVATION CLOSURE

Re-run the full preservation census after all work.

The categories must remain explicit:

SELF_CONTAINED
FULLY_PINNED_EXTERNALS
UNPINNED_EXTERNAL_DEPENDENCY
KNOWN_INCOMPLETE

Do not call a network recipe preserved merely because it happened to
succeed today.

For every external dependency ask:

CAN THIS EXACT BODY BE RECONSTRUCTED WITHOUT TRUSTING MOVING HEAD?

Do not attempt to repair all 17 remaining network-dependent recipes in
this batch.

Rank them by scientific/forensic value and preservation risk.

Return the next preservation queue.

NON-NEGOTIABLES

Preserved bodies remain immutable.

Experiments run on disposable copies.

No LLM judgment substitutes for executable controls.

No citation-free loser labels.

No specimen-count optimization.

No post-hoc tuning to make historical winners win.

No same-disk copy called a mirror.

Do not repair historical software merely to make it run unless the repair
is explicitly part of a separate reconstruction artifact.

A failure to reproduce is evidence.

An environment-dependent wrong answer is evidence.

A supposed loser whose historical disposition does not survive citation
review is evidence.

A pair whose documented pressure cannot be reproduced is evidence.

CLOSEOUT

Return:

1. corrected preservation census;
2. pin-instrument regression;
3. harvest duplicate-definition disposition;
4. evidence audit of all 15 legacy loser claims;
5. resulting evidence-backed loser fraction;
6. LINPACK/LAPACK and EISPACK/LAPACK behavioral datasets, or exact blockers;
7. environmental-assumption census and any new natural specimens;
8. any genuine pre-1970 bodies acquired;
9. ranked preservation-debt queue for the remaining 17 network recipes;
10. opening/closing vault verification and body-drift count.

Commit the preregistration/charter before experimental changes where
appropriate.

Land completed work on the Prometheus repository and current Techne
branch according to the working contract.

Push and verify every claimed carrier as an ancestor of origin/main.

Report deviations.

Failure is a result.

Do not make the vault bigger until you have made its claims harder to lie
about.
