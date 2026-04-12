import json
import re
import os
import glob
import requests
import socket
from datetime import datetime

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT_DIR, "results", "screening")
LOG_FILE = os.path.join(RESULTS_DIR, "logs", "xenolexicon.log")
JSONL_FILE = os.path.join(RESULTS_DIR, "screening_log.jsonl")
SPECIMENS_DIR = os.path.join(RESULTS_DIR, "specimens")

# Config
GITHUB_MODELS_URL = "https://models.inference.ai.azure.com/chat/completions"

def load_env():
    env_path = os.path.join(ROOT_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env()
GITHUB_MODELS_KEY = os.getenv("GITHUB_MODELS_KEY")

def get_badge(score):
    if score >= 0.5: return "🌌 **SINGULARITY**"
    if score >= 0.35: return "💜 **MUSEUM GRADE**"
    if score >= 0.23: return "🔵 **RESEARCH GRADE**"
    return "🟢 **PRESERVED**"

def get_insight(prompt_text, score, feedback):
    if not GITHUB_MODELS_KEY: return "*(Insight skipped: No API Key)*"
    sys_prompt = "You are an AI scientist analyzing a model's 'failure persona' to a high-entropy math prompt. Provide a short, profound 'Deep Insight' into the failure mode."
    user_msg = f"Trigger: {prompt_text}\nNovelty: {score}\nFeedback: {feedback}"
    payload = {"model": "DeepSeek-R1", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_msg}], "max_tokens": 512}
    
    try:
        resp = requests.post(GITHUB_MODELS_URL, headers={"Authorization": f"Bearer {GITHUB_MODELS_KEY}", "Content-Type": "application/json"}, json=payload, timeout=45)
        if resp.status_code == 200: return resp.json()["choices"][0]["message"]["content"].strip()
        
        payload["model"] = "gpt-4o-mini"
        resp = requests.post(GITHUB_MODELS_URL, headers={"Authorization": f"Bearer {GITHUB_MODELS_KEY}", "Content-Type": "application/json"}, json=payload, timeout=30)
        if resp.status_code == 200: return resp.json()["choices"][0]["message"]["content"].strip()
        return f"*(API Error: {resp.status_code})*"
    except Exception as e:
        return f"*(Insight Error: {str(e)})*"

def build_uuid_map():
    """Maps best_score to UUID by parsing permanent .pt files.
    Gracefully degrades if torch is unavailable (returns empty map)."""
    uuid_map = {}
    if not HAS_TORCH:
        print("  (torch not available — skipping .pt UUID recovery, using log-based UUIDs)")
        return uuid_map
    if not os.path.exists(SPECIMENS_DIR): return uuid_map
    for f in os.listdir(SPECIMENS_DIR):
        if f.endswith('.pt') and not f.endswith('_emb.pt'):
            uuid = f.replace('.pt', '')
            try:
                data = torch.load(os.path.join(SPECIMENS_DIR, f), map_location='cpu', weights_only=True)
                if isinstance(data, dict):
                    score = float(data.get('novelty_score', 0.0))
                    k = f"{score:.4f}"
                    uuid_map[k] = uuid
            except Exception:
                pass
    return uuid_map

def parse_logs():
    data = {}
    if not os.path.exists(LOG_FILE): return data
    
    cap_re = re.compile(r"Specimen captured: ([\w-]+) \(novelty=([\d.]+)")
    name_re = re.compile(r"NAME:\s*(.*?)\s*DESCRIPTION:\s*(.*)")
    name_alt_re = re.compile(r"Named specimen: '(.*?)' — (.*)")
    raw_re = re.compile(r"Raw response:")
    metric_re = re.compile(r"dist=([\d.]+), ppl=([\d.]+), coh=([\d.]+), novelty=([\d.]+)")
    
    current_uid = None
    collect_raw = False
    raw_lines = []

    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Metrics
            m_match = metric_re.search(line)
            if m_match:
                dist, ppl, coh, nov = m_match.groups()
                nov_key = f"{float(nov):.4f}"
                if nov_key not in data:
                    data[nov_key] = {"metrics": f"dist={dist}, ppl={ppl}, coh={coh}", "uuid": "??", "desc": "N/A", "name": "Unknown"}
                else:
                    data[nov_key]["metrics"] = f"dist={dist}, ppl={ppl}, coh={coh}"
                continue

            # Capture
            c_match = cap_re.search(line)
            if c_match:
                if collect_raw and current_uid and raw_lines:
                    for k, v in data.items():
                        if v["uuid"] == current_uid: v["desc"] = " ".join(raw_lines).strip()
                uid, nov = c_match.groups()
                current_uid = uid
                k = f"{float(nov):.4f}"
                if k not in data: data[k] = {"uuid": uid, "name": "Unknown", "desc": "N/A", "metrics": "N/A"}
                else: data[k]["uuid"] = uid
                collect_raw = False; raw_lines = []
                continue

            # Names (Standard)
            n_match = name_re.search(line)
            if n_match and current_uid:
                name, desc = n_match.groups()
                for k, v in data.items():
                    if v["uuid"] == current_uid: v["name"] = name.strip(); v["desc"] = desc.strip()
                continue
            
            # Names (Alt format like the 0.6537 hit)
            alt_match = name_alt_re.search(line)
            if alt_match and current_uid:
                name, desc = alt_match.groups()
                for k, v in data.items():
                    if v["uuid"] == current_uid: v["name"] = name.strip(); v["desc"] = desc.strip()
                continue

            # Raw
            if raw_re.search(line): collect_raw = True; raw_lines = []; continue
            if collect_raw and current_uid:
                if re.match(r"^\d{4}-\d{2}-\d{2}", line):
                    for k, v in data.items():
                        if v["uuid"] == current_uid and v["desc"] == "N/A": v["desc"] = " ".join(raw_lines).strip()
                    collect_raw = False
                else:
                    cl = re.sub(r"^\d{4}-\d{2}-\d{2}.*?(INFO|DEBUG|TRACE|WARNING|ERROR)\s+", "", line).strip()
                    if cl: raw_lines.append(cl)
    return data

def get_specimen_metadata(uuid):
    """Loads the specimen metadata JSON if it exists."""
    if not uuid or uuid == "??": return None
    meta_file = os.path.join(SPECIMENS_DIR, f"{uuid}.json")
    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None

def get_autopsy_data(uuid):
    """Loads the Token Autopsy report text and cloud analysis JSON if they exist."""
    result = {"text": None, "cloud": None}
    if not uuid or uuid == "??": return result

    cloud_file = os.path.join(SPECIMENS_DIR, f"{uuid}_cloud.json")
    text_file = os.path.join(SPECIMENS_DIR, f"{uuid}_autopsy.txt")

    if os.path.exists(cloud_file):
        try:
            with open(cloud_file, 'r', encoding='utf-8') as f:
                result["cloud"] = json.load(f)
        except Exception:
            pass

    if os.path.exists(text_file):
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract the classification and reason
                lines = content.split("\n")
                status = ""
                reason = ""
                for line in lines:
                    if line.startswith("CLASSIFICATION:"): status = line.replace("CLASSIFICATION:", "").strip()
                    if line.startswith("REASON:"): reason = line.replace("REASON:", "").strip()
                result["text"] = {"full": content, "status": status, "reason": reason}
        except Exception:
            pass

    return result

def get_scaffold_data(uuid):
    """Loads the Naming Autopsy scaffold classification and report if they exist."""
    result = {"classification": None, "report_snippet": None}
    if not uuid or uuid == "??": return result

    class_file = os.path.join(SPECIMENS_DIR, f"{uuid}_scaffold.json")
    report_file = os.path.join(SPECIMENS_DIR, f"{uuid}_scaffold_report.txt")

    if os.path.exists(class_file):
        try:
            with open(class_file, 'r', encoding='utf-8') as f:
                result["classification"] = json.load(f)
        except Exception:
            pass

    if os.path.exists(report_file):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Pull just the interpretation line for the report summary
                for line in content.split("\n"):
                    if line and not line.startswith("=") and not line.startswith("SCAFFOLD"):
                        result["report_snippet"] = line.strip()
                        break
        except Exception:
            pass

    return result

def get_scaffold_icon(mode):
    return {
        "CLEAN_NAME": "✅",
        "FIELD_BIOLOGIST": "🔬",
        "META_LINGUISTIC": "📐",
        "CONVERSATIONAL_BLEED": "💬",
        "HALLUCINATED_CITATION": "📚",
        "PERSONA_BLEND": "🎭",
        "RAW_SCAFFOLD": "⚡",
        "UNCLASSIFIABLE": "❓",
    }.get(mode, "❓")

def generate_report():
    print("Reading data...")
    if not os.path.exists(JSONL_FILE): return
    with open(JSONL_FILE, 'r', encoding='utf-8') as f:
        lines = [json.loads(line) for line in f]
    
    captures = sorted([l for l in lines if l['verdict'] == 'CAPTURE'], key=lambda x: x['best_score'], reverse=True)
    log_data = parse_logs()
    uuid_map = build_uuid_map()
    
    model_name = "Unknown Model"
    try:
        with open(os.path.join(ROOT_DIR, 'configs', 'xenolexicon.yaml'), 'r', encoding='utf-8') as f:
            for line in f:
                if 'name:' in line and 'Qwen' in line:
                    model_name = line.split('"')[1] if '"' in line else line.split("'")[1]
                    break
    except Exception:
        pass
    
    report = [
        f"# Xenolexicon: Master Screening Catalog",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Model:** {model_name}",
        "",
        f"Total Specimens Captured: **{len(captures)}**",
        ""
    ]

    for i, spec in enumerate(captures):
        k = f"{spec['best_score']:.4f}"
        info = log_data.get(k, {"uuid": "??", "name": "Unknown", "desc": "No logged feedback.", "metrics": "N/A"})
        
        # Override UUID gracefully with eternal PyTorch file map if log parsing failed
        real_uuid = uuid_map.get(k, info["uuid"])
        info["uuid"] = real_uuid
        
        # Pull separate metadata JSON if it exists
        meta_json = get_specimen_metadata(real_uuid)
        if meta_json:
            if meta_json.get("name"): info["name"] = meta_json["name"]
            if meta_json.get("description"): info["desc"] = meta_json["description"]
            # Prefer outputs from metadata JSON if they were captured
            if meta_json.get("outputs"):
                # Use the first output as the description
                first_out = list(meta_json["outputs"].values())[0] if meta_json["outputs"] else None
                if first_out: info["desc"] = first_out
        
        # Fallback to outputs in JSONL (pushed by latest xeno_screener patch)
        if info["desc"] in ["N/A", "No logged feedback."] and spec.get("outputs"):
            first_out = list(spec["outputs"].values())[0] if spec["outputs"] else None
            if first_out: info["desc"] = first_out

        # Pull deep Token Autopsy Data + Naming Scaffold Data
        autopsy = get_autopsy_data(real_uuid)
        scaffold = get_scaffold_data(real_uuid)

        report.append(f"### {i+1}. {spec['best_score']:.4f} {get_badge(spec['best_score'])}")
        report.append(f"- **Trigger**: \"{spec['prompt']}\"")
        report.append(f"- **Model Concept Name**: {info['name']}")
        report.append(f"- **Metadata**: UUID: `{info['uuid']}` | Layer: {spec['layer']} | Execution Time: {spec['elapsed_seconds']}s")
        report.append(f"- **Evaluation Metrics**: `{info['metrics']}`")
        report.append(f"- **Model Feedback/Leak**: {info['desc']}")
        
        # Inject Token Autopsy Analysis
        if autopsy["text"] or autopsy["cloud"]:
            report.append(f"")
            report.append(f"#### 🧬 Token Autopsy Results")
            if autopsy["text"] and autopsy["text"]["status"]:
                badge = "🔴" if autopsy["text"]["status"] in ["COLLISION", "ECHO"] else "🟢"
                report.append(f"- **Classification**: {badge} **{autopsy['text']['status']}**")
            if autopsy["text"] and autopsy["text"]["reason"]:
                report.append(f"- **Diagnosis**: {autopsy['text']['reason']}")
            if autopsy["cloud"]:
                cloud = autopsy["cloud"]
                report.append(f"- **Mundane Mass**: {cloud.get('mundane_fraction', 0):.1%}")
                report.append(f"- **Novelty Coherence**: {cloud.get('novelty_coherence', 0):.2f}")
                domains = cloud.get('dominant_domains', [])
                if domains: report.append(f"- **Dominant Domains**: {', '.join(domains)}")

        # Also check specimen JSON for autopsy fields (written by new screener)
        elif meta_json and meta_json.get("autopsy_classification"):
            report.append(f"")
            report.append(f"#### 🧬 Token Autopsy Results")
            ac = meta_json["autopsy_classification"]
            badge = "🔴" if ac in ["COLLISION", "ECHO"] else "🟢"
            report.append(f"- **Classification**: {badge} **{ac}**")
            conf = meta_json.get("autopsy_confidence", -1)
            if conf >= 0: report.append(f"- **Confidence**: {conf:.0%}")
            rec = meta_json.get("autopsy_recommendation", "")
            if rec: report.append(f"- **Recommendation**: {rec}")
            reason = meta_json.get("autopsy_discard_reason", "")
            if reason: report.append(f"- **Diagnosis**: {reason}")
            mf = meta_json.get("autopsy_mundane_fraction", -1)
            nc = meta_json.get("autopsy_novelty_coherence", -1)
            if mf >= 0: report.append(f"- **Mundane Mass**: {mf:.1%}")
            if nc >= 0: report.append(f"- **Novelty Coherence**: {nc:.2f}")
            domains = meta_json.get("autopsy_dominant_domains", [])
            if domains: report.append(f"- **Dominant Domains**: {', '.join(domains)}")

        # Inject Naming Scaffold Analysis
        sc_class = scaffold.get("classification")
        sc_from_json = meta_json.get("scaffold_mode") if meta_json else None
        if sc_class or sc_from_json:
            report.append(f"")
            report.append(f"#### 🎭 Naming Scaffold Analysis")
            if sc_class:
                mode = sc_class.get("primary_mode", "UNCLASSIFIABLE")
                icon = get_scaffold_icon(mode)
                report.append(f"- **Scaffold Mode**: {icon} **{mode}**")
                secondary = sc_class.get("secondary_modes", [])
                if secondary: report.append(f"- **Secondary**: {', '.join(secondary)}")
                conf = sc_class.get("confidence", -1)
                if conf >= 0: report.append(f"- **Confidence**: {conf:.0%}")
                density = sc_class.get("scaffold_density", -1)
                if density >= 0: report.append(f"- **Scaffold Density**: {density:.0%}")
                switches = sc_class.get("persona_switches", 0)
                if switches: report.append(f"- **Persona Switches**: {switches}")
                interp = sc_class.get("interpretation", "")
                if interp: report.append(f"- **Interpretation**: {interp[:300]}")
            elif sc_from_json:
                # Fall back to fields on the specimen JSON
                mode = sc_from_json
                icon = get_scaffold_icon(mode)
                report.append(f"- **Scaffold Mode**: {icon} **{mode}**")
                conf = meta_json.get("scaffold_confidence", -1)
                if conf >= 0: report.append(f"- **Confidence**: {conf:.0%}")
                interp = meta_json.get("scaffold_interpretation", "")
                if interp: report.append(f"- **Interpretation**: {interp[:300]}")
        
        # Deep Insights for singularities (>0.35)
        if spec['best_score'] >= 0.35 and info['desc'] != "No logged feedback.":
            print(f"[{i+1}/{len(captures)}] Generating Deep Insight for {k}...")
            insight = get_insight(spec['prompt'], spec['best_score'], info['desc'])
            report.append(f"  > [!NOTE]")
            report.append(f"  > **Scientist's Post-Mortem**")
            report.append(f"  > {insight}")
        
        report.append("")
        report.append("---")
        report.append("")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
    hostname = socket.gethostname().lower().replace(" ", "_")
    filename = f"{hostname}_Screening_Report_DeepAnalysis_{timestamp}.md"
    reports_dir = os.path.join(ROOT_DIR, "results", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    filepath = os.path.join(reports_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    print(f"Report generated successfully: results/reports/{filename}")

if __name__ == "__main__":
    generate_report()
