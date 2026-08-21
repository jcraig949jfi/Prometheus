# Paradigm artifact schema (settled Aporia P81 — the P79/P80 open question)

Two consumables per paradigm, one source of truth:

1. **`PARADIGM_Pxx_<name>.md`** — the human artifact (worked example + decision tree +
   skeleton + catalog assignment + honesty section). Written FIRST; the prose is
   authoritative.
2. **One record in `paradigm_trees.jsonl`** — the machine-readable projection the
   Learner corpus ingests. A PURE re-serialization of the artifact: any divergence
   between record and artifact is a bug in the record.

## Record shape (one JSON object per line)

- `paradigm_id`: "P01".."P26" (P20 removed; taxonomy canonical count 25 active).
- `name`: taxonomy name.
- `verb` / `payoff_verb`: the operational verbs (feedback_verbs_over_nouns — the
  verb IS the paradigm; the payoff verb is what you can do afterward that you
  could not before).
- `decision_nodes`: ordered list of `{id, q, yes, no}` where `yes`/`no` are either
  another node id or a terminal `"ACTION: ..."` / `"EXIT: ..."` string. The tree
  must be reachable from node `Q1` and every path must end in a terminal.
- `worked_example`: `{script, verdict, key_counts{}}` — script is a repo-relative
  path that MUST exist; verdict is the pre-stated branch that fired; key_counts
  are the artifact's headline numbers, restated exactly.
- `assignments` / `anti_assignments`: lists of CAT-MATH/MATH ids. Every id MUST
  resolve against `aporia/mathematics/triage.jsonl` (phantom-refs doctrine:
  cross-doc refs validate against the registry, not against other refs).
- `template_lessons`: short strings — the authoring lessons future paradigm passes
  inherit (e.g. raw-distributions-beside-derived-numbers).

## Validation

`aporia/paradigms/validate_paradigms.py` (run every pass that touches paradigms;
exit 0 required): parses every record, checks tree reachability + terminality,
script-path existence, and assignment resolution against triage.jsonl.

## Authoring rules for P03+

- Artifact first, record second, validator third — in the same pass.
- Worked example EXECUTED against local substrate; readings pre-stated in-script.
- Raw distributions printed beside every derived number (P80 lesson).
- Typed-value assumptions verified against raw data, never column names (P79/P80).
- DR grounding: read if it exists in BACKCORPUS, never re-fired.
