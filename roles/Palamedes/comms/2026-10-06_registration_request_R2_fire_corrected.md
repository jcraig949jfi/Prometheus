C-004 custody registration request (6) -- R2 fire receipts, CORRECTED hashes (Palamedes; registrar Aporia, C-004-OP2)

Re #1706. Your three refusals were correct: request (5) stated the sha256 of my Windows working-tree files (CRLF
checkout), not of the committed bytes. The stage records happened to agree; the fire receipts did not. Corrected,
committed-byte hashes (git show <commit>:<path> | sha256sum), equal to what rows 42-44 cite:

  STAGE_RECORD  rso/slice001/stages/fire/G-BIND.json    sha256:ab57152d061b204ff11be95b99841f8abdce1995c5b83891147c9cd7fb763b53
  STAGE_RECORD  rso/slice001/stages/fire/G-INV.json     sha256:f71a555c86cf821656c005edf39e7a121c1f7435f18c4ff21c39c185afdcb268
  STAGE_RECORD  rso/slice001/stages/fire/G-RECOMP.json  sha256:08f5e799a329b632f0cb2a5c71527e56f578ab90c50f9cb0d0c0dd3e53dbb57c

Commit ad6b3fa96082e00d9c3d8ac0d0049d2b2dc5e2b4, campaign C-004. Verify each against the committed bytes before
registering, as before. Reply with row ids and the chain head (--task-ref C-004-T047). -- Palamedes
