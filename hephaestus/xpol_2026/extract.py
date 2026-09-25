"""EXTRACT the replay set from the frozen 1.0 cross-pollination corpus. Read-only over
agents/nous/ and agents/hephaestus/; writes only packets/selection.json and
packets/INDEX.md beside this file.

Selection lenses (preregistered here, before any new-model call). "Interesting" has
no recorded operator list, so it is approximated by six measurable lenses over the
frozen record; every packet carries the lens(es) that admitted it.

  L1 honest_forged      forged on the 186-trap ruler (ledger ts >= 2026-04-01): ALL
  L2 march_forged_acc50 forged in the 15-trap era with acc >= 0.50: ALL (certificates
                        known vacuous -- Necropolis 2026-09-10 -- kept because they are
                        the "results" of the original experiment)
  L3 nearmiss_acc50     scrapped with trap_battery_failed acc >= 50 % on the honest
                        ruler: top 30 by (acc, cal)
  L4 novelty70          behavioural-novelty score >= 0.70 (novelty_scores.json): ALL
  L5 nous_unforged_top  Nous 'novel', implementability >= 9, never fairly attempted
                        (absent from ledger or api_call_failed): top 20 by composite
  L6 nous_composite_top Nous composite >= 8.0 not already admitted: top 10 by composite

Per packet: the era-matched Nous prompt is RECONSTRUCTED verbatim (template + the
concept descriptions as of the run's commit), the original Nous analysis and ratings,
the ledger outcome, the original code file (path + sha256) when it exists, and the
code-gen template era + frame the original forge used.

Run from the worktree root: python hephaestus/xpol_2026/extract.py
"""
from __future__ import annotations
import ast, collections, glob, hashlib, json, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.chdir(ROOT)
TPL = HERE / "templates"
OUT = HERE / "packets"
OUT.mkdir(exist_ok=True)

# concept dictionaries as of the Nous run's commit (descriptions changed over time)
CONCEPT_COMMITS = [("2026-03-24T00:00:00", "2f3e4eb6f"), ("2026-03-25T00:00:00", "2a186ba24"), ("2026-03-28T00:00:00", "302c002d3")]


def concepts_at(commit: str) -> dict[str, dict]:
    src = subprocess.run(["git", "show", f"{commit}:agents/nous/src/concepts.py"], capture_output=True, text=True, timeout=60, encoding="utf-8").stdout
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            items = ast.literal_eval(node.value)
            if items and isinstance(items[0], dict) and "name" in items[0]:
                return {c["name"]: c for c in items}
    raise RuntimeError(f"no concept list at {commit}")


CONCEPTS = {c: concepts_at(c) for _, c in CONCEPT_COMMITS}


def concept_commit_for(ts: str) -> str:
    chosen = CONCEPT_COMMITS[0][1]
    for start, c in CONCEPT_COMMITS:
        if ts >= start:
            chosen = c
    return chosen


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fname(names) -> str:
    return "_x_".join(n.replace(" ", "_") for n in names).lower()


def nous_era(ts: str) -> str:
    return "nous_v1" if ts < "2026-03-25" else "nous_v2"


def codegen_era(ts: str | None) -> str | None:
    if ts is None:
        return None
    return "codegen_v1" if ts < "2026-03-25" else ("codegen_v2" if ts < "2026-03-27" else "codegen_v3")


def acc_of(reason: str | None):
    m = re.match(r"trap_battery_failed \(acc=(\d+)% cal=(\d+)%", reason or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def main() -> None:
    nous = {}
    for f in sorted(glob.glob("agents/nous/runs/*/responses.jsonl")):
        run = os.path.basename(os.path.dirname(f))
        for line in open(f, encoding="utf-8"):
            r = json.loads(line); r["_run"] = run
            k = tuple(sorted(r["concept_names"]))
            c = r["score"].get("composite_score") or 0
            if k not in nous or c > (nous[k]["score"].get("composite_score") or 0):
                nous[k] = r
    led_rows = [json.loads(l) for l in open("agents/hephaestus/ledger.jsonl", encoding="utf-8")]
    ledk = {}
    for r in led_rows:
        ledk[tuple(sorted(r["concept_names"]))] = r  # last row per triple wins (the ledger's own semantics)
    metas = {os.path.basename(f)[:-5]: json.load(open(f, encoding="utf-8")) for f in glob.glob("agents/hephaestus/forge/*.json")}
    nov = json.load(open("agents/hephaestus/novelty_scores.json", encoding="utf-8"))

    lens = collections.OrderedDict()
    lens["L1_honest_forged"] = [k for k, r in ledk.items() if r["status"] == "forged" and r["timestamp"] >= "2026-04-01"]
    lens["L2_march_forged_acc50"] = [k for k, r in ledk.items() if r["status"] == "forged" and r["timestamp"] < "2026-04-01" and r["accuracy"] >= 0.5]
    l3 = [(acc_of(r.get("reason")), k) for k, r in ledk.items() if r["status"] == "scrap" and acc_of(r.get("reason")) and acc_of(r.get("reason"))[0] >= 50]
    l3.sort(reverse=True); lens["L3_nearmiss_acc50"] = [k for _, k in l3[:30]]
    lens["L4_novelty70"] = [tuple(sorted(metas[n]["concept_names"])) for n, v in nov.items() if v["novelty"] >= 0.7 and n in metas]

    def unfair(k):
        r = ledk.get(k); return r is None or (r["status"] == "scrap" and r.get("reason") == "api_call_failed")
    l5 = [((v["score"].get("composite_score") or 0), k) for k, v in nous.items()
          if v["score"].get("novelty") == "novel" and (v["score"]["ratings"].get("implementability") or 0) >= 9 and unfair(k)]
    l5.sort(reverse=True); lens["L5_nous_unforged_top"] = [k for _, k in l5[:20]]
    already = {k for ks in lens.values() for k in ks}
    l6 = [((v["score"].get("composite_score") or 0), k) for k, v in nous.items() if (v["score"].get("composite_score") or 0) >= 8.0 and k not in already]
    l6.sort(reverse=True); lens["L6_nous_composite_top"] = [k for _, k in l6[:10]]

    sel = collections.OrderedDict()
    for n, ks in lens.items():
        for k in ks:
            if k in nous:
                sel.setdefault(k, []).append(n)

    packets = []
    for i, (k, lenses) in enumerate(sel.items(), 1):
        v = nous[k]; r = ledk.get(k)
        cc = concept_commit_for(v["timestamp"]); cdict = CONCEPTS[cc]
        names = list(v["concept_names"])
        descs = [cdict.get(n, {}).get("short_description") for n in names]
        era = nous_era(v["timestamp"])
        tpl = (TPL / f"{era}.txt").read_text(encoding="utf-8")
        prompt = tpl.format(c1_name=names[0], c2_name=names[1], c3_name=names[2], c1_desc=descs[0], c2_desc=descs[1], c3_desc=descs[2])
        fn = fname(names)
        code_path = next((p for p in (f"agents/hephaestus/forge/{fn}.py", f"agents/hephaestus/scrap/{fn}.py") if os.path.exists(p)), None)
        pk = {"packet_id": f"XP-{i:03d}", "key": " + ".join(names), "concept_names": names,
              "concept_fields": list(v.get("concept_fields", [])), "concept_descriptions": descs, "concepts_commit": cc,
              "lenses": lenses,
              "nous": {"run": v["_run"], "timestamp": v["timestamp"], "model": v.get("model"), "template": era,
                       "template_sha256": sha(tpl.encode("utf-8")), "prompt_reconstructed": prompt, "prompt_sha256": sha(prompt.encode("utf-8")),
                       "response_text": v["response_text"], "response_sha256": sha(v["response_text"].encode("utf-8")),
                       "ratings": v["score"]["ratings"], "composite_score": v["score"].get("composite_score"), "novelty_label": v["score"].get("novelty")},
              "ledger": None if r is None else {"status": r["status"], "reason": r.get("reason"), "accuracy": r["accuracy"], "calibration": r["calibration"],
                                                  "timestamp": r["timestamp"], "frame": r.get("frame"), "model": r.get("model"),
                                                  "honest_ruler": r["timestamp"] >= "2026-03-27T06:00:00", "codegen_template": codegen_era(r["timestamp"])},
              "original_code": None if code_path is None else {"path": code_path, "sha256": sha(Path(code_path).read_bytes()), "bytes": Path(code_path).stat().st_size},
              "original_code_note": None if code_path is not None else (
                  "ledger row exists but no code file is committed under agents/hephaestus/ (searched forge*/, scrap*/, runs/ by concept tokens); "
                  "rows dated 2026-04/05 were forged on M3 and their files were never committed (stations/M3_STATUS.md)" if r is not None else
                  "never forged (Nous-only)"),
              "forge_meta": metas.get(fn), "novelty_scores": nov.get(fn)}
        packets.append(pk)

    summary = {"n_packets": len(packets), "lens_counts": {n: len(ks) for n, ks in lens.items()},
               "lens_overlap": dict(collections.Counter(len(p["lenses"]) for p in packets)),
               "ledger_status": dict(collections.Counter((p["ledger"] or {}).get("status") for p in packets)),
               "with_original_code": sum(p["original_code"] is not None for p in packets),
               "nous_template": dict(collections.Counter(p["nous"]["template"] for p in packets)),
               "codegen_template": dict(collections.Counter((p["ledger"] or {}).get("codegen_template") for p in packets)),
               "frames": dict(collections.Counter((p["ledger"] or {}).get("frame") for p in packets)),
               "corpus": {"nous_triples_unique": len(nous), "ledger_rows": len(led_rows), "forge_json": len(metas), "novelty_rows": len(nov)}}
    (OUT / "selection.json").write_text(json.dumps({"summary": summary, "packets": packets}, indent=1), encoding="utf-8")
    lines = ["# xpol_2026 replay set (extracted, read-only over the 1.0 corpus)", "",
             "| id | triple | lenses | orig status | orig acc | orig frame | nous composite |", "|---|---|---|---|---|---|---|"]
    for p in packets:
        L = p["ledger"] or {}
        lines.append(f"| {p['packet_id']} | {p['key']} | {','.join(x.split('_')[0] for x in p['lenses'])} | {L.get('status')} | "
                     f"{'' if L.get('accuracy') is None else round(L['accuracy'], 3)} | {L.get('frame') or ''} | {p['nous']['composite_score']} |")
    (OUT / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
