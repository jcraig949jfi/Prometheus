"""Cut: sqlite-3.49.1-amalgamation (ancestry-aware, Stage A COARSE at SUBSYSTEM grain; SOURCE_READ the amalgamation's file map (Begin file
markers, 130 files), wherePathSolver head 169072-169110, function anchors for pager / wal / btree / vdbe; 261,454 lines). The largest
body in the sample; every organ below is a subsystem confirmed by its entry points, not a line-level cut. LogEst (log2 row estimates) is
the one representation choice read."""
from nyx.atlas.author import Cut

S = "vault:sqlite-3.49.1-amalgamation/upstream/tree/sqlite-amalgamation-3490100/sqlite3.c"
c = Cut("sqlite-3.49.1-amalgamation", mode="ANCESTRY_AWARE", inspected=["sqlite3.c file map (Begin file markers)", "wherePathSolver 169072-169110", "function anchors: sqlite3PagerCommitPhaseOne 63767, sqlite3WalFrames 69364, walCheckpoint 67320, balance_nonroot 78941, sqlite3VdbeExec 94350 (188 OP_ cases)"],
        evidence=[("SOURCE_READ", S)],
        note="a layered engine whose layers are the atlas organs at this grain: tokenizer+parser -> code generator -> planner -> bytecode VM -> b-tree -> pager/wal -> VFS; the cut is confident about the layer boundaries (they are the amalgamation's own file boundaries) and says nothing about the inside of any layer except the planner's beam search")

vm = c.organ("register_based_bytecode_virtual_machine_with_188_opcodes_executed_by_one_switch", human_name="vdbe.c sqlite3VdbeExec", status="ACCEPTED",
    mechanism="a prepared statement is an array of VdbeOp (opcode, three integer operands, an optional p4); sqlite3VdbeExec runs a for-loop over the program counter with a switch of 188 cases (OP_Column, OP_SeekGE, OP_Next, OP_Halt ...) over a register file of Mem cells and a set of b-tree cursors; jumps set pc; the statement yields rows by returning SQLITE_ROW at OP_ResultRow and resumes",
    input="a VdbeOp program, bound parameters", output="rows / side effects", state="registers (Mem[]), cursors, pc", update="per opcode", evidence_ref=S + ":93447-109531 (vdbe.c); 94350 sqlite3VdbeExec; 188 'case OP_' lines", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="vdbe.c + vdbeaux.c + vdbemem.c",
    coverage={"input_topology": "SEQUENCE", "output_topology": "STREAM", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SINGLE_STEP"})

bt = c.organ("b_tree_of_fixed_size_pages_with_overflow_chains_and_sibling_balancing", human_name="btree.c: sqlite3BtreeTableMoveto / sqlite3BtreeInsert / balance_nonroot / moveToChild", status="ACCEPTED",
    mechanism="two page kinds (table b+tree keyed by rowid with payload in leaves; index b-tree keyed by record); descend by binary search per page (moveToChild); insert into a leaf, then balance across up to three siblings redistributing cells (balance_nonroot) and splitting/merging as needed; large payloads spill to overflow page chains; freelist of pages",
    input="cursor operations", output="pages modified through the pager", state="pages; cursor stacks", update="per operation", evidence_ref=S + ":70781-93446 (btree.c); 76181, 76508, 78941, 80100", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="btree.c + btmutex.c",
    coverage={"input_topology": "SEQUENCE", "output_topology": "TREE", "state_amount": "LINEAR_IN_INPUT", "update_topology": "RECURSIVE"})

pg = c.organ("pager_with_rollback_journal_of_original_pages_synced_before_the_database_is_written", human_name="pager.c: sqlite3PagerCommitPhaseOne / syncJournal / pager_write_pagelist", status="ACCEPTED",
    mechanism="before a page is first modified in a transaction its ORIGINAL content is appended to a journal file; commit phase one syncs the journal, then writes the dirty pages to the database file and syncs; phase two deletes/truncates the journal (the commit point); recovery replays a hot journal to restore the originals -- the inverse discipline of LMDB's copy-on-write: overwrite in place, keep the old bytes elsewhere",
    input="page reads/writes", output="a durable page file", state="the page cache (pcache), the journal, lock state", update="per transaction", assumptions=["fsync orders journal before database"],
    fitness_value_in_ancestor="ACID with one file plus a transient journal (the 2000-2010 design)", evidence_ref=S + ":57171-65132 (pager.c); 61589, 61732, 63767", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="pager.c + pcache.c",
    coverage={"input_topology": "EVENT", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "DURABLE", "recovery": "ROLLS_BACK"})

wl = c.organ("write_ahead_log_of_new_pages_with_a_shared_memory_hash_index_and_periodic_checkpoint", human_name="wal.c: sqlite3WalFrames / walIndexAppend / walCheckpoint", status="ACCEPTED",
    mechanism="in WAL mode modified pages are appended as frames to a -wal file (the database is untouched); a -shm memory-mapped hash index maps page numbers to the newest frame so readers find current pages without scanning; readers pin a 'mark' (the WAL end they see) and never block the writer; a checkpoint copies frames back into the database when no reader needs the old state and resets the WAL -- the LevelDB/LMDB pressure again, a third discipline",
    input="dirty pages at commit", output="frames; a checkpointed database", state="the wal-index (shm), read marks, salt/checksums", update="per commit; per checkpoint", evidence_ref=S + ":65133-70780 (wal.c); 66421, 67320, 69364", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="wal.c",
    coverage={"input_topology": "EVENT", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "DURABLE", "competition": "ISOLATES", "memory": "WINDOW"})

pl = c.organ("cost_based_join_planner_by_beam_search_over_loop_orders_in_log2_cost_units", human_name="where.c: whereLoopAddAll / whereLoopAddBtree / wherePathSolver", status="ACCEPTED",
    mechanism="for each FROM term enumerate candidate access paths (full scan, each usable index with equality/range terms, automatic index) with an estimated cost and output row count in LogEst (a 10*log2 integer scale); wherePathSolver then extends partial join orders level by level keeping only mxChoice best paths per level (1 for a single loop, up to ~50 for many), accounting for sort avoidance (ORDER BY satisfied by an index) -- a beam search, not exhaustive; statistics from ANALYZE (nRowEst0) refine the estimates",
    input="the FROM/WHERE/ORDER BY terms, indexes, statistics", output="a WhereInfo plan the code generator emits loops from", state="none per query", update="per statement prepare", assumptions=["LogEst arithmetic is precise enough to rank plans; the beam does not drop the optimum"],
    fitness_value_in_ancestor="query performance without a human hint", evidence_ref=S + ":163412-174192 (where.c); 168219, 167294, 169072-169110", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="where.c + whereexpr.c + wherecode.c",
    coverage={"input_topology": "GRAPH", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SWEEP", "uncertainty": "POINT", "representation_sensitivity": "SENSITIVE"})

cg = c.organ("sql_to_bytecode_compiler_from_a_lemon_lalr_parser_through_name_resolution_and_per_statement_generators", human_name="tokenize.c + parse.c (Lemon) + resolve.c + expr.c + build.c/select.c/insert.c/update.c/delete.c", status="ACCEPTED",
    mechanism="a hand-written tokenizer feeds a table-driven LALR(1) parser generated by Lemon (parse.c) that builds Select/Expr/SrcList trees; resolve.c binds names; the per-statement generators walk the trees emitting VdbeOps (sqlite3VdbeAddOp*), with expr.c generating expression code into registers and select.c handling subqueries, joins (via the planner) and aggregates",
    input="SQL text", output="a VdbeOp program", state="the Parse context", update="per prepare", evidence_ref=S + ":109532 (expr.c), 122145 (build.c), 143849 (select.c), 174193 (parse.c), 179768 (tokenize.c)", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the front-end files",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "update_topology": "RECURSIVE"})

vfs = c.organ("virtual_file_system_layer_with_advisory_locking_states", human_name="os.c / os_unix.c / os_win.c / memdb.c", status="CANDIDATE",
    mechanism="all file, lock, sleep and randomness access goes through an sqlite3_vfs method table; the unix VFS implements the five lock states (none, shared, reserved, pending, exclusive) with fcntl byte ranges (by names; not read)", input="pager requests", output="OS calls", state="lock state per file",
    evidence_ref=S + ":38596 (os_unix.c)", confidence="LOW", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="os*.c",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "competition": "ARBITRATES"})

c.reject("'SQLite' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="the amalgamation's own Begin-file markers: 130 files, seven layers with header-declared interfaces (pager.h, btree.h, vdbe.h, os.h)")
c.reject("extensions: fts3/fts5 (full-text), rtree, geopoly, json, session, rbu, icu, dbstat, dbpage", reason="OTHER", evidence="file map; NOT READ", note="UNKNOWN; each is likely its own organ family (an inverted index, an R-tree)")
c.reject("memory allocators (mem0-5), mutexes, printf, utf, hash, random, date, util", reason="GENERIC_LANGUAGE_MECHANICS", evidence="file map: the portability layer")
c.reject("the shell (shell.c) and the smoke harness", reason="EFFECT_FROM_ENVIRONMENT", evidence="Techne's recipe")
c.reject("pragma, auth, alter, analyze, attach, trigger, vacuum, vtab, window, upsert, fkey", reason="OTHER", evidence="front-end features NOT READ; they extend the code generator", note="UNKNOWN")

c.edge(cg, pl, "feeds", note="select.c calls the planner"); c.edge(pl, cg, "feeds", note="plan -> loop code"); c.edge(cg, vm, "stores", note="the program"); c.edge(vm, bt, "feeds", note="cursor ops"); c.edge(bt, pg, "feeds"); c.edge(pg, wl, "feeds", note="in WAL mode frames replace the journal"); c.edge(pg, vfs, "feeds"); c.edge(wl, vfs, "feeds")
c.edge(pg, wl, "competes", note="two durability disciplines selected per database")

c.pressure("a_relational_engine_must_fit_in_one_file_and_one_library_with_no_server_and_acid_on_any_filesystem",
    condition="the database is a single ordinary file opened by any number of processes; there is no daemon to coordinate; the filesystem's guarantees are the weakest common denominator", resource_or_constraint="advisory file locks; fsync semantics",
    failure_condition="corruption on power loss or concurrent access", world_punishes="assuming a coordinator; assuming atomic multi-sector writes", world_rewards="journal-then-write (or log-then-checkpoint) with lock state machines and checksums",
    observable_consequence="the pager's and WAL's crash-recovery paths; the record's smoke is only a query", vacuity_condition="single process, no crashes", trivial_shortcuts="a server (forbidden by the design)",
    cheat_control="a build told the crash instants must recover every committed transaction; the smoke harness cannot show this -- a crash-injection world is required", cost_class="CPU-scale", source_evidence="pager.c, wal.c, os_unix.c locks", purpose="PURPOSE: an embedded SQL database (Hipp, 2000)")
c.pressure("join_orders_grow_factorially_and_the_planner_has_milliseconds_and_no_statistics_by_default",
    condition="a query with n tables has n! loop orders times index choices; prepare must be fast; row counts are guesses unless ANALYZE ran", resource_or_constraint="prepare time; LogEst precision; optional statistics",
    failure_condition="a catastrophic plan (a full scan inside a loop)", world_punishes="exhaustive search; exact arithmetic", world_rewards="a bounded beam over orders with logarithmic cost units and heuristics that survive missing statistics",
    observable_consequence="plan choice vs table sizes (EXPLAIN QUERY PLAN)", vacuity_condition="single-table queries", trivial_shortcuts="always nested loops in FROM order (correct, sometimes terrible)",
    cheat_control="a planner given true cardinalities must never lose to the estimated one by more than the beam's drop; if it does not beat LogEst estimates on skewed data, the world's data is not skewed", cost_class="CPU-scale", source_evidence="wherePathSolver mxChoice tuning comment", purpose="PURPOSE: same")

c.residue("CUT_INSTRUMENT_INSUFFICIENT", ["261k lines read at file-map grain; every organ's inside is unread except the solver's head", "nine front-end feature files and nine extensions unassigned", "nothing ran here; Techne's smoke.sql is on M1", "the cut instrument (one reader, one session) cannot reach line-level anatomy for a body this size; Stage B on SQLite needs a sampling plan (one subsystem per session)"],
          note="layer boundaries are the amalgamation's own; the atlas records them as ACCEPTED because the file boundaries ARE executable boundaries (separately compilable units with declared interfaces)")
c.save(state="COARSE")
