"""
medication_module.py — Medication tracking with adherence analytics
"""

import streamlit as st
from styles import inject_styles, topbar
from data_engine import generate_medication_log


def show_medication_module():
    inject_styles()
    topbar(st.session_state.user_name, st.session_state.get("user_role", "patient"))

    if st.button("← Back to Dashboard"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="page-title">💊 Medication Tracking</div>
    <div class="page-subtitle">Monitor medication schedules, adherence rates, and missed dose alerts</div>
    """, unsafe_allow_html=True)

    schedule, adherence, weekly = generate_medication_log()
    missed = sum(1 for d in schedule if not d["taken"])
    taken  = sum(1 for d in schedule if d["taken"])

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    for col, label, val, sub, accent in [
        (k1, "Today's Adherence",   f"{adherence}%",     f"{taken}/{len(schedule)} doses taken", "#10B981" if adherence == 100 else "#F59E0B"),
        (k2, "Missed Doses Today",  str(missed),         "Requires attention" if missed else "All on schedule", "#EF4444" if missed else "#10B981"),
        (k3, "Weekly Avg Adherence",f"{round(sum(d['rate'] for d in weekly)/len(weekly),1)}%", "7-day average", "#3B82F6"),
        (k4, "Next Dose",           schedule[-1]["time"] if not schedule[-1]["taken"] else "All done", schedule[-1]["med"] if not schedule[-1]["taken"] else "✓ Complete", "#8B5CF6"),
    ]:
        col.markdown(f"""
        <div class="kpi-card" style="--accent:{accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-delta">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="section-header">💊 Today\'s Schedule</div>', unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        for dose in schedule:
            badge  = "green" if dose["taken"] else "red"
            status = f"✓ Taken at {dose['actual_time']}" if dose["taken"] else "✗ Not yet taken"
            st.markdown(f"""
            <div style="padding:12px 0;border-bottom:1px solid #F1F5F9;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-weight:700;font-size:0.9rem;color:#0F172A;">{dose['med']}</div>
                        <div style="font-size:0.78rem;color:#64748B;margin-top:2px;">Scheduled: {dose['time']}</div>
                    </div>
                    <div>
                        <span class="badge badge-{badge}">{status}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">📈 Weekly Adherence Trend</div>', unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        weekly_chart = {
            "Day":            [d["day"] for d in weekly],
            "Adherence (%)":  [d["rate"] for d in weekly]
        }
        st.bar_chart(weekly_chart, x="Day", y="Adherence (%)", height=240, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Weekly breakdown table
    st.markdown('<div class="section-header">📋 Weekly Dose Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    header_cols = st.columns([1, 1, 1, 1])
    for col, h in zip(header_cols, ["Day", "Taken", "Total", "Rate"]):
        col.markdown(f'<div style="font-size:0.75rem;font-weight:700;color:#64748B;text-transform:uppercase;">{h}</div>', unsafe_allow_html=True)
    for d in weekly:
        r = st.columns([1, 1, 1, 1])
        color = "#10B981" if d["rate"] >= 90 else ("#F59E0B" if d["rate"] >= 67 else "#EF4444")
        r[0].markdown(f'<div style="font-size:0.88rem;font-weight:600;color:#0F172A;">{d["day"]}</div>', unsafe_allow_html=True)
        r[1].markdown(f'<div style="font-size:0.88rem;color:#0F172A;font-family:DM Mono,monospace;">{d["taken"]}</div>', unsafe_allow_html=True)
        r[2].markdown(f'<div style="font-size:0.88rem;color:#64748B;">{d["total"]}</div>', unsafe_allow_html=True)
        r[3].markdown(f'<div style="font-size:0.88rem;font-weight:700;color:{color};">{d["rate"]}%</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-label">🔗 Cross-Module Insight — Medication × Glucose Integration</div>
        <div class="insight-text">
            {'⚠️ ' + str(missed) + ' missed dose(s) detected today. Missed insulin or Metformin can cause glucose elevation — '
             'cross-reference with Glucose module for potential impact. ' if missed
             else 'All scheduled doses taken today. Consistent medication adherence supports stable glucose control. '}
            7-day average adherence: <b style="color:#E2E8F0;">{round(sum(d['rate'] for d in weekly)/len(weekly),1)}%</b>.
            {'Excellent compliance — continue current regimen.' if adherence == 100
             else 'Caregiver notified of missed dose via integrated alert system.'}
        </div>
    </div>
    """, unsafe_allow_html=True)
