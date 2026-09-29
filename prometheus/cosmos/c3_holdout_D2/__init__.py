"""C3 holdout D2 (author: Nestor, M1 SKULLPORT): an OPAQUE successor to holdout D's hidden set.

D2 reuses the unchanged holdout-D family code (prometheus/cosmos/c3_holdout_D/medium.py). Only the
hidden evaluation set is new; it lives in this directory as ciphertext (hidden_D2.enc) plus a public
manifest (MANIFEST_D2.json). The plaintext, the salt and the key are NOT in any repository.

This package itself carries no secret and imports nothing from the family, so verify_reveal.py and
sealbox.py can be used by an independent checker. Modules that load the family (draw.py, runner.py,
selftest_D2.py) inherit the family's broker guard and also check COSMOS_BROKER=1 themselves.
"""
