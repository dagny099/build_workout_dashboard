import streamlit as st
import plotly.express as px

from utilities import *
import toml
import os

# LOAD pyproject.toml file
with open("pyproject.toml", "r") as f:
    config = toml.load("pyproject.toml")

# Get database configuration
dbConfig = config['tool']['project']['database']

# Get input file path
input_filepath = config['tool']['poetry']['name'].replace('-', '_') + os.path.sep + config['tool']['project']['input_filename']

# IF PROD: use RDS on AWS instead of localhost
if not(config['tool']['project']['debug']):
    print("Using production database configuration.")
    dbConfig['host'] = os.getenv('RDS_ENDPOINT')
    dbConfig['username'] = os.getenv('RDS_USER')
    dbConfig['password'] = os.getenv('RDS_PASSWORD')

# Establish mysql connection (no database specified)
print("Connecting to MySQL database...")
print(dbConfig)
connection = mysql.connector.connect(**dbConfig)
cursor = connection.cursor()

# Return list of existing databases
cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()                  # Fetch all results
databases = [item[0] for item in databases]    # Convert tuple responses to a list

# Stop if database doesn't exist
dbConfig['database'] = "sweat"
if dbConfig['database'] not in databases:
    print(f"No database named {dbConfig['database']} in {dbConfig['host']};")  
else:
    # Return df from "sweat.workout_summary" table
    cursor = connection.cursor()
    cursor.execute(f"USE {dbConfig['database']}")
    cursor.execute("SELECT * FROM workout_summary;")

    # Fetch the data and column names
    data = cursor.fetchall()  # Get all rows of the result
    column_names = [i[0] for i in cursor.description]  # Get column names

    # Step 4: Convert the data into a Pandas DataFrame
    DF = pd.DataFrame(data, columns=column_names).sort_values(by='workout_date', ascending=True).reset_index(drop=True)

    # ------------------------------------------
    # Streamlit app layout
    st.title("Exercise Dashboard")
    st.subheader("Activity Overview")

    # Group data for weekly aggregations
    weekly_data = DF.groupby(
        ['activity_type', pd.Grouper(key='workout_date', freq='W')]
    ).agg({
        'workout_id': 'count',
        'distance_mi': 'mean',
        'duration_sec': lambda x: x.mean() / 60,
        'avg_pace': 'mean',
        'kcal_burned': 'sum'
    }).reset_index()

    # Select activity type for plotting
    activity_filter = st.selectbox("Select Activity Type", weekly_data['activity_type'].unique())

    filtered_data = weekly_data[weekly_data['activity_type'] == activity_filter]

    # Plot the metrics using Plotly
    fig = px.line(filtered_data, x='workout_date', y='workout_id', title=f'{activity_filter} - Number of Workouts Per Week')
    st.plotly_chart(fig)

    # Additional metrics (distance, duration, pace, kcal)
    st.write(f"Average Distance: {filtered_data['distance_mi'].mean():.2f} miles")
    st.write(f"Average Duration: {filtered_data['duration_sec'].mean():.2f} minutes")
    st.write(f"Average Pace: {filtered_data['avg_pace'].mean():.2f} min/mile")
    st.write(f"Total Calories Burned: {filtered_data['kcal_burned'].sum():.2f} kcal")

    # st.write(DF)


