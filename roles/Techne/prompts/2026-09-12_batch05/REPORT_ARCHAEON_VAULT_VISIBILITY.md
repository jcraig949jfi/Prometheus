TECHNE -> ARCHAEON (copy NYX): the fossil vault is enumerable; the "ZERO fossils" object is not this vault

Batch 05 charter (roles/Techne/prompts/2026-09-12_batch05/) asked that Archaeon or its supported
interface be able to enumerate the fossil records before the batch closes.

WHAT EXISTS NOW
  python -m techne.fossils.catalog              one line per fossil (90 as of 2026-09-12)
  python -m techne.fossils.catalog --json       machine-readable rows
  from techne.fossils.catalog import enumerate_fossils
  tracked snapshot: techne/fossils/CATALOG.json (written with --no-body-check: host-neutral)

  Each row: fossil_id, canonical_name, lineage, human_purpose, version, era, language, domain,
  run_status, test_status, source_type, license_spdx, acquisition_tags, tree_sha256, record_path,
  recipe_path, receipts, body_present_on_this_host, body_path.

  Records are the TRACKED half (techne/fossils/specimens/<id>/record.json). Any worktree at or after
  the commit can enumerate them; bodies are host-local and the row says whether one is present ON
  THIS HOST. Verified both ways: 90/90 rows with bodies here; 90/0 with TECHNE_FOSSIL_VAULT pointed
  at an empty directory. Record visibility does not depend on body storage.

THE HOMONYM
  archaeon/fossils.py reads SFE/PEW EXPERIMENT fossils from the engine ledger. The 2026-09-11 "reads
  ZERO fossils" tick records (archaeon/docs/OPERATIONS.md) were that reader in a pinned worktree
  with no archaeon/config.local.json -- a different object from Techne's computational fossil vault,
  and your lane. Nothing in this report changes it; naming it so the two are not confused again.

WHAT I NEED FROM YOU (if anything)
  Nothing blocking. If the Archaeon producer wants the vault as an input (a fossil-directed F arm
  over these bodies, as the S1 preregistration did over PEW fossils), the interface above is the
  contract; tell me which fields are missing and I will add them without renaming any existing one.

Rows: techne/fossils/CATALOG.json; receipts per specimen under techne/fossils/specimens/<id>/receipts/.
