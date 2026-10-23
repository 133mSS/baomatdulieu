"""Export real rows from baomatdulieu_benchmark to report-friendly CSV files.

Connection settings are read from environment variables. No credentials are logged.
The exporter only exports metadata/metrics and omits password hashes, MFA secrets,
chunk/document bodies, and generated answer text.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUT = Path(__file__).resolve().parents[1] / "results" / "benchmark_v1"

# Each query is deliberately allow-listed. Do not use SELECT * for exports.
EXPORT_QUERIES: dict[str, str] = {
    "benchmark_dataset_counts.csv": """
        SELECT dataset_scale, document_count, chunk_count,
               chunks_with_embedding, chunks_without_embedding,
               public_documents, internal_documents, secret_documents,
               top_secret_documents
        FROM benchmark_dataset_counts ORDER BY dataset_scale
    """,
    "benchmark_users.csv": """
        SELECT id, username, role::text AS role, department::text AS department
        FROM users ORDER BY id
    """,
    "benchmark_documents_metadata.csv": """
        SELECT id, title, classification::text AS classification,
               department::text AS department, protection_profile,
               benchmark_scale, generation_seed
        FROM documents ORDER BY id
    """,
    "benchmark_chunks_metadata.csv": """
        SELECT id, document_id, chunk_no, vector_kind,
               (embedding IS NOT NULL) AS has_embedding
        FROM chunks ORDER BY id
    """,
    "benchmark_query_cases.csv": """
        SELECT id, case_key, query_text, username,
               expected_relevant_document_ids, protected_facts::text AS protected_facts,
               test_category, expected_answerable, notes, created_at
        FROM benchmark_query_cases ORDER BY id
    """,
    "benchmark_runs.csv": """
        SELECT id, run_name, system_variant, experiment_type, dataset_scale,
               seed, top_k, vector_dimension, distance_metric, index_description,
               postgres_version, pgvector_version, embedding_model,
               hardware_description, warmup_count, measurement_count,
               config_json::text AS config_json, started_at, finished_at, notes, created_at
        FROM benchmark_runs ORDER BY id
    """,
    "benchmark_case_results.csv": """
        SELECT r.id, r.run_id, b.run_name, b.system_variant, b.experiment_type,
               q.id AS query_case_id, q.case_key, q.test_category,
               r.repetition_no, r.returned_document_ids, r.returned_chunk_ids,
               r.unauthorized_chunk_ids, r.recall_at_k, r.unauthorized_context_count,
               r.protected_facts_leaked_exact, r.semantic_review_required,
               r.semantic_review_result, r.notes, r.created_at
        FROM benchmark_case_results r
        JOIN benchmark_runs b ON b.id = r.run_id
        JOIN benchmark_query_cases q ON q.id = r.query_case_id
        ORDER BY r.id
    """,
    "benchmark_performance_results.csv": """
        SELECT p.id, p.run_id, b.run_name, b.system_variant, b.experiment_type,
               b.dataset_scale, p.repetition_no, p.warmup, p.policy_latency_ms,
               p.embedding_latency_ms, p.vector_search_ms, p.total_retrieval_ms,
               p.returned_chunk_count, p.allowed_document_count, p.created_at
        FROM benchmark_performance_results p
        JOIN benchmark_runs b ON b.id = p.run_id
        ORDER BY p.id
    """,
    "benchmark_validation_results.csv": """
        SELECT id, dataset_scale, seed, documents_expected, documents_actual,
               chunks_expected, chunks_actual, chunks_missing_embedding,
               invalid_dimension_count, allowed_document_ratio, validation_passed,
               validation_details::text AS validation_details, created_at
        FROM benchmark_validation_results ORDER BY id
    """,
}


def csv_value(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return value


def write_query_csv(cur, sql: str, path: Path) -> int:
    cur.execute(sql)
    headers = [col.name if hasattr(col, "name") else col[0] for col in cur.description]
    rows_written = 0
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        while True:
            rows = cur.fetchmany(1000)
            if not rows:
                break
            writer.writerows([[csv_value(v) for v in row] for row in rows])
            rows_written += len(rows)
    return rows_written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT,
                        help="Output directory (default: results/benchmark_v1)")
    parser.add_argument("--database", default=os.getenv("BENCHMARK_DB_NAME", "baomatdulieu_benchmark"),
                        help="Benchmark database name; default: BENCHMARK_DB_NAME or baomatdulieu_benchmark")
    args = parser.parse_args()

    missing = [k for k in ("POSTGRES_USER", "POSTGRES_PASSWORD") if not os.getenv(k)]
    if missing:
        print("ERROR: missing required environment variable(s): " + ", ".join(missing), file=sys.stderr)
        print("Set POSTGRES_USER and POSTGRES_PASSWORD; credentials are never printed.", file=sys.stderr)
        return 2
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 is not installed in the active Python environment.", file=sys.stderr)
        print("Install project requirements, then rerun this exporter.", file=sys.stderr)
        return 2

    config = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": args.database,
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
        "connect_timeout": 8,
    }
    args.outdir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "source_database": args.database,
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "live PostgreSQL benchmark database",
        "files": {},
        "privacy": "No password hashes, MFA secrets, document/chunk bodies, or generated answer text exported.",
    }
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT current_database(), current_setting('server_version')")
                db_name, pg_version = cur.fetchone()
                if db_name != args.database:
                    raise RuntimeError(f"Connected database mismatch: expected {args.database!r}, got {db_name!r}")
                manifest["postgres_version"] = pg_version
                for filename, sql in EXPORT_QUERIES.items():
                    path = args.outdir / filename
                    count = write_query_csv(cur, sql, path)
                    manifest["files"][filename] = {"rows": count, "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest()}
        manifest_path = args.outdir / "export_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception as exc:
        # Remove partial files so the directory cannot be mistaken for a complete export.
        for filename in EXPORT_QUERIES:
            (args.outdir / filename).unlink(missing_ok=True)
        (args.outdir / "export_manifest.json").unlink(missing_ok=True)
        print(f"ERROR: benchmark export failed ({type(exc).__name__}). No partial export was retained.", file=sys.stderr)
        print("Check that the benchmark database is running, credentials are correct, and schema is initialized.", file=sys.stderr)
        return 1

    print(f"Exported {len(manifest['files'])} CSV files from database {args.database!r} to {args.outdir}")
    for name, info in manifest["files"].items():
        print(f"  {name}: {info['rows']} rows")
    print("Manifest: export_manifest.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
