"""Witness evaluator: committed bundles -> P-FLAT, binding, custody, artifact re-hash, predicates, outcome class
per subject (C-010-T012; PREREGISTRATION s5-s7).

    python -B -m rso.witness.evaluate BUNDLE_DIR [BUNDLE_DIR ...] --subjects S4=<sha256> S15=<sha256>
        [--primary S4] --seeds SEED_LISTS.json --first-check UTC   (custody read from the live keeper store)

Nothing a producer computed is trusted. From each bundle (run_witness.py layout: MANIFEST.json, inventory.json,
run.json, receipts/R###.json, artifacts/<sha256>) the evaluator reads only:
  - the launch the manifest names, the inventory rows, and each receipt's canonical bytes;
  - each artifact the receipt lists (role, sha256, length, dtype, shape), re-hashed and decoded here;
  - the seeds and arm/predicate/subject identity each receipt declares (bound by its digest), never a count,
    accuracy, decision or outcome.
It recomputes the world's oracle (r and the interrupt steps) from the seeds by running the W15 world alone (no
organism), every episode decision and count from the action bytes, and every gate and class with
rso/witness/ruler.py.

Bundle checks (a failing bundle is REFUSED: every claim resting on it is UNQUALIFIED, never a negative result):
  P-FLAT     every RECEIPT row's parent_run_id is the anchored launch; every COMPLETED RECEIPT row carries
             receipt_sha256; no node id has two RECEIPT rows (rso/binding/CLOSURE.md scope)
  launch     run.json names the manifest's launch; the launch is one TOP_LEVEL row, COMPLETED (BX1)
  binding    each receipt's row binds it (BX2: RECEIPT, the launch's, COMPLETED, its node id, its digest) and every
             COMPLETED node row of the launch is presented (BX5)
  artifacts  every listed artifact exists, re-hashes to its sha256 and length, decodes to its dtype and shape
  oracle     the reported regimes / interrupt steps equal the world's for the declared seeds and the arm's mode
  custody    manifest and inventory registered with the keeper (EVIDENCE_MANIFEST, RUN_INVENTORY) before the first
             check (CONTRACT s6); keeper store errors are never a pass

C-010-T031 repair round (rso/witness/ADJUDICATION_W1.md):
  R1  a node id presented by more than one bundle is EVIDENCE_DUPLICATE (refused; no argument-order resolution);
      the RESULT's supplied_by names the launch of every node used
  R2  the registered seed lists are REQUIRED (make_configs SEED_LISTS.json "seeds": witness, erase, pres): P-RET,
      P-CHAN, the P-CAL arms and P-OBS on the witness list exactly (P-OBS: every witness seed, s5);
      P-ERASE on the erase list (S and S-LEAK alike); P-PRES on the pres list. A mismatch refuses the node
  R3  P-ERASE triples have world regimes (pre_a, pre_b) = (0, 1) and S / S-LEAK run identical triples; a P-PRES
      warm-up draws the regime opposite to its seed's (ERASE_PROBES.md); else the node is refused
  R4  the node id is rebuilt from the receipt's own subject digest, arm, predicate and world and must equal the
      manifest's (and so the subject the node is filed under)

Registered node map (one node per (subject, arm, predicate); ares_client.node_id over world W15):
  per subject X:  S/P-RET  S-NOPL/P-CHAN  S/P-OBS  S/P-PRES  S/P-ERASE  S-LEAK/P-ERASE
  shared (on the PRIMARY subject's digest):  NULL/P-CAL  SHUF/P-CAL  POS/P-CAL
A missing node is EVIDENCE_MISSING (UNQUALIFIED for the subjects that need it); a node in a refused bundle is
EVIDENCE_REFUSED. Each subject's P-RET node is one organism (actions shape (n, 40, 1)); anything else is refused
for that subject (SHAPE).

Outcome class per subject (PREREGISTRATION s6, plus s5's UNQUALIFIED for refused or missing evidence):
  UNQUALIFIED                        evidence refused (P-FLAT, binding, artifacts, oracle, custody) or missing,
                                     seed list not the registered one, wrong shape
  DETECTION_UNQUALIFIED              P-CAL / P-OBS / P-PRES FAIL, P-ERASE not separating, or P-RET INDETERMINATE /
                                     NOT_SHOWN
  POSITIVE                           qualified, P-RET POSITIVE, P-CHAN PASS
  POSITIVE (channel unidentified)    qualified, P-RET POSITIVE, P-CHAN FAIL
  NEGATIVE                           qualified, P-RET NEGATIVE
The RESULT record is canonical JSON (receipt.canonical_bytes: no floats). Python >= 3.8; numpy (ares).
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

from rso.binding import binding as B
from rso.slice001 import evidence as EV
from rso.slice001 import receipt as R
from rso.witness import ares_client as AC
from rso.witness import ruler as RU

RESULT_SCHEMA = "rso.witness.result.v0"
WORLD = "W15"
T = 40
ARM_MODE = {"SHUF": "shuffled"}                       # every other arm runs W15 "present" (PREREGISTRATION s4)
DTYPES = ("int8",)
ARRAY_ROLES = {"P-OBS": ("trace:actions_record", "trace:actions_norecord"),
               "P-PRES": ("trace:pres_warm", "trace:pres_fresh"),
               "P-ERASE": ("trace:probe_after_a", "trace:probe_after_b")}
SUBJECT_NODES = (("S", "P-RET"), ("S-NOPL", "P-CHAN"), ("S", "P-OBS"), ("S", "P-PRES"), ("S", "P-ERASE"),
                 ("S-LEAK", "P-ERASE"))
SHARED_NODES = (("NULL", "P-CAL"), ("SHUF", "P-CAL"), ("POS", "P-CAL"))
CLASSES = ("POSITIVE", "POSITIVE (channel unidentified)", "NEGATIVE", "DETECTION_UNQUALIFIED", "UNQUALIFIED")


class Refused(Exception):
    """Evidence that cannot be evaluated. str() is the typed reason (CODE:detail)."""


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _read(root, rel):
    p = os.path.join(root, *rel.split("/"))
    if not os.path.isfile(p):
        raise Refused("BUNDLE_FILE_MISSING:%s" % rel)
    with open(p, "rb") as f:
        return f.read()


def _json(data, what):
    try:
        return json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        raise Refused("NOT_JSON:%s:%s" % (what, e))


# --------------------------------------------------------------------------------------------------------
# Artifacts and the world's oracle

def decode(root, listing):
    """The artifact a receipt lists, re-hashed against its sha256 and length and decoded to its dtype and shape."""
    for k in ("role", "sha256", "length", "dtype", "shape"):
        if k not in listing:
            raise Refused("ARTIFACT_LISTING:%s:%s" % (listing.get("role"), k))
    data = _read(root, "artifacts/" + listing["sha256"])
    if _sha(data) != listing["sha256"] or len(data) != listing["length"]:
        raise Refused("ARTIFACT_MISMATCH:%s" % listing["role"])
    if listing["dtype"] == "json":
        obj = _json(data, listing["role"])
        if not isinstance(obj, list) or [len(obj)] != list(listing["shape"]):
            raise Refused("SHAPE:%s" % listing["role"])
        return obj
    if listing["dtype"] not in DTYPES:
        raise Refused("DTYPE:%s:%s" % (listing["role"], listing["dtype"]))
    shape = [int(x) for x in listing["shape"]]
    arr = np.frombuffer(data, dtype=np.dtype(listing["dtype"]))
    if arr.size != int(np.prod(shape)) if shape else arr.size != 1:
        raise Refused("SHAPE:%s" % listing["role"])
    return arr.reshape(shape)


_ORACLE = {}


def world_oracle(seeds, mode):
    """[(r, sorted interrupt steps)] per seed, from the W15 world alone (no organism), cached."""
    key = (tuple(seeds), mode)
    if key not in _ORACLE:
        w = AC.world(WORLD, mode)
        out = []
        for s in seeds:
            w.reset(np.random.default_rng(int(s)), 1)
            out.append((int(w.r), sorted(int(x) for x in getattr(w, "reset_steps", ()))))
        _ORACLE[key] = out
    return _ORACLE[key]


def _check_oracle(rec, data):
    """The receipt's oracle artifacts equal the world's for its declared seeds and its arm's mode."""
    mode = ARM_MODE.get(rec["arm"], "present")
    if rec.get("world") != {"name": WORLD, "mode": mode}:
        raise Refused("ORACLE_MISMATCH:%s:world/mode" % rec["node_id"])
    seeds = [int(s) for s in rec["seeds"]]
    regs = data.get("oracle:regimes")
    if rec["predicate"] in ("P-ERASE", "P-PRES"):
        k = 3 if rec["predicate"] == "P-ERASE" else 2
        want = [[r for r, _ in world_oracle(seeds[i:i + k], mode)] for i in range(0, len(seeds), k)]
        if regs is None or regs.tolist() != want:
            raise Refused("ORACLE_MISMATCH:%s:regimes" % rec["node_id"])
        return
    truth = world_oracle(seeds, mode)
    if regs is None or regs.tolist() != [r for r, _ in truth]:
        raise Refused("ORACLE_MISMATCH:%s:regimes" % rec["node_id"])
    if data.get("oracle:reset_steps") != [st for _, st in truth]:
        raise Refused("ORACLE_MISMATCH:%s:reset_steps" % rec["node_id"])


# --------------------------------------------------------------------------------------------------------
# Bundle checks

def _rebuilt_node_id(rec):
    """R4: the node id the receipt's own fields name (subject digest, arm, predicate, world)."""
    try:
        return AC.node_id(rec["subject"]["genome_sha256"], rec["arm"], rec["predicate"], rec["world"]["name"])
    except (KeyError, TypeError):
        return None


def p_flat(runs, launch):
    """The flat-inventory scope of the binding (CLOSURE.md): [] when it holds, else typed reasons."""
    why, seen = [], {}
    for r in runs:
        if r.get("launch_kind") != B.RECEIPT:
            continue
        if r.get("parent_run_id") != launch:
            why.append("P-FLAT:NESTED_OR_FOREIGN_PARENT:%s" % r.get("run_id"))
        if r.get("status") == B.COMPLETED and not r.get("receipt_sha256"):
            why.append("P-FLAT:DIGESTLESS_COMPLETED_ROW:%s" % r.get("run_id"))
        seen[r.get("node_id")] = seen.get(r.get("node_id"), 0) + 1
    why.extend("P-FLAT:DUPLICATE_NODE:%s" % n for n, k in sorted(seen.items(), key=lambda kv: str(kv[0])) if k > 1)
    return why


def witness_custody(store, manifest_bytes, inventory_bytes, first_check_utc):
    """Custody of a witness bundle: its manifest and inventory blobs registered before the first check."""
    rows, err = EV.store_rows(store)
    if err is not None:
        return {"status": "UNQUALIFIED", "why": [err.code]}
    why, used = set(), []
    for kind, blob in (("EVIDENCE_MANIFEST", _sha(manifest_bytes)), ("RUN_INVENTORY", _sha(inventory_bytes))):
        of_kind = [r for r in rows if r["record_kind"] == kind]
        match = [r for r in of_kind if r["blob_sha256"] == blob]
        if not of_kind:
            why.add("KEEPER_ROW_MISSING:%s" % kind)
        elif not match:
            why.add("ROW_BLOB_MISMATCH")
        else:
            used.append(match[0])
            if not EV.utc_key(match[0]["registered_at_utc"]) < EV.utc_key(first_check_utc):
                why.add("REGISTERED_AFTER_CHECK")
    if why:
        return {"status": "UNQUALIFIED", "why": sorted(why)}
    return {"status": "QUALIFIED", "rows": sorted(str(r.get("row_id")) for r in used)}


def check_bundle(root, store, first_check_utc):
    """{launch_run_id, p_flat, custody, refused, nodes}. nodes (node id -> {receipt, data}) only when nothing is
    refused and custody is QUALIFIED; `node_ids` lists every node the bundle presents either way."""
    out = {"bundle": os.path.basename(os.path.normpath(root)), "launch_run_id": None, "p_flat": None,
           "custody": None, "refused": [], "nodes": {}, "node_ids": []}
    try:
        man_bytes, inv_bytes = _read(root, "MANIFEST.json"), _read(root, "inventory.json")
        man, inv = _json(man_bytes, "MANIFEST.json"), _json(inv_bytes, "inventory.json")
        run = _json(_read(root, "run.json"), "run.json")
        launch = man.get("launch_run_id")
        out["launch_run_id"] = launch
        out["custody"] = witness_custody(store, man_bytes, inv_bytes, first_check_utc)
        rows = inv.get("rows") if isinstance(inv, dict) else None
        if not isinstance(rows, list) or not EV.inventory_terminal(rows):
            raise Refused("INVENTORY_NOT_TERMINAL")
        runs = rows[:-1]
        flat = p_flat(runs, launch)
        out["p_flat"] = {"value": "FAIL" if flat else "PASS", "why": flat}
        out["refused"].extend(flat)
        if run.get("run_id") != launch:
            out["refused"].append("LAUNCH_UNBOUND:run.json names %s" % run.get("run_id"))
        out["refused"].extend("LAUNCH:%s" % w for w in B.launch_reasons(runs, launch))
        nodes, presented = {}, set()
        for entry in man.get("nodes", []):
            nid = entry.get("node_id")
            data = _read(root, entry.get("receipt_file", ""))
            rec = _json(data, entry.get("receipt_file"))
            out["node_ids"].append(nid)
            if not isinstance(rec, dict) or rec.get("node_id") != nid:
                out["refused"].append("NODE_ID_MISMATCH:%s" % nid)
                continue
            presented.add(nid)
            cited = [r for r in runs if r.get("launch_kind") == B.RECEIPT and r.get("node_id") == nid]
            run_id = cited[0].get("run_id") if len(cited) == 1 else None
            why = B.binding_reasons(nid, run_id, data, runs, launch)
            if why:
                out["refused"].append("BIND:%s:%s" % (nid, ",".join(why)))
                continue
            if _rebuilt_node_id(rec) != nid:                              # R4
                out["refused"].append("NODE_ID_FIELDS:%s:receipt fields give %s" % (nid, _rebuilt_node_id(rec)))
                continue
            arts = {}
            for listing in list(rec.get("outputs", [])) + list(rec.get("oracle", [])):
                arts[listing.get("role")] = decode(root, listing)
            _check_oracle(rec, arts)
            nodes[nid] = {"receipt": rec, "data": arts}
        for r in B.own_launch_rows(runs, launch):
            if r.get("status") == B.COMPLETED and r.get("node_id") not in presented:
                out["refused"].append("RUN_UNREPORTED:%s" % r.get("run_id"))
    except Refused as e:
        out["refused"].append(str(e))
        nodes = {}
    if out["custody"] is not None and out["custody"]["status"] != "QUALIFIED":
        out["refused"].append("CUSTODY_UNQUALIFIED")
    if not out["refused"]:
        out["nodes"] = nodes
    return out


# --------------------------------------------------------------------------------------------------------
# Predicates from bytes

def _node(pool, refused_ids, digest, arm, predicate, lists):
    """The registered node, checked against its registered seed list (R2); typed refusal otherwise."""
    nid = AC.node_id(digest, arm, predicate, WORLD)
    if nid in pool:
        node = pool[nid]
        _check_seeds(node, lists)
        return node
    if isinstance(refused_ids, dict) and nid in refused_ids:
        raise Refused(refused_ids[nid])
    raise Refused(("EVIDENCE_REFUSED:%s" if nid in refused_ids else "EVIDENCE_MISSING:%s") % nid)


def _check_seeds(node, lists):
    """R2: the node ran on the registered list for its predicate."""
    rec = node["receipt"]
    seeds = [int(s) for s in rec["seeds"]]
    pred = rec["predicate"]
    if pred == "P-ERASE":
        ok = seeds == lists["erase"]
    elif pred == "P-PRES":
        ok = seeds == lists["pres"]
    else:                    # P-RET, P-CHAN, the P-CAL arms and P-OBS ("every witness seed", PREREGISTRATION s5;
        ok = seeds == lists["witness"]   # FD-T031-W1 prefix reading not taken at integration, C-010-T033)
    if not ok:
        raise Refused("SEEDS_NOT_REGISTERED:%s (%s)" % (rec["node_id"], pred))


def _check_probe_shape(node):
    """R3: P-ERASE (pre_a, pre_b) regimes (0, 1) per triple; P-PRES warm-up regime opposite to the seed's. Regimes
    from the world alone (world_oracle), never the receipt."""
    rec = node["receipt"]
    seeds = [int(s) for s in rec["seeds"]]
    truth = [r for r, _ in world_oracle(seeds, ARM_MODE.get(rec["arm"], "present"))]
    if rec["predicate"] == "P-ERASE":
        if len(truth) % 3 or any((truth[i], truth[i + 1]) != (0, 1) for i in range(0, len(truth), 3)):
            raise Refused("ERASE_SHAPE:%s: a triple's (pre_a, pre_b) regimes are not (0, 1)" % rec["node_id"])
    elif rec["predicate"] == "P-PRES":
        if len(truth) % 2 or any(truth[i] == truth[i + 1] for i in range(0, len(truth), 2)):
            raise Refused("PRES_SHAPE:%s: a warm-up draws the same regime as its seed" % rec["node_id"])


def _validate_lists(seed_lists):
    if not isinstance(seed_lists, dict):
        raise ValueError("seed_lists must be the SEED_LISTS.json 'seeds' object {witness, erase, pres}")
    out = {}
    for k in ("witness", "erase", "pres"):
        v = seed_lists.get(k)
        if not isinstance(v, list) or not v or not all(isinstance(x, int) and not isinstance(x, bool) for x in v):
            raise ValueError("seed_lists[%r] must be a non-empty list of integers" % k)
        out[k] = list(v)
    return out


def episodes(node):
    """[(r, decision)] for a ruler node: one organism, decision = majority action after the LAST interrupt, r and
    the interrupt steps recomputed from the world (checked equal to the receipt's oracle in check_bundle)."""
    rec, data = node["receipt"], node["data"]
    seeds = [int(s) for s in rec["seeds"]]
    acts = data.get("trace:actions")
    if acts is None or acts.ndim != 3 or acts.shape != (len(seeds), T, 1):
        raise Refused("SHAPE:%s:trace:actions must be (n, %d, 1)" % (rec["node_id"], T))
    truth = world_oracle(seeds, ARM_MODE.get(rec["arm"], "present"))
    out = []
    for e, (r, steps) in enumerate(truth):
        last = max(steps) if steps else -1
        out.append((r, RU.episode_decision([int(a) for a in acts[e, :, 0]], last)))
    return out


def _pair_gate(node, roles):
    a, b = node["data"].get(roles[0]), node["data"].get(roles[1])
    if a is None or b is None or a.shape != b.shape:
        raise Refused("SHAPE:%s:%s" % (node["receipt"]["node_id"], "/".join(roles)))
    return int(np.count_nonzero(a != b))


def _gate(pid, value, reason, witness=None, **extra):
    g = {"kind": "GATE", "predicate": pid, "value": value, "reason": reason, "witness": witness}
    g.update(extra)
    return g


def _p_cal(pool, refused_ids, primary_digest, lists):
    try:
        eps = [episodes(_node(pool, refused_ids, primary_digest, arm, "P-CAL", lists)) for arm in ("NULL", "SHUF", "POS")]
        return RU.p_cal(*eps)
    except (Refused, RU.RulerError) as e:
        return _gate("P-CAL", "BLOCKED", str(e))


def evaluate_subject(pool, refused_ids, digest, p_cal, lists):
    """The subject's gates and outcome class (PREREGISTRATION s6; s5 UNQUALIFIED for refused evidence)."""
    res = {"digest": digest}
    try:
        n = {k: _node(pool, refused_ids, digest, k[0], k[1], lists) for k in SUBJECT_NODES}
        for k in (("S", "P-ERASE"), ("S-LEAK", "P-ERASE"), ("S", "P-PRES")):
            _check_probe_shape(n[k])                                      # R3
        if n[("S", "P-ERASE")]["receipt"]["seeds"] != n[("S-LEAK", "P-ERASE")]["receipt"]["seeds"]:
            raise Refused("ERASE_SHAPE:S and S-LEAK did not run identical triples")
        if p_cal["value"] == "BLOCKED":
            raise Refused("P-CAL BLOCKED: %s" % p_cal["reason"])
        ret_eps = episodes(n[("S", "P-RET")])
        res["P-RET"] = RU.p_ret(ret_eps)
        d_obs = _pair_gate(n[("S", "P-OBS")], ARRAY_ROLES["P-OBS"])
        res["P-OBS"] = _gate("P-OBS", "PASS" if d_obs == 0 else "FAIL", "%d differing actions" % d_obs, differing=d_obs)
        d_pres = _pair_gate(n[("S", "P-PRES")], ARRAY_ROLES["P-PRES"])
        res["P-PRES"] = _gate("P-PRES", "PASS" if d_pres == 0 else "FAIL", "%d differing actions" % d_pres,
                              differing=d_pres)
        d_x = _pair_gate(n[("S", "P-ERASE")], ARRAY_ROLES["P-ERASE"])
        d_leak = _pair_gate(n[("S-LEAK", "P-ERASE")], ARRAY_ROLES["P-ERASE"])
        erase = "PASS" if d_x == 0 else "FAIL"
        res["P-ERASE"] = _gate("P-ERASE", erase, "subject D = %d, leak D = %d" % (d_x, d_leak), D=d_x, D_leak=d_leak,
                               qualified=d_leak > 0)
        if res["P-RET"]["value"] == "POSITIVE":
            nopl = n[("S-NOPL", "P-CHAN")]
            if [int(s) for s in nopl["receipt"]["seeds"]] != [int(s) for s in n[("S", "P-RET")]["receipt"]["seeds"]]:
                res["P-CHAN"] = _gate("P-CHAN", "FAIL", "X-NOPL did not run on X's seeds in X's order",
                                      {"why": "SEEDS_NOT_PAIRED"})
            else:
                nopl_eps = episodes(nopl)
                res["P-CHAN"] = RU.p_chan([(r, dx, dn) for (r, dx), (_r, dn) in zip(ret_eps, nopl_eps)])
    except (Refused, RU.RulerError) as e:
        res.update({"class": "UNQUALIFIED", "why": [str(e)]})
        return res
    why = []
    if p_cal["value"] != "PASS":
        why.append("P-CAL %s: %s" % (p_cal["value"], p_cal["reason"]))
    for g in ("P-OBS", "P-PRES"):
        if res[g]["value"] != "PASS":
            why.append("%s FAIL: %s" % (g, res[g]["reason"]))
    if res["P-ERASE"]["value"] != "PASS":
        why.append("P-ERASE FAIL: %s" % res["P-ERASE"]["reason"])
    elif not res["P-ERASE"]["qualified"]:
        why.append("P-ERASE DETECTION_UNQUALIFIED: the leak member shows D = 0")
    ret = res["P-RET"]["value"]
    if why or ret in ("INDETERMINATE", "NOT_SHOWN"):
        if ret in ("INDETERMINATE", "NOT_SHOWN"):
            why.append("P-RET %s" % ret)
        res.update({"class": "DETECTION_UNQUALIFIED", "why": why})
    elif ret == "POSITIVE":
        res.update({"class": "POSITIVE" if res["P-CHAN"]["value"] == "PASS" else "POSITIVE (channel unidentified)",
                    "why": [] if res["P-CHAN"]["value"] == "PASS" else ["P-CHAN FAIL: %s" % res["P-CHAN"]["reason"]]})
    else:
        res.update({"class": "NEGATIVE", "why": []})
    return res


def evaluate(bundle_roots, store, first_check_utc, subjects, primary, seed_lists=None):
    """RESULT for the registered subjects ({name: genome sha256}); `primary` names the subject whose digest the
    shared P-CAL arms carry; `seed_lists` is REQUIRED (R2): the SEED_LISTS.json "seeds" object. Pure: reads bundles
    and the keeper store, writes nothing."""
    if seed_lists is None:
        raise TypeError("evaluate: seed_lists is required (make_configs SEED_LISTS.json 'seeds'; ADJUDICATION_W1 R2)")
    lists = _validate_lists(seed_lists)
    checks = [check_bundle(r, store, first_check_utc) for r in bundle_roots]
    presented = {}
    for c in checks:
        for nid in set(c["node_ids"]):
            presented.setdefault(nid, []).append(c["launch_run_id"])
    refused_ids, pool, supplied = {}, {}, {}
    for nid, launches in sorted(presented.items(), key=lambda kv: str(kv[0])):
        if len(launches) > 1:                                             # R1
            refused_ids[nid] = "EVIDENCE_DUPLICATE:%s presented by %d bundles (%s)" % (
                nid, len(launches), ", ".join(sorted(str(x) for x in launches)))
    for c in checks:
        for nid in set(c["node_ids"]):
            if nid in refused_ids:
                continue
            if c["refused"]:
                refused_ids[nid] = "EVIDENCE_REFUSED:%s" % nid
            elif nid in c["nodes"]:
                pool[nid] = c["nodes"][nid]
                supplied[nid] = c["launch_run_id"]
    p_cal = _p_cal(pool, refused_ids, subjects[primary], lists)
    return {"schema": RESULT_SCHEMA, "world": WORLD, "primary": primary, "first_check_utc": first_check_utc,
            "P-CAL": p_cal,
            "subjects": {name: evaluate_subject(pool, refused_ids, d, p_cal, lists)
                         for name, d in sorted(subjects.items())},
            "supplied_by": {nid: supplied[nid] for nid in sorted(supplied)},
            "bundles": [{k: c[k] for k in ("bundle", "launch_run_id", "p_flat", "custody", "refused")}
                        for c in checks]}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -B -m rso.witness.evaluate")
    ap.add_argument("bundles", nargs="+")
    ap.add_argument("--subjects", nargs="+", required=True, help="NAME=sha256 ...")
    ap.add_argument("--primary", default="S4")
    ap.add_argument("--seeds", required=True, help="make_configs SEED_LISTS.json (its 'seeds': witness, erase, pres)")
    ap.add_argument("--first-check", required=True)
    a = ap.parse_args(argv)
    subjects = dict(s.split("=", 1) for s in a.subjects)
    with open(a.seeds, "rb") as f:
        doc = json.loads(f.read())
    seeds = doc.get("seeds", doc) if isinstance(doc, dict) else doc
    store = EV.store_from_contract({"store": EV.REGISTRY_LOCATOR})
    res = evaluate(a.bundles, store, a.first_check, subjects, a.primary, seeds)
    sys.stdout.write(R.canonical_bytes(res).decode("utf-8") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
