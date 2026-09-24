# ALife / open-endedness ecosystem catalogue -- record schema (one JSON object per line)

Write ONE JSON object per line to your assigned .jsonl file (UTF-8, no trailing commas).
Fields (omit a field rather than guess; never invent a URL, DOI, arXiv id, year or author):

{
 "id": "kebab-case-slug, unique, e.g. poet, enhanced-poet, avida, lenia",
 "name": "canonical name",
 "aliases": ["..."],
 "cluster": "your cluster label",
 "year_first": 2019,                      // first publication/release year if known
 "people": ["lead authors or group"],     // as published
 "institution": "lab / company if known",
 "motivation": ["open_endedness" | "origin_of_life" | "ecology" | "evolutionary_biology" | "robotics" | "rl_curriculum" | "ai_benchmark" | "program_synthesis" | "art" | "education" | "game" | "other:<word>"],
 "world": {"kind": "discrete_grid | continuous_field | particles | physics_3d | physics_2d | program_memory | graph | chemistry | text_or_code | game_env | procedural_terrain | other:<word>",
           "notes": "one sentence: what the world is"},
 "organism": {"representation": "machine_code | genome_bytes | cppn | neural_net | morphology_plus_controller | ca_pattern | kernel_params | reaction_rules | llm_program | llm_agent | policy | other:<word>",
              "development": true|false|null, "notes": "one sentence"},
 "pressure": {"kind": ["implicit_replication" | "resource_competition" | "explicit_fitness" | "novelty" | "quality_diversity" | "minimal_criterion" | "coevolution" | "environment_coevolution" | "curriculum_regret" | "human_or_model_judgment" | "predator_prey" | "other:<word>"],
              "notes": "one sentence"},
 "search": "algorithm(s): e.g. GA, ES, NEAT, MAP-Elites, novelty search, RL (PPO), self-replication (no external search), LLM mutation",
 "environment_generation": "none | fixed | procedural | co-evolved | learned (world model) | LLM-generated",
 "architecture": {"language": "C++ | Python | JAX | CUDA | JS | Rust | ...", "accelerator": "CPU | GPU | TPU | mixed", "scale_note": "one phrase"},
 "key_claims": ["1-3 short sentences: what it is known for / what it demonstrated"],
 "open_endedness_evidence": "one sentence or 'none claimed'",
 "papers": [{"title": "...", "year": 2019, "venue": "...", "url": "https://...", "doi": "...", "arxiv": "1901.01753", "url_status": "VERIFIED|SEARCH_RESULT|UNVERIFIED"}],
 "code": [{"url": "https://github.com/...", "license": "...", "language": "...", "last_activity_year": 2024, "official": true|false, "url_status": "VERIFIED|SEARCH_RESULT|UNVERIFIED"}],
 "other_links": [{"kind": "website|demo|dataset|video|docs", "url": "...", "url_status": "..."}],
 "runnable_today": "yes | likely | unknown | no (why)",
 "status": "active | maintained | archived | historical",
 "relatives": ["ids of closely related entries (parents, variants, reimplementations)"],
 "prometheus_analogue": "one phrase: which of our shapes it resembles -- program-soup organism in a task world (SFE/NPE-like), environment-organism co-evolution (POET-like), continuous field pattern search, embodied morphology, LLM-driven search, or 'none'",
 "notes": "anything else useful for a later reader"
}

url_status: VERIFIED = you fetched the URL and it resolved to the thing; SEARCH_RESULT = seen in a search
result but not fetched; UNVERIFIED = from memory. Prefer VERIFIED for every code repo.
Quality over quantity, but breadth matters: aim for 30-60 distinct systems in your cluster,
including lesser-known and hobbyist-but-substantial ones, and historical ones with no code.
Do not duplicate another cluster's core systems unless yours adds a variant; list variants as their own entries.
