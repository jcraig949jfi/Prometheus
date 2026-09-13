`timescale 1ns/1ps
// Techne testbench: two arbiter instances under identical contention.
module tb;
    localparam PORTS = 4;
    reg clk = 0, rst = 1;
    reg [PORTS-1:0] request = 0, acknowledge = 0;
    wire [PORTS-1:0] g_rr, g_pr; wire v_rr, v_pr; wire [1:0] e_rr, e_pr;
    arbiter #(.PORTS(PORTS), .ARB_TYPE_ROUND_ROBIN(1), .ARB_BLOCK(0), .ARB_BLOCK_ACK(0), .ARB_LSB_HIGH_PRIORITY(1))
        rr (.clk(clk), .rst(rst), .request(request), .acknowledge(acknowledge), .grant(g_rr), .grant_valid(v_rr), .grant_encoded(e_rr));
    arbiter #(.PORTS(PORTS), .ARB_TYPE_ROUND_ROBIN(0), .ARB_BLOCK(0), .ARB_BLOCK_ACK(0), .ARB_LSB_HIGH_PRIORITY(1))
        pr (.clk(clk), .rst(rst), .request(request), .acknowledge(acknowledge), .grant(g_pr), .grant_valid(v_pr), .grant_encoded(e_pr));
    integer i, c_rr [0:PORTS-1], c_pr [0:PORTS-1];
    always #5 clk = ~clk;
    initial begin
        for (i = 0; i < PORTS; i = i + 1) begin c_rr[i] = 0; c_pr[i] = 0; end
        #12 rst = 0;
        @(negedge clk); request = 4'b1111;
        repeat (16) begin
            @(posedge clk); #1;
            $display("cycle req=%b  RR grant=%b (port %0d)  PRIORITY grant=%b (port %0d)", request, g_rr, e_rr, g_pr, e_pr);
            if (v_rr) c_rr[e_rr] = c_rr[e_rr] + 1;
            if (v_pr) c_pr[e_pr] = c_pr[e_pr] + 1;
        end
        request = 4'b0100;
        @(posedge clk); #1; $display("single requester (port 2): RR grant=%b PRIORITY grant=%b", g_rr, g_pr);
        $display("RR grants per port: %0d %0d %0d %0d", c_rr[0], c_rr[1], c_rr[2], c_rr[3]);
        $display("PRIORITY grants per port: %0d %0d %0d %0d", c_pr[0], c_pr[1], c_pr[2], c_pr[3]);
        $display("RESULT %s", (c_rr[0] == 4 && c_rr[1] == 4 && c_rr[2] == 4 && c_rr[3] == 4 && c_pr[0] == 16 && c_pr[1] == 0 && g_rr == 4'b0100 && g_pr == 4'b0100) ? "OK" : "CHECK");
        $finish;
    end
endmodule
