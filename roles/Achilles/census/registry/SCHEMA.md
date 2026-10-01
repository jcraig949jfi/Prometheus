# Achilles seat registry -- schema (prometheus.achilles_registry.v1)

Written once by the first-run reconstruction (2026-09-30), re-verified by
every census run (missing seats, engines without owners, ownership drift
are flagged automatically). Every claim carries a source path.

seats_partN.json = {"schema": "prometheus.achilles_registry.v1", "part": N,
  "built_at_utc": "...", "base_sha": "...", "seats": [SEAT, ...]}

SEAT = {
  "seat": "Theseus",                       # canonical name (roles/<dir> spelling)
  "kind": "SEAT | HISTORICAL_ROLE_DOC | BRANCH_ONLY_SEAT | AGENT_TOOL",
  "short_role": "<= 6 words",
  "declared_role": {"text": "1-2 sentences, plain", "source": "repo path", "source_currency": "YYYY-MM-DD or null"},
  "observed_role": {"text": "1-2 sentences from recent commits/work", "differs": true|false,
                    "evidence": ["<sha> <date> <subject>", "..."]},
  "domain": "science | infrastructure | audit | reporting | coordination | historical",
  "lifecycle_marker": {"state": "ACTIVE|PARKED|RETIRED|CLOSED|IDLE|DEPRECATED|BLOCKED|NONE",
                       "date": "YYYY-MM-DD or null", "quote": "short verbatim", "source": "path:line"},
  "documented_host": {"value": "M1|M2|M3|M4|ubu001|ubu002|DESKTOP-RUAPVAI|ELSA|BUCKKEEP|null", "source": "path:line"},
  "aliases": [{"name": "...", "relation": "predecessor|same-name-different-referent|instance|lane|role-doc", "source": "..."}],
  "engines": [{"engine_id": "<repo path of the engine's code, e.g. primordial or SerendipityFoundry/SerendipityFoundryEngine>",
               "relationship": "primary|maintainer|builder|reviewer|auditor|consumer", "evidence": "path or sha"}],
  "entry_file": "roles/<Seat>/RESPONSIBILITIES.md",
  "notes": "conflicts between sources, uncertainties; never resolved by invention"
}

engines.json = {"schema": "prometheus.achilles_engines.v1", "built_at_utc": "...", "base_sha": "...",
  "engines": [ENGINE, ...]}

ENGINE = {
  "engine_id": "primordial",               # repo path (stable key)
  "name": "Nestor Primordial Engine (NPE)",
  "kind": "research-engine | experiment-ecosystem | infrastructure | auditor | communication | reporting | dashboard | index-search | data | legacy",
  "purpose": "1-2 sentences, plain",
  "paths": ["primordial"],
  "primary_seat": "Nestor | null",
  "other_seats": [{"seat": "...", "relationship": "maintainer|builder|reviewer|auditor|consumer", "evidence": "..."}],
  "home_host": "M1 | null",
  "state_marker": {"state": "ACTIVE|DORMANT|RETIRED|PARKED|UNKNOWN", "quote": "...", "source": "path:line"},
  "description_source": "path",
  "notes": "..."
}
