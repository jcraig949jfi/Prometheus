"""Operational provenance: identity-check and terminate ONE orphaned process by PID, per operator ruling.
Refuses unless every check passes.  Records everything before acting.  Usage: python -m alien_circuitry.ops.recover_pid 20436
"""
import datetime, json, os, sys, time
import psutil

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED_NAME = "tail.exe"
EXPECTED_CMD_TAIL = ["-8"]
EXPECTED_EXE_FRAGMENT = os.path.join("Git", "usr", "bin")


def main(pid: int):
    rec = {"timestamp": datetime.datetime.now().isoformat(), "pid": pid}
    p = psutil.Process(pid)
    rec["name"] = p.name(); rec["exe"] = p.exe(); rec["cmdline"] = p.cmdline(); rec["status"] = p.status()
    rec["create_time"] = datetime.datetime.fromtimestamp(p.create_time()).isoformat(); rec["rss_MB"] = round(p.memory_info().rss / 2 ** 20)
    for k, fn in (("username", p.username), ("cwd", p.cwd), ("ppid", p.ppid)):
        try: rec[k] = fn()
        except Exception as e: rec[k] = f"unavailable: {e}"
    try:
        par = p.parent(); rec["parent"] = None if par is None else {"pid": par.pid, "name": par.name()}
    except Exception as e:
        rec["parent"] = f"unavailable: {e}"
    checks = {
        "is_tail_exe": rec["name"].lower() == EXPECTED_NAME,
        "same_cmdline_as_observed": rec["cmdline"][1:] == EXPECTED_CMD_TAIL and rec["cmdline"][0].lower().endswith(EXPECTED_NAME),
        "exe_is_git_usr_bin_tail": EXPECTED_EXE_FRAGMENT.lower() in rec["exe"].lower(),
        "no_live_parent_or_ownership": rec["parent"] is None,
        "rss_about_6_5GB": 5000 <= rec["rss_MB"] <= 9000,
        "not_system_critical": rec["name"].lower() not in {"system", "csrss.exe", "wininit.exe", "services.exe", "lsass.exe", "svchost.exe", "vmmemwsl", "vmmem", "python.exe", "nvidia-smi.exe"},
    }
    rec["identity_checks"] = checks; rec["all_checks_pass"] = all(checks.values())
    print(json.dumps(rec, indent=1))
    if rec["all_checks_pass"]:
        p.kill(); time.sleep(1.5)
        rec["terminated"] = not psutil.pid_exists(pid); rec["termination_time"] = datetime.datetime.now().isoformat()
        rec["available_GB_after"] = round(psutil.virtual_memory().available / 2 ** 30, 2)
    else:
        rec["terminated"] = False; rec["reason"] = "identity checks failed; NOT terminated"
    os.makedirs(os.path.join(HERE, "results", "ops"), exist_ok=True)
    with open(os.path.join(HERE, "results", "ops", f"process_recovery_pid{pid}.json"), "w") as f:
        json.dump(rec, f, indent=1)
    print("terminated:", rec["terminated"], "available_GB_after:", rec.get("available_GB_after"))


if __name__ == "__main__":
    main(int(sys.argv[1]))
