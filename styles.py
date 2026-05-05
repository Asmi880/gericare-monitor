"""
styles.py — Shared CSS for the professional medical dashboard
"""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=DM+Mono:wght@400;500&display=swap');

#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="collapsedControl"],
[data-testid="stSidebarNav"] { display: none !important; }

html, body { margin: 0; padding: 0; }

.stApp {
    background: #F0F4F8 !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #0F172A !important;
}

.block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 100% !important;
}

/* ── Top nav bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0F172A;
    border-radius: 16px;
    padding: 14px 24px;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(15,23,42,0.2);
}

.topbar-logo {
    display: flex; align-items: center; gap: 12px;
}

.topbar-logo-icon {
    font-size: 1.4rem;
    background: #1E3A5F;
    width: 38px; height: 38px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
}

.topbar-logo-text {
    color: #FFFFFF;
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.2;
}

.topbar-logo-sub {
    color: #64748B;
    font-size: 0.72rem;
}

.topbar-user {
    display: flex; align-items: center; gap: 16px;
}

.topbar-badge {
    background: #1E3A5F;
    color: #93C5FD;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.78rem;
    font-weight: 600;
}

.topbar-name {
    color: #E2E8F0;
    font-size: 0.88rem;
    font-weight: 500;
}

/* ── Page title ── */
.page-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 4px;
    line-height: 1.2;
}

.page-subtitle {
    font-size: 0.9rem;
    color: #64748B;
    margin-bottom: 20px;
}

/* ── KPI / stat cards ── */
.kpi-row { display: flex; gap: 14px; margin-bottom: 20px; flex-wrap: wrap; }

.kpi-card {
    flex: 1;
    min-width: 140px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent, #3B82F6);
    border-radius: 16px 16px 0 0;
}

.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0F172A;
    line-height: 1;
    margin-bottom: 4px;
    font-family: 'DM Mono', monospace;
}

.kpi-delta {
    font-size: 0.78rem;
    color: #64748B;
    font-weight: 500;
}

.kpi-delta.up   { color: #EF4444; }
.kpi-delta.down { color: #10B981; }
.kpi-delta.ok   { color: #3B82F6; }

/* ── Section headers ── */
.section-header {
    font-size: 0.8rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 24px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #E2E8F0;
}

/* ── Data cards ── */
.data-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-bottom: 14px;
    height: 100%;
}

.data-card-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 14px;
}

.data-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #F1F5F9;
    font-size: 0.88rem;
}

.data-row:last-child { border-bottom: none; }

.data-label { color: #64748B; font-weight: 500; }
.data-value { color: #0F172A; font-weight: 700; font-family: 'DM Mono', monospace; }

/* ── Status badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    border-radius: 6px;
    padding: 3px 9px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}

.badge-green  { background: #DCFCE7; color: #166534; }
.badge-red    { background: #FEE2E2; color: #991B1B; }
.badge-amber  { background: #FEF3C7; color: #92400E; }
.badge-blue   { background: #DBEAFE; color: #1E40AF; }
.badge-slate  { background: #F1F5F9; color: #475569; }

/* ── Alert rows ── */
.alert-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 8px;
    border-left: 4px solid transparent;
    font-size: 0.86rem;
}

.alert-critical { background: #FEF2F2; border-left-color: #EF4444; }
.alert-warning  { background: #FFFBEB; border-left-color: #F59E0B; }
.alert-ok       { background: #F0FDF4; border-left-color: #22C55E; }
.alert-info     { background: #EFF6FF; border-left-color: #3B82F6; }

.alert-icon  { font-size: 1rem; margin-top: 1px; flex-shrink: 0; }
.alert-msg   { color: #0F172A; font-weight: 500; line-height: 1.4; }
.alert-meta  { color: #94A3B8; font-size: 0.75rem; margin-top: 2px; }

/* ── Module nav cards ── */
.mod-card {
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 16px;
    padding: 18px 16px;
    cursor: pointer;
    transition: all 0.18s ease;
    margin-bottom: 10px;
    position: relative;
    overflow: hidden;
}

.mod-card:hover {
    border-color: #3B82F6;
    box-shadow: 0 6px 20px rgba(59,130,246,0.12);
    transform: translateY(-2px);
}

.mod-card-accent {
    position: absolute;
    top: 0; left: 0; bottom: 0;
    width: 4px;
    background: var(--mod-color, #3B82F6);
    border-radius: 16px 0 0 16px;
}

.mod-card-icon  { font-size: 1.4rem; margin-bottom: 8px; }
.mod-card-title { font-size: 0.9rem; font-weight: 700; color: #0F172A; margin-bottom: 4px; }
.mod-card-line  { font-size: 0.8rem; color: #64748B; margin-bottom: 2px; }
.mod-card-status { margin-top: 10px; }

/* ── Insight box ── */
.insight-box {
    background: #0F172A;
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 14px;
}

.insight-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}

.insight-text {
    font-size: 0.88rem;
    color: #CBD5E1;
    line-height: 1.6;
}

/* ── Metric gauge ── */
.gauge-wrap { text-align: center; padding: 8px 0; }
.gauge-value { font-size: 2.4rem; font-weight: 700; font-family: 'DM Mono', monospace; color: #0F172A; }
.gauge-label { font-size: 0.78rem; color: #64748B; margin-top: 4px; }

/* ── Progress bar ── */
.prog-bar-bg {
    background: #E2E8F0;
    border-radius: 999px;
    height: 8px;
    margin: 8px 0;
    overflow: hidden;
}
.prog-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: var(--prog-color, #3B82F6);
    transition: width 0.6s ease;
}

/* ── Back button override ── */
.stButton > button {
    background: #0F172A !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: #1E293B !important; }

/* ── Streamlit chart ── */
[data-testid="stArrowVegaLiteChart"],
[data-testid="stVegaLiteChart"] { border-radius: 12px; overflow: hidden; }

div[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 14px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F1F5F9;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #64748B !important;
    padding: 6px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #0F172A !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
}
</style>
"""


def inject_styles():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def topbar(user_name, role="patient"):
    import streamlit as st
    role_label = "Caregiver" if role == "caregiver" else "Patient"
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"""
        <div class="topbar">
            <div class="topbar-logo">
                <div class="topbar-logo-icon">🏥</div>
                <div>
                    <div class="topbar-logo-text">GeriCare Monitor</div>
                    <div class="topbar-logo-sub">Elderly Diabetes Management System</div>
                </div>
            </div>
            <div class="topbar-user">
                <span class="topbar-badge">{role_label}</span>
                <span class="topbar-name">{user_name}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Sign Out", use_container_width=True):
            for key in ["logged_in","user_name","user_role","current_page","page_mode"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
