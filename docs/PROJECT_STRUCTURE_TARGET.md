# PROJECT STRUCTURE TARGET

> **Lưu ý trạng thái:** Đây là cây mục tiêu gốc. Cấu trúc hiện tại được triển khai theo hướng này nhưng một số hạng mục không thể hoàn tất nếu thiếu dữ liệu nguồn/DB (báo cáo DOCX/PDF, benchmark DB export) hoặc cần kiểm chứng runtime; xem `README.md` và `EVIDENCE_INVENTORY.md`.


Cấu trúc mục tiêu dưới đây chỉ dùng các thành phần **đã có trong project**, trừ những mục đánh dấu **(MỚI)**. Chưa có thao tác nào được thực hiện trên project gốc.

## 1. Cây thư mục đề xuất

```text
baomatdulieu/
├── README.md                          (MỚI) cài đặt, thứ tự chạy, ánh xạ WP6/WP7/WP8 -> mục báo cáo
├── .env.example                       (MỚI) chỉ tên khóa, không có giá trị
├── .gitignore                         (MỚI) .env, __pycache__/, *.pyc
├── pytest.ini                         (MỚI) pythonpath = app
├── requirements.txt                   giữ nguyên
├── requirements-dev.txt               (MỚI) pytest, numpy, matplotlib
├── docker-compose.yml                 giữ nguyên
│
├── app/                               CHỈ mã hệ thống (baseline + controlled)
│   ├── auth.py  db_config.py  llm.py  audit.py
│   ├── pdp.py  pep.py  policy.py                      # kiểm soát truy cập
│   ├── retrieval.py  vector_search.py                 # controlled retrieval
│   ├── baseline_rag.py  baseline_vector_search.py     # baseline đối chứng
│   ├── controlled_rag.py  source_documents.py
│   ├── generate_embeddings.py
│   └── dlp/                           # nhóm Output DLP (nếu chấp nhận đổi import)
│       ├── output_dlp.py  output_dlp_policy.py  protection_profile.py
│       ├── redaction.py  sensitive_fact_matcher.py
│       └── structured_fact_extractor.py  entity_normalizer.py
│
├── database/
│   └── init/                          chỉ SQL của DB ứng dụng, đánh số lại
│       ├── 01_extensions.sql
│       ├── 02_schema.sql              (gộp phần protection_profile từ 06)
│       ├── 03_seed.sql
│       ├── 04_seed_chunks.sql         (đổi tên từ 03_seed_chunks.sql)
│       ├── 05_audit.sql
│       └── 06_wp7_prompt_injection_fixture.sql
│
├── benchmark_v1/                      DB benchmark (tách hẳn khỏi DB ứng dụng)
│   ├── sql/
│   │   ├── 00_benchmark_schema.sql
│   │   ├── 01_protection_profile_migration.sql
│   │   ├── 02_add_hybrid_variant.sql  (chuyển từ database/init/04_*)
│   │   └── inspect_ground_truth.sql
│   ├── generate_synthetic_dataset.py
│   ├── generate_benchmark_query_cases.py
│   └── run_retrieval_benchmark.py     (gộp 3 bản, --variant baseline|controlled|hybrid)
│
├── tests/                             giữ nguyên + nhận 2 test đang nằm ở app/
│   ├── (toàn bộ test hiện có)
│   ├── test_benchmark_evaluate.py            (từ app/)
│   └── test_output_dlp_regression_minimum.py (từ app/)
│
├── experiments/                       script tái lập kết quả báo cáo
│   ├── common/
│   │   ├── issue_benchmark_tokens.py
│   │   ├── run_public_benchmark_with_fixture_tokens.py
│   │   └── run_wp7_with_fixture_tokens.py
│   ├── retrieval_acl/    run_retrieval_matrix.py                         # Mục 4.2
│   ├── answer_leakage/   answer_leakage_test.py
│   │                     answer_leakage_test_public_entrypoints.py  <-- PHẢI KHÔI PHỤC (F-02)
│   ├── prompt_injection/ prompt_injection_test.py                        # Mục 4.4
│   ├── ablation/         run_wp8_ablation.py                             # Mục 4.5
│   ├── export/           export_results.py
│   └── diagnostics/      diagnose_*.py (5 file), review_semantic_leakage.py,
│                         diagnose_hybrid_acl.py, reembed_benchmark_chunks.py
│
├── scripts/
│   ├── load_lab_env.ps1
│   ├── prompt_demo_password.ps1       (đổi tên từ pass_for_user.txt)
│   ├── run_answer_leakage_benchmark.ps1
│   ├── seed_users.py  check_llm_service.py
│   └── test_embedding.py  test_semantic_similarity.py  test_extractor_profiles.py
│
├── results/
│   ├── final/                         số liệu đưa vào báo cáo
│   │   ├── wp6_retrieval_matrix_seed4206.csv
│   │   ├── answer_leakage_{cases,metrics,summary}_20261018T051834Z.*
│   │   ├── prompt_injection_{cases,summary}_20261018T072609Z.*
│   │   ├── wp8_ablation_cases_20261018T090103Z.csv
│   │   ├── wp8_ablation_summary_20261018T090103Z.json
│   │   ├── wp8_ablation_metrics_with_ci.csv  wp8_ablation_summary_with_ci.json
│   │   ├── wp8_prompt_injection_{runs,by_group}.csv
│   │   ├── wp8_audit_counts.csv  wp8_audit_sample_allow_deny_redact.csv
│   │   └── wp8_export_summary.json
│   ├── archive/                       lịch sử, KHÔNG xóa
│   │   ├── answer_leakage_*  (9 run còn lại)
│   │   ├── prompt_injection_*  (2 run lặp: 064741Z, 072235Z)
│   │   └── wp8_ablation_*_{075518Z,082430Z}.*  wp8_ablation_status.csv (cũ)
│   ├── benchmark_v1/                  (MỚI) CSV xuất từ DB benchmark (F-19)
│   └── figures/                       biểu đồ thang xám (tái tạo từ CSV)
│
├── tools/                             (MỚI)
│   └── make_report_figures.py         tái tạo hình báo cáo từ results/final
│
└── docs/                              (MỚI)
    ├── PROJECT_AUDIT.md
    ├── EVIDENCE_INVENTORY.md
    ├── WP8_SETUP.md                   (chuyển từ experiments/)
    └── report/  Bao_cao_tieu_luan_Bao_mat_du_lieu.{docx,pdf}
```

> Thư mục `app/dlp/` là **đề xuất tùy chọn**. Nếu chọn, phải sửa toàn bộ `import` (ví dụ `from output_dlp import …`) và 34 test chèn `sys.path`. Phương án an toàn hơn: **giữ nguyên các file DLP ở `app/`** và chỉ chuyển file không thuộc hệ thống. Tôi khuyến nghị phương án an toàn này.

## 2. Bảng ánh xạ

Mức an toàn: **A** = không ảnh hưởng chạy; **B** = cần sửa import/đường dẫn; **C** = cần xác minh thực nghiệm lại.

| Đường dẫn cũ | Đường dẫn đề xuất | Hành động | Lý do | An toàn |
|---|---|---|---|---|
| `.env` | (loại khỏi bản nộp) + `.env.example` | Xóa khỏi ZIP, rotate khóa | F-01 | A (sau khi đổi khóa) |
| `**/__pycache__/*` | — | Xóa | F-04 | A |
| `database/init/04_migration_add_hybrid_variant.sql` | `benchmark_v1/sql/02_add_hybrid_variant.sql` | Di chuyển | F-05 | C (dựng lại Docker) |
| `database/init/03_seed_chunks.sql` | `database/init/04_seed_chunks.sql` | Đổi tên | F-06 | C |
| `database/init/05_audit.sql` | `database/init/05_audit.sql` | Giữ | — | A |
| `database/init/06_protection_profile_metadata.sql` | gộp vào `02_schema.sql` + `03_seed.sql` | Gộp | F-07 | C |
| `database/init/07_wp7_prompt_injection_fixture.sql` | `database/init/06_wp7_prompt_injection_fixture.sql` | Đổi tên | Đánh số lại | C |
| `benchmark_v1/00_*.sql, 01_*.sql, inspect_ground_truth.sql` | `benchmark_v1/sql/…` | Di chuyển | Gom SQL | B |
| `app/run_retrieval_benchmark.py`, `…_hybrid.py` | `benchmark_v1/run_retrieval_benchmark.py` (`--variant`) | Gộp | F-20 | C |
| `app/run_retrieval_benchmark_hybrid_diagnostic.py` | `results/archive/` hoặc `experiments/diagnostics/` | Lưu trữ | F-20 | A |
| `app/review_semantic_leakage.py`, `app/reembed_benchmark_chunks.py`, `app/diagnose_hybrid_acl.py` | `experiments/diagnostics/` | Di chuyển | F-11 | B |
| `app/test_benchmark_evaluate.py`, `app/test_output_dlp_regression_minimum.py` | `tests/` | Di chuyển | F-11 | B |
| `experiments/answer_leakage_test*.py`, `leakage_test.py` | `experiments/answer_leakage/` | Di chuyển | Gom theo thí nghiệm | B |
| `experiments/prompt_injection_test.py` | `experiments/prompt_injection/` | Di chuyển | Gom | B |
| `experiments/run_wp8_ablation.py` | `experiments/ablation/` | Di chuyển | Gom | B |
| `experiments/run_wp8_ablation_debug.py` | `experiments/diagnostics/` (hoặc xóa) | Lưu trữ | F-21 | A |
| `experiments/diagnose_*.py` | `experiments/diagnostics/` | Di chuyển | F-22 | A |
| `experiments/export_results.py` | `experiments/export/` | Di chuyển | Gom | B |
| `experiments/WP8_SETUP.md` | `docs/WP8_SETUP.md` | Di chuyển | Gom tài liệu | A |
| `scripts/pass_for_user.txt` | `scripts/prompt_demo_password.ps1` | Đổi tên | F-23 | A |
| `results/wp8_ablation_*_{075518Z,082430Z}.*`, `results/wp8_ablation_status.csv` | `results/archive/` | Lưu trữ | F-13, F-14 | A |
| `results/answer_leakage_*` (trừ `051834Z`) | `results/archive/` | Lưu trữ | F-15 | A |
| `results/prompt_injection_*` (trừ `072609Z`) | `results/archive/` | Lưu trữ | F-16 | C (sửa tiêu chí exporter) |
| `results/wp8_*.png` | `results/archive/` + `results/figures/*.png` (thang xám) | Thay thế | F-17 | A |
| — | `README.md`, `.env.example`, `.gitignore`, `pytest.ini`, `requirements-dev.txt` | Tạo mới | F-26, F-27 | A |

## 3. Các thao tác **cần bạn phê duyệt**
1. Xóa `.env` khỏi bản nộp và rotate mật khẩu DB + `SECRET_KEY` (F-01).
2. Khôi phục `answer_leakage_test_public_entrypoints.py` hoặc cho phép viết lại (F-02).
3. Di chuyển `database/init/04_*` và đánh số lại SQL (F-05/F-06/F-07).
4. Chuyển file khỏi `app/` (F-11) — có/không dùng `app/dlp/`.
5. Gộp 3 script benchmark retrieval (F-20).
6. Lưu trữ kết quả cũ vào `results/archive/` (F-13…F-16).
7. Xuất kết quả benchmark quy mô lớn từ DB (F-19) — **bạn cần chạy**, tôi không có DB.

## 4. Kiểm tra trước khi thực hiện
- Chạy `pytest` trước và sau mỗi bước; mốc hiện tại: 476 pass / 2 fail / 11 error (không DB).
- `docker compose down -v && docker compose up` để xác nhận khởi tạo DB sạch sau khi sửa SQL.
- Chạy lại `experiments/export_results.py --skip-audit` và so sánh `wp8_export_summary.json` với bản hiện tại.
