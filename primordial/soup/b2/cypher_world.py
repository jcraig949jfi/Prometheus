"""B2 GraphWorld as FalkorDB Cypher on the private substrate (port 6391).

Graph: (:Cell {c}) with static [:MOVE {d}] edges (d 0..3) to the neighbour cell;
(:Ent {i, k}) with one [:AT] edge to its cell. A dead entity is DETACH DELETEd.
One tick = four queries in spec order (EAT, PREY, MOVE, READ). The flee test is a
pattern: a live prey whose cell is a predator's cell or one MOVE hop from it.
"""
from __future__ import annotations

import hashlib
import os

from falkordb import FalkorDB

from .graphworld import Spec, _line, step_cell

HOST, PORT = "127.0.0.1", int(os.environ.get("PM_B_PORT", "6391"))

EAT = ("MATCH (f:Ent {k: 2})-[:AT]->(c:Cell)<-[:AT]-(:Ent {k: 1}) "
       "WITH DISTINCT f DETACH DELETE f")
PREY = ("MATCH (q:Ent {k: 1})-[:AT]->(c:Cell)<-[:AT]-(:Ent {k: 0}) "
        "WITH DISTINCT q DETACH DELETE q")
THREAT = ("MATCH (q:Ent {k: 1})-[:AT]->(qc:Cell) "
          "OPTIONAL MATCH (qc)-[:MOVE]-(:Cell)<-[:AT]-(p1:Ent {k: 0}) "
          "OPTIONAL MATCH (qc)<-[:AT]-(p0:Ent {k: 0}) "
          "WITH q, count(p1) + count(p0) AS nthreat WHERE nthreat > 0 RETURN q.i")
MOVE = ("UNWIND $moves AS mv "
        "MATCH (e:Ent {i: mv[0]})-[r:AT]->(c:Cell)-[:MOVE {d: mv[1]}]->(n:Cell) "
        "DELETE r CREATE (e)-[:AT]->(n)")
READ = "MATCH (e:Ent)-[:AT]->(c:Cell) RETURN e.i, c.c ORDER BY e.i"


def run_cypher(s: Spec, cheat: str = "", graph: str = "b2g") -> str:
    db = FalkorDB(host=HOST, port=PORT)
    try:
        db.select_graph(graph).delete()
    except Exception:
        pass
    g = db.select_graph(graph)
    C, L = s.cells, s.L
    g.query("UNWIND range(0, $C - 1) AS c CREATE (:Cell {c: c})", {"C": C})
    g.query("CREATE INDEX FOR (c:Cell) ON (c.c)")
    g.query("CREATE INDEX FOR (e:Ent) ON (e.i)")
    edges = [[c, step_cell(L, c, d), d] for c in range(C) for d in range(4)]
    g.query("UNWIND $E AS e MATCH (a:Cell {c: e[0]}), (b:Cell {c: e[1]}) CREATE (a)-[:MOVE {d: e[2]}]->(b)",
            {"E": edges})
    ents = [[i, s.kind(i), s.init_cell(i)] for i in range(s.n)]
    g.query("UNWIND $X AS x MATCH (c:Cell {c: x[2]}) CREATE (:Ent {i: x[0], k: x[1]})-[:AT]->(c)", {"X": ents})
    h = hashlib.sha256()
    for t in range(s.ticks):
        g.query(EAT)
        g.query(PREY)
        threatened = set() if cheat == "no_flee" else {row[0] for row in g.query(THREAT).result_set}
        live = g.query("MATCH (e:Ent) WHERE e.k < 2 RETURN e.i").result_set
        moves = [[i, (i * 7 + t * 3 + (1 if i in threatened else 0)) % 4] for (i,) in live]
        if moves:
            g.query(MOVE, {"moves": moves})
        cells = {i: c for i, c in g.query(READ).result_set}
        h.update(_line(t, cells))
    return h.hexdigest()
