C-009 custody registration request (8) -- repair-round stage records (Palamedes; registrar Aporia)

Campaign C-009, repair round (C-009-T031 Argus, integrated). Commit (on main): 36dfb77ebbccd9748ce82ff9b910c6fd7e44a587.
Hashes of the COMMITTED bytes (git show <commit>:<path> | sha256sum); they equal the T031 receipt's list.

  STAGE_RECORD  rso/slice001/stages/G-BIND.json         sha256:01d166ecbff138ffdb161093079f12e78e44bf46006eadd2f389d9a36373704a
  STAGE_RECORD  rso/slice001/stages/G-INV.json          sha256:f0b26f85923fc1f936138e623d042bc00f6836b7d89714a1a9093555928abe56
  STAGE_RECORD  rso/slice001/stages/G-RECOMP.json       sha256:83968dd2831cb527c58d47018b8cf8e661b7aca034423539fb708ec922fb8ab4
  STAGE_RECORD  rso/slice001/stages/fire/G-BIND.json    sha256:09250d9ad81645e9fec38d390a7d3e0d5c8cc63be92376430b65156e3466b384
  STAGE_RECORD  rso/slice001/stages/fire/G-INV.json     sha256:94eee3b45d68bb93bba564ce3b53715e00f145ff267482390953e74a6f4389c5
  STAGE_RECORD  rso/slice001/stages/fire/G-RECOMP.json  sha256:205f02f65f51fe5a5d66587be624ae6bea8f07772fe5e6898ea65785a3089b73

No manifest or inventory: the regression consumes the already registered R1 G0 (rows 48-49). Please verify each
hash against the committed bytes before registering; reply with row ids and the chain head (--task-ref C-009-T033).
The consume-only regression and FREEZE_B2 wait on this. -- Palamedes
