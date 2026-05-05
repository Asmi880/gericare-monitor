"""
activity_module.py — Activity tracking with glucose correlation insight
"""

import streamlit as st
from styles import inject_styles, topbar
from data_engine import generate_activity_data, STEPS_LOW, STEPS_WARN


def show_activity_module():
    inject_styles()
    topbar(st.session_state.user_name, st.session_state.get("user_role", "patient"))

    if st.button("← Back to Dashboard"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="page-title">🚶 Activity Monitoring</div>
    <div class="page-subtitle">Daily movement tracking, activity goals, and glucose regulation correlation</div>
    """, unsafe_allow_html=True)

    data = generate_activity_data()
    pct  = min(100, round(data["today_steps"] / data["goal"] * 100, 1))
    low  = data["today_steps"] < STEPS_LOW
    warn = STEPS_LOW <= data["today_steps"] < STEPS_WARN

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    for col, label, val, sub, accent in [
        (k1, "Steps Today",      f"{data['today_steps']:,}",   f"Goal: {data['goal']:,}",       "#8B5CF6"),
        (k2, "Active Minutes",   f"{data['active_mins']} min", "Daily active time",             "#10B981"),
        (k3, "Calories Burned",  f"{data['calories']} kcal",   "Estimated expenditure",         "#F59E0B"),
        (k4, "Goal Progress",    f"{pct}%",                    "Daily step target",             "#EF4444" if low else ("#F59E0B" if warn else "#10B981")),
    ]:
        col.markdown(f"""
        <div class="kpi-card" style="--accent:{accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-delta">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    # Status alert
    if low:
        msg   = f"⚠️ Very low activity — only {data['today_steps']:,} steps. Sedentary behaviour increases glucose instability risk."
        bg, border = "#FEF2F2", "#EF4444"
    elif warn:
        msg   = f"Below activity goal — {data['today_steps']:,} steps recorded. Aim for {data['goal']:,} steps to support glucose regulation."
        bg, border = "#FFFBEB", "#F59E0B"
    else:
        msg   = f"✓ Activity goal achieved — {data['today_steps']:,} steps. Regular movement supports healthy glucose control."
        bg, border = "#F0FDF4", "#22C55E"

    st.markdown(f"""
    <div style="background:{bg};border-left:4px solid {border};border-radius:12px;padding:14px 18px;margin:16px 0;font-size:0.88rem;color:#0F172A;">
        {msg}
    </div>
    """, unsafe_allow_html=True)

    # Goal progress bar
    st.markdown(f"""
    <div class="data-card" style="margin-bottom:16px;">
        <div class="data-card-title">Daily Step Goal Progress</div>
        <div style="display:flex;justify-content:space-between;font-size:0.82rem;color:#64748B;margin-bottom:8px;">
            <span>0</span><span style="font-weight:700;color:#0F172A;">{data['today_steps']:,} / {data['goal']:,} steps</span><span>{data['goal']:,}</span>
        </div>
        <div class="prog-bar-bg" style="height:14px;">
            <div class="prog-bar-fill" style="width:{pct}%;--prog-color:{'#EF4444' if low else ('#F59E0B' if warn else '#10B981')};"></div>
        </div>
        <div style="font-size:0.78rem;color:#64748B;margin-top:6px;">{pct}% of daily goal</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">📊 Hourly Steps</div>', unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        hourly_chart = {
            "Hour":  [h["hour"] for h in data["hourly"]],
            "Steps": [h["steps"] for h in data["hourly"]]
        }
        st.bar_chart(hourly_chart, x="Hour", y="Steps", height=240, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">📈 Weekly Activity Trend</div>', unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        weekly_chart = {
            "Day":   [d["day"] for d in data["weekly"]],
            "Steps": [d["steps"] for d in data["weekly"]]
        }
        st.bar_chart(weekly_chart, x="Day", y="Steps", height=240, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Weekly summary table
    st.markdown('<div class="section-header">📋 7-Day Activity Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    cols = st.columns(len(data["weekly"]))
    for i, (col, d) in enumerate(zip(cols, data["weekly"])):
        goal_met = d["steps"] >= 5000
        col.markdown(f"""
        <div style="text-align:center;padding:8px 4px;">
            <div style="font-size:0.75rem;font-weight:700;color:#64748B;">{d['day']}</div>
            <div style="font-size:1.1rem;font-weight:700;color:#0F172A;font-family:'DM Mono',monospace;margin:4px 0;">
                {d['steps']:,}
            </div>
            <div style="font-size:0.7rem;color:{'#10B981' if goal_met else '#F59E0B'};">
                {'✓ Goal' if goal_met else '↓ Below'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-label">🔗 Cross-Module Insight — Activity × Glucose Correlation</div>
        <div class="insight-text">
            Physical activity directly influences blood glucose regulation. Today's step count of
            <b style="color:#E2E8F0;">{data['today_steps']:,}</b> represents
            <b style="color:#E2E8F0;">{pct}%</b> of the daily goal.
            {'Low activity levels can reduce insulin sensitivity and cause glucose to remain elevated — '
             'check the Glucose module for potential correlation. ' if low or warn else
             'Adequate activity supports insulin sensitivity and glucose clearance. '}
            Active minutes: <b style="color:#E2E8F0;">{data['active_mins']} min</b> ·
            Calories: <b style="color:#E2E8F0;">{data['calories']} kcal</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
