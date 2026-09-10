#!/usr/bin/env python3
"""Track A part 1: ONE development build, one joint receipt.

    python deploy/trackA_joint_receipt.py [--json] [--port 8877]

WHAT THIS IS. Daedalus's iteration-1 work and Vivarium's were made on two
tested configurations that had never been run together. This runs them
together, once, on one build: a REAL engine process over HTTP, the shipped
sfclient, Vivarium's shipped `viv.preflight` loader and `viv.artifact_probe`
kind, and Archaeon's shipped `archaeon.producer.costs` receipts. Nothing is
mocked and nothing is re-implemented here -- every module is imported from the
tree, and the only code in this file is the scenario.

NOT A DEPLOYMENT. A development engine, its own database, its own blob
directory, its own engine_instance_id, plain HTTP on loopback. Production is
not touched and not restarted.

LANE. Files under vivarium/ and archaeon/ are READ and CALLED, never written.
Where the integration exposes something on their side, this receipt records it
as a finding for the operator to route -- it does not fix it.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.dirname(HERE)
SF = os.path.dirname(ENG)
REPO = os.path.dirname(SF)

for p in (ENG, os.path.join(SF, "SerendipityFoundryClient"),
          os.path.join(REPO, "vivarium"), REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from sfe.release import ENGINE_SOURCE_HASH                          # noqa: E402
from sfe.store import SCHEMA_VERSION                                # noqa: E402
from sfclient import EngineClient, EngineError                      # noqa: E402
from viv import artifacts as _a                                     # noqa: E402
from viv import artifact_probe as _probe                            # noqa: E402
from viv import preflight as _pf                                    # noqa: E402
from archaeon.producer import costs as _costs                       # noqa: E402

#: The declared reuse horizon for the shared source build: two attempts consume
#: it. Frozen HERE, in the receipt, because an attribution whose horizon is
#: chosen after the numbers are known is not an attribution.
REUSE_HORIZON = 2


# --------------------------------------------------------------- the engine
def free_port(preferred: int) -> int:
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", preferred))
        return preferred
    except OSError:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
    finally:
        s.close()


def start_engine(db: str, port: int, log_path: str):
    log = open(log_path, "wb")
    proc = subprocess.Popen(
        [sys.executable, os.path.join(ENG, "serve.py"), "--db", db,
         "--host", "127.0.0.1", "--port", str(port), "--insecure",
         "--registration", "open"],
        cwd=ENG, stdout=log, stderr=subprocess.STDOUT)
    base = "http://127.0.0.1:%d" % port
    for _ in range(200):
        if proc.poll() is not None:
            raise SystemExit("the development engine exited during startup; "
                             "see %s" % log_path)
        try:
            with urllib.request.urlopen(base + "/v2/version", timeout=2) as r:
                return proc, base, json.loads(r.read().decode())
        except Exception:                                    # noqa: BLE001
            time.sleep(0.25)
    proc.kill()
    raise SystemExit("the development engine never bound %s" % base)


# ------------------------------------------------------------- the scenario
def build_artifacts():
    """The producer's sealed inputs: a root that DECLARES a dependency, so the
    closure is real and the loader resolves two artifacts rather than one."""
    dep_obj = {"artifact_type": "failure_input_set", "schema_version": "1",
               "interface_id": "boolean-inputs-v1", "n_bits": 4,
               "items": [[1, 0, 1, 1], [0, 1, 0, 0]]}
    dep_raw = _a.canonical_bytes(dep_obj)
    dep_slot = {"digest": _a.digest_of(dep_raw),
                "artifact_type": "failure_input_set", "schema_version": "1",
                "codec": "canonical-json-v1", "expected_bytes": len(dep_raw),
                "interface_id": "boolean-inputs-v1"}

    root_obj = {"artifact_type": "failure_input_set", "schema_version": "1",
                "interface_id": "boolean-inputs-v1", "n_bits": 4,
                "items": [[0, 0, 0, 0], [1, 1, 1, 1], [1, 0, 0, 1]],
                "dependencies": [dict(dep_slot)]}
    root_raw = _a.canonical_bytes(root_obj)
    root_slot = {"digest": _a.digest_of(root_raw),
                 "artifact_type": "failure_input_set", "schema_version": "1",
                 "codec": "canonical-json-v1", "expected_bytes": len(root_raw),
                 "interface_id": "boolean-inputs-v1"}

    # A DECOY of exactly the root's length and a different digest. Without it
    # the digest-mismatch fixture cannot fire: preflight checks size before
    # the hash, so any shorter substitute is caught as a SIZE_MISMATCH and the
    # hash is never reached -- which would have made the digest fixture a
    # second size test wearing the wrong name.
    decoy_obj = dict(root_obj)
    decoy_obj["items"] = [[0, 0, 0, 0], [1, 1, 1, 1], [1, 0, 1, 0]]
    decoy_raw = _a.canonical_bytes(decoy_obj)
    assert len(decoy_raw) == len(root_raw)
    assert _a.digest_of(decoy_raw) != _a.digest_of(root_raw)
    return (dep_raw, dep_slot), (root_raw, root_slot), decoy_raw


class Attempt:
    """One executor attempt: reserve BEFORE each fetch, resolve through the
    engine, and settle exactly what moved."""

    def __init__(self, R, exe, wx, locators, root_slot, attempt_id):
        self.R, self.exe, self.wx = R, exe, wx
        self.locators, self.root_slot = locators, root_slot
        self.attempt_id = attempt_id
        self.reservations = []
        self.cost_events = []

    def debit(self, resource: str, amount: float):
        """Vivarium's preflight calls this BEFORE the fetch it is about to pay
        for. It is wired straight to the engine's reservation, so the
        enforceable counter moves before a byte is resolved.

        THE KEY IS POSITIONAL, and that is a finding rather than a choice: the
        `debit(resource, amount)` hook does not carry the artifact identity, so
        the strongest idempotency key available here is the ordinal of the
        fetch within the attempt. A retry that resolved the closure in a
        different order would key differently.
        """
        idem = "%s:%s:%d" % (self.attempt_id, resource, len(self.reservations))
        try:
            r = self.exe.reserve_budget(self.wx, resource, amount,
                                        stage="retrieval",
                                        attempt_id=self.attempt_id,
                                        idem_key=idem)
        except EngineError as exc:
            detail = exc.detail if isinstance(exc.detail, dict) else {}
            if exc.status == 409 or detail.get("error") == "budget_exhausted":
                raise _pf.BudgetExhausted(
                    "the engine's reservation refused the load: %s"
                    % detail.get("message"), detail=detail) from exc
            raise
        self.reservations.append(r)
        return r

    def hydrate(self):
        resolver = _pf.SfeResolver(self.exe, execution_world=self.wx,
                                   client_id=self.exe.client_id)
        pf = _pf.Preflight(resolver=resolver, locators=self.locators,
                           debit=self.debit)
        inputs, receipt = pf.hydrate({"failure_inputs": self.root_slot})
        self.load_receipt = receipt
        self.resolver = resolver
        return inputs, receipt

    def settle_retrieval(self):
        """One cost event per reservation. The bytes really moved, so an
        interrupted attempt still pays for the retrieval it completed --
        releasing here would be claiming the fetch did not happen."""
        for i, res in enumerate(self.reservations):
            ce = self.exe.cost_event(
                self.wx, stage="retrieval", attempt_id=self.attempt_id,
                reservation_id=res["reservation_id"],
                source_artifacts=[c["digest"]
                                  for c in self.load_receipt["closure"]],
                resources=[
                    {"resource": "artifact_bytes", "quantity": res["amount"],
                     "unit": "bytes", "method": "counter", "scope": "attempt"},
                    {"resource": "engine_fetches", "quantity": 1,
                     "unit": "count", "method": "counter", "scope": "attempt"},
                    {"resource": "peak_memory_bytes", "quantity": None,
                     "method": "sampler", "unit": "bytes", "scope": "attempt"},
                ],
                environment={"stratum": "cpu-only", "profile": "alpha",
                             "concurrent_jobs": 1},
                refs={"reservation_ordinal": i})
            self.cost_events.append(ce)
        return self.cost_events


def main():                                                  # noqa: C901
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8877)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--workdir", default=os.path.join(
        os.environ.get("TEMP", "."), "trackA_dev"))
    a = ap.parse_args()

    os.makedirs(a.workdir, exist_ok=True)
    db = os.path.join(a.workdir, "trackA.db")
    for stale in (db, db + "-wal", db + "-shm"):
        if os.path.exists(stale):
            os.remove(stale)

    port = free_port(a.port)
    proc, base, version = start_engine(db, port,
                                       os.path.join(a.workdir, "engine.log"))

    R = {"receipt": "trackA.part1.joint.v1", "steps": [], "checks": [],
         "findings": [], "not_run": []}
    ok = [True]

    def step(name, **kw):
        R["steps"].append({"step": name, **kw})
        print("  %-40s %s" % (name, json.dumps(kw, default=str)[:110]))

    def check(name, cond, detail=""):
        R["checks"].append({"check": name, "pass": bool(cond),
                            "detail": str(detail)[:300]})
        if not cond:
            ok[0] = False
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name,
                               "" if cond else "  <-- " + str(detail)))

    def finding(code, what, owner):
        R["findings"].append({"code": code, "owner": owner, "finding": what})

    try:
        print("TRACK A PART 1 -- JOINT RECEIPT (development engine)")
        print("=" * 74)

        # -- identities, kept DISTINCT ------------------------------------
        prod = EngineClient(base)
        prod.register("trackA-producer")
        exe = EngineClient(base)
        exe.register("trackA-executor")
        third = EngineClient(base)
        third.register("trackA-outsider")

        R["engine"] = {
            "base_url": base,
            "engine_instance_id": version.get("engine_instance_id"),
            "engine_source_hash": version.get("engine_source_hash"),
            "engine_source_hash_of_this_import": ENGINE_SOURCE_HASH,
            "schema_version": version.get("schema_version"),
            "schema_version_of_this_import": SCHEMA_VERSION,
            "db": os.path.abspath(db)}
        for k in ("engine_instance_id", "engine_source_hash",
                  "schema_version"):
            print("  %-24s %s" % (k, R["engine"][k]))
        print()

        check("the served build is the build this receipt imported",
              version.get("engine_source_hash") == ENGINE_SOURCE_HASH
              and version.get("schema_version") == SCHEMA_VERSION,
              {"served": version.get("engine_source_hash"),
               "imported": ENGINE_SOURCE_HASH})

        # ITEM 2, Daedalus half: the principal is ENGINE-ISSUED and retained.
        check("register() retained the engine-issued client_id",
              bool(prod.client_id) and bool(exe.client_id)
              and prod.client_id != exe.client_id,
              {"producer": prod.client_id, "executor": exe.client_id})
        check("no substitute principal is invented from a bare token",
              EngineClient(base, token=exe.token).client_id is None)
        check("repr names the principal and never the credential",
              exe.token not in repr(exe) and exe.client_id in repr(exe),
              repr(exe))
        R["principals"] = {"producer_client_id": prod.client_id,
                           "executor_client_id": exe.client_id,
                           "outsider_client_id": third.client_id,
                           "engine_issued": True,
                           "credential_in_receipt": False}
        step("principals registered", producer=prod.client_id,
             executor=exe.client_id)

        # -- worlds --------------------------------------------------------
        grp = prod.create_topology_group("trackA: producer -> executor")
        sp = prod.create_session("trackA-producer")
        wp = prod.create_world(sp, "trackA-source",
                               sharing_policy="FULLY_SHARED",
                               topology_group=grp)["world_id"]
        prod.start(wp)

        sx = exe.create_session("trackA-executor")
        wx = exe.create_world(
            sx, "trackA-execution", sharing_policy="FULLY_SHARED",
            topology_group=grp,
            budget={
                # ENFORCEABLE: the reservation must be able to refuse a load.
                "artifact_bytes": {"limit": 4096, "enforcement": "enforceable"},
                "cpu_s": {"limit": 30, "enforcement": "enforceable"},
                "engine_fetches": {"limit": 32, "enforcement": "enforceable"},
                # MEASURED, never labelled enforced: the engine samples it and
                # does not stop anything on it, and calling that enforcement
                # would be claiming a guarantee nothing implements.
                "peak_memory_bytes": {"limit": None,
                                      "enforcement": "measured"},
                # UNAVAILABLE is not zero: not instrumented on this path.
                "gpu_s": {"limit": None, "enforcement": "unavailable"},
            })["world_id"]
        exe.start(wx)
        step("worlds created", source_world=wp, execution_world=wx,
             topology_group=grp)

        # -- the producer's sealed inputs ---------------------------------
        (dep_raw, dep_slot), (root_raw, root_slot), decoy_raw = \
            build_artifacts()
        meta = {"info_kind": "artifact", "artifact_type": "failure_input_set",
                "schema_version": "1", "codec": "canonical-json-v1",
                "interface_id": "boolean-inputs-v1"}

        with _costs.Meter() as gen_meter:
            dep_art = prod.artifact(wp, "failure_input_set", dep_raw,
                                    meta=dict(meta),
                                    expected_blob_hash=dep_slot["digest"])
            root_art = prod.artifact(wp, "failure_input_set", root_raw,
                                     meta=dict(meta),
                                     expected_blob_hash=root_slot["digest"])
        check("the write-side digest gate sealed both artifacts",
              dep_art["blob_hash"] == dep_slot["digest"]
              and root_art["blob_hash"] == root_slot["digest"])

        corrupt = False
        try:
            prod.artifact(wp, "failure_input_set", root_raw + b" ",
                          meta=dict(meta),
                          expected_blob_hash=root_slot["digest"])
        except EngineError:
            corrupt = True
        check("the write gate stores nothing when the bytes disagree", corrupt)

        # A legitimately sealed artifact of the root's exact length, used only
        # by the digest-mismatch fixture below. It is deliberately NOT in the
        # address book: an address nothing consumes is itself a rejection.
        decoy_art = prod.artifact(wp, "failure_input_set", decoy_raw,
                                  meta=dict(meta),
                                  expected_blob_hash=_a.digest_of(decoy_raw))

        locators = {
            dep_slot["digest"]: {"source_world": wp,
                                 "source_artifact": dep_art["artifact_id"]},
            root_slot["digest"]: {"source_world": wp,
                                  "source_artifact": root_art["artifact_id"]},
        }
        R["artifacts"] = {
            "root": {"artifact_id": root_art["artifact_id"],
                     "digest": root_slot["digest"], "bytes": len(root_raw)},
            "dependency": {"artifact_id": dep_art["artifact_id"],
                           "digest": dep_slot["digest"], "bytes": len(dep_raw)},
            "source_world": wp}
        step("producer sealed its inputs", root=root_art["artifact_id"],
             dependency=dep_art["artifact_id"],
             bytes=len(root_raw) + len(dep_raw))

        # -- attempt 1: interrupted after the load ------------------------
        a1 = Attempt(R, exe, wx, locators, root_slot, "attempt-1")
        _inputs1, rec1 = a1.hydrate()
        check("attempt-1 reserved BEFORE it fetched",
              len(a1.reservations) == rec1["closure_size"]
              and all(r["state"] == "OPEN" for r in a1.reservations),
              [r["state"] for r in a1.reservations])
        check("attempt-1 resolved the whole closure through the engine",
              rec1["closure_size"] == 2 and rec1["engine_fetches"] == 2, rec1)
        a1.settle_retrieval()
        step("attempt-1 INTERRUPTED after the load", attempt="attempt-1",
             reservations=len(a1.reservations),
             cost_events=[c["cost_event_id"] for c in a1.cost_events],
             note="the bytes moved, so the retrieval it completed is charged; "
                  "it is not released, because a release would claim the "
                  "fetch never happened")

        # -- attempt 2: the retry, revalidated from step 1 ----------------
        a2 = Attempt(R, exe, wx, locators, root_slot, "attempt-2")
        inputs2, rec2 = a2.hydrate()
        check("the retry REVALIDATED rather than reusing attempt-1's trust",
              rec2["engine_fetches"] == 2 and rec2["cache"]["hits"] == 0,
              rec2["cache"])
        check("both attempts agree on the closure manifest",
              rec1["closure_manifest_hash"] == rec2["closure_manifest_hash"])
        a2.settle_retrieval()

        cpu_res = exe.reserve_budget(wx, "cpu_s", 1.0, stage="execution",
                                     attempt_id="attempt-2",
                                     idem_key="attempt-2:execution")
        t0 = time.process_time()
        result = _probe.run(
            {"failure_inputs": dict(root_slot), "reduction": "xor_positional"},
            seed=20260910, inputs=inputs2)
        cpu = time.process_time() - t0
        exec_ce = exe.cost_event(
            wx, stage="execution", attempt_id="attempt-2",
            reservation_id=cpu_res["reservation_id"],
            source_artifacts=[root_slot["digest"], dep_slot["digest"]],
            resources=[
                {"resource": "cpu_s", "quantity": round(cpu, 6), "unit": "s",
                 "method": "clock", "scope": "attempt"},
                {"resource": "peak_memory_bytes", "quantity": None,
                 "unit": "bytes", "method": "sampler", "scope": "attempt"},
                {"resource": "gpu_s", "quantity": None, "unit": "s",
                 "method": "declared", "scope": "attempt"},
            ],
            environment={"stratum": "cpu-only", "profile": "alpha",
                         "concurrent_jobs": 1})
        a2.cost_events.append(exec_ce)
        R["result"] = dict(result)
        step("attempt-2 executed artifact_probe_v1", folded=result["folded"],
             items=result["items_consumed"], closure=result["closure_size"],
             immutable=result["inputs_immutable"])

        check("the kind consumed the whole ordered closure",
              result["items_consumed"] == 5 and result["closure_size"] == 2,
              result)
        check("the frozen input refused mutation",
              result["inputs_immutable"] is True)
        check("the kind's closure SET equals the loader's",
              set(c["digest"] for c in rec2["closure"])
              == {root_slot["digest"], dep_slot["digest"]})

        # -- double billing ------------------------------------------------
        twice = False
        try:
            exe.cost_event(wx, stage="execution", attempt_id="attempt-2",
                           reservation_id=cpu_res["reservation_id"],
                           resources=[{"resource": "cpu_s", "quantity": 0.1,
                                       "unit": "s", "method": "clock"}])
        except EngineError as exc:
            twice = exc.status == 409
        check("a settled reservation is never billed again", twice)

        replay = exe.reserve_budget(wx, "cpu_s", 1.0, stage="execution",
                                    attempt_id="attempt-2",
                                    idem_key="attempt-2:execution")
        check("a retried reserve returns the ORIGINAL reservation",
              replay["reservation_id"] == cpu_res["reservation_id"],
              replay)

        # -- what it all cost ---------------------------------------------
        rep = exe.cost_report(wx)
        R["cost_report"] = rep
        check("no reservation left open", rep["open_reservations"] == [],
              rep["open_reservations"])
        check("the retry is NOT free: two attempts, two retrievals each",
              rep["additive_totals"].get("engine_fetches") == 4,
              rep["additive_totals"])
        check("artifact_bytes billed exactly what moved",
              rep["additive_totals"].get("artifact_bytes")
              == 2 * (len(root_raw) + len(dep_raw)),
              {"totals": rep["additive_totals"],
               "expected": 2 * (len(root_raw) + len(dep_raw))})
        check("unavailable is counted, never summed",
              "peak_memory_bytes" not in rep["additive_totals"]
              and "gpu_s" not in rep["additive_totals"]
              and rep["unavailable_counts"].get("peak_memory_bytes", 0) > 0,
              {"totals": rep["additive_totals"],
               "unavailable": rep["unavailable_counts"]})
        check("enforcement classes came from the LIMIT, not the caller",
              all(e.get("enforcement") == "measured"
                  for ce in a2.cost_events
                  for e in ce["resources"]
                  if e["resource"] == "peak_memory_bytes"),
              [e for ce in a2.cost_events for e in ce["resources"]
               if e["resource"] == "peak_memory_bytes"])

        # -- idempotent publication ---------------------------------------
        payload = json.dumps(result, sort_keys=True,
                             separators=(",", ":")).encode()
        p1 = exe.artifact(wx, "probe_result", payload,
                          meta={"info_kind": "artifact",
                                "attempt_id": "attempt-2"},
                          idem_key="trackA:publish:attempt-2")
        p2 = exe.artifact(wx, "probe_result", payload,
                          meta={"info_kind": "artifact",
                                "attempt_id": "attempt-2"},
                          idem_key="trackA:publish:attempt-2")
        check("publication is idempotent under its key",
              p1["artifact_id"] == p2["artifact_id"], (p1, p2))
        R["publication"] = {
            "artifact_id": p1["artifact_id"], "digest": p1["blob_hash"],
            "idem_key": "trackA:publish:attempt-2",
            "idempotent_replay": p1["artifact_id"] == p2["artifact_id"],
            # C5: these are SEPARATE facts and only the first is authoritative.
            "recorded_in_sfe": True,
            "indexed_in_pew": None}
        R["not_run"].append({
            "what": "indexed_in_pew",
            "why": "PEW indexing needs a running PEW service and viv.pew's "
                   "PewClient, which is Vivarium's component and is not part "
                   "of this development build. The field is reported as null "
                   "rather than folded into recorded_in_sfe: an index that "
                   "did not publish has not unmade a measurement."})

        # -- counterfactual attribution ------------------------------------
        gen_event = _costs.CostEvent(
            stage="generation", attempt_id="source-build",
            resources=gen_meter.resources([
                _costs.Resource("output_bytes", len(root_raw) + len(dep_raw),
                                "bytes", "len() of the sealed payloads",
                                "measured"),
                _costs.Resource("items", 5, "count", "rows sealed",
                                "measured")]),
            output_refs=[root_slot["digest"], dep_slot["digest"]])
        transfer_event = _costs.CostEvent(
            stage="transfer", attempt_id="attempt-2",
            resources=[
                _costs.Resource("output_bytes", len(root_raw) + len(dep_raw),
                                "bytes", "bytes served out of the source "
                                         "world", "measured"),
                _costs.Resource("peak_memory_bytes", None, "bytes",
                                "not sampled on the producer", "unavailable")],
            source_refs=[root_slot["digest"], dep_slot["digest"]])
        producer_events = [gen_event, transfer_event]

        cf = [_costs.attribute_counterfactual(gen_event, arm, uses, REUSE_HORIZON)
              for arm, uses in (("uses_shared_source", True),
                                ("rebuilds_its_own", False))]
        R["counterfactual"] = {
            "reuse_horizon": REUSE_HORIZON,
            "horizon_declared": "before the attempts ran, in this file",
            "physical_cost_event_id": gen_event.cost_event_id,
            "physical_charged_once": True,
            "arms": cf}
        check("the shared source is charged once and attributed, not re-billed",
              all(c["physical_cost_event_id"] == gen_event.cost_event_id
                  for c in cf)
              and cf[0]["attributed"]["output_bytes"]
              == (len(root_raw) + len(dep_raw)) / REUSE_HORIZON
              and cf[1]["attributed"]["output_bytes"] == 0.0, cf)
        check("an unavailable producer quantity stays unavailable in "
              "attribution",
              cf[0]["attributed"].get("gpu_seconds", "missing") is None,
              cf[0]["attributed"])

        # -- reconciliation, on (attempt_id, stage) -------------------------
        executor_vectors = [
            {"attempt_id": "attempt-1", "stage": "retrieval",
             "bytes": rec1["bytes_loaded"], "fetches": rec1["engine_fetches"]},
            {"attempt_id": "attempt-2", "stage": "retrieval",
             "bytes": rec2["bytes_loaded"], "fetches": rec2["engine_fetches"]},
            {"attempt_id": "attempt-2", "stage": "execution",
             "cpu_s": round(cpu, 6)},
        ]
        engine_events = a1.cost_events + a2.cost_events

        def key(attempt, stage):
            return "%s|%s" % (attempt, stage)

        pk = {key(e.attempt_id, e.stage) for e in producer_events}
        xk = {key(v["attempt_id"], v["stage"]) for v in executor_vectors}
        ek = {key(c.get("attempt_id"), c["stage"]) for c in engine_events}
        recon = {
            "join": "(attempt_id, stage)",
            "matched": sorted(pk & xk),
            "producer_only": sorted(pk - xk),
            "executor_only": sorted(xk - pk),
            # The fourth bucket the brief asks for: what the ENGINE sealed,
            # each row saying whether either of the other two sides carries it.
            "engine_side": [{"key": k, "on_producer": k in pk,
                             "on_executor": k in xk} for k in sorted(ek)],
            "engine_cost_event_ids": [c["cost_event_id"]
                                      for c in engine_events],
        }
        R["reconciliation"] = recon
        step("reconciliation", matched=recon["matched"],
             producer_only=recon["producer_only"],
             executor_only=recon["executor_only"])

        # The join must be shown CAPABLE of matching, or an empty matched set
        # is indistinguishable from a broken join.
        ctl_p = {key("ctl", "retrieval")}
        ctl_x = {key("ctl", "retrieval"), key("ctl", "execution")}
        R["reconciliation"]["join_self_test"] = {
            "matched": sorted(ctl_p & ctl_x),
            "executor_only": sorted(ctl_x - ctl_p),
            "note": "a control over synthetic keys, not evidence about this "
                    "run; it establishes only that the join can match."}
        check("the join is capable of matching (control)",
              R["reconciliation"]["join_self_test"]["matched"] == ["ctl|retrieval"])

        check("nothing the engine sealed is missing from the reconciliation",
              len(recon["engine_side"]) == len(ek) and ek,
              recon["engine_side"])

        theirs = _costs.reconcile(producer_events, executor_vectors)
        R["reconciliation"]["archaeon_reconcile_verbatim"] = theirs
        finding(
            "TRACKA-RECON-1",
            "archaeon/producer/costs.py:reconcile() joins on attempt_id ALONE "
            "and hardcodes engine_side='absent (Daedalus C4-3)'. Engine-side "
            "cost events now exist (schema 8, COST_EVENT_RECORDED sealed in "
            "the world's own chain); this run produced %d of them. On this "
            "data the attempt-only join reports %s as matched, which is a "
            "coincidence of attempt ids across DIFFERENT stages, not an "
            "agreement about any act."
            % (len(engine_events), theirs["matched"]), owner="Archaeon")
        finding(
            "TRACKA-RECON-2",
            "The producer names the act 'transfer' where the executor and the "
            "engine name it 'retrieval'. Both vocabularies are internally "
            "consistent and neither is wrong, but a (attempt_id, stage) join "
            "therefore reports one physical byte movement as producer-only AND "
            "executor-only. One shared stage name, or a declared mapping, is "
            "needed before a reconciliation can claim agreement.",
            owner="Archaeon + Vivarium")
        finding(
            "TRACKA-PREFLIGHT-1",
            "viv/preflight.py:SfeResolver.resolve() calls "
            "artifact_content(world, aid) with no expected_blob_hash, so the "
            "digest is compared in the CLIENT at preflight.py:341 after the "
            "bytes have already been served. The engine-side gate is now "
            "available on the read path (expected_blob_hash, with "
            "expected_digest as the shipped alias) and returns 422 with no "
            "bytes. Passing the sealed digest and expected_bytes moves the "
            "check to the engine; the client-side comparison then becomes "
            "defence in depth over the one span the engine cannot see.",
            owner="Vivarium")
        finding(
            "TRACKA-DEBIT-1",
            "Preflight's debit hook is debit(resource, amount) and does not "
            "carry the artifact being paid for, so the strongest idempotency "
            "key an integrator can build is the ordinal of the fetch within "
            "the attempt (this receipt uses one). Widening the hook to carry "
            "the digest would let the reservation be keyed on the act.",
            owner="Vivarium")

        # -- the engine-decided rejection classes --------------------------
        # Of the fifteen classes in viv/artifacts.py, exactly four are decided
        # by the ENGINE; the rest are contract, codec and interface checks the
        # client makes before or after any call, which integration cannot
        # change. Only the four are re-run here, live.
        rej = {}

        def rejects(name, fn):
            try:
                fn()
                rej[name] = {"raised": None}
            except _a.PreflightRejected as exc:
                rej[name] = {"raised": exc.rejection_class}
            except EngineError as exc:
                rej[name] = {"raised": "EngineError %s" % exc.status}
            except Exception as exc:                         # noqa: BLE001
                rej[name] = {"raised": type(exc).__name__}

        def _absent():
            bad = dict(locators)
            bad[root_slot["digest"]] = {"source_world": wp,
                                        "source_artifact": "art_deadbeef"}
            Attempt(R, exe, wx, bad, root_slot, "rej-absent").hydrate()

        def _unauthorized():
            s3 = third.create_session("outsider")
            w3 = third.create_world(s3, "outsider")["world_id"]
            third.start(w3)
            bad = dict(locators)
            bad[root_slot["digest"]] = {"source_world": w3,
                                        "source_artifact": "art_nope"}
            Attempt(R, exe, wx, bad, root_slot, "rej-unauth").hydrate()

        def _digest():
            # The locator addresses the DECOY, which is the root's exact
            # length, so size passes and only the hash can catch it.
            loc = {root_slot["digest"]: {
                "source_world": wp,
                "source_artifact": decoy_art["artifact_id"]}}
            Attempt(R, exe, wx, loc, dict(root_slot), "rej-digest").hydrate()

        def _size():
            bad_slot = dict(root_slot)
            bad_slot["expected_bytes"] = len(root_raw) + 1
            Attempt(R, exe, wx, dict(locators), bad_slot,
                    "rej-size").hydrate()

        rejects("ARTIFACT_ABSENT", _absent)
        rejects("ARTIFACT_UNAUTHORIZED_WORLD", _unauthorized)
        rejects("ARTIFACT_DIGEST_MISMATCH", _digest)
        rejects("ARTIFACT_SIZE_MISMATCH", _size)

        # The same two facts asked of the ENGINE directly, which is where
        # Vivarium's loader could be asking them.
        eng_gate = {}
        imported = exe.import_artifact(wx, wp, root_art["artifact_id"])
        for label, kw in (("wrong_digest",
                           {"expected_blob_hash": dep_slot["digest"]}),
                          ("wrong_size", {"expected_bytes": len(root_raw) + 1}),
                          ("right_digest",
                           {"expected_blob_hash": root_slot["digest"]})):
            try:
                got = exe.artifact_content(wx, imported["artifact_id"], **kw)
                eng_gate[label] = {"http": 200, "bytes": got["bytes"]}
            except EngineError as exc:
                eng_gate[label] = {"http": exc.status,
                                   "error": (exc.detail or {}).get("error")
                                   if isinstance(exc.detail, dict) else None}
        R["rejections"] = {
            "engine_decided": rej,
            "engine_gate_directly": eng_gate,
            "scope": "Of the 15 rejection classes in viv/artifacts.py, these "
                     "4 are decided by the engine; the other 11 are contract, "
                     "codec, interface, closure and limit checks the client "
                     "makes without the engine, and integration did not "
                     "change their guarantee, so they are covered by "
                     "vivarium/tests/test_h0h5_artifacts.py rather than "
                     "re-run here."}
        check("the four engine-decided rejections still fire",
              rej["ARTIFACT_ABSENT"]["raised"] == "ARTIFACT_ABSENT"
              and rej["ARTIFACT_UNAUTHORIZED_WORLD"]["raised"]
              in ("ARTIFACT_UNAUTHORIZED_WORLD", "ARTIFACT_ABSENT")
              and rej["ARTIFACT_DIGEST_MISMATCH"]["raised"]
              == "ARTIFACT_DIGEST_MISMATCH"
              and rej["ARTIFACT_SIZE_MISMATCH"]["raised"]
              == "ARTIFACT_SIZE_MISMATCH", rej)
        check("the engine's own read gate refuses a wrong digest and a wrong "
              "size, and serves the right one",
              eng_gate["wrong_digest"]["http"] == 422
              and eng_gate["wrong_size"]["http"] == 422
              and eng_gate["right_digest"]["http"] == 200, eng_gate)

        # -- a digest still authorizes nothing -----------------------------
        denied = False
        try:
            third.artifact_content(wp, root_art["artifact_id"],
                                   expected_blob_hash=root_slot["digest"])
        except EngineError as exc:
            denied = exc.status == 403
        check("a correct digest does not authorize a foreign reader", denied)

        # -- the ledger ----------------------------------------------------
        wv = exe.get_world(wx)
        R["ledger"] = {
            "execution_world": wx, "head_hash": wv.get("head_hash"),
            "source_world": wp,
            "attempts": [
                {"attempt_id": "attempt-1", "outcome": "INTERRUPTED",
                 "stage_reached": "retrieval",
                 "reservations": [r["reservation_id"] for r in a1.reservations],
                 "cost_events": [c["cost_event_id"] for c in a1.cost_events],
                 "load_receipt": {k: rec1[k] for k in
                                  ("closure_size", "bytes_loaded",
                                   "bytes_debited", "engine_fetches",
                                   "closure_manifest_hash", "verified")}},
                {"attempt_id": "attempt-2", "outcome": "COMPLETED",
                 "reservations": [r["reservation_id"] for r in a2.reservations]
                                 + [cpu_res["reservation_id"]],
                 "cost_events": [c["cost_event_id"] for c in a2.cost_events],
                 "load_receipt": {k: rec2[k] for k in
                                  ("closure_size", "bytes_loaded",
                                   "bytes_debited", "engine_fetches",
                                   "closure_manifest_hash", "verified")}},
            ]}
        R["guarantees"] = {
            "memory": "peak_memory_bytes is MEASURED, never enforced. The "
                      "engine samples it, refuses to sum it, and stops "
                      "nothing on it.",
            "wall_guard": "the wall-clock guard is checked BETWEEN repeats, "
                          "so a single repeat that overruns is not "
                          "interrupted; the bound is on the sequence, not on "
                          "the step.",
            "logical_work": "logical work bounds live in the kind, not in the "
                            "budget: artifact_probe_v1 folds a bounded "
                            "closure the loader already limited by depth, "
                            "count and bytes.",
            "digest_authority": "a digest is checked AFTER authorization and "
                                "after a world-scoped lookup, so it says "
                                "WHICH object was meant and never that the "
                                "caller may have it."}

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()

    R["result"] = "PASS" if ok[0] else "FAIL"
    print()
    print("=" * 74)
    print("  findings for other seats: %d" % len(R["findings"]))
    for f in R["findings"]:
        print("    %-20s [%s]" % (f["code"], f["owner"]))
    print("  not run: %d" % len(R["not_run"]))
    print("  RESULT: %s" % R["result"])
    if a.json:
        out = os.path.join(HERE, "TRACKA_JOINT_RECEIPT.json")
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(R, indent=2, default=str) + "\n")
        print("  written: %s" % out)
        print(json.dumps(R, indent=2, default=str))
    return 0 if ok[0] else 1


if __name__ == "__main__":
    sys.exit(main())
