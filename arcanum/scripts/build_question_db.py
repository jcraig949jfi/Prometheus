import json
import re
import os
import hashlib
from datetime import datetime
import socket
import glob

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
PROMPT_FILES = glob.glob(os.path.join(DOCS_DIR, "PromptAndQuestions*.md"))
SCREENING_DIR = os.path.join(ROOT_DIR, "results", "screening")
REPORTS_DIR = os.path.join(ROOT_DIR, "results", "reports")
OUTPUT_FILE = os.path.join(ROOT_DIR, "questions", "DiscoveryDB.md")
DETAIL_DIR = os.path.join(ROOT_DIR, "questions", "detail")

# Identify this local machine
LOCAL_HOSTNAME = socket.gethostname().lower()


def get_qid(text: str) -> str:
    """Generate a stable 8-char QID from prompt text."""
    clean_text = re.sub(r'\W+', '', text).lower()
    return hashlib.sha256(clean_text.encode()).hexdigest()[:8].upper()


def machine_from_filename(filename):
    """Infer machine name from a report or log filename."""
    fname_lower = filename.lower()
    if "gandalf" in fname_lower:
        return "gandalf"
    elif "skullport" in fname_lower:
        return "skullport"
    return LOCAL_HOSTNAME


def parse_prompts_file(path):
    """Parse a markdown file for question text and original author."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            blocks = re.split(r'\n\[(.*?)\]\n', content)
            author_q_map = {}
            if len(blocks) > 1:
                for i in range(1, len(blocks), 2):
                    author = blocks[i].strip().upper()
                    text_block = blocks[i+1]
                    questions = re.findall(r'^\d+\.\s+(.*)', text_block, re.MULTILINE)
                    for q in questions:
                        q_clean = q.strip().strip('"')
                        author_q_map[q_clean] = author
            return author_q_map
    except:
        return {}


def parse_reports():
    """Parse all reports, returning full specimen data grouped by trigger text.

    Returns: dict[trigger_text -> list[specimen_dict]]
    Each specimen contains all fields from the report block for that trigger.
    """
    specimens_by_trigger = {}
    if not os.path.exists(REPORTS_DIR):
        return specimens_by_trigger

    for f in sorted(os.listdir(REPORTS_DIR)):
        if not f.endswith(".md"):
            continue

        machine = machine_from_filename(f)
        ts_match = re.search(r'(\d{8}_\d{6})', f)
        report_dt = datetime.strptime(ts_match.group(1), '%Y%m%d_%H%M%S') if ts_match else None

        path = os.path.join(REPORTS_DIR, f)
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()

            model_match = re.search(r'\*\*Model:\*\*\s*(.*)', content[:500])
            model = model_match.group(1).split('|')[0].strip() if model_match else "UNKNOWN"

            # Split into (heading, body) pairs — heading is the ### N. line
            parts = re.split(r'\n(### \d+\. .*)\n', content)
            for i in range(1, len(parts), 2):
                heading = parts[i]
                body = parts[i + 1] if i + 1 < len(parts) else ""

                trigger_match = re.search(r'- \*\*Trigger\*\*: "?(.*?)"?\s*$', body, re.MULTILINE)
                if not trigger_match:
                    continue
                trigger = trigger_match.group(1).strip().strip('"')

                score_match = re.search(r'### \d+\.\s+([\d.]+)', heading)
                grade_match = re.search(r'\*\*([\w\s]+)\*\*\s*$', heading)
                concept_match = re.search(r'- \*\*Model Concept Name\*\*:\s*(.*)', body)
                uuid_match = re.search(r'UUID: `(.*?)`', body)
                layer_match = re.search(r'Layer:\s*(\d+)', body)
                exec_match = re.search(r'Execution Time:\s*([\d.]+)s', body)
                metrics_match = re.search(r'`dist=(.*?), ppl=(.*?), coh=(.*?)`', body)

                # Model feedback: text after the label, up to the note block or next field
                feedback_match = re.search(
                    r'- \*\*Model Feedback/Leak\*\*:\s*(.+?)(?=\n  >|\n- \*\*|\n---|\Z)',
                    body, re.DOTALL
                )

                # Post-mortem: everything inside the [!NOTE] block, with > prefixes stripped
                note_match = re.search(r'> \[!NOTE\](.*?)(?=\n---|\Z)', body, re.DOTALL)
                if note_match:
                    raw_note = note_match.group(1)
                    postmortem = re.sub(r'\n\s*> ?', '\n', raw_note).strip()
                else:
                    postmortem = None

                specimen = {
                    "score": float(score_match.group(1)) if score_match else 0.0,
                    "grade": grade_match.group(1).strip() if grade_match else "---",
                    "concept": concept_match.group(1).strip() if concept_match else "---",
                    "uuid": uuid_match.group(1) if uuid_match else "---",
                    "layer": int(layer_match.group(1)) if layer_match else -1,
                    "exec_time": exec_match.group(1) if exec_match else "---",
                    "dist": metrics_match.group(1) if metrics_match else "---",
                    "ppl": metrics_match.group(2) if metrics_match else "---",
                    "coh": metrics_match.group(3) if metrics_match else "---",
                    "feedback": feedback_match.group(1).strip() if feedback_match else None,
                    "postmortem": postmortem,
                    "machine": machine,
                    "model": model,
                    "report_ts": report_dt.strftime('%Y-%m-%d %H:%M:%S') if report_dt else "---",
                }
                # Deduplicate: same run can appear in multiple report snapshots.
                # Key on metrics that uniquely identify a run; keep the latest report_ts.
                dedup_key = (specimen["uuid"], specimen["dist"], specimen["ppl"],
                             specimen["coh"], specimen["layer"], specimen["machine"], specimen["model"])
                existing = specimens_by_trigger.setdefault(trigger, [])
                for prev in existing:
                    prev_key = (prev["uuid"], prev["dist"], prev["ppl"],
                                prev["coh"], prev["layer"], prev["machine"], prev["model"])
                    if prev_key == dedup_key:
                        # Keep the most recent report_ts
                        if specimen["report_ts"] > prev["report_ts"]:
                            prev["report_ts"] = specimen["report_ts"]
                        break
                else:
                    existing.append(specimen)
        except:
            continue

    return specimens_by_trigger


def parse_logs():
    """Parse all *.jsonl logs in screening dir for historical results."""
    results = {}
    if not os.path.exists(SCREENING_DIR):
        return results

    log_files = [f for f in os.listdir(SCREENING_DIR) if f.endswith(".jsonl")]
    for log_filename in log_files:
        log_machine = machine_from_filename(log_filename)
        path = os.path.join(SCREENING_DIR, log_filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        p = data.get("prompt", "").strip().strip('"')
                        if not p:
                            continue
                        if p not in results:
                            results[p] = []
                        results[p].append({
                            "score": data.get("best_score", 0.0),
                            "verdict": data.get("verdict", "SKIP"),
                            "layer": data.get("layer", -1),
                            "ts": data.get("ts", ""),
                            "source": data.get("source", "UNKNOWN").upper(),
                            "machine": log_machine
                        })
                    except:
                        continue
        except:
            pass
    return results


def get_model_map():
    """Returns a per-machine dict of sorted (datetime, model_name) tuples."""
    model_map = {}
    if not os.path.exists(REPORTS_DIR):
        return model_map
    for f in os.listdir(REPORTS_DIR):
        if not f.endswith(".md"):
            continue
        machine = machine_from_filename(f)
        path = os.path.join(REPORTS_DIR, f)
        try:
            with open(path, 'r', encoding='utf-8') as file:
                head = file.read(500)
                m = re.search(r'\*\*Model:\*\*\s*(.*)', head)
                if m:
                    model_name = m.group(1).split('|')[0].strip()
                    ts_match = re.search(r'(\d{8}_\d{6})', f)
                    if ts_match:
                        dt = datetime.strptime(ts_match.group(1), '%Y%m%d_%H%M%S')
                        model_map.setdefault(machine, []).append((dt, model_name))
        except:
            continue
    for machine in model_map:
        model_map[machine].sort(key=lambda x: x[0])
    return model_map


def infer_model(ts_str, machine, model_map):
    """Look up the model active on a specific machine at the time of a run."""
    entries = model_map.get(machine) or []
    if not ts_str or not entries:
        return "UNKNOWN"
    try:
        ts = datetime.fromisoformat(ts_str)
        best_match = entries[0][1]
        for dt, m in entries:
            if dt <= ts:
                best_match = m
            else:
                break
        return best_match
    except:
        return "UNKNOWN"


def score_str(score_val):
    if score_val >= 0.5:   return f"🟣 **{score_val:.4f}**"
    elif score_val >= 0.3: return f"🟢 **{score_val:.4f}**"
    elif score_val >= 0.1: return f"🟡 **{score_val:.4f}**"
    elif score_val > 0:    return f"⚪ {score_val:.4f}"
    return "---"


def extract_safe_blocks(path):
    """Return any <!-- [SAFE] -->...<!-- [/SAFE] --> blocks from an existing detail file."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return re.findall(r'<!-- \[SAFE\] -->.*?<!-- \[/SAFE\] -->', content, re.DOTALL)
    except:
        return []


def build_detail_files(db, specimens_by_trigger):
    """Write one Q-{qid}.md per question into questions/detail/.

    Each file aggregates all report specimens (rich data) and all
    screening log runs for that question across all machines and models.
    Any <!-- [SAFE] -->...<!-- [/SAFE] --> blocks in existing files are
    preserved verbatim under an Expert Analysis section.
    """
    os.makedirs(DETAIL_DIR, exist_ok=True)
    count = 0

    for entry in db:
        trigger = entry["text"]
        qid = entry["qid"]
        specimens = sorted(
            specimens_by_trigger.get(trigger, []),
            key=lambda x: x["score"], reverse=True
        )
        runs = sorted(entry["runs"], key=lambda x: x["score"], reverse=True)

        # Skip questions with no report data and no runs
        if not specimens and not runs:
            continue

        path = os.path.join(DETAIL_DIR, f"Q-{qid}.md")
        safe_blocks = extract_safe_blocks(path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# Q-{qid}\n\n")
            f.write(f"> {trigger}\n\n")
            f.write(f"**Author:** {entry['author']} | **Top Score:** {entry['top_score']:.4f} | ")
            f.write(f"**Top Machine:** {entry['top_machine']} | **Top Model:** {entry['top_model'].split('/')[-1]}\n\n")
            f.write(f"[← Back to DiscoveryDB](../DiscoveryDB.md)\n\n")

            # --- Specimens from deep analysis reports ---
            if specimens:
                f.write("---\n\n## Specimens from Deep Analysis\n\n")
                for s in specimens:
                    model_slug = s["model"].split("/")[-1]
                    f.write(f"### {score_str(s['score'])} — {s['grade']} &nbsp;`{s['machine']}` / `{model_slug}`\n\n")
                    f.write(f"| Field | Value |\n| :--- | :--- |\n")
                    f.write(f"| **Concept Name** | {s['concept']} |\n")
                    f.write(f"| **UUID** | `{s['uuid']}` |\n")
                    f.write(f"| **Layer** | {s['layer']} |\n")
                    f.write(f"| **Execution Time** | {s['exec_time']}s |\n")
                    f.write(f"| **dist / ppl / coh** | {s['dist']} / {s['ppl']} / {s['coh']} |\n")
                    f.write(f"| **Report Date** | {s['report_ts']} |\n\n")

                    if s["feedback"]:
                        f.write(f"**Model Output:**\n\n")
                        # Indent as blockquote
                        for line in s["feedback"].splitlines():
                            f.write(f"> {line}\n")
                        f.write("\n")

                    if s["postmortem"]:
                        f.write(f"**Post-Mortem:**\n\n")
                        f.write(f"{s['postmortem']}\n\n")

                    f.write("---\n\n")

            # --- Screening log run history ---
            if runs:
                f.write("## Screening Run History\n\n")
                f.write("| Machine | Model | Score | Layer | Timestamp | Verdict |\n")
                f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
                for r in runs:
                    vic = "✅" if r["verdict"] in ["HIT", "CAPTURE"] else "❌"
                    model_slug = r["model"].split("/")[-1]
                    f.write(f"| {r['machine']} | {model_slug} | {r['score']:.4f} | {r['layer']} | {r['ts']} | {vic} {r['verdict']} |\n")
                f.write("\n")

            # Re-inject any protected expert analysis blocks
            if safe_blocks:
                f.write("---\n\n## 🔒 Expert Analysis\n\n")
                for block in safe_blocks:
                    f.write(block + "\n\n")

        count += 1
    return count


def build_db():
    print(f"Building Discovery Database (Local Host: {LOCAL_HOSTNAME})...")

    author_map = {}
    for path in PROMPT_FILES:
        print(f"  Parsing {os.path.basename(path)}...")
        author_map.update(parse_prompts_file(path))

    all_runs = parse_logs()
    model_history = get_model_map()
    specimens_by_trigger = parse_reports()

    db = []
    all_prompts = set(author_map.keys()) | set(all_runs.keys()) | set(specimens_by_trigger.keys())
    stats = {}

    for p in all_prompts:
        runs = all_runs.get(p, [])
        author = author_map.get(p) or (runs[0]['source'] if runs else "UNKNOWN")

        if author not in stats:
            stats[author] = {'questions': set(), 'runs': 0, 'hits': 0}
        stats[author]['questions'].add(p)
        stats[author]['runs'] += len(runs)

        enriched_runs = []
        for r in runs:
            if r['verdict'] in ["HIT", "CAPTURE"]:
                stats[author]['hits'] += 1
            enriched_runs.append({
                "model": infer_model(r['ts'], r['machine'], model_history),
                "score": r['score'],
                "layer": r['layer'],
                "ts": r['ts'],
                "verdict": r['verdict'],
                "machine": r['machine']
            })

        # Best run from screening logs
        if enriched_runs:
            best_run = max(enriched_runs, key=lambda x: x['score'])
            top_score = best_run['score']
            top_model = best_run['model']
            top_machine = best_run['machine']
        else:
            top_score, top_model, top_machine = 0.0, "---", "---"

        # Best specimen from deep analysis reports (for the summary table UUID column)
        specimens = specimens_by_trigger.get(p, [])
        best_specimen = max(specimens, key=lambda x: x['score']) if specimens else {}

        db.append({
            "qid": get_qid(p),
            "text": p,
            "author": author,
            "top_score": top_score,
            "top_model": top_model,
            "top_machine": top_machine,
            "uuid": best_specimen.get("uuid", "---"),
            "runs": enriched_runs,
        })

    db.sort(key=lambda x: x['top_score'], reverse=True)
    total_q = len(db)

    # Build per-question detail files
    print("  Writing detail files...")
    detail_count = build_detail_files(db, specimens_by_trigger)
    print(f"  {detail_count} detail files written to questions/detail/")

    # Write main DB index
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Arcanum ∞: Provocation Discovery Database\n")
        f.write(f"> **Status Report:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## 📊 Discovery Summary\n\n")
        f.write(f"- **Total Provocations Catalogued:** {total_q}\n")
        f.write(f"- **Total Specimens Captured (HITs):** {sum(s['hits'] for s in stats.values())}\n")
        f.write(f"- **Total Screening Runs Evaluated:** {sum(s['runs'] for s in stats.values())}\n")
        f.write(f"- **Local Host Identity:** `{LOCAL_HOSTNAME}`\n")
        f.write(f"- **Remote Data Sources:** `Gandalf`, `Local Screening Logs`\n\n")

        f.write("### 🧬 Author Contribution\n")
        f.write("| Source | Ques. | % | Runs | Hits | Yield |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        sorted_stats = sorted(stats.items(), key=lambda x: len(x[1]['questions']), reverse=True)
        for auth, s in sorted_stats:
            q_count = len(s['questions'])
            pct = (q_count / total_q) * 100 if total_q > 0 else 0
            yield_pct = (s['hits'] / s['runs'] * 100) if s['runs'] > 0 else 0
            f.write(f"| **{auth}** | {q_count} | {pct:.1f}% | {s['runs']} | {s['hits']} | {yield_pct:.1f}% |\n")

        f.write("\n---\n\n")
        f.write("## 🏆 Top Provocations (Ranked by Novelty)\n\n")
        f.write("| Rank | QID | Top Score | Top Model | Machine | Source | UUID | Question |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")

        for i, e in enumerate(db):
            s_str = score_str(e['top_score'])
            m_slug = e['top_model'].split('/')[-1] if e['top_model'] else "---"
            uuid_str = f"`{e['uuid']}`" if e['uuid'] != '---' else "---"
            qid_link = f"[{e['qid']}](detail/Q-{e['qid']}.md)"
            f.write(f"| {i+1} | {qid_link} | {s_str} | {m_slug} | {e['top_machine']} | {e['author']} | {uuid_str} | {e['text']} |\n")

    print(f"Database built successfully: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_db()
