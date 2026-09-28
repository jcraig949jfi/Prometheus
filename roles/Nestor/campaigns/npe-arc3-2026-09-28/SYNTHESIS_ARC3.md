# ARC3 synthesis: endogenous heredity, reproductive machinery, environmental scaffolding (Nestor, 2026-09-28)

- **Directive:** `roles/Nestor/prompts/2026-09-28_arc3_endogenous_heredity_portfolio/` (sha256 2b2aeca0). Theory-aware by
  date; not offered as Selective-Irreversibility evidence.
- **Durable state:** `roles/Nestor/EXPERIMENT_GRAPH.jsonl` (ARC3 nodes X-A3-*, C-A3-*), `roles/Nestor/FINDINGS.md`
  (sections "ARC3 ..."), `BACKLOG_ARC3.md`, `work_packages/`, `delegates/`.

## Headline

**The ARC3 central question has a first, confirmed, partial answer: yes, for one scaffold.**
- In the default CARRIED world, reproductive lineages that start out dependent on environment-supplied register
  values **recurrently come to set up those values themselves** (C-A3-INTERNALIZE: 8 of 144 fresh runs, frozen bar 4).
- **Self-location does not follow suit.** Every SELF-free copier is anchored to absolute tape positions, and true
  locators are vanishingly rare (2 of 332 copiers, one motif).

The environment's contributions therefore split. Register initialization is **internalizable scaffolding** and is
internalized. Placement / self-location has so far behaved like **support the lineages never replace**.

## 1. Acquisition

**What controls access to reproductive machinery is carrier exposure: the frequency of copy-capable genomes times
how long they persist.**
- The one-byte alias acts mainly through persistence.
- A planted two-byte copy decays from ~210 to <21 carriers per 256.
- A one-parameter hazard fitted on one arm predicts the other (PLANT 28.6 vs 32 observed; DENSE 54.8 vs 49).
- Block-write density alone does nothing (X-P2-SHAM 0/96). Presence alone, while it lasts, does a lot (X-P2-PLANT 32/96).

The landscape (delegate):
- There are no competent genomes among random genomes or their one- and two-step mutants.
- Copiers sit on broad neutral networks (72-80% of 1-step mutants stay competent).
- Partial copiers are stepping stones (22-27% become competent in one step).
- Losing the copy instruction is a trap (0/144 recovered).

## 2. Establishment

After removing the ruler circularity (X-A3-FAIR; treatment-blind ruler over entry states zero / 0x5A / random):
- **Zero-specialization is real, not a ruler artefact.** The default world discovers zero-only donors under a fair
  ruler (26 of 49 first-donor genomes).
- **Specialization tracks whatever the world supplies, over time** (0x5A world: 346 0x5A-only vs 24 zero-only donors
  late).
- **Literal zero is special for establishment** (runaway 23/48 under ZERO vs 3/48 under 0x5A), because zero supplies
  geometry-aligned self-location (HL = 0 = own start at offset 0).
- **Net:** "zero-state specialization" = specialization to environment-supplied values, which pays off most when those
  values double as the organism's own address.

## 3. Descendant competence

X-A3-AUTOPSY: after a certified copy, the dominant loss is the **child's material** (C3), in both worlds (0.51 / 0.63
of losses C1->C6).
- Only 6-11% of certified copies are exact.
- Execution inheritance (a valid child with an unusable start state) is minor: 5/63 CARRIED.
- Every child reached its next execution.
- In NPE, genome copying and organism reproduction largely coincide; the post-copy bottleneck is **copy fidelity**.

## 4. Endogenous transition

- **Candidate 7ae3 16000006 was KILLED as a single-change transition** (knock-in 0/5, revert 0/8, cross-graft 0/12).
- The same reconstruction showed **robustness arose within the lineage by distributed change**: 118-126 replications,
  49-54/64 bytes, lost and regained on 6/8 paths, with the copier fixing its own destination.
- Re-framed as "state-freedom", it recurred:
  - X-A3-ENDOSTATE-R: population share 0.32 -> 0.65;
  - X-A3-SFLINEAGE: 3/5 lineages by descent;
  - **C-A3-INTERNALIZE: CONFIRMED on fresh runs, 8/144.**
- The class is real. The single-mutation story is not.

## 5. Self-location

What the organism supplies versus the environment (transplant delegate, 332 copiers):
- All 280 SELF-free copiers fail when moved >= 16 bytes; they use absolute addresses.
- 210/332 need the 128-byte wrap.
- 33/52 SELF users still copy to a fixed destination.
- Only 2 true locators (seed 16000026: SELF, LD D,L; LD E,D, LDDR) work at any offset, on other tape sizes and from
  random registers, and never self-poison.
- The environment supplies placement and geometry. The organism supplies, at most, register setup.

## 6. Environmental scaffolding

| Environmental contribution | Class (current evidence) | Internalized? |
|---|---|---|
| Register initialization (zero reset / never-written zeros) | SCAFFOLDING | **YES, recurrently** (C-A3-INTERNALIZE) |
| Tape placement / offset | SCAFFOLDING in principle (a true locator exists) | Almost never (2/332) |
| Tape geometry (128-byte wrap) | SUPPORT / PHYSICS for current copiers | Not observed |
| Copy primitive availability | PHYSICS (the instruction set) + accessibility (carrier exposure) | n/a |
| Execution order / partner | Partner is not used by copiers (transplant T4); side-1 hijack exists | n/a |

[X-A3-WITHDRAW, gradual vs abrupt withdrawal of the zero reset: PENDING at the time of writing.]

## 7. Accessibility landscape

- Search does not change accessibility within these horizons; persistence of carriers does (s1).
- Architecture class predicts little beyond **state-freedom**, which strongly predicts state robustness (3/179 vs
  74/143 self-poison; p = 1.5e-28). The class catalogue was stopped there.

## 8. Random / neutral baseline

- Pilot (delegate): a matched neutral mutation walk reaches competence at about the soup's rate (ratio 1.75, p = 0.20).
- No evidence yet that soup variation-selection adds anything to FIRST APPEARANCE beyond material availability. Its
  visible advantage is spread.
- The full fair comparison is designed and portable (WP-9, ~9 CPU-h).

## 9. External research (what changed)

- **No published program-soup case of internalization after scaffold removal.** Designed reproducers degrade to cheaper
  copiers that exploit leftover registers (Tierra, Baugh 2015). NPE's confirmed internalization of register
  initialization is therefore NOT the literature's default. It is worth scrutiny and replication.
- **Bourrat 2022:** internalization only when one trait pays under the scaffold and replaces it. Register self-setting
  fits that: it works under zeros and replaces them.
- Every published soup supplies self-location through its resets. NPE's non-internalization of placement is the
  expected outcome.

## 10. Cross-engine

- **Artemis (#793) and Odysseus (#803): P-11 certifies construction, not heredity** (painters pass). This was the most
  consequential external pressure of ARC3.
  - The Cycle-9 S1-C counts were qualified: 2/57 genuinely self-copy.
  - The W1/P2/ARC3 corpora screen clean (DOM max 0.28).
  - CVT-R heredity certification was requested (#802).
- **Aphrodite:** the accessibility law generalizes as carrier exposure (T-XE-APH-1).
- **Odysseus** independently ranks NPE's "copiers set their own registers" among the three strongest Z80-family
  acquisition cases.
- **Ananke:** its evolved state-normalization precedent (T-M3-1) now has an NPE counterpart.

## 11. Delegation

| Delegate | Result |
|---|---|
| External | contradicting evidence first (no internalization precedent) |
| Forensic | killed the single-change candidate, found the ruler defect, found distributed within-lineage change |
| Self-location | placement is environmental; register setup is not |
| Accessibility | corrected MY description of the mutation operator (no indels; 7ae3 opcodes never mutate: an erratum on P2); carrier-exposure model; neutral pilot |
| D2 build | built the opaque successor seal |

Disagreements: the accessibility delegate's operator description contradicted mine, and mine was wrong. The forensic
delegate's verdict (KILLED) disagreed with my framing of the candidate as a transition, and it was right in the
single-change form.

## 12. Backlog

`BACKLOG_ARC3.md`:
- 11 new Threads.
- T-STATE-1 ANSWERED/CONFIRMED.
- T-END-1 killed in its single-change form.
- New T-DC-5 (copy fidelity: do lineages evolve more exact copying?).
- Ruler Threads for P-11 heredity (CVT-R) and the cycle-aware self-state ruler.

## 13. Leases / queue

| Run | Lease | Queued behind | Ran |
|---|---|---|---|
| X-A3-FAIR | cpu8 host lease file | Ananke W-I (until ~03:07) | 03:07-05:06 |
| X-A3-AUTOPSY | cpu8 | FAIR | 05:06-05:28 |
| C-A3-INTERNALIZE | cpu8 | AUTOPSY | 05:28-07:31 |
| X-A3-WITHDRAW | cpu8 | C-A3-INTERNALIZE | 07:32-[PENDING] |

- Re-prioritized: WITHDRAW moved behind the confirm (queue health).
- Repaired before launch: WITHDRAW's ruler (cycle-aware).
- Every acquire and release is announced on comms and logged in `roles/Nestor/LEASES.jsonl`.
- [Final release confirmation: PENDING.]

## 14. Research-ready inventory

- P2's WP-1..6 remain valid (WP-1, WP-2 and WP-4 advanced here).
- ARC3 adds:
  - WP-7: tape-rotation world, to withdraw the self-location scaffold;
  - WP-8: descendant execution inheritance;
  - WP-9: full neutral baseline, PORTABLE;
  - WP-10: candidate-transition assay;
  - WP-11: architecture comparison;
  - WP-12: external scaffolding synthesis, REPO.

## 15. NPE's current value

NPE is a substrate in which reproduction is **mostly supplied by the environment** yet lineages **measurably take
over part of that supply**. The tools separate internalized from supplied machinery:
- a reset-policy world axis;
- fair entry-state rulers;
- transplantation;
- lineage-tagged state-freedom.

Its unique lens is **which scaffolds are internalizable, at what rate, and by what route (descent vs replacement)**. It
now also carries a documented ruler lesson for the program: P-11 certifies construction, not heredity.

## 16. HITL

[To be finalized after X-A3-WITHDRAW; see the final report.]
