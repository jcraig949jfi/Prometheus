"""prodledger -- production conserved-risk admission ledger + cryptographic seal.

Mission: G9a/G9b/G14 productionization and G15 hostile qualification.
The ledger is an append-only, hash-chained, event-sourced state machine:
state is a pure fold of the log, so there is no debit/record gap for a crash
to fall into, and replay is deterministic byte-for-byte.

  CONSERVED-RISK INVARIANT (per namespace, at every valid history prefix):
    unreserved + sum(open-family remaining reservations) + purchased == BUDGET
  where purchased = sum of irrevocable 1/K admission-risk purchases.
  Scientific BUDGET = ALPHA_LIFE = 1/10, permanent. Purchases are NEVER
  refunded. Unspent reservations are releasable. Calibration is a separate
  pool with a separate record type and NO migration path.

FINAL RULE (mission): in a deterministic substrate, "not yet observed" is
not a seal. Evidence is sealed only when some indispensable information
required to derive it did not exist until after the hypothesis paid for the
right to look. Here that information is the public beacon value of a round
fixed BY RULE strictly after the external anchor of the registration commit.
"""

LEDGER_VERSION = "prodledger-1.0"
ALPHA_LIFE_NUM, ALPHA_LIFE_DEN = 1, 10       # 0.1, exact
CALIB_BUDGET_NUM, CALIB_BUDGET_DEN = 1000, 1 # calibration pool (separate currency)
K_MIN_SCIENTIFIC = 1000
K_MIN_CALIBRATION = 100
