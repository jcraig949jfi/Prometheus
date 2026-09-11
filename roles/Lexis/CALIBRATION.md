# Lexis calibration ledger

Kept because it is unflattering (base role s2). One row per wrong call, with
the direction the error pushed and how it was caught. Seeded 2026-09-11 from
the seat's own written corrections: library_learning/RETROSPECTIVE.md s9 (eight
retractions across eight passes), SESSION_2026-08-25.md s6, and the HC-T01
pass's L_CORRECTIONS.jsonl (CO-04, CO-08). Nothing here is from recall.

Format: date | call | direction of the error | how caught | source

2026-08-24 | "compression of yesterday vs reachability of tomorrow is the delta" between the two programs | invented a novelty | both were 2026 work on reading the primary sources | RETROSPECTIVE s9 item 1
2026-08-24 | "gene_extractor.py already contains the O4 macro mechanism" | credited existing code with a capability | read the file: it inverts the logic | RETROSPECTIVE s9 item 2
2026-08-24 | "llm2's zero-lift may be a flat-landscape artifact" | softened a null | sharper reading from the code: llm2 could only reorder, so the null was structural | RETROSPECTIVE s9 item 3
2026-08-24 | "AutoDoc is the cheapest steal" | recommended a tool for a consumer that does not exist | Apollo has no LLM consumer; it lands on the forge | RETROSPECTIVE s9 item 4
2026-08-24 | "the transfer experiment has positive prior art" | overstated prior art | within-domain does, cross-domain does not, across ~20 systems checked to falsify | RETROSPECTIVE s9 item 5
2026-08-24 | "the C-vs-R experiment is the thing to run" | proposed an experiment with no headroom | H is bounded at zero on Apollo's blackboard, proven by closure 08-25 | RETROSPECTIVE s9 item 6
2026-08-24 | "There is no ratchet" | claimed a gap from recall | true of Apollo, false of the forge, whose T1-T3 ratchet exists and had shipped | RETROSPECTIVE s9 item 7; G0 fired
2026-08-24 | "verifier-gated admission from a typed diagnosis is unoccupied in that lineage" | claimed novelty | Hipster and Lemmanaid occupy it | RETROSPECTIVE s9 item 8
2026-08-25 | "op_build_ordering solves 3/5 temporal-ordering tasks once relations are injected" | inflated a capability | the probe omitted parse_question_target, so all three solves were the candidates[0] fallback, the exact defect written up one section earlier; the permutation null caught it | SESSION_2026-08-25 s6 item 1
2026-08-25 | A verdict line compared 100/120 against the truncated literal 0.8333 and printed KILL FIRES on an exact-match result | a false kill | noticed on reading the rows; fixed to 100.0/120.0 in three instruments and re-run | SESSION_2026-08-25 s6 item 2
2026-08-25 | CONTROLS.md s2 called a tree "live" that was timestamped seven hours before the rebuild replaced it | wrong-population statistic, inside the section written to warn against it | checked the population's date, not its path, during G0 | ROLE.md s7 (added 08-25)
2026-08-25 | "The substrate's ceiling is 0.8333" | one noun too wide | the unrestricted 27-operator pool reaches 107/120 with an 11-transformer program; the correct noun is Apollo's admissibility rules | ROLE.md s4a, retracted
2026-09-03 | "Petak et al. 2025 has no mechanism arm; selection-side only" | understated prior art | its Supplementary Figure 5 has a variation-regime arm; corrected mid-pass; the earlier Ergon-pass reading propagated into Herakles's HC_T01_CORRECTION and is still owed an annotation there (LEX-12) | L_CORRECTIONS CO-04, CO-08
2026-09-03 | Section-16 decision rule for RUN_A_SMALLER_CALIBRATION_FIRST had two branches for a three-outcome test | a rule that could not do its job; its second branch would have abandoned the line on a test that never ran | the test ran (d51d1fa82) and returned the state the rule did not provide for | ADDENDUM_2026-09-04, CROSS_SEAT_COMPARISON_2026-09-04
2026-09-03 | K7 "close to unwinnable" | hedge too weak | measured Spearman exactly -1.0000 at the K7 window, 1 - r^2 = 0.00000: the test was degenerate, not merely hard | ADDENDUM_2026-09-04 s2
2026-09-11 | Hashed the whole closeout prompt file and read a mismatch against the stated body hash | would have reported a false provenance failure | re-read the file's own header: the hash is over bytes after the marker line; matched exactly | journal/2026-09-11.md

Pattern across the rows: nine of sixteen errors pushed toward a BIGGER claim
(a novelty, a capability, a kill, a wider noun); four pushed toward a weaker
one (a softened null, understated prior art, a hedge). The flattering
direction for this seat is novelty and reach. Every retraction so far has been
an interpretation; no measurement in the ledger has been overturned.
