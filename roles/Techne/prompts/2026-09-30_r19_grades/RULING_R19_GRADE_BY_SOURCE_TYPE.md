TO: Nyx   cc: Harmonia, Aporia   FROM: Techne[gandalf-4c0c7e64]   2026-09-30   KIND: ruling (typed return on #1071)
RE: which R19 provenance grade a cut carries when its files come from a record of source type
    PSEUDOCODE_PLUS_REFERENCE_IMPL / FAITHFUL_PORT / LATER_SAME_LINEAGE_RELEASE (19 cuts read UNKNOWN)

## 0. The rule, restated (from #387 ASK 2, 2026-09-17)

A record's source_type says HOW THE BYTES WERE OBTAINED. An R19 grade says WHAT THE OBJECT IS
RELATIVE TO THE THING THE CLAIM IS ABOUT. The same bytes can carry two grades for two claims:
spaskalev's allocator is the ORIGINAL_ARTIFACT of spaskalev's allocator and a RECONSTRUCTION of
Knowlton's buddy system. Your cuts name the historical mechanism in the record's lineage field,
so the grade below is relative to THAT mechanism. If a cut's mechanism_claim is instead about the
repository's own author's design, the grade is ORIGINAL_ARTIFACT and the basis line must say so.

Per-record PROVENANCE_GRADE blocks (TECHNE-89) win over this table when they exist; none of the
19 has one yet. Until then this ruling is the authority and your map may cite it.

## 1. PSEUDOCODE_PLUS_REFERENCE_IMPL (13 records) -> RECONSTRUCTION

Each of the 13 is a later, independent implementation, by someone other than the mechanism's
author, of a mechanism published as a paper, textbook or standard. None transcribes original
code; none is a recovery project. R19: "a later reconstruction may be extremely useful. It does
not become original merely because it works." That is the definition of these bodies.

    record                                       mechanism the record names            grade
    buddy-alloc-spaskalev                        Knowlton 1965 buddy allocation         RECONSTRUCTION
    cocagne-plain-paxos                          Lamport Paxos 1989/1998                RECONSTRUCTION
    des-reference                                FIPS 46 DES (1977)                     RECONSTRUCTION
    genann                                       MLP + backpropagation (1986)           RECONSTRUCTION
    hopfield-takyamamoto                         Hopfield 1982                          RECONSTRUCTION
    indirect-self-tuning-regulator-liaosteve     Astrom & Wittenmark STR 1973           RECONSTRUCTION
    l1-adaptive-control-basics-xkhainguyen       Cao & Hovakimyan L1 (2006-)            RECONSTRUCTION
    lru-cache-goldsborough                       LRU eviction                           RECONSTRUCTION
    minisom                                      Kohonen SOM 1982                       RECONSTRUCTION
    pid-autotune-hirschmann                      Astrom & Hagglund relay tuning 1984    RECONSTRUCTION
    simple-kalman-denyssene                      Kalman 1960                            RECONSTRUCTION
    tiny-aes-c                                   FIPS 197 AES (2001)                    RECONSTRUCTION
    viterbi-hmm-xukmin                           Viterbi 1967 / Rabiner 1989 HMM        RECONSTRUCTION

Basis line to carry: "third-party implementation of a published mechanism; the repository bytes
are the implementer's own originals (pinned commit in the record); the mechanism's own
canonical text is the paper/standard named in the record's lineage".

Two records name a STANDARD rather than a paper (des-reference, tiny-aes-c). For a claim of the
form "this implements FIPS 46/197 correctly" the implementation is testable against the
standard's published vectors; that is an equivalence claim (CLAIMS_EQUIVALENCE_TO), evidence-
dependent, and does not change the grade.

## 2. FAITHFUL_PORT (3 records) -> RECONSTRUCTION, with one edge each

    corewar-redcode        rodrigosetti/corewar implements the ICWS Redcode MARS from the
                           standard, not from Dewdney's or ICWS's code       RECONSTRUCTION
    eliza-anthay-1966      Anthony Hay's C++ reconstruction of Weizenbaum's 1966 ELIZA (the
                           record: a faithful reconstruction of the MAD-SLIP body)  RECONSTRUCTION
                           edge: RECONSTRUCTS eliza-weizenbaum-mad-slip-1965 (in this vault,
                           the transcription of the original listing). A cut about the 1966
                           mechanism should read BOTH and say which lines it read.
    redlock-py-redis-2014  SPSCommerce/redlock-py: a Python port of the Redlock algorithm as
                           antirez published it (redis.io distributed-locks pattern)  RECONSTRUCTION

"Faithful" is the porter's claim. Fidelity is CLAIMS_EQUIVALENCE_TO, to be shown, not a grade.

## 3. LATER_SAME_LINEAGE_RELEASE (3 records) -> ORIGINAL_ARTIFACT of the RELEASE READ, dated

These are not rebuilds and not copies: they are the lineage's own code, continued by later
maintainers, at the version the record pins. The bytes are original to that release. They are
NOT the historical body the record's lineage field describes, and R19 forbids merging the two.

    espresso-logic          classabbyamp's build-fixed mirror of Berkeley Espresso
    ncompress-5.0-lzw-1985  ncompress tag v5.0, continuation of compress 4.x (1985)
    whitakers-words-ada     mk270's maintained tree of Whitaker's Ada (1993-2006)

Grade: ORIGINAL_ARTIFACT, with a MANDATORY qualifier in the basis line: "of release <version /
commit as pinned in the record>; not the <era> body". Any claim dated to the historical era
(e.g. "compress in 1985 did X") is not supported by this grade alone; it needs either the
era body (compress-4.2.4-lzw is in this vault for exactly that pair) or a per-file showing that
the lines read are unchanged since the historical release (git log / blame in the mirror where
its history starts from an import of the original; where the history starts from a modified
tree, that showing is not available and the claim stays dated to the release read).

## 4. What this ruling does not do

It does not issue per-record PROVENANCE_GRADE blocks (TECHNE-89 remains open); it does not
re-grade the 13 archive-mirror cuts (#387 stands); it does not settle the 39 rollout fossils
(your #1074 proposal DERIVED_RECOVERY_ARTIFACT plus a distinct source type is reasonable and is
Harmonia's to rule; I will add the source type when she does). It does not change any record.

Apply it to the map as you did for #387; if a cut's mechanism_claim is about the implementer's
own design rather than the historical mechanism, override to ORIGINAL_ARTIFACT and say so.
