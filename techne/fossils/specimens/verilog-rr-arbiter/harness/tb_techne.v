`timescale 1ns/1ps
module tb_techne;
  reg clk=0, rst_an=1; reg [3:0] req=0; wire [3:0] grant;
  round_robin_arbiter dut(.rst_an(rst_an),.clk(clk),.req(req),.grant(grant));
  always #1 clk=~clk;
  integer i; integer seen0=0,seen1=0,seen2=0,seen3=0;
  initial begin
    rst_an=1; #2 rst_an=0; #2 rst_an=1;
    req=4'b1111;                       // full contention: everyone wants the bus
    for(i=0;i<16;i=i+1) begin @(posedge clk); #0
      $display("cycle=%0d req=%b grant=%b", i, req, grant);
      if(grant[0])seen0=1; if(grant[1])seen1=1; if(grant[2])seen2=1; if(grant[3])seen3=1;
    end
    if(seen0&&seen1&&seen2&&seen3) $display("ARBITER_ROTATES_ALL_FOUR");
    else $display("ARBITER_STARVES some=%b%b%b%b",seen0,seen1,seen2,seen3);
    $finish;
  end
endmodule
