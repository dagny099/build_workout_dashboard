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

# 1. Connect to the database
connection_type = st.sidebar.selectbox("Select Connection Type", ["Local", "Remote"], index=0)

# 1. Load database configuration (.streamlit/secrets.toml)
if connection_type == "Local":
    with open(".streamlit/secrets.toml", "r") as f:
        dbconfig = toml.load(f)
        dbconfig = dbconfig['connections']['mysql']
        #del dbconfig['dialect']
else:
    dbconfig = {
        "host": os.getenv("RDS_ENDPOINT"),
        "port": 3306,
        "username": os.getenv("RDS_USER"),
        "password": os.getenv("RDS_PASSWORD"),
        "database": 'sweat-mapmyrun-rds',
    }

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

# Date range selection
start_date = st.date_input("Start Date", value=df["workout_date"].min())
end_date = st.date_input("End Date", value=df["workout_date"].max())

# Dropdown menu for aggregation
aggregation = st.selectbox("Select Aggregation Level", ["Days", "Weeks", "Months", "Years"])

# Dropdown menu for Y-axis metric
y_axis_metric = st.selectbox(
    "Select Y-Axis Metric",
    [
        "total_workouts",
        "avg_distance",
        "avg_duration",
        "avg_calories",
        "fastest_speed"
    ],
    format_func=lambda x: x.replace("_", " ").title()
)

# Filter data based on the date range
filtered_df = df[(df["workout_date"] >= pd.to_datetime(start_date)) & (df["workout_date"] <= pd.to_datetime(end_date))]

# Aggregate data based on the selected aggregation
if aggregation == "Days":
    filtered_df["time_group"] = filtered_df["workout_date"].dt.date
elif aggregation == "Weeks":
    filtered_df["time_group"] = filtered_df["workout_date"].dt.to_period("W").apply(lambda r: r.start_time)
elif aggregation == "Months":
    filtered_df["time_group"] = filtered_df["workout_date"].dt.to_period("M").apply(lambda r: r.start_time)
elif aggregation == "Years":
    filtered_df["time_group"] = filtered_df["workout_date"].dt.to_period("Y").apply(lambda r: r.start_time)

# Define the y-axis metric
# Aggregate metrics
aggregated_df = filtered_df.groupby("time_group").agg(
    total_workouts=("workout_date", "count"),
    avg_distance=("distance_mi", "mean"),
    avg_duration=("duration_sec", "mean"),
    avg_calories=("kcal_burned", "mean"),
    fastest_speed=("avg_pace", "min")
).reset_index()

# Display the aggregated data
st.write("Filtered and Aggregated Data")
st.dataframe(aggregated_df)

# Plotly bar chart
fig = px.bar(
    aggregated_df,
    x="time_group",
    y=y_axis_metric,
    title=f"Time Series of {y_axis_metric.replace('_', ' ').title()}",
    labels={
        "time_group": "Time Group",
        y_axis_metric: y_axis_metric.replace("_", " ").title()
    },
    text_auto=True  # Display values on bars
)
st.plotly_chart(fig)

