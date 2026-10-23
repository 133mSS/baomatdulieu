
import psycopg2
import getpass

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="baomatdulieu_benchmark",
    user="admin",
    password=getpass.getpass("Postgres password: "),
)

try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT username, role::text, department::text
            FROM users
            WHERE username LIKE 'bench_%'
            ORDER BY username;
        """)

        rows = cur.fetchall()
        for row in rows:
            print(row)

        print(f"\nTotal benchmark users: {len(rows)}")
finally:
    conn.close()
