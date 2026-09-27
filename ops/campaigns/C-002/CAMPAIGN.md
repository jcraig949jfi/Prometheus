# C-002 -- Aether research block (2026-09-27)

Thread: TH-007. Owner: Aether (BUCKKEEP, Aether[buckkeep-5c60d0f5]). Opened 2026-09-27 under the operator's research-block
directive (roles/Aether/prompts/2026-09-27_research_block/, verbatim, manifest-verified). Aether is the SECOND test bed of the
ops/ shape after C-001; it is a test bed, not a control plane (directive). Same lightweight shape as C-001: Markdown records,
Task and Attempt rows, no schema engine, no scheduler.

Purpose: sharpen the Aether physics search (TH-007) and, while doing it, test whether Aether work units
(law + seed + origin batch + arm -> result) are genuinely portable, and what a known-answer lane and an open-science lane each
reveal about the Campaign / Experiment / Task / Attempt model.

Constraints: CPU first; no GPU spend on a law until it earns it; RunPod only as a disposable executor or for platform work; no
worker GitHub credentials added; the orchestrating seat commits on behalf of executors.

| Experiment | Question | State |
|---|---|---|
| E-003 | Is the propagation assay's exact causal-generation argument sound? (Block A) | see E-003 |
| E-004 | What did rcv actually teach beyond "received -> fires once"? (Block B) | see E-004 |
| E-005 | Do locality conclusions depend on the observation horizon? (Block C) | see E-005 |
| E-006 | Do combinations of understood mechanisms create new causal behaviour? fwd as content-transport control (Blocks D, E) | see E-006 |
| E-007 | Known-answer lane: does the unit machinery dispatch, duplicate, verify and complete correctly? (Block G) | see E-007 |

Task numbering is campaign-wide (as C-001). Portable-Task record, as C-001: code refs (pinned commit + LF-normalised sha256 of
every imported module), inputs (canonical parameters + sha256; the unit id is derived from them), a host-independent command
(`python Aether/observatory/aeth03_unit.py ...`), resources (wall, peak RSS, CPUs), expected result hash where one exists, where
verification runs, output destination, cleanup rule.

## Pilot findings

(Appended as they occur. Only friction that actually happened is recorded.)
