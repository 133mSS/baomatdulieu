# Data-Centric Access Control for RAG — Nhóm 11

## Mục tiêu
Thử nghiệm kiểm soát truy cập dữ liệu cho RAG theo nguyên tắc **DATA → POLICY → RETRIEVAL → LLM**. Baseline và controlled system được giữ để so sánh leakage; Output DLP là lớp bổ sung, không thay thế kiểm soát trước retrieval.

## Cấu trúc
- `app/`: mã hệ thống baseline/controlled, policy, retrieval, auth, audit và DLP. Các module DLP được giữ tại `app/` để tránh phá vỡ imports.
- `database/init/`: SQL khởi tạo DB ứng dụng theo thứ tự tên file.
- `benchmark_v1/sql/`: schema và migration của DB benchmark, tách khỏi DB ứng dụng.
- `benchmark_v1/run_retrieval_benchmark.py`: benchmark thống nhất; chọn `--variant baseline|controlled|hybrid`.
- `experiments/`: runners theo retrieval ACL, answer leakage, prompt injection, ablation, export và diagnostics.
- `results/final/`: kết quả được chọn làm bằng chứng báo cáo; `results/archive/` lưu lịch sử, không xóa.
- `results/benchmark_v1/`: nơi đặt CSV export từ DB benchmark khi có DB thật.
- `tools/make_report_figures.py`: tái tạo biểu đồ đơn sắc từ CSV trong `results/final/`.
- `docs/`: audit, inventory bằng chứng và hướng dẫn WP8.

## Cài đặt và thứ tự chạy
1. Cài Docker Desktop và Python; kiểm tra các biến môi trường trong `.env.example`. Sao chép thành `.env` và tự đặt mật khẩu/`SECRET_KEY` mới.
2. Cài dependency runtime: `python -m pip install -r requirements.txt`; test/plot: `python -m pip install -r requirements-dev.txt`.
3. Khởi động dịch vụ: `docker compose up -d`. Chỉ dùng `docker compose down -v` khi chủ động chấp nhận xóa volume và dữ liệu lab.
4. Tạo user demo và dữ liệu/embedding theo các script hiện có trong `scripts/` và `app/generate_embeddings.py`. Một số thực nghiệm cần PostgreSQL, Ollama và model `nomic-embed-text`.
5. Chạy kiểm thử: `python -m pytest -q`. Integration tests yêu cầu DB; không có DB thì lỗi kết nối không chứng minh logic ứng dụng sai.
6. Chạy retrieval benchmark sau khi database benchmark đã được seed và embed: `python benchmark_v1/run_retrieval_benchmark.py --variant controlled --dry-run`, sau đó bỏ `--dry-run`; thay `controlled` bằng `baseline` hoặc `hybrid` cho biến thể cần chạy.
7. WP6: `experiments/retrieval_acl/run_retrieval_matrix.py` (ACL matrix; mục báo cáo 4.2). WP7: `experiments/common/run_wp7_with_fixture_tokens.py` và `experiments/prompt_injection/prompt_injection_test.py` (prompt injection; mục 4.4). WP8: `experiments/ablation/run_wp8_ablation.py` và `experiments/export/export_results.py` (ablation/audit; mục 4.5). Answer leakage: `experiments/common/run_public_benchmark_with_fixture_tokens.py` gọi runner trong `experiments/answer_leakage/`; xem caveat ngay dưới.
8. Tái tạo hình: `python tools/make_report_figures.py`. Kiểm tra hình và CSV đầu vào trước khi chèn vào báo cáo.

## Caveat quan trọng trước khi nộp
- `.env` gốc đã bị loại khỏi bản nộp; hãy rotate DB password và `SECRET_KEY` từng có trong ZIP nguồn.
- Source `answer_leakage_test_public_entrypoints.py` không tồn tại trong ZIP nguồn, chỉ còn bytecode Python 3.14. Runner trong thư mục answer leakage là bản tái dựng từ helper 10-case có sẵn, **không tái tạo được kết quả 40-case đã lưu**; không dùng nó để tuyên bố tái lập đầy đủ.
- Không có CSV export cho benchmark quy mô lớn từ DB `baomatdulieu_benchmark`; xem `results/benchmark_v1/README.md`. Không được suy diễn kết quả benchmark này nếu chưa xuất dữ liệu thật.
- Các kết quả audit tổng hợp là số liệu tích lũy DB, không phải số liệu của riêng một lần chạy. Các run cũ nằm trong archive có thể dùng bộ case/DLP khác nhau.
- `app/dlp/` không được tạo vì tài liệu mục tiêu nêu đây là tùy chọn và việc chuyển module có rủi ro import. Các script benchmark được hợp nhất về một runner nhưng cần xác minh runtime với PostgreSQL/Ollama.
- Báo cáo DOCX/PDF không có trong ZIP nguồn hoặc các file báo cáo được cung cấp; xem `docs/report/README.md`.
