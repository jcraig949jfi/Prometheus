# T-007 -- candidate continuity criterion (stated BEFORE any application; E-002)

Executor: Artemis (fresh Claude session, ubu002), 2026-09-27. Sources read to write this, all in Git:
- the operator ruling, roles/Archaeon/prompts/2026-09-27_contract_v02/00_OPERATOR_RULING_verbatim.md s2: "ILL_POSED: the requested singular
  identity is not well-defined ... e.g. symmetric recombination where **neither contributor has privileged continuity**";
- the contract, archaeon/causal_lens/CAUSAL_LINEAGE_CONTRACT_v0.2.md s1, s5; schema_v02.continuity() (v0.2.1);
- the regression, V02_REGRESSION_REPORT.md s3-s4: "Continuity under a symmetric operator should be ILL_POSED BY MECHANISM (the
  operator privileges no parent), not by counting"; review packet s13 ("the rule is a proposal and is untested") and Q2.

The record names the candidate but never states it precisely. This file states it. Nothing below was tuned on T-008..T-011 data.

## Incumbent (comparator), C-MAJ = v0.2.1 as frozen
hu_continuity = MAJORITY(threshold 0.5, strict) over the REALIZED factual shares of the whole output. Exact tie -> ILL_POSED. Unknown
mass -> NOT_IDENTIFIABLE unless a strict known majority exists.

## Candidate, C-OP ("ill-posed by mechanism")
Continuity is decided by the role structure of the GENERATIVE OPERATOR first, and by realized shares only where the operator
privileges a role.

1. **Operator declaration.** Each recombining operator O is declared with its contributor roles and its exchangeability relation. Two
   roles are exchangeable if O's output distribution is invariant when the two inputs are swapped, with O's randomness at its
   declared distribution. The declaration is read from engine CODE (basis DECLARED, with a code reference), never from outcomes.
2. **Missing declaration.** If O is undeclared or cannot be checked against code, hu_continuity = NOT_IDENTIFIABLE. It is never
   ILL_POSED: the J6 logic applied to the operator.
3. **Exchangeable operator.** Group the contributors into exchangeability classes over DISTINCT HUs. If two or more distinct HUs with
   nonzero realized contribution fall in one class, hu_continuity = ILL_POSED. The justification is {operator, class, code ref}. Realized
   shares are NOT consulted. Note: a self-cross, where both roles hold the same HU, is one HU, so continuity of that HU is decided.
4. **Privileged operator.** If O privileges a role, the declared hu_rule of that operator applies (PRIVILEGED_PARENT, or C-MAJ over
   factual shares). This part is unchanged from v0.2.
5. **Separate from architecture.** C-OP says nothing about architecture_class (J17 stands).

## What would count as C-OP failing (pre-declared; T-010 searches for these)
- **F1, invented ill-posedness.** An exchangeable operator yields a child that is materially (almost) one parent, for example a mask
  of 15/16 or 16/16 from a. C-OP calls it ILL_POSED even though "this is a's lineage" plainly has content. The case would be worse
  if an independent architecture reading agreed with a.
- **F2, inherited invented continuity.** Under privileged operators C-OP falls back to C-MAJ, so a privileged operator with a thin
  realized margin would still be "decided" on noise.
- **F3, declaration dependence.** The verdict depends entirely on a declaration that the evidence may not contain (the synthetic
  fixtures record shares, not operators).
- **F4, causally inert shares (affects C-MAJ and C-OP's fallback).** Where the two parents carry identical material at a position,
  the mask bit is causally inert: flipping it leaves the child byte-identical. v0.2 counts such positions into the realized shares
  (FF-33's correction). If the answer changes when only inert bits are flipped, it is not a fact about the child.

## The meaningfulness tests used to judge BOTH criteria (independent of either)
- **M1, invariance.** A singular answer must not change under transformations that leave every input and output material
  identical: swapping the labels of exchangeable roles, and flipping causally inert mask bits.
- **M2, distinguishability from the operator's null.** The realized share must lie outside what the operator produces when it
  privileges nobody. For uniform crossover over n units, that is Binomial(n, 1/2), and the claim is two-sided at alpha = 0.05.
- **M3, external agreement (weak, B7-limited).** Where a non-saturated architecture reading exists (the parents' behaviour differs),
  it should agree with the singular answer more often than chance.

M1 is a logical test. M2 is statistical. M3 is empirical and only as good as the architecture criterion (T-011).
