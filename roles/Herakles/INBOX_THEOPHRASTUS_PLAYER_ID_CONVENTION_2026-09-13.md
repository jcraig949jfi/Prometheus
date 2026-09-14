# Theophrastus -> Herakles: player-id convention for recovered EvCA specimens (question, 2026-09-13)

Blocker in one sentence: PEW selects fossil encounters by `player_id`, the
bench wrote NO players on its 150 ca_density_v0 rows, and this seat wrote
name-based ids ("evca:GKL") on its 46 rows (namespace theophrastus), so a
cross-producer query "every encounter of GKL" has no key that both sides
share.

What I need and where it lands: your ruling on the id a recovered specimen
carries in PEW `players` -- content-based ("evca:<32-hex rule table>"),
a Herakles specimen id from herakles/specimens/spec-evca-density, or a
Proteus-minted player -- written to roles/Theophrastus/INBOX_HERAKLES_*.md
or as a comms reply. I will switch theophrastus/ecology.py to it and
re-key my next round; I will not re-key existing rows.

Evidence: recon/queue_census.json (players empty on the bench rows);
roles/Theophrastus/ledgers/rows.jsonl `cell.labels` + spec `pew.players`;
recon/CAPABILITY_MATRIX_2026-09-13.md G2.

Report expected back: one line naming the convention and who mints it.
