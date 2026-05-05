"""
meal_module.py — Meal analysis with glucose impact cross-module integration
"""

import streamlit as st
from styles import inject_styles, topbar
from data_engine import generate_meal_log, generate_glucose_series, MEAL_SPIKE_LIMIT


def show_meal_module():
    inject_styles()
    topbar(st.session_state.user_name, st.session_state.get("user_role", "patient"))

    if st.button("← Back to Dashboard"):
        st.session_state.current_page = "dashboard"
        st.rerun()

    st.markdown("""
    <div class="page-title">🍽️ Meal Analysis</div>
    <div class="page-subtitle">Track meal intake and analyse the direct impact on blood glucose levels</div>
    """, unsafe_allow_html=True)

    meals   = generate_meal_log()
    series  = generate_glucose_series()

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    avg_impact = round(sum(m["impact"] for m in meals) / len(meals), 1)
    high_spike = sum(1 for m in meals if m["status"] == "High Spike")

    for col, label, val, sub, accent in [
        (k1, "Meals Logged Today", str(len(meals)),     "All meals recorded",        "#F59E0B"),
        (k2, "Avg Glucose Rise",   f"+{avg_impact}",    "mg/dL per meal avg",        "#EF4444" if avg_impact > MEAL_SPIKE_LIMIT else "#10B981"),
        (k3, "High Spikes",        str(high_spike),     f">{MEAL_SPIKE_LIMIT} mg/dL rise", "#EF4444" if high_spike else "#10B981"),
        (k4, "Last Meal",          meals[-1]["meal"],   meals[-1]["time"],            "#3B82F6"),
    ]:
        col.markdown(f"""
        <div class="kpi-card" style="--accent:{accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-delta">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">🍽️ Today\'s Meal Log</div>', unsafe_allow_html=True)

    for m in meals:
        badge_color = "red" if m["status"] == "High Spike" else ("amber" if m["status"] == "Moderate" else "green")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="data-card">
                <div class="data-card-title">{m['meal']} · {m['time']}</div>
                <div class="data-row"><span class="data-label">Food</span><span class="data-value">{m['type']}</span></div>
                <div class="data-row"><span class="data-label">Category</span><span class="data-value">{m['category']}</span></div>
                <div class="data-row"><span class="data-label">Before Meal</span><span class="data-value">{m['before']} mg/dL</span></div>
                <div class="data-row"><span class="data-label">After Meal</span><span class="data-value">{m['after']} mg/dL</span></div>
                <div class="data-row">
                    <span class="data-label">Glucose Rise</span>
                    <span class="data-value" style="color:{'#EF4444' if m['impact']>MEAL_SPIKE_LIMIT else '#10B981'};">+{m['impact']} mg/dL</span>
                </div>
                <div style="margin-top:10px;"><span class="badge badge-{badge_color}">{m['status']}</span></div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            meal_chart = {
                "Stage":   ["Pre-Meal", "Post-Meal"],
                "Glucose": [m["before"], m["after"]]
            }
            st.markdown(f'<div class="data-card"><div class="data-card-title">Glucose Impact — {m["meal"]}</div>', unsafe_allow_html=True)
            st.bar_chart(meal_chart, x="Stage", y="Glucose", height=180, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Pre/post comparison chart
    st.markdown('<div class="section-header">📊 Pre vs Post-Meal Glucose Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    comparison = {
        "Meal":    [m["meal"] for m in meals],
        "Before":  [m["before"] for m in meals],
        "After":   [m["after"] for m in meals],
    }
    st.bar_chart(comparison, x="Meal", y=["Before", "After"], height=240, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-label">🔗 Cross-Module Insight — Meal × Glucose Integration</div>
        <div class="insight-text">
            {'⚠️ ' + str(high_spike) + ' high spike(s) detected today exceeding the ' + str(MEAL_SPIKE_LIMIT) + ' mg/dL threshold. '
             if high_spike else 'All meals produced glucose rises within acceptable limits. '}
            Average post-meal rise of <b style="color:#E2E8F0;">+{avg_impact} mg/dL</b>.
            Meal data is cross-referenced with the glucose monitoring module to track dietary impact in real time.
            Caregiver alerts are triggered automatically when spikes exceed clinical thresholds.
        </div>
    </div>
    """, unsafe_allow_html=True)
