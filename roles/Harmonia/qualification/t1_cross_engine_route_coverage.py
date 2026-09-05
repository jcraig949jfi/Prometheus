"""T1 -- cross-ENGINE session affinity across the WHOLE live route table.

Harmonia, 2026-09-05. Same host, two engines, two databases. This is a
cross-ENGINE test and explicitly NOT a cross-MACHINE test: no LAN hop, no
second TLS identity, no second clock, no independently deployed build. See
integration/M1_TEST_SURFACE_FOR_HARMONIA.md section 3.

The route list is ENUMERATED FROM THE LIVE openapi.json and the request bodies
are SYNTHESISED FROM THE LIVE SCHEMAS. Nothing here is hand-written, because a
hand-drawn boundary is what produced two coverage holes in this feature
already: the previous coverage test scoped itself with the same predicate that
created the gap it missed.

Two arms, and the second is what makes the first mean anything:

  FOREIGN  engine B's own bearer token + engine A's session key
           -> must be 421 WRONG_SESSION on every session-scoped route
  CONTROL  engine B's own bearer token + engine B's OWN session key
           -> must NOT be 421 on any route

Without the control arm a route that answered 421 unconditionally -- broken,
not protected -- would score as a pass.
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.request

EXEMPT = {
    "/v2/version", "/v2/clients", "/v2/sessions", "/v2/topology-groups",
    "/v2/audit/verify-anchor",
}


class Http:
    def __init__(self, base, cafile=None, token=None):
        self.base = base.rstrip("/")
        self.ctx = ssl.create_default_context(cafile=cafile) if cafile else None
        self.token = token

    def call(self, method, path, body=None, session_key=None):
        url = self.base + path
        data = json.dumps(body).encode() if body is not None else None
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        if session_key:
            h["X-SFE-Session"] = session_key
        req = urllib.request.Request(url, data=data, headers=h, method=method)
        try:
            kw = {"context": self.ctx} if self.ctx else {}
            with urllib.request.urlopen(req, timeout=30, **kw) as r:
                return r.status, json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode() or "{}")
            except Exception:                                      # noqa: BLE001
                return e.code, {}
        except Exception as e:                                     # noqa: BLE001
            return None, {"transport_error": repr(e)}


def err_code(payload):
    d = (payload or {}).get("detail", payload)
    return d.get("error") if isinstance(d, dict) else None


# --------------------------------------------------------------------------
# Body synthesis from the LIVE OpenAPI schema. Required fields only, filled by
# declared type. The point is a body that PASSES validation, so that what the
# probe measures is the affinity decision and not a 422 from an empty body.
# --------------------------------------------------------------------------
def synth(schema, comps, depth=0):
    if depth > 4 or not isinstance(schema, dict):
        return {}
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        return synth(comps.get(name, {}), comps, depth + 1)
    for key in ("anyOf", "oneOf", "allOf"):
        if key in schema:
            for alt in schema[key]:
                if alt.get("type") != "null":
                    return synth(alt, comps, depth + 1)
    t = schema.get("type")
    if t == "object" or "properties" in schema:
        out = {}
        props = schema.get("properties", {})
        for f in schema.get("required", []):
            out[f] = synth(props.get(f, {}), comps, depth + 1)
        return out
    if t == "array":
        return [synth(schema.get("items", {}), comps, depth + 1)]
    if t == "integer":
        return 1
    if t == "number":
        return 1.0
    if t == "boolean":
        return False
    if t == "string":
        return "probe"
    return {}


def body_for(spec, comps, method, path):
    op = spec["paths"][path].get(method.lower(), {})
    rb = op.get("requestBody")
    if not rb:
        return None
    sch = rb.get("content", {}).get("application/json", {}).get("schema", {})
    return synth(sch, comps)


def query_for(spec, method, path):
    """Required query params, filled so the route is reachable."""
    op = spec["paths"][path].get(method.lower(), {})
    q = []
    for p in op.get("parameters", []):
        if p.get("in") == "query" and p.get("required"):
            q.append(f"{p['name']}=probe")
    return ("?" + "&".join(q)) if q else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a-url", default="https://192.168.1.202:8811/v2")
    ap.add_argument("--a-cacert", required=True)
    ap.add_argument("--b-url", default="http://127.0.0.1:8899/v2")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    A = Http(a.a_url, cafile=a.a_cacert)
    B = Http(a.b_url)

    # --- identities, live, from the engines that answer -------------------
    st, av = A.call("GET", "/version")
    st, bv = B.call("GET", "/version")
    A.token = A.call("POST", "/clients", {"name": "harmonia-t1-A"})[1]["token"]
    B.token = B.call("POST", "/clients", {"name": "harmonia-t1-B"})[1]["token"]
    a_id = A.call("POST", "/audit/verify-anchor", {
        "world_id": "wld_" + "0" * 24, "event_id": "evt_" + "0" * 16,
        "entry_hash": "sha256:" + "0" * 64})[1]["engine"]["engine_instance_id"]
    b_id = B.call("POST", "/audit/verify-anchor", {
        "world_id": "wld_" + "0" * 24, "event_id": "evt_" + "0" * 16,
        "entry_hash": "sha256:" + "0" * 64})[1]["engine"]["engine_instance_id"]

    print("engine A (live) : %s  %s" % (a_id, av.get("engine_source_hash", "")[:22]))
    print("engine B (scratch): %s  %s" % (b_id, bv.get("engine_source_hash", "")[:22]))
    if a_id == b_id:
        print("ABORT: both engines report the same instance id; nothing to test")
        return 2
    if av.get("engine_source_hash") != bv.get("engine_source_hash"):
        print("NOTE: builds differ between A and B -- affinity semantics may "
              "not be comparable")

    # --- real objects on each engine --------------------------------------
    sa = A.call("POST", "/sessions", {"name": "t1-A"})[1]
    sb = B.call("POST", "/sessions", {"name": "t1-B"})[1]
    key_a, key_b = sa["session_key"], sb["session_key"]

    wa = A.call("POST", "/worlds", {"session_id": sa["session_id"],
                                    "name": "t1-A"}, session_key=key_a)[1]
    wb = B.call("POST", "/worlds", {"session_id": sb["session_id"],
                                    "name": "t1-B"}, session_key=key_b)[1]
    A.call("POST", "/worlds/%s/start" % wa["world_id"], {}, session_key=key_a)
    B.call("POST", "/worlds/%s/start" % wb["world_id"], {}, session_key=key_b)
    ha = A.call("POST", "/worlds/%s/hypotheses" % wa["world_id"],
                {"statement": "H"}, session_key=key_a)[1]
    xa = A.call("POST", "/worlds/%s/experiments" % wa["world_id"],
                {"spec": {"action": "encounter", "ticks": 4},
                 "hyp_id": ha.get("hyp_id"), "commit": True},
                session_key=key_a)[1]

    ids_a = {"wid": wa["world_id"], "eid": xa.get("exp_id", "exp_" + "0" * 24),
             "aid": "sha256:" + "0" * 64, "work_id": "wrk_" + "0" * 24}
    ids_b = {"wid": wb["world_id"], "eid": "exp_" + "0" * 24,
             "aid": "sha256:" + "0" * 64, "work_id": "wrk_" + "0" * 24}

    # --- enumerate from the LIVE spec -------------------------------------
    spec = A.call("GET", "/openapi.json")[1]
    comps = spec.get("components", {}).get("schemas", {})
    routes = sorted({(m.upper(), p) for p, ops in spec["paths"].items()
                     for m in ops if m.upper() in ("GET", "POST")},
                    key=lambda r: (r[1], r[0]))

    def fill(path, ids):
        # openapi paths carry the /v2 prefix and the base URL already ends in
        # /v2. Concatenating both silently produced /v2/v2/... and a uniform
        # 404 on the first run -- which reads exactly like "no affinity check
        # anywhere". A probe artifact, not an engine finding; stripped here.
        out = path[3:] if path.startswith("/v2/") else path
        for k, v in ids.items():
            out = out.replace("{%s}" % k, v)
        return out

    rows, foreign_fail, control_fail = [], [], []
    for method, path in routes:
        scoped = path not in EXEMPT
        body = body_for(spec, comps, method, path)
        if body is not None and "session_id" in body:
            body["session_id"] = sb["session_id"]       # a valid id ON B
        qs = query_for(spec, method, path)

        fst, fp = B.call(method, fill(path, ids_a) + qs, body, session_key=key_a)
        cst, cp = B.call(method, fill(path, ids_b) + qs, body, session_key=key_b)

        row = {"method": method, "path": path, "session_scoped": scoped,
               "foreign_status": fst, "foreign_code": err_code(fp),
               "control_status": cst, "control_code": err_code(cp)}
        rows.append(row)

        if scoped:
            if not (fst == 421 and row["foreign_code"] == "WRONG_SESSION"):
                foreign_fail.append(row)
            if cst == 421:
                control_fail.append(row)
        else:
            if fst == 421:
                foreign_fail.append(row)                # exempt must NOT 421

    n_scoped = sum(1 for r in rows if r["session_scoped"])
    n_exempt = len(rows) - n_scoped

    print("\nroutes enumerated from live openapi.json : %d" % len(rows))
    print("  session-scoped                         : %d" % n_scoped)
    print("  exempt                                 : %d" % n_exempt)
    print("\nFOREIGN arm  (B's token + A's session key)")
    print("  session-scoped answering 421 WRONG_SESSION : %d/%d"
          % (n_scoped - len([r for r in foreign_fail if r["session_scoped"]]),
             n_scoped))
    print("CONTROL arm  (B's token + B's own session key)")
    print("  session-scoped NOT answering 421           : %d/%d"
          % (n_scoped - len(control_fail), n_scoped))

    if foreign_fail:
        print("\nROUTES THAT DID NOT FAIL CLOSED:")
        for r in foreign_fail:
            print("  %-5s %-52s -> %s %s"
                  % (r["method"], r["path"], r["foreign_status"], r["foreign_code"]))
    if control_fail:
        print("\nCONTROL VIOLATIONS (421 with its OWN key -- route is broken,"
              " not protected):")
        for r in control_fail:
            print("  %-5s %-52s" % (r["method"], r["path"]))

    # --- the exempt route PEW depends on ----------------------------------
    va_st, va_p = B.call("POST", "/audit/verify-anchor", {
        "world_id": ids_b["wid"], "event_id": "evt_" + "0" * 16,
        "entry_hash": "sha256:" + "0" * 64}, session_key=key_a)
    va_ok = va_st == 200 and "engine" in va_p
    print("\nverify-anchor with a FOREIGN key (must still answer, PEW depends "
          "on it): %s %s -> %s" % (va_st, err_code(va_p),
                                   "ANSWERS" if va_ok else "BROKEN"))

    ok = (not foreign_fail) and (not control_fail) and va_ok
    out = {"engine_a": a_id, "engine_b": b_id,
           "build": av.get("engine_source_hash"),
           "routes_total": len(rows), "session_scoped": n_scoped,
           "exempt": n_exempt,
           "foreign_arm_failures": foreign_fail,
           "control_arm_failures": control_fail,
           "verify_anchor_exempt_answers": va_ok,
           "verify_anchor_status": va_st,
           "all_pass": ok, "rows": rows}
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("\nT1 %s   rows: %s" % ("PASS" if ok else "FAIL", a.out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
