# Phase 3: comparative hardening review

Date: 2026-10-02. Author: Enceladus, ASTRA-6.0 report lane, BUCKKEEP.
Verdict: **REPAIR the contracts; BUILD bounded qualification fixtures;
REFRAME strong recursion as DETECTION_UNQUALIFIED.**

This is a response to the operator's request to compare Fable 5.1 with the
prior ASTRA review, incorporate the supplied ChatGPT 5.6 meta-analysis, and
strengthen both the design and test plan. Original sources are not overwritten.
The directory retains the incoming review-round name rso-v0.2; the two revised
specifications are v0.3 to distinguish them from the supplied v0.2 documents.

## Read first

1. [Comparison and decisions](reports/Comparison_and_decisions.md): what each
   approach earns, corrections to our own claims, and unresolved disagreements.
2. [Hardened design v0.3](HARDENED_DESIGN_v0.3.md): implementable contracts,
   claim-specific qualification, native reset and causal requirements.
3. [Hardened test plan v0.3](HARDENED_TEST_PLAN_v0.3.md): exact fixtures,
   mutation tests, dependency gates, budgets and binding stop rules.
4. [New finite reference harness](reference_harness/README.md): executable
   bounded examples, not the missing original harness or a native observatory.
5. [Validation receipt](VALIDATION.md) and
   [self-contained review packet](REVIEW_PACKET_2026-10-02.md).

## Evidence classes: do not collapse them

| Class | What is in this package |
| --- | --- |
| Source-reported execution | Fable's stored runs and later corrections; not rerun here. |
| Locally checked provenance | Pinned git objects, script hashes, receipts, source-file inventory. |
| New local execution | Exact finite controls and software/mutation tests; see validation. |
| Proposed implementation | v0.3 native contracts, runtime qualifications, W1 and confirmation. |
| Missing input | Original ChatGPT harness: BLOCKED_BY_MISSING_ARTIFACT. |
| Scientific authority | No native cross-physics or strong-recursion qualification; NOT_VERIFIED. |

The supplied folder contains exactly five Markdown files and no harness
directory. Its design line 288 says a minimal harness is implemented; this
delivery claim is not supported by the supplied artifacts. We did not run
discovery in an empty directory or call a zero-test result a pass. The NEW
reference harness is separately named and has a nonzero test inventory.

## Provenance

- Worktree: C:/Prometheus-worktrees/enceladus-base-role.
- Branch: enceladus/rso-hardening-2026-10-02.
- Base SHA: f4d9e72d9cf72ee11bc3a4f01171154dc8a5c90e.
- Linked-worktree guard passed: git-dir differs from git-common-dir.
- Initial tracked tree/index clean. New review files are ignored by the
  repository's broad docs rule until explicitly force-added; clean tracked
  status before staging therefore does not mean the new files do not exist.
- No main merge, source-package edits, package installation, cloud resources,
  paid experiments, scientific campaign, or changes to other seats.
- Evidence Wiki read failed earlier with ModuleNotFoundError. No wiki evidence
  imported and no submission claimed; this package is the local provenance.

### Source index

| ID | Source and pin |
| --- | --- |
| A | ASTRA prior report at base SHA, docs/phase3/reviews/ASTRA-6.0/rso-v0.1/reports/Wind tunnel charter review.md; SHA-256 696a0b6e5cf5209edabc44a6d905e5317c4a38928f3bdf430350e7e8fa4df85b |
| F | Fable review and counterfeit directory at 5d397dfd73f7cbcb834b9207549bff3187db4902, docs/phase3/review/FABLE-5.1/ |
| D | C:/Prometheus_Phase3/01_HARDENING_DESIGN_v0.2.md; 9258 bytes; SHA-256 abc1f5722c81b8a1470d736866a16404f398561c0eceaebbb8f9c3b4dfe97987 |
| H | C:/Prometheus_Phase3/02_TEST_HARNESS_SPEC.md; 3895 bytes; SHA-256 4366b31f6f15a91713239bc2c70e5b66a76331270824c3b985ca41256d3da18c |
| P | C:/Prometheus_Phase3/03_ARCHITECTURE_PORTFOLIO_v0.2.md; 2563 bytes; SHA-256 fd3e1c1c58b45784d2741bc21ed34cc91ca23dd398cfdde3639ed8312e5df513 |
| S | C:/Prometheus_Phase3/05_90_DAY_HARDENING_PLAN.md; 2623 bytes; SHA-256 448a27f80e133da57e0d009f1aab37934f553e9ff0326c46bbdf1bfb707a6513 |
| C | C:/Prometheus_Phase3/06_NEXT_REVIEW_CHARTER.md; 1186 bytes; SHA-256 b296830b4adc21f796c3f7f02afed7215fa0de45a986e3b096f0abd846c1d041 |

Hashes identify inspected bytes, not author identity, truthful execution or
preregistration. Fable script/preregistration/receipt details and line-level
citation keys are in the comparison note. We did not reproduce its information
certificate derivation or claim independent replication of its toy experiments.

### Supporting research, with assignment-local limitations preserved

- [Fable comparison](research_notes/Wind%20tunnel%20design%20hardening/fable_comparison.md)
- [Design audit](research_notes/Wind%20tunnel%20design%20hardening/design_audit.md)
- [Test-plan audit](research_notes/Wind%20tunnel%20design%20hardening/test_plan_audit.md)

These notes were written before the new implementation; their statements
"no tests run" describe those notes-only assignments. The validation receipt
records subsequent parent execution. Where notes disagree, the two v0.3
specifications make the final decisions: no blanket exact-bound ceiling for
named empirical comparisons, and no retained percentage budget without an
absolute resource authorization. We preserve disagreements instead of counting
agreement among authors as evidence.