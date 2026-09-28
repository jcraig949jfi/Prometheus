# NPE ancestry replay: gate report (Archaeon, 2026-09-28). Full text: ANCESTRY_PREREG_v5.md Amendment C9

**G1: PASS.** Frozen reference 3757111de; G1_FIXTURES_K16b_K16c_K37.json.
- **K16b PASS.** The value 0x42 is labelled a2. It is stored by slice b, at pc 56 in b's half, and the performer is a1. The
  attribution follows the material (a), not the location or slice (b).
- **K16c PASS.** The value 0x55 is labelled b25. It is stored by slice a, at pc 24 in a's half, and the performer is b24. The
  attribution follows the material (b).
- **K37 PASS.** 8 loci, all b16 = 0xA0, from one instruction (pc 41) and one performer (b9).
  * Diagnostics only: 1 source, 1 instruction, 1 value, 1 performer.
  * One source painting a region.

**G2: FAIL** under the preregistered rule (v4 s4.3, raw, per class, >= 0.995).
- 300 interactions: Nestor e5af0cae1 vs reference 3757111de.

| class (loci) | label | addr | ctrl | exec | written | store_by | performer |
|---|---|---|---|---|---|---|---|
| written_self (587) | 0.9353 FAIL | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| written_other (320) | 0.9250 FAIL | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| written_perf_none (33) | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.9394 |
| unwritten (18,260) | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | -- | -- |

- **Secondary ctrl_slice:** 0.9710 (self) / 1.0 (other) / 0.9394 (none).
- **Descriptive:**
  * source locus 1.0;
  * class key 1.0;
  * carry/flag loci 0.931 / 0.952 / 1.0.
- **Not exercised (INCONCLUSIVE):** MUTATION, IN, OUT, pdom scope, and existence dependence (interventional, not a tracer field).
- **Discrepancies:** 83 loci (G2_DISCREPANCIES_RAW.jsonl), each record with a full pre-state and both readings. All are category
  (1), specification ambiguity in Archaeon's C6 summary:
  * S1: CF(COMPUTED S) vs COMPUTED S, 24 loci;
  * S2: idiom CONST kind names, 40 loci;
  * S3: ctrl_slice transitive bases, 19 loci, Nestor's set a strict subset.
  * Minimal reductions D1-D4 are in G2_MINIMAL_CASES.json.
- **C8's A1/A2 clearance is WITHDRAWN** as a post-agreement-test repair.
- **Repair:**
  1. spec clarifications (C9 s5a);
  2. Nestor re-freezes;
  3. the reference is re-attested, unchanged;
  4. FRESH set: npe_fresh_set.py, seeded by the SHA of the commit recording both re-freezes; 300 + 100 with write-back.

**Freeze integrity** (sha256, LF-normalized):
- reference ref_tracer_npe.py 2851bcdb6cc9a074db3b0338b663c1dec6b533a22b2e34c0cb522ac69de2a4e2 (unchanged since 3757111de);
- Nestor's TRACER_FREEZE (e5af0cae1): z8shadow 28dbe1c5..., observe eb68f847..., interventions 33c1e3a0..., run_production
  c31cca76...;
- fixture pack npe_fixtures.py 25c8507e51acbf6b2c02690ccfb889c54af4477a31a34ac3fe6f2b9cfe18c644;
- ARCHAEON_ADDITIONS.json 1753023c...;
- spec: ANCESTRY_PREREG_v4.md cb61142a...; v5 before C9 dba2689b...; v5 with C9 is hashed at the commit that carries it;
- fuzz export used: 46eb4a15bce82dbabd3f0e93a7f2140df4c64cda814d7ec3ee2667cbea44132c.

**Production: HOLD.** G2 failed under the preregistered rule; the repair and the fresh-set G2 are pending. No production outcome
was computed or inspected.
