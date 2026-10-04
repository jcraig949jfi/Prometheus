Re #1411 / #1417 (stage-record version convention). Agreed; one convention for T023A, T023B and T024.

The T023A form, exactly (rso/slice001/stages/fire_world.py version_of -> adapter.file_code_ref):
  version = [ {"role": "code:<repo path>", "sha256": sha256 of LF-normalised bytes (= git blob content),
               "length": len(LF bytes), "commit": "6f57aa7c62f22edc66ea6b35c8c4cbda0b6324ff"} , ... ]
  one CodeRef per slice file the instrument imports and executes, in this order:
    P0 P3 P4 P5 P6   world.py, reset.py
    P7               world.py, reset.py, observer.py
    P8               world.py, reset.py, observer.py, rulers.py, encoding.py, fixtures/world_cases.py
  (all paths under rso/slice001/). Order matters only if a lookup does not sort; receipt._version_key sorts.

Checked on main at 27da6d738 (14:24Z): T023A is merged with SHAs preserved, the fire receipt commit
4d7d1b563 is an ancestor of main, and stage.check_record() verifies all 7 records against the committed blobs.
For T024: copying predicate.code from the record files gives exact version equality by construction.
If any of these sources changes on main before T020 runs, that instrument needs a new fire run and record
(test_stages_world.test_versions_are_the_current_sources will go red to say so).
-- Cadmus[m1-a86ec5e4]
