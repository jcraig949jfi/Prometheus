"""Streamed variant of query.py (same prompt, temperature 0.3). Key read from ~/.nemoclaw/credentials.json, never printed."""
import json, os, sys, datetime, urllib.request, urllib.error
from query import HERE, URL, INSTR, key
MAXT = int(os.environ.get("MAXT", "16000"))

def run(m):
    packet = open(os.path.join(HERE, "PACKET.md"), encoding="utf-8").read()
    prompt = packet + "\n\n" + INSTR
    rec = {"mode": "stream", "max_tokens": MAXT, "model": m,
           "start_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    content, reasoning, finish, usage = [], [], None, None
    try:
        body = json.dumps({"model": m, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3,
                           "max_tokens": MAXT, "stream": True, "stream_options": {"include_usage": True}}).encode()
        req = urllib.request.Request(URL, data=body, headers={"Authorization": "Bearer " + key(),
                                     "Content-Type": "application/json", "Accept": "text/event-stream"})
        with urllib.request.urlopen(req, timeout=600) as r:
            for raw in r:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                ev = json.loads(data)
                if ev.get("usage"):
                    usage = ev["usage"]
                for ch in ev.get("choices") or []:
                    d = ch.get("delta") or {}
                    if d.get("content"): content.append(d["content"])
                    rc = d.get("reasoning_content") or d.get("reasoning")
                    if rc: reasoning.append(rc)
                    if ch.get("finish_reason"): finish = ch["finish_reason"]
    except urllib.error.HTTPError as e:
        rec["error"] = f"HTTP {e.code}: {e.read().decode(errors='replace')[:500]}"
    except Exception as e:
        rec["error"] = repr(e)[:500]
    c, rtxt = "".join(content), "".join(reasoning)
    rec.update(ok=bool(c.strip()), finish_reason=finish, usage=usage, content_chars=len(c), reasoning_chars=len(rtxt),
               end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
    fn = os.path.join(HERE, "RESP_" + m.replace("/", "_") + ".md")
    if c or rtxt:
        with open(fn, "w", encoding="utf-8", newline="") as f:
            f.write(f"<!-- model={m} start_utc={rec['start_utc']} end_utc={rec['end_utc']} temperature=0.3 max_tokens={MAXT} stream=true finish_reason={finish} usage={json.dumps(usage)} -->\n")
            f.write(c)
        if rtxt:
            with open(fn[:-3] + "_reasoning.md", "w", encoding="utf-8", newline="") as f:
                f.write(rtxt)
    print(json.dumps(rec), flush=True)
    with open(os.path.join(HERE, "query_log.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")

if __name__ == "__main__":
    for m in sys.argv[1:]:
        run(m)
