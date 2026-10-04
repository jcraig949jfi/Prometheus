# S1 contract amendment v1.0.3 (CPU cap, operator decision OP-4)

Amends contract v1.0.2. Written by Palamedes[harry1-679179c6], 2026-10-04. STATUS: ADOPTED; contract.json caps are updated
by C-004-T025 in the same commit as test_ledger.py (test_caps_read_from_the_real_contract pins the live cap, so setting it
here first would turn main red -- the T021 pattern).

Authority: C-004-OP4 (operator, 2026-10-04: "You can go past the cap by 4x").

U1  caps.cpu_minutes: 30 -> 120. All other caps unchanged.
U2  caps.accounting: "120 CPU-minutes total; an estimated 40 CPU-minutes of unmetered development and verification (before
    ledgered launches began) is booked against it, leaving 80 CPU-minutes for ledgered validation launches (T020, S3, S4);
    every validation launch passes --ledger; mutation children are charged; stop at the first exhausted cap."

Why 40: an estimate, not a measurement. Recorded receipts give ci runs of 8 s to 240 s per packet, T024's author reported
about 14 CPU-minutes of development, and Palamedes ran several end-to-end checks of 50-80 s. Booking it keeps the slice
inside the cap under the strict reading of plan s6 ("charge ... analysis and confirmation attempts").
