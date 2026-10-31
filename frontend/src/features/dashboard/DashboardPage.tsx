import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { ApiError, requestJson } from '../../lib/api/client'
import type { SessionUser } from '../auth/types'
import type {
  AdvisorSummary,
  DashboardCharts,
  DashboardData,
  DashboardFilters,
} from './types'

const LEGACY_APP_URL =
  import.meta.env.VITE_LEGACY_APP_URL ??
  (import.meta.env.DEV ? 'http://127.0.0.1:5000' : window.location.origin)

const EMPTY_FILTERS: DashboardFilters = {
  department: 'All',
  start: '',
  end: '',
  auditor: '',
  advisor_q: '',
  score_bracket: 'All',
  fatal_status: 'All',
}

function filterFromUrl(): DashboardFilters {
  const params = new URLSearchParams(window.location.search)
  return {
    department: params.get('department') || 'All',
    start: params.get('start') || '',
    end: params.get('end') || '',
    auditor: params.get('auditor') || '',
    advisor_q: params.get('advisor_q') || '',
    score_bracket: params.get('score_bracket') || 'All',
    fatal_status: params.get('fatal_status') || 'All',
  }
}

function makeSearch(filters: DashboardFilters) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value && value !== 'All') params.set(key, value)
  })
  return params.toString()
}

function countText(value: number) {
  return new Intl.NumberFormat('en-IN').format(value)
}

function RingChart({
  values,
  colors,
  total,
  label,
}: {
  values: number[]
  colors: string[]
  total: number
  label: string
}) {
  const radius = 39
  const circumference = Math.PI * radius * 2
  let offset = 0
  const positiveTotal = values.reduce((sum, value) => sum + value, 0)

  return (
    <div className="ref-donut-canvas-box">
      <svg viewBox="0 0 100 100" role="img" aria-label={`${label}: ${countText(total)}`}>
        <circle cx="50" cy="50" r={radius} fill="none" stroke="var(--border-light)" strokeWidth="12" />
        {positiveTotal > 0 && values.map((value, index) => {
          const length = (value / positiveTotal) * circumference
          const segment = (
            <circle
              key={`${colors[index]}-${index}`}
              cx="50"
              cy="50"
              r={radius}
              fill="none"
              stroke={colors[index]}
              strokeWidth="12"
              strokeDasharray={`${length} ${circumference - length}`}
              strokeDashoffset={-offset}
              transform="rotate(-90 50 50)"
            />
          )
          offset += length
          return segment
        })}
      </svg>
      <div className="ref-donut-center-text">
        <strong>{countText(total)}</strong>
        <small>{label}</small>
      </div>
    </div>
  )
}

function ChartLegend({
  items,
}: {
  items: Array<{ label: string; value: number; color: string; percentage?: number }>
}) {
  return (
    <div className="ref-chart-legend-list">
      {items.map((item) => (
        <div className="ref-chart-legend-item" key={item.label}>
          <span>
            <span className="ref-legend-bullet" style={{ background: item.color }} />
            {item.label}
          </span>
          <span>
            <strong>{countText(item.value)}</strong>
            {item.percentage !== undefined && (
              <> &nbsp;<small>{Math.round(item.percentage)}%</small></>
            )}
          </span>
        </div>
      ))}
    </div>
  )
}

function SummaryLineChart({ chart }: { chart: DashboardCharts }) {
  const width = 360
  const height = 145
  const allValues = [...chart.inbound_by_date, ...chart.outbound_by_date]
  const maxValue = Math.max(1, ...allValues)
  const x = (index: number) =>
    chart.dates.length < 2 ? width / 2 : 12 + (index * (width - 24)) / (chart.dates.length - 1)
  const y = (value: number) => height - 12 - (value / maxValue) * (height - 28)
  const points = (values: number[]) =>
    values.map((value, index) => `${x(index)},${y(value)}`).join(' ')

  return (
    <div className="react-chart-plot">
      {chart.dates.length ? (
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Inbound and outbound audits over time">
          {[0, 1, 2, 3].map((line) => (
            <line key={line} x1="0" x2={width} y1={16 + line * 35} y2={16 + line * 35} className="chart-grid-line" />
          ))}
          <polyline points={points(chart.inbound_by_date)} className="chart-line-inbound" />
          <polyline points={points(chart.outbound_by_date)} className="chart-line-outbound" />
          {chart.dates.map((date, index) => (
            <text key={date} x={x(index)} y={height - 1} textAnchor="middle" className="chart-date-label">
              {date.slice(5)}
            </text>
          ))}
        </svg>
      ) : (
        <p className="chart-empty">No dated audit records match these filters.</p>
      )}
    </div>
  )
}

function MetricCard({
  href,
  tone,
  icon,
  title,
  value,
  subtitle,
}: {
  href: string
  tone: string
  icon: string
  title: string
  value: string | number
  subtitle: string
}) {
  return (
    <a className={`ref-kpi-card ${tone}`} href={`${LEGACY_APP_URL}${href}`}>
      <div>
        <div className="ref-kpi-header">
          <span className={`ref-kpi-icon ${tone}`} aria-hidden="true">{icon}</span>
          <span className="ref-kpi-title">{title}</span>
        </div>
        <div className="ref-kpi-value">{typeof value === 'number' ? countText(value) : value}</div>
      </div>
      <div className="ref-kpi-sub">{subtitle}</div>
    </a>
  )
}

function AdvisorTable({
  rows,
  user,
}: {
  rows: AdvisorSummary[]
  user: SessionUser
}) {
  const [query, setQuery] = useState('')
  const visibleRows = useMemo(() => {
    const search = query.trim().toLowerCase()
    if (!search) return rows
    return rows.filter((row) =>
      [row.advisor_name, row.advisor_id ?? '', row.department]
        .some((value) => value.toLowerCase().includes(search)),
    )
  }, [rows, query])
  const canIssuePip = user.role !== 'viewer' && user.role !== 'advisor'

  return (
    <section className="card dashboard-advisor-register">
      <div className="card-header">
        <div>
          <h2 className="card-title">Advisor-wise Quality Summary ({rows.length} Advisors)</h2>
          <p className="card-subtitle">Quality scores, fatal calls, and coaching triggers</p>
        </div>
        <div className="action-buttons">
          <input
            type="search"
            className="ref-input-control advisor-filter-input"
            placeholder="Filter advisors…"
            aria-label="Filter advisors"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <a href={`${LEGACY_APP_URL}/export-center`} className="btn btn-secondary btn-sm">Export Detailed Data</a>
        </div>
      </div>
      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>Employee ID</th><th>Advisor Name</th><th>Department</th>
              <th>Audited Calls</th><th>Avg Quality Score</th><th>Fatal Errors</th>
              <th>Low (&lt;80%)</th><th>Average (80–90%)</th><th>Good (&gt;90%)</th>
              <th>Target Compliance</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.length ? visibleRows.map((row) => {
              const status = row.avg_score >= 90 && row.fatals === 0
                ? 'Benchmark'
                : row.fatals > 0 ? 'Fatal Alert' : 'Under Target'
              const statusClass = status === 'Benchmark' ? 'badge-success' : row.fatals > 0 ? 'badge-danger' : 'badge-warning'
              const advisorKey = row.advisor_id || row.advisor_name
              return (
                <tr key={`${row.advisor_id}-${row.department}-${row.advisor_name}`}>
                  <td><span className="badge badge-neutral">{row.advisor_id || '—'}</span></td>
                  <td><strong>{row.advisor_name}</strong></td>
                  <td><span className="badge badge-neutral">{row.department}</span></td>
                  <td><strong>{countText(row.calls)}</strong></td>
                  <td><strong className={row.avg_score < 80 ? 'score-low' : row.avg_score >= 90 ? 'score-good' : 'score-average'}>{row.avg_score}%</strong></td>
                  <td><span className={row.fatals > 0 ? 'badge badge-danger' : 'badge badge-neutral'}>{row.fatals > 0 ? `⚠ ${row.fatals}` : '0'}</span></td>
                  <td><span className={row.low_calls > 0 ? 'badge badge-warning' : ''}>{row.low_calls}</span></td>
                  <td>{row.mid_calls}</td>
                  <td><span className="badge badge-success">{row.good_calls}</span></td>
                  <td><span className={`badge ${statusClass}`}>{status}</span></td>
                  <td>
                    <div className="action-buttons">
                      <a className="btn btn-secondary btn-sm" href={`${LEGACY_APP_URL}/advisor-search?emp_id=${encodeURIComponent(advisorKey)}`}>Inspect</a>
                      {canIssuePip && (row.fatals > 0 || row.low_calls > 0 || row.avg_score < 90) && (
                        <a className="btn btn-primary btn-sm" href={`${LEGACY_APP_URL}/warnings`}>PIP</a>
                      )}
                    </div>
                  </td>
                </tr>
              )
            }) : (
              <tr><td colSpan={11} className="dashboard-empty-row">
                {rows.length ? 'No advisor records match your search.' : 'No advisor records match these filters.'}
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function DashboardContent({
  data,
  user,
  onApplyFilters,
}: {
  data: DashboardData
  user: SessionUser
  onApplyFilters: (filters: DashboardFilters) => void
}) {
  const { metrics, chart_data: chart, sync_status: sync } = data
  const total = metrics.total_audits
  const scoreItems = [
    { label: 'Good (>90%)', value: metrics.good_score_count, color: '#10b981' },
    { label: 'Average (80–90%)', value: metrics.avg_score_count, color: '#0284c7' },
    { label: 'Low (<80%)', value: metrics.low_score_count, color: '#f59e0b' },
    { label: 'Fatal Errors', value: metrics.fatal_count, color: '#ef4444' },
  ]
  const quickLinks = [
    ['📄', 'View Reports', '/score-reports'],
    ['🔍', 'Search Advisor', '/advisor-search'],
    ['🛡️', 'Manage Warnings & PIP', '/warnings'],
    ['📥', 'Export Data', '/export-center'],
  ]

  return (
    <>
      <section className="dashboard-intro" aria-labelledby="dashboardIntroTitle">
        <div>
          <h2 id="dashboardIntroTitle">Quality audit overview</h2>
          <p>Monitor call outcomes, advisor performance, and actions that need attention.</p>
        </div>
      </section>

      <form
        className="ref-filter-container"
        onSubmit={(event: FormEvent<HTMLFormElement>) => {
          event.preventDefault()
          const form = new FormData(event.currentTarget)
          onApplyFilters({
            ...data.filters,
            department: String(form.get('department') || 'All'),
            start: String(form.get('start') || ''),
            end: String(form.get('end') || ''),
            auditor: String(form.get('auditor') || ''),
          })
        }}
        id="refFilterForm"
        key={makeSearch(data.filters)}
      >
        <div className="ref-filter-grid">
          <label className="ref-filter-item">
            <span className="ref-filter-label"><span className="icon-tag blue">🏢</span>Department</span>
            <select name="department" className="ref-input-control" defaultValue={data.filters.department}>
              <option value="All">All Departments</option>
              <option value="Inbound">Inbound Only</option>
              <option value="Outbound">Outbound Only</option>
            </select>
          </label>
          <label className="ref-filter-item">
            <span className="ref-filter-label"><span className="icon-tag blue">📅</span>Start Date</span>
            <input type="date" name="start" defaultValue={data.filters.start} className="ref-input-control" />
          </label>
          <label className="ref-filter-item">
            <span className="ref-filter-label"><span className="icon-tag blue">📅</span>End Date</span>
            <input type="date" name="end" defaultValue={data.filters.end} className="ref-input-control" />
          </label>
          <label className="ref-filter-item">
            <span className="ref-filter-label"><span className="icon-tag cyan">👤</span>Auditor Filter</span>
            <select name="auditor" className="ref-input-control" defaultValue={data.filters.auditor}>
              <option value="">All Evaluators</option>
              {data.auditors_list.map((auditor) => <option value={auditor} key={auditor}>{auditor}</option>)}
            </select>
          </label>
          <div><button type="submit" className="btn-filter-apply"><span>⚡</span> Apply Filters</button></div>
          <div><button
            type="button"
            className="btn-filter-reset"
            onClick={() => onApplyFilters(EMPTY_FILTERS)}
          >↻ Reset</button></div>
        </div>
      </form>

      <div className="ref-kpi-row-1">
        <MetricCard href="/audits/Inbound" tone="blue" icon="📞" title="Audited calls" value={metrics.total_audits} subtitle={`Inbound: ${countText(metrics.inbound_count)} | Outbound: ${countText(metrics.outbound_count)}`} />
        <MetricCard href="/fatal-calls" tone="red" icon="⚠️" title="Fatal call errors" value={metrics.fatal_count} subtitle={`${metrics.fatal_rate.toFixed(1)}% of audited interactions`} />
        <MetricCard href="/score-reports" tone="amber" icon="⏱️" title="Low score (<80%)" value={metrics.low_score_count} subtitle="Requires active coaching" />
        <MetricCard href="/score-reports" tone="blue" icon="⭐" title="Average band (80–90%)" value={metrics.avg_score_count} subtitle="Acceptable quality band" />
        <MetricCard href="/score-reports" tone="green" icon="👍" title="High-scoring calls (>90%)" value={metrics.good_score_count} subtitle="Benchmark performers" />
      </div>

      <div className="ref-kpi-row-2">
        <div className="ref-kpi-card purple">
          <div><div className="ref-kpi-header"><span className="ref-kpi-icon purple">★</span><span className="ref-kpi-title">Average quality score</span></div><div className="ref-kpi-value">{metrics.overall_avg}%</div></div>
          <div className="ref-kpi-sub">Aggregated weighted quality</div>
        </div>
        <MetricCard href="/warnings" tone="cyan" icon="⚠️" title="Warnings and PIPs" value={metrics.total_warnings} subtitle={`Open: ${metrics.open_warnings} | PIPs: ${metrics.active_pips}`} />
        <div className="ref-banner-card">
          <div className="ref-banner-info">
            <span className="ref-banner-calendar-icon" aria-hidden="true">▦</span>
            <div>
              <span className="sync-label">Last Updated</span>
              <strong className="sync-timestamp">{sync.display_date}<span>|</span>{sync.display_time}</strong>
              <div className="live-status"><span />Live Data <small>({sync.last_sync_file})</small></div>
            </div>
          </div>
          <div className="ref-banner-art hide-mobile" aria-hidden="true">
            <svg width="240" height="82" viewBox="0 0 240 82" fill="none">
              <circle cx="205" cy="36" r="26" fill="#f59e0b" fillOpacity=".18" />
              <path d="M70 72V52H85V72M85 72V42H102V72M102 72V56H118V72M118 72V46H136V72M136 72V58H154V72M154 72V40H175V72" stroke="#60a5fa" strokeOpacity=".4" strokeWidth="2" />
              <path d="M0 66C50 66 90 75 160 63C195 57 215 62 240 64V82H0V66Z" fill="#2563eb" fillOpacity=".7" />
              <path d="M0 32Q95 52 185 24M0 40Q100 60 185 36" stroke="#38bdf8" strokeWidth="1.2" strokeDasharray="3 3" />
              <g stroke="#1d4ed8" strokeWidth="2" strokeLinejoin="round">
                <path d="M185 10L168 76M185 10L202 76M158 24H212M162 38H208M166 54H204M172 24L198 38M198 24L172 38M170 38L200 54M200 38L170 54M168 54L202 76M202 54L168 76" />
              </g>
              <circle cx="185" cy="9" r="2.5" fill="#ef4444" />
            </svg>
          </div>
        </div>
      </div>

      <div className="ref-charts-row">
        <section className="ref-chart-card">
          <header className="ref-chart-header"><h3 className="ref-chart-title">📊 Score Category Distribution</h3><span className="ref-chart-subtitle">Total Audited: <strong>{countText(total)}</strong></span></header>
          <div className="ref-donut-container">
            <RingChart values={scoreItems.map((item) => item.value)} colors={scoreItems.map((item) => item.color)} total={total} label="Total Calls" />
            <ChartLegend items={scoreItems.map((item) => ({ ...item, percentage: item.value / Math.max(1, total) * 100 }))} />
          </div>
        </section>
        <section className="ref-chart-card">
          <header className="ref-chart-header"><h3 className="ref-chart-title">👥 Fatal vs Non-Fatal Ratio</h3></header>
          <div className="ref-donut-container">
            <RingChart values={[metrics.fatal_count, chart.non_fatal_count]} colors={['#ef4444', '#3b82f6']} total={total} label="Total Calls" />
            <ChartLegend items={[
              { label: 'Fatal Calls', value: metrics.fatal_count, color: '#ef4444', percentage: metrics.fatal_rate },
              { label: 'Non-Fatal Calls', value: chart.non_fatal_count, color: '#3b82f6', percentage: 100 - metrics.fatal_rate },
            ]} />
          </div>
        </section>
        <section className="ref-chart-card">
          <header className="ref-chart-header"><h3 className="ref-chart-title">📞 Inbound vs Outbound Audits</h3></header>
          <div className="chart-inline-legend"><span><i className="ref-legend-bullet inbound-bullet" />Inbound</span><span><i className="ref-legend-bullet outbound-bullet" />Outbound</span></div>
          <SummaryLineChart chart={chart} />
        </section>
      </div>

      <div className="ref-charts-row secondary-charts-row">
        <section className="ref-chart-card">
          <header className="ref-chart-header"><h3 className="ref-chart-title">📋 Auditor Evaluation Activity</h3><span className="ref-chart-subtitle">Auditors: <strong>{data.auditors_list.length}</strong></span></header>
          {chart.auditor_names.length ? chart.auditor_names.map((name, index) => (
            <div className="dashboard-bar-row" key={name}><span title={name}>{name}</span><div><i style={{ width: `${Math.min(100, chart.auditor_counts[index] / Math.max(1, ...chart.auditor_counts) * 100)}%` }} /></div><strong>{countText(chart.auditor_counts[index])}</strong></div>
          )) : <p className="chart-empty">No auditor evaluations match these filters.</p>}
        </section>
        <section className="ref-chart-card">
          <header className="ref-chart-header"><h3 className="ref-chart-title">🏆 Top Advisor Quality Scores</h3><span className="ref-chart-subtitle">Top performers</span></header>
          {chart.top_advisors.length ? chart.top_advisors.map((name, index) => (
            <div className="dashboard-bar-row score-bar-row" key={`${name}-${index}`}><span title={name}>{name}</span><div><i style={{ width: `${Math.max(0, Math.min(100, chart.top_scores[index] ?? 0))}%` }} /></div><strong>{chart.top_scores[index]}%</strong></div>
          )) : <p className="chart-empty">No advisor scores match these filters.</p>}
        </section>
        <section className="ref-chart-card">
          <header className="ref-chart-header"><h3 className="ref-chart-title">🛡️ Warning &amp; PIP Action Status</h3><span className="ref-chart-subtitle">Total: <strong>{countText(metrics.total_warnings)}</strong></span></header>
          <div className="ref-donut-container">
            <RingChart
              values={[chart.open_warnings, chart.in_progress_warnings, chart.closed_warnings]}
              colors={['#ef4444', '#f59e0b', '#10b981']}
              total={metrics.total_warnings}
              label="Actions"
            />
            <ChartLegend items={[
              { label: 'Open', value: chart.open_warnings, color: '#ef4444' },
              { label: 'In Progress', value: chart.in_progress_warnings, color: '#f59e0b' },
              { label: 'Closed', value: chart.closed_warnings, color: '#10b981' },
              { label: 'Active PIPs', value: chart.active_pips, color: '#8b5cf6' },
            ]} />
          </div>
        </section>
      </div>

      <section className="ref-quick-links-bar">
        <h3 className="ref-quick-links-title">⚡ Quick Links</h3>
        <div className="quick-links-list">
          {quickLinks.map(([icon, label, href]) => (
            <a className="ref-quick-link-item" key={label} href={`${LEGACY_APP_URL}${href}`}>
              <span>{icon}</span><span>{label}</span><span aria-hidden="true">›</span>
            </a>
          ))}
        </div>
      </section>

      <AdvisorTable rows={data.advisor_summary} user={user} />
    </>
  )
}

export function DashboardPage({ user }: { user: SessionUser }) {
  const [filters, setFilters] = useState(filterFromUrl)
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    const query = makeSearch(filters)
    requestJson<DashboardData>(`/dashboard${query ? `?${query}` : ''}`)
      .then((response) => {
        if (active) setData(response)
      })
      .catch((requestError: unknown) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          window.location.replace('/login')
          return
        }
        setError(requestError instanceof Error ? requestError.message : 'Dashboard data could not be loaded.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [filters])

  function applyFilters(next: DashboardFilters) {
    setLoading(true)
    setError('')
    setFilters(next)
    const query = makeSearch(next)
    window.history.replaceState(null, '', query ? `/?${query}` : '/')
  }

  return (
    <div className="react-dashboard">
      {error && <div className="alert alert-danger" role="alert">{error}</div>}
      {loading && !data ? (
        <div className="card dashboard-loading" role="status">Loading dashboard data…</div>
      ) : data ? (
        <DashboardContent data={data} user={user} onApplyFilters={applyFilters} />
      ) : (
        <div className="card dashboard-loading">
          <p>Dashboard data is unavailable.</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => {
              setLoading(true)
              setError('')
              setFilters({ ...filters })
            }}
          >Try again</button>
        </div>
      )}
      {loading && data && <p className="dashboard-refreshing" role="status">Updating dashboard…</p>}
    </div>
  )
}
