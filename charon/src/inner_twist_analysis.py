"""
North Star Experiment 2: Inner Twist Analysis (from existing DB data)
=====================================================================
LMFDB API is behind reCAPTCHA, but we already have self_twist_type,
is_cm, is_rm, is_self_dual in our modular_forms table.

Compare Type B (EC-proximate) dim-2 wt-2 forms vs ALL dim-2 wt-2 forms.
If Type B is enriched for CM/RM/self-twist, the EC-proximity is
algebraically explained by inner twist structure.
"""

import duckdb
from collections import Counter
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"


def main():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    print("=" * 60)
    print("INNER TWIST ANALYSIS: Type B vs ALL dim-2 wt-2")
    print("=" * 60)

    # Count totals
    n_tb = con.execute("""
        SELECT COUNT(*) FROM disagreement_atlas da
        JOIN modular_forms mf ON da.object_id = mf.object_id
        WHERE da.disagreement_type = 'B' AND mf.dim = 2 AND mf.weight = 2
    """).fetchone()[0]

    n_all = con.execute("""
        SELECT COUNT(*) FROM modular_forms mf
        WHERE mf.dim = 2 AND mf.weight = 2
    """).fetchone()[0]

    print(f"Type B dim-2 wt-2: {n_tb}")
    print(f"ALL dim-2 wt-2:    {n_all}")
    print(f"Type B fraction:   {n_tb/n_all*100:.1f}%")
    print()

    # Compare each field
    fields = [
        ('is_cm', 'CM (Complex Multiplication)'),
        ('is_rm', 'RM (Real Multiplication)'),
        ('self_twist_type', 'Self-twist type (0=none, 1=CM, 2=RM, 3=both)'),
        ('is_self_dual', 'Self-dual'),
        ('char_order', 'Character order'),
        ('fricke_eigenval', 'Fricke eigenvalue'),
    ]

    for field, desc in fields:
        print(f"--- {desc} ({field}) ---")

        tb = con.execute(f"""
            SELECT mf.{field}, COUNT(*)
            FROM disagreement_atlas da
            JOIN modular_forms mf ON da.object_id = mf.object_id
            WHERE da.disagreement_type = 'B' AND mf.dim = 2 AND mf.weight = 2
            GROUP BY mf.{field} ORDER BY 1
        """).fetchall()

        al = con.execute(f"""
            SELECT mf.{field}, COUNT(*)
            FROM modular_forms mf
            WHERE mf.dim = 2 AND mf.weight = 2
            GROUP BY mf.{field} ORDER BY 1
        """).fetchall()

        tb_dict = {str(r[0]): r[1] for r in tb}
        al_dict = {str(r[0]): r[1] for r in al}
        all_keys = sorted(set(list(tb_dict.keys()) + list(al_dict.keys())))

        for k in all_keys:
            tb_n = tb_dict.get(k, 0)
            al_n = al_dict.get(k, 0)
            tb_pct = tb_n / n_tb * 100 if n_tb > 0 else 0
            al_pct = al_n / n_all * 100 if n_all > 0 else 0
            enrichment = (tb_pct / al_pct) if al_pct > 0 else float('inf')
            marker = " ***" if abs(enrichment - 1.0) > 0.3 else ""
            print(f"  {k:>10s}: TypeB={tb_n:>5d} ({tb_pct:>5.1f}%)  "
                  f"ALL={al_n:>5d} ({al_pct:>5.1f}%)  "
                  f"enrichment={enrichment:.2f}x{marker}")
        print()

    # Cross-tabulation: CM x char_order for Type B
    print("=" * 60)
    print("CROSS-TAB: is_cm x char_order (Type B only)")
    print("=" * 60)
    cross = con.execute("""
        SELECT mf.is_cm, mf.char_order, COUNT(*)
        FROM disagreement_atlas da
        JOIN modular_forms mf ON da.object_id = mf.object_id
        WHERE da.disagreement_type = 'B' AND mf.dim = 2 AND mf.weight = 2
        GROUP BY mf.is_cm, mf.char_order ORDER BY 1, 2
    """).fetchall()
    for row in cross:
        print(f"  CM={str(row[0]):>5s}, char_order={row[1]:>2d}: {row[2]:>5d}")

    # Sato-Tate groups
    print()
    print("=" * 60)
    print("SATO-TATE GROUP DISTRIBUTION")
    print("=" * 60)
    for label, q_extra in [('Type B', """
        FROM disagreement_atlas da
        JOIN modular_forms mf ON da.object_id = mf.object_id
        WHERE da.disagreement_type = 'B' AND mf.dim = 2 AND mf.weight = 2
    """), ('ALL', """
        FROM modular_forms mf
        WHERE mf.dim = 2 AND mf.weight = 2
    """)]:
        rows = con.execute(f"""
            SELECT mf.sato_tate_group, COUNT(*)
            {q_extra}
            GROUP BY mf.sato_tate_group ORDER BY COUNT(*) DESC
        """).fetchall()
        print(f"  {label}:")
        for r in rows[:10]:
            print(f"    {str(r[0]):>20s}: {r[1]:>5d}")
    print()

    # VERDICT
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)

    con.close()


if __name__ == "__main__":
    main()
