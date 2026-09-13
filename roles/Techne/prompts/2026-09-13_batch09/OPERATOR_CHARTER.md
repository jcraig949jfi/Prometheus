TECHNE — NEXT ROUND
LOSERS, LOST WORLDS, AND PRESERVATION DEBT

The vault now contains 109 preserved specimens.

Breadth remains available, but the cheap canonical frontier is thinning.

The next round should therefore optimize for:

FAILED / SUPERSEDED MACHINERY
HISTORICAL WORLDS
PRESERVATION COMPLETENESS
UNLOCKING EXISTING SOURCE-ONLY FOSSILS

rather than raw specimen count.

OPENING GATE

Run:

python -m techne.fossils.harvest verify --all

Expected:

109 specimens
109 match
0 differ
0 missing

Any failure outranks acquisition.

PRIORITY 1 — FIX THE SUBMODULE PRESERVATION GAP

The Avida attempt exposed a real defect:

git fossils may preserve the superproject commit while failing to preserve
required submodule bodies.

That is a preservation invariant problem.

Repair the acquisition layer so a fossil using submodules records:

superproject commit
.gitmodules
exact submodule URL
exact submodule commit
nested tree hash
acquisition receipt
preservation status

Do not fetch submodules implicitly or unpinned.

Add positive and negative controls.

Negative control:

omit or alter a required submodule
    ->
preservation/readiness check must fail.

Then re-acquire Avida properly.

Do not modernize it merely to obtain PASS.

PRIORITY 2 — LOSERS

The coverage map says:

only 15 / 109 specimens carry failed/superseded disposition.

This is now the emptiest first-class axis.

Acquire 10-20 specimens whose historical importance includes failure,
replacement, abandonment, inferiority, pathological behavior, or dead-end
design.

Seek different failure reasons:

performance collapse
instability
poor scaling
resource explosion
brittleness
incorrect assumptions
security weakness
ecosystem loss
patent/legal displacement
architectural dead end
superior rival
maintainability failure
numerical failure
concurrency failure

Require evidence for the disposition.

Suitable evidence:

original paper
retrospective
release notes
standards history
benchmark history
project documentation
successor documentation
archived technical discussion

Do NOT let an LLM label a design "bad" merely because it looks obsolete.

PRESERVE THE LOSER IN ITS ORIGINAL WORLD

Where practical acquire:

loser
winning/succeeding rival
shared problem/input

This allows later comparison without Techne deciding why one won.

Especially valuable:

before failure
observed failure
replacement

PRIORITY 3 — PRE-1970 COMPUTATIONAL WORLDS

The coverage map says pre-1970 remains thin.

Deliberately search for machinery from:

1940s
1950s
1960s

Source forms may include:

original source listings
punched-card listings
scanned manuals
reconstructed source with provenance
emulator input decks
historical language distributions
reference tapes/images
faithful scholarly reconstructions

Candidate cultures include:

early Lisp
IPL
SNOBOL
early FORTRAN
ALGOL
early BASIC
assembly systems
early theorem proving
early game programs
symbolic algebra
scheduling
operations research
cybernetics
adaptive systems
early neural models

Faithful reconstruction is legal.

It must be labeled:

FAITHFUL RECONSTRUCTION

not original source.

PRIORITY 4 — BSD TCP AS EXPERIMENTAL DEPTH

The historical BSD world now boots.

Complete TECHNE-69b if tractable.

Goal:

exercise multiple BSD TCP generations under the SAME network pressures.

Target lineage:

4.2 BSD
Tahoe
Reno

Pressure conditions:

clean transfer
constrained bandwidth
packet loss
delayed acknowledgement if feasible
retransmission event

Record raw observations such as:

netstat counters
retransmissions
transfer completion
timing
congestion-related state where exposed

Do NOT interpret which internal mechanism caused the differences.

A successful shared experiment over this lineage may be more valuable than
another twenty isolated fossils.

PRIORITY 5 — UNLOCK EXISTING BLOCKED FOSSILS

Review all:

SOURCE_ONLY
BLOCKED_PLATFORM
NOT_ATTEMPTED
environment-blocked

records.

Prioritize existing fossils whose blocker is now cheap to remove.

Current known targets include:

Avida
SWI-Prolog
Souffle
xv6

Do not chase all of them blindly.

Estimate expected recovery value versus environment cost and proceed in bounded
passes.

PRIORITY 6 — FAILED BEHAVIOR DATASETS

Continue the successful pattern from:

decompressor corruption
Kalman overconfidence
Core War non-transitivity

Create pressure/failure datasets over EXISTING fossils.

Candidate areas:

SAT timeout / structured hardness
parser error recovery
allocator fragmentation
GC pressure
control instability
ECC beyond correction radius
routing under failure
database crash recovery
numerical cancellation
ill-conditioned optimization
malformed symbolic input

The goal is not ranking.

The goal is exposing different behavioral regimes.

PRIORITY 7 — HISTORICAL DISPOSITION FIELD

Improve the coverage map for losers.

Where evidence exists, distinguish:

ACTIVE
SUPERSEDED
ABANDONED
FAILED
LOSING_RIVAL
OBSOLETED_BY_ENVIRONMENT
LEGAL_OR_PATENT_DISPLACED
HISTORICAL_ONLY
UNKNOWN

Keep this factual.

Do not infer disposition merely from project age.

PRIORITY 8 — PRESERVATION DEBT CENSUS

The submodule defect suggests there may be other incomplete bodies.

Audit acquisition types for hidden dependencies:

git submodules
git-lfs
vendored tarballs
generated tables
model/data files
external ROMs
test corpora
downloaded-at-build dependencies
package-manager resolution
nested archives

Classify each fossil as:

SELF_CONTAINED
FULLY_PINNED_EXTERNALS
UNPINNED_EXTERNAL_DEPENDENCY
KNOWN_INCOMPLETE
UNKNOWN

Do not mark a fossil fully preserved solely because its top-level tree hash
matches.

NETWORK-FETCH DEBT

Find recipes that fetch from the network at build/run time.

For each:

identify dependency
pin exact version/content if lawful
hash it
preserve it where appropriate

or explicitly record:

NETWORK_DEPENDENT

The Avida apto failure shows why this matters.

OFF-HOST MIRROR

TECHNE-65 remains urgent.

If an actually independent destination appears:

mirror immediately before further expansion.

If none exists:

report SINGLE_HOST_RISK unchanged.

Do not call another path on the same physical storage a mirror.

BREADTH STILL CONTINUES

Do not stop exploring.

Reserve approximately 20-30% of acquisition effort for genuinely new territory.

Prefer:

absent domain
absent era
absent architecture
absent language culture
absent failure regime

over another easy canonical specimen.

CLASSIFICATION

Continue only the lightweight coverage classification needed to guide harvest.

Useful maps:

era
human domain
language
execution world
pressure
disposition
runnability
preservation completeness
ancestry depth

Do NOT begin behavioral clustering or organ classification.

That remains downstream work.

ROUND SUCCESS

A strong round might add only 10-15 new fossils if it also:

repairs the submodule invariant;
makes Avida complete;
makes BSD TCP experimentally runnable;
materially increases the loser axis;
eliminates several network-dependent recipes;
improves preservation completeness.

Count new evidence, not merely directories.

RETURN

Report:

1. PRESERVATION DEBT
    submodule repair
    external-dependency census
    network-fetch census
    unresolved incomplete bodies
2. LOSERS
    new failed/superseded specimens
    disposition evidence
    loser/winner pairs
    failure regimes
3. HISTORICAL WORLDS
    pre-1970 additions
    faithful reconstructions
    emulators/toolchains
4. UNLOCKS
    Avida
    TCP
    SWI-Prolog
    Souffle
    xv6
    other existing fossils
5. BEHAVIORAL DATASETS
    new pressure/failure datasets over existing fossils
6. COVERAGE
    loser fraction
    pre-1970 depth
    source-only count
    preservation-completeness map
    newly exposed holes
7. VAULT
    opening verify
    closing verify
    body drift
    mirror status

FINAL DIRECTION

THE EASY FOSSILS ARE NOT THE INTERESTING PROBLEM ANYMORE.

DIG WHERE HISTORY BROKE.

DIG WHERE SOFTWARE LOST.

DIG WHERE THE ORIGINAL WORLD HAS DISAPPEARED.

AND BEFORE COLLECTING ANOTHER HUNDRED BODIES,
MAKE SURE THE 109 WE ALREADY HAVE ARE ACTUALLY COMPLETE.
