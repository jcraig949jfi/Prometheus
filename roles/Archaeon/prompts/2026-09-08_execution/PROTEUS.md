PROTEUS — EXECUTION ORDER 2026-09-08 (from the operator)

Baseline: archaeon/v0 at 5191c3383. Your requests:
roles/Proteus/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md (later sections
supersede). Tests per package: archaeon/docs/expansion/WORK_PACKAGES.md.
Branch B is Tier 3, but nothing below depends on anyone else, so start now
and report when done; Vivarium wraps your library when it lands.

DO NOW
1. WP-B1. Expose the foundry VM's evaluation as a PURE LIBRARY:
   (program, immutable specification or input set, step_budget, seed) ->
   outputs, halting/budget status, steps, bounded trace information, and
   the FIRST FAILING INPUT under a declared ordering. Specify whether budget
   exhaustion can be a counterexample or is a distinct status. No registry
   reads, no fossil reads, no file writes. Tests B1-a..d: tiny hand-authored
   programs with exact first counterexample; all 64 specimens agree with the
   arena path on the same inputs, with world-blindness reported and no
   specimen counted as a responsive agent by default; zero/min/exhausted
   budgets, invalid opcodes, absent outputs, missing specifications have
   defined results; replay and semantic opcode relabelling hold; trace
   truncation is explicit and cannot change execution or the witness.
2. PR-ID (D-7). Canonical manifests for programs, rule tables and genomes
   with representation and semantic version; organism_ref =
   sha256(canonical manifest) generalised from your organism_id rule;
   identity separate from evaluation environment and from any
   behaviour-equivalence claim; identity-bearing metadata declared. Tests
   PR-ID-a/b/c. Ship a shared fixture of two equal-score artifacts with
   different observable behaviour for Archaeon's WP-X8.

NOT ASKED: breeding, mutation, naming an organism interesting, any player
reading fossils. WP-B4 (the wider input channel) is yours with Harmonia and
gates only claims about that population; schedule it after B1.

REPORT FORMAT: item ID; revisions; commands run; expected vs observed;
fixture hashes; unresolved limits; next permitted action.
