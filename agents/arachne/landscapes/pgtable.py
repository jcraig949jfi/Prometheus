"""Generic Postgres-table landscape — widen the fabric cheaply.

A row is a node; two rows linked when they share a column value (same invariant).
Subclass by setting the class attributes. Verbs are operator-typed
(shares_<invariant>), null_p reflects how generic the invariant is.
"""
from __future__ import annotations

from agents.arachne.landscapes import _pg


class PgTableLandscape:
    name = "pgtable"
    DB = "prometheus_sci"
    TABLE = ""            # e.g. "topology.knots"
    LABEL_COL = ""        # human-readable unique id column
    LINKS: list = []      # [(column, verb, null_p), ...]
    SAMPLE_PCT = 1.0      # TABLESAMPLE SYSTEM percentage for seeds

    def __init__(self):
        self._conn = _pg.connect(self.DB)

    def available(self) -> bool:
        if self._conn is None or not self.TABLE:
            return False
        try:
            cur = self._conn.cursor()
            cur.execute(f"SELECT 1 FROM {self.TABLE} LIMIT 1;")
            cur.fetchone(); cur.close()
            return True
        except Exception:
            return False

    def _q(self, sql, args=()):
        cur = self._conn.cursor()
        cur.execute(sql, args)
        rows = cur.fetchall()
        cur.close()
        return rows

    def seeds(self, rng, k: int = 4) -> list:
        rows = self._q(
            f"SELECT {self.LABEL_COL} FROM {self.TABLE} TABLESAMPLE SYSTEM (%s) "
            f"WHERE {self.LABEL_COL} IS NOT NULL LIMIT %s;", (self.SAMPLE_PCT, k * 4))
        out = [f"{self.name}:{r[0]}" for r in rows if r[0] is not None]
        rng.shuffle(out)
        return out[:k]

    def expand(self, node: str, rng, ruleset) -> list:
        prefix = f"{self.name}:"
        if not node.startswith(prefix):
            return []
        label = node[len(prefix):]
        cols = ", ".join(c for (c, _, _) in self.LINKS)
        rows = self._q(
            f"SELECT {cols} FROM {self.TABLE} WHERE {self.LABEL_COL}=%s LIMIT 1;", (label,))
        if not rows:
            return []
        n = max(2, ruleset.max_neighbors)
        out = []
        for i, (col, verb, null_p) in enumerate(self.LINKS):
            val = rows[0][i]
            if val is None:
                continue
            try:
                for (other,) in self._q(
                        f"SELECT {self.LABEL_COL} FROM {self.TABLE} WHERE {col}=%s "
                        f"AND {self.LABEL_COL}<>%s AND {self.LABEL_COL} IS NOT NULL LIMIT %s;",
                        (val, label, n)):
                    out.append((f"{self.name}:{other}", verb, null_p))
            except Exception:
                pass
        return out


class KnotsLandscape(PgTableLandscape):
    name = "knots"
    TABLE = "topology.knots"
    LABEL_COL = "name"
    SAMPLE_PCT = 5.0
    LINKS = [
        ("determinant", "same_determinant", 0.40),
        ("signature", "same_signature", 0.55),
        ("crossing_number", "same_crossing", 0.65),
    ]


class GroupsLandscape(PgTableLandscape):
    name = "groups"
    TABLE = "algebra.groups"
    LABEL_COL = "label"
    SAMPLE_PCT = 0.01
    LINKS = [
        ("order_val", "same_order", 0.55),
        ("exponent", "same_exponent", 0.60),
        ("n_conjugacy", "same_n_conjugacy", 0.60),
    ]
