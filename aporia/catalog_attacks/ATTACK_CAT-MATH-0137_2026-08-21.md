# ATTACK CAT-MATH-0137 — Agoh-Giuga full conjunction (re-authored spec, ELENCHUS-SOUND)
Date: 2026-08-21 (Aporia P68) | Code: attack_0066_0137.py | Data: attack_0066_0137_results.json
History: the ORIGINAL spec was REJECTED (Korselt half missing; four demonstrated false
alarms); this attack executes the re-authored full conjunction the reviewer verified.

Pre-stated readings: ZERO-HITS + ALARMS-EXCLUDED (each cross-checked against the raw
statistic) / any hit = instrument-bug-first at extreme prior.

Result: composites n <= 1e7 satisfying squarefree AND (for all p|n: p | n/p-1 AND
p-1 | n/p-1): NONE (10s, spf-sieve factored test). The four Giuga-half false alarms
{30, 858, 1722, 66198} each FIRE the half-condition and are EXCLUDED by the full
conjunction; raw statistic sum k^(n-1) mod n cross-checks reproduce the reviewer's
values exactly: 15/429/861/33099 vs required 29/857/1721/66197.

NOT claimed: nothing about Agoh-Giuga's truth (range far inside literature bounds);
the product is the certified conjunction instrument + the demonstrated exclusion of
the rejected spec's false-alarm class.

Trace-vector: problem_id CAT-MATH-0137 | operations [spf-factored-conjunction,
false-alarm-exclusion-crosscheck, raw-statistic-verification] | kill_pattern none |
residue: a rejected spec's false alarms become the re-authored spec's TEST FIXTURES —
rejection evidence is calibration material, never waste
