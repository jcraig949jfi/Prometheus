import pathlib
p=pathlib.Path('tools/kind_audit.py'); s=p.read_text(encoding='utf-8')
def rep(a,b):
    global s
    assert s.count(a)==1, a
    s=s.replace(a,b)
old_start=s.index('def audit_text(')
old_end=s.index('def flags(')
s=s[:old_start]+'''def _block(text: str, s: int, e: int, lo: int, hi: int) -> tuple[int, int]:
    """The citation's own text block, clipped to [lo, hi): its table/ledger cell when the line has 2+ '|',
    else its paragraph or list item. Hard-wrapped prose continues across single newlines; a blank line,
    a bullet/numbered item, a heading or a table row starts a new block."""
    ls = text.rfind("\n", 0, s) + 1
    le = text.find("\n", e)
    le = len(text) if le < 0 else le
    if text.count("|", ls, le) >= 2:
        cs = text.rfind("|", ls, s)
        ce = text.find("|", e, le)
        return max(lo, ls if cs < 0 else cs + 1), min(hi, le if ce < 0 else ce)

    def boundary(line: str) -> bool:
        return not line.strip() or bool(BLOCK_START.match(line)) or line.count("|") >= 2

    start = ls
    while start > lo and not BLOCK_START.match(text[start:text.find("\n", start) % (len(text) + 1)]):
        ps = text.rfind("\n", 0, start - 1) + 1
        if boundary(text[ps:start - 1]):
            break
        start = ps
    end = le
    while end < hi:
        ne = text.find("\n", end + 1)
        ne = len(text) if ne < 0 else ne
        if boundary(text[end + 1:ne]):
            break
        end = ne
    return max(lo, start), min(hi, end)


def audit_text(text: str, path: str = "<text>", index: Index | None = None, min_len: int = 8,
               scope: str = "block") -> list[dict]:
    """Every resolved C1 citation in text, flagged or not. Line numbers are 1-based in text.

    scope="block" (default): outcome terms count only inside the citation's own block (paragraph, list
    item or table cell) within +-WINDOW chars. scope="window": the whole +-WINDOW (W2-I behaviour).
    The true-kind exoneration (LOW) always looks at the whole +-WINDOW."""
    if min_len < 6 or min_len > MAX_HEX:
        raise ValueError(f"min_len must be in 6..{MAX_HEX}")
    if scope not in ("block", "window"):
        raise ValueError("scope must be 'block' or 'window'")
    index = index or load_index()
    out = []
    for m in _id_re(min_len).finditer(text):
        tok = m.group(1)
        cid = index.resolve(tok)
        if cid is None:
            continue
        meta = index.cells[cid]
        a, b = max(0, m.start() - WINDOW), min(len(text), m.end() + WINDOW)
        lo, hi = _block(text, m.start(), m.end(), a, b) if scope == "block" else (a, b)
        terms, wide, dmin = set(), set(), None
        for name, rx in OUTCOME_RES:
            for t in rx.finditer(text, a, min(len(text), b + 16)):
                if t.end() > b:
                    continue
                wide.add(name)
                if t.start() < lo or t.end() > hi:
                    continue
                terms.add(name)
                d = min(abs(t.start() - m.start()), abs(t.end() - m.end()))
                dmin = d if dmin is None else min(dmin, d)
        win = text[a:b]
        kind_named = bool(KIND_WORDS[meta["kind"]].search(win))
        sev = _severity(meta["kind"], terms, kind_named)
        out.append({
            "file": path, "line": text.count("\n", 0, m.start()) + 1, "token": tok, "cell_id": cid,
            "kind": meta["kind"], "wave": meta["wave"], "family": meta["family"],
            "flagged": int(bool(sev)), "severity": sev, "terms": "|".join(sorted(terms)),
            "terms_outside_block": "|".join(sorted(wide - terms)),
            "nearest_term_chars": "" if dmin is None else dmin, "kind_named_in_window": int(kind_named),
            "context": " ".join(win.split())[:420],
        })
    return out


'''+s[old_end:]
rep('''KIND_WORDS = {''','''BLOCK_START = re.compile(r"[ \t]*(?:[-*+][ \t]|\d+[.)][ \t]|#|\|)")
KIND_WORDS = {''')
p.write_text(s,encoding='utf-8',newline='\n')
