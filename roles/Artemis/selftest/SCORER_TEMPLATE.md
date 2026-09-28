You are an independent scorer. You will read {N} short research reports and code
each one against a fixed rubric. You know nothing else about these reports and
must not look for anything else: do not read any repository, any other file,
or any message board. Use only the files named below.

RUBRIC: {DIR}/RUBRIC.md (read it first; it is frozen and is the only standard).
REPORTS: {LIST}

For EACH report, decide:
  primary      -- exactly one of ID, FP, ED, PR, NU, KN, UR (definitions in the rubric)
  consequential -- yes or no, using the rubric's CONSEQUENTIAL definition exactly
  confidence   -- high / medium / low
  reason       -- one sentence citing what in the report decided it
"[redacted]" marks words removed to keep you blind; ignore it.

Write your codes, one JSON object per line, to {OUT}:
{"label": "X123", "primary": "..", "consequential": "yes|no", "confidence": "..", "reason": ".."}
If writing the file fails, put all lines in your final reply. Final reply: the
count per primary category and per consequential value.
