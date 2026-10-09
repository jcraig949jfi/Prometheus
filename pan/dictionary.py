"""PAN-22: generate roles/Pan/docs/DATA_DICTIONARY.md from the live catalog
(table comments, columns, sizes, row counts) and the Iceberg catalog."""
import datetime as dt

from . import REPO


def run(out=print):
    from . import db, iceberg
    lines = ["# Pan data dictionary (generated)", "",
             "Generated {} by `python -m pan dictionary` from the live schema pan on the".format(
                 dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")),
             "canonical cluster and the Iceberg catalog in schema pan_iceberg. Do not edit by",
             "hand: change the table comments (pan/migrations/006_comments.sql) and regenerate.", ""]
    with db.cursor() as cur:
        cur.execute("""select c.relname, obj_description(c.oid, 'pg_class'), c.reltuples::bigint,
                              pg_size_pretty(pg_total_relation_size(c.oid))
                       from pg_class c join pg_namespace n on n.oid=c.relnamespace
                       where n.nspname='pan' and c.relkind='r' order by c.relname""")
        tables = cur.fetchall()
        lines += ["## Postgres tables (schema pan)", ""]
        for name, comment, est, size in tables:
            cur.execute("select count(*) from pan.{}".format(name)) if est < 200000 else None
            n = cur.fetchone()[0] if est < 200000 else "~{:,} (estimate)".format(est)
            lines += ["### pan.{}".format(name), "", "{} rows, {}.".format(
                "{:,}".format(n) if isinstance(n, int) else n, size), "", comment or "(no comment)", "",
                      "    column                type"]
            cur.execute("""select a.attname, format_type(a.atttypid, a.atttypmod) from pg_attribute a
                           where a.attrelid = 'pan.{}'::regclass and a.attnum > 0 and not a.attisdropped
                           order by a.attnum""".format(name))
            for col, typ in cur.fetchall():
                lines.append("    {:<21} {}".format(col, typ))
            lines.append("")
    lines += ["## Iceberg tables (catalog pan_iceberg; data under the lake on M2)", ""]
    for t in iceberg.tables():
        lines.append("- {}: {:,} records, {} snapshots, location {}".format(
            t["table"], t["records"], t["snapshots"], t["location"]))
    lines.append("")
    p = REPO / "roles" / "Pan" / "docs" / "DATA_DICTIONARY.md"
    p.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    out("wrote {} ({} tables)".format(p, len(tables)))
