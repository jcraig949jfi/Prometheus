"""Cut: swipl-9.2.9 (SWI-Prolog; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; position 30 of the 2026-09-17 NOT_CUT order).
Read: src/pl-vmi.c -- the 230 VMI names (inventory), and the bodies of I_CALL/normal_call, I_DEPART (last-call optimisation),
I_EXIT, C_OR (in-clause choice point), I_CUT. NOT read: pl-wam.c (the main loop and backtracking), pl-comp.c (the clause compiler),
pl-tabling.c (SLG tabling, 9,468 lines), pl-gc.c, pl-thread.c, the 1,860 other files. Nothing ran (SOURCE_ONLY; a 220k-line C
build). The cut is an inventory-level map of the VM with two mechanisms read, not a dissection of the engine.
"""
from nyx.atlas.author import Cut

V = "vault:swipl-9.2.9/upstream/tree/swipl-devel-9.2.9/src/pl-vmi.c"
c = Cut("swipl-9.2.9", mode="ANCESTRY_AWARE", inspected=["src/pl-vmi.c: VMI inventory; I_CALL, I_DEPART, I_EXIT, C_OR, I_CUT bodies"], evidence=[("SOURCE_READ", V + ":1967-2010"), ("SOURCE_READ", V + ":2171-2300"), ("SOURCE_READ", V + ":2708-2830")],
        note="a WAM-descended VM with 230 instructions in families: H_ (head unification), B_ (body argument construction), A_ (arithmetic), C_ (control: choice points, if-then-else, cuts), I_ (calls, exits, foreign calls, exceptions), S_ (supervisors per predicate kind), T_ (trie/tabling); the two mechanisms read are the frame/choice-point discipline and last-call optimisation")

vm = c.organ("instruction_families_partitioning_unification_construction_control_call_supervision_and_tabling", human_name="the 230 VMI() definitions in pl-vmi.c (H_* B_* A_* C_* I_* S_* T_*)", status="ACCEPTED",
    mechanism="clause heads compile to H_ instructions that unify incoming arguments against the head's structure (specialised per term type: atom, small int, var, first-var, functor, list, with FF/VF/VV variants); bodies compile to B_ instructions that build argument frames; A_ does compiled arithmetic; C_ handles in-clause control (or, if-then-else, soft cut, cuts); I_ handles predicate call/depart/exit, foreign determinate/nondeterminate calls, catch/throw, delimited continuations (reset/shift); S_ are per-predicate supervisors (static, dynamic, multifile, wrapped, undefined); T_ walk answer tries for tabling",
    input="compiled clauses", output="execution", state="the local (frame) stack, global (term) stack, trail, choice-point chain", update="per instruction",
    assumptions=["specialising instructions per term type and per variable-occurrence class (first/subsequent) is worth the instruction count (a JIT-free way to skip general unification)"],
    fitness_value_in_ancestor="the instruction set IS the engine's design record: every specialisation is a measured hot path made explicit", failure_landscape="UNKNOWN by run", human_prior="Warren's Abstract Machine (1983) as the ancestor; SWI's set diverged from the WAM in the 1980s (its own documentation)",
    evidence_ref=V + ":VMI inventory (grep)", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the VMI list; MEDIUM because only names were read for most",
    coverage={"input_topology": "SEQUENCE", "output_topology": "MIXED", "state_amount": "UNBOUNDED", "state_persistence": "PER_EPISODE", "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP"})

lco = c.organ("last_call_optimisation_that_reuses_the_frame_when_no_newer_choice_point_exists", human_name="I_DEPART vs I_CALL (pl-vmi.c 1967-2010, 2171-2280)", status="ACCEPTED",
    mechanism="I_CALL saves the current frame's state, allocates the next frame at lTop with the arguments already written there, and jumps to normal_call; I_DEPART is emitted for the last goal of a clause: if the newest choice point is older than the current frame (BFR <= FR) and the flag allows, the current frame is released (leaveDefinition) and the callee reuses its space, so tail-recursive predicates run in constant stack; watched frames and undefined predicates fall back to I_CALL semantics",
    input="a call to a predicate as the last goal", output="a frame reused or a new one", state="FR, NFR, BFR, lTop", update="per last call", assumptions=["a choice point newer than the frame pins the frame (it may be needed on backtracking); determinism is what makes the reuse safe"],
    fitness_value_in_ancestor="loops written as recursion do not grow the stack; the whole style of Prolog programming depends on it", failure_landscape="by reading: a leftover choice point (a non-deterministic predicate earlier in the clause) silently disables the optimisation and the stack grows -- the classic Prolog performance trap, visible here as the BFR <= FR test",
    human_prior="the WAM's execute instruction; SWI's conditions (watched frames, undefined-procedure trapping) are its own", evidence_ref=V + ":1967-2010, 2171-2280", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="I_CALL, normal_call, I_DEPART",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "resource_dependence": "MEMORY", "failure_mode": "DEGRADES"})

chp = c.organ("in_clause_choice_points_and_cut_as_operations_on_a_choice_chain_relative_to_the_frame", human_name="C_OR / I_CUT / I_EXIT (pl-vmi.c 2708-2830)", status="ACCEPTED",
    mechanism="C_OR pushes a jump choice point whose alternative is PC+skip (a disjunction's second branch), growing the local stack if needed; I_CUT discards every choice point newer than the current frame (nothing to do if BFR <= FR); I_EXIT leaves a clause: if newer alternatives exist the frame must stay for backtracking, else it is popped; the debugger hooks (ports) sit inside these instructions",
    input="disjunctions and cuts in the clause", output="a choice chain", state="the choice-point chain (BFR), the trail", update="per C_OR / cut / exit", assumptions=["backtracking is a chain walk to the newest choice point; the cut's semantics are 'newer than my frame'"],
    fitness_value_in_ancestor="disjunction and cut without predicate calls; the choice chain is the engine's search state", failure_landscape="UNKNOWN by run", evidence_ref=V + ":2708-2830", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the three instructions",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_EPISODE", "stochasticity": "DETERMINISTIC", "recovery": "ROLLS_BACK"})

c.reject("pl-wam.c (the main loop, backtracking, exception unwinding), pl-comp.c (clause compilation), pl-tabling.c (SLG resolution / answer tries -- the most mechanism-rich unread module), pl-gc.c, pl-thread.c, libbf, the 1,860 other files", reason="OTHER", evidence="NOT READ (~215,000 of 220,000 lines); residue", note="pl-tabling.c should be its own specimen: tabled evaluation is a distinct mechanism family (the record's lineage tags name it)")
c.reject("'Prolog' / 'the WAM' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the instruction families, the frame discipline, the choice chain and tabling are separable; the vault's gnu-prolog-1.5.0 holds a different WAM to compare against")

c.edge(vm, lco, "feeds"); c.edge(vm, chp, "feeds"); c.edge(chp, lco, "gates", note="BFR <= FR")

c.pressure("a_search_over_alternatives_must_retain_exactly_the_state_needed_to_resume_older_alternatives_and_discard_the_rest_as_soon_as_determinism_is_known",
    condition="an organism explores alternatives depth-first with unification; each alternative may need the state at its creation; most calls turn out deterministic; memory is the cost", resource_or_constraint="a frame stack and a choice chain",
    failure_condition="stack growth on deterministic recursion, or a lost alternative", world_punishes="keeping frames pinned by choice points that will never be taken; discarding a frame an alternative needed", world_rewards="last-call reuse gated on the choice chain and cuts that trim it",
    observable_consequence="stack size vs recursion depth on a deterministic loop with and without a spurious earlier choice point", vacuity_condition="no alternatives (a functional language)", trivial_shortcuts="unbounded memory",
    cheat_control="a determinism oracle supplied by the world must give constant stack always; the ancestor with LCO disabled (the PLFLAG_LASTCALL flag in the code) must grow linearly: the world must show both",
    cost_class="CPU-scale", source_evidence="pl-vmi.c I_DEPART, C_OR, I_CUT", purpose="PURPOSE: logic programming execution (SWI-Prolog, Wielemaker 1987-)")

c.ancestry("derived_from", "Warren 1983 (WAM); SWI-Prolog's own VM lineage from 1987; tabling from XSB (SLG resolution)", note="from the source comments and the record")
c.residue("LARGE_RESIDUE", ["~98% of the source unread; the VM read as an inventory plus three instruction groups", "tabling, GC and the compiler are each specimen-sized", "nothing ran"], note="a map, not a dissection; recorded as such")
c.save(state="COARSE")
