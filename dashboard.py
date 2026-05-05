"""
dashboard.py — Main dashboard with cross-module integration, real alerts, evaluation metrics
Directly answers RQ2 (unified framework) and RQ3 (usability, effectiveness, applicability)
"""

import streamlit as st
from datetime import datetime
from styles import inject_styles, topbar
from data_engine import (
    generate_glucose_series, generate_meal_log, generate_medication_log,
    generate_activity_data, generate_night_data,
    evaluate_alerts, compute_evaluation_metrics
)


def render_alert_item(alert):
    cls = {
        "CRITICAL": "alert-critical",
        "WARNING":  "alert-warning",
        "OK":       "alert-ok",
        "INFO":     "alert-info"
    }.get(alert["level"], "alert-info")

    return f"""
    <div class="alert-item {cls}">
        <div class="alert-icon">{alert['icon']}</div>
        <div>
            <div class="alert-msg">{alert['message']}</div>
            <div class="alert-meta">{alert['module']} · {alert['time']}</div>
        </div>
    </div>
    """


def render_badge(text, color="slate"):
    return f'<span class="badge badge-{color}">{text}</span>'


def render_progress(value, color="#3B82F6", label=""):
    return f"""
    <div style="margin-bottom:6px;">
        <div style="display:flex;justify-content:space-between;font-size:0.78rem;color:#64748B;margin-bottom:4px;">
            <span>{label}</span><span style="font-family:'DM Mono',monospace;font-weight:700;color:#0F172A;">{value}%</span>
        </div>
        <div class="prog-bar-bg">
            <div class="prog-bar-fill" style="width:{value}%;--prog-color:{color};"></div>
        </div>
    </div>
    """


def show_dashboard_page():
    inject_styles()

    # ── Load all data ──────────────────────────────────────────────────────
    # generate_glucose_series() now returns (series, evening_dose_missed)
    glucose_tuple   = generate_glucose_series()
    glucose_series, evening_dose_missed = glucose_tuple

    meal_log        = generate_meal_log()
    med_schedule, adherence_pct, weekly_med = generate_medication_log()
    activity        = generate_activity_data()
    night           = generate_night_data()

    # Cross-module alert evaluation (RQ2 — unified rule engine)
    # Pass the tuple so evaluate_alerts can unpack internally
    alerts  = evaluate_alerts(glucose_tuple, activity, med_schedule, night)
    metrics = compute_evaluation_metrics(alerts, glucose_tuple, activity, med_schedule, weekly_med)

    latest_g = glucose_series[-1]["glucose"]
    prev_g   = glucose_series[-2]["glucose"]
    g_delta  = round(latest_g - prev_g, 1)

    critical_count = metrics["critical"]
    warning_count  = metrics["warnings"]

    now = datetime.now()
    user_role = st.session_state.get("user_role", "patient")

    # ── Top bar ────────────────────────────────────────────────────────────
    topbar(st.session_state.user_name, user_role)

    # ── Page title ─────────────────────────────────────────────────────────
    if critical_count:
        badge_html = f'<span class="badge badge-red">⚠ {critical_count} Critical</span>'
    elif warning_count:
        badge_html = f'<span class="badge badge-amber">{warning_count} Warning{"s" if warning_count > 1 else ""}</span>'
    else:
        badge_html = '<span class="badge badge-green">✓ All Clear</span>'

    st.markdown(f"""
    <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:20px;">
        <div>
            <div class="page-title">Patient Overview Dashboard</div>
            <div class="page-subtitle">
                Unified monitoring across glucose, medication, meals, activity &amp; night risk
                &nbsp;·&nbsp; {now.strftime('%A, %d %B %Y  %H:%M')}
            </div>
        </div>
        <div style="display:flex;gap:8px;align-items:center;margin-top:4px;">
            {badge_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Strip ──────────────────────────────────────────────────────────
    delta_cls = "up" if g_delta > 0 else ("down" if g_delta < 0 else "ok")
    delta_sym = "↑" if g_delta > 0 else ("↓" if g_delta < 0 else "→")

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    def kpi(col, label, value, delta_text, accent, delta_cls2="ok"):
        col.markdown(f"""
        <div class="kpi-card" style="--accent:{accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta {delta_cls2}">{delta_text}</div>
        </div>
        """, unsafe_allow_html=True)

    kpi(k1, "Current Glucose",  f"{latest_g} mg/dL",
        f"{delta_sym} {abs(g_delta)} from last",
        "#EF4444" if latest_g < 70 or latest_g > 180 else "#3B82F6", delta_cls)

    tir_color = "#10B981" if metrics["time_in_range"] >= 70 else "#F59E0B"
    kpi(k2, "Time in Range",    f"{metrics['time_in_range']}%",
        "Target ≥ 70%", tir_color,
        "ok" if metrics["time_in_range"] >= 70 else "up")

    kpi(k3, "Med Adherence",    f"{metrics['medication_adherence']}%",
        f"{'Perfect' if metrics['medication_adherence']==100 else 'Needs attention'}",
        "#10B981" if metrics["medication_adherence"] >= 90 else "#F59E0B",
        "ok" if metrics["medication_adherence"] >= 90 else "up")

    kpi(k4, "Steps Today",      f"{activity['today_steps']:,}",
        f"Goal: {activity['goal']:,}", "#8B5CF6",
        "ok" if activity["today_steps"] >= activity["goal"] else "up")

    kpi(k5, "Night Risk",       night["hypo_risk"],
        f"Lowest: {night['lowest']} mg/dL",
        "#EF4444" if night["hypo_risk"]=="HIGH" else ("#F59E0B" if night["hypo_risk"]=="MODERATE" else "#10B981"),
        "up" if night["hypo_risk"]!="LOW" else "ok")

    # Stream coverage replaces the old 'health_score' KPI — more research-meaningful
    kpi(k6, "Stream Coverage",  f"{metrics['stream_coverage']}%",
        "Data continuity",
        "#0EA5E9",
        "ok" if metrics["stream_coverage"] >= 95 else "up")

    # ── Two-column main layout ─────────────────────────────────────────────
    left_col, right_col = st.columns([3, 2], gap="large")

    with left_col:
        # Glucose trend chart
        st.markdown('<div class="section-header">📈 Glucose Trend — Last 24 Hours</div>', unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)

        chart_data = {
            "Time":    [r["time"] for r in glucose_series[::2]],
            "Glucose": [r["glucose"] for r in glucose_series[::2]]
        }
        st.line_chart(chart_data, x="Time", y="Glucose", height=220, use_container_width=True)

        st.markdown(f"""
        <div style="display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;">
            <span style="font-size:0.75rem;color:#EF4444;">● Hypo &lt; 70</span>
            <span style="font-size:0.75rem;color:#F59E0B;">● Target 80–130</span>
            <span style="font-size:0.75rem;color:#EF4444;">● Hyper &gt; 180</span>
            <span style="font-size:0.75rem;color:#64748B;margin-left:auto;">
                Current: <b style="color:#0F172A;">{latest_g} mg/dL</b>
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Module navigation cards
        st.markdown('<div class="section-header">🧩 Monitoring Modules</div>', unsafe_allow_html=True)

        ma, mb = st.columns(2)
        mc, md = st.columns(2)
        me, _  = st.columns(2)

        glucose_status = "Stable" if 80 <= latest_g <= 160 else ("⚠ Low" if latest_g < 80 else "⚠ High")
        glucose_badge  = "green" if 80 <= latest_g <= 160 else "red"

        missed_doses = sum(1 for d in med_schedule if not d["taken"])
        med_badge    = "green" if missed_doses == 0 else "amber"

        steps_badge = "green" if activity["today_steps"] >= activity["goal"] else "amber"
        night_badge = "green" if night["hypo_risk"] == "LOW" else ("red" if night["hypo_risk"] == "HIGH" else "amber")

        def mod_nav(col, page, icon, title, stat1, stat2, status_text, badge_color, accent):
            with col:
                st.markdown(f"""
                <div class="mod-card" style="--mod-color:{accent};">
                    <div class="mod-card-accent"></div>
                    <div style="padding-left:8px;">
                        <div class="mod-card-icon">{icon}</div>
                        <div class="mod-card-title">{title}</div>
                        <div class="mod-card-line">{stat1}</div>
                        <div class="mod-card-line">{stat2}</div>
                        <div class="mod-card-status">{render_badge(status_text, badge_color)}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Open →", key=f"nav_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()

        mod_nav(ma, "glucose", "🩸", "Glucose Monitor",
                f"Current: {latest_g} mg/dL", f"TIR: {metrics['time_in_range']}%",
                glucose_status, glucose_badge, "#EF4444")

        mod_nav(mb, "meal", "🍽️", "Meal Analysis",
                f"{len(meal_log)} meals logged", f"Last: {meal_log[-1]['meal']}",
                "Tracked", "blue", "#F59E0B")

        mod_nav(mc, "medication", "💊", "Medication",
                f"Adherence: {adherence_pct}%",
                f"{'No missed doses' if missed_doses==0 else str(missed_doses)+' dose(s) missed'}",
                "On Schedule" if missed_doses == 0 else "Missed Dose", med_badge, "#8B5CF6")

        mod_nav(md, "activity", "🚶", "Activity",
                f"{activity['today_steps']:,} steps today",
                f"Active: {activity['active_mins']} min",
                "Goal Met" if activity["today_steps"] >= activity["goal"] else "Below Goal",
                steps_badge, "#10B981")

        # Evaluation page nav
        st.markdown('<div class="section-header">📊 Framework Evaluation (RQ3)</div>', unsafe_allow_html=True)
        if st.button("View Full Evaluation Report →", key="nav_eval", use_container_width=True):
            st.session_state.current_page = "evaluation"
            st.rerun()

        mod_nav(me, "night", "🌙", "Night Monitor",
                f"Lowest: {night['lowest']} mg/dL",
                f"Risk: {night['hypo_risk']}",
                f"{night['hypo_risk']} Risk", night_badge, "#6366F1")

    with right_col:
        # Live alerts panel (cross-module integration — RQ2)
        st.markdown('<div class="section-header">🚨 Active Alerts</div>', unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        for a in alerts:
            st.markdown(render_alert_item(a), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Patient summary
        risk_priority = "High" if critical_count else ("Moderate" if warning_count else "Low")
        st.markdown('<div class="section-header">👤 Patient Summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="data-card">
            <div class="data-card-title">Clinical Profile</div>
            <div class="data-row">
                <span class="data-label">Patient ID</span>
                <span class="data-value">P-2025-001</span>
            </div>
            <div class="data-row">
                <span class="data-label">Age Group</span>
                <span class="data-value">Elderly (65+)</span>
            </div>
            <div class="data-row">
                <span class="data-label">Diabetes Type</span>
                <span class="data-value">Type 2</span>
            </div>
            <div class="data-row">
                <span class="data-label">Monitoring Mode</span>
                <span class="data-value">Active</span>
            </div>
            <div class="data-row">
                <span class="data-label">Risk Priority</span>
                <span class="data-value">{risk_priority}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Last Updated</span>
                <span class="data-value">{now.strftime('%H:%M')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Evaluation metrics panel (RQ3)
        tir_color = '#10B981' if metrics['time_in_range'] >= 70 else '#F59E0B'
        med_color = '#10B981' if metrics['medication_adherence'] >= 90 else '#F59E0B'
        latency   = metrics['latency_ms']
        total_al  = metrics['total_alerts']

        st.markdown('<div class="section-header">📊 System Evaluation (RQ3 Metrics)</div>', unsafe_allow_html=True)
        st.markdown('<div class="data-card"><div class="data-card-title">Framework Performance Metrics</div>', unsafe_allow_html=True)

        st.markdown(render_progress(metrics['time_in_range'],        tir_color,  'Time in Glucose Range (TIR)'), unsafe_allow_html=True)
        st.markdown(render_progress(metrics['medication_adherence'], med_color,  'Medication Adherence'),        unsafe_allow_html=True)
        st.markdown(render_progress(metrics['activity_score'],       '#8B5CF6',  'Daily Activity Goal'),         unsafe_allow_html=True)
        st.markdown(render_progress(metrics['stream_coverage'],      '#0EA5E9',  'Stream Coverage'),             unsafe_allow_html=True)

        st.markdown(f"""
        <div class="data-row" style="margin-top:10px;">
            <span class="data-label">Alert Latency (measured)</span>
            <span class="data-value">{latency} ms</span>
        </div>
        <div class="data-row">
            <span class="data-label">Alert Precision / Recall</span>
            <span class="data-value">{metrics['alert_precision']}% / {metrics['alert_recall']}%</span>
        </div>
        <div class="data-row">
            <span class="data-label">Modules Integrated</span>
            <span class="data-value">5 / 5</span>
        </div>
        <div class="data-row">
            <span class="data-label">Active Alerts</span>
            <span class="data-value">{total_al}</span>
        </div>
        </div>
        """, unsafe_allow_html=True)

        # Cross-module clinical insight
        g_status   = "elevated" if latest_g > 130 else "stable"
        risk_level = night['hypo_risk'].lower()
        act_pct    = round(metrics['activity_score'])

        missed_insulin = any(
            not d["taken"] and "Insulin" in d["med"] for d in med_schedule
        )

        if critical_count:
            insight_text = "⚠️ Critical condition detected. Immediate caregiver review required."
        elif missed_insulin:
            insight_text = (
                f"Glucose is {g_status} at {latest_g} mg/dL. "
                f"Evening insulin was missed — nocturnal glucose risk is elevated tonight. "
                f"Activity at {act_pct}% of daily goal. "
                f"Check the Night module for tonight's pre-sleep risk assessment."
            )
        else:
            insight_text = (
                f"Glucose is {g_status} at {latest_g} mg/dL. "
                f"Medication adherence: {adherence_pct}%. "
                f"Activity at {act_pct}% of daily goal. "
                f"Night monitoring shows {risk_level} hypoglycemia risk. "
                f"Stream coverage: {metrics['stream_coverage']}%."
            )

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-label">🔗 Cross-Module Clinical Insight</div>
            <div class="insight-text">{insight_text}</div>
        </div>
        """, unsafe_allow_html=True)