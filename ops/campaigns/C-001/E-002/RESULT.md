# E-002 RESULT (T-012) -- B1: hereditary continuity under recombination

Executor: Artemis (fresh Claude session on ubu002, from Git alone), 2026-09-27. Detail: T-007_CRITERION.md, T-008_T-011_RESULTS.md.

## Adjudication of B1
B1 was "REPRESENTABLE, RULE INADEQUATE". **That verdict stands, and the inadequacy is now located precisely.** The proposed repair
("ILL_POSED by mechanism") is **right in the bulk and wrong at its edges.**

1. **C-MAJ is not merely ill-conditioned: its "decided" answers are mostly not facts about the child.**
   - 10 of its 15 "decided" GA crossovers can be reversed by flipping only mask bits that leave the child byte-identical (M1).
   - 0/16 GA crossovers have a difference-making share distinguishable from the operator's own null (M2).
2. **The record's one ILL_POSED PTE case is a self-cross**, a genome crossed with itself. Its continuity is trivially well-posed.
   4/16 GA crossovers are self-crosses, which C-MAJ read as three "decisions" and one "tie". Correct: "1/16 exact tie" -> "4/16
   self-crosses (single parent); 12 real crossovers".
3. **The "3/48 match behaviour" statistic carries no information.** Behavioural architecture is NOT_IDENTIFIABLE for all 48:
   - 24 have two ceiling parents with identical signatures;
   - the 3 matches are ceiling matches;
   - the rest are mostly broken mosaics.
   The ruling's hypothesis ("ILL_POSED continuity with a meaningful architecture class") is **untestable** with a saturating
   criterion, not refuted. The record said "not supported".
4. **Pure C-OP invents ill-posedness (F1).** Exact parent copies (mask 16/16) and near-copies that keep the parent's exact behaviour
   are called ILL_POSED. It also needs an operator declaration that no synthetic fixture carries (F3).

## When is a singular parent-lineage answer meaningful? (the E-002 question)
**Supported on PTE plus the NPE/Archaeon data in Git.** A singular answer is meaningful only when all three hold:
- **(a) Distinct difference-making material.** The contributors differ where the child is concerned. Self-crosses, and positions
  where the parents are identical, carry no lineage information: the child is the same whichever way they are attributed.
- **(b) Departure from the operator's unprivileged null.** Under an exchangeable operator, the child's difference-making share
  lies outside what the operator produces when it privileges nobody. Uniform crossover over n units gives Binomial(n, 1/2).
- **(c) Complete evidence for (a) and (b).** Otherwise the answer is NOT_IDENTIFIABLE.

When (a) holds and the evidence is complete but (b) fails under an exchangeable operator, the singular answer is **ILL_POSED**. It is
not "decided", and architecture does not rescue it. Where (a)-(c) hold, the answer is the majority contributor, and every
non-ceiling behavioural identity observed agreed with it.

Scale:
- For PTE's operator on 16 instructions, the null puts only 2.1% of crossover children in the (b) zone at alpha 0.05 (k <= 3 or
  >= 13).
- Non-ceiling behavioural identity was observed only at k <= 2 (p ~ 0.004).
- Nearly every real PTE recombinant therefore has no singular parent.

**Proposed rule C-OP'** (a proposal for a future contract revision; NOT adopted, and NOT tested outside PTE):
- apply clause 3 of C-OP only after collapsing identical contributors and excluding inert units;
- lift ILL_POSED when the difference-making share clears the declared operator null at a declared alpha.
The alpha is a free choice. Behaviour suggests about 0.005 rather than 0.05; that suggestion is not tuned or frozen.

## What survives, what changes, what is unresolved
Survives:
- ILL_POSED as a value;
- J6/J7/J17;
- "no singular lineage" as the typical outcome of symmetric recombination;
- the principle that the operator, not the count, is what makes the question ill-posed.

Changes:
- the 1/16 tie becomes a self-cross;
- 3/48 becomes uninformative;
- "not supported" becomes "untestable here";
- pure operator-level ILL_POSED gets two exceptions: distinct-HU collapse, and null departure.

Unresolved:
- **F2, privileged operators with thin margins.** No case appears in Git: the Archaeon sample is >= 27/32, and NPE is decided only
  at >= 0.906. The full distributions are on M2.
- What the null is for a privileged operator.
- **Architecture continuity under recombination has no usable criterion** in PTE: behavioural ones saturate, and graded ones track
  fitness.
- Whether C-OP' holds in any second substrate.

## New threads exposed
- **Contribution has two referents: FLOW vs DIFFERENCE.** FLOW asks which source the operator copied a unit from (mask, taint).
  DIFFERENCE asks which source's distinguishing material the child carries.
  * PTE v0.1 counted DIFFERENCE. FF-33 "corrected" it to FLOW; that swapped one referent for the other and did not fix an error.
  * The NPE v0.2 adapter uses DIFFERENCE (same-value mass NI).
  This is the B4/B6 pattern applied to material contribution: a candidate break, B8.
- **B7 generalises.** A behavioural class anchored to a ceiling parent is not an identity. Graded behavioural distance is confounded
  with fitness. Recombination-era architecture needs a structural or non-saturating criterion (already an observatory ask).
- **PTE-internal (for Ananke, not the lens).** 16-instruction programs rarely survive mixing: mid-share mosaics mostly collapse to
  chance. Self-crossing runs at 1/(trunc*pop), 1/4 at pop 16.

Proposed false-friend rows, for Archaeon's ledger. I did not edit that ledger:
- "exact tie" = self-cross;
- "same_as_a" with a at the ceiling = "perfect";
- "nearer parent by behaviour" = "nearer in fitness".
