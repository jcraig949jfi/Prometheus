"""Cross-check the declared vector against independently extracted evidence.

The atlas derives a world's structure twice, by two unrelated routes:

  1. the DECLARED VECTOR, from weighted keyword scoring over rules sections
  2. the CONDITIONS TABLE, from whole sentences matched as win/lose/eliminate/
     boundary/terminate rules, with thresholds parsed out

Neither is authoritative. But where they *disagree*, at least one is wrong, and
the disagreement is free to compute -- which makes it the cheapest quality
signal the atlas has. Monopoly is the case that motivated this: its conditions
table carries explicit elimination rules while its declared `loss_shape` was
NULL, and the generated turn trace showed a game that could never end.

Two modes:

  report  -- list contradictions, change nothing
  repair  -- fill NULLs and correct contradictions where the conditions table is
             the more specific evidence, never touching a reviewed or audited
             world, and recording every change for audit

A repair does NOT promote a world to `reviewed`. It is still machine inference;
it has merely been corroborated by a second machine route. Only a human can
produce `reviewed`, and only the operator with a rulebook can produce `audited`.
"""
from __future__ import annotations

import json

import store


def _has(con, slug, kind, min_n=1, needs_threshold=False):
    q = "SELECT COUNT(*) FROM conditions WHERE slug = ? AND kind = ?"
    a = [slug, kind]
    if needs_threshold:
        q += " AND threshold IS NOT NULL"
    return con.execute(q, a).fetchone()[0] >= min_n


# Each check: (name, why, predicate(world, con) -> None | (field, value))
# Returning a (field, value) pair means "the conditions table says this".

def _elimination(w, con):
    """Explicit elimination rules, but no loss shape that admits them."""
    if not _has(con, w["slug"], "ELIMINATE"):
        return None
    if w.get("loss_shape") in ("ELIMINATION", "TOTAL_RUIN"):
        return None
    return ("loss_shape", "ELIMINATION")


def _race(w, con):
    """A thresholded 'first to N' win rule, but no race horizon."""
    row = con.execute(
        "SELECT trigger FROM conditions WHERE slug = ? AND kind = 'WIN'"
        "  AND threshold IS NOT NULL LIMIT 1", (w["slug"],)).fetchone()
    if not row:
        return None
    trig = (row["trigger"] or "").lower()
    if "first" not in trig and "race" not in trig:
        return None
    if w.get("horizon") == "RACE_TO_TARGET":
        return None
    return ("horizon", "RACE_TO_TARGET")


def _dice_iid(w, con):
    """Dice named as a randomness source, but no exogenous process recorded."""
    if "DICE" not in (w.get("randomness_sources") or []):
        return None
    if w.get("exogenous_process"):
        return None
    return ("exogenous_process", "IID")


def _deck_depleting(w, con):
    """A shuffled deck named, but no exogenous process recorded."""
    rs = set(w.get("randomness_sources") or [])
    if not (rs & {"DECK_SHUFFLE", "DECK_DEPLETING"}):
        return None
    if w.get("exogenous_process"):
        return None
    return ("exogenous_process", "DEPLETING_DECK")


def _terminates(w, con):
    """An explicit game-end rule, but no horizon at all."""
    if w.get("horizon"):
        return None
    if not _has(con, w["slug"], "TERMINATE"):
        return None
    return ("horizon", "VARIABLE")


def _solitaire_but_multiplayer(w, con):
    """Wikidata says the game needs 2+ players, but interaction says solitaire.

    Cleared to NULL rather than guessed at. The minimum-player count is
    independent source evidence and is enough to know SOLITAIRE is wrong; it is
    not enough to know what the right answer is (competitive? cooperative?
    team?). 'We do not know' is a truthful cell. 'COMPETITIVE' would be a
    fabricated one, and the whole point of the coverage grid is that its cells
    mean something.
    """
    if w.get("interaction") != "SOLITAIRE":
        return None
    if (w.get("players_min") or 0) <= 1:
        return None
    return ("interaction", None)


REPAIRS = [
    ("solitaire_but_needs_two_players",
     "interaction=SOLITAIRE but the source says the game needs 2+ players",
     _solitaire_but_multiplayer),
    ("elimination_without_loss_shape",
     "conditions carry ELIMINATE rules but loss_shape does not admit elimination",
     _elimination),
    ("race_without_horizon",
     "a thresholded 'first to N' win rule but horizon is not RACE_TO_TARGET",
     _race),
    ("dice_without_process",
     "DICE randomness but no exogenous_process", _dice_iid),
    ("deck_without_process",
     "shuffled-deck randomness but no exogenous_process", _deck_depleting),
    ("terminate_without_horizon",
     "an explicit game-end rule but no horizon", _terminates),
]


# Contradictions that are reported but never auto-repaired: both sides are
# assertions, so silently picking one would manufacture false confidence.
def contradictions(con):
    out = []
    q = con.execute(
        "SELECT slug, name, information, randomness_sources, turn_structure,"
        "       tractability, interaction, players_max, exogenous_process"
        "  FROM worlds")
    for row in q:
        w = store.dec(row)
        rs = set(w.get("randomness_sources") or []) - {"NONE"}
        if w.get("information") == "PERFECT" and rs:
            out.append((w["slug"], w["name"], "information=PERFECT but randomness %s"
                        % ",".join(sorted(rs))))
        if w.get("turn_structure") == "REAL_TIME" and w.get("tractability") == "EXACT":
            out.append((w["slug"], w["name"], "REAL_TIME but tractability=EXACT"))
        if w.get("interaction") == "SOLITAIRE" and (w.get("players_max") or 0) > 1:
            out.append((w["slug"], w["name"], "interaction=SOLITAIRE but players_max=%s"
                        % w["players_max"]))
        if w.get("exogenous_process") == "NONE" and rs:
            out.append((w["slug"], w["name"], "exogenous=NONE but randomness %s"
                        % ",".join(sorted(rs))))
    return out


def run(con, repair=False, limit=None):
    """-> (findings, applied). findings is [(check, slug, name, field, value)]."""
    rows = con.execute(
        "SELECT * FROM worlds WHERE method IN ('heuristic','source')").fetchall()
    findings, applied = [], 0
    for row in rows:
        w = store.dec(row)
        for name, _why, fn in REPAIRS:
            try:
                hit = fn(w, con)
            except Exception:                                   # noqa: BLE001
                continue
            if not hit:
                continue
            field, value = hit
            findings.append((name, w["slug"], w["name"], field, value))
            if repair:
                cur = con.execute(
                    "UPDATE worlds SET %s = ?, last_updated = ?"
                    " WHERE id = ? AND method IN ('heuristic','source')"
                    % field, (value, store.now(), w["id"]))
                if cur.rowcount:
                    con.execute(
                        "INSERT INTO reviews (slug, field, old_value, value, note,"
                        " reviewer, ts) VALUES (?,?,?,?,?,?,?)",
                        (w["slug"], field, str(w.get(field)),
                         "<cleared>" if value is None else value,
                         "coherence: %s" % name, "coherence-check", store.now()))
                    applied += 1
                    w[field] = value      # later checks in this pass see the fix
            if limit and len(findings) >= limit:
                break
    if repair:
        con.commit()
    return findings, applied


def summarise(findings):
    counts = {}
    for name, _s, _n, field, value in findings:
        key = (name, field, "<cleared>" if value is None else value)
        counts[key] = counts.get(key, 0) + 1
    return sorted(counts.items(), key=lambda kv: -kv[1])


if __name__ == "__main__":
    import sys
    con = store.connect()
    do = "--repair" in sys.argv
    f, applied = run(con, repair=do)
    print("findings: %d   applied: %d" % (len(f), applied))
    for (name, field, value), n in summarise(f):
        print("  %-34s %-20s -> %-18s %d" % (name, field, value, n))
    c = contradictions(con)
    print("\ncontradictions (reported, never auto-repaired): %d" % len(c))
    seen = {}
    for _slug, _nm, msg in c:
        key = msg.split(" but ")[0] + " but ..."
        seen[key] = seen.get(key, 0) + 1
    for k, n in sorted(seen.items(), key=lambda kv: -kv[1])[:10]:
        print("  %-52s %d" % (k, n))
