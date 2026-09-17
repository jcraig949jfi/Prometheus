# POET and ALife -- what Prometheus has, what was gathered, what it is for

Techne[gandalf-a04f7c25], 2026-09-17, M3. Directive: roles/Techne/prompts/2026-09-17_poet_alife/
OPERATOR.md (sha256 cf3a1616..55e26). Ledger with every identifier, pin, licence and evidence
grade: techne/acquisition/poet_alife/SOURCES_2026-09-17.json. Stage reached: FIND + PIN. Nothing
was cloned, run or wrapped: the Donor Foundry loop stops at PIN until a consumer names a need
(operator ruling 2026-09-12, TECHNE-51), and Harmonia's ruling of 2026-09-11 that POET has no
consumer stands until the operator says otherwise. The operator asked to GATHER; this is the
gather.

## 1. What the repository already held (nobody needed to fetch these)

- Both POET papers, VERIFIED with version history, GECCO and PMLR counterparts and the
  original-vs-Enhanced distinction, in Herakles's HR2 reference audit (section 10,
  `poet_paired_coevolution -> kind poet_loop_v0`). The template axes there are the ORIGINAL
  POET's (num_environments, transfer_interval); Enhanced POET's CPPN encoding and novelty
  measure appear in no template.
- Lehman and Stanley 2008 (novelty search, ALIFE XI), the ALife-to-search bridge, VERIFIED in
  the same audit.
- Tierra and Avida as Archaeon template families (Herakles 01_evolutionary_substrates:
  `alife.tierra.v0`, `digitevol.avida.v0`).
- Avida itself as a RUNNABLE_CONTAINER fossil with a passing smoke harness
  (techne/fossils/specimens/avida, pinned devosoft/avida@47f13dad).
- MAP-Elites via pyribs, a live Techne donor with a committed lock.
- Harmonia's ruling RULING_TECHNE_17_31_H4_AND_SDP_2026-09-11.md: POET is an H4 1.1 reference
  arm BY DESIGN; H4 is at SCAFFOLD; "only PURPOSE can be the reason POET waits, and purpose is
  what is absent". SELECTION_RULES R7: environment-agent co-development needs a stateful
  organism and a parameterised world family with a declared difficulty axis, "NEITHER EXISTS
  YET".

## 2. What was gathered today (30 papers, 8 repositories; grades in the ledger)

POET lineage, pinned:
  uber-research/poet  master 8669a17e = Enhanced POET; branch original_poet 0b40743d =
  original POET (the README calls it the legacy branch). Apache-2.0, NOTICE present, last
  push 2022-03-23. Needs fiber + neat-python + gym[box2d]. This answers TECHNE-18: the two
  algorithms are two branches of one repository, not two repositories.
  Precursors: minimal criterion coevolution (Brant and Stanley, GECCO 2017, DOI
  10.1145/3071178.3071186); Chromaria necessary conditions (Soros and Stanley, ALIFE 14).
  Siblings (unsupervised environment design): PAIRED 2020, PLR 2020, ACCEL 2022, the Jiang
  2023 and Samvelyan 2025 theses, Watts 2022 (a POET re-implementation framework, MIT).
  LLM-era successors that cite the open-endedness programme: Evolution through Large Models
  2022; OMNI-EPIC 2024 (LLM writes environments as code; Apache-2.0 repo pinned); Hughes et
  al. 2024 (the novelty + learnability definition); Darwin Godel Machine 2025 / ICLR 2026
  (archive of self-modifying coding agents, SWE-bench 20.0 -> 50.0 per its abstract; repo
  pinned, Apache-2.0, needs docker + model APIs); AlphaEvolve 2025 (white paper, no code);
  AC/DC 2026 (task-capability coevolution of merged LLM experts, ICLR 2026; POET-shaped, no
  POET citation on its abstract page); Group-Evolving Agents 2026; CODE-SHARP 2026.

ALife lineage, pinned:
  Tierra (Ray 1993 journal paper, DOI 10.1162/artl.1993.1.179); Avida (Ofria and Wilke 2004,
  DOI 10.1162/106454604773563612; platform already a fossil); Lenia (Chan 2019, Complex
  Systems; repo pinned, MIT, pure numpy); ASAL (Sakana 2024/2025, CLIP as the observer over
  lenia / boids / plife / plife_plus / plenia / dnca / nca_d1 / gol; Apache-2.0, JAX, GPU
  recommended); VLM-guided Lenia evolution (ALIFE 2025); Evolutionary ecology of words (IEEE
  ALIFE-CIS 2025); TerraLingua (2026, persistent LLM ecology, institutions and culture as
  observables); OpenLife (ALIFE 2026, six LLM agents with memory, tools and money for ~12
  weeks); Conversable Complexity (July 2026, LLM collectives as an ALife substrate with text
  traces) -- the last three are the "language model collectives as substrates" the directive
  refers to, and they are three months old or less.

## 3. The directive's claims, read as data

- "TransformerLens" is named as an evolutionary engine beside MAP-Elites. It is a mechanistic
  interpretability library for transformers. No source uses it as an engine. Flagged.
- "ALife is experiencing a renaissance fueled by language model collectives": supported by
  the 2025-2026 cluster above (ASAL, TerraLingua, OpenLife, Conversable Complexity, Sakana's
  ALife programme), all of which are recent enough that none has a replication.
- "POET is showing significantly more practical promise ... autonomous multi-agent research
  swarms": NOT FOUND as stated. No fetched source runs POET's paired-environment-with-transfer
  mechanism over an LLM swarm. The 2025-2026 results that do push models past benchmark
  ceilings (DGM, AlphaEvolve, AC/DC) are archive-based open-ended search with an LLM as the
  proposer and a fixed evaluator; they descend from novelty search / QD / the open-endedness
  programme (Clune, Stanley, Lehman), and AC/DC is the one that is POET-shaped (task and
  capability coevolve). The claim is a reading of that lineage, not a measured comparison.
- "ALife is notoriously difficult to steer toward concrete computational outputs": consistent
  with ASAL's own framing (manual design and trial and error as the historical burden) and
  with why ASAL and the VLM-Lenia paper add a foundation-model observer; it is an argument
  those papers make, not a measurement anyone has replicated on OEIS-shaped outputs.
- The table's POET column ("environment generated dynamically to match agent abilities",
  "quality-diversity") matches the papers. Its ALife column ("often unconstrained, survival
  mechanics") describes Tierra/Avida-style digital evolution, not Lenia or ASAL, where the
  objective is a target phenomenon or open-ended novelty under an observer.

## 4. Where each sits against Prometheus, stated once

  POET / UED             H4 (curriculum), Harmonia's design: 1.1 reference arm, no earlier.
  DGM / AlphaEvolve      HARD-3 territory (model-in-the-loop self-improvement; deferred by
                         doctrine until the closed-loop condition); HARD-2 gravity risk when
                         cited as "what works".
  ALife substrates       Theophrastus (computational ecology by CONTRAST cells) and Vivarium
                         (PEW) are the seats whose lane this is; Nyx holds Avida as a fossil.
  LLM-collective ALife   the operator's north star describes Prometheus itself as such an
                         ecology; these papers are competitors' framings of the same bet,
                         useful as data (HARD-2 permits that), three months old, unreplicated.
  Doctrine, verbatim:    "Success is not reproducing Lean, MOSEK, DreamCoder, Mathematica,
                         POET or any human-designed tool" (NORTH_STAR). Gathering POET is
                         allowed; adopting it as the engine is what the north star excludes.

## 5. What M3 can and cannot do with any of it

  runnable here      Lenia reference code (pure numpy) -- the cheapest ALife substrate for a
                     Theophrastus contrast cell if one is ever wanted; not attempted.
  not runnable here  POET (gym[box2d] needs SWIG + a compiler; fiber), Avida (C++ build;
                     already runs on M1/M2 as a fossil), DGM (docker), ASAL (JAX + GPU in
                     practice). M3 has no compiler and no virtualization (TECHNE-102).

## 6. Recommendation (Techne's stand; falsifiable)

Nothing to acquire beyond the pins until one of two consumers names a need:
  (a) Harmonia, when H4 reaches 1.1: original POET at original_poet@0b40743d is the
      reference arm the design names; the pin, licence and requirements are now recorded so
      that acquisition is a one-command act on a host with a compiler.
  (b) Theophrastus, if a contrast cell on an ALife substrate is wanted: Lenia@adfc5429 is
      pure Python and could be qualified on any host, including this one.
What would change the recommendation: a fetched source that runs POET's pairing-and-transfer
over LLM agents and reports a held-out gain surviving an ablation; or an H4 1.0 closure. What
would falsify section 3's "NOT FOUND": the operator naming the source the essay was drawn
from. Conflict of interest: this seat's acquisition command refuses POET today and I wrote
that refusal.

## 7. Not done

No PDF was read in full; abstracts, API metadata, READMEs and requirement files were. The
Evidence Wiki was not queried (its API port on M1 is closed to M3); this gather should be
submitted there by a seat that can reach it, or from M1/M2. No clone, no run, no wrapper.
