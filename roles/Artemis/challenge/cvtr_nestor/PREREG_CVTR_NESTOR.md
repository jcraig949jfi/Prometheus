# PREREG_CVTR_NESTOR -- CVT-R on Nestor's genome sets (comms #802)

Seat: Artemis (Prometheus), host ubu002, delegate. Written 2026-09-28, PHASE 1 (design, design check, cost
pilot). The certification run itself (`run_cvtr.py run`) is NOT executed until the seat says so. Everything
below is fixed before that run; any change after it is an amendment in a separate, dated file.

Scope: computational artificial life (integer programs on NPE's z8 VM). Nothing biological.

## 0. Request (Nestor, comms #802, essentials)

Run CVT-R on
- (a) the 32 genomes in `x_p2_bridge/DONORS.json` and `c_zero_specific/DONORS.json`
  (campaign npe-p2-endogenous-heredity-2026-09-27);
- (b) a fixed-seed random sample of 100 competent genomes (rate_full >= 0.5) from
  `delegates/corpus/q1_partial.jsonl`, on the dense VM (`run_dc.dense_z8`) when vm == DENSE, with the cell
  given in each row;
- (c) the late state-free genomes of the 7ae3 / 16000006 lineage (npe-arc3-2026-09-28,
  delegates/forensic_16000006, files named in FORENSIC_16000006.md).
Report the CVT-R accept rate per set, and every genome that P-11 certifies but CVT-R rejects.

## 1. Sources (read-only; nothing written into any git checkout)

- Nestor's files: `git archive` of origin/main at b5b77af8c914058a0aff7fecba842e52cdfabb45 into
  /home/jcraig/artemis-cvtr/foreign/ (GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE unset). This includes the VM and
  assay code: z80atlas-verify-2026-09-22/*.py and MANIFEST_FROZEN.json, c9x x_donor_swap/run_ds.py, and W1
  x_dd_dense_copy/run_dc.py, x_donor_discovery/run_dd.py, x_dd_establish/run_de.py.
  z8.py and p11.py are byte-identical to d7641744d, the version used by the P-11 challenge.
  constants.py only adds H1/H2/H3 keys; none of the P-11 thresholds change.
- CVT code: `certs.py` copied unchanged from roles/Artemis/challenge/p11 (commit 2af325f7b), sha256 5b22111c...
  It is identical to the worktree copy. `artemis_p11/common.py` is a shim that supplies only `shabytes`
  (verbatim copy) and `fid` (= p11.fidelity).
- SHA-256 values of the inputs:

| file | sha256 (first 16 hex) |
|---|---|
| x_p2_bridge/DONORS.json | 6e9c66788831f286 |
| c_zero_specific/DONORS.json | 0f9e283740c6ba7a |
| corpus/q1_partial.jsonl | 9b2eb45ce92931a2 |
| forensic_16000006/paths700.json | d0b5a8c298a7777c |
| z80atlas-verify z8.py / p11.py | 8382574ba5db28d5 / 7a47c25dcf08ea7b |
| adapter.py | 9d096e5cdaf1e68a |
| run_cvtr.py | 8a4d162800ebbb3e |
| results/SELECTION.json (the frozen list, section 2) | f6b0928b10581312 |

  Full hashes are written to results/ADAPTER_CHECK.json and results/SUMMARY.json.

## 2. Sets and exact genome selection (`run_cvtr.selection()`; frozen as results/SELECTION.json, 140 rows)

**(a) 32 rows, as listed.**
- Rows are taken in file order: x_p2_bridge 0..15, then c_zero_specific 0..15. Each file has 8 genomes of
  origin 7ae3 and 8 of origin ffa6.
- VM: DENSE. Both panels come from DENSE_COPY runs: run_br.donors() and run_cz.donors() read
  x_dd_dense_copy and c_dense_copy DENSE_COPY results, and every run in both experiments sets
  `world.z8 = run_dc.dense_z8()`.
- Cell: the row's `origin`. See section 3 for why this choice is immaterial.

**(b) 100 rows.**
- Pool: every row of q1_partial.jsonl with rate_full >= 0.5. That is 1,278 of 1,532 rows: DENSE ffa6 842,
  DENSE 7ae3 409, PLAIN 7ae3 26, PLAIN ffa6 1. The pool has no duplicate (vm, cell, hex).
- Order: sorted by (vm, cell, hex).
- Draw: `random.Random("CVTR-NESTOR-802-b").sample(pool, 100)`. Result: DENSE ffa6 65, DENSE 7ae3 31,
  PLAIN 7ae3 3, PLAIN ffa6 1.
- VM: dense_z8 for vm == DENSE; the stock z80atlas-verify z8 for vm == PLAIN. The request names the dense VM
  only for DENSE rows. PLAIN rows were produced and assayed on the stock VM (corpus_analysis.env), so that is
  where their P-11 status is defined. PLAIN rows are also reported as their own stratum.
- Cell: the row's `cell`.

**(c) 8 rows.**
- The 8 epoch-700 modal genomes, `paths700.json` paths[0..7].genome. These are vids 27070, 26882, 27200,
  26706, 27003, 26971, 27107 and 27023, the same 8 genomes as causal.json "b".
- FORENSIC_16000006.md calls these the lineage's late, genuinely state-robust genomes ("copy after every
  k = 1..6 and from 0x5A and random register starts").
- VM: DENSE. Cell: 7ae3, as in forensic measure.py.
- All 8 are included, even though causal.json marks one of them (27200, `ffff1931...`) FRESH 0.0 / FR False on
  the forensic copy criterion (it is still competent: True). The forensic FR / FRESH / competent flags are
  carried into the output.

**Overlap.** Two genomes are in both (a) and (b): c_zero_specific 0 = b:50 (cf974a34...) and c_zero_specific 3
= b:56 (067af3cf...). Each set is scored on its own, and the verdicts are identical because everything is
deterministic. So 140 rows cover 138 distinct genomes.

**Not included** (possible readings of (c), reported only if Nestor asks):
- vid 1005, the first FR genome at epoch 399. Its key byte 0 is not heritable (FORENSIC s. Localized change),
  so it is not a "late" genome.
- The D0 founders.

## 3. VM, cell, side and budget per genome (the adapter)

The environment is built exactly as Nestor's corpus delegate builds it (corpus_analysis.env):
- `world.z8 = run_dc.dense_z8()` or the stock z8, set explicitly;
- `r = world.Runner(dict(run_ds.cells()[run_dd.CELLS[cell]]["cell"], atlas_axis="NONE"), 1, tier=<arm tier>)`;
- n = r.L, tape = world._pow2(2n), slice budget = r.t["slice"], ops mask = r._ops_mask(), copy rate = r.copy_mut.

Values measured for both cells:

| cell | representation / structure | tier | n | tape | slice | mask | copy rate |
|---|---|---|---|---|---|---|---|
| 7ae3 | Z8_64 / WELL_MIXED | M | 64 | 128 | 300 | 0x2A | 0.002 |
| ffa6 | Z8_SLOTTED / NICHES_HIGH_MIG | M | 64 | 128 | 300 | 0x2A | 0.002 |

The pair-assay parameters are identical in the two cells. P-11 and CVT-R depend only on these parameters and
the VM, so the cell label (including the question of which cell to use for (a)) cannot change any verdict.
It is recorded for bookkeeping.

**Sides.** CVT-R is computed with the genome as donor at side 0 AND at side 1. Everything else is the same on
both sides, so each genome needs 2 CVT computations.
- A genome is CVT-R ACCEPTED iff CVT-R accepts on at least one side. This mirrors NPE's COMPETENT ruler,
  which counts a pass on either side.
- Reason for this rule: the P-11 challenge (RESULT s7) found that a copier at side 1 can be hijacked when
  the side-0 partner executes it first. A side-agnostic rule avoids scoring that artefact as non-heredity.
- Also reported (secondary): whether CVT-R accepts on a side where P-11 itself certifies.

**CVT step** (harness.step, kind "pair", unchanged in substance):
- One `p11.interact` on the cell's VM with the cell's n, tape, slice and mask.
- Fresh registers for both halves; copy mutation 0 (as preregistered for all certificate computations).
- The victim half is common-random bytes sha256("VICTIM", sid, g, k). The descendant is the victim half, and
  it is re-placed at the same donor side for the next generation.
- sid = the genome's full hex, so the perturbation values r_i and the victims depend only on the genome,
  never on the set it came from.

## 4. P-11 status (re-applied first, fresh state)

For every genome, before CVT, P-11 is re-applied exactly as NPE's fresh-start COMPETENT screen does it
(run_dd.assay_one):
- p11.assay unchanged, at the cell's copy rate;
- donor on side 0 and side 1 against a blank partner, fresh registers;
- K = 20 seeds; seed ("X-DONOR-DISCOVERY", ("CVTR-NESTOR-802-P11", hex), i, side).

Outputs: the either-side rate (a seed counts if either side passes) and the side-0 and side-1 rates.

**"P-11 certified" (primary) := fresh either-side rate >= 0.5.** This is NPE's own L2 COMPETENT threshold. The
K1 = 4 pre-screen is omitted because it only saves time.

Every genome in all three sets was admitted by a Nestor screen as competent: the W1 checkpoint L2, the
C-ZERO-SPECIFIC re-screen, q1 rate_full >= 0.5, and forensic competent = True. So the output also lists
**every** CVT-R rejection as "recorded-competent but CVT-R reject". That is the literal answer to "certified by
P-11 that fails CVT-R" if Nestor means their recorded status. The primary list uses the fresh re-application.

Rates close to 0.5 can move between seed sets; the pilot's a:x_p2_bridge:0 gave 0.35 fresh. Both classifications
are therefore given, and neither is dropped.

**Environment gate for (b).** Each (b) genome is also re-assayed with q1's own seeds
(`run_dd.assay_one(world, r, g, ("CORPUS-Q1", hex), 20)`). The result must equal the recorded rate_full
exactly. A mismatch means the VM, cell or seed environment differs from Nestor's, and the genome is then
UNSCORABLE (section 6).

## 5. The CVT-R accept rule (as implemented, certs.py @2af325f7b; PREREG_P11.md s3)

- **Perturbations.** For each site i of the n = 64 sites, m = 3 substitutions:
  - x ^ 0x01;
  - x ^ 0x80;
  - r_i = sha256("VAR", sid, i, j)[0], taking the first j whose value differs from all three of the others.

  That gives 192 variants.
- **Lineages.** Each variant and the unperturbed genome run through generations g = 1..4 under draws
  k = 0, 1, 2 (common random victims, identical across variants).
- **Signatures.** Delta_g(v, k) = {(pos, byte): variant descendant != baseline descendant}. Delta_g(v) is
  DEFINED iff the same non-empty signature occurs in at least 2 of the 3 draws.
- **Certificates.**
  - CVT-1: some v has Delta_1 defined.
  - CVT-2: some v has both Delta_1 and Delta_2 defined.
  - **CVT-R: some v passes CVT-2 AND (Delta_3(v) == Delta_2(v) OR Delta_4(v) == Delta_2(v)).**
- **TB.** TBR = log2(1 + number of distinct recurrent Delta_2 classes).
- **Reported per side:** CVT1, CVT2 and CVTR (accept, n, classes, TB, h) and LOCAL. CVT-2 is reported beside
  CVT-R.

## 6. Adapter failure = UNSCORABLE (never dropped)

A genome is UNSCORABLE if any of these happen:
- any exception while evaluating it;
- genome length != cell L;
- the VM module name differs from its assignment (z8_dense_copy for DENSE, z8 for PLAIN);
- (b only) the q1 rate_full reproduction check fails.

Its row is still written, with `status: UNSCORABLE` and the reason. The per-set tables show n_listed,
n_unscorable and n_scored. The accept rate is computed over scored rows, and two bounds are given beside it:
one with all UNSCORABLE rows counted as accept, one with all counted as reject. The run asserts that the row
keys equal the 140 selection keys exactly.

## 7. Outputs (results/)

- ROWS.jsonl: one row per selected genome, containing
  - the key, set, VM, cell and hex;
  - the source fields;
  - params;
  - P11 (either-side, side 0 and side 1 rates; certified; certified sides);
  - q1_reproduced (b only);
  - CVT per side;
  - CVTR_accept, CVTR_sides, CVTR_TB_max, CVT2_accept and CVTR_on_P11_side;
  - status and seconds.
- SUMMARY.json, per set: (a), (a)/x_p2_bridge, (a)/c_zero_specific, (b), (b)/DENSE, (b)/PLAIN and (c). For each:
  - the CVT-R accept count and rate, with a Wilson 95% interval;
  - the same among fresh-P-11-certified genomes;
  - the CVT-2 accept count;
  - the UNSCORABLE bounds.

  SUMMARY.json also lists the genomes that are P-11 certified (fresh) but CVT-R rejected, with their P-11
  rates and CVT-1 and CVT-2 TB values. It also lists the recorded-competent genomes that CVT-R rejects, the
  genomes accepted by CVT-R only on the side where P-11 does not certify, the UNSCORABLE genomes, and the
  file hashes and origin/main SHA.
- The seat writes the human report for Nestor after the run. No thresholds are applied beyond the rule
  above, and no verdict about Nestor's claims is computed mechanically.

## 8. Design check (phase 1, done; results/ADAPTER_CHECK.json)

`python3 -B run_cvtr.py check` result: **PASS**, 1.8 s.
- Dense VM self-test (run_dc.selftest): plain False, dense True, as required.
- NATURAL 7ae3f9c1, side 1, stock z8, n 64, slice 360, mask 0x2A: CVT-R ACCEPT, TB 7.3837, 166 classes.
  CVT1, CVT2, CVTR and LOCAL are identical to results/NATURAL_REAPPLY.jsonl.
- NATURAL 12ad3d5f (the 0x36 painter), side 0, n 32: CVT-R REJECT. Identical to the record.
- PANEL Z1 (homopolymer painter), stock z8: REJECT, identical to PANEL.jsonl. On the dense VM: REJECT.
- PANEL Z3 (block copier) on the dense VM: ACCEPT, TB 6.2479 (the record value).
- A single PLAIN row of (b) (b:44) was checked with the q1 reproduction only: rate 1.0 = recorded 1.0. No CVT
  was run on it.

## 9. Cost (pilot, `run_cvtr.py pilot`, results/PILOT.json)

The pilot ran three genomes, one per set: a:x_p2_bridge:0, b:q1_competent:0 and c:epoch700_modal:0. Each took
the full per-genome path (P-11 with K 20 x 2 sides, the (b) q1 check, and CVT on 2 sides x 192 variants). Times
were 0.85 s, 1.05 s and 1.00 s of CPU.

Disclosure: the pilot's verdicts on these three genomes have been seen. They are recomputed identically in the
run and are not treated specially:
- a:0: fresh P-11 0.35, CVT-R reject;
- b:0: P-11 0.95 on side 0, CVT-R accept, TB 7.29;
- c:0: P-11 1.0 on side 0, CVT-R accept, TB 7.37.

**Estimate:** 140 genomes x about 1 s = about 2.5 CPU-minutes, or about 1.5 minutes of wall time on 2 processes.
Allowing 5x for painters or run-to-budget genomes, the ceiling is under 15 CPU-minutes. Peak memory is
small (a single-process CVT cache of a few MB).

Command for phase 2: `cd /home/jcraig/artemis-cvtr && python3 -B run_cvtr.py run`, with 2 workers, resumable.

## 10. What the result can and cannot say

- CAN: for each genome, whether a single-byte parental difference reliably produces an offspring difference
  that is re-transmitted and recurs within period 2, when the genome acts as a donor in NPE's own pair
  interaction, from a fresh state, on its own VM and cell. The accept rate per set, with its interval, then
  gives the share of P-11-competent genomes that carry transmitted variation, as opposed to "construction
  without heredity" (painting).
- CANNOT:
  - CVT-R ACCEPT is a property of the genome's reproduction map from a fresh state. It is not evidence that
    the lineage's evolutionary claim holds. In particular it does not show that (c)'s state robustness is
    heritable, that the 16000006 lineage transmitted its robustness, or that any establishment result in
    x_p2_bridge or c_zero_specific was caused by heredity.
  - Carried register state, copy mutation, non-blank partners and population context are all excluded by
    design: fresh registers, copy rate 0, and common random victims.
  - CVT-R REJECT on a genome that is P-11 competent means that, in this harness, the genome's copies do not
    carry its own single-byte variation forward (the painter pattern). It does not rule out heredity under
    carried state or under another perturbation set. m = 3 per site is a lower bound on transmitted
    classes, not an exhaustive test.
  - Because the certificate is side-agnostic, a copier that works only at side 0 counts as accepted.
  - The (b) sample describes the corpus sample. It does not describe all genome copies (q1 weights runs
    roughly equally, CORPUS_ANALYSIS.md s. Sampling).
- (a) is not a random sample. It is two fixed donor panels, so its rate describes those 32 donors only.

## 11. Ambiguities to put to Nestor (the design does not wait on them; each has a stated default)

1. (c) "late state-free genomes": the forensic files do not use the word "state-free".
   - Default: the 8 epoch-700 modal genomes of paths700.json, including 27200, which is FR False with
     FRESH 0.0 on the forensic copy criterion.
   - Alternatives: only the 7 FR = True genomes (a subset, which can be read off the output), or other
     late or FR genomes not listed in a file (for example vid 1005, or robust genomes after epoch 700,
     which the forensic did not trace and so cannot be selected from files).
2. (a) cell: the request gives no cell for (a). The default is the donor's origin cell. The panels actually
   ran in C7/C7S/C7N/CF (bridge) and CF (c_zero_specific). This is immaterial because the pair-assay
   parameters are identical (section 3).
3. (b) PLAIN rows: the request names only the DENSE VM. The default keeps the 4 sampled PLAIN rows, on the
   stock VM, and also reports DENSE-only rates. The alternative (sample from DENSE rows only) would change
   the sample, so Nestor must ask before the run if Nestor wants it.
4. "Certified by P-11": the default is a fresh re-application (K 20, either side, >= 0.5), with the
   recorded-competent reading also listed.
