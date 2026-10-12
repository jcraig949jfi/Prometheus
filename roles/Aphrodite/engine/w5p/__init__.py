"""W5P -- bounded representation promotion (Aphrodite Beta-03 E3). See W5P_DESIGN.md.

promote.py  the Promoted primitive, promoted-form terms, expansion, recognition, W5P instantiation, derivation
donor.py    donor_w5p (gtc.donor_g + promotion hooks + two-ledger cost meter), pluggable selection
harness.py  Beta-02-compatible job wrapper (b02._donor semantics)
tests/      test_w5p.py (pytest or `python -m w5p.tests.test_w5p` from engine/)
"""
