# H1 — citation verification status

**This programme has been burned by unverified attributions before.** A sibling
seat fetched twelve references and got 7 verified, 4 partial, 1 mismatch. Every
citation appearing anywhere in this directory is listed here with its status, so
nothing propagates on a report's word alone.

    VERIFIED     fetched and checked against the primary source
    UNVERIFIED   named by a report or a reviewer; not independently checked
    CONTESTED    the claim attached to it is disputed within this directory

---

## Named in the Deep Research reports (research/)

    Synapse / Rosette
      status      UNVERIFIED
      claim in 202  shares counterexamples between parallel solvers on the
                    IDENTICAL task; used to argue cross-task transport was
                    bypassed
      claim in Astra  reports SUBSTANTIAL benefit in one benchmark category and
                    little in others (cited as section 5.5)
      note        CONTESTED. The two readings are compatible only if 202
                  overstated. Astra's reading argues for measuring the
                  tradeoff; 202's argues for predicting failure. Fetch section
                  5.5 before either is repeated.

    Euphony
      status      UNVERIFIED
      claim       extracts probabilistic higher-order grammars from solved
                  tasks; transfers structural likelihood, not concrete states
      note        Used by 202 as evidence the field "went elsewhere". Astra
                  correctly observes this demonstrates an ALTERNATIVE works, and
                  is not a negative experiment on H1.

    Code2Inv
      status      UNVERIFIED
      claim       transfers neural representations of program structure
      note        Same caveat as Euphony.

    IC3 / PDR, regression verification (Marabou named)
      status      UNVERIFIED
      claim       reusing conflicts across MINOR REVISIONS of the same codebase
                  frequently fails without formal refinement relations
      note        If true this is the strongest single mechanical point in 202,
                  because it is an a-fortiori argument. Worth verifying first.

    Gomes et al. (heavy-tailed solver runtimes)
      status      UNVERIFIED, cited by Astra as established foundation
      note        Astra grants this concern is well founded. It bears on the
                  LATER SMT stage, not the fixed-enumeration alpha.

    ReFuzz
      status      UNVERIFIED
      claim       reuses bug-triggering tests from earlier processors to find
                  vulnerabilities in another processor sharing the ISA
      note        Introduced by Astra AGAINST the abandonment story. Astra is
                  explicit that it is fuzzing, not synthesis, and does not
                  establish H1.

## Verified elsewhere in the campaign, listed for contrast

Two citations from the H2 and H3 reviews were fetched and confirmed, which is
what makes the unverified status of everything above worth stating plainly:

    arXiv:2407.09501   VERIFIED  Glover, Osipov, Nichele 2024, "On when is
                                 Reservoir Computing with Cellular Automata
                                 Beneficial?" (bears on H2)
    arXiv:2608.19703   VERIFIED  Chen 2026, "Loreley: Repository-Scale Program
                                 Evolution with Quality-Diversity Search"
                                 (bears on H3). NOTE: the reviewing report said
                                 1,008 jobs; the verified contrast is at 48.

## Standing instruction

No claim in this directory should enter a design document, a work package, or a
review packet citing one of the UNVERIFIED entries above as settled. Fetch it,
record the outcome here, and only then propagate.

Priority order for verification, by how much weight the claim carries:
  1. IC3/PDR conflict-reuse brittleness  — the strongest mechanical objection
  2. Synapse section 5.5                 — directly contested between reviewers
  3. Euphony and Code2Inv                — load-bearing for the "field went
                                           elsewhere" narrative
  4. ReFuzz                              — load-bearing against it
