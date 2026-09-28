# G2 fresh set: seed record (Amendment C9 s5(c)-(d)). The SHA of the commit that adds this file is the fresh-set seed

- **Nestor's tracer, re-frozen v2:**
  * commit fb1c322cbc0cc157e50be70c9b4ab3234f865e5d;
  * TRACER_FREEZE.json sha256 (LF) af5ec3dabd62bb025dfdd263c7faa42d460772b71ae17ef931ff5ea86621b19a, verified by Archaeon;
  * z8shadow.py b391ebc5e4910d88b9701ddbd9cdaac4f2979cdb9fa4e4cb9f60f58f75b72ba9;
  * run_production.py c31cca76b7458dfb048c6b4d895935926353021919501185ef27ab0daf4c42c4.
- **Reference tracer:** unmodified since 3757111de; ref_tracer_npe.py sha256 (LF)
  2851bcdb6cc9a074db3b0338b663c1dec6b533a22b2e34c0cb522ac69de2a4e2.
- **Generator:** archaeon/attribution/probes/npe_fresh_set.py, sha256 (LF) c6ac358fc552b6a6f6b62932fb7f605ea0d2974f4e518798338cd16f1434ffcf. Committed before this record.
- **Fixture pack:** unchanged (npe_fixtures.py 25c8507e..., ARCHAEON_ADDITIONS.json 1753023c...).
- **Comparison:** v4 s4.3 raw, per class, >= 0.995. The C9 s5(a) forms are native in both tracers; there is no canonicalizer.
  * Set A: 300 interactions, before write-back.
  * Set M: 100 interactions, after write-back. MUTATION is reported as its own class.
- **ctrl_deps_slice (S3):** secondary and not gated. D5 is traced by both sides.
