# Render deployment

The root `render.yaml` defines one Docker-based web service. Its multi-stage
Docker build compiles the React/Vite client and packages it with Flask, so the
React UI, Flask session, JSON API, and remaining Jinja pages use one origin.

## Important: this Blueprint is for demos

The Blueprint uses Render's **free** web-service plan and stores SQLite at
`/app/quality_audit.db` on the container's ephemeral filesystem. Data can be
lost whenever Render replaces or restarts the instance, including during
deploys. This includes audit records, user accounts, settings, and audit logs.
Free services can also spin down when idle. Do not use this deployment for
production, confidential, or irreplaceable data.

For operational use, select an appropriate paid Render plan, attach a
persistent disk, set `DATABASE_PATH` to a file under the disk's mount path,
and set up an independent backup/restore process. A persistent disk is not
configured by this free-tier Blueprint.

## Deploy from a Git repository

1. Make sure the repository includes `render.yaml`, `Dockerfile`,
   `.dockerignore`, `requirements.txt`, and `frontend/package-lock.json`.
2. Push the repository to your Git provider and connect it to Render.
3. In the Render Dashboard, choose **New → Blueprint**, select the repository,
   and apply the Blueprint.
4. When prompted, provide unique values for `ADMIN_PASSWORD`,
   `QUALITY_PASSWORD`, and `MANAGER_PASSWORD`. Use long, randomly generated
   passwords and store them in a password manager. The Blueprint does not
   contain default production passwords.
5. Wait for the Docker build and the `/healthz` health check to pass.
6. Open the Render service URL. Sign in at `/login` using the `qaadmin`
   username and the `ADMIN_PASSWORD` you configured.

Render generates `APP_SECRET_KEY`; the service enables secure session cookies
for HTTPS. Do not put secrets in `render.yaml`, `Dockerfile`, or committed
`.env` files.

## What the deployment runs

- **Build:** Docker installs locked frontend dependencies with `npm ci`,
  runs the TypeScript/Vite production build, then installs Python dependencies.
- **Startup:** `scripts/prestart.py` initializes and migrates the configured
  SQLite database before Gunicorn starts.
- **React:** Flask serves the built application at `/`, `/login`, and the
  migrated admin routes. It serves Vite assets from `/assets/`, `/css/`, and
  `/favicon.svg`.
- **Legacy workflows:** routes not yet migrated remain available through
  Flask/Jinja at their existing URLs.
- **Health:** `GET /healthz` returns `{"status":"ok"}` for Render's health
  check.
- **Workers:** one Gunicorn worker is configured to avoid unnecessary SQLite
  write contention on a small demo instance.

## After deploy

Check these paths on the service URL:

| Check | Expected result |
|---|---|
| `/healthz` | HTTP 200 with a JSON `status` of `ok` |
| `/login` | React sign-in page and its CSS/JavaScript load |
| `/` without a session | Redirect to sign-in |
| Sign-in with configured admin credentials | React dashboard loads from live API data |
| `/admin/settings` as admin | React settings page loads and saves through the API |
| An unmigrated path such as `/warnings` | Existing Flask/Jinja page remains available |

Use Render's deploy logs if the image build, database startup, or health check
fails. A new empty production database requires all three account password
environment variables; startup intentionally fails instead of seeding
production with the local demo passwords.

## Deploying updates

Render deploys commits pushed to the service's configured branch. Verify the
local checks before pushing:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
Set-Location frontend
npm ci
npm run lint
npm run build
```

In the deployed free-tier app, treat every redeploy as a potential database
reset. Export or otherwise preserve anything you need before deploying. Local
SQLite backups are not a substitute for testing the production restore path.

## Rollback and migration note

Render can redeploy a previous successful commit, but rollback does not restore
data from an ephemeral filesystem. Before moving a demo to persistent
production storage, plan and verify the database copy, mount path, file
permissions, backup schedule, and restore procedure. The current schema uses
SQLite; do not scale this single-instance deployment to multiple app
instances sharing writes without first migrating to a database designed for
that deployment model.
