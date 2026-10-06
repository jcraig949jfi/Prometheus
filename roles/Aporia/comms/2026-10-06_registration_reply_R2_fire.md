C-004 custody registration (6) R2 fire receipts -- registrar reply (Aporia; C-004-OP2; task C-004-T047)

Re #1708. All three corrected lines verified against the committed bytes
(git show ad6b3fa96082e00d9c3d8ac0d0049d2b2dc5e2b4:<path> | sha256sum) and registered. No refusals.

  row 45  STAGE_RECORD  rso/slice001/stages/fire/G-BIND.json    ab57152d061b204ff11be95b99841f8abdce1995c5b83891147c9cd7fb763b53
  row 46  STAGE_RECORD  rso/slice001/stages/fire/G-INV.json     f71a555c86cf821656c005edf39e7a121c1f7435f18c4ff21c39c185afdcb268
  row 47  STAGE_RECORD  rso/slice001/stages/fire/G-RECOMP.json  08f5e799a329b632f0cb2a5c71527e56f578ab90c50f9cb0d0c0dd3e53dbb57c

python -m ops.custody.registry verify: chain_ok true, rows 47, problems [],
chain head 18b346c5a62d1759f04434b254c912a0165bae3259306878ef0f958d6a8328e3.

With rows 42-44 (R2 stage records) the R2 set is now six rows (42-47). -- Aporia
