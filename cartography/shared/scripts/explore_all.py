"""All 6 explorations. Fixed user/schema/autocommit issues."""
import sys, io, time, json
import numpy as np
from scipy import stats
import psycopg2
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def safe(fn, *args):
    try:
        fn(*args)
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback; traceback.print_exc()


def connect(dbname, user='postgres', password='prometheus'):
    conn = psycopg2.connect(host='192.168.1.176', port=5432, dbname=dbname,
                            user=user, password=password)
    conn.autocommit = True
    return conn


def explore_1_gue(conn_fire):
    print("\n" + "=" * 70)
    print("EXPLORATION 1: GUE DEVIATION — PROPER UNFOLDING")
    print("=" * 70)

    cur = conn_fire.cursor()
    t0 = time.time()
    # Pull EC zeros. Conductor from source_key (e.g. "11.a1" -> 11)
    cur.execute("""
    SELECT z.object_id, z.zeros_vector, z.root_number, z.analytic_rank, r.source_key
    FROM zeros.object_zeros z
    JOIN xref.object_registry r ON z.object_id = r.object_id
    WHERE r.object_type = 'elliptic_curve'
      AND array_length(z.zeros_vector, 1) >= 10
    """)
    rows = cur.fetchall()
    print(f"Got {len(rows)} EC with >= 10 zeros [{time.time()-t0:.1f}s]")

    def parse_cond(label):
        try:
            return float(label.split('.')[0])
        except:
            return None

    data = []
    for obj_id, zeros, rn, rank, label in rows:
        cond = parse_cond(label) if label else None
        if cond is None or zeros is None:
            continue
        data.append({'zeros': np.array(zeros, dtype=np.float64),
                     'conductor': cond, 'rank': rank or 0, 'rn': rn})
    print(f"Parsed {len(data)} with conductor")

    def unfold(zeros, N):
        if N <= 0:
            return None
        out = []
        for g in zeros:
            if g <= 0:
                continue
            arg = N * g * g / (4 * np.pi * np.pi)
            if arg > 0:
                v = (g / (2 * np.pi)) * (np.log(arg) - 2)
                if v > 0:
                    out.append(v)
        return np.array(out) if out else None

    raw_sp, unf_sp = [], []
    for d in data:
        if d['conductor'] < 10:
            continue
        z = d['zeros']
        if len(z) < 3:
            continue
        g = np.diff(np.sort(z))
        mg = g.mean()
        if mg > 1e-10:
            raw_sp.extend((g / mg).tolist())
        u = unfold(z, d['conductor'])
        if u is not None and len(u) > 1:
            unf_sp.extend(np.diff(np.sort(u)).tolist())

    raw = np.array(raw_sp)
    unf = np.array(unf_sp)
    GUE_VAR = 0.178

    if len(raw) == 0:
        print("No data.")
        return

    print(f"\nRaw spacings: n={len(raw)}, mean={raw.mean():.4f}, var={raw.var():.4f}")
    if len(unf) > 0:
        unf_norm = unf / unf.mean()
        print(f"Unfolded (normalized): n={len(unf_norm)}, mean={unf_norm.mean():.4f}, var={unf_norm.var():.4f}")
        print(f"GUE Wigner target variance: {GUE_VAR}")

        raw_z = (raw.var() - GUE_VAR) / (raw.std() / np.sqrt(len(raw)) + 1e-10)
        unf_z = (unf_norm.var() - GUE_VAR) / (unf_norm.std() / np.sqrt(len(unf_norm)) + 1e-10)
        print(f"\nRaw variance z-score vs GUE: {raw_z:.2f}")
        print(f"Unfolded variance z-score vs GUE: {unf_z:.2f}")

        print("\nVERDICT:")
        if abs(unf_z) < 3:
            print(f"  REDEMPTION: Unfolded variance matches GUE.")
            print(f"  Yesterday's z=-19.26 was an UNFOLDING ARTIFACT.")
        elif unf_z < -3:
            print(f"  SURVIVES: Still below GUE after unfolding ({unf_z:.1f}σ).")
            print(f"  This is REAL fine structure worth investigating.")
        else:
            print(f"  UNCLEAR: unfolded z={unf_z:.2f}")
    cur.close()


def explore_2_extremes(conn_lmfdb_p, conn_sci):
    print("\n" + "=" * 70)
    print("EXPLORATION 2: EXTREMES TOUR")
    print("=" * 70)

    cur = conn_lmfdb_p.cursor()

    print("\n--- EC: highest L^(r)(1)/r! (rank <= 4) ---")
    t0 = time.time()
    cur.execute("""
    SELECT ec_label, rank, conductor, leading_term
    FROM bsd_joined
    WHERE leading_term IS NOT NULL AND rank <= 4
    ORDER BY leading_term DESC NULLS LAST LIMIT 5
    """)
    print(f"[{time.time()-t0:.2f}s]")
    for r in cur.fetchall():
        print(f"  {r[0]}: rank={r[1]}, cond={r[2]}, L^(r)/r! = {r[3]:.4e}")

    print("\n--- EC: smallest L(1) for rank 0 (near-zero L-values) ---")
    cur.execute("""
    SELECT ec_label, rank, conductor, leading_term FROM bsd_joined
    WHERE leading_term IS NOT NULL AND rank = 0
    ORDER BY leading_term ASC NULLS LAST LIMIT 5
    """)
    for r in cur.fetchall():
        print(f"  {r[0]}: cond={r[2]}, L(1) = {r[3]:.4e}")

    print("\n--- EC: largest regulator (rank >= 2) ---")
    cur.execute("""
    SELECT ec_label, rank, conductor, regulator, leading_term FROM bsd_joined
    WHERE regulator IS NOT NULL AND rank >= 2
    ORDER BY regulator DESC LIMIT 5
    """)
    for r in cur.fetchall():
        lt_s = f"{r[4]:.4e}" if r[4] else "?"
        print(f"  {r[0]}: rank={r[1]}, cond={r[2]}, reg={r[3]:.4f}, lt={lt_s}")

    print("\n--- EC: smallest non-zero L(1) regardless of rank (near-vanishing) ---")
    cur.execute("""
    SELECT ec_label, rank, conductor, leading_term FROM bsd_joined
    WHERE leading_term > 0 AND leading_term < 0.01
    ORDER BY leading_term ASC LIMIT 5
    """)
    for r in cur.fetchall():
        print(f"  {r[0]}: rank={r[1]}, cond={r[2]}, lt={r[3]:.4e}")
    cur.close()

    cur2 = conn_sci.cursor()
    print("\n--- Knots: largest determinants ---")
    t0 = time.time()
    cur2.execute("""
    SELECT name, crossing_number, determinant,
           array_length(alexander_coeffs,1), array_length(jones_coeffs,1)
    FROM topology.knots WHERE determinant > 0
    ORDER BY determinant DESC LIMIT 5
    """)
    print(f"[{time.time()-t0:.2f}s]")
    for r in cur2.fetchall():
        print(f"  {r[0]}: crossing={r[1]}, det={r[2]}, |alex|={r[3]}, |jones|={r[4]}")

    print("\n--- Groups: non-abelian with smallest n_conjugacy/√|G| ---")
    cur2.execute("""
    SELECT label, order_val, n_conjugacy,
           n_conjugacy::float / sqrt(order_val::float) AS ratio, is_solvable
    FROM algebra.groups
    WHERE order_val::float BETWEEN 100 AND 1e9 AND is_abelian = false
    ORDER BY n_conjugacy::float / sqrt(order_val::float) ASC LIMIT 5
    """)
    for r in cur2.fetchall():
        print(f"  {r[0]}: |G|={r[1]}, n_cc={r[2]}, ratio={r[3]:.5f}, solvable={r[4]}")

    print("\n--- Groups: largest n_conjugacy ---")
    cur2.execute("""
    SELECT label, order_val, n_conjugacy FROM algebra.groups
    WHERE n_conjugacy IS NOT NULL ORDER BY n_conjugacy DESC LIMIT 5
    """)
    for r in cur2.fetchall():
        print(f"  {r[0]}: |G|={r[1]}, n_cc={r[2]}")

    print("\n--- Materials: band gap outlier within space group ---")
    t0 = time.time()
    cur2.execute("""
    WITH sg_stats AS (
      SELECT spacegroup_number, AVG(band_gap) m, STDDEV(band_gap) s, COUNT(*) n
      FROM physics.materials WHERE band_gap IS NOT NULL
      GROUP BY spacegroup_number HAVING COUNT(*) >= 20
    )
    SELECT m.material_id, m.spacegroup_number, m.band_gap, s.m, s.s, s.n,
           (m.band_gap - s.m) / NULLIF(s.s, 0)
    FROM physics.materials m JOIN sg_stats s USING (spacegroup_number)
    WHERE m.band_gap IS NOT NULL AND s.s > 0
    ORDER BY ABS((m.band_gap - s.m) / NULLIF(s.s, 0)) DESC LIMIT 5
    """)
    print(f"[{time.time()-t0:.2f}s]")
    for r in cur2.fetchall():
        print(f"  {r[0]}: sg={r[1]}, gap={r[2]:.3f}, sg_avg={r[3]:.3f}±{r[4]:.3f} (n={r[5]}), z={r[6]:.2f}")

    print("\n--- QM9: tightest HOMO-LUMO gap (most metallic) ---")
    t0 = time.time()
    cur2.execute("""
    SELECT smiles, homo, lumo, homo_lumo_gap, n_atoms FROM chemistry.qm9
    WHERE homo_lumo_gap IS NOT NULL AND n_atoms > 3
    ORDER BY homo_lumo_gap ASC LIMIT 5
    """)
    print(f"[{time.time()-t0:.2f}s]")
    for r in cur2.fetchall():
        print(f"  {r[0]}: HOMO={r[1]:.3f}, LUMO={r[2]:.3f}, gap={r[3]:.3f}, atoms={r[4]}")

    print("\n--- QM9: largest HOMO-LUMO gap (most insulator) ---")
    cur2.execute("""
    SELECT smiles, homo, lumo, homo_lumo_gap, n_atoms FROM chemistry.qm9
    WHERE homo_lumo_gap IS NOT NULL AND n_atoms > 3
    ORDER BY homo_lumo_gap DESC LIMIT 5
    """)
    for r in cur2.fetchall():
        print(f"  {r[0]}: gap={r[3]:.3f}, atoms={r[4]}")

    cur2.close()


def explore_3_cross_domain(conn_lmfdb_p, conn_sci):
    print("\n" + "=" * 70)
    print("EXPLORATION 3: CROSS-DOMAIN JOINS")
    print("=" * 70)

    cur = conn_lmfdb_p.cursor()
    print("\n--- 3a: CM vs non-CM EC zero spacings ---")
    t0 = time.time()
    cur.execute("""
    SELECT cm, rank, positive_zeros, conductor FROM bsd_joined
    WHERE positive_zeros IS NOT NULL AND positive_zeros != ''
      AND conductor BETWEEN 100000 AND 400000
    LIMIT 8000
    """)
    rows = cur.fetchall()
    print(f"[{time.time()-t0:.1f}s] {len(rows)} curves")

    cm_sp, ncm_sp = [], []
    for cm, rank, zs, cond in rows:
        try:
            z = np.array(json.loads(str(zs)))
            if len(z) < 5:
                continue
            g = np.diff(np.sort(z))
            mg = g.mean()
            if mg > 1e-10:
                norm = (g / mg).tolist()
                (cm_sp if cm and cm != 0 else ncm_sp).extend(norm)
        except:
            pass

    if cm_sp and ncm_sp:
        cm_a, ncm_a = np.array(cm_sp), np.array(ncm_sp)
        ks, p = stats.ks_2samp(cm_a, ncm_a)
        print(f"  CM: n={len(cm_a)}, var={cm_a.var():.4f}")
        print(f"  non-CM: n={len(ncm_a)}, var={ncm_a.var():.4f}")
        print(f"  KS: {ks:.4f}, p={p:.4e}")
        print(f"  VERDICT: {'DIFFER at p<0.01' if p < 0.01 else 'indistinguishable'}")
    cur.close()

    cur2 = conn_sci.cursor()
    print("\n--- 3b: Knot signature vs determinant ---")
    t0 = time.time()
    cur2.execute("""
    SELECT name, crossing_number, signature, determinant
    FROM topology.knots WHERE signature IS NOT NULL AND determinant > 0
    """)
    knots = cur2.fetchall()
    print(f"[{time.time()-t0:.2f}s] {len(knots)} knots")

    sigs = np.array([abs(k[2]) for k in knots])
    dets = np.array([k[3] for k in knots])
    rho, p = stats.spearmanr(sigs, dets)
    print(f"  Spearman(|σ|, det): rho={rho:.4f}, p={p:.4e}")

    violations = [(k[0], k[1], abs(k[2]), k[3]) for k in knots if k[3] < abs(k[2]) + 1]
    print(f"  det < |σ|+1 (non-alternating): {len(violations)}/{len(knots)} ({len(violations)/len(knots)*100:.2f}%)")
    for r in violations[:5]:
        print(f"    {r[0]}: crossings={r[1]}, |σ|={r[2]}, det={r[3]}")

    print("\n--- 3c: Crystal symmetry classes ---")
    t0 = time.time()
    cur2.execute("""
    SELECT
      CASE
        WHEN spacegroup_number BETWEEN 195 AND 230 THEN 'cubic (hi-sym)'
        WHEN spacegroup_number BETWEEN 75 AND 142 THEN 'tetragonal'
        WHEN spacegroup_number BETWEEN 168 AND 194 THEN 'hex/trigonal'
        WHEN spacegroup_number BETWEEN 16 AND 74 THEN 'orthorhombic'
        WHEN spacegroup_number BETWEEN 3 AND 15 THEN 'monoclinic'
        WHEN spacegroup_number BETWEEN 1 AND 2 THEN 'triclinic (lo-sym)'
      END AS sym,
      AVG(band_gap), STDDEV(band_gap), AVG(density), COUNT(*)
    FROM physics.materials WHERE band_gap IS NOT NULL
    GROUP BY sym ORDER BY MIN(spacegroup_number)
    """)
    print(f"[{time.time()-t0:.2f}s]")
    for sym, mg, sg, dens, n in cur2.fetchall():
        mg_s = f"{mg:.3f}" if mg else "?"
        sg_s = f"{sg:.3f}" if sg else "?"
        dens_s = f"{dens:.2f}" if dens else "?"
        print(f"  {sym}: gap={mg_s}±{sg_s}, density={dens_s}, n={n}")
    cur2.close()


def explore_4_lehmer(conn_lmfdb_p):
    print("\n" + "=" * 70)
    print("EXPLORATION 4: LEHMER SCAN — local nf_fields")
    print("=" * 70)

    LEHMER = 1.17628081825991
    def mahler(cs):
        if len(cs) < 2:
            return None
        poly = [float(c) for c in reversed(cs)]
        if abs(poly[0]) < 1e-15:
            return None
        try:
            roots = np.roots(poly)
            return abs(poly[0]) * float(np.prod([max(1.0, abs(r)) for r in roots]))
        except:
            return None

    cur = conn_lmfdb_p.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM nf_fields")
        cnt = cur.fetchone()[0]
        print(f"Local nf_fields: {cnt:,} rows")
    except Exception as e:
        print(f"No local nf_fields: {e}")
        cur.close()
        return

    for degree in range(2, 25):
        t0 = time.time()
        # Try with ::integer if degree is stored as integer
        try:
            cur.execute("""
            SELECT label, coeffs FROM nf_fields
            WHERE degree::int = %s AND coeffs IS NOT NULL
            ORDER BY disc_abs::numeric ASC LIMIT 3000
            """, (degree,))
            rows = cur.fetchall()
        except Exception as e:
            print(f"  deg {degree}: {e}")
            continue

        measures = []
        for label, cs_raw in rows:
            try:
                if isinstance(cs_raw, list):
                    cs = [float(c) for c in cs_raw]
                else:
                    cs = [float(c.strip()) for c in str(cs_raw).strip('{}[]').split(',')]
            except:
                continue
            mm = mahler(cs)
            if mm is not None and mm > 1.0001:
                measures.append((mm, label))

        if measures:
            measures.sort()
            m, lbl = measures[0]
            mk = " *** BELOW LEHMER ***" if m < LEHMER else (" << VERY CLOSE" if m < LEHMER * 1.01 else "")
            print(f"  deg {degree:>2}: {len(measures):>4} nontrivial, min M={m:.8f} [{lbl}]{mk}  [{time.time()-t0:.1f}s]")
    cur.close()


def explore_5_bsd(conn_lmfdb_p):
    print("\n" + "=" * 70)
    print("EXPLORATION 5: BSD PARITY ON bsd_joined")
    print("=" * 70)

    cur = conn_lmfdb_p.cursor()
    t0 = time.time()
    cur.execute("""
    SELECT COUNT(*),
           SUM(CASE WHEN rank = analytic_rank THEN 1 ELSE 0 END),
           SUM(CASE WHEN root_number::numeric = CASE WHEN rank % 2 = 0 THEN 1 ELSE -1 END THEN 1 ELSE 0 END)
    FROM bsd_joined
    WHERE rank IS NOT NULL AND analytic_rank IS NOT NULL AND root_number IS NOT NULL
    """)
    total, rok, pok = cur.fetchone()
    print(f"[{time.time()-t0:.2f}s] Total: {total:,}")
    print(f"  rank = analytic_rank: {rok:,}/{total:,} ({rok/total*100:.6f}%)")
    print(f"  parity: {pok:,}/{total:,} ({pok/total*100:.6f}%)")

    cur.execute("""
    SELECT rank, COUNT(*),
           SUM(CASE WHEN rank = analytic_rank THEN 1 ELSE 0 END),
           SUM(CASE WHEN root_number::numeric = CASE WHEN rank % 2 = 0 THEN 1 ELSE -1 END THEN 1 ELSE 0 END)
    FROM bsd_joined WHERE root_number IS NOT NULL
    GROUP BY rank ORDER BY rank
    """)
    print("\nPer-rank:")
    for r, n, rk, pk in cur.fetchall():
        print(f"  rank {r}: n={n:>10,}, rank=ov: {rk/n*100:>7.4f}%, parity: {pk/n*100:>7.4f}%")

    cur.execute("""
    SELECT ec_label, conductor, rank, analytic_rank, root_number, leading_term
    FROM bsd_joined WHERE rank >= 4 ORDER BY rank, conductor
    """)
    rows = cur.fetchall()
    print(f"\nAll rank 4+ in bsd_joined ({len(rows)}):")
    for r in rows:
        lt = f"{r[5]:.4e}" if r[5] else "?"
        print(f"  {r[0]}: cond={r[1]}, rank={r[2]}, ov={r[3]}, rn={r[4]}, lt={lt}")
    cur.close()


def explore_6_delinquent(conn_lmfdb_p):
    print("\n" + "=" * 70)
    print("EXPLORATION 6: DELINQUENT EC — no L-function data")
    print("=" * 70)

    cur = conn_lmfdb_p.cursor()
    t0 = time.time()
    cur.execute("SELECT COUNT(DISTINCT lmfdb_iso) FROM ec_curvedata")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT ec_iso) FROM bsd_joined")
    joined = cur.fetchone()[0]
    print(f"[{time.time()-t0:.1f}s] Total iso: {total:,}, joined: {joined:,}, delinquent: {total-joined:,} ({(total-joined)/total*100:.1f}%)")

    print("\nDelinquent conductor bands:")
    t0 = time.time()
    cur.execute("""
    WITH delinquent AS (
      SELECT DISTINCT e.lmfdb_iso, e.conductor::numeric c
      FROM ec_curvedata e
      WHERE NOT EXISTS (SELECT 1 FROM bsd_joined b WHERE b.ec_iso = e.lmfdb_iso)
    )
    SELECT CASE
      WHEN c < 100000 THEN '<100K'
      WHEN c < 400000 THEN '100K-400K'
      WHEN c < 1000000 THEN '400K-1M'
      WHEN c < 5000000 THEN '1M-5M'
      ELSE '>5M' END AS band,
      COUNT(*), MIN(c), MAX(c)
    FROM delinquent GROUP BY band ORDER BY MIN(c)
    """)
    print(f"[{time.time()-t0:.1f}s]")
    for band, n, mn, mx in cur.fetchall():
        print(f"  {band}: {n:>10,} classes ({mn:.0f} to {mx:.0f})")

    print("\nDelinquent rank distribution:")
    cur.execute("""
    SELECT e.rank::int, COUNT(*) FROM ec_curvedata e
    WHERE NOT EXISTS (SELECT 1 FROM bsd_joined b WHERE b.ec_iso = e.lmfdb_iso)
      AND e.rank IS NOT NULL
    GROUP BY e.rank::int ORDER BY e.rank::int
    """)
    for r, n in cur.fetchall():
        print(f"  rank {r}: {n:>10,}")

    print("\nAll rank-5 delinquents (the 19):")
    cur.execute("""
    SELECT e.lmfdb_label, e.conductor::numeric FROM ec_curvedata e
    WHERE NOT EXISTS (SELECT 1 FROM bsd_joined b WHERE b.ec_iso = e.lmfdb_iso)
      AND e.rank::int = 5
    ORDER BY e.conductor::numeric
    """)
    rows = cur.fetchall()
    print(f"  Found {len(rows)}:")
    for l, c in rows:
        print(f"    {l}: cond={c:.0f}")
    cur.close()


# MAIN
print("=" * 70)
print("HARMONIA EXPLORATION BATCH — all 6")
print("=" * 70)

conn_lmfdb_p = connect('lmfdb')   # postgres user for bsd_joined
conn_fire = connect('prometheus_fire')
conn_sci = connect('prometheus_sci')

safe(explore_5_bsd, conn_lmfdb_p)
safe(explore_6_delinquent, conn_lmfdb_p)
safe(explore_2_extremes, conn_lmfdb_p, conn_sci)
safe(explore_3_cross_domain, conn_lmfdb_p, conn_sci)
safe(explore_1_gue, conn_fire)
safe(explore_4_lehmer, conn_lmfdb_p)

conn_lmfdb_p.close(); conn_fire.close(); conn_sci.close()
print("\n" + "=" * 70)
print("ALL 6 EXPLORATIONS COMPLETE")
print("=" * 70)
