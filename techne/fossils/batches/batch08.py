"""Batch 08 of the fossil harvest (2026-09-13): THE EDGES -- beyond the CS canon.

Round 08 of the autonomous loop digs where the coverage map is thinnest and least like the rest of
the vault: historical worlds and unusual computational cultures. This round:
  - eliza-anthay-1966: the 1966 conversational program (pattern-matching, script-driven dialogue) --
    a pre-1970 historical world and a computational culture (early AI / NLP) absent from the vault,
    entered via Anthony Hay's faithful reconstruction from Weizenbaum's CACM paper + recovered script.
  - avida (UNLOCK, no new record here): the flagship digital-evolution fossil, made runnable.
Every disposition label is the human record's, cited. Techne acquires + proves-it-runs; it does not
decide what the machinery means.
"""
from __future__ import annotations

from .. import record

S = []


def spec(sid, **kw):
    S.append(record.skeleton(sid, **kw))


# ============================ NEW EDGE: conversational AI / NLP (1966) ========================
spec("eliza-anthay-1966",
    canonical_name="ELIZA (1966) -- Weizenbaum's script-driven conversational program (DOCTOR script), Anthony Hay's faithful C++ reconstruction",
    aliases=["ELIZA", "DOCTOR", "Weizenbaum ELIZA"],
    lineage="ELIZA (Joseph Weizenbaum, MIT, 1966, CACM 9(1)): the first widely known natural-language conversation program. Not learning, not parsing -- a SCRIPT of decomposition/reassembly rules matched against keywords with a ranked agenda and memory. The DOCTOR script imitates a Rogerian therapist. A distinct execution model absent from the vault: keyword-triggered pattern transformation over text, no model of meaning. This body is Anthony Hay's C++ reconstruction built from the 1966 CACM paper and the recovered original script, reproducing the paper's canonical conversation exactly.",
    domain=["conversational-ai", "natural-language", "pattern-matching", "symbolic", "early-ai", "human-computer-interaction"],
    era="1966 (Weizenbaum ELIZA); this reconstruction 2021-",
    version="github.com/anthay/ELIZA master as of 2026-09-13 (commit in hashes)",
    source_origin={"artifacts": [{"kind": "git", "url": "https://github.com/anthay/ELIZA", "commit": "HEAD"}]},
    source_type="FAITHFUL_PORT", source_identity={"repo": "github.com/anthay/ELIZA (Anthony Hay)", "reconstructs": "Weizenbaum 1966 ELIZA + DOCTOR script"},
    license={"spdx": "Unlicense-or-similar", "status": "public-domain-intent", "evidence": "repo LICENSE/README (Anthony Hay dedicates it to the public domain)"},
    language=["C++"], build_system="single-file g++ (C++11)", compiler_or_interpreter="g++ (docker prometheus-fossil-lang:bookworm)",
    dependencies=["a C++11 compiler"],
    entry_points=["eliza -- reads a line, applies the DOCTOR script, prints ELIZA's reply; a built-in mode reproduces the 1966 CACM conversation"],
    example={"command": "printf 'Men are all alike.\\n' | ./eliza", "input": "the opening line of Weizenbaum's 1966 paper conversation", "output": "the script's canonical reply 'IN WHAT WAY' (the ORACLE: the exact dialogue printed in CACM 1966)"},
    environment={"runner": "docker", "image": "prometheus-fossil-lang:bookworm"},
    upstream_docs=["Weizenbaum, ELIZA -- A Computer Program For the Study of Natural Language Communication Between Man And Machine, CACM 9(1) 1966", "anthay/ELIZA README (reconstruction notes)"],
    human_capability_summary={"built_to": "hold a text conversation by transforming the user's own words back at them via scripted keyword rules -- to study man-machine communication and, unintentionally, how readily people attribute understanding",
                              "pressure": "no model of meaning; the illusion must be produced entirely by decomposition/reassembly rules, keyword ranking, and a memory of recent topics",
                              "success_means": "the scripted transformation reproduces the documented 1966 conversation; the program sustains a plausible exchange with no understanding"},
    known_human_problem_solved="scripted natural-language dialogue (the origin of the chatbot)",
    human_environmental_pressure="producing believable dialogue with pure surface pattern transformation, no semantics",
    human_failure_condition="an input with no matching keyword falls through to a canned deflection ('PLEASE GO ON'); the illusion breaks when the script's rules do not cover the turn",
    behavioral_entry_point="feed inputs that hit vs miss the DOCTOR keywords and watch reflection vs the memory/none-keyword fallbacks; swap the script to change the 'personality' with no code change",
    acquisition_tags=["batch08", "edge", "historical_world", "pre_1970_program", "computational_culture", "early_ai", "outside_queue"],
    lineage_relations=[{"relation": "algorithm_from", "to": "Weizenbaum 1966 (keyword decomposition/reassembly)", "note": "first conversational-AI fossil; a pre-1970 program recovered via a faithful reconstruction, not the original MAD-SLIP binary (which runs only under CTSS emulation)"},
                       {"relation": "shares_ancestor_with", "to": "gnu-apl-2.0", "note": "both are interpreters of a small formal notation, but ELIZA transforms text by rules and APL evaluates array expressions -- Techne records the shared machinery domain, not equivalence"}])


def main():
    from .. import record as R
    for rec in S:
        try:
            old = R.load(rec["specimen_id"])
            for k in ("run_classification", "test_classification", "receipts", "hashes", "acquisition_date",
                      "observability", "nyx_handoff"):
                if old.get(k):
                    rec[k] = old[k]
            R.merge_artifact_pins(rec, old)   # batch 10 P1: never lose an established pin
        except FileNotFoundError:
            pass
        probs = R.validate(rec)
        R.save(rec)
        print("%-34s %s" % (rec["specimen_id"], "ok" if not probs else probs))
    print(len(S), "records")


if __name__ == "__main__":
    main()
