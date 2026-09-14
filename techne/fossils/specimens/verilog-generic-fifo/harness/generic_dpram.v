`timescale 1ns/1ps
module generic_dpram (rclk,rrst,rce,oe,raddr,do,wclk,wrst,wce,we,waddr,di);
  parameter aw=5, dw=8;
  input rclk,rrst,rce,oe,wclk,wrst,wce,we;
  input [aw-1:0] raddr, waddr; input [dw-1:0] di; output reg [dw-1:0] do;
  reg [dw-1:0] mem [(1<<aw)-1:0];
  always @(posedge wclk) if (wce & we) mem[waddr] <= di;   // synchronous write
  always @(posedge rclk) if (rce) do <= mem[raddr];        // registered read (OpenCores contract)
endmodule
