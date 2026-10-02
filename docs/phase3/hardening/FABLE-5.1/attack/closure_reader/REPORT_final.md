# Report of the closure reader on version three

Verbatim, as it was returned.

3 HTML entities put in by the notification wrapper were turned back into their characters. Nothing else was changed.

---

```
FINAL CLOSURE READ -- FABLE-5.1 hardening package, version three

Not ready to commit: 1 blocker (fire_test.py cannot write its receipt as it
stands), 4 majors.
Worktree untouched; all runs on copies in
C:\Users\jcrai\AppData\Local\Temp\claude\F--prometheus\3815a3b9-a31a-46a9-be9d-0e7abfa3cbf8\scratchpad\verify5\
Abbreviations: D1, D2, D3; RM = 00_README.md; HR = harness\README.md;
AR = attack\README.md; CH = check_hardening.py; FT = fire_test.py.
A1 = RESPONSE_1; B = ASTRA's report; B-val = its VALIDATION.md; C1..C6 = package files.

1. CLOSURE TABLE
N0   NOT ASSESSED  manifests, excluded by the brief
N1   CLOSED   D1:93-96, D1:132-134 (but see m8)
N2   CLOSED   D1:317-324, D1:343-344, D2:289-293, RM:46-48
N3   CLOSED   D2:348-351, D1:489-490
N4   CLOSED   audits.py:218-249 holds 26 rows = 26 receipt cells; audits.py:294-296
              reads bits and guards; BITS PASS, 4 yes 5 no; no reuse answer
N5   CLOSED   D3:104-110, HR:53-56, D1:575-577, D2:154-158. Probe re-run on a
              copy: 167 / 165 / 159 / 6; I read the six survivors, none alters a verdict
N6   CLOSED   meta.py:793-904, test_harness.py:105-106, D3:524-525
N7   CLOSED   torture.py:183-216; xor of last two FAIL at gaps 6 to 20; an
              unfitted view gives INDETERMINATE; bit3 pinned
N8   CLOSED   search.py:160-179, 213-218; cherry-picked null FAIL both ways;
              distance 0 FAIL (residue: m5, m6)
N9   CLOSED   retain1.py:83-86; healing observer FAIL; hidden field pinned
N10  CLOSED   rulers.py:26, 128-129; of 17 alphas tried only 9.5e-7 and 1e-6
              pass; of 13 weakest rates only 0.935 and 0.9375; D2:424-435 (residue: m4)
N11  PARTLY   RM:109 "six tables" (eight parsed); RM:111 "whole text"
              (whitespace is collapsed). See M1, m1
N12  CLOSED   registration.py:46-67, D2:377-383; pinned (residue: m7)
N13  CLOSED   D2:307-336, D2:758-764, D3:432-466, audits.py:261-264
N14  CLOSED   D1:302-306, D2:247-259
N15  CLOSED   D1:408-409, 449
N16  CLOSED   D3:95-97, AR:56-59
N17  CLOSED   RM:126-138
N18  CLOSED   D2:220-222
N19  PARTLY   D3:65, D1:566 "five gates": G5.neutrality computes it too
              (rulers.py:100-101); five have a registered case
N20  CLOSED   RM:49-50, D1:165-166
N21  CLOSED   D1:392-393, D1:122-123, 210-211
N22  CLOSED   RM:87-88, D2:191-192
N23  CLOSED   D1:296-297, RM:53-54
N24  CLOSED   D2:269-270 (reproduced: 4.058 against 4.046 at 4,000 lives)
N25  CLOSED   registration.py:85-86, D3:235-239, torture.py:172
N26  CLOSED   audits.py:152-155, claims.py:137-138; the seed-per-episode cell
              still FAILS, now stated (D3:204-205)
N27  CLOSED   pinned: meta.py:832-836, 851-853
N28  PARTLY   D3:14-15, 172-173: the 7 INDETERMINATE cases (clock tick, 64
              episodes, 49 of 64) still count among "215 cases broken on purpose"
M6   CLOSED   D1:127-128, 257-258 (but see m13: my wording, and it misleads)
M9   CLOSED   D1:165-166
M19  CLOSED   D1:519-520
M22  CLOSED   as N7
M27  CLOSED   as N8
M29  CLOSED   as N4
M30  CLOSED   pinned (meta.py:873-875, D3:570-571)
M31  CLOSED   D2:629-635; hash and custodians stated as limits (meta.py:892-903)
M32  PARTLY   fitted figure is labelled; at first sight 12 of 26 fresh changes
              pass the 103 tests (M3)
M42  CLOSED   D2:702, 713-714
M44  PARTLY   words are held by the pins only (M1, M4)
Second reader 32-42, 45, 46: CLOSED. 43: PARTLY (m9). 44: "four groups"
closed; manifests not assessed.

2. DEFECTS STILL OPEN OR NEW

BLOCKER
X1  FT:179-182, CH:323-325. fire_test.py fails its own baseline, pins or no pins.
    - CH runs the mirror's copy of check_review.py; that file calls
      git -C <mirror root> (check_review.py:405-406), which is no repository.
    - Four prereg checks fail, n_review becomes 0, and two checks fail:
      "statements 01...: checker with 0 checks" and "record: 85 defects".
    - Reproduced with PINS filled and placeholders removed. No receipt is written,
      so the fire line (RM:116) and CH:412 cannot be met.
    - Fix: at CH:323 run pathlib.Path(GIT_ROOT)/"docs/phase3/review/FABLE-5.1/check_review.py"
      with cwd=GIT_ROOT.

MAJOR
M1  CH:152-153, 176-177; RM:111-113; FT:8-9. The pins do not freeze whitespace.
    - Two whitespace-only edits to D1:116-119 pass all 55 checks with the pins on:
      B's cell "days 10 to 15; the simple" moved under A, and "retire defer" put
      on one side.
    - In the two-column tables the column is the attribution. "Any change is
      caught, by construction" is false.
    - Fix: pin the raw LF text.
M2  D2:330-332. "the package's kit registers both of those as negatives for
    reuse of built parts".
    - C registers no answers and names no reuse claim. C1:228-238 lists them as
      counterfeits of nested improvement; C3:43 says the verdict is claim-specific.
    - D1:460-462 says so itself. The registration is yours (audits.py:268-279).
    - Fix: "my kit table (section 12) registers both".
M3  HR:69, D3:104-110. First sight on version three: 12 of 26 fresh one-line
    changes pass the 103 tests.
    - rulers.py:119  impostor blocks may repeat the first block
    - rulers.py:194  a physics with no known answer counts toward three
    - torture.py:174 first step after the cut not compared
    - torture.py:187 clock table sees two bits (no world the harness can build
      shows the difference)
    - audits.py:43   two arms with one series allowed
    - claims.py:126  setting hash depends on key order
    - stats.py:113   bound of 0 or 1 accepted
    - rulers.py:114  empty panel not refused
    - search.py:170  founders compared as sets
    - rulers.py:151  impostor judged on 48 seeds
    - torture.py:149 earlier episode on the same seed
    - registration.py:34 top count of a verdict table unchecked
    - Written after reading the gates and half the test file.
    - Fix: a case for each; quote 12 of 26 at HR:69.
M4  FT:39-89, RM:115-116. The fire figure is fitted, like the mutation figure was.
    - 32 of the 59 plants are "numbers that the checker rebuilds".
    - Result: 48 of 59 without pins, against 3 of 26 for plants I chose and
      35 of 80 for plants sampled by rule.
    - Fix: quote it by kind (word 2 of 9, attribution 1 of 3) with a figure
      from plants you did not choose.

MINOR
m1  RM:109, CH:18 "six tables": eight are parsed (CH:732-803). Fix: "eight".
m2  FT:100-101. The attribution plant is caught by the 80-column form check.
    Re-wrapped, it is caught only because the displaced quote has no other use.
    Two B sentences given to the package (D1:187-188, 205) pass. Fix: wrap the
    plant; add one that reuses a twice-used quote.
m3  FT:149 overwrites HARDENING_GIT_ROOT with its own root, so a copy cannot
    run it. Fix: os.environ.get first.
m4  D3:230-233 "The gate needs ... nine blocks ... six thresholds".
    rulers.py:116-118 needs only non-empty ones: a perfect "weak" positive, two
    thresholds and one block PASS. Fix: check the panel's shape or say
    "the fixture holds".
m5  search.py:170 compares founders in order: the registered founders reported
    in another order FAIL (a sound report refused). registration.py:128 sorts.
    Fix: sort.
m6  search.py:180-184. A discovery on founders registered because they hit
    passes: 128 of 128 at exact reach 0.271. Only the null is held against
    exact reach. Fix: compare, or pin.
m7  meta.py:366, registration.py:46-67. A registered sound case has
    design_seeds=[] ("no design runs were made") and 480 design units. Fix:
    BLOCK when design_n > 0 and no design seeds.
m8  D1:93-96. B's row lost its executed consistency check (B-val:12-19, 38-48)
    while A keeps "a checker with 72 checks". Fix: add it back.
m9  D1:17-18 "PROMISES NO DETECTOR". B:65-66 says no "universal depth
    detector"; B:486-487 says what a detector should distinguish. Fix: restore
    "universal".
m10 D1:588-590 "AGREED BY ALL THREE ... one fresh confirmation". A names none
    (A1:1164-1202 has gates and registered W1 predictions). Fix: "B and C".
m11 D2:769-771 "AS THE PACKAGE: ... event store; ... no automatic promoter; no
    single score". Not in C (C2:85 wants promotion as a function of facets).
    They are B:663-670, and D1:430-431 says C left the scalar rule out. Fix:
    credit B.
m12 D2:452-455 "AS THE PACKAGE AND B ... with a margin". The margin is B's only
    (B:119-122; D1:427). Fix: say which part is whose.
m13 D1:127-128, 257-258 "seven carry a quantity, two a day" reads as 7 + 2 = 9.
    Reversals 6 and 9 (A1:1317-1324, 1335-1337) carry neither and are in words,
    like B's. My round-two wording. Fix: "seven carry a number, two of them a
    day; two are in words".
m14 D1:333-335 "the attack is new here". C6:5, 14-16 asks reviewers to attack
    the gates and add mutants; D1:412-414 says so. Fix: "making it a condition
    is new here".
m15 D1:312-313 "Its fixture experiment ends:". One more sentence follows
    (B:611-612). Fix: "says".
m16 D3:106-108, HR:53-55. "165 run, 159 noticed" counts 17 repeated edits: 148
    distinct, 143 noticed, 5 equivalent (mutation_probe.py:453). Fix: give both.
m17 N19 and N28 residues, as in the table.

3. COUNTS
- fire_test.py: 59 planted; 59 caught with pins; 48 without. This needed two
  scratch changes (X1, m3); as it stands it stops at the baseline.
  By kind without pins: number 32/32, pinned number 0/2, quote 3/3,
  attribution 1/3, table 7/7, word 2/9, form 3/3.
- My plants, --no-pins:
  chosen after reading the checker: 26 planted (12 digits, 14 words), 3 caught
  (3 digits, 0 words).
  sampled by rule, fixed seed: 80 planted, 35 caught (numbers 25/40, "not"
  removed 5/20, verdict word swapped 5/20). Eight of the 15 missed numbers are
  cross-references.
- With pins on: 2 whitespace-only plants, 0 caught.
- README section Checks against the code: Form, Sources, Quotations, Receipts
  true. Numbers: "six" is eight. Pins: whitespace is collapsed. Fire line:
  cannot be produced until X1.
- Fairness: about 310 attributed statements checked (D1 about 215, D2 about
  100); 9 not supported (M2, m8 to m15). 58 quotations, all verbatim, each read
  in context.
- Fresh one-line changes: 26; 12 unnoticed.
- Closure: N1-N28: 25 closed, 3 partly. Eleven M items: 9 closed, 2 partly.

4. NOT CHECKED
- replay_attack.py not re-run this round.
- Second reader's items 1 to 31, except where they overlap mine.
- Whether attack\closure_reader and attack\second_reader files are
  byte-identical to what was returned.
- B's README, review packet and reviewed_findings (read B's report and
  VALIDATION.md only); the Downloads archive.
- D3 against the sources, beyond item 33 and the fixture list.
- Manifests, pins, placeholders, .gitignore (excluded). Readability and length.
- No fresh attack gate by gate; the escapes above were found in passing.

FOUND SOUND
- 103 tests pass on a copy (8.5 s).
- run_harness.py regenerates its receipt identically, timestamp apart.
- check_hardening.py in place: 49 checks, 1 failed (the placeholder).
- Second reader's 32-42, 45, 46 applied.
- Falsifier 6 can now fire.
- The class and the control of world two are as stated.
```

Scripts and outputs are in the scratch folder above; `out_p30.txt`, `out_p32.txt`, `out_plants_chosen.txt`, `out_plants_random.txt` and `out_fire_run.txt` are the ones to open first.
