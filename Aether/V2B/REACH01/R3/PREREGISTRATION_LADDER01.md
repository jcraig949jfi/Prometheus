# REACH01 LADDER01 preregistration: where does spontaneous combination become discoverable?

Motivation: R3 (FRONTIER_NO_GAIN) found ZERO cells jointly dependent on both inputs in ~920k evaluations, with inputs
7 rows apart and the output 17 columns away. A scout (1024 random XOR patches per geometry, seen before this freeze):
- inputs 2 rows apart give 8-16 joint-dependent patches per 1024 (vs 0 in R3's geometry);
- output rung 0 in all 1024 at every geometry.
LADDER01 maps discoverability against output distance with the inputs close.

Physics, search code, arms, mutation, descriptor (v2) and certifier: as R3 attempt 2. One new parameter, --geom:
  G1 inputs (8,1), (10,1); output (9,6)    -- 5 columns from the input deposit
  G2 inputs (8,1), (10,1); output (9,10)   -- 9 columns
  G3 inputs (8,1), (10,1); output (9,18)   -- 17 columns (R3's output distance, inputs close)
Arms: C certificate-guided and A ordinary. 8 seeds, 20 x 1024 evaluations per unit (scaling rule 1x).
Certification: up to 10 COMBINE candidates per unit (ablation COMPOSE + autonomy).
Outcomes, per geometry and arm:
- DISCOVERED: >= 1 certified COMPOSE in >= 2/8 seeds.
- COMBINE_ONLY: COMBINE found but no COMPOSE.
- NONE.
Arm effect: C vs A seeds with COMBINE (descriptive at 8 seeds).
Escalation (4x seeds) is permitted only for a geometry where the C-vs-A comparison is unresolved AND discoveries exist.
A discovered AUTONOMOUS COMPOSE becomes the component for a genuine (non-assisted) R4c reuse test (separate
preregistration).

Hashes:
  7c23e8b270c9c34474c54d6ca327d69762e6463730a76b55fd2e3fa6d65e1039 plan_ladder_search.json
  5477e645499e15aad5ed2bd5179d534e797c34b81bcfd4243c0ac2e6b3ec88b5 plan_ladder_certify.json
  b5d0ba8c340d93788b7f3bacbea9b3e37f28f8cae353cd4be6f934eb10a84d96 r3_frontier.py
  520257905ce0ee739ab2f03513f22c8f9452c9ad3881d305f31a7cb8092a26a9 r3_certify_run.py
  851208e771ba2fc9e90dae7ded5bc2aeb77abf3a40a56525a5984e06f3ed86f7 r3_certify.py
