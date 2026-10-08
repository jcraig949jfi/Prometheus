"""PROP01 tree utilities: cut-site choice (preregistered) and descendant sets."""


def children_map(tree):
    ch = {}
    for s, p in zip(tree["site"], tree["parent"]):
        if p >= 0:
            ch.setdefault(p, []).append(s)
    return ch


def choose_cut(unit):
    """B = the earliest-diverging generation-1 site with >= 1 STRUCT (1) or CARRY (2) child; ties -> lowest index.
    Returns (site, tick it first diverged) or (None, None)."""
    tr = unit["tree"]
    ch = children_map(tr)
    info = {s: (g, t, ty) for s, g, t, ty in zip(tr["site"], tr["gen"], tr["ftick"], tr["type"])}
    cands = [(info[s][1], s) for s in tr["site"] if info[s][0] == 1 and
             any(info[c][2] in (1, 2) for c in ch.get(s, []))]
    if not cands:
        return None, None
    t, s = min(cands)
    return s, t


def descendants(tree, root):
    ch = children_map(tree)
    out, stack = set(), list(ch.get(root, []))
    while stack:
        x = stack.pop()
        if x in out:
            continue
        out.add(x)
        stack.extend(ch.get(x, []))
    return out
