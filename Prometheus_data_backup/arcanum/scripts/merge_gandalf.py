import argparse
import shutil
import os
import sys
import socket
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION ---
DEFAULT_SOURCE_DIR = r"C:\skullport_shared"
LOCAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(LOCAL_DIR, "_pre_merge_backups", datetime.now().strftime("%Y%m%d_%H%M%S"))


def backup_local():
    """Create a backup of the local results and questions before merging."""
    print(f"--- Creating safety backup at {BACKUP_DIR} ---")
    os.makedirs(BACKUP_DIR, exist_ok=True)

    for sub in ["results", "questions", "docs"]:
        local_path = os.path.join(LOCAL_DIR, sub)
        if os.path.exists(local_path):
            shutil.copytree(local_path, os.path.join(BACKUP_DIR, sub))
            print(f"Backed up {sub}/")


def merge_files(src_base, src_sub, dst_sub, ext_filter=None):
    """Safely copy files from remote subfolder to local, avoiding name collisions."""
    src_full = os.path.join(src_base, src_sub)
    dst_full = os.path.join(LOCAL_DIR, "results", dst_sub)

    if not os.path.exists(src_full):
        print(f"Warning: {src_full} not found, skipping.")
        return 0

    os.makedirs(dst_full, exist_ok=True)

    count = 0
    skipped = 0
    for f in os.listdir(src_full):
        src_file = os.path.join(src_full, f)
        if not os.path.isfile(src_file):
            continue
        if ext_filter and not f.endswith(ext_filter):
            continue

        dst_file = os.path.join(dst_full, f)

        if os.path.exists(dst_file):
            skipped += 1
        else:
            shutil.copy2(src_file, dst_file)
            count += 1

    print(f"Merged {src_sub} → {dst_sub}: {count} new, {skipped} skipped (duplicates).")
    return count


def merge_logs(source_dir):
    """Ingest the main screening_log from Gandalf."""
    src_log = os.path.join(source_dir, "results", "screening", "screening_log.jsonl")
    dst_log = os.path.join(LOCAL_DIR, "results", "screening", "screening_log_gandalf.jsonl")

    os.makedirs(os.path.dirname(dst_log), exist_ok=True)

    if os.path.exists(src_log):
        if os.path.exists(dst_log):
            os.remove(dst_log)
            print("Removed stale 'screening_log_gandalf.jsonl' (will re-import fresh copy).")
        shutil.copy2(src_log, dst_log)
        print("Injected Gandalf's screening log as 'screening_log_gandalf.jsonl'")
        return True
    else:
        print(f"No log file found at {src_log}. Skipping log merge.")
        return False


def merge_prompts(source_dir):
    """Copy the provocation source list."""
    remote_prompts = os.path.join(source_dir, "PromptAndQuestions.md")
    dst_prompts = os.path.join(LOCAL_DIR, "docs", "PromptAndQuestions_gandalf.md")
    if os.path.exists(remote_prompts):
        if not os.path.exists(dst_prompts):
            shutil.copy2(remote_prompts, dst_prompts)
            print("Integrated Gandalf's Prompt list as 'PromptAndQuestions_gandalf.md'")
        else:
            print("Gandalf's Prompt list already exists in docs. Skipping.")
    else:
        print(f"Warning: Prompt file missing at: {remote_prompts}")


def run_db_build():
    """Regenerate the discovery database after the merge."""
    print("\n--- Regenerating Discovery Database (Consolidating skullport + gandalf) ---")
    script_path = os.path.join(LOCAL_DIR, "scripts", "build_question_db.py")
    if os.path.exists(script_path):
        import subprocess
        result = subprocess.run([sys.executable, script_path], cwd=LOCAL_DIR)
        if result.returncode != 0:
            print(f"[WARN] build_question_db.py exited with code {result.returncode}")
    else:
        print("Build script not found. You will need to run it manually.")


def main():
    parser = argparse.ArgumentParser(
        description="Arcanum Infinity — Merge Gandalf results into local workspace",
    )
    parser.add_argument("--source", default=DEFAULT_SOURCE_DIR,
                        help=f"Path to Gandalf's shared results (default: {DEFAULT_SOURCE_DIR})")
    parser.add_argument("--skip-backup", action="store_true",
                        help="Skip the safety backup (faster, riskier)")
    parser.add_argument("--skip-db-build", action="store_true",
                        help="Skip the discovery database rebuild")
    args = parser.parse_args()

    source_dir = args.source
    remote_results = os.path.join(source_dir, "results")

    print("########################################")
    print("   ARCANUM-INFINITY MACHINE MERGER")
    print(f"   Merging GANDALF -> {socket.gethostname().upper()}")
    print(f"   Source: {source_dir}")
    print(f"   Target: {LOCAL_DIR}")
    print("########################################\n")

    if not os.path.exists(source_dir):
        print(f"[ERROR] Source directory not found: {source_dir}")
        print("Use --source <path> to specify the correct location.")
        sys.exit(1)

    if not args.skip_backup:
        backup_local()

    print("\n--- Merging Results ---")
    total = 0

    # 1. Reports — source: results/reports → dest: results/reports
    total += merge_files(remote_results, "reports", "reports", ext_filter=".md")

    # 2. Specimens — all file types (.pt, .json, .txt)
    total += merge_files(remote_results,
                         os.path.join("screening", "specimens"),
                         os.path.join("screening", "specimens"))

    # 3. Plots
    total += merge_files(remote_results,
                         os.path.join("screening", "plots"),
                         os.path.join("screening", "plots"))

    # 4. Logs
    merge_logs(source_dir)

    # 5. Prompts
    merge_prompts(source_dir)

    print(f"\n--- Total new files merged: {total} ---")

    # 6. Rebuild discovery database
    if not args.skip_db_build:
        run_db_build()

    print(f"\nMerge Complete. Verify results in 'questions/DiscoveryDB.md'.")


if __name__ == "__main__":
    main()
