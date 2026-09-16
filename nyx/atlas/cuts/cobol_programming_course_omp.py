"""Cut: cobol-programming-course-omp (ancestry-aware, Stage A COARSE; SOURCE_READ Course #2 Labs/cbl/CBL0006.cobol in full, SRCHBIN.cobol
(table and SEARCH ALL), PAYROL00.cobol (grepped for arithmetic); file census: 23 .cobol + 7 .cbl programs, 41 JCL, 219 images, 44 md).
The machinery here is the LANGUAGE's data semantics exercised by 30 small programs, not an algorithm."""
from nyx.atlas.author import Cut

S = "vault:cobol-programming-course-omp/upstream/tree/COBOL Programming Course #2 - Learning COBOL/Labs/cbl/"
c = Cut("cobol-programming-course-omp", mode="ANCESTRY_AWARE", inspected=["CBL0006.cobol", "SRCHBIN.cobol (data + SEARCH)", "PAYROL00.cobol (grep)", "file census"],
        evidence=[("SOURCE_READ", S + "CBL0006.cobol"), ("SOURCE_READ", S + "SRCHBIN.cobol")],
        note="a fossil of a LANGUAGE's computational stance: data described byte-exactly and declaratively, control flow by named paragraphs; the atlas records the mechanisms the programs exercise, each of which is executed by the compiler runtime rather than written in the program")

rl = c.organ("byte_exact_record_layout_declared_by_level_numbers_and_pictures", human_name="DATA DIVISION: 01/05/10 levels, PIC X(n) / 9(n) / S9(7)V99 COMP-3", status="ACCEPTED",
    human_interpretation="the shape of every record on disk and in memory is written in the program",
    mechanism="a hierarchy of level-numbered items with PICTURE clauses fixes the offset, length, encoding (display vs packed decimal COMP-3), sign and implied decimal point of every field; the same 150-byte input record is read into ACCT-FIELDS and its fields addressed by name; FILLER pads; VALUE initialises",
    input="a file record's bytes", output="named fields", state="the record areas", update="per READ / per MOVE", assumptions=["the file's bytes match the declared layout exactly (record: EBCDIC names appear untranslated under GnuCOBOL -- the layout is byte-faithful, the character set is not)"],
    fitness_value_in_ancestor="format longevity (record pressure): a 1970s file is readable today because its layout is in the program", evidence_ref=S + "CBL0006.cobol:18-44 (FD / 01 / 05 / 10 lines)", confidence="HIGH", portability="NO", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="FILE SECTION + WORKING-STORAGE of every program",
    coverage={"input_topology": "SEQUENCE", "output_topology": "VECTOR", "state_amount": "CONSTANT", "representation_sensitivity": "SENSITIVE", "state_persistence": "DURABLE"})

ed = c.organ("edited_move_formats_by_picture_at_assignment", human_name="MOVE ACCT-LIMIT TO ACCT-LIMIT-O where ACCT-LIMIT-O PIC $$,$$$,$$9.99", status="ACCEPTED",
    mechanism="a MOVE from a numeric packed field to an edited picture performs currency floating, comma insertion, zero suppression and decimal alignment by the picture alone; no formatting code exists in the program",
    input="a packed decimal", output="a 13-character edited string", state="none", update="per MOVE", evidence_ref=S + "CBL0006.cobol:24-27,157-159", confidence="HIGH", portability="NO", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="edited PICTUREs and the MOVEs into them",
    coverage={"input_topology": "SCALAR", "output_topology": "SEQUENCE", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

dec = c.organ("fixed_point_decimal_arithmetic_at_declared_scale", human_name="COMPUTE GROSS-PAY = HOURS * RATE on PIC S9(n)V99 (COMP-3)", status="ACCEPTED",
    mechanism="arithmetic on pictured fields is exact decimal at the declared scale; the result is truncated (or ROUNDED if asked) to the target picture's digits; overflow past the picture is silently truncated unless ON SIZE ERROR is written -- the record's failure condition ('a truncated or mis-edited amount')",
    input="pictured numerics", output="a pictured numeric", state="none", update="per statement", assumptions=["money is decimal; binary floating point is never used"],
    evidence_ref=S + "PAYROL00.cobol (COMPUTE GROSS-PAY = HOURS * RATE); CBL0006.cobol ADD 1 TO VIRGINIA-CLIENTS", confidence="HIGH", portability="NO", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="COMPUTE / ADD / MULTIPLY statements",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "failure_mode": "CORRUPTS", "uncertainty": "POINT"})

lp = c.organ("record_at_a_time_sequential_loop_with_an_at_end_flag", human_name="PERFORM READ-RECORD; PERFORM UNTIL LASTREC = 'Y' ... END-PERFORM", status="ACCEPTED",
    mechanism="prime the loop with one READ; loop until the AT END clause has set a flag; each iteration processes the record area in place (a conditional count, a formatted WRITE) and reads the next; headers before, totals after; files opened and closed explicitly",
    input="a sequential file", output="a report file", state="LASTREC flag, running counters", update="per record", evidence_ref=S + "CBL0006.cobol:106-165", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="PROCEDURE DIVISION of CBL0001..CBL0014",
    coverage={"input_topology": "STREAM", "output_topology": "STREAM", "state_amount": "CONSTANT", "update_topology": "SWEEP", "memory": "SUMMARY_STATISTIC"})

sr = c.organ("declared_ordered_table_searched_by_binary_or_linear_search_statement", human_name="OCCURS 45 TIMES ASCENDING KEY IS ACCT-NO INDEXED BY TABLE-IDX; SEARCH ALL vs SEARCH", status="ACCEPTED",
    mechanism="a table declared with an ordering key lets SEARCH ALL perform a binary search (the runtime's), WHEN naming the key comparison and AT END the miss; plain SEARCH is a linear scan from the index; the record pairs SRCHBIN and SRCHSER as the comparison",
    input="a loaded table, a key value", output="an index or 'Not Found'", state="TABLE-IDX", update="per search", assumptions=["the table IS sorted as declared (the runtime does not check)"],
    evidence_ref=S + "SRCHBIN.cobol (OCCURS ... ASCENDING KEY; SEARCH ALL block)", confidence="HIGH", portability="NO", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="SRCHBIN / SRCHSER",
    coverage={"input_topology": "VECTOR", "output_topology": "DECISION", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC"})

pf = c.organ("named_paragraph_control_flow_by_perform", human_name="PERFORM paragraph / PERFORM UNTIL / GOBACK", status="ACCEPTED",
    mechanism="the procedure is a flat sequence of named paragraphs; PERFORM calls one (or a range) and returns; PERFORM UNTIL loops; control otherwise falls through paragraphs in order; no local variables, no recursion, all state global in WORKING-STORAGE",
    input="none", output="none", state="none beyond the perform return", update="none", evidence_ref=S + "CBL0006.cobol:106-165", confidence="HIGH", portability="NO", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="every PROCEDURE DIVISION",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "NONE", "update_topology": "SWEEP"})

c.reject("JCL job streams (41 .jcl files)", reason="EFFECT_FROM_ENVIRONMENT", evidence="Labs/jcl/*.jcl -- bind DD names (ACCTREC, PRTLINE) to datasets and run the compiled program; Techne's recipe replaces them with DD_ environment variables", note="the file-name indirection (SELECT ... ASSIGN TO PRTLINE) is where the program meets the world; recorded here, not as an organ")
c.reject("course text, images, LaTeX, Zowe configuration", reason="OTHER", evidence="219 png, 44 md, 4 tex, zowe.*.json -- the course, not the machinery")
c.reject("'COBOL program' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the programs are near-identical exercises of the six mechanisms above; CBL0001..CBL0014 differ by one mechanism each")
c.reject("the 30 programs as 30 organs", reason="OTHER", evidence="by name and the record's entry-point list: headers, totals, conditionals, PERFORM, SEARCH, DB2 (CBLDB2x, unread), testing labs (DEPTPAY, EMPPAY, unread)", note="Course #3 DB2 labs and Course #4 testing labs unread -- UNKNOWN")

c.edge(rl, ed, "feeds"); c.edge(rl, dec, "feeds"); c.edge(lp, rl, "updates", note="READ fills the record area"); c.edge(lp, ed, "triggers", note="WRITE-RECORD"); c.edge(pf, lp, "schedules"); c.edge(rl, sr, "feeds"); c.edge(dec, ed, "feeds", note="totals formatted at the end")

c.pressure("data_formats_must_outlive_every_program_and_machine_that_touches_them",
    condition="files written decades ago must be readable byte-for-byte by programs written today; the layout is the contract and no schema exists outside the programs", resource_or_constraint="no runtime type information in the file",
    failure_condition="a misread field (record: mis-edited amount)", world_punishes="implicit layouts; encodings that change with the machine", world_rewards="the layout written in the program, byte-exact, with the encoding named per field",
    observable_consequence="the record's observation: packed-decimal amounts format correctly under GnuCOBOL while EBCDIC text does not -- the layout survived, the character set did not", vacuity_condition="short-lived data", trivial_shortcuts="a self-describing format (not available to the 1960s world)",
    cheat_control="a program given the layout as data (a copybook) must read the file; if the world rewards it equally to one that guesses the layout from the bytes, format longevity is not being measured", cost_class="CPU-scale", source_evidence="record pressure and example output", purpose="PURPOSE: business record processing")
c.pressure("money_arithmetic_must_be_exact_to_the_cent_and_auditable_on_paper",
    condition="every amount is a decimal with a fixed scale; rounding and truncation are legally specified; the output is a printed report that an auditor reads", resource_or_constraint="decimal exactness; fixed report columns",
    failure_condition="a cent of drift; a truncated total", world_punishes="binary floating point; silent overflow", world_rewards="declared-scale decimal arithmetic and edited output",
    observable_consequence="totals on the report vs a hand sum of the file", vacuity_condition="approximate quantities", trivial_shortcuts="integers in cents (correct; the world may allow it)",
    cheat_control="corrupt one COMP-3 field (the record's entry point): the report must show the corruption, not hide it", cost_class="CPU-scale", source_evidence="record failure condition; COMPUTE / edited pictures", purpose="PURPOSE: same")

c.residue("PARTIALLY_EXPLAINED", ["Course #3 DB2 labs (CBLDB21-23) and Course #4 testing labs (DEPTPAY, EMPPAY) unread", "the compiler runtime that executes every mechanism above is NOT in the body (GnuCOBOL is Techne's world)", "nothing ran here; Techne's CBL0001 receipt is on M1"],
          note="the six mechanisms are the language's; the fossil shows humans exercising them one at a time")
c.save(state="COARSE")
