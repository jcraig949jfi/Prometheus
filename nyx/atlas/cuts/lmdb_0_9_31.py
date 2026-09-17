"""Cut: lmdb-0.9.31 (ancestry-aware, Stage A COARSE; SOURCE_READ mdb.c 1370-1446 (forward declarations), 2124-2142, 2176-2352,
2439-2540, 2703-2790 (reader slot claim), 3099-3120, 3471-3560 (commit order, grepped), 3837-3870, 3967-3971; the B+tree
functions (page_search 5316, cursor_put 6574, rebalance 8281, page_split 8642) located and their signatures read, bodies skimmed).
One 10,354-line file."""
from nyx.atlas.author import Cut

S = "vault:lmdb-0.9.31/upstream/tree/lmdb-LMDB_0.9.31/libraries/liblmdb/mdb.c"
c = Cut("lmdb-0.9.31", mode="ANCESTRY_AWARE", inspected=["mdb.c (forward decls; page_alloc; page_touch; find_oldest; txn_renew0 reader claim; freelist_save head; commit order; write_meta head; pick_meta)"],
        evidence=[("SOURCE_READ", S)], note="a copy-on-write B+tree in one memory-mapped file; the record's oracle (kill between put and commit; the previous root comes back) is the double-meta organ")

cow = c.organ("copy_on_write_page_touch_relinking_the_parent", human_name="mdb_page_touch (shadow paging)", status="ACCEPTED",
    human_interpretation="a page is never modified in place; the first write in a transaction copies it",
    mechanism="if the page on top of the cursor is not already dirty in this txn: allocate a fresh page (from the freelist or the map end), append the OLD page number to the txn's free list, copy, and point the parent node's page number (or the DB root) at the new page; if the txn has a parent, the page must also be in the child's dirty list",
    input="a cursor positioned on a page", output="a dirty copy in the txn's dirty list; the old pgno on mt_free_pgs", state="mt_dirty_list, mt_free_pgs, md_root", update="once per page per txn", assumptions=["readers hold the old root and never see the new page"],
    fitness_value_in_ancestor="every property below (crash safety, lock-free reads) is built on pages never changing under a reader", evidence_ref=S + ":2439-2540", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="mdb_page_touch",
    coverage={"input_topology": "TREE", "output_topology": "TREE", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "DURABLE", "memory": "FULL_HISTORY"})

meta = c.organ("two_meta_pages_alternating_by_transaction_id_parity", human_name="double meta page / atomic root switch", status="ACCEPTED",
    mechanism="the file begins with two meta pages; pick_meta returns the one with the larger txnid (3967-3971); commit writes the meta for txnid N into slot N & 1, i.e. the slot NOT currently current, after the data pages are flushed and synced; a crash before the meta write leaves the other slot as the valid root; a torn meta write is detected by txnid ordering (not verified here)",
    input="the committed root pgno, txnid, freelist root, mapsize", output="one meta page write", state="me_metas[2]", update="per commit", assumptions=["a single page write of the meta is atomic enough, or at least that a torn one is distinguishable"],
    fitness_value_in_ancestor="the record's oracle: what comes back after a kill is the previous root", evidence_ref=S + ":3837-3966,3967-3971", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="mdb_env_write_meta + mdb_env_pick_meta",
    coverage={"input_topology": "VECTOR", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "DURABLE", "recovery": "ROLLS_BACK", "failure_mode": "NONE_KNOWN"})

fl = c.organ("freed_pages_keyed_by_the_freeing_transaction_and_reused_only_below_the_oldest_reader", human_name="freeDB / me_pghead reclamation", status="ACCEPTED",
    mechanism="pages freed by a txn are saved at commit under that txnid in a hidden B+tree (FREE_DBI, freelist_save); page_alloc walks FREE_DBI from me_pglast upward, merging records into me_pghead, but stops at any record whose txnid >= the oldest txnid still held by a registered reader (find_oldest scans the reader table); loose pages (freed and reallocated in the same txn) bypass the list; if the list has no contiguous run, new pages come from the end of the map",
    input="num pages wanted; the reader table; FREE_DBI", output="a page range", state="me_pghead (in-memory id list), me_pglast, me_pgoldest, mt_loose_pgs", update="per allocation; per commit", assumptions=["a reader that registered txnid T may still dereference any page live at T"],
    fitness_value_in_ancestor="space reuse without a garbage collector and without blocking readers", failure_landscape="UNKNOWN by run; by reading: a long-lived reader pins every page freed since it started -- the file grows (the well-known LMDB operational hazard, stated here from the code's stopping rule, not measured)",
    evidence_ref=S + ":2124-2142,2176-2352,3099-3323", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="mdb_page_alloc + mdb_find_oldest + mdb_freelist_save",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "DURABLE", "resource_dependence": "MEMORY", "competition": "ARBITRATES", "temporal_horizon": "UNBOUNDED"})

rd = c.organ("reader_slots_in_shared_memory_holding_pid_and_snapshot_txnid", human_name="reader table (lock file mmap)", status="ACCEPTED",
    mechanism="a read txn claims a slot in the mmapped lock file under the reader mutex once (per thread via TLS, or per txn with NOTLS): reset the slot, publish numreaders, then write (pid, txnid of the current meta); reads then proceed with NO locks, dereferencing the map; dead readers are found by pid liveness (reader_check0) and their slots cleared",
    input="a begin-read request", output="a registered (pid, txnid)", state="mti_readers[], mti_numreaders", update="per read txn begin/end", assumptions=["pids are meaningful across the processes sharing the file (containers break this -- stated by reading the pid check, not measured)"],
    fitness_value_in_ancestor="readers never block writers and writers never block readers; the table is the only thing a writer consults about readers (via find_oldest)", evidence_ref=S + ":2703-2790,10225-10300", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="mdb_txn_renew0 read branch + mdb_reader_check0",
    coverage={"input_topology": "EVENT", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "competition": "ISOLATES", "hidden_state": "ASSUMES"})

wc = c.organ("single_writer_commit_in_a_fixed_order_freelist_then_pages_then_sync_then_meta", human_name="mdb_txn_commit", status="ACCEPTED",
    mechanism="one write txn at a time (writer mutex taken at begin, not read here); commit: merge child dirty lists into the parent if nested, save the freelist, flush dirty pages to the file (write(), or msync on a writable map), fsync, write the meta page, fsync, release; on error the txn is marked and aborted",
    input="a write txn", output="a durable new root", state="mt_dirty_list, mt_flags", update="per commit", assumptions=["fsync orders the page writes before the meta write"],
    evidence_ref=S + ":3471-3830 (grepped for the order), 3324-3470 (page_flush)", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="mdb_txn_commit + mdb_page_flush",
    coverage={"input_topology": "SET", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SWEEP", "competition": "ARBITRATES"})

bt = c.organ("b_plus_tree_with_binary_search_split_and_rebalance", human_name="the B+tree (page_search, node_search, cursor_put, page_split, rebalance)", status="CANDIDATE",
    mechanism="sorted keys in fixed-size pages; descend from the root by binary search over node keys (node_search); insert into the leaf, split when full (page_split, with the new key propagating up), merge or borrow from a sibling when a page falls below the fill threshold (rebalance); sub-databases and duplicate-key sub-pages (xcursor) nest the same structure",
    input="key/value operations", output="a modified tree", state="pages", update="per operation", evidence_ref=S + ":5316,6574,8281,8642 (signatures; bodies skimmed)", confidence="LOW", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="the mdb_page_search/mdb_node_*/mdb_cursor_*/mdb_page_split/mdb_rebalance family",
    coverage={"input_topology": "SEQUENCE", "output_topology": "TREE", "state_amount": "LINEAR_IN_INPUT", "update_topology": "RECURSIVE"})

mm = c.organ("whole_file_memory_map_as_the_read_path", human_name="mdb_env_map", status="CANDIDATE",
    mechanism="the database file is mmapped once at a fixed size (mapsize); pages are dereferenced as pointers into the map; with WRITEMAP writes go through the map, otherwise through write()", input="the file", output="a base address", state="me_map, me_mapsize", update="once (and on mapsize change)",
    evidence_ref=S + ":3999-4090 (skimmed)", confidence="LOW", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="mdb_env_map",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "CONSTANT", "resource_dependence": "MEMORY"})

sp = c.organ("spill_dirty_pages_early_when_the_transaction_dirty_list_is_full", human_name="mdb_page_spill", status="CANDIDATE",
    mechanism="when a write txn's dirty room is exhausted, pages not needed by the current cursors are written to the file ahead of commit and marked spilled; a later touch unspills them (page_unspill in page_touch)", input="the dirty list", output="fewer dirty pages", state="mt_spill_pgs, MDB_TXN_SPILLS", update="on dirty-room exhaustion",
    evidence_ref=S + ":2025-2122 (skimmed), 2447-2453", confidence="LOW", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="mdb_page_spill + mdb_page_unspill",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "resource_dependence": "MEMORY", "recovery": "DEGRADES_GRACEFULLY"})

c.reject("'LMDB' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="eight mechanisms above with distinct state; the tree and the storage discipline are separable (the B+tree could sit on any page allocator)")
c.reject("platform shims (Windows handles, POSIX semaphores vs mutexes, utf8_to_utf16, robust-mutex fallbacks)", reason="GENERIC_LANGUAGE_MECHANICS", evidence=S + ":347-480,1457-1466")
c.reject("mdb_audit / mdb_page_list / mdb_cursor_chk / DPRINTF", reason="OTHER", evidence=S + ":1579-1774 -- debug instruments; read-only", note="instruments, not machinery")
c.reject("the mtest*.c drivers and mdb_stat / mdb_dump / mdb_load", reason="EFFECT_FROM_ENVIRONMENT", evidence="tools directory; the harness Techne ran (mtest, mtest3)")
c.reject("nested (child) transactions as a separate organ", reason="CANNOT_BE_ISOLATED", evidence=S + ":2470-2540 -- the parent/child dirty-list merge is interleaved through page_touch and commit; not read enough to bound it", note="UNKNOWN rather than absent")

c.edge(rd, fl, "gates", note="oldest reader txnid bounds reclamation"); c.edge(cow, fl, "feeds", note="old pgnos -> mt_free_pgs -> freeDB at commit"); c.edge(fl, cow, "feeds", note="page_alloc supplies the copy")
c.edge(cow, bt, "transforms", note="every tree mutation goes through touch first"); c.edge(bt, wc, "feeds", note="dirty pages"); c.edge(wc, meta, "triggers", note="meta written last"); c.edge(meta, rd, "feeds", note="a reader's snapshot is pick_meta at begin")
c.edge(mm, bt, "feeds", note="pages are pointers into the map"); c.edge(sp, wc, "feeds", note="spilled pages are already on disk at commit"); c.edge(sp, cow, "restores", note="unspill on touch"); c.edge(wc, fl, "stores", note="freelist_save")

c.pressure("a_crash_at_any_instant_must_leave_the_previous_consistent_state_readable",
    condition="the process or host can die between any two writes; the medium may tear a multi-page write; on reopen there is no log to replay", resource_or_constraint="no write-ahead log; one file",
    failure_condition="a torn write corrupts the tree (record)", world_punishes="in-place modification of reachable pages; a root pointer updated before its pages are durable", world_rewards="never overwriting reachable state and switching the root atomically after a sync",
    observable_consequence="the record's oracle after a kill between put and commit", vacuity_condition="no crashes; or a medium with atomic multi-page writes", trivial_shortcuts="rewrite the whole file on every commit (correct, O(size))",
    cheat_control="a store told when the crash will happen must always recover; if the world scores it no better than a store that corrupts on a torn meta, the world is not injecting crashes at the right instants", cost_class="CPU-scale (kill -9 in a loop)", source_evidence="record failure condition; write_meta / pick_meta", purpose="PURPOSE: an embedded key-value store")
c.pressure("readers_must_neither_block_writers_nor_observe_a_half_committed_state",
    condition="many processes read while one writes; reads must be consistent snapshots and must not slow the writer or each other", resource_or_constraint="shared memory; no coordination on the read path",
    failure_condition="a reader observes a page mid-change (record) or waits on the writer", world_punishes="locks on the read path; in-place writes", world_rewards="immutable versions plus a cheap registration of which version each reader holds",
    observable_consequence="read throughput under a concurrent writer; snapshot consistency checks", vacuity_condition="one process", trivial_shortcuts="a global lock (consistent, serialised); the world must reward concurrency",
    cheat_control="a reader given a private frozen copy must see a consistent snapshot; a world that does not detect torn reads on the naive store is not measuring isolation", cost_class="CPU-scale", source_evidence="reader table + page_touch + find_oldest", purpose="PURPOSE: same")
c.pressure("space_freed_by_new_versions_must_be_reclaimed_while_old_versions_may_still_be_read",
    condition="copy-on-write leaves the old page behind; without reclamation the file grows without bound; with premature reclamation a reader dereferences reused bytes", resource_or_constraint="disk space vs reader lifetime",
    failure_condition="unbounded growth (long reader) or corruption (early reuse)", world_punishes="both", world_rewards="a version-stamped free list gated by the oldest live snapshot",
    observable_consequence="file size vs reader lifetime distribution", vacuity_condition="no readers, or infinite disk", trivial_shortcuts="never free (bounded workloads only)",
    cheat_control="a store told every reader's exit time exactly must reclaim eagerly and never corrupt; if the world rewards a never-free store equally on a long run, it is not charging for space", cost_class="CPU-scale", source_evidence="page_alloc stopping rule", purpose="PURPOSE: same")

c.ancestry("algorithm_from", "shadow paging (Lorie 1977) and append-only B-trees (the code's own doc references not read)", note="human prior, not from the body")
c.residue("PARTIALLY_EXPLAINED", ["the B+tree operations, the memory map, and spilling are CANDIDATE from signatures and skims, not read in full", "nested transactions and sub-databases / DUPSORT sub-pages (xcursor) are unread", "the writer mutex acquisition and the NOLOCK / NOTLS / WRITEMAP flag variants are unread", "nothing ran; the crash oracle is a Stage C candidate (kill between put and commit inside Techne's container)"],
          note="the storage discipline (COW, double meta, freelist, reader table, commit order) is fully read; the tree on top of it is not")
c.save(state="COARSE")
