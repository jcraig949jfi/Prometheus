# E-002 handoff test -- what a fresh worker needed (Artemis, ubu002, 2026-09-27)

Observed, not designed. The worker had the verbatim instruction and Git only, with no briefing.

## Recovered from Git without help
The question, the task table, the thread (TH-001), contract v0.2/v0.3 text and code, the operator rulings (verbatim), the regression
report and review packet, the frozen adapters, the preserved outputs (out_v02), the PTE rows and engine, and the exact probe recipe
(regress_v02.pte_arch with its seed). That was enough to reproduce the preserved PTE result exactly on a different OS, and then to go
beyond it.

## Missing, and why it mattered
1. **The candidate criterion was named, never stated.** "ILL_POSED by mechanism" appears as one sentence (regression s4) and one
   reviewer question (Q2). T-007 had to formalise it: exchangeability, the distinct-HU clause, and the missing-declaration -> NI rule.
   A different worker could formalise it differently.
2. **No acceptance test for "meaningful".** The tasks say "invents continuity" but give no test for it. M1-M3 were supplied by the
   worker (T-007). The conclusions depend on them.
3. **The synthetic fixtures carry no operator declaration**, so the candidate cannot be applied to them without adding information
   (T-008).
4. **The preserved outputs dropped what the claims rest on.** PTE_V02/PTE_ARCH_V02 keep class labels but not parent hashes, masks or
   child signatures. The self-cross finding and the ceiling finding were only visible after replay. The replay was cheap here; it
   would not be for a campaign-scale specimen.
5. **Unlike E-001, the E-002 tasks had no inputs/command/expected-result recipe.** Recovered by reading regress_v02.py.
6. **Environment facts were missing.**
   - PTE needs numpy + torch, and ubu002 had neither. E-001's "stdlib only" was true for BEE/NPE, not for PTE.
   - regress_v02.py hard-codes Windows evidence paths and writes into out_v02/, so running it as-is would overwrite frozen outputs.
     It was imported around, not run.
   - A directory-wide pytest run needs Postgres.

## Portable
Everything E-002 needed. All inputs are in Git; verification against the preserved result is in-repo. Every step is < 2 min and
< 400 MB on a 4-core, 7 GB node. The torch CPU output was float-identical across Windows (M2) and Linux (ubu002) for all 50
reproduced genomes.

## Host- or evidence-bound
Only the breadth of F2 (thin margins under privileged operators). The full Archaeon block-13 events and BEE's per-birth margins live
on M2 (C:\Prometheus-data\evidence\portability01_2026-09-26\). The B1 adjudication did not need them.

## Git transition
Commits are on branch artemis/e002-2026-09-27 in a ubu002 worktree. Pushing was not attempted without operator say-so. The pilot
record says nodes cannot push; whether ubu002 can push was not tested.
