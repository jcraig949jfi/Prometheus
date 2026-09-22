"""Batch 15 -- prior-art raid, First Return (operator directive 7, 2026-09-21). Fossilizes the one donor
with a canonical, public, permissively-licensed, fully-inspected source at this stage: Voyager. The
other First Return subjects (SIMA 2, Genie 3) have NO public source (research previews only, verified
by fetching DeepMind's own blog posts, 2026-09-21) so there is no body to acquire; their PAPER_ONLY /
BLOCKED status is recorded in the raid ledger, not as a fossil record. Open substitutes named in the
First Return (open-oasis, MineWorld) are pinned in the ledger for a later batch once a consumer names one.

Usage: python -m techne.fossils.batches.batch15_prior_art_raid [--write]
"""
from __future__ import annotations

import argparse

from techne.fossils import record

S = [
    record.skeleton("voyager-minedojo-2023",
        canonical_name="Voyager -- An Open-Ended Embodied Agent with Large Language Models (Wang, Xie, Jiang, Mandlekar, Xiao, Zhu, Fan, Anandkumar; NVIDIA/Caltech/UT Austin/Stanford/UCLA, 2023)",
        aliases=["Voyager", "MineDojo/Voyager"],
        lineage="MineDojo (2022, the same lab's Minecraft simulation suite) -> Voyager (2023): the first LLM-driven lifelong-learning agent with a persistent, growing, retrievable skill library",
        domain=["embodied-agents", "llm-agents", "open-ended-learning", "skill-libraries", "automatic-curriculum", "lifelong-learning"], era="2023-",
        version="MineDojo/Voyager main @ 55e45a880755d0c8c66ca7fb5fe7962ac8974f89 (last push 2024-04-03)",
        source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/MineDojo/Voyager", "commit": "55e45a880755d0c8c66ca7fb5fe7962ac8974f89"}]},
        source_type="ORIGINAL_AUTHORITATIVE_RELEASE", source_identity={"repo": "github.com/MineDojo/Voyager", "project_site": "voyager.minedojo.org"},
        license={"spdx": "MIT", "status": "permissive", "evidence": "GitHub API license field + LICENSE in repo"},
        language=["Python", "JavaScript"], build_system="pip (requirements.txt) + npm (voyager/env/mineflayer/package.json)", compiler_or_interpreter="CPython 3 + Node.js (mineflayer bridge)",
        dependencies=["langchain (ChatOpenAI, OpenAIEmbeddings, Chroma vectorstore)", "chromadb==0.3.29", "openai (GPT-4/GPT-3.5 API, paid)", "gymnasium", "minecraft_launcher_lib",
                     "Node.js mineflayer 4.8.1 + mineflayer-pathfinder/pvp/tool/collectblock, prismarine-*, @babel/core (JS AST parsing for skill code)", "a licensed Minecraft Java Edition client"],
        entry_points=["voyager/voyager.py Voyager.learn() (the main open-ended loop)", "voyager/agents/curriculum.py CurriculumAgent.propose_next_task", "voyager/agents/action.py ActionAgent.process_ai_message",
                     "voyager/agents/critic.py CriticAgent.check_task_success", "voyager/agents/skill.py SkillManager.add_new_skill / retrieve_skills", "voyager/control_primitives/*.js (fixed primitive tool library)"],
        example={"command": "python -c \"from voyager import Voyager; v = Voyager(mc_port=..., openai_api_key=...); v.learn()\"", "input": "a running Minecraft server + OpenAI API key (both require spending; not exercised here)", "output": "ckpt/skill/{code,description,vectordb}/ -- the growing skill library"},
        environment={"runner": "native", "note": "needs a licensed Minecraft client + a paid OpenAI API key; not runnable on M3 without spending (standing rule: no spending without authorization). Source-level autopsy performed instead (voyager.py, agents/{skill,curriculum,action,critic}.py fetched and read in full at the pinned commit)."},
        runtime={"python_major": 3, "native_deps": ["Node.js runtime", "a Minecraft Java Edition installation"], "host_class": "any host with Node.js + Python + a Minecraft licence + OpenAI credits"},
        upstream_docs=["arXiv:2305.16291 (v1 2023-05-25, v2 2023-10-19)", "voyager.minedojo.org", "README.md"],
        human_capability_summary={"built_to": "explore Minecraft indefinitely, inventing its own tasks, writing and reusing JavaScript programs as skills, without human task specification", "pressure": "single-task RL agents in Minecraft plateau; hand-designed curricula do not scale to open-ended exploration",
                                  "success_means": "3.3x more unique items, 2.3x longer distances travelled, unlocking the tech tree up to 15.3x faster than the prior SOTA (paper's own comparison)"},
        known_human_problem_solved="lifelong open-ended skill acquisition in a fixed but unbounded world, using an LLM as both curriculum proposer and code generator",
        behavioral_entry_point="Voyager.learn(): propose_next_task -> rollout (iterative code-gen/execute/critique up to action_agent_task_max_retries) -> on success, SkillManager.add_new_skill -> next proposal conditioned on updated completed/failed task lists",
        acquisition_tags=["operator-directive-2026-09-21", "prior_art_raid", "voyager", "fifth-engine-candidate"]),
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
