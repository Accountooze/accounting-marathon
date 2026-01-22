import os
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables (LOCAL ONLY)
# Render ignores .env automatically
# --------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

st.set_page_config(page_title="Accounting Marathon", layout="wide")

st.title("🏁 Accounting Marathon – DB Health Check")

# --------------------------------------------------
# Validate ENV
# --------------------------------------------------
if not DATABASE_URL:
    st.error("❌ DATABASE_URL is not set")
    st.stop()

st.success("✅ DATABASE_URL loaded")

# --------------------------------------------------
# Create SQLAlchemy Engine
# --------------------------------------------------
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    st.success("✅ SQLAlchemy engine created")
except Exception as e:
    st.error("❌ Failed to create engine")
    st.exception(e)
    st.stop()

# --------------------------------------------------
# Test DB Connection
# --------------------------------------------------
try:
    with engine.begin() as conn:
        result = conn.execute(text("SELECT NOW();"))
        current_time = result.scalar()
    st.success(f"✅ Connected to PostgreSQL at {current_time}")
except Exception as e:
    st.error("❌ Database connection failed")
    st.exception(e)
    st.stop()

# --------------------------------------------------
# Create Sample Table
# --------------------------------------------------
create_table_sql = """
CREATE TABLE IF NOT EXISTS marathon_users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

try:
    with engine.begin() as conn:
        conn.execute(text(create_table_sql))
    st.success("✅ Table `marathon_users` ready")
except Exception as e:
    st.error("❌ Table creation failed")
    st.exception(e)

# --------------------------------------------------
# Insert Sample Data
# --------------------------------------------------
if st.button("➕ Add Sample User"):
    try:
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO marathon_users (name, score) VALUES (:n, :s)"),
                {"n": "Test User", "s": 10},
            )
        st.success("🎉 Sample user added")
    except Exception as e:
        st.error("Insert failed")
        st.exception(e)

# --------------------------------------------------
# Display Leaderboard
# --------------------------------------------------
st.subheader("🏆 Leaderboard")

try:
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT name, score, created_at FROM marathon_users ORDER BY score DESC")
        ).fetchall()

    if rows:
        st.table(rows)
    else:
        st.info("No users yet")
except Exception as e:
    st.error("Failed to load leaderboard")
    st.exception(e)
