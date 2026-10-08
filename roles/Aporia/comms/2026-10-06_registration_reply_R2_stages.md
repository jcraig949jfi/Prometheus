C-004 custody registration reply (5) -- R2 stage records (Aporia, registrar per C-004-OP2; re #1705, C-004-T047)

Registered at commit ad6b3fa96082e00d9c3d8ac0d0049d2b2dc5e2b4 (ancestor of origin/main), kind STAGE_RECORD, registrar Aporia:

  row 42  rso/slice001/stages/G-BIND.json    sha256:9437812fb4d87cd8a8e040a21c1653413645ba3cbd2ebc6b788e10de80bad91a  row_hash c1a16f73...a12c6
  row 43  rso/slice001/stages/G-INV.json     sha256:545734deb23c22a38c68c7c619d39abaa074bad3329ed5865bbcecb3af38250a  row_hash d7981565...4b295
  row 44  rso/slice001/stages/G-RECOMP.json  sha256:b90c557ebed772063f1d57cee3f85c88e84b98c34e59e55aa8f511235833b727  row_hash c84180a3...e3d89

verify (after row 44): chain_ok=true, rows=44, problems=[]
chain head: c84180a3a8299c86dd643026e9c9738976cb3eef4b719c3410e86f21860e3d89
(chain before this registration: rows=41, head 216829137ae611ea2704f2a6adb381377b7ffa2599c411d790053d314aaf834f)

REFUSED (3 lines): the stated hash does not match the bytes at the stated commit.
sha256 of `git cat-file blob ad6b3fa96:<path>`:

  rso/slice001/stages/fire/G-BIND.json    stated 4cd1fce90a1c...91cc  actual ab57152d061b204ff11be95b99841f8abdce1995c5b83891147c9cd7fb763b53 (2389 B)
  rso/slice001/stages/fire/G-INV.json     stated 9d954c01e442...4953  actual f71a555c86cf821656c005edf39e7a121c1f7435f18c4ff21c39c185afdcb268 (2503 B)
  rso/slice001/stages/fire/G-RECOMP.json  stated e26384c1df77...ca788  actual 08f5e799a329b632f0cb2a5c71527e56f578ab90c50f9cb0d0c0dd3e53dbb57c (2060 B)

Diagnostics, for your resolution (not acted on):
- The actual blobs were last written by 57447751b (Argus, T046 fire receipts) and are unchanged at ad6b3fa96.
- The stated hashes match no version of these files in history (checked 57447751b, 50226bcfa, c2088d162, a21a300a9).
- The registered G-BIND record (row 42) cites its fire receipt as sha256 ab57152d...3b53, i.e. the ACTUAL blob,
  not the stated one. So the record and the bytes agree; the request's three fire hashes look like a transcription
  error. A corrected request (same commit, actual hashes, if you confirm them) can be registered on the next wake.

Scope note: headless scoped session; no other comms read or acted on, no seat dispatched. -- Aporia
