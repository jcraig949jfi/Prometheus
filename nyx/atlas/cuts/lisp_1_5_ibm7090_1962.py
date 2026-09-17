"""Cut: lisp-1-5-ibm7090-1962 (ancestry-aware, Stage A COARSE; SOURCE_READ on M3; third of the 2026-09-17 NOT_CUT order).
The body is Bourguignon's machine-readable transcription (2014) of the 1961-62 IBM 7090 assembly listing: lisp15.asm 11,092
cards. Read: README, notes.txt (all); lisp15.asm RECLAIMER 1512-1830 (the storage control program: setup, TEMLIS/PDL/array
marking, free-storage sweep, full-word sweep by bit table, exit accounting, MRKLST, RCERR), CONS/ARREST/SPEAK 2091-2143,
SAVE/UNSAVE 1329-1400, EVALQ/EVALQT 5240-5330, APPLY 7180-7360 (dispatch, LAMBDA, LABEL, FUNARG, APP2 property-list search),
the EVAL variable lookup and FSUBR/EXPR branches 7700-7800. NOT read: the compiler (LAP, 8163-8900), the reader/printer,
arithmetic (6369-7180), arrays (6095-6350), RELOC (full-word compaction), error handling beyond RCERR. Nothing ran
(BUILDS_BUT_NOT_RUN; provenance grade is Techne's to issue: the body is a transcription of a listing, not the cards).
"""
from nyx.atlas.author import Cut

A = "vault:lisp-1-5-ibm7090-1962/upstream/tree/lisp15.asm"
c = Cut("lisp-1-5-ibm7090-1962", mode="ANCESTRY_AWARE",
        inspected=["lisp15.asm 1329-1400, 1512-1830, 2091-2143, 5240-5330, 7180-7360, 7700-7800", "README, notes.txt (all)"],
        evidence=[("SOURCE_READ", A + ":1512-1830"), ("SOURCE_READ", A + ":2091-2143"), ("SOURCE_READ", A + ":1329-1400"), ("SOURCE_READ", A + ":7180-7360"),
                  ("SOURCE_READ", A + ":7700-7800"), ("SOURCE_READ", A + ":5240-5330"), ("SOURCE_READ", "vault:lisp-1-5-ibm7090-1962/upstream/tree/README")],
        note="the famous names (eval/apply, garbage collection, the a-list) are here as 7090 machine code with the mechanisms exposed: marking by sign bit and by a separate bit table, "
             "a free list threaded during the sweep, a recursion stack that is itself a root, a cons budget that traps, and an interpreter whose environment is a list searched linearly")

fl = c.organ("free_storage_as_a_singly_linked_free_list_threaded_by_the_sweep", human_name="$FREE / CONS / sweep SFSL-SFSC (1640-1656, 2091-2104)", status="ACCEPTED",
    mechanism="a cons takes the word at $FREE and advances $FREE to that word's decrement (its cdr); the sweep walks free storage top to bottom, and every word whose sign is still plus (unmarked) is linked into a new free list by storing its address into the previously collected word; marked words get their sign restored",
    input="cons requests; the marked heap", output="a fresh cell, or the reconstructed free list", state="$FREE (one word); the list itself lives in the free cells", update="per cons; rebuilt per collection",
    assumptions=["a cell is one 36-bit word holding two 15-bit addresses (car in the address field, cdr in the decrement); the sign bit is free for marking"],
    fitness_value_in_ancestor="allocation is three instructions; no size classes because every cell is the same size", failure_landscape="by reading: $FREE = 0 -> FROUT -> RECLAM; if the collection recovers fewer than the critical number the run is aborted (*GC 2*)",
    human_prior="uniform cell size; the 7090 word layout dictates car/cdr as address/decrement", evidence_ref=A + ":1640-1656, 2091-2104", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="CONS, FREE, labels RCB-SFSC",
    coverage={"input_topology": "EVENT", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "NONE", "stochasticity": "DETERMINISTIC", "resource_dependence": "MEMORY", "failure_mode": "STARVES", "recovery": "EXTERNAL_RESET"})

mk = c.organ("recursive_mark_by_sign_bit_using_the_public_push_down_list_as_the_recursion_stack", human_name="MRKLST (1758-1797)", status="ACCEPTED",
    mechanism="MRKLST takes a pointer in IR2: reject if outside LISP storage; if in free storage, complement the word (CLS/STO: the sign bit becomes the mark; TPL exits if already marked), push the cdr on the push-down list, recurse on the car (a loop with an explicit stack), pop the cdr and continue; "
              "if in full-word space, set a bit in a separate bit table instead (full words have no spare sign); the stack depth is bounded by the free part of the PDL (MLPDC) and overflow is a fatal *NO PDL* error",
    input="a root pointer", output="every reachable free-storage word marked (sign minus) and every reachable full word marked in the bit table", state="the PDL between $CPPI and ENDPDL", update="per root",
    assumptions=["marking may run out of stack (the PDL) -- accepted as fatal; no pointer reversal", "a word already marked is a shared or circular structure and is not re-entered"],
    fitness_value_in_ancestor="reachability from roots without any per-cell header; the sign bit and a bit table are the entire mark storage", failure_landscape="by reading: deep lists (long car chains) exhaust the PDL; cdr chains cost stack too (one push per cons)",
    human_prior="the mark bit is the SIGN of the word, so 'marked' and 'negative' are the same test (TMI); an era-specific trick", evidence_ref=A + ":1758-1797", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="MRKLST",
    coverage={"input_topology": "GRAPH", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE", "failure_mode": "COLLAPSES", "resource_dependence": "MEMORY"})

bt = c.organ("side_bit_table_for_marking_full_word_space_and_sweeping_it_by_32_bit_words", human_name="MONE/MLTBT, SWPFWS-SFWC, MBTT (1660-1700, 1783-1789, 1602-1625)", status="ACCEPTED",
    mechanism="full-word space (numbers, print names, arrays) cannot carry a mark, so a bit table with one bit per word is zeroed at the start of a collection (A/B), set by MRKLST (bit = address mod 32 in word address/32), set 32 at a time for arrays (MBTT: CAL MONS / ORS), and swept: a table word of all ones skips 32 words at once (ONT MONES), otherwise each clear bit's word is threaded onto the full-word free list",
    input="marks", output="the full-word free list FWORDL and the count FWC", state="the bit table", update="per collection",
    assumptions=["full-word space is contiguous so address arithmetic gives the bit"], fitness_value_in_ancestor="a second heap with different marking cost (no sign bit) shares one collection", failure_landscape="UNKNOWN by run",
    evidence_ref=A + ":1602-1625, 1660-1700, 1783-1789", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the bit-table code paths",
    coverage={"input_topology": "SET", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP"})

roots = c.organ("root_set_declared_by_registration_lists_OBLIST_TEMLIS_ARYLIS_plus_the_live_stack", human_name="RECLAM 1512-1600 (OBLIST, TEMLIS, PDL, ARYLIS)", status="ACCEPTED",
    mechanism="the collector marks from: the object list (unless a debug/read-in flag says to skip it), TEMLIS -- a list of (begin,,end) full-word ranges that code (mainly the compiler) registers as 'places where list structure may be' -- , then the active part of the push-down list treated as such a range, then every declared array's list elements; a word in a range is marked only if it has no tag/prefix bits (OFT TMPTM), i.e. looks like a pointer",
    input="the registration lists and the PDL bounds", output="the marked heap", state="TEMLIS, ARYLIS, $CPPI/$CSSI", update="registrations by the mutator; read per collection",
    assumptions=["a full word with prefix/tag bits is not a pointer (conservative-by-tag scanning of the stack and registered ranges)", "code that holds pointers elsewhere (index registers) must have registered them or they are lost"],
    fitness_value_in_ancestor="the compiler and machine code can hold pointers in raw storage and still survive a collection", failure_landscape="by reading: an unregistered temporary is a use-after-collect; the design pushes root discipline onto every machine-code author",
    human_prior="TEMLIS is a manual root registry -- the ancestor of 'GC roots' declarations", evidence_ref=A + ":1512-1600", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="RECLAM through MRKE",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "hidden_state": "ASSUMES"})

crit = c.organ("collection_yield_test_against_a_critical_word_number_with_a_typed_bad_exit", human_name="CRITWN / RCBE / *GC 2* (1700-1735, 1809-1818)", status="ACCEPTED",
    mechanism="after the sweep the number of full words and of free cells recovered are each compared with a critical number (CRITWN, the free-storage bound is 16x the full-word one via LGL 4); if either is below, a bad-exit flag is set and the collection ends in error *GC 2* 'NOT ENOUGH WORDS COLLECTED' after printing the counts; totals and cycle counts are accumulated; VERBOS prints per collection",
    input="FWC, FSC", output="continue or abort; statistics", state="TFWC, TFSC, RCC, RLC counters", update="per collection",
    assumptions=["a collection that recovers little will be followed immediately by another; aborting early is cheaper than thrashing"], fitness_value_in_ancestor="the machine refuses to thrash: near-full memory is reported as a failure, not endured",
    failure_landscape="the record's own: 'the free list exhausts and the collector cannot recover enough cells'", human_prior="the critical number is a constant, not derived from the allocation rate",
    evidence_ref=A + ":1700-1735, 1809-1818", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="ZPDLA through RCEXIT and RCBEX",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "SUMMARY_STATISTIC", "stochasticity": "DETERMINISTIC", "failure_mode": "STALLS", "recovery": "EXTERNAL_RESET"})

cc = c.organ("cons_budget_counter_that_traps_when_exhausted", human_name="CNTR1 / ARREST / AWHOA / SPEAK (2104-2143); ERRORSET 5400", status="ACCEPTED",
    mechanism="CONS decrements a 15-bit counter kept as the address field of an instruction (self-modifying: AXT **,4 / SXA CNTR1); when it runs out ARREST reloads it from the high part CNTS or, if the whole count is exhausted and the counter is on (TCOUNT), calls error *F 1* 'CONS COUNTER TRAP' with 8 spare conses reserved to build the error number; SPEAK reads the count as a fixnum; ERRORSET evaluates an expression under a cons limit N and returns F on overrun",
    input="cons calls; a limit set by COUNT/ERRORSET", output="a trap after N conses", state="CNTR1 (low 15 bits, in the instruction), CNTS (rest), CNTST (initial)", update="per cons",
    assumptions=["allocation count is a usable proxy for work done (the era's resource limit)"], fitness_value_in_ancestor="a runaway evaluation is bounded by memory allocation, not wall time; ERRORSET makes the bound catchable",
    failure_landscape="UNKNOWN by run", human_prior="budget in conses rather than in time or in stack depth", evidence_ref=A + ":2104-2143, 5400-5450", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the counter code inside CONS and the ARREST/AWHOA/SPEAK routines",
    coverage={"input_topology": "EVENT", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "stochasticity": "DETERMINISTIC", "resource_dependence": "MEMORY", "failure_mode": "STALLS", "recovery": "ROLLS_BACK"})

pdl = c.organ("public_push_down_list_with_block_save_unsave_by_jump_into_a_move_table", human_name="SAVE / UNSAVE / END1..END16 (1329-1400)", status="ACCEPTED",
    mechanism="one stack ($CPPI counter) for every routine: SAVE is called with a parameter word naming how many contiguous cells to save (the first is 'PZE name,,IR4', the return address); it bumps the counter, checks for overflow (NOPDL), stores the parameter word, and jumps INTO a table of CLA/STO pairs at the entry for N so exactly N moves execute; UNSAVE reads the parameter word back off the stack to know how many to restore and where to return",
    input="a block of cells to preserve", output="the block restored on return", state="the PDL", update="per call/return of a recursive routine",
    assumptions=["routines keep their locals in fixed cells (no re-entrancy by design), so recursion is made possible by copying the cells to the stack"], fitness_value_in_ancestor="recursion on a machine with no stack instructions; the same stack is the GC's mark stack and a GC root",
    failure_landscape="by reading: fixed-size PDL; overflow is a fatal error (NOPDL, *NO PDL* in MRKLST)", human_prior="self-modifying, table-driven block copy: the 7090 idiom for a variable-length move", evidence_ref=A + ":1329-1400", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="SAVE, UNSAVE and the END table",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE", "failure_mode": "COLLAPSES"})

ap = c.organ("apply_dispatch_on_the_shape_of_the_function_object_with_environment_as_an_association_list", human_name="APPLY / APP2 (7203-7360) and EVAL's variable lookup EVP1-EVP12 (7735-7775)", status="ACCEPTED",
    mechanism="APPLY(F,L,A): if car(F) is an atom-marker (-1) go to APP2; LAMBDA -> EVAL(caddr F, nconc(PAIR(cadr F, L), A)) i.e. bind parameters by consing onto the a-list; LABEL -> APPLY(caddr F, L, cons((cadr F . caddr F), A)) i.e. bind the name to the body; FUNARG -> apply with the carried a-list; otherwise APPLY(EVAL(F,A), L, A). "
              "APP2 searches the atom's property list for TRACE, SUBR (call machine code via the stored TXL instruction after distributing args) or EXPR (apply the S-expression). EVAL's variable lookup: APVAL on the property list first, then a linear search of the a-list (EVL1: compare caar(J) with E), else error *A 8* UNBOUND VARIABLE",
    input="F, L, A", output="a value", state="$ARG3 (the current a-list) and $ALIST; the PDL for recursion", update="per application",
    assumptions=["dynamic scope: the a-list at call time is searched; FUNARG is the escape hatch that carries a captured a-list", "linear search cost is acceptable; property lists are searched before the a-list"],
    fitness_value_in_ancestor="the interpreter is the paper's metacircular definition transliterated (the REM comments are the M-expressions); machine-code SUBRs and interpreted EXPRs share one calling convention through the property list",
    failure_landscape="by reading: the FUNARG problem is present in exactly the form later named (dynamic a-list vs captured); deep recursion exhausts the PDL", human_prior="McCarthy's apply with the a-list environment; the SUBR/EXPR/FSUBR/FEXPR property-list typing",
    evidence_ref=A + ":7203-7360, 7735-7775", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="APPLY, APP2, EVP1-EVP12",
    coverage={"input_topology": "TREE", "output_topology": "TREE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "memory": "FULL_HISTORY", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE", "representation_sensitivity": "SENSITIVE"})

evq = c.organ("evalquote_driver_reading_doublets_with_a_per_doublet_error_return_and_time_stamps", human_name="EVALQ / EVQERR (5240-5330)", status="ACCEPTED",
    mechanism="read (function, argument-list) doublets from cards into a buffer until STOP; then for each: reset $ALIST, print a heading, apply, print the answer; an error anywhere unwinds (TERPDL resets the PDL, buffers are cleaned) and continues with the NEXT doublet; the time is printed at start, after read-in, and at the end",
    input="a card deck", output="printed answers and error messages", state="the doublet buffer, EVQRTS phase switch", update="per doublet",
    assumptions=["batch operation: no interaction; an error must not lose the rest of the deck"], fitness_value_in_ancestor="a job survives its own errors; the first REPL-like loop, batch form", failure_landscape="UNKNOWN by run",
    evidence_ref=A + ":5240-5330", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="EVALQ, EVALQT, EVQERR",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "stochasticity": "DETERMINISTIC", "recovery": "ROLLS_BACK"})

c.reject("RELOC (compaction of full-word space for arrays), the arithmetic package, the reader/printer, LAP and the compiler, the overlord/direction-card loader", reason="OTHER", evidence="NOT READ this pass (lisp15.asm 1830-2090, 2221-5240, 5586-7180, 8163-11092); residue, not a rejection on the merits", note="the compiler's LINK (8565: patches STR into TSX on first call) is the most promising unread mechanism")
c.reject("the assembler-transcription apparatus (pjb-asm7090.el, asm7090.patch, generated GENER/GPLI/GPLA cards, lisp15.lisp)", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY", evidence="README: 2014 tooling to reproduce the 1962 listing; not the machine", note="but it IS the provenance object: the body is LATER_TRANSCRIPTION-class by its own README")
c.reject("'LISP 1.5' / 'garbage collection' / 'eval' as single organs", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the collector alone is five separable mechanisms (free list, sign-bit mark, bit table, root registry, yield test)")
c.reject("self-modifying-code idioms (AXT **, SXA into instructions) as mechanisms", reason="GENERIC_LANGUAGE_MECHANICS", evidence="notes.txt; the 7090 way to pass a parameter; no behaviour of its own")

c.edge(fl, mk, "triggers", note="FROUT on exhaustion"); c.edge(roots, mk, "feeds"); c.edge(mk, pdl, "stores", note="the mark stack IS the PDL"); c.edge(pdl, roots, "feeds", note="and the PDL is a root"); c.edge(mk, bt, "updates"); c.edge(bt, fl, "feeds", note="full-word free list"); c.edge(mk, fl, "feeds", note="sweep rebuilds the list")
c.edge(crit, fl, "gates"); c.edge(cc, fl, "gates"); c.edge(ap, pdl, "stores"); c.edge(ap, fl, "feeds", note="PAIR/CONS of the a-list"); c.edge(evq, ap, "feeds"); c.edge(evq, pdl, "restores", note="TERPDL on error"); c.edge(cc, ap, "gates", note="ERRORSET")

c.pressure("a_fixed_pool_of_uniform_cells_is_consumed_by_a_computation_that_cannot_track_the_lifetime_of_what_it_builds",
    condition="the organism's work product is linked structure in a fixed pool of identical cells; structure is shared and cyclic; the organism cannot know when a cell dies; the pool must be recycled or the computation halts",
    resource_or_constraint="pool size; a bounded scratch area for whatever reclamation needs (the ancestor's PDL)", failure_condition="halt on exhaustion with live data still small (a leak), or reclaiming a live cell (corruption)",
    world_punishes="both; and thrashing (collecting often for little yield)", world_rewards="reclamation that is exact from a declared root set and cheap in scratch space",
    observable_consequence="cells reclaimed per collection vs live cells; collections per 10^6 conses; corruption detected by a reachability oracle", vacuity_condition="a pool larger than total allocation (never collect) or acyclic unshared data (reference counts suffice)",
    trivial_shortcuts="reference counting when the world has no cycles; a world that exposes lifetimes", cheat_control="an organism given a lifetime oracle must reclaim every dead cell at zero scratch cost; an organism that never reclaims must halt at pool size: the world must separate them and must contain cycles or the pressure is a different one",
    cost_class="CPU-scale", source_evidence="record human_failure_condition; lisp15.asm RECLAIMER; CONS/FROUT", purpose="PURPOSE: automatic storage reclamation (McCarthy 1960, as coded 1961)")

c.pressure("machine_code_that_holds_pointers_in_raw_storage_must_declare_them_or_lose_them",
    condition="the reclaimer sees only registered ranges and a stack; any organism component that keeps a pointer elsewhere across an allocation must register the place", resource_or_constraint="registration cost per temporary; scanning cost per registered word",
    failure_condition="a dangling pointer after a collection", world_punishes="unregistered temporaries (corruption) and over-registration (scan cost, retention)", world_rewards="a discipline that registers exactly the live temporaries",
    observable_consequence="corruptions per collection under a mutator that allocates during computation; scan words per collection", vacuity_condition="no allocation between taking a pointer and using it", trivial_shortcuts="register the whole address space (conservative scan)",
    cheat_control="a mutator that registers nothing must corrupt on the first collection during a hold; one that registers everything must show the scan cost: if the world cannot see either, the root-declaration pressure is absent",
    cost_class="CPU-scale", source_evidence="TEMLIS marker 1537-1570", purpose="PURPOSE: root registration for a non-moving collector")

c.ancestry("algorithm_from", "McCarthy 1960 (Recursive functions of symbolic expressions); Hart, Levin et al., LISP 1.5 Programmer's Manual 1962", note="from the README and the REM comments (M-expressions); not verified against the manual PDF this pass")
c.residue("PARTIALLY_EXPLAINED", ["~9,000 of 11,092 cards unread: compiler/LAP, reader/printer, arithmetic, arrays, RELOC, overlord", "provenance: the body is a 2014 transcription of a 1962 listing (README); Techne's grade is what Harmonia should read, not the record's handoff string",
                                   "no claim was executed; simh i7094 is the record's named world (REACHABLE, untried)"],
          note="the storage control program and the interpreter core are accounted for at mechanism level; everything else is named as unread")
c.save(state="COARSE")
