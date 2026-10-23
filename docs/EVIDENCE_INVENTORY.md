# Evidence inventory

| Evidence | Path | Scope / caveat |
|---|---|---|
| WP6 retrieval ACL matrix | `results/final/wp6_retrieval_matrix_seed4206.csv` | Seed 4206; row-level expected/actual decisions. |
| Answer leakage run | `results/final/answer_leakage_*_20261018T051834Z.*` | Saved historical run; its original public-entrypoint source was absent from the input ZIP. Reconstructed runner is limited to 10 cases and does not reproduce this run. |
| Prompt injection run | `results/final/prompt_injection_*_20261018T072609Z.*` | One final run; earlier repeated runs are archived and are not independent samples. |
| WP8 ablation | `results/final/wp8_ablation_*_20261018T090103Z.*`, `wp8_ablation_metrics_with_ci.csv` | Current selected run; earlier runs retained in `results/archive/`. |
| Audit aggregates | `results/final/wp8_audit_counts.csv`, `wp8_audit_sample_allow_deny_redact.csv` | Cumulative DB counts, not attributed to a single experiment run. |
| Large-scale retrieval benchmark | `results/benchmark_v1/README.md` | No CSV export was present; export from the live benchmark DB before citing results. |
| Figures | `results/figures/` | Regenerated from CSV only where the script's input fields support the figure; check labels before using in final report. |

Do not treat a missing output as zero, and do not combine archived runs that use different cases or DLP versions.
