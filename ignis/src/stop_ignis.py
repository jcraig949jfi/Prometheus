import sys
import time
from pathlib import Path

# Result directory matching IgnisConfig default
RESULTS_DIR        = Path("results/ignis")
STOP_FILE          = RESULTS_DIR / "STOP"
PID_FILE           = RESULTS_DIR / "orchestrator.pid"
WATCHMAN_STOP_FILE = RESULTS_DIR / "WATCHMAN_STOP"

def is_process_running(pid):
    """Check if a process with the given PID is still running (Windows-safe).

    os.kill(pid, 0) on Windows raises OSError that Python wraps in SystemError,
    so we use psutil when available, then fall back to ctypes OpenProcess.
    """
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
        print("[Ignis] No 'orchestrator.pid' found. Is SETI running?")
        sys.exit(1)
        
    try:
        pid = int(PID_FILE.read_text().strip())
    except Exception as e:
        print(f"[Ignis] Could not read PID from {PID_FILE}: {e}")
        pid = None

    # 2. Signal the Night Watchman unconditionally — it may be running even if
    #    the orchestrator is already dead (crash, manual kill, etc.)
    WATCHMAN_STOP_FILE.write_text("pipeline stopped", encoding="utf-8")

    # 3. Check if the process is already gone before we even signal
    if pid and not is_process_running(pid):
        print(f"[Ignis] Process {pid} is not running (already exited).")
        if STOP_FILE.exists():
            STOP_FILE.unlink()
            print("[Ignis] Cleaned up stale STOP semaphore.")
        print("[Ignis] Watchman quiesce signal written (WATCHMAN_STOP).")
        sys.exit(0)

    # 4. Create the STOP semaphore
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Manual shutdown"
    print(f"\n[Ignis] Signaling STOP to orchestrator (PID: {pid if pid else 'unknown'})...")
    STOP_FILE.write_text(msg, encoding="utf-8")

    # 4. Wait for the orchestrator to exit (Smart Mode)
    if pid:
        print(f"[Ignis] Waiting for process {pid} to shut down gracefully and release VRAM...")
        start_time = time.time()
        try:
            while is_process_running(pid):
                elapsed = time.time() - start_time
                print(f"\r  │ Waiting... ({int(elapsed)}s elapsed)", end="", flush=True)
                time.sleep(1)
            print(f"\n[Ignis] SUCCESS: Process {pid} has exited.")
        except KeyboardInterrupt:
            print("\n[Ignis] Wait cancelled by user. Semaphore is still set.")
            sys.exit(0)
    else:
        print("[Ignis] Semaphore set. (Cannot verify shutdown without valid PID file)")

    print("[Ignis] Watchman quiesce signal written (WATCHMAN_STOP).")
    print("[Ignis] Shutdown complete. VRAM should now be clear.\n")

if __name__ == "__main__":
    main()
