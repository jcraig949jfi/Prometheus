# CVT-R reconciliation for the NPE ancestry replay (Nestor, 2026-09-29; MWO-0001 NESTOR section)

**Purpose.** Keep construction/dependence certification DISTINCT from hereditary transmission in everything this replay
reports. This is not an ancestry verdict: that is Archaeon's synthesis, pending. This record narrows no claim; it
bounds what may be claimed.

## 1. What CVT-R established (Artemis #891; prereg 77bc0dbce, result d050937ec)
| set | accepted |
|---|---|
| (a) 32 P2 donors | 23/32 |
| (b) 100 W1 q1-competent | 83/100 |
| (c) 16000006 epoch-700 modal | 8/8 |

- **19 P-11-certified genomes FAIL CVT-R.** 11 fail at generation 2: the copy carries the parental change but does not
  pass it on. 8 fail the recurrence clause only.
- **They are competent CONSTRUCTORS, not heredity carriers.** P-11 certifies that the donor BUILT the victim half
  (construction and dependence). It does not certify that variation is transmitted across generations.
- **Recorded as a QUALIFICATION** in roles/Nestor/FINDINGS.md: every earlier "competent donor" statement is a construction
  claim.

## 2. How it applies to this replay
- **The replay's births are P-11 predecessor acceptances.** The T-003 specimen (4931614d912c52b2) was NOT in any CVT-R set,
  so none of its births is CVT-R-certified.
- **The attribution layers measure construction and dependence ONLY:**
  - L1: written;
  - L2: causally donor-written (R1 identified);
  - L3/L4: construction chains built from the P-11 native parent pointer (erratum in GATES.json).
- **Heredity is L5 alone:** the Q4 recert of the child genomes (Odysseus, #813) or CVT-R. It has not been measured.
- **Descriptive observation from the committed production exports** (instrument-level, not a result):
  - All **29/29** distinct child genomes have a dominant-byte share >= 0.75, and **27/29** are dominated by 0x36 (the
    specimen's LD (HL),0x36 idiom).
  - That is the PAINTING signature, which P-11 is known to certify as construction (Artemis #793; Odysseus #803).
  - For comparison, the earlier DOM screen of the W1/P2/ARC3 corpora maxed at 0.28.
  - Only 2 of the 29 children later appear as a parent (L3), and that is a construction chain.
- **Consequence for reporting:**
  - no statement from this replay may say "inherited", "transmitted", "heredity" or "lineage carries" on the basis of
    L1-L4 or P-11;
  - such statements need L5 evidence on the specific child genomes;
  - the replay can support claims about WHO BUILT WHICH BYTES and WHAT THEY DEPENDED ON, within the validated scope (G2
    fields; ctrl_slice and pdom excluded).

## 3. What would change this
- A CVT-R or Q4 PASS on the specific T-003 child genomes (the list is in exports/*.summary.json "child_genomes_for_Q4").
- Until then, heredity from this replay is **NOT MEASURED**. It is neither refuted nor supported.
