"""Cut: verilog-rr-arbiter (ancestry-aware, Stage A COARSE-but-complete; SOURCE_READ all three arbiter files in full (74 + 66 + 79 lines),
readme.txt; tb.v (50 lines) skimmed). Three circuits claimed by the author to implement the same round-robin arbiter."""
from nyx.atlas.author import Cut

T = "vault:verilog-rr-arbiter/upstream/tree/"
c = Cut("verilog-rr-arbiter", mode="ANCESTRY_AWARE", inspected=["round_robin_arbiter.v", "round_robin_arbiter2.v", "round_robin_arbiter3.v", "readme.txt", "tb.v (skimmed)"],
        evidence=[("SOURCE_READ", T + "round_robin_arbiter.v"), ("SOURCE_READ", T + "round_robin_arbiter2.v"), ("SOURCE_READ", T + "round_robin_arbiter3.v")],
        note="the smallest fossil in the sample: 4 mechanisms, 2 compositions of them claimed behaviourally identical by the author -- a ready-made human-different / behaviour-near test pair for Stage D")

pr = c.organ("fixed_priority_grant_to_the_lowest_set_request_bit", human_name="simple priority arbiter", status="ACCEPTED",
    human_interpretation="requester 0 always beats 1 beats 2 ...",
    mechanism="one-hot output: grant[i] = req[i] & ~|req[i-1:0]; written as an if/else-if chain (arbiter 1, 2) and as a generate loop (arbiter 3); appears FIVE times across the three files (once in arbiter 1, twice each in 2 and 3)",
    input="req[N-1:0]", output="one-hot grant or zero", state="none (combinational)", update="none", assumptions=["N >= 1"], fitness_value_in_ancestor="the only decision element; everything else re-labels its inputs and outputs",
    evidence_ref=T + "round_robin_arbiter.v:33-40; round_robin_arbiter3.v:53-64", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="each always @(*) priority block / generate block",
    coverage={"input_topology": "VECTOR", "output_topology": "DECISION", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "competition": "ARBITRATES", "order_sensitivity": "SENSITIVE", "temporal_horizon": "INSTANT"})

rp = c.organ("rotating_pointer_set_one_past_the_last_grant", human_name="rotate_ptr", status="ACCEPTED",
    mechanism="a register updated on the clock edge from the CURRENT grant: arbiter 1 stores the index after the granted line (2 bits); arbiters 2 and 3 store a thermometer mask with ones from that index upward (N bits; 1111 after grant[N-1] or reset); arbiter 3 updates only when some grant is high (update_ptr), arbiters 1 and 2 hold when no grant matches",
    input="grant[N-1:0]", output="a priority origin", state="rotate_ptr (2 bits or N bits)", update="per clock", assumptions=["the granted line is the one to demote"],
    fitness_value_in_ancestor="fairness: the just-served requester becomes lowest priority", evidence_ref=T + "round_robin_arbiter.v:61-73; round_robin_arbiter2.v:24-36; round_robin_arbiter3.v:27-49", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the rotate_ptr always blocks",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "LAST_VALUE", "update_topology": "EVENT_DRIVEN"})

ro = c.organ("rotate_requests_then_prioritise_then_unrotate_grants", human_name="arbiter 1 composition (rotate -> priority -> rotate)", status="ACCEPTED",
    mechanism="shift_req = req rotated right by rotate_ptr (a 4-way case), priority-pick on shift_req, grant_comb = shift_grant rotated left by rotate_ptr", input="req, rotate_ptr", output="grant_comb", state="none", update="none",
    assumptions=["N = 4 (the case statements are written out)"], evidence_ref=T + "round_robin_arbiter.v:22-51", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two case blocks around the priority block",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

mk = c.organ("masked_priority_with_unmasked_fallback", human_name="arbiter 2/3 composition (two priority arbiters and a mask)", status="ACCEPTED",
    mechanism="mask_req = req & rotate_ptr (only requesters at or above the pointer); grant = priority(mask_req), or if mask_req is zero, priority(req) (wrap-around); arbiter 3 is the same with generate loops for any N",
    input="req, rotate_ptr", output="grant_comb", state="none", update="none", assumptions=["N >= 2 (arbiter 3 comment line 35)"], evidence_ref=T + "round_robin_arbiter2.v:38-59; round_robin_arbiter3.v:51-69", confidence="HIGH",
    portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="mask_req / mask_grant / nomask_grant / grant_comb assigns",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "NONE", "representation_sensitivity": "SENSITIVE"})

gr = c.organ("registered_grant_that_deasserts_itself_the_next_cycle", human_name="grant <= grant_comb & ~grant", status="ACCEPTED",
    mechanism="the grant register takes the combinational grant AND NOT the current grant: a line granted this cycle cannot be granted next cycle even if it is the only requester; identical in all three files",
    input="grant_comb, grant", output="grant", state="grant[N-1:0]", update="per clock", assumptions=["a one-cycle grant pulse is what the consumer wants (a bus that needs a hold time would need a different rule)"],
    fitness_value_in_ancestor="UNKNOWN -- the readme does not say; by reading it enforces a release cycle between consecutive grants to the same requester, and also means a sole continuous requester is served at most every other cycle",
    failure_landscape="UNKNOWN by run", evidence_ref=T + "round_robin_arbiter.v:53-57; round_robin_arbiter2.v:61-65; round_robin_arbiter3.v:71-75", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the grant always block",
    coverage={"input_topology": "VECTOR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "memory": "LAST_VALUE", "temporal_horizon": "STEP"})

c.reject("tb.v testbench", reason="EFFECT_FROM_ENVIRONMENT", evidence=T + "tb.v -- drives req and prints grant; Techne's harness replaces it")
c.reject("'round-robin arbiter' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="two different circuits (1 vs 2/3) with a shared decision element and a shared state register")
c.reject("arbiter 2 vs arbiter 3 as separate anatomy", reason="OTHER", evidence="arbiter 3 is arbiter 2 with N parameterised and update_ptr gating; the readme says so and the code agrees", note="recorded as one composition with a scalability variant")

c.edge(rp, ro, "feeds"); c.edge(rp, mk, "feeds"); c.edge(ro, pr, "feeds"); c.edge(mk, pr, "feeds", note="twice: masked and unmasked"); c.edge(pr, ro, "feeds"); c.edge(pr, mk, "feeds")
c.edge(ro, gr, "feeds"); c.edge(mk, gr, "feeds"); c.edge(gr, rp, "updates", note="pointer follows the registered grant"); c.edge(gr, gr, "suppresses", note="self-deassert"); c.edge(ro, mk, "competes", note="two compositions claimed equivalent (readme); not measured")

c.pressure("several_requesters_contend_every_cycle_for_one_grant_and_none_may_starve",
    condition="N lines may request in any combination each clock; exactly zero or one may be granted; a line that keeps requesting must be served within a bounded number of cycles", resource_or_constraint="one shared resource; one decision per clock; bounded logic depth",
    failure_condition="starvation, or two grants at once (record)", world_punishes="fixed priority (starves high indices); unregistered state (glitches)", world_rewards="a priority origin that moves past the served requester",
    observable_consequence="the grant sequence under all-lines-high (rotation) and under one-line-always-high (others still served)", vacuity_condition="at most one requester at a time", trivial_shortcuts="a free-running counter that grants line (t mod N) whether or not it requests (fair, wastes cycles; the world must reward utilisation)",
    cheat_control="an arbiter given the request schedule in advance must achieve zero idle grants and zero starvation; if the world scores the counter equally, it is not charging idle cycles", cost_class="CPU-scale (exhaustive: 2^N requests x N pointer states)", source_evidence="record pressure / failure condition; all three files", purpose="PURPOSE: share a bus among masters")

c.ancestry("algorithm_from", "Matt Weber, 'Arbiters: Design Ideas and Coding Styles' (readme reference [1])", note="from readme.txt")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["the equivalence of composition 1 and composition 2/3 is the author's claim; exhaustively checkable (64 cases at N=4) and NOT checked here", "the self-deassert rule's purpose is unstated in the body"],
          note="every line of the three modules is accounted for by five mechanisms")
c.save(state="DEEP")
