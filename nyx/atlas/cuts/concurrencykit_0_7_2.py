"""Cut: concurrencykit-0.7.2 (ancestry-aware, Stage A COARSE; SOURCE_READ include/ck_backoff.h in full, include/spinlock/ticket.h and mcs.h
(grepped bodies), src/ck_epoch.c 320-424 + function index, include/ck_ring.h (grepped); the header list (41 files). A library of
concurrency primitives; cut at the level of the SHAPES that recur across its 8 spinlocks and 3 reclamation schemes."""
from nyx.atlas.author import Cut

S = "vault:concurrencykit-0.7.2/upstream/tree/ck-0.7.2/"
c = Cut("concurrencykit-0.7.2", mode="ANCESTRY_AWARE", inspected=["include/ck_backoff.h", "include/spinlock/ticket.h", "include/spinlock/mcs.h", "src/ck_epoch.c 320-424", "include/ck_ring.h", "header list"],
        evidence=[("SOURCE_READ", S + "include/ck_backoff.h"), ("SOURCE_READ", S + "include/spinlock/ticket.h"), ("SOURCE_READ", S + "include/spinlock/mcs.h"), ("SOURCE_READ", S + "src/ck_epoch.c")],
        note="every primitive is built from three atomic operations (load/store with fences, fetch-and-add, compare-and-swap) plus a stall; the anatomy is in HOW waiting is organised (where each waiter spins) and HOW freed memory waits for readers")

bo = c.organ("exponential_backoff_by_spinning_a_doubling_count_of_barriers_up_to_a_ceiling", human_name="ck_backoff_eb", status="ACCEPTED",
    mechanism="spin `ceiling` compiler barriers, then double the caller's counter unless it reached CK_BACKOFF_CEILING (2^20 - 1); initial 2^9; the state is the caller's unsigned int -- no randomisation, no decrease",
    input="a counter", output="a delay; the counter doubled", state="the counter (caller-owned)", update="per call", assumptions=["contention persists so ever-longer waits are right; the counter is reset by the caller when it wins"],
    fitness_value_in_ancestor="reduces cache-line traffic under contention for the CAS-based locks (record: 'a convoy of spinning threads starving the holder')", evidence_ref=S + "include/ck_backoff.h:1-30", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="ck_backoff.h",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "CONSTANT", "adaptation": "PARAMETER", "competition": "CONTENDS", "temporal_horizon": "STEP"})

tk = c.organ("ticket_lock_serving_fetch_and_add_numbers_in_order_on_one_shared_word", human_name="ck_spinlock_ticket", status="ACCEPTED",
    mechanism="one word holds (next ticket, now serving) as two halves; lock = fetch-and-add the ticket half and spin (with a stall hint) until the serving half equals your ticket; unlock increments the serving half; FIFO by construction; every waiter spins on the SAME word",
    input="lock/unlock calls", output="mutual exclusion in arrival order", state="one word", update="per acquire / release", assumptions=["a 32/64-bit atomic FAA exists"],
    failure_landscape="UNKNOWN by run; by reading: N waiters on one cache line means every release invalidates N caches (the reason MCS exists)", evidence_ref=S + "include/spinlock/ticket.h", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="spinlock/ticket.h",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "competition": "ARBITRATES", "order_sensitivity": "INVARIANT", "resource_dependence": "SHARED_RESOURCE"})

mcs = c.organ("queue_lock_where_each_waiter_spins_on_its_own_node_linked_by_fetch_and_store", human_name="ck_spinlock_mcs (and clh, hclh, anderson: the same idea with different node ownership)", status="ACCEPTED",
    mechanism="lock = fetch-and-store the queue tail with your node; if there was a predecessor, link its next to you and spin on YOUR node's locked flag; unlock = if next is NULL try CAS the tail back to NULL, else spin until next appears and clear its flag; anderson uses an array slot per waiter, clh spins on the predecessor's node, hclh adds NUMA clustering (names only for the last three)",
    input="lock/unlock with a caller-provided node", output="mutual exclusion, FIFO, one cache line invalidated per handoff", state="tail pointer + per-waiter nodes", update="per acquire / release", assumptions=["each thread supplies its own node (the interface's cost)"],
    fitness_value_in_ancestor="the fix for the ticket lock's invalidation storm", evidence_ref=S + "include/spinlock/mcs.h; anderson.h, clh.h, hclh.h by name", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="spinlock/mcs.h",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "competition": "ARBITRATES", "order_sensitivity": "INVARIANT", "resource_dependence": "SHARED_RESOURCE"})

cas = c.organ("test_and_set_style_locks_with_backoff", human_name="ck_spinlock_cas / fas / dec", status="ACCEPTED",
    mechanism="lock = loop { if CAS(word, 0, 1) succeeds break; backoff }; unlock = store 0 (fas: fetch-and-store; dec: decrement-and-test); no ordering, no per-waiter state; the backoff organ is what makes them usable under contention", input="lock/unlock", output="mutual exclusion, unordered", state="one word",
    update="per acquire / release", evidence_ref=S + "include/spinlock/cas.h, fas.h, dec.h (by name; ticket.h includes ck_backoff.h)", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="spinlock/cas.h, fas.h, dec.h",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "competition": "CONTENDS", "order_sensitivity": "SENSITIVE"})

ep = c.organ("epoch_based_reclamation_deferring_frees_until_every_active_reader_has_left_the_epoch", human_name="ck_epoch: register / begin / end / call / synchronize / poll / reclaim", status="ACCEPTED",
    mechanism="readers register a record and mark themselves active with the current global epoch on entry; a writer that frees memory pushes it on the record's pending stack for the current epoch (ck_epoch_call); synchronize/poll scan all records (ck_epoch_scan) and may advance the global epoch only when no active record is still in an older epoch; dispatch pops the pending stack of an epoch two behind and runs the deferred functions; counters n_pending / n_peak / n_dispatch are kept",
    input="reader entries/exits; deferred frees", output="frees executed when safe", state="global epoch, per-record (epoch, active, pending[CK_EPOCH_LENGTH])", update="per read section; per poll", assumptions=["readers are short and always exit; a stalled reader stalls reclamation for everyone"],
    fitness_value_in_ancestor="the answer to use-after-free in lock-free structures without per-object reference counts", failure_landscape="UNKNOWN by run; by reading: one stuck reader stops all reclamation (the same shape as LMDB's long reader pinning the freelist)", evidence_ref=S + "src/ck_epoch.c:228-620", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="ck_epoch.c + ck_epoch.h",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "memory": "WINDOW", "competition": "ISOLATES", "temporal_horizon": "WINDOW", "cooperation": "COORDINATES"})

hp = c.organ("hazard_pointers_publishing_the_object_a_reader_is_about_to_touch", human_name="ck_hp (+ ck_hp_fifo, ck_hp_stack)", status="CANDIDATE",
    mechanism="a reader stores the pointer it is dereferencing in a per-thread slot; a freer scans all slots and frees only objects no slot names (by header name and the record; not read)", input="reader pointers; frees", output="safe frees", state="per-thread hazard slots", update="per dereference",
    evidence_ref=S + "include/ck_hp.h (name)", evidence_grade="METADATA", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="ck_hp.h + ck_hp_*.h",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "competition": "ISOLATES"})

rg = c.organ("single_producer_single_consumer_ring_with_masked_indices_and_a_published_tail", human_name="ck_ring (spsc; mpmc variants by name)", status="ACCEPTED",
    mechanism="a power-of-two buffer; producer and consumer heads are unsigned counters masked to index; the producer writes the slot then fences and publishes p_tail; the consumer reads c_head vs p_tail; capacity checks use (p - c) & mask; no CAS on the spsc path; mpmc variants add CAS on the heads (by name)",
    input="enqueue/dequeue", output="FIFO transfer without locks", state="c_head, p_head, p_tail, mask", update="per operation", evidence_ref=S + "include/ck_ring.h:9-110", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="ck_ring.h",
    coverage={"input_topology": "STREAM", "output_topology": "STREAM", "state_amount": "CONSTANT", "memory": "WINDOW", "cooperation": "SHARES"})

c.reject("ck_pr (the atomic primitive layer: load/store/cas/faa/fas/fence per architecture)", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY", evidence="include/ck_pr.h + gcc/ -- wrappers over compiler intrinsics and inline assembly; the hardware's machinery, named here as the dependency of every organ", note="the memory model the record names as a pressure lives here, not in any organ")
c.reject("the 8 spinlocks as 8 organs", reason="OTHER", evidence="three shapes: shared-word spinning (cas/fas/dec), ordered shared-word (ticket), per-waiter node (mcs/clh/hclh/anderson); the rest differ in who owns the node", note="by name for clh/hclh/anderson")
c.reject("ck_hs / ck_ht / ck_rhs (hash sets and tables), ck_fifo, ck_stack, ck_bitmap, ck_array, ck_barrier, ck_cohort, ck_elide, ck_sequence, ck_rwlock, ck_brlock, ck_pflock, ck_tflock, ck_swlock, ck_bytelock, ck_ec", reason="OTHER", evidence="NOT READ (25 of 41 headers)", note="UNKNOWN; the reader/writer lock family and the sequence lock are likely further shapes")
c.reject("regressions/ (validate and benchmark drivers)", reason="EFFECT_FROM_ENVIRONMENT", evidence="the record's entry point runs ck_ticket validate; harness, not machinery")

c.edge(bo, cas, "transforms", note="wait between attempts"); c.edge(tk, mcs, "competes", note="same contract, different spin location"); c.edge(cas, tk, "competes"); c.edge(ep, hp, "competes", note="two reclamation disciplines for the same hazard")
c.edge(ep, rg, "gates", note="a lock-free structure's frees go through epoch (ck_hp_fifo / epoch-protected structures by name)"); c.edge("ENVIRONMENT", ep, "gates", note="a stalled reader stops the epoch")

c.pressure("many_cores_contend_for_one_word_and_every_write_to_it_invalidates_every_other_cache",
    condition="mutual exclusion must be cheap when uncontended and must not collapse when N cores spin; the cost of a cache-line transfer dwarfs the critical section", resource_or_constraint="cache coherence traffic; no OS involvement",
    failure_condition="a convoy of spinning threads starving the holder (record)", world_punishes="all waiters spinning on the same line; retrying without waiting", world_rewards="waiting where nobody else writes (per-node spinning), or waiting longer each time (backoff), while keeping order",
    observable_consequence="acquisitions per second vs thread count > core count (the record's entry point)", vacuity_condition="one thread", trivial_shortcuts="an OS mutex (sleeps; the world must charge the syscall)",
    cheat_control="a lock that knows the next holder in advance (a scheduler oracle) must beat every spinlock; if the world's benchmark cannot separate ticket from MCS at 2x oversubscription, it is not measuring the pressure", cost_class="CPU-scale (multi-core needed)", source_evidence="record pressure / failure; ticket.h vs mcs.h", purpose="PURPOSE: building blocks for lock-free and low-latency systems")
c.pressure("memory_may_be_freed_while_another_thread_still_holds_a_pointer_it_read_without_a_lock",
    condition="lock-free readers hold no lock, so a writer cannot know who still references a node it unlinked", resource_or_constraint="no reference counts on the read path (they would be contended writes)",
    failure_condition="use-after-free (record)", world_punishes="immediate free; per-object counters", world_rewards="deferring frees behind a global notion of 'all readers have moved on' (epochs) or per-reader announcements (hazard pointers)",
    observable_consequence="ASan-clean runs under churn; reclamation latency vs reader stall", vacuity_condition="no concurrent readers, or a garbage collector", trivial_shortcuts="never free (memory; the world must charge it)",
    cheat_control="a freer told exactly when the last reader leaves must reclaim immediately with zero faults; if the world scores never-free equally, memory is not charged", cost_class="CPU-scale", source_evidence="ck_epoch.c; record pressure 'reclamation hazards'", purpose="PURPOSE: same")
c.pressure("the_hardware_reorders_loads_and_stores_and_the_program_must_say_where_it_may_not",
    condition="different architectures give different guarantees; a primitive correct on x86 is wrong on ARM without fences", resource_or_constraint="the memory model",
    failure_condition="torn reads, lost updates (record)", world_punishes="unfenced publication", world_rewards="explicit acquire/release/lock/unlock fences at the primitive layer",
    observable_consequence="the ck_pr_fence_* calls in every organ", vacuity_condition="a sequentially consistent machine", trivial_shortcuts="full fences everywhere (slow)",
    cheat_control="N/A on x86 hardware (the pressure is invisible there); a world on a weak-memory machine is required", cost_class="unknown (needs non-x86 hardware)", source_evidence="ck_pr.h; the fence calls", purpose="PURPOSE: same")

c.residue("LARGE_RESIDUE", ["25 of 41 headers unread (hash tables, rwlocks, sequence lock, cohort locks, elision)", "hazard pointers by name only", "nothing ran; Techne's ck_ticket validate is on M1", "the epoch's actual advance rule (ck_epoch_synchronize_wait 425-527) skimmed, not read"],
          note="four shapes (backoff, shared-word lock, per-node lock, epoch reclamation) are read; the library is much wider")
c.save(state="COARSE")
