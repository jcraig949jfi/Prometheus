"""Batch 09 depth (P6): when the ENVIRONMENT moves out from under a preserved artifact.

Found while making md5-rfc1321 runnable. RFC 1321's own reference implementation declares

    typedef unsigned long int UINT4;

which was a 32-bit type on the machines of 1992 and is a 64-bit type on today's LP64 targets.
The same preserved bytes, compiled by a modern toolchain, BUILD CLEANLY, RUN WITHOUT ERROR, and
print WRONG digests -- failing the test suite printed inside the very document that defines them.
No compiler warning, no crash, no signal: the artifact is silently wrong because the world changed.

This driver runs the identical extracted sources in two worlds and records what each produces
against the digests published in RFC 1321 section A.5.

    python run_environment_assumption.py -> ENVIRONMENT_ASSUMPTION_<date>.json

Techne records the divergence. It does not patch the fossil to make it pass (the charter forbids
modernising a fossil for a PASS), and it does not decide what the divergence means.
"""
import json, pathlib, subprocess, time

HERE = pathlib.Path(__file__).resolve().parent
VAULT = "/mnt/f/Prometheus/vault/fossils"
DATE = "2026-09-13"

# the digests RFC 1321 section A.5 prints for its own reference implementation
RFC_EXPECTED = {
    "": "d41d8cd98f00b204e9800998ecf8427e",
    "a": "0cc175b9c0f1b6a831c399e269772661",
    "abc": "900150983cd24fb0d6963f7d28e17f72",
    "message digest": "f96b697d7cb7938d525a2f31aaf161d0",
}

# Extraction is byte-identical in both worlds; only the compiler's data model differs.
SCRIPT = r'''
cd /tmp
R=/vault/md5-rfc1321/upstream/rfc1321.txt
strip_rfc() { grep -v '\[Page ' | grep -v '^RFC 1321' | tr -d '\f' \
  | awk '{ if ($0 ~ /^[[:space:]]*$/ && cont) next; print; cont = ($0 ~ /\\[[:space:]]*$/) }'; }
sed -n '/^A\.1 global\.h/,/^A\.2 md5\.h/p'      "$R" | sed '1d;$d' | strip_rfc > global.h
sed -n '/^A\.2 md5\.h/,/^A\.3 md5c\.c/p'        "$R" | sed '1d;$d' | strip_rfc > md5.h
sed -n '/^A\.3 md5c\.c/,/^A\.4 mddriver\.c/p'   "$R" | sed '1d;$d' | strip_rfc > md5c.c
sed -n '/^A\.4 mddriver\.c/,/^A\.5 Test suite/p' "$R" | sed '1d;$d' | strip_rfc > mddriver.c
printf 'int main(){return sizeof(unsigned long);}' > z.c
gcc -o z z.c 2>/dev/null; ./z; SZ=$?
echo "SIZEOF_UNSIGNED_LONG=$SZ"
echo "SOURCE_SHA256=$(cat global.h md5.h md5c.c mddriver.c | sha256sum | cut -d' ' -f1)"
gcc -w -DMD=5 -o mddriver md5c.c mddriver.c 2>&1 | head -3
./mddriver -x 2>&1 | head -8
'''


def _run(image):
    out = subprocess.run(["wsl.exe", "-e", "bash", "-lc",
        "docker run --rm -v %s:/vault:ro %s bash -lc %s" % (VAULT, image, _q(SCRIPT))],
        capture_output=True, text=True, timeout=900).stdout
    row = {"image": image, "sizeof_unsigned_long": None, "source_sha256": "", "digests": {}}
    for line in out.splitlines():
        if line.startswith("SIZEOF_UNSIGNED_LONG="):
            row["sizeof_unsigned_long"] = int(line.split("=", 1)[1])
        elif line.startswith("SOURCE_SHA256="):
            row["source_sha256"] = line.split("=", 1)[1].strip()
        elif line.startswith('MD5 ("') and ") = " in line:
            msg = line[len('MD5 ("'):line.rindex('") = ')]
            row["digests"][msg] = line.rsplit(" = ", 1)[1].strip()
    checked = {m: d for m, d in row["digests"].items() if m in RFC_EXPECTED}
    row["checked"] = {m: {"observed": d, "rfc_says": RFC_EXPECTED[m], "matches": d == RFC_EXPECTED[m]}
                      for m, d in checked.items()}
    row["all_match_rfc"] = bool(checked) and all(v["matches"] for v in row["checked"].values())
    return row


def main():
    rows = [_run("prometheus-fossil-i386:bookworm"), _run("prometheus-fossil-c:bookworm")]
    same_source = len({r["source_sha256"] for r in rows if r["source_sha256"]}) == 1
    doc = {"schema": "techne.fossil.environment_assumption/1",
           "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "fossil_driven": "md5-rfc1321",
           "assumption": "RFC 1321 global.h: typedef unsigned long int UINT4 -- i.e. `unsigned long` is 32 bits",
           "method": "extract the SAME appendix sources from the RFC text in two container worlds, compile with the same flags, run the RFC's own -x test suite, and compare against the digests printed in RFC 1321 section A.5.",
           "identical_source_in_both_worlds": same_source,
           "rfc_expected": RFC_EXPECTED, "rows": rows,
           "note": "The artifact is not patched. Where sizeof(unsigned long)==4 the 1992 code reproduces its own published digests; where it is 8 the same bytes compile and run without error and produce WRONG digests. A silent failure caused by the environment moving, not by the code changing. Techne records it; what it means is not Techne's question."}
    op = HERE / ("ENVIRONMENT_ASSUMPTION_%s.json" % DATE)
    op.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8", newline="\n")
    for r in rows:
        print("%-36s sizeof(ulong)=%-3s all_match_rfc=%-5s md5('')=%s" % (
            r["image"], r["sizeof_unsigned_long"], r["all_match_rfc"], r["digests"].get("", "?")))
    print("identical source in both worlds:", same_source)
    print("wrote", op)


def _q(s):
    return "'" + s.replace("'", "'\\''") + "'"


if __name__ == "__main__":
    main()
