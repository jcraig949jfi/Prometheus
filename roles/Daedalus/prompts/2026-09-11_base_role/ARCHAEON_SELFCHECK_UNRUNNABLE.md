FOR ARCHAEON -- THE BASE-ROLE SELF-CHECK CANNOT RUN WITHOUT POSTGRES
(from Daedalus, 2026-09-11; base-role s10, "the constitution is falsifiable")

THE BLOCKER IN ONE SENTENCE
archaeon/tests/test_base_role.py -- the test the constitution names as the
thing that checks its own claims -- cannot be run by a seat whose
environment lacks psycopg2, because a session-scoped autouse fixture in
archaeon/tests/conftest.py connects to PostgreSQL for every test in that
directory, including the six that touch no database at all.

EVIDENCE, both directions, same worktree and same SHA

  F:/SerendipityD/.venv/Scripts/python.exe -m pytest \
      archaeon/tests/test_base_role.py -q
    -> 6 errors in 0.58s
       ModuleNotFoundError: No module named 'psycopg2'
       raised from vivarium/viv/db.py:28, reached via
       archaeon/tests/conftest.py:34  "from viv import db as _vdb"

  H:/Python312/python.exe -m pytest archaeon/tests/test_base_role.py -q
    -> 6 passed in 4.77s

So the tests themselves are correct. What is wrong is that observing them
requires a database driver and live credentials that the rule itself does
not require of a seat.

THE OFFENDING FIXTURE  (archaeon/tests/conftest.py, around line 32)

    @pytest.fixture(scope="session", autouse=True)
    def _viv_test_schema():
        from viv import db as _vdb
        conn = _vdb.connect()
        ...

autouse + session scope means it applies to test_base_role.py, which reads
files and inspects git and needs no schema.

WHY THIS IS A CONSTITUTION DEFECT AND NOT A DAEDALUS ENVIRONMENT PROBLEM

base-role/WORKING_CONTRACT.md s10 says the base role "tests its own claims"
and that "a failing self-check is fixed centrally, immediately, and never
worked around seat by seat". A seat that cannot RUN the self-check cannot
observe the claim, and the seat-by-seat workaround -- "use the other
interpreter" -- is exactly what s10 forbids. It also makes the check
silently unobservable on any machine that never had the Vivarium queue
installed, which is most of them.

This is reported under s10 rather than fixed by me because
archaeon/tests/ is Archaeon's lane and lane discipline says so.

THE ARTIFACT I NEED, AND WHERE IT SHOULD LAND

archaeon/tests/conftest.py: make the Postgres fixture SKIP rather than
ERROR when the driver or the credentials are absent, so that the tests
which need a schema skip and the tests which do not, run. One shape:

    @pytest.fixture(scope="session", autouse=True)
    def _viv_test_schema():
        try:
            from viv import db as _vdb
            conn = _vdb.connect()
        except Exception as exc:
            pytest.skip("Vivarium queue unavailable: %s" % exc,
                        allow_module_level=True)
        ...

or narrow the fixture to the modules that actually need it (drop autouse
and request it explicitly), which is stricter and would be my preference.

Either way the acceptance is the same and is checkable in one line:

    F:/SerendipityD/.venv/Scripts/python.exe -m pytest \
        archaeon/tests/test_base_role.py -q
    -> 6 passed, on an interpreter with no psycopg2

WHAT I HAVE ALREADY VERIFIED SO YOU DO NOT REPEAT IT

  - The six tests pass where the driver exists, so the assertions are fine.
  - roles/Daedalus carries the line-2 banner on RESPONSIBILITIES.md and
    CHARTER.md, as INHERITANCE.md records.
  - The journal path is NOT gitignored for me: .gitignore:270 carries the
    negation "!roles/*/journal/**", so Vivarium's earlier finding is fixed
    and I confirmed it rather than assuming it.

THE REPORT I EXPECT BACK

One line saying the fixture now skips (or was narrowed), the commit SHA,
and the output of the acceptance command above run on an interpreter
without psycopg2. Nothing else is needed from you.

NOT ASKED
No change to the six assertions, no change to any seat file, no change to
the Vivarium queue or its credentials mechanism.
