# Dependency and complexity graph

Annex to `archaeon/docs/ROADMAP.md` §Diversity. 2026-09-07. `==>` required,
`-->` helpful, `~~>` alternative route, `<->` later bridge between families.
Effort: S under a day, M a few days, L longer. Work-package detail in
`WORK_PACKAGES.md`.

```mermaid
flowchart LR
  subgraph G0[Integrity, required by every branch]
    WP0a[WP-0a F-1 executor refuses length mismatch · Daedalus · S]
    WP0b[WP-0b F-4 degeneracy guard · Vivarium · S]
    WP0c[WP-0c both arm seals from one value · Vivarium+Daedalus · S]
    WP0d[WP-0d D3 null number explained · Archaeon · S]
    WP0e[WP-0e kind-generic spec builder E18 · Archaeon · M]
    WP0f[WP-0f result_schema per kind I-1 · Vivarium · S]
  end
  subgraph GX[Cross-cutting]
    X1[WP-X1 analysis-family convention C-5 · Harmonia · S policy]
    X6[WP-X6 novelty reserve R1 · Archaeon · S]
    X8[WP-X8 descriptor archive R2 · Archaeon · M]
    X7[WP-X7 per-family directed template + frozen control · Archaeon · S each]
    X2[WP-X2 external_backend contract C-4 · Vivarium · M]
    X5[WP-X5 PEW witness column + edge writes I-8 · Mnemosyne · S]
  end
  subgraph A[Branch A · interacting landscapes]
    A1[WP-A1 nk_landscape_v0 · Daedalus exec + Vivarium kind · M]
    A2[WP-A2 permutation null + k=0 control templates · Archaeon · S]
    A3a[WP-A3-acq NK corpus acquisition via random route · Archaeon issues, Vivarium runs · S]
    A3b[WP-A3-cmp frozen NK comparison · needs frozen corpus + protocol + qualified detector]
    A4[WP-A4 related landscapes + source-artifact transfer · Daedalus, Harmonia · M]
  end
  subgraph B[Branch B · symbolic execution]
    B1[WP-B1 program_eval_v0 on Proteus VM · Proteus lib + Vivarium kind · M]
    B2[WP-B2 opcode-bijection null + witness-withheld control · Archaeon · S]
    B3a[WP-B3 frozen route · frozen evidence, canonical M-SIGNAL endpoint]
    B3b[WP-B3 adaptive route · precommitted policy, own protocol, never called M-SIGNAL]
    B4[WP-B4 PATH B input channel · Proteus+Harmonia · L · gates claims on THAT population only]
  end
  subgraph C[Branch C · spatial stateful]
    C1[WP-C1 ca_density_v0 from EvCA verifier · Herakles lib + Vivarium kind · S/M]
    C2[WP-C2 reflection null + r=0 / T=1 controls · Archaeon · S]
    C3a[WP-C3-hist historical reproduction · C1-e]
    C3b[WP-C3-acq random-rule corpus via random route]
    C3c[WP-C3-cmp frozen selection evaluation]
    C4[WP-C4 IC-distribution vs rule coevolution · later]
  end
  subgraph D[Branch D · population ecology]
    P0[WP-P0 replicator spike: Avida build / soup / hct01, double-run · Vivarium+operator · 2 days]
    P1[WP-P1 replicator_soup_v0 or backend · conditional on P0 · M]
    P2[WP-P2 unit=generation vocabulary · Harmonia+Daedalus · S]
    P3[WP-P3 neutral-kernel qualification by detailed balance · Harmonia · M]
  end
  WP0e ==> A2 & B2 & C2
  WP0f --> A1 & B1 & C1
  A1 ==> A2 ==> A3a ==> A3b
  A1 ==> A4
  B1 ==> B2 ==> B3a
  B2 ==> B3b
  C1 ==> C2 ==> C3b ==> C3c
  C1 ==> C3a
  X1 ==> A3b & B3a & C3c
  X7 ==> A3b & B3a & C3c
  P0 ==> P1
  P2 -.gates analyses using units.-> P1
  P3 -.gates neutrality claims.-> P1
  X2 -.~~>.- P1
  X2 -.~~>.- B1
  A3b <-.later bridge.-> C4
  C3c <-.later bridge.-> P1
  X6 --> A3a & B3a & C3b
  X8 --> X7
  X5 --> B3a & P1
```

Plain-text form, for terminals and diffs:

```
[BENCH TODAY] one qualified world (24-bit seeded onemax), 3 kinds,
              1 informative walk axis, scalar outcome rule + within-run
              aggregate (branch), no witness, no relatedness, no population

INTEGRITY (every branch; not diversity work)
  WP-0a F-1 refuse length mismatch ........ Daedalus ........ S
  WP-0b F-4 degeneracy guard under reset .. Vivarium ........ S
  WP-0c one arm value -> both seals ....... Vivarium+Daedalus S
  WP-0d D3 null fire-rate explained ....... Archaeon ........ S   (before M-SIGNAL)
  WP-0e kind-generic spec builder (E18) ... Archaeon ........ M   ==> every non-bitstring template
  WP-0f result_schema per kind (I-1) ...... Vivarium ........ S   --> every new kind checkable

CROSS-CUTTING
  WP-X1 analysis-family convention (C-5) .. Harmonia ........ S   ==> any cross-observation claim
  WP-X6 novelty reserve (R1) .............. Archaeon ........ S   --> new families get draws
  WP-X8 descriptor archive (R2) ........... Archaeon ........ M   --> region seeds for directed templates
  WP-X7 directed template + frozen control  Archaeon ........ S/family ==> closes the fossil->selection loop per family
  WP-X2 external_backend contract (C-4) ... Vivarium ........ M   ~~> alternative route for B1, P1
  WP-X5 PEW witness column + edge writes .. Mnemosyne ....... S   --> queryable witness, lineage

A  INTERACTING LANDSCAPES      A1 nk_landscape_v0 (M) ==> A2 null+control (S) ==> A3-acq corpus (random route)
                                                                              ==> A3-cmp frozen comparison (X1, X7, qualified detector)
                               A1 ==> A4 related landscapes + source-artifact transfer (mapping + baselines; no runtime memory needed)
B  SYMBOLIC EXECUTION          B1 program_eval_v0 on Proteus VM (M) ==> B2 (S) ==> B3 frozen route (M-SIGNAL) | B3 adaptive route (own protocol)
                               B4 PATH B input channel (L) ......... gates claims relying on that population/channel ONLY
C  SPATIAL STATEFUL            C1 ca_density_v0 from EvCA verifier (S/M) ==> C2 (S) ==> C3-acq random-rule corpus ==> C3-cmp frozen evaluation
                               C1 ==> C3-hist historical reproduction (separate qualification report)
                               C4 co-development .................. bounded design/spike may precede full C3 qualification
D  POPULATION ECOLOGY          P0 spike (operator-capped) ==> P1 route (M); P2 units gate ANALYSES using them;
                               P3 neutral baseline gates CLAIMS needing neutrality; descriptive execution proceeds

Later bridges:  A3-cmp <-> C4 (a landscape the IC distribution co-evolves on)
                C3-cmp <-> P1 (rule populations under resource competition)
```

**Reading the graph (amended).** Three branches (A, B, C) are independent of
each other and of D. Each first **corpus acquisition** needs only its
library/kind, the generic builder, local integrity checks, the admitted
random route and its null/control semantics. Each **frozen comparison** needs
a frozen corpus/universe, the approved protocol, correct provenance/units and
the qualification of the detector used. No pure-library test waits on B4, P3
or D3. Dependencies are local: 0a gates affected candidates, 0d gates D3
claims, P2 gates analyses using its units. The population branch begins with
a spike because nothing runnable exists for it.
