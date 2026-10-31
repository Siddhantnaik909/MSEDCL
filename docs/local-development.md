# Local development

## Requirements

- Python 3.10 or later (Python 3.11 recommended)
- Node.js 22 LTS or later and npm
- Windows, macOS, or Linux

## One-command startup on Windows

From Command Prompt, run:

```cmd
run.bat
```

The launcher creates the Python virtual environment and `.env` when missing,
installs missing dependencies, initializes and migrates SQLite, and opens Flask
and Vite in separate terminal windows. Use the React client at
`http://127.0.0.1:5173/login`; the legacy Flask pages remain at
`http://127.0.0.1:5000`. Close both server windows to stop the application.

## Manual setup

Run these commands from the repository root.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe init_db.py
.\.venv\Scripts\python.exe migrate_db.py
.\.venv\Scripts\python.exe app.py
```

In another terminal:

```powershell
Set-Location frontend
npm ci
npm run dev
```

### macOS / Linux

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python init_db.py
python migrate_db.py
python app.py
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

The React sign-in is at `http://127.0.0.1:5173/login`. Vite proxies `/api/v1`
to Flask at `http://127.0.0.1:5000`. Set `VITE_API_PROXY_TARGET` in
`frontend/.env.local` if Flask uses a different address. The Flask server
continues to serve the unmigrated Jinja workflows.

## Configuration and accounts

Copy `.env.example` to `.env` and set local values as needed. `.env` is ignored
by Git. The local demo account names and initial passwords are read from
`ADMIN_USERNAME` / `ADMIN_PASSWORD`, `QUALITY_USERNAME` / `QUALITY_PASSWORD`,
and `MANAGER_USERNAME` / `MANAGER_PASSWORD`. These credentials are for local
development only. Change them before working with non-demo data.

The application creates `quality_audit.db` in the project root by default.
Set `DATABASE_PATH` to use another database file. If you change a password
environment variable after the account has already been created, it will not
change that account's stored password; use administrator password management
or initialize a fresh local database.

## Validation

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Run from `frontend/`:

```powershell
npm run lint
npm run build
```

## Troubleshooting

| Symptom | Check |
|---|---|
| Python or Node is not found | Install Python 3 and Node.js LTS, then reopen the terminal. |
| Port 5000 or 5173 is occupied | Stop the existing local server or configure a different port and update the Vite proxy. |
| React shows “workspace could not be loaded” | Confirm Flask is running and `/api/v1/auth/me` is reachable through the Vite proxy. |
| Login fails after changing `.env` | Seeded account passwords do not update automatically; use a fresh local database or reset the password as an administrator. |
| Database is locked | Stop duplicate server processes and ensure only one local app instance is writing to the database. |

For production deployment, follow [Render deployment](./render-deployment.md).
