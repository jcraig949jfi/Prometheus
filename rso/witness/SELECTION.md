# Native witness runtime selection (Palamedes, 2026-10-07; operator directive s6)

Selected: Ares, world W15 (W4 as the no-interrupt reference), per rso/witness/CANDIDATES.md C1 and DESIGN_DRAFT.md.
Fallback: Ensorain (C2); third: Z80 Atlas (C3).

Why: the runtime states its own channel split (W15 erases activations at unobservable interrupts; plastic weights
survive), so the observatory imposes no allowed/forbidden ontology (BX6); its two native boundaries (B1 interrupt,
B2 episode reset) map onto retention/CHANNEL and ERASE/PRESERVE; the oracle r stays in the world; it is seeded,
CPU-only and cheap (0.08 CPU-s per 64 x 16 smoke); across B1 the carrier must be continuous plastic weights, not
the slice001 register.

Why reversible: no shared code depends on the choice. The adapter is a client module (rso/witness/), the shared
machinery stays rso/binding + the evidence plane; switching to the fallback costs one adapter and its fire cases.
Revisit if P-CAL fails on W15 or the frozen subject turns out to be unusable for reasons visible before witness
outcomes (e.g. it fails P-OBS determinism).

Decisions on DESIGN_DRAFT s8 (reversible until the witness preregistration is frozen):
  1. Stochastic ruler (P-RET statistic, alpha, n, INDETERMINATE band) and P-CAL: specified by Argus (C-009-T014),
     with the evidence-plane sign-off, before preregistration.
  2. S-LEAK is in the WITNESS campaign's own fire set (native boundary B2), not a C-009 fire case: C-009 stays
     runtime-agnostic.
  3. One subject, evolved once on W4 under a registered config, digest committed before any witness episode. The
     W15-evolved secondary arm is dropped for this first witness (narrowness, directive s5).

Gate: the witness campaign opens only if C-009 closes CC1-CC4 (directive s6). Until then only preparation: adapter
code and plumbing tests (determinism, arm wrappers applied, receipts, binding rows) on random/hand-wired organisms;
no subject evolution, no witness predicate, and no retention or accuracy statistic computed for ANY arm or control
(P-CAL's numbers are outcomes too).
