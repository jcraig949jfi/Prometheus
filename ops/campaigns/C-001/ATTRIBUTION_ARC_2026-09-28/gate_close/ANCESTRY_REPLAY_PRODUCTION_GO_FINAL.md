# ANCESTRY_REPLAY_PRODUCTION_GO_FINAL (NPE; Archaeon, 2026-09-28)

**Authority:** the operator directive "CLOSE THE INDEPENDENCE GATES" and ANCESTRY_PREREG_v5 Amendments C9 s6 and C10.
- This record supersedes and replaces Archaeon's withdrawn GO (#845) and the C8 clearance (#848).
- It makes Nestor's run_production.py gate ELIGIBLE, only under the bindings below.
- No production outcome was computed or inspected by Archaeon.

## Gates
| gate | status | evidence |
|---|---|---|
| G1 fixtures | PASS | See "G1 fixtures" below. |
| G2 tracer agreement | PASS | See "G2 tracer agreement" below. |
| G3 flip rule | CLEAR | C7.2 prefix-preserving rule, gating for both engines; the strict rule is reported (Nestor GATES.json, 2026-09-28T22:16:52Z). |
| G4 experimental unit | CLEAR | C7.4: 9 distinct simulations / 29 distinct births, cluster at the simulation level, duplicates kept in the evidence trail. |

**G1 fixtures (C9 s2, re-run fixture by fixture on the frozen reference):**
- K16b PASS: performer by material a, store location and slice b.
- K16c PASS: performer by material b, store location and slice a.
- K37 PASS: 8 loci, 1 source, 1 instruction, 1 value.
- The full pack agrees 451/451. It was re-checked against the C10 reference.

**G2 tracer agreement:**
- The set: fresh set 2, seed 49220fae2, pre-states sha256 c1589c6f, 300 A + 100 M.
- The comparison was declared before opening, and both outputs were sealed before the exchange (SEALED_HASHES_SET2.json).
- RAW, per class, >= 0.995: label, addr, ctrl and exec are 1.0000 in every class of both sets.
  * A: unwritten 17,904, written_self 676, written_other 553, written_perf_none 67.
  * M: 5,965 / 233 / 169 / 33, including the MUTATION class, 212/212.
  * written, store_by and performer are also 1.0000.
- Two independent comparisons agree: Archaeon's fresh2_result/, and Nestor's NESTOR_COMPARISON_SET2.json at e2d055fa9.

## Bindings (sha256 of LF-normalized bytes)
| item | hash |
|---|---|
| Nestor tracer freeze v3 (TRACER_FREEZE.json @ b187824e6) | 77a822acb7203295c28187b16a93d368bb0a8cf1bc72a3630aed304015d4bc3e |
| production code run_production.py (unchanged v1-v3) | c31cca76b7458dfb048c6b4d895935926353021919501185ef27ab0daf4c42c4 |
| Archaeon reference tracer ref_tracer_npe.py (C10; commit 9d7eafcf5) | 157374444597750fe114602cd83fa02faa36048161889b06f15e40d4ec7d7368 |
| fixture pack npe_fixtures.py | 25c8507e51acbf6b2c02690ccfb889c54af4477a31a34ac3fe6f2b9cfe18c644 |
| fixture additions ARCHAEON_ADDITIONS.json | 1753023ca4f5f168860c2610f1ef3dc183f4f3d170f9e2715c7394d76297b012 |
| spec ANCESTRY_PREREG_v4.md | cb61142ad260c7c9ea33d6ded9774c53d8ca01fb384c24b57c225a65feda19b4 |
| spec + amendments ANCESTRY_PREREG_v5.md (through C10) | 45bc06eaf8ca5f07d2ee94091f8eb8b382213efedd0e4aba17a9c68073fe08bd |
| experimental-unit rule | C7.4, as above |
| flip-test rule | C7.2, as above |
| agreement set pre-states FRESH_SET2_PRE.jsonl | c1589c6f659415345c12dd5a65d218f54ed829c2710c381f6b18bf0dd6565d28 |
| agreement outputs (uncompressed; ref / Nestor) | e638eeb105403e5b44402bc4f0a816c16c51e2ac08b3200534a0c70a0c5e9a9f / 4f542a708ba3d8398893c0de1c4b041b91a014b7ae0f14cf5a52d87683a8ce61 |
| agreement result FRESH_AGREEMENT.txt | 43ed2545d647987e02a540dd6f9015b412f729396d83c1e5ae478d0cfed2a8b3 |

## Scope limits, stated so they are not read as cleared
- **ctrl_deps_slice (secondary, non-gating per v5):**
  * agreement is 0.92-0.99. All 70 set-2 discrepancies are this field.
  * The cause is diagnosed (S3): whether IN's input-cursor guard is a slice-scope condition. D6 is the counterexample. It is
    OPEN.
  * No production quantity may use ctrl_deps_slice without a ruling and a fresh agreement set.
- **Post-dominator scope:** not in Nestor's export. It is non-gating (C7.1) and NOT compared. It may not feed any production
  quantity.
- **Existence dependence (Q8c-whether):** this is interventional (engine re-execution), not a tracer field. G2 does not
  validate it. Its validity rests on the interventions code under the freeze hash and on G3.
- **Post-agreement-test repairs,** all recorded (C9, C10) and flagged for the independent final reviewer:
  * A1/A2 withdrawn;
  * the C9 s5(a) label clarifications;
  * the C10(a) draw index;
  * the C10(b) MUTATION addr EMPTY. The reference owner changed the reference after seeing the owner's reading.

## Production hygiene (binding from now on)
- **Frozen:** thresholds, eligibility, flip rule, clustering, tracers, fixtures and semantics.
- No case may be dropped.
- At start, the production run must verify every file against TRACER_FREEZE (77a822ac...) and run_production.py (c31cca76...),
  and record the verification in its receipt.
- **A severe defect** means:
  1. stop;
  2. invalidate;
  3. document;
  4. repair;
  5. re-freeze;
  6. restart under a new receipt.
- **Keep L1-L5 separate:**

  | layer | meaning |
  |---|---|
  | L1 | written |
  | L2 | causally donor-written |
  | L3 | child later reproduces |
  | L4 | contribution persists |
  | L5 | independent heredity/recert |

  Do not claim L5 from P-11 or attribution. Source-diversity metrics are diagnostics only.
- **The 1% production agreement sample (~28k interactions, ~115 MB) is NOT in git, in any form.** The transfer:
  1. Nestor hashes the file and posts the sha256.
  2. scp to M2 C:/Prometheus-data/evidence/attribution_arc_2026-09-28/npe_sample/.
  3. Archaeon verifies the sha256 before reading.
  4. The frozen reference (15737444...) runs on it.
  5. The result artefact is hashed.
  6. Only receipts and statistics go into git.
  7. No reduction after anything is seen.
- **Open item:** Nestor's GATES.json "sample_transfer" still names the withdrawn orphan-branch route. It must be corrected to the
  route above. This is not a gate.
