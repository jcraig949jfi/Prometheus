import sys
import time
from pathlib import Path

# Result directory for Xenolexicon
RESULTS_DIR        = Path("results/xenolexicon")
STOP_FILE          = RESULTS_DIR / "STOP"
PID_FILE           = RESULTS_DIR / "orchestrator.pid"

def is_process_running(pid):
    """Check if a process with the given PID is still running (Windows-safe)."""
    try:
        import psutil
        return psutil.pid_exists(pid)
    except ImportError:
        pass

    import sys
    if sys.platform == "win32":
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if handle == 0:
            return False
        exit_code = ctypes.c_ulong()
        ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
        ctypes.windll.kernel32.CloseHandle(handle)
        STILL_ACTIVE = 259
        return exit_code.value == STILL_ACTIVE
    else:
        import os
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

def main():
    # Ensure results directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Check if orchestrator is even running
    if not PID_FILE.exists():
        print("[Xenolexicon] No 'orchestrator.pid' found. Is the orchestrator running?")
        sys.exit(1)
        
    try:
        pid = int(PID_FILE.read_text().strip())
    except Exception as e:
        print(f"[Xenolexicon] Could not read PID from {PID_FILE}: {e}")
        pid = None

    # 2. Check if the process is already gone before we even signal
    if pid and not is_process_running(pid):
        print(f"[Xenolexicon] Process {pid} is not running (already exited).")
        if STOP_FILE.exists():
            STOP_FILE.unlink()
            print("[Xenolexicon] Cleaned up stale STOP semaphore.")
        sys.exit(0)

    # 3. Create the STOP semaphore
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Manual shutdown"
    print(f"\n[Xenolexicon] Signaling STOP to orchestrator (PID: {pid if pid else 'unknown'})...")
    STOP_FILE.write_text(msg, encoding="utf-8")

    # 4. Wait for the orchestrator to exit
    if pid:
        print(f"[Xenolexicon] Waiting for process {pid} to shut down gracefully...")
        start_time = time.time()
        try:
            while is_process_running(pid):
                elapsed = time.time() - start_time
                print(f"\r  Waiting... ({int(elapsed)}s elapsed)", end="", flush=True)
                time.sleep(1)
            print(f"\n[Xenolexicon] SUCCESS: Process {pid} has exited.")
        except KeyboardInterrupt:
            print("\n[Xenolexicon] Wait cancelled by user. Semaphore is still set.")
            sys.exit(0)
    else:
        print("[Xenolexicon] Semaphore set. (Cannot verify shutdown without valid PID file)")

    print("[Xenolexicon] Shutdown complete.\n")

if __name__ == "__main__":
    main()
