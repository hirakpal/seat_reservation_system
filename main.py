import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel
from typing import TypedDict, List

# --- 1. Database Layer ---
def init_db():
    conn = sqlite3.connect("railway.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS seats (seat_id INTEGER PRIMARY KEY, status TEXT DEFAULT 'available', user_id TEXT, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    if cursor.execute("SELECT count(*) FROM seats").fetchone()[0] == 0:
        cursor.executemany("INSERT INTO seats (seat_id, status) VALUES (?, ?)", [(i, 'available') for i in range(1, 6)])
    conn.commit(); conn.close()

def get_data(): return pd.read_sql("SELECT * FROM seats ORDER BY seat_id", sqlite3.connect("railway.db"))

def update_seat(seat_id, status, user_id=None):
    conn = sqlite3.connect("railway.db")
    if status == 'booked':
        success = conn.execute("UPDATE seats SET status='booked', user_id=? WHERE seat_id=? AND status='available'", (user_id, seat_id)).rowcount > 0
    else:
        success = conn.execute("UPDATE seats SET status='available', user_id=NULL WHERE seat_id=? AND user_id=?", (seat_id, user_id)).rowcount > 0
    conn.commit(); conn.close()
    return success

# --- 2. Logic Layer (Agents) ---
def run_action(task, seat_id, user):
    if "Book" in task: return f"Booking: {'Success' if update_seat(seat_id, 'booked', user) else 'Failed'}"
    if "Cancel" in task: return f"Cancellation: {'Success' if update_seat(seat_id, 'available', user) else 'Failed'}"
    if "Status" in task: 
        row = sqlite3.connect("railway.db").execute("SELECT status, user_id FROM seats WHERE seat_id=?", (seat_id,)).fetchone()
        return f"Seat {seat_id}: {row[0]} (User: {row[1] or 'None'})"
    return f"Available seats: {list(pd.read_sql('SELECT seat_id FROM seats WHERE status=\"available\"', sqlite3.connect('railway.db'))['seat_id'])}"

# --- 3. Orchestrator ---
class State(TypedDict): task: str; seat_id: int; user: str; history: List[str]
graph_builder = StateGraph(State)
graph_builder.add_node("agent", lambda s: {"history": [run_action(s['task'], s['seat_id'], s['user'])]})
graph_builder.set_entry_point("agent"); graph_builder.add_edge("agent", END)
graph = graph_builder.compile(checkpointer=MemorySaver())

# --- 4. Streamlit UI ---
st.set_page_config(layout="wide")
st.title("🚆 AI Railway Reservation")
init_db()

col1, col2 = st.columns([1, 2])
with col1:
    action = st.radio("Action:", ["See Availability", "Book Seat", "Cancel Seat", "Search Seat Status"])
    sid = st.number_input("Seat ID:", 1, 5) if "Availability" not in action else None
    if st.button("Process"):
        res = graph.invoke({"task": action, "seat_id": sid, "user": "user1"}, {"configurable": {"thread_id": "user1"}})
        st.success(res['history'][0])
        st.rerun()

with col2:
    st.subheader("Live Status")
    st.table(get_data())
