# E-006 result -- mechanism combinations and the fwd control (Blocks D, E). CLOSED 2026-09-27 with one falsifier open.

Full account: Aether/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md s5. Reduction: REDUCTION.json (from 72 units, T-015..T-086,
flight aether-units-20260927T165531Z on an RTX A5000, 7 effective CPUs of 96 reported; unit files kept outside the repository at
C:/Prometheus-data/aether/C-002/E-006/attempts/, each sha256 in the receipt's units_manifest.json). Cause probe:
Aether/AETH-03/evidence/2026-09-27_content_probe/.

- rcv_add NEW_BEHAVIOUR, rcv_str NEW_BEHAVIOUR (preregistered N1 and N2; super-additive; every seed), rcv_cnd additive-or-less.
- Falsifier 1 (cause probe): the "content" they propagate is not transport. rcv_add = persistence of activity traces (76% of
  content differences are one-world writes; 7.6% of deep ones written in both worlds). rcv_str = activity re-routing activity via
  energy-steered aim, without injected noise.
- Block E: E-P1 FAILED -- the XOR content signature does not detect transport in a rich soup even for fwd; E-P2 fired; the probe
  explains why (timing marks and different-source substitution dominate). Instrument limit recorded.
- Falsifier 2 (10,000-tick horizon for rcv_add / rcv_str): NOT COMPLETED. Flight aether-units-20260927T173607Z: controller killed
  under host memory pressure; pod recovered and terminated by --resume; results lost to a resume defect (fixed, 3bd6f82b4). Not
  re-run without the operator (instruction attached to the stop).

Attempts of note: T-055/T-063/T-071/T-079 also ran on BUCKKEEP (attempts_buckkeep/): result hashes identical to the pod's.
