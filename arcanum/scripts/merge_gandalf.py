import shutil
import os
import socket
from datetime import datetime

# --- CONFIGURATION ---
SOURCE_DIR = r"C:\skullport_shared"
LOCAL_DIR = r"F:\Arcanum ∞"
BACKUP_DIR = os.path.join(LOCAL_DIR, "_pre_merge_backups", datetime.now().strftime("%Y%m%d_%H%M%S"))

REMOTE_RESULTS = os.path.join(SOURCE_DIR, "results")
LOCAL_RESULTS = os.path.join(LOCAL_DIR, "results")
REMOTE_PROMPTS = os.path.join(SOURCE_DIR, "PromptAndQuestions.md")

def backup_local():
    """Create a backup of the local results and questions before merging."""
    print(f"--- Creating safety backup at {BACKUP_DIR} ---")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    for sub in ["results", "questions", "docs"]:
        local_path = os.path.join(LOCAL_DIR, sub)
        if os.path.exists(local_path):
            shutil.copytree(local_path, os.path.join(BACKUP_DIR, sub))
            print(f"Backed up {sub}/")
            
def merge_files(src_sub, dst_sub, ext_filter=None):
    """Safely copy files from remote subfolder to local, avoiding name collisions."""
    src_full = os.path.join(REMOTE_RESULTS, src_sub)
    dst_full = os.path.join(LOCAL_RESULTS, dst_sub)
    
    if not os.path.exists(src_full):
        print(f"Warning: {src_full} not found, skipping.")
        return
        
    os.makedirs(dst_full, exist_ok=True)
    
    count = 0
    skipped = 0
    for f in os.listdir(src_full):
        if ext_filter and not f.endswith(ext_filter): continue
        
        src_file = os.path.join(src_full, f)
        dst_file = os.path.join(dst_full, f)
        
        if os.path.exists(dst_file):
            # Collision detection
            skipped += 1
            # print(f"  [SKIPPED] collision: {f}")
        else:
            shutil.copy2(src_file, dst_file)
            count += 1
            
    print(f"Merged {src_sub}/: {count} new files copied, {skipped} skipped (duplicates/collisions).")

def merge_logs():
    """Injest the main screening_log from Gandalf."""
    src_log = os.path.join(REMOTE_RESULTS, "screening", "screening_log.jsonl")
    dst_log = os.path.join(LOCAL_RESULTS, "screening", "screening_log_gandalf.jsonl")
    
    if os.path.exists(src_log):
        if os.path.exists(dst_log):
            os.remove(dst_log)
            print(f"Removed stale 'screening_log_gandalf.jsonl' (will re-import fresh copy).")
        shutil.copy2(src_log, dst_log)
        print(f"Injected Gandalf's screening log as 'screening_log_gandalf.jsonl'")
    else:
        print(f"No log file found at {src_log}. Skipping log merge.")

def merge_prompts():
    """Copy the provocation source list."""
    dst_prompts = os.path.join(LOCAL_DIR, "docs", "PromptAndQuestions_gandalf.md")
    if os.path.exists(REMOTE_PROMPTS):
        if not os.path.exists(dst_prompts):
            shutil.copy2(REMOTE_PROMPTS, dst_prompts)
            print(f"Integrated Gandalf's Prompt list as 'PromptAndQuestions_gandalf.md'")
        else:
            print(f"Gandalf's Prompt list already exists in docs. Skipping.")
    else:
        print(f"Warning: Prompt file missing on remote shared drive: {REMOTE_PROMPTS}")

def run_db_build():
    """Regenerate the discovery database after the merge."""
    print("--- Regenerating Discovery Database (Consolidating skullport + gandalf) ---")
    script_path = os.path.join(LOCAL_DIR, "scripts", "build_question_db.py")
    if os.path.exists(script_path):
        import subprocess
        subprocess.run(["python", script_path])
    else:
        print("Build script not found. You will need to run it manually.")

if __name__ == "__main__":
    print(f"########################################")
    print(f"   ARCANUM-INFINITY MACHINE MERGER")
    print(f"   Merging GANDALF -> SKULLPORT")
    print(f"########################################\n")
    
    backup_local()
    
    print("\n--- Merging Results ---")
    # 1. Reports
    merge_files("reports", "", ext_filter=".md")
    
    # 2. Specimens
    merge_files(os.path.join("screening", "specimens"), os.path.join("screening", "specimens"))
    
    # 3. Plots
    merge_files(os.path.join("screening", "plots"), os.path.join("screening", "plots"))
    
    # 4. Logs
    merge_logs()
    
    # 5. Prompts
    merge_prompts()
    
    print("\n--- Finalizing ---")
    run_db_build()
    
    print(f"\nMerge Complete. You should verify the results in 'questions/DiscoveryDB.md'.")
