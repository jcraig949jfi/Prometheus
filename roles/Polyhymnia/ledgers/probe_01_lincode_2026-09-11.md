# PROBE-01 readout: lincode decoder family through the H5 exact reference (2026-09-11)

Preregistered at e6f0b64fb before this run. Rows: probe_01_lincode_2026-09-11.json (per-genome vectors).
Class map: herakles/eca/class_map_fixture.json (224 classes, sha256:ce7a5a4c12f702d2)

member               d  mean_reach  min  max  mean_neutral  mean_reach_classes  table_sha256
-------------------  -  ----------  ---  ---  ------------  ------------------  ------------
direct               1      8.0000    8    8        4.0000              7.7812  c8f5d0341d54
A0_member            1      8.0000    8    8        4.0000              7.7812  c8f5d0341d54
hamming              3      5.6875    0    7        2.2500              5.6104  c077ebbdbc46
random1              2      6.6875    2    8        2.5000              6.5942  073cd247ffa9
random2              2      7.2500    4    8        2.7500              7.1040  143ff228bb63
scrambled_hamming_3  -      5.6875    0    7        2.2500              5.6350  be7a8176aa18
balanced_7           -     11.7305    9   12        0.0444             11.5542  dded53a0f74a

reach histograms (rules):
  direct              {"8": 4096}
  A0_member           {"8": 4096}
  hamming             {"0": 256, "5": 512, "6": 2560, "7": 768}
  random1             {"2": 256, "6": 1280, "7": 1280, "8": 1280}
  random2             {"4": 256, "6": 256, "7": 1536, "8": 2048}
  scrambled_hamming_3 {"0": 256, "5": 512, "6": 2560, "7": 768}
  balanced_7          {"9": 5, "10": 115, "11": 859, "12": 3117}

neutral histograms:
  direct              {"4": 4096}
  A0_member           {"4": 4096}
  hamming             {"1": 2048, "2": 1280, "3": 512, "12": 256}
  random1             {"1": 1280, "2": 1280, "3": 1280, "10": 256}
  random2             {"1": 768, "2": 1792, "3": 512, "4": 512, "5": 256, "8": 256}
  scrambled_hamming_3 {"1": 2048, "2": 1280, "3": 512, "12": 256}
  balanced_7          {"0": 3921, "1": 168, "2": 7}

prediction / control table:

  P1 analytic                PASS     hamming: exactly 256 genomes at reach 0 / neutral 12 (planted; cheat control)
                                      -> count = 256
  P2 analytic                PASS     hamming: max reach <= 11, min reach 0
                                      -> max 7 min 0
  P3 analytic (corrected s7) PASS     hamming preimage: one component of 16, center degree 12; direct: 4-cube
                                      -> components [16] for all 256 rules (degree structure in tests)
  P4 analytic                PASS     scrambled(hamming) histogram and mean_neutral identical to hamming
                                      -> identical
  P5 analytic                PASS     A=0 member equals h5.direct.v0 entry for entry
                                      -> table_sha256 equal
  positive control           PASS     direct: {8: 4096}, neutral 4.0
                                      -> {"8": 4096}
  gate refusal               PASS     rule = g mod 255 refused by check_exact
                                      -> PASS: refused (decoder does not reach every rule exactly: missing [255])
  spread                     PASS     random1 != random2 on histogram or mean_neutral
                                      -> random1 mean_neutral 2.5 / random2 2.75
  M1 measured                MEASURED hamming mean neutral (expected BELOW 4.0)
                                      -> 2.2500; min 1 max 12; histogram {"1": 2048, "2": 1280, "3": 512, "12": 256}
  M2 measured                MEASURED hamming mean reach, rules (expected ABOVE 8.0)
                                      -> 5.6875; histogram {"0": 256, "5": 512, "6": 2560, "7": 768}
  M3 measured                MEASURED hamming mean reach, 224 classes (expected below M2; vs direct not predicted)
                                      -> 5.6104 vs direct 7.7812
  M4 guess                   MEASURED random1 / random2 mean neutral and mean reach (rules)
                                      -> random1 2.5000/6.6875; random2 2.7500/7.2500 (min_distance 2 / 2)
  M5 measured                MEASURED class-collapsed mean reach: hamming vs balanced_7 (no prediction)
                                      -> hamming 5.6104 vs balanced_7 11.5542

limits: access structure at the fixture scope on the published 224-class map; no usefulness claim; the live H5-1 map is partial (232/256) and not used
