"""Batch 16 -- prior-art raid, section II (open-ended environment design / auto-curricula), unit 1
(operator directive 7, 2026-09-21; TECHNE-122). Fossilizes facebookresearch/dcd: the reference
implementation of PLR, Robust PLR, ACCEL, PAIRED, REPAIRED and minimax adversarial training that
directive 7 s.II names, and the body Atlas's UED-2 / UED-4 records need
(roles/Atlas/prompts/2026-09-21_to_techne/TO_TECHNE.md). FIND + PIN + licence read were done on
2026-09-30 from a read-only clone at the pin; `python -m techne.fossils.harvest acquire <id>` fetches,
hashes and pins the body.

Facts recorded here were READ at the pin on 2026-09-30, not recalled:
  * upstream is ARCHIVED (GitHub API archived=true, pushed_at 2024-08-20T19:05:37Z);
  * the LICENSE file is CC BY-NC 4.0 while the README badge says CC BY-SA 4.0 (the file governs the
    record; the conflict is stated, not resolved);
  * the README's setup clones openai/baselines with no pin (an unpinned fetch in the recipe).

Usage: python -m techne.fossils.batches.batch16_prior_art_raid_ued [--write]
"""
from __future__ import annotations

import argparse

from techne.fossils import record

S = [
    record.skeleton("dcd-facebookresearch-2022",
        canonical_name="DCD -- Dual Curriculum Design: reference implementation of PLR, Robust PLR, ACCEL, PAIRED, REPAIRED and minimax (Jiang, Dennis, Parker-Holder, Foerster, Grefenstette, Rocktaschel et al.; Meta AI / FAIR, 2021-2023)",
        aliases=["dcd", "Dual Curriculum Design", "facebookresearch/dcd", "ACCEL reference implementation", "Robust PLR reference implementation"],
        lineage="PLR (Jiang et al. 2020, arXiv:2010.03934) and PAIRED (Dennis et al. 2020, arXiv:2012.02096) -> Replay-Guided Adversarial Environment Design (Jiang et al., NeurIPS 2021, arXiv:2110.02439: Robust PLR, REPAIRED, the DCD framing) -> ACCEL (Parker-Holder et al., ICML 2022) -> PAIRED + HiEnt/BC/Evo (Mediratta et al., CoLLAs 2023, arXiv:2308.10797); all in one codebase on branch main",
        domain=["unsupervised-environment-design", "curriculum", "open-ended-learning", "reinforcement-learning", "level-replay", "adversarial-environment-generation"], era="2021-2024",
        version="facebookresearch/dcd main @ cefd88196f2696860e42405d7b32f47d3d12bbde (committed 2024-08-20; 11 commits; upstream ARCHIVED per GitHub API on 2026-09-30)",
        source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/facebookresearch/dcd", "commit": "cefd88196f2696860e42405d7b32f47d3d12bbde"}]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/facebookresearch/dcd", "branch": "main", "other_branches_at_find": "collas-pairedbc @ 41c23101, collas-pairedevo @ 3b39a9ed (the latter merged into main by the pinned commit, PR #14)"},
        license={"spdx": "CC-BY-NC-4.0", "status": "read 2026-09-30; NON-COMMERCIAL; preservation and research permitted; NOT OSI; code may be read and studied, any adaptation that ships must stay non-commercial and attributed",
                 "evidence": "LICENSE at the pin begins 'Attribution-NonCommercial 4.0 International' (file sha256 ffe3b1e0b58c1f1250ce48f84d8c37328f9a1ff59bb77b63bc97480cf2778b64); Meta file headers point at that LICENSE file. CONFLICT RECORDED: the README badge at the same pin says 'License: CC BY-SA 4.0'; GitHub API reports spdx NOASSERTION. Vendored third-party files keep their own headers (Flowers Team teachDeepRL, Google Research, OpenAI, Kostrikov, Chevalier-Boisvert, Raffin); no separate licence files for them are present in the tree"},
        language=["Python"], build_system="none (conda python=3.8 + pip requirements.txt, per README)", compiler_or_interpreter="CPython 3.8 (README)",
        dependencies=["torch>=1.7.0", "torchvision==0.11.2", "tensorflow==2.4.1", "gym==0.15.7", "gym-minigrid==1.0.1", "Box2D", "networkx==2.5", "cma==2.7.0", "gin-config==0.1.1", "geopandas==0.9.0", "scikit-learn==1.1.1",
                      "openai/baselines installed from a git clone with NO pin (README)", "pyglet==1.5.11", "pyvirtualdisplay"],
        entry_points=["train.py (builds the env, agents and AdversarialRunner; one call to runner.run() per update)",
                      "envs/runners/adversarial_runner.py AdversarialRunner.run (the DCD loop: replay decision -> teacher/generator rollout -> student rollouts -> regret scores -> level-sampler update -> optional edit)",
                      "level_replay/level_sampler.py LevelSampler (sample_replay_decision, sample_replay_level, update_with_rollouts, the score functions _average_positive_value_loss / _average_gae / _one_step_td_error / ..., sample_weights = score transform mixed with a staleness term)",
                      "level_replay/level_store.py LevelStore (insert with parent_seeds, get_level, reconcile_seeds: the level archive that carries ACCEL's edit lineage)",
                      "envs/multigrid/adversarial.py and envs/bipedalwalker/adversarial.py (reset_to_level, reset_random, step_adversary, mutate_level: the adversarial-environment interface)",
                      "eval.py Evaluator (zero-shot benchmarks: maze, f1, bipedal, poetrose)",
                      "train_scripts/make_cmd.py + train_scripts/grid_configs/*.json (the published hyperparameter settings per method and domain)"],
        example={"command": "python train_scripts/make_cmd.py --json minigrid/60_blocks_uniform/mg_60b_uni_accel_empty --num_trials 1   # prints the train.py command for ACCEL on mazes", "input": "a grid_configs JSON (method x domain)", "output": "<log_dir>/<xpid>/logs.csv, model.tar checkpoints, screenshots/update_<n>.png of generated levels"},
        environment={"runner": "docker", "image": "NOT BUILT: needs a python 3.8 world with torch, tensorflow 2.4.1, gym 0.15.7, Box2D (SWIG + C++) and an unpinned openai/baselines; named, not reconstructed"},
        runtime={"python_major": 3, "native_deps": ["torch", "tensorflow 2.4.1 (prebuilt wheels need AVX)", "Box2D (C++ via SWIG)", "a virtual display for pyglet rendering"], "host_class": "Linux compiler+docker host with AVX (M2 / ubu nodes); NOT M3"},
        upstream_docs=["arXiv:2110.02439 (Replay-Guided Adversarial Environment Design, NeurIPS 2021)", "accelagent.github.io (Evolving Curricula with Regret-Based Environment Design, ICML 2022)", "arXiv:2010.03934 (Prioritized Level Replay)", "arXiv:2012.02096 (PAIRED)",
                       "arXiv:2308.10797 (Stabilizing Unsupervised Environment Design with a Learned Adversary, CoLLAs 2023)", "arXiv:1910.07224 (ALP-GMM, vendored under teachDeepRL/)", "README.MD (incl. the 'Integrating a new environment' checklist)", "docs/bibtex/{dcd,accel,collas}.bib"],
        human_capability_summary={"built_to": "train a student agent on a curriculum of environment instances chosen or generated to maximise its regret, so that it transfers zero-shot to unseen, harder instances",
                                  "pressure": "domain randomization wastes experience on uninformative levels; a learned adversary (PAIRED) is unstable; a curriculum needs a selection signal that does not require hand-written difficulty",
                                  "success_means": "higher zero-shot return on held-out benchmark environments (human-designed mazes, CarRacing-F1 tracks, BipedalWalker challenges, the POET 'rose' settings) than DR, minimax and PAIRED at matched student gradient updates"},
        known_human_problem_solved="regret-prioritized curation and evolution of training environments without a hand-designed curriculum",
        human_environmental_pressure="RL generalisation research where the training-level distribution, not the learner, limits robustness",
        human_failure_condition="the replay buffer collapses onto unsolvable or trivial levels; the regret estimate stops tracking real learnability; the adversary stops producing solvable levels",
        behavioral_entry_point="AdversarialRunner.run() with the four README switches (ued_algo, use_plr, no_exploratory_grad_updates, ued_editor): the SAME loop becomes DR, PLR, Robust PLR, ACCEL, PAIRED, REPAIRED or minimax, so each mechanism is an ablation of the others; LevelSampler.sample_replay_decision and the score function are the admission and priority rules",
        lineage_relations=[{"relation": "inspired_by", "to": "poet-original-2019", "note": "README at the pin: benchmark `poetrose` = environments based on the most challenging level settings discovered by POET (Wang et al. 2019, Fig. 5); config bipedal/bipedal_accel_poet.json = ACCEL in the POET design space. A benchmark and design-space link stated by upstream; no code ancestry is claimed"}],
        acquisition_tags=["operator-directive-2026-09-21", "prior_art_raid", "section-II-auto-curricula", "TECHNE-122", "Atlas UED-2/UED-4", "upstream-archived"]),
]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    from techne.fossils import vault
    for rec in S:
        probs = record.validate(rec)
        exists = (vault.specimen_dir(rec["specimen_id"]) / "record.json").exists()
        print("%-28s %s%s" % (rec["specimen_id"], "OK" if not probs else "; ".join(probs), "  [EXISTS: not rewritten]" if exists and not a.force else ""))
        if a.write and not probs and (not exists or a.force):
            print("   wrote", record.save(rec))


if __name__ == "__main__":
    main()
