# Cycle 9 -- STOPPED BEFORE FREEZE (2026-09-24)

**Nothing is frozen. Nothing is launched.** There is no `CALIBRATION.json`, no final hash
in `PREREGISTRATION.md` and no production observatory. The operator's ruling of
2026-09-24 says: *"If a NEW scientific-validity defect appears before launch, stop
instead of repairing across the freeze boundary."* One appeared (C9-D14). Every ruling
has been applied. Every gate has been run and passes. The tree is ready for a freeze
decision.

## 1. The new validity defect -- C9-D14

**On the pair tape, organism identity is not heredity, and the H3 certificate follows
identity.**

The P-1 certificate walks the parent map by organism id (oid):

    born in the easy niche -> migrated out -> ... -> crossing in a hard niche

On `PAIR_EXECUTION`, an organism keeps its oid while its bytes are rewritten. The
world mutates both halves every epoch, and the partner writes into it. None of this
creates a lineage event unless the predecessor criterion fires. The ruled repair (every
pair edge must be P-11 causal) makes each recorded **step** causal. It says nothing about
the bytes carried **between** steps. It also still accepts a certificate with **zero
edges**: an organism born in niche 0 that migrates and crosses. Test T-H3-P11 shows that
case forming with `lineage_len 1`.

Measured with `d14_probe.py` / `D14_PROBE.json`. The world is H3 arm A of each pinned
cell at tier S, on off-manifest seed 9,900,101. Only byte fidelity is read; no held,
crossing or certificate outcome.

| epochs | organisms never the child of any lineage edge | median identity with their own birth genome | share below 0.10 |
|---|---|---|---|
| 1 | 128 / 128 | 0.969 | 0.0 |
| 10 | 128 / 128 | 0.656 | 0.008 |
| 50 | 128 / 128 | 0.250 | 0.141 |
| 600 | 128 / 128 (both cells) | **0.000** | **1.000** |

In both H3 cells **no lineage edge of any kind** was recorded in 600 epochs, and every
organism's bytes were fully replaced. An H3 arm-A certificate in these worlds would
therefore certify that an **organism id** moved from the easy niche to a hard niche. It
would not show that any **genetic material** did. The reservoir claim is about material.

Why this was not caught before: C9-D11 was framed as "which edges may be walked". The
gap is that a chain of pair-tape oids, causal edges included, is not a chain of
inherited bytes.

### Options (operator decision; none implemented)

1. **Byte-carried certificate.** Require every link, including the zero-edge founder
   segment, to carry bytes. At the crossing, the crossing genome must match the
   founder's easy-niche genome, or the last P-11 donor's genome, above a declared
   fidelity. The rule is declared before any result.
2. **Certificate only across P-11 edges, with a minimum of one edge**, and the crossing
   within k epochs of the last causal copy. The window k is declared now and bounds how
   far drift can go.
3. **H3 on a physics where identity is heredity.** The ruling rejects EXTERNAL
   reproduction; a private-slot endogenous world would qualify. S1-A shows those produce
   no births from random starts, so this would need seeded populations.
4. **Withhold H3 this cycle**, as H4 was. H1 and H2 carry the campaign: 1,008 runs.

## 2. Launch blocker (engineering, not validity)

The Cycle-9 tree has **no campaign runner, no H1 or H3 adjudicator, and no report or
report-audit pipeline**. The rev-B gate list never required them. It has a bundle store
and a generic margin rule; the H2 rule now exists in `hypotheses.py`. To launch, the
following must be written and tested **before** freeze, because the protocol hash covers
every campaign module:

- a manifest consumer on the P-7 bundle store (drain, restart, no replacement jobs);
- the observatory under the frozen protocol;
- H1, H2 and H3 adjudicators;
- a report built from the index;
- a report audit with injected-defect controls.

Estimated at several hours of build and test.

## 3. Rulings applied (all pre-freeze)

| ruling | done | evidence |
|---|---|---|
| 1 H4 withheld | removed from manifest; A-22; autopsy preserved | T-MAN "H4 withheld" |
| 2 H2 rule | 16 specimens, 16 seeds; B >= 8/16, C <= 2/16; panel >= 2 strata; depth >= 2, >= 3 secondary only | `hypotheses.py`, T-H2 (12 checks + injection caught) |
| 3 P-11 authorship | primary causal_value_authorship; literal last-write sensitivity mandatory; 57 / 48 | A-16, P-11 section |
| 4 H3 certificate | non-P-11 pair edge breaks it | T-H3-P11: 3 ruled cases, 2 fail-on-old-code |
| 4 H3 repick | 2 RESERVOIR cells, 32 seeds, 3 arms, 192 runs | `manifest.H3_CELLS` |
| 4 H3 arm B | **C9-D13 found and applied as ruled:** rev B's arm B migrated at 0.08 against the reservoir's 0.02; now RESERVOIR with the easy niche off | T-H3-B, A-21 |
| 5 manifest | **1,200 runs** (H1 240, H2 768, H3 192, H4 0), 380 bundles, 0 problems | T-MAN |
| 6 prereg | rev C, amendment log A-15..A-23 | PREREGISTRATION.md |
| 7 gates | all pass (section 4) | GATES_PREFREEZE.json |

One case the ruling does not name: two or more supporting H2 specimens in the **same**
stratum. It is reported as SAME_STRATUM_CANDIDATES, never as panel-positive. Please
confirm.

## 4. Gates, projection, proposed hashes

**Gates: 12 of 12 PASS** (`run_gates.py` -> `GATES_PREFREEZE.json`). The suite is:
- VM selftest;
- T-P1/2/3/8/9/10, T-P4, T-P5, T-P7;
- T-P11 (14 checks);
- T-S3 (12 checks);
- **T-H3-P11** (3 ruled cases + 2 fail-on-old-code + 4 arm-B checks);
- **T-H2** (12 checks + 1 injection);
- the P-6 report audit;
- the calibration controls (PREFREEZE);
- **T-MAN/T-HASH**: manifest validation, and every hash recomputed in 3 processes under
  3 `PYTHONHASHSEED` values, compared with `PROPOSED_HASHES.json`.

No `CALIBRATION.json` exists.

**Projection** (`S4_TIMING.json`): full-length timed runs, wall time only, on
off-manifest seeds.

| | runs | CPU-h |
|---|---|---|
| H1 | 240 | 0.77 |
| H2 | 768 | 31.84 |
| H3 | 192 | 7.48 |
| **total** | **1,200** | **40.1 -> 6.7 wall-hours at 6 workers** |

The repicked H3 cells cost 140 s per run, against 52 s for the rev-B cells.

**Proposed hashes (NOT FINAL):**

| | value |
|---|---|
| protocol | `d70495cc6bcf66e73d7de6f69af7ee49ff458973666a994a78862bbc37a9ba8b` |
| manifest | `8d88cf06123b6e62c85c356a65c85a5d9903b220d09979ba71b20509241ea67a` |
| panel | `d52426aff80d509cd6a16e8ddad3aea25a9265ee8ef079b7b1da8da81a4006fb` |
| grammar | `61da6513ea0b36e04d4b2164a208fe4e1fd700e078076db847dc037f1c327f4e` |
| constants | `b1c8a904d092dd61eff970f581424635c591475f8d441351d6a01caf89cccffb` |

Any change made to resolve C9-D14, or to add the runner, changes the protocol hash, and
the gates must be re-run.
