C1b BUDGET CALIBRATION (controls only; rule in crius/calibrate_c1b.py)
streams: gate 301-310 (depths 2-3), qual 201-203 (depth 4 only); code a78569dad
depth  n   old   RANDOM<5pct at  proc_p95  proc_max  headroom(2xp95)  NEW  random_rate_at_new  conflict
  2   160   800      50             18       266        36.0          50   0.025   False
      random solve-within-b curve: 50:0.025 100:0.037 200:0.069 300:0.087 400:0.144 500:0.181 600:0.225 700:0.237 800:0.269
  3   140  1200      50             21       984        42.0          50   0.0143   False
      random solve-within-b curve: 50:0.014 100:0.029 200:0.043 300:0.057 400:0.079 500:0.093 600:0.107 700:0.129 800:0.129 900:0.150 1000:0.186 1100:0.214 1200:0.221
  4    12  1600    None             20        20        40.0          50   0.0833   True
      random solve-within-b curve: 50:0.083 100:0.083 200:0.083 300:0.083 400:0.083 500:0.083 600:0.083 700:0.083 800:0.083 900:0.083 1000:0.083 1100:0.083 1200:0.167 1300:0.167 1400:0.167 1500:0.167 1600:0.167
budget vector (interactions_by_depth): {"1": 2000, "2": 50, "3": 50, "4": 50}
new config hash: bbf684cd638167f2
