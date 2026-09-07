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
    A3[WP-A3 first NK series · Archaeon issues, Vivarium runs · S]
    A4[WP-A4 shared-table relatedness C-1 · later]
  end
  subgraph B[Branch B · symbolic execution]
    B1[WP-B1 program_eval_v0 on Proteus VM · Proteus lib + Vivarium kind · M]
    B2[WP-B2 opcode-bijection null + witness-withheld control · Archaeon · S]
    B3[WP-B3 rounds-to-match, two arms · Archaeon, Harmonia · S]
    B4[WP-B4 PATH B input channel · Proteus+Harmonia · L]
  end
  subgraph C[Branch C · spatial stateful]
    C1[WP-C1 ca_density_v0 from EvCA verifier · Herakles lib + Vivarium kind · S/M]
    C2[WP-C2 reflection null + r=0 / T=1 controls · Archaeon · S]
    C3[WP-C3 random rules vs historical genomes · Archaeon, Harmonia · S]
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
  X1 ==> A3 & B3 & C3
  X7 ==> A3 & B3 & C3
  A1 ==> A2 ==> A3
  B1 ==> B2 ==> B3
  C1 ==> C2 ==> C3
  P0 ==> P1
  P2 ==> P1
  P3 ==> P1
  X2 -.~~>.- P1
  X2 -.~~>.- B1
  B4 -.-> A4
  A3 <-.later bridge.-> C4
  C3 <-.later bridge.-> P1
  X6 --> A3 & B3 & C3
  X8 --> X7
  X5 --> B3 & P1
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

A  INTERACTING LANDSCAPES      A1 nk_landscape_v0 (M) ==> A2 null+control (S) ==> A3 first series (S)
                               A4 shared-table relatedness .......... later, behind a stateful organism
B  SYMBOLIC EXECUTION          B1 program_eval_v0 on Proteus VM (M) ==> B2 (S) ==> B3 two-arm rounds-to-match (S)
                               B4 PATH B input channel (L) ......... prerequisite for organism/transfer claims
C  SPATIAL STATEFUL            C1 ca_density_v0 from EvCA verifier (S/M) ==> C2 (S) ==> C3 random vs historical (S)
                               C4 IC-vs-rule coevolution ........... later bridge to D
D  POPULATION ECOLOGY          P0 spike (2 days) ==> P1 soup or backend (M); P2 unit vocabulary (S) ==> P1;
                               P3 neutral kernel by detailed balance (M) ==> any diversity claim

Later bridges:  A3 <-> C4 (a landscape the IC distribution co-evolves on)
                C3 <-> P1 (rule populations under resource competition)
                B4 --> A4 (a stateful organism makes relatedness a transfer experiment)
```

**Reading the graph.** Three branches (A, B, C) are independent of each other
and of D; each is three increments deep to its first bounded experiment; each
first experiment needs only the integrity packages, the analysis convention,
and its own directed template. Nothing in A, B, or C waits on the population
branch, on the external backend, or on relatedness. The population branch is
the only one that begins with a spike rather than a build, because nothing
runnable exists for it.
