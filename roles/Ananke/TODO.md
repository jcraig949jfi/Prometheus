# Ananke TODO

Currency: 2026-09-25T00:10Z (from date -u). Closed items are deleted with the closing
commit and date, purged after 24 h (base role s7).

Closed 2026-09-24/25: PTE built, preregistered, launched, completed;
A0 analysis (c2f81c273); report + packet (this commit).

- [ ] PTE-C1b PREREG: fresh-seed replication + fingerprints for the
      delay-line HOLD memory (4ab2ba01) and self-modifying MAJ (0a23398f,
      f6b623cd)
- [ ] PTE-C2 PREREG (ANANKE-26) with the amended boundary criterion and
      ablation-fingerprint labels
- [ ] Answer Kairos/Elenchus reviews when they arrive
- [ ] FLIP zero-comm twin census rerun (ANANKE-27)
- [ ] c1b_run.check_release: catch TypeError beside ValueError for created_at
      (Aporia #706, optional; do at the next code touch, which forces a v3 re-freeze)
