"""Batch 17 -- prior-art raid, sections II-V and VII (operator, chat, 2026-09-30: "find some stuff to
download for the program for Nyx to chop up"; scope = the donors directive 7 names in sections II
(auto-curricula), III (quality diversity), IV (digital life), V (evolving programs / agents) and VII
(automated science) that have a public repository and a readable licence).

FIND + PIN: git ls-remote on 2026-09-30 (pins below are the default-branch HEADs at that moment);
licence, size and archive state from the GitHub API and the raw licence file; MABE2 located through
the GitHub search API (mercere99/MABE2), Aevol at its canonical Inria GitLab.

RECORD FACTS: ten read-only reader agents cloned each repository at its pin into a scratch directory
and wrote a facts file per repository, quoting the tree (licence line, README, manifests, class lists
of the core files). Those files are committed VERBATIM beside this batch at
techne/acquisition/prior_art_raid/READER_DRAFTS_2026-09-30/<draft_id>.json and every record here is
built from its draft plus the small OVERRIDES table below (final specimen_id, source_type, domain,
era, lineage edges, tags). A reader's "NOT_FOUND_AT_PIN" stays visible in the record. Nothing was
executed from any repository; every run_classification is NOT_ATTEMPTED.

DEFERRED, with the reason (not records; listed so the gap is visible):
  mmore500/dishtiny            MIT, but 2.5 GB per the GitHub API -- too large for this vault pass
  adaptive-intelligent-robotics/AURORA   archived, NO licence file or field -> all rights reserved
  erwanplantec/FlowLenia       NO licence file or field -> all rights reserved
  jbrant/MinimalCriterionCoevolution     NO licence (GitHub search hit; the only MCC code found)
  SakanaAI/AI-Scientist (v1)   116 MB under the same custom licence as v2; v2 taken first
  DRED, ATEP, AdA, XLand (DeepMind), SIMA 2, Genie 3   no public source found / research previews

Usage: python -m techne.fossils.batches.batch17_prior_art_raid_ii_v [--write]
"""
from __future__ import annotations

import argparse
import json
import pathlib

from techne.fossils import record, vault

DRAFTS = vault.REPO / "techne" / "acquisition" / "prior_art_raid" / "READER_DRAFTS_2026-09-30"
TAG_OP = "operator-chat-2026-09-30-download-for-nyx"

PERMISSIVE = {"MIT", "BSD-3-Clause", "Apache-2.0"}
COPYLEFT = {"GPL-3.0-only", "GPL-2.0-only", "GPL-3.0-or-later", "CECILL-2.1"}

# draft_id -> (specimen_id, section, source_type, domain, era, lineage_relations, extra_tags, submodules_required)
OVERRIDES = {
    "jaxued": ("jaxued-dramacow-2024", "II", "ORIGINAL_AUTHORITATIVE_RELEASE",
               ["unsupervised-environment-design", "curriculum", "reinforcement-learning", "jax"], "2024-2025",
               [{"relation": "reimplementation_of", "to": "dcd-facebookresearch-2022", "note": "reader draft: two files credit facebookresearch/minimax as source, which itself reimplements dcd; JaxUED implements the same UED methods (DR, PLR, Robust PLR, ACCEL, PAIRED) as single-file JAX programs"}],
               [], False),
    "minimax": ("minimax-facebookresearch-2023", "II", "ORIGINAL_AUTHORITATIVE_RELEASE",
                ["unsupervised-environment-design", "curriculum", "reinforcement-learning", "jax"], "2023-2024",
                [{"relation": "reimplementation_of", "to": "dcd-facebookresearch-2022", "note": "reader draft: Meta's JAX reimplementation of the facebookresearch/dcd UED baselines, adding Parallel PLR/ACCEL"}],
                [], False),
    "xland-minigrid": ("xland-minigrid-corl-2023", "II", "ORIGINAL_AUTHORITATIVE_RELEASE",
                       ["meta-reinforcement-learning", "procedural-environments", "gridworld", "jax"], "2023-2025", [], [], False),
    "omni-epic": ("omni-epic-faldor-zhang-2024", "II", "ORIGINAL_AUTHORITATIVE_RELEASE",
                  ["open-ended-learning", "llm-task-generation", "environment-generation", "curriculum"], "2024",
                  [], ["fifth-engine-candidate"], False),
    "qdax": ("qdax-airl-2022", "III", "ORIGINAL_AUTHORITATIVE_RELEASE",
             ["quality-diversity", "map-elites", "evolutionary-computation", "jax"], "2022-2025", [], [], False),
    "pyribs": ("pyribs-icaros-2020", "III", "ORIGINAL_AUTHORITATIVE_RELEASE",
               ["quality-diversity", "map-elites", "cma-me", "evolutionary-computation"], "2020-2026", [], [], False),
    "sferes2": ("sferes2-mouret-2014", "III", "ORIGINAL_AUTHORITATIVE_RELEASE",
                ["evolutionary-computation", "multiobjective", "cpp-framework"], "2014-2021", [], [], False),
    "map-elites-sferes2": ("map-elites-sferes2-2015", "III", "ORIGINAL_AUTHORITATIVE_RELEASE",
                           ["quality-diversity", "map-elites", "evolutionary-computation"], "2015-2017",
                           [{"relation": "algorithm_from", "to": "Mouret & Clune 2015 (arXiv:1504.04909)", "note": "the MAP-Elites paper; this module is the authors' own sferes2 implementation"},
                            {"relation": "derived_from", "to": "sferes2-mouret-2014", "note": "a sferes2 module: builds only inside sferes2/modules/map_elites via waf use=sferes2 (reader draft)"}],
                           [], False),
    "leniabreeder": ("leniabreeder-faldor-2024", "IV", "ORIGINAL_AUTHORITATIVE_RELEASE",
                     ["artificial-life", "quality-diversity", "lenia", "open-endedness", "jax"], "2024-2025",
                     [{"relation": "inspired_by", "to": "lenia-chan-2019", "note": "Lenia is the substrate searched (reader draft: JAX Lenia genotypes); the reference Lenia implementation is a separate specimen"},
                      {"relation": "derived_from", "to": "qdax-airl-2022", "note": "reader draft: a vendored qdax 0.3.0 provides MAP-Elites and AURORA machinery"}],
                     [], False),
    "stringmol": ("stringmol-york-2014", "IV", "ORIGINAL_AUTHORITATIVE_RELEASE",
                  ["artificial-chemistry", "artificial-life", "self-replication", "string-rewriting"], "2010-2025", [], [], False),
    "mabe2": ("mabe2-ofria-2019", "IV", "ORIGINAL_AUTHORITATIVE_RELEASE",
              ["evolutionary-computation", "artificial-life", "agent-based", "cpp-framework"], "2019-2026", [], [], True),
    "aevol": ("aevol-inria-2010", "IV", "ORIGINAL_AUTHORITATIVE_RELEASE",
              ["digital-evolution", "artificial-life", "genome-evolution", "cpp"], "2010-2026", [], [], False),
    "neat-python": ("neat-python-codereclaimers-2008", "V", "ORIGINAL_AUTHORITATIVE_RELEASE",
                    ["neuroevolution", "neat", "evolutionary-computation"], "2008-2026",
                    [{"relation": "algorithm_from", "to": "Stanley & Miikkulainen 2002 NEAT", "note": "a Python implementation of NEAT; the record's own README/CITATION is the source for the attribution"}],
                    [], False),
    "funsearch": ("funsearch-deepmind-2023", "V", "ORIGINAL_AUTHORITATIVE_RELEASE",
                  ["llm-guided-search", "program-synthesis", "evolutionary-computation", "mathematics"], "2022-2024",
                  [], ["partial-release"], False),
    "openevolve": ("openevolve-codelion-2025", "V", "ORIGINAL_AUTHORITATIVE_RELEASE",
                   ["llm-guided-search", "program-synthesis", "map-elites", "evolutionary-coding"], "2025-2026",
                   [{"relation": "inspired_by", "to": "AlphaEvolve (DeepMind 2025, no public source)", "note": "pyproject: an open-source implementation of AlphaEvolve (reader draft)"}],
                   [], False),
    "dgm": ("dgm-zhang-hu-2025", "V", "ORIGINAL_AUTHORITATIVE_RELEASE",
            ["self-improving-agents", "open-ended-learning", "llm-agents", "archive-search"], "2025", [], [], False),
    "evolutionary-model-merge": ("evolutionary-model-merge-sakana-2024", "VIII", "ORIGINAL_AUTHORITATIVE_RELEASE",
                                 ["model-merging", "evolutionary-computation", "foundation-models", "evaluation-harness"], "2024",
                                 [], ["evaluation-only-no-search-code"], False),
    "cycleqd": ("cycleqd-sakana-2024", "VIII", "ORIGINAL_AUTHORITATIVE_RELEASE",
                ["quality-diversity", "model-merging", "foundation-models", "map-elites"], "2024-2025", [], [], False),
    "natural-niches-m2n2": ("natural-niches-m2n2-sakana-2025", "VIII", "ORIGINAL_AUTHORITATIVE_RELEASE",
                            ["model-merging", "evolutionary-computation", "niching", "foundation-models"], "2024-2025", [], [], False),
    "ai-scientist-v2": ("ai-scientist-v2-sakana-2025", "VII", "ORIGINAL_AUTHORITATIVE_RELEASE",
                        ["automated-science", "llm-agents", "tree-search", "experiment-management"], "2025",
                        [], ["use-restricted-licence"], False),
}


def _license(d: dict) -> dict:
    lic = d["license"]
    guess = str(lic.get("spdx_guess", ""))
    head = guess.split(" ")[0]
    if head in PERMISSIVE:
        status = "permissive"
    elif head in COPYLEFT or "GPL" in guess or "CECILL" in guess:
        status = "copyleft; preservation and research permitted; derivative distribution inherits the licence"
    elif guess.startswith("custom"):
        status = "read 2026-09-30; custom use-restricted licence (RAIL-derived); preservation and study permitted; use restrictions flow down; NOT OSI"
    else:
        status = "UNRESOLVED (see evidence)"
    ev = "licence file %s, first line %r; metadata field: %s; %s" % (lic.get("file"), lic.get("first_line"), lic.get("metadata_license_field"), lic.get("notes"))
    return {"spdx": guess, "status": status, "evidence": ev.strip()}


def build(draft_id: str) -> dict:
    d = json.loads((DRAFTS / (draft_id + ".json")).read_text(encoding="utf-8"))
    sid, section, stype, domain, era, rels, tags, subs = OVERRIDES[draft_id]
    art = {"kind": "git", "url": d["url"], "commit": d["commit"]}
    if subs:
        art["submodules"] = "required"
    langs = d.get("language") or ["NOT_FOUND_AT_PIN"]
    py = 3 if any(str(l).lower().startswith("python") for l in langs) else None
    deps = list(d.get("dependencies") or [])
    for n in d.get("network_fetches_in_setup") or []:
        deps.append("SETUP FETCH: " + str(n))
    version = "%s %s @ %s (committed %s; %s commits since %s; %s tracked files)" % (
        d["url"].replace("https://", ""), d.get("default_branch"), d["commit"], str(d.get("commit_date", ""))[:10],
        d.get("n_commits"), str(d.get("first_commit_date", ""))[:10], d.get("n_tracked_files"))
    rec = record.skeleton(sid,
        canonical_name=d["canonical_name"],
        aliases=list(d.get("aliases") or []),
        lineage="%s || main loop (reader, from the code): %s" % (d.get("lineage_notes", ""), d.get("main_loop_one_sentence", "")),
        domain=domain, era=era, version=version,
        source_origin={"artifacts": [art]},
        source_type=stype,
        source_identity={"repo": d["url"].replace("https://", ""), "branch": d.get("default_branch"),
                         "other_branches_or_versions": d.get("other_branches_or_versions", "")},
        license=_license(d),
        language=langs, build_system=d.get("build_system", ""), compiler_or_interpreter=d.get("interpreter_or_compiler", ""),
        dependencies=deps,
        entry_points=list(d.get("entry_points") or []),
        example={"command": d.get("example_command", ""), "input": d.get("example_input", ""), "output": d.get("example_output", "")},
        environment={"runner": "native", "note": "NOT RUN in this pass (nothing executed from the tree); host class from the reader draft: %s" % d.get("host_class", "")},
        runtime={"python_major": py, "native_deps": list(d.get("runtime_native_deps") or []), "host_class": d.get("host_class", "")},
        upstream_docs=list(d.get("upstream_docs") or []),
        human_capability_summary={"built_to": d.get("built_to") or "NOT_FOUND_AT_PIN", "pressure": d.get("pressure") or "NOT_FOUND_AT_PIN",
                                  "success_means": d.get("success_means") or "NOT_FOUND_AT_PIN"},
        known_human_problem_solved=d.get("built_to", ""),
        behavioral_entry_point=d.get("behavioral_entry_point", ""),
        lineage_relations=rels,
        acquisition_tags=[TAG_OP, "prior_art_raid", "section-" + section, "TECHNE-132",
                          "reader-draft:READER_DRAFTS_2026-09-30/%s.json" % draft_id] + tags,
        reader_notes={"draft": "techne/acquisition/prior_art_raid/READER_DRAFTS_2026-09-30/%s.json" % draft_id,
                      "copyright_holders_by_header_count": d.get("copyright_holders_by_header_count", {}),
                      "things_the_reader_could_not_verify": d.get("things_i_could_not_verify", []),
                      "has_gitmodules_at_pin": d.get("has_gitmodules"), "has_lfs_at_pin": d.get("has_lfs"),
                      "approx_tree_bytes_at_pin": d.get("approx_tree_bytes")})
    return rec


S = [build(k) for k in OVERRIDES]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--write", action="store_true"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    for rec in S:
        probs = record.validate(rec)
        exists = (vault.specimen_dir(rec["specimen_id"]) / "record.json").exists()
        print("%-40s %s%s" % (rec["specimen_id"], "OK" if not probs else "; ".join(probs), "  [EXISTS: not rewritten]" if exists and not a.force else ""))
        if a.write and not probs and (not exists or a.force):
            print("   wrote", record.save(rec))


if __name__ == "__main__":
    main()
