# Recovery artifact

The original archive contains Python 3.14 bytecode for `answer_leakage_test_public_entrypoints.py`, but not its source. This file is preserved for recovery only; it is not a source-code replacement and has not been used as proof that the benchmark is reproducible. A reconstructed source entrypoint is included under `experiments/answer_leakage/` and explicitly limits itself to the 10 cases defined by the available legacy helper; it does not claim to reproduce the saved 40-case run.
