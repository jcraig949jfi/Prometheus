"""EOS-02 Mission 6: shrink, do not federate.

Operator's provisional disposition:
    duplicated model-provider rows   RETIRE
    stale local-model inventory      RETIRE
    seven non-model source rows      PRESERVE AS SOURCES RESIDUE
    no synchronisation with prometheus_llm, no second general registry

This script performs the shrink once and is kept so the transformation is
reproducible rather than asserted. It writes:

    roles/Eos/sources/SOURCES.json        the 7 preserved rows, retyped
    roles/Eos/archive/api_registry_2026-04-01.json
                                          the original, byte-preserved,
                                          so nothing retired is lost

THE SOURCE TYPE is the smallest thing that describes an external
information source WITHOUT pretending it is a model provider. It has no
model list, no token accounting, no completions endpoint and no chat
shape, because these sources have none of those. It has the two things a
model provider row does not carry: what the source RETURNS, and whether
anyone has actually called it.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OLD = REPO / "agents" / "eos" / "data" / "api_registry.json"
OUT = REPO / "roles" / "Eos" / "sources" / "SOURCES.json"
ARCHIVE = REPO / "roles" / "Eos" / "archive" / "api_registry_2026-04-01.json"

#: Covered by prometheus_llm today -> RETIRE (duplication with a measured
#: failure to stay current: these rows never noticed they were superseded
#: in August).
RETIRE_COVERED = ("cerebras", "google_gemini", "groq", "openrouter")
#: Model providers prometheus_llm does not carry -> RETIRE from here and
#: OFFER once to prometheus_llm. Eos does not keep a model registry.
RETIRE_OFFERED = ("github_models", "huggingface_inference", "sambanova", "together_ai")
#: The residue. Not model providers: no completions interface, no model
#: names, no token accounting; three need no credential at all.
KEEP = ("arxiv_api", "openalex", "semantic_scholar", "crossref",
        "tavily", "serper_dev", "google_custom_search")

RETURNS = {
    "arxiv_api": "Atom XML records of preprints",
    "openalex": "JSON academic metadata records",
    "semantic_scholar": "JSON paper records with TLDRs and citation edges",
    "crossref": "JSON publication metadata by DOI",
    "tavily": "parsed page content for agent consumption",
    "serper_dev": "web search result lists",
    "google_custom_search": "web search result lists",
}
AUTH = {"arxiv_api": "none", "openalex": "none (polite pool wants a mailto)",
        "crossref": "none (polite pool wants a mailto)", "semantic_scholar": "api_key",
        "tavily": "api_key", "serper_dev": "api_key", "google_custom_search": "api_key"}
#: Facts this seat established rather than copied. Everything else is
#: UNVERIFIED until a call is made and recorded.
KNOWN_STATE = {
    "semantic_scholar": ("REJECTED", "403 with a present key, Techne 0d76ac34d, 2026-08-31"),
    "serper_dev": ("PARKED", "2,500 LIFETIME budget; unspent, and it stays unspent until a "
                             "typed query set exists (EOS-R8)"),
}


def main() -> int:
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from archaeon.workspace import assert_not_canonical
    assert_not_canonical("the EOS-02 registry shrink", allow_override=False)

    old = json.loads(OLD.read_text(encoding="utf-8"))
    apis = old["apis"]

    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OLD, ARCHIVE)

    probe = json.loads((REPO / "roles/Eos/intake/probe_arxiv.json").read_text(encoding="utf-8"))
    rec = probe["records"][0]

    sources = {}
    for name in KEEP:
        row = apis.get(name, {})
        state, note = KNOWN_STATE.get(name, ("UNVERIFIED", "never called by this seat; every "
                                                           "limit below is the provider's claim"))
        obs = None
        if name == "arxiv_api":
            state, note = "MEASURED", "called 2026-09-11 by this seat"
            obs = {"endpoint": rec["endpoint"], "observed_at": rec["observed_at"],
                   "status": rec["status"], "latency_ms": rec["latency_ms"],
                   "items_returned": rec["items_returned"], "observed_by": rec["observed_by"]}
        sources[name] = {
            "id": name,
            "kind": "SOURCE",
            "returns": RETURNS[name],
            "auth": AUTH[name],
            "documented_limit": row.get("rate_limit") or row.get("notes") or "UNRECORDED",
            "limit_read_on": "2026-04-01",
            "limit_source": "the provider's documentation as recorded in April; NOT re-read",
            "budget_rule": "at or under 75 percent of the documented limit (the Dawn Constitution)",
            "observation": obs,
            "state": state,
            "note": note,
            "decay_days": 30,
        }

    out = {
        "schema": "eos.sources/v1",
        "written_at": "2026-09-11",
        "what_this_is": (
            "External INFORMATION SOURCES. Not model providers: none has a completions "
            "interface, model names or token accounting, and three need no credential. "
            "prometheus_llm is the program's one model API and this file does not "
            "duplicate, mirror or synchronise with it. If prometheus_llm's maintainer "
            "claims these belong there, this file is migrated once and deleted."),
        "retired_from_the_old_registry": {
            "covered_by_prometheus_llm": list(RETIRE_COVERED),
            "model_providers_offered_once_to_prometheus_llm": list(RETIRE_OFFERED),
            "local_model_weights_inventory": list(old.get("local_models", {})),
            "where_they_went": "roles/Eos/archive/api_registry_2026-04-01.json (byte-preserved)",
        },
        "rule": ("A row is not usable capacity until `observation` is non-null and younger "
                 "than decay_days. A provider's documented free tier is a label."),
        "sources": sources,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=2)
        fh.flush()

    measured = sum(1 for s in sources.values() if s["state"] == "MEASURED")
    print("kept {} sources ({} MEASURED, {} not), retired {} model rows and {} local-model rows"
          .format(len(sources), measured, len(sources) - measured,
                  len(RETIRE_COVERED) + len(RETIRE_OFFERED), len(old.get("local_models", {}))))
    for n, s in sources.items():
        print("   {:<22} {:<10} {}".format(n, s["state"], s["returns"]))
    print("wrote", OUT.relative_to(REPO))
    print("archived", ARCHIVE.relative_to(REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
