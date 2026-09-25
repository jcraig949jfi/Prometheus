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
