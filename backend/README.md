# CartaOS Backend

## Running backend tests with coverage safely

Some native Python C-extensions (e.g., PyMuPDF) can crash under coverage tracing in certain environments if they are imported during tests. CartaOS mitigates this by:

- Lazy-importing heavy modules in `cartaos/utils/pdf_utils.py`.
- Guarding the PDF triage path in `cartaos/api/server.py` to avoid calling `extract_text()` during tests or when a coverage-safe mode is enabled.

Recommended local commands:

- Fast (no coverage):
```bash
poetry run python -m pytest -W error -q -s
```

- Coverage (safe mode):
```bash
CARTAOS_COVERAGE_SAFE=1 poetry run python -m pytest -W error \
  --cov --cov-report=term-missing \
  --cov-report=xml:coverage.xml \
  --junitxml=pytest-junit.xml -q -s
```

Alternatively, you can use the unified runner shortcut:
```bash
scripts/run_all.sh test:cov:safe
```

Notes:
- CI does not need the `CARTAOS_COVERAGE_SAFE` variable; it remains unchanged.
- The guard also activates under pytest via `PYTEST_CURRENT_TEST`, so full-suite coverage runs are safe locally.
