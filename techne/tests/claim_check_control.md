Control document with KNOWN defects.

1. A symbol that does not exist: `techne/lib/mahler_measure.py::_verify_mahler_mpmath`
2. A symbol that DOES exist:     `techne/lib/mahler_measure.py::mahler_measure`
3. Bad arithmetic: the score was 7/8 = 0.500 on that population.
4. Good arithmetic: the score was 4/8 = 0.500 on that population.
5. A missing file: `techne/lib/does_not_exist_anywhere.py`

<!-- POSITIVE CONTROL for techne/scripts/claim_check.py.
     Expected: exactly 3 issues -- one UNRESOLVABLE SYMBOL, one UNRESOLVABLE FILE, one RATE
     MISMATCH -- and NO issue for the real symbol or the correct arithmetic.
     If this document stops producing exactly that, the checker is broken and its verdicts on
     real reports must not be read. Cycles 049-059: six of seven bad measurements were caught
     by implausibility rather than by a guard; this file is the guard for this instrument. -->
