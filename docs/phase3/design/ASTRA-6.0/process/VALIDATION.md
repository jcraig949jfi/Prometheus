# Offline package validation: executed checks, bounded conclusions

## Receipt status, 2026-10-01

**PASS for the executed offline checks below. Scientific qualification: NOT_VERIFIED.**

The delegated writers lacked command-launch access and originally recorded
NOT_RUN, missing concurrent companions, and null manifest hashes. The parent
then executed the tools in the Enceladus linked worktree; all eight required
documents now exist. No installs, live services, remote compute or campaign runs.

| Executed check | Actual final result | Exit code |
|---|---|---:|
| Validator unit suite with Harmonia opt-in | 32 passed, 0 failures/errors/skips; includes two expected-defect tests | 0 |
| Exact finite-law/planning arithmetic suite | 9 passed, 0 failures/errors/skips | 0 |
| Two focused base-role tests plus comms manifest tests | 4 passed | 0 |
| Charter manifest verification | 2 entries, 0 mismatches | 0 |
| Package check plus manifest generation; then read-only verification | PASS, 0 errors in both invocations | 0 |
| Scoped Git whitespace check | No whitespace errors | 0 |

First-run incidents are retained rather than hidden: the original 31-test suite
had one Windows alias-classification failure. Windows abspath stripped a trailing
dot before lexical checking; pre-normalization rejection and an additional
regression fixed it. Both Harmonia probes passed on the first and final runs.
The initial package run rejected the placeholder manifest, as intended; actual
generation replaced it with source and document LF SHA-256 hashes.
A combined shell command passed four tests and verified the charter but exited 1
because Windows PowerShell lacks Get-Date -AsUTC. It was rerun successfully using
`[DateTime]::UtcNow`; the observed UTC clock was 2026-10-01T19:21:31.2368939Z.
Adding this receipt to the manifest allowlist exposed the unquoted PowerShell
expression as a malformed Markdown link definition; inline-code quoting fixed
the documentation. A broad own-role ASCII assertion also failed on the exact
Unicode shared-mandate snapshot; preserve that source rather than transliterate
it. Active role files and the review packet are checked separately for ASCII.

Validation counted 48 requirements/16 groups, six 27-field cards, 24 failure
classes, 56 salvage rows, 25 report sections/10 closing answers, and 1,802 artifact
rows/247 engine-perspective rows. Rulers: 152 records, 146 explicit alias groups.
The original requirement payload and architecture's 201-line prefix match the
freeze; 81 architecture appendix lines record later recommendations. Link totals
are in the machine manifest; bounds/existence checks do not establish citation
semantics. Pattern scans found zero configured secret-pattern matches, not proof
that every possible secret form is absent.

## Implemented check boundary

- Exactly eight mandated Markdown deliverables, plus README, two implementation-plan
  companions, five evidence notes, original process record, validation receipt,
  and review packet. No recursive
  document discovery; this receipt itself is not an input to its own validation.
- 48 unique requirement definitions in 16 numbered groups, three IDs per prefix;
  all explicit `R-...-...` references must resolve to those definitions.
- Six ordered Q1-Q6 cards with the observed 27 unique, nonempty fields each.
- T01-T24 failure headings, C01-C56 exactly once, valid recommendation/axis values,
  and recomputed S/I/total counts reconciled to the decision-summary table.
- Main report sections 1-25 and Q1-Q10 answer headings, each exactly once.
- Inline, full/collapsed reference and defined shortcut Markdown links. Local
  destinations must exist; `#Lstart-Lend`, `#Lstart-end`, and `#Lstart` ranges must
  be well formed, positive, ordered and within the file. Fenced/inline code is
  ignored. This is the observed package syntax, not a full CommonMark parser.
- Remote links are never fetched. Non-line fragments are explicitly counted as
  unchecked: header-anchor validity is not certified. Unknown bare `[text]` is
  treated as prose, since it need not be a shortcut reference.
- Other design trees and `roles/Dionysus` / `roles/Epimetheus` are blocked before
  filesystem traversal, including URL-encoded links. Sensitive-looking paths,
  Windows aliases/alternate streams, symlinks and junctions are also blocked.
  Blocked links are errors, not successful existence checks. A nonexcluded
  repository target outside the package is opened only to count lines, never
  recursively parsed or imported. Individual content reads are capped at 32 MiB.
- Pattern-based secret checks on allowlisted package/intake inputs return counts
  and safe source labels only. Matching values, record bodies, raw destinations,
  Git stderr and exception messages never enter the JSON summary. This heuristic
  is not a proof that all possible secrets are absent.
- `REQUIREMENTS.md` must equal the frozen Git blob after CRLF/CR-to-LF conversion,
  with no trimming, encoding reinterpretation or final-newline rewriting.
  Architecture must retain the original 201-line frozen prefix; appended deltas
  are allowed, changes within that prefix are not.
- Only four fixed read-only Git commands: resolve the supplied freeze/base
  commits, then `git show` the two exact frozen ASTRA paths, with a 20-second
  timeout per command. No log, global diff, grep, checkout, staging or commit.
- Parse every nonblank JSONL line in all four artifact and engine indexes and
  the Tityos ruler inventory. Invalid JSON, nonobject records, duplicate object
  keys and non-JSON numeric constants fail. Expected counts are 528/528/348/398
  artifact records (1,802), 51/46/74/76 engine records (247), and 152 ruler records.
  Resolve `same_instrument_as` as an undirected alias graph when supplied;
  unavailable aliases remain explicitly unavailable, not asserted independent.
- Manifest scope is the 16 explicit required intake files: four reports, eight
  indexes, Tityos taxonomy/inventory and Ixion dependency map/timeline. It records
  their LF SHA-256 hashes, frozen payload hashes, supplied full freeze/base SHAs,
  and package-document snapshot hashes. It does not pretend to hash every seat
  dossier or every source body referenced by an intake record.

The command emits metadata-only JSON and returns 0 only with no check errors;
1 means validation failure (including missing inputs, Git failure or stale
manifest). Argument-usage errors use argparse's exit code 2. Generating a manifest
does not suppress package failures. No script edits Markdown source documents.
Readers must rerun after concurrent companion/document edits; the manifest is a
per-read snapshot, not a transactional repository lock.

**Actual scientific qualification remains NOT_VERIFIED even if every check passes.**
These checks do not reproduce historical campaigns, qualify rulers, establish
developmental reasoning, or authorize the proposed MVP gates.

## Tests and expected-defect boundary

The executed suite contains 32 unittest methods: 30 validator fixtures and two
opt-in Harmonia tests, all passing. The separate arithmetic suite has nine tests.
Fixtures cover positive/missing packages, malformed ranges, bad requirements,
duplicate cards/classes/rows, decision arithmetic, bad JSONL, alias chains, frozen
content changes, safe path exclusions, secret-safe diagnostics, Git failure and
the manifest CLI round trip. Fixtures use `TemporaryDirectory` outside the
workspace, clean up only their own temporary directory, and mock Git reads.

The optional tests read only the inspected first 284 lines of
`roles/Harmonia/qualification/h0h5/qualification_rules.py`, select five arithmetic
functions through AST, and literal-evaluate the `_T` table. They do not import
the Harmonia package or run any campaign. An inert namedtuple supplies the
Estimate result container; no scientific decision method executes.

Their deliberate expected-defect assertions are:

- Nonconstant 12-block input yields identical interval endpoints for
  `n_primary=2` and `n_primary=3`, while alpha labels differ (.025 versus .05/3).
- `t_crit(11, .05)` returns **2.179**, the same lookup value as df=12.

A pass means the defects were reproduced in that inspected
source, **not** that the statistics are correct. A future corrected implementation
should make these tests fail and require the defect documentation to be reviewed.
The parent executed these two probes. No historical verdict impact or complete
Harmonia qualification follows from their passing expected-defect assertions.

The nine arithmetic tests use Fraction to enumerate all 32 independent and 16
correlated W3-R/W3b-R support cases. Each sums to probability 1. Bayes-optimal
query decisions differ across laws, majority accuracy is 27/32, bought-cue
disagreement is 3/8, and the low-price primary headroom is 0.05 normalized.
Normal/binomial calculations, 240/1,920 Q5 trajectory counts, conditional zero-hit
bound, tariff hand arithmetic and live document CPU/energy/token tables pass.
These are analytical checks, not native A0 execution, achieved detection power,
independent scientific replication or historical campaign reproduction.

Final editorial reconciliation also removed a propagated drafting error: eight
of 32 bridge-search slots are an allocation, not an 8/32 recovery threshold.
Path-specific stochastic recovery gates remain to be frozen before calibration.

## Reproduction commands

Run from `C:/Prometheus-worktrees/enceladus-base-role` with Python 3.10+ and Git.
The `-B` flag prevents bytecode writes. Manifest generation writes only the owned
JSON receipt; regenerate after any allowlisted document changes, then verify.

<augment_code_snippet mode="EXCERPT">
````powershell
python -B docs/phase3/design/ASTRA-6.0/tools/test_validate_package.py --harmonia-defect -v
python -B docs/phase3/design/ASTRA-6.0/tools/test_design_arithmetic.py -v
python -B docs/phase3/design/ASTRA-6.0/tools/validate_package.py --write-manifest
python -B docs/phase3/design/ASTRA-6.0/tools/validate_package.py
````
</augment_code_snippet>

The focused pytest run disabled plugin autoload, conftest discovery and cache;
it selected test_base_role_files_exist_and_are_pure_ascii and
test_this_test_runs_from_a_linked_worktree_and_journals_are_committable_here from
archaeon/tests/test_base_role.py, plus comms/tests/test_manifest.py. The full
base-role suite was deliberately not run: several tests read every seat's entry
or prompt files, violating this task's architect-independence boundary.
Keep writing/updating and rerunning these small tests after edits. Later native
transition, reset, leak, oracle, statistical, intervention and admission-route
tests are still required before any claim-bearing implementation campaign.