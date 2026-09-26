"""Batch 14 -- the ALife / open-endedness bodies the operator ordered landed (directives 2-4, 2026-09-17/18;
Nyx #379 ASK 3-5). FIND + PIN were done on 2026-09-17 (techne/acquisition/poet_alife/SOURCES_2026-09-17.json);
this batch writes the RECORDS. `python -m techne.fossils.harvest acquire <id>` fetches, hashes and pins.

New in this batch (Nyx #379 ASK 4, operator directive 4 s5): every record carries `runtime` =
{python_major, native_deps, host_class} so M3-runnability is readable from the record, and the ASAL /
TerraLingua data slices are their own artifacts with extract=False (an .npz is a zip and must stay a file).

Usage: python -m techne.fossils.batches.batch14_alife  [--write]
"""
from __future__ import annotations

import argparse

from techne.fossils import record

HF = "https://huggingface.co/datasets/GPaolo/TerraLingua/resolve/main/data/abundant_exp_1/"
TL_TOP = ["agent_events.json", "agent_names.json", "agent_trajectories.pkl", "artifacts.json", "communities.json",
          "food_counts.json", "graph.pkl", "messages.json", "open_gridworld.log", "params.json", "video.mp4"]
TL_ANN = ["anthropologist_notes.json", "being0.json", "being1.json", "being10.json", "being10_0.json", "being11.json",
          "being12.json", "being13.json", "being14.json", "being15.json", "being15_0.json", "being15_0_0.json",
          "being16.json", "being16_0.json", "being17.json", "being18.json", "being19.json", "being1_0.json",
          "being1_0_0.json", "being1_0_0_0.json", "being2.json", "being2_0.json", "being3.json", "being4.json",
          "being5.json", "being6.json", "being6_0.json", "being7.json", "being7_0.json", "being8.json", "being9.json",
          "token_usage.jsonl"]


def _url(url: str, filename: str) -> dict:
    return {"kind": "url", "url": url, "filename": filename, "extract": False}


S = [
    record.skeleton("poet-enhanced-2020",
        canonical_name="Enhanced POET -- Wang, Lehman, Rawal, Zhi, Li, Clune, Stanley (Uber AI, ICML 2020)",
        aliases=["Enhanced POET", "poet_distributed"],
        lineage="POET (2019, GECCO) -> Enhanced POET (2020, ICML): paired environment/agent coevolution with minimal-criterion admission, PATA-EC novelty and cross-environment transfer; the reference implementation for both lives in one repository (this = branch master)",
        domain=["open-ended-learning", "coevolution", "curriculum", "evolution-strategies", "quality-diversity"], era="2019-2020",
        version="uber-research/poet master @ 8669a17e6958f80cd547b2de61c51d4518c833d9 (last push 2022-03-23)",
        source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/uber-research/poet", "commit": "8669a17e6958f80cd547b2de61c51d4518c833d9"}]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/uber-research/poet", "branch": "master"},
        license={"spdx": "Apache-2.0", "status": "permissive", "evidence": "LICENSE + NOTICE in repo (Uber Technologies 2020)"},
        language=["Python"], build_system="none (pip requirements.txt)", compiler_or_interpreter="CPython 3 (paper era 3.6-3.7)",
        dependencies=["fiber", "neat-python", "gym[box2d] (Box2D needs SWIG + a C++ compiler)"],
        entry_points=["master.py (poet_distributed.poet_algo.PopulationManager.optimize)", "poet_distributed/es.py (ESOptimizer: update_pata_ec, evaluate_transfer, pick_proposal)", "poet_distributed/novelty.py (compute_novelty_vs_archive)", "poet_distributed/reproduce_ops.py (Reproducer.mutate)"],
        example={"command": "./run_poet_local.sh final_test", "input": "run_poet_local.sh arguments (mc_lower/mc_upper, max_num_envs, adjust_interval)", "output": "logs/<name>.<optim_id>.log CSVs + <optim_id>.best.json policies"},
        environment={"runner": "docker", "image": "NOT BUILT: needs a gym[box2d] world (SWIG, C++); named, not reconstructed"},
        runtime={"python_major": 3, "native_deps": ["Box2D (C++ via SWIG)", "fiber (multiprocessing/k8s runtime)"], "host_class": "compiler+docker host (M2 / Linux); NOT M3"},
        upstream_docs=["arXiv:2003.08536 (Enhanced POET, ICML 2020 PMLR 119)", "arXiv:1901.01753 (POET, GECCO 2019 DOI 10.1145/3321707.3321799)", "README.md"],
        human_capability_summary={"built_to": "invent an unbounded stream of learning challenges and solve them, transferring solutions across challenges", "pressure": "static curricula stall; hand-designed environment distances do not measure meaningful difference", "success_means": "agents solving environments unreachable by direct optimisation; ANNECS (accumulated number of novel environments created and solved) rising"},
        known_human_problem_solved="open-ended coevolution of problems and solvers",
        human_environmental_pressure="RL research where the environment distribution, not the learner, was the bottleneck",
        human_failure_condition="the population collapses to trivial or impossible environments; transfers never improve a target",
        behavioral_entry_point="PopulationManager.adjust_envs_niches(): mutate -> pass_mc on the parent's theta -> compute_novelty_vs_archive (PATA-EC) -> admit; ESOptimizer.evaluate_transfer/pick_proposal: the transfer boundary",
        acquisition_tags=["operator-directive-2026-09-17", "poet_alife", "TECHNE-104"]),

    record.skeleton("poet-original-2019",
        canonical_name="POET (original) -- Wang, Lehman, Clune, Stanley (Uber AI, 2019)",
        aliases=["Paired Open-Ended Trailblazer", "original_poet branch"],
        lineage="the 2019 algorithm on the repository's legacy branch original_poet; Enhanced POET (branch master) supersedes it with CPPN environments, PATA-EC novelty and ANNECS",
        domain=["open-ended-learning", "coevolution", "curriculum", "evolution-strategies"], era="2019",
        version="uber-research/poet original_poet @ 0b40743d414a11e1b96cb0b7869483462724bb1e",
        source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/uber-research/poet", "commit": "0b40743d414a11e1b96cb0b7869483462724bb1e"}]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/uber-research/poet", "branch": "original_poet"},
        license={"spdx": "Apache-2.0", "status": "permissive", "evidence": "LICENSE in repo"},
        language=["Python"], build_system="none (pip)", compiler_or_interpreter="CPython 3 (2019 era 3.6)",
        dependencies=["gym[box2d]", "ipyparallel or fiber (era-dependent; see README at the pin)"],
        entry_points=["master.py", "poet_distributed/poet_algo.py"],
        example={"command": "see README at the pin (legacy branch)", "input": "", "output": ""},
        environment={"runner": "docker", "image": "NOT BUILT (gym[box2d] world)"},
        runtime={"python_major": 3, "native_deps": ["Box2D (C++ via SWIG)"], "host_class": "compiler+docker host; NOT M3"},
        upstream_docs=["arXiv:1901.01753", "GECCO 2019 DOI 10.1145/3321707.3321799"],
        human_capability_summary={"built_to": "co-generate environments and their solutions with periodic transfer", "pressure": "same as Enhanced POET", "success_means": "environments solved that direct optimisation cannot reach"},
        known_human_problem_solved="open-ended coevolution of problems and solvers (first version)",
        lineage_relations=[{"relation": "superseded_by", "to": "poet-enhanced-2020", "note": "same repository, branch master"}],
        acquisition_tags=["operator-directive-2026-09-17", "poet_alife", "TECHNE-104", "TECHNE-18"]),

    record.skeleton("asal-sakana-2024",
        canonical_name="ASAL -- Automating the Search for Artificial Life with Foundation Models (Kumar et al., Sakana AI / MIT, 2024-2025)",
        aliases=["ASAL"],
        lineage="Lenia (Chan 2019), Boids, Particle Life, NCA and Life-like CA substrates searched with CLIP as the observer; Artificial Life 31(3) 2025",
        domain=["artificial-life", "open-endedness", "foundation-model-observer", "cellular-automata", "quality-diversity"], era="2024-2025",
        version="SakanaAI/asal main @ 677ba0ea4d3b3ca78273c9906c6e84d2b1481ce7 (last push 2025-10-23)",
        source_origin={"artifacts": [
            {"kind": "git", "url": "https://github.com/SakanaAI/asal", "commit": "677ba0ea4d3b3ca78273c9906c6e84d2b1481ce7"},
            _url("https://pub.sakana.ai/asal/data/illumination_boids.npz", "illumination_boids.npz"),
            _url("https://pub.sakana.ai/asal/data/illumination_plife.npz", "illumination_plife.npz"),
            _url("https://pub.sakana.ai/asal/data/sweep_gol.npz", "sweep_gol.npz")]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/SakanaAI/asal", "datasets": "pub.sakana.ai/asal/data (illumination_lenia.npz was 404 on 2026-09-17)"},
        license={"spdx": "Apache-2.0", "status": "permissive", "evidence": "LICENSE in repo; datasets carry no separate licence statement (recorded, not assumed)"},
        language=["Python"], build_system="none (pip requirements.txt)", compiler_or_interpreter="CPython 3.10 (README)",
        dependencies=["jax 0.4.38 (needs AVX on CPU)", "flax", "evosax", "transformers (FlaxCLIPModel openai/clip-vit-base-patch32)", "einops"],
        entry_points=["asal_metrics.py (calc_open_endedness_score, calc_illumination_score, calc_supervised_target_score)", "rollout.py (rollout_simulation)", "substrates/lenia.py, boids.py, plife.py, gol.py, ...", "main_opt.py / main_illuminate.py / main_sweep_gol.py"],
        example={"command": "python main_opt.py --substrate lenia --fm clip ...", "input": "substrate parameters (evosax search)", "output": "rollout embeddings (8x512) and the score"},
        environment={"runner": "native", "note": "on M3 the metric and observer were exercised via a numpy/torch port (techne/scripts/techne107_asal_observer.py); ASAL's own JAX path needs AVX"},
        runtime={"python_major": 3, "native_deps": ["jaxlib (AVX required)", "torch (for the M3 port)", "CLIP ViT-B/32 weights ~354 MB"], "host_class": "any x86-64 with AVX for the JAX path; M3 runs the metric + observer via torch"},
        upstream_docs=["arXiv:2412.17799", "README.md", "MIT Press Artificial Life 31(3) 2025"],
        human_capability_summary={"built_to": "find ALife simulations by target phenomenon, open-ended novelty or illumination, using a vision-language model as the measuring instrument", "pressure": "hand-written metrics cannot capture lifelike behaviour; manual parameter search does not scale", "success_means": "simulations whose CLIP-embedded rollouts satisfy the target / novelty / diversity objective"},
        known_human_problem_solved="replacing hand-authored phenotype metrics with a learned observer",
        behavioral_entry_point="calc_open_endedness_score(z): mean over frames of max similarity to any earlier frame, minimised (TECHNE-107 measured what it rewards)",
        acquisition_tags=["operator-directive-2026-09-17", "poet_alife", "TECHNE-107"]),

    record.skeleton("tierra-6.02-ray-1998",
        canonical_name="Tierra 6.02 -- Thomas S. Ray (1991-1998), mirror of the life.ou.edu source",
        aliases=["Tierra", "Tierra Simulator V5.0/6.02"],
        lineage="Ray 1991 'An approach to the synthesis of life' (Artificial Life II) -> Tierra releases through 6.02 (1998); Avida (1993-) is the instrumentation-rich descendant lineage",
        domain=["artificial-life", "digital-evolution", "self-replication", "virtual-machine", "ecology"], era="1991-1998",
        version="acisternino/tierra master @ 195c2eb84d91a1938faabad38e24b9b47d0e262c (mirror of Tierra v6.02 from life.ou.edu; two further mirrors pinned in SOURCES_2026-09-17.json)",
        source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/acisternino/tierra", "commit": "195c2eb84d91a1938faabad38e24b9b47d0e262c"}]},
        source_type="HISTORICAL_ARCHIVE_MIRROR", source_identity={"archive": "life.ou.edu/tierra/source/Tierra6_02.tgz (original URL, offline); mirror github.com/acisternino/tierra"},
        license={"spdx": "custom non-commercial (Ray, tierra/license.h 1995): free copying and distribution without fees; no commercial use; modified versions must document changes and notify the principal author; notice must not be removed", "status": "read 2026-09-17; preservation and research permitted; NOT OSI", "evidence": "tierra/license.h at the pin"},
        language=["C"], build_system="make (per-platform Makefiles under tierra/)", compiler_or_interpreter="gcc (era: SunOS/Linux 1990s; build in fossil-c bookworm to be measured)",
        dependencies=["libc", "X11 (optional GUI: Bgl-GUI_X11)"],
        entry_points=["tierra/tierra.c (the simulator)", "tierra/genebank.h / rambank.c / diskbank.c (the gene bank: what earns a permanent name and is saved as a .gen)", "tierra/soup_in (configuration)"],
        example={"command": "make -C tierra && ./tierra soup_in", "input": "soup_in (soup size, mutation rates, gene bank settings) + the ancestor 0080aaa", "output": "gb/ directory of .gen genotypes (the gene bank); tierra.log"},
        environment={"runner": "docker", "image": "prometheus-fossil-c:bookworm (to be measured; not built on M3)"},
        runtime={"python_major": None, "native_deps": ["C toolchain", "X11 for the optional GUI only"], "host_class": "compiler host (M2 / Linux); NOT M3"},
        upstream_docs=["Ray 1993 Artificial Life 1(1) DOI 10.1162/artl.1993.1.179", "tomray.me/pubs/doc/ (Documentation for the Tierra Simulator)", "tierra/README, Tierra.doc"],
        human_capability_summary={"built_to": "evolve self-replicating machine-code creatures in a shared memory 'soup' under CPU-time and space competition", "pressure": "study open-ended evolution with a substrate simple enough to run on 1990s hardware and rich enough for parasitism to arise", "success_means": "the gene bank filling with novel, persistent genotypes; parasites, hyperparasites and social behaviour observed"},
        known_human_problem_solved="a minimal executable ecology in which evolution invents ecological relations unprogrammed by the author",
        human_environmental_pressure="disk and compute scarcity: only genotypes that earn a name are banked (the admission rule Nyx will cut)",
        human_failure_condition="the soup dies out or fills with the ancestor only; the bank records nothing new",
        behavioral_entry_point="run to a fixed number of instructions and diff gb/ against the ancestor; vary the admission threshold in soup_in",
        acquisition_tags=["operator-directive-2026-09-17", "poet_alife", "TECHNE-106"]),

    record.skeleton("terralingua-2026",
        canonical_name="TerraLingua -- Emergence and Analysis of Open-endedness in LLM Ecologies (Paolo et al., Cognizant AI Lab, 2026)",
        aliases=["TerraLingua", "AI Anthropologist"],
        lineage="LLM-agent ecology (2026) with a post-hoc LLM annotation pipeline; sibling of OpenLife (ALIFE 2026) and Conversable Complexity (2026)",
        domain=["artificial-life", "llm-agents", "cultural-evolution", "open-endedness", "annotation-pipeline"], era="2026",
        version="cognizant-ai-lab/terralingua main @ bf276dbe33e66b2c3b592df27df8ca42c489a4c7 (last push 2026-09-02)",
        source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/cognizant-ai-lab/terralingua", "commit": "bf276dbe33e66b2c3b592df27df8ca42c489a4c7"}]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/cognizant-ai-lab/terralingua"},
        license={"spdx": "Apache-2.0", "status": "permissive", "evidence": "LICENSE in repo"},
        language=["Python"], build_system="none (pyproject.toml)", compiler_or_interpreter="CPython 3",
        dependencies=["an LLM API (anthropic / openai clients) for the agents and for the AI Anthropologist", "ffmpeg for videos"],
        entry_points=["main.py / run_experiment.sh (the ecology)", "analysis_scripts/001..006 (the AI Anthropologist; 006_artifact_philogeny.py = artifact ancestry by text match or LLM inference)"],
        example={"command": "python analysis_scripts/006_artifact_philogeny.py", "input": "an experiment's agent logs + artifacts.json (see terralingua-data-abundant-exp-1)", "output": "artifact ancestry edges with relationship type and model confidence"},
        environment={"runner": "native", "note": "analysis scripts are pure Python; the LLM arm needs an API key and spend (operator decision)"},
        runtime={"python_major": 3, "native_deps": [], "host_class": "any Python 3 host for the deterministic analysis; LLM arms need network + keys"},
        upstream_docs=["arXiv:2603.16910", "README.md", "analysis_scripts/AI_ANTHROPOLOGIST.md"],
        human_capability_summary={"built_to": "run a persistent multi-agent LLM ecology and reconstruct its cultural history afterwards", "pressure": "understanding coordination, institutions and culture in agent populations", "success_means": "cooperative norms, division of labour and branching artifact lineages observed and annotated"},
        known_human_problem_solved="post-hoc reconstruction of cultural ancestry in an LLM ecology (inference, not recorded provenance -- MEASURED 2026-09-17)",
        behavioral_entry_point="006_artifact_philogeny.py with BYNARY/LLM_PHYLOGENY toggles: method 1 (text match) vs method 2 (LLM) on the same experiment",
        acquisition_tags=["operator-directive-2026-09-17", "poet_alife", "TECHNE-108"]),

    record.skeleton("terralingua-data-abundant-exp-1",
        canonical_name="TerraLingua dataset slice: experiment abundant_exp_1 (top-level files + annotations/)",
        aliases=["hf GPaolo/TerraLingua data/abundant_exp_1"],
        lineage="one of the 40 experiments (8 conditions x 5 repetitions) of terralingua-2026; annotations by Claude Sonnet 4.5 / Haiku 4.5 per the dataset README",
        domain=["dataset", "artificial-life", "llm-agents", "annotations"], era="2026",
        version="hf GPaolo/TerraLingua main (lastModified 2026-03-19); files pinned by sha256 at acquire",
        source_origin={"artifacts": [_url(HF + f, f) for f in TL_TOP] + [_url(HF + "annotations/" + f, "annotations__" + f) for f in TL_ANN]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"dataset": "huggingface.co/datasets/GPaolo/TerraLingua", "path": "data/abundant_exp_1 (+ annotations/); agent_logs/, artifact_analysis/, community_annotations/ NOT taken"},
        license={"spdx": "Apache-2.0 (dataset card tag)", "status": "permissive", "evidence": "hf dataset card license tag"},
        language=["JSON", "pickle", "log"], build_system="none", compiler_or_interpreter="n/a",
        dependencies=[], entry_points=["artifacts.json, messages.json, agent_events.json, open_gridworld.log; annotations__being*.json"],
        example={"command": "python -c \"import json; a=json.load(open('artifacts.json')); print(len(a))\"", "input": "the slice", "output": "artifact count"},
        environment={"runner": "native"},
        runtime={"python_major": 3, "native_deps": [], "host_class": "any"},
        upstream_docs=["hf GPaolo/TerraLingua README (Total size ~4.7 GB, 40 experiments)"],
        human_capability_summary={"built_to": "record one ecology run for post-hoc analysis", "pressure": "n/a (data)", "success_means": "n/a (data)"},
        known_human_problem_solved="n/a (data slice for TECHNE-108)",
        lineage_relations=[{"relation": "derived_from", "to": "terralingua-2026", "note": "produced by the code at or before the pinned commit; exact commit not stated by the dataset"}],
        acquisition_tags=["operator-directive-2026-09-17", "poet_alife", "TECHNE-108", "data-slice"]),
    record.skeleton("lenia-chan-2019",
        canonical_name="Lenia -- Biology of Artificial Life, reference implementation and lifeform catalogue (Bert Wang-Chak Chan, 2018-)",
        aliases=["Lenia", "Chakazul/Lenia", "animals.json"],
        lineage="continuous cellular automaton generalising Conway's Life (Chan 2019, Complex Systems 28(3)); the substrate ASAL (asal-sakana-2024) searches and the source of the Orbium pattern used in TECHNE-107",
        domain=["artificial-life", "cellular-automata", "continuous-dynamics", "self-organization"], era="2018-2024",
        version="Chakazul/Lenia master @ adfc542939266de7f4bb7ebb552e8499701ee107 (last push 2024-07-19)",
        source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/Chakazul/Lenia", "commit": "adfc542939266de7f4bb7ebb552e8499701ee107"}]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/Chakazul/Lenia"},
        license={"spdx": "MIT", "status": "permissive", "evidence": "LICENSE.md in repo (GitHub API: MIT)"},
        language=["Python", "JavaScript", "Matlab", "R"], build_system="none", compiler_or_interpreter="CPython 3 (Python/LeniaND.py + numpy/scipy; optional reikna GPU)",
        dependencies=["numpy", "scipy", "PIL (Python reference)"],
        entry_points=["Python/LeniaND.py (Automaton: kernel_shell, calc_kernel, growth_func; Board.rle2arr)", "Python/animals.json (548+ catalogued lifeforms with params and RLE cells; Orbium = code O2u)"],
        example={"command": "python Python/LeniaND.py", "input": "a lifeform from animals.json", "output": "the running automaton (GUI); TECHNE-107 uses a headless numpy port"},
        environment={"runner": "native"},
        runtime={"python_major": 3, "native_deps": ["numpy", "scipy"], "host_class": "any Python 3 host; runs on M3"},
        upstream_docs=["arXiv:1812.05433 / Complex Systems 28(3) 2019 DOI 10.25088/ComplexSystems.28.3.251", "README.md"],
        human_capability_summary={"built_to": "explore self-organising, self-propelling patterns in a continuous CA and catalogue them", "pressure": "Life-like CAs are discrete and brittle; a continuous generalisation admits smooth, lifelike dynamics", "success_means": "stable, moving, catalogued lifeforms (the animals.json zoo)"},
        known_human_problem_solved="a continuous cellular automaton with a reproducible lifeform catalogue",
        behavioral_entry_point="load O2u (Orbium) from animals.json, step 256 times, measure mass and displacement (the TECHNE-107 LENIA arm)",
        acquisition_tags=["operator-directive-2026-09-18", "poet_alife", "TECHNE-107", "Harmonia #429 (fixture pinned from the packet, not Temp)"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite an EXISTING record (destroys acquire()'s pins; never the default)")
    a = ap.parse_args()
    from techne.fossils import vault
    for rec in S:
        probs = record.validate(rec)
        exists = (vault.specimen_dir(rec["specimen_id"]) / "record.json").exists()
        print("%-34s %s%s" % (rec["specimen_id"], "OK" if not probs else "; ".join(probs), "  [EXISTS: not rewritten]" if exists and not a.force else ""))
        if a.write and not probs and (not exists or a.force):
            print("   wrote", record.save(rec))


if __name__ == "__main__":
    main()
