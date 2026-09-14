"""Question-to-instrument forensic map (court charter 2026-09-14, ONE ADDITIONAL HARVEST).

LAYER: NECROPOLIS VALIDATION.  The 13 charter questions (plus the gaps found while
mapping) are keyed to registry rows.  The Keeper's judgement is WHICH rows bear on
WHICH question and how (DIRECT / PARTIAL); the registry decides whether a row may be
listed as an answerer at all: a tool_id whose admissibility.admissible is false is
moved to candidates_if_validated with its blocked_by, whatever the mapping says.
Empty and partial cells are the product ("Do not invent instruments to fill empty
cells").

    python engine/necropolis/workshop/build_forensic_map.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (tool_id, role, how it bears on the question).  role: DIRECT = the instrument's
# evidentiary_scope IS an answer to the question for the object class named;
# PARTIAL = it answers a necessary sub-question or a restricted object class.
Q = [
    {"id": "FQ-01", "scope": 'RESTRICTED: statistics, graders and gates as functions; not pipeline-level tautology', "question": "Was the test tautological?",
     "needs": "an instrument that can show a statistic, grader or gate cannot respond to its inputs (identity, constant, or same-computation)",
     "tools": [("NT-047", "DIRECT", "instrument-null probe: does the statistic respond to its inputs at all (tautological / nondeterministic / unmeasurable)"),
               ("NT-056", "DIRECT", "literal-verdict lint: functions whose every return is the same verdict cannot discriminate"),
               ("NT-040", "DIRECT", "instrument contract: a meter is certified only if it responds to a negative"),
               ("NT-041", "PARTIAL", "degenerate audit: B1 degeneracy of a measure (conflating vs refusing)"),
               ("NT-033", "PARTIAL", "EvCA C3 null check: were two 'independent' runs the same computation"),
               ("NT-073", "PARTIAL", "Pattern 30: is a correlation an algebraic identity of its inputs (sympy)"),
               ("NT-062", "PARTIAL", "descriptor-collapse audit: are archive axes secretly dependent")],
     "limits": "covers statistics, graders and gates as FUNCTIONS; a test that is tautological at the pipeline level (evaluation set identical to the construction set) is caught only if the artifacts are fingerprinted (see FQ-04)"},
    {"id": "FQ-02", "scope": 'PARTIAL: presence of a positive control and one pinned example; no planted-effect generator for an arbitrary claim class', "question": "Was the positive control capable of passing?",
     "needs": "an instrument that plants an effect of the class the claim asserts and shows the claimed instrument detects it at a rate not pinned at alpha",
     "tools": [("NT-034", "PARTIAL", "measurement guard: a passing, type-matched control had to exist before the value was read"),
               ("NT-049", "PARTIAL", "resampling null: its PERTURBATION control is the worked example of a positive control pinned at alpha (DISP-001)"),
               ("NT-047", "PARTIAL", "instrument-null probe: whether the statistic can respond at all (necessary, not sufficient)"),
               ("NT-015", "PARTIAL", "canon R11 calibration: declared-vs-reported completeness for forecasters only"),
               ("NT-065", "DIRECT", "Archaeon D1-D6 planted / no-effect control battery, per detector"),
               ("NT-014", "PARTIAL", "Archaeon D3 exact vs simulated false-alarm rate"),
               ("NT-069", "PARTIAL", "Archaeon stage-0 fragility survey with positive control")],
     "limits": "no admissible instrument PLANTS an effect of an arbitrary claim class; the admissible cells only verify that some positive control existed or that one specific control is pinned.  A planted-shift generator keyed by claim class is the missing organ (CR-001 descendant requirement)"},
    {"id": "FQ-03", "scope": 'RESTRICTED: statistics and classifiers; not LLM-graded claims', "question": "Was the negative control capable of failing?",
     "needs": "a null / constant / costume / chance-floor reference the claimed instrument must beat",
     "tools": [("NT-031", "DIRECT", "Nemesis cheatlib: chance floor and constant responder the tool must beat"),
               ("NT-028", "DIRECT", "baseline costume: does the claim only beat the marginal majority"),
               ("NT-045", "DIRECT", "control certifier + defect battery: every named defect shape must be caught"),
               ("NT-040", "DIRECT", "instrument contract: negative required for certification"),
               ("NT-013", "DIRECT", "modal-collapse synthetic: chance floor for that claim class"),
               ("NT-047", "DIRECT", "synthetic-null probe: independent samples must not read as signal"),
               ("NT-061", "PARTIAL", "Westfall-Young max-T null over binary splits")],
     "limits": "answerable for statistics and classifiers; for LLM-graded claims the constant/costume responder exists (NT-031) but the grader itself is UNTRUSTED (NT-001), so the negative control is only as good as the alternative judge (FQ-13)"},
    {"id": "FQ-04", "scope": 'RESTRICTED: graves that fingerprinted their producer (record-limited)', "question": "Did the producer change between claim and evaluation?",
     "needs": "fingerprints of code and inputs at claim time and at evaluation time, and a reader that compares them",
     "tools": [("NT-051", "DIRECT", "git-history census: when an instrument existed and what its bytes were at any commit"),
               ("NT-038", "DIRECT", "Vivarium spec hash: identity of an experiment spec, key-order invariant"),
               ("NT-007", "DIRECT", "comms.manifest: do the files beside a manifest still match it"),
               ("NT-053", "DIRECT", "manifest verify with coverage: uncovered files, self-hash"),
               ("NT-033", "DIRECT", "EvCA C3: transform digest identity of two runs"),
               ("NT-016", "PARTIAL", "H3 replay input-fingerprinting stream manifest (Archaeon only)"),
               ("NT-067", "PARTIAL", "H1/H0 spec_hash dedup: two 'independent' arms with one spec_hash refused"),
               ("NT-070", "PARTIAL", "Arachne frozen specimen loader with manifest verification"),
               ("NT-081", "PARTIAL", "Proteus specimen gate BYTES/SHAPE/MEANING")],
     "limits": "record-limited, not instrument-limited: the question is answerable only where the grave fingerprinted its producer; where it did not, the map says UNANSWERABLE_RECORD, never 'unchanged'"},
    {"id": "FQ-05", "scope": 'RESTRICTED: exact-equality leaks only', "question": "Did the judge have access to answer-bearing information?",
     "needs": "a leak detector over what the judge could read at grade time versus the answer",
     "tools": [("NT-030", "DIRECT", "ladder leakage audit: exact-equality leak fields with chance floor"),
               ("NT-021", "DIRECT", "Vivarium library-leak: a component equal to the task answer"),
               ("NT-031", "PARTIAL", "chance floor the judge's score must beat"),
               ("NT-035", "DIRECT", "Icarus tier oracle declares its own cheat fields"),
               ("NT-075", "DIRECT", "Ergon packet invariants + leak-gate fire tests")],
     "limits": "EXACT-equality leaks only.  Derived, paraphrased or partial leakage (an answer recoverable by a 3-line reader that is not byte-equal, memory 2026-08-12) has no admissible detector"},
    {"id": "FQ-06", "scope": 'RESTRICTED: graves with a declared class', "question": "Was the search weak or the domain empty?",
     "needs": "a B1 (degenerate domain) vs B2 (insufficient search) discriminator given a declared class",
     "tools": [("NT-002", "DIRECT", "coverage diagnostic: expressiveness ceiling (B2) vs degenerate domain (B1) for a declared class"),
               ("NT-041", "DIRECT", "degenerate audit: B1 degeneracy of a measure"),
               ("NT-029", "PARTIAL", "kill-scheme information audit: do kill labels carry coordinate information"),
               ("NT-059", "PARTIAL", "Erebos KillTensor coverage over four axes"),
               ("NT-078", "PARTIAL", "generator quality probe: generators that only ever produce one kill pattern"),
               ("NT-084", "DIRECT", "lattice void miner: exhaustive evaluation with certificate (product-measure decision)"),
               ("NT-080", "PARTIAL", "lane exhaustion rubric EXHAUSTION@v1")],
     "limits": "requires the grave to have DECLARED its class; a grave with no class declaration gets B1/B2 UNDECIDABLE, which is itself a finding"},
    {"id": "FQ-07", "scope": 'GENERAL', "question": "Was the gate vacuous?",
     "needs": "evidence the gate could and did refuse something",
     "tools": [("NT-056", "DIRECT", "literal-verdict lint: a gate that returns one verdict unconditionally"),
               ("NT-034", "DIRECT", "measurement guard: gate refuses when control absent or type-mismatched"),
               ("NT-019", "DIRECT", "Atalanta null_bound: bound had to be declared before emissions were counted"),
               ("NT-004", "PARTIAL", "Erebos residue gate replayed on ledger rows: did it ever refuse"),
               ("NT-050", "PARTIAL", "ledger census verdict cardinality: a gate column that never said NO"),
               ("NT-036", "PARTIAL", "dead-field detector: a gate column never populated"),
               ("NT-085", "PARTIAL", "Theseus content-aware promotion gate with F2 null"),
               ("NT-063", "PARTIAL", "battery-chain audit: ACCUMULATING vs DESTROYING checks")],
     "limits": "static vacuity (code shape) and ledger vacuity (never refused) are both covered; a gate that refused only cases it was never shown (selection upstream) is FQ-09"},
    {"id": "FQ-08", "scope": 'RESTRICTED: static consumption; runtime consumption only where logged', "question": "Was the consumer absent?",
     "needs": "who imported, read or acted on the instrument's output",
     "tools": [("NT-052", "DIRECT", "consumer trace: who imports / mentions a path (never piped through head)"),
               ("NT-032", "PARTIAL", "Pronoia productive-liveness: were artifacts consumed downstream (L-class)"),
               ("NT-050", "PARTIAL", "ledger census: whether a consumer's ledger ever carried the producer's ids"),
               ("NT-054", "PARTIAL", "read-only Postgres probe: did the canonical store ever receive the rows")],
     "limits": "static consumption is answerable; RUNTIME consumption (the output was read by a running process) is answerable only where the consumer logged it or wrote to the store"},
    {"id": "FQ-09", "scope": 'GENERAL', "question": "Was the claimed evidence actually pipeline state?",
     "needs": "a reader that grades artifacts rather than stdout, and detects heartbeats / status columns / dead fields masquerading as results",
     "tools": [("NT-032", "DIRECT", "productive-liveness L0-L5 from artifacts, not stdout"),
               ("NT-036", "DIRECT", "dead-field detector"),
               ("NT-050", "DIRECT", "ledger census: rows, dead / partial fields, verdict cardinality"),
               ("NT-044", "DIRECT", "Charon C1/C2: unfingerprinted pool and transport-failure residue rulings"),
               ("NT-042", "DIRECT", "Eos intake gate: the claim must name a real referent in the tree"),
               ("NT-043", "PARTIAL", "environment identity: the store read is the store claimed"),
               ("NT-089", "PARTIAL", "Alethelia anomaly rules: stale heartbeats, zombies, dormant inputs"),
               ("NT-074", "PARTIAL", "Vivarium orphan-verdict / scope-recurrence / degeneracy checks")],
     "limits": "answerable"},
    {"id": "FQ-10", "scope": 'RESTRICTED: degeneracy, costume and scale; not semantic mismatch', "question": "Was the comparator measuring the intended quantity?",
     "needs": "a reader of the claim's DECLARED quantity checked against what the comparator computes",
     "tools": [("NT-028", "DIRECT", "baseline costume: the comparator only beats the marginal majority"),
               ("NT-024", "DIRECT", "block-shuffle null: dependence beyond what the stratifier explains (the 'explained by scale' clause)"),
               ("NT-047", "PARTIAL", "instrument-null: comparator can respond"),
               ("NT-040", "PARTIAL", "instrument contract"),
               ("NT-041", "PARTIAL", "degenerate audit"),
               ("NT-039", "PARTIAL", "divergence decomposition: how much of a divergence is attributable below the ceiling"),
               ("NT-006", "PARTIAL", "two-sample KS: distribution difference (not location/scale-specific)"),
               ("NT-073", "PARTIAL", "Pattern 30 algebraic identity"),
               ("NT-062", "PARTIAL", "descriptor-collapse dependence")],
     "limits": "degeneracy, identity and costume are detectable; SEMANTIC mismatch (the code computes X, the claim says Y, both non-degenerate) has no instrument -- it needs a declared-quantity record and a reader of it"},
    {"id": "FQ-11", "scope": 'RESTRICTED: store identity and cwd; not package / interpreter environment', "question": "Did dependency / configuration state invalidate the test?",
     "needs": "the environment (packages, env vars, store identity, cwd convention) at claim time versus at evaluation time",
     "tools": [("NT-043", "DIRECT", "comms.identity: canonical store or a fork, fails closed"),
               ("NT-054", "DIRECT", "read-only Postgres probe with identity check"),
               ("NT-055", "PARTIAL", "sigma_kernel fresh-interpreter runner: historical cwd convention reproduced"),
               ("NT-051", "PARTIAL", "git-history census: which bytes were present"),
               ("NT-038", "PARTIAL", "spec hash identity"),
               ("NT-071", "PARTIAL", "Herakles workspace guard (canonical vs worktree)"),
               ("NT-064", "PARTIAL", "Techne fossil isolation battery"),
               ("NT-086", "PARTIAL", "evidence-wiki store identity guard"),
               ("NT-020", "PARTIAL", "Lean runtime session: is the REPL present")],
     "limits": "store identity and cwd are covered; PACKAGE / interpreter environment at claim time was almost never recorded (FRANKENSTEIN_XREF 'missing_here' is per-host), so this is mostly UNANSWERABLE_RECORD"},
    {"id": "FQ-12", "scope": 'RESTRICTED: graves with an admissible replay harness (Pollux, Archaeon, sigma_kernel, prometheus_math ledgers, Techne canon)', "question": "Can the historical result be reproduced from frozen artifacts?",
     "needs": "a replay harness for THAT grave's producer over its preserved inputs, with fingerprints",
     "tools": [("NT-048", "DIRECT", "Pollux statistic replay (unchanged daemon logic)"),
               ("NT-016", "DIRECT", "Archaeon H3 replay from preserved births"),
               ("NT-055", "DIRECT", "sigma_kernel modules re-run as historically run"),
               ("NT-027", "DIRECT", "Archaeon fossil inference: what two fossils jointly imply"),
               ("NT-005", "DIRECT", "reasoning_quality_emit: contested tasks re-derived from a preserved ledger"),
               ("NT-015", "DIRECT", "canon R11: declared vs reported"),
               ("NT-007", "PARTIAL", "manifest verification as a precondition"),
               ("NT-053", "PARTIAL", "manifest coverage as a precondition"),
               ("NT-046", "DIRECT", "Apollo E9 scorer: reproduce the published number"),
               ("NT-023", "DIRECT", "sigma_kernel A148 obstruction numbers"),
               ("NT-069", "DIRECT", "Archaeon pinned-blob replay"),
               ("NT-057", "DIRECT", "Techne acquisition checks re-run with ledger redirect"),
               ("NT-093", "DIRECT", "Noesis tensor completion (what it lacked is the finding)"),
               ("NT-091", "DIRECT", "Noesis sympy chain verifiers")],
     "limits": "PER-GRAVE column: admissible replay exists for Pollux, Archaeon H3, sigma_kernel, prometheus_math ledgers and Techne canon.  For every other grave in the 48-agent roster the cell is EMPTY -- there is no replay harness and, for daemons whose state/ was gitignored (FRANK-003), no bytes to replay"},
    {"id": "FQ-13", "scope": 'RESTRICTED: statistical and boolean claims; not LLM-judged claims', "question": "Can the claimed failure survive an alternative admissible instrument?",
     "needs": "a second, independently validated instrument for the same claim class",
     "tools": [("NT-006", "DIRECT", "two-sample KS"),
               ("NT-008", "DIRECT", "permutation null"),
               ("NT-025", "DIRECT", "bootstrap / matched-null / permutation with correct p floor"),
               ("NT-024", "DIRECT", "block-shuffle null"),
               ("NT-049", "DIRECT", "random-subset resampling null + KS (caveat: lower tail is uninformative, DISP-001)"),
               ("NT-037", "DIRECT", "BOCPD changepoint"),
               ("NT-012", "DIRECT", "truth-table oracle, the reference for NT-011"),
               ("NT-011", "DIRECT", "z3 oracle checked against NT-012: two oracles for boolean claims"),
               ("NT-026", "DIRECT", "kill-resurrection audit: would a killed claim survive re-evaluation"),
               ("NT-060", "PARTIAL", "percentile bootstrap CI"),
               ("NT-061", "PARTIAL", "Westfall-Young"),
               ("NT-066", "PARTIAL", "Archaeon C3 exact-symmetry null"),
               ("NT-068", "PARTIAL", "Archaeon H5 exact neighbourhood reference"),
               ("NT-076", "PARTIAL", "z3-backed verifier lens")],
     "limits": "answerable for statistical and boolean claims.  For LLM-JUDGED claims there is NO admissible alternative judge: NT-001 is UNTRUSTED, NT-082 needs an absent package, NT-083 needs a fine-tuned verifier; a failure graded by an LLM cannot currently be cross-examined"},
    # ---- questions the mapping surfaced that the charter list does not name
    {"id": "FQ-14", "scope": 'PARTIAL: denominator fragments only', "question": "Was the reported result selected from a larger unreported set (forking paths / file drawer)?",
     "needs": "an enumerator of runs, seeds and variants that existed versus those reported",
     "tools": [("NT-015", "PARTIAL", "canon R11: completeness of reporting for declared forecasts only"),
               ("NT-051", "PARTIAL", "git-history census: run directories and result files that existed at each commit"),
               ("NT-050", "PARTIAL", "ledger census: rows present vs rows cited")],
     "limits": "no instrument compares the set of runs that EXISTED with the set REPORTED; every admissible cell is a denominator fragment"},
    {"id": "FQ-15", "scope": 'PARTIAL: commit order and one declared-bound gate shape', "question": "Was the claim written before or after the evidence it cites existed (temporal order)?",
     "needs": "timestamp / commit ordering of claim text versus artifact bytes",
     "tools": [("NT-019", "PARTIAL", "Atalanta null_bound: bound declared before emissions counted (one gate shape)"),
               ("NT-051", "PARTIAL", "git-history census gives commit order of files, not of claims inside files")],
     "limits": "commit order is a lower bound on write order; claims edited in place have no admissible ordering instrument"},
    {"id": "FQ-16", "scope": 'PARTIAL: p floors only, no power', "question": "Did the test have the power to see the effect claimed (sample size, p floor)?",
     "needs": "a power / p-floor calculator against the claimed effect size",
     "tools": [("NT-025", "PARTIAL", "resampling p-values with the correct floor (PRF-2)"),
               ("NT-013", "PARTIAL", "chance floor for modal-collapse claims")],
     "limits": "p floors are covered; POWER against a claimed effect size has no instrument"},
]


def main() -> int:
    rows = {r["tool_id"]: r for r in (json.loads(l) for l in (HERE / "TOOLS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip())}
    out = {"schema": "necropolis.workshop.forensic_map/1", "generated_by": "engine/necropolis/workshop/build_forensic_map.py",
           "rule": "a tool appears under admissible_instruments only if TOOLS.jsonl says admissibility.admissible; the Keeper's mapping cannot promote a tool. Verdict ANSWERABLE requires scope GENERAL; any named restriction caps the verdict at ANSWERABLE_RESTRICTED; a scope declared PARTIAL may list no DIRECT row. Empty and partial cells are the product.",
           "questions": [], "summary": {}}
    unknown = []
    for q in Q:
        adm, cand = [], []
        for tid, role, how in q["tools"]:
            r = rows.get(tid)
            if r is None:
                unknown.append(tid); continue
            a = r["admissibility"]
            item = {"tool_id": tid, "name": r["name"], "role": role, "how": how, "necropolis_status": r["necropolis_status"]}
            if a["admissible"]:
                item["admissible_as"] = a["admissible_as"]
                if r.get("caveat"):
                    item["caveat"] = r["caveat"]
                adm.append(item)
            else:
                item["blocked_by"] = a["blocked_by"]
                cand.append(item)
        direct = [x for x in adm if x["role"] == "DIRECT"]
        sc = q["scope"]
        if not adm:
            verdict = "EMPTY"
        elif not direct or sc.startswith("PARTIAL"):
            verdict = "PARTIAL"
        elif sc == "GENERAL":
            verdict = "ANSWERABLE"
        else:
            verdict = "ANSWERABLE_RESTRICTED"
        if sc.startswith("PARTIAL") and direct:
            raise SystemExit(f"{q['id']}: scope says PARTIAL but a DIRECT admissible row is listed; fix the mapping, not the scope")
        out["questions"].append({"id": q["id"], "question": q["question"], "instrument_must": q["needs"], "verdict": verdict, "scope": sc,
                                 "admissible_instruments": adm, "candidates_if_validated": cand, "limits": q["limits"],
                                 "n_admissible_direct": len(direct), "n_admissible_partial": len(adm) - len(direct), "n_candidates": len(cand)})
    if unknown:
        print("unknown tool ids in mapping:", unknown); return 2
    used = {x["tool_id"] for q in out["questions"] for x in q["admissible_instruments"]}
    all_adm = {t for t, r in rows.items() if r["admissibility"]["admissible"]}
    out["summary"] = {"questions": len(Q), "verdicts": {v: sum(1 for q in out["questions"] if q["verdict"] == v) for v in ("ANSWERABLE", "ANSWERABLE_RESTRICTED", "PARTIAL", "EMPTY")},
                      "admissible_tools_total": len(all_adm), "admissible_tools_mapped": len(used),
                      "admissible_tools_unmapped": sorted(all_adm - used),
                      "note_unmapped": "an admissible tool that answers none of the sixteen questions is a tool without a forensic question; listed, not dropped"}
    (HERE / "FORENSIC_QUESTIONS.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    # markdown view
    L = ["# Forensic question -> instrument map (generated; do not edit)", "",
         "Source: build_forensic_map.py over TOOLS.jsonl.  A row appears as an answerer only if the registry's",
         "admissibility ladder says so.  DIRECT = evidentiary_scope answers the question for the named object class;",
         "PARTIAL = necessary sub-question or restricted class.  Candidates are NOT answerers.", "",
         "| id | question | verdict | scope | direct | partial | candidates |", "|---|---|---|---|---|---|---|"]
    for q in out["questions"]:
        L.append(f"| {q['id']} | {q['question']} | {q['verdict']} | {q['scope']} | {q['n_admissible_direct']} | {q['n_admissible_partial']} | {q['n_candidates']} |")
    for q in out["questions"]:
        L += ["", f"## {q['id']} {q['question']}", "", f"Verdict: **{q['verdict']}** (scope: {q['scope']}).  Instrument must: {q['instrument_must']}", ""]
        for x in q["admissible_instruments"]:
            cav = f" _(caveat: {x['caveat']})_" if x.get("caveat") else ""
            L.append(f"- {x['tool_id']} {x['role']} [{x['admissible_as']}] {x['how']}{cav}")
        if q["candidates_if_validated"]:
            L.append("- candidates (not answerers): " + "; ".join(f"{x['tool_id']} ({x['necropolis_status']}, blocked_by {x['blocked_by']})" for x in q["candidates_if_validated"]))
        L.append(f"- limits: {q['limits']}")
    s = out["summary"]
    L += ["", "## Summary", "", f"- verdicts: {s['verdicts']}", f"- admissible tools mapped: {s['admissible_tools_mapped']} / {s['admissible_tools_total']}",
          f"- admissible tools answering no question: {', '.join(s['admissible_tools_unmapped']) or 'none'}"]
    (HERE / "FORENSIC_QUESTIONS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(s, indent=1))
    for q in out["questions"]:
        print(q["id"], q["verdict"], "direct", q["n_admissible_direct"], "partial", q["n_admissible_partial"], "cand", q["n_candidates"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
