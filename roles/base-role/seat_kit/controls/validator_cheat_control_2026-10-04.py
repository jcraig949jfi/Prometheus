"""Cheat control for new_seat.validate(): a good seat passes; each injected defect is caught."""
import json, pathlib, shutil, subprocess, sys, tempfile

WT = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(WT / "roles/base-role/seat_kit"))
import new_seat

SEAT, CDIR = "Hestia", "prompts/2026-10-04_creation"
tmp = pathlib.Path(tempfile.mkdtemp(prefix="vcheat_"))

def sh(*a, cwd=tmp):
    subprocess.run(a, cwd=cwd, check=True, capture_output=True)

def fresh():
    if (tmp / "roles").exists():
        shutil.rmtree(tmp / "roles")
    shutil.copytree(WT / "roles/Hestia", tmp / "roles/Hestia")
    (tmp / "roles/base-role").mkdir(parents=True, exist_ok=True)
    shutil.copy(WT / "roles/base-role/INHERITANCE.md", tmp / "roles/base-role/INHERITANCE.md")
    if not (tmp / "comms").exists():
        shutil.copytree(WT / "comms", tmp / "comms", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(WT / ".gitignore", tmp / ".gitignore")

sh("git", "init", "-q")
cases = {}
fresh(); cases["GOOD seat"] = new_seat.validate(tmp, SEAT, CDIR)

fresh(); p = tmp / "roles/Hestia/RESPONSIBILITIES.md"
t = p.read_text(encoding="utf-8").splitlines(); t[2] = "> (banner removed)"; p.write_text("\n".join(t) + "\n", encoding="utf-8")
cases["no banner"] = new_seat.validate(tmp, SEAT, CDIR)

fresh(); p = tmp / "roles/Hestia/STATUS.md"; p.write_bytes(p.read_bytes() + "caf\u00e9\n".encode("utf-8"))
cases["non-ASCII in a status file"] = new_seat.validate(tmp, SEAT, CDIR)

fresh(); p = tmp / "roles/Hestia/TODO.md"; p.write_bytes(p.read_bytes().replace(b"\n", b"\r\n"))
cases["CRLF in a file"] = new_seat.validate(tmp, SEAT, CDIR)

fresh(); p = tmp / "roles/Hestia" / CDIR / "02_OPERATOR_CREATION_verbatim.md"; p.write_bytes(p.read_bytes() + b"tampered\n")
cases["tampered verbatim file (manifest)"] = new_seat.validate(tmp, SEAT, CDIR)

fresh(); p = tmp / "roles/base-role/INHERITANCE.md"; raw = p.read_bytes()
eol = b"\r\n" if b"\r\n" in raw else b"\n"
p.write_bytes(eol.join(l for l in raw.split(eol) if l != b"| Hestia | RESPONSIBILITIES.md |"))
cases["entry-file row missing"] = new_seat.validate(tmp, SEAT, CDIR)

fresh(); (tmp / "roles/Hestia/WORK_STATE.json").write_text(json.dumps({"seat": "Hestia", "state": "ACTIVE"}))
cases["WORK_STATE wrong"] = new_seat.validate(tmp, SEAT, CDIR)

fresh(); (tmp / "roles/Hestia/WAKE.md").unlink()
cases["file missing"] = new_seat.validate(tmp, SEAT, CDIR)

ok = True
for name, bad in cases.items():
    good_case = name == "GOOD seat"
    verdict = (not bad) if good_case else bool(bad)
    ok &= verdict
    print("%-38s %-6s %s" % (name, "OK" if verdict else "WRONG", "[]" if not bad else "; ".join(bad)[:110]))
print("CONTROL", "PASSED" if ok else "FAILED")
shutil.rmtree(tmp, ignore_errors=True)
