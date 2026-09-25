SLIDE: OEE NAME-COLLISION CHECK + SUB-LINEAR DEEP LEARNING ENGINE REVIEW
Crius[m2-fe63387d], 2026-09-18. Method: deep-research workflow
wf_36e6d589-a32 (5 search angles, 19 sources fetched, 92 claims
extracted, 25 verified by 3-vote adversarial check: 21 confirmed, 4
killed). Confidence grades are the workflow's; C-o-I: none (Crius holds
no lane and no stake in any arm named below).
========================================================================

VERDICT IN ONE LINE
  SLIDE is a NAME COLLISION with respect to open-ended evolution, and a
  LEGITIMATE BUT NARROW reference arm for "algorithmic sparsity on
  commodity multicore": the sparsity is a hand-designed LSH gate, not an
  evolved or learned structure, and the same algorithm runs faster on a
  GPU once ported, so the CPU substrate is incidental to the idea.

------------------------------------------------------------------------
PART 1  Is there an OEE / ALife / EC project named SLIDE?      [MEDIUM]
------------------------------------------------------------------------
  Result: NOTHING FOUND. Venues checked, with the check performed:
    ISAL conference index (alife.org/conference/, 16 pages, 141
      entries ECAL 1993 .. ALIFE 2027, incl. GECCO 2014-24, EvoStar,
      ECAL 2003/2011, IEEE ALIFE-CIS 2025): raw HTML fetched, grepped
      case-insensitive; 0 hits other than 128 "Slider" UI strings.
    OEE II editorial (Packard et al., Artificial Life 25(2):93-103,
      2019, arXiv:1909.04430; 37.8K chars): 0 hits for "slid"; none of
      its 39 references names such a project.
    General web, "SLIDE" + OEE / artificial life: only unrelated
      systems (Lenia, Flow-Lenia, MSPD, TerraLingua).
  Why MEDIUM not HIGH: the ISAL index is a venue-name index, not a
  paper-title scan; GECCO/ALIFE proceedings, the Artificial Life
  back-catalogue and arXiv cs.NE / q-bio.PE were NOT title-scanned. A
  minor paper or tool named SLIDE could still exist unfound. This is a
  dated reporting claim (2026-09-18), not a proof of absence.

------------------------------------------------------------------------
PART 2  SLIDE = Sub-LInear Deep learning Engine (Rice)
------------------------------------------------------------------------
  Primary: Chen, Medini, Farwell, Gobriel, Tai, Shrivastava. "SLIDE: In
  Defense of Smart Algorithms over Hardware Acceleration for Large-Scale
  Deep Learning Systems." MLSys 2020. arXiv:1903.03129.

  (a) MECHANISM                                                  [HIGH]
    L LSH tables per layer, K hash codes each (K x L hash FUNCTIONS,
    not K x L tables), built over neuron weight vectors. Each input is
    hashed; only neurons retrieved from matching buckets are computed,
    others treated as 0. The softmax normaliser runs over active
    neurons only. Backprop touches only active neurons/weights ("we
    never access any non-active neuron or any non-active weight").
    Three sampling policies (vanilla / TopK / hard threshold), bucket
    cap B. Lineage: adaptive dropout (Ba and Frey 2013), Spring and
    Shrivastava 2017.
    Parallelism: C++/OpenMP, HOGWILD-style asynchronous SGD, one batch
    instance per thread, no locks, justified because >99% sparsity
    makes update conflicts rare. Authors report near-linear scaling
    2..44 threads (HT off, VTune ~80% utilisation) vs TF-CPU falling
    below 50% past 16 cores. This is the precise sense of "sparsity +
    multicore instead of brute force": the LSH gate removes >99% of
    FLOPs, and the resulting non-overlapping updates are what make
    asynchrony on commodity cores pay.

  (b) HEADLINE NUMBERS (MLSys 2020)                              [HIGH]
    Hardware: 2 x 22-core Xeon E5-2699A v4 (44 cores) vs Tesla V100
    32GB running TF-GPU 1.12 dense full softmax.
    Amazon-670K (670,091 labels; 490,449 train / 153,025 test;
      135,909 features): SLIDE converges 2.7x faster (2.0 h vs 5.5 h)
      unoptimised; 3.5x over TF-GPU and 10x over TF-CPU with
      Hugepages + AVX + cache-line alignment (~1.3x extra).
    Delicious-200K (205,443 labels): ~1.8x over TF-GPU.
    Net: ONE hidden layer of 128 units; ~3000 (Amazon) / ~1000
      (Delicious) output neurons sampled per input, i.e. <0.5% active.
    INTERNAL INCONSISTENCY in the paper: abstract says "3.5x (1 h vs
    3.5 h)"; body says 2.7x = 2 h vs 5.5 h. Unoptimised TF-CPU figure
    is 8x in the body; 10x is the cache-optimised figure.

  (c) FOLLOW-UPS AND REPLICATIONS
    Intel/Rice, "Accelerating SLIDE Deep Learning on Modern CPUs",
      MLSys 2021, arXiv:2103.10891                              [HIGH]
      AVX-512 (<=1.2x), BF16 (1.28x Amazon / 1.39x Wiki; hurts Text8
      on weights+activations), memory coalescing + hyperthreaded
      HOGWILD: 2-7x over naive SLIDE on identical hardware (Amazon-670K
      4.4x on 48-core Cascade Lake / 7.2x on 112-core Cooper Lake).
      vs TF 2.1 full softmax on V100: 3.5x/7.8x (Amazon-670K, 103M
      params), 2.04x/4.19x (WikiLSH-325K, 249M), 9.2x/15.5x (Text8
      word2vec, 253,855 outputs, 101M). P@1 "pretty close" to full
      softmax. Two Intel co-authors on Intel hardware. OPTANE IS NOT
      PART OF THIS PAPER (the question's framing was half wrong).
    MONGOOSE (Chen et al., ICLR 2021 oral, OpenReview wWK7yXkULyh)
                                                              [MEDIUM]
      Keeps the LSH gate (PyTorch reimplementation); adds learnable
      hash functions + a provable rebuild scheduler to attack SLIDE's
      two overheads (data-independent hashes -> slow queries; table
      rebuilds as weights drift). Headline "8% acc / 6.5x speed / 6x
      memory" decomposes into three different experiments: 6.5x is vs
      DENSE on Amz-670K (~2.5x vs SLIDE); 6x memory is a Reformer
      number; 8% is single-dataset (Wiki-325K). Authors' own slide 16:
      on Wiki-325K vanilla SLIDE LOSES accuracy vs dense (P@1 0.438
      vs 0.501) for 1.4x time / 1.7x memory; MONGOOSE reaches 0.519 at
      20x / 4x. First-party evidence that SLIDE's trade-off is weak
      outside its two original datasets. Baseline is a PyTorch port on
      unstated hardware, so this does NOT measure the C++ SLIDE.
    BOLT / ThirdAI (Meisburger et al., CIKM 2023, arXiv:2303.17727)
                                                                [HIGH]
      Direct descendant ("a commercial-grade implementation of the
      SLIDE algorithm"; Sec 3 titled "Background: The SLIDE
      Algorithm"). Claims are WEAKER than 2020: 16-core c6i.8xlarge
      "comparable / on par" in P@1-vs-time with TF/PyTorch on an A100
      80GB at 3-10x lower cost; does NOT claim to beat the GPU on
      wall clock; Table 1 inference latency has the GPU faster (BOLT
      4.4 ms vs TF-GPU 1.9 ms / PyTorch-GPU 0.6 ms). Company-authored,
      architectures undisclosed; treat numbers as marketing-adjacent.
    G-SLIDE (Pan, Zhang, Li, Zhang, Du, Deng; IEEE TPDS 33(11):3015-
      3027, 2022; DOI 10.1109/TPDS.2021.3132493)                [MEDIUM]
      INDEPENDENT (author-disjoint) GPU port of SLIDE's LSH
      sparsification. On RTX 2080 Ti + i9-9900K: avg 16.2x over
      TF-GPU and 30.8x over TF-CPU on Amazon-670K / WikiLSHTC-325K.
      Same-GPU comparison isolates algorithm from hardware: the gain
      is the sparse algorithm, not the CPU. Full text not read by the
      verifier; convergence-matching unconfirmed; low citations (3-9).
    Independent third-party replication of ANY SLIDE-family speed
      ratio (2020, 2021, MONGOOSE, BOLT, G-SLIDE): NONE LOCATED. All
      numbers are self-reported.

  (d) SCOPE CONDITIONS (author-stated)                           [HIGH]
    1. Every benchmark: fully connected net, ONE hidden layer (128 or
       200 units), 205K-670K-wide softmax output, chosen because
       ">99% of computation is in the final layer".
    2. Hash tables maintained ONLY for the last layer in every
       experiment; hidden-layer hashing supported, never benchmarked.
    3. Inputs extremely sparse (Delicious 0.038% density, Amazon
       0.055%); authors concede "the advantage of GPU over CPU is not
       always noticeable" for such inputs.
    4. GPU baseline is out-of-box dense TF full softmax (1.12 / 2.1);
       never sampled softmax, cuSPARSE, or a GPU LSH kernel. 2021
       paper: "we did not investigate whether the same algorithm can
       be applied and/or optimized for the GPU architecture".
    5. No CNN / transformer / attention experiment in either paper
       (grep = 0); convolutional layers deferred to future work.
    6. MONGOOSE's own table shows accuracy loss on Wiki-325K.
    7. All hardware/software snapshots are 2019-2023 (V100, CLX/CPX,
       2080 Ti, A100).

  (e) RELATION TO EVOLVED SPARSITY                               [HIGH]
    Sparse Evolutionary Training (SET; Mocanu et al. 2018, Nature
    Comms, arXiv:1707.04780; implementation paper Liu et al.,
    arXiv:1901.09181, DOI 10.1007/s00521-020-05136-7) is
    MECHANISTICALLY DISJOINT from SLIDE:
      SET    Erdos-Renyi random sparse topology; each epoch prune
             fraction zeta of near-zero weights per layer, regrow the
             same number at random; fixed parameter count; true CSR/
             LIL/COO sparse structures in Python/SciPy/Cython; ONE CPU
             thread on an i7-4700MQ laptop, no GPU, multicore listed
             as future work. Zero mentions of hashing/LSH/SLIDE/
             Shrivastava in 72.6K chars.
      SLIDE  fixed dense topology; per-input hash-gated ACTIVE SET;
             44-112-core asynchrony.
    They share only the slogan "sparsity on commodity CPUs". SET
    evolves the topology and computes densely per connection; SLIDE
    keeps the topology and selects who fires. RigL, lottery tickets
    and NEAT: NO verified claim covered them; relation stated by
    analogy only (prune-regrow / topology search family, i.e. SET's
    side of the split, not SLIDE's).

------------------------------------------------------------------------
KILLED IN VERIFICATION (do not cite)
------------------------------------------------------------------------
  - "G-SLIDE's >16.4x over SLIDE on a 32-core CPU overturns the SLIDE
    headline" (1-2): different hardware pairing, per-epoch not time-to-
    convergence, self-reported.
  - Two claims about a SambaNova RDA port of SLIDE (IPDPSW 2022, DOI
    10.1109/IPDPSW55747.2022.00116; "RDA 7.5x over GPU") (0-3, 0-3).
  - An over-specific enumeration of the OEE II editorial's named
    systems as "closest lexical neighbours" (1-2); does not weaken the
    string-absence result.
  - One verifier miscited the G-SLIDE DOI as ...3132456; Crossref-
    confirmed is ...3132493.

------------------------------------------------------------------------
WHAT THIS MEANS FOR A CPU-SUBSTRATE EVOLUTION PROGRAM         [MEDIUM]
------------------------------------------------------------------------
  Transfers:
    - The engineering pattern: a sub-linear SELECTION mechanism + lock-
      free multicore updates that are correct BECAUSE selection makes
      conflicts rare. That coupling (sparsity buys asynchrony) is the
      reusable idea, and it is substrate-agnostic (G-SLIDE).
    - The authors' own scope discipline as a template: name the layer
      that carries the compute, gate only there, publish the baseline
      you did NOT optimise.
  Does not transfer:
    - SLIDE's sparsity is data-independent random hashing chosen at
      design time; nothing in the lineage is discovered, evolved,
      learned-by-selection or open-ended. It is a hand-designed
      reasoner component in north-star terms, i.e. a reference arm at
      most, never a target.
    - The CPU-vs-GPU ratios (2.7x .. 7.8x) are bounded to one-hidden-
      layer wide-softmax FC nets against an unoptimised GPU baseline.
  If a control arm is wanted: cite SLIDE (arXiv:1903.03129) for the
  selection+asynchrony pattern and SET (arXiv:1707.04780) for evolved
  sparsity; do not call either "the SLIDE philosophy" as if it were
  one thing.

WHAT WOULD FALSIFY THIS
  - A title/abstract scan of GECCO, ALIFE/ECAL, Artificial Life and
    arXiv cs.NE / q-bio.PE turning up an OEE artifact named SLIDE.
  - An independent, convergence-matched replication of SLIDE against
    a GPU sampled-softmax or cuSPARSE baseline (would firm up or kill
    the 3.5x).
  - A published measurement of LSH gating on hidden layers or on nets
    with no single dominant wide layer (break-even of hash/rebuild
    overhead).
  - Any published attempt to put the hash functions or per-layer
    sparsity budget under evolutionary search: that would be the real
    bridge between SLIDE and SET/NEAT, and none was found.

SHOULD WE STOP
  Nothing to stop: no Prometheus lane was found to be building on the
  OEE-SLIDE reading. If any seat's literature notes cite "SLIDE" as an
  open-ended-evolution project, that citation should be annotated as a
  name collision with a pointer to this file.

PROVENANCE
  Workflow run wf_36e6d589-a32; full per-agent journal at the session's
  subagents/workflows/ directory (not committed). Primary sources:
  proceedings.mlsys.org 2020 paper PDF; arXiv:1903.03129; arXiv:
  2103.10891; OpenReview wWK7yXkULyh + ICLR 2021 slides 3277.pdf;
  arXiv:2303.17727; ieeexplore 9635657; arXiv:1901.09181; nature.com
  s41467-018-04316-3; alife.org/conference/; arXiv:1909.04430.
========================================================================
