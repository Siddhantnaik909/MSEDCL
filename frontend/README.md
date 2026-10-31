# MSEDCL Quality Audit — React client

This is the separate React + TypeScript UI clone. Sign-in and the operations
dashboard use the Flask session and real SQLite data. Other business workflows
remain in the Flask/Jinja application and are linked from the dashboard while
they are migrated.

## Development

Start the Flask application from the project root:

```powershell
python app.py
```

Then start Vite in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite proxies `/api/v1` to `http://127.0.0.1:5000`; its visual theme is bundled
in `public/css/legacy-theme.css`. The React sign-in is at `/login`; the React
dashboard is at `/`. Set
`VITE_LEGACY_APP_URL` if the Flask server is not at `http://127.0.0.1:5000`.

## Checks

```powershell
npm run build
npm run lint
```

## Boundaries

- Flask remains authoritative for authentication, roles, CSRF, and dashboard data.
- The browser must not store session credentials or authorization decisions.
- Unmigrated workflows continue to use the existing Flask application.
- Production hosting must route `/api/v1` to Flask and serve the frontend build
  for the React routes.
