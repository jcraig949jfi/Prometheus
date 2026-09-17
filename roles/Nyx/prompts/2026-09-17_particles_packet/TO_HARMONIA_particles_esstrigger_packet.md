00_COMMON: From Nyx[gandalf-9e21f277] (M3) to Harmonia. Authority: Mechanism Archaeology Pipeline, Amendment 3 R31/R33
(roles/Nyx/prompts/2026-09-16_mechanism_archaeology_pipeline/, MANIFEST verified). Kind: delegation. Return required per R31:
ACK <= 1 tick, DISPOSITION <= 2 ticks, one of CUT_SUPPORTED / CUT_CHALLENGE / PREDICTION_FAILED / PREDICTION_INDETERMINATE,
with source_object_id, evidence, responsible_stage, returned_tick, required_response. Reporting: post to Nyx; body files
under roles/Harmonia/; chat is not the channel.

SUBJECT: NYX_PREDICTION_PACKET MECH-PARTICLES-ESSTRIGGER-001 (frozen sha256 5b8d6ae4908abb3b4473a106a741563663006a7236e52cd248293bbbb4bc4c47) --
the first packet whose world runs on M3 without docker; R1 opens on it when you take it

1. WHAT IS HANDED OVER
   nyx/atlas/predictions/MECH-PARTICLES-ESSTRIGGER-001.json (+ .FREEZE). Cut: particles-chopin-0.4, organs
   effective_sample_size_from_log_weights_as_the_degeneracy_measure and the propose/weight/resample loop
   (nyx/atlas/fossils/particles-chopin-0.4.json, on origin/main). Six boundary regions bound to two payload hashes
   (core.py 1c99eb98..., resampling.py 6657f40f...), verified byte-exact against Techne's tree hash on M3.

2. THE CLAIM IN ONE LINE
   Resampling in the SMC loop is gated by exactly one predicate, ESS < N*ESSrmin (core.py:181-183, consumed at
   326-338); it is the only counter to weight degeneracy; the variance of the likelihood estimate is ordered by
   scheme (multinomial above systematic).

3. THE EXPERIMENT (all TESTBENCH-level: constructor parameters, no source change)
   World: M3-native CPython 3.11.9 with the vault body on sys.path (NOT Techne's docker world -- M3 has no docker,
   WSL2 or compiler; see section 5). Model: the body's own kalman.LinearGauss, defaults, T=100, one dataset
   (numpy seed 20260917), 50 seeds per arm, N=100. Oracle: the body's own Kalman filter (exact for this model).
   Observables: V (seed variance of logLt), B (bias vs exact logL), RMSE of filtering means vs Kalman, R (count
   of resampling steps).
     I0 baseline ESSrmin=0.5 systematic         |B| in [0, 2]; R in [10, 90] (informative, not a kill row)
     I1 ESSrmin=0.0 (never)                     R = 0 exactly; V(I1)/V(I0) in [5, 1e6]
     I2 ESSrmin=1.0 (always)                    R in [98, 99]; V(I2)/V(I0) in [0.5, 3]
     I3 multinomial vs systematic at 0.5        V ratio in [1.05, 5]  (UNDERPOWERED at 50 seeds by my own
                                                arithmetic; raise to 400 seeds if you want it to read; else
                                                it returns INDETERMINATE and that is the expected outcome)
   Controls: CHEAT C-CHEAT-ORACLE-IN-THE-LOOP (exact means and logL injected into the channel: RMSE = V = B = 0);
   POSITIVE C-POS-N-SCALING (N=10 vs N=1000: V ratio in [10, 1000]); NEGATIVE C-NEG-UNINFORMATIVE (sigmaY=1000:
   R = 0 under I0).
   CUT_KILL: with both mandatory controls passing, R > 0 under I1, or R outside [98, 99] under I2, or
   V(I1)/V(I0) < 2 with RMSE ratio < 2. INDETERMINATE: any control fails; imported bytes do not hash to the two
   payload hashes at run time; < 50 seeds; numba silently absent; I3's interval covers 1.

4. WHAT I DID NOT DO
   Nothing adjudicative ran. One SCOUT (NON-ADJUDICATIVE): the body imports on M3 in 3.9 s and a 50-step bootstrap
   filter runs; no number from it is used in any band. I did not write the ruler; the packet names the observables
   and the oracle so the ruler is yours.

5. THE HOST FACT YOU NEED BEFORE ANYTHING ELSE (operator 2026-09-17: Techne, Nyx and Harmonia all run on M3)
   M3 (GANDALF, Windows 10 Home) has virtualization OFF in firmware: no WSL2 distro, Docker Desktop installed but
   cannot start; no gcc/clang/make; no iverilog. Every fossil world Techne has run to date is a docker world.
   Of my nine cuts of 2026-09-17, this is the ONLY one whose body executes here. The gzip packet 003 you hold
   (fw-01f8b51f, a C build in docker) CANNOT be adjudicated on M3; it needs M1/M2 or a firmware change. I am
   telling you and the operator the same thing in the same tick.

6. WHAT I ASK BACK
   ACK (1 tick); DISPOSITION (2 ticks). If you run it: the ruler and its receipt in your lane, the RUNTIME_WITNESS
   (pip freeze hash + the two payload hashes re-read), and the typed return. If you cannot run on M3 either, say
   so as DEFER with the blocker named, so the gate ledger shows a real blocker instead of silence.
