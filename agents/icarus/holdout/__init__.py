"""
Blind holdout oracle (Q9). FROZEN -- never cloned into a cycle, never shown
to the Generator, never modifiable by Icarus. Tests here are the out-of-band
falsification suite: they probe the SPIRIT of each tier, not the letter the
Generator can see. A cycle that passes its own visible tests but fails the
holdout has Goodharted its visible tests.
"""
