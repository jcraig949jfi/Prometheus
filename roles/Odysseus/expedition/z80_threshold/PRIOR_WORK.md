# Z80 affordance threshold -- prior-work search log and what is already known

Currency: 2026-09-28. Odysseus disposable worker, ubu001, worktree at 7720539d4
(branch odysseus/expedition-1-2026-09-28). Pure ASCII. Read-only search; nothing
outside roles/Odysseus/expedition/z80_threshold/ was changed.

Directive: roles/Odysseus/prompts/2026-09-28_expeditionary/01_OPERATOR_DIRECTIVE_verbatim.md s7
("strip conveniences one by one ... The scientific object is the affordance threshold").

## 0. Search log (what was read, how)

Read in full or in the relevant sections:
- roles/Nestor/campaigns/npe-p2-endogenous-heredity-2026-09-27/SYNTHESIS.md, BACKLOG.md,
  delegates/EXTERNAL_RESEARCH.md (s0, s1.1, s1.2, s2, s3, s4, s5), delegates/CROSS_ENGINE.md (grep).
- roles/Artemis/backlog/threads/FR-010.md, FR-011.md; chops/FR-011.md;
  prior_art/PA_origin_of_replication.md (s3 W1-W3, s4 P1-P8, s6 U1-U8, s7 T1-T7).
- origin/artemis/challenge-2026-09-28 (branch only, commit 2af325f7b):
  roles/Artemis/challenge/p11/RESULT.md and certs.py (the CVT certificates). NOT ON MAIN.
- aporia/docs/frontier_campaign_69/dossiers/74_emergent_self_replication_in_artificial_systems.md (grep of
  threshold / primitive / LDIR / trivial / Avida lines; line 218 records the "Z80 has LDIR/LDDR built in"
  critique).
- roles/Odysseus/frontier/poi/ready/R1_copier_encoding_law.md, R2_no_gift_soup_design.md;
  raw/E1_alife_open_endedness.md (Knierim, Cicala, Cotler-Hongler-Hudcova entries; anti-gravity list);
  raw/I1_z80_lineage_worlds.md T1; spikes/S1_copyless_sr/ (probe.py, RECEIPT.md).
- roles/Odysseus/expedition/accumulation/ACCUMULATION_v0.md (rungs R0-R6).
- roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md s3-s5, POST_CAMPAIGN_FORENSICS.md s2.6,
  receipts/BASIN.json, tools/basin.py.
- VM sources: prometheus/z80atlas/vm.py (BEE), archaeon/z80atlas/vm.py (header + opcodes 20/28/29),
  roles/Nestor/campaigns/z80atlas-2026-09-19/z8.py (header: ALLOC/BIRTH/SELF/GETPC/SPLIT).
git grep on the worktree (main-derived) for: ldir / "ldir off" / cost4, "block copy", PUSH / stack,
affordance, homopolymer, painting. Relevant hits are all cited below; "affordance" hits outside this
topic (Aether, Hephaestus, proteus/contracts/affordance_table.v0.json = Proteus's opcode-class table, not a
replication threshold) were checked and set aside. An all-refs git grep was attempted and abandoned
(timed out at 120 s on a host at load ~36 from sibling greps); instead the Artemis, worker/W1, worker/W2
branches were diffed against main for FR-011 / homopolymer / copier files, which found the P-11 result.

## 1. What is already settled (do not redo)

K1. Copy is gated by the supplied op in all three Prometheus VMs, at the level of random emergence.
    - BEE P8 in-world (n = 300 random worlds per arm): base 8 spontaneous; LDIR off 0; LDIR cost x4 0;
      undefined -> HALT 0 (GROUNDING_REPORT.md:78). LDIR-off leaves LDI and LD (T),A; no byte loop arose.
    - BEE HIST: NOPing every copy byte in 345 historical replicators is rescued in 126 by a copy op
      re-created at a new position: byte knockouts are not ablations; only ISA-level removal is (PA P5).
    - Archaeon census: COPY-as-NOP z80 substrate 0 copiers in 1.2e7 random tapes; vmcopy32 9.6e-6
      (FR-011, I1 T1).
    - NPE: BLOCK 47/531 vs BYTEWISE 10/500 runs with a P-11 event; all 10 BYTEWISE donors are
      near-homopolymers (FR-011).
K2. The BEE random-tape density WITH LDIR is measured: 6/200,000 = 3.0e-5 (Z80_64, zero window, own-copy
    rule), 2.0e-5 BYTECODE32, 6.5e-5 VM_COPY; every hit copies with LDIR; minimal copier `LD T,L ; LDIR`
    (3 bytes) reached through a NOP slide (80% of byte values undefined = NOP; registers start at 0; LDIR
    with C = 0 sweeps) (POST_CAMPAIGN_FORENSICS.md s2.6; receipts/BASIN.json). Random tapes have 0/60
    single-mutant copiers (NEIGHBOURHOOD.json).
K3. Copy detectors that do not perturb the parent certify painting as copying. Artemis P-11 challenge
    (branch origin/artemis/challenge-2026-09-28, 2af325f7b): P-11 certifies 4/4 zero-bit painters; of 6
    natural NPE donors that re-pass P-11 from a fresh state, 4 are single-value painters (0x36, 0x2a,
    0x21; three in BLOCK cells) and 2 are real copiers (~7.4 bits). The adequate certificate is CVT-2
    (single-byte parental variants x^0x01, x^0x80, one random; consistent offspring difference in
    generation 1 AND re-transmitted in generation 2; TB = log2(1 + distinct classes)); CVT-R adds a
    recurrence check. Budget finding A0: in a one-slice budget a 3-step/byte painter passes, a 5-step/byte
    bytewise copier cannot finish. -> The information criterion for this study is CVT-2, not a
    dominant-byte rule (DOM misclassifies a genuine 91.7%-0x00 copier).
K4. Environment-supplied self-location is universal in successful soups. Reset registers (BFF heads = 0;
    Z80 2024 emulator reset; Cicala 2026 HL = BC = E = PC = 0, A = F = SP = 0xFF so PUSH writes into the
    partner) supply self-location and a destination (EXTERNAL_RESEARCH.md s0.1). NPE: 95.7% of competent
    donors are SELF-free, borrow HL from never-written zero state; only the ZERO reset rescues establishment
    (C-ZERO-SPECIFIC ZERO 26/48 vs CONST 2/48). Archaeon: 265/265 random exact copiers environment-gated.
K5. No Prometheus VM has a stack route. PUSH is absent in BEE, NPE (LD SP,nn loads nothing) and Archaeon
    (FR-010 spec diff). In real-Z80 soups the FIRST replicators are stack (Load-Push) copiers
    (Aguera y Arcas 2024, 2406.19108; Cicala 2026). So "copy needs the block op" in our VMs is partly an
    ISA-subset fact (PA P2); the PUSH seed test (PA T5) has not been run in any engine.
K6. Cicala et al. 2026 (arXiv 2607.09211, v2 2026-09-02; cited and VERIFIED in PA W2 and
    EXTERNAL_RESEARCH s1.2; also raw/E1): 32-byte Z80 programs, pair concatenation, 512-step budget,
    reset registers, task niches raise interaction probability 0.3 -> 1.0, metabolic step cost. Families
    Load-Push -> LDIR (displaces) and LDD loops. ABLATION: with block copy absent "consistent emergence of
    a different replication mechanism based on the LDD instruction", but "only under task pressure;
    without it, the transition from Load-Push ... fails to complete within ten million epochs". Detector
    is byte-pattern matching of known families (weaker than causal). Code not found.
    -> Cicala already ran ONE rung of the removal ladder (block copy off) in ONE world, with the
    stack route and reset registers present, and with a byte-pattern detector.
K7. Knierim et al. 2026 (2607.01483): a plain mutation walk finds BFF replicators about as fast as the
    soup (walk p=1/100: 9.9e5 programs; soup 5e6; uniform 2.9e7; tuned distribution 9.4e4); blocking
    mergers (even all copying, depth 0) still gives first replicators in 40% of runs: interaction is needed
    for spread, not appearance. Cotler-Hongler-Hudcova 2025 (2510.08342): universality does not imply
    replication; SUBLEQ soups (minimal replicator 25-6060 bytes) never transition.
K8. Nestor npe-p2 re-described NPE acquisition as AVAILABILITY of copy-capable material (1-byte alias
    372/372 attribution; SHAM 0/96; PLANT 2-byte copy 32/96) and establishment as dependence on
    environmental scaffolding the copier's own action destroys. Endogenization of scaffolding is Nestor's
    North-Star thread (T-END-*); the ENGINE campaigns belong to Nestor/Bellerophon.
K9. Accumulation after replication is undemonstrated anywhere in the program: BEE replicator lineages
    carry no task computation (beneficial density 1e-4, identical to random), reproduction-computation
    ANTAGONISM (G4), endogenous reproduction loses the task 178 vs 2 (G3). ACCUMULATION_v0 predicts the
    first unplanted boundary at R2/R3.

## 2. What is NOT known (the gaps this study may fill)

G1. Nobody has an ordered, ISA-level removal ladder with the SAME detector at every rung, reporting
    density, walk time and heredity bits per rung (PA U1 names this as unexplored; FR-011 "NEW-LENS
    SIGNAL: heredity route as the unit of an ISA-level reachability map ... not measured by any engine").
G2. BEE's LDIR-off and cost4 arms were measured only in-world (0/300); their per-tape densities and the
    route that would carry copying without LDIR (LDI loop, byte loop) are unquantified. No density below
    the sampling floor has been estimated in any engine.
G3. No heredity-information (CVT) measurement exists for BEE's spontaneous random copiers or for any
    rung without the block op.
G4. The removals past the copy op (genome boundary, reset/self-location, reproduction API/birth rule,
    task/fitness, contiguity) have never been crossed with the copy-op removals in one design. Cicala
    removes none of boundary, reset, stack or task in its ablation; Knierim removes interaction only.
G5. PUSH/stack: never seeded in any Prometheus VM (PA T5 open).
G6. Operator decision APO-28 / D-A02 ("author the replicator and say so" vs "it condenses") is pending;
    this design supplies inputs, not the decision.

## 3. Consequences for this packet

- Do not re-measure BEE A0 density at scale; cite 3.0e-5 and use it to CALIBRATE a route-conditional
  importance estimator that can reach densities below the sampling floor (G2).
- Use CVT-2 (K3) as the heredity-information measure; a dominant-byte rule is a diagnostic only.
- Treat the stack route and reset registers as ladder rungs (K4, K5), not background.
- Stay on the comparative question; engine campaigns stay with Nestor/Bellerophon.
