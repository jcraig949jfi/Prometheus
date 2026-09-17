"""Cut: femtolisp (Bezanson's femtolisp; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; position 76 of the 2026-09-17 NOT_CUT
order). Read: the file list; flisp.c apply_cl 934-1000 (the bytecode interpreter's frame layout and dispatch), the gc function names
(335, 403-410, 525); compiler.lsp function names (bcode:*, emit, compile-sym / -if / -begin / -while / -for). NOT read: the 59 opcode
cases, gc's body, the reader and printer, cvalues (the C-type layer), builtins, the boot image mechanism (flisp.boot, mkboot*.lsp).
Nothing ran (C; no compiler on M3).
"""
from nyx.atlas.author import Cut

F = "vault:femtolisp/upstream/tree/flisp.c"; CL = "vault:femtolisp/upstream/tree/compiler.lsp"
c = Cut("femtolisp", mode="ANCESTRY_AWARE", inspected=["flisp.c 934-1000, 335-410, 525 (names)", "compiler.lsp function inventory"], evidence=[("SOURCE_READ", F + ":934-1000"), ("SOURCE_READ", CL + ":52-320")],
        note="a small Lisp whose compiler is written in the Lisp itself and whose runtime is a C bytecode interpreter: the compiler (compiler.lsp) emits bytecode into a code object with a constant table; the interpreter (apply_cl) runs a stack machine with explicit frames (environment, previous frame, argument count, captured flag) and computed-goto dispatch when available; a boot image (flisp.boot) holds the compiled compiler so the system starts without interpreting source; a mark-and-sweep collector with a handle stack protects C-held references")

vm = c.organ("bytecode_stack_machine_with_explicit_frames_holding_environment_previous_frame_argument_count_and_a_captured_flag_dispatched_by_computed_goto", human_name="apply_cl (934-1000): func from the stack, ip from fn_bcode, stack growth check from the code's declared depth, the frame push (fn_env, curr_frame, nargs, ip slot, captured), OP(OP_ARGC) and the 59 opcode cases; USE_COMPUTED_GOTO", status="ACCEPTED",
    mechanism="calling a closure pushes its environment, the caller's frame pointer, the argument count and a flag saying whether the frame's variables have been captured by an inner closure (in which case they live in a heap vector, not the stack); the code object declares its maximum stack depth so the check happens once per call; opcodes are dispatched by a jump table of label addresses when the compiler supports it; tail calls reuse the frame (the record's 'tail calls')",
    input="a closure and arguments on the stack", output="a value", state="the value stack, curr_frame", update="per instruction", assumptions=["a stack machine with a per-function depth declaration is simple and fast enough; capturing decides at compile time which frames must be heap-allocated"],
    fitness_value_in_ancestor="a Lisp small enough to embed (it bootstraps Julia's parser) with proper tail calls", failure_landscape="UNKNOWN by run", human_prior="the classic bytecode Lisp/Scheme VM; computed-goto dispatch from the gcc idiom", evidence_ref=F + ":934-1000", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="apply_cl; MEDIUM because the opcode bodies were not read",
    coverage={"input_topology": "SEQUENCE", "output_topology": "MIXED", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_EPISODE", "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP"})

comp = c.organ("compiler_written_in_the_language_emitting_bytecode_into_a_code_object_with_a_constant_table_and_shipped_as_a_boot_image", human_name="compiler.lsp: bcode:code / ctable / nconst / cdepth (52-57), emit (65), compile-sym, compile-if, compile-begin, compile-while, compile-for (245-320); flisp.boot; mkboot0.lsp / mkboot1.lsp; bootstrap.sh", status="CANDIDATE",
    mechanism="the compiler walks source forms with an environment of lexical variables, emitting opcodes and constant-table indices into a growing code vector while tracking the maximum stack depth; special forms each have a compile function; the result is a closure over a code object; because the compiler is itself Lisp, the build compiles it once into flisp.boot (a serialised heap image) that the C runtime loads at start, and rebuilding the image from source is a two-stage bootstrap",
    input="source forms", output="code objects", state="the code vector under construction", update="per form", assumptions=["writing the compiler in the language keeps the C core small; a boot image avoids interpreting the compiler at every start"],
    fitness_value_in_ancestor="the C core is under 3,000 lines with the compiler outside it", failure_landscape="by reading: a change to the VM's opcodes requires regenerating the boot image with the old image (the bootstrap chicken-and-egg the two mkboot files handle)", human_prior="the metacircular compiler with a boot image (every self-hosting Lisp since MacLisp)", evidence_ref=CL + ":52-320 (names)", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="compiler.lsp and the boot files; CANDIDATE because bodies were not read",
    coverage={"input_topology": "TREE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE"})

c.reject("gc (mark-and-sweep with a handle stack: 335-410, 525-620), the reader, printer, equal/hash, cvalues (a C-type and foreign-value layer), builtins, operators, iostream, the numeric tower, the examples and the ASCII Mona Lisa", reason="OTHER", evidence="NOT READ; residue", note="cvalues (typed C values as first-class Lisp objects) is the part Julia inherited and deserves its own DEEP item")
c.reject("'Lisp interpreter' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the VM, the compiler and the collector are separable; the atlas's lisp-1-5-ibm7090-1962 cut holds the ancestor's interpreter")

c.edge(comp, vm, "feeds", note="code objects")

c.pressure("a_language_runtime_must_be_small_enough_to_embed_in_another_system_yet_fast_enough_to_run_its_own_compiler_at_startup_and_support_deep_recursion_by_tail_calls",
    condition="an organism implements a Lisp for use inside a larger program; the score is core size (lines of C), startup time, and correct tail-call behaviour on deep recursion; the compiler must be part of the system", resource_or_constraint="a few thousand lines of C; one boot image",
    failure_condition="a core too large to embed, a startup that interprets the compiler from source, or stack growth on tail recursion", world_punishes="a tree-walking interpreter with the compiler in C; no boot image", world_rewards="a bytecode VM with frame reuse and a self-hosted compiler shipped as an image",
    observable_consequence="lines of C in the core, startup time with and without the boot image, and stack depth on a million-iteration tail loop", vacuity_condition="a language without recursion", trivial_shortcuts="linking an existing large Lisp (which the size score punishes)",
    cheat_control="an organism given a precompiled image must start in milliseconds; the same system bootstrapped from source must take seconds; a VM without tail-call frame reuse must overflow on the loop: the world must show all three",
    cost_class="CPU-scale", source_evidence="flisp.c apply_cl; compiler.lsp; the boot files", purpose="PURPOSE: an embeddable Scheme-like Lisp (Bezanson 2008-)")

c.ancestry("derived_from", "Scheme (Sussman & Steele 1975) in design; the atlas's lisp-1-5-ibm7090-1962 is the family's origin", note="from the README and the record")
c.residue("LARGE_RESIDUE", ["opcodes, gc, reader, cvalues and builtins unread", "the compiler read by names (CANDIDATE)", "nothing ran"], note="the organisation (self-hosted compiler + C VM + boot image) is located; the substance is in the residue")
c.save(state="COARSE")
