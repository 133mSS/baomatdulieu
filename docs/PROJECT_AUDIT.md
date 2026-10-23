# PROJECT AUDIT — Tiểu luận Bảo mật dữ liệu, Nhóm 11

> **Lưu ý trạng thái:** Đây là audit gốc trước khi tái cấu trúc. Các thao tác đã thực hiện và các giới hạn còn lại được ghi trong `README.md` và `EVIDENCE_INVENTORY.md`. Không xem bảng đề xuất trong audit là bằng chứng rằng mọi vấn đề đã được giải quyết.


Phạm vi: toàn bộ `baomatdulieu.zip` (285 file; 92 file `.py`, 191 file `.pyc`) và đề cương `DE_CUONG_TIEU_LUAN_BAO_MAT_DU_LIEU_NHOM_11.pdf`.
Nguyên tắc: **chưa di chuyển, đổi tên, xóa hay ghi đè bất kỳ file gốc nào.** Mọi đề xuất bên dưới chờ bạn phê duyệt.

---

## 1. Tổng quan trạng thái

Project là một hệ RAG thử nghiệm hoàn chỉnh về mặt chức năng. Các thành phần đề cương yêu cầu đều có implementation:

| Mục tiêu đề cương | Bằng chứng trong ZIP | Trạng thái |
|---|---|---|
| Phân loại 4 mức, mô hình quyền | `database/init/02_schema.sql`, `app/pdp.py` | Đã triển khai |
| Xác thực mật khẩu + token + MFA | `app/auth.py` (bcrypt, TOTP, token HMAC-SHA256) | Đã triển khai |
| Kho vector + baseline không lọc | `docker-compose.yml` (pgvector), `app/baseline_rag.py`, `app/baseline_vector_search.py` | Đã triển khai |
| ABAC + PDP/PEP, lọc trước prompt | `app/pdp.py`, `app/pep.py`, `app/retrieval.py`, `app/vector_search.py` | Đã triển khai |
| Che dữ liệu động (output filter) | `app/output_dlp.py`, `protection_profile.py`, `redaction.py`, `output_dlp_policy.py` | Đã triển khai (cấu hình theo catalog, xem F-09) |
| Prompt injection | `experiments/prompt_injection_test.py` (20 case, 7 nhóm) | Đã triển khai + có kết quả |
| Audit log allow/deny/redact | `app/audit.py`, bảng `audit_log` | Đã triển khai + có số liệu tổng hợp |
| So sánh baseline vs có kiểm soát | `results/answer_leakage_*`, `results/wp8_ablation_*` | Có kết quả |
| Dashboard (tùy chọn) | Không thấy | Không triển khai (đúng tinh thần "tùy chọn") |

Kiểm thử tự động: tôi chạy `pytest` trong môi trường của tôi (Python 3.12, **không có PostgreSQL/Ollama**): **476 passed, 2 failed, 11 error**. 11 error đều là `psycopg2.OperationalError` do không có DB (8 ở `tests/test_policy.py`, 3 ở `tests/test_retrieval_postgres_integration.py`). 2 failed là test lỗi thời (F-12). Đây **không phải** xác nhận tái lập toàn bộ thực nghiệm: các thực nghiệm cần Ollama + PostgreSQL và tôi không chạy lại chúng.

Điểm kiểm chứng độc lập tôi đã làm được: duyệt toàn bộ 6 vai trò × 4 nhãn × 4 giá trị phòng ban (96 tổ hợp) cho thấy `pdp.decide()` cho cùng kết quả với mô hình BLP + ABAC "chặt" viết lại độc lập → **0 khác biệt**. Nghĩa là ngoại lệ `LEGACY-LEADERSHIP` không làm thay đổi hành vi trong mô hình vai trò hiện tại (xem F-10).

---

## 2. Bảng kiểm kê vấn đề

Mức ưu tiên: **P0** = phải xử lý trước khi nộp/vấn đáp; **P1** = nên xử lý; **P2** = dọn dẹp.

| STT | Đường dẫn hiện tại | Vấn đề | Bằng chứng | Ưu tiên | Đề xuất | Lý do |
|---|---|---|---|---|---|---|
| F-01 | `.env` | File cấu hình thật (chứa mật khẩu DB và `SECRET_KEY`) nằm trong ZIP | Có 6 khóa: `POSTGRES_HOST/DB/USER/PASSWORD/PORT`, `SECRET_KEY` (không ghi giá trị) | **P0** | **Loại khỏi bản nộp**, đổi (rotate) mật khẩu và `SECRET_KEY`, tạo `.env.example` chỉ có tên khóa | Lộ secret khi nộp/chia sẻ ZIP; đề tài bảo mật nên không thể tự lộ khóa |
| F-02 | `experiments/answer_leakage_test_public_entrypoints.py` | **Source bị thiếu** — chỉ còn `__pycache__/…cpython-314.pyc` (24.715 byte) | `answer_leakage_test.py`, `run_public_benchmark_with_fixture_tokens.py`, `scripts/run_answer_leakage_benchmark.ps1` đều tham chiếu file này; `find` không thấy `.py` | **P0** | Khôi phục file `.py` từ máy nhóm; nếu mất, viết lại và so khớp với `results/answer_leakage_cases_*.csv` | Đây là script sinh ra **toàn bộ** số liệu answer-leakage (10 lần chạy). Không có source thì không tái lập được và không giải thích được cách tính "leak" khi vấn đáp |
| F-03 | `scripts/test_llm.py` | Source thiếu, còn `.pyc`; `check_llm_service.py` có docstring vẫn gọi `test_llm.py` | `scripts/__pycache__/test_llm.cpython-314-pytest-9.1.1.pyc`; docstring dòng 4 | P2 | Đã đổi tên thành `check_llm_service.py` → sửa docstring, xóa `.pyc` | Tên cũ gây hiểu nhầm (smoke test chứ không phải pytest) |
| F-04 | `**/__pycache__/` (191 file `.pyc`) | Artifact tái tạo được, kể cả bản `pytest-9.1.1.pyc` | Danh sách file | P2 | **Xóa** + thêm `.gitignore` | Tái tạo tự động; làm phình ZIP, và là nơi lộ F-02 |
| F-05 | `database/init/04_migration_add_hybrid_variant.sql` | Migration của **DB benchmark** nằm trong thư mục khởi tạo **DB ứng dụng** | File chạy `ALTER TABLE benchmark_runs …`; bảng này chỉ có trong `benchmark_v1/00_benchmark_schema.sql`; `docker-compose.yml` mount cả `database/init` vào `docker-entrypoint-initdb.d` | **P0** | Chuyển sang `benchmark_v1/sql/`; đánh số lại `database/init` | Rất có khả năng làm khởi tạo container lỗi (image `postgres` chạy các `.sql` theo thứ tự tên và dừng khi lỗi). *Tôi chưa chạy Docker nên cần bạn xác minh.* |
| F-06 | `database/init/03_seed.sql` & `03_seed_chunks.sql` | Hai file cùng tiền tố `03_`; thứ tự phụ thuộc sắp xếp chữ cái | Tên file | P1 | Đổi `03_seed_chunks.sql` → `04_seed_chunks.sql`, đánh số lại các file sau | Thứ tự chạy phải tường minh |
| F-07 | `database/init/02_schema.sql`, `06_protection_profile_metadata.sql`, `07_*.sql` | Cột `protection_profile` được định nghĩa trong `02` rồi `ALTER … ADD COLUMN IF NOT EXISTS` lại trong `06`; `UPDATE` backfill lặp ở `03` và `06` | Nội dung các file | P1 | Gộp `06` vào `02`/`03`; giữ `07` (fixture) tách riêng | Trùng trách nhiệm; không đổi hành vi nếu gộp đúng |
| F-08 | `benchmark_v1/00_benchmark_schema.sql` | `decision_t` chỉ có `ALLOW/DENY/REDACT` (thiếu `BLOCK`), `audit_log` thiếu `request_id, stage, rule_id, release_context`; ràng buộc `system_variant` chưa có `hybrid` cho tới khi chạy 04 | So sánh với `05_audit.sql` và `04_migration…` | P1 | Cập nhật schema benchmark cho khớp schema ứng dụng, gộp migration | Hai schema lệch nhau gây lỗi khi dùng `audit.py` trên DB benchmark |
| F-09 | `app/protection_profile.py`, `app/output_dlp.py` | DLP cấu hình bằng **hằng số của benchmark** (`money:45:million:USD`, `"XYZ"`, `"Nhà cung cấp A"`, `ratio:12/20`…) và `DOCUMENT_PROFILES` theo ID 1–8 | Nội dung file | **P0 (về học thuật)** | Giữ code; **bắt buộc nêu trong 5.2** rằng DLP là catalog cấu hình sẵn, không phải bộ phát hiện tổng quát | Nếu không nêu, kết quả "0 rò rỉ dữ kiện" dễ bị hiểu là khả năng tổng quát |
| F-10 | `app/pdp.py` | Ngoại lệ `LEGACY-LEADERSHIP` cho phép đọc trước khi kiểm tra nhãn/phòng ban; docstring tự nhận là "documented policy deviation" | Mã nguồn; duyệt 96 tổ hợp: 0 khác biệt với mô hình chặt | P1 | Giữ nguyên; **nêu rõ** trong 3.2/5.2; cân nhắc xóa ngoại lệ vì thừa | Hiện thừa về hành vi nhưng sẽ trở thành lỗ hổng nếu thêm vai trò mới |
| F-11 | `app/test_benchmark_evaluate.py`, `app/test_output_dlp_regression_minimum.py`, `app/run_*`, `app/review_semantic_leakage.py`, `app/reembed_benchmark_chunks.py`, `app/diagnose_hybrid_acl.py` | Lẫn script thực nghiệm/test vào thư mục lõi `app/` | Danh sách file | P1 | Chuyển sang `tests/` và `experiments/benchmark/` | Tách mã sản phẩm khỏi mã đo lường. **Rủi ro:** 34 file test tự chèn `sys.path` (xem mục 3) |
| F-12 | `tests/test_wp8_ablation_runner.py`, `tests/test_wp8_export_results.py` | 2 test fail: gọi hàm `collect_ablation` (đã đổi tên thành `collect_ablation_final`) và assert cảnh báo WP7 cũ | `AttributeError: … no attribute 'collect_ablation'`; `assert False` | P1 | Cập nhật test theo `export_results.py` hiện tại | Test đỏ làm giảm độ tin cậy khi nộp |
| F-13 | `results/wp8_ablation_status.csv` | **Mâu thuẫn** với kết quả hiện tại: ghi Baseline `fact_leaked=48`, DLP-only `block=21`, `harmless_over_redaction=0.8`, `answerable=0.3333`; trong khi `wp8_ablation_metrics_with_ci.csv` (run `…090103Z`) ghi 78 / redact=21, block=0 / 0.0 / 0.8333 | Trích dẫn nguồn trong file là `…075518Z.json` | **P0** | Xóa hoặc tái tạo từ run `…090103Z`; chuyển hai run cũ sang `results/archive/` | Nếu trích nhầm, báo cáo sẽ có hai bộ số mâu thuẫn |
| F-14 | `results/wp8_ablation_summary_20261018T075518Z.json`, `…082430Z.json` (+ `cases_*.csv`) | Hai lần chạy ablation dùng **phiên bản detector/DLP cũ** — không so sánh trực tiếp được với lần `…090103Z` | Cả hai: DLP-only over-redaction 12/15, block 21; Baseline `leaked_fact_count=48` so với 78 | P1 | Giữ làm lịch sử trong `archive/` (không xóa) | Là bằng chứng cho quá trình tinh chỉnh DLP; chỉ nên dùng khi bàn về over-redaction |
| F-15 | `results/answer_leakage_*_2026101*` (10 run) | 10 lần chạy với **3 bộ case khác nhau** (10 → 30 → 40 case); hai run cuối (`044243Z`, `051834Z`) có CSV case **giống hệt từng byte** | So sánh nhị phân hai file CSV | P1 | Dùng `051834Z` làm kết quả chính; lưu 9 run còn lại vào `archive/` | Tránh trộn các bộ case khác nhau |
| F-16 | `results/prompt_injection_*_{064741Z,072235Z,072609Z}` | 3 lần chạy cho **kết quả đồng nhất** (cùng 20 case, `temperature=0, seed=42`) | `wp8_prompt_injection_runs.csv`: 11/20 và 0/20 ở cả 3 run | P1 | Ghi nhận là **lặp lại tính tái lập**, không phải 3 mẫu độc lập; giữ 1 bản chính, lưu 2 bản kia vào `archive/` | `WP8_SETUP.md` đếm "3 run ID" là đủ yêu cầu lặp; về thống kê không thêm thông tin |
| F-17 | `results/wp8_*.png` (3 file) | Biểu đồ **có màu** (RGBA) — vi phạm yêu cầu đơn sắc; chỉ biểu diễn run cuối | Kiểm tra pixel: có điểm chroma > 30 | P1 | Dùng bản thang xám tái tạo từ CSV (`tools/make_report_figures.py` kèm theo) | Yêu cầu định dạng báo cáo |
| F-18 | `results/wp8_audit_counts.csv` | Số liệu audit (retrieval ALLOW 673, DENY 347; output_dlp REDACT 180) là **tích lũy toàn bộ DB** qua mọi lần chạy, không gắn run nào | Script `export_results.py` chỉ `COUNT(*) GROUP BY stage, decision` | P1 | Ghi rõ "tích lũy" trong báo cáo, hoặc xuất theo `request_id`/khoảng thời gian | Không được diễn giải như kết quả của một thí nghiệm |
| F-19 | `benchmark_v1/*`, `app/run_retrieval_benchmark*.py` | Có schema, generator (1.000/5.000/10.000 tài liệu), 3 phiên bản script benchmark, nhưng **không có file kết quả** (kết quả nằm trong bảng DB `benchmark_case_results`, không xuất ra `results/`) | `results/` không có CSV benchmark; `review_semantic_leakage.py` đọc từ DB | **P0 (về bằng chứng)** | Xuất bảng DB ra CSV vào `results/benchmark_v1/`, hoặc báo cáo chỉ nêu đây là công cụ chưa có bằng chứng | Tránh viết kết quả mà ZIP không chứng minh được |
| F-20 | `app/run_retrieval_benchmark.py`, `…_hybrid.py`, `…_hybrid_diagnostic.py` | Ba phiên bản gần giống nhau (21 KB, 29 KB, 35 KB); docstring bản hybrid vẫn hướng dẫn chạy `run_retrieval_benchmark.py` | Đầu file | P1 | Gộp thành một script có tham số `--variant`; giữ bản diagnostic trong `archive/` | Dễ chạy nhầm; khó giải thích khi vấn đáp |
| F-21 | `experiments/run_wp8_ablation_debug.py` | Bản sao của `run_wp8_ablation.py`, khác 38 dòng diff | `diff` | P2 | Archive hoặc xóa sau khi xác nhận khác biệt | Trùng chức năng |
| F-22 | `experiments/diagnose_*.py` (5 file) | Script chẩn đoán dùng một lần | Tên và nội dung | P2 | Chuyển `experiments/diagnostics/` | Không cần cho tái lập kết quả chính |
| F-23 | `scripts/pass_for_user.txt` | Tên gây hiểu nhầm (nghe như chứa mật khẩu), thực chất là đoạn PowerShell nhập `SEED_DEMO_PASSWORD` bằng `-AsSecureString`; không thấy mật khẩu tường minh | 6 dòng đầu | P1 | Gộp vào `scripts/load_lab_env.ps1` hoặc đổi thành `prompt_demo_password.ps1` | Tên file không phản ánh chức năng; dễ bị nhầm là lộ secret |
| F-24 | `benchmark_v1/generate_*.py`, `tests/test_retrieval_postgres_integration.py` | Giá trị mặc định `BENCHMARK_DB_USER="admin"`, `BENCHMARK_DB_PASSWORD="admin"` khi thiếu biến môi trường | Các dòng 31–32, 62–63, 32–33 | P1 | Bỏ mặc định, báo lỗi khi thiếu biến (như `db_config.py` đang làm) | Mật khẩu mặc định yếu trong mã nguồn |
| F-25 | `database/init/…`, `app/auth.py` | `mfa_secret` (seed TOTP) lưu **plaintext** trong cột `users.mfa_secret`; token không có cơ chế thu hồi | `auth.py`, `02_schema.sql` | P2 | Nêu là hạn chế/hướng phát triển (quản lý khóa nằm **ngoài phạm vi** theo đề cương) | Phù hợp phạm vi nhưng phải thừa nhận |
| F-26 | Toàn project | **Không có README** hay hướng dẫn chạy; chỉ có `experiments/WP8_SETUP.md`; thuật ngữ "WP6/WP7/WP8", "G10" không được định nghĩa | `find -name "*.md"` | **P0** | Tạo `README.md` (cài đặt, thứ tự chạy, ánh xạ WP → mục báo cáo) | Giảng viên/nhóm khác không chạy được |
| F-27 | `requirements.txt` | Thiếu `numpy` (dùng trong `benchmark_v1/generate_synthetic_dataset.py`) và `matplotlib` (dùng trong `export_results.py` để vẽ PNG); `pytest` không được liệt kê | Import trong các file | P1 | Bổ sung `requirements-dev.txt` | Tái lập môi trường |
| F-28 | `app/audit.py`, `app/vector_search.py`, `app/controlled_rag.py` | Audit `DENY` được tạo từ **truy vấn bóng (shadow query)** — chỉ ghi các chunk nằm trong top-k *không lọc* mà người dùng không được phép; `rule_id` luôn là `acl_policy`, lý do là `policy_violation` — không lưu quy tắc PDP cụ thể (`BLP-1`/`ABAC-2`) | Mã nguồn | P1 | Giữ; **nêu rõ trong 3.6/4.3** cách đọc `DENY` | Nếu không, 347 `DENY` sẽ bị hiểu là "số tài liệu bị từ chối" |

### Các mục **cần giữ** (nhóm A)
`app/{auth,pdp,pep,policy,retrieval,vector_search,baseline_rag,baseline_vector_search,controlled_rag,llm,audit,db_config,source_documents,output_dlp,output_dlp_policy,protection_profile,redaction,sensitive_fact_matcher,structured_fact_extractor,entity_normalizer,generate_embeddings}.py`; `database/init/*` (sau khi sửa F-05..F-07); `docker-compose.yml`; `requirements.txt`; toàn bộ `tests/` (sau F-12); `experiments/{prompt_injection_test,run_wp8_ablation,export_results,run_retrieval_matrix,leakage_test,issue_benchmark_tokens,run_public_benchmark_with_fixture_tokens,run_wp7_with_fixture_tokens}.py`; `benchmark_v1/*`; `results/{wp8_ablation_cases_20261018T090103Z.csv, wp8_ablation_summary_20261018T090103Z.json, wp8_ablation_metrics_with_ci.csv, wp8_ablation_summary_with_ci.json, answer_leakage_*_20261018T051834Z.*, prompt_injection_*_20261018T072609Z.*, wp6_retrieval_matrix_seed4206.csv, wp8_prompt_injection_by_group.csv, wp8_prompt_injection_runs.csv, wp8_audit_*.csv, wp8_export_summary.json}`.

### Thành phần còn thiếu (nhóm F)
1. Source `answer_leakage_test_public_entrypoints.py` (F-02).
2. `README.md`, `.env.example`, `.gitignore`, `pytest.ini` (F-26, F-01).
3. Kết quả benchmark quy mô 1.000/5.000/10.000 xuất ra CSV (F-19).
4. Thông tin phần cứng/phiên bản môi trường chạy thật (hiện chỉ suy ra từ `docker-compose.yml`, `llm.py`, tên `.pyc`): phiên bản PostgreSQL ngoài `pg16`, phiên bản Ollama, CPU/GPU/RAM. **Cần bạn bổ sung** — báo cáo đánh dấu "cần xác minh".
5. Kiểm thử cho khẳng định "audit log không ghi dữ kiện nhạy cảm" ngoài `query_text` (xem F-18/F-28) — `query_text` **được** ghi nguyên văn vào `audit_log`.

---

## 3. Rủi ro khi thực hiện các đề xuất
- **Di chuyển file khỏi `app/`:** 34 file test dùng `sys.path.insert(...)` hoặc import trần (`from pdp import decide`). Cần thêm `pytest.ini` với `pythonpath = app` trước khi di chuyển, rồi chạy lại toàn bộ `pytest` để đối chiếu **476 pass** hiện tại.
- **Đánh số lại SQL:** cần dựng lại volume Docker (`docker compose down -v`) để kiểm tra khởi tạo sạch; các script `experiments/*` giả định DB `baomatdulieu` đã có dữ liệu seed + embedding.
- **Archive kết quả:** `export_results.py` tìm `results/*_summary_*.json` bằng `glob` — nếu chuyển file cũ vào `archive/` thì exporter sẽ chỉ thấy 1 run; điều này **thay đổi** số "run ID" mà `WP8_SETUP.md` dùng làm tiêu chí. Cần sửa tiêu chí đó (F-16).
- **Xóa `.env`:** các script `experiments/*` gọi `_load_dotenv()`; sau khi rotate khóa, phải cập nhật `SECRET_KEY` mới và mật khẩu DB mới.
