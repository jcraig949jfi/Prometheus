"""The sealed holdout. Engineered separation:

- the family module (well.py) refuses to import unless COSMOS_BROKER=1, which only the
  broker subprocess sets;
- sealed_spec.json (worlds, nonce) is written once by seal.py and its sha256 is the
  commitment quoted in the preregistration; the broker refuses a spec whose hash differs;
- the miner, sampler, adversary and pipeline may not import this package (AST test);
- the broker only adjudicates a law whose freeze hash is recorded in the ledger, and
  writes its predictions (and their hash) to the receipt chain BEFORE running any D world.
This package's __init__ imports nothing from well.py.
"""
