"""LMFDB landscape — number-theoretic objects (local 363 GB Postgres mirror).

Node:  "lmfdb:ec/<lmfdb_label>"   (elliptic curves over Q)
Verbs: "isogenous"        (same isogeny class — structural, low null)
       "same_conductor"   (semi-generic — mid null)

Zero API limit: this is a local mirror. Queries are LIMITed to stay cheap.
"""
from __future__ import annotations

from agents.arachne.landscapes import _pg


class LmfdbLandscape:
    name = "lmfdb"

    def __init__(self):
        self._conn = _pg.connect("lmfdb")
        self._cond_lo = 11

    def available(self) -> bool:
        if self._conn is None:
            return False
        try:
            cur = self._conn.cursor()
            cur.execute("SELECT 1 FROM ec_curvedata LIMIT 1;")
            cur.fetchone()
            cur.close()
            return True
        except Exception:
            return False

    def _q(self, sql, args=()):
        cur = self._conn.cursor()
        cur.execute(sql, args)
        rows = cur.fetchall()
        cur.close()
        return rows

    def seeds(self, rng, k: int = 4) -> list[str]:
        # TABLESAMPLE = cheap random page sample (conductor is a TEXT column, so
        # numeric range scans are both wrong-ordered and unindexed; sampling
        # gives varied seeds without a full scan).
        rows = self._q(
            "SELECT lmfdb_label FROM ec_curvedata TABLESAMPLE SYSTEM (0.02) "
            "WHERE lmfdb_label IS NOT NULL LIMIT %s;", (k * 4,))
        out = [f"lmfdb:ec/{r[0]}" for r in rows if r[0]]
        rng.shuffle(out)
        return out[:k]

    def expand(self, node: str, rng, ruleset) -> list:
        if not node.startswith("lmfdb:ec/"):
            return []
        label = node.split("lmfdb:ec/", 1)[1]
        rows = self._q(
            "SELECT conductor, lmfdb_iso FROM ec_curvedata WHERE lmfdb_label=%s LIMIT 1;",
            (label,))
        if not rows:
            return []
        conductor, iso = rows[0]
        n = max(2, ruleset.max_neighbors)
        out = []
        # isogeny class — structural, specific
        if iso:
            for (other,) in self._q(
                    "SELECT lmfdb_label FROM ec_curvedata WHERE lmfdb_iso=%s "
                    "AND lmfdb_label<>%s LIMIT %s;", (iso, label, n)):
                out.append((f"lmfdb:ec/{other}", "isogenous", 0.15))
        # same conductor — semi-generic
        for (other,) in self._q(
                "SELECT lmfdb_label FROM ec_curvedata WHERE conductor=%s "
                "AND lmfdb_label<>%s LIMIT %s;", (conductor, label, n)):
            out.append((f"lmfdb:ec/{other}", "same_conductor", 0.55))
        return out
