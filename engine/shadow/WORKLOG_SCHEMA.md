# Shadow Worklog — schema and rules
Established 2026-08-20 per James's directive: every Aporia loop pass commits a work log
detailed enough for an EXTERNAL agent to critique, with citations and external links per
iteration. The reviewer (M2, "Elenchus" seat) writes REVIEWS.jsonl alongside; Aporia ingests
open reviews each pass and responds in-log. Neither side ever blocks the other.

## Files (this directory)
- WORKLOG.jsonl  — one record per loop pass, appended BEFORE the pass's commit, included IN it.
- REVIEWS.jsonl  — written only by the reviewer. One record per reviewed pass.
- REVIEW_AGENT_PROMPT.md — the reviewer's standing charter (cut-and-paste for M2).

## WORKLOG.jsonl record schema (v1)
{
  "pass_id":        "YYYY-MM-DDTHH:MMZ-<short>"   // unique, chronological
  "prev_commit":    "<hash the pass started from>",
  "threads":        ["CAT-MATH-0505", ...],        // executed / parked / closed this pass
  "intent":         "one sentence: what the pass set out to do",
  "pre_stated_readings": ["SUPPORTIVE-X: ...", "CHALLENGE: ..."],  // BEFORE measurement
  "actions":        ["queries/computations run, with parameters and sample sizes"],
  "evidence":       ["exact numbers produced, with enough precision to re-derive claims"],
  "claims":         [{"text": "...", "type": "measurement|status|doctrine|infra",
                      "strength": "certain|supported|ambiguous|withheld"}],
  "narrative_resistance": ["simplest-explanation checks actually performed, and their outcomes"],
  "alternatives_rejected": ["what was NOT done and why — the reviewer judges these choices"],
  "citations":      [{"ref": "Author (Year). Title.", "link": "https://arxiv.org/abs/...",
                      "role": "grounding|verification|comparison"}],
  "external_links_fetched": ["URLs actually fetched this pass, if any"],
  "self_identified_weaknesses": ["the pass's own list — reviewer checks it for completeness"],
  "falsifier":      "what observation would show this pass's main claim is wrong",
  "files_touched":  ["paths"],
  "review_responses": [{"review_id": "...", "disposition": "fixed|acknowledged|rebutted",
                        "note": "..."}]   // responses to open REVIEWS entries
}

## Rules
1. The log is written EVERY pass, in the same commit as the pass's work. A pass without a
   log entry is an incomplete pass.
2. Citations: every pass whose content touches mathematics cites the relevant PRIMARY
   literature (arXiv/DOI links). Infra-only passes cite the internal doctrine files they
   apply. Links must be real; the reviewer spot-checks them.
3. self_identified_weaknesses is mandatory and non-empty. An empty weakness list is itself
   a weakness.
4. Review ingestion: at pass start, read REVIEWS.jsonl entries with no matching
   review_responses; respond to each in this pass's record. Rebuttals must argue from
   evidence, not authority. Fixes reference the fixing commit.
5. The reviewer NEVER blocks the loop; the loop NEVER edits REVIEWS.jsonl.
6. Passes before 2026-08-20 are documented by their commit messages and
   aporia/catalog_attacks/ + engine/queues/ artifacts; a retrospective seed entry
   summarizes them for reviewer context.
