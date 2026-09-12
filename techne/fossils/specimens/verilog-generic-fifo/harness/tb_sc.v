`timescale 1ns/1ps
module test;                                   // bounded single-clock FIFO oracle
  parameter DW=8, AW=3;                         // depth 8
  reg clk=0, rst=1, clr=0, we=0, re=0; reg [DW-1:0] din=0;
  wire [DW-1:0] dout; wire full,empty,full_r,empty_r,full_n,empty_n,full_n_r,empty_n_r; wire [1:0] level;
  generic_fifo_sc_a #(DW,AW) dut(.clk(clk),.rst(rst),.clr(clr),.din(din),.we(we),.dout(dout),.re(re),
    .full(full),.empty(empty),.full_r(full_r),.empty_r(empty_r),
    .full_n(full_n),.empty_n(empty_n),.full_n_r(full_n_r),.empty_n_r(empty_n_r),.level(level));
  always #5 clk=~clk;
  integer i, wrote, errs; reg [DW-1:0] exp [0:255];
  initial begin
    errs=0; wrote=0;
    rst=1; repeat(3)@(posedge clk); rst=0; repeat(2)@(posedge clk); rst=1; repeat(2)@(posedge clk);
    if(!empty) begin $display("ERROR: FIFO not empty after reset"); errs=errs+1; end
    for(i=0;i<8 && !full;i=i+1) begin          // fill until full (backpressure)
      @(negedge clk); din=8'hA0+i; we=1; exp[wrote]=din; wrote=wrote+1; @(posedge clk); #3 we=0; end
    we=0; @(posedge clk); #3;                   // let the RTL's <= #1 wp/gb updates settle
    $display("filled=%0d full=%b empty=%b level=%b", wrote, full, empty, level);
    if(!full) begin $display("ERROR: FIFO never asserted full"); errs=errs+1; end
    if(empty) begin $display("ERROR: FIFO empty while holding data"); errs=errs+1; end
    for(i=0;i<wrote;i=i+1) begin               // drain, check FIFO order (registered read)
      @(negedge clk); re=1; @(posedge clk); #3 re=0;
      if(dout!==exp[i]) begin $display("ERROR: Data mismatch idx %0d exp %h got %h",i,exp[i],dout); errs=errs+1; end end
    @(posedge clk); #3;
    if(!empty) begin $display("ERROR: FIFO not empty after drain"); errs=errs+1; end
    if(errs==0) $display("SC_FIFO_DONE_OK"); else $display("SC_FIFO_FAIL errs=%0d",errs);
    $finish; end
endmodule
