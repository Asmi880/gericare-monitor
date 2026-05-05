"""
main.py — GeriCare Monitor: Elderly Diabetes Management System
Entry point and router for the Streamlit application.

Run with: streamlit run main.py
"""

import streamlit as st

st.set_page_config(
    page_title="GeriCare Monitor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state defaults
defaults = {
    "logged_in":    False,
    "user_name":    "",
    "user_role":    "patient",
    "page_mode":    "choice",
    "current_page": "dashboard",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Routing ────────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    page = st.session_state.current_page

    if page == "dashboard":
        from dashboard import show_dashboard_page
        show_dashboard_page()

    elif page == "glucose":
        from glucose_module import show_glucose_module
        show_glucose_module()

    elif page == "meal":
        from meal_module import show_meal_module
        show_meal_module()

    elif page == "medication":
        from medication_module import show_medication_module
        show_medication_module()

    elif page == "activity":
        from activity_module import show_activity_module
        show_activity_module()

    elif page == "night":
        from night_module import show_night_module
        show_night_module()

    elif page == "evaluation":
        from evaluation_page import show_evaluation_page
        show_evaluation_page()

    else:
        st.session_state.current_page = "dashboard"
        st.rerun()

else:
    st.session_state.current_page = "dashboard"
    from login import show_login_page
    show_login_page()
