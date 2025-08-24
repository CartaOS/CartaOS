#!/usr/bin/env bash
# Unified runner with end-of-run summary. Does not exit on first failure; aggregates results.
set -uo pipefail

# CartaOS: Run all tests, linters, type checks, and formatters across the monorepo.
# Usage:
#   scripts/run_all.sh                   # check-only (CI style)
#   scripts/run_all.sh --fix             # auto-fix formatting where possible, then run checks/tests
#   scripts/run_all.sh test:cov:safe     # backend pytest with coverage in safe mode
#
# Env toggles:
#   SKIP_E2E=1       # skip Playwright E2E tests
#   SKIP_PERF=1      # skip Lighthouse/perf checks
#   RUST_FEATURES=.. # pass features to cargo (optional)

# Handle special subcommand for convenience
if [[ "${1:-}" == "test:cov:safe" ]]; then
  ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
  BACKEND_DIR="$ROOT_DIR/backend"
  echo "Running backend pytest with coverage (safe mode)"
  (
    cd "$BACKEND_DIR"
    CARTAOS_COVERAGE_SAFE=1 poetry run python -m pytest -W error \
      --cov --cov-report=term-missing \
      --cov-report=xml:coverage.xml \
      --junitxml=pytest-junit.xml -q -s
  )
  exit $?
fi

MODE=check
if [[ "${1:-}" == "--fix" ]]; then
  MODE=fix
fi

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
RUST_DIR="$ROOT_DIR/src-tauri"

section() { echo -e "\n\033[1;34m==> $1\033[0m"; }

# --- Helpers ---
FAILURES=()
LOG_DIR="${ROOT_DIR}/.run-logs"
mkdir -p "$LOG_DIR"

run_step() {
  local title="$1"; shift
  local cwd="$1"; shift
  local cmd="$1"; shift
  local logfile="$LOG_DIR/$(echo "$title" | tr ' /:' '___').log"
  echo -e "\033[1;36m[RUN] $title\033[0m"
  (
    cd "$cwd"
    # Use bash -lc to allow complex commands
    bash -lc "$cmd" 2>&1 | tee "$logfile"
  )
  local status=${PIPESTATUS[0]}
  if [[ $status -ne 0 ]]; then
    echo -e "\033[31m[FAIL] $title (exit $status)\033[0m"
    FAILURES+=("$title|$logfile|$status")
  else
    echo -e "\033[32m[OK]   $title\033[0m"
  fi
}

print_hint() {
  local title="$1"; local logfile="$2";
  case "$title" in
    Frontend:*Prettier*|Frontend:*lint*)
      echo "- Hint: In frontend/, run: npm run format (or: npm run lint -- --fix)" ;;
    Frontend:*types*)
      echo "- Hint: Fix Svelte/TS errors shown above. Run locally: npm run check" ;;
    Frontend:*unit\ tests*)
      echo "- Hint: Investigate Vitest failures. Re-run: npm run test:run -- --reporter=verbose" ;;
    Frontend:*E2E*)
      echo "- Hint: Check Playwright report. Re-run: npm run e2e and open e2e-artifacts/report" ;;
    Frontend:*Perf*)
      echo "- Hint: Check Lighthouse report. Re-run: npm run perf or perf:e2e" ;;
    Backend:*black*|Backend:*isort*)
      echo "- Hint: In backend/, auto-fix: poetry run black . && poetry run isort ." ;;
    Backend:*mypy*)
      echo "- Hint: Fix typing errors in files listed. Re-run: poetry run mypy cartaos" ;;
    Backend:*pytest*)
      echo "- Hint: Inspect failing tests. Re-run: poetry run pytest -q" ;;
    Rust:*fmt*)
      echo "- Hint: In src-tauri/, auto-fix: cargo fmt --all" ;;
    Rust:*clippy*)
      echo "- Hint: Fix warnings. Re-run: cargo clippy --all-targets --all-features -- -D warnings" ;;
    Rust:*tests*)
      echo "- Hint: Inspect failing tests. Re-run: cargo test --all-features" ;;
    *)
      echo "- Hint: See log above: $logfile" ;;
  esac
}

# ---------- Frontend ----------
section "Frontend: ${MODE} + lint + types + unit tests${SKIP_E2E:+ (E2E skipped)}"
if [[ "$MODE" == "fix" ]]; then
  run_step "Frontend: Prettier format" "$FRONTEND_DIR" "npm run -s format"
else
  run_step "Frontend: Prettier + ESLint (lint)" "$FRONTEND_DIR" "npm run -s lint"
fi
run_step "Frontend: Svelte type check" "$FRONTEND_DIR" "npm run -s check"
run_step "Frontend: unit tests (Vitest)" "$FRONTEND_DIR" "npm run -s test:run"
if [[ -z "${SKIP_E2E:-}" ]]; then
  run_step "Frontend: E2E (Playwright)" "$FRONTEND_DIR" "npm run -s e2e"
else
  echo "Skipping Playwright E2E (SKIP_E2E=1)"
fi
if [[ -z "${SKIP_PERF:-}" ]]; then
  run_step "Frontend: Perf checks (Lighthouse/E2E)" "$FRONTEND_DIR" "npm run -s perf:e2e"
else
  echo "Skipping Perf checks (SKIP_PERF=1)"
fi

# ---------- Backend (Python) ----------
section "Backend: ${MODE} + mypy + pytest"
if [[ "$MODE" == "fix" ]]; then
  run_step "Backend: black (format)" "$BACKEND_DIR" "poetry run black ."
  run_step "Backend: isort (format)" "$BACKEND_DIR" "poetry run isort ."
else
  run_step "Backend: black --check" "$BACKEND_DIR" "poetry run black --check ."
  run_step "Backend: isort --check-only" "$BACKEND_DIR" "poetry run isort --check-only ."
fi
run_step "Backend: mypy" "$BACKEND_DIR" "poetry run mypy cartaos"
run_step "Backend: pytest" "$BACKEND_DIR" "poetry run pytest -q"

# ---------- Rust (Tauri) ----------
section "Rust: ${MODE} + clippy -D warnings + tests"
if [[ "$MODE" == "fix" ]]; then
  run_step "Rust: cargo fmt (format)" "$RUST_DIR" "cargo fmt --all"
else
  run_step "Rust: cargo fmt --check" "$RUST_DIR" "cargo fmt --all -- --check"
fi
run_step "Rust: cargo clippy -D warnings" "$RUST_DIR" "cargo clippy --all-targets --all-features ${RUST_FEATURES:+--features \"$RUST_FEATURES\"} -- -D warnings"
run_step "Rust: cargo test" "$RUST_DIR" "cargo test --all-features ${RUST_FEATURES:+--features \"$RUST_FEATURES\"}"

# ---------- Summary ----------
echo -e "\n\033[1;35m==> Unified Summary\033[0m"
if [[ ${#FAILURES[@]} -eq 0 ]]; then
  echo -e "\033[32mAll checks passed\033[0m"
  echo "Mode: $MODE"
else
  echo -e "\033[31mSome steps failed. See details below.\033[0m"
  for entry in "${FAILURES[@]}"; do
    IFS='|' read -r title logfile status <<<"$entry"
    echo -e "\n• $title"
    echo "  Status: $status"
    echo "  Log: $logfile"
    # Print first few file hints if available
    if grep -E "(would reformat|reformatted) /|\.py:|\.ts:|\.svelte:|\.rs:" -m 5 "$logfile" >/dev/null 2>&1; then
      echo "  Files:"
      grep -E "(would reformat|reformatted) /|\.py:|\.ts:|\.svelte:|\.rs:" -m 5 "$logfile" | sed 's/^/    - /'
    fi
    print_hint "$title" "$logfile"
  done
  # Exit non-zero for CI
  exit 1
fi
