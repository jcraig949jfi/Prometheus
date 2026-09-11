"""Does a Windows job object actually reap a whole process tree on THIS host?

EXTERNAL_BACKEND_CONTRACT.md section 2.1 requires a job object rather than
taskkill /T, and this is the evidence for that requirement rather than an
appeal to documentation. It launches a process that FORKS before it is killed
-- the case taskkill races -- and then closes the job handle.

    python tools/probe_process_tree_kill.py
    -> VERDICT: TREE REAPED        (measured 2026-09-11 on SKULLPORT)

Re-run it on any host before admitting a backend there. The contract is
explicit that a backend admitted on one cancellation mechanism is not admitted
on another, and this is how a host earns the claim.
"""
import ctypes
import subprocess
import sys
import time
from ctypes import wintypes

k = ctypes.windll.kernel32
k.CreateJobObjectW.restype = wintypes.HANDLE
k.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
k.OpenProcess.restype = wintypes.HANDLE


class _BASIC(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t),
                ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.POINTER(ctypes.c_ulong)),
                ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD)]


class _IO(ctypes.Structure):
    _fields_ = [("ReadOperationCount", ctypes.c_uint64),
                ("WriteOperationCount", ctypes.c_uint64),
                ("OtherOperationCount", ctypes.c_uint64),
                ("ReadTransferCount", ctypes.c_uint64),
                ("WriteTransferCount", ctypes.c_uint64),
                ("OtherTransferCount", ctypes.c_uint64)]


class _EXT(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", _BASIC), ("IoInfo", _IO),
                ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t)]


KILL_ON_JOB_CLOSE = 0x2000
JOB_MEMORY = 0x200
ACTIVE_PROCESS = 0x8

CHILD = ("import subprocess, sys, time\n"
         "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
         "time.sleep(120)\n")

job = k.CreateJobObjectW(None, None)
info = _EXT()
info.BasicLimitInformation.LimitFlags = (KILL_ON_JOB_CLOSE | JOB_MEMORY
                                         | ACTIVE_PROCESS)
info.BasicLimitInformation.ActiveProcessLimit = 8
info.JobMemoryLimit = 512 * 1024 * 1024
assert k.SetInformationJobObject(job, 9, ctypes.byref(info),
                                 ctypes.sizeof(info)), ctypes.GetLastError()

p = subprocess.Popen([sys.executable, "-c", CHILD])
h = k.OpenProcess(0x1F0FFF, False, p.pid)
assert k.AssignProcessToJobObject(job, h), ctypes.GetLastError()
time.sleep(2.0)

# wmic is gone on this Windows build; PowerShell's CIM is the replacement.
out = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "(Get-CimInstance Win32_Process -Filter 'ParentProcessId=%d')"
     ".ProcessId" % p.pid],
    capture_output=True, text=True).stdout
grandchildren = [x for x in out.split() if x.isdigit()]
print("parent pid          %d" % p.pid)
print("grandchildren       %s" % grandchildren)

k.CloseHandle(job)                      # the whole tree dies with the job
time.sleep(1.5)
print("parent alive after  %s" % (p.poll() is None))
still = []
for g in grandchildren:
    r = subprocess.run(["tasklist", "/FI", "PID eq %s" % g],
                       capture_output=True, text=True).stdout
    if g in r:
        still.append(g)
print("grandchildren alive %s" % (still or "none"))
print("VERDICT: %s" % ("TREE REAPED" if p.poll() is not None and not still
                       else "SURVIVORS -- job object insufficient here"))
