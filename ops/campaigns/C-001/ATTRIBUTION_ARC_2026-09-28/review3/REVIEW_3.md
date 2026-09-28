# REVIEW 3 -- adversarial review of ANCESTRY_PREREG.md v1 (byte-level ancestry replays, BEE + NPE)

Target: ops/campaigns/C-001/ATTRIBUTION_ARC_2026-09-28/ANCESTRY_PREREG.md at 99339fbb3 (cited below as "PREREG sN").
Reviewer: an isolated worker with no prior context and no stake. Read-only on the repo. Everything I executed is in this folder:
- review3_cx.py: a reference shadow tracer that implements PREREG s1 literally, run on BEE's FROZEN VM
  (git 16fc6c2a:prometheus/z80atlas/vm.py, the harness r016299 was replayed with; E-001/TASKS.md:14). Every case is
  value-checked (memory bit-identical to the frozen vm.execute); only the labels come from the rule set.
  Reproduce: `git show 16fc6c2a:prometheus/z80atlas/vm.py > /tmp/rev3_vm16.py; python3 review3_cx.py`.
- review3_npe_align.txt: NPE's own `_mutated_orig` run on a 6-byte deletion.

NPE code IS in this repo: roles/Nestor/campaigns/z80atlas-verify-2026-09-22/{z8taint.py, z8.py, world.py}. I cite it as
"NPE/<file>:<line>".

Overall verdict: UNSOUND as frozen. The rule set is an explicit-data-flow taint policy. Its "identifiable" gate measures whether
the tracer is complete WITH RESPECT TO ITS OWN RULES, not whether the answer is right. In a closed 256-byte VM that gate is met by
construction, so P1 cannot lose. Meanwhile the flows the rules do not model (control dependence, address dependence) are
misattributed silently, not reported as "unknown". The fixtures are all explicit-flow cases, so a tracer with the known classic
bugs passes them. And the decision rule cannot return VALIDATED, whatever the data say.

-------------------------------------------------------------------------------------------------------------------------------
## Executed counter-examples (BEE frozen VM, PAIR_EXECUTION layout, L = 64, run with review3_cx.py)

| id | construction (writer code, partner tape random) | ground truth | PREREG s1 label | consequence |
|---|---|---|---|---|
| CX-A | control-flow copy: `LD A,(S); LD B,A; LD A,0; loop: INC A; DJNZ loop; LD (T),A` over 16 loci | child[0:16] == partner[0:16] exactly (IBS 1.0); every byte's value is fully determined by the partner | 16/16 `(COMPUTED, {(writer, 9)})`, 0 unknown links, identified share 1.0 | partner donor share 0%; Q3 "new material >= 10%" fires; Q2 counts a resemblance/IBD disagreement that is really an implicit copy |
| CX-B | translation table: `child[p] := writer[partner[p]]` (pointer = partner byte) | the child is a function of the partner's bytes (change 1 partner byte -> that child byte changes; verified) | 16/16 `(writer, x)`, 14 distinct source loci | reads as a high-diversity COPY OF THE WRITER (Q7 "copying"). This is von Neumann's constructor + description, the case the packet leaves OPEN (F13). The instrument is blind to exactly that open question. |
| CX-C | writer stores its own locus 63 into input byte 0xE0, then `IN A`, then stores A to the window | child[0] = writer locus 63 | `(INPUT)`: the rule labels by INSTRUCTION, but BEE's IN reads memory (vm.py:207) that organisms may write (vm.py:128-132) | laundering: writer material becomes INPUT |
| CX-D | `OUT A` then read back from 0xF0 | child[1] = partner locus 0 | a tracer hooked on the VM's write function W() (the traced_replay.py:79-94 pattern) gives `(OTHER, 0xF0)`: OUT stores to memory WITHOUT W() (frozen vm16:185; HEAD vm.py:213) and 0xF0 is absent from Trace.writes (verified) | a stale label from a store the instrumented hook never sees |
| CX-E | one `COPYALL` with S=60, T=64 in pair execution (the VM's L is 2*64, so 128 bytes move, overlapping) | the window becomes a period-4 smear of writer loci 60..63 (a painter; 4 distinct sources) | correct sequential tracer: 64/64 writer, 4 sources. A plausible WRONG tracer (block/memmove label copy): 4 writer + 60 PARTNER, 64 sources | the wrong tracer calls a writer painter a partner-majority high-diversity copy, and passes K1-K9 |
| CX-F | `LD T,64; LD (T),A` with A never loaded (BEE zeroes all registers per execute, vm.py:96) | child[0] = 0 from reset state | undefined: s1 says registers "carry a label" but gives start labels only for memory | the implementer improvises (UNKNOWN, CONSTANT, or "writer") and the result moves |
| CX-G | K8 as written: the writer writes a literal equal to the occupant byte | -- | `(writer, operand locus 1)` by s1's operand rule | K8's expected `(CONSTANT)` contradicts s1. In BEE, K8 cannot pass unless the operand rule is broken. |

NPE (executed): NPE's native post-mutation retagging `_mutated_orig` (NPE/world.py:1351-1382) aligns pre/post genomes by VALUE
(difflib). Deleting locus 1 of `3e 00 00 00 00 76` with tags 10..15 returns tags [10,11,12,13,15]; the truth is [10,12,13,14,15].
The deleted byte's tag survives, and the docstring's "can only miss a surviving byte, never invent one" (world.py:1355-1356) is
false for repeats. This is a value-match source, which PREREG s1 forbids. It does not bite T-003's cell (mutation_locality LOCAL,
MANIFEST_FROZEN.json), but it bites any owner who reuses the helper for (entity, locus) labels.

-------------------------------------------------------------------------------------------------------------------------------
## s0 Division of labour -- SOUND WITH CORRECTION

Problem: each owner writes the tracer, runs the fixtures and reports the pass. That is the self-certification pattern
REVIEW_1_ADJUDICATION.md ("My tests encoded my assumptions") names as the failure that let v1 through. The fixtures' expected
answers encode the same rule set the tracer implements, so they cannot catch a wrong rule, only a wrong implementation of it.

Amendment A0: Archaeon (or a context-free reviewer) runs an INDEPENDENT differential check on a random 1% of production births
before the synthesis (see A4.1). It can, because BEE's VM is in the repo at 16fc6c2a and a birth is a pure function of
(memory, entry, budget, inputs) (vm.py:18). NPE's world is also in the repo.

-------------------------------------------------------------------------------------------------------------------------------
## s1 What "ancestry" means -- UNSOUND

1. **Standard terms, and what s1 actually specifies.** s1 is a dynamic taint-tracking policy with explicit-flow (data-dependence)
   propagation only. Its ENTITY labels are "where-provenance" in the sense of Buneman, Khanna and Tan (2001): which source
   location a value was copied from. COMPUTED is a coarse "how-provenance". Calling the result "IBD" is a redefinition. In
   population genetics, IBD is relative to a genealogy and a base population, and it is indifferent to mechanism. Here "IBD" means
   "reached the child only through the tracer's move instructions". CX-A shows the gap: a perfect copy made through a loop counter
   is "not IBD" and "new material".
   The document never says that implicit flows are out of scope. Both classic under-tainting channels are silently resolved:
   - control dependence (branches, loop counters, flags: CX-A);
   - address dependence (pointer / table index: CX-B).
   An "unknown link" (s2) covers only "a read from an untracked region or register, a dropped label, or an operation the tracer
   does not model". Neither implicit channel ever produces one.
   **Amendment A1.1:** state the policy by name: explicit-flow where-provenance; no control or address taint in the label. Then
   add two per-locus dependence sets to the label:
   - `ctrl_deps`: labels of every flag or counter that decided a branch dynamically in scope of the write (standard
     post-dominator scoping, or conservatively every branch since the last write to that locus);
   - `addr_deps`: labels of the pointer register used for the load and the store.
   A locus is "IDENTIFIED" only if its data label is resolved AND its ctrl_deps/addr_deps name no entity other than the data
   label's entity. Otherwise it is "IDENTIFIED_EXPLICIT_ONLY", and it counts AGAINST the identified share.
2. **The operand rule contradicts K8.** Every BEE constant comes from an operand byte (LD r,n; vm.py:143-148), so s1 labels it
   (writer, operand locus). K8 expects CONSTANT (CX-G). BEE has almost no operand-free constants: registers reset to 0 (vm.py:96),
   IN past 16 inputs returns 0 (vm.py:207), and scratch memory is zero-filled (world.py _execute / _pair_execute, `bytearray(256)`).
   **Amendment A1.2:** K8's expected answer for BEE = (writer, operand locus). Also define labels for register-reset values
   (RESET) and zero-filled scratch (OTHER, region). Scratch also gets EXECUTED: 528,897 writes by code at pc >= 2L in r016299
   (archaeon/causal_lens/out_v02/B6_PROBE_r016299.json, "elsewhere").
3. **No start label for registers (CX-F); NPE registers persist across interactions.** NPE carries `org.regs` and
   `org.reg_taint` from one interaction to the next (NPE/world.py:805-811; z8taint.py:35-36). A value read from partner X in one
   interaction can be written into partner Y in the next, which is a cross-birth flow through registers.
   **Amendment A1.3:** start labels for every register and flag:
   - BEE: RESET;
   - NPE: the label persisted from that organism's previous execution, in multi-generation ids.
   A fixture must cover it (K15 below).
4. **INPUT is labelled by instruction, not by the memory byte (CX-C).** **Amendment A1.4:** "the label of the byte read. The input
   region starts labelled (INPUT, k)."
5. **Stores that bypass the VM's write function (CX-D).** OUT_A writes memory directly: frozen vm16:185; HEAD vm.py:213.
   **Amendment A1.5:** "every store to shadow memory, including OUT, LDIR/COPYALL and the harness's input and window
   initialisation, updates labels". This needs a fixture (K14).
6. **COMPUTED is under-specified:**
   - no flattening rule, so nested COMPUTED labels grow without bound in any counter loop;
   - no rule for idioms whose result does not depend on the operand (XOR A,A / SUB A,A: over-taint);
   - no rule for bijective single-input operations (INC, ADD n, XOR n). These are the OPERAND mutations in NPE: +/-8 deltas and bit
     flips, NPE/world.py:505-513.
   **Amendment A1.6:**
   - contributors are flattened to base labels;
   - a single-contributor bijective op is `(COMPUTED_FROM, label)`, reported separately from multi-contributor COMPUTED;
   - Q3's "new material" is computed both with and without COMPUTED_FROM.
7. **MUTATION assumes post-execution copy noise. Neither engine works that way:**
   - BEE has no copy noise. Background mutation hits every live tape every tick, including the newborn in its birth tick and the
     writer (world.py step 4; 16fc6c2a:375). STRUCTURAL insert/delete/dup (world.py:305-316) MOVES bytes. `dup` is an
     intra-genome copy (IBD, not MUTATION) and `delete` shifts every downstream locus. "MUTATION regardless of value" applied per
     locus erases the shifted material.
   - NPE applies copy noise INSIDE LDIR during execution (z8taint.py:281-284). Later instructions can re-copy the mutated byte.
   - NPE's mutation step can splice in a random living organism (RECOMBINATION axis, NPE/world.py:501, `_recombine` at :552). That is
     third-party material, not mutation.
   **Amendment A1.7:**
   - MUTATION is assigned at the RNG draw, not by diff;
   - structural moves carry labels positionally (shift/dup = move, inserted byte = MUTATION);
   - in-VM copy noise is labelled at the write and propagates;
   - recombination splices are ENTITY labels of the splice donor.
8. **Multi-generation ids need labels for every tape, not only children.** BEE persists the writer's post-execution tape after
   EVERY interaction (world.py: `o.tape = new_a` / `mem[:L]`), birth or not. Partner code can rewrite the writer's half, and there
   is no birth record for that. NPE rewrites both halves (NPE/world.py:813-830).
   **Amendment A1.8:** the owner maintains a per-organism label vector updated after every execution, every null_rewrite and
   refused write, every mutation, and every migration. s3 exports the writer's post-execution labels too (see A3).

-------------------------------------------------------------------------------------------------------------------------------
## s2 Questions and identifiability -- UNSOUND

1. **The identifiability gate is met by construction.** BEE is a closed 256-byte space with six registers and two flags
   (vm.py:11-16, 96-97). A tracer that shadows all of it never has an "untracked region". So identified share is about 1.0 for
   every birth, whatever the implicit flows are. The gate tests coverage, not correctness. This makes P1 nearly unlosable and lets
   every Q be declared identifiable.
   **Amendment A2.1:** identifiability = (explicit coverage >= 0.9) AND (implicit-flow-free share >= 0.9 per A1.1) AND (the birth
   passes the counterfactual agreement check A4.1).
2. **"Performer" is undefined.**
   - Q1 says "executing code's owner, from the native trace". BEE's native trace is PC LOCATION (traced_replay.py:71-73), which is
     WHERE. E-001 already showed WHERE != WHAT in 27,083 of 28,163 location-foreign r038751 births (E-001/RESULT.md:10).
   - K3 expects "performer = partner" without saying by location or by material. A writer that copies itself into the window and
     executes the copy is "partner" by location and "writer" by material.
   - The Q1 BREAK condition, "code of both parties interleaved at byte granularity", describes BEE PAIR_EXECUTION literally: one 2L
     program (world.py `_pair_execute`), with the PC free to cross the half boundary at any byte. So BROKEN can be declared at will.
   **Amendment A2.2:** performer = the MATERIAL label of each executed opcode byte (Q6's field), aggregated per write. Location is
   reported separately as `exec_where`. Replace the Q1 break condition with a measurable one, for example: "for >= X% of births, no
   entity executes >= 50% of the opcode bytes that led to window writes".
3. **The engine's birth rule drives "majority donor", which is undefined.** In BEE PAIR_EXECUTION a birth is ANY change to the
   partner half (16fc6c2a world.py:333-337). 8,452 r016299 births change <= 2 bytes (TRACED_spontaneous.json). Those children are
   occupant-majority by retention, so Q1 "producer != donor" and Q3 fire because of the BIRTH RULE, not the attribution.
   "Majority donor" also has no tie rule, and it is not said whether retained occupant bytes make the occupant a "donor".
   **Amendment A2.3:**
   - define majority donor (plurality of child loci, ties -> TIED);
   - report every Q twice, over ALL loci and over WRITTEN loci only;
   - stratify by the number of written loci (<= 2, 3..L/2-1, >= L/2).
4. **Q2's break condition is not a break.** "IBD and native label agree on > 99%" is a null result for that engine. It does not
   show that the per-event record is the wrong unit, yet it triggers BROKEN, which "means" plural substrate-specific records.
   **Amendment A2.4:** move it to "uninformative for Q2", no verdict effect.
5. **Q3's break condition cannot be met.** It requires loss < 1% "in both engines AND in Archaeon", and Archaeon is already 4.9%
   (ASSAY.md). **Amendment A2.5:** delete it, or restate it per engine.
6. **Q4 is uninformative in the chosen run.** r016299 has 18 self-replication births in total and 0 SR-born organisms alive at the
   end (TRACED_spontaneous.json; ASSAY.md: 0.04%). "Later writes an is_sr birth" is about 0 for every child, so Q4 returns about
   100% "material without capability" and is still counted identifiable. This is survival (lifespan 40, overwriting every tick),
   not capability.
   **Amendment A2.6:** Q4 needs an ISOLATED capability test per child: BEE VM, child tape vs K random partners and K=40 random
   inputs, as TH-015 did. The in-situ flag is kept only as a secondary field.
7. **Q5 needs a mutation null.** Under BYTE/MED mutation (0.008 per byte per tick, r016299.config.json; world.py:98) an
   unreplaced founder byte survives 500 ticks with probability about exp(-4) = 0.018. "Founder share < 10%" is expected from the
   mutation clock alone.
   **Amendment A2.7:** Q5 compares against a mutation-only expectation at the child's material age, and reports the excess.
8. **Q6 counts non-code as co-execution.** Executed bytes in zeroed scratch (NOP slides) and executed INPUT bytes are "non-donor"
   material under Q6. **Amendment A2.8:** only ENTITY-labelled opcode bytes count toward "belongs to a non-donor". OTHER, INPUT
   and RESET are separate categories.
9. **Q7 is undefined for COMPUTED loci** (a counting painter). **Amendment A2.9:** Q7 is over ENTITY loci. Report the COMPUTED
   share alongside it.
10. **Decision rules: VALIDATED is unreachable and ALTERED is guaranteed.**
    - VALIDATED needs every Q identifiable in >= 80% of births. Q5 needs multi-generation ids, and Q4 is stuck as in point 6.
    - "The v0 schema holds the results without new fields" is false by construction. v0's SOURCE_KINDS
      (archaeon/attribution/schema.py:48) has no EMPTY, no OTHER, no contributor set, no original_material_id and no per-executed-
      byte material, yet s3 mandates all five.
    - So the synthesis can only say ALTERED or BROKEN, whatever the data. This is a prediction that cannot lose, hidden in the
      decision rule.
    - Also missing: the prereg never says how the two engines' verdicts combine, or who adjudicates "an alter condition is met".
      Archaeon owns both the questions and the synthesis.
    **Amendment A2.10:**
    - drop "without new fields" (the new fields are agreed in advance);
    - make VALIDATED "every Q that the engine's design makes identifiable is identifiable in >= 80% of births", with the list of
      such Qs fixed NOW per engine;
    - give a combination rule (per-engine verdicts, no pooling);
    - name the adjudicator of each alter condition as the reviewer, not Archaeon.

-------------------------------------------------------------------------------------------------------------------------------
## s3 Fields -- SOUND WITH CORRECTION

Missing fields:
- `ctrl_deps` and `addr_deps` per locus (A1.1);
- the writer's pre AND post labels (A1.8);
- the full per-write log for the window, not only the last writer. The last-writer map is what v1 misread (traced_replay.py:87-88);
- register start labels;
- the mutation-event list with the RNG draw index;
- the counterfactual check result (A4.1);
- `n_written` (A2.3).

Harness pinning is also missing. The BEE simulator at HEAD (prometheus/z80atlas/) is NOT the frozen one:
- `git diff 16fc6c2a HEAD` shows 292 changed lines in vm.py and world.py;
- traced_replay.py's `execute` (lines 54ff) has no `prov_L`, `strict_budget`, `ldir` or `undefined` parameters, while HEAD
  world.py passes them (world.py `_pair_execute`: `prov_L=L, **cfg.chem`). traced_replay cannot drive the HEAD world;
- traced_replay.py:37 hard-codes a Windows HARNESS path.

**Amendment A3:** name the frozen module hashes (E-001/TASKS.md:52-53: world 5b985241, vm 2536b1ac, grammar 3767d73d) as a
precondition. Require that the ancestry replay reproduces the preserved 83,384-row r016299 birth log bit-for-bit, as T-002 did,
before any label is read.

-------------------------------------------------------------------------------------------------------------------------------
## s4 Calibration fixtures -- UNSOUND

K1-K9 are all explicit-flow, non-overlapping cases. The CX-E snapshot tracer, a tracer that treats IN as INPUT (CX-C), a
W()-hooked tracer (CX-D), and a tracer with any register start label (CX-F) all pass K1-K9 in BEE. K8 cannot pass under s1 (CX-G).
K9 is "inapplicable" in BEE (no copy noise), yet BEE background mutation is exactly what Q5 needs. Hand-built fixtures with fixed
offsets can also be passed by a tracer tuned to them.

Amendment A4 -- add these fixtures, with the answers fixed now:

| K | construction | expected |
|---|---|---|
| K10 | overlapping LDIR (T = S+1) and overlapping COPYALL in pair execution (CX-E) | sequential smear labels; source diversity = overlap period |
| K11 | control-flow copy (CX-A) | data label COMPUTED{writer}; ctrl_deps contains (partner, p); locus NOT identified |
| K12 | translation table (CX-B) | data label (writer, x); addr_deps contains (partner, p); locus NOT identified |
| K13 | input laundering (CX-C) | (writer, 63) |
| K14 | OUT store read back (CX-D) | (partner, 0) |
| K15 | uninitialised register (BEE) / persisted register carrying a previous partner's byte (NPE) | RESET / (previous partner, locus) |
| K16 | writer copies its code into the window and executes it | performer material = writer, exec_where = window |
| K17 | address wrap (LDIR across 0xFF -> 0x00) and budget exhaustion mid-LDIR | labels on exactly the bytes written |
| K18 | same-tick sequence: child born, executes, is overwritten, and is mutated in one tick | per-event labels in tick order |
| K19 | STRUCTURAL delete/dup (BEE world.py:305-316) | shifted labels preserved; dup = ENTITY |
| K20 | NPE in-LDIR copy noise, then re-copy of the noisy byte | MUTATION propagates |
| K21 | NPE interaction in which both halves are rewritten (sequential contexts) | per-context performer |

**Amendment A4.1 (the one that matters): a property-based counterfactual check replaces "known answers" as the pass criterion.**
On >= 10,000 random soups plus a random 1% of production births, re-execute each birth with one entity's bytes randomised (the
P-11 method, already in NPE):
- soundness: every locus labelled (E, X, j) must change when X's byte j is randomised, modulo value collisions;
- completeness: every locus that changes when X is randomised must name X in its data label, ctrl_deps or addr_deps.
Pre-register the pass thresholds: soundness >= 99%, completeness >= 95%.

-------------------------------------------------------------------------------------------------------------------------------
## s5 Samples -- UNSOUND

1. **The run choice is a forking path.** "Alternative the owner may choose instead, with a stated reason: r038751" lets the result
   select the sample. **Amendment A5.1:** fix one run now, or run both and report both.
2. **r016299 is atypical and uninformative for Q4/Q5:** 18 SR births, 0 SR-born alive at the end. It was chosen for being rich in
   decoupling, which E-001/RESULT.md:41 itself flags as "not a random sample". **Amendment A5.2:** if r016299 stays, Q4/Q5 are
   declared NOT INFORMATIVE for BEE in advance, or r038751 (42,915 SR births) is added.
3. **The NPE 34 births are selected by resemblance.** They are events accepted by `p11.predecessor_accepts(fid_other, fid_self,
   ...)` (NPE/world.py:839), which is a fidelity comparison. Q2 on NPE can therefore find resemblance FALSE POSITIVES, never
   FALSE NEGATIVES: descent events that resemblance did not flag. They are also 11 runs of one specimen, so the births are not
   independent.
   **Amendment A5.3:** trace ALL pair interactions in the 11 runs, and report Q2 on both the accepted and the non-accepted
   interactions, by run, with a run-level bootstrap.
4. **NPE's native taint cannot supply s1 labels:**
   - z8taint tags are 1-byte NICHE ids (z8taint.py:4, 24; `orig` is a bytearray);
   - COMPUTED, INPUT, SELF/GETPC and pointer arithmetic take `here`, the executing organism's niche (z8taint.py:10-12, 130, 143,
     248, 338-352). That is execution context, which s1 forbids;
   - the two organisms in a pair can share a niche (random `niche`, NPE/world.py:997).
   **Amendment A5.4:** state that NPE must build a NEW shadow with (entity, locus) labels. Reusing z8taint "natively" is a
   fixture failure.

-------------------------------------------------------------------------------------------------------------------------------
## s6 Predictions -- UNSOUND

- **P1** cannot lose with any complete explicit tracer (s2 point 1). **Amend:** restate it on the A2.1 identified share, and
  predict the implicit-flow share separately.
- **P2**'s 50% has no rationale. Its population (10,454 "partner code executed") is a LOCATION count, and the result is dominated
  by the retention and birth-rule effect (A2.3). **Amend:** P2 over WRITTEN loci, in births with n_written >= L/2, with the
  performer defined by material.
- **P3**: "field 8 >= L/2" is `copied_from_own` (traced_replay.py:223). It counts copy-op writes sourced in [0,L), including source
  bytes that were overwritten earlier in the same execution (CX-5a). Fine as a test, but 90% is arbitrary, and the prereg does not
  say what a loss means for the verdict.
- **P4**'s band [5%, 40%] brackets the already-known 22.5% (s5 text). It loses only in the extremes and is not tied to Q2's
  break/alter thresholds.
- **P5-P7** rest on 34 correlated births with no interval. P7 is a conjunction across engines built on the "new material"
  definition that CX-A shows is contaminated. "Victim" in P6 is NPE vocabulary, not defined in s1.
- **No prediction covers Q4, Q5 or Q7**, so their answers will be read post hoc.
- **No prediction outcome feeds VALIDATED/ALTERED/BROKEN.** Predictions can lose without consequence.

**Amendment A6:** every prediction names its Q, uses the A2.3 stratum, states a run-level interval, and states what its loss does
to the verdict (for example "P3 loses -> the address reading is not a usable proxy: ALTERED for BEE"). Add predictions for Q4 (on
the isolated test) and Q5 (as excess over the mutation null).

-------------------------------------------------------------------------------------------------------------------------------
## s7 What this cannot establish -- SOUND WITH CORRECTION

Missing limits:
- the replay establishes explicit-flow where-provenance only;
- it is blind to information transmitted by control or address dependence, i.e. to the constructor + description route (F13)
  that is the program's open boundary question;
- "descent" results are conditional on the tracer's move set.

**Amendment A7:** add these limits verbatim.

-------------------------------------------------------------------------------------------------------------------------------
## Terminology map (where the document reinvents or misuses standard terms)

| PREREG term | standard term | comment |
|---|---|---|
| material provenance / "material label" | dynamic taint tracking; where-provenance (Buneman-Khanna-Tan) | explicit-flow policy only; say so |
| "unknown link" | under-tainting / incomplete shadow coverage | the implicit-flow form of under-tainting is not included |
| (not named) | implicit flow: control dependence (Denning 1976), address or pointer taint | the omission is the central defect |
| IBD | identity by descent relative to a genealogy | here it is "copy-descent under the tracer's move set"; mechanism-dependent unlike pop-gen IBD (CX-A) |
| IBS / "resemblance" | identity by state | used correctly |
| retention | carry-over / unmodified inherited state | fine, but it interacts with the engine's birth rule |
| producer vs donor; Q6 "executed code material" | trans-acting replicase vs cis template; von Neumann constructor vs description | CX-B is exactly the constructor + description case |
| singular-parent loss | information lost by forcing a pedigree onto a reticulate genealogy (ancestral recombination graph) | |
| founder-material share | genome contribution of founders / kinship to founders | needs a neutral mutation expectation (A2.7) |
| COMPUTED | how-provenance; over-tainting for XOR A,A-type idioms | needs flattening and bijective-op rules (A1.6) |

-------------------------------------------------------------------------------------------------------------------------------
## The single most important amendment

The rules track only explicit data flow, yet they declare a locus "identified" whenever that flow is fully shadowed. So the replay
will report near-100% identifiability while misattributing every control- or address-dependent copy, which is the
constructor + description case the program most needs to see (CX-A, CX-B, executed on BEE's frozen VM). Replace "no unknown link"
as the identifiability and fixture pass criterion with a pre-registered counterfactual agreement check: re-execute each sampled
birth with one entity's bytes randomised, and require that the label, plus the new ctrl/addr dependence sets, name every entity
whose perturbation changes the child byte, and only those.
