# P0 Command Baseline

## Scope and environment

Repository: Mohdnkh/structicode. Baseline commit: b3801df62fdf1ba0ce61515e1ec5c29d28cacc32. Working branch: codex/48h-enterprise-remediation. This is a local Windows PowerShell baseline. Node.js 24.11.1, npm 11.14.1, and Python 3.14.0 are available on the host. The Dockerfile declares Python 3.11; its image was not built in P0.

The commands below were run without installing or changing project dependencies. The existing tracked frontend/node_modules and frontend/dist directories remained in place. A failed command is recorded as a baseline result, not repaired here.

## Commands expected by the current manifests

| Purpose | Manifest command | Expected working directory | Observation |
| --- | --- | --- | --- |
| Backend development | npm run backend | Repository root | Delegates to cd backend and a POSIX-style PYTHONPATH assignment. |
| Frontend development | npm run dev | frontend | Delegates to Vite. |
| Combined development | npm run dev | Repository root | Requires root concurrently and wait-on dependencies; there is no root lockfile or installed root node_modules. |
| Frontend build | npm run build | frontend | Delegates to Vite. |
| Root build | npm run build | Repository root | Runs npm install in frontend first; intentionally not executed because P0 forbids dependency alteration. |
| Backend production-style start | npm run start | Repository root | Has the same cd backend / PYTHONPATH structure as the backend development script; not needed after the observed backend script failure. |
| Docker start | Dockerfile CMD | Repository root build context | Starts backend.api.main:app from /app, relying on copied prebuilt frontend/dist. Not executed. |
| Automated tests | None declared | Not applicable | Neither package manifest has a test script; no first-party test files or test configuration were found. |

## Executed baseline checks

| Command | Working directory | Result | Relevant output |
| --- | --- | --- | --- |
| git status --short --branch; git rev-parse HEAD | C:/Users/MOHAMMED/Desktop/structicode-p0 | PASS | Clean clone on main before branching; HEAD b3801df62fdf1ba0ce61515e1ec5c29d28cacc32. |
| git switch -c codex/48h-enterprise-remediation | C:/Users/MOHAMMED/Desktop/structicode-p0 | PASS | Dedicated local branch created from the exact baseline SHA. |
| npm run dev | C:/Users/MOHAMMED/Desktop/structicode-p0 | FAIL | concurrently is not recognized; root dependencies are not installed. |
| npm run backend | C:/Users/MOHAMMED/Desktop/structicode-p0 | FAIL | PYTHONPATH is not recognized as a command by the Windows npm shell. |
| npm run dev | C:/Users/MOHAMMED/Desktop/structicode-p0/frontend | FAIL | Tracked Vite installation imports missing dist/node/chunks/dep-C6uTJdX2.js. |
| npm run build | C:/Users/MOHAMMED/Desktop/structicode-p0/frontend | FAIL | Same missing Vite chunk; no successful build was produced. |
| npm ci --dry-run --ignore-scripts --no-audit --no-fund | C:/Users/MOHAMMED/Desktop/structicode-p0/frontend | FAIL | npm reports package.json and package-lock.json out of sync; multiple optional Rollup platform packages are missing from the lockfile. Dry run did not install dependencies. |
| python -B -c "import backend.api.main" | C:/Users/MOHAMMED/Desktop/structicode-p0 | FAIL | ModuleNotFoundError: No module named 'fpdf' in the host Python environment. The declared requirement was not installed in P0. |
| Python ast.parse over all backend Python source files | C:/Users/MOHAMMED/Desktop/structicode-p0 | PASS | All 36 Python source files parsed; this does not validate runtime imports or calculations. |
| Inline python -B calculation probes | C:/Users/MOHAMMED/Desktop/structicode-p0 | FAILURES REPRODUCED | ACI structure route returned HTTP 500; Eurocode route returned HTTP 500 around an embedded 400; free-support frame raised LinAlgError; unit and verdict defects are detailed in P0_BASELINE_AUDIT.md. |
| git status --porcelain=v1 --untracked-files=all | C:/Users/MOHAMMED/Desktop/structicode-p0 | PASS | Clean after baseline commands and before P0 documentation was added. |

## Verification limits

The backend import check was blocked by a missing host package; it does not establish whether the declared Python dependency set can be installed cleanly. The frontend checks fail before Vite processes application source. The root build and Docker build were not executed because they install dependencies or build artifacts and would exceed the inspection-only intent of this phase. Railway and all hosting operations were not invoked.
