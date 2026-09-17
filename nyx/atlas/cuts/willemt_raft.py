"""Cut: willemt-raft (ancestry-aware, Stage A COARSE; SOURCE_READ on M3; fifth of the 2026-09-17 NOT_CUT order).
Read: src/raft_server.c 60-96 (timeout randomisation, raft_new), 146-270 (election start, become leader/candidate/follower,
periodic), 275-385 (append-entries response: next_idx backoff, match_idx, commit advance), 385-530 (append-entries receipt:
term rules, consistency check, truncation, commit follow), 530-575 (vote grant); include/raft.h grep for the message fields and
defaults. NOT read: raft_log.c, raft_node.c, snapshot code (1258-1435), requestvote receipt/response bodies (575-720),
raft_recv_entry, membership change paths, the tests and virtraft2.py. Nothing ran.
"""
from nyx.atlas.author import Cut

S = "vault:willemt-raft/upstream/tree/src/raft_server.c"
H = "vault:willemt-raft/upstream/tree/include/raft.h"
c = Cut("willemt-raft", mode="ANCESTRY_AWARE", inspected=["src/raft_server.c 60-96, 146-575", "include/raft.h (message structs, defaults; grep)"],
        evidence=[("SOURCE_READ", S + ":60-96"), ("SOURCE_READ", S + ":146-575"), ("SOURCE_READ", H)],
        note="a library implementation of the Raft paper (Ongaro & Ousterhout 2014) with the I/O externalised through callbacks; the mechanisms are the paper's rules as code, "
             "and the code carries a few choices the paper leaves open (randomisation range, single-node fast path, lazy apply, aggressive resend)")

et = c.organ("randomised_election_timeout_redrawn_on_every_role_change", human_name="raft_randomize_election_timeout (60-67); called at become_candidate/follower", status="ACCEPTED",
    mechanism="election_timeout_rand = T + rand() % T, i.e. uniform in [T, 2T) with T = 1000 ms default; redrawn each time the node becomes candidate or follower; raft_periodic accumulates elapsed ms and starts an election when it exceeds the draw (unless a snapshot is in progress); receipt of a valid append-entries resets the elapsed time",
    input="wall-clock deltas; role changes; valid leader traffic", output="an election start", state="election_timeout_rand, timeout_elapsed", update="per tick; per role change",
    assumptions=["rand() is good enough to break ties; the range [T,2T) is wide relative to message latency so split votes are rare"], fitness_value_in_ancestor="liveness: some node times out first and wins before the others notice",
    failure_landscape="UNKNOWN by run; by reading: a heartbeat period (request_timeout 200 ms) five times shorter than T keeps followers quiet", human_prior="the paper's randomisation; the specific [T,2T) range and the use of libc rand()",
    evidence_ref=S + ":60-67, 179-232", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two timeout fields and raft_periodic's else-branch",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "SEEDED_RANDOM", "update_topology": "EVENT_DRIVEN", "competition": "CONTENDS", "temporal_horizon": "WINDOW"})

term = c.organ("monotonic_term_with_unconditional_step_down_on_a_higher_term", human_name="term checks at 275-300, 400-420; raft_become_candidate 179-212", status="ACCEPTED",
    mechanism="every message carries the sender's term; a receiver with a lower term adopts it (persisted via callback) and becomes follower before doing anything else; a message with a lower term is answered false / ignored; becoming candidate increments the term, votes for self, clears other votes, and redraws the timeout",
    input="term fields of every message", output="a role change or a rejection", state="current_term, voted_for (both persisted)", update="per message",
    assumptions=["the persist callback flushes term and vote before the node acts on them (raft.h 300-313: MUST flush)"], fitness_value_in_ancestor="a stale leader can never be obeyed; the whole safety argument rests on this",
    failure_landscape="UNKNOWN by run", evidence_ref=S + ":179-212, 293-305, 404-420", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the term comparisons at the top of each receive routine",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "DURABLE", "stochasticity": "DETERMINISTIC", "cooperation": "AGREES"})

vote = c.organ("grant_at_most_one_vote_per_term_and_only_to_a_candidate_whose_log_is_at_least_as_up_to_date", human_name="__should_grant_vote (535-573)", status="ACCEPTED",
    mechanism="refuse if this node is non-voting, if the candidate's term is older, or if already voted this term; then compare logs: grant if own log is empty, or the candidate's last term is newer, or same last term and candidate's last index >= own; the own last term may come from the snapshot metadata when the log is compacted",
    input="a RequestVote (term, last_log_idx, last_log_term)", output="grant / refuse", state="voted_for (persisted)", update="per request",
    assumptions=["'up-to-date' by (last term, last index) is sufficient for the leader-completeness property (the paper's election restriction)"], fitness_value_in_ancestor="a leader always holds every committed entry, so no log is ever rewritten",
    failure_landscape="by reading: a TODO notes that re-granting to the same candidate is not implemented, so a lost grant costs a full timeout", evidence_ref=S + ":530-573", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="__should_grant_vote",
    coverage={"input_topology": "VECTOR", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "DURABLE", "stochasticity": "DETERMINISTIC", "cooperation": "AGREES", "competition": "ARBITRATES"})

ae = c.organ("log_consistency_check_by_previous_entry_term_with_truncation_of_conflicting_suffix", human_name="raft_recv_appendentries (385-528)", status="ACCEPTED",
    mechanism="a follower accepts a batch only if it holds an entry at prev_log_idx with term prev_log_term (or that index is its snapshot point with matching term); a mismatch deletes from prev_log_idx and answers false with its current index; on match, each incoming entry is compared with any existing entry at that index: a term conflict deletes the suffix (a conflict at or below the commit index is a fatal RAFT_ERR_SHUTDOWN), then the remainder is appended; finally commit_idx follows min(leader_commit, last index)",
    input="AppendEntries (term, prev_log_idx, prev_log_term, entries[], leader_commit)", output="success + current_idx, or failure + current_idx + first_idx", state="the log; commit_idx; current_leader; timeout_elapsed", update="per message",
    assumptions=["the log is index-dense from 1; entries are (term, data)", "a conflict below the commit index cannot happen if the invariants hold, so it is treated as corruption"],
    fitness_value_in_ancestor="the log matching property is maintained by induction on prev entry; followers converge to the leader's log by deletion and append", failure_landscape="UNKNOWN by run",
    evidence_ref=S + ":385-528", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="raft_recv_appendentries",
    coverage={"input_topology": "SEQUENCE", "output_topology": "DECISION", "state_amount": "UNBOUNDED", "state_persistence": "DURABLE", "stochasticity": "DETERMINISTIC", "recovery": "ROLLS_BACK", "cooperation": "AGREES"})

nx = c.organ("per_follower_next_index_backoff_using_the_follower_reported_index", human_name="raft_recv_appendentries_response failure branch (309-327)", status="ACCEPTED",
    mechanism="on a failed append: ignore if stale (follower's current_idx < match_idx); if the follower reports an index below next_idx-1 jump next_idx to min(follower_idx+1, own current) (the follower's log is short), else decrement by one (a term conflict); resend immediately",
    input="a failed AppendEntries response with current_idx", output="a new next_idx and a resend", state="per-node next_idx", update="per failed response",
    assumptions=["the follower's reported length is honest, so jumping is safe"], fitness_value_in_ancestor="catch-up in O(gap) messages for a short follower instead of O(gap) decrements", failure_landscape="UNKNOWN by run",
    human_prior="the paper's optional optimisation (report the conflicting index) done with the follower's log length only, not the conflicting term", evidence_ref=S + ":309-327", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the if (0 == r->success) block",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PER_EPISODE", "stochasticity": "DETERMINISTIC", "recovery": "RETRIES"})

cm = c.organ("commit_index_advanced_by_majority_match_only_for_entries_of_the_current_term", human_name="raft_recv_appendentries_response success branch (343-375)", status="ACCEPTED",
    mechanism="on a successful append the follower's match_idx and next_idx are set to its reported index; then, if that index is above commit_idx and the entry there has the CURRENT term, count the voting nodes whose match_idx reaches it (self counts); if more than half, commit_idx = that index; older-term entries are committed only indirectly, when a current-term entry above them commits",
    input="match_idx of every voting node; the term of the candidate entry", output="commit_idx", state="per-node match_idx; commit_idx", update="per successful response",
    assumptions=["counting replicas is unsafe for prior-term entries (the paper's Figure 8 scenario); the code implements the restriction literally"], fitness_value_in_ancestor="safety: a committed entry is never lost by a later leader",
    failure_landscape="UNKNOWN by run", evidence_ref=S + ":343-375", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the 'Update commit idx' block",
    coverage={"input_topology": "SET", "output_topology": "SCALAR", "state_amount": "LINEAR_IN_INPUT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "cooperation": "AGREES"})

hb = c.organ("leader_heartbeat_by_periodic_append_entries_and_lazy_apply_of_committed_entries", human_name="raft_periodic (222-268); raft_apply_all", status="ACCEPTED",
    mechanism="a leader sends append-entries to all when request_timeout (200 ms) has elapsed since its last send, which doubles as the heartbeat; on any node, if last_applied < commit_idx and applying is allowed, all committed entries are applied through the callback in the periodic tick, not in the message handler; a single voting node becomes leader immediately",
    input="ticks; commit_idx", output="heartbeats; applied entries", state="timeout_elapsed, last_applied_idx", update="per tick",
    assumptions=["the caller ticks often enough; applying is idempotent from the state machine's point of view"], fitness_value_in_ancestor="one timer serves heartbeat and election; apply is decoupled from network handling", failure_landscape="UNKNOWN by run",
    evidence_ref=S + ":222-268", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="raft_periodic",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN", "temporal_horizon": "STEP"})

c.reject("the callback vector raft_cbs_t (send, persist, log offer/pop, applylog) and the heap-function hooks", reason="INHERITED_FROM_RUNTIME_OR_LIBRARY", evidence=H + ":286-420; the library's I/O boundary, supplied by the host", note="the persistence contract (MUST flush) is an ASSUMPTION of the term organ, recorded there")
c.reject("snapshot begin/end/load, membership change (voting cfg entries, non-voting node promotion), raft_recv_entry, requestvote receive/response bodies, raft_log.c, raft_node.c", reason="OTHER", evidence="NOT READ this pass; residue")
c.reject("'Raft' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="election timeout, term discipline, vote restriction, log matching, next_idx backoff, commit rule and heartbeat are each separately replaceable and separately testable")
c.reject("__log tracing and the tests/virtraft2.py simulator", reason="OTHER", evidence="instruments; the simulator is a ready world for Stage C (not run)", note="an instrument, not a mechanism")

c.edge(et, term, "triggers", note="candidate: term+1"); c.edge(term, vote, "gates"); c.edge(vote, hb, "triggers", note="majority -> leader -> heartbeats"); c.edge(hb, ae, "feeds"); c.edge(ae, et, "restores", note="valid leader traffic resets the timer")
c.edge(ae, nx, "feeds", note="failure + current_idx"); c.edge(nx, ae, "retries"); c.edge(ae, cm, "feeds", note="success + current_idx"); c.edge(cm, hb, "feeds", note="commit_idx -> lazy apply"); c.edge(term, ae, "gates"); c.edge(term, cm, "gates", note="current-term entries only")

c.pressure("a_replicated_ordered_record_must_stay_consistent_when_any_minority_of_replicas_and_any_messages_can_be_lost_and_clocks_are_unsynchronised",
    condition="N organisms each hold a copy of an append-only record; clients submit entries to any; the world crashes and restarts any minority, delays and drops messages, and gives each organism only a local clock",
    resource_or_constraint="messages per entry; durable writes per role change; a bounded election gap", failure_condition="two replicas apply different entries at the same index, or a committed entry vanishes, or no progress while a majority is alive",
    world_punishes="split brain; lost commits; livelock of elections", world_rewards="an organism set that agrees on a single leader per epoch and only counts replication toward commitment under that epoch",
    observable_consequence="divergence count under injected partitions and crashes; time to first commit after a leader crash; messages per committed entry", vacuity_condition="N = 1, or a synchronous lossless network, or a world that supplies a leader",
    trivial_shortcuts="a fixed leader (dies on its crash); a world with a global clock and no loss", cheat_control="an organism handed a perfect failure detector and a global clock must commit every entry with no divergence at minimum messages; the ancestor with randomisation disabled (all timeouts equal) must show repeated split votes: if the world cannot show the livelock, it is not exerting the asynchrony pressure",
    cost_class="CPU-scale", source_evidence="raft_server.c 60-67, 385-528, 343-375; record domain consensus/leader-election/recovery", purpose="PURPOSE: replicated state machine consensus (Raft, Ongaro & Ousterhout 2014)")

c.pressure("competitors_must_break_symmetry_using_only_local_randomness_and_a_shared_timescale",
    condition="several equal organisms must elect one of themselves without a coordinator; they share only an approximate timescale; simultaneous attempts cancel", resource_or_constraint="attempts per election; the spread of the random draw versus the message delay",
    failure_condition="repeated simultaneous attempts (livelock) or an election gap much longer than the draw range", world_punishes="both", world_rewards="a draw whose spread exceeds the round-trip time and is redrawn per attempt",
    observable_consequence="elections needed per leader change as message delay is varied relative to the draw range", vacuity_condition="one competitor or a coordinator", trivial_shortcuts="static priorities (fails when the top priority dies)",
    cheat_control="organisms given distinct fixed offsets larger than the delay must elect in one round; organisms with zero spread must livelock for delay > 0: the world must show both",
    cost_class="CPU-scale", source_evidence="raft_server.c 60-67, 232-246", purpose="PURPOSE: randomised leader election timeouts (Raft)")

c.ancestry("algorithm_from", "Ongaro & Ousterhout 2014, In Search of an Understandable Consensus Algorithm (the code cites the paper's section numbers in comments)", note="from the source comments; the record's lineage not re-read")
c.residue("PARTIALLY_EXPLAINED", ["snapshotting, membership change and the vote request/response bodies were not read (about 700 of 1435 lines of raft_server.c); raft_log.c and raft_node.c not opened",
                                   "no claim was executed; tests/virtraft2.py is a ready world (a Python network simulator with partitions) for a SCOUT run"],
          note="the paper's five rules are each located at a line range; the library-specific choices (range [T,2T), length-based backoff, lazy apply, aggressive resend) are named")
c.save(state="COARSE")
