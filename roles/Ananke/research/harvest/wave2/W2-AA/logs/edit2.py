import pathlib
p = pathlib.Path("tools/kind_audit.py"); s = p.read_text(encoding="utf-8")
R = [
 ("                min_len: int = 8) -> list[dict]:\n    index = index or load_index()\n    recs = []\n    for q in iter_files(paths, exts, exclude):\n        recs += audit_text(q.read_text(encoding=\"utf-8\", errors=\"replace\"), _display(q), index, min_len)",
  "                min_len: int = 8, scope: str = \"block\") -> list[dict]:\n    index = index or load_index()\n    recs = []\n    for q in iter_files(paths, exts, exclude):\n        recs += audit_text(q.read_text(encoding=\"utf-8\", errors=\"replace\"), _display(q), index, min_len, scope)"),
 ("def summary(records: list[dict], index: Index | None = None, min_len: int = 8) -> dict:",
  "def summary(records: list[dict], index: Index | None = None, min_len: int = 8, scope: str = \"block\") -> dict:"),
 ("\"min_len\": min_len,\n", "\"min_len\": min_len, \"scope\": scope,\n"),
 ("    ap.add_argument(\"--min-len\", type=int, default=8)\n",
  "    ap.add_argument(\"--min-len\", type=int, default=8)\n    ap.add_argument(\"--scope\", choices=[\"block\", \"window\"], default=\"block\")\n"),
 ("audit_text(sys.stdin.read(), \"<stdin>\", index, a.min_len)", "audit_text(sys.stdin.read(), \"<stdin>\", index, a.min_len, a.scope)"),
 ("(*DEFAULT_EXCLUDE, *a.exclude), a.min_len)", "(*DEFAULT_EXCLUDE, *a.exclude), a.min_len, a.scope)"),
 ("summary(recs, index, a.min_len)[\"counts\"]", "counts(recs)"),
]
for a, b in R:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8", newline="\n")
