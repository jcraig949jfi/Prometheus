# Validation and delivery receipt

Date 2026-10-02; host BUCKKEEP; Python 3.13.5. Worktree
C:/Prometheus-worktrees/enceladus-base-role; branch
enceladus/rso-hardening-2026-10-02; base
f4d9e72d9cf72ee11bc3a4f01171154dc8a5c90e.
Linked-worktree guard passed. At execution there were no tracked modifications;
new ignored review files were present. This is not a claim the experiment used
a committed preregistered tree. Staging and final branch delivery follow tests.

## Actual execution

Parent command from reference_harness: `python -B -m unittest discover -v`.
Final recorded run: **28 tests, 0 failures, 0 errors, 0 skips, exit 0**;
runner time 0.032 seconds on this host, not a performance guarantee.
Breakdown: 14 contract, 9 finite-world, 5 source-mutation test methods.
Nested mutant probes and subtests are not additional independent trials.

[Machine-readable receipt](VALIDATION_RESULTS.json) records all test IDs,
five Python source hashes, worktree/base, red/green results and claim ceilings.
It is transcribed from actual parent tool output, not an independently signed
attestation. The final git commit identifies the complete delivered file set.

| Stage | Observed result |
| --- | --- |
| Initial delegated implementation, parent execution | 26 tests passed, exit 0. Delegated session had no runner, so its original NOT RUN handoff was correct. |
| Parent adversarial binding regressions before fix | 2 failures, 0 errors, exit 1. Both invalid evidence graphs incorrectly returned PASS. |
| Focused regressions after fix | 2 passed, exit 0. |
| Full suite after fix | 28 passed, exit 0. |
| Final full suite after strengthening source mutant | 28 passed, exit 0; five semantic mutants killed. |
| Original supplied ChatGPT harness | NOT RUN, BLOCKED_BY_MISSING_ARTIFACT; only five Markdown files supplied. |
| Fable experiments | NOT RERUN; receipt/source provenance inspection only. |
| Native runtime/cross-physics/strong-recursion science | NOT RUN / NOT_VERIFIED / DETECTION_UNQUALIFIED. |

## Escapes found and fixed in our new checker

1. **Whole-graph scope laundering.** Original anchors bound only bytes. Changing
   every node to a different physics left their mutual scope comparisons equal
   and reused the same artifact hashes; the graph falsely passed.
2. **Dependency stripping.** Removing the detector's source dependency left
   its anchored byte payload unchanged; the graph falsely passed. This could
   bypass the intended invalidation path.

Added tests first and observed PASS != FAIL assertions on both. The fix binds
complete immutable expected evidence Nodes externally: ID, eight-axis scope,
predicate, dependencies and artifact ref. The consumer compares those anchors
as well as length/hash. Tests now refuse both alterations as EVIDENCE_BINDING.

The unrelated-invalidation fixture previously reused dependent payloads under
renamed nodes with stripped dependencies. It now uses an actually separate
reset evidence node, not a dependency-erasing clone. This fixes the test's
meaning as well as the implementation. External anchors in unit tests remain
synthetic; a caller who fabricates anchors is outside the trust model.

## Mutation record

Final source faults: missing facet check disabled; external node binding
disabled; repair/cold comparison bypassed; byte digest comparison skipped;
invalidation restricted to direct children. Each unchanged probe passes and
its changed-source probe yields exactly one assertion failure with no errors
or skips. Five implemented, executed and killed; zero survived, equivalent or
blocked in this selected set. No syntax/import crash counts as a kill.

The original internal-scope-only mutant was replaced after external binding
became a second defense: its remaining failure would only change the diagnostic
reason, not falsely admit the whole graph. The final binding mutant witnesses
a false PASS. This is not an estimated scientific false-positive rate.

## Exact finite results

- Uniform one-bit carry: 2/2; no-carry fixed answer: 1/2; flip: 0/2;
  independent uniform donor: 1/2 across all four key/donor pairs.
- Four keys, one/two/four carried states: exact best success 1/4, 1/2, 1.
  Two-state case cross-checks all 256 encoder/decoder pairs.
- Plateau: strict ascent stuck, nondecreasing hits at proposal 2. Valley:
  both greedy cold policies fail within two proposals; unconditional chain
  walk hits at 2, repair from state 1 hits at 1.
- Omitting q from the four-state checkpoint breaks exactly two of four
  two-step traces. A faithful checkpoint can preserve forbidden packets.
- Clean reset preserves allowed state and removes forbidden packet influence;
  display-only reset restores the forbidden bit at the next tick.
- Re-encoding counterexample detects first-coordinate bias. Two encodings
  are not unlike physical implementations.
- Rational updater, flattened program and sign-gradient R0 each solve all
  eight finite tasks. Difference in accuracy against R0: exactly zero.
  No-gradient task output is zero. U swaps/clamps and explicit bypass have
  the expected finite responses. No strong-recursion positive is established.

## Review and validation limits

Research notes supplied scoped documentary audits; parent integrated and
reviewed executable logic. An additional validation-agent request returned no
usable response. Do not count it as an independent review or a passed check.
All tests were developed with the implementation; no held-out constructors,
preregistration, independent authorship, independent custody or native physical
qualification is claimed. No new packages, GPU jobs, deployments or paid runs.

The finite checker checks fixed toy tables, graph consistency and externally
anchored identity; it cannot prove truthful execution, physical channel closure,
resource completeness, holdout isolation, or independent methods. Graph-wide
structural validation fails closed at its first error; strong-recursion refusal
precedes graph evaluation. It does not provide a complete production gate log.

## Package checks and delivery

Executed static precommit pass: exit 0, zero errors; 16 files, 5 Python files,
43 unique link targets, exact 28-test inventory, 6 source hashes and 5 code
hashes verified. Checks covered ASCII, trailing whitespace, local/source/git
links and Python parsing. Final explicit staging check also passed: 17 own
package files, ASCII/whitespace clean, no other staged changes; five index
Python blobs match the receipt hashes. These are LF source bytes as tested
and stored by git; on a CRLF checkout compare the git blobs or LF-normalized
source, not raw CRLF bytes. This source-code convention does NOT normalize
runtime evidence artifacts before integrity checking.
No main merge is authorized; delivery is only to the hardening branch with
remote-tip verification.
The final chat reports the actual commit and final check results; no pre-push
receipt claims successful remote delivery.

## Next validation

Keep and rerun these regression/mutation tests for any checker changes. Add
withheld constructor/attack variants and a separately implemented oracle before
native acceptance. First native test: retained bit, no-carry impostor, clean
reset, reachable forbidden packet and allowed-state twin; separately authorize
owners, absolute budget and stop rules. Strong recursion stays unqualified.