"""OEIS landscape — integer sequences (prometheus_sci.analysis.oeis, 394K rows).

Node:  "oeis:<A-number>"
Verbs: "shares_prefix"   (same first 3 terms but distinct sequence — structural,
                          low null; this is exactly the Sleeping-Beauty wiring)
       "similar_growth"  (close growth_rate, same monotonicity — generic, mid null)
"""
from __future__ import annotations

from agents.arachne.landscapes import _pg


class OeisLandscape:
    name = "oeis"

    def __init__(self):
        self._conn = _pg.connect("prometheus_sci")
        if self._conn is not None:
            try:
                cur = self._conn.cursor()
                cur.execute("SET statement_timeout = 4000;")
                cur.close()
            except Exception:
                pass

    def available(self) -> bool:
        if self._conn is None:
            return False
        try:
            cur = self._conn.cursor()
            cur.execute("SELECT 1 FROM analysis.oeis LIMIT 1;")
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
        start = rng.randint(1, 380000)
        rows = self._q(
            "SELECT oeis_id FROM analysis.oeis WHERE seq_id >= %s AND oeis_id IS NOT NULL "
            "ORDER BY seq_id LIMIT %s;", (start, k * 2))
        out = [f"oeis:{r[0]}" for r in rows if r[0]]
        rng.shuffle(out)
        return out[:k]

    def expand(self, node: str, rng, ruleset) -> list:
        if not node.startswith("oeis:"):
            return []
        aid = node.split(":", 1)[1]
        rows = self._q(
            "SELECT first_terms, growth_rate, is_monotone FROM analysis.oeis "
            "WHERE oeis_id=%s LIMIT 1;", (aid,))
        if not rows:
            return []
        first_terms, growth, monotone = rows[0]
        n = max(2, ruleset.max_neighbors)
        out = []
        # shares_prefix: same first 3 terms, structural
        if first_terms and len(first_terms) >= 3:
            pref = list(first_terms[:3])
            try:
                for (other,) in self._q(
                        "SELECT oeis_id FROM analysis.oeis WHERE first_terms[1:3] = %s::bigint[] "
                        "AND oeis_id<>%s AND oeis_id IS NOT NULL LIMIT %s;",
                        (pref, aid, n)):
                    out.append((f"oeis:{other}", "shares_prefix", 0.2))
            except Exception:
                pass
        # similar_growth: generic dynamics
        if growth is not None:
            eps = 0.05
            try:
                for (other,) in self._q(
                        "SELECT oeis_id FROM analysis.oeis WHERE growth_rate BETWEEN %s AND %s "
                        "AND is_monotone IS NOT DISTINCT FROM %s AND oeis_id<>%s "
                        "AND oeis_id IS NOT NULL LIMIT %s;",
                        (growth - eps, growth + eps, monotone, aid, n)):
                    out.append((f"oeis:{other}", "similar_growth", 0.6))
            except Exception:
                pass
        return out
