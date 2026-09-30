# Prometheus Collider

A mobile-first, full-screen vertical feed of generative 3D collisions between three
concepts. Each item is one world: three concept-bodies approach, collide, a new
structure emerges, and it stabilizes with a short reasoning shard. Swipe to the next.

The feed is seeded with **real Prometheus history**: every one of the 5,727 unique
concept triples that Nous evaluated (and Hephaestus tried to forge) between March and
April 2026, with a pointer to the exact artifact line it came from. Curated and
generated collisions are mixed in and are always labelled as such.

## Run

```
cd collider
npm install
npm run dev        # http://localhost:5188/
npm test           # vitest: grammar determinism, lineage, URL replay, provenance
npm run build      # tsc --noEmit + vite build -> dist/
npm run ingest     # re-derive public/data/ from the historical artifacts (read-only)
npm run snap       # puppeteer contact sheets + 35-swipe endurance (needs `npm run dev`)
```

`npm run snap` and `scripts/interact.mjs` / `scripts/smoke_prod.mjs` drive a local
Chrome (`C:/Program Files/Google/Chrome/Application/chrome.exe`). Edit `exe` in those
scripts on other machines.

URL options: `?q=high|mid|low` forces a quality tier; `?feed=N` sets the feed length
before it extends; `h` (or triple-tap the wordmark) toggles the HUD (fps, worlds alive,
GPU resources, heap).

### Controls

| Action | Touch / mouse | Key |
|---|---|---|
| next / previous | swipe, wheel | ↓ ↑ / j k |
| freeze / resume | ❙❙ rail | space |
| remix (replace one concept) | ↻ rail | r |
| reorder (same concepts, same seed, new order) | ⇄ rail | o |
| provenance sheet | ⓘ rail | i |
| collide your own three ideas | ✦ Collide | c |
| copy the replay URL | link rail | s |
| favourite | ♡ rail | f |
| sound (off by default) | speaker rail | m |

## What is real and what is not

| Badge | Meaning |
|---|---|
| **HEPHAESTUS · HISTORICAL** | Triple taken from `agents/nous/runs/<run>/responses.jsonl` line N. The provenance sheet shows the run, line, Nous scores, the model's own mechanism name (if it named one), and the forge outcome from `agents/hephaestus/ledger.jsonl`. The reasoning shard is an excerpt of that historical LLM output, labelled as such. |
| **CURATED SHOWCASE** | Hand-picked dictionary triples chosen to show each archetype. Not historical. |
| **GENERATED** | Feed-generated, remixed, or reordered. Remixes of a historical collision record `derivedFromHistorical`. |
| **YOUR COLLISION** | Typed in by you; names that match the Nous dictionary pick up its field and mechanism. |

Non-historical reasoning shards come from a deterministic template grammar and are
labelled *speculative synthesis — not a scientific claim*. **No collision in this app
is a validated finding.** The visual archetype encodes the concept signatures, not
truth.

See `FINDINGS.md` for what was inspected in the repo, what was ingested, and what was
deliberately left out.

## Architecture

```
public/data/                     derived by scripts/ingest_hephaestus.py (read-only over sources)
  concepts.json                    95 Nous concepts, 20 fields
  hephaestus-collisions.json       index of 5,727 historical triples (+ ingest-manifest.json sha256s)
  hephaestus/detail-<0-f>.json     lazily fetched shards: analysis excerpts, scores, forge outcome
src/model/
  hash.ts        fnv1a + mulberry32; everything random is seeded
  genome.ts      encodeConcept -> ConceptSignature; collisionOperator; compileCollision(concepts, seed) -> VisualGenome
  collision.ts   ids, makeCollision, remix / reorder (lineage: parentCollisionId + mutation), userConcept
  url.ts         #h=<historical id>  |  #n=A|B|C&s=seed&src=kind[&p=parent&m=mutation&a=archetype]
src/data/store.ts            DataStore (lazy shards, address resolution), FeedSource (historical/curated/generated mix)
src/synthesis/service.ts     provider chain: Historical -> External (VITE_SYNTH_URL, off) -> Template
src/render/
  engine.ts      ONE WebGL2 renderer, scissored viewports per slide, bounded world window, adaptive tiers
  world.ts       base World: phases, shared uniforms, particle builder, glyphs, dispose tracking
  glsl.ts        shared particle vertex template: approach body -> collision impulse -> emerge()
  glyphs.ts      concept names as shader text planes (approach billboard, impact stretch, orbit ring)
  archetypes/    8 World subclasses + registry
src/ui/app.ts                feed, rail, sheet, modal, keyboard/wheel, URL state, favourites, HUD
src/audio/sonify.ts          WebAudio: three voices glide into a chord at impact (muted by default)
```

**Determinism.** `compileCollision` is a pure function of the ordered concept names
(plus dictionary metadata) and the seed. Each concept is encoded to a signature
(field priors + mechanism affinities + name hash); the operator weights positions
0.5 / 0.3 / 0.2 and adds an antisymmetric twist term, so order matters. The archetype
is the argmax of affinity + calibrated offsets. All motion is analytic in time on the
GPU (reaction–diffusion excepted: it is a fixed-step Gray–Scott simulation from a
seeded initial state), so the same URL replays the same world.

**Archetypes.** CRYSTALLIZATION (polycrystal grains that meet at glowing boundaries),
VORTEX (interlocking toroidal cores + axial jets), FRACTURE (instanced shards, crack
glow), REACTION_DIFFUSION (GPU Gray–Scott on a sphere), ORBITAL_CAPTURE (three-body
choreographies), BRANCHING_GROWTH (three lineages growing from the impact),
STRANGE_ATTRACTOR (seven RK4-integrated systems), DIMENSIONAL_FOLD (Hopf fibration,
stereographically projected). The calibrated distribution over random dictionary
triples is 11–13.5% each.

**Lifecycle and memory.** Only slides i-1, i, i+1 own a World. Leaving the window
disposes every tracked geometry, material, texture and render target. Measured over
35 swipes: 37 worlds created, 34 disposed, max 3 alive, geometries 10→11, heap ~21 MB,
60 fps (RTX 5060 Ti, ANGLE/D3D11). If fps drops, the engine steps down a tier (46k →
24k → 11k particles).

## Extending

**Add an archetype**
1. Add the name to the `Archetype` union in `src/model/types.ts` and to `ARCHETYPES`,
   `MECH_AFFINITY` and `CALIBRATION` in `src/model/genome.ts`.
2. Write `src/render/archetypes/<name>.ts`: a `World` subclass whose `build()` calls
   `this.particles(n, EMERGE)` with a GLSL
   `vec3 emerge(float k, vec4 r, float idx, float te, inout vec3 col, inout float alpha, inout float size)`
   (k = concept index, r = per-particle randoms, te = time since emergence). Add extra
   meshes through `this.track(...)` so they are disposed.
3. Register it in `src/render/archetypes/index.ts` (`ARCHETYPE_WORLDS`, `ARCHETYPE_BLURB`).
4. Re-run `npx vite-node scripts/calibrate.ts`, paste the new offsets into
   `CALIBRATION`, and run `npm test` (the distribution test bounds every share to 6–22%).

**Add a concept source.** Emit records in the `HistoricalIndexRecord` shape (id, three
names, source, artifact path + line) from a read-only ingest script, add a `SourceKind`
if it is a new provenance class, and give it a badge in `styles.css`. Never label
generated content as historical.

**Plug in a synthesis model.** Set `VITE_SYNTH_URL` to an endpoint that accepts the
collision JSON and returns `{ title, reasoningShard }`. Its output is labelled
`external` and stays speculative. The template provider is the fallback.

## Limitations

- WebGL2 only. WebGPU is detected but not used.
- Reaction–diffusion needs float render targets (`EXT_color_buffer_float`). The
  half-float path rounds the updates away, so it is not supported. Devices without
  float targets fall back to nearest filtering; devices with no float targets at all
  will show a static pattern.
- Synthesis for non-historical collisions is a template grammar, not a model.
- `public/data` is ~8.5 MB committed (index gzips to ~280 KB; detail shards load lazily).
- Showcase triples pin their archetype so every archetype appears early in the feed;
  all other collisions use the grammar's own choice.
- Mechanism titles were extracted from the historical text only when the model named a
  specific mechanism (2,740 of 5,727). The rest show no title rather than an invented one.
