"""Mint a self-signed TLS cert/key for an Engine host.

    python deploy/make_cert.py --ip 192.168.1.191 --prefix m2

Writes <prefix>.crt (PUBLIC — commit it, clients trust it) and <prefix>.key
(PRIVATE — never leaves this machine, never enters git; deploy/.gitignore
excludes *.key). CN and SAN are both the bind IP, so a client that pins the
cert as its CA verifies the hostname it dialled.

Existing files are never overwritten: rotating a key is a deliberate act that
invalidates every client's trust anchor, so it must be an explicit removal
first.
"""
from __future__ import annotations

import argparse
import datetime as dt
import ipaddress
import sys
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ip", required=True, help="bind IP; becomes CN and SAN")
    ap.add_argument("--prefix", required=True, help="output basename, e.g. m2")
    ap.add_argument("--days", type=int, default=1200)
    ap.add_argument("--out-dir", default=str(Path(__file__).resolve().parent))
    args = ap.parse_args()

    ip = ipaddress.ip_address(args.ip)
    out = Path(args.out_dir)
    crt_path = out / f"{args.prefix}.crt"
    key_path = out / f"{args.prefix}.key"
    for p in (crt_path, key_path):
        if p.exists():
            print(f"ERROR: {p} exists; refusing to overwrite a live trust "
                  f"anchor. Remove it deliberately to rotate.", file=sys.stderr)
            return 2

    key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, str(ip))])
    now = dt.datetime.now(dt.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(minutes=5))
        .not_valid_after(now + dt.timedelta(days=args.days))
        .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ip)]),
                       critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None),
                       critical=True)
        .sign(key, hashes.SHA256())
    )

    key_path.write_bytes(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()))
    crt_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    print(f"wrote {crt_path} (public) and {key_path} (PRIVATE — keep local)")
    print(f"CN/SAN = {ip}, valid until {cert.not_valid_after_utc.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
