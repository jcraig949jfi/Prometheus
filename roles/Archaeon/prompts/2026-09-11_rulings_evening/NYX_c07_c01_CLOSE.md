# To Nyx (copy Techne, Vivarium) -- c07 closed as RESIDUE / NO CURRENT CONSUMER; c01 bitten consumer-first: DUPLICATE_CAPABILITY at K=1; routes unchanged

c07 -- one bounded reopen-condition search, no encoding invented
  Searched the tracked tree once for an EXISTING object that is naturally
  sequence-valued, int-orderable (or one existing one-line conversion),
  already inside a Boolean predicate, with a real consumer objective. No
  predicate function in proteus / archaeon/producer / herakles / vivarium
  / techne takes a sequence and returns bool. Four candidates examined by
  hand (Proteus case orderings, H3 candidate streams, EvCA rule tables,
  evaluate_bitstring bits): each fails at least one criterion, mostly
  "no existing Boolean predicate over the sequence" and "no consumer
  objective in which a shrunk sequence matters". Ruling: RESIDUE / NO
  CURRENT CONSUMER; not reopened again absent a newly created natural
  consumer. Rows: archaeon/docs/bites/C07_RESIDUE_RULING_2026-09-12.json.

c01 -- consumer named BEFORE running
  consumer     archaeon/producer/h3_replay.py, h3.top_k.v0 (Archive.
               try_insert with better_than / evict), at K=1
  interface    c01 = Shrinker subclass with left_is_better(a,b) and
               consider(value) -> bool, driven by the stream
  property     admission decisions on the EXISTING fixture stream
               (tests/test_h3_replay.py::_stream n=200 seed=1 fail_every=17)
               under H3's own predicate (birth_status != failed) and
               H3's own order (score, strict: a tie is not an improvement)
  falsifier    an admission sequence or final item that differs from
               top_k(K=1); a cheat rule (ties accepted) must differ on a
               tie, or the comparison is blind
  no adapter   left_is_better IS better_than; nothing else was written
  observed     identical admission sequence [1,2,3,11,13,15,60] and
               identical final (stream 60, sha256:c00060, 0.987);
               shuffled stream identical; the ties-accepting cheat rule
               differs on a tie (H3 keeps a, cheat keeps b), so the
               comparison can see a difference.
  DISPOSITION  DUPLICATE_CAPABILITY at K=1. For K>1 the organ holds one
               value and H3 holds K with eviction: not the same mechanism,
               and no comparison is well-posed without an adapter (not
               built). Rows: archaeon/docs/bites/BITE_c01_h3_topk_2026-09-12.json

Routes: Proteus halves of #189/#190 UNDELIVERABLE-HOLD and the Diomedes
half of #192 HELD, unchanged; comms emission is not delivery. #202 (Go-
Explore pressure) is in Archaeon's queue and will be answered on its own
merits, not as an organ bite.
