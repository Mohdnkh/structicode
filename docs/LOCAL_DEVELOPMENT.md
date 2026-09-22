# Local Development

This guide describes the reproducible local release-candidate workflow. Run commands from the repository root. P11 acceptance is local only and does not deploy the application or validate structural engineering results.

## Prerequisites

| Tool | Tested version | Notes |
| --- | --- | --- |
| Python | 3.12 | Required acceptance runtime; the recorded host used 3.12.10. |
| pip | 25.0.1 | Supplied in the Python 3.12 virtual environment. |
| Node.js | 20 LTS or newer | The acceptance baseline is Node 20; the recorded host used 24.11.1. |
| npm | Bundled with Node 20+ | The sole supported JavaScript package manager. |

The commands below present a platform-neutral workflow first, followed by Windows PowerShell notes. The verified host was Windows with PowerShell 7.6.5.

## Install Python dependencies

Create and activate a virtual environment in the repository root:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements-dev.txt
python -m pip check
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements-dev.txt
python -m pip check
```

On a Unix-like system with Python 3.12 installed:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip check
```

Keep the virtual environment active when running the root backend or combined development scripts. They invoke `python` from the active environment. `.venv` is ignored by Git.

## Configure local environment and migrate

Use an isolated SQLite URL for acceptance or local experiments. Do not point it at a developer database you need to preserve. Set a dedicated local auth secret of at least 32 bytes:

```sh
export STRUCTICODE_DATABASE_URL=sqlite:///./structicode-local.sqlite3
export STRUCTICODE_AUTH_SECRET=replace-with-a-local-secret-at-least-32-bytes
python -m alembic upgrade head
```

PowerShell equivalents are:

```powershell
$env:STRUCTICODE_DATABASE_URL = "sqlite:///./structicode-local.sqlite3"
$env:STRUCTICODE_AUTH_SECRET = "replace-with-a-local-secret-at-least-32-bytes"
python -m alembic upgrade head
```

The auth variables are optional for anonymous analysis but required for registration, login, and project persistence.

## Install JavaScript dependencies

From the repository root:

```sh
npm ci
```

The root `package-lock.json` covers the root package and the `frontend` npm workspace. Do not run Yarn or install separately inside `frontend`.

## Run both services

After activating `.venv` and running `npm ci`:

```sh
npm run dev
```

This starts FastAPI at `http://127.0.0.1:8000` and Vite at `http://localhost:5173`. Stop the command with Ctrl+C. Vite starts independently while the backend is still starting.

## Run one service

With `.venv` active, start only the backend:

```sh
npm run backend
```

Start only Vite in another terminal:

```sh
npm run frontend
```

The backend can import and serve `/health` without a `frontend/dist` directory. When a valid build exists, it can also serve that build and its assets locally. The frontend development server does not require `dist`.

## Verify process health and local transport

With both services running:

```sh
curl http://127.0.0.1:8000/health
curl http://localhost:5173/health
```

Both should return `{"status":"ok"}`. In PowerShell, `Invoke-RestMethod` can be used for the same URLs. The Vite development proxy forwards `/api`, `/analyze`, `/generate-pdf`, and `/health` to FastAPI at `127.0.0.1:8000`. The health endpoint confirms process availability only; it does not validate calculations, database access, or engineering readiness.

For a backend import check from the repository root:

```sh
npm run verify:backend
```

## Build the frontend

After `npm ci`:

```sh
npm run build
```

The build writes to `frontend/dist`. Installing dependencies and building are separate commands. `dist`, `node_modules`, `.venv`, Python bytecode, and generated reports are ignored by Git.

## Tests and acceptance checks

```sh
python -m pytest backend/tests -q
node --test frontend/tests/*.test.mjs
npm run build
npm run verify:backend
```

The Structure Designer and Analyzer use the versioned `/api/v1` analysis routes through the shared frontend client. The Structure Designer supports node creation, member connection, support editing, and minimal model controls; backend validation remains authoritative for stability and complexity, and slab transfer is unavailable. See [API_CONTRACTS.md](API_CONTRACTS.md) and [UNIT_SYSTEM.md](UNIT_SYSTEM.md) for request units and trust semantics. The tests verify transport and normalization, not structural engineering accuracy. The primary report path is `GET /api/v1/reports/{run_id}.pdf`; `POST /generate-pdf` remains legacy compatibility only. Deployment is reserved for P12.
