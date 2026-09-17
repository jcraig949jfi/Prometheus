"""Cut: biriscv-branch-predictor (the next-PC unit of biRISC-V; ancestry-aware, Stage A DEEP on the predictor module, COARSE on the
core; SOURCE_READ on M3; position 26 of the 2026-09-17 NOT_CUT order). Read in full: src/core/biriscv_npc.v (446 lines: BTB, BHT,
gshare, RAS, next-PC selection). Read by structure: biriscv_frontend.v (the wiring). NOT read: the rest of the core (issue, exec,
lsu, caches), the LFSR replacement module. Nothing ran (Verilog; no iverilog on M3).
"""
from nyx.atlas.author import Cut

N = "vault:biriscv-branch-predictor/upstream/tree/src/core/biriscv_npc.v"
c = Cut("biriscv-branch-predictor", mode="ANCESTRY_AWARE", inspected=["src/core/biriscv_npc.v (all)", "src/core/biriscv_frontend.v (instantiation)"], evidence=[("SOURCE_READ", N), ("SOURCE_READ", "vault:biriscv-branch-predictor/upstream/tree/src/core/biriscv_frontend.v")],
        note="four predictors in one module, each a separate memory with its own update rule, arbitrated by a fixed priority: return-address stack, then taken-branch bit or unconditional jump from the BTB, else fall-through; the module keeps a SPECULATIVE copy of the global history and of the RAS pointer beside the ARCHITECTURAL one")

btb = c.organ("branch_target_buffer_fully_associative_on_the_fetch_pc_with_call_ret_jmp_type_bits_and_random_replacement", human_name="btb_pc_q / btb_target_q / btb_is_*_q; the two lookup loops; btb_hit_r / btb_miss_r; u_lru (biriscv_npc_lfsr)", status="ACCEPTED",
    mechanism="32 entries each holding a branch PC, its last target and three type bits; the lookup compares every entry against the fetch PC (and, for a 64-bit fetch, against PC | 4 for the upper slot); on a resolved branch a hit updates the target (if taken) and type bits in place, a miss allocates an entry chosen by an LFSR (pseudo-random replacement, not LRU despite the instance name)",
    input="pc_f_i (fetch), branch_request_i with source/target/type (resolve)", output="btb_valid, target, type bits, upper-slot flag", state="32 x (32+32+3) bits", update="per resolved branch",
    assumptions=["a branch's target is usually the same next time (true for direct branches, false for indirect ones)", "32 entries cover the hot loops"],
    fitness_value_in_ancestor="the target is known at fetch, one cycle before decode; without it a taken branch costs the pipeline depth", failure_landscape="by reading: fully associative compare of 32 entries every cycle is the timing-critical path; random replacement can evict a hot loop's branch",
    human_prior="the BTB (Lee & Smith 1984); random replacement is the designer's area/timing choice", evidence_ref=N + ":btb_* blocks and u_lru", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the BTB registers, the two always @* lookup loops, the write block",
    coverage={"input_topology": "SCALAR", "output_topology": "VECTOR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "ARCHIVE", "stochasticity": "SEEDED_RANDOM", "update_topology": "SINGLE_STEP"})

bht = c.organ("two_bit_saturating_counters_indexed_by_pc_or_by_gshare_xor_of_pc_and_global_history", human_name="bht_sat_q[512]; bht_wr_entry_w / bht_rd_entry_w; GSHARE_ENABLE; gshare_*_entry_w", status="ACCEPTED",
    mechanism="512 two-bit counters initialised to 3 (strongly taken); a resolved taken branch increments its counter (saturating at 3), not-taken decrements (at 0); predict taken when the counter >= 2; the index is either PC bits (bimodal) or, with GSHARE_ENABLE, PC bits XOR the global history register; the read uses the SPECULATIVE history, the write uses the ARCHITECTURAL one at resolve time",
    input="the fetch PC; the history; resolve events", output="bht_predict_taken", state="512 x 2 bits", update="per resolved conditional branch",
    assumptions=["a branch's recent behaviour predicts its next outcome (bimodal) or its behaviour correlated with recent global outcomes does (gshare)"],
    fitness_value_in_ancestor="hysteresis: one anomalous outcome does not flip the prediction; gshare captures correlated branches at the cost of aliasing", failure_landscape="by reading: 512 entries alias heavily in large code; GSHARE is OFF by default in the parameter list, so the shipped configuration is bimodal",
    human_prior="the 2-bit counter (Smith 1981) and gshare (McFarling 1993)", evidence_ref=N + ":global_history_*, gshare_*, bht_*", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the BHT and history registers",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "SUMMARY_STATISTIC", "stochasticity": "DETERMINISTIC", "adaptation": "PARAMETER", "failure_mode": "DEGRADES"})

ras = c.organ("return_address_stack_with_a_speculative_pointer_beside_the_architectural_one", human_name="ras_stack_q[8], ras_index_q (speculative) / ras_index_real_q (architectural); ras_call_pred_w / ras_ret_pred_w", status="ACCEPTED",
    mechanism="an 8-entry circular stack of return addresses; on a PREDICTED call (BTB says call) the fetch PC + 4 is pushed and the speculative pointer advanced; a predicted return pops it and supplies the target; on a RESOLVED call/return the architectural pointer moves and, for a call, the real return address is written; a resolved branch resets the speculative pointer from the architectural one, discarding the speculative pushes/pops of a mispredicted path; an entry equal to RAS_INVALID (bit 0 set) disables the prediction",
    input="BTB type bits at fetch; resolve events", output="the predicted return PC; a valid flag", state="8 x 32 bits; two pointers", update="per predicted and per resolved call/return",
    assumptions=["calls and returns nest (a stack); 8 deep covers the hot call depth"], fitness_value_in_ancestor="indirect returns, which the BTB cannot predict after a call from a new site, become predictable", failure_landscape="by reading: overflow wraps silently (deep recursion mispredicts every return beyond 8); the invalid marker is bit 0 of the stored address, which relies on aligned return addresses",
    human_prior="the RAS (Kaeli & Emma 1991); the dual-pointer recovery scheme is the designer's", evidence_ref=N + ":ras_* blocks", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the RAS registers and the four always blocks that touch them",
    coverage={"input_topology": "EVENT", "output_topology": "SCALAR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "memory": "WINDOW", "stochasticity": "DETERMINISTIC", "recovery": "ROLLS_BACK", "failure_mode": "CORRUPTS"})

spec = c.organ("speculative_shadow_state_updated_by_predictions_and_resynchronised_from_architectural_state_on_resolve", human_name="global_history_q vs global_history_real_q; ras_index_q vs ras_index_real_q", status="ACCEPTED",
    mechanism="two copies of the global history: the real one shifts in each RESOLVED outcome; the speculative one shifts in each PREDICTION as it is made (so back-to-back predictions see the effect of earlier predictions) and, on any resolve, is reloaded from the real one plus the resolved outcome; the RAS pointer follows the same pattern",
    input="predictions; resolutions", output="the history the predictor reads", state="two 9-bit registers; two 3-bit pointers", update="per prediction and per resolve",
    assumptions=["predictions are usually right, so the speculative copy is usually the truth one step early; when wrong, resynchronisation costs nothing beyond the pipeline flush that already happens"],
    fitness_value_in_ancestor="prediction can proceed at fetch rate without waiting for resolution; the classic speculative-update problem solved by shadowing", failure_landscape="UNKNOWN by run",
    evidence_ref=N + ":global_history_real_q / global_history_q; ras_index_real_* / ras_index_*", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the paired registers",
    coverage={"input_topology": "EVENT", "output_topology": "VECTOR", "state_amount": "CONSTANT", "state_persistence": "PERSISTENT", "stochasticity": "DETERMINISTIC", "recovery": "ROLLS_BACK"})

sel = c.organ("next_pc_arbitration_by_fixed_priority_ras_then_bht_or_jmp_then_fall_through", human_name="assign next_pc_f_o / next_taken_f_o / pred_taken_w / pred_ntaken_w", status="ACCEPTED",
    mechanism="next PC = the RAS top if the BTB says this is a return (and the entry is valid); else the BTB target if the BHT predicts taken or the BTB says unconditional jump; else the fall-through (PC aligned to 8 plus 8, i.e. the next 64-bit fetch pair); next_taken flags which of the two 32-bit slots redirects, so the decode stage can drop the instruction after a taken branch in the pair",
    input="the four predictors' outputs; pc_f_i[2] (upper/lower slot)", output="next_pc_f_o, next_taken_f_o", state="none", update="per fetch", assumptions=["returns are best served by the RAS, jumps are always taken, conditional branches by the BHT"],
    fitness_value_in_ancestor="one mux; the priority encodes which predictor is trusted for which branch class", failure_landscape="UNKNOWN by run", evidence_ref=N + ":the four assign statements at the end", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the assigns",
    coverage={"input_topology": "MIXED", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "DETERMINISTIC", "competition": "ARBITRATES"})

c.reject("the rest of the core (fetch, decode, issue, exec, LSU, caches, CSRs), the LFSR module body", reason="OTHER", evidence="NOT READ; residue", note="the record's tag 'hidden-state' is this module: the predictor is the core's only learned state")
c.reject("the SUPPORT_BRANCH_PREDICTION = 0 branch (static fall-through)", reason="DUPLICATES_A_CONTROL", evidence=N + ":generate else branch", note="the body ships its own negative control: prediction off")
c.reject("'branch predictor' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="BTB, BHT, RAS and the shadow state are four memories with four update rules and four parameter switches")

c.edge(btb, sel, "feeds"); c.edge(bht, sel, "feeds"); c.edge(ras, sel, "feeds"); c.edge(btb, ras, "gates", note="call/ret type bits"); c.edge(spec, bht, "feeds", note="read index"); c.edge(spec, ras, "feeds", note="pointer"); c.edge(sel, spec, "updates", note="predictions shift the speculative history"); c.edge(btb, bht, "gates", note="BHT is consulted only on a BTB hit")

c.pressure("the_next_action_must_be_guessed_before_its_condition_is_known_from_a_small_memory_of_past_outcomes_with_the_guess_itself_feeding_later_guesses",
    condition="a stream of conditional decisions arrives faster than their conditions resolve; the organism must guess each one now from bounded memory of past outcomes, and its guesses change what it sees next before the truth arrives; a wrong guess costs a fixed penalty (the flush)",
    resource_or_constraint="a few kilobits of state; one cycle per guess", failure_condition="misprediction rate above the static baseline on real code", world_punishes="guessing from stale or aliased state; waiting for resolution",
    world_rewards="hysteresis, correlation with recent history, a stack for nested returns, and speculative shadow state resynchronised on truth", observable_consequence="misprediction rate per predictor component on instruction traces with each component disabled (the module's own parameters do this)",
    vacuity_condition="branches that are always taken or never taken (static prediction suffices)", trivial_shortcuts="an oracle trace",
    cheat_control="a predictor fed the resolved outcome one cycle early must mispredict nothing; SUPPORT_BRANCH_PREDICTION = 0 (the body's own control) must show the static rate: the world must show both",
    cost_class="CPU-scale", source_evidence="biriscv_npc.v; record tags speculation / hidden-state", purpose="PURPOSE: instruction fetch redirection in a pipelined CPU (biRISC-V, Ultra-Embedded)")

c.ancestry("algorithm_from", "Smith 1981 (2-bit counters); Lee & Smith 1984 (BTB); Kaeli & Emma 1991 (RAS); McFarling 1993 (gshare)", note="from the mechanisms; not verified against the record this pass")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["the core outside npc.v not read; the LFSR replacement body not read", "nothing ran; the record says RUNNABLE_EMULATED (iverilog on M2), and the parameter switches make each organ its own ablation"], note="every always block and assign in biriscv_npc.v is in an organ")
c.save(state="DEEP")
