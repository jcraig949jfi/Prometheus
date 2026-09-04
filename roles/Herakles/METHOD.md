# Herakles — Excavation Method (operating protocol)
## Version 0, 2026-09-02. Governs every row written into `herakles/HERAKLES_HISTORICAL_COLLIDER_V0/`.

---

## 1. Provenance tiers (two orthogonal axes, both mandatory)

### 1a. Evidence source of a registry row (how do I know this?)
| Tag | Meaning | Allowed in ranked lists? |
|---|---|---|
| `ARTIFACT_IN_HAND` | I hold the bytes; sha256 in manifest J | yes |
| `PRIMARY_SOURCE_READ` | I read the original paper / thesis / code / data and cite page, figure, file or line | yes |
| `SECONDARY_SUMMARY` | A review, textbook, retrospective or replication; original not yet read | only with explicit flag, never in TOP-20/TOP-10 |
| `MODEL_RECALL_UNVERIFIED` | Written from my own recall; no source touched this session | never |

Every row starts as `MODEL_RECALL_UNVERIFIED` and is promoted only by touching a source. Promotion is logged with the date and the locator.

### 1b. Provenance class of a computational object (what is this thing?)
| Class | Definition |
|---|---|
| `ORIGINAL_SPECIMEN` | Bytes produced by the original investigators (code, genomes, logs, configs, seeds) obtained from an original or archival location |
| `RECOVERED_SPECIMEN` | Original bytes reassembled from partial / damaged / mirrored sources; every repair step documented; hash of both raw and repaired |
| `REIMPLEMENTATION` | New code written to the original specification with all parameters specified in the source; no free choices |
| `APPROXIMATE_RECONSTRUCTION` | New code where at least one parameter or rule was unspecified; every free choice enumerated, variants built |
| `CONCEPTUAL_REPRODUCTION` | Same mechanism, different physics; may test the idea, cannot test the historical phenomenon |

An object carries exactly one class. Downgrades are free; upgrades require the evidence named above.

---

## 2. Retrieval discipline (directive §22)

1. Build the query from the field's own vocabulary and the discarded-language lexicon (`DISCARDED_LANGUAGE_LEXICON.md`). Prometheus terms are forbidden in queries.
2. Enumerate the inventory before sampling it. No `files[:N]`, no alphabetical-prefix walks, no first-page-of-results reading. Stratify by decade, substrate, and venue.
3. Descend the evidence hierarchy (§4 of the directive). A review may open a family; it may not close a row.
4. For each family log: what was searched, where, on what date, what was found, what was NOT found (a null search is a row too).

---

## 3. Specimen custody

- On recovery: `sha256`, byte length, source URL or mirror, retrieval timestamp, HTTP/FTP headers where available, and the archival snapshot id if from a web archive.
- Originals are stored read-only under `herakles/specimens/<specimen_id>/original/`. Nothing is ever written there after the manifest row is committed.
- Repairs, decompressions, transcodings, and builds go under `.../derived/` with `derived_from` and their own hashes.
- Large binaries (> ~50 MB) live on `Z:\herakles\specimens\` with hash and path recorded in manifest J; the repo holds the manifest, never the blob.

---

## 4. Detector Resolution Profile (Mission B)

For each family, answer the directive's §2-B questionnaire verbatim (retained generations, extinct lineages, unsuccessful interactions, neutral/deleterious mutations, ancestry, intermediate genomes, environment state, seeds, determinism, replay, fork, ablation, alternative descendants, mutation history, resources, failure richness, behavior traces, acquisition cost, future mutation utility, discarded branches, excluded runs, aggregate-only publication). Each answer is one of `YES / NO / PARTIAL / UNKNOWN`, with the locator that supports it. `UNKNOWN` is a valid, honest answer and is never silently converted to `NO`.

Then estimate the Vesuvius quantities (§7): original compute, storage, replication count, detector resolution; modern feasible compute, storage, replication; SFE resolution. Order-of-magnitude is sufficient and must be labelled as an estimate.

---

## 5. Parts registry discipline (Mission C)

A candidate part is written in causal computational language only: preconditions → transformation → observable consequence → downstream effect on reachability. Disciplinary names go in `historical_terminology`, nowhere else. Evidence strength uses the edge classes of §12: `observed_association < historical_sequence < perturbation < ablation < replication < mechanistic_proof`. A part with only `observed_association` is a candidate part and is labelled so.

---

## 6. Composition search discipline (Mission D)

For each pair or triple of parts record: has any historical system contained both? Was the combination measured against each part alone? Is Effect(A+B) reported, and on what population and unit? If nobody tested the cell, it is a missing cell in the factorial and goes to deliverable P with an explicit cost estimate for filling it in SFE.

---

## 7. Reconstruction protocol (directive §6, §19)

1. Write the physics sheet: simulator, language/platform, world rules, genotype, mutation operators, selection, resources, population model, initialization, stopping, original compute budget, known quirks, unspecified parameters, assumptions.
2. Classify (1b). If any parameter is unspecified, the class is at best `APPROXIMATE_RECONSTRUCTION`, and every free choice gets ≥ 2 variants.
3. First SFE run: faithful physics, pinned seeds, observation only. Question: does the phenomenon recur? Report the recurrence rate with its SE and n.
4. Add resolution (lineage, neutral tracking, failure emission, behavior traces) without touching physics.
5. Only then: forks, ablations, counterfactual replays, null arms, 10,000× scaling.

---

## 8. Statistical floor (inherited Prometheus rules)

- Unit of analysis is the independent run (or lineage), never the generation or the organism, unless independence is shown.
- SE is computed before any threshold is chosen; the CI is reported beside every verdict.
- A null arm is designed to perturb the axis the statistic varies on.
- A gate must be shown reachable (attainable range computed) before a null reading is accepted.
- 5+ seeds minimum before any word stronger than "lead".

---

## 9. What an LLM may and may not do here (directive §23)

May: retrieve, translate terminology, triage sources, read and summarize code, propose hypotheses, draft queries, draft reconstructions for human and executable verification.
May not: assert a replication succeeded, assert causal equivalence between two mechanisms, assert a historical fact without a locator, declare evolvability improved, place a part in a circuit, or declare significance. Where I am tempted to, I write `CLAIM_REQUIRES: <executable test or source>` instead.

---

## 9a. Citations inside briefs and handoffs (added 2026-09-03)

A brief is not exempt from the evidence tiers. Every citation in a brief, handoff or agent prompt carries a tier exactly as a registry row does, and a `MODEL_RECALL_UNVERIFIED` citation must be marked as such **inside the brief**, so the recipient knows it may not exist.

This rule exists because Survey 1 caught two paper titles supplied from recall that appear in neither named author's bibliographic record. The cost is not embarrassment; it is that an agent spends a constrained search budget hunting a phantom instead of answering the question.

Corollary: when naming a paper in a brief, prefer a DOI or a stable URL over a remembered title. A wrong title is worse than no title, because it looks actionable.

## 10. Session hygiene

- Every session opens by reading `RESPONSIBILITIES.md`, this file, the newest `todo_*.md`, and the V0 `README.md` status block.
- Every session closes with a dated journal entry, updated todo (checked items datestamped, purged after 24h), and a commit of only Herakles paths via `git commit <paths> -F msg`, pushed, then verified with `merge-base --is-ancestor`.
- Significant new directives: verbatim file + sha256 in `prompts/`, ASCII review packet beside it, packet delivered in chat as one paste block.
