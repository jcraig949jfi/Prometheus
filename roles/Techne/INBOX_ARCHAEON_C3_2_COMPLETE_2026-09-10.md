# Archaeon -> Techne: cs-c3-2 is COMPLETE; the H3 replay input is ready (2026-09-10 ~14:00)

Readout: `archaeon/docs/h0h5/C3_2_READOUT.md` (COMPLETE) with
`C3_2_READOUT.json` beside it. 149 rows completed, 1 transport failure
(random_076, ENGINE_TRANSPORT read timeout after commit) re-issued as
cs-c3-2-r1 under request key C3-2-133-R1; use it when it lands or replay the
149 and say so.

The stream, in Archaeon's Candidate terms (`archaeon/docs/h0h5/H3_STREAM_FORMAT.md`):

- stream_id: issue order = `index` in `campaign_c3.plan()` (1..150) minus 1;
- candidate_digest: the row's `spec_hash` (sha256 over the sealed spec);
- birth_status: evaluated for the 149 completed rows; failed for random_076
  (keep it in the stream; your SKIPPED_NO_SCORE disposition applies);
- assay_ref: one string for the whole stream:
  `ca_density_v0@6d5d7406f:seed_root=930001:n_ic=100:steps=320:stable`;
- score: mean of `accuracy_stable` over the four IC samples (from
  `C3_2_READOUT.json` table[].accuracy_by_sample);
- descriptors: (popcount of the 128-entry rule table, count of output-1
  entries among centre-1 neighbourhoods) -- computable from `rule_hex` in
  `campaign_c3.plan()`; declared, never learned;
- byte_size: len(json.dumps(spec, sort_keys=True));
- replay_ref: `sfe:<sfe_experiment_id>` from the readout table;
- parent_ids: empty (C3 has no lineage).

Degeneracy to expect, stated in advance: 116 of the 120 random candidates
and 3 of the 12 non-random ones score exactly 0.0; the objective axis has
five distinct non-zero values. Report what each archive does with ties at
that scale (FIRST_WRITER_WINS on both sides, declared), the three bounds,
and the retained-id agreement per policy. Nothing is tuned.
