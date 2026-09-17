# Provenance of migrated evidence

Origin: Claude Code session scratchpad `.../scratchpad/ac01/` (session 05a5464a-bd77-4711-8bde-7a383b1e104c),
written 2026-09-12 during the first-receipt critique, before any repository branch existed for AC-01.
Copied verbatim; nothing edited after copy. Python 3.12.10, numpy 2.2.6, Windows 11.

```
591e1a8b6503632378246b1e811b4d774ca866fce187b993b52c13e4f7551dbf  datalog_results.json
c6079bc66596ecabe48c961e565cc893532fc18f4a35afecb37a66eb84aa4ed3  probe_datalog.py
018d3811c665fe8f24143bda98e6f2577292504de36ec93228bfa93c04db5ae6  probe_rewrite.py               (symmetric variant, with introduce)
03f040017651556c1fa5ec86568c1a4707191ba5f09431894e86fac86085afca  probe_rewrite_directed.py      (directed variant, no introduce)
31e67542d7ea2fd602359c837666ff1ea37d60ce13b9b65361732d4eb2343856  rewrite_directed_results_L8.json
11ffff48ea2c152eff4e766465d8210defa801c9840cfabe070eaf900ccf69d9  rewrite_directed_results_L9.json
ec88657951c39e4d6abefba63026f9a0a3131830b55e3f65880467a1724a096c  rewrite_results_L7.json        (symmetric variant)
```

`probe_datalog.py` is self-contained: `python probe_datalog.py out.json` reproduces `datalog_results.json`
(seeded sampling; PYTHONHASHSEED-independent because states are integers).
`probe_rewrite_directed.py <L>` reproduces the directed results. The Phase A/B package under `universe/`
re-implements the directed variant with vectorised transitions and reverse-BFS distances; its L=8 and L=9
counts agree with these probe files (state counts, eligibility, max D).
