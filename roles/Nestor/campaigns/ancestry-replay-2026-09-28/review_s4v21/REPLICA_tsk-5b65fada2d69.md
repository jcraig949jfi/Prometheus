**Verdict: DOES NOT CONFORM.** There is one blocking finding: the code's pass/fail rule for the floors is not the spec's rule. Every K_R1 tally and point estimate reproduces exactly from the committed inputs.

**How this was checked:** Python was denied in this session, so I recomputed by pulling fields out of the committed JSONL with search and tallying by hand. My counts match addendum 3's invariants (171 unwritten, 757 written, 735 ENTITY-MOVE loci), and the K_DONOR numbers match too. I did **not** re-run the bootstrap confidence intervals (CIs); I only checked they are plausible. The per-simulation numbers needed to re-run them are in the review file.

## Findings

**B1 — BLOCKING: the floor verdict ignores the point estimate** (`s4v2.py:133-140`, `:216`; docstring `:22-24`)
- **Spec:** C4.4 and addendum 3 ruling 2 say to judge each class on the point estimate against the floor, and to mark it MARGINAL if the 95% CI straddles the floor.
- **Code:** `verdict()` never uses the point estimate. It returns PASS if the CI is wholly passing, FAIL if wholly failing, and otherwise MARGINAL. So MARGINAL replaces the decision instead of qualifying it.
- **Effect:** K_R1 "other" flip coverage is 48/168 = 0.286 with CI [0.127, 0.653]. The correct result is **FAIL (marked MARGINAL)**; s4v2 and the 88b9d0a13 commit message say only "MARGINAL".
- **Engine-level outcome is unchanged**, because "self" fails outright (0.321, CI [0.139, 0.488]).
- **Fix:** output the point-estimate pass/fail and a separate flag for "CI straddles the floor".

**S1 — SHOULD-FIX: the completeness universe drops the persisted flags** (`s4v2.py:91-94` vs frozen `interventions.py:302-305`)
- `s4_run`'s completeness test (R5) also randomises the `fz`/`fc` flags on each side; s4v2 leaves them out.
- 3 of the 6 sampled births have persisted registers and are affected: s04/257, s08B/256 and s08B/259 (84 vs 80 tested items per locus).
- A leak through the flags would go unmeasured.

**S2 — SHOULD-FIX: the leak share is counted per draw, but R5 counts per byte** (`:111-114`, `:207-209`)
- Counting per draw dilutes the numerator by up to 4× (K = 4).
- It makes no difference here because there are 0 leaks.

**Notes**
- **N1:** The docstring claims "identical … seeds as s4_run". The selected subset is identical (6 of 29 births), but the random seed is new (`S4V2CA|…`, `:88`).
- **N2:** Weaknesses in the bootstrap:
  - It silently drops resamples with a zero denominator.
  - A class with one simulation (TIED) gets a degenerate CI but still receives a gate verdict.
- **N3:** K_R1 checks ties before "none", so a non-ENTITY majority performer with a tied store_by would come out TIED. This never occurs in the data.
- **N4:** NO_MATERIAL counts only kind "E" loci as ENTITY-labelled. Only kinds E and C occur, so there is no effect.
- **N5:** 22 "self" loci count as rule-identified with zero usable dependence draws. That is a literal reading of R1, and s4v2 reports the count.
- **N6:** s4v2 does not hash-check the births files, which supply store_by for the class key. I checked by hand: all 11 match `births_sha256` in the index.

## Checklist
1. **identified** = ENTITY MOVE, prefix flip not FAILED, and dependence changes == 0: **OK.**
2. **Coverage denominator** = loci meeting R1 conditions 1 and 3: **OK.**
3. **K_R1:** matches ruling 3; NO_MATERIAL and TIED are handled: **OK** (edge cases N3, N4).
4. **Q8c None** is never counted as 0: **OK.**
5. **Floors and CI:** floors, clustering and seed are correct, but **the verdict rule is non-conforming (B1).**
6. **Completeness applicability:** the subset and the "applicable" definition are correct, but the universe (S1), unit (S2) and seed text (N1) are not.
7. **Units:** 9 simulations and 29 births, 5 duplicates excluded; a missing index entry exits with REFUSED: **OK.**
8. **Reproduce:** every K_R1 total matches exactly (CIs not re-run).
9. **Frozen files:** `interventions.py`, `run_production.py` and `z8shadow.py` match TRACER_FREEZE v4; `s4_run.py` is still 68779d3e. The s4v2 commits touch only `s4v2.py` and the S4V2 outputs: **OK.**

## Recomputed K_R1 numbers

| class | births / sims | MOVE loci | rule-identified | CONFIRMED | FAILED | coverage | leaks / applicable draws (all draws) |
|---|---|---|---|---|---|---|---|
| self | 19 / 8 | 515 | 496 | 159 | 0 | 0.3206 | 0 / 12964 (13656) |
| other | 8 / 5 | 188 | 168 | 48 | 0 | 0.2857 | 0 / 2366 (3144) |
| TIED | 1 / 1 | 32 | 32 | 8 | 0 | 0.2500 | 0 / 2360 (2416) |
| NO_MATERIAL | 1 / 1 | 0 | – | – | – | not gated | not sampled |

- **"other" births:** s04/256, s04/258, s06A/256, s08A/256, s08B/256, s08B/262, s08B/263, s10/256.
- **TIED:** s04/257 (performers split 16/16).
- **NO_MATERIAL:** s09/256 (all written loci are COMPUTED).

Under the conforming rule, flip coverage is FAIL in every gated class ("other" marked MARGINAL). FAILED share and completeness leak share PASS in every class.

Files are in `/home/jcraig/fabric-work/worker.ubu001/attempts/att-0e8528760bb0/out/`:
- `REVIEW_s4v2_conformance.md` — the full review, including the per-simulation numbers and a per-birth performer/store_by table.
- `hashes.py` — a helper script left over; it never ran because Python was blocked.