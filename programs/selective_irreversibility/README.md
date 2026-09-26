# Selective Irreversibility -- shared canonical program record

Currency: 2026-09-25 (skeleton, Aporia[m1-cb5a6069]; location agreed with
Cyclops[m2-e8056938] in comms #579 / #580).

Stewards, peers, neither subordinate (directive s0, s14):

    Aporia   M1 (SKULLPORT)   roles/Aporia/
    Cyclops  M2 (SPECTREX5)   roles/Cyclops/

This directory is the ONE record the directive's s14 asks for. There is no
M1 copy and no M2 copy of the hypothesis. If two versions exist anywhere,
this one wins and the other is the defect.

## The directive (cited, never re-transcribed)

    path    roles/Cyclops/prompts/2026-09-25_selective_irreversibility/
            01_OPERATOR_DIRECTIVE_verbatim.md
    sha256  f0dd0599cbf624847460eccac057c46798a808c9021770b33af00382f85fce4a
    commit  608b672d5 (Cyclops received it first; it is the charter of both)
    verify  git show origin/main:<path> | sha256sum

Section numbers used anywhere in this directory (s1 ... s16) are that
file's numbering. The candidate law is its s1 text, byte for byte. Nothing
here paraphrases it. A paraphrase is how post-hoc retreat starts (s12).

## Prior exposure (read before BLIND_LANES.md)

The hypothesis was public inside the fleet BEFORE this program existed:
docs/essays/2026-09-23-selective-irreversibility.md (1ba514fce, the
operator's verbatim note), linked from README.md:60. So no seat is blind by
default. Blindness is measured per lane in BLIND_LANES.md.

## Files, one per s14 item

    HYPOTHESIS.md          pointer to s1 + frozen conceptual version (Harmonia, s12)
    AMENDMENTS.md          dated, append-only; each amendment cites a ruling
    FALSIFIERS.md          what result damages the law, per countermodel A-D (s4)
    PORTFOLIO_MAP.md       engine -> class (DIRECT / BLIND / OBSERVATION, s5) -> host
    BLIND_LANES.md         blind-lane registry with measured exposure
    EXPERIMENTS.md         running and queued, with frozen/prereg pointers
    RESOURCE_CONFLICTS.md  per host, per resource, who yields
    DEPENDENCIES.md        cross-engine and cross-machine
    ANOMALIES.md           counterexamples and anomalies, surfaced immediately (s13.12)
    DISAGREEMENTS.md       both positions + discriminating evidence (s14)
    RULINGS.md             operator rulings, verbatim or cited by hash
    memo/                  the joint first portfolio memorandum (s15)

## Writing rules

1. APPEND, NEVER REWRITE. Every entry starts with a line
   `### <UTC timestamp> <Seat>[<instance tag>]`. No steward rewrites a whole
   file or edits the other's entry. A correction is a new dated entry that
   cites the one it corrects.
2. EVIDENCE, NOT CONCLUSIONS (s13.10). Every state claim carries its source:
   a SHA, a path, a comms id, or a command and when it was run.
3. A NULL IS A NULL (s13). No entry records a null as support.
4. FROZEN CONTRACTS ARE CITED, NOT RESTATED. An experiment's prereg is linked
   by path + hash. This directory never re-words a frozen contract.
5. ASCII only, LF, so the hashes here equal the git blobs.
