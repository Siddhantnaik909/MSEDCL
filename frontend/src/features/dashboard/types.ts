export interface DashboardFilters {
  department: string
  start: string
  end: string
  auditor: string
  advisor_q: string
  score_bracket: string
  fatal_status: string
}

export interface DashboardMetrics {
  total_audits: number
  inbound_count: number
  outbound_count: number
  fatal_count: number
  fatal_rate: number
  low_score_count: number
  avg_score_count: number
  good_score_count: number
  overall_avg: number
  total_warnings: number
  open_warnings: number
  active_pips: number
}

export interface DashboardCharts {
  low_scores: number
  mid_scores: number
  good_scores: number
  fatal_count: number
  non_fatal_count: number
  inbound_count: number
  outbound_count: number
  dates: string[]
  inbound_by_date: number[]
  outbound_by_date: number[]
  auditor_names: string[]
  auditor_counts: number[]
  top_advisors: string[]
  top_scores: number[]
  open_warnings: number
  in_progress_warnings: number
  closed_warnings: number
  active_pips: number
}

export interface AdvisorSummary {
  advisor_id: string | null
  advisor_name: string
  department: string
  calls: number
  avg_score: number
  fatals: number
  low_calls: number
  mid_calls: number
  good_calls: number
}

export interface DashboardData {
  metrics: DashboardMetrics
  chart_data: DashboardCharts
  advisor_summary: AdvisorSummary[]
  auditors_list: string[]
  sync_status: {
    display_date: string
    display_time: string
    last_sync_time: string
    last_sync_file: string
    all_time_records: number
    filtered_count: number
    is_filtered: boolean
  }
  filters: DashboardFilters
}
