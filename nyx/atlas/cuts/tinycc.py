"""Cut: tinycc (ancestry-aware, Stage A COARSE; SOURCE_READ function indexes of tccgen.c, tccpp.c, tccrun.c, tccelf.c; tccgen.c 1844-1900 (gv)
and 3042-3075 (gen_op) read; file sizes. 26,579 lines in the nine core files; a one-pass C compiler with no IR. Read at subsystem
grain only: the anatomy below is the architecture's, confirmed at two points, not a line-level cut."""
from nyx.atlas.author import Cut

S = "vault:tinycc/upstream/tree/"
c = Cut("tinycc", mode="ANCESTRY_AWARE", inspected=["tccgen.c (index; gv; gen_op)", "tccpp.c (index)", "tccrun.c (index)", "tccelf.c (index)", "file sizes"],
        evidence=[("SOURCE_READ", S + "tccgen.c"), ("SOURCE_READ", S + "tccpp.c"), ("SOURCE_READ", S + "tccrun.c")],
        note="the interesting anatomy is what is ABSENT: no AST, no IR, no optimiser; parsing emits machine code directly through a value stack; every mechanism below is a consequence of that one design decision")

pp = c.organ("token_stream_with_macro_substitution_and_conditional_skipping_pulled_by_next", human_name="tccpp.c: next() / preprocess() / macro_subst / preprocess_skip", status="ACCEPTED",
    mechanism="the parser pulls one token at a time (next); the preprocessor is inline in that pull: directives are handled when a '#' is seen at line start (preprocess), macro bodies are stored as token strings (TokenString) and substituted with argument expansion and rescanning (macro_subst / macro_subst_tok), #if groups are skipped by scanning tokens (preprocess_skip), includes push a file on a stack",
    input="source bytes", output="one token per call", state="the file stack, the define table, the token-string buffers", update="per token", evidence_ref=S + "tccpp.c:874,1519,1792,2978-3470", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="tccpp.c",
    coverage={"input_topology": "STREAM", "output_topology": "STREAM", "state_amount": "LINEAR_IN_INPUT", "update_topology": "EVENT_DRIVEN", "memory": "FULL_HISTORY"})

vs = c.organ("value_stack_of_symbolic_operands_materialised_to_registers_on_demand", human_name="vstack / vtop / vpush* / vpop / vswap / vrott / gv()", status="ACCEPTED",
    mechanism="expression parsing pushes SValues (a type and a location: constant, symbol, local offset, register, lvalue flag) instead of emitting code; gv(rc) is the only point that forces a value into a register of class rc, generating loads (and, for bitfields, shift sequences; for float constants, a rodata entry) at that moment; operators pop two SValues and push one",
    input="parsed operands", output="register-resident values when needed", state="vstack (bounded), vtop", update="per operand / per operator", assumptions=["expressions are compiled left to right in one pass; no reordering is ever possible"],
    fitness_value_in_ancestor="the substitute for an IR: delayed materialisation gets constant folding and addressing modes for free", evidence_ref=S + "tccgen.c:898-1003,1844-2000", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the v* functions and gv/gv2",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "update_topology": "SINGLE_STEP", "memory": "WINDOW", "order_sensitivity": "SENSITIVE"})

fo = c.organ("constant_folding_and_type_promotion_inside_the_operator_dispatcher", parent=vs, human_name="gen_op / gen_opic / gen_opif / gen_opl", status="ACCEPTED",
    mechanism="gen_op classifies the operator (shift, compare, arithmetic), promotes the two top types per C rules (functions to pointers, integer promotion, pointer arithmetic scaling), and if both operands are constants folds them at compile time (gen_opic for integers, gen_opif for floats) else calls the target's gen_opi/gen_opf; long long on 32-bit targets is split in gen_opl",
    input="an operator token and two SValues", output="one SValue (constant or register)", state="none", update="per operator", evidence_ref=S + "tccgen.c:2100-3245", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="gen_op and its four helpers",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "NONE"})

jp = c.organ("forward_jump_lists_patched_when_the_label_is_reached", human_name="gjmp / gsym / gvtst / gind", status="ACCEPTED",
    mechanism="a conditional or unconditional jump to a not-yet-known target emits the instruction with the previous unresolved jump's address in its displacement field, forming a linked list through the code; gsym(t) walks that list writing the current position into each; gvtst turns the top SValue into a jump-on-condition (folding constants into an always/never jump)",
    input="jump requests and label positions", output="patched code", state="the chain heads (ints in the parser's locals)", update="per jump / per label", assumptions=["displacements are wide enough to hold a chain link"],
    fitness_value_in_ancestor="how one pass compiles if/while/&&/|| without a tree", evidence_ref=S + "tccgen.c:167-200,1056-1114", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="gsym / gjmp* / gvtst*",
    coverage={"input_topology": "EVENT", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "memory": "FULL_HISTORY"})

td = c.organ("recursive_descent_over_declarations_statements_and_expressions_emitting_as_it_goes", human_name="decl / type_decl / block / expr_* / unary", status="ACCEPTED",
    mechanism="the grammar is hand-written recursive descent (decl -> type_decl -> block -> statements -> expr_eq -> ... -> unary); each nonterminal pushes SValues or emits code immediately; symbols are a hashed stack scoped by block (sym_push / sym_pop); there is no tree",
    input="tokens", output="code + symbols", state="the symbol stack, local offsets, loop/switch contexts", update="per construct", evidence_ref=S + "tccgen.c:132-156 (declarations), 804 (labels)", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the parsing functions of tccgen.c",
    coverage={"input_topology": "STREAM", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "update_topology": "RECURSIVE"})

tg = c.organ("per_target_instruction_emitters_behind_a_fixed_interface", human_name="x86_64-gen.c / i386-gen.c / arm*-gen.c / riscv64-gen.c: load, store, gen_opi, gen_opf, gfunc_call, gfunc_prolog/epilog, gjmp", status="ACCEPTED",
    mechanism="the generic layer calls a fixed set of target functions to move SValues to and from registers and to emit arithmetic, calls and jumps; each target file is a few thousand lines of byte-emission (o(), gen_le32) with register-class tables; no instruction selection beyond that",
    input="SValues and register classes", output="machine bytes into the text section", state="ind (the emission pointer)", update="per emitted instruction", evidence_ref=S + "x86_64-gen.c, i386-gen.c (sizes; interface names from tccgen.c call sites)", confidence="LOW", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the *-gen.c files",
    coverage={"input_topology": "VECTOR", "output_topology": "SEQUENCE", "state_amount": "CONSTANT"})

el = c.organ("elf_sections_symbols_and_relocations_built_in_memory_then_written_or_relocated_in_place", human_name="tccelf.c + tccrun.c", status="ACCEPTED",
    mechanism="code and data are appended to Section buffers (section_add / section_ptr_add) with an ELF symbol table and relocation entries as they are referenced; output either writes an ELF object/executable (tccelf) or, for -run, allocates executable memory, relocates the sections in place (tcc_relocate_ex), protects pages and jumps to main, with a backtrace/exception hook (tccrun)",
    input="sections, symbols, relocs", output="a file or a running program", state="the Section list, symtab", update="per emission; once at link", evidence_ref=S + "tccelf.c:130-380; tccrun.c:59-91", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="tccelf.c + tccrun.c",
    coverage={"input_topology": "SET", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_EPISODE"})

c.reject("an optimiser / intermediate representation", reason="OTHER", evidence="none exists: tccgen.c emits from the value stack directly; there is no file between the parser and the target emitters", note="NEGATIVE ANATOMY: the absence is the fossil's identity (compile speed over code quality)")
c.reject("'the compiler' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="seven subsystems with separate state and files")
c.reject("tccasm.c (inline assembler), tccpe.c / tccmacho.c (other object formats), libtcc.c (API and option parsing), tcc.c (driver)", reason="OTHER", evidence="by file name; unread", note="UNKNOWN, not rejected on merit")
c.reject("lib/ (runtime helpers: bcheck, libtcc1), include/, tests/", reason="EFFECT_FROM_ENVIRONMENT", evidence="runtime support and the test suite; Techne's smoke (exit 42) is the executed evidence")

c.edge(pp, td, "feeds"); c.edge(td, vs, "feeds"); c.edge(vs, fo, "feeds"); c.edge(fo, tg, "triggers", note="non-constant ops"); c.edge(vs, tg, "triggers", note="gv loads"); c.edge(td, jp, "feeds"); c.edge(jp, tg, "updates", note="patches displacements"); c.edge(tg, el, "stores", note="bytes into sections"); c.edge(vs, el, "stores", note="float constants into rodata; symbols")

c.pressure("a_whole_language_must_compile_fast_enough_to_run_source_as_a_script",
    condition="C programs are to be compiled and executed in one command in the time an interpreter would take to start; code quality is secondary", resource_or_constraint="compile time; memory during compilation",
    failure_condition="a multi-pass pipeline too slow for -run", world_punishes="intermediate representations, separate passes, optimisation", world_rewards="single-pass emission with just enough deferral (the value stack) to be correct",
    observable_consequence="compile time per line vs gcc; code speed of the output (worse)", vacuity_condition="no time budget", trivial_shortcuts="an interpreter (slower to run; the world must charge run time too)",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="the absence of an IR; tccrun.c", purpose="PURPOSE: a small fast C compiler (Bellard)")
c.pressure("control_flow_targets_are_not_known_when_the_jump_must_be_emitted",
    condition="one pass means the code for a branch target does not exist when the branch is compiled", resource_or_constraint="no second pass",
    failure_condition="unresolvable forward references", world_punishes="two passes", world_rewards="threading the unresolved jumps through the code itself and patching at the label",
    observable_consequence="correct if/while/&&/|| code from one pass", vacuity_condition="a tree or a second pass", trivial_shortcuts="none in one pass",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="gsym / gjmp", purpose="PURPOSE: same")

c.ancestry("algorithm_from", "Bellard's OTCC / obfuscated C compiler lineage (by common knowledge, not from the body)", note="human prior")
c.residue("LARGE_RESIDUE", ["the parser (9,001 lines) confirmed at two functions only", "targets, assembler, PE/Mach-O, libtcc API, bounds checker unread", "nothing ran here"],
          note="the architecture is confidently cut at subsystem grain; every organ below the value stack is CANDIDATE-quality evidence despite the ACCEPTED status of the ones whose entry points were read")
c.save(state="COARSE")
