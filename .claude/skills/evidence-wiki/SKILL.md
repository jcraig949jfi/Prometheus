---
name: evidence-wiki
description: Query and contribute to the Prometheus Evidence Wiki (Mnemosyne's canonical empirical memory). Use BEFORE starting substantial new research — "has this been tested?", "is there counterevidence?", "has this mechanism failed elsewhere?", "who consumes this output?" — and AFTER completing a gated result, to submit the experiment, claim, evidence, failure, or correction. Also for finding related findings across agents, contradictions, provenance chains, orphaned findings, and (clearly-labeled) hypothesis gaps.
---

# Evidence Wiki (Mnemosyne)

One knowledge substrate, many representations. Canonical evidence lives in the
`ew` schema of prometheus_fire behind a REST service; **never query the
database directly — the API is the contract.**

Service: `http://localhost:8377` on M1; from other machines set
`EW_SERVICE_URL=http://192.168.1.202:8377`. Human UI at `/wiki`.

## How to call it

Use the Python client (repo-relative):

```python
import sys; sys.path.insert(0, "evidence_wiki")
from ew.client import EvidenceWiki
ew = EvidenceWiki(agent="<your seat name>")   # machine auto-detected
```

## Read before reinventing (scoped, bounded — don't dump the wiki into context)

```python
ew.search_evidence("mutational redundancy", k=5)        # hybrid bm25+embedding
ew.search_evidence("forgetting", status="REFUTED")       # filter by status
ew.get_claim(claim_id)              # versions, evidence, relations, ceiling
ew.get_counterevidence(claim_id)    # refutations, contradictions, qualifications
ew.related_findings(claim_id)       # graph (observed) + semantic (similarity)
ew.contradictions()                 # direct vs apparent-under-differing-conditions
ew.provenance(object_id)            # walk to source packet / commit / hash
ew.find_consumers()                 # orphaned findings (no consumer edge)
ew.find_gaps()                      # HYPOTHESIZED missing cells — NOT evidence
```

## Write after earning (staged; the server rejects provenance-free writes)

Submissions enter as `SUBMITTED`/agent-attributed; they do NOT become
established by transport. Statuses describe what the SOURCE adjudicated.

```python
p = ew.register_packet("ergon/gen2/REVIEW_PACKET.txt", "review_packet",
                       git_commit="<sha>")
x = ew.register_experiment("Ergon", "gen2", "Gen-2 retention transplant",
                           substrate="D-5 program ecology",
                           packet_id=p["packet_id"])
c = ew.submit_claim("<one-sentence claim>", "SUPPORTED",
                    packet_id=p["packet_id"], experiment_id=x["experiment_id"],
                    source_span="L40-L55", source_wording="<verbatim>",
                    claim_ceiling="<scope limits>", agent="Ergon",
                    write_stage="SOURCE_BOUND")
ew.submit_evidence(p["packet_id"], "<VERBATIM adjudicating quote>",
                   "CONTROLLED_EXPERIMENT", claim_id=c["claim_id"],
                   outcome_canonical="CONFIRMED", metric_text="<numbers>",
                   gate="<prereg/correction>", write_stage="SOURCE_BOUND")
ew.register_failure(p["packet_id"], "<verbatim>", claim_id=...)  # negative results are first-class
ew.submit_relation(src_claim, "QUALIFIES", dst_claim,
                   epistemic_class="OBSERVED", packet_id=p["packet_id"])
```

Corrections are never destructive: submit a new claim + a `CORRECTS`/
`SUPERSEDES` relation; history is preserved.

## Hard epistemic rules the service enforces (don't fight them)

- Evidence requires a registered source packet + verbatim quote; a derived
  view (wiki page, tensor output) is REFUSED as evidence provenance.
- `OBSERVED` relations need packet provenance; tensor/model output is
  `INFERRED`/`HYPOTHESIZED` and is labeled so everywhere.
- Retries are safe: idempotency keys + content-addressed IDs mean duplicates
  collapse; never hand-dedupe.
- Every response carries `canonical_revision` and derived-view freshness;
  treat stale latent views accordingly.
