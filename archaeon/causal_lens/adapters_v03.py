"""v0.3 adapter mappings (E-001 / T-005): each engine field goes to the referent it actually measures. Engines are untouched.

  engine    native field                                   -> v0.3 field (referent)
  BEE       own_steps / win_steps / other_steps            -> code_location_share (WHERE)
            by_own_code (copy op pc < L)                   -> code_location_share of the copy writes (WHERE); NEVER write_governing
            writer id                                      -> executor_identity (WHO); context_authorship = the writer (WHO)
            FULL replay code-material probe (T-001/T-002)  -> write_governing (WHAT): own-region + self-copied = writer material,
                                                              foreign = window original material, elsewhere = NOT_IDENTIFIABLE share
            (no probe)                                     -> write_governing = NOT_IDENTIFIABLE
  NPE       prov / prov_lit (context that wrote)           -> context_authorship (WHO); NEVER write_governing
            T-003 probe (code-byte provenance at the pc)   -> write_governing (WHAT) and code_location_share (WHERE)
            (no probe)                                     -> write_governing = NOT_IDENTIFIABLE
  Archaeon  taint fetch labels E / N / other (exec_counts) -> execution_share (WHAT, native)
            exec_foreign                                   -> code_location_share (WHERE)
            'self' / 'neighbour' fetch-only executions     -> write_governing (WHAT) decided; 'mixed' -> NOT_IDENTIFIABLE
"""
from __future__ import annotations

from archaeon.causal_lens.schema_v03 import Graph, NI, NONE


def _F(value, referent, basis, source):
    return dict(value=value, basis=basis, source=source, referent=referent)


def bee_fields(row, L, codeprov=None):
    own_s, win_s, oth_s = row[13], row[14], row[15]; tot = max(1, own_s + win_s + oth_s)
    f = {"executor_identity": dict(value="org:%s" % row[1], basis="NATIVE_RECORD", source="writer id"),
         "context_authorship": _F({"writer": 1.0}, "WHO", "NATIVE_RECORD", "the writer's context executed every write"),
         "code_location_share": _F({"own_region": round(own_s / tot, 4), "window": round(win_s / tot, 4), "elsewhere": round(oth_s / tot, 4)},
                                   "WHERE", "TRACE", "step counts by pc region")}
    if codeprov is None:
        f["write_governing"] = _F(NI, "WHAT", "NATIVE_RECORD", "code material not persisted in traced rows")
    else:
        n = sum(codeprov.values()) or 1
        f["write_governing"] = _F({"writer_material": round((codeprov["own_region"] + codeprov["self_copied"]) / n, 4),
                                   "window_original_material": round(codeprov["foreign"] / n, 4), "unclassified": round(codeprov["elsewhere"] / n, 4)},
                                  "WHAT", "REPLAY", "code-byte provenance of each own-sourced copy write (FULL replay)")
    return f


def npe_fields(birth):
    ww = birth["who_where_what"]; D = max(1, birth["D"])
    def s(pred): return round(sum(v for k, v in ww.items() if pred(*k.split("|"))) / D, 4)
    return {"context_authorship": _F({"donor_context": s(lambda w, l, m: w == "donor_ctx"), "victim_context": s(lambda w, l, m: w == "victim_ctx")},
                                     "WHO", "TRACE", "prov_lit context of the last write to each directed byte"),
            "code_location_share": _F({"donor_half": s(lambda w, l, m: l == "donor_half"), "victim_half": s(lambda w, l, m: l == "victim_half"),
                                       "outside": s(lambda w, l, m: l == "outside")}, "WHERE", "TRACE", "instruction address of each directed write"),
            "write_governing": _F({"donor_material": s(lambda w, l, m: (l == "donor_half" and m == "original") or m == "changed_by_donor"),
                                   "victim_material": s(lambda w, l, m: (l == "victim_half" and m == "original") or m == "changed_by_victim")},
                                  "WHAT", "REPLAY", "code-byte provenance at execution (T-003 observation-only replay)")}


def archaeon_fields(ev, exec_foreign=None, steps=None):
    sc = ev["exec_counts"]; tot = max(1, sc.get("self", 0) + sc.get("nbr", 0) + sc.get("other", 0))
    f = {"execution_share": _F({"executor_material": round(sc.get("self", 0) / tot, 4), "neighbour_material": round(sc.get("nbr", 0) / tot, 4),
                                "other": round(sc.get("other", 0) / tot, 4)}, "WHAT", "TRACE", "taint labels of fetched bytes"),
         "write_governing": _F({"self": {"executor_material": 1.0}, "neighbour": {"neighbour_material": 1.0}}.get(ev["executed_material"], NI),
                               "WHAT", "TRACE", "single-material executions decide; mixed not recorded per write")}
    if exec_foreign is not None and steps:
        f["code_location_share"] = _F({"own_region": round((steps - exec_foreign) / steps, 4), "neighbour_region": round(exec_foreign / steps, 4)},
                                      "WHERE", "TRACE", "exec_foreign (pc >= G)")
    return f


def graph_of(engine, events_fields):
    g = Graph(engine, "segment")
    for k, f in enumerate(events_fields):
        g.event("e%d" % k, ["UNCLASSIFIED"], **f)
    return g
