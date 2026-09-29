# E-003 BEE leg: GO v2 -- re-binding after Amendment C11 (Archaeon, 2026-09-29)
**Supersedes** BEE_PRODUCTION_GO.md (sha256 aa958093...) for the evidence chain.
- Its gates, bindings, conditions and hygiene carry over UNCHANGED, except the bindings below.
- Production is NOT re-run: the owner's frozen tracer (823cbef1) and its production outputs (72ed6e160, PRODUCTION_SEAL.json)
  are unchanged.

**Why:**
- The preregistered production s4.3 agreement FAILED on the all-CONSTANT computation label.
- C11 ruled the literal text and repaired the two ARCHAEON-SIDE tracers. They are re-frozen.

**Changed bindings (sha256, LF):**

| item | hash |
|---|---|
| reference ref_tracer_bee.py (C11) | 571fba8c5ccfde192cd2aa0b42a40e6fbebdb8d9ba8fbd80aa666b32f45534dd |
| Archaeon bee_ref_tracer.py (C11) | c644911932d8ce62a0899cb545d664235501008ae2808198ac63a7acfc80f848 |
| spec ANCESTRY_PREREG_v5.md (through C11) | c432bcd3193a08e6ea359d7dce91687f72125947eca98904b44345178022f5cd |
| FRESH set 2 agreement (seed 6cae86e4a) | bee_fresh2_result/BEE_FRESH_AGREEMENT.txt ab60270d7ec1507626624540f096b8f658f4615261e01c2a22afc0cb3cdc5529 |

**Evidence now standing:**
- **Fresh set 2** (independent; all three outputs sealed before exchange, BEE_SEALED_HASHES_SET2.json): PASS.
  * Every pair agrees 1.0 on every field in every class (self 14,048; other 791; perf_none 68; unwritten 17,093).
  * 0 discrepancies.
- **Production s4.3 on the 200 s4-sampled births,** re-run after C11 (bee_production_agreement_C11/): PASS.
  * owner ~ Archaeon exact; reference 1 label (the B-L1 flattening shape).
  * POST-EXPOSURE: supporting, not independent.
- The original fresh set (seed fefefe074): PASS under the pre-C11 tracers. Kept as history.

**Claim gate:**
- GO condition 3 (production agreement before any claim) is now SATISFIED.
- The owner may report E003_RESULTS.json under the frozen rules, including the B-P1 A/B reading-dependence.
- Archaeon has still inspected no Q or verdict value.

**Open, carried over:**
- The persisted ORIGIN attributes (pre_labels) are not tested by the exchange format (declared limit).
- Q5 is not reported without its null. The pdom scope feeds nothing.
