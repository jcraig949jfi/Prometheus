# Blind-lane registry

Part of programs/selective_irreversibility/ (README.md: writing rules,
directive path + hash). Append-only.

Blindness is a MEASUREMENT, not a label (README.md, Prior exposure).

Per lane: the probe terms and paths (frozen before any probe is run),
the probe command and SHA it ran at, hits, whether the seat's boot reads
README.md, the date of first exposure, and a verdict:

    BLIND             probe run, zero exposure, boot path does not reach the essay
    UNVERIFIED_BLIND  no probe run yet
    EXPOSED           exposure found; the lane may still be useful, but not as blind evidence

A blind lane's artifacts are tested against the law only AFTER it has
produced them, under its own prior charter (s5).

---

### 2026-09-25T16:30Z Aporia[m1-cb5a6069]
File created (skeleton). No entries yet.

### 2026-09-25T16:45Z Aporia[m1-cb5a6069]

PRELIMINARY EXPOSURE PROBE, M1 seats. CAVEAT: the probe terms were NOT frozen before it ran. So
this entry is a scouting read, not the registry measurement the header requires.
  terms   git grep -il -e "selective irreversib" -e "selective-irreversib", origin/main 0a9f5614d
  hits    roles/Nestor 0, roles/Ananke 0, roles/Atlas 0, roles/Cosmos 0, roles/Harmonia 0,
          roles/Techne 0, roles/Nyx 0, prometheus/ananke 0, prometheus/cosmos 0, atlas 0,
          primordial 0. Local worktrees nestor-s1-forensics, ananke-base-role, atlas-base-role: 0.
  boot    these seats boot via roles/base-role/README.md, which does not reach root README.md
          (observed). Root README.md:60 links the essay, so any seat that opens README directly
          is exposed.
  limits  zero grep hits is not blindness: the search misses paraphrase, operator chat, and a
          seat that read the essay without writing about it. Every M1 lane above is
          UNVERIFIED_BLIND. Nestor, Ananke and Cosmos are DIRECT lanes under s5 in any case.

### 2026-09-25T18:07Z Cyclops[m2-e8056938]
PRELIMINARY EXPOSURE PROBE, M2 seats. Same caveat as Aporia's M1 entry: the terms were not
frozen before the probe ran, so this is a scouting read, not a registry measurement.
  terms   git grep -il -e "selective irreversib" -e "selective-irreversib", origin/main fbe4d8071
  hits    roles/Aether 0, Aether/ 0, roles/Bellerophon 0, prometheus/z80atlas 0,
          prometheus/toolbox 0, roles/Archaeon 0, archaeon/ 0, roles/Daedalus 0,
          roles/Vivarium 0, roles/Aphrodite 0, roles/Cosmos 0, roles/Hephaestus 0, roles/Nyx 0.
          roles/Ensorain 1 (prompts/2026-09-24_foundry_directive/01_...verbatim.md)
          -> Ensorain EXPOSED since 2026-09-24.
          roles/Crius 2 (journal/2026-09-24.md; prompts/2026-09-24_post_closure_essay/)
          -> Crius EXPOSED since 2026-09-24.
  candidate BLIND lane: the Bellerophon Z80xAtlas coupling campaign. Its code and plan were frozen
          2026-09-24, before this directive existed, and its running process reads only its
          frozen workdir. It is still UNVERIFIED_BLIND: Bellerophon's seat sessions may have seen
          README.md:60. A frozen, running process cannot absorb new objectives, though, so the
          campaign's ROWS are blind by construction for this segment. That holds only while
          nobody amends the campaign with hypothesis-derived terms.
