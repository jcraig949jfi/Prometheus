# NS-01 exclusion-engine qualification (run 07:50-08:00Z under supervise, DONE; criteria fixed in 39a1899e0)

QUALIFIED: false rejection 1/66 disguised witnesses (.015 <= .10); false acceptance 0/7 look-alike pairs (<= 1/7).
- The one false rejection: LinearEncode(stig_diffusing), distance .070 > TAU .05 from its source, class preserved
  (the random-feature decoder is not exactly invariant to an invertible linear mix of a 300-dim state).
- Look-alike pairs: all kept apart; register vs hidden carrier only .055 apart by distance (kept apart by class:
  the transplant rule). stig_moving vs stig_diffusing kept apart by distance (.435) but share the same rule classes.
- LIMITATION (resolution): at TAU .05 the behavioural signature COLLAPSES perfect memories (delayline = register =
  stig_static) and near-chance systems (nomemory = reservoir_fast). A purely behavioural signature cannot tell
  mechanisms apart when their task behaviour is saturated (perfect) or absent; such candidates will read as
  KNOWN_EQUIVALENCE whatever their internal organisation. Directive s5 ("familiar code may possess different causal
  behaviour") is therefore only testable here for behaviour that is NEITHER perfect NOR absent.
- Witness classes as measured (not as named): graph = M-UNREACHABLE + M-DECAY; phase = M-LINBLIND + M-INTERFERENCE +
  M-DECAY; sediment = M-INTERFERENCE + M-DECAY; rotreservoir = M-DECAY; reservoir_slow = viable; stig_static = viable.
