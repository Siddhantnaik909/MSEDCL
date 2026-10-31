"""Dashboard queries and presentation data."""

from datetime import datetime


def get_dashboard_data(db_factory, filters):
    department = filters.get("department", "All")
    start = filters.get("start", "")
    end = filters.get("end", "")
    auditor = filters.get("auditor", "").strip()
    advisor_query = filters.get("advisor_q", "").strip()
    score_bracket = filters.get("score_bracket", "All")
    fatal_status = filters.get("fatal_status", "All")

    if department not in ("All", "Inbound", "Outbound"):
        department = "All"
    if score_bracket not in ("All", "low", "mid", "good"):
        score_bracket = "All"
    if fatal_status not in ("All", "fatal", "non_fatal"):
        fatal_status = "All"

    where = ["1=1"]
    params = []
    if department in ("Inbound", "Outbound"):
        where.append("department=?")
        params.append(department)
    if start:
        where.append("COALESCE(call_date, evaluation_date) >= ?")
        params.append(start)
    if end:
        where.append("COALESCE(call_date, evaluation_date) <= ?")
        params.append(end)
    if auditor:
        where.append("auditor_name=?")
        params.append(auditor)
    if advisor_query:
        where.append("(advisor_id LIKE ? OR advisor_name LIKE ?)")
        params.extend([f"%{advisor_query}%", f"%{advisor_query}%"])
    if fatal_status == "fatal":
        where.append("is_fatal=1")
    elif fatal_status == "non_fatal":
        where.append("is_fatal=0")
    if score_bracket == "low":
        where.append("quality_score < 80")
    elif score_bracket == "mid":
        where.append("quality_score >= 80 AND quality_score <= 90")
    elif score_bracket == "good":
        where.append("quality_score > 90")

    sql_base = " FROM audits WHERE " + " AND ".join(where)

    with db_factory() as connection:
        last_batch = connection.execute(
            "SELECT uploaded_at, source_file FROM import_batches ORDER BY uploaded_at DESC LIMIT 1"
        ).fetchone()
        all_time_records = connection.execute(
            "SELECT COUNT(*) FROM audits"
        ).fetchone()[0]

        def count(suffix="", count_params=None):
            return connection.execute(
                "SELECT COUNT(*)" + sql_base + suffix,
                params if count_params is None else count_params,
            ).fetchone()[0]

        total_audits = count()
        inbound_count = count(" AND department='Inbound'")
        outbound_count = count(" AND department='Outbound'")
        fatal_count = count(" AND is_fatal=1")
        low_score_count = count(" AND quality_score < 80")
        avg_score_count = count(" AND quality_score >= 80 AND quality_score <= 90")
        good_score_count = count(" AND quality_score > 90")
        overall_avg = connection.execute(
            "SELECT ROUND(AVG(quality_score), 2)" + sql_base,
            params,
        ).fetchone()[0] or 0

        total_warnings = connection.execute(
            "SELECT COUNT(*) FROM warnings"
        ).fetchone()[0]
        open_warnings = connection.execute(
            "SELECT COUNT(*) FROM warnings WHERE status='Open'"
        ).fetchone()[0]
        in_progress_warnings = connection.execute(
            "SELECT COUNT(*) FROM warnings WHERE status='In Progress'"
        ).fetchone()[0]
        closed_warnings = connection.execute(
            "SELECT COUNT(*) FROM warnings WHERE status='Closed'"
        ).fetchone()[0]
        active_pips = connection.execute(
            "SELECT COUNT(*) FROM warnings WHERE warning_type LIKE '%PIP%' AND status != 'Closed'"
        ).fetchone()[0]

        auditors = [
            row[0]
            for row in connection.execute(
                """
                SELECT DISTINCT auditor_name FROM audits
                WHERE auditor_name IS NOT NULL AND auditor_name != ''
                ORDER BY auditor_name
                """
            ).fetchall()
        ]
        auditor_stats = connection.execute(
            """
            SELECT auditor_name, COUNT(*) AS cnt
            """
            + sql_base
            + """
            AND auditor_name IS NOT NULL
            GROUP BY auditor_name ORDER BY cnt DESC LIMIT 10
            """,
            params,
        ).fetchall()
        date_stats = connection.execute(
            """
            SELECT COALESCE(call_date, evaluation_date) AS dt,
                   SUM(CASE WHEN department='Inbound' THEN 1 ELSE 0 END) AS inbound,
                   SUM(CASE WHEN department='Outbound' THEN 1 ELSE 0 END) AS outbound
            """
            + sql_base
            + """
            AND COALESCE(call_date, evaluation_date) IS NOT NULL
            GROUP BY dt ORDER BY dt DESC LIMIT 14
            """,
            params,
        ).fetchall()
        date_stats = list(reversed(date_stats))
        advisor_summary = connection.execute(
            """
            SELECT advisor_id, advisor_name, department, COUNT(*) AS calls,
                   ROUND(AVG(quality_score), 2) AS avg_score,
                   SUM(is_fatal) AS fatals,
                   SUM(CASE WHEN quality_score < 80 THEN 1 ELSE 0 END) AS low_calls,
                   SUM(CASE WHEN quality_score >= 80 AND quality_score <= 90 THEN 1 ELSE 0 END) AS mid_calls,
                   SUM(CASE WHEN quality_score > 90 THEN 1 ELSE 0 END) AS good_calls
            """
            + sql_base
            + """
            GROUP BY COALESCE(advisor_id, advisor_name), department
            ORDER BY fatals DESC, low_calls DESC LIMIT 20
            """,
            params,
        ).fetchall()
        top_advisors = connection.execute(
            """
            SELECT advisor_name, ROUND(AVG(quality_score), 2) AS avg_score, COUNT(*) AS cnt
            """
            + sql_base
            + """
            GROUP BY COALESCE(advisor_id, advisor_name)
            ORDER BY avg_score DESC, cnt DESC LIMIT 8
            """,
            params,
        ).fetchall()

    fatal_rate = fatal_count / max(1, total_audits) * 100
    last_sync_time = last_batch["uploaded_at"] if last_batch else None
    now = datetime.now()
    if last_sync_time and len(last_sync_time) >= 10:
        try:
            parsed = datetime.fromisoformat(last_sync_time.replace("T", " ")[:19])
            display_date = parsed.strftime("%d %b %Y")
            display_time = parsed.strftime("%I:%M %p")
        except ValueError:
            display_date = now.strftime("%d %b %Y")
            display_time = now.strftime("%I:%M %p")
    else:
        display_date = now.strftime("%d %b %Y")
        display_time = now.strftime("%I:%M %p")

    return {
        "metrics": {
            "total_audits": total_audits,
            "inbound_count": inbound_count,
            "outbound_count": outbound_count,
            "fatal_count": fatal_count,
            "fatal_rate": fatal_rate,
            "low_score_count": low_score_count,
            "avg_score_count": avg_score_count,
            "good_score_count": good_score_count,
            "overall_avg": overall_avg,
            "total_warnings": total_warnings,
            "open_warnings": open_warnings,
            "active_pips": active_pips,
        },
        "chart_data": {
            "low_scores": low_score_count,
            "mid_scores": avg_score_count,
            "good_scores": good_score_count,
            "fatal_count": fatal_count,
            "non_fatal_count": max(0, total_audits - fatal_count),
            "inbound_count": inbound_count,
            "outbound_count": outbound_count,
            "dates": [row["dt"] for row in date_stats],
            "inbound_by_date": [row["inbound"] for row in date_stats],
            "outbound_by_date": [row["outbound"] for row in date_stats],
            "auditor_names": [row["auditor_name"] for row in auditor_stats],
            "auditor_counts": [row["cnt"] for row in auditor_stats],
            "top_advisors": [row["advisor_name"] for row in top_advisors],
            "top_scores": [row["avg_score"] for row in top_advisors],
            "open_warnings": open_warnings,
            "in_progress_warnings": in_progress_warnings,
            "closed_warnings": closed_warnings,
            "active_pips": active_pips,
        },
        "advisor_summary": [dict(row) for row in advisor_summary],
        "auditors_list": auditors,
        "sync_status": {
            "display_date": display_date,
            "display_time": display_time,
            "last_sync_time": last_sync_time or "Live Database",
            "last_sync_file": last_batch["source_file"] if last_batch else "Connected",
            "all_time_records": all_time_records,
            "filtered_count": total_audits,
            "is_filtered": bool(
                department != "All"
                or start
                or end
                or auditor
                or advisor_query
                or score_bracket != "All"
                or fatal_status != "All"
            ),
        },
        "filters": {
            "department": department,
            "start": start,
            "end": end,
            "auditor": auditor,
            "advisor_q": advisor_query,
            "score_bracket": score_bracket,
            "fatal_status": fatal_status,
        },
    }
