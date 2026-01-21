import streamlit as st
import time

st.set_page_config(page_title="Accounting Marathon", layout="centered")

# ----------------------------
# QUESTIONS DATABASE (MVP)
# ----------------------------
questions = [
    {
        "question": "Security deposit received from tenant should be recorded as:",
        "options": [
            "Rental Income",
            "Liability",
            "Accounts Receivable",
            "Owner Contribution"
        ],
        "answer": "Liability"
    },
    {
        "question": "Loan taken from bank will increase which account?",
        "options": [
            "Expense",
            "Income",
            "Asset",
            "Liability"
        ],
        "answer": "Liability"
    },
    {
        "question": "Owner withdrawal should be recorded as:",
        "options": [
            "Expense",
            "Equity / Draw",
            "Liability",
            "Income"
        ],
        "answer": "Equity / Draw"
    }
]

transaction_questions = [
    {
        "transaction": "Paid office rent from bank",
        "correct_account": "Rent Expense",
        "correct_dc": "Debit"
    },
    {
        "transaction": "Received rent from tenant",
        "correct_account": "Rental Income",
        "correct_dc": "Credit"
    }
]

# ----------------------------
# SESSION STATE
# ----------------------------
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "score" not in st.session_state:
    st.session_state.score = 0

# ----------------------------
# UI
# ----------------------------
st.title("🏁 Accounting Marathon")
st.write("Test your accounting skills. Results shown instantly.")

name = st.text_input("Enter your name")

if st.button("Start Test"):
    st.session_state.start_time = time.time()
    st.session_state.score = 0

# ----------------------------
# MCQ SECTION
# ----------------------------
if st.session_state.start_time:
    st.subheader("🧠 Round 1: Accounting Basics")

    for q in questions:
        user_answer = st.radio(q["question"], q["options"], key=q["question"])
        if user_answer == q["answer"]:
            st.session_state.score += 1

    # ----------------------------
    # TRANSACTION CLASSIFICATION
    # ----------------------------
    st.subheader("🧾 Round 2: Transaction Classification")

    for t in transaction_questions:
        st.write(f"**Transaction:** {t['transaction']}")
        acc = st.text_input("Account Name", key=t["transaction"] + "acc")
        dc = st.selectbox("Debit / Credit", ["Debit", "Credit"], key=t["transaction"] + "dc")

        if acc.strip().lower() == t["correct_account"].lower() and dc == t["correct_dc"]:
            st.session_state.score += 2

    # ----------------------------
    # SUBMIT
    # ----------------------------
    if st.button("Submit Test"):
        end_time = time.time()
        time_taken = round(end_time - st.session_state.start_time, 2)

        st.success("✅ Test Completed")

        st.subheader("📊 Results")
        st.write(f"👤 Name: **{name}**")
        st.write(f"🏆 Score: **{st.session_state.score}**")
        st.write(f"⏱ Time Taken: **{time_taken} seconds**")

        if st.session_state.score >= 8:
            st.success("CPA READY 🔥")
        elif st.session_state.score >= 5:
            st.warning("GOOD – Needs Improvement")
        else:
            st.error("BASICS WEAK – Training Required")
