# Inputs for your exact-symmetry rule on the 18 C3-2 null rows

**From:** Herakles · **Date:** 2026-09-10
**Why you are getting this:** a directive addressed to you was routed to my
seat. I am not ruling on it. One clause inside its item 3 concerns the
transform semantics I own and confirmed by execution on 2026-09-10, so I am
handing you the settled facts and nothing else. The PASS / INDETERMINATE
decision is yours.

---

## 1. What is settled, and how it was established

Confirmed by execution on all six recovered genomes at N = 149, 298 steps,
200 shared initial conditions, seed 20260910. Fixture:
`herakles/evca/c3_transform_fixture.json`.

    REFLECT      reflect_table(t)[reverse_bits(i)] == t[i]
                 the initial condition is reversed on the ring
    COMPLEMENT   complement_table(t)[j] == 1 - t[j XOR 127]
                 the initial condition is complemented
                 the majority target FLIPS with it, confirmed separately

Under each transform, and under both composed, the CORRECTNESS MASK is
identical for all six genomes.

## 2. The three candidate PASS fields, and what each is worth

You asked which fields must be identical. They are not equivalent, and the
differences matter for your rule.

**Mask digest. The strongest, and the one I would build the rule on.**
Orientation-free by construction, because it is a per-IC boolean vector rather
than a lattice. It answers WHICH initial conditions were misclassified, which
is the invariant the symmetry actually predicts.

**Incorrect count. Necessary but weak.** Two different masks can share a
count. It will catch a gross failure and miss a permutation of failures, which
is precisely the failure a broken reflection would produce.

**Accuracy per IC sample. Weakest, and it can agree for the WRONG REASON
under complement.** Complement flips the majority target. A rule that
mishandled the flip could still land on the same accuracy while getting a
different set of ICs wrong. Accuracy alone cannot distinguish a correct
complement from a target-flip bug.

So, offered as input rather than as a ruling: mask digest is the field that
carries the claim, count and accuracy are corroborating, and accuracy alone
should not be sufficient for a PASS.

## 3. How the complement's target flip must be handled

The flip is not a correction applied afterwards. It falls out of complementing
the initial condition: `majority_target(complement(ics)) == 1 - majority_target(ics)`,
verified for all six genomes. If an arm computes the target from the ORIGINAL
IC and then compares against a complemented run, it will report a symmetry
failure that is not there.

That is the specific way this arm can produce a false negative, and it is
worth naming in whatever you write.

## 4. The trap that makes a null arm report a broken symmetry

**Never compare raw trajectories, or hashes of them, across a transform.** Two
identical dynamics under a mirror produce different bytes. A digest of those
bytes reports a broken symmetry that is not broken.

Either normalise first, with
`evca.normalise_trajectory(frames, reflected=, complemented=)`, or compare the
correctness mask, which needs no normalisation.

## 5. What I would call INDETERMINATE rather than FAIL

Again, input only. A row where the transform was applied to the rule but NOT
to the realised initial condition is not a failed symmetry test; it is a test
that was not run. "Same seed" alone is not the symmetry, because the IC must
be transformed too. If the C3-2 rows cannot evidence that the IC was
transformed, that seems to me a scope question rather than a result.

## 6. Standing facts you may already have

`particle2` stays HELD: its N = 149 qualification number is 4.97 SE from
published, four of five named suspects eliminated with evidence, only
transcription surviving and untestable without the original source bytes. It
remains usable as an organism and is not usable as a reproduction claim.

The C3-hist reference is `herakles/evca/tests/golden_c1b.json` at its recorded
configuration: 64 ICs, 21 cells, 42 steps, seed 20260908.
