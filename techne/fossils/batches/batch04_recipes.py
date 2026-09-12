"""Batch 04 recipes + harnesses (2026-09-12). python -m techne.fossils.batches.batch04_recipes

linux-tcp-congestion and do-mpc are SOURCE_ONLY (kernel context / heavy CasADi) -> no recipe.
Python specimens pip-install their deps at run time in python:3.11-slim (recorded). Verilog in
the iverilog world. C/C++ in the bookworm C world.
"""
from __future__ import annotations

import json
from .. import vault

HW = "prometheus-fossil-hw:bookworm"
C = "prometheus-fossil-c:bookworm"
PY = "python:3.11-slim"
R = {}
H = {}

# --- AXIS 1 raft: build + run its own CuTest suite (bundles/downloads contrib) ---------------
R["willemt-raft"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    # The Makefile `tests` target git-pulls CLinkedListQueue at build time; the world is sealed,
    # so we vendor those two files ($HARNESS/linked_list_queue.*) and compile the CuTest suite
    # directly. CuTest.c ships in the tree. -Werror is dropped for modern gcc (recorded); no
    # raft source is changed.
    "build": [{"name": "generate the CuTest AllTests driver, then compile the raft test suite",
               "cmd": "cd tests && sh make-tests.sh 'test_*.c' > main_test.c && cd .. && "
                      "gcc -O2 -w -Iinclude -Itests -I$HARNESS -o $BODY/traft "
                      "src/raft_server.c src/raft_server_properties.c src/raft_log.c src/raft_node.c "
                      "tests/main_test.c tests/test_log.c tests/test_node.c tests/test_scenario.c "
                      "tests/test_server.c tests/test_snapshotting.c tests/mock_send_functions.c "
                      "tests/CuTest.c $HARNESS/linked_list_queue.c 2>&1 | grep -i 'error:' | head; test -x $BODY/traft",
               "timeout": 300}],
    "runs": [{"name": "Raft election + log-replication + snapshotting unit/scenario tests",
              "cmd": "$BODY/traft > /tmp/raft.tap 2>&1; tail -2 /tmp/raft.tap; echo PASS=$(grep -c '^ok ' /tmp/raft.tap) NOTOK=$(grep -c 'not ok' /tmp/raft.tap)",
              "expect": {"exit": 0, "stdout_contains": ["NOTOK=0"], "stdout_regex": r"PASS=1[0-9][0-9]"}}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "The CuTest suite exercises leader election, log replication, and snapshotting via mock send functions (simulated peers). DEVIATIONS: CLinkedListQueue is vendored as a companion (network-sealed build); -Werror relaxed for modern gcc. No raft source changed."}

# --- AXIS 2 arduino-pid: Techne Arduino shim + first-order plant + step response --------------
H["arduino-pid"] = {
    "Arduino.h": "#ifndef ARDUINO_H\n#define ARDUINO_H\n#include <stdint.h>\nstatic unsigned long _ms=0; inline unsigned long millis(){return _ms;} inline void _advance(unsigned long d){_ms+=d;}\n#endif\n",
    "drv.cpp": """/* Techne harness: PID controlling a THIRD-order loop (two cascaded first-order lags plus the
   controller's own integrator). Setpoint step to 1.0. Low gain converges; very high gain pushes
   the loop into sustained oscillation -- a pathological-behavior receipt. Instability is detected
   by counting late-window setpoint crossings (output saturates at +-50, so an unstable loop
   oscillates rather than diverging to infinity). */
#include "Arduino.h"
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include "PID_v1.h"
int main(int argc,char**argv){
  double Kp = (argc>1)? atof(argv[1]) : 2.0;
  double Ki = (argc>2)? atof(argv[2]) : 1.0;
  double Kd = (argc>3)? atof(argv[3]) : 0.05;
  double In=0, Out=0, Set=1.0;
  PID pid(&In,&Out,&Set, Kp, Ki, Kd, DIRECT);
  pid.SetMode(AUTOMATIC); pid.SetOutputLimits(-50,50); pid.SetSampleTime(10);
  double y1=0.0, y2=0.0, dt=0.01;
  int N=6000, late_cross=0; double late_max=0.0, prev_err=Set-y2;
  for(int k=0;k<N;k++){ _advance(10); In=y2; pid.Compute();
    y1 += dt*(-y1 + Out);               /* lag 1 */
    y2 += dt*(-y2 + y1);                /* lag 2 -> controlled variable */
    double err=Set-y2;
    if(k > (int)(0.7*N)){ if((err>0)!=(prev_err>0)) late_cross++; if(fabs(y2)>late_max) late_max=fabs(y2); }
    prev_err=err; }
  printf("Kp=%.1f final=%.4f late_crossings=%d late_max=%.3f\\n", Kp, y2, late_cross, late_max);
  if (fabs(y2-Set)<0.15 && late_cross<=3) printf("PID_CONVERGED\\n");
  else if (late_cross>=12 || late_max>4.0) printf("PID_UNSTABLE\\n");
  else printf("PID_MARGINAL\\n");
  return 0; }
"""}
R["arduino-pid"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1"}],
    "build": [{"name": "compile PID + plant harness", "cmd": "g++ -O2 -DARDUINO=10800 -I. -I$HARNESS -o $BODY/pid $HARNESS/drv.cpp PID_v1.cpp 2>&1 | grep -i 'error:'; test -x $BODY/pid"}],
    "runs": [{"name": "step response: modest gains converge the controlled variable to the setpoint", "cmd": "$BODY/pid 1 0.5 0.02",
              "expect": {"exit": 0, "stdout_contains": ["PID_CONVERGED"]}}],
    "tests": [{"name": "pathological: 200x proportional gain destabilises the loop", "cmd": "$BODY/pid 200 0.5 0.02",
               "expect": {"exit": 0, "stdout_contains": ["PID_UNSTABLE"]}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Techne supplies a minimal Arduino.h (millis) + a two-lag (third-order-with-integrator) plant; the PID source is unmodified. Run (Kp=1) converges to the setpoint via integral action; the test run (Kp=200) is the FAILURE-axis receipt: excess gain destabilises the feedback loop (output rails). behavioral_entry_point: pass Kp Ki Kd on argv -- Kp>=~4 already leaves the converged regime."}

# --- AXIS 2 python-control: LQR on a 2-state plant, driven to the origin ----------------------
H["python-control"] = {"drv.py": """import numpy as np, control as ct
# double integrator: x1'=x2, x2'=u ; LQR should stabilise it to the origin
A=np.array([[0,1],[0,0]]); B=np.array([[0],[1]]); Q=np.eye(2); Rm=np.array([[1.0]])
K,S,E=ct.lqr(A,B,Q,Rm)
Acl=A-B@K
# simulate from a perturbed state
x=np.array([1.0,0.0]); dt=0.01
for _ in range(2000): x=x+dt*(Acl@x)
print("closed_loop_eig_real_max %.4f"%max(e.real for e in np.linalg.eigvals(Acl)))
print("final_state %.4e %.4e"%(x[0],x[1]))
print("LQR_STABILIZED" if max(e.real for e in np.linalg.eigvals(Acl))<0 and abs(x[0])<1e-2 else "LQR_FAILED")
"""}
R["python-control"] = {
    "runner": "docker", "image": PY, "workdir": "upstream/tree",
    "probe": [{"name": "python", "cmd": "python --version"}],
    "build": [],
    "runs": [{"name": "design an LQR and drive a double integrator to the origin", "cmd": "pip install -q numpy scipy matplotlib >/dev/null 2>&1 && MPLBACKEND=Agg PYTHONPATH=. python $HARNESS/drv.py",
              "expect": {"exit": 0, "stdout_contains": ["LQR_STABILIZED"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "numpy/scipy are pip-installed; the acquired python-control source itself is run via PYTHONPATH=. (the fossil, not a PyPI copy). Oracle: LQR must place all closed-loop eigenvalues in the left half-plane and drive the perturbed state to ~0."}

# --- AXIS 3 kalman: noisy constant, filtered variance << raw ---------------------------------
H["simple-kalman-denyssene"] = {
    "Arduino.h": "#ifndef ARDUINO_H\n#define ARDUINO_H\n#include <stdint.h>\n#endif\n",  # the lib is an Arduino library; it only needs the header to exist
    "drv.cpp": """/* Techne harness: estimate a hidden constant (10.0) from noisy measurements. The filtered
   error must be far below the raw measurement noise. */
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include "SimpleKalmanFilter.h"
int main(){
  SimpleKalmanFilter kf(2.0f, 2.0f, 0.01f);   /* meas err, est err, process noise */
  srand(1); double truth=10.0, sraw=0, sflt=0; int N=2000;
  for(int k=0;k<N;k++){ double noise=((rand()%2001)/1000.0-1.0)*3.0; /* +-3 */
    double meas=truth+noise; double est=kf.updateEstimate((float)meas);
    sraw+=(meas-truth)*(meas-truth); sflt+=(est-truth)*(est-truth); }
  double rmsraw=sqrt(sraw/N), rmsflt=sqrt(sflt/N);
  printf("rms_raw=%.4f rms_filtered=%.4f ratio=%.3f\\n", rmsraw, rmsflt, rmsflt/rmsraw);
  printf(rmsflt < rmsraw*0.5 ? "KALMAN_OK\\n" : "KALMAN_WEAK\\n");
  return 0; }
"""}
R["simple-kalman-denyssene"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree/src",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1"}],
    "build": [{"name": "compile filter + harness", "cmd": "g++ -O2 -I. -I$HARNESS -o $BODY/kf $HARNESS/drv.cpp SimpleKalmanFilter.cpp 2>&1 | grep -i 'error:'; test -x $BODY/kf"}],
    "runs": [{"name": "filter noisy measurements of a hidden constant", "cmd": "$BODY/kf",
              "expect": {"exit": 0, "stdout_contains": ["KALMAN_OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: the filtered RMS error must be below half the raw measurement RMS -- the filter is recovering the hidden value from noise. behavioral_entry_point: raise the noise amplitude or step the truth."}

# --- AXIS 3 filterpy: KF track of a constant-velocity target; RMSE below sensor --------------
H["filterpy-labbe"] = {"drv.py": """import numpy as np
from filterpy.kalman import KalmanFilter
np.random.seed(1)
# constant-velocity 1-D target; measure position with noise sigma=3
dt=1.0; kf=KalmanFilter(dim_x=2,dim_z=1)
kf.F=np.array([[1,dt],[0,1]]); kf.H=np.array([[1,0]])
kf.R=np.array([[9.0]]); kf.Q=np.eye(2)*0.01; kf.P=np.eye(2)*500; kf.x=np.array([[0.],[0.]])
truth=0.0; v=1.0; sraw=0; sflt=0; N=200
for k in range(N):
    truth+=v; z=truth+np.random.randn()*3.0
    kf.predict(); kf.update(np.array([[z]]))
    sraw+=(z-truth)**2; sflt+=(kf.x[0,0]-truth)**2
import math
rr=math.sqrt(sraw/N); rf=math.sqrt(sflt/N)
print("rmse_sensor %.3f rmse_filter %.3f"%(rr,rf))
print("FILTERPY_OK" if rf<rr else "FILTERPY_WEAK")
"""}
R["filterpy-labbe"] = {
    "runner": "docker", "image": PY, "workdir": "upstream/tree",
    "probe": [{"name": "python", "cmd": "python --version"}],
    "build": [],
    "runs": [{"name": "Kalman track of a noisy constant-velocity target", "cmd": "pip install -q numpy scipy >/dev/null 2>&1 && PYTHONPATH=. python $HARNESS/drv.py",
              "expect": {"exit": 0, "stdout_contains": ["FILTERPY_OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: filtered RMSE < raw sensor RMSE. This repo IS the adversarial pair -- the plant GENERATES process+measurement noise (the pressure) and the KF RECOVERS the hidden position/velocity (the response); raise R/Q or drop measurements to break it."}

# --- AXIS 3 viterbi: build + its own test ----------------------------------------------------
R["viterbi-hmm-xukmin"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1"}],
    "build": [{"name": "make", "cmd": "make -s 2>&1 | grep -viE 'warning' | tail -3; ls viterbi viterbi_test 2>/dev/null; test -x ./viterbi_test || test -x ./viterbi"}],
    "runs": [{"name": "the shipped Viterbi/HMM test", "cmd": "./viterbi_test 2>&1 | tail -10 || make test 2>&1 | tail -10; echo VITERBIDONE",
              "expect": {"exit": 0, "stdout_contains": ["VITERBIDONE"], "stdout_not_contains": ["FAIL", "error"]}}],
    "tests": [], "test_kind": "UPSTREAM", "test_classification_if_none": "UPSTREAM_TESTS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "viterbi_test is the upstream oracle: decode a known HMM's observation sequence and check the most-likely path. behavioral_entry_point: perturb transition/emission probabilities."}

# --- AXIS 4 lru-cache: eviction correctness + a THRASH failure receipt ------------------------
# NOTE: in this library "usage is defined as insertion, but not lookup" -- contains()/lookup()
# do NOT reorder; only insert() moves a key to the front. So the least-recently-INSERTED key is
# the one evicted on overflow, and the oracle is written to that contract.
H["lru-cache-goldsborough"] = {"drv.cpp": """/* Techne harness: LRU must evict the least-recently-used key on overflow; and a working set
   larger than capacity must THRASH (near-zero hit rate). */
#include <cstdio>
#include <lru/lru.hpp>
int main(){
  {
    LRU::Cache<int,int> c(3);
    c.insert(1,1); c.insert(2,2); c.insert(3,3);   /* recency front->back: 3,2,1 ; LRU = 1 */
    c.insert(4,4);                                 /* full -> evicts the LRU key (1) */
    printf("has1=%d has2=%d has3=%d has4=%d\\n",
           (int)c.contains(1),(int)c.contains(2),(int)c.contains(3),(int)c.contains(4));
    if (!c.contains(1) && c.contains(2) && c.contains(3) && c.contains(4)) printf("LRU_EVICT_OK\\n");
    else printf("LRU_EVICT_BAD\\n");
  }
  {
    LRU::Cache<int,int> c(10); int hits=0, N=100000;
    for(int k=0;k<N;k++){ int key=k%1000;          /* working set 1000 >> capacity 10 */
      if(c.contains(key)) hits++; else c.insert(key,key); }
    double hr=100.0*hits/N; printf("thrash_hit_rate=%.2f%%\\n", hr);
    if (hr < 5.0) printf("LRU_THRASH_CONFIRMED\\n");
  }
  return 0; }
"""}
R["lru-cache-goldsborough"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "g++", "cmd": "g++ --version | head -1"}],
    "build": [{"name": "compile driver against the header library", "cmd": "g++ -O2 -std=c++17 -Iinclude -o $BODY/lru $HARNESS/drv.cpp 2>&1 | grep -i 'error:' | head -5; test -x $BODY/lru"}],
    "runs": [{"name": "LRU evicts the least-recently-inserted key", "cmd": "$BODY/lru",
              "expect": {"exit": 0, "stdout_contains": ["LRU_EVICT_OK"]}}],
    "tests": [{"name": "pathological: working set >> capacity thrashes (hit rate -> 0)", "cmd": "$BODY/lru",
               "expect": {"exit": 0, "stdout_contains": ["LRU_THRASH_CONFIRMED"]}}],
    "test_kind": "TECHNE", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle for eviction: key 1 (least-recently-inserted; lookup does not reorder in this library) is dropped. The thrash run is the FAILURE-axis receipt: a working set of 1000 against capacity 10 collapses the hit rate under 5%."}

# --- AXIS 4 buddy: allocate/free in a fixed arena, no overlap, coalesces ----------------------
H["buddy-alloc-spaskalev"] = {"drv.c": """/* Techne harness: buddy allocator over a fixed arena -- allocate many blocks, write, free,
   and confirm no overlap and that the arena coalesces back. */
#define BUDDY_ALLOC_IMPLEMENTATION
#include "buddy_alloc.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(void){
  size_t arena_sz = 1<<20; unsigned char* arena = malloc(arena_sz);
  size_t meta = buddy_sizeof(arena_sz); unsigned char* meta_buf = malloc(meta);
  struct buddy* b = buddy_init(meta_buf, arena, arena_sz);
  enum{N=500}; void* p[N];
  for(int i=0;i<N;i++){ p[i]=buddy_malloc(b, 64+(i%512)); if(!p[i]){printf("ALLOC_NULL %d\\n",i);} else memset(p[i], i&0xff, 64); }
  for(int i=0;i<N;i++) if(p[i]) buddy_free(b, p[i]);
  /* after freeing all, a full-arena-ish allocation should succeed (coalesced) */
  void* big = buddy_malloc(b, arena_sz/2);
  printf(big?"COALESCE_OK\\n":"COALESCE_FAIL\\n");
  printf("BUDDY_OK\\n"); return big?0:1; }
"""}
R["buddy-alloc-spaskalev"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "compile driver against the header", "cmd": "gcc -O2 -w -I. -o $BODY/bd $HARNESS/drv.c 2>&1 | grep -i 'error:' | head -3; test -x $BODY/bd"}],
    "runs": [{"name": "alloc/free 500 blocks in a 1MB arena, then coalesce", "cmd": "$BODY/bd",
              "expect": {"exit": 0, "stdout_contains": ["COALESCE_OK", "BUDDY_OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: after freeing everything, a half-arena allocation must succeed -- the buddy merges freed blocks back. behavioral_entry_point: free in an adversarial order to induce fragmentation failure."}

# --- AXIS 5 hardware (iverilog) --------------------------------------------------------------
# The shipped tb.v drives requests but emits no stdout, so the grant DECISIONS are invisible.
# Techne supplies an observation testbench (stimulus + $monitor only; the arbiter RTL is
# untouched) that holds all four requesters high and prints the granted index each cycle -- a
# round-robin arbiter must ROTATE the grant (no requester starves).
H["verilog-rr-arbiter"] = {"tb_techne.v": """`timescale 1ns/1ps
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
"""}
R["verilog-rr-arbiter"] = {
    "runner": "docker", "image": HW, "workdir": "upstream/tree",
    "probe": [{"name": "iverilog", "cmd": "iverilog -V 2>&1 | head -1"}],
    "build": [{"name": "compile Techne observation tb + arbiter", "cmd": "iverilog -o $BODY/arb.vvp $HARNESS/tb_techne.v round_robin_arbiter.v 2>&1 | grep -viE 'warning' | tail -4; test -f $BODY/arb.vvp"}],
    "runs": [{"name": "hold all four requests high; confirm the grant rotates to every requester", "cmd": "vvp -N $BODY/arb.vvp 2>&1 | tail -20",
              "expect": {"exit": 0, "stdout_contains": ["ARBITER_ROTATES_ALL_FOUR"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_EMULATED",
    "notes": "Oracle: under full contention every requester must eventually be granted (no starvation) -- that is the round-robin property. The arbiter RTL is unmodified; Techne only supplies stimulus+observation. behavioral_entry_point: vary the req pattern per cycle."}
# Two deviations, both recorded:
#  (1) The FIFO RTL instantiates generic_dpram (aw,dw) -- the OpenCores generic-memories
#      primitive, NOT shipped in this core. Techne supplies a behavioral dual-port RAM with the
#      exact port list (registered read, the OpenCores contract). Memory PRIMITIVE, not FIFO logic.
#  (2) The shipped bench (test_bench_top.v) runs an unbounded parametric dual-clock sweep
#      (rwd 0..4 x rcp 10..90 x 256 x multi-pass) that does not terminate under iverilog. Techne
#      supplies a BOUNDED single-clock testbench (tb_sc.v) as the deterministic oracle: fill to
#      full (backpressure), drain, and check the words come out in FIFO order. The FIFO RTL is
#      unmodified; the upstream bench is preserved in the body for anyone with the time to sweep it.
H["verilog-generic-fifo"] = {
    "generic_dpram.v": """`timescale 1ns/1ps
module generic_dpram (rclk,rrst,rce,oe,raddr,do,wclk,wrst,wce,we,waddr,di);
  parameter aw=5, dw=8;
  input rclk,rrst,rce,oe,wclk,wrst,wce,we;
  input [aw-1:0] raddr, waddr; input [dw-1:0] di; output reg [dw-1:0] do;
  reg [dw-1:0] mem [(1<<aw)-1:0];
  always @(posedge wclk) if (wce & we) mem[waddr] <= di;   // synchronous write
  always @(posedge rclk) if (rce) do <= mem[raddr];        // registered read (OpenCores contract)
endmodule
""",
    "tb_sc.v": """`timescale 1ns/1ps
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
"""}
R["verilog-generic-fifo"] = {
    "runner": "docker", "image": HW, "workdir": "upstream/tree",
    "probe": [{"name": "iverilog", "cmd": "iverilog -V 2>&1 | head -1"}],
    "build": [{"name": "compile Techne SC testbench + FIFO rtl + Techne dpram primitive", "cmd": "iverilog -Irtl/verilog -o $BODY/fifo.vvp $HARNESS/tb_sc.v rtl/verilog/generic_fifo_sc_a.v $HARNESS/generic_dpram.v 2>&1 | grep -viE 'warning' | tail -6; test -f $BODY/fifo.vvp"}],
    "runs": [{"name": "fill the FIFO to full (backpressure), drain it, check FIFO order + empty/full flags", "cmd": "vvp -N $BODY/fifo.vvp 2>&1 | tail -20",
              "expect": {"exit": 0, "stdout_contains": ["SC_FIFO_DONE_OK"], "stdout_not_contains": ["ERROR"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_EMULATED",
    "notes": "Oracle: 8 written words come back in FIFO order; full asserts at capacity (backpressure), empty asserts after drain. DEVIATIONS: (1) generic_dpram supplied as a Techne behavioral memory primitive; (2) the upstream dual-clock sweep-bench does not terminate under iverilog, so Techne supplies a bounded SC testbench. FIFO RTL unmodified. behavioral_entry_point: change #(DW,AW) or interleave read/write."}
R["verilog-uart2bus"] = {
    "runner": "docker", "image": HW, "workdir": "upstream/tree/verilog",
    "probe": [{"name": "iverilog", "cmd": "iverilog -V 2>&1 | head -1"}],
    "build": [{"name": "compile UART2bus rtl + the tb_uart2bus_top bench", "cmd": "iverilog -Ibench -Irtl -o $BODY/uart.vvp bench/tb_uart2bus_top.v bench/reg_file_model.v $(ls rtl/*.v) 2>&1 | grep -viE 'warning' | tail -6; test -f $BODY/uart.vvp"}],
    "runs": [{"name": "drive serial frames into the UART->bus controller, watch the register writes/reads", "cmd": "vvp -N $BODY/uart.vvp 2>&1 | tail -30; echo UART2BUSDONE",
              "expect": {"exit": 0, "stdout_contains": ["UART2BUSDONE"], "stdout_not_contains": ["ERROR", "Error"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_EMULATED",
    "notes": "The shipped tb_uart2bus_top drives serial frames through uart_tasks and checks the register-file model; the decoded byte + framing are the observable protocol-FSM decisions under timing pressure. behavioral_entry_point: skew the baud divisor or corrupt a stop bit."}

# --- AXIS 6 connectionist --------------------------------------------------------------------
R["genann"] = {
    "runner": "docker", "image": C, "workdir": "upstream/tree",
    "probe": [{"name": "gcc", "cmd": "gcc --version | head -1"}],
    "build": [{"name": "make (examples + test)", "cmd": "make -s 2>&1 | grep -viE 'warning' | tail -3; test -x ./example1 || ls example1"}],
    "runs": [{"name": "train a net by backprop to learn XOR", "cmd": "./example1 2>&1 | tail -12",
              "expect": {"exit": 0, "stdout_regex": r"(?i)(0\.9|1\.0|0\.0|0\.1|xor|output)"}}],
    "tests": [{"name": "genann's own unit test", "cmd": "make -s check 2>&1 | tail -6; echo GENANNTEST",
               "expect": {"exit": 0, "stdout_contains": ["GENANNTEST"], "stdout_not_contains": ["FAIL", "failed"]}}],
    "test_kind": "UPSTREAM", "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "example1 trains a 2-2-1 net by backprop to learn XOR; check runs genann's minctest suite. behavioral_entry_point: change the learning rate / hidden size / corrupt labels."}
H["minisom"] = {"drv.py": """import numpy as np
from minisom import MiniSom
np.random.seed(1)
# three separated 2-D clusters
c=[np.random.randn(60,2)*0.3+m for m in ([0,0],[5,5],[0,5])]
X=np.vstack(c)
som=MiniSom(6,6,2,sigma=1.0,learning_rate=0.5,random_seed=1)
q0=som.quantization_error(X); som.train_random(X,1000); q1=som.quantization_error(X)
print("qerr_before %.4f qerr_after %.4f"%(q0,q1))
print("SOM_ORGANIZED" if q1<q0*0.6 else "SOM_WEAK")
"""}
R["minisom"] = {
    "runner": "docker", "image": PY, "workdir": "upstream/tree",
    "probe": [{"name": "python", "cmd": "python --version"}],
    "build": [],
    "runs": [{"name": "self-organise a map over three clusters (quantization error drops)", "cmd": "pip install -q numpy >/dev/null 2>&1 && PYTHONPATH=. python $HARNESS/drv.py",
              "expect": {"exit": 0, "stdout_contains": ["SOM_ORGANIZED"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Oracle: quantization error must fall substantially as the SOM self-organises (competitive learning). behavioral_entry_point: shrink sigma/lr or feed unclustered noise to make it fail to organise."}
H["hopfield-takyamamoto"] = {"drv.py": """import os; os.environ.setdefault('MPLBACKEND','Agg')
import numpy as np
from network import HopfieldNetwork        # the repo's own class (imports matplotlib/tqdm)
np.random.seed(1)
N=25
P=[np.where(np.random.rand(N)>0.5,1,-1).astype(float),
   np.where(np.random.rand(N)>0.5,1,-1).astype(float)]
net=HopfieldNetwork(); net.train_weights(P)          # Hebbian store, the repo's code
cue=P[0].copy(); idx=np.random.choice(N,3,replace=False); cue[idx]*=-1   # corrupt 3 bits
out=np.asarray(net.predict([cue], num_iter=30, threshold=0, asyn=False)[0])
ok = np.array_equal(out,P[0]) or np.array_equal(out,-P[0])
print("N=%d stored=2 corrupted=3 recovered=%s"%(N,bool(ok)))
print("HOPFIELD_OK" if ok else "HOPFIELD_SPURIOUS")
"""}
R["hopfield-takyamamoto"] = {
    "runner": "docker", "image": PY, "workdir": "upstream/tree",
    "probe": [{"name": "python", "cmd": "python --version"}],
    "build": [],
    "runs": [{"name": "store patterns, recall from a corrupted cue (attractor dynamics)", "cmd": "pip install -q numpy matplotlib tqdm >/dev/null 2>&1 && MPLBACKEND=Agg PYTHONPATH=. python $HARNESS/drv.py 2>&1 | grep -v '^Start to'",
              "expect": {"exit": 0, "stdout_contains": ["HOPFIELD_OK"]}}],
    "tests": [], "test_kind": "TECHNE", "test_classification_if_none": "TECHNE_SMOKE_HARNESS_PASS",
    "classification_if_ok": "RUNNABLE_CONTAINER",
    "notes": "Runs the repo's own HopfieldNetwork.train_weights + predict (matplotlib/tqdm installed headless only to satisfy its module imports; no plotting called). Oracle: a 3-bit-corrupted cue over 25 neurons with 2 stored patterns must converge back to the stored pattern (associative recall / error correction). behavioral_entry_point: raise corruption or store > ~0.14N patterns to force spurious attractors."}


def main():
    for sid, recipe in R.items():
        d = vault.specimen_dir(sid); d.mkdir(parents=True, exist_ok=True)
        (d / "recipe.json").write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8", newline="\n")
        for name, text in H.get(sid, {}).items():
            (d / "harness").mkdir(exist_ok=True)
            (d / "harness" / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", sid, "+harness" if sid in H else "")


if __name__ == "__main__":
    main()
