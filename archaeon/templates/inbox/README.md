# Template inbox

**Nothing in this directory is drawn from.** That is the whole point of it.

Per `archaeon/docs/ROADMAP.md`, Challenge 2, the experiment template registry
separates *proposing* from *admitting*:

- Anyone may propose. Literature miners, other seats, the chaos mutator, and
  the operator all write `PROPOSED` templates here.
- **Admission is a human act.** A template goes `PROPOSED` to `ADMITTED` only
  by the operator, and only an admitted template can be drawn by a tick.
- A `PROPOSED` template whose `kind` Vivarium does not implement **is an
  expansion request**, automatically. It is exactly the "the bench is not
  capable of this" case, and it belongs to Challenge 3.

## What a file here looks like

One JSON object per file, named `<template_id>.json`, in the schema given in
the roadmap: `template_id`, `kind`, `param_space`, `origin`, `status`,
`admitted_by`, `admitted_at`, `rationale`.

Files written by an automated miner carry an extra `_ingest` object recording
which report and which deck produced them. That key is provenance, not part of
the template schema, and an admitting operator may drop it.

## The one hard rule about `param_space`

`vivarium/viv/kinds.py` declares the **exact** parameter set of every executor
kind. Not a minimum, an exact set. A payload missing a parameter is rejected,
and so is a payload carrying an extra one, because no executor is permitted a
default: a default would mean the bench silently choosing a scientific value
on the experimenter's behalf.

So a template naming an existing kind must declare exactly that kind's
parameters in `param_space`. A template naming a kind that does not exist yet
must declare the exact parameter set the proposed executor would consume.

As of 2026-09-06 the implemented kinds are `noop_v0` (no parameters),
`evaluate_bitstring` (`bits`, `length`) and `random_walk_v0` (`steps`,
`step_scale`, stateful). `archaeon.probe.v0` is RETIRED and cannot be admitted
again. Read the registry rather than trusting this paragraph, which will age.

## Provenance of the current contents

The 2026-09-06 literature-mining batch was produced by Herakles under the
roadmap's delegation, from
`roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/`. The deck,
the returned reports, the ingest script and the rejection log all live there.
Each template's `origin.reference` names the published method it came from.
Those references were produced by an automated research agent and have **not**
been verified against primary sources, so treat `origin.reference` as a lead to
check at admission time, not as an established citation.
