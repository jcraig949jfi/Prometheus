# C-019 closeout -- Observatory generation 5 (from mechanism attribution to cumulative discovery)

Palamedes[harry1-679179c6], 2026-10-15.
- **Timing:** opened 09:05Z; closed early, as the directive provides for a selection-gate rejection, about 9 h into the
  72-hour window.
- **Directive:** roles/Palamedes/prompts/2026-10-15_generation5/01_OPERATOR_DIRECTIVE_verbatim.md.
- **External review packet:** rso/scale/review/GEN5_EXTERNAL_REVIEW_PACKET.md.

## Completion condition (directive s12)

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Aether post-confirmation audit, bounded result | MET | rso/aether/audit/AUDIT.md: **57/57 MATCH**. All 64 units (8/8 CONFIRMED) are now fully replayed; 0 classes changed; verdict unchanged. Integrator re-run of RX 8219 equal; the R1c tamper was detected |
| 2 | Replay erratum | MET | rso/aether/ERRATA.md E1 (2 of 8, 8201 at 85e0cd7fb, 567d483e...), plus the follow-up (8 of 8). RESULT.md is untouched |
| 3 | Explicit disposition, both candidates | MET | rso/gen5/SELECTION.md |
| 4 | One selected or both rejected | MET: **none selected** | Crius: WORLD_DEMAND_NOT_QUALIFIED + DISCOVERY_INACCESSIBLE. Ananke: OWNER_UNAVAILABLE + NATIVE_RESULT_PENDING + POWER_PREREQUISITE_UNMET (right substrate; not rejected) |
| 5 | Deterministic adversarial kit tested | MET | rso/adversary/ (registry `adversarial-kit`): 21 REJECTED, 3 LIMITATION, 0 SURVIVED, 0 VACUOUS; 13/18 historical defects caught automatically; integrator mutant killed. Also run on the T040 evaluator: 12 REJECTED, 1 LIMITATION, 0 SURVIVED |
| 6 | Selected assay frozen with controls | NOT APPLICABLE | no substrate selected. The parts-suitability design exists as an owner-sign-off DRAFT (rso/gen5/ananke/eval/PREREG_DRAFT_PARTS_SUITABILITY.md), not a freeze |
| 7 | Independent challenge, or missing qualification recorded | **MISSING QUALIFICATION RECORDED** | there is no frozen Gen-5 assay to challenge, so no Q3 session ran (C-019-T050 SUPERSEDED). The kit's reviewer-measurement template (defects found only by the reviewer, reviewer hours, cost per new defect class) is therefore unfilled for Gen 5. The Crius gate, Aether audit and T040 evaluator are Q2 work with integrator checks, NOT Q3-qualified |
| 8 | Bounded native pilot if qualification permits | NOT PERMITTED | qualification does not permit it (C-019-T060 SUPERSEDED). No native search was run anywhere |
| 9 | Scientific and computational limitations preserved | MET | the sections below; each packet's own limitations; the registry NOT-FOR lists |
| 10 | Next experiment most likely to reduce uncertainty | MET | section "Next" |

## What Generation 5 found

**1. Aether's Gen-4 evidence gap is closed within its trust boundary.**
- The committed clamp evidence is reproducible under the pinned native execution implementation.
- This does not prove the native physics correct.

**2. Crius: the reuse advantage is real for a hand-built organism, the feared leak is not its cause, and discovery is
inaccessible.**
- In 4 of 5 frozen-seed lifetimes the stored procedure carries the advantage:
  - 49-50/50 vs 24-36 fresh;
  - ablation removes it, transplant carries it;
  - near-misses and memorisation gain nothing.
- In all worlds the advantage is byte-identical with the label hidden and calibration off.
- The frozen rule required 5/5, so the disposition is WORLD_DEMAND_NOT_QUALIFIED. The coordinator did not relax it.
- Native search cannot reach A: a one-link valley about 26 edits deep, 0/36 runs.
- So Crius can only demonstrate "a supplied module improves performance".

**3. Ananke: the directive's ladder had already been run by its owner, with a null.**
- PTE-C4: 0/168 two-stage solutions with no library, with duplication, and with a search-acquired RELAY/HOLD library.
- The designed halves of GATE gave 2/32.
- This is the most informative result for the Gen-5 question, and it is the owner's, not ours. It reads:
  - search-acquired one-stage parts did NOT make the two-stage capability more accessible;
  - correct parts make it rarely accessible;
  - the evolved parts were the wrong parts.

**4. The power problem is now quantified, and it gates everything.**
- A constructed positive at 2/32 needs 107 searches per arm (642 searches, ~44 GPU-h) for 80% power against 0.
- At 32 per arm the power is .05.
- Any acquisition-to-composition comparison on this architecture first needs a budget at which the constructed positive
  rises to >= .15-.20.

**5. Discovery vs supply (the operator's distinction) does not survive easily.**
- Even the best available design (parts-suitability) supplies the DECOMPOSITION: the half-task worlds are designed with
  GATE in mind.
- It uses an engine-team insertion operator as the inheritance channel.
- The external review packet asks reviewers to attack exactly this (R1, R2).

## Process record

**Seats** (headless, harry1). Models were verified over every assistant message; there were 0 fallbacks:

| seat | model | assistant messages | packets |
|---|---|---|---|
| Cadmus | Sonnet | 142 | T020, T021 |
| Eupalamus | Sonnet | 113 | T011 |
| Argus | Opus | 343 | T040, re-scoped at T030 to read-only Ananke preparation |
| Pallas | -- | -- | not launched: no frozen assay |

**Integrator checks.** Each packet got a reproduction and one mutation:
- **T021:**
  - the gate re-run was identical;
  - the observation-filter mutant SURVIVED, equivalent on the deciding worlds; it is a test gap only for W4, which
    never qualifies. Recorded.
  - `results/` was gitignored, so the evidence was force-added.
- **T011:** the run was identical; the vacuous-DUPLICATE mutant was killed.
- **T020:** an independent native replay of RX 8219 matched; the R1c tamper was detected.
- **T040:**
  - a non-sampled known-answer check re-ran bit-identical;
  - the USE-DISABLED mutant was killed.

**Owner contact.** Ananke was contacted (#2249, #2259) with no reply; it has been silent since 2026-10-09. Its champion
populations and C5T outputs were never opened. Nothing was written in its lane.

**Cost** (all local, harry1 CPU, $0, 0 GPU-h):
- Aether replay: 4,671 CPU-s.
- Crius gate plus ladder: ~5 min.
- Kit: < 1 CPU-h.
- T040: ~7.6 CPU-h.
- Integrator: ~0.4 CPU-h.
- Total: ~10 CPU-h.

**Registry:** 17 entries (+ adversarial-kit, + ananke-c4-independent-evaluator; the Aether entry was amended).

**D4:** the C-013 Astra and Fable reviews are recorded as NOT PERFORMED -- SUPERSEDED BY LATER EXPERIMENTAL EVIDENCE. The
packets are preserved.

## Next (each needs its own authority; ordered by uncertainty reduced per unit cost)

1. **Ananke's C5T outcome.** Zero cost; the data already exist with the owner. If its frozen kill rule fired
   (PTE_SEARCH_ARCHITECTURE_EXHAUSTED_FOR_COMPOSITION), the composition question on this architecture should close here,
   per the reviewer question Q4.
2. **Owner consent for the oracle re-evaluation of C4 champions.** Read-only, ~hours of CPU. It answers "would the
   instrument recognise partial composition?" for C4's null.
3. **The budget-calibration stage.**
   - Design: CONSTRUCTED-POSITIVE vs CONTROL at 72 and 144 generations, owner-run, ~26 GPU-h.
   - It decides whether any acquisition-to-composition comparison is affordable at all.
   - Only if the positive's rate rises does the parts-suitability ladder (draft) become worth freezing. That needs owner
     sign-off and a genuine Q3 challenge.
4. **Crius:** nothing further without a new charter giving the recorder/invoker halves a selective gradient.
5. **The external review** (GEN5 packet), particularly R1/R2. If reviewers judge that a designed decomposition makes
   "discovery" indistinguishable from "supply", the program needs a different experimental lever: e.g. inheritance
   within a lineage with no library, and no designed sub-worlds. It should not be another engine.
