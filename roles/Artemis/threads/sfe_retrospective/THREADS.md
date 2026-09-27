# Open threads found by the SFE retrospective

Artemis, 2026-09-27. REPORT.md s7. Each is a question the evidence
raised and could not answer from the repository and the store alone.
None is launched; the operator decides. Ordered by what is at risk if
it waits. Pure ASCII.

Format per thread: the question; why the evidence says it matters; what
would answer it; who holds the evidence; the smallest first step.

-----------------------------------------------------------------------

## T1 -- SFE disposition and archive custody  (risk: evidence loss)

Question: what is SFE now, and are its two ledgers safe?

Why: every label disagrees with the property (REPORT s0.7). The M1
ledger eng_8a37a5d3 (89,939 experiments, the H0-H5 corpus, 86,296 rows
from Vivarium) sits on SKULLPORT D:, which now belongs to Nestor. The M2
production ledger eng_906356f7 (2,070 experiments incl. CMP1-3) is at
C:\Prometheus-data\sfe on SPECTREX5, with a D: rollback copy. Neither is
in git or the shared store. Harmonia HARM-13/16/18 and Archaeon ARCH-47
are blocked on reading the M1 corpus from M2 (c09c9891e). PEW backups
on M2 are UNKNOWN after 2026-09-17.

What would answer it: host evidence on M1 and M2 (file presence, size,
mtime, sha256 of both ledgers and the newest PEW dump; which process
holds 8811/8377; watchdog task states: B_alive s10), then an explicit
operator disposition (resume / freeze as reference / retire with
migration).

Holds the evidence: Daedalus (silent since 09-18), Mnemosyne (PEW,
silent since 09-23), the operator; host access on SKULLPORT and
SPECTREX5.

First step: a read-only custody census on both hosts. It moves nothing
and settles whether either ledger is a sole copy.

## T2 -- Provenance as an embeddable contract, not a service

Question: can SFE's three guarantees (prediction before observation,
loser-keeping selection families, executed-vs-requested attestation) be
delivered as a small receipt format an engine writes locally and the
shared store collects, with no request-path service?

Why: they are the one capability SFE has that no post-SFE engine has
(REPORT s2.1). The service form cost 98% of each row's time (b57dd8c0e)
and was abandoned; the guarantees were abandoned with it. Best-of-N and
configuration drift appear among the ecology's forensic reversals (Ares
gate C, BEE P1). The operator already ruled the SFE ledger belongs in
the shared Postgres (6dc37ef5d).

What would answer it: specify the minimum contract from SFE's own tests
(SCIENTIFIC_PROVENANCE.md, T11, FAMILY_EXTENT_DIVERGENCE), then
retro-apply it to one finished campaign from a new engine and check
whether it would have exposed anything the seat's forensics later found,
or found anything they missed. A null result is informative: it would
say the guarantees are not worth carrying.

Holds the evidence: SFE docs and tests (in repo); a closed campaign with
complete receipts (Crius C2 or Ares cycle 2 are small and closed).

First step: a one-page contract derived from SFE's tests, reviewed by
whoever owns provenance (Daedalus/Harmonia/Archaeon, the operator to
name).

## T3 -- Where the ecology's evidence actually lives

Question: for each active engine, is the evidence behind its reported
results reachable by another seat -- in git, in the canonical store, or
only on the host that ran it?

Why: after 09-18 PEW receives nothing; Atlas indexes 5 of ~19 engines
(harvester regexes miss the Z80 worlds, e.g.
atlas/harvest/archaeon_campaigns.py:59); raw evidence is recorded on
off-repo paths (BEE 2.2 GB under C:/Users/James/...; the 72 h
CAMPAIGN_PACKET.md not in git; Archaeon envgate "off-machine copy
BLOCKED"; Cosmos runs under C:/Users/James/cosmos_runs). The North Star
requires residue to "remain available to future search"; the ecology's
fossil record is fragmented.

What would answer it: a census per engine of result -> evidence path ->
reachable-from (git / store / host-only) -> size -> replayable?; then
compare with Atlas's view.

Holds the evidence: the repo (reports cite their paths) plus each
seat's host for existence checks.

First step: the repo-only half of the census, runnable from ubu002 now.

## T4 -- Host coupling and placement

Question: which engines must run where, and what does co-location cost?

Why: code independence did not produce runtime independence. On 09-24,
48 pool children from Archaeon's ENVGATE-02 assays drove M2 to 98%
commit and hung SFE and PEW; the Vivarium dead-man could not alert
because comms lived on the store it was escalating (8c5a1a23b). Ensorain
already carries a rule "no launch on M2 while Bellerophon's campaign
runs". Most engines are "merely located" (notes/P_portability.md) and
could move; the program has not made placement decisions, M3/M4/ubu
hosts are lightly used.

What would answer it: per engine, the inherent requirement (GPU, RAM,
OS) vs the current host; a measured peak RSS and CPU for one standard
run of each; the list of standing processes per host.

Holds the evidence: seat STATUS files and host process tables.

First step: collect declared peak resources from each engine's receipts
(repo-only), then ask seats to fill gaps.

## T5 -- A cross-engine failure catalogue

Question: can the ecology's forensic reversals be catalogued by failure
class so a new engine checks for them before launch rather than after?

Why: the same classes recur engine after engine -- stale comparator
(Aether), best-of-N (Ares), author-planted law (CWE, WTP), window that
misses the event (PTE), identity vs heredity (NPE), detector-only flags
(BEE), mutation read before fidelity (NPE) -- each found alone, often
after a headline (REPORT s3.3). The engines document their own failures
well; nothing collects them. Nestor's twelve methodology lessons
(FINDINGS s D) are the nearest existing seed.

What would answer it: extract each reversal into (class, detection
method, cost of late detection, pre-launch test that would have caught
it); measure whether classes recur after being documented elsewhere.

Holds the evidence: seat FINDINGS/forensics/review packets (in repo).

First step: the extraction, repo-only; it fits ubu002.

## T6 -- The Z80 triplication as a planned triangulation

Question: should the three independent Z80 worlds (Nestor, Bellerophon,
Archaeon) be treated as one deliberate cross-implementation experiment,
or consolidated?

Why: they were built from one 2026-09-19 directive in one week with no
shared code (95fff9111). That duplication is only worth its cost if the
same assay runs on all three: agreement is a real cross-implementation
result, divergence locates an implementation artefact. PORTABILITY-01
already ran the causal lens on two of them (BEE, NPE) with domain limits.

What would answer it: one preregistered assay (e.g. the causal lens's
host-mediated reproduction test) run on all three, with the
disagreement budget declared before rows.

Holds the evidence: Archaeon (lens), Nestor, Bellerophon.

First step: an inventory of which of the three persists enough per-birth
provenance to run the lens without abstaining.
