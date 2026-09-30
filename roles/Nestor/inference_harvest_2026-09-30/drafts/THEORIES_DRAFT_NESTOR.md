# Nestor's independent theory draft (written before reading the adversary reports)

Frozen as-is for provenance. The final deliverable is NPE_COMPETING_THEORIES.md, which resolves this draft against the
adversaries. Evidence keys refer to dossiers A–G.

## T1. Search and reachability: mutational supply times exposure
- **Claim.** Every NPE transition is a first-passage event in genotype space.
  - Its rate is the density of functional genotypes within mutational reach, times the number of trials: population ×
    time × effective mutation rate.
  - Selection shapes what persists, not what appears.
- **Copying.** It appears when a 2-instruction motif is reachable: about 1e-5 per random genome on the stock VM (D U2),
  far more once an alias or a plant makes the motif common (C-DENSE-COPY 1/64 vs 39/64; PLANT 32/96; SHAM 0/96).
- **Internalization.** It appears after takeover (8/8, E 6.1) because takeover is what supplies trials.
- **The ffa6 > 7ae3 difference.** It is the mutation operator: 7ae3 opcodes are immune, giving 34 vs 239 effective
  mutations per lineage in 2000 epochs.
- **Existing-data check (harvest, this session).** Among the 15 established runs whose founders were not state-free:
  - ffa6: 7 internalization events over about 975k lineage organism-epochs, a hazard of about 1 per 140k;
  - 7ae3: 1 event over about 1,150k.
  - The ratio of about 8x matches the operator ratio of about 7x with no fitting.
  - Caveat: organism-epochs, not copy events; the 7ae3 figure rests on n = 1.

## T2. Scaffold tracking: the world supplies reproduction, and organisms take over what the world supplies unreliably
- **Claim.** The world defines reproduction:
  - placement at offset 0;
  - HL = 0 as the address;
  - BC = 0 as the long periodic count;
  - the 64-byte geometry;
  - pairing, write-back, and register carry-over.
- A lineage internalizes exactly the supplied functions that become unreliable in its current world. It never internalizes
  reliable ones.
- **Evidence.**
  - CARRIED makes the zero registers unreliable, and the lineage then sets its own destination (LD DE,3200).
  - Placement is always reliable: 280/280 SELF-free copiers are tape-anchored, and there are 2 locators in 332.
  - Specialization follows the world supplied (X-A3-FAIR: K_ONLY under 5A; ZERO_LITERAL).

## T3. Compact copy instruction: the representation does the work
- **Claim.** A complete "replicator" is 2 instructions (`1E 40 E5`), and everything else is environment plus passengers.
  - State-freedom is the addition of a few register-setting immediates.
  - The core is the copy opcode.
  - Painters are degenerate fixed points of the same instruction semantics (0x36 = LD (HL),n with n = the opcode).
  - Heredity carries about 0 bits without the supplied block copy: 10/500 BYTEWISE survivors, all near-homopolymers.
- **Organization** is a word for motif plus scaffold.

## T4. Reproductive organization: a self-maintaining process
- **Claim.** The hereditary unit is a lineage process, not a byte string. It:
  - regenerates its own material (most bytes are made by the lineage; founder bytes run 3–33% and fall steadily);
  - conserves function while turning material over (the e160 LDIR→LDDR flip, and 9cba LDIR re-created at 55-56);
  - maintains a core by purifying selection;
  - reorganizes by DISTRIBUTED multi-site change when the scaffold becomes unreliable (16000006: 49-54 bytes; single
    knock-ins 0/5).
- **Establishment** is a takeoff into a self-sustaining regime: bistable depth, with no single-founder run between 22 and
  161.

## T5. Frequency-dependent collective (Allee / kin-pairing)
- **Claim.** The reproducer is the lineage in the population, not the organism.
- On the pair tape, erosion by non-kin partners sterilizes small lineages (write-back changes 57% of member interactions).
  A copier paired with its own copy is not eroded: writing a copy onto a copy changes nothing.
- As the lineage becomes common, self-pairing rises, erosion falls, and copying accelerates. The result is an Allee
  threshold: win given ≥ 8 members 7/9; ≥ 16: 5/5; losers stop writing by epoch 12.
- The same frequency dependence explains why internalization only follows takeover. Only a majority lineage meets itself
  often enough for kin-conditional functions, including data-as-code partner execution (E-003 F7/F8; side-1 hijack), to
  be selected.
- It also explains why state-free genomes never occur in both compartments.

## T6. First principles: fixed points of a two-party rewrite map (no program vocabulary)
- **The system.**
  - A 128-byte joint string is rewritten by executing both 64-byte halves in turn, then perturbed.
  - Each string s induces a map on partners x: R_s(x) = the half it leaves behind.
- **What persists.** A string grows in number if R_s maps a large measure of partners, and of its own post-execution
  register contexts, to itself, and if its own half is stable under the partner's action.
- **Painters and copiers.** Painters are strings whose image is a constant that happens to equal themselves (a low-dimension
  image). Copiers are strings whose image restricted to the window is the identity (a high-dimension image), but only for
  a subset of pointer contexts.
- **Growth.** The population is a noisy replicator equation over strings, with pair-sampled fitness.
- **"State-freedom"** is enlargement of the context set over which the identity image holds.
- **Bistability** is the existence of two stable points of the pair-sampled equation.
- **Observable directly.** The image dimension (source diversity), the basin measure over partners and contexts, and the
  self-stability of R, all computed genome by genome, need no lineage labels at all.
