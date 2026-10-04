# V2-B TEST-1 result -- provenance qualification and first content-rung readings

Thread: TH-P2B-AETHER-V2B, cycle 1, TEST window 1 (opened 2026-10-04T15:37Z). Attempt 1.
Preregistration: Aether/V2B/TEST-1/PREREGISTRATION.md (frozen at 190a17e33, before any run). Code 9770203e6.
Reduction: `python Aether/observatory/aeth_prov_reduce.py Aether/V2B/TEST-1/attempts` -> REDUCTION.json.

## Results by rule

| item | rung | value | rule | **class** |
|---|---|---|---|---|
| Primary: fwd positive control | P3 (P0 for the observatory) | fwd P3_far 0.125 (32/256); rcv 0.0117; v1 0 | >= max(0.05, 2 x rcv) AND > v1 | **QUALIFIED -> MECHANISM_SUPPORTED (instrument)** |
| S1: rcv_add composition | P5 | 0.0078 (2/256); add 0, rcv 0 | SUPPORTED >= 0.05; NO_EFFECT <= 1/256 | **PARTIAL** |
| S2: rcv_str far content | P3 | 0.0078 (2/256) vs bar max(0.05, 2 x 0.0117) | below the bar | **NO_EFFECT** (activity without far content) |

Per law (256 origins each, horizon +400, FAR = 3, DEEP = 5):

| law | P3_far | P4_transformed | P5_composed | P6_deep | alive |
|---|---|---|---|---|---|
| v1 | 0 | 0 | 0 | 0.016 | 0.926 |
| rcv | 0.012 | 0 | 0 | 0.016 | 0.816 |
| **fwd** (calibration law) | **0.125** | 0 | 0 | 0.145 | 0.758 |
| add | 0.004 | **0.945** | 0 | **0.945** | 1.000 |
| rcv_add | 0.023 | **0.918** | 0.008 | **0.898** | 1.000 |
| rcv_str | 0.008 | 0 | 0 | 0.031 | 0.813 |
| rcv_adr (E-011 lesion) | 0.012 | 0.586 | 0 | 0.578 | 0.887 |

## Interpretation (at its width)

- **The instrument works where the old one did not.** The XOR content signature failed this exact positive control
  (E-P1). prov0 sees fwd carry content three or more sites, ten times rcv's rate, on fresh seeds. From now on, content
  nulls can constrain the programme (directive: "no negative result about content transport should constrain the
  programme until that defect is repaired").
- **fwd is a calibration law.** Its code says "forward the received byte". Its P3 is an instrument qualification, not a
  discovery.
- **Content in the current laws does not travel; it transforms in place.**
  - add-family laws keep an origin's ancestry alive through many rewrites, with the value changing (P4 and P6
    around 0.9), but almost always at or next to the origin.
  - rcv_add's super-additive ACTIVITY propagation (E-006/E-009) is not mirrored by far CONTENT (P3_far 0.023).
  - rcv_str carries no content far (S2 NO_EFFECT), in line with the E-006 cause probe and E-010/E-012.
- **Composition is rare.** rcv_add composed two tracked lineages for 2/256 origins (PARTIAL). The n=64 pilot's 6/64
  did not hold up at full size and on fresh seeds. Note that "composed" here counts only TRACKED lineages: an ADD
  that combines a tracked origin with an untracked value is transformation, not composition, under this ruler (a
  limit; see the review questions).
- **E-011 corroborated from a second instrument.** rcv_adr (relay writes replace) cuts rcv_add's persistent
  transformed ancestry from 0.92 to about 0.59. Compounding relay writes carry much of the persistence, and
  replacement removes it only partly. This is the same partial picture E-011's twin assay gave.

What this does NOT establish: anything about other energy regimes, the ON arm, or larger horizons; anything about
whether a law with a mobile medium (TH-009) moves content (none was tested).

## Execution
- Fabric was the planned path. All 28 Tasks sat unclaimed for 20 minutes. The three ubu001 workers showed "online"
  but had not been seen since 2026-10-02 10:37 (stale instances; DEF-ODY-017 class). The Tasks were cancelled
  unexecuted.
- MWO-0004 R3 native fallback on BUCKKEEP:
  - detached worktree pinned at 9770203e6;
  - canonical lease buckkeep:cpu8 lse-a03858e1b71d, acquired 16:01Z and released after the run;
  - waves of 3, foreground; 28/28 units, 41-68 s each.
- Verification:
  - all 28 exited 0, so prov0's per-tick shadow-vs-physics self-check passed in every unit (a mismatch raises);
  - result_sha256 was recomputed and matches for 28/28;
  - determinism: T1-fwd-s4 re-run gave the identical hash (f49b4a5c59509fc4).
- Compute: about 0.4 CPU-h.

## Replay
`git worktree add --detach <dir> 9770203e6 && cd <dir> && python Aether/observatory/aeth_prov_assay.py --law <law>
--seed-index <s> --arm off --out <f>` for law in {v1, rcv, fwd, add, rcv_add, rcv_str, rcv_adr} and s in {4..7}; then
the reducer above.
