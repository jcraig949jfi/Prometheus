# DETECTOR GENEALOGY

Where the MVG accessibility instrument came from, and what that means for the Historical
Collider's claim that the local-longitudinal cell is empty.

Method note: the ancestry below is not recalled. It is read from the reference list of the
retrieved 2008 publisher XML at the exact citation points where the instrument is defined.
Standing gate 4 of the Historical Collider README requires date-stamping any "nobody has
measured this" claim; this file exists to make that possible for accessibility detectors.

================================================================================
1. THE CITATION POINT
================================================================================

The 2008 paper introduces its detector with three citations attached:

  "we considered the phenotypic neighborhood [37]-[39], defined as the set of phenotypes
   that are accessible from a given genotype by a single point mutation."

Resolving [37], [38], [39] from the article's own reference list:

  [37] Dichtel-Danjoy ML, Felix MA (2004). Phenotypic neighborhood and micro-evolvability.
       Trends in Genetics 20:268-276.
  [38] Fontana W, Schuster P (1998). Continuity in evolution: on the nature of transitions.
       Science 280:1451-1455.
  [39] Stadler BM, Stadler PF, Wagner GP, Fontana W (2001). The topology of the possible:
       formal spaces underlying patterns of evolutionary change.
       Journal of Theoretical Biology 213:241-274.

So the instrument is NOT an Alon-lab invention. Parter/Kashtan/Alon 2008 is an APPLICATION
of a named, pre-existing concept with a formal literature behind it, and the paper says so
at the point of use.

================================================================================
2. THE ANCESTRY, AND WHY [39] IS THE ROOT
================================================================================

Stadler, Stadler, Wagner & Fontana 2001 is the formal foundation: it constructs the
topological spaces in which "what is reachable from here" is the primitive object, rather
than a distance or a fitness. Fontana & Schuster 1998 supplies the empirical predecessor in
RNA -- the observation that transitions between structures are continuous or discontinuous
depending on the accessibility structure of the neighbourhood. Dichtel-Danjoy & Felix 2004
supplies the term itself and ties it to micro-evolvability in a biological setting.

Parter/Kashtan/Alon's contribution on top of that inheritance is threefold and should be
credited precisely:
  (a) they measured it EXHAUSTIVELY rather than by sampling, because their genome is short
      enough (B = 104, 76) to enumerate every 1-mutant;
  (b) they made it LONGITUDINAL -- tracked as a trajectory over 1e5 generations across
      30-40 replicate runs, which none of the ancestors did;
  (c) they built a scalar summary (the FV measure) that permits the trajectory to be
      plotted and compared across treatment arms at all.

(b) and (c) together are what lifts this lineage to D3/D4. The concept was inherited; the
longitudinal population measurement was not.

================================================================================
3. THE DEFINITIONAL TRAP, RESOLVED FOR THIS SPECIMEN
================================================================================

The house registry (Q_DETECTOR_PARTS_REGISTRY.md) warns that "accessibility" is overloaded:
Hu and Banzhaf's accessibility is a sum over INBOUND transition frequencies to a phenotype,
which is inbound, phenotype-indexed and landscape-global, whereas the ladder concerns an
OUTBOUND, individual-indexed, local quantity -- what is reachable from here. The registry
notes that matching on the word alone mis-classifies work in both directions.

Adjudicated for this specimen: the MVG phenotypic neighbourhood is OUTBOUND,
INDIVIDUAL-INDEXED and LOCAL. It is anchored to a specific wild-type genotype, enumerates
its 1-mutants, and asks what phenotypes THEY produce. It is on the ladder's side of the
trap, not Hu and Banzhaf's. Its ancestry through Stadler et al 2001 is the outbound formal
tradition, which is consistent.

This matters because it means the classification is not a word match. It is the quantity
the ladder is about.

================================================================================
4. OTHER INSTRUMENTS THE 2008 PAPER INHERITED
================================================================================

  genetic variance via entropy      Adami C, Ofria C, Collier TC (2000), PNAS 97:4463-4468
                                    -- used for the mechanism-(c) test that FAILED
  pleiotropy / modularity framing   Griswold CK (2006), Evol Dev 8:81-93
  RNA neutral-network search        Sumedha, Martin OC, Wagner A (2007), Biosystems 90:475
  RNA folding engine                Hofacker IL (2003), Vienna RNA secondary structure
                                    server, Nucleic Acids Res 31:3429-3431
  modularity measure Q              Newman-Girvan, via Kashtan & Alon 2005 [33]

Two of these are worth flagging. The Vienna RNA server is a live external dependency: the
RNA half of the 2008 result is only reproducible against a specific folding implementation,
and folding energy models have changed since 2003. And the Adami entropy measure is the one
used for the leg of the framework that did not replicate, so its negative result is
inherited-instrument-mediated and should not be over-read.

================================================================================
5. CONSEQUENCE FOR THE HISTORICAL COLLIDER
================================================================================

The Collider's killable question asks how often the local offspring / reachable
distribution was measured REPEATEDLY ACROSS POPULATION LINEAGES such that changes in future
accessibility can be reconstructed over evolutionary time.

For this specimen the answer is: at least once, in 2008, with 30-40 replicates and reported
standard errors, on a substrate small enough to enumerate the neighbourhood exhaustively,
under an intervention that does not touch the variation operator.

DATE-STAMP, per standing gate 4: as of 2026-09-03, on the evidence retrieved in this pass,
the local-longitudinal accessibility cell is NOT empty and has not been empty since 2008.
Any Collider document asserting otherwise should be corrected. What remains genuinely
unoccupied, in this lineage and in Toussaint's and in Kouvaris's alike, is D5: a
perturbation OF the accessibility structure, with acquisition measured after.

================================================================================
6. SEARCH STATUS -- DESCENDANTS AND CORRECTIONS
================================================================================

Honest statement of coverage, because an incomplete search that presents as complete is the
failure this file is meant to prevent.

DONE, from retrieved primaries: the ancestry above, resolved from the 2008 reference list
at the citation point.

RETURNED, and the results are in DESCENDANTS_AND_REPLICATION.md. Summary of what the pass
changed:

  - A peer-reviewed FAILED REPLICATION exists and is now the strongest item against the
    lineage: Clune, Beckmann, McKinley & Ofria 2010 (GECCO), on the retina arm, with a
    direct-encoding control, sign reversed. The earlier draft of this file recorded no
    such literature.
  - The circuit arm has never been independently replicated or refuted by anyone. Every
    accessibility result quoted in this deep-dive lives in that arm.
  - Two candidate challenges were REMOVED as challenges after checking: Hintze & Adami
    2008 (their environments vary randomly -- the authors disclaim it themselves) and
    Crombach & Hogeweg 2008 (no sub-goal decomposition at all).
  - The Toussaint composition is ASSERTED IN PRINT and never run: Fernando, Szathmary &
    Husbands 2012 name Toussaint's non-trivial neutrality as the enabling condition for
    the Parter/Kashtan/Alon effect, citing the same 2003 thesis the house specimen uses.
  - Kouvaris 2017 cites Toussaint only in a bulk background bracket with zero body-prose
    mentions, so the MVG-to-Kouvaris link established in MVG_VS_KOUVARIS_MATRIX.md
    remains STRUCTURAL, not citational.
  - Effect size corroborated externally at "nearly an order of magnitude", consistent with
    the ~10x worked example and NOT with the 700x headline, which is conditioned on the
    hardest goals only.

STILL UNVERIFIED after the pass: Hoverstad 2011 (publisher 403/418); any PNAS Letter
responding to the 2007 paper; the five TREE comments on Watson & Szathmary 2016; and
Kashtan's PhD thesis -- the Weizmann repository returned empty shells for all queries
INCLUDING CONTROLS, so its absence from that repository is not evidence of anything. A
full forward-citation sweep of Toussaint's thesis was blocked by HTTP 429.

None of this affects the verdict, which rests on the authors' own Figure 6E null and their
own NBVG control, both verified from retrieved bytes. It affects USE: the specimen is
single-laboratory and contested, and is downgraded accordingly in
SFE_MVG_CALIBRATION_PROPOSAL.md.
