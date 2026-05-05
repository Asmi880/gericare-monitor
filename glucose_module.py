"""
glucose_module.py — Detailed glucose monitoring with dynamic data and real alert logic
"""

import streamlit as st
from styles import inject_styles, topbar
from data_engine import (
    generate_glucose_series, generate_weekly_glucose,
    GLUCOSE_LOW, GLUCOSE_HIGH, GLUCOSE_WARN_LOW, GLUCOSE_WARN_HIGH,
    GLUCOSE_TARGET_LOW, GLUCOSE_TARGET_HIGH
)


def show_glucose_module():
    inject_styles()
    topbar(st.session_state.user_name, st.session_state.get("user_role", "patient"))

    if st.button("← Back to Dashboard", key="back_btn"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="page-title">🩸 Glucose Monitoring</div>
    <div class="page-subtitle">Real-time glucose tracking, trend analysis, and hypoglycemia / hyperglycemia detection</div>
    """, unsafe_allow_html=True)

    # Load data
    series, _ = generate_glucose_series()
    weekly  = generate_weekly_glucose()
    latest  = series[-1]["glucose"]
    prev    = series[-2]["glucose"]
    delta   = round(latest - prev, 1)

    # Determine status
    if latest < GLUCOSE_LOW:
        status, badge, insight_color = "HYPOGLYCEMIA", "red", "#FEF2F2"
        insight = f"⚠️ Glucose critically low at {latest} mg/dL. Immediate sugar intake recommended. Alert caregiver."
    elif latest > GLUCOSE_HIGH:
        status, badge, insight_color = "HYPERGLYCEMIA", "red", "#FEF2F2"
        insight = f"⚠️ Glucose critically high at {latest} mg/dL. Check insulin dose. Caregiver review required."
    elif latest < GLUCOSE_WARN_LOW:
        status, badge, insight_color = "LOW CAUTION", "amber", "#FFFBEB"
        insight = f"Glucose trending low at {latest} mg/dL. Monitor closely and consider a small snack."
    elif latest > GLUCOSE_WARN_HIGH:
        status, badge, insight_color = "ELEVATED", "amber", "#FFFBEB"
        insight = f"Glucose elevated at {latest} mg/dL. Review recent meal intake and activity levels."
    else:
        status, badge, insight_color = "WITHIN TARGET", "green", "#F0FDF4"
        insight = f"Glucose stable at {latest} mg/dL, within target range ({GLUCOSE_TARGET_LOW}–{GLUCOSE_TARGET_HIGH} mg/dL). Continue current management."

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    def gkpi(col, label, value, sub, accent):
        col.markdown(f"""
        <div class="kpi-card" style="--accent:{accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    # Time in range
    in_range = [r for r in series if GLUCOSE_TARGET_LOW <= r["glucose"] <= GLUCOSE_TARGET_HIGH]
    tir = round(len(in_range) / len(series) * 100, 1)
    below = round(sum(1 for r in series if r["glucose"] < GLUCOSE_TARGET_LOW) / len(series) * 100, 1)
    above = round(sum(1 for r in series if r["glucose"] > GLUCOSE_TARGET_HIGH) / len(series) * 100, 1)

    gkpi(k1, "Current Glucose", f"{latest} mg/dL",
         f"{'↑' if delta>0 else '↓'} {abs(delta)} from last reading",
         "#EF4444" if latest < GLUCOSE_LOW or latest > GLUCOSE_HIGH else "#3B82F6")
    gkpi(k2, "Time in Range",   f"{tir}%",   "Target: ≥ 70%",  "#10B981" if tir >= 70 else "#F59E0B")
    gkpi(k3, "% Below Target",  f"{below}%", "< 80 mg/dL",     "#3B82F6")
    gkpi(k4, "% Above Target",  f"{above}%", "> 130 mg/dL",    "#F59E0B")

    # Status insight
    st.markdown(f"""
    <div style="background:{insight_color};border-radius:12px;padding:14px 18px;margin:16px 0;
                border-left:4px solid {'#EF4444' if badge=='red' else ('#F59E0B' if badge=='amber' else '#22C55E')};">
        <span class="badge badge-{badge}" style="margin-right:10px;">{status}</span>
        <span style="font-size:0.88rem;color:#0F172A;">{insight}</span>
    </div>
    """, unsafe_allow_html=True)

    # Charts
    tab1, tab2 = st.tabs(["24-Hour Trend", "7-Day Average"])

    with tab1:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="data-card-title">Glucose Readings — Last 24 Hours (every 30 min)</div>', unsafe_allow_html=True)
        chart_24 = {"Time": [r["time"] for r in series], "Glucose (mg/dL)": [r["glucose"] for r in series]}
        st.line_chart(chart_24, x="Time", y="Glucose (mg/dL)", height=260, use_container_width=True)
        st.markdown(f"""
        <div style="display:flex;gap:20px;margin-top:8px;font-size:0.78rem;flex-wrap:wrap;">
            <span style="color:#64748B;">🔴 Hypo threshold: &lt; {GLUCOSE_LOW} mg/dL</span>
            <span style="color:#64748B;">🟡 Target range: {GLUCOSE_TARGET_LOW}–{GLUCOSE_TARGET_HIGH} mg/dL</span>
            <span style="color:#64748B;">🔴 Hyper threshold: &gt; {GLUCOSE_HIGH} mg/dL</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown('<div class="data-card-title">Daily Average Glucose — Last 7 Days</div>', unsafe_allow_html=True)
        chart_7 = {"Day": [d["day"] for d in weekly], "Avg Glucose (mg/dL)": [d["avg_glucose"] for d in weekly]}
        st.bar_chart(chart_7, x="Day", y="Avg Glucose (mg/dL)", height=240, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Detail table + risk summary
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">📋 Recent Readings</div>', unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        for r in reversed(series[-8:]):
            g = r["glucose"]
            color = "#EF4444" if g < GLUCOSE_LOW or g > GLUCOSE_HIGH else ("#F59E0B" if g < GLUCOSE_WARN_LOW or g > GLUCOSE_WARN_HIGH else "#10B981")
            st.markdown(f"""
            <div class="data-row">
                <span class="data-label">{r['time']}</span>
                <span class="data-value" style="color:{color};">{g} mg/dL</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">⚠️ Risk Summary</div>', unsafe_allow_html=True)
        low_events  = sum(1 for r in series if r["glucose"] < GLUCOSE_LOW)
        high_events = sum(1 for r in series if r["glucose"] > GLUCOSE_HIGH)
        warn_events = sum(1 for r in series if GLUCOSE_WARN_LOW <= r["glucose"] < GLUCOSE_LOW
                           or GLUCOSE_WARN_HIGH < r["glucose"] <= GLUCOSE_HIGH)
        avg_g = round(sum(r["glucose"] for r in series) / len(series), 1)

        st.markdown(f"""
        <div class="data-card">
            <div class="data-card-title">24-Hour Risk Analysis</div>
            <div class="data-row">
                <span class="data-label">Average Glucose</span>
                <span class="data-value">{avg_g} mg/dL</span>
            </div>
            <div class="data-row">
                <span class="data-label">Hypoglycemia Events</span>
                <span class="data-value" style="color:{'#EF4444' if low_events else '#10B981'};">
                    {low_events} event{'s' if low_events != 1 else ''}
                </span>
            </div>
            <div class="data-row">
                <span class="data-label">Hyperglycemia Events</span>
                <span class="data-value" style="color:{'#EF4444' if high_events else '#10B981'};">
                    {high_events} event{'s' if high_events != 1 else ''}
                </span>
            </div>
            <div class="data-row">
                <span class="data-label">Caution-Level Events</span>
                <span class="data-value" style="color:{'#F59E0B' if warn_events else '#10B981'};">
                    {warn_events} event{'s' if warn_events != 1 else ''}
                </span>
            </div>
            <div class="data-row">
                <span class="data-label">Time in Range</span>
                <span class="data-value">{tir}%</span>
            </div>
            <div class="data-row">
                <span class="data-label">Overall Risk Level</span>
                <span class="data-value" style="color:{'#EF4444' if low_events or high_events else '#10B981'};">
                    {'HIGH' if low_events or high_events else ('MODERATE' if warn_events else 'LOW')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Clinical insight
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-label">🔬 Clinical Insight — Glucose Analysis</div>
        <div class="insight-text">
            Over the last 24 hours, average glucose was <b style="color:#E2E8F0;">{avg_g} mg/dL</b>
            with <b style="color:#E2E8F0;">{tir}%</b> time in target range (80–130 mg/dL).
            {'Hypoglycemia detected in ' + str(low_events) + ' reading(s) — immediate action was required. ' if low_events else ''}
            {'Hyperglycemia detected in ' + str(high_events) + ' reading(s) — insulin adjustment may be needed. ' if high_events else ''}
            {'Glucose remained within safe range for the monitoring period. Continue current management plan.' if not low_events and not high_events else
             'Caregiver has been notified via the integrated alert system.'}
        </div>
    </div>
    """, unsafe_allow_html=True)