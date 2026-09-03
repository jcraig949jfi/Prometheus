# Campaign 1 — PROPOSAL ONLY. Not launched. Not authorized. Deliverable 16 of the V0 brief.

**What this is.** The shape of the first population-generation campaign, written so a reviewer
can attack it before anything runs. Nothing below is scheduled. The addendum's disposition
withholds authorization for launch, qualification-world inspection, and self-operation, and
this proposal changes none of that.

## 1. Preconditions, all currently unmet

1. **A neutral experiment operator is assigned.** Proteus cannot run a qualification (A10/A9;
   addendum disposition). No operator exists as of 2026-09-02.
2. **The neutrality-gate disposition is ruled.** Three preregistered runs failed the gate as
   written; the surviving finding is "stationary away from the bounds, drifting toward the
   interior near them". A reviewer must say whether that is a ratchet. If it is, the grammar is
   not qualified and Campaign 1 does not start.
3. **Daedalus answers the four open items** in `contracts/SFE_INTEGRATION.md` §6 (payload
   granularity, meter-as-observation, encounter-id placement, checkpoint `info_kind`).
4. **A machine and a core count.** Generation and signatures are single-core Python; see §4.
5. Optional: the PEW client lands on `origin/main` so the export can be exercised, not just shaped.

## 2. What Proteus supplies

- A generation-0 population from a Foundry manifest whose `seed` is a public value chosen by the
  operator (not by Proteus) and recorded in the campaign's `CONFIG_IDENTITY.json`.
- For every organism: manifest, `organism_id`, `lineage_id`, runtime hash; the two Foundry
  signatures (transcript class, knockout vector) and the resource vector on the frozen probe
  ensemble; the degeneracy map per transcript class.
- A descent function the operator calls with its own mutation seeds and mates; every descent
  yields a lineage record. Proteus proposes no selection rule.
- The failure ledger for Foundry-local deaths.

Proposed size: 10^5 generation-0 organisms under the default Foundry manifest. This is a
proposal about instrument cost, not about what size is "enough"; §4 shows why it is cheap.

## 3. What the operator does, and what Proteus must not see

The operator binds the population to a world of their choosing through the ABI, runs encounters
as committed SFE experiments, applies whatever selection rule they preregister, and calls
`descend` to make the next generation. Proteus receives back only what SFE publishes to it:
identities. **Proteus does not receive transcripts from qualification worlds, does not receive
scores, and does not receive the world binding.** If the operator wants Proteus to change the
Foundry configuration between generations, that is a new frozen identity and a new neutrality
prereg, and the request must not carry qualification outcomes as its justification (A8).

## 4. Cost, measured on the V0 machine (single core, pure Python)

| step | measured | at 10^5 organisms |
|---|---|---|
| generation | 2,000 in 0.01 s (generation) | ~1 s |
| Foundry-local qualification on the 4-probe ensemble | 4,000 in 2.3 s | ~1 min |
| both signatures (1 + up to 9 knockout ensembles) | 4,000 in 16.5 s | ~7 min |
| one descent generation | 2,000 in <1 s | ~30 s |

Encounter cost is the world's and is not estimated here. Storage: ~0.5 MB gzipped per 1,000
organisms including rows and lineage; 10^5 is ~50 MB, which argues for the population-blob
option in the Daedalus questions rather than 10^5 artifact POSTs.

## 5. The bump protocol (brief §13–14), restated as the operator's obligations

When any organism or class is flagged by the operator's own criteria:
- Proteus **freezes** the manifest, lineage records, checkpoints and runtime hash (they are
  already immutable; freezing means: no further descent from it under this campaign identity).
- Proteus **emits** the falsification bundle: replay seed; the organism's neighbours under each
  of the thirteen operators (one application each, seeded); the nine single-class knockouts;
  the ancestor chain; matched fresh controls (same manifest limits, fresh random genome, same
  seed derivation).
- Proteus **stops** generating from it and says nothing about why it is not dead.

## 6. What would kill Campaign 1 before it starts

- The reviewer rules the bound-adjacent drift a ratchet: grammar unqualified.
- The operator cannot write a binding without a channel layout Proteus has authored: the ABI is
  then not usable as designed and needs review, not a Proteus-side layout.
- The population's silent fraction (79% on the Foundry probes) makes the operator's world unable
  to distinguish anything in generation 0: that is a fact about uniform initialisation and about
  the world, and the answer is more generations or a different world, never a Proteus-side
  initialisation prior chosen to look better.
