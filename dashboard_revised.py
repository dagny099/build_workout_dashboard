"""
dashboard.py

Usage:
    Run this script from main directory to view the interactive dashboard
    $ ~/.local/bin/poetry python streamlit run python dashboard.py

Pre-requisites:
    $ ~/.local/bin/poetry run python init.py
    $ ~/.local/bin/poetry run python build_workout_dashboard/update_db.py
"""

from build_workout_dashboard.utilities import execute_query, get_db_connection
import streamlit as st
import plotly.express as px
import pandas as pd
import toml
import json
import os

# 0. Load dashboard style configuration from a JSON file
with open("build_workout_dashboard/style_config.json") as config_file:
    style_config = json.load(config_file)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .metric-container {
        border: 1px solid #d1d1d1;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        text-align: center;
        background-color: #f9f9f9;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Extract color and font styles from configuration
colors, font = style_config['colors'], style_config['font']

# 1. Load database configuration (.streamlit/secrets.toml)
with open(".streamlit/secrets.toml", "r") as f:
    dbconfig = toml.load(f)
    dbconfig = dbconfig['connections']['mysql']
    #del dbconfig['dialect']

# 2. Connect to the database
connection_type = st.sidebar.selectbox("Select Connection Type", ["Local", "Remote"], index=0)

# ADD LOGIC HERE TO TOGGLE dbconfig options based on connection_type
st.sidebar.write("Connecting to MySQL database...")
st.sidebar.write(dbconfig)

conn = get_db_connection(dbconfig=dbconfig)

# 3. Load data from the database
if "subset_query" not in st.session_state:
    st.session_state["subset_query"] = "SELECT * FROM workout_summary LIMIT 2"

subset_query = st.sidebar.text_area("Query table", value=st.session_state["subset_query"], max_chars=None)
st.session_state["subset_query"] = subset_query

response = execute_query(subset_query, dbconfig) 
df =  pd.DataFrame(response)


st.title("Workout Dashboard")

st.subheader("Workout Table")
st.write(f"Visibilty controlled by the sidebar; currently showing {df.shape[0]} rows.")
st.dataframe(df, hide_index=True)


# Create two containers for query input and results
st.subheader("Enter a custom SQL query")
query_container, response_container = st.columns(2)

# Query submission in the left container
with query_container:
    query = st.text_area("Enter SQL Query", placeholder="e.g., SELECT * FROM your_table")

    # Button to execute the query
    if st.button("Run Query"):
        with response_container:
            st.write("RESPONSE")
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()

                    # Display results
                    if rows:
                        for row in rows:
                            st.write(row)
                    else:
                        st.write("No results returned.")
            except Exception as e:
                st.error(f"Error executing query: {e}")
            finally:
                conn.close()

# ---------------------------------------------
 
# Static Visual Layout - Section 1: Weekly Summary
st.subheader("Statistics Calculated on Subset of Data")

total_workouts = df.shape[0]
avg_distance = round(df['distance_mi'].mean(), 2)
avg_duration = round(df['duration_sec'].mean(), 2)
avg_calories = round(df['kcal_burned'].mean(), 2)
fastest_speed = round(df['max_pace'].max(), 2)

metrics = [
    {"label": "Total Workouts", "value": total_workouts, "color": colors["distance"]},
    {"label": "Avg Distance", "value": f"{avg_distance} km", "color": colors["distance"]},
    {"label": "Avg Duration", "value": f"{avg_duration} min", "color": colors["duration"]},
    {"label": "Avg Calories", "value": f"{avg_calories} kcal", "color": colors["calories"]},
    {"label": "Fastest Speed", "value": f"{fastest_speed} km/h", "color": colors["speed"]},
]

col1, col2, col3 = st.columns(3)  # Three columns in a row

# Display metrics
with col1:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(label= metrics[0]['label'], value=metrics[0]['value'], help= "Total number of workouts")
    # st.metric(label= metrics[1]['label'], value=metrics[1]['value'], help= "Average distance in miles")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(label= metrics[2]['label'], value=metrics[2]['value'], help= "Average duration in seconds")
    st.metric(label= metrics[3]['label'], value=metrics[3]['value'], help= "Average calories burned")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.metric(label= metrics[4]['label'], value=metrics[4]['value'])
    st.markdown('</div>', unsafe_allow_html=True)


# # Render each metric dynamically
# for metric in metrics:
#     st.markdown(
#         f"""
#         <div style="display: inline-block; text-align: center; width: 20%; color: {metric['color']}">
#             <h3 style="font-family: {font['heading']};">{metric['label']}</h3>
#             <p style="font-family: {font['data_label']}; font-size: 24px;">{metric['value']}</p>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# Section 2: Interactive Trend Chart Placeholder
st.subheader("Trend Analysis")
metric_choice = st.selectbox("Select a metric to view trend:", ["Distance", "Duration", "Calories", "Speed"])
st.line_chart([1, 2, 3, 4, 5])  # Placeholder line chart data

# Example footer or additional space for future interactivity
st.markdown("<div style='padding: 20px'></div>", unsafe_allow_html=True)


# if st.checkbox("Show Charts"):
#     fig = px.line(df, x='date', y='steps', title="Daily Exercise Steps")
#     st.plotly_chart(fig)


