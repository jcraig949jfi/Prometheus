# Herakles backlog, H0-H5 lanes

Seeded 2026-09-10. Schema per `roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md`.
Status: OPEN / BLOCKED / DONE. Owner is me unless named otherwise.
Ordered by lane, not by priority; priority is the operator's.

---

## LIT -- recovery and lineages

**L-1 OPEN. Juille and Pollack 1998 coevolved rule.** Highest-value single
recovery: a different SEARCH PROCESS, not another run of the same one.
Needs the GP-1998 proceedings. Bar: transcribe, execute, reproduce the
published figure under a named criterion.
BLOCKED ON: fetch access.

**L-2 OPEN. Capcarrere, Sipper, Tomassini 1996, PRL 77(24):4969-4971.** A
radius-1 density classifier, executable in `eca_rule_eval_v1` the day it is
recovered. Carries a DIFFERENT output convention and therefore needs its own
criterion declared beside the existing three. BLOCKED ON: fetch access.

**L-3 OPEN. Andre, Bennett, Koza 1996 GP rule.** A different REPRESENTATION.
Proc. First Annual Conf. on Genetic Programming, pages 3-11.
BLOCKED ON: fetch access.

**L-4 OPEN. Wolz and de Oliveira 2008.** Named in the field map, no citation
recovered. First step is finding the citation, not the table.

**L-5 OPEN. Resolve the Das/Mitchell/Crutchfield 1994-95 provenance.** Are
`par`, `particle1`, `particle2` the specific rules of those papers or siblings
from other runs? Today this is AMBIGUOUS and calling them recovered would be a
provenance claim I cannot support.

**L-6 OPEN. Every recoverable evolved-CA / GA artifact 1990-2005, with
status.** The full inventory L-1..L-5 are the first entries of. Seed from the
reference lists of the thirteen PDFs already held; those are primary sources
we own and have not exhausted.

**L-7 OPEN. A synchronising rule.** The task is implemented and EVERY organism
we hold scores 0.0. An empty cell with an instrument already built.

**L-8 OPEN. Particle catalogue (Hordijk, Crutchfield, Mitchell) as an
executable fixture.** Particles and domains are the mechanism the EvCA line
actually discovered; we hold the rules and not the analysis that reads them.

**L-9 OPEN. Avida 2003 thread in `ergon/avida2003/` as organisms.** 2041 files
of artifacts, configs and an unbuilt Avida 2.2 tarball of the wrong version.
Status today: a dossier, NOT a route. Deciding this is worth an hour before it
is worth a week.

**L-10 OPEN. Kouvaris 2017 thread in `ergon/kouvaris2017/`.** Cited-by graph
present. Same first question as L-9: dossier or route.

## CRIT -- criteria and their conventions

**C-1 OPEN. One table of every CA criterion and its published-figure
convention.** Four now exist: `at_T`, `stable`, `cellwise_majority_match`,
`synchronisation`. Only `at_T` is comparable to a published P. That sentence
needs to live in one place before a fifth is added.

**C-2 OPEN. A positive control for the synchronisation task that SOLVES it.**
`blinker_rule_table` proves the detector fires; it does not solve the task from
arbitrary initial conditions. Until something does, a score of 0.0 cannot be
separated from an unreachable target. Depends on L-7.

**C-3 OPEN. Attainable range and eligible count for every criterion, in the
same table as C-1.** `at_T` gives random tables the single point {0};
`cellwise_majority_match` gives them [0.4939, 0.5099]. That contrast is the
argument for having more than one criterion and it should be stated once.

## H5 -- encodings and scope

**H5-1 OPEN. Trajectory-class equivalence, for when the path matters.** Both
published maps are TERMINAL classes: two rules with different intermediate
trajectories and the same endpoint are one class. If a decoder's merit depends
on the path, terminal classes are the wrong equivalence.

**H5-2 OPEN. Larger rings and their class ceilings.** Measured: a 7-ring
saturates at 236 by T=9. N=9 gives 232 at T=8 and N=11 gives 238. The ceiling
as a function of N is not mapped, and enumeration cost is 2^N.

**H5-3 BLOCKED. The 12-bit genome decoder round trip.** Producer-side and
Archaeon's; my evaluator consumes only a resolved rule number. Listed so the
boundary stays visible.

**H5-4 OPEN. eca_rule_eval_v1 library-side handover.** Vivarium registered the
kind (aa3365df6). What a thin wrapper needs from me is written down; the
library is pure and side-effect free at import. Not blocking anything today.

## H2 -- streaming

**H2-1 BLOCKED ON THE OPERATOR. Issue ca_stream_v2 under D-18.** Plan frozen
and unissued at `herakles/ca_stream/CA_STREAM_V2_PLAN.md`. One command on the
day.

**H2-2 OPEN. Rule search, beta.** After H2-1 and not before: a search with no
baseline to compare against measures nothing.

**H2-3 OPEN. Wider injection, alternative 2 of the obstruction.** Untested. Its
risk is computable in advance: at k near half the lattice the injection IS the
answer to the density task, so the bound on k should be computed before k is
chosen.

**H2-4 OPEN. A non-linear readout, declared.** The shift register has perfect
memory and fails temporal XOR because XOR is not linear in the stored bits. A
low CA score on XOR therefore cannot be attributed to the substrate under the
current readout. Changing the readout class changes what every H2 number
means, so it is a new kind, not an edit.

## C3 / cross-seat

**X-1 OPEN. C1-e reference at other lattice sizes.** The C3-2 comparison used
N=149 only. C1-e also has 599 and 999 and C3-2 did not exercise them.

**X-2 OPEN. Re-run C1-e's particle2 cell if the original EvEmComp bytes are
ever recovered.** The only surviving suspect is transcription and it is
untestable without them. HELD until then.

**X-3 OPEN. The F-20 recording gap.** The live null rows carry no
`ic_transformed` flag, so `c3_null_check` correctly returns INDETERMINATE on
them as recorded. Filed to Vivarium; listed here because my checker's verdict
depends on it.

**X-4 OPEN. Second-lineage C3-hist arm.** The whole point of L-1..L-4: a
historical arm with one lineage in it is a historical arm with one lineage in
it. No cross-lineage claim is available until at least one lands.
