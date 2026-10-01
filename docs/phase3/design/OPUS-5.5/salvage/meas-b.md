# Salvage digest meas-b: lineage, causal intervention, heredity and mechanism tooling

Evaluator: salvage subagent for EPIMETHEUS / OPUS-5.5 (Phase 3 independent architect). Date 2026-10-01.
Frozen inputs: RSE_ARCHITECTURE.md and requirements.jsonl at commit 77d3c99c3.
Question asked of every component: does it satisfy a Phase 3 requirement better than rebuilding it?
There is no preservation quota.

Independence: nothing under docs/phase3/design/ outside OPUS-5.5/ was opened. roles/Dionysus/ was not opened. No
holdout, nestor_secrets, credential or key file was opened. Other salvage digests in this folder were not read.
Git was used read-only (one `git show` of a file on the unmerged branch origin/archaeon/attribution-arc-2026-09-28).

Method: evidence digests (sis-a, sis-b, tan-a, tan-b, tit-a, ixi, atl, idx) were used only to find files. Every
verdict below rests on the source code and tests themselves. Pure tests were run from a scratch directory with
PYTHONDONTWRITEBYTECODE=1 and `-p no:cacheprovider`. Tests that write receipts into the repository were run on copies
in the scratchpad. One new probe was run, on a planted painter (section 3.1). No experiment or campaign was run.

---------------------------------------------------------------------------------------------------------------------

## 1. Verdicts at a glance

    #  component                                   seat        category            slot      cost  decisive reason
    1  taint VM + lineage core (archaeon/lineage)  Archaeon    REBUILD             R3/R2     M     right pattern, but it is a
                                                                                                    second Z80 interpreter;
                                                                                                    painter read as SELF_COPY
                                                                                                    (shown here)
    2  causal-lineage contract v0.2/v0.3           Archaeon    EXTRACT             R2/R0     M     engine-neutral provenance
       (archaeon/causal_lens schema + corpus)                                                       schema + validator +
                                                                                                    attack fixtures; extend
                                                                                                    vocabulary
    3  z8taint (H3 ruler R3)                       Nestor      HISTORICAL_CONTROL  R2 plants NA    coarse niche tags; the
                                                                                                    ruler tournament is the
                                                                                                    asset
    4  NPE z8shadow tracer + interventions +       Nestor      REBUILD             R2/R3     M(*)  best DEV-14 design
       26-fixture pack                                                                              precursor; bound to the Z8
                                                                                                    ISA; flip arm is blind on
                                                                                                    code-as-data
    5  bee_tracer                                  Bellerophon HISTORICAL_CONTROL  R2/REP    NA    evidence that an
                                                                                                    independent rebuild from
                                                                                                    the spec text works
    6  Artemis CVT-2/CVT-R (certs.py) + W2-36 R*   Artemis/    HISTORICAL_CONTROL  R2 plants NA    no self-replication in
                                                   Nestor                                           Phase 3; ground-truth
                                                                                                    panel and failure modes
                                                                                                    are the asset
    7  P-11 randomized-victim assay                Nestor      HISTORICAL_CONTROL  R2 plants NA    known painter false
                                                                                                    positive; re-execution
                                                                                                    pattern is the asset
    8  CW01 qualified Bernoulli(f) damage ruler    Nestor      EXTRACT             R2        S     dose sampler + sham +
                                                                                                    5-check battery; the
                                                                                                    planted-sensitivity half
                                                                                                    is missing
    9  Ares carriers.py edge/SCC cuts              Ares        REBUILD             R2/R3     M     useful concepts; zero
                                                                                                    ablation; ad hoc
                                                                                                    transplant
    10 Ananke carrier-swap lens (lens.py,          Ananke      REBUILD             R2        M     best interchange design in
       lens_swap.py)                                                                                the record; PTE/torch
                                                                                                    specific
    11 Ananke swap_rel.py (REL4/H2 certificate)    Ananke      EXTRACT             R2 stats  S     pure numpy decision rule
                                                                                                    with tabulated
                                                                                                    false-certificate rates
    12 Aether one-bit twin + locality check +      Aether      REBUILD             R2/R3     S     exact causal-reach ruler;
       counterfactual-parent audit                                                                  basis for an ORG-19
                                                                                                    closure audit; grid-CA
                                                                                                    specific
    13 Nyx prediction packet + mechanism ledger    Nyx         RETIRE              -         NA    prose interventions;
                                                                                                    reading-based boundaries;
                                                                                                    R0 + SCI-04 supersede it
    14 Diomedes decomposition ladder + hidden-     Diomedes    HISTORICAL_CONTROL  R2 MEA-15 NA    off-domain corpus; keep
       variable proxy baseline                                                                      the failure shape and the
                                                                                                    proxy-baseline idea
    15 Hephaestus closure gauntlet                 Hephaestus  REBUILD             R3/R2     M     the expressibility-probe
                                                                                                    protocol is sound; the
                                                                                                    enumerator targets the
                                                                                                    wrong object

    (*) The port itself is M. DEV-14 as a whole stays L, as requirements.jsonl says.

Bottom line. No component in this group is KEEP. Two small, substrate-agnostic primitives are worth extracting
(swap_rel, the Bernoulli dose battery). One schema is worth extracting and extending (the causal-lineage contract).
Five designs are worth rebuilding on the DGM (taint shadow, shadow tracer, carrier-swap lens, twin, closure
gauntlet). Ares carriers.py is rebuilt from its concepts only. The rest are failure or known-answer corpora, or retire.

---------------------------------------------------------------------------------------------------------------------

## 2. R2 needs named in the brief, mapped to salvage sources

    need (requirement)                 best historical source in this group                verdict
    ---------------------------------  --------------------------------------------------  ---------------------------
    matched ablation (CAU-01)          none. Ares cuts to ZERO (carriers.py:77-90), which   BUILD NEW. Port only the
                                       is exactly the anti-pattern. CW01 'nop'/'operand'   sham route (CW01) and the
                                       modes are disable/randomise, not matched resampling  applied-tick / arm_identical
                                       from other runs. Ananke 'perturb' arms are           guards (Ananke)
                                       sensitivity probes that cannot FLIP
    interchange (CAU-04, CAU-09)       Ananke mirror-pair carrier swap + S/C/N census +     REBUILD the lens; EXTRACT
                                       reach verification (lens.py, lens_swap.py);          swap_rel
                                       swap_rel H2 certificate; Aether single-site
                                       patching audit
    transplant with sham arms          Ares transplant vs count-matched random sham         BUILD NEW. Port the sham
    (CAU-02)                           (carriers.py:272-322); Archaeon inert-host           count-matching, output-node
                                       fixtures; P-11 donor-writes-blocked control          mapping and host-execution
                                                                                            fixtures
    graded dose as fractions (CAU-03)  CW01 scattered Bernoulli(f) + sham + P-G01 sampler   EXTRACT. Add a planted
                                       battery; P-G08 geometry comparison                   monotonicity battery
    blind localisation (CAU-06)        Ares per-edge / per-SCC exhaustive cut sweep;        BUILD NEW: a sweep over
                                       Ananke all-carrier x tick table                      every ORG-19 channel class
    minimisation (CAU-10)              nothing in this group. Hephaestus finds minimum-     BUILD NEW
                                       depth witnesses by synthesis, which is not
                                       ablation-minimisation of an organism
    write-order tracer (DEV-14)        NPE z8shadow + interventions + mutant-tested         REBUILD. Port the label
                                       fixture pack; bee_tracer and the Archaeon reference  algebra, performer = WHAT,
                                       tracers (independent implementations of one spec,    the depend/complete arms,
                                       ANCESTRY_PREREG v4/v5); causal lens v0.3             mutant tracers and the I2
                                       WHO/WHERE/WHAT                                       protocol. Redesign the flip
                                                                                            arm. Add write orders and
                                                                                            the four planted order
                                                                                            organisms
    decoder qualification (MEA-15)     Diomedes cross-fitted hidden-variable proxy          BUILD NEW. Add a proxy rung
                                       (concept only)                                       with folds by object
                                                                                            identity
    material provenance shadow         Archaeon taint VM + lineage core (refuse on          REBUILD in the DGM kernel;
    (ORG-08, PRV-10, AGR-04)           disagreement; inserted material never becomes        EXTRACT the contract
                                       random; 10 known-answer births); causal-lineage
                                       contract

---------------------------------------------------------------------------------------------------------------------

## 3. Components

### 3.1 Archaeon taint VM and lineage core -- REBUILD (cost M; slot R3 instrument hooks + R2 provenance assays)

Paths: archaeon/lineage/taint_vm.py (145 lines), archaeon/lineage/core.py (303), archaeon/lineage/assay_block.py (81),
archaeon/tests/test_lineage_attribution.py (152).

What it really does
- taint_vm.execute_taint re-implements the frozen z80atlas VM instruction by instruction. It carries one label per
  memory byte and register: ('E',p) for executor material, ('N',q) neighbour, ('I',) input, ('K',) constant,
  ('Z',) scratch, and ('X', frozenset(sources)) for any computed value (taint_vm.py:7-13).
- Moves carry labels. LD r,imm takes the label of the code byte it reads (:59-60). ALU, INC and DEC produce X with
  conservative contributor sets (:65-81). The COPY primitive carries labels (:110-122).
- Conditional branches (:86-95) update no label. Control dependence and implicit flows are not tracked.
- core.World._labels (:181-190) takes a fast path when a full-window self copy needs no taint run. Otherwise it runs
  the taint VM and raises "refusing to attribute" if the shadow's result differs from the frozen VM's. That is a
  sound guard.
- core.World.attribute (:192-215) assigns material ids per byte:
  - a byte changed by copy noise becomes new MUT material;
  - E and N labels map to the parents' material ids;
  - X becomes new COMP material, with contributor lineages recorded;
  - inserted-control taint propagates.
- core.World._birth (:224-238): the template is whichever side contributed more copied bytes. If the template
  contributed >= G/2 bytes, the child continues the template's genetic lineage (glin). Otherwise the birth is an
  ORIGINATION.

Correctness evidence
- test_lineage_attribution.py covers 10 known-answer births. Highlights:
  - an inert host executing a resident copier is HOST_EXECUTION, not ancestry;
  - a host mutation that contributes no bytes stays out of ancestry;
  - 16/16 recombination;
  - a mutation byte is new material;
  - inserted control can never become random through hosting;
  - 23 block-15 host labels collapse to one genetic lineage.
  It also checks fast-path equivalence and runs a 2 x 3,000 random-tape differential against vm.execute.
- RUN (this evaluation): 11 passed, 1 skipped (test_10, the 20-minute replay, needs Z80ATLAS_SLOW).

DEFECT DEMONSTRATED IN THIS EVALUATION
- Probe: an 11-instruction homopolymer painter, `LD r0,0x36; LD r2,NBR; LD r1,32; loop: ST [r2],r0; INC r2; DJNZ
  loop; HALT`. It writes 32 copies of its own immediate byte over the neighbour window.
- Result:
  - the core labels the birth mechanism SELF_COPY, template executor, copied_exec 32;
  - child glin == parent glin;
  - all 32 child material ids equal parent byte 1.
- The material provenance is correct: every byte really is material from parent byte 1. The genetic-lineage rule
  (core.py:228-234) is the problem. It counts copied bytes without positional or structural correspondence, so
  material share is read as genome reproduction.
- This is the same failure class that made P-11 certify painters. Any Phase 3 count built on this rule would inflate
  "descent".

Other defects
- Control dependence is ignored: a value written under a condition on input or neighbour state is attributed only to
  its data source.
- The shadow is a second, hand-maintained copy of the ISA, kept honest only by differential tests.
- Hard-wired G = 32 and z80atlas grammar constants.
- Imports proteus.foundry.prng (another seat's PRNG) and archaeon.envgate.*.

Coupling: pure Python, OS-neutral, CPU, no GPU. Depends on archaeon.z80atlas, archaeon.envgate and proteus.foundry.prng.

Phase 3 role: ORG-08, PRV-10, AGR-04, and REP-02 / CMP-01 for the slow-reference differential pattern.

Decisive reason: Phase 3 needs exactly this provenance discipline, but as native state of the DGM kernel. The
reference design puts a material provenance shadow on every instruction and register value. The code cannot be
reused on the DGM.

What carries over:
- the refuse-on-disagreement guard;
- the rule that inserted material never becomes random;
- NEW material for mutations and computed values;
- the 10 known-answer birth tests, as the PRV-10 / AGR-04 fixture specification.

Fix in the rebuild: report material descent and positional/structural correspondence as separate quantities, never
one "lineage" number.

### 3.2 Archaeon causal-lineage contract v0.2/v0.3 -- EXTRACT (cost M; slot R2 provenance query layer + R0 row schema)

Paths: archaeon/causal_lens/schema_v02.py (316), schema_v03.py (73), corpus_v02.py (267), adapters/*.py,
PORTABILITY01_REPORT.md, tests/test_causal_lens_v02.py and test_causal_lens_v03.py.

What it really does
- An engine-neutral causal-lineage graph ("Pure Python, no engine imports", schema_v02.py:1-3), with:
  - node kinds MATERIAL, BODY, IDENTITY, EXECUTION, TRANSFORMATION, CF_TEST, ...;
  - typed relations (copies_from, contributes_material, mutates_from, hosted_by, ...);
  - origins RANDOM_INIT, INSERTED_SEED, TRANSPLANT, MUTATION, COPY, COMPUTED, ...;
  - evidence bases TRACE, REPLAY, NATIVE_RECORD, DERIVED, DECLARED;
  - tri-state fields YES / NO / NOT_IDENTIFIABLE;
  - a validator (J1-J20) that rejects prohibited inferences.
- v0.3 splits "which code governed the write" into three referents, measured to diverge (schema_v03.py:1-22):
  - WHO, the executing context;
  - WHERE, the instruction's location;
  - WHAT, the material of the executing instruction.
  Measured divergence: BEE WHERE != WHAT in 27,083 of 28,163 location-foreign births; NPE WHO != WHAT in 26.4% of
  directed writes; Archaeon 28%.

Correctness evidence
- 15 attack fixtures, each with cheats that must be rejected by the invariant they violate; a v0.1 -> v0.2 upgrader
  test.
- RUN: 52 passed (v02 + v03).
- PORTABILITY01 (REPORTED): adapters for 4 engines. The contract caught a real adapter defect (D1, 12 I2/I3
  violations). On BEE the lens disagrees with the native ruler on 847,000 births (frame-shifted copying). 33.1% of
  births are NOT_IDENTIFIABLE.

Defects
- The vocabulary is built around self-replicating soups (heritable-unit continuity, HOSTING, BODY). It has no origin
  for a developmental REWRITE event or a model-authored edit, both required by ORG-08 and AGR-04.
- J21 is enforced on the adapter's declared referent and on regexes over source wording. The docstring admits "an
  adapter that mis-declares its referent can pass".

Coupling: stdlib only.

Phase 3 role: ORG-08, PRV-10, AGR-04, SCI-17 (vocabulary lock), MEA-10.

Decisive reason: it is the only artefact in the group that is already substrate-neutral and has adversarial
qualification. Lift it into R2 as the schema and validator for provenance-shadow outputs:
- add DGM origins (genome element, SPAWN copy, REWRITE event, transplant, model edit, fixture ancestry);
- keep NOT_IDENTIFIABLE first-class;
- keep the WHO/WHERE/WHAT separation, because it is exactly the writer definition DEV-14 needs: a write's order
  belongs to the WHAT of the writing instruction.

### 3.3 NPE z8taint (H3 material ruler R3) -- HISTORICAL_CONTROL (slot R2 plant library; NA)

Path: roles/Nestor/campaigns/z80atlas-verify-2026-09-22/z8taint.py (361); tests/test_h3_material.py (270).

What it really does
- A line-for-line copy of z8.run that carries a one-byte niche TAG per byte (z8taint.py:1-17).
- Every computed value takes the executing organism's niche `here`: ALU (:129-130), INC/DEC (:140-155), IN (:248),
  SELF/GETPC/SENSE (:331-353).
- LDIR copies tags, but a copy-error flip takes `here` (:283-286).

Correctness evidence
- RUN on a scratch copy (the test writes H3_RULER_TOURNAMENT.json into the repo). T-H3-MAT PASS:
  - R3 material ruler scores 9/9;
  - R0 id certificate 4/9 (it certifies an overwritten id);
  - R1 founder fidelity 7/9;
  - R2 causal-edge window 4/9;
  - run_tainted is bit-identical to z8.run on 400 random programs.

Defects
- A tag records the niche where a value was made, not element provenance. It cannot express genome, rewrite,
  transplant or model edit.
- Computed values lose their contributors, unlike Archaeon's X sets.
- Copy-error mutations are credited to the executor's niche.
- The fixture expectations were written by the ruler's author with the same >= 0.50 material-share definition R3
  computes, so R3's 9/9 is close to definitional (independence class I0).

Decisive reason: superseded by z8shadow. What is worth keeping is the 9-fixture tournament: a known-answer
demonstration that id- and resemblance-based descent rulers fail. Phase 3 should keep it as a planted descent battery
for PRV-10.

### 3.4 NPE z8shadow tracer + interventions + fixture pack -- REBUILD (port M; DEV-14 overall L; slot R2 write-order tracer + R3 hooks)

Paths: roles/Nestor/campaigns/ancestry-replay-2026-09-28/tracer/z8shadow.py (586), interventions.py (343),
npe_fixtures.py (464), check_fixtures.py (250), selftest_shadow.py (97), GATES.json, TRACER_FREEZE.json.

What it really does
- Every byte and register carries a data label (E entity-move, K constant, X context, P persisted register,
  C computed over base labels, F computed-from for bijective register ops, M mutation at the write-back draw) plus an
  address-dependence set (z8shadow.py:8-29).
- Each store records:
  - the ctrl set: deps of every conditional evaluated so far, including the LDIR count (:206-215, :491);
  - exec deps of every fetched byte;
  - the performer: the data label of the store instruction's opcode byte (:262-271).
- An optional post-dominator-scoped ctrl label (Xin-Zhang style) is computed (:98-164, :217-223).
- interventions.py:1-30 defines four confirmation arms:
  - flip: flip a bit in the pre-state; the arm applies only if the trace, store and load sequences are unchanged;
  - depend: randomise source groups outside {data source, performer}, K = 8; IDENTIFIED only with 0 changes;
  - complete: randomise each byte not named; gate at <= 5% leak;
  - precision.
- check_fixtures.py runs 26 fixtures and 10 MUTANT tracers: loc0, reverse, positional, ptrlabel, noexec, exec_all,
  noctrl, implicit_move, value_alignment, performer_by_location. Each mutant must fail at least one fixture.

Correctness evidence
- RUN: selftest_shadow 3,000 random pair interactions, 0 mismatches vs the frozen z8.run; the injected ADD defect is
  detected.
- RUN on a scratch copy: the fixture pack (26 fixtures, 85 loci incl. 12 Archaeon adversarial additions) has 0 real
  failures, and 10/10 mutants are caught.
- The world-level fixtures (K9/K18/K28) were NOT run. They need pin/pin_reproduce.py, which git-archives a pinned
  commit.
- GATES.json (REPORTED):
  - G1: 451/451 expectations agree with the independent Archaeon reference tracer;
  - G2: fresh sealed set 2 raw PASS.
  - BUT the s4 flip-coverage floor FAILS in both classes (self 0.447, other 0.125).
  - ctrl_deps_slice and pdom are NOT validated and are barred from production quantities.
- E-003 synthesis (arc branch): the NPE leg was uninformative by construction (29 births < 30-birth floor).

Defects
- The flip arm counts as applicable only if the fetched-instruction trace is unchanged. It is therefore structurally
  blind whenever copied bytes are later executed (G3 evidence: prefix rule 31/32 on one birth, 0/32 on another).
  That is exactly the code-as-data case DEV-14 exists for, since the DGM's REWRITE writes instructions that then run.
- Control-dependence labels are unvalidated.
- ISA-bound: Z8, pair context only, no callbacks (z8shadow.py:181-182).
- Production sample custody was host-local (M2).

Coupling: imports the frozen z8.py, world.py and p11.py from a sibling campaign directory by sys.path. The pin step
needs git and a cpu8 host lease.

Phase 3 role: DEV-14, ORG-08, PRV-10, CAU-06, MEA-01 (mutant testing as qualification), REP-02.

Decisive reason: the most complete write-provenance design in the record (label algebra, performer, ctrl/addr/exec
sets, confirmation arms, mutant tracers, independent reference with sealed fresh sets). It is bound to one ISA and has
a known blind arm.

To port onto the DGM:
- the spec;
- the fixture taxonomy (painter literal, partner-executed copy, retention, computed, bit decoder, operand cipher, ...);
- mutation testing of the tracer;
- the depend and complete arms.

Redesign the confirmation of written code: patch the writer's state at the write event (twin-style, see 3.12)
instead of flipping a pre-state bit under a trace-identity condition. Then add what DEV-14 actually asks for:
- write orders;
- reversion at or above an order;
- donor-history dose transplants;
- the four planted organisms (order 1, 2, 3, maturation clock).

### 3.5 bee_tracer -- HISTORICAL_CONTROL (slot R2 / REP; NA)

Path: roles/Bellerophon/e003_2026-09-29/tools/bee_tracer.py (274), README.md, FREEZE_MANIFEST.json.

What it really does: an observation-only shadow of BEE's vm.execute with the same label algebra (E / INPUT / CONST,
COMPUTED, COMPUTED_FROM, transitive addr sets, ctrl, exec, performer). It was written from the prereg TEXT only,
without reading archaeon/attribution/bee_ref_tracer.py (bee_tracer.py:1-8). Every run is value-checked against the
frozen VM. The post-dominator scope is not implemented.

Correctness evidence (REPORTED):
- 32,827/32,827 births replayed bit-for-bit; 28/28 fixtures; 123,210 interactions value-equal.
- Production agreement first FAILED at 0.974 < 0.995. It passed after the post-exposure C11 amendment.
- The BEE verdict is "VALIDATED only as amended": three post-exposure amendments sat on verdict boundaries
  (E003_SYNTHESIS on origin/archaeon/attribution-arc-2026-09-28).
- NOT RUN: it needs the pinned BEE harness 16fc6c2a and the fixture pack, which exists only on the unmerged branch.

Decisive reason: no BEE substrate in Phase 3. The lasting value is process evidence. An independent reimplementation
from spec text reached three-way exact agreement on a sealed fresh set, and the one disagreement exposed a spec
ambiguity that no single author would have found. That is the REP-02 / REP-06 pattern to use when qualifying the DGM
provenance shadow, with the amendment rule frozen in advance this time.

### 3.6 Artemis CVT-2 / CVT-R (certs.py) and the W2-36 R* proposal -- HISTORICAL_CONTROL (slot R2 plant library; NA unless DEV-12 is preregistered)

Paths: roles/Artemis/challenge/p11/{certs.py (115), harness.py (143), specimens.py (121), tv.py, common.py,
results/VERDICT.json}; roles/Nestor/inference_saturation_wave2/W2-36_cvtr_audit/{_cvtx.py (164), REPORT.md}.

What it really does
- For each parental byte, certs.py makes 3 variants: x^01, x^80 and one sha-random value (:14-24).
- It runs base and variant lineages for 4 generations x 3 draws against common random victims (:40-66). The
  stepfn(G, g, k) interface is substrate-agnostic.
- Signature = (position, value) pairs where the variant child differs from the base child. It is "defined" if the
  same signature appears in >= 2 of 3 draws (:27-37).
- CVT-2 = defined at g1 and g2. CVT-R = the g3 or g4 signature equals the g2 signature.
- ACCEPT IFF AT LEAST ONE VARIANT qualifies (:80-84). TB = log2(1 + classes).
- specimens.py is a 17-specimen ground-truth panel on z8 and a toy VM with exact transmissible-bit content:
  - 0-bit homopolymer and periodic painters; 1-bit and 4-bit painters;
  - copiers, incl. a budget-limited one; a complement cycle; a host-mediated guest; two cooperating tapes;
  - a low-entropy copier; a hash scrambler; a counter copier.

Correctness evidence
- VERDICT.json (committed):
  - P-11 is UNSOUND FOR HEREDITY: it certifies painters Z1, Z2, TV-1, TV-2;
  - P-11 is OVER_STRICT: it rejects TV-4, Z5a, TV-5b, Z3u96;
  - CVT-2 is the weakest adequate certificate; CVT-R is adequate;
  - calibration is exact (TB 0, 0, 1, 4).
- W2-36 (REPORTED):
  - CVT-R false-accepts rescue mutants and HALFBLANK (9/9 seeds), and counts attractor switches;
  - a single seed gives coin flips: 6 recorded verdicts flip under K = 8.
- R* adds three things: an inheritance clause (the variant is carried at its own site in >= 2/3 draws above base), a
  lineage-fidelity floor of 0.9 for g1-g3, and K = 8 seeds with an INDETERMINATE band.
  POS 8/8, NEG 0/8 on constructed controls. NEVER FROZEN.

Defects
- Accept-on-one-variant (certs.py:84).
- No inheritance clause, no lineage-fidelity check, one seed.
- The panel was authored by the certificate's author (I0).
- common.py:10 hard-codes `/tmp/claude-1000/-home-jcraig-Prometheus/.../scratchpad/p11`, scratch copies on another
  host, so the code on main cannot run here. NOT RUN.

Decisive reason: the architecture has no self-replicating substrate; reproduction in R4 is explicit, so these
certificates have no production slot. Two things are worth keeping:
- The panel design: specimens of known bit content, including painters and multi-bit painters. It becomes the
  template for any heredity or transmission battery (MEA-02, MEA-16).
- The certificate shape: perturb the PARENT, follow >= 2 generations under common random numbers, require
  inheritance and lineage fidelity, use K seeds with INDETERMINATE.
If a DEV-12 transmission-of-developed-structure claim is ever preregistered, rebuild this shape (cost M) around a
perturbation operator on DGM elements.

### 3.7 P-11 randomized-victim assay -- HISTORICAL_CONTROL (slot R2 plant library + intervention pattern; NA)

Path: roles/Nestor/campaigns/z80atlas-verify-2026-09-22/{p11.py (178), P11_SPEC.md, tests/test_p11.py (245)}.

What it really does (p11.py:12-30, 105-150)
- Re-executes one pair interaction from the exact pre-state (genomes, registers, flags, order, budget, op mask, copy
  rate) on a private tape with a private RNG, so the world trajectory is untouched.
- Replaces the victim half with random bytes and applies three criteria:
  - C2: final fidelity to the donor >= 0.90;
  - C4: the donor authored >= 0.90 of the donor-directed changes, by last-VALUE-change provenance;
  - C5: with the donor's writes blocked, fidelity stays < 0.90.
- 3 draws, majority 2, behind the predecessor prefilter.

Correctness evidence
- RUN on a scratch copy (the test writes T_P11_RECEIPT.json into the repo): 14/14 PASS. This includes 3 negatives
  that fool the predecessor, CRITERION-CAN-FIRE for each of C2, C4 and C5, and prov vs prov_lit (a genuine copier
  would fail under last-write).

Defects (REPORTED, IMPL-confirmed)
- Certifies painters: it measures construction, not heredity.
- Over-strict for multi-slice copiers.
- Only 6 of 57 recorded survivors re-pass from a fresh state.
- 26 of 57 rest on one 2-of-3 event whose per-draw files were gitignored.

Decisive reason: no pair-tape soup in Phase 3. Two things transfer:
- the geometry, as the template for every R2 counterfactual: re-execute from an exact snapshot with keyed streams on
  a private replay, leaving the world untouched (DEV-03, CAU-09);
- the criterion-can-fire discipline (MEA-05).
The painter false positive is a canonical construction-vs-heredity fixture.

### 3.8 CW01 qualified Bernoulli(f) damage ruler -- EXTRACT (cost S; slot R2 dose operator)

Paths: roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-arch4/{scatter.py (113), P-G01/run_PG01.py (113),
P-G01/RESULT.json, P-G08/RESULT.json}; loop/perturbations_g.py.

What it really does
- mask(n, f, key) draws an independent Bernoulli(f) per eligible instruction from a keyed SplitMix64 stream
  (scatter.py:36-38).
- apply() has three modes (:41-60): delete, NOP (length and jump topology preserved), operand randomisation.
- A HALT-probe reach map (:63-71).
- A SHAM that draws the mask, applies nothing and takes the same evaluation route (:107-113).

Correctness evidence (committed RESULT.json)
- P-G01 INSTRUMENT_QUALIFIED:
  - hit counts mean z -0.011, var z 0.991, Monte Carlo chi-square p 0.485 over 25,200 draws on 126 programs;
  - gap variance inside band for 100%;
  - length slope inside the permutation band;
  - masks reproducible;
  - sham neutral on 126/126.
- P-G08 compared five geometries on 122 programs:
  - exact-count and contiguous rulers produce length slopes outside the permutation band (-0.107, -0.143) and set
    effects below p05;
  - Bernoulli, reached-only and disable stay inside.
  This is the known-answer that count-fixed geometry manufactures length effects (4 of 7 CW01 claims vanished,
  REPORTED).
- NOT RUN (an experiment script that writes into the repo and uses a process pool).

Defects
- The "qualification" covers the SAMPLER only (mask statistics and the sham route). No planted organism with a known
  dose-response was used, so it is half of an MEA-01 dossier. CAU-03's own test is "planted mechanisms monotone".
- run_PG01.py:52 seeds the simulated gap band with abs(hash(organism_id)). That depends on PYTHONHASHSEED and is not
  reproducible across processes.
- 'delete' changes length and jump targets downstream: dilution-neutral in hit count only.
- apply() is specific to the Proteus genome (instruction width IW).

Decisive reason: the mask, the sham and the five-check sampler battery are substrate-agnostic and tiny. They belong
inside the R2 dose operator (CAU-03), applied per DGM carrier class (instructions, nodes, edges, registers), with a
planted monotone/threshold battery added. Rewriting the battery from scratch would cost about as much as extracting
it; extracting keeps the qualified acceptance thresholds.

### 3.9 Ares carriers.py -- REBUILD (cost M; slot R2 localisation/transplant + R3 operators)

Path: ares/carriers.py (343); ares/tests/test_carriers.py (162).

What it really does
- Non-trivial SCC inventory and carrier inventory: self-loops incl. on output nodes, recurrent edges, keep (leak)
  nodes, plastic edges (:28-70).
- carrier_ablation (:93-134) evaluates:
  - the intact organism;
  - each class cut (self_loops, recurrent, keep, plasticity);
  - all cross-step channels cut;
  - each SCC cut and each recurrent edge cut.
  Collapse is (v - floor) <= 0.25 x gain. classify (:137-149) returns NONE, REDUNDANT, RECUR, KEEP, PLAST or MIXED.
- Mutational opportunity p_create per carrier class (:156-187).
- splice_carrier (:221-269) moves edges and maps output nodes onto the host's same output.
- random_carrier_like (:272-298) builds a count-matched random sham. transplant (:301-322) uses 64 naive hosts and
  calls a carrier PORTABLE if the gap is >= 25% of the gain.

Correctness evidence
- Hand-wired RECUR, KEEP and output-self-loop plants are classified correctly. Edge ablation finds the single carrier
  edge. Transplant moves an output self-loop (the cycle-1 blind spot). The exclusion constraints bind under mutation.
- RUN: 9 passed.

Defects
- Every cut sets weights, keep and R to ZERO (:77-90): silence-forcing ablation, which CAU-01 forbids.
- classify labels co-dependence as MIXED, and the campaign read it as redundancy (ARES-W15: MIXED 6/10, REDUNDANT
  1/10).
- Transplant edges whose endpoint is not in the carrier are reattached at RANDOM (:252-254, :266-268). CAU-02 requires
  null, host-corresponding and carried variants, all run.
- The sham has random weights rather than structure drawn from another lineage. There is no host-distance ladder.
- The 25% thresholds have no planted sensitivity curve.
- swap() promises at :336 to "free the donor's hidden slots", and no code does it.
- Float ties.

Coupling: numpy and the Ares substrate and search modules. CPU.

Phase 3 role: CAU-01, CAU-02, CAU-05, CAU-06, CAU-08, ORG-19.

Decisive reason: the concepts are right for a graph substrate: name every carrier class and cut it separately,
work at edge and SCC level, measure the mutational-opportunity denominator, use count-matched shams. The DGM is a
graph, so these become DGM intervention operators and entries in the ORG-19 channel list. The implementation violates
CAU-01 and CAU-02 at its core. The hand-wired per-class plants are a good fixture template.

### 3.10 Ananke carrier-swap lens (lens.py, lens_swap.py) -- REBUILD (cost M; slot R2 interchange)

Paths: prometheus/ananke/lens.py (297), lens_swap.py (490); tests/test_lens_instruments.py (144),
tests/test_lens_swap.py (307).

What it really does
- Mirror-pair worlds share every exogenous draw and have negated cue sequences (lens.py:1-11).
- Between ticks, with the physics untouched, it swaps named state arrays between partners (:31-46). The arrays cover
  site state, inbox, rule pointer, routing weights, energy, in-flight channel content and count, and single payload
  components (:146-163).
- Verdicts are FLIP, NO-EFFECT or CHANCE (:125-134). 'perturb' arms (delay, recipient roll) can never FLIP by design.
- arm_identical flags an intervention that never took effect, so its NO-EFFECT is trivial (:166-189).
- Single-cue twins give the temporal reach (:207-237).
- REACH VERIFICATION (:244-297) combines a lockstep applied-tick count with a must-flip plant run through the same
  intervention code. Verdicts: REACHED, UNREACHED or NOT_VERIFIED. A null is read only when REACHED.
- lens_swap adds single-trial arms and an S/C/N mixture census (lens_swap.py:1-27). The census separates a 50/50
  per-trial mixture from 100% "neither"; both produce chance-level sums by construction.

Correctness evidence
- Known-answer hand plants: echo is a channel carrier, latch a site carrier, rule a rule-pointer carrier, route a
  routing-weight carrier. The tests include wrong-carrier negatives, show the verdict rule can return each outcome,
  check reach against a known answer, and cover arm_identical and the three reach verdicts.
- RUN: test_lens_instruments.py 11 passed (203 s, CPU). test_lens_swap.py: 2 passed before the 300 s cap
  (incomplete).

Defects
- It requires worlds generated as mirror pairs with negated cues and shared draws. That is a world-forge constraint:
  F3/F4 generators must be able to emit such pairs.
- EVERY-trial swaps broke mirror identity (W-M: 5/7 census cells JOINT), so single-trial arms are mandatory.
- Repaired 5 times in 3 days (atl).
- The hand-set FLIP bound (hi99 < 0.40) was later replaced by swap_rel.
- torch, with PTE-specific array names. lens.run defaults to device="cuda" (:84-85).

Phase 3 role: CAU-04, CAU-09, CAU-05, ORG-19, MEA-01, MEA-05.

Decisive reason: this is the best interchange instrument in the record and the only one qualified per carrier class
on planted organisms. It is also the only one that refuses a null whose intervention did not reach. CAU-04 and CAU-09
want it as is. The code is tied to PTE; the design, the plants-per-class test battery and the reach-verification
rule should be rebuilt on DGM carriers: registers, edges in flight with delays, node programs, store contents,
organism-written world state.

### 3.11 Ananke swap_rel.py (REL4 / H2 relative swap certificate) -- EXTRACT (cost S; slot R2 statistics library)

Path: prometheus/ananke/swap_rel.py (201); tests/test_swap_rel.py (121).

What it really does: pure numpy.
- Pair statistics DF = (s-.5) + (a-.5)/2 and DN = (s-.5) - (a-.5)/2, relative to normal accuracy.
- A 99% studentized pair bootstrap with a design-fixed variance floor (H2). FLIP_REL beats NO_EFFECT_REL beats
  CHANCE_REL.
- A floor of P >= 32 pairs and an identification guard.
- A tabulated maximum false-certificate rate <= 1% at boundary truths over a P x K grid (docstring table).

Correctness evidence: RUN: 11 passed. These cover the nesting inside REL3, recovery of a near-degenerate flip that
REL3 misses, point intervals, and false-certificate behaviour near the FLIP boundary.

Defects
- The docstring admits the FC grid certifies H2 only where it coincides with REL3.
- Heavier-skew nulls are untested; the REACH p_min was not re-tabulated.
- Specific to pair means of binary accuracy.

Decisive reason: a known-answer-tested, substrate-agnostic decision rule for interchange outcomes. Exactly what
MEA-11 asks for. Move it into the shared statistics library.

### 3.12 Aether one-bit twin with locality check and counterfactual-parent audit -- REBUILD (cost S; slot R2 + R3 hook)

Paths: Aether/observatory/aeth03_propagation.py (406), aeth03_assay_audit.py (296);
Aether/test/test_aeth03_propagation.py (135), test_aeth03_assay_audit.py (79).

What it really does
- Two worlds identical except one bit. They run under the same law and seed, and perturbation is a hash of
  (seed, tick, site, field), so both receive the identical injected stream (aeth03_propagation.py:8-14).
- Causal generation = 1 + min generation of differing neighbours.
- Locality violations are counted every tick; a nonzero count voids the result. A null self-test flips the bit
  twice.
- The full carried state is compared, not just the visible bytes (:86-96).
- The audit (aeth03_assay_audit.py:1-44) attacks its own premise three ways:
  - lightcone: each law must stay within its declared radius;
  - hidden: a BYTES-ONLY predicate must produce orphan violations when a hidden flag differs, while the full predicate
    produces none;
  - parents: patch only neighbour y's state into A_t, step, and test whether y alone is a sufficient cause. JOINT
    events are counted. Adjacency generation is shown to be a lower bound.

Correctness evidence
- RUN: 20 passed. These include the null twin, exact hop counts on a known relay, catching an undeclared radius,
  hidden-flag predicate violations, and the parent audit equal to the assay on a pure relay.
- REPORTED: bytes-only predicate 32 violations vs full predicate 0; parent audit agrees with adjacency in 84-100%.

Defects
- Specific to a grid cellular automaton (Manhattan stencil, five byte fields).
- Only as good as the declared radius: 'mov' turned out to be radius 2, found by the audit.
- Generation is a lower bound.
- The host substrate had no organisms and no task demand.

Phase 3 role: ORG-19, CAU-09, CAU-04, DEV-14, ORG-08.

Decisive reason: an exact causal-reach ruler built on common random numbers that checks itself. On the DGM, locality
becomes edge adjacency with declared delays and parents become in-neighbours. It serves three Phase 3 needs at once:
1. the ORG-19 closure audit: the hidden-flag fixture IS "an unlisted-channel organism fails the audit";
2. interventional confirmation of provenance labels for DEV-14 (the twin shows what changed; the taint shows what
   data flowed);
3. transient-state carriers for CAU-09.
Small to rebuild.

### 3.13 Nyx prediction packet schema and mechanism ledger -- RETIRE

Paths: nyx/atlas/predictions/schema.py (130), nyx/atlas/mechanisms.py (130), nyx/tests/test_prediction_schema.py.

What it really does
- schema.py validates a packet by field presence, vocabulary membership and the [low, high] shape of the magnitude
  band (:46-103). It hashes canonical bytes (:38-43). It refuses to re-freeze changed bytes; a correction is a new
  packet with `supersedes` (:115-125).
- mechanisms.py validates:
  - unique mechanism ids;
  - an "executable boundary" (cut_id + boundary);
  - a non-empty falsifier;
  - a transplant receipt behind SURVIVED_TRANSPLANT.
  It counts over unique ids (:50-112).

Correctness evidence: RUN: 2 passed (the frozen packets validate and match their FREEZE hashes; novelty_kind
vocabulary).

Defects
- Interventions and controls are prose. No code computes a verdict from a packet, which fails SCI-04's executable
  preregistration.
- A mechanism boundary is a file path plus line range in another system's source code. That is localisation by
  reading, which CAU-06 says can only propose.
- tit-a: 7 mechanisms, 0 transplants; 549 cuts, 0 blind.
- mechanisms.py:82 tests outcome "SURVIVED", which is not in TRANSPLANT_OUTCOMES (dead branch).

Decisive reason: R0's ledger, signed verdict job, derived status and SCI-04 replace all of it. The canonical-bytes
hash and supersedes chain are a few lines and belong to R0 (PRV-01, PRV-03).

### 3.14 Diomedes decomposition ladder and hidden-variable proxy baseline -- HISTORICAL_CONTROL (slot R2 MEA-15 dossier; NA)

Paths: roles/Diomedes/cycle001_run.py (238), review_round2_run.py (296), and the cycle00x scripts.

What it really does
- cycle001 ranks candidate substitutions on a math corpus (knot and elliptic-curve invariants). The label is an exact
  relation of ONE withheld integer (relation_holds :39-44).
- review_round2_run A1-NL (:1-17, :43-60, :102-140) is the proxy baseline. Cross-fitted gradient boosting, with folds
  by CANDIDATE OBJECT IDENTITY, reconstructs the withheld invariant from companion invariants and re-applies the exact
  relation. It reproduces 41-45% of the local above-chance span (CONFIRMED in tan-b). So the "navigation" signal was
  largely hidden-variable sensing.

Defects
- No organism and no world.
- Depends on an untracked corpus (theseus/corpus, PROMETHEUS_CORPUS).
- Folds are seeded with hash((seed, cellname)) at :109, which depends on PYTHONHASHSEED and is not reproducible.
- Dead loop at :120-121.
- Cluster bootstrap of zero width for power-of-two cluster counts (FAILURES F1); a 52x SE unit error.
- NOT RUN.

Decisive reason: the code has no Phase 3 role. Two things carry into the MEA-15 decoder dossier and the MEA-03
baseline ladder:
- the failure shape (a decoder/predictor that wins by reconstructing a hidden scalar from correlates);
- the baseline it implies: a cross-fitted proxy reconstruction, with folds by object identity, as a planted
  input-only rung.

### 3.15 Hephaestus closure gauntlet (substrate-capacity probe) -- REBUILD (cost M; slot R3/R2 capacity-proof tool)

Paths: hephaestus/src/closure_test.py (244), gauntlet_controls.py (178), closure_specs/*.py, STATE.json.

What it really does
- Arms of increasing permissiveness, never collapsed: A0 frozen primitives, A1 + routing, A2 + a frozen generic basis,
  B a small generic language. CLOSURE_MARGIN is the first arm with a mechanism-bearing witness on every route
  (closure_test.py:1-27).
- Membership is extensional:
  - coerced vs typed;
  - verify_exhaustive on points disjoint from search;
  - verify_shift on a structurally shifted regime;
  - mechanism_bearing = typed AND verify_exhaustive.
- A bottom-up typed enumerator with observational-equivalence classes, depth 3, budget 300k (:76-170).
- The COERCE correction (:84-93) followed a bool() degeneracy that made every vector-valued program "match".
- Classification SEARCH_ROUTING / OPERATOR / INCONCLUSIVE (:173-212).
- gauntlet_controls.py has three controls:
  - NEGATIVE: a seeded random target column;
  - POSITIVE: a named buildable expression, with minimum-depth check;
  - CHEAT: the real kernel injected under a decoy name into A1, or into A2 only.

Correctness evidence
- REPORTED: controls ALL_PASS on two boolean walls; Q045 18 OPERATOR / 2 INCONCLUSIVE.
- No pytest suite. The controls script was run on a scratch copy (forge_primitives copied) and did not finish within
  the 300 s cap: not completed.

Defects
- The object is stateless typed expressions over Python callables (kernels of Forge reasoning tools), not stateful
  organisms.
- INCONCLUSIVE at depth 3 carries no completeness bound.
- Validated on 2 specimens plus Q045.
- Writes closure_results/*.json into the repo and records state on every run.
- Coupled to agents/hephaestus/src/forge_primitives.py.

Phase 3 role: ORG-14, ORG-15, DEV-13, MEA-05.

Decisive reason: the need is real. Phase 3 needs an expressible-tier probe and constructive capacity proofs compiled
by any recorded procedure (X4). The portable content is the protocol: nested arms answering distinct questions,
extensional membership on sealed verify and shift sets, coerced vs typed, and the negative/positive/cheat battery.
The enumerator must be rebuilt over DGM programs, which have state and time.

---------------------------------------------------------------------------------------------------------------------

## 4. Cross-cutting findings

F1. Material share is not heredity. This evaluation showed it on the Archaeon core (painter -> SELF_COPY, child
    continues the parent lineage), and the record shows it for P-11 (painters certified). Phase 3 must report AGR-04
    counts as "material descent" only. Any heredity or transmission claim needs perturb-the-parent evidence (CVT/R*
    shape) and positional/structural correspondence measured separately.

F2. Label propagation is not causal dependence.
    - Archaeon taint ignores control flow.
    - The NPE tracer adds ctrl sets, but they were never validated.
    - Its flip confirmation fails whenever copied bytes are executed.
    The DGM is code-as-data by design (REWRITE, SPAWN). DEV-14's "trace plus intervention confirmation" must therefore
    use write-event patching (twin style, 3.12) from day one, not pre-state flips gated on trace identity.

F3. Duplicated interpreters. Every provenance tool here is a second copy of a VM, kept honest by differential tests:
    taint_vm, z8taint, z8shadow, bee_tracer. In Phase 3 the provenance shadow should be native kernel state (ORG-08),
    and the slow reference interpreter (REP-02 CORE) should carry the same shadow. One differential test then checks
    both values and provenance. This removes a whole class of drift.

F4. Spec-first independent reimplementation works. The attribution arc had 3 tracers, sealed fresh sets and a 0.995
    agreement threshold, and it found a real spec ambiguity (C11). But post-exposure amendments decided the BEE
    verdict. Reuse the protocol to qualify the DGM shadow, with the amendment rule frozen before exposure.

F5. Custody defects that make parts of this group unreproducible from main:
    - The reference tracers, ANCESTRY_PREREG v1-v5, bee fixture packs and the E-003 synthesis exist only on the
      unmerged branch origin/archaeon/attribution-arc-2026-09-28.
    - Data is host-local (M2 C:/Prometheus-data; C:/Users/James/...).
    - Artemis code imports from a foreign /tmp scratch path.
    - RNGs seeded with hash() in CW01 P-G01 and Diomedes.
    - Tests write receipts into the repository: T_P11_RECEIPT.json, H3_RULER_TOURNAMENT.json, closure_results/.

F6. Qualification maturity in this group, best first:
    1. Ananke lens: planted plant per carrier class + reach verification.
    2. NPE shadow tracer: mutant-tested fixture pack + independent reference.
    3. Archaeon lineage: known-answer births + differential.
    4. Aether twin: self-checks + adversarial audit.
    5. Artemis CVT: ground-truth panel, but defective accept rule.
    6. CW01: sampler only.
    7. Ares: hand-wired plants, but zero ablation.
    8. P-11: known false positive.
    9. Hephaestus: two specimens.
    10. Nyx, Diomedes: no organism.

F7. Must be built new, because nothing in this group provides it:
    - matched-resampling ablation (CAU-01);
    - CAU-02-complete transplant arms (frame, three dangling-pointer rules, host-distance ladder, five arms);
    - ablation-based minimisation to a causal core (CAU-10);
    - write ORDERS with reversion and donor-history dose (DEV-14);
    - decoder selectivity controls (MEA-15).

## 5. Suggested order for this group's slice of R2 (dependencies only; budgets are the architect's)

1. S1: provenance shadow in the DGM kernel and the slow reference interpreter (ORG-08). Port the Archaeon birth
   fixtures, the inserted-never-random rule and the separate positional-correspondence quantity. Extend the extracted
   causal-lineage contract with DGM origins.
2. S1-S2: dose operator with the CW01 sampler battery plus planted monotone/threshold organisms (CAU-03). swap_rel
   and the dose statistics go into the MEA-11 library.
3. S2: twin/patch tool on DGM graph locality, and the ORG-19 closure audit built on it: a hidden-channel plant must
   produce violations under an incomplete channel list.
4. S2-S3: interchange lens on F3/F4 mirror-pair worlds, with planted carriers per class and reach verification
   (CAU-04, CAU-09). This needs the world forge to emit mirror pairs.
5. After REWRITE exists and before E6: the write-order tracer, with the label algebra, depend/complete arms, mutant
   tracers, write-event patch confirmation and the four planted order organisms (DEV-14), qualified by an I2
   reimplementation.
6. GATE-L3 work: transplant arms, blind localisation sweep, minimisation.

---------------------------------------------------------------------------------------------------------------------

## 6. Tests and probes run in this evaluation

    item                                                          how                          result
    archaeon/tests/test_lineage_attribution.py                    pytest, scratch cwd          11 passed, 1 skipped (slow)
    archaeon/tests/test_causal_lens_v02.py + _v03.py              pytest, scratch cwd          52 passed
    painter probe on archaeon.lineage.core (new, read-only)       python -c, scratch cwd       SELF_COPY, same glin (defect)
    ares/tests/test_carriers.py                                   pytest                       9 passed
    prometheus/ananke/tests/test_swap_rel.py                      pytest                       11 passed
    prometheus/ananke/tests/test_lens_instruments.py              pytest, CPU                  11 passed (203 s)
    prometheus/ananke/tests/test_lens_swap.py                     pytest, CPU                  2 passed before 300 s cap;
                                                                                               incomplete
    Aether/test/test_aeth03_assay_audit.py + _propagation.py      pytest                       20 passed
    nyx/tests/test_prediction_schema.py                           pytest                       2 passed
    Nestor tests/test_p11.py                                      copy in scratchpad           T-P11 PASS 14/14
    Nestor tests/test_h3_material.py                              copy in scratchpad           PASS (R3 9/9; 400 progs
                                                                                               identical)
    Nestor tracer/selftest_shadow.py 3000                         direct, prints only          0 mismatches; defect caught
    Nestor tracer fixture pack + mutants (world part excluded)    copy in scratchpad           0 failures; 10/10 mutants
    Hephaestus gauntlet_controls (vacuous_truth)                  copy in scratchpad           did not finish in 300 s
    bee_tracer, Artemis certs, CW01 P-G01, Diomedes               -                            NOT RUN (pinned harness /
                                                                                               foreign /tmp path / writes
                                                                                               to repo / untracked corpus)

Worktree note: during this evaluation (12:32:44 local), prometheus/toolbox/series.py and
prometheus/toolbox/tests/test_kernel.py appeared modified in the worktree. The change is line endings only: `git diff`
and `git diff -w` show no content change. None of the tests run here import prometheus.toolbox, and every run used
PYTHONDONTWRITEBYTECODE, so the change came from a concurrent process, not from this evaluator. It was left untouched.

## 7. Files opened (read-only)

Design: docs/phase3/design/OPUS-5.5/{RSE_ARCHITECTURE.md, requirements.jsonl}; evidence/{sis-a, sis-b, tan-a, tan-b,
tit-a, ixi, atl, idx}.md (grep and sections only).
Archaeon: archaeon/lineage/{taint_vm, core, assay_block}.py; archaeon/tests/{test_lineage_attribution, conftest,
test_causal_lens_v02}.py; archaeon/causal_lens/{schema_v02 (head), schema_v03 (head), PORTABILITY01_REPORT.md (head)};
archaeon/z80atlas/vm.py (grep).
Nestor: z80atlas-verify-2026-09-22/{z8taint.py, p11.py, constants.py (grep), tests/test_p11.py, tests/test_h3_material.py
(head + grep)}; ancestry-replay-2026-09-28/{tracer/z8shadow.py, tracer/interventions.py (head), tracer/check_fixtures.py,
tracer/selftest_shadow.py, tracer/FIXTURES_RESULT.json, tracer/TRACER_FREEZE.json, GATES.json, pin/pin_reproduce.py (head)};
cw01-2026-09-17/{experiments/cw01-arch4/scatter.py, P-G01/run_PG01.py, P-G01/RESULT.json, P-G08/RESULT.json,
loop/perturbations_g.py}; inference_saturation_wave2/W2-36_cvtr_audit/{_cvtx.py, REPORT.md (head)}.
Bellerophon: roles/Bellerophon/e003_2026-09-29/{README.md, tools/bee_tracer.py (head + grep), tools/run_fixtures.py (grep)}.
Artemis: roles/Artemis/challenge/p11/{certs.py, harness.py, specimens.py, common.py, results/VERDICT.json};
cvtr_nestor/artemis_p11/certs.py (diff only).
Ares: ares/carriers.py; ares/tests/test_carriers.py.
Ananke: prometheus/ananke/{lens.py, lens_swap.py (head + grep), swap_rel.py (head)}; tests/{test_lens_instruments.py
(head), test_swap_rel.py (head), conftest.py}.
Aether: Aether/observatory/{aeth03_propagation.py (1-130), aeth03_assay_audit.py (1-60, 186-260)};
Aether/test/{test_aeth03_assay_audit.py, test_aeth03_propagation.py (head), conftest.py}.
Nyx: nyx/atlas/predictions/schema.py; nyx/atlas/mechanisms.py; nyx/tests/test_prediction_schema.py.
Diomedes: roles/Diomedes/{cycle001_run.py (1-80), review_round2_run.py (1-140 + grep)}.
Hephaestus: hephaestus/src/{closure_test.py, gauntlet_controls.py (head + grep), closure_specs/vacuous_truth.py (head)};
hephaestus/STATE.json (head).
Arc branch (git show, read-only): ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/E003_SYNTHESIS.md (head).
