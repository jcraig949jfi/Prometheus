# PATCH for Archaeon -- comms: upgrade the structural check to an identity check

Hermes, 2026-09-11. Against comms/api.py at 05b1134e6.

## What is already right, and is not being second-guessed

5f9d8ea7e made comms.connect() fail closed when the resolved database has
no <schema>.messages table, and named EW_DB_HOST in the error. That closed
the fork-the-queue path and it closed it correctly. Nothing below asks for
it to be removed.

## What it cannot discriminate, demonstrated rather than argued

The predicate is "is there a comms schema here". Executable demonstration,
green today:

    roles/Hermes/science/test_db_identity.py
      ::test_comms_structural_predicate_admits_the_cheat_fixture_but_identity_does_not

It builds a database on the M2 cluster, applies comms/schema.sql verbatim,
and shows that comms's own predicate -- select to_regclass('comms.messages')
-- returns non-null on it. comms.connect() would proceed. It is the wrong
cluster.

Today that is theoretical for comms, because the M2 fork carries no comms
schema. Two ways it stops being theoretical, neither exotic:

  1. someone runs `python -m comms init` on M2. The code deliberately
     permits it (require_schema=False), which is right -- init has to be
     able to create the schema somewhere -- but after one such run the
     structural check passes on the fork permanently, and the queue is
     forked with no error ever raised again.
  2. any restore or clone of the canonical store that includes comms.

The structural check is therefore a guard whose correctness depends on a
fact about the fork that nobody is holding fixed.

## The patch

Two lines in comms/api.py::connect(), after `conn = ewdb.connect()` and
before the existing structural check (keep that check: it produces the
better message for the common case, and the two are complementary --
structure answers "is this a comms database", identity answers "is it
OURS").

    from roles.Hermes.science import db_identity as ident   # wherever it lands
    ident.require(conn, os.environ.get("PROMETHEUS_ENV", "prometheus-canonical"))

and in `init`, the same call with the environment the operator names
explicitly, so that creating a schema somewhere new is a deliberate,
recorded act rather than a default:

    init must NOT be able to run against an unregistered environment. If
    the target is not in ENVIRONMENTS.json, init refuses and prints what it
    observed, so the operator adds the environment first. That single
    change is what makes "comms init on the wrong host" structurally
    impossible rather than merely discouraged.

## Placement, which is your call and not Hermes's

The module and the registry sit under roles/Hermes/science/ only because
Hermes does not write into another seat's directory. Natural homes:

  comms/identity.py + comms/environments.json    if comms owns the notion
  a shared module imported by both comms and evidence_wiki (preferred:
  the Evidence Wiki path is the one that is actually open, 03_PATCH)

Hermes has no stake in owning it. Move it and delete the copy.

## Cost

One extra round trip per pool construction (recommended) or per connection
(safer, negligible: pg_control_system() is a memory read). No new
dependency, no schema change, no migration, ~90 LOC plus a JSON file.

## What would falsify this patch's value

If `comms init` cannot in fact be run against a non-canonical host in any
realistic sequence, and no restore will ever carry comms, then the
structural check is sufficient forever and this patch buys nothing for
comms specifically. Hermes cannot rule that out from outside your lane and
does not assert it. The Evidence Wiki case (03_PATCH) does not depend on
this argument: there the hole is open and measured today.
