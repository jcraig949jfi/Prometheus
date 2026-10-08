# Literature anchoring for the LOCAL composition laws (2026-10-08; written before EXP-01 results)

- Ganguli, Huh & Sompolinsky (2008), "Memory traces in dynamical systems", PNAS 105:18970
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC2596211). Fisher Memory Curve (FMC): SNR of a past input in the
  current state of a linear system with noise. Normal networks: total capacity exactly 1; non-normal (hidden
  feed-forward) networks up to N. => spectral radius alone (C4-L-0001) cannot carry memory in non-normal
  substrates; the full one-step matrix composed by powers (C4-L-0003) is the local FMC.
- Dambre, Verstraeten, Schrauwen & Massar (2012), "Information processing capacity of dynamical systems",
  Sci. Rep. 2:514 (https://pmc.ncbi.nlm.nih.gov/articles/PMC3400147). Total capacity bounded by the number of
  linearly independent state variables; a memory-nonlinearity trade-off. => a LINEAR local composition is
  expected to fail where storage is nonlinear.

PREDICTION recorded before EXP-01 analysis (not a gate; used to read failure shapes):
L-0003 (local FMC) should do best on rnn (near-linear for small inputs) and worst where the stored trace is
carried by thresholds or all-or-nothing events: graph (threshold network with flips) and theseus_sediment
(clump settling / scour). If L-0003 instead fails on rnn and succeeds on graph/sediment, the linear-response
reading of its success is wrong.
