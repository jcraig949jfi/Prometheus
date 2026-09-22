"""Cut: dmtcp-3.1.2 (ancestry-aware, Stage A COARSE; SOURCE_READ dmtcp_coordinator.cpp 365-530 and 1222-1253, threadlist.cpp 356-536,
writeckpt.cpp 73-180 + function list, mtcp/mtcp_restart.c function list + 112-330 skimmed, plugin/ipc/socket/kernelbufferdrainer.cpp 1-120 +
function list, connectionrewirer.cpp function list, include/virtualidtable.h 43-270 (signatures), dmtcp_launch.cpp 460-480/747-750,
syscallsreal.c 202-260, socketconnlist.cpp event switch). 506 files; the alloc / dl / timer / svipc plugins were NOT read."""
from nyx.atlas.author import Cut

T = "vault:dmtcp-3.1.2/upstream/tree/dmtcp-3.1.2/src/"
c = Cut("dmtcp-3.1.2", mode="ANCESTRY_AWARE",
        inspected=["dmtcp_coordinator.cpp (barrier + state aggregation)", "threadlist.cpp (ckpt thread, suspendThreads)", "writeckpt.cpp", "mtcp/mtcp_restart.c (function list, args, restore)", "plugin/ipc/socket/kernelbufferdrainer.cpp", "plugin/ipc/socket/connectionrewirer.cpp (signatures)", "include/virtualidtable.h", "dmtcp_launch.cpp (LD_PRELOAD)", "syscallsreal.c", "plugin/ipc/socket/socketconnlist.cpp (event switch)"],
        evidence=[("SOURCE_READ", T + "dmtcp_coordinator.cpp"), ("SOURCE_READ", T + "threadlist.cpp"), ("SOURCE_READ", T + "writeckpt.cpp"), ("SOURCE_READ", T + "mtcp/mtcp_restart.c"), ("SOURCE_READ", T + "plugin/ipc/socket/kernelbufferdrainer.cpp")],
        note="transparent distributed checkpoint/restart; a large body cut at subsystem grain -- ten mechanisms named, four plugins unread")

bar = c.organ("coordinator.barrier_released_when_every_registered_worker_reports_it", human_name="coordinator barrier / global cut", status="ACCEPTED",
    human_interpretation="all processes reach the same phase before any goes on, so the set of checkpoints is consistent",
    mechanism="each worker sends the name of the barrier it reached; the coordinator asserts every arrival names the SAME barrier, counts arrivals, and when the count equals the number of registered peers broadcasts DMT_BARRIER_RELEASED with that name; the coordinator's view of the fleet is the min and max of per-client WorkerState (RUNNING, SUSPENDED, ..., CHECKPOINTED, RESTARTING) recomputed on every message",
    input="DMT_BARRIER messages (name), client states", output="DMT_BARRIER_RELEASED broadcasts; minimumState/maximumState", state="currentBarrier, workersAtCurrentBarrier, per-client state, numPeers", update="per message",
    assumptions=["one coordinator process reachable by all; peers never disagree on the next barrier name"], fitness_value_in_ancestor="the consistency of a multi-process checkpoint rests here", failure_landscape="UNKNOWN by run; by reading: a peer that dies mid-barrier is handled by threadIsDead on the worker side, at the coordinator by numPeers accounting (not read in full)",
    evidence_ref=T + "dmtcp_coordinator.cpp:465-530,1222-1253; dmtcpmessagetypes.h eWorkerState", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="processBarrier + releaseBarrier + getStatus",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "cooperation": "COORDINATES", "update_topology": "EVENT_DRIVEN"})

ct = c.organ("worker.checkpoint_thread_loop_anchored_by_a_saved_context", human_name="the checkpoint thread (sleep -> suspend -> write -> resume), getcontext anchor", status="ACCEPTED",
    mechanism="a dedicated thread blocks all signals but glibc's internal ones, saves its own register context ONCE (getcontext / sigsetjmp) and its stack pointer, then loops: wait for a checkpoint request from the coordinator, suspend all user threads, run pre-checkpoint hooks, save TLS and signal state, write the image, resume; on RESTART the restorer jumps back to the saved context, the originalstartup flag is false, so the thread waits for the other threads to be restored and re-enters the loop",
    input="checkpoint requests", output="a checkpoint image; resumed threads", state="ckptThread->savctx / jmpbuf, saved_sp, originalstartup", update="per checkpoint / per restart", assumptions=["the thread's frame is never left, so its locals are valid targets for a jump from a different process incarnation"],
    fitness_value_in_ancestor="the single point where 'time restarts' for the process", evidence_ref=T + "threadlist.cpp:356-455", confidence="HIGH", portability="UNKNOWN", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="checkpointhread()",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "DURABLE", "recovery": "ROLLS_BACK", "temporal_horizon": "UNBOUNDED"})

st = c.organ("worker.stop_every_other_thread_by_signal_with_rescan_until_quiescent", human_name="suspendThreads / stopthisthread", status="ACCEPTED",
    mechanism="take the thread-list lock; loop: for each thread not the ckpt thread, by state: RUNNING -> CAS to SIGNALED and tgkill the checkpoint signal (ESRCH marks it dead); SIGNALED -> probe with signal 0 and rescan; SUSPINPROG/SUSPENDED -> count; repeat until no rescan needed; each signalled thread runs stopthisthread, saves its context and blocks on a semaphore; four documented cases of who sent the signal (comment 560-580)",
    input="activeThreads list", output="all user threads in ST_SUSPENDED with saved contexts", state="per-thread state enum, numUserThreads, threadResumeLock", update="per checkpoint", assumptions=["a thread in a syscall will be interrupted by the signal; the wrappers make interrupted calls safe (not read)"],
    evidence_ref=T + "threadlist.cpp:456-536,560-600", confidence="HIGH", portability="UNKNOWN", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="ThreadList::suspendThreads + stopthisthread",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SWEEP", "competition": "ARBITRATES"})

wr = c.organ("ckpt.memory_image_from_proc_self_maps_with_area_headers_and_zero_page_elision", human_name="mtcp_writememoryareas", status="ACCEPTED",
    mechanism="parse /proc/self/maps into Areas; special-case nscd shared areas (remapped private), vdso/vvar, the restorer's own region; for each area write a header (address, size, prot, flags, name, offset) then the bytes; anonymous areas are scanned page-range by page-range and all-zero ranges are recorded as zero instead of written",
    input="the process address space", output="a sequential image file", state="none beyond the area list", update="per checkpoint", assumptions=["/proc/self/maps is complete and stable while threads are stopped"],
    evidence_ref=T + "writeckpt.cpp:73-180,408-525; procselfmaps.cpp", confidence="MEDIUM", portability="UNKNOWN", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="writeckpt.cpp",
    coverage={"input_topology": "SEQUENCE", "output_topology": "SEQUENCE", "state_amount": "LINEAR_IN_INPUT", "update_topology": "SWEEP"})

rs = c.organ("restart.self_relocating_restorer_unmaps_the_host_process_and_remaps_the_image", human_name="mtcp_restart", status="ACCEPTED",
    mechanism="a statically linked restorer with its own syscall layer (mtcp_sys.h) reads the image header, moves itself to a reserved address range that no image area overlaps (remapMtcpRestartToReservedArea, mremap_move), switches to a new stack, unmaps every region of the current process except itself (compute_regions_to_munmap), mmaps each image area at its recorded address (mmapfile / readmemoryareas), restores brk and vdso/vvar, flushes the icache on ARM, and jumps into the checkpoint thread's saved context",
    input="the image file, argv", output="the resumed process", state="RestoreInfo", update="once per restart", assumptions=["addresses in the image are still mappable (no ASLR collision; vdso relocation handled 624-760)"],
    fitness_value_in_ancestor="the only code that runs while the process is 'nobody' -- it cannot use libc", failure_landscape="UNKNOWN by run; by reading: an image area overlapping the restorer or the vdso is the designed failure surface (doAreasOverlap, validateRestoreBufferLocation)",
    evidence_ref=T + "mtcp/mtcp_restart.c:66-101,112-330,570-760", confidence="MEDIUM", portability="NO", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="mtcp/ directory",
    coverage={"input_topology": "SEQUENCE", "output_topology": "EVENT", "state_amount": "CONSTANT", "recovery": "ROLLS_BACK", "resource_dependence": "MEMORY"})

ip = c.organ("interposition.preloaded_wrappers_resolving_the_real_call_by_dlsym", human_name="LD_PRELOAD wrappers / _real_* table", status="ACCEPTED",
    mechanism="dmtcp_launch sets LD_PRELOAD to the plugin libraries plus libdmtcp.so; each wrapped libc/syscall function is redefined; the real one is looked up once (dlsym RTLD_NEXT style, syscallsreal.c initialize_libc_wrappers) into a table; a wrapper takes the DMTCP lock, translates ids, records fds/sockets/pids, calls _real_X, and dispatches plugin events",
    input="every wrapped call from the application", output="the same call, observed and translated", state="the _real_ function table; per-subsystem bookkeeping", update="per call", assumptions=["the application is dynamically linked and does not bypass libc (record: dmtcp_nocheckpoint / static binaries are the known hole)"],
    fitness_value_in_ancestor="transparency: the application is never modified", evidence_ref=T + "dmtcp_launch.cpp:460-480,747-750; syscallsreal.c:202-260; *wrappers.cpp by name", confidence="MEDIUM", portability="NO", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="syscallsreal.c + the wrapper files",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "update_topology": "EVENT_DRIVEN"})

vt = c.organ("virtualization.stable_virtual_ids_mapped_to_kernel_ids_and_remapped_after_restart", human_name="VirtualIdTable / VirtualPidTable", status="ACCEPTED",
    mechanism="a template table virtual<->real with updateMapping; the application only ever sees virtual pids/tids/ipc ids (the wrappers translate both ways); after restart, when the kernel hands out new real ids, the table is updated and the application's ids stay valid",
    input="real ids from the kernel; virtual ids from the application", output="the other one", state="the map", update="on create / on restart", assumptions=["every path by which an id can reach the application is wrapped"],
    evidence_ref=T + "../include/virtualidtable.h:43-270; plugin/pid/virtualpidtable.h:38-61", confidence="MEDIUM", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="virtualidtable.h + plugin/pid",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "DURABLE", "memory": "FULL_HISTORY"})

dr = c.organ("ipc.drain_kernel_socket_buffers_through_a_cookie_and_refill_after_resume", human_name="KernelBufferDrainer", status="ACCEPTED",
    mechanism="before the snapshot, for every TCP connection to another checkpointed process: send a magic cookie string through the socket and read from it until the cookie arrives, storing everything read (the in-kernel bytes now live in user memory, which the image captures); send buffers are scaled to make room; after resume/restart refillAllSockets writes the stored bytes back; sockets to external processes are not drained (577)",
    input="the set of connections", output="_drainedData per connection", state="_drainedData", update="per checkpoint", assumptions=["both ends are under DMTCP so the cookie is consumed, never delivered to the application"],
    fitness_value_in_ancestor="state the process does not own is pulled inside the process boundary", evidence_ref=T + "plugin/ipc/socket/kernelbufferdrainer.cpp:1-120,171-260; socketconnection.cpp:516-580", confidence="MEDIUM", portability="UNKNOWN", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="KernelBufferDrainer",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "hidden_state": "ESTIMATES", "recovery": "ROLLS_BACK"})

rw = c.organ("ipc.reconnect_sockets_by_identifier_exchange_through_the_coordinator_name_service", human_name="ConnectionRewirer", status="CANDIDATE",
    mechanism="after restart each side opens a restore socket, registers its incoming/outgoing connection identifiers and address with the coordinator's key-value service (registerNSData / sendQueries), learns the peer's new address, reconnects, and the old fd is dup'd onto the new socket (doReconnect)",
    input="connection identifiers, coordinator kv service", output="re-established fds", state="pending incoming/outgoing maps", update="once per restart", evidence_ref=T + "plugin/ipc/socket/connectionrewirer.cpp:69-340 (signatures read, bodies skimmed)", confidence="LOW",
    portability="UNKNOWN", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="connectionrewirer.cpp + kvdb.cpp / lookup_service.cpp (not read)",
    coverage={"input_topology": "SET", "output_topology": "SET", "cooperation": "COORDINATES"})

ev = c.organ("plugin.fixed_event_sequence_with_registered_hooks", human_name="DMTCP_EVENT_* dispatch", status="CANDIDATE",
    mechanism="the checkpoint cycle emits a fixed vocabulary of events (INIT, PRECHECKPOINT, RESUME, RESTART, CLOSE_FD, DUP_FD, VFORK_*...); each plugin switches on them (socketconnlist.cpp 27-70); the pluginmanager calls them in registration order -- not read",
    input="phase transitions", output="hook invocations", state="plugin list", update="per phase", evidence_ref=T + "plugin/ipc/socket/socketconnlist.cpp:27-70; pluginmanager.cpp by name", confidence="LOW", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN", source_boundary="pluginmanager.cpp",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT"})

c.reject("'DMTCP' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="four processes (coordinator, launch, the preloaded library, the restorer) with distinct address spaces and lifetimes")
c.reject("JASSERT / JTRACE / jalib", reason="GENERIC_LANGUAGE_MECHANICS", evidence="jalibinterface.cpp; logging and assertion macros used everywhere")
c.reject("dmtcp_command CLI", reason="OTHER", evidence=T + "dmtcp_command.cpp -- sends one message to the coordinator; an interface, not machinery", note="the record's entry point; Stage C drives it")
c.reject("configure / Makefile / cpplint", reason="GENERIC_LANGUAGE_MECHANICS", evidence="build system; util/cpplint.py is 237 KB of style checker")
c.reject("alloc / dl / timer / svipc plugins", reason="OTHER", evidence="NOT READ -- listed under plugin/; their anatomy is UNKNOWN, not rejected on merit", note="residue")

c.edge(bar, ct, "triggers", note="the request the ckpt thread waits for; barriers between phases"); c.edge(ct, st, "triggers"); c.edge(st, wr, "gates", note="image written only when all threads are suspended")
c.edge(ct, wr, "feeds", note="ckpt thread context + TLS + sigstate go into the image"); c.edge(wr, rs, "stores", note="the image"); c.edge(rs, ct, "restores", note="jump to savctx")
c.edge(ip, vt, "feeds", note="wrappers translate through the table"); c.edge(ip, dr, "feeds", note="socket wrappers register connections"); c.edge(ip, ev, "triggers", note="CLOSE_FD / DUP_FD events")
c.edge(ev, dr, "schedules", note="PRECHECKPOINT -> drain; RESUME/RESTART -> refill"); c.edge(ev, rw, "schedules"); c.edge(bar, rw, "feeds", note="name service"); c.edge(rs, vt, "updates", note="new real ids after restart")
c.edge("ENVIRONMENT", rs, "gates", note="ASLR / vdso placement decides whether the image can be mapped")

c.pressure("a_long_computation_must_survive_the_death_of_its_host_without_having_been_written_to",
    condition="work runs for hours on machines that fail or are reclaimed; the program has no save/restore of its own and cannot be modified", resource_or_constraint="time-limited allocations; partial failure",
    failure_condition="hours lost at a crash; or a restart that silently diverges (record)", world_punishes="recomputation from zero; divergence after restore", world_rewards="capturing all state that determines the future and reinstating it exactly",
    observable_consequence="the record's oracle: a counter resumes at the checkpointed value, not zero", vacuity_condition="no failures; or programs that already checkpoint themselves", trivial_shortcuts="rerun from the start (correct, pays the full cost); the world must charge for lost work",
    cheat_control="a program that persists its own counter to a file must pass the oracle without DMTCP; if the world rewards it equally, the world measures persistence, not transparency", cost_class="CPU-scale (a container)", source_evidence="record human_environmental_pressure / failure condition", purpose="PURPOSE: fault tolerance for unmodified programs")
c.pressure("the_environment_renames_everything_between_two_incarnations",
    condition="identifiers the program holds (pids, tids, fds, addresses, ports) are assigned by the OS and differ in the new incarnation while the program's memory still holds the old ones", resource_or_constraint="OS naming is not under the program's control",
    failure_condition="a restored program signals the wrong pid, writes to a closed fd, connects to a dead address", world_punishes="holding raw environment names", world_rewards="an indirection layer that owns the names the program sees and remaps them",
    observable_consequence="post-restart calls succeed or fail", vacuity_condition="an OS that preserves ids across restart (none does)", trivial_shortcuts="never use ids (impossible for real programs)",
    cheat_control="a program that only ever uses names DMTCP virtualises must restart cleanly; one that smuggles a raw pid through shared memory must fail -- the world can tell", cost_class="CPU-scale", source_evidence="virtualidtable.h; plugin/pid", purpose="PURPOSE: same")
c.pressure("state_the_process_does_not_own_must_be_pulled_inside_before_the_snapshot",
    condition="bytes in flight live in the kernel (socket buffers) and in peers, invisible to a memory image", resource_or_constraint="the process boundary is narrower than the computation's state",
    failure_condition="a restart that loses or duplicates in-flight messages", world_punishes="snapshots of the process alone", world_rewards="a protocol that flushes external state into the process (cookie-drain) and replays it after",
    observable_consequence="message counts before and after restart", vacuity_condition="no communication", trivial_shortcuts="quiesce the whole application first (needs cooperation the pressure forbids)",
    cheat_control="a pair of processes given a shared flush-and-replay must show byte-identical streams across restart", cost_class="CPU-scale", source_evidence="kernelbufferdrainer.cpp", purpose="PURPOSE: same")
c.pressure("many_processes_need_one_consistent_cut_without_a_global_clock",
    condition="a checkpoint of a distributed computation is only useful if no message is recorded as received but not sent; processes have no shared clock", resource_or_constraint="asynchrony",
    failure_condition="orphan / lost messages on restart", world_punishes="independent per-process snapshots", world_rewards="a barrier protocol (a coordinator counting arrivals, or its distributed equivalent)",
    observable_consequence="consistency of the restored fleet", vacuity_condition="one process", trivial_shortcuts="stop the world by an external signal (works if all processes are on one host)",
    cheat_control="a fleet with a known-consistent cut injected must restart cleanly; a fleet snapshotted at random times must sometimes fail -- if it never does, the world is not exercising the pressure", cost_class="CPU-scale", source_evidence="dmtcp_coordinator.cpp barrier logic", purpose="PURPOSE: same")

c.residue("LARGE_RESIDUE", ["four plugins (alloc, dl, timer, svipc) unread", "file-descriptor virtualization for files / pipes / ptys (plugin/ipc/file, event) unread", "kvdb / lookup_service (the coordinator's name service) unread", "signal wrappers, exec wrappers (how a checkpointed process forks and execs) unread", "nothing ran; Techne's counter oracle is on M1"],
          note="ten mechanisms cover the checkpoint/restart cycle; the wrapper corpus (dozens of files) is characterised only by its shape")
c.save(state="COARSE")
