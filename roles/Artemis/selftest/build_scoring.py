"""Build blind scoring bundles (PREREG amendment 2, A2.6). Run only after executions end.
Reads worker reports, redacts ids and package-format cues, relabels runs with fresh random
labels (secret key kept outside the repo), writes RUBRIC.md verbatim from the frozen prereg.
usage: python3 build_scoring.py REPORT_DIR OUT_DIR SECRET_DIR
"""
import hashlib, json, random, re, subprocess, sys, pathlib
rep, out, sec = map(pathlib.Path, sys.argv[1:4]); out.mkdir(parents=True, exist_ok=True); sec.mkdir(parents=True, exist_ok=True)
prereg = subprocess.run(['git', 'show', 'a9d5f5f23:roles/Artemis/challenge/prospective/PREREG.md'], capture_output=True, text=True).stdout
rubric = prereg[prereg.index('## Outcome categories'):prereg.index('## Execution protocol')]
(out / 'RUBRIC.md').write_text("# Scoring rubric (frozen; verbatim from the preregistration)\n\n" + rubric)
REDACT = [r'\bFR-\d+\b', r'\bH-D\d-\d+\b', r'\bR-\d\d\b', r'\bArtemis\b', r'\bcurator\b', r'\bharvest(ed|er|s)?\b',
          r'work sketch', r'\bsharpen(ed|ing)?\b', r'\bSHARPENED\b', r'\bMATURE\b', r'\bRAW\b', r'\bchops?\b',
          r'\bbacklog\b', r'\bthread(s)?\b', r'\bpackage(\'s)?\b', r'\bbriefing\b', r'artemis-selftest/work/[^\s)`]*']
runs = sorted(p.name for p in rep.iterdir() if (p / 'REPORT.md').exists())
labels = [f'X{n:03d}' for n in random.Random(hashlib.sha256(b'artemis-scoring-labels').hexdigest()).sample(range(100, 1000), len(runs))]
key = dict(zip(runs, labels))
for r, lab in key.items():
    t = (rep / r / 'REPORT.md').read_text(errors='ignore')
    for pat in REDACT: t = re.sub(pat, '[redacted]', t, flags=re.I)
    (out / f'{lab}.md').write_text(f'# Report {lab}\n\n' + t)
(sec / 'SCORING_KEY.json').write_text(json.dumps(key, indent=1, sort_keys=True))
print(len(runs), 'reports ->', out, '| key sha256', hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:16])
