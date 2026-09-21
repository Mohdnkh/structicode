# P1 Local Build Report

## Scope and starting state

- Repository: `Mohdnkh/structicode` in `C:\Users\MOHAMMED\Desktop\structicode-main`.
- Branch: `codex/48h-enterprise-remediation`.
- Starting commit: `7111a51b0e939ff3d9a03e6622bd7aa9f0316335`.
- Starting working tree: clean; no pre-existing local changes were displaced.
- Scope: local installation, startup, build, smoke tests, and generated-file hygiene. No engineering calculation changes, commit, push, deployment, or P2 work occurred.

## Tested environment

| Component | Tested value |
| --- | --- |
| Operating system | Microsoft Windows NT 10.0.26200.0 |
| Shell | PowerShell 7.6.5 |
| Python | 3.12.10 |
| Virtual environment | `C:\Users\MOHAMMED\Desktop\structicode-main\.venv` |
| pip | 25.0.1 |
| Node.js | 24.11.1 |
| npm | 11.14.1 |

Python 3.11 was not installed on the test host. The existing Python 3.12 runtime was used without installing a system-wide interpreter. `.venv` is repository-local and ignored.

## Package-manager and dependency decisions

- npm is the sole JavaScript package manager. The root package orchestrates the `frontend` npm workspace and owns only `concurrently` for local process orchestration. Frontend runtime and build dependencies remain in `frontend/package.json`.
- `package-lock.json` at the repository root is the authoritative npm lockfile. `frontend/package-lock.json` and `frontend/yarn.lock` were removed after the workspace installation and build were verified.
- The first generated root lock omitted React Router's `@remix-run/router` transitive package. The first build failed with an unresolved import. The dependency was resolved into the root lock, then removed as a direct frontend dependency. A subsequent clean `npm ci` and build passed with it present transitively.
- Five previously unpinned direct Python requirements were pinned: Passlib with bcrypt, python-jose with cryptography, email-validator, psycopg2-binary, and NumPy. Ten newly resolved transitive packages were pinned in the existing requirements file. Previously pinned versions were retained. The legacy UTF-16LE requirements file was converted to UTF-8.
- The initially resolved `bcrypt==5.0.0` caused a Passlib 1.7.4 hash smoke test to fail. `bcrypt==4.0.1` passed hash and verify tests and was pinned. This is dependency compatibility work; no authentication feature was implemented.
- `python -m pip install --force-reinstall -r backend/requirements.txt` passed in `.venv`; `python -m pip check` reported no broken requirements.

## Generated artifacts removed from Git tracking

| Category | Tracked paths removed | Local handling |
| --- | ---: | --- |
| `frontend/node_modules` | 6,798 | Untracked; the installed local tree remains ignored. |
| `frontend/dist` | 13 | Untracked; a fresh local build regenerates ignored output. |
| Python `.pyc` files | 49 | Untracked and ignored. |
| `backend/reports/report.pdf` | 1 | Untracked and ignored as generated report output. |
| FPDF DejaVu `.pkl` caches | 2 | Untracked and narrowly ignored; pyfpdf source confirms these are regenerated font metrics and width caches. |
| Frontend npm and Yarn locks | 2 | Deleted after the root npm workspace lock passed installation and build. |

The `backend/api/utils/DejaVuSans.ttf` font remains tracked. Report generation behavior was not redesigned. Generated files left locally are excluded by `.gitignore`.

## Commands and results

All commands below ran from the canonical repository root unless noted. Python commands used `.venv` or an activated `.venv`.

| Check | Command or request | Result |
| --- | --- | --- |
| Python install | `python -m pip install --force-reinstall -r backend/requirements.txt` | PASS; all pinned packages installed on Python 3.12.10. |
| Python dependency integrity | `python -m pip check` | PASS; no broken requirements. |
| Passlib compatibility | Hash and verify a local test string using `passlib.hash.bcrypt` | PASS with pinned bcrypt 4.0.1; initial bcrypt 5.0.0 failed. |
| Clean JavaScript install | `npm ci --no-audit --no-fund` | PASS after obsolete workspace locks were removed; 130 packages installed. Markers placed in both prior `node_modules` trees were absent afterward, proving they were cleared. |
| Frontend dependency graph | `npm ls --workspaces --depth=0` and full workspace dependency listing | PASS; workspace dependencies resolved through the root lock. |
| Frontend build | `npm run build` | PASS after final clean install; Vite 5.4.19 transformed 511 modules and wrote `frontend/dist/index.html` plus assets. |
| Backend import | `python -B -c "import backend.api.main"` | PASS from repository root, including while `frontend/dist` was temporarily absent. No `PYTHONPATH` override was used. |
| Root import script | `npm run verify:backend` with `.venv` active | PASS. |
| Backend startup | `npm run backend` | PASS; Uvicorn started at `http://127.0.0.1:8000` from repository root. |
| Health endpoint | `GET http://127.0.0.1:8000/health` | HTTP 200, `{"status":"ok"}`. No calculation or external service was invoked. |
| Built static serving | `GET /` and `GET /assets/<built JavaScript>` at the backend origin | HTTP 200 for both when `frontend/dist` existed. |
| Backend without build | `python -B -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000` with `dist` temporarily moved | PASS; `/health` returned HTTP 200 and `/` returned an intentional HTTP 404. The build directory was restored afterward. |
| Frontend development | `npm run frontend` | PASS; Vite started at `http://localhost:5173`; `/` and `/src/main.jsx` returned HTTP 200. |
| Combined development | `npm run dev` with `.venv` active | PASS; both Uvicorn and Vite started without a startup wait dependency. |
| Vite proxy | `GET http://localhost:5173/health` | HTTP 200, `{"status":"ok"}`, forwarded to FastAPI. |
| Existing API transport | `POST http://localhost:5173/analyze` with `{}` | HTTP 422 JSON validation response from FastAPI. This proves routing only; no engineering result was assessed. |
| Process cleanup | Ctrl+C after individual and combined tests; inspect ports and project processes | PASS; ports 8000 and 5173 closed and no project Node/Python process remained. |

The first build attempt after the initial root lock failed because `@remix-run/router` was absent. It was repaired within P1 and the final clean install and build passed. Vite emitted a nonblocking CommonJS API deprecation warning; `concurrently` emitted a Node `util._extend` deprecation warning. No first-party automated test suite exists in this repository.

## Change boundary and deferred work

- `backend/api/main.py` changed only to resolve built frontend paths from its file location, allow startup when `dist` is absent, and expose process-only `/health`. Existing analysis and PDF routes were not redesigned.
- No structural equation, demand/capacity calculation, design-code formula, verdict rule, seismic method, load combination, or solver mathematics was changed.
- **P2:** Normalize API paths, payloads, responses, and units. In particular, Structure Designer still calls `/structure/analyze` while the backend route is `/api/structure/analyze`.
- **P3:** Stabilize the frame solver and its load and stability handling.
- **P4/P5:** Repair and independently verify concrete and steel calculations and design verdicts.
- **P7:** Redesign report trust, traceability, concurrency, and Unicode handling. The generated report artifact was untracked, but the PDF engine was not changed.
- **P8:** Repair incomplete UI workflows and control visibility.
- **P12:** Review Docker and Railway packaging. A clean checkout no longer contains committed `frontend/dist`; the current Dockerfile does not build it, and `.dockerignore` excludes the root lockfile. These deployment files were deliberately left unchanged in P1.

The installation and smoke tests were run on this Windows host. Unix-like operation, Python 3.11, browser interaction beyond HTTP reachability, and engineering correctness remain unverified. P0 remains `PUSHED`; P1 is prepared for independent review; P2-P12 remain `HOLD`.

## Independent Review Rework — Lockfile Reproducibility

The independent reviewer found that the root npm lock lacked `resolved` and `integrity` on many normal registry packages, and that the earlier `npm ci` had not been tested against an empty cache. This rework addresses only that lockfile evidence. It did not change either JavaScript manifest or application source.

- **npm environment:** Node.js 24.11.1 and npm 11.14.1. `npm config get registry` returned `https://registry.npmjs.org/`; `npm config get package-lock` returned `true`; `npm config get omit-lockfile-registry-resolved` returned `false`. No project, frontend, user, or global `.npmrc` file existed at the reported config paths, and no matching `npm_config_*` environment override was present. No global npm configuration was changed.
- **Original defect and cause:** The old root lockfile was version 3 with 129 ordinary registry entries; 72 lacked both `resolved` and `integrity`. Every missing-metadata entry was under `frontend/node_modules/`, including `react` and multiple Babel packages. All 72 corresponding entries in the previously tracked `frontend/package-lock.json` had the same versions **and complete registry metadata**, so that old lock was not itself the source of missing fields. The original P1 root lock was generated while an existing frontend dependency tree was present. The concentrated path pattern, complete old frontend lock, normal npm config, and clean regeneration strongly indicate npm reused local installed-tree data without registry provenance when it created the root lock. The precise internal npm decision for each entry cannot be recovered from the old root lock alone; this is the evidence-backed cause, not a claim that an npm setting disabled metadata.
- **Regeneration:** The generated root and frontend `node_modules` trees were moved out of the repository, and the old root lockfile was retained in a separate temporary folder for comparison. With neither dependency tree present, npm generated a new root lock directly from the unchanged root and frontend manifests using `npm install --package-lock-only --ignore-scripts --no-audit --no-fund --prefer-online --cache <fresh-lock-cache> --omit-lockfile-registry-resolved=false`. The lock was not edited entry by entry. The initial lock cache was empty and located under the Windows system temporary directory, outside the repository.
- **Metadata classification:** Before: 129 ordinary registry entries, 72 missing `resolved`, 72 missing `integrity`, 72 missing both. After: 178 ordinary registry entries, zero missing `resolved`, zero missing `integrity`, zero missing both. Both locks also contained two local workspace records (`""` and `frontend`) and one `node_modules/frontend` workspace link; these correctly do not require registry tarball metadata. No bundled, `file:`, or other non-registry package entries were found. All post-regeneration registry URLs use `https://registry.npmjs.org/`.
- **Version movement:** A fresh resolution of existing semver ranges refreshed 44 previously present package names, added 50 package names (mostly cross-platform optional binaries), and omitted one obsolete package name. Examples include `@radix-ui/react-slot` 1.2.3→1.3.3, `framer-motion` 12.23.12→12.43.0, `i18next` 25.3.2→25.10.10, `react-router-dom` 6.30.1→6.30.6, and Vite 5.4.19→5.4.21. No version was intentionally changed in either manifest; this is the effect of resolving their declared ranges from the registry. The lock now pins those exact versions. Runtime behavior beyond the build and import checks remains a review consideration.
- **Cold-cache install:** A separate unique `ci-cache` directory under `C:\Users\MOHAMMED\AppData\Local\Temp\structicode-p1-lock-rework-de24490a5d1145378e38c9b76b6f7a86` was verified empty immediately before `npm ci`. Both repository `node_modules` paths were absent. `npm ci --no-audit --no-fund --prefer-online --cache <empty-ci-cache>` exited 0 and installed 132 packages in about eight minutes. npm's log showed cache misses and HTTP 200 tarball downloads from the public registry. No install error or dependency warning appeared; npm only noted that a newer npm version was available. Network downloads on this host were slow, including one tarball that took over four minutes.
- **Dependency tree:** `npm ls --depth=0` exited 0 and showed `concurrently@8.2.2` plus the linked frontend workspace and its declared direct dependencies. `npm ls --all --json` exited 0 with zero `problems`; no invalid, extraneous, unmet, or peer dependency problem was reported.
- **Build and backend regression:** `npm run build` exited 0 with Vite 5.4.21, 522 transformed modules, and output in ignored `frontend/dist`. Vite emitted its existing CommonJS Node API deprecation warning. `npm run verify:backend` exited 0 using the existing `.venv`.
- **Remaining limits:** The cold install was verified on this Windows host only. Dependency version movement within declared ranges requires normal review for runtime regressions. The temporary caches and old generated dependency trees were retained outside the repository because automatic approval review rejected a guarded recursive deletion of the temporary folder as blocked by policy, without a more specific reason. They are not Git changes or inputs to the decisive install. No engineering or deployment verification was expanded in this targeted rework.
