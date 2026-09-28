
## 2026-09-28: operator rulings D1 / D4-H5 (Cosmos #788)

- **D1 (done).** The original seal a56ef7787 was merged into main by merge commit 7c018d92b. The sealed files are
  byte-identical; sha256(sealed_spec_D.json) is still ae4479c6...57ac. The original hidden set is now EXPOSED and is
  never to be used blind.
- **D4 / H5, opaque successor D2.**
  - Location: prometheus/cosmos/c3_holdout_D2/ on main, commit 95b31a30d.
  - A fresh 128-world hidden set, disjoint from the exposed D worlds, is committed as AES-256-GCM ciphertext
    (sha256 f75ba333...fc9f).
  - Salted commitment: sha256(salt||plaintext) = 69f91153...9c4b. spec_id e2d3213b...d9fe.
  - The key, salt and plaintext exist only on M1, outside every repository. Nestor is the custodian.
  - The runner enforces hash-bound package loading and predict-before-certify.
  - The self-test passed. Nestor's own check found no secret material in the repo files.
  - The independent firewall check was requested from Harmonia (repo / M2 side) and Ananke (M1 host side) in comms
    #796. The public report goes to Cosmos after it returns.
