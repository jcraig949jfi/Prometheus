# BEL-48H Window 2 -- Heredity and genetic provenance

Campaign BEL-48H-2026-10-08, Bellerophon[ubu005-0eb14d49]. Prereg s4 (frozen 7133438e5), analysis tools/analyze_w2.py
(committed 681f39b6f before the results were read). Runs: 1,050/1,050, 0 voids, 2.10 h active on 6 workers
(2026-10-08T05:52:58Z -> 07:59:15Z), pinned code 7133438e5 (kernel = repaired dc1833bc2). Raw: ~/bel48h_runs/w2
(results.jsonl, events/*.jsonl.gz); analysis output ~/bel48h_runs/analysis/w2.json. Physics v2, historical defaults;
every measurement below is a hook proven not to change the trajectory (tests/test_belinst.py, test_heredity.py).

## 1. Frozen predictions -- scorecard

| id | prediction | result | verdict |
|---|---|---|---|
| W2-P1 | first FUNC tape BORN (not in place) in >= 90% of origins | 3/27 = 11.1% [3.9, 28.1]; 24/27 became FUNC IN PLACE after birth | FALSIFIED |
| W2-P2 | multi-source first-FUNC origins more frequent under PARTIAL than COPY | PARTIAL 10/11, COPY 6/7; Fisher one-sided p = 0.64 | FALSIFIED (both near ceiling) |
| W2-P3 | in A+B worlds the critical LDIR comes mostly from random background, not from B | LD T,64 from A in 99/99; LDIR from B in 64/99 (random founders 32, novel 3) | FALSIFIED (B supplies it) |
| W2-P4 | the first assembled machine leaves living copy-descendants in >= 50% of runs | A 36/95 = 38%; AB 32/99 = 32% | FALSIFIED |
| W2-P5 | COPY physics blocks the 2-byte complementation | 97/100 COPY/AB runs with 0 causal-assembly events | HOLDS |
| W2-P6 | B-only and no-fragment worlds reach FUNC in <= 5/100 | B 6/100, none 8/100 | FALSIFIED (narrowly) |

Independent origins (CORRECTED by prereg amendment 2): 27 of 550 H1 runs produced a FUNC tape (COPY/Z80 7/150,
PARTIAL 11/150, PAIR 7/150, VM_COPY 2/100), but the four H1 cells share seeds (run k of every cell starts from the same
initial population): the 27 runs come from 21 DISTINCT initial populations. Per distinct seed, W2-P1 reads: 3/21 seeds
with any BORN origin (2/21 with only BORN origins) -- the falsification stands. W2-P2's Fisher test treated the PARTIAL
and COPY cells as independent; they share seed k = 31 (the same founder near-replicator, see W3a); its verdict (no
difference, both near ceiling) is unchanged. H2: 100 worlds per arm, arms paired by seed by design (PAIRED init).

## 2. What the corrected rulers show

**A. Spontaneous replicators are finished IN PLACE, not born whole.** In 24 of 27 independent origins the first
organism that passes FUNC was copy-made but non-functional at birth and became functional later by a change to its own
tape. Only 3 origins (2 PARTIAL, 1 PAIR) were born functional, all by ASSEMBLY (neither parent functional). The
grounding round's G6a ("160/160 first self-replicators BUILT_BY_COPY") is not contradicted -- it classified the WRITER's
birth -- but it is refined: copying built the carrier, a later in-place change built the machine. W2 tags could not say
which kind of change; W3a (eager tags: mutation vs self-construction vs uptake) answers that.

**B. The working machinery is newly made, not found.** Of the 10 runs with a functional tape alive at the end, the
dominant tape's critical bytes (2-8 per machine) carry founder material in only 2 runs (1 byte each); every other
critical byte is a post-founding change, and nearly every critical byte comes from a DIFFERENT change event (n_origins
== n_critical in 7/10). Random initial material supplies almost none of the machine. CONFIRMED as a measurement on these
10 machines; DETECTOR-level for the claim "built by several independent changes" until W3a separates the change kinds.

**C. Two non-replicating fragments complement each other into a heritable replicator (H2).** CAUSALLY_CONFIRMED.
- Fragment A (writes its own LD T,64 into a partner's window bytes 0-1) and fragment B (carries LDIR at byte 2) are each
  MORE than one mutation from FUNC (all 16,320 single-byte mutants of each are non-FUNC, both physics), and B-only / none worlds reach
  FUNC in 6/100 and 8/100. With A present, 100/100 worlds (A alone) and 100/100 (A+B) reach FUNC, by CAUSAL_ASSEMBLY
  events in 95/100 and 99/100 runs: the child is FUNC while neither the writer-only nor the target-only reconstruction
  is, and its critical set holds bytes from both. Dominant critical-vector signature WWT (writer, writer, target): 382
  events (AB), 303 (A).
- Byte-level attribution of the FIRST causal assembly per run: LD T,64 from an A founder in 99/99 (AB) and 94/95 (A);
  the LDIR from a B founder in 64/99 AB runs; in A-only worlds from random initial material in 86/95 and from a novel
  change in 8/95. B therefore supplies the decisive byte when present -- the prediction (random background dominates)
  was wrong; the pilot of 3 runs had misled it.
- Physics control: under ENDOGENOUS_COPY (a 2-byte write is no birth) causal assembly is abolished (97/100 runs with
  none). COPY/AB still reaches FUNC in 61/100 by other routes (37 in place, 23 born by non-causal 'assembly') -- an
  unexplained excess over none (8/100); both fragments are > 1 mutation from FUNC, so this is not single-mutation
  proximity. Under replay in W3b (exploratory).

**D. Function persists without lineage continuity.** (POST-HOC, labelled.) The first assembled machine leaves living
copy-chain descendants in only 32-38% of runs (W2-P4 falsified), yet 99-100/100 A and AB worlds end with ~200 functional
organisms. Assembly is recurrent (median 4 causal assemblies per run, max 22), and in 34/100 runs of each arm no
assembly event has an unbroken TRB lineage at the end: functional machinery is re-made and re-captured (CAPTURE births:
a functional target partly overwritten yields a functional child carrying the target's machine) rather than handed down
a single line. Inheritance here is distributed across organisms and events; a parent->child tree is the wrong ontology
for it. PROVISIONAL (post-hoc; confirm in W6 with a frozen endpoint).

## 3. Ruler limits that apply to these numbers (BEL_48H_REVIEW_RECORD.md)

FUNC is a single-execution own-copy test: it rejects prefix and shifted replicators that work under PARTIAL physics
and passes sterile near-copies; TRB counts only FUNC->FUNC chains. The W2 'n' tag conflates mutation and
self-modification. Founder tags are exact; one tag per byte (the last material move). PAIR_EXECUTION births need no
minimum write.

## 4. Mechanism record (directive s8): two-fragment complementation

1. Mechanism: a non-replicating writer that lays down part of a copy routine (LD T,64) into a partner whose own bytes
   supply the rest (LDIR) produces a child whose combined bytes form a self-copier; the child then propagates by copying.
2. Conditions: physics in which unwritten target bytes survive into the child (ENDOGENOUS_PARTIAL); a partner carrying a
   reachable LDIR at the right offset (B fragment or ~1 in N random tapes).
3. Causal dependencies: both byte sets necessary (single-source reconstructions non-FUNC; every critical byte necessary
   by NOP knockout).
4. Failure boundary: ENDOGENOUS_COPY (complete-overwrite births) abolishes it (97/100).
5. Smallest specimen: writer = 07 14 08 40 03 02 15 ff (+ 08 40 at bytes 20-21); partner = 01 01 15; child = 08 40 15 ...
6. Independent origins: 194 independent worlds (A 95, AB 99) with >= 1 causal assembly.
7. Ablation: remove A -> 6/100 (B) / 8/100 (none) worlds reach FUNC at all.
8. Transplant: not measured in W2 (queued for W5: implant the assembled core into foreign backgrounds and offsets).
9. Generalisation limits: single fragment pair, one task-free world type, 300 ticks, GRID WELL_MIXED.
10. Other engines: 'complementation of partial programs across individuals' is a direct test any engine with partial
    writes / crossover-like construction can run (NPE, SFE): measure single-source reconstructions vs the composite.

## 5. CONFIRMATION of distributed persistence (W6 block 1 lane C2, prereg s9)

100 fresh A-fragment worlds (distinct seeds): FUNC alive at the end in 98/100; the FIRST assembly event's TRB lineage
alive in 36/100; function alive with NO assembly event's TRB lineage alive in 42/100. C2-P1 HOLDS. W2 s2.D (function
persists without lineage continuity: re-made and re-captured, not handed down one line) PROVISIONAL -> REPRODUCED.
