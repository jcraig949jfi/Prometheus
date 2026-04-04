"""Quick test of LMFDB PostgreSQL mirror connection."""
import psycopg2

try:
    conn = psycopg2.connect(
        host='devmirror.lmfdb.xyz',
        port=5432,
        dbname='lmfdb',
        user='lmfdb',
        password='lmfdb',
        connect_timeout=15
    )
    cur = conn.cursor()

    # Find tables with zeros or L-function data
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND (table_name LIKE '%%zero%%' OR table_name LIKE '%%lfunc%%' 
             OR table_name LIKE '%%ec_curve%%' OR table_name LIKE '%%mf_%%')
        ORDER BY table_name LIMIT 30
    """)
    print('Relevant tables:')
    for row in cur.fetchall():
        print(f'  {row[0]}')

    # Check lfunc_zeros or similar
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_name LIKE '%%lfunc%%'
        ORDER BY table_name
    """)
    print('\nL-function tables:')
    for row in cur.fetchall():
        print(f'  {row[0]}')

    # Check ec tables
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_name LIKE '%%ec%%'
        ORDER BY table_name
    """)
    print('\nEC tables:')
    for row in cur.fetchall():
        print(f'  {row[0]}')

    conn.close()
    print('\nConnection successful!')
except Exception as e:
    print(f'Connection failed: {e}')
