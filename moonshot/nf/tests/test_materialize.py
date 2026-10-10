"""C-012-T005: materializing Moonshot evidence into Pan's lake (contract s6).

Pan's own functions (pan.iceberg.write / last_snapshot_properties / read) run against a THROWAWAY Iceberg catalog: a
throwaway Postgres schema for the catalog tables and a temporary warehouse directory, swapped in for pan.iceberg's
module catalog. Pan's lake is never touched. Needs EW_DB_HOST and pyarrow + pyiceberg (Moonshot's lake venv,
C:/Prometheus-data/moonshot/venv); otherwise every test is skipped with that reason."""
import importlib.util
import os
import secrets
import shutil
import tempfile
import unittest
import urllib.parse
from pathlib import Path

from moonshot.epoch import canonical as C
from moonshot.epoch import model
from moonshot.epoch.tests.harness import planted_runner

PG = bool(os.environ.get("EW_DB_HOST"))
LAKE = all(importlib.util.find_spec(m) is not None for m in ("pyarrow", "pyiceberg", "sqlalchemy"))
APPROVED = "c0de" * 10
TABLES = ("epochs", "trace_lines", "attempts", "validations", "contests_opened", "resolutions")


def genesis(cid, epochs=3):
    return model.make_genesis(cid, epochs=epochs, params={"work_iterations": 60, "trace_every": 20,
                                                          "checkpoint_bytes": 64},
                              approved_code_sha=APPROVED, initial_checkpoint=b"lake " + cid.encode())


@unittest.skipUnless(PG and LAKE, "needs EW_DB_HOST and pyarrow/pyiceberg/sqlalchemy (Moonshot's lake venv)")
class LakeCase(unittest.TestCase):
    def setUp(self):
        from moonshot.nf import materialize as Mz
        from moonshot.nf import pg
        from pan import iceberg
        from pyiceberg.catalog.sql import SqlCatalog
        from evidence_wiki.ew import db as ewdb
        self.Mz, self.pg, self.ice = Mz, pg, iceberg
        tag = secrets.token_hex(4)
        self.schema, self.catschema = "moonshot_t_" + tag, "moonshot_lake_t_" + tag
        self.admin = pg.connect()
        pg.init_schema(self.admin, self.schema)
        cur = self.admin.cursor()
        cur.execute("CREATE SCHEMA {}".format(self.catschema))
        self.admin.commit()
        self.wh = tempfile.mkdtemp(prefix="lake-t-")
        cfg = ewdb.load_config()
        q = urllib.parse.quote
        uri = "postgresql+psycopg2://{}:{}@{}/{}?options={}".format(
            q(cfg["db_user"], safe=""), q(cfg["db_password"] or "", safe=""), cfg["db_host"], cfg["db_name"],
            q("-csearch_path=" + self.catschema, safe=""))
        self._saved_cat = iceberg._CAT
        iceberg._CAT = SqlCatalog("t", uri=uri, warehouse=Path(self.wh).resolve().as_uri(),
                                  **{"py-io-impl": "pyiceberg.io.fsspec.FsspecFileIO"})
        self.addCleanup(self._drop)
        self.coord = pg.Moonshot(pg.connect(), self.schema, "coordinator", "test")
        self.pub = pg.Moonshot(pg.connect(), self.schema, "publisher", "test")
        self.val = pg.Moonshot(pg.connect(), self.schema, "validator", "test")
        self.res = pg.Moonshot(pg.connect(), self.schema, "resolver", "test")
        self.reader = pg.Moonshot(pg.connect(), self.schema, "reader", "test")
        self._n = 0

    def _drop(self):
        for h in (self.coord, self.pub, self.val, self.res, self.reader):
            h.close()
        self.ice._CAT = self._saved_cat
        self.pg.drop_schema(self.admin, self.schema)
        cur = self.admin.cursor()
        cur.execute("DROP SCHEMA IF EXISTS {} CASCADE".format(self.catschema))
        self.admin.commit()
        self.admin.close()
        shutil.rmtree(self.wh, ignore_errors=True)

    def att(self):
        self._n += 1
        return "att-lake{:05d}".format(self._n)

    def chain(self, cid, upto, epochs=3):
        """Publish epochs 1..upto of a fresh chain; returns (genesis, results)."""
        g = genesis(cid, epochs)
        self.coord.create_chain(g, namespace="test", approved_code_sha=APPROVED)
        inp, parent, out = g.initial_checkpoint, None, []
        for k in range(1, upto + 1):
            r = model.execute(g.obj, k, inp)
            self.assertEqual(self.pub.publish(self.att(), "tsk-lake", cid, k, parent, k - 1, r.files())["outcome"],
                             "PUBLISHED")
            out.append(r)
            inp, parent = r.checkpoint, r.epoch_digest
        return g, out

    def populate(self):
        """A source with every kind of row: publications, an INVALID attempt, a duplicate, validations, a contest
        opened by a disagreement and resolved."""
        g, rs = self.chain("L1", 3)
        self.val.record_validation("L1", 1, rs[0].epoch_digest, "VALIDATED", ["REPLAY"], rs[0].epoch_digest, "t")
        self.pub.publish(self.att(), "tsk-lake", "L1", 1, None, 0, rs[0].files())               # DUPLICATE
        bad = dict(rs[0].files(), trace=rs[0].trace + b"x")
        self.pub.publish(self.att(), "tsk-lake", "L1", 1, None, 0, bad)                         # INVALID
        g2, rs2 = self.chain("L2", 1, epochs=2)
        wrong = model.execute(g2.obj, 1, g2.initial_checkpoint, planted_runner())
        self.pub.publish(self.att(), "tsk-lake", "L2", 1, None, 0, wrong.files())               # DISAGREEMENT
        cid = self.reader.open_contest("L2")["contest_id"]
        self.res.resolve_contest(cid, [rs2[0].epoch_digest] * 2)                                # UPHELD
        return {"L1": (g, rs), "L2": (g2, rs2)}

    def run_mz(self, **kw):
        kw.setdefault("settle_s", 0)
        return self.Mz.materialize(self.schema, namespace="mt", prefix="", **kw)

    def lake_rows(self, name):
        return self.ice.read(name, namespace="mt").to_pylist()


class TestMaterialize(LakeCase):
    def test_first_run_fills_every_table_and_the_oracle_holds(self):
        src = self.populate()
        rep = self.run_mz()
        self.assertEqual(sorted(rep["tables"]), sorted(TABLES))
        for t in TABLES:
            with self.subTest(table=t):
                r = rep["tables"][t]
                self.assertEqual((r["lake"], r["oracle"]), (r["postgres"], "OK"), r)
                self.assertGreater(r["appended"], 0)
        epochs = self.lake_rows("epochs")
        self.assertEqual(len(epochs), 4)                                         # L1 x3 + L2 x1
        g, rs = src["L1"]
        e1 = [e for e in epochs if (e["chain_id"], e["epoch_index"]) == ("L1", 1)][0]
        self.assertEqual((e1["epoch_digest"], e1["object_sha256"]), (rs[0].epoch_digest,
                                                                     C.sha256_hex(rs[0].manifest_bytes)))
        self.assertEqual(e1["record"], rs[0].manifest_bytes.decode("ascii"))
        n_lines = sum(r.trace.count(b"\n") for _, rr in src.values() for r in rr)
        self.assertEqual(len(self.lake_rows("trace_lines")), n_lines)
        outcomes = sorted(a["outcome"] for a in self.lake_rows("attempts"))
        self.assertEqual(outcomes, sorted(["PUBLISHED"] * 4 + ["DUPLICATE", "INVALID", "DISAGREEMENT"]))
        self.assertEqual([r["verdict"] for r in self.lake_rows("resolutions")], ["UPHELD"])

    def test_rows_carry_pans_provenance_columns(self):
        self.populate()
        self.run_mz(materializer="test-instance")
        for t, kind in (("epochs", "epoch"), ("trace_lines", "trace"), ("attempts", "attempt"),
                        ("validations", "validation"), ("contests_opened", "contest"), ("resolutions", "resolution")):
            with self.subTest(table=t):
                row = self.lake_rows(t)[0]
                for col in ("seat", "kind", "record", "object_sha256", "publication_id", "published_at",
                            "materialized_at", "materializer", "moonshot_schema"):
                    self.assertIn(col, row)
                self.assertEqual((row["seat"], row["kind"], row["materializer"], row["moonshot_schema"]),
                                 ("Themis", kind, "test-instance", self.schema))
        lines = self.lake_rows("trace_lines")
        self.assertEqual(min(r["line_no"] for r in lines), 1)

    def test_a_second_run_appends_nothing(self):
        self.populate()
        first = self.run_mz()
        second = self.run_mz()
        for t in TABLES:
            with self.subTest(table=t):
                self.assertEqual(second["tables"][t]["appended"], 0)
                self.assertEqual(second["tables"][t]["watermark"], first["tables"][t]["watermark"])
                self.assertEqual(second["tables"][t]["oracle"], "OK")

    def test_new_evidence_is_appended_after_the_watermark(self):
        self.populate()
        self.run_mz()
        g, rs = genesis("L3", 1), None
        self.coord.create_chain(g, namespace="test", approved_code_sha=APPROVED)
        r = model.execute(g.obj, 1, g.initial_checkpoint)
        self.pub.publish(self.att(), "tsk-lake", "L3", 1, None, 0, r.files())
        rep = self.run_mz()
        self.assertEqual((rep["tables"]["epochs"]["appended"], rep["tables"]["attempts"]["appended"],
                          rep["tables"]["trace_lines"]["appended"]), (1, 1, r.trace.count(b"\n")))
        self.assertTrue(all(rep["tables"][t]["oracle"] == "OK" for t in TABLES))

    def test_a_crash_between_commits_loses_and_duplicates_nothing(self):
        self.populate()
        with self.assertRaises(self.Mz.InjectedCrash):
            self.run_mz(_crash_before="trace_lines")                 # epochs committed, trace_lines not
        self.assertEqual(len(self.lake_rows("epochs")), 4)
        rep = self.run_mz()
        self.assertEqual(rep["tables"]["epochs"]["appended"], 0)    # resumed after its own watermark
        self.assertGreater(rep["tables"]["trace_lines"]["appended"], 0)
        self.assertTrue(all(rep["tables"][t]["oracle"] == "OK" for t in TABLES), rep)

    def test_the_settle_window_defers_fresh_rows(self):
        self.populate()
        rep = self.run_mz(settle_s=3600)
        self.assertTrue(all(rep["tables"][t]["appended"] == 0 and rep["tables"][t]["oracle"] == "OK" for t in TABLES))
        rep = self.run_mz(settle_s=0)
        self.assertTrue(all(rep["tables"][t]["appended"] > 0 for t in TABLES))

    def test_the_oracle_catches_a_missed_row_and_repair_restores_exactly_it(self):
        self.populate()
        rep = self.run_mz(_drop_key={"epochs": 2})        # instrument fault: the row with key 2 never reaches the lake
        self.assertEqual(rep["tables"]["epochs"]["oracle"], "MISSED")
        self.assertEqual(rep["tables"]["epochs"]["missing_keys"], [2])
        fixed = self.run_mz(repair=True)
        self.assertEqual((fixed["tables"]["epochs"]["appended"], fixed["tables"]["epochs"]["oracle"]), (1, "OK"))
        self.assertEqual(sorted(e["publication_id"] for e in self.lake_rows("epochs")), [1, 2, 3, 4])

    def test_the_oracle_reports_rows_a_rogue_writer_duplicated(self):
        # One writer per table is Pan's rule; a second writer re-appending rows must not pass silently (mutation MM05
        # survived without this). Detection only: an append-only lake is repaired by rewriting, an owner's decision.
        self.populate()
        self.run_mz()
        rows = self.ice.read("epochs", namespace="mt")
        self.ice.write("epochs", rows.slice(0, 1), namespace="mt")
        rep = self.run_mz()
        self.assertEqual(rep["tables"]["epochs"]["oracle"], "DUPLICATED")
        self.assertEqual(rep["tables"]["attempts"]["oracle"], "OK")

    def test_one_materializer_at_a_time(self):
        self.populate()
        cur = self.admin.cursor()
        cur.execute("SELECT pg_advisory_lock(%s, %s)", self.Mz.lock_key(self.schema, "mt"))
        try:
            with self.assertRaises(self.Mz.Busy):
                self.run_mz()
        finally:
            cur.execute("SELECT pg_advisory_unlock(%s, %s)", self.Mz.lock_key(self.schema, "mt"))
            self.admin.commit()

    def test_each_run_is_logged_in_moonshots_own_records(self):
        self.populate()
        rep = self.run_mz()
        logged = self.reader.materializations()
        self.assertEqual(len(logged), 1)
        self.assertEqual(logged[0]["tables"]["epochs"]["lake"], rep["tables"]["epochs"]["lake"])


class TestCatalogueView(LakeCase):
    def test_catalog_v_lists_live_published_epochs_for_pans_collector(self):
        self.populate()
        rows = self.reader.raw("SELECT object_sha256, kind, title, summary, published_at, ref FROM {s}.catalog_v "
                               "ORDER BY ref")
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(r[1] == "moonshot.epoch" and len(r[0]) == 64 for r in rows))
        self.assertIn("{}:L1/1".format(self.schema), [r[5] for r in rows])

    def test_catalog_v_drops_an_overturned_epoch(self):
        g = genesis("L9", 2)
        self.coord.create_chain(g, namespace="test", approved_code_sha=APPROVED)
        bad = model.execute(g.obj, 1, g.initial_checkpoint, planted_runner())
        good = model.execute(g.obj, 1, g.initial_checkpoint)
        self.pub.publish(self.att(), "tsk-lake", "L9", 1, None, 0, bad.files())                 # faulty, published
        self.pub.publish(self.att(), "tsk-lake", "L9", 1, None, 0, good.files())                # DISAGREEMENT
        cid = self.reader.open_contest("L9")["contest_id"]
        self.assertEqual(self.res.resolve_contest(cid, [good.epoch_digest] * 2), "OVERTURNED")
        refs = [r[0] for r in self.reader.raw("SELECT ref FROM {s}.catalog_v")]
        self.assertNotIn("{}:L9/1".format(self.schema), refs)
        self.pub.publish(self.att(), "tsk-lake", "L9", 1, None, 2, good.files())                # honest, re-published
        rows = self.reader.raw("SELECT object_sha256 FROM {s}.catalog_v WHERE ref = %s", ("{}:L9/1".format(self.schema),))
        self.assertEqual([r[0] for r in rows], [C.sha256_hex(good.manifest_bytes)])


if __name__ == "__main__":
    unittest.main()
