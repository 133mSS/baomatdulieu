# Benchmark database exports (F-19)

The CSV files in this directory must be exported from the live `baomatdulieu_benchmark`
PostgreSQL database. They are not derived from WP6/WP8 results and must not be filled
with synthetic placeholder rows.

## Export on the machine hosting the project

Ensure the benchmark database has already been initialized and populated. From the
project root, activate the same Python environment that has `psycopg2` installed and
set the database credentials in PowerShell (use your actual local values; do not commit
`.env`):

```powershell
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_USER = "admin"
$env:POSTGRES_PASSWORD = "<your local PostgreSQL password>"
$env:BENCHMARK_DB_NAME = "baomatdulieu_benchmark"
python .\benchmark_v1\export_benchmark_db.py
```

The exporter writes nine allow-listed CSVs plus `export_manifest.json`, including row
counts and SHA-256 checksums. It deliberately omits password hashes, MFA secrets,
document/chunk bodies, and generated answer text. If connection or schema validation
fails, it removes partial CSVs and exits non-zero; it never fabricates an export.

**Current status:** exporter implemented and statically validated. This delivery
environment has no `docker`, `psql`, `pg_dump`, or installed `psycopg2`, and has no
live connection/backup of `baomatdulieu_benchmark`; therefore no genuine DB CSVs are
claimed here. Run the command above on the project's configured machine to complete
the actual database export.
