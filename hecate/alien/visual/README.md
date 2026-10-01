# Visual Cortex phase-2 set (prepared, not run)

sets.json: 15 unlabeled systems (per family: one standard alien, its
incompressible matched null, one known), 12 runs x 40 steps each. Every
visual channel maps to exactly one source variable ("channel i" = state
position i, range given); graph systems carry their link list, so a node
layout can be drawn from source structure, not invented.

key.json: hidden answer key (class, null type, planted properties) -- do
not open during an observation session. A human observer's calls
(structured / unstructured / anomaly at channel c, run r, step t) are
scored against key.json by the same rules as the model tasks; an anomaly
that cannot be mapped back to a channel and step is not scored as a hit.

Suggested renderings (any must preserve the channel->variable map):
lattice (position x time raster per run), field (state as a point cloud
over time), graph (node colour = value on the listed links), glyph strip
(rewrite family). Interactions to try: freeze, step, perturb one channel
(requires the simulator: hecate.alien.systems.step with the key's params).
