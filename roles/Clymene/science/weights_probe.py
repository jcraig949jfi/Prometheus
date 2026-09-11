"""Supplementary probe: are the WEIGHTS obtainable at the recorded revision?

Defect this repairs, found while reading the first model run: the
preregistered reproducibility probe HEADs "one sidecar-covered file", and for
a stub the only sidecar-covered files are the PUBLIC ones (README, LICENSE,
config). On a gated repository those return 200 while the weights return 401 --
so the probe reported REPRODUCIBLE=True for two artifacts whose weights cannot
be fetched at all. Green for the wrong reason, in this seat's own instrument.

This probe asks the question that matters: at the recorded revision, does a
WEIGHT file resolve? It is an addition, not a relaxation: no row can move from
IRREPRODUCIBLE to REPRODUCIBLE because of it, only the reverse.

For a directory with weights on disk, the weight filename is taken from disk.
For a stub, the canonical single-file and sharded names are tried.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

SCRATCH = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(SCRATCH, "model_audit.jsonl")
OUT = os.path.join(SCRATCH, "weights_probe.jsonl")
VAULT_MODELS = "D:/Prometheus/vault/models"
UA = {"User-Agent": "prometheus-clymene-audit/1.0 (read-only provenance check)"}

CANDIDATES = ("model.safetensors", "model-00001-of-00002.safetensors",
              "model-00001-of-00003.safetensors", "pytorch_model.bin",
              "model-00001-of-00004.safetensors")


def head(url, timeout=45):
    req = urllib.request.Request(url, method="HEAD", headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return "ERR:" + type(e).__name__


def main():
    rows = [json.loads(l) for l in open(IN, encoding="utf-8")]
    models = [r for r in rows if r["kind"] == "model"]
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        # control: a file known to be public on a known-open repo must be 200,
        # and a fabricated filename on the same repo must be 404. Without both,
        # a blanket 401 would be indistinguishable from a broken probe.
        c1 = head("https://huggingface.co/Qwen/Qwen2.5-1.5B/resolve/"
                  "8faed761d45a263340a0528343f099c05c9a4323/model.safetensors")
        c2 = head("https://huggingface.co/Qwen/Qwen2.5-1.5B/resolve/"
                  "8faed761d45a263340a0528343f099c05c9a4323/zzq-not-a-file.safetensors")
        rec = {"kind": "control", "control": "WEIGHTS_PROBE_CHANNEL",
               "open_repo_weight_status": c1, "fabricated_filename_status": c2,
               "PASS": c1 == 200 and c2 == 404}
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        print("CONTROL PASS=%s (open=%s fabricated=%s)" % (rec["PASS"], c1, c2))

        for m in models:
            d = os.path.join(VAULT_MODELS, m["dir"])
            rev = m.get("recorded_revision")
            names = []
            if os.path.isdir(d):
                for dirpath, _dn, fns in os.walk(d):
                    if ".cache" in dirpath.replace("\\", "/").split("/"):
                        continue
                    for fn in fns:
                        if fn.lower().endswith((".safetensors", ".bin", ".gguf")) \
                                and not fn.endswith(".index.json"):
                            names.append(os.path.relpath(os.path.join(dirpath, fn), d)
                                         .replace(os.sep, "/"))
            names = sorted(names)[:1] or list(CANDIDATES)
            result = {"kind": "weights_probe", "dir": m["dir"], "hf_id": m["hf_id"],
                      "recorded_revision": rev, "tried": [], "status": None,
                      "weights_obtainable": None}
            if not rev:
                result["note"] = "no recorded revision"
            else:
                for n in names:
                    url = "https://huggingface.co/{}/resolve/{}/{}".format(m["hf_id"], rev, n)
                    st = head(url)
                    result["tried"].append({"file": n, "status": st})
                    if st in (200, 302):
                        result["status"], result["weights_obtainable"] = st, True
                        break
                    if st in (401, 403):
                        result["status"], result["weights_obtainable"] = st, False
                        result["note"] = "GATED at the weights"
                        break
                    result["status"] = st
                if result["weights_obtainable"] is None:
                    result["weights_obtainable"] = False
                    result.setdefault("note", "no candidate weight file resolved")
            fh.write(json.dumps(result) + "\n")
            fh.flush()
            print("%-44s rev=%s weights_obtainable=%s %s" % (
                m["dir"][:44], (rev or "-")[:10], result["weights_obtainable"],
                result.get("note", "")))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
