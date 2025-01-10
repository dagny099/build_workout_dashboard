"""
dashboard.py

Usage:
    Run this script from main directory to view the interactive dashboard
    $ ~/.local/bin/poetry python streamlit run python dashboard.py

Pre-requisites:
    $ ~/.local/bin/poetry run python init.py
    $ ~/.local/bin/poetry run python build_workout_dashboard/update_db.py
"""

# from build_workout_dashboard.utilities import load_data
import streamlit as st
import plotly.express as px
import pandas as pd
import toml
import json
import os
import mysql.connector
# import pymysql

# 0. Load dashboard style configuration from a JSON file
with open("build_workout_dashboard/style_config.json") as config_file:
    style_config = json.load(config_file)

# Extract color and font styles from configuration
colors, font = style_config['colors'], style_config['font']

# 1. Load database configuration (.streamlit/secrets.toml)
with open(".streamlit/secrets.toml", "r") as f:
    dbconfig = toml.load(f)
    dbconfig = dbconfig['connections']['mysql']
    del dbconfig['dialect']

# IF PROD: use RDS on AWS instead of localhost
with open("pyproject.toml", "r") as f:
    proj_config = toml.load(f)

# if not(proj_config['tool']['project']['debug']):
if False:
    print("Using remote database configuration.")
    dbconfig['host'] = os.getenv('RDS_ENDPOINT')
    dbconfig['username'] = os.getenv('RDS_USER')
    dbconfig['password'] = os.getenv('RDS_PASSWORD')
    dbconfig['port'] = 3306
    dbconfig['database'] = 'sweat-'

# 2. Connect to the database
if 'connection' not in globals():
    st.sidebar.write("Connecting to MySQL database...")
    st.sidebar.write(dbconfig)
    print(f"\n-------\nUsing this Databse configuration:")    
    print(dbconfig)    

    connection = mysql.connector.connect(**dbconfig)
#     connection = pymysql.connect(
#         host=dbconfig["host"],
#         port=dbconfig["port"],
#         user=dbconfig["username"],
#         password=dbconfig["password"],
#         database = dbconfig["database"]
# )

# 3. Load data from the database
# df = load_data("SELECT * FROM workout_summary")
cursor = connection.cursor()
cursor.execute("SELECT * FROM workout_summary")
data = cursor.fetchall()  # Get all rows of the result
# cursor.close()
column_names = [i[0] for i in cursor.description]  # Get column names
df = pd.DataFrame(data, columns=column_names)  # Convert the data into a Pandas DataFrame

total_workouts = df.shape[0]
avg_distance = round(df['distance_mi'].mean(), 2)
avg_duration = round(df['duration_sec'].mean(), 2)
avg_calories = round(df['kcal_burned'].mean(), 2)
fastest_speed = round(df['max_pace'].max(), 2)

# Generate summary layout programmatically
metrics = [
    {"label": "Total Workouts", "value": total_workouts, "color": colors["distance"]},
    {"label": "Avg Distance", "value": f"{avg_distance} km", "color": colors["distance"]},
    {"label": "Avg Duration", "value": f"{avg_duration} min", "color": colors["duration"]},
    {"label": "Avg Calories", "value": f"{avg_calories} kcal", "color": colors["calories"]},
    {"label": "Fastest Speed", "value": f"{fastest_speed} km/h", "color": colors["speed"]},
]

# Static Visual Layout - DEMO

st.title("Workout Dashboard")

st.subheader("Workout Table")
st.write(f"Rows in database total: {total_workouts}")
st.dataframe(df)

# Static Visual Layout - Section 1: Weekly Summary
st.subheader("Current Week Summary")

# Render each metric dynamically
for metric in metrics:
    st.markdown(
        f"""
        <div style="display: inline-block; text-align: center; width: 20%; color: {metric['color']}">
            <h3 style="font-family: {font['heading']};">{metric['label']}</h3>
            <p style="font-family: {font['data_label']}; font-size: 24px;">{metric['value']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Section 2: Interactive Trend Chart Placeholder
st.subheader("Trend Analysis")
metric_choice = st.selectbox("Select a metric to view trend:", ["Distance", "Duration", "Calories", "Speed"])
st.line_chart([1, 2, 3, 4, 5])  # Placeholder line chart data

# Example footer or additional space for future interactivity
st.markdown("<div style='padding: 20px'></div>", unsafe_allow_html=True)

# # Close the cursor and connection
# connection.close()
# print("MySQL connection is closed")
# print("-------\n")        


# if st.checkbox("Show Charts"):
#     fig = px.line(df, x='date', y='steps', title="Daily Exercise Steps")
#     st.plotly_chart(fig)


