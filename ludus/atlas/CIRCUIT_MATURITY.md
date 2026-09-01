# Circuit maturity

Support is four separate counts. A larger count at the same evidence
class is never grounds for promotion.

## r0003 — **ABLATION_SUPPORTED**
- development: ['FLIP7', 'MARTIAN_DICE']
- repair: — | threshold: —
- prospective: ['INCAN_GOLD', 'CANT_STOP']
- untouched: ['INCAN_GOLD', 'CANT_STOP']
- **blocked at PARTNER_ROBUST**: partner spread of 1.0000 in FOUNDRY[gate=1,k=3,cap=4]
- Prediction registered in CYCLE_002 §8.1 before either prospective world existed; both returned 1.0000 and survived re-pairing. That is CROSS_WORLD evidence on its face. It is NOT promoted past ABLATION_SUPPORTED because PARTNER_ROBUST fails outright: the same circuit reads 0.0000 and 1.0000 in one FOUNDRY world depending only on its partner. A circuit cannot be credited as cross-world while its value is not yet a function of the world.

## r0007 — **EXECUTABLE**
- development: ['FLIP7']
- repair: — | threshold: —
- prospective: —
- untouched: ['INCAN_GOLD', 'MARTIAN_DICE', 'CANT_STOP']
- Pot-blind control. Reads the risk and ignores the stake; retained to show whether the stake matters. Controls are never promoted.

## r0010 — **EXECUTABLE**
- development: ['MARTIAN_DICE']
- repair: — | threshold: —
- prospective: —
- untouched: ['CANT_STOP']
- Baseline.

## r0011 — **EXECUTABLE**
- development: ['MARTIAN_DICE']
- repair: — | threshold: —
- prospective: —
- untouched: ['CANT_STOP']
- **blocked at IDENTIFIABLE**: sign reverses between two worlds sharing an interface; no registered prediction distinguishes the two cases in advance
- CONTAMINATION FLAG: written from the seat's own 'option preservation' vocabulary, not from data. Worst circuit in Martian Dice (0.2501, below the null circuit) and best in Can't Stop (0.9389). No prediction was ever registered for it, so its Can't Stop result is retrospective and cannot raise its rung.

## r0012 — **EXECUTABLE**
- development: ['MARTIAN_DICE']
- repair: — | threshold: —
- prospective: ['FOR_SALE (unbuilt)']
- untouched: ['CANT_STOP']
- **blocked at IDENTIFIABLE**: kill condition replaced after the fact; the replacement has not yet faced an untouched world
- Registered kill condition was MIS-SPECIFIED -- it named a reversal outside push-your-luck, and the reversal happened inside it. Replaced, not reinterpreted.

## r0014 — **EXECUTABLE**
- development: ['MARTIAN_DICE']
- repair: — | threshold: —
- prospective: —
- untouched: ['CANT_STOP']
- **blocked at IDENTIFIABLE**: no registered prediction
- CONTAMINATION FLAG: same 'spend capacity only when it pays' origin as r0011.

## r0015 — **EXECUTABLE**
- development: ['FLIP7', 'MARTIAN_DICE']
- repair: — | threshold: —
- prospective: —
- untouched: ['INCAN_GOLD', 'CANT_STOP']
- **blocked at IDENTIFIABLE**: unresolved collision with r0003
- Standing COLLISION RISK with r0003. Until a world separates them, one of the two may be a redundant name.
