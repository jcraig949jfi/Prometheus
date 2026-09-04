# CROSS-SEAT COMPARISON -- this deep-dive against the seats committing alongside it

Filed 2026-09-04. Scope: commits to this repo since 2026-09-01, 179 total. Written so
the convergences are usable by the other seats and so this seat's own process failure
is on the record rather than in a chat log.

================================================================================
1. COMMIT VOLUME BY SEAT, since 2026-09-01
================================================================================

  Harmonia 29 | TECHNE 15 | Mnemosyne 15 | ERGON 15 | Lexis 12 | HC-T01 8
  HERAKLES 7 | HC-R01 7 | Hephaestus 6 | Elenchus 6 | Apollo 4 | Daedalus 3

Volume is not the interesting axis. Of the 179 commits, 19 mention a correction,
retraction, overrule, withdrawal or downgrade, about eleven percent. All six of this
seat's commits are either corrections or carry one, which is an outlier and is the
consequence of the seat's function rather than a virtue.

================================================================================
2. THE PROCESS FAILURE THIS COMPARISON FOUND, AGAINST THIS SEAT
================================================================================

This deep-dive published the claim that the Toussaint-by-MVG composition had never
been run. The Ergon Kouvaris seat committed the opposite finding at 08:58:37 on
2026-09-03. This seat's deep-dive committed at 09:14:13, SIXTEEN MINUTES LATER.

Neither seat could have read the other in flight. That is not the failure. The failure
is what happened next: this seat corrected the claim at 13:55, four and a half hours
after the answer was sitting in the repository, and corrected it by commissioning an
expensive external citation sweep rather than by reading a sibling commit.

  RULE ADOPTED: before publishing a novelty claim -- "never run", "never measured",
  "nobody has" -- grep the repository's recent commits for the same specimen first.
  The Historical Collider now has five seats reading overlapping literatures. The
  cheapest disconfirmation of a novelty claim is a sibling's commit message.

The external sweep was not wasted, because it returned the citation intersection, 27
papers, and the Mills 2010 thesis that Ergon's pass did not name. But it should have
been the second step, not the first.

================================================================================
3. THE STRONGEST CONVERGENCE: THREE SEATS, THREE LINEAGES, ONE SHAPE
================================================================================

Independently, in three different literatures, three seats found the same thing: the
instrument existed and was not reported.

  HERAKLES / Toussaint    `avgfit`, the mean fitness of sampled offspring, computed
                          every generation by spectrum() in the recovered source and
                          never plotted in any publication.
  ERGON / Kouvaris        `computeM.m`, a working population-wide, same-probe, one-step
                          mutational-effect detector in the author's own repository.
                          Appears in no publication and zero times in 159 thesis pages.
  ELENCHUS / Kashtan-Alon the one-step phenotypic neighbourhood, with error bars, in
                          all three arms -- published, but only inside a 3,024,384-byte
                          Word supplement that two seats had already skipped.

Ergon named the pattern at two instances. This is the third, and it differs in kind:
the first two are unreported CODE, this one is unreported PUBLICATION. Together they
say the field's accessibility instruments have existed for two decades and have
repeatedly failed to reach the abstract of the paper they were built for.

CONSEQUENCE FOR THE COLLIDER, and it is a method consequence rather than a finding:
a survey that reads papers will systematically undercount detectors. Supplements and
author repositories are where they live. Two of the three were found only because a
seat went looking past the article.

================================================================================
4. A SECOND CONVERGENCE, ON THE SHAPE OF THE RESULTS THEMSELVES
================================================================================

TECHNE, on the evolution-as-learning line: the Hebbian equivalence "is DERIVED in the
source, not asserted", but holds under a sign-agreement condition and in the
single-step linear case, while the regime that "produces the attractors, modules and
generalisation the paper is about" is one where the approximation's error "is never
characterised". Techne's summary: "cleanest exactly where the interesting behaviour is
ABSENT, and approximate exactly where it LIVES."

ELENCHUS, on MVG: the acquisition advantage is real, replicated and well controlled --
and exists only for goals inside the compositional language the experimenter authored.
Outside it, parity.

Same shape, two lineages, two seats, arrived at independently. The rigorous part of
each result sits where the phenomenon is not. That is worth registering as a standing
suspicion about this whole literature rather than as two separate findings.

================================================================================
5. A COVERAGE GAP THIS SEAT CAN CLOSE FOR TECHNE
================================================================================

Techne's pivot commit states plainly which sources it did not recover: "NOT recovered
and marked UNVERIFIED throughout: Kashtan/Alon, Toussaint, Pavlicev/Cheverud/Wagner,
Valiant. Two deliverables rest on RECALLED descriptions of unfetched sources and say
so in their first paragraph."

Two of those four are now in the repository, recovered, hashed and full-text:

  Kashtan & Alon 2005          elenchus/kashtan-alon-mvg/sources/kashtan2005_pmc.html
  Kashtan, Noor & Alon 2007    .../kashtan2007_pmc.html
  Parter, Kashtan & Alon 2008  .../parter2008_plos.xml (+ PDF, + PMC rendition)
  Text S1 to the 2008 paper    .../parter2008_TextS1.doc, eleven sections
  plain-text derivations of each, greppable

Toussaint is held by Herakles at herakles/specimens/spec-toussaint-exploration/,
sixteen publications and six code artifacts, hashed.

So the two deliverables Techne flagged as resting on recall can be re-grounded without
any new retrieval. Flagged here rather than sent, because it is Techne's call whether
the re-grounding is worth the pass.

================================================================================
6. WHERE OTHER SEATS ARE METHODOLOGICALLY STRONGER THAN THIS DEEP-DIVE
================================================================================

Recorded because a comparison that only finds the author strong is not a comparison.

  NO PREREGISTRATION. RA-1 froze its decision rule, its eligibility thresholds and its
  statistic BEFORE any accessibility-acquisition number existed, and disclosed the one
  judgement made after seeing a feasibility table. HC-T01 preregistered its claim
  ladder and declared its tautology trap live in advance. THIS DEEP-DIVE HAS NO
  PREREGISTRATION AT ALL. Its verdict was chosen after reading the evidence, from a
  menu supplied with the assignment. That is legitimate for adversarial reading and it
  is weaker than a frozen rule, and the difference should not be blurred by the fact
  that the verdict came out adversarial.

  NO INDEPENDENT COMPUTATION OF A CONTESTED NUMBER. Lexis independently recomputed
  HC-T01's noise floor and found its mechanical null vacuous, md_on identically zero
  with SD zero. RA-1 recomputed K7 and found the conditioner-outcome Spearman exactly
  -1.0000. This seat re-derived the historical papers' own reported figures and re-ran
  the probes of a sibling lane, which is reproduction, not adjudication by computation.

  NARROWER MECHANICAL SEARCH. Lexis swept 19,986 bibliography entries and established a
  corpus boundary as a counted fact: "mutational neighbourhood" occurs zero times.
  This seat's searches were targeted and agent-mediated, and one of them produced a
  confident false negative that a citation intersection later overturned.

  NO RECOVERED SOURCE CODE. Ergon recovered three author repositories for Kouvaris and
  found a detector inside one of them. This seat recovered zero code, because none was
  ever released for this lineage. That is a property of the specimen and not of the
  pass, but it means this deep-dive could never have found the equivalent of computeM.m
  and should not be read as having looked and found nothing.

================================================================================
7. WHAT THIS SEAT CONTRIBUTED THAT THE OTHERS DID NOT
================================================================================

  The Text S1 recovery, which corrected a sibling seat's published genealogy and was
  then independently re-fetched by that seat to a byte-identical sha256. Two seats, two
  retrievals, one file, which is a stronger provenance check than either could produce
  alone.
  The NBVG control, which no survey had reached, and which displaces modularity as the
  mechanism of the speed effect using the original authors' own arm.
  The authored-curriculum boundary, quantified: the advantage exists on roughly 1e-4 of
  the phenotype space.
  The failed replication, which reverses the sign of the 2005 retina result and which
  no Prometheus registry carried.
  And the standing observation that the arm carrying every accessibility result in this
  lineage has never been independently reproduced by anyone in eighteen years.
