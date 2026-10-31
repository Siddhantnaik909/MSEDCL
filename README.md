<div align="center">

# ⚡ Maharashtra State Electricity Distribution Co. Ltd. (MSEDCL)
### Enterprise Quality Audit & Performance Analytics Management Portal

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4.1-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://chartjs.org)
[![Render](https://img.shields.io/badge/Render-Deploy%20Ready-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Status](https://img.shields.io/badge/Quality%20System-Active%20%26%20Protected-success?style=for-the-badge)]()

<br/>

<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Python-Dark.svg" width="48" height="48" alt="Python" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Flask-Dark.svg" width="48" height="48" alt="Flask" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/HTML.svg" width="48" height="48" alt="HTML" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/CSS.svg" width="48" height="48" alt="CSS" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/Javascript.svg" width="48" height="48" alt="JS" />
&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://raw.githubusercontent.com/tandpfun/skill-icons/main/icons/SQLite.svg" width="48" height="48" alt="SQLite" />

<br/>

**A mission-critical Quality Assurance, Contact Center Analytics, Disciplinary Warning/PIP Governance, and Multi-department Audit portal engineered for MSEDCL.**

---

</div>

## 📑 Table of Contents
- [✨ Core Highlights & Features](#-core-highlights--features)
- [📊 Executive Analytics & Visualizations](#-executive-analytics--visualizations)
- [🛡️ Warning & PIP Action Governance](#-warning--pip-action-governance)
- [👥 Role-Based Access Control (RBAC)](#-role-based-access-control-rbac)
- [🚀 Quick Start & Installation (Windows / Linux)](#-quick-start--installation)
- [🌐 Cloud Deployment (Render / Gunicorn)](#-cloud-deployment-render--gunicorn)
- [🧭 Project Guides](#-project-guides)
- [📧 Email Dispatch Configuration](#-email-dispatch-configuration)
- [📥 Automated Report Generation & Exports](#-automated-report-generation--exports)
- [🔐 Security Best Practices](#-security-best-practices)

---

## ✨ Core Highlights & Features

| Capability | Description |
| :--- | :--- |
| **⚡ Live Ingestion & Auditing** | Seamless `.xlsx`, `.xlsm`, and `.csv` audit file ingestion with duplicate hashing & validation. |
| **📅 Real-Time Live Clock & Sync** | Auto-ticking client banner with transmission tower electrical substation art and live sync state. |
| **🏆 360° Advisor Drilldown** | Instant employee history search, coaching flags, fatal alerts, and custom PDF/Excel summaries. |
| **🛡️ Disciplinary Warning & PIPs** | Multi-tier corrective notice generator with draft email transmission and admin deletion control. |
| **🌓 Day / Night Smart Themes** | Dynamic dark/light mode toggle with persistent local preferences and contrast compliance. |
| **📱 100% Mobile & Tablet Responsive** | Modern layout with collapsible sidebar, floating quick-links, and responsive analytics tables. |

---

## 📊 Executive Analytics & Visualizations

The Home Dashboard integrates 6 interactive Chart.js visualizations that auto-adapt to day/night palettes:

```
+---------------------------------------------------------------------------------------+
|                                    MSEDCL QA KPI ROW                                  |
| [ TOTAL AUDITS ]   [ INBOUND ]   [ OUTBOUND ]   [ FATAL CALLS ]   [ AVG SCORE % ]     |
+---------------------------------------------------------------------------------------+
|                                  PRIMARY ANALYTICS ROW                                |
|  [ Score Distribution ]       [ Fatal Ratio Donut ]      [ Inbound vs Outbound Trend] |
|   • Good (>90%)                • Fatal Calls              • Daily Call Volumes        |
|   • Average (80-90%)           • Non-Fatal Calls          • Comparative Trajectory    |
|   • Low (<80%)                                                                        |
+---------------------------------------------------------------------------------------+
|                                 SECONDARY ANALYTICS ROW                               |
|  [ Auditor Activity Bar ]     [ Top Advisor Scores ]     [ Warning & PIP Status ]     |
|   • Evaluations Per QA         • Ranked High Performers   • Open / In Progress        |
|   • Activity Benchmarks        • Score Percentages        • Closed & Active PIPs      |
+---------------------------------------------------------------------------------------+
|                     ADVISOR-WISE QUALITY SUMMARY REGISTER (FILTERABLE)                |
+---------------------------------------------------------------------------------------+
```

---

## 🛡️ Warning & PIP Action Governance

Formal corrective action governance system:
1. **Notice Creation**: Automated draft generation with interaction ID, evaluator remarks, and targeted review dates.
2. **Action Register**:
   - `✉️ Send`: Direct SMTP transmission with full audit trail.
   - `👁️ View`: Expandable drawer showing detailed notice body and advisor response.
   - `💬 Advisor Response`: Direct input form for advisors to submit corrective action plans.
   - `🗑️ Remove`: **Admin-only deletion button** allowing permanent removal of records with confirmation.
3. **Resolution Lifecycle**: *Open* ➔ *In Progress* ➔ *Closed / Resolved*.

---

## 👥 Role-Based Access Control (RBAC)

| Role | Dashboard | Ingestion | Reports & Exports | Issue PIP | Delete PIP | User Management |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Admin** | ✅ Full | ✅ Yes | ✅ All 12 Formats | ✅ Yes | ✅ **Yes** | ✅ Complete |
| **Quality** | ✅ Full | ✅ Yes | ✅ All 12 Formats | ✅ Yes | ❌ No | ❌ View Only |
| **Manager** | ✅ Full | ❌ Read | ✅ View & Export | ✅ Yes | ❌ No | ❌ View Only |
| **Advisor** | 🔒 Own Data | ❌ No | 🔒 Own Performance| 💬 Feedback Only | ❌ No | ❌ No |

---

## 🚀 Quick Start & Installation

### 1. Clone & Set Up Directory
```bash
git clone https://github.com/WeWake2026/MSEDCL.git
cd MSEDCL
```

### 2. Set Up Virtual Environment

**Windows PowerShell:**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Initialize Database & Migrations
```bash
python init_db.py
python migrate_db.py
```

### 4. Run the Application
```bash
python app.py
```
Visit **`http://localhost:5000`** for the Flask application. Local demo
accounts are configured by `ADMIN_USERNAME` / `ADMIN_PASSWORD`,
`QUALITY_USERNAME` / `QUALITY_PASSWORD`, and `MANAGER_USERNAME` /
`MANAGER_PASSWORD` in `.env`. The sample passwords are local-demo-only; Render
rejects them when initializing a hosted database.

### React dashboard and sign-in

The React + TypeScript UI is under `frontend/`. Sign-in and the operations
dashboard use real Flask sessions and SQLite dashboard data. Other workflows
remain on Flask/Jinja during the feature-by-feature migration.

**Windows:** double-click `run.bat` from the project folder, or run this single
command from Command Prompt:

```cmd
run.bat
```

The launcher checks the required runtimes, installs missing dependencies,
initializes the database, and starts Flask and Vite in separate terminal
windows. It opens the React sign-in page at `http://127.0.0.1:5173/login`.
Close both server windows to stop the application. Install Python 3 and
Node.js LTS first if they are not already available.

**Other platforms / manual startup:** run Flask with `python app.py` from the
project root, then run `npm install` and `npm run dev` from `frontend/`.
Vite proxies `/api/v1` to Flask at `http://127.0.0.1:5000` by default. Set
`VITE_API_PROXY_TARGET` if Flask is listening on another local address.

---

## 🌐 Cloud Deployment (Render)

The root `render.yaml` deploys a single Docker web service. Docker builds the
React client and serves it from Flask on the same origin as the session-backed
API. The migrated dashboard and admin pages use React; workflows not yet
migrated continue to use Flask/Jinja.

1. Push the repository to a Git provider connected to Render.
2. In Render, choose **New → Blueprint**, select the repository, and apply the
   root `render.yaml`.
3. Set the prompted `ADMIN_PASSWORD`, `QUALITY_PASSWORD`, and
   `MANAGER_PASSWORD` values in Render. Choose unique passwords; these values
   are only used when the database first seeds its accounts.
4. Wait for the service health check at `/healthz` and open the service URL.
   The React sign-in page is `/login`.

**Free-tier data warning:** this Blueprint intentionally uses Render's free
ephemeral filesystem. The SQLite database (including users, audits, settings,
and audit logs) can be erased when the service is redeployed, restarted, or
replaced. This is suitable only for demos and testing; do not enter production
or sensitive records. For persistent operational use, choose a paid Render
plan, attach a persistent disk, set `DATABASE_PATH` to a file under its mount
path, and configure backups before deployment.

See [Render deployment instructions](./docs/render-deployment.md) for service
configuration, first-deploy checks, upgrades, and persistence guidance.

The container sets `SESSION_COOKIE_SECURE=true` and generates
`APP_SECRET_KEY` through Render. Do not copy real passwords into `render.yaml`,
the Docker image, or committed files.

## 🧭 Project Guides

- [Local development and test instructions](./docs/local-development.md)
- [Current architecture and runtime flow](./docs/CURRENT_ARCHITECTURE.md)
- [Render deployment and data-persistence warning](./docs/render-deployment.md)
- [Project audit and known migration boundaries](./docs/PROJECT_AUDIT.md)

---

## 📧 Email Dispatch Configuration

Configure SMTP in `.env` or through **Admin Settings** (`/admin/settings`):

```ini
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=quality.audit@msedcl.in
SMTP_PASSWORD=YourAppPasswordHere
SMTP_FROM=quality.audit@msedcl.in
```

---

## 📥 Automated Report Generation & Exports

- **Individual Category Reports**: Excel (`.xlsx`) & CSV formats with auto-fitted columns, brand borders, and frozen title headers.
- **Combined Master Workbook**: Multi-sheet workbook assembling Inbound, Outbound, Fatal, and Advisor performance summaries.
- **Bulk ZIP Archive**: One-click download of all 12 operational datasets.

---

## 🔐 Security Best Practices

- **Zero Plain-Text Credentials**: Passwords hashed using PBKDF2 with SHA-256 and unique salts.
- **Strict CSRF & Session Isolation**: Session cookies marked `HttpOnly` and `SameSite=Lax`.
- **SQL Parameterization**: Zero raw query string interpolation to prevent injection attacks.
- **Immutable System Audit Log**: Dedicated security audit records for all user logins, failed attempts, and administrative actions.

---

<div align="center">
<sub>Designed & Maintained for Maharashtra State Electricity Distribution Co. Ltd. (MSEDCL). All rights reserved.</sub>
</div>
