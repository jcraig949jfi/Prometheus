"""Cut: hashicorp-memberlist-0.5.4 (ancestry-aware, Stage A COARSE; SOURCE_READ state.go probeNode 305-420 (grepped), gossip 590-647, aliveNode
943-1000 (grepped); suspicion.go 1-80; awareness.go 20-60; queue.go / util.go retransmitLimit; file list). SWIM with Lifeguard, Go."""
from nyx.atlas.author import Cut

S = "vault:hashicorp-memberlist-0.5.4/upstream/tree/memberlist-0.5.4/"
c = Cut("hashicorp-memberlist-0.5.4", mode="ANCESTRY_AWARE", inspected=["state.go (probeNode, gossip, aliveNode, pushPull index)", "suspicion.go", "awareness.go", "queue.go + util.go retransmitLimit", "file list"],
        evidence=[("SOURCE_READ", S + "state.go"), ("SOURCE_READ", S + "suspicion.go"), ("SOURCE_READ", S + "awareness.go"), ("SOURCE_READ", S + "util.go")],
        note="SWIM's three mechanisms (random probe, indirect probe, gossip piggyback) plus Lifeguard's three refinements (self-awareness scaling, log-scaled suspicion timeout with confirmations, buddy suspicion) -- each a separately ablatable organ; the record's entry point ablates two of them")

pr = c.organ("periodic_probe_of_one_random_member_with_indirect_ping_via_k_others_on_timeout", human_name="probe / probeNode (SWIM failure detector)", status="ACCEPTED",
    mechanism="every ProbeInterval (scaled by awareness) pick the next node of a shuffled ring; send a UDP ping with a sequence number and wait ProbeTimeout for the ack; on timeout ask IndirectChecks (3) random other members to ping it on our behalf (they reply ack or nack), and also try a TCP ping; if nothing comes back within the interval, broadcast a suspect message for the node's current incarnation",
    input="the member list; acks/nacks", output="suspect messages; awareness deltas", state="the probe index / shuffled order, pending ack channels keyed by seqno", update="per interval", assumptions=["UDP loss is common and independent; an indirect path distinguishes 'it is dead' from 'my link is bad'"],
    fitness_value_in_ancestor="constant per-node load regardless of cluster size (SWIM's claim); the record's oracle asserts the suspect -> dead transitions", evidence_ref=S + "state.go:232-420", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="probe / probeNode / probeNodeByAddr + setProbeChannels",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "feedback": "DELAYED_CLOSED_LOOP", "stochasticity": "SEEDED_RANDOM", "hidden_state": "ESTIMATES", "temporal_horizon": "WINDOW"})

aw = c.organ("self_awareness_score_scaling_own_timeouts_from_probe_outcomes", human_name="awareness.go ApplyDelta / ScaleTimeout (Lifeguard 'local health')", status="ACCEPTED",
    mechanism="an integer score in [0, max): a probe that got a direct ack subtracts 1, a nack from an indirect helper adds 1, a full miss adds more; ScaleTimeout multiplies ProbeInterval / ProbeTimeout by (score + 1), so a node whose own probes keep failing slows itself down instead of declaring others dead",
    input="probe outcomes", output="a timeout multiplier", state="score", update="per probe", assumptions=["my failures are more likely my fault than everyone else's"], fitness_value_in_ancestor="Lifeguard's fix for false positives from a slow/overloaded prober",
    evidence_ref=S + "awareness.go:20-70; state.go:305-330 (ScaleTimeout, ApplyDelta)", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="awareness.go",
    coverage={"input_topology": "EVENT", "output_topology": "SCALAR", "state_amount": "CONSTANT", "adaptation": "PARAMETER", "feedback": "CLOSED_LOOP", "memory": "SUMMARY_STATISTIC"})

su = c.organ("suspicion_timer_shrinking_logarithmically_with_independent_confirmations", human_name="suspicion.go remainingSuspicionTime / Confirm", status="ACCEPTED",
    mechanism="a suspected node gets a timer between min and max: timeout = max - (log(n + 1) / log(k + 1)) * (max - min), where n is the number of DISTINCT members that have also reported it suspect and k the expected number; each new confirmer (Confirm dedups by name) re-evaluates the remaining time; at expiry the node is declared dead; min = SuspicionMult * log10(cluster size) * ProbeInterval",
    input="suspect messages from peers", output="a dead declaration at the timer's end", state="n, the confirmations set, start time", update="per confirmation", assumptions=["independent confirmations are evidence; one suspicious reporter is not"],
    fitness_value_in_ancestor="Lifeguard's second fix: fewer false positives at the cost of slower detection when only one node notices", evidence_ref=S + "suspicion.go:1-80", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="suspicion.go",
    coverage={"input_topology": "EVENT", "output_topology": "DECISION", "state_amount": "CONSTANT", "temporal_horizon": "WINDOW", "uncertainty": "SAMPLE", "cooperation": "AGREES"})

inc = c.organ("incarnation_numbers_letting_a_node_refute_its_own_suspicion", human_name="aliveNode / suspectNode: Incarnation", status="ACCEPTED",
    mechanism="every membership message carries the subject's incarnation; a node that hears itself suspected (or dead) increments its own incarnation and broadcasts alive with the new number, which supersedes the suspicion; older-incarnation messages are ignored; conflicting alive messages for the same name from different addresses are refused (conflict delegate)",
    input="alive/suspect/dead messages", output="state transitions; refutations", state="per-node incarnation, state, StateChange time", update="per message", evidence_ref=S + "state.go:943-1000,1160-1252", confidence="MEDIUM", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="aliveNode / suspectNode / deadNode",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "memory": "LAST_VALUE", "order_sensitivity": "INVARIANT"})

gs = c.organ("gossip_of_membership_changes_piggybacked_to_k_random_nodes_with_a_log_scaled_retransmit_limit", human_name="gossip / TransmitLimitedQueue / retransmitLimit", status="ACCEPTED",
    mechanism="every GossipInterval send the pending broadcasts (as a compound UDP packet within a byte budget) to GossipNodes (3) random live or recently-dead members; a broadcast leaves the queue after RetransmitMult * ceil(log10(n + 1)) transmissions; the queue is a b-tree ordered by transmits-so-far then size, so fresh messages go first; newer messages about the same node invalidate older ones",
    input="membership events", output="UDP packets", state="the transmit-limited queue", update="per interval", assumptions=["O(log n) rounds of random fan-out reach everyone with high probability (epidemic dissemination)"],
    evidence_ref=S + "state.go:590-647; queue.go; util.go:76-81", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="gossip + queue.go + broadcast.go",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "LINEAR_IN_INPUT", "stochasticity": "SEEDED_RANDOM", "resource_dependence": "BANDWIDTH", "cooperation": "SHARES"})

pp = c.organ("periodic_full_state_push_pull_over_tcp_with_a_random_peer", human_name="pushPull / pushPullNode / mergeState", status="CANDIDATE",
    mechanism="every PushPullInterval (scaled by cluster size) open a TCP stream to one random member, exchange complete member lists, and merge (aliveNode/suspectNode/deadNode per entry); also used at Join -- an anti-entropy repair for what gossip missed (index and signatures)", input="the full state", output="a merged state", state="none", update="per interval",
    evidence_ref=S + "state.go:186-231,648-700 (index)", confidence="LOW", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="pushPull*",
    coverage={"input_topology": "SET", "output_topology": "SET", "state_amount": "LINEAR_IN_INPUT", "cooperation": "SHARES", "recovery": "SELF_RESETS"})

c.reject("transport / net_transport / mock_transport / peeked_conn / label / security / keyring (encryption)", reason="GENERIC_LANGUAGE_MECHANICS", evidence="by file name: I/O, framing, AES-GCM wrapping of packets", note="security.go would be an instance of tiny-aes-c's mode organ (GCM) -- not read")
c.reject("delegates (alive, conflict, event, merge, ping) and logging", reason="OTHER", evidence="hook interfaces for the embedding application; the record's tests use them as observers", note="interfaces, not machinery")
c.reject("'SWIM' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="probe, gossip and push-pull run on separate timers with separate state; Lifeguard added three more mechanisms without touching the others")
c.reject("the test suite", reason="EFFECT_FROM_ENVIRONMENT", evidence="Techne's oracle is go test's assertions")

c.edge(aw, pr, "updates", note="scales interval and timeout"); c.edge(pr, aw, "feeds", note="deltas"); c.edge(pr, su, "triggers", note="suspect broadcast"); c.edge(gs, su, "feeds", note="confirmations arrive by gossip"); c.edge(su, gs, "feeds", note="dead broadcast")
c.edge(inc, su, "suppresses", note="a refutation cancels the timer"); c.edge(gs, inc, "feeds"); c.edge(inc, gs, "feeds", note="alive with a higher incarnation"); c.edge(pp, inc, "feeds", note="merge applies the same transitions"); c.edge(pp, gs, "competes", note="anti-entropy vs epidemic")

c.pressure("membership_must_be_agreed_by_thousands_of_nodes_with_no_central_authority_over_a_lossy_network",
    condition="nodes join, leave and crash; messages are lost; no node may pay more than a constant per round; a false 'dead' evicts a healthy node and a slow 'dead' leaves a ghost", resource_or_constraint="O(1) messages per node per period; UDP loss; clock-free",
    failure_condition="false positives from a slow prober or a lossy link; unbounded detection time", world_punishes="heartbeats to everyone (O(n^2)); trusting one missed ack", world_rewards="random probing with indirect confirmation, epidemic spread with a log(n) retransmit budget, and evidence-weighted suspicion timers",
    observable_consequence="the record's entry point: shrink ProbeTimeout / SuspicionMult and count false positives; detection time vs cluster size", vacuity_condition="a reliable network with few nodes", trivial_shortcuts="a central registry (forbidden by the design); the world must remove the coordinator",
    cheat_control="a detector told which nodes are truly dead must have zero false positives and minimal delay; if the world cannot separate it from SWIM under injected loss, loss is not being injected", cost_class="CPU-scale (in-process cluster over loopback, as the tests do)", source_evidence="record pressure / entry point; state.go", purpose="PURPOSE: cluster membership for Consul / Nomad / Serf")
c.pressure("a_node_cannot_tell_whether_a_missed_ack_is_the_peer_s_fault_or_its_own",
    condition="an overloaded or partitioned prober sees everyone fail; declaring them all dead is exactly wrong", resource_or_constraint="only local observations",
    failure_condition="a sick node evicting the healthy cluster", world_punishes="symmetric interpretation of misses", world_rewards="a local health score that slows the prober's own clocks and a suspicion timer that wants independent confirmation",
    observable_consequence="false positive rate with one degraded node (Lifeguard's experiment)", vacuity_condition="uniformly healthy nodes", trivial_shortcuts="a very long timeout (slow detection; the world must charge delay)",
    cheat_control="a prober told its own health must outperform awareness scoring; if it does not, the world's degradation is not local", cost_class="CPU-scale", source_evidence="awareness.go; suspicion.go", purpose="PURPOSE: same")

c.ancestry("algorithm_from", "SWIM (Das, Gupta, Motivala 2002) + Lifeguard (Dadgar, Phillips, Currey 2018) -- named in the package's README, not re-read", note="human prior")
c.residue("PARTIALLY_EXPLAINED", ["push-pull merge and the conflict rules read by index", "the transport, encryption and compression layers unread", "nothing ran here; Techne's go test oracle is on M1"],
          note="the failure detector, suspicion, awareness and gossip queue are read")
c.save(state="COARSE")
