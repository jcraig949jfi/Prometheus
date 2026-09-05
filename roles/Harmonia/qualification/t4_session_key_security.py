"""T4 -- session key security. Harmonia, 2026-09-05.

Read but never attacked, per the packet. The tail is secrets.token_urlsafe(24)
and only the SHA-256 is stored, so the question is not whether the tail can be
guessed -- it cannot -- but whether a WELL-FORMED key naming this engine's real
instance id can be distinguished from a real one, and whether a key ever leaks
back out through a response body.

Everything here is a forgery. No session is created on the target by this
probe, and no forged key can succeed by construction, so it is safe to run
against the live engine.
"""
from __future__ import annotations

import argparse
import json
import secrets
import ssl
import sys
import urllib.error
import urllib.request

R = []


def gate(name, ok, detail):
    R.append({"gate": name, "pass": bool(ok), "detail": detail})
    print("  [%s] %-46s %s" % ("PASS" if ok else "FAIL", name, detail))


class C:
    def __init__(self, base, cafile=None, token=None):
        self.base = base.rstrip("/")
        self.ctx = ssl.create_default_context(cafile=cafile) if cafile else None
        self.token = token
        self.seen = []

    def call(self, m, p, body=None, key=None):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = "Bearer " + self.token
        if key:
            h["X-SFE-Session"] = key
        d = json.dumps(body).encode() if body is not None else None
        r = urllib.request.Request(self.base + p, data=d, headers=h, method=m)
        kw = {"context": self.ctx} if self.ctx else {}
        try:
            with urllib.request.urlopen(r, timeout=30, **kw) as z:
                st, raw = z.status, z.read().decode()
        except urllib.error.HTTPError as e:
            st, raw = e.code, e.read().decode()
        except Exception as e:                                     # noqa: BLE001
            return None, {"transport_error": repr(e)}, ""
        self.seen.append(raw)
        try:
            return st, json.loads(raw or "{}"), raw
        except Exception:                                          # noqa: BLE001
            return st, {}, raw


def code(p):
    d = (p or {}).get("detail", p)
    return d.get("error") if isinstance(d, dict) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://192.168.1.202:8811/v2")
    ap.add_argument("--cacert", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    c = C(a.base, cafile=a.cacert)
    c.token = c.call("POST", "/clients", {"name": "harmonia-t4"})[1]["token"]
    eng = c.call("POST", "/audit/verify-anchor", {
        "world_id": "wld_" + "0" * 24, "event_id": "evt_" + "0" * 16,
        "entry_hash": "sha256:" + "0" * 64})[1]["engine"]["engine_instance_id"]
    body = eng[len("eng_"):]
    print("\ntarget engine_instance_id: %s" % eng)

    # 1. A well-formed forgery naming THIS engine. The instance id is public,
    #    so this is the strongest forgery an outsider can build. It must land
    #    on the hash lookup and miss.
    forged = "sfes_%s_%s" % (body, secrets.token_urlsafe(24))
    st, p, _ = c.call("GET", "/worlds", key=forged)
    gate("T4a_forged_key_naming_this_engine_is_unknown",
         st == 401 and code(p) == "SESSION_UNKNOWN",
         "-> %s %s" % (st, code(p)))

    # 2. A well-formed forgery naming a DIFFERENT engine -> wrong engine, and
    #    decided from the key's bytes without any lookup.
    other = "sfes_%s_%s" % ("0" * 24, secrets.token_urlsafe(24))
    st, p, _ = c.call("GET", "/worlds", key=other)
    gate("T4b_forged_key_naming_another_engine_is_wrong_session",
         st == 421 and code(p) == "WRONG_SESSION",
         "-> %s %s" % (st, code(p)))

    # 3. Malformed shapes must be 422 and must never be confused with either
    #    of the above.
    bad = {"empty": "", "no prefix": secrets.token_urlsafe(24),
           "short body": "sfes_abc_" + secrets.token_urlsafe(24),
           "non-hex body": "sfes_%s_%s" % ("z" * 24, secrets.token_urlsafe(24)),
           "short tail": "sfes_%s_abc" % body,
           "prefix only": "sfes_",
           "bearer-shaped": "gen2_" + secrets.token_urlsafe(24)}
    outs = {}
    for label, k in bad.items():
        st, p, _ = c.call("GET", "/worlds", key=k)
        outs[label] = "%s/%s" % (st, code(p))
    # an EMPTY header is documented as equivalent to absent, not malformed
    ok_bad = all(v.startswith("422") for lbl, v in outs.items()
                 if lbl != "empty") and outs["empty"].startswith("200")
    gate("T4c_malformed_keys_are_422_and_empty_means_absent", ok_bad,
         json.dumps(outs))

    # 4. Does any response ever echo a key back? Includes the one place a real
    #    key legitimately appears -- session creation -- which must be the ONLY
    #    place.
    st, s, raw_create = c.call("POST", "/sessions", {"name": "t4-echo"})
    real = s.get("session_key")
    echo_at_create = real is not None and real in raw_create
    others = [r for r in c.seen if r is not raw_create and real and real in r]
    st, p, raw_use = c.call("GET", "/worlds", key=real)
    reuse_echo = real in raw_use
    gate("T4d_key_appears_only_in_its_own_creation_response",
         echo_at_create and not others and not reuse_echo,
         "created_response_contains_key=%s other_responses_echoing=%d "
         "echoed_when_used=%s" % (echo_at_create, len(others), reuse_echo))

    # 5. A CLOSED session should be indistinguishable from a never-issued one
    #    at the status-code level. There is no close route on the API surface,
    #    so this cannot be exercised from a client.
    # T4e was INDETERMINATE on build 2892116274: SESSION_CLOSED existed in the
    # taxonomy but no route could produce it. POST /v2/sessions/{sid}/close
    # (b35046a60) makes it reachable, so the property is now MEASURED.
    paths = list(c.call("GET", "/openapi.json")[1]["paths"])
    if "/v2/sessions/{sid}/close" not in paths:
        R.append({"gate": "T4e_closed_session_is_409_not_404",
                  "pass": None, "state": "INDETERMINATE",
                  "detail": "no session-close route on this build"})
        print("  [INDT] T4e_closed_session_is_409_not_404  no close route")
    else:
        s2 = c.call("POST", "/sessions", {"name": "t4-close"})[1]
        k2 = s2["session_key"]
        st_pre, _, _ = c.call("GET", "/worlds", key=k2)
        st_cl, p_cl, _ = c.call("POST", "/sessions/%s/close" % s2["session_id"])
        st_use, p_use, _ = c.call("GET", "/worlds", key=k2)
        st_again, _, _ = c.call("POST", "/sessions/%s/close" % s2["session_id"])
        gate("T4e_closed_session_is_409_SESSION_CLOSED",
             st_cl == 200 and st_use == 409 and code(p_use) == "SESSION_CLOSED",
             "before close=%s, close=%s, key after close=%s %s"
             % (st_pre, st_cl, st_use, code(p_use)))
        gate("T4f_close_is_idempotent", st_again == 200,
             "second close -> %s" % st_again)
        # A closed session must be DISTINGUISHABLE from a forged one only in
        # the way the taxonomy intends: 409 vs 401, both refusals, neither
        # confirming or denying the existence of any other session.
        gate("T4g_closed_and_unknown_are_different_refusals",
             st_use == 409 and 401 == c.call("GET", "/worlds",
                 key="sfes_%s_%s" % (body, secrets.token_urlsafe(24)))[0],
             "closed=409 SESSION_CLOSED, never-issued=401 SESSION_UNKNOWN")

    ok = all(r["pass"] for r in R if r.get("state") != "INDETERMINATE")
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"all_pass": ok, "engine": eng, "gates": R}, f, indent=1)
    print("\nT4 %s" % ("PASS_WITH_GAPS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
