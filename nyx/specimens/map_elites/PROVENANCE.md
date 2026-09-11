# MAP-Elites -- provenance

Currency: 2026-09-11 (opened). Grades: T1 committed artifact here or a
resolver-verified DOI; T2 remembered citation, not yet resolved; T3
hearsay. NYX-05 regrades every T2 after the resolver pass; until then a
T2 row is a claim about where the mechanism came from, not a fact.

## Ancestry chain as read on 2026-09-11

1. Mouret and Clune, "Illuminating search spaces by mapping elites",
   arXiv:1504.04909, 2015. The archive-over-a-behaviour-grid mechanism
   with uniform parent selection from the archive. T2.
2. Cully, Clune, Tarapore, Mouret, "Robots that can adapt like animals",
   Nature 2015, doi:10.1038/nature14422. The archive as a repertoire that
   a later process (damage recovery) searches; the reason the archive was
   useful. T2.
3. Vassiliades, Chatzilygeroudis, Mouret, CVT-MAP-Elites, IEEE TEC 2018,
   doi:10.1109/TEVC.2017.2735550. Replaces the grid with a centroidal
   Voronoi tessellation because the grid's cell count explodes with
   descriptor dimension: the failure that motivated the variant. T2.
4. pyribs (Tjanaka et al., GECCO 2023, doi:10.1145/3583131.3590374), the
   implementation pinned in this repository. T2 for the citation; T1 for
   the pin: techne/acquisition/locks/pyribs-cp312-win-amd64.lock.txt.
5. Techne's adapter techne/h3_retention/adapter.py: declares
   TIE_POLICY = FIRST_WRITER_WINS and verifies it against the installed
   pyribs at both granularities before any replay; logs every
   disposition (RETAINED_NEW_CELL, RETAINED_IMPROVED_CELL,
   REJECTED_BY_ARCHIVE, CAP_REFUSED_COUNT, CAP_REFUSED_BYTES,
   SKIPPED_NO_SCORE); refuses to report a cap it did not exercise. T1.
6. Techne's qualification receipt
   techne/acquisition/receipts/adapter_qualification-pyribs-20260911T064705Z.json:
   n=150 stream, grid 4x4, measures PRE-BINNED because pyribs GridArchive
   bins by equal width and cannot express Archaeon's equal-mass declared
   edges (widths 60.5 / 4.0 / 4.0 / 59.5 on axis 0); 10 of 150
   descriptors outside the declared edges. Stage ADAPTER_QUALIFICATION;
   the receipt itself says it does not establish INSTALLATION,
   FIRST_USEFUL_CHECK, PAPER_REPRODUCTION or LOCAL_SCIENTIFIC_BENEFIT. T1.
7. Archaeon's archaeon/producer/h3_replay.py: the `behavioral` policy is
   an independent, numpy-free re-implementation of the same mechanics
   (fixed-descriptor grid, one cell one item, strictly better replaces,
   first-writer-wins on exact ties, declared as the policy). T1. Two
   implementations of one mechanism inside the repository is itself
   evidence about which parts are the mechanism and which are pyribs.

## What is NOT established by this chain

- That any of the four papers say what row 1-4 attribute to them, until
  NYX-05 resolves the DOIs (T2 rows).
- That the local implementations reproduce any published result: the
  receipt says PAPER_REPRODUCTION is not established, and nothing here
  claims otherwise.
- Any benefit of the mechanism to Prometheus: LOCAL_SCIENTIFIC_BENEFIT
  is explicitly not established by Techne's receipt, and this dissection
  adds no measurement.

## Lineage rule for descendants

Any organ record under this directory carries provenance.ancestor
"MAP-Elites" and at least one T1 source; a descendant mutated inside SFE
keeps this file's path in its refs. The famous name confers nothing.
