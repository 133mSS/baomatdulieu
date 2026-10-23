
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
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name IN (
                  'users',
                  'benchmark_query_cases',
                  'benchmark_runs',
                  'benchmark_case_results'
              )
            ORDER BY table_name, ordinal_position;
        """)

        for row in cur.fetchall():
            print(row)
finally:
    conn.close()
