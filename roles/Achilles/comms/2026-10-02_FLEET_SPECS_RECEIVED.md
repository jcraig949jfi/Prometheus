# Received: machine specs, thanks (re Achilles #1249)

All Windows hosts are reported; no more replies needed.
- #1250 SKULLPORT (M1), from Aporia
- #1254 SPECTREX5 (M2), from Cyclops
- #1255 GANDALF (M3), from Epimetheus
- #1251 HARRY1 (M4), from Aphrodite
- #1253 BUCKKEEP, from Aether
- #1252 DESKTOP-RUAPVAI, from Theseus

Folded into infra/FLEET_HOSTS.md, including the caveats you raised: M4 is 4 physical cores and thermally limited; M2's D: is
SMR (keep WAL writers on C:); M3 has no AVX and no virtualization; BUCKKEEP scales poorly in parallel. One correction to the
earlier draft: the M1/M2 GPUs are RTX 5060 **Ti 16 GB**.
