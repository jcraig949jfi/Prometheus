# Forensic question -> instrument map (generated; do not edit)

Source: build_forensic_map.py over TOOLS.jsonl.  A row appears as an answerer only if the registry's
admissibility ladder says so.  DIRECT = evidentiary_scope answers the question for the named object class;
PARTIAL = necessary sub-question or restricted class.  Candidates are NOT answerers.

| id | question | verdict | scope | direct | partial | candidates |
|---|---|---|---|---|---|---|
| FQ-01 | Was the test tautological? | ANSWERABLE_RESTRICTED | RESTRICTED: statistics, graders and gates as functions; not pipeline-level tautology | 3 | 2 | 2 |
| FQ-02 | Was the positive control capable of passing? | PARTIAL | PARTIAL: presence of a positive control and one pinned example; no planted-effect generator for an arbitrary claim class | 0 | 4 | 3 |
| FQ-03 | Was the negative control capable of failing? | ANSWERABLE_RESTRICTED | RESTRICTED: statistics and classifiers; not LLM-graded claims | 6 | 0 | 1 |
| FQ-04 | Did the producer change between claim and evaluation? | ANSWERABLE_RESTRICTED | RESTRICTED: graves that fingerprinted their producer (record-limited) | 5 | 1 | 3 |
| FQ-05 | Did the judge have access to answer-bearing information? | ANSWERABLE_RESTRICTED | RESTRICTED: exact-equality leaks only | 2 | 1 | 2 |
| FQ-06 | Was the search weak or the domain empty? | ANSWERABLE_RESTRICTED | RESTRICTED: graves with a declared class | 2 | 1 | 4 |
| FQ-07 | Was the gate vacuous? | ANSWERABLE | GENERAL | 3 | 3 | 2 |
| FQ-08 | Was the consumer absent? | ANSWERABLE_RESTRICTED | RESTRICTED: static consumption; runtime consumption only where logged | 1 | 3 | 0 |
| FQ-09 | Was the claimed evidence actually pipeline state? | ANSWERABLE | GENERAL | 5 | 1 | 2 |
| FQ-10 | Was the comparator measuring the intended quantity? | ANSWERABLE_RESTRICTED | RESTRICTED: degeneracy, costume and scale; not semantic mismatch | 2 | 5 | 2 |
| FQ-11 | Did dependency / configuration state invalidate the test? | ANSWERABLE_RESTRICTED | RESTRICTED: store identity and cwd; not package / interpreter environment | 2 | 3 | 4 |
| FQ-12 | Can the historical result be reproduced from frozen artifacts? | ANSWERABLE_RESTRICTED | RESTRICTED: graves with an admissible replay harness (Pollux, Archaeon, sigma_kernel, prometheus_math ledgers, Techne canon) | 6 | 2 | 6 |
| FQ-13 | Can the claimed failure survive an alternative admissible instrument? | ANSWERABLE_RESTRICTED | RESTRICTED: statistical and boolean claims; not LLM-judged claims | 9 | 0 | 5 |
| FQ-14 | Was the reported result selected from a larger unreported set (forking paths / file drawer)? | PARTIAL | PARTIAL: denominator fragments only | 0 | 3 | 0 |
| FQ-15 | Was the claim written before or after the evidence it cites existed (temporal order)? | PARTIAL | PARTIAL: commit order and one declared-bound gate shape | 0 | 2 | 0 |
| FQ-16 | Did the test have the power to see the effect claimed (sample size, p floor)? | PARTIAL | PARTIAL: p floors only, no power | 0 | 2 | 0 |

## FQ-01 Was the test tautological?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: statistics, graders and gates as functions; not pipeline-level tautology).  Instrument must: an instrument that can show a statistic, grader or gate cannot respond to its inputs (identity, constant, or same-computation)

- NT-047 DIRECT [EVIDENCE] instrument-null probe: does the statistic respond to its inputs at all (tautological / nondeterministic / unmeasurable)
- NT-056 DIRECT [EVIDENCE] literal-verdict lint: functions whose every return is the same verdict cannot discriminate
- NT-040 DIRECT [EVIDENCE] instrument contract: a meter is certified only if it responds to a negative
- NT-041 PARTIAL [EVIDENCE] degenerate audit: B1 degeneracy of a measure (conflating vs refusing)
- NT-033 PARTIAL [EVIDENCE] EvCA C3 null check: were two 'independent' runs the same computation
- candidates (not answerers): NT-073 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-062 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only))
- limits: covers statistics, graders and gates as FUNCTIONS; a test that is tautological at the pipeline level (evaluation set identical to the construction set) is caught only if the artifacts are fingerprinted (see FQ-04)

## FQ-02 Was the positive control capable of passing?

Verdict: **PARTIAL** (scope: PARTIAL: presence of a positive control and one pinned example; no planted-effect generator for an arbitrary claim class).  Instrument must: an instrument that plants an effect of the class the claim asserts and shows the claimed instrument detects it at a rate not pinned at alpha

- NT-034 PARTIAL [EVIDENCE] measurement guard: a passing, type-matched control had to exist before the value was read
- NT-049 PARTIAL [EVIDENCE_WITH_CAVEAT] resampling null: its PERTURBATION control is the worked example of a positive control pinned at alpha (DISP-001) _(caveat: FRANK-004 kill condition (2) fires on synthetic data before any grave is read; upper-tail direction or a different statistic is the well-posed read)_
- NT-047 PARTIAL [EVIDENCE] instrument-null probe: whether the statistic can respond at all (necessary, not sufficient)
- NT-015 PARTIAL [EVIDENCE] canon R11 calibration: declared-vs-reported completeness for forecasters only
- candidates (not answerers): NT-065 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-014 (NEEDS_VALIDATION, blocked_by STATUS NEEDS_VALIDATION); NT-069 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only))
- limits: no admissible instrument PLANTS an effect of an arbitrary claim class; the admissible cells only verify that some positive control existed or that one specific control is pinned.  A planted-shift generator keyed by claim class is the missing organ (CR-001 descendant requirement)

## FQ-03 Was the negative control capable of failing?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: statistics and classifiers; not LLM-graded claims).  Instrument must: a null / constant / costume / chance-floor reference the claimed instrument must beat

- NT-031 DIRECT [EVIDENCE_WITH_CAVEAT] Nemesis cheatlib: chance floor and constant responder the tool must beat _(caveat: None answers are not filtered)_
- NT-028 DIRECT [EVIDENCE] baseline costume: does the claim only beat the marginal majority
- NT-045 DIRECT [EVIDENCE] control certifier + defect battery: every named defect shape must be caught
- NT-040 DIRECT [EVIDENCE] instrument contract: negative required for certification
- NT-013 DIRECT [EVIDENCE] modal-collapse synthetic: chance floor for that claim class
- NT-047 DIRECT [EVIDENCE] synthetic-null probe: independent samples must not read as signal
- candidates (not answerers): NT-061 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only))
- limits: answerable for statistics and classifiers; for LLM-graded claims the constant/costume responder exists (NT-031) but the grader itself is UNTRUSTED (NT-001), so the negative control is only as good as the alternative judge (FQ-13)

## FQ-04 Did the producer change between claim and evaluation?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: graves that fingerprinted their producer (record-limited)).  Instrument must: fingerprints of code and inputs at claim time and at evaluation time, and a reader that compares them

- NT-051 DIRECT [EVIDENCE] git-history census: when an instrument existed and what its bytes were at any commit
- NT-038 DIRECT [EVIDENCE] Vivarium spec hash: identity of an experiment spec, key-order invariant
- NT-007 DIRECT [EVIDENCE_WITH_CAVEAT] comms.manifest: do the files beside a manifest still match it _(caveat: laundering undetected and subdirectories uncovered -- use adapters/manifest_verify.py which reports uncovered files and the manifest's own hash)_
- NT-053 DIRECT [EVIDENCE] manifest verify with coverage: uncovered files, self-hash
- NT-033 DIRECT [EVIDENCE] EvCA C3: transform digest identity of two runs
- NT-016 PARTIAL [EVIDENCE] H3 replay input-fingerprinting stream manifest (Archaeon only)
- candidates (not answerers): NT-067 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-070 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-081 (NEEDS_VALIDATION, blocked_by EXECUTES)
- limits: record-limited, not instrument-limited: the question is answerable only where the grave fingerprinted its producer; where it did not, the map says UNANSWERABLE_RECORD, never 'unchanged'

## FQ-05 Did the judge have access to answer-bearing information?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: exact-equality leaks only).  Instrument must: a leak detector over what the judge could read at grade time versus the answer

- NT-030 DIRECT [EVIDENCE_WITH_CAVEAT] ladder leakage audit: exact-equality leak fields with chance floor _(caveat: exact-equality scope; transformed leaks are invisible)_
- NT-021 DIRECT [EVIDENCE] Vivarium library-leak: a component equal to the task answer
- NT-031 PARTIAL [EVIDENCE_WITH_CAVEAT] chance floor the judge's score must beat _(caveat: None answers are not filtered)_
- candidates (not answerers): NT-035 (NEEDS_VALIDATION, blocked_by STATUS NEEDS_VALIDATION); NT-075 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only))
- limits: EXACT-equality leaks only.  Derived, paraphrased or partial leakage (an answer recoverable by a 3-line reader that is not byte-equal, memory 2026-08-12) has no admissible detector

## FQ-06 Was the search weak or the domain empty?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: graves with a declared class).  Instrument must: a B1 (degenerate domain) vs B2 (insufficient search) discriminator given a declared class

- NT-002 DIRECT [EVIDENCE] coverage diagnostic: expressiveness ceiling (B2) vs degenerate domain (B1) for a declared class
- NT-041 DIRECT [EVIDENCE] degenerate audit: B1 degeneracy of a measure
- NT-029 PARTIAL [EVIDENCE] kill-scheme information audit: do kill labels carry coordinate information
- candidates (not answerers): NT-059 (NEEDS_VALIDATION, blocked_by EXECUTES); NT-078 (NEEDS_VALIDATION, blocked_by EXECUTES); NT-084 (NEEDS_DEPENDENCY, blocked_by CONTROLLED (author tests only)); NT-080 (NEEDS_VALIDATION, blocked_by EXECUTES)
- limits: requires the grave to have DECLARED its class; a grave with no class declaration gets B1/B2 UNDECIDABLE, which is itself a finding

## FQ-07 Was the gate vacuous?

Verdict: **ANSWERABLE** (scope: GENERAL).  Instrument must: evidence the gate could and did refuse something

- NT-056 DIRECT [EVIDENCE] literal-verdict lint: a gate that returns one verdict unconditionally
- NT-034 DIRECT [EVIDENCE] measurement guard: gate refuses when control absent or type-mismatched
- NT-019 DIRECT [EVIDENCE] Atalanta null_bound: bound had to be declared before emissions were counted
- NT-004 PARTIAL [EVIDENCE] Erebos residue gate replayed on ledger rows: did it ever refuse
- NT-050 PARTIAL [EVIDENCE] ledger census verdict cardinality: a gate column that never said NO
- NT-036 PARTIAL [EVIDENCE] dead-field detector: a gate column never populated
- candidates (not answerers): NT-085 (NEEDS_DEPENDENCY, blocked_by CONTROLLED (author tests only)); NT-063 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only))
- limits: static vacuity (code shape) and ledger vacuity (never refused) are both covered; a gate that refused only cases it was never shown (selection upstream) is FQ-09

## FQ-08 Was the consumer absent?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: static consumption; runtime consumption only where logged).  Instrument must: who imported, read or acted on the instrument's output

- NT-052 DIRECT [EVIDENCE] consumer trace: who imports / mentions a path (never piped through head)
- NT-032 PARTIAL [EVIDENCE] Pronoia productive-liveness: were artifacts consumed downstream (L-class)
- NT-050 PARTIAL [EVIDENCE] ledger census: whether a consumer's ledger ever carried the producer's ids
- NT-054 PARTIAL [EVIDENCE_WITH_CAVEAT] read-only Postgres probe: did the canonical store ever receive the rows _(caveat: guard validated offline; no live query executed)_
- limits: static consumption is answerable; RUNTIME consumption (the output was read by a running process) is answerable only where the consumer logged it or wrote to the store

## FQ-09 Was the claimed evidence actually pipeline state?

Verdict: **ANSWERABLE** (scope: GENERAL).  Instrument must: a reader that grades artifacts rather than stdout, and detects heartbeats / status columns / dead fields masquerading as results

- NT-032 DIRECT [EVIDENCE] productive-liveness L0-L5 from artifacts, not stdout
- NT-036 DIRECT [EVIDENCE] dead-field detector
- NT-050 DIRECT [EVIDENCE] ledger census: rows, dead / partial fields, verdict cardinality
- NT-044 DIRECT [EVIDENCE] Charon C1/C2: unfingerprinted pool and transport-failure residue rulings
- NT-042 DIRECT [EVIDENCE] Eos intake gate: the claim must name a real referent in the tree
- NT-043 PARTIAL [EVIDENCE] environment identity: the store read is the store claimed
- candidates (not answerers): NT-089 (NEEDS_VALIDATION, blocked_by IMPORTS); NT-074 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only))
- limits: answerable

## FQ-10 Was the comparator measuring the intended quantity?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: degeneracy, costume and scale; not semantic mismatch).  Instrument must: a reader of the claim's DECLARED quantity checked against what the comparator computes

- NT-028 DIRECT [EVIDENCE] baseline costume: the comparator only beats the marginal majority
- NT-024 DIRECT [EVIDENCE] block-shuffle null: dependence beyond what the stratifier explains (the 'explained by scale' clause)
- NT-047 PARTIAL [EVIDENCE] instrument-null: comparator can respond
- NT-040 PARTIAL [EVIDENCE] instrument contract
- NT-041 PARTIAL [EVIDENCE] degenerate audit
- NT-039 PARTIAL [EVIDENCE] divergence decomposition: how much of a divergence is attributable below the ceiling
- NT-006 PARTIAL [EVIDENCE] two-sample KS: distribution difference (not location/scale-specific)
- candidates (not answerers): NT-073 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-062 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only))
- limits: degeneracy, identity and costume are detectable; SEMANTIC mismatch (the code computes X, the claim says Y, both non-degenerate) has no instrument -- it needs a declared-quantity record and a reader of it

## FQ-11 Did dependency / configuration state invalidate the test?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: store identity and cwd; not package / interpreter environment).  Instrument must: the environment (packages, env vars, store identity, cwd convention) at claim time versus at evaluation time

- NT-043 DIRECT [EVIDENCE] comms.identity: canonical store or a fork, fails closed
- NT-054 DIRECT [EVIDENCE_WITH_CAVEAT] read-only Postgres probe with identity check _(caveat: guard validated offline; no live query executed)_
- NT-055 PARTIAL [EVIDENCE] sigma_kernel fresh-interpreter runner: historical cwd convention reproduced
- NT-051 PARTIAL [EVIDENCE] git-history census: which bytes were present
- NT-038 PARTIAL [EVIDENCE] spec hash identity
- candidates (not answerers): NT-071 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-064 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-086 (NEEDS_DEPENDENCY, blocked_by IMPORTS); NT-020 (NEEDS_DEPENDENCY, blocked_by IMPORTS)
- limits: store identity and cwd are covered; PACKAGE / interpreter environment at claim time was almost never recorded (FRANKENSTEIN_XREF 'missing_here' is per-host), so this is mostly UNANSWERABLE_RECORD

## FQ-12 Can the historical result be reproduced from frozen artifacts?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: graves with an admissible replay harness (Pollux, Archaeon, sigma_kernel, prometheus_math ledgers, Techne canon)).  Instrument must: a replay harness for THAT grave's producer over its preserved inputs, with fingerprints

- NT-048 DIRECT [EVIDENCE] Pollux statistic replay (unchanged daemon logic)
- NT-016 DIRECT [EVIDENCE] Archaeon H3 replay from preserved births
- NT-055 DIRECT [EVIDENCE] sigma_kernel modules re-run as historically run
- NT-027 DIRECT [EVIDENCE] Archaeon fossil inference: what two fossils jointly imply
- NT-005 DIRECT [EVIDENCE] reasoning_quality_emit: contested tasks re-derived from a preserved ledger
- NT-015 DIRECT [EVIDENCE] canon R11: declared vs reported
- NT-007 PARTIAL [EVIDENCE_WITH_CAVEAT] manifest verification as a precondition _(caveat: laundering undetected and subdirectories uncovered -- use adapters/manifest_verify.py which reports uncovered files and the manifest's own hash)_
- NT-053 PARTIAL [EVIDENCE] manifest coverage as a precondition
- candidates (not answerers): NT-046 (NEEDS_VALIDATION, blocked_by STATUS NEEDS_VALIDATION); NT-023 (NEEDS_ADAPTER, blocked_by STATUS NEEDS_ADAPTER); NT-069 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-057 (NEEDS_VALIDATION, blocked_by STATUS NEEDS_VALIDATION); NT-093 (HISTORICAL_ONLY, blocked_by PATH_EXISTS); NT-091 (HISTORICAL_ONLY, blocked_by PATH_EXISTS)
- limits: PER-GRAVE column: admissible replay exists for Pollux, Archaeon H3, sigma_kernel, prometheus_math ledgers and Techne canon.  For every other grave in the 48-agent roster the cell is EMPTY -- there is no replay harness and, for daemons whose state/ was gitignored (FRANK-003), no bytes to replay

## FQ-13 Can the claimed failure survive an alternative admissible instrument?

Verdict: **ANSWERABLE_RESTRICTED** (scope: RESTRICTED: statistical and boolean claims; not LLM-judged claims).  Instrument must: a second, independently validated instrument for the same claim class

- NT-006 DIRECT [EVIDENCE] two-sample KS
- NT-008 DIRECT [EVIDENCE] permutation null
- NT-025 DIRECT [EVIDENCE] bootstrap / matched-null / permutation with correct p floor
- NT-024 DIRECT [EVIDENCE] block-shuffle null
- NT-049 DIRECT [EVIDENCE_WITH_CAVEAT] random-subset resampling null + KS (caveat: lower tail is uninformative, DISP-001) _(caveat: FRANK-004 kill condition (2) fires on synthetic data before any grave is read; upper-tail direction or a different statistic is the well-posed read)_
- NT-037 DIRECT [EVIDENCE] BOCPD changepoint
- NT-012 DIRECT [EVIDENCE] truth-table oracle, the reference for NT-011
- NT-011 DIRECT [EVIDENCE_WITH_CAVEAT] z3 oracle checked against NT-012: two oracles for boolean claims _(caveat: ledger-appending side effect; use the redirect adapter)_
- NT-026 DIRECT [EVIDENCE] kill-resurrection audit: would a killed claim survive re-evaluation
- candidates (not answerers): NT-060 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-061 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-066 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-068 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only)); NT-076 (NEEDS_VALIDATION, blocked_by CONTROLLED (author tests only))
- limits: answerable for statistical and boolean claims.  For LLM-JUDGED claims there is NO admissible alternative judge: NT-001 is UNTRUSTED, NT-082 needs an absent package, NT-083 needs a fine-tuned verifier; a failure graded by an LLM cannot currently be cross-examined

## FQ-14 Was the reported result selected from a larger unreported set (forking paths / file drawer)?

Verdict: **PARTIAL** (scope: PARTIAL: denominator fragments only).  Instrument must: an enumerator of runs, seeds and variants that existed versus those reported

- NT-015 PARTIAL [EVIDENCE] canon R11: completeness of reporting for declared forecasts only
- NT-051 PARTIAL [EVIDENCE] git-history census: run directories and result files that existed at each commit
- NT-050 PARTIAL [EVIDENCE] ledger census: rows present vs rows cited
- limits: no instrument compares the set of runs that EXISTED with the set REPORTED; every admissible cell is a denominator fragment

## FQ-15 Was the claim written before or after the evidence it cites existed (temporal order)?

Verdict: **PARTIAL** (scope: PARTIAL: commit order and one declared-bound gate shape).  Instrument must: timestamp / commit ordering of claim text versus artifact bytes

- NT-019 PARTIAL [EVIDENCE] Atalanta null_bound: bound declared before emissions counted (one gate shape)
- NT-051 PARTIAL [EVIDENCE] git-history census gives commit order of files, not of claims inside files
- limits: commit order is a lower bound on write order; claims edited in place have no admissible ordering instrument

## FQ-16 Did the test have the power to see the effect claimed (sample size, p floor)?

Verdict: **PARTIAL** (scope: PARTIAL: p floors only, no power).  Instrument must: a power / p-floor calculator against the claimed effect size

- NT-025 PARTIAL [EVIDENCE] resampling p-values with the correct floor (PRF-2)
- NT-013 PARTIAL [EVIDENCE] chance floor for modal-collapse claims
- limits: p floors are covered; POWER against a claimed effect size has no instrument

## Summary

- verdicts: {'ANSWERABLE': 2, 'ANSWERABLE_RESTRICTED': 10, 'PARTIAL': 4, 'EMPTY': 0}
- admissible tools mapped: 44 / 45
- admissible tools answering no question: NT-003
