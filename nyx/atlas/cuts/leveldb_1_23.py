"""Cut: leveldb-1.23 (ancestry-aware, Stage A COARSE; SOURCE_READ db/db_impl.cc 1200-1260 (Write, grepped), 1325-1400 (MakeRoomForWrite in
full); db/version_set.cc 1032-1069 (Finalize), 1253-1300 (PickCompaction); function indexes of db_impl.cc / version_set.cc;
log_writer.cc constants; skiplist.h, memtable.cc, table_builder.cc, cache.cc by name. The LSM-tree engine; organ names chosen against
lmdb-0.9.31 (same human domain, opposite storage discipline)."""
from nyx.atlas.author import Cut

S = "vault:leveldb-1.23/upstream/tree/leveldb-1.23/"
c = Cut("leveldb-1.23", mode="ANCESTRY_AWARE", inspected=["db/db_impl.cc (Write, MakeRoomForWrite; index)", "db/version_set.cc (Finalize, PickCompaction; index)", "db/log_writer.cc (constants)", "file list"],
        evidence=[("SOURCE_READ", S + "db/db_impl.cc"), ("SOURCE_READ", S + "db/version_set.cc"), ("SOURCE_READ", S + "db/log_writer.cc")],
        note="where LMDB never overwrites a page and reclaims by reader epoch, LevelDB never overwrites a FILE and reclaims by compaction; both keep old versions alive for readers by reference counting -- the same pressure, two disciplines; a Stage E pair")

wal = c.organ("write_ahead_log_of_batches_in_crc_framed_32k_blocks_before_any_in_memory_apply", human_name="log::Writer / AddRecord; RecoverLogFile", status="ACCEPTED",
    mechanism="every write batch is appended to the current .log file as records split across 32 KB blocks with a 7-byte header (crc32c of type + payload, length, type = full/first/middle/last); the CRC is seeded per type; optionally fsync'd (WriteOptions.sync); on open, RecoverLogFile replays every record into a fresh memtable (the record's entry point: reopen without a clean close)",
    input="serialised write batches", output="a durable log", state="block_offset_", update="per batch", assumptions=["a torn record fails its CRC and ends replay"],
    evidence_ref=S + "db/log_writer.cc:16-60; db/db_impl.cc:385-504 (RecoverLogFile, index)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="db/log_writer.cc + log_reader.cc + RecoverLogFile",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "DURABLE", "recovery": "ROLLS_BACK"})

gc = c.organ("group_commit_where_the_front_writer_batches_the_queue_behind_it", human_name="DBImpl::Write / BuildBatchGroup / writers_ deque", status="ACCEPTED",
    mechanism="a writer pushes itself on a deque and waits unless it is at the front; the front writer merges the batches queued behind it (up to a size bound, and never mixing a sync write into a non-sync group) into one log record and one memtable insert, then pops and signals every writer it absorbed; the lock is released during the log write",
    input="concurrent Write calls", output="fewer, larger log records", state="writers_ deque, per-writer condvars", update="per write", evidence_ref=S + "db/db_impl.cc:1200-1324", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="DBImpl::Write + BuildBatchGroup",
    coverage={"input_topology": "EVENT", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "competition": "ARBITRATES", "cooperation": "SHARES"})

mt = c.organ("sorted_in_memory_table_on_a_skip_list_with_sequence_numbered_internal_keys", human_name="MemTable / SkipList / InternalKey", status="CANDIDATE",
    mechanism="writes go into a skip list keyed by (user key, sequence number descending, type put/delete) from an arena; reads look up the newest sequence <= the snapshot; an immutable copy (imm_) is frozen when full while a new memtable takes writes (by index and names; skiplist.h not read)", input="batches", output="an ordered in-memory map", state="the skip list, arena",
    evidence_ref=S + "db/memtable.cc, db/skiplist.h, db/dbformat.h (names)", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="memtable.cc + skiplist.h",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "memory": "FULL_HISTORY"})

th = c.organ("write_admission_by_memtable_size_and_level0_file_count_with_a_1ms_slowdown_then_a_stop", human_name="MakeRoomForWrite", status="ACCEPTED",
    mechanism="loop: if a background error, fail; else if level-0 has >= kL0_SlowdownWritesTrigger (8) files, sleep 1 ms once per write; else if the memtable is under write_buffer_size, proceed; else if an immutable memtable is still being flushed, wait; else if level-0 has >= kL0_StopWritesTrigger (12) files, wait; else rotate: new log file, current memtable becomes immutable, schedule a compaction",
    input="the memtable size, level-0 file count, background state", output="admission / delay / rotation", state="mem_, imm_, log_", update="per write", assumptions=["compaction keeps up on average; the sleep is a soft back-pressure, the stop a hard one"],
    fitness_value_in_ancestor="the only place writes are throttled; couples foreground latency to background progress", failure_landscape="UNKNOWN by run; by reading: write stalls when compaction falls behind (the well-known LevelDB latency spike, stated from the code's two triggers, not measured)",
    evidence_ref=S + "db/db_impl.cc:1325-1400", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="MakeRoomForWrite",
    coverage={"input_topology": "VECTOR", "output_topology": "DECISION", "state_amount": "CONSTANT", "feedback": "CLOSED_LOOP", "resource_dependence": "MEMORY", "failure_mode": "STALLS", "recovery": "DEGRADES_GRACEFULLY"})

lv = c.organ("leveled_sorted_files_with_a_compaction_score_from_size_per_level_and_a_seek_counter", human_name="VersionSet::Finalize / PickCompaction / DoCompactionWork", status="ACCEPTED",
    mechanism="files live in 7 levels; level 0 may overlap, others are sorted and disjoint; Finalize scores level 0 by file count / 4 and other levels by bytes / (10^level MB); PickCompaction takes the highest score >= 1 (size compaction), else a file whose allowed_seeks counter ran out (seek compaction), picks the input file after the last compacted key (round-robin pointer), pulls in all overlapping files of the next level, and merges them into new files, dropping overwritten and deleted keys older than the oldest snapshot",
    input="the current Version's file lists", output="new files and a VersionEdit", state="compact_pointer_ per level, compaction_score_", update="in the background thread", assumptions=["a 10x size ratio between levels bounds write amplification"],
    fitness_value_in_ancestor="the LSM invariant; reads touch at most one file per level above 0", evidence_ref=S + "db/version_set.cc:1032-1069,1253-1445; db/db_impl.cc:892-1114 (index)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="version_set.cc compaction functions + DoCompactionWork",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "update_topology": "EVENT_DRIVEN", "resource_dependence": "MEMORY", "memory": "FULL_HISTORY"})

vs = c.organ("immutable_versions_of_the_file_set_with_reference_counts_and_a_manifest_log_of_edits", human_name="Version / VersionSet::LogAndApply / MANIFEST", status="ACCEPTED",
    mechanism="the set of live files is an immutable Version object; a change is a VersionEdit (files added/deleted per level, log numbers) appended to the MANIFEST log and applied to produce a new Version at the head of a linked list; iterators and snapshots Ref() the Version they read; a Version is freed when its count hits zero and its files become obsolete only when no live Version names them (RemoveObsoleteFiles)",
    input="VersionEdits", output="a new current Version", state="the Version list, the MANIFEST", update="per flush / compaction", assumptions=["compare lmdb-0.9.31::freed_pages_keyed_by_the_freeing_transaction...: LMDB gates reuse on the oldest reader's txnid; LevelDB gates deletion on Version refcounts"],
    evidence_ref=S + "db/version_set.cc:453-462,760-861; db/db_impl.cc:225-291", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="Version + VersionSet + RemoveObsoleteFiles",
    coverage={"input_topology": "EVENT", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "DURABLE", "competition": "ISOLATES", "memory": "FULL_HISTORY"})

tb = c.organ("sorted_string_table_of_prefix_compressed_blocks_with_an_index_and_optional_bloom_filter", human_name="table/table_builder.cc, block_builder.cc, filter_block.cc; util/cache.cc (LRU block cache)", status="CANDIDATE",
    mechanism="keys within a block share prefixes with restart points every 16 entries; blocks are optionally snappy-compressed and CRC'd; an index block maps last-keys to block handles; a filter block (bloom) lets Get skip files; a sharded LRU cache holds decoded blocks (by file names and the record; bodies not read)", input="sorted key/values", output="an .ldb file",
    evidence_ref=S + "table/*.cc, util/cache.cc (names)", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="table/ + util/cache.cc",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "representation_sensitivity": "SENSITIVE"})

c.reject("'LevelDB' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="log, memtable, versions, compaction, tables are separate directories with separate state; RocksDB (Techne's successor edge) replaced several independently")
c.reject("Env / port abstraction (file system, threads, mutexes)", reason="GENERIC_LANGUAGE_MECHANICS", evidence="util/env_posix.cc, port/ -- OS wrappers")
c.reject("Get's read path (memtable -> imm -> versions) and iterators (merging iterator, two-level iterator)", reason="OTHER", evidence="db/db_impl.cc:1115-1173 and table/merger.cc, two_level_iterator.cc NOT read", note="UNKNOWN, not rejected on merit")
c.reject("the test suite and db_bench", reason="EFFECT_FROM_ENVIRONMENT", evidence="Techne built with LEVELDB_BUILD_TESTS=OFF")

c.edge(gc, wal, "feeds"); c.edge(wal, mt, "feeds", note="apply after the log write"); c.edge(th, gc, "gates", note="admission before the batch"); c.edge(th, mt, "restores", note="rotation freezes the memtable"); c.edge(mt, lv, "feeds", note="flush = level-0 file")
c.edge(lv, vs, "updates", note="VersionEdit"); c.edge(vs, lv, "feeds", note="Finalize scores the new version"); c.edge(lv, th, "feeds", note="level-0 count"); c.edge(lv, tb, "stores"); c.edge(vs, tb, "gates", note="files deleted only when unreferenced"); c.edge(wal, vs, "feeds", note="log numbers in the manifest")

c.pressure("random_writes_must_become_sequential_disk_writes_while_reads_stay_bounded",
    condition="a spinning disk (2011) writes sequentially 100x faster than randomly; a key-value store receives random keys; reads must not degrade into scanning every file", resource_or_constraint="disk seek cost; write amplification budget",
    failure_condition="either random-write throughput collapses or reads touch unbounded files", world_punishes="in-place trees on disk (random writes); unbounded file counts", world_rewards="append-only files merged in the background under a size invariant per level",
    observable_consequence="write throughput vs read latency vs write_buffer_size (the record's entry point)", vacuity_condition="a random-access medium with no seek cost", trivial_shortcuts="a log with no compaction (reads scan; the world must charge reads)",
    cheat_control="a store given the final key set in advance (one sorted file) must show the best reads and no compaction cost; if the world does not distinguish it from a live LSM, background work is not being charged", cost_class="CPU-scale (disk simulation)", source_evidence="the level structure; MakeRoomForWrite", purpose="PURPOSE: an embedded ordered key-value store (Google, 2011)")
c.pressure("a_crash_between_a_write_and_its_durable_home_must_lose_nothing_acknowledged",
    condition="the process may die after acknowledging a write; the in-memory table is gone; the on-disk tables were not yet updated", resource_or_constraint="one fsync per group at most",
    failure_condition="acknowledged keys missing after reopen (the record's entry point)", world_punishes="applying before logging", world_rewards="a CRC-framed log written first and replayed on open, with batching to amortise the sync",
    observable_consequence="keys present after an unclean close", vacuity_condition="no crashes", trivial_shortcuts="fsync every write (slow; the world must charge latency)",
    cheat_control="a store told the crash instant must lose exactly the unacknowledged writes; if the world does not inject the crash between AddRecord and InsertInto, it is not testing the log", cost_class="CPU-scale", source_evidence="db_impl.cc Write; log_writer.cc", purpose="PURPOSE: same")
c.pressure("background_work_must_keep_pace_with_foreground_writes_or_bounded_memory_is_exceeded",
    condition="flushes and merges run on one background thread; writes arrive at any rate; memory for the memtable and the level-0 file count are bounded", resource_or_constraint="one background thread; write_buffer_size; kL0 triggers",
    failure_condition="unbounded memtables or level-0 files; or writes stalled for seconds", world_punishes="no back-pressure; hard stops only", world_rewards="graded back-pressure (a 1 ms delay before a stop) keyed to the backlog",
    observable_consequence="write latency distribution under a burst", vacuity_condition="writes slower than compaction", trivial_shortcuts="unbounded memory",
    cheat_control="a store with an infinitely fast compactor must never stall; if the world's write rate never triggers the slowdown, the mechanism is untested", cost_class="CPU-scale", source_evidence="MakeRoomForWrite triggers", purpose="PURPOSE: same")

c.ancestry("superseded", "RocksDB (Facebook fork 2012)", note="Techne's edge with its note")
c.residue("PARTIALLY_EXPLAINED", ["memtable / skip list, the table format, the block cache and the read path are CANDIDATE or unread", "DoCompactionWork's snapshot-aware dropping rule read by index only", "nothing ran here; Techne's reopen harness is on M1"],
          note="the write path (group commit, log, admission) and the version/compaction machinery are read")
c.save(state="COARSE")
