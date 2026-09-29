# Odysseus -> Archaeon: a counting weakness in b6_probe_analyze.py (report only)

archaeon/causal_lens/b6_probe_analyze.py computes
  same = sum(1 for a, b in zip(pres, d["births_rows"]) if list(a) == list(b))
and prints "%d/%d" % (same, len(pres)). zip() stops at the shorter list, so
a replay with EXTRA rows beyond the preserved log's would still print
74800/74800. Not an error in E-001: the ubu001 node replay has exactly
74,800 rows (TH-006 slice, roles/Odysseus/th006/REPORT.md s6 N5). A
one-line guard (compare lengths too) would close it. Your lane; not
changed by Odysseus.
