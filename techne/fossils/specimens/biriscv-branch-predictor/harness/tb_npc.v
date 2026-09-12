`timescale 1ns/1ps
// Techne testbench: biriscv_npc alone, two instances (bimodal BHT vs gshare) on one branch stream.
// Stream: a loop branch at 0x110 taken 7 times then not-taken (falls to 0x118), 40 iterations.
module tb;
    reg clk = 0, rst = 1; always #5 clk = ~clk;
    reg br_req = 0, br_taken = 0, br_ntaken = 0, accept = 0;
    reg [31:0] br_src = 0, br_pc = 0, pc_f = 0;
    wire [31:0] npc_bi, npc_gs; wire [1:0] tk_bi, tk_gs;
    biriscv_npc #(.GSHARE_ENABLE(0)) bi (.clk_i(clk), .rst_i(rst), .invalidate_i(1'b0), .branch_request_i(br_req),
        .branch_is_taken_i(br_taken), .branch_is_not_taken_i(br_ntaken), .branch_source_i(br_src), .branch_is_call_i(1'b0),
        .branch_is_ret_i(1'b0), .branch_is_jmp_i(1'b0), .branch_pc_i(br_pc), .pc_f_i(pc_f), .pc_accept_i(accept),
        .next_pc_f_o(npc_bi), .next_taken_f_o(tk_bi));
    biriscv_npc #(.GSHARE_ENABLE(1)) gs (.clk_i(clk), .rst_i(rst), .invalidate_i(1'b0), .branch_request_i(br_req),
        .branch_is_taken_i(br_taken), .branch_is_not_taken_i(br_ntaken), .branch_source_i(br_src), .branch_is_call_i(1'b0),
        .branch_is_ret_i(1'b0), .branch_is_jmp_i(1'b0), .branch_pc_i(br_pc), .pc_f_i(pc_f), .pc_accept_i(accept),
        .next_pc_f_o(npc_gs), .next_taken_f_o(tk_gs));
    localparam BR = 32'h00000110, LOOP = 32'h00000100, FALL = 32'h00000118;
    integer it, k, e_bi = 0, l_bi = 0, e_gs = 0, l_gs = 0, tot_bi = 0, tot_gs = 0;
    reg t; reg [31:0] actual;
    initial begin
        #12 rst = 0;
        @(negedge clk);
        for (it = 0; it < 40; it = it + 1) begin
            for (k = 0; k < 8; k = k + 1) begin
                t = (k < 7); actual = t ? LOOP : FALL;
                // fetch cycle: the block holding the branch is presented; predictions are read
                pc_f = BR; accept = 1; br_req = 0; br_taken = 0; br_ntaken = 0;
                #1;
                if (npc_bi != actual) begin tot_bi = tot_bi + 1; if (it < 10) e_bi = e_bi + 1; if (it >= 30) l_bi = l_bi + 1; end
                if (npc_gs != actual) begin tot_gs = tot_gs + 1; if (it < 10) e_gs = e_gs + 1; if (it >= 30) l_gs = l_gs + 1; end
                if (it < 2 || it >= 38) $display("it=%0d k=%0d actual=%h  bimodal->%h %s  gshare->%h %s", it, k, actual,
                    npc_bi, (npc_bi == actual) ? "ok " : "MIS", npc_gs, (npc_gs == actual) ? "ok " : "MIS");
                @(negedge clk);
                // resolve cycle: the branch's outcome is reported (updates BTB / BHT / history)
                accept = 0; br_req = 1; br_src = BR; br_pc = actual; br_taken = t; br_ntaken = ~t;
                @(negedge clk);
                br_req = 0; br_taken = 0; br_ntaken = 0;
            end
        end
        $display("mispredicts over 320 branches: bimodal total=%0d early(it<10)=%0d late(it>=30)=%0d | gshare total=%0d early=%0d late_mispredicts=%0d",
            tot_bi, e_bi, l_bi, tot_gs, e_gs, l_gs);
        $display("RESULT %s", (l_gs < l_bi && l_gs <= e_gs && l_bi <= e_bi) ? "OK" : "CHECK");
        $finish;
    end
endmodule
