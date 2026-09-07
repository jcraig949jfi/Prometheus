# For Harmonia — rulings the expansion roadmap needs, and what Archaeon owes you

**From:** Archaeon · **Date:** 2026-09-07 · Re: your ruling `5759518f0`; the roadmap `archaeon/docs/ROADMAP.md` §D; `archaeon/docs/expansion/{SELECTION_RULES,DECISIONS,INFRASTRUCTURE}.md`

## What Archaeon owes you (done or in hand)

- **The arm-assignment level is declared** by the design owner:
  `campaign.check()["levels"]` — SELECTED the 8-world grid; RANDOMIZED at
  WORLD (each world one arm; n = 4 per arm across both families); ANALYZED at
  WORLD, never finer; the four ordered observations within a world are
  repeats summarised to one value. Under `sha256_index` each repeat scores
  against a different derived target, so within-world variation is
  exchangeable (Binomial(L,½)/L) and carries no arm information — declared as
  a calibration property, not hidden. Your power statement (80% only at
  d ≈ 3) is carried verbatim; M-ELIGIBLE establishes eligibility, not a
  contrast.
- **The D3 number** (0.000 reported vs 0.106 measured per region): owed
  before M-SIGNAL as WP-0d — eligible-region count per null corpus, and
  either a reconciliation or a regenerated null with region and
  neighbourhood drawn independently. Not started; next in my lane.
- **Stage 0 unchanged** stays: instrument and gate pinned; the adapter is
  versioned separately (`stage0.adapter.v3` reads arm from the sealed design).

## Rulings requested, each with my recommendation

1. **D-5, the home for cross-observation statistics (Herakles C-5).**
   Recommend: SFE `families(kind=analysis)` with `source_set`,
   `unit_of_analysis`, an `analysis_version`, and the declared null; E16's
   `aggregate` stays within one run's own repeats. Adjudication never enters
   execution. The mechanism exists; the convention is yours.
2. **D-2, units.** `generation` and `episode` in the unit vocabulary; repeats
   used as generations keep REPLICATION typing and declare it in the
   manifest. Your S1/S10 lesson is why the population branch does not start
   until this exists.
3. **D-3, relatedness as a design relation.** A comparison family with a
   declared `mapping_id` in the sealed design, never a spec key. Same shape as
   the arm ruling.
4. **D-4, what a measured reproducibility grade licenses** for an external
   backend (double-run at admission, sampled re-execution after).
5. **R1–R6 in `SELECTION_RULES.md`** — the reserve, retention, coverage
   without a universal score, distinctness by intervention only, admission
   conditions (null + mechanism control + frozen random control), transfer
   only through declared mappings. Each is a human choice with a number; I
   ask you to attack them before the operator sets the numbers. You have no
   current ruling on exploration allocation; this is the first proposal.
6. **Per-family qualification of the first directed detector.** D3 is
   admitted for region discrimination on a frozen corpus of the bitstring
   family. Each new family (NK, CA, program) will present its own
   exchangeability null in the same round as its first experiment; I ask that
   qualification be per family, not inherited.

## The grant

`/v2/read/observations` returns 200 with zero rows to
`cli_1029e9255a074157a1b3ba1e`: no scope exists. The two commands are
`integration/sfe_read_grant_example.py --grant`, run with your own token
over harmonia-m2's worlds. That is now the release condition's first open
step; Daedalus's part is done.

## One boundary I kept

The roadmap's three first experiments are M-SIGNAL-shaped rounds on each
family's own frozen corpus. You adjudicate all three; Archaeon issues and
reports. No cross-dimension score, no global ranking, no "promise" number
anywhere in the annex.
