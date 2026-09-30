"""Cut: avida (Devosoft/Ofria digital-evolution platform, github master pinned 2026-09-12; ancestry-aware, Stage A COARSE; SOURCE_READ
on M3; seventh of the 2026-09-17 NOT_CUT order, cut after positions 8-10 because it is the largest body: 2,871 files).
Read (by function, not by file): cpu/cHardwareCPU.cc -- the default instruction table 73-150, ReadLabel 1484-1500, FindLabel 1177-1230,
SingleProcess 908-1000, Inst_HeadCopy 7130-7175, Inst_HeadSearch 7245-7256, Inst_IfLabel 6914-6920, Divide_Main 1775-1830;
cpu/cHardwareBase.cc -- Divide_CheckViable 140-232, Divide_DoMutations 296-360; main/cPopulation.cc -- AdjustSchedule 613-618,
ActivateOffspring 624-700, ActivateOrganism 1353-1400, PositionOffspring 5253-5400, BuildTimeSlicer, ScheduleOrganism/ProcessStep
5766-5800; main/cPhenotype.cc -- ResetMerit/DivideReset 805-860, CalcSizeMerit, CalcFitness 1827-1835; main/cEnvironment.cc --
reaction process types 170-176, DoProcesses 1610-1760; main/cTaskLib.cc -- AddTask 73-142; main/cBirthChamber.cc -- DoAsexBirth
226-260; main/cOrganism.cc -- age limit 220-232; main/cMutationRates.h (all); libs/apto/include/apto/scheduler/Integrated.h (all).
NOT read: ~40,000 of the ~60,000 core lines -- demes, predator/prey, mating types, tolerance, energy model, HGT, promoters,
resource bins, the four alternative hardwares (BCR, GP8, TransSMT, Experimental), analyze mode, AvidaScript, stats, the viewers.
Nothing ran (docker world; M3 has none).

SECOND PASS 2026-09-30 -- THE ANCESTRY CUT (operator directive 2026-09-18 s3: "Nyx cuts the save/population/ancestry mechanics
rather than the whole simulator"). Read IN FULL: systematics/GenotypeArbiter.cc (588 lines), systematics/Genotype.cc (554),
systematics/Group.cc, systematics/Manager.cc, systematics/Unit.cc, output/File.cc 98-256. Read by function: main/cPopulation.cc
SavePopulation 6362-6563, SaveStructuredSystematicsGroup 6566-6632, LoadPopulation 6820-7032 (+ sTmpGenotype::operator< 6752),
InjectGenome 7605-7626, Inject 7170-7198, ActivateOrganism 1353-1362, KillOrganism 2317-2318; actions/SaveLoadActions.cc 138-183;
actions/PopulationActions.cc 145-210; targets/avida/Avida2Driver.cc 91-162; main/cEventList.cc 56-76, 127-202, 426-459;
main/cBirthChamber.cc 135-313, 435-587 (the four modular variants 315-432 skimmed); main/cBirthEntry.cc 63-70, 119-124; main/cDeme.cc 950-993; core/Genome.cc 87-98, 125-132.
NOT read: SexualAncestry.cc, Clade.cc, CladeArbiter.cc, GenomeTestMetrics.cc, SaveFlameData, the analyze-mode lineage tools.
NO .spop FILE WAS OPENED: the body ships 177 of them and they are the sealed test domain of packet
MECH-AVIDA-ANCESTRY-RETENTION-001 (nyx/atlas/experiments/avida_ancestry/).
"""
from nyx.atlas.author import Cut

S = "vault:avida/upstream/tree/avida-core/source/"
CPU = S + "cpu/cHardwareCPU.cc"; BASE = S + "cpu/cHardwareBase.cc"; POP = S + "main/cPopulation.cc"; PHEN = S + "main/cPhenotype.cc"
ENV = S + "main/cEnvironment.cc"; TASK = S + "main/cTaskLib.cc"; BIRTH = S + "main/cBirthChamber.cc"; ORG = S + "main/cOrganism.cc"
MUT = S + "main/cMutationRates.h"; SCHED = "vault:avida/upstream/tree/libs/apto/include/apto/scheduler/Integrated.h"
GARB = S + "systematics/GenotypeArbiter.cc"; GENO = S + "systematics/Genotype.cc"; GRP = S + "systematics/Group.cc"; UNIT = S + "systematics/Unit.cc"
OFILE = S + "output/File.cc"; SLA = S + "actions/SaveLoadActions.cc"; PACT = S + "actions/PopulationActions.cc"; DRV = S + "targets/avida/Avida2Driver.cc"
EVL = S + "main/cEventList.cc"; BENT = S + "main/cBirthEntry.cc"; DEME = S + "main/cDeme.cc"; GNM = S + "core/Genome.cc"
c = Cut("avida", mode="ANCESTRY_AWARE",
        inspected=["cpu/cHardwareCPU.cc (instruction table, label search, single step, head-copy, head-search, if-label, divide main)", "cpu/cHardwareBase.cc (divide viability, divide mutations)",
                   "main/cPopulation.cc (scheduling, offspring activation/placement, process step)", "main/cPhenotype.cc (merit, fitness)", "main/cEnvironment.cc (reaction processing)", "main/cTaskLib.cc (task registry)",
                   "main/cBirthChamber.cc (asexual birth; birth-entry reference holds)", "main/cOrganism.cc (age limit)", "main/cMutationRates.h", "libs/apto scheduler/Integrated.h",
                   "systematics/GenotypeArbiter.cc (all)", "systematics/Genotype.cc (all)", "systematics/Group.cc (all)", "systematics/Unit.cc (all)", "systematics/Manager.cc (all)",
                   "output/File.cc (row and header writer)", "main/cPopulation.cc (SavePopulation, LoadPopulation, InjectGenome)", "actions/SaveLoadActions.cc (SavePopulation action)",
                   "actions/PopulationActions.cc (whole-genome-duplication injects)", "targets/avida/Avida2Driver.cc (the update loop)", "main/cEventList.cc (event order and triggers)",
                   "main/cBirthEntry.cc, main/cDeme.cc (the reference holders outside the arbiter)", "core/Genome.cc (equality, save columns)"],
        evidence=[("SOURCE_READ", CPU + ":73-150"), ("SOURCE_READ", CPU + ":908-1000"), ("SOURCE_READ", CPU + ":1177-1230"), ("SOURCE_READ", CPU + ":1484-1500"), ("SOURCE_READ", CPU + ":1775-1830"),
                  ("SOURCE_READ", CPU + ":6914-6920"), ("SOURCE_READ", CPU + ":7130-7175"), ("SOURCE_READ", CPU + ":7245-7256"), ("SOURCE_READ", BASE + ":140-232"), ("SOURCE_READ", BASE + ":296-360"),
                  ("SOURCE_READ", POP + ":613-700"), ("SOURCE_READ", POP + ":1353-1400"), ("SOURCE_READ", POP + ":5253-5400"), ("SOURCE_READ", POP + ":5766-5800"), ("SOURCE_READ", PHEN + ":805-860"),
                  ("SOURCE_READ", PHEN + ":1827-1835"), ("SOURCE_READ", ENV + ":170-176"), ("SOURCE_READ", ENV + ":1610-1760"), ("SOURCE_READ", TASK + ":73-142"), ("SOURCE_READ", BIRTH + ":226-260"),
                  ("SOURCE_READ", ORG + ":220-232"), ("SOURCE_READ", MUT), ("SOURCE_READ", SCHED),
                  ("SOURCE_READ", GARB + ":39-63"), ("SOURCE_READ", GARB + ":85-103"), ("SOURCE_READ", GARB + ":123-138"), ("SOURCE_READ", GARB + ":278-369"), ("SOURCE_READ", GARB + ":372-410"),
                  ("SOURCE_READ", GARB + ":498-559"), ("SOURCE_READ", GENO + ":128-184"), ("SOURCE_READ", GENO + ":187-263"), ("SOURCE_READ", GENO + ":282-299"), ("SOURCE_READ", GENO + ":321-331"),
                  ("SOURCE_READ", GENO + ":356-402"), ("SOURCE_READ", GENO + ":406-478"), ("SOURCE_READ", GRP + ":46-49"), ("SOURCE_READ", UNIT + ":60-126"), ("SOURCE_READ", OFILE + ":183-252"),
                  ("SOURCE_READ", POP + ":6362-6563"), ("SOURCE_READ", POP + ":6820-7032"), ("SOURCE_READ", POP + ":7605-7626"), ("SOURCE_READ", SLA + ":138-183"), ("SOURCE_READ", PACT + ":145-210"),
                  ("SOURCE_READ", DRV + ":91-162"), ("SOURCE_READ", EVL + ":56-76"), ("SOURCE_READ", EVL + ":152-202"), ("SOURCE_READ", BIRTH + ":135-175"), ("SOURCE_READ", BIRTH + ":178-224"), ("SOURCE_READ", BIRTH + ":264-313"), ("SOURCE_READ", BIRTH + ":435-587"), ("SOURCE_READ", BENT + ":63-70"),
                  ("SOURCE_READ", DEME + ":950-993"), ("SOURCE_READ", GNM + ":87-132")],
        note="the famous name (Avida, digital evolution) covers a small closed loop: a virtual CPU whose programs copy themselves with per-instruction copy errors; a divide that is refused unless the copy "
             "is plausible; a merit that is genome size times a task bonus; a scheduler that hands out CPU cycles in proportion to merit; a placement rule that kills whoever occupies the chosen cell; "
             "and an environment that scores logic functions on the organism's own I/O. Everything else in 60k lines is a configuration-gated extension of one of those")

iset = c.organ("nop_modified_instruction_set_where_three_nops_double_as_register_selectors_and_label_alphabet", human_name="nop-A/B/C; the tInstLibEntry table; ReadLabel (cHardwareCPU.cc 73-150, 1484-1500)", status="ACCEPTED",
    mechanism="every instruction is a fixed-size opcode from a table; nop-A/B/C do nothing when executed but MODIFY the instruction before them (which register ?BX? means) and, in sequence, spell a LABEL that other instructions read by scanning the following nops (ReadLabel); "
              "so the same three symbols are the argument system and the addressing system, and every mutation lands on a legal instruction",
    input="the genome as a sequence of opcodes", output="register choice and labels", state="none (read at execution)", update="per instruction",
    assumptions=["a closed alphabet where every string is a valid program (no syntax errors) is what makes random mutation productive rather than fatal"],
    fitness_value_in_ancestor="mutational robustness by construction; labels give position-independent addressing so insertions and deletions do not break jumps", failure_landscape="by reading: a mutation inside a label changes what it matches, silently; the record's tasks are typically evolved with only 26 of the ~200 table entries enabled (the instruction set is a config file)",
    human_prior="Ray's Tierra (1991) introduced nop-templates; Avida's three-nop alphabet and register modification are Ofria/Brown/Adami's redesign", evidence_ref=CPU + ":73-150, 1484-1500", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="the s_n_array / s_f_array tables and ReadLabel",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "representation_sensitivity": "INVARIANT", "failure_mode": "NONE_KNOWN"})

tmpl = c.organ("template_matching_by_complement_label_for_control_flow_and_for_finding_the_copy_loop", human_name="Inst_HeadSearch / Inst_IfLabel / FindLabel (7245-7256, 6914-6920, 1177-1230)", status="ACCEPTED",
    mechanism="h-search reads the nop label that follows it, takes its COMPLEMENT (Rotate by 1 over the three nops: A->B, B->C, C->A) and searches the genome forward from the start for that complement, leaving the FLOW head after the match and the distance in BX; "
              "if-label compares the complement of the label just read with the label most recently copied, so a program can detect that it has finished copying its own end marker; a search that finds nothing leaves the head where it was",
    input="a label read from the genome; the genome", output="a head position; a skip decision", state="the flow head; the read label", update="per h-search / if-label",
    assumptions=["complement matching means a program never matches its own search template accidentally; the default ancestor uses nop-A nop-B ... nop-C nop-A as the copy-loop markers"],
    fitness_value_in_ancestor="the self-copy loop terminates by recognising its own end label rather than by counting; loops survive length changes", failure_landscape="UNKNOWN by run",
    human_prior="Tierra's template addressing; the complement rule is Avida's", evidence_ref=CPU + ":1177-1230, 6914-6920, 7245-7256", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="FindLabel*, Inst_HeadSearch, Inst_IfLabel",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SCALAR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "representation_sensitivity": "SENSITIVE"})

copy = c.organ("head_based_self_copy_with_per_instruction_copy_error_insertion_deletion_and_slip", human_name="Inst_HeadCopy (7130-7175); the copy-time rates in cMutationRates", status="ACCEPTED",
    mechanism="h-copy reads the instruction under the READ head, and with probability copy_mut_prob replaces it with a random instruction from the set before writing it under the WRITE head (flagging the site); "
              "then, each with its own probability, inserts a random instruction, deletes one, applies a uniform mutation, or SLIPS (jumps the read head or duplicates/deletes a stretch); both heads advance; the parent program itself decides when and where to copy",
    input="the genome under the read head; the mutation rates", output="one instruction written (possibly wrong) under the write head", state="the read and write heads; per-site flags (copied, mutated)", update="per h-copy executed",
    assumptions=["mutation is an error in the organism's OWN copying act, so an organism that copies less (or copies fewer sites) exposes itself to fewer errors -- the rate is per copied instruction, not per generation"],
    fitness_value_in_ancestor="variation is produced by the same machinery selection acts on; slip mutations give whole-block duplications (the source of length change)", failure_landscape="by reading: an organism can evolve to skip copying part of itself (checked by the divide gate below)",
    human_prior="copy-time error as THE mutation source (Tierra); Avida adds divide-time and inject-time classes", evidence_ref=CPU + ":7130-7175; " + MUT, confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="Inst_HeadCopy and the copy-time TestCopy* probes",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_EPISODE", "stochasticity": "SEEDED_RANDOM", "update_topology": "SINGLE_STEP", "adaptation": "STRUCTURE"})

div = c.organ("divide_refused_unless_the_offspring_is_plausible_by_age_size_range_executed_fraction_and_copied_fraction", human_name="cHardwareBase::Divide_CheckViable (140-232); Divide_Main (1775-1830)", status="ACCEPTED",
    mechanism="a divide instruction succeeds only if: the parent has executed at least JUV_PERIOD and MIN_CYCLES instructions; both halves are within OFFSPRING_SIZE_RANGE of the genome length and within absolute bounds; the parent executed at least MIN_EXE_LINES fraction of its length; "
              "the offspring has at least MIN_COPIED_LINES fraction of its sites actually written by h-copy; optionally the offspring must be an exact copy (REQUIRE_EXACT_COPY); then the memory is cropped at the divide point, divide-time mutations are applied, and the parent is reset",
    input="the parent memory, the divide point, the execution/copy flags", output="an offspring genome or a fault (divide fails, parent continues)", state="per-site executed/copied flags", update="per divide attempt",
    assumptions=["a program that divides without copying (or after copying junk) is a cheat the world must refuse, or replication collapses to trivial short genomes"],
    fitness_value_in_ancestor="closes the shortcut of 'divide immediately'; the fractions are the world's minimum notion of a real copy", failure_landscape="UNKNOWN by run; by reading: the thresholds are constants, so an organism can sit exactly at MIN_COPIED_LINES",
    human_prior="the size-range and copied-fraction gates are Avida-specific anti-cheat rules (not in Tierra)", evidence_ref=BASE + ":140-232; " + CPU + ":1775-1830", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="Divide_CheckViable + Divide_Main",
    coverage={"input_topology": "SEQUENCE", "output_topology": "DECISION", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "DETERMINISTIC", "failure_mode": "NONE_KNOWN"})

dmut = c.organ("divide_time_mutation_spectrum_per_site_binomial_or_per_divide_or_poisson", human_name="cHardwareBase::Divide_DoMutations (296-360); cMutationRates.h", status="ACCEPTED",
    mechanism="after a successful divide the offspring genome receives, independently: slip, transposition, lateral-gene-transfer, point, insertion, deletion, uniform mutations, each drawn either per site (binomial over genome length, divided by a mut_multiplier), or at most once per divide, or Poisson with a constant genomic mean; "
              "parent mutations (applied to the parent's own memory) exist too; meta-mutation can perturb the copy-mutation rate itself",
    input="the offspring genome; the rate table", output="a mutated offspring", state="none", update="per divide", assumptions=["divide-time mutation decouples variation from the copy act (a different evolutionary regime from copy-time error, selectable by config)"],
    fitness_value_in_ancestor="experiments can hold the genomic mutation rate constant across genome lengths (the Poisson class) -- a control the copy-time class cannot offer", failure_landscape="UNKNOWN by run",
    human_prior="the per-site vs per-genome distinction is the experimenter's, encoded as three rate families", evidence_ref=BASE + ":296-360; " + MUT, confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="Divide_DoMutations and the divide-time rates",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "NONE", "stochasticity": "SEEDED_RANDOM", "adaptation": "STRUCTURE"})

merit = c.organ("merit_as_size_base_times_accumulated_task_bonus_locked_in_at_divide_and_inherited", human_name="cPhenotype::DivideReset / CalcSizeMerit / CalcFitness; cBirthChamber::DoAsexBirth (805-860, 1827-1835, 226-260)", status="ACCEPTED",
    mechanism="merit = base x bonus, where base is a size measure chosen by BASE_MERIT_METHOD (copied size, executed size, full length, least of them, sqrt of least, or a bonus-instruction count) and bonus starts at DEFAULT_BONUS and is modified by reactions during the organism's life; "
              "the product is locked in when the organism divides (DivideReset) and the offspring is born with the parent's merit (INHERIT_MERIT) or the bare size merit; fitness (for statistics, not for selection) is merit_base x bonus / gestation_time",
    input="size counts; the bonus from the environment; gestation time", output="merit (the scheduler's priority); fitness (a reported number)", state="cur_bonus, cur_merit_base, last_* copies", update="bonus per reaction; merit per divide",
    assumptions=["size in the base term compensates for the fact that a longer genome needs more cycles to copy: without it, the shortest replicator always wins", "merit is inherited so a lineage's rewards persist until its offspring earn their own"],
    fitness_value_in_ancestor="one scalar carries both 'how much work is a copy' and 'what has this program computed'; selection acts on the product", failure_landscape="by reading: with BASE_MERIT_FULL_SIZE an organism gains merit by growing junk; the LEAST_SIZE options exist because of that",
    human_prior="merit x bonus, and merit/gestation as fitness, are Avida's central design decisions (Ofria & Wilke 2004)", evidence_ref=PHEN + ":805-860, 1827-1835; " + BIRTH + ":226-260", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the merit fields of cPhenotype and their two writers",
    coverage={"input_topology": "MIXED", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "memory": "SUMMARY_STATISTIC", "stochasticity": "DETERMINISTIC", "adaptation": "PARAMETER"})

task = c.organ("task_reward_as_consumed_resource_times_value_composed_by_add_mult_pow_across_reactions", human_name="cEnvironment::DoProcesses (1610-1760); the reaction process types (170-176); cTaskLib::AddTask (73-142)", status="ACCEPTED",
    mechanism="when an organism's output matches a task on its inputs (the library: echo, add, sub, not, nand, and, orn, or, andn, nor, xor, equ, three-input logic 3AA-3AV, ...), each reaction process computes consumed = min(max, resource available x max_fraction) x task_quality, and bonus = consumed x value; "
              "the bonus is applied to the phenotype as ADD, MULT (bonus *= value), POW (bonus *= 2^value), LIN (value x task count), or into energy; resources may be depletable (a finite pool shared by the population) or unlimited (resource NULL: consumed = max x quality)",
    input="the organism's I/O history; the environment's reaction list; resource levels", output="a bonus change; resource consumption", state="resource counts; per-organism task counts", update="per output event",
    assumptions=["logic functions on 32-bit inputs are the world's notion of computation; the 'nand' primitive is the only logic instruction, so every other function must be built from it"],
    fitness_value_in_ancestor="the reward structure (multiplicative doubling by task complexity in the classic EQU experiments) is what makes complex functions evolve from simpler ones (Lenski et al. 2003)", failure_landscape="by reading: with unlimited resources the bonus is a pure function of the genome; with depletable resources it is frequency-dependent",
    human_prior="the logic-9 environment and its 2^n reward ladder are the experimenter's world design, not the organism's", evidence_ref=ENV + ":170-176, 1610-1760; " + TASK + ":73-142", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="DoProcesses and the task registry",
    coverage={"input_topology": "EVENT", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "resource_dependence": "SHARED_RESOURCE", "competition": "CONTENDS"})

sched = c.organ("cpu_time_allocated_in_proportion_to_merit_by_binary_decomposition_or_by_probability", human_name="Apto::Scheduler::Integrated / Probabilistic; cPopulation::AdjustSchedule, ScheduleOrganism, ProcessStep (613-618, 5766-5800)", status="ACCEPTED",
    mechanism="every cell's priority is its organism's merit (times a deme merit if any); the INTEGRATED scheduler decomposes each merit into powers of two and alternates 'the best' with 'everything else' recursively so that time slices are spread as evenly as possible while honouring the ratios; "
              "the PROBABILISTIC scheduler draws the next cell with probability proportional to merit; ROUND_ROBIN ignores merit; each schedule step executes ONE instruction of the chosen organism",
    input="merits; a clock of instruction slots", output="the next cell to execute", state="the priority chart / node tree", update="per instruction executed and per merit change",
    assumptions=["CPU cycles are the only currency; an organism's reproductive rate is its merit divided by the cycles a copy costs"], fitness_value_in_ancestor="selection is implemented as scheduling: nothing 'chooses' survivors, higher merit simply runs more often",
    failure_landscape="by reading: the integrated scheduler is deterministic given merits, so identical-merit populations execute in a fixed order (a hidden bias the probabilistic scheduler removes at the cost of variance)",
    human_prior="merit-proportional time slicing (Adami/Brown 1994) is the ecological law of the world; the binary-decomposition trick is an implementation choice", evidence_ref=SCHED + "; " + POP + ":613-618, 5766-5800", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="the scheduler classes and the three cPopulation methods",
    coverage={"input_topology": "VECTOR", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "PRIORITY", "resource_dependence": "COMPUTE", "competition": "CONTENDS"})

place = c.organ("offspring_placement_by_birth_method_that_kills_the_occupant_of_the_chosen_cell", human_name="cPopulation::PositionOffspring (5253-5400); ActivateOrganism (1353-1360)", status="ACCEPTED",
    mechanism="a newborn is assigned a cell by BIRTH_METHOD: a random cell in the whole population (optionally preferring empty cells), the ELDEST cell via a reaper queue, a random cell in the parent's deme, the cell the parent faces, a neighbourhood cell (handlers), or a migration target; "
              "population caps kill a random or the oldest organism first; then ActivateOrganism KILLS whatever occupies the target cell and inserts the newborn; death is therefore mostly replacement, not aging",
    input="the parent cell; config", output="a target cell (whose occupant dies)", state="the reaper queue; deme counters", update="per birth",
    assumptions=["space is the second finite resource; a full world means every birth is a death"], fitness_value_in_ancestor="the geometry of placement (well-mixed vs neighbourhood) is what makes spatial structure an experimental variable",
    failure_landscape="by reading: FULL_SOUP_RANDOM with a full world gives every organism the same expected lifetime regardless of merit, so selection acts only through birth rate", human_prior="the birth-method menu is the experimenter's; 'kill the occupant' is Tierra's reaper generalised",
    evidence_ref=POP + ":5253-5400, 1353-1360", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="PositionOffspring and the KillOrganism call in ActivateOrganism",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "SEEDED_RANDOM", "resource_dependence": "MEMORY", "competition": "CONTENDS", "failure_mode": "NONE_KNOWN"})

age = c.organ("age_limit_death_with_gaussian_deviation_optionally_scaled_by_genome_length", human_name="cOrganism.cc 220-232 (DEATH_METHOD, AGE_LIMIT, AGE_DEVIATION)", status="ACCEPTED",
    mechanism="if DEATH_METHOD is on, each organism draws at birth a maximum instruction count = AGE_LIMIT + N(0,1) x AGE_DEVIATION, optionally multiplied by genome length; an organism that executes more than that dies regardless of merit",
    input="config; a normal draw", output="a death time per organism", state="m_max_executed", update="once per organism", assumptions=["a lifetime cap prevents an immortal non-replicating high-merit organism from holding a cell forever"],
    fitness_value_in_ancestor="the only death that is not replacement; off by default", failure_landscape="UNKNOWN by run", evidence_ref=ORG + ":220-232", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the DEATH_METHOD block in cOrganism's constructor",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PER_EPISODE", "stochasticity": "SEEDED_RANDOM", "temporal_horizon": "EPISODE"})

# ---------------------------------------------------------------------------------------------------------------------------------------
# THE ANCESTRY CUT (2026-09-30). What Avida records of descent, what it keeps, what it writes, what it reads back.
found = c.organ("genotype_as_exact_genome_class_whose_parent_edge_is_written_once_at_founding_and_never_for_breed_true_or_live_convergent_births",
    human_name="Genotype::ClassifyNewUnit (Genotype.cc 282-299); GenotypeArbiter::ClassifyNewUnit (GenotypeArbiter.cc 278-369); the founder constructor (Genotype.cc 128-184); Matches (406-456)", status="ACCEPTED",
    mechanism="a newborn is offered to its parent's genotype. Same genome: it joins that genotype and NOTHING is recorded but a count (breed true). Different genome: the arbiter searches the hash of LIVING genotypes for an identical genome "
              "(same hardware type, instruction set and transmission class); if one exists the newborn joins it and who bore it is not recorded. Only if none exists is a new genotype founded: id = a counter that only increments, parents = the parental "
              "genotype(s), depth = first parent's depth + 1, update_born = the arbiter's clock. That founding is the ONLY moment a parent edge is written. Because only living genotypes are searched, a genome that re-arises while its genotype lives "
              "is absorbed into it, while the same genome re-arising after that genotype died founds a second genotype with a new id",
    input="a newborn unit's genome and source; its parent's genotype(s)", output="the unit's genotype; at most one new record with one parent edge", state="a hash of living genotypes by genome; the next id; per-genotype counts",
    update="per birth and per inject (an injected unit is classified with no parents and founds a ROOT)",
    assumptions=["identity is exact genome equality, so descent is recorded between CLASSES of identical organisms, never between organisms", "a class is founded once; later arrivals by mutation from elsewhere are the same class"],
    fitness_value_in_ancestor="memory and bookkeeping scale with distinct genomes, not with births; the dominant genotype is one record however many organisms carry it",
    failure_landscape="by reading: the recorded tree is a tree of FIRST APPEARANCES. Convergent and back-mutation births leave no edge, so gene flow into an existing class is invisible; sequence is not a key across time (a revived genome gets a new id); "
                      "with DISABLE_GENOTYPE_CLASSIFICATION every genotype is founded parentless (GenotypeArbiter.cc 348-352)",
    human_prior="genotype-as-class bookkeeping as written by David M. Bryson, 2009-2011 (the file headers); whether other platforms keep an organism-level pedigree instead was not checked",
    evidence_ref=GENO + ":128-184, 282-299, 406-456; " + GARB + ":278-369", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the two ClassifyNewUnit methods, the founder constructor and Matches",
    coverage={"input_topology": "SEQUENCE", "output_topology": "TREE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "memory": "ARCHIVE", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN",
              "order_sensitivity": "SENSITIVE", "representation_sensitivity": "SENSITIVE"})

retain = c.organ("reference_counted_retention_that_keeps_living_genotypes_and_their_ancestors_and_drops_an_extinct_branch_the_moment_its_last_leaf_dies",
    human_name="GenotypeArbiter::removeGenotype (GenotypeArbiter.cc 498-533), AdjustGenotype (372-410), PerformUpdate (85-103); Genotype::RemoveUnit (Genotype.cc 321-331); Group reference counts (Group.cc 46-49)", status="ACCEPTED",
    mechanism="every genotype carries an ACTIVE count (its living units) and a PASSIVE count (the child genotypes that name it as parent). When the last unit dies the genotype is deactivated, stamped with update_deactivated and moved to a "
              "'historic' list. If nothing passive refers to it, each of its parents loses one passive reference and is examined in turn, recursively, and the genotype is unlinked for good. So at every instant memory holds exactly the living "
              "genotypes and the ancestors of the living; a lineage with no living descendant disappears when its last leaf does, not at the end of the run",
    input="unit deaths", output="the set of retained genotype records", state="two counters per genotype; the historic list", update="per death, recursively up the parent chain; a sweep at the end of every update",
    assumptions=["what will be asked of the record is the line of descent of what survives; extinct side branches are not worth their memory"],
    fitness_value_in_ancestor="a run of any length keeps memory proportional to the living population's ancestry, not to every genotype ever founded",
    failure_landscape="by reading: an event that replaces organisms with INJECTED copies severs the record entirely -- the injects are roots, the old tree loses its last units and is pruned to nothing, though every new organism is a physical descendant "
                      "of an old one (PopulationActions.cc 153-171). Two holders outside the arbiter break the invariant in opposite directions: a deme's founder/germline hold is PASSIVE (cDeme.cc 958, 985), so a dead leaf survives; a waiting sexual "
                      "birth entry's hold is ACTIVE (cBirthChamber.cc 159-161), so a genotype with no organism stays 'living', is on neither list, and is written by nobody",
    human_prior="UNKNOWN beyond this body; here the pruning is unconditional (no configuration switch keeps the full tree: DISABLE_GENOTYPE_CLASSIFICATION only removes more)",
    evidence_ref=GARB + ":85-103, 372-410, 498-533; " + GENO + ":321-331, 395-402; " + GRP + ":46-49", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="removeGenotype and its three callers",
    coverage={"input_topology": "EVENT", "output_topology": "TREE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "memory": "ARCHIVE", "stochasticity": "DETERMINISTIC", "update_topology": "RECURSIVE",
              "resource_dependence": "MEMORY", "recovery": "NONE"})

save = c.organ("structured_population_save_one_row_per_genotype_living_rows_with_their_cells_then_every_historic_row",
    human_name="cPopulation::SavePopulation (cPopulation.cc 6362-6563); Genotype::LegacySave (Genotype.cc 356-392); GenotypeArbiter::LegacySave (123-131); Output::File (File.cc 183-252); the SavePopulation action (SaveLoadActions.cc 138-183)", status="ACCEPTED",
    mechanism="walks the cells, groups living organisms by genotype, and writes one line per living genotype: id, source, source arguments, parent id(s), living units, total units ever, length, mean merit / gestation / fitness, generation and update "
              "born, update deactivated, depth, hardware type, instruction set, sequence -- then the cells it occupies and per-organism offsets. Then, unless save_historic=0 (the default is 1), one line for every genotype on the historic list: the "
              "same first seventeen columns and nothing else. The header's #format line is taken from the first row written",
    input="the cell array; the arbiter's historic list", output="a text file, one genotype per line", state="none", update="per SavePopulation event",
    assumptions=["a population is restorable from genotypes plus cell lists; organisms of one genotype are interchangeable except for position and gestation offset"],
    fitness_value_in_ancestor="the save is at once a checkpoint and the run's phylogeny (the line of descent of every survivor, with sequences)",
    failure_landscape="by reading: fields are separated by single spaces and src_args is written raw, so a source argument containing spaces ('whole-genome duplication', PopulationActions.cc 169) shifts every later column of that row; "
                      "a living genotype with no organism in a cell (held only by a birth entry) is written nowhere; with save_historic=0 parent ids point at rows that are not in the file; rows are NOT in ancestral order (living rows in hash-map order, 6466, then the historic list), so a parent's row may follow its child's; the #format line names the twenty columns of a living row while historic rows carry seventeen",
    human_prior="the .spop (Structured POPulation) format; its columns are the experimenter's notion of what a genotype is",
    evidence_ref=POP + ":6362-6563; " + GENO + ":356-392; " + GARB + ":123-131; " + OFILE + ":183-252; " + SLA + ":138-183; " + GNM + ":125-132", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="SavePopulation and the three LegacySave methods",
    coverage={"input_topology": "TREE", "output_topology": "SEQUENCE", "state_amount": "NONE", "state_persistence": "DURABLE", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "failure_mode": "CORRUPTS"})

load = c.organ("population_load_that_renumbers_genotypes_and_silently_drops_every_parent_not_present_in_the_file",
    human_name="cPopulation::LoadPopulation (cPopulation.cc 6820-7032); the load constructor (Genotype.cc 187-263); GenotypeArbiter::LegacyLoad (133-138) and the id-hint path of ClassifyNewUnit (290-332)", status="ACCEPTED",
    mechanism="reads every row, sorts them by id, and re-creates the genotypes oldest first with FRESH ids from the arbiter's counter; each row's parent list is rewritten to the new ids of parents already re-created, and a parent id that names "
              "no row in the file is dropped without a message (the warning is commented out, 6996). Then num_units organisms are injected per row with an id hint, which makes the arbiter reactivate that genotype instead of founding one",
    input="a .spop (or older .pop) file", output="a population and an arbiter state", state="the id map old -> new", update="per LoadPopulation event",
    assumptions=["a file saved with historic rows reloads its whole line of descent; one saved without them reloads as unrelated roots, and that is acceptable"],
    fitness_value_in_ancestor="runs can be resumed and populations transplanted between experiments", failure_landscape="by reading: a save_historic=0 file loads with every living genotype whose parent is extinct turned into a ROOT that keeps its old depth "
    "(depth is read from the file, the parent is gone); ids are not stable across a save/load; the loaded organisms' source argument becomes the file name (6858-6861)",
    human_prior="checkpoint/restart; the silent degradation of ancestry on load is an implementation choice, not a documented one",
    evidence_ref=POP + ":6820-7032; " + GENO + ":187-263; " + GARB + ":133-138, 290-332", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="LoadPopulation's parent-fix loop (6968-6995, after the sort at 6960-6962) and the hinted classification",
    coverage={"input_topology": "SEQUENCE", "output_topology": "TREE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "DETERMINISTIC", "failure_mode": "DEGRADES", "recovery": "NONE"})

clock = c.organ("arbiter_clock_that_stamps_founding_with_the_update_after_the_last_completed_one_so_minus_one_covers_update_zero_and_zero_never_occurs",
    human_name="m_cur_update (GenotypeArbiter.cc 49, 87); the driver loop (Avida2Driver.cc 91-162); event triggers (cEventList.cc 127-202)", status="ACCEPTED",
    mechanism="the arbiter's clock starts at -1 and is set to (update just completed + 1) at the END of each update; the driver fires the events for update T after update T has been processed and before the counter advances. So a genotype founded "
              "before the run or during update 0 is stamped -1; one founded while update u >= 1 runs is stamped u; one founded by an event scheduled at update T is stamped T+1; and no genotype is ever stamped 0",
    input="the driver's update counter", output="update_born / update_deactivated stamps", state="one integer", update="once per update",
    assumptions=["the stamp is for statistics (age = current update - update born), where an off-by-one at the origin is harmless"],
    fitness_value_in_ancestor="a time base for genotype age", failure_landscape="by reading: a reconstruction that orders genotypes by update_born cannot separate 'before the run' from 'during update 0', and sees an event-injected genotype as one update "
    "younger than a genotype founded in the update the event fired after; update_deactivated = -1 means 'alive' and also 'died during update 0'",
    human_prior="UNKNOWN", evidence_ref=GARB + ":39-63, 85-103; " + DRV + ":91-162; " + EVL + ":152-202", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="m_cur_update and its one writer",
    coverage={"input_topology": "EVENT", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "temporal_horizon": "STEP"})

coal = c.organ("coalescent_genotype_as_the_oldest_living_or_branching_genotype_on_the_first_parent_line_of_the_most_abundant_genotype",
    human_name="GenotypeArbiter::updateCoalescent (GenotypeArbiter.cc 535-559); provided as systematics.genotype.coalescent_depth (444)", status="ACCEPTED",
    mechanism="after each pruning step, walk from the most abundant genotype up its FIRST parents to the root; the last genotype met that is alive or is named by more than one retained child is the coalescent, and its depth is published. "
              "Below it the retained tree is a single file of dead genotypes with one child each, so it is the most recent common ancestor of everything retained -- provided everything retained descends through that line",
    input="the retained tree", output="one genotype and its depth", state="the current coalescent", update="per pruned genotype, skipped while the current coalescent still qualifies (537)",
    assumptions=["asexual: only first parents are followed (the source says so, 545)", "one ancestor: with several injected roots the walk follows only the dominant's line"],
    fitness_value_in_ancestor="the depth of the population's common ancestor, read without a tree traversal at analysis time", failure_landscape="by reading: with two retained roots the 'coalescent' is the common ancestor of one root's descendants only",
    human_prior="coalescence depth as a run statistic (Avida's 'coalescent depth')", evidence_ref=GARB + ":535-559", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="updateCoalescent",
    coverage={"input_topology": "TREE", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "SWEEP", "hidden_state": "ASSUMES"})

recomb = c.organ("two_parent_recombination_by_swapping_one_region_located_as_the_same_fractions_of_each_genome_with_the_majority_parent_recorded_first",
    human_name="cBirthChamber::SubmitOffspring sexual branch (cBirthChamber.cc 443-587); DoBasicRecombination (286-313); RegionSwap / GenomeSwap (178-224); DoPairAsexBirth (264-282); SetupGenotypeInfo (435-441)", status="ACCEPTED",
    mechanism="an offspring from a sexual divide waits in the birth chamber until a second one arrives. Then two random fractions of genome length are drawn, the region between them is cut out of BOTH genomes at the same fractions (so unequal lengths are "
              "allowed and the pieces may differ in size) and exchanged; merit is blended by the exchanged fraction; if more than half was exchanged the two results swap labels, so each child is named after the parent it took the MAJORITY from. "
              "Two children are built (or one, chosen by coin, under a two-fold cost), and each is classified with BOTH parents' genotypes, its majority parent first -- which is therefore the parent its depth is counted from. "
              "With MODULE_NUM > 0 the cut points are module boundaries, contiguous, independent per module, or shuffled between modules",
    input="two offspring genomes and their parents' genotypes and merits; two uniform draws", output="two (or one) recombinant genomes, each with an ordered pair of parent genotypes", state="the waiting entries", update="per sexual divide that finds a waiting entry",
    assumptions=["homology is positional and proportional: the same FRACTION of two genomes is treated as the same place", "one exchanged region is enough; the operator is symmetric in the two parents"],
    fitness_value_in_ancestor="recombination between programs of different lengths without alignment; the modular variants test whether exchange at module boundaries preserves function",
    failure_landscape="by reading: the OPERATOR LEAVES NO RECORD -- the two fractions, the module choices and whether the labels were swapped are drawn, used and discarded; the save keeps only the two parent ids. A swap refused for illegal "
                      "length (RegionSwap 192-196) still blends merit and still records two parents for a child that is genetically one parent's. A child identical to its first parent's genotype, or to any living genotype, is absorbed and "
                      "records no parents at all. When recombination is skipped (RECOMBINATION_PROB, or zero cross points) the pair is born as two single-parent children (DoPairAsexBirth). Under ENERGY_ENABLED with a two-fold cost, line 576 "
                      "reads child_array[1] of a one-element array",
    human_prior="two-point crossover (the GA operator), located by fraction rather than by index so that variable-length programs can be crossed; the modular variants are Avida's (Misevic, Ofria, Lenski on sex and modularity, recalled not checked)",
    evidence_ref=BIRTH + ":178-224, 264-313, 435-441, 443-587", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="DoBasicRecombination + RegionSwap + the two SetupGenotypeInfo calls at 553-554",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_CALL", "stochasticity": "SEEDED_RANDOM", "update_topology": "EVENT_DRIVEN", "order_sensitivity": "PARTIALLY",
              "adaptation": "STRUCTURE", "cooperation": "SHARES"})

c.reject("SexualAncestry.cc (162 lines), Clade.cc / CladeArbiter.cc (464 lines), GenomeTestMetrics.cc", reason="OTHER", evidence="NOT READ this pass; a second arbiter role and per-genotype attached data", note="the clade arbiter is a parallel classification under another role id; the ancestry cut is of the 'genotype' role only")
c.reject("SaveFlameData (cPopulation.cc 6667-) and SaveStructuredSystematicsGroup (6566-6632)", reason="OTHER", evidence=POP + ":6566-6632 read; SaveFlameData not read beyond its header", note="the group save is SavePopulation without the organism columns; flame data is a different file that shares the .spop extension and is out of the packet's scope by its missing #filetype line")
c.reject("threshold status and genotype names (nameGenotype 482-496; SetThreshold)", reason="BELOW_MEANINGFUL_GRAIN", evidence=GARB + ":482-496", note="labels for genotypes that reached an abundance; nothing reads them back into the dynamics")
c.reject("'the phylogeny' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="what is called the phylogeny is four separable acts with separate code: founding an edge, retaining by reference count, writing rows, and reading them back with renumbering; each loses different information")

c.reject("demes and deme competition, predator/prey, mating types and sexual birth handlers, tolerance/groups, the energy model, HGT genome fragments, promoters/regulation, resource bins, avatars, multi-process worlds", reason="OTHER", evidence="NOT READ (configuration-gated extensions, ~30,000 lines); residue, not rejected on the merits", note="each is a separate experimental world built on the core loop; a second pass should treat them as separate specimens")
c.reject("cHardwareBCR / GP8 / TransSMT / Experimental hardware variants", reason="OTHER", evidence="NOT READ; alternative CPUs sharing cHardwareBase's divide gates and mutation code", note="the shared base (read) is the anatomy; the variants are alternative instruction semantics")
c.reject("analyze mode (cAnalyze), AvidaScript, cStats, the viewers (macOS app, CorePlot), the speculative-execution cache (ProcessStepSpeculative: up to 32 instructions run ahead)", reason="OTHER", evidence="instruments, tooling and a performance optimisation; the speculative cache changes no semantics by design", note="instruments")
c.reject("'digital evolution' / 'Avida' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the loop is ten separable mechanisms with independent config switches; the platform's own literature varies each independently")
c.reject("the ~200-entry instruction table beyond the nop/copy/divide/search/if-label core", reason="BELOW_MEANINGFUL_GRAIN", evidence=CPU + ":73-150 and onward; arithmetic, stack, I/O and sensing instructions are the organism's alphabet, not mechanisms of the world", note="the alphabet is data for a world; the mechanisms above are what act on it")

c.edge(iset, tmpl, "feeds"); c.edge(tmpl, copy, "feeds", note="h-search places the flow head; the copy loop jumps to it"); c.edge(copy, div, "feeds"); c.edge(div, dmut, "triggers"); c.edge(div, merit, "triggers", note="DivideReset locks merit in")
c.edge(task, merit, "updates", note="bonus"); c.edge(merit, sched, "feeds", note="priority = merit"); c.edge(sched, copy, "feeds", note="CPU cycles"); c.edge(sched, task, "feeds", note="cycles to compute"); c.edge(div, place, "triggers"); c.edge(place, sched, "updates", note="new cell priority; killed cell removed")
c.edge(age, place, "competes", note="the two deaths"); c.edge(merit, div, "feeds", note="offspring inherits merit via the birth chamber"); c.edge(dmut, iset, "updates", note="every mutant is a legal program")
# the ancestry cut's edges: birth writes an edge (sometimes), death prunes, the save writes what is left, the load reads it back with loss
c.edge(div, found, "triggers", note="every successful divide classifies the newborn (cBirthChamber.cc 257-259)"); c.edge(dmut, found, "feeds", note="a mutated offspring is what founds a genotype")
c.edge(place, retain, "triggers", note="the occupant of the chosen cell dies; its unit is removed (Unit.cc 60-65)"); c.edge(found, retain, "stores", note="a founding adds one passive reference to each parent (Genotype.cc 160)")
c.edge(retain, save, "feeds", note="the historic list is written as is"); c.edge(found, save, "feeds", note="parents, depth and the stamp are written as founded"); c.edge(save, load, "feeds")
c.edge(load, found, "restores", note="loaded genotypes are reactivated by id hint, not re-founded"); c.edge(clock, found, "feeds", note="update_born"); c.edge(clock, retain, "feeds", note="update_deactivated")
c.edge(recomb, found, "feeds", note="each recombinant is classified with both parents, majority parent first (553-554)"); c.edge(div, recomb, "triggers", note="only when the dividing organism's phenotype says DivideSex (448)")
c.edge(retain, coal, "triggers", note="recomputed at each pruning step"); c.edge(retain, found, "forgets", note="a pruned genotype's genome, re-arising, founds a new id")

c.pressure("a_program_must_copy_its_own_description_under_a_per_symbol_error_rate_while_cpu_time_is_rationed_by_a_score_it_can_raise_by_computing",
    condition="the world executes many programs a few instructions at a time; a program persists only by producing a copy of itself that passes a plausibility gate; each copied symbol is corrupted with a fixed probability; the share of execution a lineage receives is proportional to a score that starts at its length and multiplies when its inputs and outputs satisfy functions the world names",
    resource_or_constraint="instruction slots per world step; cells (a copy needs an empty or killed cell); a mutation rate per copied symbol", failure_condition="no lineage replicates within the run (the ancestor is lost), or the population collapses to minimal replicators that compute nothing",
    world_punishes="long genomes (more to copy per cycle) and computation that does not pay in score; slow copiers under replacement death", world_rewards="lineages whose copy is fast and accurate enough AND whose extra instructions earn multiplicative score",
    observable_consequence="fraction of runs in which any named function appears by generation G; genome length and per-site mutation load over time; time to the highest-value function as the reward ladder's base (ADD vs MULT vs POW) is varied",
    vacuity_condition="no copy error (nothing varies), or unlimited CPU and space (no competition), or a score independent of computation", trivial_shortcuts="a program that divides without copying (closed by the copied-fraction gate); a world that rewards length alone",
    cheat_control="an organism handed the full score directly (bonus injected) must dominate the population within a few generations without computing anything -- if it does not, the scheduler is not reading merit; a non-replicating organism must vanish within one replacement cycle -- if it persists, death is not replacement",
    cost_class="CPU-scale", source_evidence="record human_capability_summary; cHardwareCPU Inst_HeadCopy; cHardwareBase Divide_CheckViable; cPhenotype DivideReset; Apto Integrated scheduler; cPopulation PositionOffspring", purpose="PURPOSE: experimental digital evolution (Adami, Ofria, Brown; Avida 1993-)")

c.pressure("a_reward_ladder_composed_multiplicatively_across_functions_decides_whether_complex_functions_are_reachable_from_simple_ones",
    condition="the world names a set of functions with values; an organism's score is the composition (add, multiply, or 2^value) of the rewards of every function it performs; complex functions are built from simpler ones the same programs already perform",
    resource_or_constraint="the score is the only lever on CPU share; the functions cost instructions to perform", failure_condition="the most complex function never appears because its stepping stones are not rewarded, or because rewards for stepping stones saturate",
    world_punishes="a ladder whose intermediate rungs pay nothing", world_rewards="a ladder whose rungs compound", observable_consequence="appearance rate of the top function across reward compositions (Lenski et al. 2003 shape: EQU evolves only when simpler functions are rewarded)",
    vacuity_condition="one function, or additive rewards so small that score is dominated by length", trivial_shortcuts="rewarding the top function directly at a value that dwarfs length",
    cheat_control="a world rewarding only the top function must show it evolving rarely or never; the same world with the compounding ladder must show it often: if the difference is not visible, the ladder is not the operative pressure",
    cost_class="CPU-scale", source_evidence="cEnvironment DoProcesses 1729-1760 (ADD/MULT/POW); cTaskLib logic-9 registry", purpose="PURPOSE: evolution of complex features (Lenski, Ofria, Pennock, Adami 2003)")

c.pressure("finite_space_where_every_birth_is_a_death_and_the_victim_is_chosen_by_a_placement_rule_not_by_fitness",
    condition="N cells; a newborn takes a cell and its occupant dies; the cell is chosen at random (well-mixed), by age (eldest), or by neighbourhood (spatial); no organism dies for being unfit -- it dies because a neighbour reproduced",
    resource_or_constraint="cells", failure_condition="a lineage that reproduces slowly is replaced before it reproduces even when its score is high (score buys cycles, not immunity)", world_punishes="long gestation", world_rewards="short gestation relative to neighbours; in spatial worlds, local clustering",
    observable_consequence="lineage persistence vs gestation time under each placement rule; spatial correlation of genotypes under neighbourhood placement vs well-mixed", vacuity_condition="more cells than organisms (nobody is replaced)", trivial_shortcuts="a world that never fills",
    cheat_control="an organism given a cell that is excluded from placement must never die and must not spread: the world must show both, or placement is not the death mechanism",
    cost_class="CPU-scale", source_evidence="cPopulation PositionOffspring 5253-5400; ActivateOrganism 1353-1360", purpose="PURPOSE: population structure in digital evolution (Avida birth methods)")

c.pressure("a_line_of_descent_must_be_readable_at_the_end_from_memory_bounded_by_the_living_not_by_everything_that_ever_lived",
    condition="a population turns over thousands of times; nearly every lineage founded goes extinct; whoever reads the run afterwards wants to know how the survivors came to be; memory and the save file are finite",
    resource_or_constraint="one record per retained class of identical organisms; a run founds far more classes than it ever holds alive", failure_condition="memory grows with every class ever founded and the run dies, or a survivor's line of descent cannot be read back",
    world_punishes="keeping every record (unbounded growth); keeping none (no history)", world_rewards="keeping exactly the living classes and their ancestors, and forgetting an extinct branch as soon as its last member dies",
    observable_consequence="in a saved population, dead records that no record names as a parent: none under this rule, the large majority of dead records without it; retained records / records ever founded falls as the run lengthens",
    vacuity_condition="no extinction (nothing to forget) or no mutation (one class, no tree)", trivial_shortcuts="found every class parentless (DISABLE_GENOTYPE_CLASSIFICATION); write only the living (save_historic=0)",
    cheat_control="the same population run with forgetting switched off must show dead unnamed records in its save; if it shows none, the observable cannot see forgetting and a zero in the real save means nothing "
                  "(run on the reference model, nyx/atlas/experiments/avida_ancestry: 92 unnamed dead records of 131 with forgetting off, 0 of 23 with it on)",
    cost_class="memory-scale; the check on a saved file is milliseconds", source_evidence="GenotypeArbiter removeGenotype 498-533; Genotype founder constructor 153-177; cPopulation SavePopulation 6557-6560", purpose="PURPOSE: phylogeny and line-of-descent analysis of digital evolution runs")

c.ancestry("algorithm_from", "Tierra (Ray 1991): self-replicating programs with template addressing and a reaper; Avida (Adami & Brown 1994) adds per-organism CPUs, merit-proportional scheduling, and the task-reward environment", note="from the code's structure and the record's lineage; not verified against the papers this pass")
c.residue("LARGE_RESIDUE", ["about two thirds of avida-core is unread: demes, predator/prey, mating, tolerance, energy, HGT, promoters, resource bins, alternative hardwares, analyze mode, script, stats, viewers",
                            "the default instruction set and default config (which of the ~200 instructions and which BIRTH/SLICING/BASE_MERIT settings are in force) live in config files not opened this pass; every 'default' claim above names the config key instead",
                            "nothing ran; the body is a docker world (Techne TECHNE_SMOKE_HARNESS_PASS) and cannot run on M3",
                            "ancestry pass 2026-09-30: sexual ancestry (SexualAncestry.cc), the clade arbiter, and parasite genotype bookkeeping are unread, so the ancestry organs are claimed for asexual, host-only, non-deme runs only",
                            "ancestry pass 2026-09-30: whether the 177 .spop files the body ships were written by THIS revision of the code is unknown; the packet tests exactly that"],
          note="the core replication-selection-reward loop is located function by function, and the genotype-ancestry subsystem is read whole; the platform's scale is why this is COARSE despite seventeen organs")
c.save(state="COARSE")
