"""Cut: corewar-redcode (ancestry-aware, Stage A COARSE; SOURCE_READ corewar/mars.py 31-330 (MARS class, step through MOV), corewar/core.py
(function index), corewar/redcode.py (class index); graphics.py, the parser body, tests/ and warriors/ skimmed by name). A Python
MARS (ICWS '94) -- the WORLD of the Core War artificial-life lineage, not a warrior."""
from nyx.atlas.author import Cut

S = "vault:corewar-redcode/upstream/tree/corewar/"
c = Cut("corewar-redcode", mode="ANCESTRY_AWARE", inspected=["mars.py 31-330", "core.py (index)", "redcode.py (index)", "tests/, warriors/ (names)"],
        evidence=[("SOURCE_READ", S + "mars.py"), ("SOURCE_READ", S + "core.py")],
        note="this fossil is an ENVIRONMENT: every mechanism below is a rule of the world the warriors evolve in; the atlas records it because Vivarium-shaped questions (what a world must contain) are answered by exactly these rules")

core = c.organ("circular_shared_memory_of_instructions_with_read_and_write_reach_limits", human_name="Core", status="ACCEPTED",
    mechanism="a fixed-size (8000) array of instruction records, addressed modulo its size (trim); reads and writes are further folded into a window around the executing address (trim_read / trim_write with read_limit / write_limit, both default to the whole core); cleared to a DAT instruction",
    input="addresses", output="instruction records", state="the array", update="per write", assumptions=["all warriors share one address space; there is no protection"],
    fitness_value_in_ancestor="the single resource fought over", evidence_ref=S + "core.py:10-50", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="core.py",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "resource_dependence": "SHARED_RESOURCE", "competition": "CONTENDS"})

sch = c.organ("round_robin_over_warriors_each_popping_one_task_from_a_bounded_fifo", human_name="MARS.step / task_queue / enqueue", status="ACCEPTED",
    mechanism="one step executes one instruction per LIVE warrior in fixed order: pop the front of the warrior's task queue as the program counter; instructions push their successor (pc + 1, or a jump target, or both for SPL -- not shown) at the back; enqueue is dropped silently when the queue holds max_processes; a warrior with an empty queue is dead",
    input="warriors' task queues", output="one executed instruction per warrior", state="task_queue per warrior (a list of addresses)", update="per step", assumptions=["fairness by construction: every live warrior gets exactly one instruction per step regardless of its process count -- a warrior's processes share its turn"],
    fitness_value_in_ancestor="the game's clock and its death rule (DAT executes -> no enqueue -> process lost)", evidence_ref=S + "mars.py:80-100,286-330", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="MARS.step outer loop + enqueue",
    coverage={"input_topology": "SET", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SWEEP", "competition": "ARBITRATES", "failure_mode": "COLLAPSES"})

ad = c.organ("operand_resolution_with_pre_decrement_and_post_increment_side_effects", human_name="addressing modes (#, $, @, <, >, *, {, })", status="ACCEPTED",
    mechanism="for each of the two operands: immediate -> the instruction itself; direct -> pc + number; indirect -> pc + number + the pointed instruction's A or B field; pre-decrement modes first decrement that field in core, post-increment modes increment it after the read; the read and write pointers are trimmed separately; the operand instruction is COPIED before the opcode acts (ira, irb) so a self-modifying instruction sees the old value",
    input="an instruction, pc, core", output="ira, irb (copies), rpa/rpb/wpa/wpb (offsets)", state="core (mutated by pre/post modes)", update="per instruction", assumptions=["the ICWS '94 evaluation order (A operand fully before B)"],
    fitness_value_in_ancestor="side-effecting addressing is where Core War's compact self-modifying programs (the Imp, the Dwarf's bomb pointer) come from", evidence_ref=S + "mars.py:96-184", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the operand blocks of step()",
    coverage={"input_topology": "MIXED", "output_topology": "VECTOR", "state_amount": "NONE", "order_sensitivity": "SENSITIVE", "representation_sensitivity": "SENSITIVE"})

op = c.organ("opcode_and_modifier_dispatch_over_field_subsets", human_name="DAT MOV ADD SUB MUL DIV MOD JMP JMZ JMN DJN CMP/SEQ SNE SLT SPL NOP with modifiers .A .B .AB .BA .F .X .I", status="ACCEPTED",
    mechanism="the modifier selects which fields (A, B, cross, both, swapped, whole instruction) the opcode reads from ira/irb and writes at pc + wpb; arithmetic through do_arithmetic, comparisons through do_comparison (skip the next instruction on true: enqueue pc + 2); DAT enqueues nothing (kills the process); DIV/MOD by zero kills (the try in do_arithmetic, by structure); every access fires a core_event for observers",
    input="ir, ira, irb", output="core writes and the next pc", state="none", update="per instruction", evidence_ref=S + "mars.py:186-330 (through MOV; ADD..SPL follow the same shape, skimmed)", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="do_arithmetic / do_comparison / the opcode chain",
    coverage={"input_topology": "VECTOR", "output_topology": "MIXED", "state_amount": "NONE", "update_topology": "SINGLE_STEP"})

ld = c.organ("warrior_placement_at_random_offsets_with_minimum_separation", human_name="load_warriors", status="ACCEPTED",
    mechanism="the core is divided into equal spaces; each warrior is copied at n * space + a random offset bounded so that warriors stay at least minimum_separation apart; its task queue starts with one process at its start label",
    input="warriors, core size, minimum_separation, a random source", output="initial core and task queues", state="none", update="once per round", evidence_ref=S + "mars.py:55-79", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="load_warriors",
    coverage={"input_topology": "SET", "output_topology": "VECTOR", "state_amount": "NONE", "stochasticity": "ENVIRONMENT_RANDOM"})

pa = c.organ("redcode_assembler_with_labels_expressions_and_default_modifiers", human_name="redcode.parse / Instruction.default_modifier", status="CANDIDATE",
    mechanism="text -> Instruction records (opcode, modifier, two modes, two numbers); labels and EQU-style definitions resolved to relative offsets; a missing modifier is filled per the ICWS '94 defaults (default_modifier)", input="Redcode text", output="a Warrior", state="none",
    evidence_ref=S + "redcode.py:105-365 (index only)", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="redcode.py",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "NONE"})

c.reject("graphics.py (pygame visualiser via core_event)", reason="OTHER", evidence=S + "graphics.py -- an observer of core events", note="instrument")
c.reject("'Core War' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the memory, the scheduler, the addressing rules and the instruction set are separate rules that other MARS implementations vary independently (read/write limits, max processes, core size are constructor parameters here)")
c.reject("the shipped warriors (warriors/*.red) and tests", reason="EFFECT_FROM_ENVIRONMENT", evidence="tests/mars_test.py, warriors/ -- organisms and checks, not the world", note="the Imp and Dwarf in the record's example are ORGANISMS of this world; the atlas of organisms is not this pass")

c.edge(pa, ld, "feeds"); c.edge(ld, core, "stores"); c.edge(ld, sch, "stores", note="initial task queues"); c.edge(sch, ad, "feeds", note="pc"); c.edge(ad, op, "feeds"); c.edge(op, core, "updates"); c.edge(op, sch, "updates", note="enqueue successors / none on DAT")
c.edge(core, ad, "feeds"); c.edge(ad, core, "updates", note="pre-decrement / post-increment")

c.pressure("programs_share_one_unprotected_memory_and_can_only_survive_by_overwriting_each_other_first",
    condition="every program's code is data in the same circular memory; any instruction can write anywhere (within the reach limit); a program dies when all its processes execute a DAT; turns alternate one instruction per program", resource_or_constraint="8000 cells; one instruction per turn; max_processes",
    failure_condition="being overwritten with DAT before overwriting the opponent", world_punishes="staying still (bombable), being large (findable), spending turns on non-lethal work", world_rewards="self-copying / self-moving code (the Imp), sparse bombing (the Dwarf), process splitting to survive partial damage",
    observable_consequence="which warrior survives after N cycles, over many random placements", vacuity_condition="one warrior", trivial_shortcuts="none obvious inside the rules; the rules themselves (read/write limits, process cap) are the knobs",
    cheat_control="a warrior told the opponent's placement must win nearly always; if random placement is not enforced, the world rewards fixed-address bombs", cost_class="CPU-scale", source_evidence="mars.py step / enqueue / DAT; record example (Imp vs Dwarf)", purpose="PURPOSE: a programming game (Dewdney 1984); later, an artificial-life substrate")
c.pressure("side_effecting_address_arithmetic_makes_tiny_programs_expressive",
    condition="with pre-decrement and post-increment operand modes one instruction can advance a pointer and act through it; program length is a liability (pressure 1)", resource_or_constraint="instruction count",
    failure_condition="long, slow warriors", world_punishes="explicit loop counters and pointer updates", world_rewards="folding the pointer update into the operand fetch",
    observable_consequence="warrior length vs win rate", vacuity_condition="no reach limit and no bombing (length is free)", trivial_shortcuts="none",
    cheat_control="N/A", cost_class="CPU-scale", source_evidence="mars.py addressing modes", purpose="PURPOSE: same")

c.ancestry("algorithm_from", "ICWS '94 standard (docs/icws94.txt in the body); Dewdney 1984", note="docs/icws94.txt is in the tree; not read")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["opcodes after MOV (ADD..SPL) skimmed; SPL's dual enqueue and DJN's decrement-then-test are assumed per the standard", "the parser body unread", "nothing ran here (Techne: RUNNABLE_HISTORICAL_TOOLCHAIN, Python 2 -- __getslice__ in core.py)"],
          note="the world's rules are fully accounted for by five mechanisms; the organisms are out of scope")
c.save(state="COARSE")
