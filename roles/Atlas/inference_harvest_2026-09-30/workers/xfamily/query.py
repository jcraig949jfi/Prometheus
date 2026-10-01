"""Query NVIDIA NIM models with PACKET.md. Key is read from ~/.nemoclaw/credentials.json and never printed."""
import json, os, sys, time, datetime, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://integrate.api.nvidia.com/v1/chat/completions"
INSTR = ("Identify the 8-12 strongest regularities that hold ACROSS multiple engines (not within one). For each: a precise "
         "statement; which engine codes support it (cite line numbers); how independent those supports seem; one observation "
         "that would falsify it. Also list 3 things this corpus seems unable to tell us. Be concrete; do not use generic ML platitudes.")

def key():
    with open(os.path.expanduser("~/.nemoclaw/credentials.json")) as f:
        return json.load(f)["NVIDIA_API_KEY"]

def ask(model, prompt, max_tokens=6000):
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0.3, "max_tokens": max_tokens, "stream": False}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Authorization": "Bearer " + key(),
                                 "Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read().decode())

MAXT = int(os.environ.get("MAXT", "6000"))

def main(models):
    packet = open(os.path.join(HERE, "PACKET.md"), encoding="utf-8").read()
    prompt = packet + "\n\n" + INSTR
    log = []
    for m in models:
        t0 = datetime.datetime.now(datetime.timezone.utc)
        rec = {"max_tokens": MAXT, "model": m, "start_utc": t0.isoformat(timespec="seconds")}
        try:
            d = ask(m, prompt, MAXT)
            msg = d["choices"][0]["message"]
            content = msg.get("content") or ""
            rec.update(ok=bool(content.strip()), finish_reason=d["choices"][0].get("finish_reason"), usage=d.get("usage"))
            fn = os.path.join(HERE, "RESP_" + m.replace("/", "_") + ".md")
            with open(fn, "w", encoding="utf-8", newline="\n") as f:
                f.write(f"<!-- model={m} start_utc={rec['start_utc']} temperature=0.3 max_tokens={MAXT} finish_reason={rec['finish_reason']} usage={json.dumps(rec['usage'])} -->\n")
                f.write(content)
            rc = msg.get("reasoning_content")
            if rc:
                rec["reasoning_chars"] = len(rc)
                with open(fn[:-3] + "_reasoning.md", "w", encoding="utf-8", newline="") as f:
                    f.write(rc)
        except urllib.error.HTTPError as e:
            rec.update(ok=False, error=f"HTTP {e.code}: {e.read().decode(errors='replace')[:500]}")
        except Exception as e:
            rec.update(ok=False, error=repr(e)[:500])
        rec["end_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        log.append(rec)
        print(json.dumps(rec), flush=True)
    with open(os.path.join(HERE, "query_log.jsonl"), "a", encoding="utf-8") as f:
        for r in log:
            f.write(json.dumps(r) + "\n")

if __name__ == "__main__":
    main(sys.argv[1:])
