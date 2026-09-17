"""Cut: pforth (Phil Burk's portable Forth in C; ancestry-aware, Stage A COARSE; SOURCE_READ on M3; position 29 of the 2026-09-17
NOT_CUT order). Read: csrc/pf_inner.c pfCatch 286-330 (register caching, the secondary-descent loop) and the EXIT/BRANCH/EXECUTE/
LOOP cases; csrc/pfcompil.c ffInterpret 834-880 and the function list (dictionary, colon/semicolon, literals, outer loop).
NOT read: the ~180 remaining primitive cases, pf_save.c (dictionary images), pf_core.c, pf_words.c, the Forth-level system in
fth/. Nothing ran (C; not on M3).
"""
from nyx.atlas.author import Cut

I = "vault:pforth/upstream/tree/csrc/pf_inner.c"; C = "vault:pforth/upstream/tree/csrc/pfcompil.c"
c = Cut("pforth", mode="ANCESTRY_AWARE", inspected=["pf_inner.c pfCatch head + control-flow cases", "pfcompil.c ffInterpret + function list"], evidence=[("SOURCE_READ", I + ":286-330"), ("SOURCE_READ", I + ":381-400, 513-518, 961-970, 1465-1475"), ("SOURCE_READ", C + ":834-880"), ("SOURCE_READ", C + ":51-131, 594-731")],
        note="a token-threaded Forth: a word is either a primitive (a small integer dispatched by one switch) or a secondary (an address of a cell array of tokens); the inner loop descends into secondaries by pushing the instruction pointer, and the outer interpreter is the same loop with a text source and a compile/interpret state flag")

inner = c.organ("token_threaded_inner_interpreter_descending_into_secondaries_by_pushing_the_instruction_pointer", human_name="pfCatch (pf_inner.c): the while(!IsTokenPrimitive) loop, M_R_PUSH(InsPtr), the switch, ID_EXIT", status="ACCEPTED",
    mechanism="a token below a threshold is a primitive and is executed by a switch case; any other token is a secondary: the current instruction pointer is pushed on the return stack, the pointer is set to the secondary's body, and the next token is read; EXIT pops the return stack; the top of the data stack, the two stack pointers and the instruction pointer are cached in C registers for the whole run (LOAD/SAVE_REGISTERS around any call out)",
    input="an execution token", output="side effects on the two stacks and memory; a ThrowCode on error", state="data stack, return stack, instruction pointer (all in the task struct)", update="per token",
    assumptions=["secondaries contain only tokens (no machine code), so the same image runs on any C platform -- the 'portable' in the name", "the return stack is shared with the program's own R> >R use"],
    fitness_value_in_ancestor="one C function is the whole VM; portability over speed", failure_landscape="by reading: no bounds checks in the hot loop; a corrupted token past the switch falls to default", human_prior="token threading (vs direct/indirect) chosen for portability; the register-caching macros are the author's",
    evidence_ref=I + ":286-330, 381-386, 961-970", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="pfCatch's loop head, the descent loop, ID_EXIT and ID_EXECUTE",
    coverage={"input_topology": "SEQUENCE", "output_topology": "MIXED", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE"})

ctl = c.organ("control_flow_as_relative_branch_tokens_with_loop_indices_on_the_return_stack", human_name="ID_BRANCH / ID_0BRANCH (M_BRANCH) / ID_LOOP_P and friends", status="ACCEPTED",
    mechanism="BRANCH reads a cell offset after itself and adds it to the instruction pointer; 0BRANCH does so only if the popped top is zero; counted loops keep index and limit on the RETURN stack and LOOP increments, compares and branches back or skips the offset; IF/ELSE/THEN and DO/LOOP compile to these tokens with offsets patched at compile time",
    input="the token stream", output="a new instruction pointer", state="the return stack (loop parameters)", update="per control token",
    assumptions=["structured control compiles to a handful of branch primitives; the return stack doubles as loop-parameter storage (so R> inside a loop is a footgun the language accepts)"],
    fitness_value_in_ancestor="no parser at run time; control is data", failure_landscape="UNKNOWN by run", evidence_ref=I + ":513-518, 1465-1475", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the branch and loop cases",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SCALAR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "update_topology": "SINGLE_STEP"})

outer = c.organ("outer_interpreter_that_reads_words_and_either_executes_or_compiles_them_by_a_state_flag", human_name="ffInterpret / FindAndCompileOrExecute / ffColon / ffSemiColon / ffLiteral (pfcompil.c)", status="ACCEPTED",
    mechanism="read a whitespace-delimited word from the source; look it up in the dictionary; if found, execute it (interpret state) or append its token to the definition under construction (compile state), unless the word is IMMEDIATE, which executes even while compiling; if not found, try to parse a number and push it or compile a LITERAL token; ':' opens a definition (creates a header, sets compile state), ';' appends EXIT and closes it",
    input="text", output="executed effects or a new dictionary entry", state="gVarState (compile/interpret), the dictionary pointer", update="per word",
    assumptions=["the language extends itself: IMMEDIATE words run the compiler; there is no grammar beyond 'words separated by blanks'"],
    fitness_value_in_ancestor="the compiler is a few dozen lines because the inner interpreter is the compiler's target and the language's own words build the rest", failure_landscape="by reading: an error mid-definition leaves the state flag cleared (the finally block) and the partial definition in the dictionary",
    human_prior="Moore's Forth outer interpreter; immediate words as the extension mechanism", evidence_ref=C + ":834-880, 594-731", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="ffInterpret and the colon/semicolon/literal functions",
    coverage={"input_topology": "STREAM", "output_topology": "MIXED", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "adaptation": "STRUCTURE"})

dic = c.organ("dictionary_as_a_linked_list_of_name_headers_searched_newest_first", human_name="CreateDicEntry / ffFindNFA / ffFind / NameToToken (pfcompil.c 64-160, 416-540)", status="ACCEPTED",
    mechanism="each definition gets a header (name, flags, link to the previous header, the execution token); lookup walks the list from the newest entry, comparing names, so a redefinition shadows the old one without deleting it; the token is recovered from the header by fixed offsets",
    input="a word name", output="its token and flags, or not found", state="the dictionary (a growing array of cells)", update="per definition",
    assumptions=["linear search is fast enough for a few thousand words; newest-first gives redefinition semantics for free"], fitness_value_in_ancestor="the whole namespace in one structure the program can inspect and extend", failure_landscape="UNKNOWN by run",
    evidence_ref=C + ":64-160, 416-540", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the dictionary functions",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "DURABLE", "memory": "ARCHIVE", "stochasticity": "DETERMINISTIC"})

c.reject("the ~180 arithmetic/stack/memory/I/O primitives, pf_save.c (dictionary image save/load), pf_core.c, pf_words.c, the fth/ Forth sources, the C-call bridge (ID_CALL_C)", reason="OTHER", evidence="NOT READ; the primitives are the alphabet, not mechanisms", note="pf_save.c is where the 'image' portability lives; unread")
c.reject("'Forth' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="inner interpreter, control primitives, outer interpreter and dictionary are four separable mechanisms; the vault's tinyscheme/femtolisp interpreters replace each differently")

c.edge(dic, outer, "feeds"); c.edge(outer, dic, "updates"); c.edge(outer, inner, "feeds", note="executes found words"); c.edge(inner, ctl, "feeds"); c.edge(outer, ctl, "updates", note="compiles branch tokens with patched offsets")

c.pressure("a_language_must_be_extended_by_its_own_programs_at_run_time_with_no_parser_and_a_few_kilobytes_of_interpreter",
    condition="an organism must accept new named behaviours at run time, composed from existing ones, and run them at near-primitive speed, on a machine with tiny memory; no grammar beyond tokens and blanks",
    resource_or_constraint="interpreter size; dictionary memory; one dispatch per token", failure_condition="a definition that cannot be built from earlier ones, or a run-time cost per token that grows with program size",
    world_punishes="parsers (size), tree-walking (speed), fixed vocabularies (no extension)", world_rewards="threaded code with a self-extending dictionary and immediate words", observable_consequence="interpreter size vs tokens per second vs number of user definitions",
    vacuity_condition="a fixed program (compile once)", trivial_shortcuts="a bigger machine", cheat_control="a native-compiled version of the same program is the speed ceiling; a tree-walking interpreter of the same words is the floor: the world must place threaded code between them",
    cost_class="CPU-scale", source_evidence="pf_inner.c pfCatch; pfcompil.c ffInterpret", purpose="PURPOSE: a portable, self-extending Forth (Burk 1994-)")

c.ancestry("algorithm_from", "Moore's Forth (1970); token threading as the portable variant", note="from the code; not verified")
c.residue("PARTIALLY_EXPLAINED", ["the primitive set, the image save/load and the Forth-level system unread", "nothing ran"], note="the four interpreter mechanisms are located")
c.save(state="COARSE")
