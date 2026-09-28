# G2 fresh set: comparison declaration, committed BEFORE either sealed output is opened

**Sealed outputs** (sha256 of the uncompressed jsonl):
- reference 9fd3bc4486ba8dc5445da7d1d1db2f26eae9765365cbaee3db4ff5a6fb90eeb5 (#853);
- Nestor v2 c6aa5569a43321526e761904a158871f300b616500e3fedfbc8c9cad084f8e75 (#858).

**Known before opening: the MUTATION draw-index encodings differ.**
- Reference: ["M", side, draw, pos, old_label], where draw = the RNG-call index across the whole write-back, at the random() call.
- Nestor: ["M", [k, side, call], old_label], where call = the index within that half's _mutate, at the randrange().
- The spec (v4 s1 "MUTATION(draw index, old_label) at the RNG draw"; C6 E) does not define the index. This is category (1), a
  spec ambiguity, found BEFORE the exchange.

**GATE (unchanged): v4 s4.3 RAW**, per class, >= 0.995, on the data label and on addr, ctrl and exec.
- Set A and set M are reported separately. Classes: written_self / written_other / written_perf_none / unwritten.
- In set M, MUTATION loci are compared RAW like every other locus. Because of the encoding gap, a raw MUTATION disagreement is
  expected on every mutated locus. If it pushes an M-set class below 0.995, set M FAILS, with category (1). That is repaired by
  a spec amendment defining the index, a re-freeze, and a FRESH M set. No canonicalization is applied to the gate.

**Declared DIAGNOSTICS** (not gates; they cannot rescue a gate):
- (d1) set-M classes restricted to NON-mutated loci;
- (d2) the MUTATION class compared on the spec-defined content: mutated flag, side, pos, and old_label (raw);
- (d3) ctrl_slice (secondary) per class;
- (d4) performer and store_by per class.
