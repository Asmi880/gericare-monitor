"""
night_module.py — Nocturnal glucose monitoring AND pre-sleep risk prediction.

Research alignment:
- Gap 4 (SLR): Liu et al. (2026) — NH predictable from daytime CGM + activity + medication.
  This is the key novel contribution: predict tonight's risk from today's data.
- Liu et al. (2026): 25–40% NH prevalence in elderly T2D — NH is a clinical necessity.
- Hasan & Ahmed (2024): caregiver escalation pipeline for nocturnal events.
"""

import streamlit as st
from styles import inject_styles, topbar
from data_engine import (
    generate_night_data, generate_glucose_series,
    generate_activity_data, generate_medication_log,
    compute_presleep_risk,
    GLUCOSE_LOW, NIGHT_LOW
)


def show_night_module():
    inject_styles()
    topbar(st.session_state.user_name, st.session_state.get("user_role", "patient"))

    if st.button("← Back to Dashboard"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="page-title">🌙 Night Monitoring</div>
    <div class="page-subtitle">
        Overnight glucose surveillance, nocturnal hypoglycaemia detection (10 PM – 6 AM),
        and pre-sleep risk prediction from daytime data
    </div>
    """, unsafe_allow_html=True)

    # Load data
    night_data = generate_night_data()
    glucose_series = generate_glucose_series()
    activity = generate_activity_data()
    schedule, adherence, weekly = generate_medication_log()

    avg_night   = round(sum(r["glucose"] for r in night_data["readings"]) / len(night_data["readings"]), 1)
    hypo_events = [r for r in night_data["readings"] if r["glucose"] < NIGHT_LOW]

    risk_color = {"HIGH": "#EF4444", "MODERATE": "#F59E0B", "LOW": "#10B981"}[night_data["hypo_risk"]]
    risk_badge = {"HIGH": "red",     "MODERATE": "amber",   "LOW": "green"}[night_data["hypo_risk"]]

    # ── KPIs ─────────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    for col, label, val, sub, accent in [
        (k1, "Overnight Lowest",  f"{night_data['lowest']} mg/dL",  f"Threshold: {NIGHT_LOW} mg/dL", risk_color),
        (k2, "Overnight Highest", f"{night_data['highest']} mg/dL", "Peak during sleep window",       "#3B82F6"),
        (k3, "Average (Night)",   f"{avg_night} mg/dL",             "Mean overnight glucose",          "#8B5CF6"),
        (k4, "Hypo Events",       str(len(hypo_events)),            f"Readings < {NIGHT_LOW} mg/dL",  "#EF4444" if hypo_events else "#10B981"),
    ]:
        col.markdown(f"""
        <div class="kpi-card" style="--accent:{accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-delta">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Last Night Alert Banner ───────────────────────────────────────────────
    if night_data["hypo_risk"] == "HIGH":
        msg    = f"🚨 CRITICAL: Nocturnal hypoglycemia detected last night — glucose dropped to {night_data['lowest']} mg/dL. Caregiver must be notified."
        bg, border = "#FEF2F2", "#EF4444"
    elif night_data["hypo_risk"] == "MODERATE":
        msg    = f"⚠️ CAUTION: Night glucose dipped to {night_data['lowest']} mg/dL, near hypoglycemia threshold. Monitor closely tonight."
        bg, border = "#FFFBEB", "#F59E0B"
    else:
        msg    = f"✓ SAFE: Overnight glucose stable (lowest: {night_data['lowest']} mg/dL). No hypoglycemia events detected."
        bg, border = "#F0FDF4", "#22C55E"

    st.markdown(f"""
    <div style="background:{bg};border-left:4px solid {border};border-radius:12px;
                padding:14px 18px;margin:16px 0;font-size:0.88rem;color:#0F172A;">
        <b>Last Night:</b> {msg}
    </div>
    """, unsafe_allow_html=True)

    # ── PRE-SLEEP RISK PREDICTION (Novel contribution — Gap 4 from SLR) ──────
    st.markdown('<div class="section-header">🔮 Tonight\'s Pre-Sleep Risk Prediction</div>',
                unsafe_allow_html=True)

    presleep = compute_presleep_risk(glucose_series, activity, schedule, night_data)
    pr_color = {"HIGH": "#EF4444", "MODERATE": "#F59E0B", "LOW": "#10B981"}[presleep["risk_level"]]
    pr_bg    = {"HIGH": "#FEF2F2", "MODERATE": "#FFFBEB", "LOW": "#F0FDF4"}[presleep["risk_level"]]
    pr_border= {"HIGH": "#EF4444", "MODERATE": "#F59E0B", "LOW": "#22C55E"}[presleep["risk_level"]]

    st.markdown(f"""
    <div style="background:{pr_bg};border:2px solid {pr_border};border-radius:14px;
                padding:18px 20px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
            <div style="font-size:0.8rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.06em;">
                Predicted Nocturnal Risk — Tonight
            </div>
            <div style="font-size:1.4rem;font-weight:800;color:{pr_color};font-family:'DM Mono',monospace;">
                {presleep['risk_level']} RISK
            </div>
        </div>
        <div style="margin-bottom:10px;">
            <div style="font-size:0.78rem;color:#64748B;margin-bottom:4px;">Risk Score</div>
            <div style="background:#E2E8F0;border-radius:999px;height:10px;overflow:hidden;">
                <div style="width:{presleep['risk_score']}%;height:100%;background:{pr_color};
                            border-radius:999px;transition:width 0.6s;"></div>
            </div>
            <div style="font-size:0.75rem;color:#64748B;margin-top:4px;">{presleep['risk_score']} / 100</div>
        </div>
    """, unsafe_allow_html=True)

    for factor in presleep["risk_factors"]:
        st.markdown(f"""
        <div style="font-size:0.84rem;color:#374151;padding:6px 0;border-bottom:1px solid #E2E8F0;">
            {factor}
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="background:#0F172A;border-radius:10px;padding:12px 14px;margin-top:12px;">
            <div style="font-size:0.72rem;color:#64748B;text-transform:uppercase;font-weight:700;
                        letter-spacing:0.06em;margin-bottom:4px;">Recommended Action</div>
            <div style="font-size:0.88rem;color:#CBD5E1;">{presleep['recommendation']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.75rem;color:#94A3B8;margin-bottom:16px;font-style:italic;">
        ℹ️ Pre-sleep risk prediction is based on daytime glucose trend, activity level, and medication adherence.
        Evidence: Liu et al. (2026) — nocturnal hypoglycaemia predictable from daytime CGM patterns in elderly T2D.
        This is a research prototype — not for clinical use.
    </div>
    """, unsafe_allow_html=True)

    # ── Overnight Charts ──────────────────────────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-header">📈 Last Night\'s Glucose Trace</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        night_chart = {
            "Time":            [r["time"] for r in night_data["readings"]],
            "Glucose (mg/dL)": [r["glucose"] for r in night_data["readings"]]
        }
        st.line_chart(night_chart, x="Time", y="Glucose (mg/dL)",
                      height=280, use_container_width=True)
        st.markdown(f"""
        <div style="display:flex;gap:20px;margin-top:8px;font-size:0.78rem;flex-wrap:wrap;">
            <span style="color:#EF4444;">● Critical threshold: &lt; {GLUCOSE_LOW} mg/dL</span>
            <span style="color:#F59E0B;">● Caution threshold: &lt; {NIGHT_LOW} mg/dL</span>
            <span style="color:#64748B;">Monitoring window: 10:00 PM – 06:00 AM</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">📋 Risk Assessment</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
        <div class="data-card">
            <div class="data-card-title">Overnight Safety Summary</div>
            <div class="data-row">
                <span class="data-label">Monitoring Window</span>
                <span class="data-value">10 PM – 6 AM</span>
            </div>
            <div class="data-row">
                <span class="data-label">Lowest Reading</span>
                <span class="data-value" style="color:{risk_color};">{night_data['lowest']} mg/dL</span>
            </div>
            <div class="data-row">
                <span class="data-label">Highest Reading</span>
                <span class="data-value">{night_data['highest']} mg/dL</span>
            </div>
            <div class="data-row">
                <span class="data-label">Average (Night)</span>
                <span class="data-value">{avg_night} mg/dL</span>
            </div>
            <div class="data-row">
                <span class="data-label">Hypo Events</span>
                <span class="data-value" style="color:{'#EF4444' if hypo_events else '#10B981'};">
                    {len(hypo_events)}
                </span>
            </div>
            <div class="data-row">
                <span class="data-label">Alerts Triggered</span>
                <span class="data-value">{night_data['alerts_triggered']}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Sleep Safety</span>
                <span class="data-value">{night_data['sleep_status']}</span>
            </div>
            <div class="data-row">
                <span class="data-label">Hypoglycemia Risk</span>
                <span class="data-value" style="color:{risk_color};font-weight:800;">
                    {night_data['hypo_risk']}
                </span>
            </div>
            <div style="margin-top:12px;">
                <span class="badge badge-{risk_badge}">{night_data['hypo_risk']} RISK</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if hypo_events:
            st.markdown('<div class="section-header" style="margin-top:12px;">🚨 Low Readings</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            for e in hypo_events:
                st.markdown(f"""
                <div class="data-row">
                    <span class="data-label">{e['time']}</span>
                    <span class="data-value" style="color:#EF4444;">{e['glucose']} mg/dL</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Cross-module insight ──────────────────────────────────────────────────
    series_data = glucose_series[0] if isinstance(glucose_series, tuple) else glucose_series
    missed_insulin = any(not d["taken"] and "Insulin" in d["med"] for d in schedule)

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-label">🔗 Cross-Module Insight — Night × Glucose × Activity × Medication</div>
        <div class="insight-text">
            Last night's lowest glucose: <b style="color:#E2E8F0;">{night_data['lowest']} mg/dL</b>.
            Tonight's predicted risk: <b style="color:{pr_color};">{presleep['risk_level']}</b>
            (score: {presleep['risk_score']}/100).
            {'<br>⚠️ Evening insulin was missed today — this is a direct predictor of nocturnal hyperglycaemia '
             '(Lanke et al., 2025). Caregiver review recommended before sleep. '
             if missed_insulin else
             ''}
            {'<br>High daytime activity may deplete glycogen stores, increasing nocturnal hypoglycaemia risk. '
             if activity["today_steps"] > 7000 else ''}
            Activity today: <b style="color:#E2E8F0;">{activity['today_steps']:,} steps</b>.
            Sleep safety status last night: <b style="color:#E2E8F0;">{night_data['sleep_status']}</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)