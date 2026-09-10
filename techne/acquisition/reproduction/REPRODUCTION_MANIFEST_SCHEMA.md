# Reproduction manifest — schema and the rule that makes it worth writing

H0–H5 design v0.1, §7: *"Fable must create a reproduction manifest before a benchmark
claim: paper/version, claim/table/figure, exact metric and expected value, task/data
hashes, seed and compute settings, comparison variant, tolerated deviation, observed value
and failure status. An unresolved expected value blocks a reproduction verdict, not source
acquisition or smoke tests."*

## The rule

A manifest is written and **committed before the run**, with `observed` null and
`status: "DECLARED_NOT_RUN"`. The run then writes a **separate** result file. The manifest
is never edited to match what came back.

This is not ceremony. A tolerance chosen after seeing the number is not a tolerance, and a
"reproduction" whose expected value was filled in from the observation is a tautology. The
same error class is already on record in this programme as a threshold picked after the
measurement.

## Required fields

```
id                      stable identifier, used by the result file to point back here
tool                    manifest entry id in techne/acquisition/MANIFEST.json
source                  what is being reproduced, WITH its own provenance:
  kind                  "upstream_documentation" | "paper" | "artifact" | "design_citation"
  reference             URL or citation
  retrieved_utc         when this seat read it
  sha256                digest of the retrieved text, if retrieved
  NOTE                  if a number's provenance is a SECOND-HAND citation rather than a
                        page this seat read, say so here. A design packet quoting a figure
                        is a design_citation, not upstream documentation.
claim                   the specific claim, table or figure
metric                  exact metric name and units
expected                the value, or null if UNRESOLVED
expected_provenance     which `source` entry the expected value came from
tolerated_deviation     declared BEFORE the run; absolute or relative, with a reason
data                    every input, each with filename, bytes and sha256
invocation              exact call, including every parameter that affects the result
seed                    RNG seed, or "NONE_DECLARED_UPSTREAM" with the consequence stated
compute                 threads, memory ceiling, budget profile name
comparison_variant      "upstream-reproduction" or "prometheus-adapter" (the design's two
                        named tracks). A modernised dependency stack, a reduced task set or
                        a changed compressor is a DEVIATION and is listed.
deviations              known differences from the upstream configuration
observed                null until the run
status                  DECLARED_NOT_RUN -> REPRODUCED | DEVIATED_WITHIN_TOLERANCE |
                        FAILED_OUTSIDE_TOLERANCE | BLOCKED_UNRESOLVED_EXPECTED_VALUE |
                        BLOCKED_RESOURCE
what_this_does_not_show the stages this reproduction says nothing about
```

## Three outcomes are not one

The design separates *a smoke test*, *an algorithm reconstruction* and *a published-metric
reproduction*. A manifest covers the third. A run that executes the tool on the upstream
input and produces *some* output has done the first. Saying "reproduced" for that is the
inflation this file exists to prevent.

## Partial resolution is a normal state

If the expected value is UNRESOLVED, the manifest is still written, the smoke run still
happens, and the verdict field stays `BLOCKED_UNRESOLVED_EXPECTED_VALUE`. Source
acquisition and smoke execution are not blocked by it — only the verdict is.
