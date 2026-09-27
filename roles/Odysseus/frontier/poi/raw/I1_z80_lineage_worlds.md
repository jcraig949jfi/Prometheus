# I1 -- Z80 / byte-tape lineage worlds and the causal lens that audits them

Raw mining note for Odysseus (physics-of-intelligence frontier). Delegate pass, 2026-09-27.
Repository read at /home/jcraig/Prometheus-worktrees/odysseus-base-role (HEAD 22bfbc966) plus
origin/nestor/s1-forensics-2026-09-23 (head d63b76a5f), origin/bellerophon/multiday-campaign-2026-09-26
(head ee7a7d954). Nothing was run except read-only stdlib tabulations of JSON already in git (they are
marked COMPUTED-HERE and can be re-derived in seconds). INFERRED = my reading, not a recorded finding.

---------------------------------------------------------------------------------------------------

## 1. Territory summary

- Three independent Z80-style byte-tape worlds were built from one 2026-09-19 directive (ENGINE_LANDSCAPE
  95fff9111; roles/Artemis/threads/sfe_retrospective/ENGINE_LENS_CARDS.md "LENS AS A TRIPLE").
- NPE (Nestor, M1): Z8 VM with ALLOC/LDIR/BIRTH and a shared "pair tape"; the P-11 causal-copy certificate
  (randomized-victim counterfactual). Lens: barrier decomposition of heredity. roles/Nestor/FINDINGS.md.
- BEE z80atlas (Bellerophon, M2): prometheus/z80atlas, 256-byte tapes, real LDI/LDIR, neighbour window
  [L,2L); physics v3 couples task output to a copy-resource. Lens: endogenous vs exogenous reproduction,
  coupling of computation to reproduction. roles/Bellerophon/forensics_2026-09-23, coupling_2026-09-24.
- Archaeon (M2): archaeon/z80atlas (vmcopy32 / z80 VMs, COPY op 20), envgate / envgate2 (environment as
  the manipulated variable), archaeon/lineage (taint VM, 4 identities per birth), archaeon/causal_lens
  (substrate-neutral contract v0.1 -> v0.3, ran on BEE, NPE and PTE). ops/threads TH-001..006, C-001.
- Crius (closed): existence vs accessibility of reuse in a different VM (roles/Crius/STATUS.md).
- Common arc: every headline "replicator"/"flag" result was cut down by its own forensics; what survived
  is a map of barriers (acquisition, establishment, erosion, host dependence) and a growing ontology of
  what "parent", "own code", "lineage" and "host" mean.

---------------------------------------------------------------------------------------------------

## 2. Candidate research threads

### T1. Is spontaneous-replication accessibility a law of minimal-copier encoding length?
QUESTION: Across the three Z80 worlds, is the per-tape / per-run probability that random material
becomes a heredity-capable copier set mainly by the byte length (and alignment, NOP density) of the
shortest copy program, rather than by the presence of a copy primitive?
WHY IT MATTERS: If accessibility is an encoding-geometry coordinate, then "capability that was not
installed" is gated by representation, and a substrate designer controls it without installing the
capability itself. It would be a transferable accessibility coordinate.
WHAT IS KNOWN:
- NPE: plain encodings 0/47 spontaneous non-pair replication with every other barrier relieved; giving
  ALLOC/LDIR/BIRTH extra 1-byte encodings -> 13/40 vs 0/40 (Fisher p=3.8e-5); "at 3 bytes it is found"
  (roles/Nestor/FINDINGS.md:241-251). Pair tape: 1-byte LDIR/LDDR alias raises donor acquisition 1/64 ->
  39/64, p=1e-14; "Presence is not the barrier: block-copy encodings occur in 87/96 plain populations"
  (FINDINGS.md W1 E-W1-1 on origin/nestor/s1-forensics-2026-09-23, d63b76a5f).
- BEE: minimal copier `LD T,L ; LDIR` is 3 bytes reached through an undefined-byte NOP slide (80% of byte
  values are NOPs); a random Z80_64 tape self-copies alone with p=6/200,000=3.0e-5; ~7% of 500-tick random
  runs enter the basin (roles/Bellerophon/forensics_2026-09-23/POST_CAMPAIGN_FORENSICS.md s2.6, s2.2).
  Ablating LDIR or the NOP slide abolishes it: 0/300 vs 8/300 (GROUNDING_REPORT.md:27-28, s3 P8).
- Archaeon census: vmcopy32 (has COPY primitive) exact-copier density 9.6e-6; z80_32 / z80_64 (no COPY
  primitive) 0 in 1.2e7 tapes; "Copying in this bench is effectively a property of one primitive"
  (archaeon/z80atlas/pivot/Z80ATLAS_RULINGS_FOLLOWUP_REVIEW_2026-09-24.md:78-130). Essential bytes per
  exact copier median 4.
- Nestor W1 report states the abstraction explicitly: "A primitive's DISCOVERABILITY is set by its encoding
  length and alignment, not only by whether it exists" (W1_REPORT.md s6, nestor branch).
WHAT IS UNKNOWN: Genuine: whether one curve (rate vs minimal program length, NOP density) fits all three
VMs, or each VM has its own offset. Missing documentation: nobody has tabulated minimal-copier length per
VM variant side by side. Note a FALSE FRIEND: BEE "Z80_64" has LDIR and a NOP slide; Archaeon "z80_64"
has no block copy (INFERRED from census text), so the two "Z80_64" zeros/non-zeros are not contradictory.
CHEAPEST DISCRIMINATOR: Tabulate, from VM source, the minimal copier byte length and fraction of no-op byte
values for each VM variant (NPE plain/dense, BEE Z80_64/BYTECODE32/VM_COPY, Archaeon vmcopy32/64,
z80_32/64), and plot against the measured rates already in git (BEE BASIN.json / RATES.json, Archaeon
census RESULTS.json, NPE C-DENSE / C-DENSE-COPY). A prediction to register first: log(rate) roughly
linear in minimal length x log(1/256) plus a NOP-slide term.
LENSES: all three Z80 engines; Crius (reuse existence vs accessibility) as a non-Z80 check.
NEW-LENS SIGNAL: No new world needed for the tabulation; a clean test would want one VM with a dial for
encoding length of a fixed-semantics copy op (NPE already has it: the 1-byte alias).
RELATED: T2, T9, Crius (T20).

### T2. Why does partial window restoration give nothing (ENVGATE-02) when the viability model predicts graded rescue?
QUESTION: In ENVGATE-02, restoring 128, 128..131 or 125..128 produced no window-dependent establishments.
Is establishment a threshold (near-critical branching) phenomenon, and what supplies the missing
multiplier that lets the U arm establish at all at an estimated R0 of 0.96?
WHY IT MATTERS: Environmental structure as a switch on lineage establishment, with a threshold, is exactly
the kind of condition under which an environment "decides" whether heredity starts.
WHAT IS KNOWN:
- Frozen verdict WINDOW_NOT_SUPPORTED: genetic establishments U 24, RRIGHT 3, RWEAK 2, R128 5, BAND0 5;
  planned ~36 / ~13 / ~5 / ~0.7 / ~0.7 (archaeon/envgate2/VERDICT_2026-09-26.md:43-65; c5ba19571).
- Frozen per-arm predictions: branching R0 U 0.961, RRIGHT 0.694, RWEAK 0.422, R128 0.234, BAND0 0
  (archaeon/envgate2/RESULTS.json "predictions").
- COMPUTED-HERE from archaeon/envgate2/RESULTS.json established_glins (39 rows): of U's 24 establishments,
  21 are arm-unique; in RRIGHT, RWEAK, R128, BAND0 the arm-unique counts are 0, 0, 2, 2, and the four
  arm-unique non-U founders have first-birth inputs 71, 163, 15, 170, all outside 120..135. Every other
  non-U establishment is the SAME arrival (same block, arrival id, tape hash) that also established in U.
  So window-dependent establishment is ~21 in U and 0 in every rescue arm.
- ENVGATE-01: gated copiers produce copier-grade children only at inputs 120..131 (OFFSPRING_VIABILITY.json);
  the RESCUE forensic replay: "The gate does not drift. The lineages fail because they cannot GROW"
  (archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md:199-206).
WHAT IS UNKNOWN: Genuine: why a supposedly subcritical U (R0 0.96) establishes 21 times and RRIGHT (0.69)
never does; candidates are host amplification, mutation to wider/ungated gates, and multi-input children
(INFERRED list, none tested). Missing doc: the frozen R0 formula is "60 x k/256" (ENVGATE01 review s0) and
does not include hosting or mutation.
CHEAPEST DISCRIMINATOR: Recompute the branching model with per-input offspring viability from
archaeon/envgate/OFFSPRING_VIABILITY.json and census HITS.json, add a hosting term from the ENVGATE-01
births_hosted counts, and ask whether any parameter set gives U supercritical and RRIGHT subcritical.
A zero-compute prediction test, then (with operator) a 2-arm replay of a few ENVGATE-02 U blocks with
hosting disabled via the attributed core (archaeon/lineage/core.py).
LENSES: Archaeon envgate2 engine + lineage core; RIE observatory classes (ENV_GATED, HOST_DEPENDENT).
NEW-LENS SIGNAL: No.
RELATED: T3, T4, T5.

### T3. The "unexplained" BAND0 establishments: are they simply window-independent copiers?
QUESTION: Are the 5 BAND0 establishments (7x the frozen prediction) explained by founders whose gates lie
outside the blocked band plus arm-invariant takeover arrivals, rather than by any new mechanism?
WHY IT MATTERS: The closure record keeps them as an unexplained fossil (archaeon/envgate2/
ENVGATE_CLOSURE_2026-09-26.md:109-112); TH-001 lists "5 BAND0 establishments unexplained". Removing a
false anomaly is cheap and prevents a campaign on it.
WHAT IS KNOWN (COMPUTED-HERE, archaeon/envgate2/RESULTS.json established_glins):
- BAND0 block 11: arrival 17983, tape c1829c8f, first-birth input 221, NEAR_COPIER, 3.78M births, peak 128
  (takeover); same arrival establishes in U, R128, RRIGHT (not RWEAK).
- BAND0 block 13: arrival 541685, tape 41e34180, EXACT_UNGATED (256 exact inputs); establishes in all 5 arms.
- BAND0 block 14: arrival 74051, tape 23c1800b, EXACT_UNGATED; all 5 arms.
- BAND0 block 4 (NEAR_COPIER, first input 15, 2,351 births) and block 15 (NEAR_COPIER, first input 170,
  81 births) are the only BAND0-unique ones.
- The three shared takeovers are in blocks 11, 13, 14, which are also the three slowest blocks (5.9/3.3/5.9 h
  vs median 1.0 h, VERDICT:82-84): INFERRED explanation of the "heterogeneity observation" -- millions of
  births per world cost wall time.
WHAT IS UNKNOWN: Missing documentation more than genuine uncertainty. Genuine residue: why block 11's
takeover fails only in RWEAK (identical arrival, gate outside the band): contingency of a takeover on the
environment stream it never reads? And why an input-15 NEAR_COPIER in block 4 reached 2,351 births.
CHEAPEST DISCRIMINATOR: Already done from git above; the remaining test is a single-world replay of block 11
RWEAK vs U from the off-repo block files (C:\Prometheus-data\evidence\envgate02_2026-09-26\runs\) or from
seed, checking at which epoch the two diverge.
LENSES: Archaeon envgate2 + lineage core.
NEW-LENS SIGNAL: No.
RELATED: T2, T13 (contingency).

### T4. Host-mediated reproduction: amplification only, or can foreign execution originate?
QUESTION: Can execution hosting (an inert tape executing a resident's code, or a writer building another
tape) create a new heritable genome, or does it only amplify existing ones?
WHY IT MATTERS: Origination vs amplification is the central distinction for "capabilities not installed".
If hosts only amplify, open-endedness must come from elsewhere.
WHAT IS KNOWN:
- Archaeon: 26 of 63 INERT hosts gave births against the block-15 resident, 23 EXACT copies of the
  resident, all via foreign execution; "amplifies residents but does not originate genomes"
  (ENVGATE01_REVIEW s8; ruling R2 in archaeon/envgate/ADJUDICATION_ADDENDUM_2026-09-24.md:16-17).
  E-001 refinement: 71.5% of block-15 hosting births run resident material in place; 28.5% run the host's
  own relocated material, "a second route to the same outcome" (ops/campaigns/C-001/E-001/RESULT.md).
- BEE, contrary direction: "160/160 first self-replicators are BUILT_BY_COPY ... ALL of those are copy-born
  too: no initial random tape and no mutated initial tape became the first self-replicator"; RAMP 52%
  (GROUNDING_REPORT.md:60-68). BEE forensics: "65% of first self-replicators were constructed by other
  organisms' imperfect copies" (POST_CAMPAIGN_FORENSICS.md s2.6).
- BEE AN2: in 17 of 42 transplant runs the first autonomous reproducer descends from the RANDOM background,
  not the transplant (archaeon/causal_lens/PORTABILITY01_REPORT.md:119-120).
WHAT IS UNKNOWN: Genuine: in BEE, foreign WRITING appears to construct the first replicator (origination by
imperfect copying), while in Archaeon foreign EXECUTION only amplifies. Whether this is a real difference
between writing-hosts and executing-hosts, or a definitional one (BEE's "built by copy" uses parent = writer,
FF-3 in archaeon/causal_lens/FALSE_FRIENDS.md) is unresolved. Whether transplants catalyse background
origination (AN2) is untested.
CHEAPEST DISCRIMINATOR: For BEE AN2, compare background-origin rate in transplant runs vs matched no-transplant
runs from GROUNDING_RESULTS_RAW.jsonl.gz (fields first_self_replication.genealogy, spontaneous, cell).
For writer-origination, reclassify BEE's 160 first SRs with the causal lens's material shares (needs FULL
replay per specimen, 51-108 s each on a laptop per ops/campaigns/C-001/CAMPAIGN.md finding 2).
LENSES: causal lens (material vs executor), BEE traced replay, Archaeon lineage core.
NEW-LENS SIGNAL: Possibly: an ORIGINATION class exists in the lens (13,476 BEE births, PORTABILITY01 s3) but
no engine has an assay designed to score origination causally.
RELATED: T5, T6, T11.

### T5. Is host-conditioned reproduction one phenomenon across three engines? (assay drafted, not preregistered)
QUESTION: Does reproduction of donor material depend on the host's prior state, beyond the donor's own
writes, with the same sign in Archaeon, NPE and BEE?
WHY IT MATTERS: A cross-engine result would be substrate-independent evidence that reproduction is a joint
property of donor and host (host dependence), i.e. heredity is not a property of a genome alone.
WHAT IS KNOWN: Three independent sightings (PORTABILITY01_REPORT.md:168-176): Archaeon R2; NPE AN3 (v0.2:
16 of 34 births coherent: donor material flows in situ, necessity YES, random-victim sufficiency NO;
V02_REGRESSION_REPORT.md:55-66); BEE CAPTURE 1.26M births and 8,166 genuinely foreign-material-governed
births in r016299 (V02 s5). The assay is specified with arms REALIZED / SHAM / SUBSTITUTED / DONOR-BLOCKED,
kills, compute "well under 1 CPU-hour" (archaeon/causal_lens/HOST_CONDITIONED_ASSAY_READINESS.md,
READY_WITH_ENGINE_SPECIFIC_LIMITS). NPE lead: cross-execution in 46% of directed writes in host-conditioned
births vs 11% otherwise (ops/threads/TH-003.md).
WHAT IS UNKNOWN: Genuine: sign agreement across engines. Blocking: BEE needs a single-interaction harness on
its traced VM; NPE continuity NOT_IDENTIFIABLE in 25/34 (HOST_CONDITIONED s6). Operator gate: "No
preregistration or launch of the host-conditioned assay without the operator" (C-001/CAMPAIGN.md).
CHEAPEST DISCRIMINATOR: Archaeon-only arm first (native, ~0.1 ms per re-execution): 63 block-15 hosts x
{realized, sham, randomized-matched} using archaeon/lineage/core.py `_birth` as in tests 02/08/09.
LENSES: causal lens contract v0.3 + three adapters.
NEW-LENS SIGNAL: No (BEE harness is an instrument add, not a world).
RELATED: T4, T6, T7.

### T6. AN8: births with no necessary donor -- self-conversion, artefact, or pre-existing similarity?
QUESTION: In 11 of 34 NPE pair births, blocking the donor's writes on the REAL victim still leaves the
victim >= 0.9 like the donor. What made the "child"?
WHY IT MATTERS: If a victim converts itself toward a neighbour's genome, reproduction can happen by the
recipient's own dynamics (a crude "learning by imitation" at the chemistry level) -- or the parent label is
simply wrong in a third of births.
WHAT IS KNOWN: V02_REGRESSION_REPORT.md:65-66; ops/threads/TH-004.md (median initial fidelity 0.625).
Victims already matched donors at median 62.5% before the event.
WHAT IS UNKNOWN: Genuine. Candidate explanations listed in TH-004 are untested.
CHEAPEST DISCRIMINATOR: Re-execute the 11 births with (a) donor blocked + victim's own writes blocked,
(b) victim replaced by a fidelity-matched random tape. Tools: archaeon/causal_lens/tools_npe/npe_b6_replay.py
and NPE P-11 interact() (HOST_CONDITIONED s2). T-003 already ran NPE replays on a laptop (C-001/CAMPAIGN.md).
LENSES: NPE P-11, causal lens.
NEW-LENS SIGNAL: No.
RELATED: T5, T10.

### T7. What code runs at pc >= 2L in BEE, and does it change who authored those births?
QUESTION: 528,897 own-sourced copy writes in r016299 (66,669 in r038751) were executed by code outside both
the writer region and the window. Where is it and whose material is it?
WHY IT MATTERS: Unmodelled execution regions are where "environment as computation" could hide: code
living in I/O areas or reached by wrap-around is neither organism nor window.
WHAT IS KNOWN: ops/threads/TH-005.md; NOT_IDENTIFIABLE with the current probe (classifies only pc < 2L).
WHAT IS UNKNOWN: Missing instrumentation, not deep uncertainty.
CHEAPEST DISCRIMINATOR: Extend archaeon/causal_lens/tools_bee/codeprov_replay.py to bin pc >= 2L by region
and by taint label; run on r016299 using the committed config ops/campaigns/C-001/E-001/inputs/
r016299.config.json and the frozen harness commit 16fc6c2a (the T-001/T-002 recipe; 51-108 s, 141-150 MB on
a 4-thread laptop, C-001/CAMPAIGN.md findings 1-2). Verification of the result hash needs M2 or the
roles/Odysseus/th006 pack approach.
LENSES: BEE traced VM + Archaeon code-material check.
NEW-LENS SIGNAL: No.
RELATED: T8.

### T8. Does BEE's native self-replication count under-count copying run from self-copied code?
QUESTION: BEE's SR criterion is "copy ops ran with pc < L" (a WHERE reading). A writer that copies itself into
the window and then runs the copy is "foreign" by location but "own" by material. How many SR events are
missed and does any BEE verdict change?
WHY IT MATTERS: Self-copied code executing from its new location is a primitive form of self-modification
and relocation; if systematic, it is a mechanism class the native detector cannot see.
WHAT IS KNOWN: r038751: 27,083 of 28,163 location-foreign births are own-material governed; writes by
self-copied code 1,726,650 vs foreign code 941 (V02_REGRESSION_REPORT.md:98-108). ops/threads/TH-002.md
(parked; "Coordinate with Bellerophon before any claim").
WHAT IS UNKNOWN: Rate over BEE's 845 traced runs; whether sustained-lineage or SR verdicts move. The two
runs were chosen for being rich in decoupled births (V02 s10) -- not a random sample.
CHEAPEST DISCRIMINATOR: Code-material replay of a RANDOM sample of 10 of the 845 traced runs (58-122 s each).
Blocked on evidence locality: traced runs are only on M2 (TH-002), but configs can be committed per run as
in E-001.
LENSES: BEE traced VM, causal lens v0.3 (J21).
NEW-LENS SIGNAL: No.
RELATED: T7, T12.

### T9. Establishment, not acquisition, is the limit once a copier exists -- and it fails through carried state
QUESTION: What controls whether a competent donor, once present, establishes heredity? NPE says register
state left by the donor's own execution ("self-poisoning") in one cell but not the other; why?
WHY IT MATTERS: Heredity failing in CARRIED EXECUTION STATE while the genome is fine is a clean case of
state vs genome separation -- the precursor of any system whose capability depends on its internal state.
WHAT IS KNOWN: C-STATELESS-FFA6 CONFIRMED: ffa6 establishment 11/33 -> 34/42 (p=3e-5) with fresh state per
execution; C-STATELESS on both cells NOT_CONFIRMED (p=0.012), 7ae3 3/8 -> 4/8; X-DD-STATE-RESET CLEAN_NULL
"it is not the inherited state, it is the self-produced one"; X-DD-SELFSTATE: every stalled donor copies at
0.0 from the state its own execution leaves (18/18), 48% of established donors too (FINDINGS.md W1 E-W1-2
and EXPERIMENT_GRAPH.jsonl on the nestor branch). Proposed next: "Resolve the 7ae3 / ffa6 split" axis by
axis (W1_REPORT.md s7).
WHAT IS UNKNOWN: Genuine: why the same mechanism matters in ffa6 (Z8_SLOTTED, NICHES_HIGH_MIG) and not
confirmably in 7ae3 (Z8_64, WELL_MIXED). 48% of established donors also self-poison, so self-poisoning is not
sufficient to block -- what rescues them is unknown.
CHEAPEST DISCRIMINATOR: The per-run JSON for x_dd_selfstate / x_dd_stateless is in git on the nestor branch
(roles/Nestor/campaigns/npe-w1-donor-discovery-2026-09-26/*/SUMMARY.json); tabulate which property of the 11
self-poisoned-but-established donors differs (partner availability, side, niche migration). Pure reading.
LENSES: NPE only. BEE has registers that start at 0 each execution? (UNKNOWN; worth checking in
prometheus/z80atlas/vm.py) -- if BEE resets state per execution, BEE is the natural "stateless" control.
NEW-LENS SIGNAL: No.
RELATED: T1, T10.

### T10. Pair-tape heredity: erosion, splice and the depth-1 wall -- what fraction of heredity loss is world physics?
QUESTION: In NPE the world's own operators (recombination splice, two-sided write-back) both manufactured
fake replicators and stopped real ones. How much of "heredity failure" in any of these worlds is the world
overwriting organisms rather than organisms failing?
WHY IT MATTERS: Persistence of heritable information is a property of the medium's write discipline; a
general law ("heredity requires atomic write-back") would transfer to other substrates.
WHAT IS KNOWN: Z80A-D05: fidelity read after _mutate; splice made the match in 6,287 of 6,547 events;
C-RUNAWAY: splice off 7/150 vs 0/150 runaways; tape-write erosion ~5%/byte/epoch, ~25x nominal; C-ATOMIC C1
46/80 vs 1/80 (p=4e-17), C2 generality 1/120 vs 0/120 NOT confirmed (FINDINGS.md:280-328). E-7: depth-1 wall
under energy economies is newborn starvation, 20/40 vs 4/40 (FINDINGS.md:230-239). Losing tickets lose by
CESSATION not extinction (X-TICKET, FINDINGS.md:305-308).
WHAT IS UNKNOWN: Genuine: whether BEE (LDIR into a neighbour window) and Archaeon (COPY op) have an
analogous erosion term (both overwrite neighbours: BEE CAPTURE 1.26M births). Nobody has measured
"bytes changed per organism per epoch not by an accepted copy" in BEE or Archaeon.
CHEAPEST DISCRIMINATOR: From BEE GROUNDING_RESULTS_RAW.jsonl.gz, 'captures' vs 'sr_max_depth' per run;
then a small replay measuring per-organism non-copy byte turnover in BEE (stdlib VM).
LENSES: NPE, BEE, Archaeon.
NEW-LENS SIGNAL: No.
RELATED: T9, T13.

### T11. Do descendants acquire competence the founder lacks? (C-SWAP-ACQUIRE missed by one)
QUESTION: When a competent genome is implanted into a foreign cell where it cannot copy from a fresh state,
do descendant genomes acquire copy competence there?
WHY IT MATTERS: This is the most direct "capability not installed" observation in the Z80 record:
competence as a property of genome x cell, acquired by descendants.
WHAT IS KNOWN: X-DONOR-SWAP: genome runs away in 3 of 11 foreign cells; competence 0.955 only in 7ae3/ffa6,
0.0 in ten others ("competence is a property of genome x cell"); X-SWAP-ANCESTRY all five foreign runaways
founder-descended; C-SWAP-ACQUIRE NOT CONFIRMED 9/240 vs 0/240 (p=0.0018; rule needed 10); X-ACQUIRE: 9-15%
(lower bound) of runaway populations carry genomes that copy where the founder cannot; X-CONTENT: only 13-25%
of bytes are founder material (FINDINGS.md:329-366).
WHAT IS UNKNOWN: Genuine and near a decision boundary. Also a definitional trap: founder-descended = lineage
descent, not content inheritance (X-CONTENT). The SI framing was withdrawn by operator directive
(FINDINGS.md:389-393), so this is a Nestor question only.
CHEAPEST DISCRIMINATOR: Mine the 9 C-SWAP-ACQUIRE runaways (per-run JSON under
roles/Nestor/campaigns/c9x-explore-2026-09-24/ on the nestor branch, 2,434 result files) for which bytes
differ between founder and competent descendants, and test the minimal diff in isolation (stdlib).
LENSES: NPE; causal lens (z8taint material).
NEW-LENS SIGNAL: No.
RELATED: T1, T12.

### T12. What is conserved in runaway heredity -- and is it more than purifying selection?
QUESTION: Runaways conserve OP_SELF and LDIR as material and replace everything else (C-CORE 17/27). Is that
distinguishable from purifying selection + drift, and does the conserved core ever move?
WHY IT MATTERS: Separates "machinery that preserves itself" from generic purifying selection; the null is what
Aporia #621 asked for.
WHAT IS KNOWN: C-CORE CONFIRMED, thin margin; X-CORE-TIME: core held at ~0.99 from epoch ~200 while other
founder material falls to 0 by 300-900; "one run shows a late sweep instead"; interpretation limit: "exactly
what PURIFYING SELECTION on a functional core plus drift elsewhere predicts" (FINDINGS.md:367-382). Open
branch: "an SI knockout + purifying-selection null (Aporia #621 s3)", "e160 coverage of X-CORE"
(roles/Nestor/STATUS.md WINDOW CLOSE).
WHAT IS UNKNOWN: Genuine: the late-sweep run (a core that is re-fixed rather than held) is n=1 and unexplained.
CHEAPEST DISCRIMINATOR: Per-position conservation curves already exist for 27 runaways (C-CORE evidence dir);
fit a neutral-drift + purifying model per position and look for any position conserved beyond what its
knockout cost predicts. Pure reading of c_core outputs if they are in git (CHECK: campaigns/c9x-explore-
2026-09-24/c_core* on the nestor branch).
LENSES: NPE.
NEW-LENS SIGNAL: No.
RELATED: T11, T17.

### T13. Why do most unselected origins die? (persistence after origin)
QUESTION: 160 spontaneous origins in BEE, only 39.4% sustain (prereg >= 50% FAILED). Competition,
overwriting by neighbours, or hostile random background?
WHY IT MATTERS: Establishment after origination is the bottleneck in all three worlds (NPE ~13% lottery
tickets decided in ~12 epochs; Archaeon R0 < 1; BEE 39%). A shared cause would be a general law of early
lineage survival.
WHAT IS KNOWN: GROUNDING_REPORT.md:56-59 and s9 item 7 ("New uncertainties: why unselected origins mostly
die (competition vs overwriting vs hostile random neighbours)"); fresh random worlds 95-100% extinct in
LOCAL/NICHES/GRAPH; WELL_MIXED survives most (73% extinct). NPE X-DOSE-CURVE: founders are independent
lottery tickets p~0.13, no critical mass (FINDINGS.md:302-304); X-TICKET dominant loss is cessation.
WHAT IS UNKNOWN: Genuine.
CHEAPEST DISCRIMINATOR: roles/Bellerophon/forensics_2026-09-23/receipts/GROUNDING_RESULTS_RAW.jsonl.gz has
per-run first_self_replication.tick, genealogy, summary.extinct_tick, captures, sr_max_depth, cell: regress
sustain on origin tick, captures, topology, and genealogy length. Seconds of stdlib Python.
LENSES: BEE; NPE X-TICKET data for comparison.
NEW-LENS SIGNAL: No.
RELATED: T2, T10.

### T14. Coupling campaign: are the "de novo competent self-replicators" in control arms self-copiers at all?
QUESTION: In the coupling origin ledger, 15 of 68 de novo competent "SR" tapes have NO copy op in their own
architecture descriptor, and they concentrate in the non-contingent arms. Are control-arm "acquisitions"
mostly context-dependent or hosted reproducers, and does that sharpen or weaken the ON > control contrast?
WHY IT MATTERS: The only acquisition evidence of the coupling loop (computation -> resource -> reproduction)
is ECHO K40 29/150 ON vs 6/150 controls (COUPLING_CAMPAIGN_REPORT.md:49-53). What the control 6s are
determines whether ON is selecting a different KIND of organism.
WHAT IS KNOWN (COMPUTED-HERE from roles/Bellerophon/coupling_2026-09-24/COUPLING_ORIGIN_LEDGER.jsonl):
ECHO K40: ON 27 self-copiers + 2 no-copy; YOKED 1 self + 5 no-copy; OFF 3 self + 2 copy-not-self + 1 no-copy;
SHUFFLED 3 self + 2 copy-not-self + 1 no-copy. Across all cells, no-copy tapes are 3/39 in ON vs 12/29 in
non-ON arms. The origin rule counts "dominant_competent_sr_tape" (coupling_analysis.py:120-124), which is
labelled SR in-world, while arch descriptors are measured in isolation. BEE forensics already knew a
"context-dependent copiers that write nothing when run alone" class, 57/361 = 16%
(POST_CAMPAIGN_FORENSICS.md s2.2).
WHAT IS UNKNOWN: Whether no-copy tapes reproduce by executing window/partner code (B6 WHERE vs WHAT) or by
being hosted; whether ON vs YOKED differs significantly in self-copier origins (27 vs 1 looks larger than 29
vs 6, INFERRED, not tested).
CHEAPEST DISCRIMINATOR: Replay each of the 15 tapes alone and with a random partner through
prometheus/z80atlas/vm.py execute() (stdlib), record whether copy writes occur and whose code runs. Minutes.
LENSES: BEE z80atlas VM; causal lens WHO/WHERE/WHAT.
NEW-LENS SIGNAL: No.
RELATED: T4, T8, T15.

### T15. Can coupling carry copiers up a task ladder? (multi-day campaign running blind)
QUESTION: Beyond maintenance of seeded code, does contingent earning produce acquisition of the NEXT task
(ECHO -> INC -> COND_ONE), protection of task code, and common repair?
WHY IT MATTERS: This is the direct test of capability accumulation that was not installed, in a Z80 world.
WHAT IS KNOWN: Coupling campaign: P1-P4 hold, P5 reversed at ceiling, P6 4/60 vs 0/60 n.s.; "core effects are
MAINTENANCE of seeded code"; B-rand 0/3,200 (COUPLING_CAMPAIGN_REPORT.md s1, s5). Multi-day prereg frozen
12ce26e23, 4,160 runs x 20k ticks, lanes LADDER1/COPIER/REPAIR/LADDER2, launched 2026-09-26T16:40:28Z,
"Blind until md_analysis.py runs after the stop" (origin/bellerophon/multiday-campaign-2026-09-26
roles/Bellerophon/STATUS.md). Grounding established "reproduction and computation are antagonistic, not
coupled" in un-coupled physics (GROUNDING_REPORT.md s4, s7).
WHAT IS UNKNOWN: The result (not in git as of this pass). Also whether the campaign is a blind lane for the SI
program: Bellerophon was exposed by comms #585 (programs/selective_irreversibility/BLIND_LANES.md:132-148).
CHEAPEST DISCRIMINATOR: None to run -- read md_analysis output when committed. Pre-commit a prediction now.
LENSES: BEE.
NEW-LENS SIGNAL: No.
RELATED: T14, T16.

### T16. Reproduction-computation antagonism: is it general?
QUESTION: In BEE, endogenous reproduction selects the copier and task code decays (EXTERNAL-only 178 vs
ENDOGENOUS-only 2); grafted copiers destroy task witnesses; beneficial mutants mostly break the copier. Is
antagonism between self-copying and computing a substrate law in shared-memory byte worlds?
WHY IT MATTERS: If reproduction machinery and computation compete for the same bytes/cycles, capability
accumulation requires a separation mechanism (modularity, protection) -- the thing BEE Q2 now tests.
WHAT IS KNOWN: GROUNDING_REPORT.md s4, s6 ("the effect that exists has the opposite meaning
(reproduction-computation ANTAGONISM)"; "98 of the 115 'beneficial' mutants (85%) are mutations that BREAK the
copier"). NPE A-2: reproduction PAIR_EXECUTION -> EXTERNAL mean d -0.12 favouring EXTERNAL (FINDINGS.md:56);
NPE C9-H1R: gating answers on cue consumption abolishes competence when reading costs instructions (0.000 vs
0.200) (FINDINGS.md:263-273). Archaeon: transplanted lineages persist 39/39 but task competence travels 0/39
(Z80ATLAS_POSTCAMPAIGN_REVIEW_2026-09-23.md:21-23).
WHAT IS UNKNOWN: Genuine: whether antagonism is about shared bytes (copy covers task), shared cycles, or
selection target. Coupling origin ledger shows copy_covers_task True in 47/68 de novo origins (COMPUTED-HERE),
i.e. task code sits inside the copied span.
CHEAPEST DISCRIMINATOR: From COUPLING_ORIGIN_LEDGER.jsonl and the causal ledger, compare copy_covers_task and
task_before_copy between ON and control origins (fields present). Seconds.
LENSES: BEE, NPE, Archaeon.
NEW-LENS SIGNAL: A world where copy machinery and task code cannot overlap (separate code segments) would be
a new lens; none exists in the Z80 family.
RELATED: T15.

### T17. Environment-as-computation: copiers that read their destination from the environment
QUESTION: 85% of Archaeon vmcopy32 copiers are exact only when the input stream names the neighbour-window
base (128). Is the environment computing part of the organism's reproduction, and can lineages liberate
themselves from that dependence?
WHY IT MATTERS: A reproductive program whose key parameter is supplied by the environment is a minimal case of
an agent offloading computation onto its world; "liberation" would be an acquired capability.
WHAT IS KNOWN: Census: dominant copier "reads its copy DESTINATION from the environment (IN C ... COPY loop)";
94/96 exact copiers exact at exactly ONE input byte (Z80ATLAS_RULINGS_FOLLOWUP_REVIEW:106-116). ENVGATE-01 block
15 U: "an EXACT_UNGATED copier ... evolved inside the world. Gating DISAPPEARED once a lineage took over"
(ENVGATE01_REVIEW:222-225, falsifier list :272-273). RIE-01 observatory already defines ENV_GATED, ENV_FREE,
HOST_DEPENDENT, liberation, acquisition (archaeon/rie/world.py docstring); RIE-01 staged, unfrozen, not
launched, precondition failed (ENVGATE_CLOSURE:106).
WHAT IS UNKNOWN: Genuine: how often liberation happens, and whether it is selection or drift. Only one
documented instance.
CHEAPEST DISCRIMINATOR: In ENVGATE-01 LINEAGES.json (1.2 MB, in git) check whether ruler/gate fields exist for
dominant descendant genomes; if so, count gate-set widening events per established lineage. Otherwise needs
RIE-01 or a targeted replay (operator).
LENSES: Archaeon (RIE observatory).
NEW-LENS SIGNAL: No -- RIE-01 is that lens, staged.
RELATED: T2, T18.

### T18. Parent-chain vs genetic identity: how much of any lineage result is a labelling choice?
QUESTION: Parent-chain tracing gives 8-42x more "establishments" than genetic tracing. Which historical
lineage claims in NPE and BEE rely on executor/writer labels and would move under genetic identity?
WHY IT MATTERS: Heredity without causal control (labels that follow the executor) is the most repeated
failure in this territory; knowing its size bounds every lineage claim.
WHAT IS KNOWN: ENVGATE-02: parent-chain U 194, RRIGHT 126, RWEAK 59, R128 139, BAND0 108 vs genetic
24/3/2/5/5 -- "A label-based endpoint would have manufactured a rescue gradient" (VERDICT_2026-09-26.md:68-70).
FALSE_FRIENDS FF-1..FF-34 (archaeon/causal_lens/FALSE_FRIENDS.md). NPE C9-D14: pair tape keeps id while bytes
are replaced (identity to birth genome 0.97 -> 0.00 by 600 epochs, FINDINGS.md:217). X-CERT-BREAK: ~10%
per-edge certification break caps certified depth at ~1/p (FINDINGS.md:383-388).
WHAT IS UNKNOWN: The ENVGATE-01 historical genetic audit (21 worlds, audit_envgate01.py) was never run
(roles/Archaeon/RESUME.md step table). Missing execution, not uncertainty.
CHEAPEST DISCRIMINATOR: Run archaeon/lineage/audit_envgate01.py on a few worlds -- needs ENVGATE-01 run state
(off-repo on M2) or reconstruction from seed with the frozen engine (deterministic; cost unknown, likely hours
per world -- CHECK).
LENSES: Archaeon lineage core.
NEW-LENS SIGNAL: No.
RELATED: T3, T4.

### T19. Symmetric recombination: when does a child have a singular lineage? FLOW vs DIFFERENCE (B8)
QUESTION: Contribution has two referents: which source the operator copied a unit from (FLOW) vs which source's
distinguishing material the child carries (DIFFERENCE). Which one governs heredity-relevant claims?
WHY IT MATTERS: Any claim that a capability was "inherited" from a parent under recombination depends on it.
WHAT IS KNOWN: E-002: 10 of 15 "decided" GA crossovers reversible by flipping mask bits that leave the child
byte-identical; 0/16 departs from the operator null; the one "ILL_POSED" case is a self-cross; proposed rule
C-OP' not adopted; candidate break B8 FLOW vs DIFFERENCE (ops/campaigns/C-001/E-002/RESULT.md).
WHAT IS UNKNOWN: "F2, privileged operators with thin margins. No case appears in Git" -- data on M2 (E-002
RESULT). Whether C-OP' holds in a second substrate. NPE C9-D11 (H3 walks non-causal pair edges in
RECOMBINATION cells) is NOT repaired (FINDINGS.md:214).
CHEAPEST DISCRIMINATOR: Apply C-OP' to NPE RECOMBINATION pair births (splice events are logged per Z80A-D05) --
NPE's splice is a privileged operator, the missing F2 case.
LENSES: causal lens; NPE; PTE (non-Z80).
NEW-LENS SIGNAL: No.
RELATED: T18.

### T20. Existence vs accessibility: one shape seen by Crius, NPE, BEE and Archaeon
QUESTION: Is "the capability exists and is executable but search cannot reach it" a single phenomenon with a
measurable accessibility coordinate?
WHY IT MATTERS: The frontier question is not whether a capability is possible but whether undirected variation
can reach it.
WHAT IS KNOWN: Crius C2: reuse executable at three levels of construction but 0 reproducible ACC > FRESH over 36
runs, "not accessible to (8+24) mutation + splice in 300 iterations" (roles/Crius/STATUS.md). NPE: block-copy
present in 87/96 plain populations yet donors 1/96 (E-W1-1). BEE: copier is ONE mutation away from any tape
carrying setup (HISTa: 126/345 NOP-ablated tapes still replicate; POST/GROUNDING s5) -- a wide shallow basin,
i.e. high accessibility; but random tapes 0/60 have any single mutant that self-copies (NEIGHBOURHOOD, s2.6).
WHAT IS UNKNOWN: Genuine: a common metric (e.g. expected mutational distance from random material to the
capability) has not been computed in any engine.
CHEAPEST DISCRIMINATOR: For BEE and Archaeon vmcopy32, estimate by sampling the distribution of Hamming
distance from random tapes to the nearest copier using the committed VMs (stdlib, small samples).
LENSES: BEE, Archaeon census, NPE, Crius.
NEW-LENS SIGNAL: Maybe -- a shared accessibility metric would be a cross-engine instrument.
RELATED: T1.

### T21. Heredity without fidelity: establishments with 17% mean fidelity
QUESTION: ENVGATE-01 copier-founded establishments have median mean fidelity 0.17 and exact-birth fraction
1.6%, yet persist a median 357 epochs after the founder's removal. What is inherited, if not the sequence?
WHY IT MATTERS: Persistence of a lineage whose members are mostly not copies challenges the sequence-copy notion
of heredity; it may be heredity of a gate/function rather than bytes (cf. NPE C-CORE: 13-25% founder bytes).
WHAT IS KNOWN: ENVGATE01_REVIEW:166-172; "Descendants keep gate 128 (46/47 samples)" (:202); NPE X-CONTENT and
C-CORE (FINDINGS.md:362-375).
WHAT IS UNKNOWN: Genuine: whether a functional core (the gate + copy loop) is what is conserved in Archaeon as
in NPE.
CHEAPEST DISCRIMINATOR: If ENVGATE-01 FORENSIC_REPLAY.json (75 KB, in git) contains sampled descendant tapes,
compute per-position conservation relative to founder and compare with the census "essential bytes" (median 4).
LENSES: Archaeon, NPE.
NEW-LENS SIGNAL: No.
RELATED: T12, T17.

### T22. The world reproduces and the organism gets credit: a general audit
QUESTION: How much apparent organism reproduction in each engine is actually performed by world operators
(migration spawn, splice, sweeps, chamber contact)?
WHY IT MATTERS: Any claim of self-reproduction or self-modification must subtract world-made copies.
WHAT IS KNOWN: BEE P1: POLLINATION migration spawns copies under endogenous physics, median 888 per run;
extinction 0/150 v1 vs 148/150 v2 (POST_CAMPAIGN_FORENSICS s2.4, GROUNDING s3 G7P1). NPE Z80A-D05 splice
(FINDINGS.md:207). BEE COPY_EVENT: 9,271 of 14,003 "first replications" are junk (POST s3.1). Archaeon:
"Chamber-to-ecology contact is itself a reproductive channel" (ENVGATE01_REVIEW:298-300). BEE grounding
summary field 'world_copies_under_endogenous' exists per run (GROUNDING_RESULTS_RAW).
WHAT IS UNKNOWN: Mostly repaired per engine; no cross-engine accounting of world-made vs organism-made births.
CHEAPEST DISCRIMINATOR: Sum world_copies_under_endogenous per cell from GROUNDING_RESULTS_RAW.jsonl.gz to verify
the repaired physics shows 0 outside declared channels.
LENSES: all three.
NEW-LENS SIGNAL: No.
RELATED: T4, T10.

### T23. Contingency: identical arrivals, different fates
QUESTION: How sensitive is lineage takeover to environment streams the lineage never reads?
WHY IT MATTERS: Measures how much of "which capability gets established" is historical accident.
WHAT IS KNOWN: COMPUTED-HERE: ENVGATE-02 block 11 arrival 17983 (gate input 221, outside every manipulated
band) takes over in 4 of 5 arms, fails in RWEAK; block 13 arrival 541685 reaches 1.9M births in 4 arms but
629k in RWEAK (archaeon/envgate2/RESULTS.json). ENVGATE-01 block 15 takeover by a 255-gated copier in RESCUE and
BAND (ENVGATE01_REVIEW:194-198). NPE: competence 0.955 vs 0.0 across near-identical cells (FINDINGS.md:333-334).
WHAT IS UNKNOWN: Genuine; no divergence-time measurement exists.
CHEAPEST DISCRIMINATOR: Replay block 11 U vs RWEAK from seed with the frozen engine and log first epoch of
population divergence (needs estimate of per-block cost; blocks took 1-6 h on M2 -- too long for a quick spike
unless truncated at first divergence).
LENSES: Archaeon envgate2.
NEW-LENS SIGNAL: No.
RELATED: T3.

### T24. Cross-engine evidence locality blocks most verifications
QUESTION (instrumentation): which of the above can be verified off M2 at all?
WHY IT MATTERS: Every thread that needs a FULL replay or preserved traces is gated on M2-only evidence.
WHAT IS KNOWN: "compute was portable and evidence was not" (ops/threads/TH-006.md); BEE run dirs 2.2 GB local
only (GROUNDING_REPORT.md:7); ENVGATE-01/02 evidence under C:\Prometheus-data, off-machine copy BLOCKED
(ENVGATE01_REVIEW s1); BEE 72 h CAMPAIGN_PACKET.md not in git (roles/Bellerophon/STATUS.md); Atlas indexes no
Z80 world (notes/C_engines.md D1). The TH-006 pack shows a 10,970-byte committed pack suffices for one task.
WHAT IS UNKNOWN: Which specimen sets (BAND0 fossils, block 13/15, 7ae3 runaways) are reconstructible from seed
+ commit alone.
CHEAPEST DISCRIMINATOR: For each fossil, check whether a seed + frozen commit reproduces it on a laptop
(deterministic engines: BEE 606/606, 341/341 replays; Archaeon legacy-exact).
LENSES: n/a (operational).
NEW-LENS SIGNAL: No.
RELATED: all.

---------------------------------------------------------------------------------------------------

## 3. Anomalies and reversals

| what | evidence | failure shape |
|---|---|---|
| NPE 1,031 "spontaneous replicators" -> 57 | all 1,031 PAIR_EXECUTION; ~88% splice artefacts (fidelity read after _mutate, Z80A-D05); 57 survive P-11, max depth 2 (roles/Nestor/FINDINGS.md:19-41, 192-195, 207) | measurement taken after the world's own variation operator; similarity mistaken for copying |
| NPE A-4 endogenous-only accessibility | 0 births, 0 deaths in 4,000 epochs; matched control crossed first (FINDINGS.md:197-201) | frozen population read as competence; control inherited from sibling (Z80A-D04) |
| NPE C9 H1 | world never passed output_gate into task; four arms identical to last decimal (FINDINGS.md:261-262) | intervention inert at the measurement; identical arms = defect signature |
| NPE X-POSITION | "register dependence" was partner sabotage in the assay draw (EXPERIMENT_GRAPH; FINDINGS D.11) | assay artefact built into the counterfactual |
| NPE C-CRITICAL-MASS "superadditive" | X-DOSE-CURVE LRT p=0.42, independent tickets (FINDINGS.md:297-304) | null parameter taken from a small arm as exact |
| NPE X-SWAP-ORIGIN "NATIVE" | meant "outside certified chain"; certification breaks ~10%/edge (FINDINGS.md:337-353, 383-388) | instrument cap read as biology |
| NPE "founder-descended" | lineage descent, 13-25% founder bytes (FINDINGS.md:362-366) | identity/label mistaken for content inheritance |
| NPE C-SWAP-ACQUIRE | 9/240 vs 0/240, bar 10 (FINDINGS.md:357) | near miss; open |
| NPE C-STATELESS | both cells p=0.012; effect only in ffa6 (graph, nestor branch) | cell-dependent mechanism |
| BEE 72 h: 5 flag classes (1,629 flags) | 2 FALSIFIED, 1 INSTRUMENT_FAILURE, 2 CONFOUNDED/DETECTOR_ONLY (POST_CAMPAIGN_FORENSICS headline) | detector triggers + allocation feedback ("exposure, not discovery", s2.1) |
| BEE "endogenous not external" | reversed: EXTERNAL-only 178 vs ENDOGENOUS-only 2, p 2.5e-15 (GROUNDING_REPORT.md:20) | direction inverted once one-axis matched design was used |
| BEE POLLINATION topology effect | defect P1: migration spawns copies; extinction 0/150 vs 148/150 (GROUNDING s3 G7P1) | world-made reproduction credited to organisms/topology |
| BEE sustained 90% | 39.4% of unselected origins (GROUNDING s3 G2) | trigger-selected subset |
| BEE beneficial density | effect is copy-task antagonism (GROUNDING s4) | sign of meaning inverted |
| BEE HISTa ablation | NOP-ablated tapes replicate 126/345; new copy byte 1-18 bytes away (GROUNDING s5) | knockout not a knockout in a wide shallow basin |
| BEE P5 preservation | r_cc 0.999 both arms, reversed by 0.0007 (COUPLING report s1; F7) | ceiling metric |
| BEE P3 heritability | copy fidelity of whole-window LDIR, passes for any code (F6) | metric measures the copier, not evolution |
| BEE AN1 decoupling 233,499 births | mostly location accounting (B6); 27,083/28,163 own-material in r038751 (V02 s5) | WHERE read as WHAT |
| Archaeon 26 spontaneous-replication flags | all transplanted-lineage replication, material inserted twice; de novo = 0 of 101,003 (Z80ATLAS_POSTCAMPAIGN_REVIEW:13-19) | provenance not travelling with material |
| Archaeon DENOVO-01 | 0/80, every treatment world extinct (same review :33-36) | clean null |
| Archaeon ENVGATE-01 rescue | C4 significance from one takeover world (block 15, 255-gated); block-level p=0.5 (ENVGATE01_REVIEW s6) | non-independent lineages + host labels |
| Archaeon ENVGATE-02 | WINDOW_NOT_SUPPORTED; BAND0 5 vs 0.7 predicted (VERDICT) | model missing window-independent founders (COMPUTED-HERE, T3) |
| Archaeon ENVGATE-02 analyze.main() | KeyError 'blocks'; wrapper (VERDICT:35-40) | frozen code never exercised on the frozen config |
| Lens v0.1 NPE adapter | used WHO-wrote as material share: 20/34 -> 9/34 (FF-32, V02 s3) | adapter maps wrong referent |
| Lens v0.1 PTE "11/16 no majority parent" | counting artefact; 1/16 tie, which is a self-cross (FF-33, E-002) | incomplete evidence + definitional |
| Lens "3/48 match behaviour" | uninformative: ceiling signatures (E-002, B7) | saturating criterion |
| Archaeon moat flags | 828 of 932 seeded replays QUALIFIED; partial confound (RULINGS_FOLLOWUP:30-34) | blanket subtraction would destroy valid flags |
| Unexplained, still open | BAND0 (partly explained here), blocks 11/13/14, block-11 RWEAK miss, AN2, AN8, pc >= 2L writes, 7ae3 side-1-only copying (roles/Nestor/STATUS.md resume item 3), late core sweep (X-CORE-TIME) | -- |

---------------------------------------------------------------------------------------------------

## 4. Recurring shapes (with evidence)

S1. The world does the reproducing and the organism gets the credit. BEE P1 migration spawn; NPE splice
(Z80A-D05); Archaeon chamber contact and host labels; BEE COPY_EVENT junk. (T22 citations.)

S2. Heredity without causal control (labels follow executor/slot/id, not material). Parent-chain 8-42x
genetic (ENVGATE-02 VERDICT:68-70); NPE id kept while bytes replaced (C9-D14); anc = slot lineage (X-CONTENT);
BEE parent = writer (FF-3). Every engine converged on this independently.

S3. Presence is not access. The capability exists but is not reached: NPE block-copy present 87/96, donors 1/96;
Crius reuse executable but 0 accessible; Archaeon 1-byte gate copiers need one exact input 1/256 of the time.
Contrast: BEE's basin is wide per population once setup exists (one mutation away).

S4. Barriers in series; relieving one exposes the next. NPE: acquisition (encoding) -> establishment (register
state) -> erosion -> depth-1 starvation (W1_REPORT s3; FINDINGS E-7..E-10). BEE: origin 1-5% -> sustain 39%.
Archaeon: exact copier 9.6e-6 -> establishment ~0.46 per latent copier (ENVGATE01 s5).

S5. Persistence without propagation / copying ceases while lineages live. NPE X-TICKET "dominant loss is
cessation, not extinction"; H2 REPLICATION_EVENTS_WITHOUT_PROPAGATION; 911 of 1,031 depth 1. Archaeon
establishments with fidelity 0.17. (Also AGE outside this territory: "the substrate lacks propagation",
ENGINE_LENS_CARDS AGE card.)

S6. Host dependence of reproduction, seen three times independently: Archaeon R2, NPE AN3 (16/34), BEE CAPTURE
and 8,166 foreign-material births (T5).

S7. Self/foreign distinction breaks down under relocation. BEE writers copy themselves then run the copy
(foreign by location, own by material); NPE threads run the other organism's code in 26.4% of directed writes;
Archaeon block-15 hosts run host material relocated (E-001 RESULT). The WHO/WHERE/WHAT split (B6) is the
same axis applied recursively; "role-splitting is not yet shown to be bounded" (V02 s10). B8 (FLOW vs
DIFFERENCE) may be the next recursion.

S8. Competence is a property of genome x context, not genome. NPE donor competence 0.955 in 2 cells, 0.0 in 10
(X-DONOR-SWAP); Archaeon copiers exact at one input; self-poisoning register state (E-W1-2); BEE context-
dependent copiers 16%.

S9. Reproduction antagonises computation unless coupled. BEE G3/G4; NPE C9-H1R cost of reading; Archaeon 0/39
task retention in transplants; coupling restores maintenance, acquisition only at ECHO (T16).

S10. Headline -> own forensics -> fraction. Every engine: 1,031->57, 1,629 flags->0 classes, 26->0 de novo,
GATING_CAUSALLY -> PARTIALLY, 233,499 decoupled -> mostly artefact. The forensic instruments (P-11, traced
replay, taint) are now the durable products.

S11. Conservation of machinery, turnover of everything else. NPE C-CORE (OP_SELF + LDIR held ~0.99, rest to 0);
Archaeon descendants keep gate 128 (46/47) at fidelity 0.17 (INFERRED parallel; not measured per position).

Two engines, same thing: host-dependent reproduction (Archaeon + NPE, T5); copy accessibility set by primitive
encoding (NPE + BEE + Archaeon census, T1); establishment as the limit after acquisition (NPE + Archaeon + BEE).
Two engines, apparently contradictory: BEE says foreign writing CONSTRUCTS first replicators (160/160 built
by copy) while Archaeon says foreign execution never ORIGINATES (T4); BEE finds ramps with partial copiers
(52%) while NPE finds "Random computation produces no partial copies at all" (X-NEARMISS, graph) -- different
VMs, but no one has reconciled them.

---------------------------------------------------------------------------------------------------

## 5. Cheap discriminators runnable on a 4-core 7 GB laptop, stdlib Python, git only

D1 (DONE here, 1 s): BAND0 decomposition. File: archaeon/envgate2/RESULTS.json (established_glins, per_block,
predictions). Result: all non-U establishments are either arm-invariant arrivals (blocks 11/13/14) or
founders gated outside 120..135; window-dependent establishments U 21, every rescue arm 0. Next step: write it
into T2/T3 as a registered prediction.

D2 (minutes): Coupling origin no-copy tapes. Files: roles/Bellerophon/coupling_2026-09-24/
COUPLING_ORIGIN_LEDGER.jsonl (tapes, hex), prometheus/z80atlas/vm.py (execute(), line 85),
prometheus/z80atlas/world.py (for the window layout), roles/Bellerophon/coupling_2026-09-24/tools/
coupling_analysis.py:120 (origin rule). Replay 15 no-copy tapes alone / with random partner; record copy
writes and executing region. Changes the reading of ECHO acquisition (T14).

D3 (seconds): Why origins die. File: roles/Bellerophon/forensics_2026-09-23/receipts/
GROUNDING_RESULTS_RAW.jsonl.gz (12,130 rows: first_self_replication.tick/genealogy, summary.extinct_tick,
captures, sr_max_depth, world_copies_under_endogenous, cell, spontaneous). Regress sustain on tick, captures,
topology, ramp length (T13, T22, T4-AN2 background-origin rate).

D4 (an hour of reading + a table): Accessibility vs encoding length. Files: prometheus/z80atlas/vm.py,
archaeon/z80atlas/vm.py, roles/Nestor/campaigns/z80atlas-2026-09-19/z8.py (main) and the dense-encoding
variant under campaigns/c9x-explore-2026-09-24/ on origin/nestor/s1-forensics-2026-09-23,
roles/Bellerophon/forensics_2026-09-23/receipts/BASIN.json and RATES.json, archaeon/z80atlas/census/
RESULTS.json and HITS.json, NPE C-DENSE / C-DENSE-COPY VERDICT.json (nestor branch). Register the
log-rate-vs-length prediction before fitting (T1).

D5 (seconds): Branching model with hosting. Files: archaeon/envgate/OFFSPRING_VIABILITY.json,
archaeon/envgate/RESULTS.json, archaeon/envgate2/RESULTS.json (predictions), archaeon/z80atlas/census/HITS.json.
Question: can any hosting/mutation term make U supercritical and RRIGHT subcritical (T2).

D6 (seconds): Antagonism fields. Files: COUPLING_ORIGIN_LEDGER.jsonl, COUPLING_CAUSAL_LEDGER.jsonl (439 rows;
kinds auto_candidate, laneF_task, laneG_perturbation). Compare copy_covers_task / task_before_copy by arm (T16).

D7 (minutes): Self-poisoned but established donors. Files (nestor branch): roles/Nestor/campaigns/
npe-w1-donor-discovery-2026-09-26/x_dd_selfstate/SUMMARY.json, x_dd_establish/SUMMARY.json,
x_dd_stateless/SUMMARY.json, c_stateless*/VERDICT.json, EXPERIMENT_GRAPH.jsonl. What distinguishes the 11 of 23
established donors that also self-poison (T9).

D8 (minutes): Acquired competence diff. Files: nestor branch roles/Nestor/campaigns/c9x-explore-2026-09-24/
(x_acquire, c_swap_acquire result JSONs -- CHECK exact dir names with git ls-tree), plus the Z8 VM to test
minimal byte diffs in isolation (T11).

D9 (~1-2 min per run, needs BEE harness commit 16fc6c2a from git): TH-005 pc >= 2L binning. Files:
archaeon/causal_lens/tools_bee/codeprov_replay.py, ops/campaigns/C-001/E-001/inputs/r016299.config.json,
ops/campaigns/C-001/E-001/TASKS.md (T-001 recipe), roles/Odysseus/th006/ (portable verification pack pattern).
Proven to run on a 4-thread 8 GB laptop in 51-108 s / 141-150 MB (C-001/CAMPAIGN.md). Local verification
against M2's preserved log is not possible; result hash can be compared with M2 later (T7).

D10 (minutes, if fields exist): Heredity without fidelity. Files: archaeon/envgate/FORENSIC_REPLAY.json,
archaeon/envgate/LINEAGES.json, archaeon/envgate/ESTABLISHED_LINEAGES_TABLE.txt. Per-position conservation
vs founder; gate-set widening (liberation) events (T17, T21).

Not laptop-cheap (need M2 evidence or operator): host-conditioned assay (T5, operator gate), ENVGATE-01
genetic audit (T18), block-11 divergence replay (T23, hours), BEE-wide SR recount (T8, traced runs on M2),
multi-day results (T15, pending).
