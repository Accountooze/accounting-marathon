from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import time
import os
from sqlalchemy import create_engine, text


# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Accountooze Accounting Marathon",
    layout="centered"
)

# =================================================
# BRANDING
# =================================================
st.markdown("""
<style>
.block-container { padding-top: 2rem; }
body { background-color: #f6f8fb; }
h1, h2, h3 { color: #0f2a44; }

.stButton button {
    background-color: #0f2a44;
    color: white;
    border-radius: 6px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
}

.accountooze-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    margin-bottom: 1.5rem;
}

.footer {
    text-align: center;
    font-size: 0.85rem;
    color: #777;
    margin-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

# =================================================
# DATABASE
# =================================================
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# =================================================
# CREATE TABLE
# =================================================
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            name TEXT,
            team TEXT,
            score INT,
            time_taken FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """))

# =================================================
# QUESTIONS
# =================================================
MCQS = [
    ("Security deposit received from tenant should be recorded as:",
     "Liability",
     ["Rental Income", "Liability", "Accounts Receivable", "Owner Contribution"]),

    ("Loan taken from bank will increase which account?",
     "Liability",
     ["Expense", "Income", "Asset", "Liability"]),

    ("Owner withdrawal should be recorded as:",
     "Equity / Draw",
     ["Expense", "Equity / Draw", "Liability", "Income"]),

    ("Which report does a CPA review first at tax time?",
     "Balance Sheet",
     ["Profit & Loss", "Trial Balance", "Balance Sheet", "Cash Flow"]),

    ("Security deposits should appear on which report?",
     "Balance Sheet",
     ["Profit & Loss", "Balance Sheet", "Cash Flow", "AR Aging"]),
]

BANK_TASKS = [
    {
        "description": "AMZN Mktp US*2A45 Office Supplies Seattle",
        "vendor": "amazon",
        "gl": "Office Supplies Expense"
    },
    {
        "description": "UBER *TRIP HELP.UBER.COM",
        "vendor": "uber",
        "gl": "Travel Expense"
    },
    {
        "description": "COMCAST CABLE INTERNET",
        "vendor": "comcast",
        "gl": "Internet Expense"
    }
]

GL_OPTIONS = [
    "Office Supplies Expense",
    "Travel Expense",
    "Internet Expense",
    "Repairs & Maintenance",
    "Rent Expense",
    "Advertising Expense"
]

# =================================================
# SESSION STATE
# =================================================
for key in ["started", "submitted", "score", "start_time", "name", "team"]:
    if key not in st.session_state:
        st.session_state[key] = None

# =================================================
# HEADER
# =================================================
st.markdown("""
<div class="accountooze-card">
<h1>Accountooze Accounting Marathon</h1>
<p>Real-world accounting skill evaluation</p>
</div>
""", unsafe_allow_html=True)

# =================================================
# START SCREEN
# =================================================
if not st.session_state.started:
    st.markdown('<div class="accountooze-card">', unsafe_allow_html=True)

    name = st.text_input("Your Name")
    team = st.text_input("Team / Department")

    if st.button("Start Test"):
        if not name or not team:
            st.error("Please enter Name and Team")
        else:
            st.session_state.name = name.strip()
            st.session_state.team = team.strip()
            st.session_state.started = True
            st.session_state.score = 0
            st.session_state.start_time = time.time()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =================================================
# TEST
# =================================================
elif not st.session_state.submitted:

    # -------- MCQs --------
    st.markdown('<div class="accountooze-card">', unsafe_allow_html=True)
    st.subheader("🧠 MCQs")

    for q, correct, options in MCQS:
        ans = st.radio(q, options, key=q)
        if ans == correct:
            st.session_state.score += 1

    st.markdown('</div>', unsafe_allow_html=True)

    # -------- BANK TASK --------
    st.markdown('<div class="accountooze-card">', unsafe_allow_html=True)
    st.subheader("🏦 Bank Transaction Classification")

    for i, task in enumerate(BANK_TASKS):
        st.write(f"**Bank Description:** {task['description']}")
        vendor_input = st.text_input("Vendor Name", key=f"vendor_{i}")
        gl_input = st.selectbox("GL Account", GL_OPTIONS, key=f"gl_{i}")

        if vendor_input.strip().lower() == task["vendor"]:
            st.session_state.score += 1
        if gl_input == task["gl"]:
            st.session_state.score += 2

    if st.button("Submit Test"):
        st.session_state.submitted = True
        st.session_state.end_time = time.time()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =================================================
# RESULTS + LEADERBOARD
# =================================================
else:
    time_taken = round(st.session_state.end_time - st.session_state.start_time, 2)

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO results (name, team, score, time_taken)
                VALUES (:n, :t, :s, :tt)
            """),
            {
                "n": st.session_state.name,
                "t": st.session_state.team,
                "s": st.session_state.score,
                "tt": time_taken
            }
        )

        leaderboard = conn.execute(text("""
            SELECT name, team, score, time_taken
            FROM results
            ORDER BY score DESC, time_taken ASC
            LIMIT 10
        """)).fetchall()

    st.markdown('<div class="accountooze-card">', unsafe_allow_html=True)
    st.success("✅ Test Completed")
    st.write(f"Name: **{st.session_state.name}**")
    st.write(f"Team: **{st.session_state.team}**")
    st.write(f"Score: **{st.session_state.score}**")
    st.write(f"Time Taken: **{time_taken} seconds**")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="accountooze-card">', unsafe_allow_html=True)
    st.subheader("🏆 Leaderboard")
    st.table(leaderboard)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()

# =================================================
# FOOTER
# =================================================
st.markdown("""
<div class="footer">
© 2026 Accountooze Outstaffing · Accounting Training Platform
</div>
""", unsafe_allow_html=True)
 
 