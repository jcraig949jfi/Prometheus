# Erebos v2 Design Template

**Date:** 2026-05-27
**Purpose:** Each of the 22 unblocked plugins will receive a v2 design document populated from the Gemini Deep Research output and ready to drive the frontier-model review prompts. This template defines the per-plugin v2-design schema so each design is consistent and reviewable.

**Inputs to fill the template:**
1. v1 plugin file (`charon/agents/erebos/generators/g<NN>_<name>.py`)
2. v1 composition loader file(s) (`charon/agents/stygian/loaders/composition_g<NN>_*.py`) if any
3. Gemini DR output (`aporia/docs/deep_research_reports/erebos_v2_2026-05-27/<NN>_<slug>.md`)
4. Relevant substrate finding doc(s) (per whitepaper section 5)

**Output:** `aporia/docs/erebos_v2_designs/g<NN>_<name>_v2.md`

---

## Template

```markdown
# G<NN> <Name> — v2 design

**Date:** 2026-05-27
**Status:** v2 design proposal, informed by DR `aporia/docs/deep_research_reports/erebos_v2_2026-05-27/<NN>_<slug>.md`
**Predecessor:** v1 at `charon/agents/erebos/generators/g<NN>_<name>.py`; loader(s) at `charon/agents/stygian/loaders/composition_g<NN>_*.py`

## 1. v1 state — what we have

- **Plugin tier:** R<n>, F<n>, M<n>, H<n> (per Reasoning Ladder v0.1)
- **Cognitive move:** <2-sentence summary of transformation>
- **Expected kill_pattern:** `<kill_pattern_name>`
- **Composition loader status:** <none / one variant / multi-variant>
- **Live substrate finding (if any):** <e.g., "ITER-4 Salem moderation at observed=0.997 vs null_p95=0.024">

## 2. DR-surfaced critical objections (top 3)

For each, cite the primary source the DR cited.

- **Objection 1:** <load-bearing v1 assumption the DR challenged>
  - Source: <arXiv ID / DOI, year>
  - Failure mode it predicts: <specific shape>
- **Objection 2:** <...>
- **Objection 3:** <...>

## 3. v2 architectural changes

Concrete code-level changes. Each change must reference (a) what v1 module changes, (b) what new module is added, (c) what tests get updated.

### 3.1 <Change 1: e.g., replace argmax-|value| with PC-algorithm confounder identification>

- **What changes:** <file/module/function>
- **New module:** <if needed>
- **New constants:** <e.g., new threshold variables with calibrated values>
- **Test updates:** <existing tests that must be re-baselined; new tests that get added>

### 3.2 <Change 2: ...>

### 3.3 <Change 3: ...>

## 4. New kill_patterns introduced

| kill_pattern | When it fires | Substrate-grade meaning |
|---|---|---|
| `<new_kp_1>` | <empirical condition> | <what the substrate learns when it fires> |
| `<new_kp_2>` | <...> | <...> |

## 5. Cross-plugin interactions

How v2 changes the plugin's relationship with neighboring plugins:
- vs G<X>: <distinction or interaction change>
- vs G<Y>: <distinction or interaction change>

## 6. Refinement loop trigger

Conditions under which v2 should become v3 (i.e., what the substrate-grade falsification of v2 would look like):
- <condition 1>
- <condition 2>

## 7. Falsification route specification

The exact battery shape an Erebos v2 emission flows through:

```
queue_payload → loader.applicable() → loader.build_battery_input() → verdict
```

For each step, specify:
- **applicable():** <gate logic>
- **build_battery_input():** <data accessor + transformation>
- **verdict:** <decision rule, with thresholds>

## 8. Anti-gravitational-well check

The DR surfaced N conventional framings. v2 explicitly rejects:
- <conventional framing 1> — substrate alternative: <approach actually taken>
- <conventional framing 2> — substrate alternative: <approach actually taken>

## 9. Open questions for frontier review

3-5 specific questions where v2 leaves a design choice ambiguous and frontier critique would be load-bearing. These become Section X of the corresponding frontier review prompt.

- Q1: <specific design question>
- Q2: <...>
- Q3: <...>

## 10. Implementation budget

Estimated iteration cost:
- v2 plugin update: <N iterations>
- v2 loader update: <N iterations>
- Synthetic-control tests: <N iterations>
- Substrate finding doc (if v2 surfaces new structure): <N iterations>

Total: <range>
```

---

## How to fill this template for each plugin

After DR `<NN>` lands in `aporia/docs/deep_research_reports/erebos_v2_2026-05-27/<NN>_<slug>.md`:

1. **Skim the DR's Key Points + section 1-3 headings** to identify the top critique vectors.
2. **For each of the 7 DR sub-tasks**, extract the most actionable recommendation.
3. **Populate section 2 (top 3 objections)** with the load-bearing critiques.
4. **Populate section 3 (architectural changes)** with concrete diffs against the v1 module.
5. **Populate section 4 (kill_patterns)** with newly-introduced labels.
6. **Populate section 9 (open questions for frontier review)** with the design ambiguities the DR did not resolve.
7. **Leave section 10 (implementation budget)** until the v2 module is sketched.

The completed v2 design then drives the corresponding frontier review prompt from `aporia/docs/erebos_v2_frontier_review_prompts_2026-05-27.md`.

## Sequencing dependencies

```
DR completes  →  v2 design template populated  →  frontier review prompts fired
   (now)            (next, sequential to DR)         (after v2 designs land)
```

For 22 plugins running in parallel:
- DR batch 1 (G01, G02, G03): COMPLETE
- DR batch 2 (G04, G05, G06): COMPLETE OR IN-FLIGHT
- ... etc

As each DR lands, the corresponding v2 design can be drafted immediately rather than waiting for all 22.

## Quality bar for v2 designs

Per `feedback_take_a_stand` and `feedback_substrate_passive_consumer_warning`:
- Every v2 design MUST commit to ≥1 concrete architectural change.
- Every v2 design MUST commit to ≥1 new test or new kill_pattern.
- A v2 design that says "we should investigate X further" without committing is rejected — push back to DR for more specificity, or admit the plugin is not ready for v2.
- The 22 v2 designs are themselves a falsifiable artifact: if frontier review aggregates show that ≥1 frontier model identifies a substrate-grade alternative the v2 missed, v2 was wrong on that plugin and v3 is owed.
