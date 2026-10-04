# V2-B DEV-1 -- value-provenance observatory (prov0): design

Thread: TH-P2B-AETHER-V2B (operator directive 2026-10-04). Cycle 1, DEV window 1.
Limiting layer (the DEV question): the CONTENT DETECTOR. The XOR content signature failed its own fwd positive control
in rich soup (E-P1), and E-011's rcv_add lesion could not be completed without value provenance. Until this layer is
repaired, nothing above rung P2 is measurable.

## Design

An external SHADOW. The physics is not modified and is never given provenance metadata. Each tick the shadow reads:
- the pre-tick state;
- the kernel's existing read-only `observer` export, which gives each field's winning slot (V.step and K.gpu_step
  both provide it; aeth01_graph.py already uses it);
- the post-tick state;
- the law's declared commit rule.

Node table (append-only). Each committed template value (fields opcode/arg0/arg1/payload) gets a node:
`id, tick, site, field, value, op, parents[]`.
- **INIT**: leaf, tick 0.
- **COPY**: replacement by a winning proposal. 1 parent = the proposer's payload node (for fwd relays, the node of the
  byte the relay received).
- **ADD**: add-family composition. 2 parents = the previous target node and the incoming proposal node.
- **MUT**: a perturbation flip (recomputed with K.mu_vec). Parent = the pre-flip node, plus event tag (seed, tick, bit).
- **KEEP**: no winning write, so the node is unchanged (no new node).
- Losing proposals are never parents (arbitration records the winner only).
- Energy (field 4) is bookkeeping. In prov0 it is NOT a content lineage. Its winning transfer is recorded as an edge
  attribute only. This is stated as a prov0 limit.

**Self-check (the observatory's own P0).** Every tick, the shadow's predicted committed value for every site and field
must equal the physics output byte for byte. Any mismatch is a hard error. The shadow cannot silently drift from the
law.

Queries:
- `last_writer(site, field)`;
- `ancestry(node)` (DAG closure);
- `lineage_reach(origin_node)`: sites currently holding a descendant, with hop count, op mix (COPY-only = carried;
  passed through ADD/MUT = transformed; more than one independent INIT lineage = composed) and age.

These map directly to P3 (carried), P4 (transformed: descendant value != source value, ancestry kept), P5 (composed:
two or more distinct origin lineages) and P6 (persisted: at least k rewrites survived).

## Qualification fixtures (hand-worked known answers; tests)

1. direct forwarding (fwd relay copies its received byte);
2. no forwarding (an inert site keeps its node);
3. transformed forwarding (ADD: a descendant value differs but keeps ancestry);
4. two-parent composition (an ADD node has both parents);
5. perturbation (a MUT node with event tag; the value changed, the parent kept);
6. overwritten ancestry (a later COPY replaces the node; the old lineage is gone from that site);
7. arbitration between competing writers (only the winner is a parent).

Plus a rich-soup self-check: hundreds of ticks of v1, rcv, fwd, rcv_add and rcv_str with zero shadow/physics
mismatches.

## Frozen next TEST (written at the end of DEV-1, before any TEST run)

TEST-1, provenance qualification and first rung readings. In rich soup, does fwd's lineage reach exceed rcv's
(forwarding made visible: the E-P1 repair), and what P3-P6 profile do rcv_add and rcv_str show? Decision rules are fixed
in the TEST-1 preregistration.
