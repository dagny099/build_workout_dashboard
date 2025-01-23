"""
test_persistence.py

Simple script to test session storage and persistence functionality.
Run this script multiple times to verify data persists between runs.
"""

import streamlit as st
from session_manager import SessionManager
import time

def main():
    st.title("Session Persistence Test")
    
    # Initialize SessionManager
    session_mgr = SessionManager()
    
    # Display current session ID
    st.write(f"Current Session ID: {st.session_state.session_id}")
    
    # Test Scratchpad
    st.subheader("Scratchpad Test")
    current_notes = session_mgr.get_scratchpad()
    new_notes = st.text_area("Scratchpad", value=current_notes)
    if new_notes != current_notes:
        session_mgr.update_scratchpad(new_notes)
        st.success("Scratchpad updated!")
    
    # Test Query History
    st.subheader("Query History Test")
    if st.button("Add Test Query"):
        test_query = f"SELECT * FROM test_table -- Test query at {time.strftime('%H:%M:%S')}"
        session_mgr.add_query_to_history(
            query=test_query,
            result={'execution_time': 0.1, 'row_count': 5}
        )
        st.success("Test query added to history!")
    
    # Display Query History
    history = session_mgr.get_query_history()
    st.write(f"Total queries in history: {len(history)}")
    for idx, record in enumerate(history):
        with st.expander(f"Query {idx + 1}"):
            st.code(record['query'])
            st.write(f"Timestamp: {record['timestamp']}")
    
    # Test Saved Queries
    st.subheader("Saved Queries Test")
    if st.button("Add Test Saved Query"):
        session_mgr.add_saved_query(
            query=f"SELECT count(*) FROM test_table -- Saved at {time.strftime('%H:%M:%S')}",
            name=f"Test Query {time.strftime('%H:%M:%S')}",
            description="Test saved query"
        )
        st.success("Test query saved!")
    
    # Display Saved Queries
    saved_queries = session_mgr.get_saved_queries()
    st.write(f"Total saved queries: {len(saved_queries)}")
    for idx, query in enumerate(saved_queries):
        with st.expander(f"Saved Query {idx + 1}"):
            st.write(f"Name: {query['name']}")
            st.code(query['query'])
            st.write(f"Description: {query['description']}")
    
    # Database Inspection
    st.subheader("Storage Database Content")
    from storage import SQLiteAdapter
    adapter = SQLiteAdapter()
    import sqlite3
    
    with sqlite3.connect(adapter.db_path) as conn:
        cursor = conn.execute("SELECT session_id, created_at, updated_at FROM sessions")
        rows = cursor.fetchall()
        
        st.write("Sessions in database:")
        for row in rows:
            st.write(f"- Session {row[0]}")
            st.write(f"  Created: {row[1]}")
            st.write(f"  Updated: {row[2]}")

if __name__ == "__main__":
    main()