"""
login.py — Authentication module with professional medical UI
"""

import streamlit as st
import sqlite3


# ── Database helpers ──────────────────────────────────────────────────────────
def create_users_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT NOT NULL,
            pin TEXT NOT NULL,
            role TEXT DEFAULT 'patient'
        )
    """)
    conn.commit()
    conn.close()


def create_default_users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    defaults = [
        ("Admin User",    "admin123",    "0000000000", "123", "caregiver"),
        ("Patient User",  "patient123",  "1111111111", "456", "patient"),
    ]
    for u in defaults:
        c.execute("SELECT id FROM users WHERE full_name=?", (u[0],))
        if not c.fetchone():
            c.execute("INSERT INTO users (full_name,password,phone,pin,role) VALUES (?,?,?,?,?)", u)
    conn.commit()
    conn.close()


def login_user(full_name, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE full_name=? AND password=?", (full_name, password))
    user = c.fetchone()
    conn.close()
    return user


def add_user(full_name, password, phone, pin):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (full_name,password,phone,pin,role) VALUES (?,?,?,?,?)",
                  (full_name, password, phone, pin, "patient"))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def recover_user(full_name, phone, pin):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE full_name=? AND phone=? AND pin=?", (full_name, phone, pin))
    user = c.fetchone()
    conn.close()
    return user


# ── Styles ────────────────────────────────────────────────────────────────────
def apply_login_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    #MainMenu, header, footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="collapsedControl"] { display: none !important; }

    html, body, .stApp {
        background: #F0F4F8 !important;
        font-family: 'DM Sans', sans-serif !important;
        color: #0F172A !important;
    }

    .block-container {
        padding: 2rem 2rem !important;
        max-width: 520px !important;
        margin: 0 auto !important;
    }

    .login-panel {
        background: #FFFFFF;
        border-radius: 24px;
        padding: 48px 44px;
        width: 100%;
        max-width: 480px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.25);
    }

    .login-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 32px;
    }

    .logo-icon {
        width: 44px; height: 44px;
        background: #0F172A;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px;
    }

    .logo-text {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }

    .logo-sub {
        font-size: 0.75rem;
        color: #64748B;
        font-weight: 400;
    }

    .login-heading {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
        line-height: 1.2;
    }

    .login-sub {
        font-size: 0.9rem;
        color: #64748B;
        margin-bottom: 28px;
    }

    .demo-hint {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #166534;
        margin-bottom: 20px;
        font-family: 'DM Mono', monospace;
    }

    .stTextInput label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
        margin-bottom: 4px !important;
    }

    div[data-baseweb="input"] > div {
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 10px !important;
        background: #F8FAFC !important;
        transition: border-color 0.2s;
    }

    div[data-baseweb="input"] > div:focus-within {
        border-color: #3B82F6 !important;
        background: #FFFFFF !important;
    }

    div[data-baseweb="input"] input {
        color: #0F172A !important;
        font-size: 0.95rem !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .stButton > button {
        background: #0F172A !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.7rem 1rem !important;
        width: 100%;
        transition: background 0.2s !important;
    }

    .stButton > button:hover {
        background: #1E293B !important;
    }

    .btn-secondary > button {
        background: #F1F5F9 !important;
        color: #0F172A !important;
    }

    .divider {
        border: none;
        border-top: 1px solid #E2E8F0;
        margin: 20px 0;
    }

    .choice-card {
        background: #F8FAFC;
        border: 1.5px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 12px;
    }

    .choice-card:hover { border-color: #3B82F6; background: #EFF6FF; }

    .choice-icon { font-size: 2rem; margin-bottom: 8px; }
    .choice-title { font-weight: 700; font-size: 1rem; color: #0F172A; }
    .choice-desc  { font-size: 0.82rem; color: #64748B; margin-top: 4px; }

    .stAlert { border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)


# ── Page renderers ────────────────────────────────────────────────────────────
def render_logo():
    st.markdown("""
    <div style="text-align:center;margin-bottom:28px;padding-top:20px;">
        <div style="display:inline-flex;align-items:center;gap:12px;
                    background:#0F172A;border-radius:16px;padding:14px 24px;">
            <span style="font-size:1.6rem;">🏥</span>
            <div style="text-align:left;">
                <div style="color:#FFFFFF;font-size:1rem;font-weight:700;">GeriCare Monitor</div>
                <div style="color:#64748B;font-size:0.72rem;">Elderly Diabetes Management System</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_choice_page():
    render_logo()
    st.markdown('<div style="font-size:1.6rem;font-weight:700;color:#0F172A;margin-bottom:4px;">Welcome back</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.9rem;color:#64748B;margin-bottom:20px;">Secure access to your patient monitoring dashboard</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;
                padding:10px 14px;font-size:0.82rem;color:#166534;margin-bottom:20px;
                font-family:'DM Mono',monospace;">
        Demo → Name: <b>Admin User</b> &nbsp;|&nbsp; Password: <b>admin123</b>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔐  Existing User Login", use_container_width=True):
            st.session_state.page_mode = "login"
            st.rerun()
    with c2:
        if st.button("✨  New User Sign Up", use_container_width=True):
            st.session_state.page_mode = "signup"
            st.rerun()


def show_existing_user_login():
    render_logo()
    st.markdown('<div style="font-size:1.6rem;font-weight:700;color:#0F172A;margin-bottom:4px;">Sign in</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.9rem;color:#64748B;margin-bottom:16px;">Enter your credentials to access the dashboard</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;
                padding:10px 14px;font-size:0.82rem;color:#166534;margin-bottom:16px;
                font-family:'DM Mono',monospace;">
        Demo → Name: <b>Admin User</b> &nbsp;|&nbsp; Password: <b>admin123</b>
    </div>
    """, unsafe_allow_html=True)

    full_name = st.text_input("Full Name", placeholder="e.g. Admin User", key="login_name")
    password  = st.text_input("Password", type="password", placeholder="Enter password", key="login_pw")

    if st.button("Sign In →", use_container_width=True):
        name = full_name.strip().title()
        if not name or not password.strip():
            st.error("Please enter both name and password.")
        else:
            user = login_user(name, password.strip())
            if user:
                st.session_state.logged_in  = True
                st.session_state.user_name  = name
                st.session_state.user_role  = user[5] if len(user) > 5 else "patient"
                st.session_state.current_page = "dashboard"
                st.rerun()
            else:
                st.error("Incorrect name or password.")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Forgot Password", use_container_width=True):
            st.session_state.page_mode = "recover"
            st.rerun()
    with c2:
        if st.button("← Back", use_container_width=True):
            st.session_state.page_mode = "choice"
            st.rerun()


def show_signup_page():
    render_logo()
    st.markdown('<div style="font-size:1.6rem;font-weight:700;color:#0F172A;margin-bottom:4px;">Create account</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.9rem;color:#64748B;margin-bottom:20px;">Set up your monitoring access</div>', unsafe_allow_html=True)

    full_name = st.text_input("Full Name", key="su_name")
    c1, c2   = st.columns(2)
    with c1: password = st.text_input("Password", type="password", key="su_pw")
    with c2: confirm  = st.text_input("Confirm Password", type="password", key="su_cpw")
    phone = st.text_input("Phone Number", key="su_phone")
    pin   = st.text_input("3-Digit Security PIN", max_chars=3, key="su_pin")

    if st.button("Create Account →", use_container_width=True):
        name = full_name.strip().title()
        if not all([name, password, confirm, phone, pin]):
            st.error("Please fill in all fields.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif not pin.isdigit() or len(pin) != 3:
            st.error("PIN must be exactly 3 digits.")
        elif not phone.strip().isdigit():
            st.error("Phone must contain digits only.")
        else:
            if add_user(name, password, phone, pin):
                st.success("Account created! Please sign in.")
                st.session_state.page_mode = "login"
                st.rerun()
            else:
                st.error("An account with this name already exists.")

    if st.button("← Back to Home", use_container_width=True):
        st.session_state.page_mode = "choice"
        st.rerun()


def show_recovery_page():
    render_logo()
    st.markdown('<div style="font-size:1.6rem;font-weight:700;color:#0F172A;margin-bottom:4px;">Recover access</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.9rem;color:#64748B;margin-bottom:20px;">Verify identity with your registered details</div>', unsafe_allow_html=True)

    full_name = st.text_input("Full Name", key="rec_name")
    phone     = st.text_input("Phone Number", key="rec_phone")
    pin       = st.text_input("3-Digit PIN", max_chars=3, key="rec_pin")

    if st.button("Verify Identity →", use_container_width=True):
        name = full_name.strip().title()
        user = recover_user(name, phone.strip(), pin.strip())
        if user:
            st.success(f"Verified. Your password is: **{user[2]}**")
        else:
            st.error("Details do not match our records.")

    if st.button("← Back to Login", use_container_width=True):
        st.session_state.page_mode = "login"
        st.rerun()


# ── Entry point ───────────────────────────────────────────────────────────────
def show_login_page():
    create_users_table()
    create_default_users()
    apply_login_styles()

    if "page_mode" not in st.session_state:
        st.session_state.page_mode = "choice"

    mode = st.session_state.page_mode
    if   mode == "choice":  show_choice_page()
    elif mode == "login":   show_existing_user_login()
    elif mode == "signup":  show_signup_page()
    elif mode == "recover": show_recovery_page()