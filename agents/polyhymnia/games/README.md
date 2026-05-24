# Polyhymnia Games

Games are how the Omnitensor stops being a static knowledge object and starts becoming a play surface. They also double as Learner training data — each game is a `(prompt, expected response)` generator.

The catalog below was largely contributed by a ChatGPT cross-frontier review on 2026-05-24 and curated by Aporia. Adopting verbatim; Polyhymnia's job is to instantiate them as runnable scripts when Phase 0.5 lands.

## The seven games

### 1. Name That Decomposition
Given formula snippets, code snippets, and partial descriptions, identify the method family: CP, Tucker, TT, tensor network, completion, contraction, rank theory.

- **Tesserae used:** `object_kind ∈ {equation, algorithm, decomposition}`
- **Output:** classification + confidence + supporting tesserae shown
- **Learner training value:** classification head over reasoning-tagged code

### 2. Tensor Archaeology
Given a modern method, trace its ancestry backward through papers, people, fields, and formulas.

Example: Tensor Train → Matrix Product States → DMRG → quantum spin chains → numerical linear algebra translation.

- **Tesserae used:** lineage_ancestors tag axis traversed backwards from a seed
- **Output:** a timeline + a graph + a beginner lesson
- **Learner training value:** historical reasoning chains

### 3. Frankenfactorization
Take two unrelated tensor methods and force an agent to invent a hybrid game.

Example: combine hyperspectral tensor completion with matrix multiplication tensor rank.

- **Tesserae used:** two far-apart cells from `object_kind=decomposition`
- **Output:** creative bridge artifact (may be nonsense — that's fine)
- **Learner training value:** open-ended combinatorial generation under constraint

### 4. Find the Hidden Axis
Given a dataset description, propose the axes that make it tensorial.

Example: "Scientific papers with citations and formulas" → `paper × author × concept × formula × year × field × citation_relation`.

- **Tesserae used:** `object_kind=dataset` cells (Dataset Scour output)
- **Output:** proposed axis list + which axes are sparse
- **Learner training value:** tensor-vision pattern recognition

### 5. Contraction Goblin
Given an `einsum` expression or tensor network, find cheaper contraction paths.

- **Tesserae used:** `code_language=python` + `free_tags contains 'einsum'`
- **Output:** alternate contraction path + cost comparison
- **Learner training value:** concrete algorithmic optimization

### 6. Open Problem Pinata
Pick one open tensor problem from the Omnitensor. Generate: plain-English explanation + toy version + synthetic dataset + baseline method + scoring rule + one-hour agent challenge.

- **Tesserae used:** `object_kind=problem` AND `epistemic_status ∈ {MENTIONED, EXTRACTED}` AND lineage shows no `solves` edge
- **Output:** a self-contained challenge bundle ready to fire at an agent or human
- **Learner training value:** problem-decomposition curriculum

### 7. One Tensor To Rule Them All
Given 20 new artifacts, agents must place each into the Omnitensor by inventing coordinates. The judge scores consistency, usefulness, interestingness.

- **Tesserae used:** holdout set, validated by the existing Omnitensor's coordinate structure
- **Output:** scored coordinate assignment + axis-evolution proposal
- **Learner training value:** schema evolution through play; teaches the agent to grow the axes

## Implementation conventions (when Phase 0.5 ships)

- Each game lives in its own module: `agents/polyhymnia/games/<game_name>.py`
- Each exposes `generate(tensor: PolyhymniaTensor, seed: Any = None, n: int = 1) → list[GameInstance]`
- Each `GameInstance` is a dict: `{game_id, prompt, expected_response, scoring_rubric, source_tesserae, generated_at}`
- Games write to `agents/polyhymnia/games/generated/<date>/<game_id>.json` (gitignored — large)
- Lenses and games share a common rendering surface (jinja-style template or markdown formatter)

## CLI sketch (Phase 0.5)

```
python -m agents.polyhymnia.daemon game generate --type tensor_archaeology --seed "Tensor Train"
python -m agents.polyhymnia.daemon game play --type contraction_goblin --difficulty easy
python -m agents.polyhymnia.daemon game leaderboard --type open_problem_pinata
```

— Aporia, 2026-05-24 (game catalog from ChatGPT cross-frontier 2026-05-24)
