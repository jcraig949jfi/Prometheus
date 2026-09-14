"""Cut: glibc-rwlock-writer-starvation-2.36 (ancestry-aware; SOURCE_READ of the three nptl files + Techne's run receipt).
Read: pthread_rwlock_common.c lines 1-420 and 526-680 (design comment, rdunlock, rdlock_full64, wrlock_full64 head);
NOT read: 420-526 (rdlock tail: timed wait / cancellation), 680-950 (wrlock tail, wrunlock detail). Residue says so."""
from nyx.atlas.author import Cut

B = "F:/Prometheus/vault/fossils/glibc-rwlock-writer-starvation-2.36/upstream/"
c = Cut("glibc-rwlock-writer-starvation-2.36", mode="ANCESTRY_AWARE",
        inspected=["upstream/pthread_rwlock_common.c[1-420,526-680]", "harness/starve.c", "run/20260913T054149Z/runs-*.stdout.txt"],
        evidence=[("SOURCE_READ", B + "pthread_rwlock_common.c"),
                  ("EXECUTED", "techne receipt run/20260913T054149Z: PREFER_READER 8 readers 3 s -> writer 1 acquisition (0.3/s); PREFER_WRITER_NONRECURSIVE -> 1.65e6/s (Techne's run, not Nyx's)")],
        note="small fossil (3 files, 1034 lines); the pathology is the specimen; the anti-starvation gate is one flag path")

pw = c.organ("phase_word", human_name="__readers state word (WP/WL/R/RW)", status="ACCEPTED",
    human_interpretation="the single-writer-multiple-readers lock: which phase the lock is in and who is present",
    mechanism="one 32-bit word packs four fields -- a write-phase bit, a primary-writer bit, a readers-waiting bit and a reader count -- and every state change of the lock is one atomic read-modify-write on that word (fetch_add for readers, fetch_or for the writer bit, CAS for phase transfers), so the eight legal lock states are eight value classes of one integer",
    input="atomic RMW requests from reader/writer paths", output="the new word value (the caller reads its own success from the returned bits)",
    state="32-bit word: WP bit, WL bit, RW bit, R = count << 3", update="fetch_add(1<<3) register reader; fetch_or(WL) elect writer; CAS to flip WP on hand-over; CAS to set RW",
    assumptions=["fewer than 2^28 concurrent readers", "a single-word atomic RMW exists"], interface="the word is the lock; every other mechanism here reads or RMWs it",
    dependencies=["hardware atomic RMW"], fitness_value_in_ancestor="the whole lock's correctness rests on all transitions being single RMWs on one word; splitting the fields would need a second synchronisation",
    failure_landscape="reader-count overflow (guarded, see child); ABA on RW is declared harmless in the comment", decomposability="the four fields are not separable without a second lock (the comment argues this)",
    composability="any mechanism that can express its states as bit classes of one word", human_prior="named by glibc's own comment (state table #1-#8)",
    observability="the word is readable from a debugger/probe; no API exposes it", intervention_readiness="freeze/corrupt possible by patching the source; not tried",
    evidence_ref=B + "pthread_rwlock_common.c:63-95,275-330", confidence="HIGH that the word exists and is the sole lock state; MEDIUM on the exact transition set (tails unread)",
    portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="struct field __readers + all atomic ops on it",
    coverage={"input_topology": "EVENT", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "update_topology": "EVENT_DRIVEN", "stochasticity": "ENVIRONMENT_RANDOM", "competition": "ARBITRATES"})

c.organ("phase_word.overflow_guard", parent=pw, human_name="reader overflow check", mechanism="after registering, if the count field is at its limit, CAS the count back down and report EAGAIN; the undo is a CAS not a fetch_add because the undoing thread might be the last reader and then owes a hand-over",
    input="the post-registration word", output="EAGAIN or continue", state="none beyond the word", update="CAS decrement", assumptions=["fewer than 2^28 threads in practice"],
    fitness_value_in_ancestor="bounds a field that would otherwise wrap into the flag bits", failure_landscape="a wrap would corrupt WP/WL",
    evidence_ref=B + "pthread_rwlock_common.c:355-375", confidence="HIGH (read)", portability="YES", compatibility="N/A", utility="N/A", source_boundary="rdlock_full64 overflow while-loop",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "NONE", "failure_mode": "CORRUPTS"})

rr = c.organ("reader_register_optimistic", human_name="reader fast path", status="ACCEPTED",
    human_interpretation="acquiring a read lock costs one atomic add when other readers hold it",
    mechanism="a reader increments the count FIRST, unconditionally, and only then looks at the phase bit of the value it got back; if the lock was in a read phase it is already in, otherwise it is registered-but-waiting and must wait for hand-over or start a read phase itself if no primary writer exists",
    input="request to read-acquire", output="acquired / waiting", state="the phase word", update="fetch_add then branch on WP",
    assumptions=["registering before checking is safe because the count is part of the same word the writer inspects"],
    fitness_value_in_ancestor="read-mostly workloads are the declared design target; this is why reader preference is the default", failure_landscape="a registered-waiting reader prolongs the read phase for a writer -- the starvation mechanism when readers are preferred",
    evidence_ref=B + "pthread_rwlock_common.c:348-395", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="rdlock_full64 after the RWAITING block",
    coverage={"input_topology": "EVENT", "output_topology": "DECISION", "state_amount": "CONSTANT", "update_topology": "EVENT_DRIVEN", "competition": "CONTENDS", "order_sensitivity": "SENSITIVE"})

we = c.organ("primary_writer_election", human_name="WRLOCKED election", status="ACCEPTED",
    human_interpretation="only one of the concurrent writers becomes THE writer; others wait",
    mechanism="every arriving writer does fetch_or of one bit; the one that saw the bit clear is the primary writer, the rest register as waiting writers (count in a second word) and loop: retry the CAS when the bit clears, or accept a direct hand-over token",
    input="write-acquire request", output="primary / waiting", state="WL bit in the phase word; __writers count", update="fetch_or(WL); fetch_add(__writers)",
    assumptions=["one bit suffices because the count of writers lives elsewhere"], fitness_value_in_ancestor="serialises writers without a mutex; uncontended write is one RMW",
    failure_landscape="writer-writer contention is 'somewhat more costly' (comment) because the exact writer count is tracked",
    evidence_ref=B + "pthread_rwlock_common.c:611-660", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="wrlock_full64 fetch_or + for(;;) loop",
    coverage={"input_topology": "EVENT", "output_topology": "DECISION", "state_amount": "CONSTANT", "competition": "ARBITRATES", "update_topology": "EVENT_DRIVEN"})

ho = c.organ("explicit_phase_handover", human_name="explicit hand-over", status="ACCEPTED",
    human_interpretation="the last reader hands the lock to the waiting writer; a releasing writer hands it to the waiting readers",
    mechanism="the thread that flips the phase bit also, as a SEPARATE later step, writes the new phase into a dedicated wait word and wakes everyone blocked on it; every waiter is obliged to block on that word rather than spin on the state word, so that one final store by the hander-over is guaranteed to free all of them -- which is what makes it safe to destroy the lock the moment nobody holds it",
    input="a phase-ending release", output="a phase flip plus a wake of all waiters of the other class", state="__wrphase_futex (mirrors WP) with a FUTEX_USED bit", update="CAS phase bit on the state word, then exchange on the wait word, then futex_wake(INT_MAX) if USED was set",
    assumptions=["waiters never take the spin shortcut (a discipline, enforced by code shape not by the hardware)"],
    fitness_value_in_ancestor="POSIX allows destroying a lock as soon as nobody holds it; without the two-step hand-over a pending wake could touch freed memory",
    failure_landscape="a waiter that spins on the state word instead of the wait word breaks destruction safety (comment names this)",
    evidence_ref=B + "pthread_rwlock_common.c:96-121,256-272", confidence="HIGH on the mechanism; MEDIUM on completeness (wrunlock body unread)", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="rdunlock tail + wrunlock",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "cooperation": "COORDINATES", "update_topology": "EVENT_DRIVEN"})

c.organ("writer_writer_token_pass", human_name="WRHANDOVER", status="ACCEPTED",
    human_interpretation="a releasing writer passes the lock straight to a waiting writer, bypassing readers, when writers are preferred",
    mechanism="if registered waiting writers exist, the primary writer CASes a hand-over bit into the writers word instead of clearing its ownership bit; a registered waiter that clears the hand-over bit by CAS becomes primary without the phase ever leaving write; the last waiter to give up while the bit is set must take ownership",
    input="writer release with waiters registered", output="ownership transferred without a phase change", state="WRHANDOVER bit in __writers", update="CAS set by releaser; CAS clear by taker",
    assumptions=["writers preferred (policy flag)"], fitness_value_in_ancestor="fast writer-to-writer transfer; readers cannot slip in between writers",
    failure_landscape="a cancelling waiter must check the bit or the token is lost (comment)", evidence_ref=B + "pthread_rwlock_common.c:139-150,660-680",
    confidence="MEDIUM (take side read; give side in unread wrunlock)", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="__writers WRHANDOVER CAS pair",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "competition": "ARBITRATES", "cooperation": "COORDINATES"})

gate = c.organ("arrival_gate_for_dominant_class", human_name="RWAITING (PREFER_WRITER_NONRECURSIVE)", status="ACCEPTED",
    human_interpretation="new readers wait behind a waiting writer instead of joining the current read phase",
    mechanism="when a reader arrives during a read phase and sees that a primary writer is already waiting, it does NOT register in the count; it sets a waiting flag and blocks on the state word until the flag clears (the writer got in, or gave up); so the read phase can drain and the writer's turn comes; only active when the policy flag disallows recursive readers, because a recursive reader waiting behind a writer that waits for that same reader would deadlock",
    input="reader arrival while WL set and WP clear and R>0", output="the reader blocks without extending the phase", state="RW bit", update="CAS set RW; futex wait on the state word; cleared by whoever changes state out of #4a",
    assumptions=["no recursive read acquisition (declared by the kind flag)", "the writer eventually gets the phase"],
    fitness_value_in_ancestor="THIS is the anti-starvation machinery: Techne's run shows writer throughput 0.3/s -> 1.65e6/s when the flag enables it (8 readers)",
    failure_landscape="with recursive readers it deadlocks (hence opt-in); readers now wait behind writers -- the pressure moves, it does not vanish (reader acquisitions fell 21e6 -> 2.3e6 in the same run)",
    ablation="Techne's harness IS the switch ablation (kind flag on/off), executed by Techne; not yet varied by Nyx",
    evidence_grade="EXECUTED", evidence_ref="run/20260913T054149Z: kind=PREFER_READER writer_acquisitions=1; kind=PREFER_WRITER_NONRECURSIVE writer_acquisitions=4950536 (Techne)",
    confidence="HIGH that the gate exists and is the flag-dependent path; the throughput numbers are Techne's, one machine, 2 repeats", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="rdlock_full64 lines 297-345 (the PREFER_WRITER_NONRECURSIVE_NP block)",
    coverage={"input_topology": "EVENT", "output_topology": "DECISION", "state_amount": "CONSTANT", "competition": "ARBITRATES", "failure_mode": "STARVES", "order_sensitivity": "SENSITIVE"})

fu = c.organ("lazy_wake_flag", human_name="PTHREAD_RWLOCK_FUTEX_USED", status="ACCEPTED",
    human_interpretation="skip the wake syscall when nobody is asleep",
    mechanism="a wait word has three states -- cannot block, can block, someone may be blocked; a thread about to sleep CASes the third state in; a waker only issues the system call if it sees that state; several sleepers share one flag so the waker must assume more remain",
    input="sleep/wake intents", output="a syscall or nothing", state="one bit per wait word", update="CAS before sleep; test-and-clear on wake",
    assumptions=["a lost wake is impossible because the flag is set under the same conditions that make sleeping possible"], fitness_value_in_ancestor="avoids a syscall on every release in the uncontended case",
    failure_landscape="spurious wakes are accepted; the comment says the same scheme is in pthread_mutex_lock (an ancestry pointer inside glibc)",
    evidence_ref=B + "pthread_rwlock_common.c:152-162,193-200", confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="FUTEX_USED bit handling on __wrphase_futex and __writers_futex",
    coverage={"input_topology": "EVENT", "output_topology": "DECISION", "state_amount": "CONSTANT", "resource_dependence": "COMPUTE"})

c.organ("self_deadlock_detect", human_name="EDEADLK check", mechanism="compare the recorded owner id with the calling thread's id before acquiring; equal means the caller already holds it as writer, report an error instead of blocking forever",
    input="acquire request", output="EDEADLK or continue", state="__cur_writer (owner id)", update="load; compare", fitness_value_in_ancestor="turns one class of hang into an error code",
    evidence_ref=B + "pthread_rwlock_common.c:290-296,600-604", confidence="HIGH (read); LOW on whether it matters behaviourally -- never exercised by the harness", portability="YES", compatibility="N/A", utility="UNKNOWN",
    source_boundary="two 3-line checks", coverage={"input_topology": "EVENT", "output_topology": "DECISION", "state_amount": "CONSTANT", "failure_mode": "STALLS"})

# ---- rejected cuts (negative anatomy)
c.reject("spin-then-block back-off before CAS retry", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY",
         evidence=B + "pthread_rwlock_common.c: three '/* TODO Back-off. */' and one '/* TODO Spin first. */' comments; no code", note="the design names a mechanism the body does not contain; a reader of the comments alone would invent it")
c.reject("memory-ordering (acquire/release/relaxed) discipline", reason="GENERIC_LANGUAGE_MECHANICS",
         evidence="every atomic call site carries an MO annotation; it constrains the compiler/hardware, it is not a mechanism with state of its own", note="recorded because half the comment volume is about it")
c.reject("futex wait/wake", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY", evidence="futex_wake / __futex_abstimed_wait64 are kernel primitives; the fossil's contribution is WHEN to call them (lazy_wake_flag), not the sleep itself")
c.reject("the kind flag (PREFER_READER vs PREFER_WRITER_NONRECURSIVE)", reason="OTHER",
         evidence="__data.__flags is read at two sites and chooses whether arrival_gate and writer_writer_token_pass run; it has no update of its own -- it is POLICY selecting mechanisms, recorded as composition edges ENVIRONMENT gates ...")

# ---- composition
c.edge(rr, pw, "updates"); c.edge(we, pw, "updates"); c.edge(ho, pw, "updates"); c.edge(gate, pw, "updates")
c.edge(gate, rr, "suppresses", note="a gated reader never reaches the register step until the flag clears")
c.edge(ho, fu, "gates", note="hand-over issues the wake only if the flag says someone may sleep")
c.edge("ENVIRONMENT", gate, "gates", note="kind flag enables the gate")
c.edge("ENVIRONMENT", "writer_writer_token_pass", "gates", note="kind flag enables direct writer hand-over")
c.edge(we, "writer_writer_token_pass", "feeds", note="registered losers of the election are the token's recipients")
c.edge(rr, ho, "triggers", note="the last reader out performs the hand-over")

# ---- pressures (stated without organ names)
c.pressure("asymmetric_contention_dominant_class_starves_minority",
    condition="one shared resource; two classes of users; the numerous class can share it among themselves, the rare class needs it alone; the numerous class re-arrives continuously",
    resource_or_constraint="exclusive access for the rare class", failure_condition="the rare class never obtains access while the numerous class keeps arriving",
    world_punishes="updates that never land; unbounded wait for the rare class", world_rewards="the numerous class if admitted freely (throughput), the rare class if admitted at all",
    observable_consequence="Techne run: 8 continuous readers, 3 s: writer got in ONCE under the default policy", vacuity_condition="no writer, or readers that pause",
    trivial_shortcuts="make everyone exclusive (kills the reader throughput the lock exists for)", cheat_control="measure BOTH classes' acquisition counts, not writer alone (the same run shows reader acquisitions fall 9x when writers are preferred)",
    cost_class="throughput of the dominant class traded for progress of the rare class", source_evidence="record.human_failure_condition + run receipt", purpose="PURPOSE: let many threads read a structure concurrently while writers update it safely")
c.pressure("destroy_as_soon_as_free",
    condition="a synchronisation object may be freed by its owner the instant no thread holds or will acquire it, yet a releasing thread may still owe wake-ups to sleepers",
    resource_or_constraint="memory of the lock object", failure_condition="a wake-up touches freed memory", world_punishes="use-after-free in the releaser", world_rewards="a hand-over protocol whose final store is the last touch",
    observable_consequence="the two-step phase flip + separate wait word in the source", vacuity_condition="lock lifetime managed elsewhere (never destroyed under contention)", trivial_shortcuts="never free locks", cheat_control="UNKNOWN (not measurable from the harness)",
    cost_class="an extra store and a discipline on waiters", source_evidence=B + "pthread_rwlock_common.c:96-121", purpose="PURPOSE: POSIX conformance of destruction semantics")
c.pressure("syscall_cost_on_uncontended_release",
    condition="waking sleepers costs a kernel transition; most releases have no sleepers", resource_or_constraint="CPU time per release", failure_condition="a release always pays the syscall",
    world_punishes="latency on the common path", world_rewards="knowing whether anyone sleeps before calling", observable_consequence="FUTEX_USED bit in two wait words", vacuity_condition="always contended",
    trivial_shortcuts="never wake (deadlock)", cheat_control="count syscalls per release with and without sleepers (not run)", cost_class="one extra CAS before sleeping", source_evidence=B + "pthread_rwlock_common.c:152-162", purpose="PURPOSE: fast uncontended locking")

c.residue("PARTIALLY_EXPLAINED", ["rdlock tail (lines 420-526): timed wait, cancellation, the read-phase start CAS loop -- not read",
                                  "wrunlock and wrlock tail (680-950): the give side of the token pass and the write->read hand-over -- not read",
                                  "__cur_writer maintenance (where set/cleared) not traced",
                                  "whether the harness's system glibc (Debian 12 = 2.36) matches the preserved source byte-for-byte is Techne's claim, not checked by Nyx"],
          note="9 organs account for the two acquisition paths and the two policy modes as described in the design comment; the release paths are asserted from the comment, not the code")
c.save(state="DEEP")
