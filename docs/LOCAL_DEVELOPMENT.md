# Local Development

This guide describes the local development workflow verified during P1. Run commands from the repository root. P1 does not deploy the application or validate structural engineering results.

## Prerequisites

| Tool | Tested version | Notes |
| --- | --- | --- |
| Python | 3.12.10 | Python 3.11 was unavailable on the test host. Other versions were not tested. |
| pip | 25.0.1 | Supplied in the Python 3.12 virtual environment. |
| Node.js | 24.11.1 | Used for the clean install, Vite, and build. |
| npm | 11.14.1 | The sole supported JavaScript package manager. |

The verified host was Windows with PowerShell 7.6.5. The shell commands below also show a Unix-like virtual environment setup, which was not exercised during P1.

## Install Python dependencies

Create and activate a virtual environment in the repository root. On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python -m pip check
```

On a Unix-like system with Python 3.12 installed:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m pip check
```

Keep the virtual environment active when running the root backend or combined development scripts. They invoke `python` from the active environment. `.venv` is ignored by Git.

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

## Current limits

The Structure Designer request path `/structure/analyze` does not yet match the backend `/api/structure/analyze` route. API contract work belongs to P2. The existing structural calculations and report contents have not been verified by these local smoke tests. Deployment is outside P1 and remains reserved for P12.
