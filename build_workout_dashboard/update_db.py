"""
update_db.py

Usage:
    Run this script from main directory to update the database with new workout data from a CSV file.
    $ ~/.local/bin/poetry run python build_workout_dashboard/update_db.py

    Nothing is added if CSV file already is consistent with the database.

Pre-requisites:
    $ ~/.local/bin/poetry run python init.py     # Initialize the database
"""

from build_workout_dashboard.utilities import insert_data, clean_data, enrich_data
import os
import toml
import pandas as pd
import pymysql

# ----------------------------------------------
# Get the project & database configuration
with open("pyproject.toml", "r") as f:
    config = toml.load(f)

# Get the input file path: for `user2632022_workout_history.csv`
input_filepath = 'build_workout_dashboard' + os.path.sep + config['tool']['project']['input_filename'] 
print(input_filepath)
# Load the CSV file with full workout history
if os.path.exists(input_filepath):
    print(f'\n-------\nImporting this full workout CSV file: {input_filepath}')
    df = pd.read_csv(input_filepath)
else:
    print(f"File {input_filepath} not found. Please check the path in pyproject.toml")
    exit(1)

# Prepare data for import into database
df = clean_data(df)         
df = enrich_data(df)        # Enrich data (for now, just extract workoutID)

print(f"Workout CSV has {df.shape[0]} entries (includes entries probably already in db)")

tablename = "workout_summary"

# ----------------------------------------------
# DATABASE INTERACTIONS START HERE

# 1. Load database configuration (.streamlit/secrets.toml)
with open(".streamlit/secrets.toml", "r") as f:
    dbconfig = toml.load(f)
    dbconfig = dbconfig['connections']['mysql']
    print(f"\n-------\nUsing this Databse configuration:")    
    print(dbconfig)    

# 2. Connect to the database
connection = pymysql.connect(
        host=dbconfig["host"],
        port=dbconfig["port"],
        user=dbconfig["username"],
        password=dbconfig["password"],
        database = dbconfig["database"]
)

# 3. Insert new workouts into table
with connection.cursor() as cursor:

    # Check which workout_ids already exist in the table
    cursor.execute("SELECT workout_id FROM workout_summary")
    existing_workout_ids = [row[0] for row in cursor.fetchall()]

    # Exclude existing workout_ids from the new data
    newDf = df[~df['workout_id'].isin(existing_workout_ids)]  
    print(f"\n-------\nExisting workouts in table: {len(existing_workout_ids)} | New workouts to import: {newDf.shape[0]}")

    # INSERT NEW WORKOUTS IN TABLE
    rows_affected = insert_data(newDf)
    print(f"Inserted {rows_affected} rows into {tablename}")

# 11/22/24 NOT SURE WHY BUT THIS GIVES WRONG VALUE IF THE INSERT_DATA FUNCTION ACTUALLY INSERTED ROWS
# with connection.cursor() as cursor:
#     # Get the total number of rows in the table -
#     cursor.execute("SELECT COUNT(*) FROM workout_summary")
#     total_rows = cursor.fetchone()[0]
#     print(f"Total rows in the table after insert: {total_rows}")

# 6. Close the connection
cursor.close()
connection.close()
print("MySQL connection is closed")
print("-------\n")        
        

# # (Optional) Check how many rows are in the table
# with connection.cursor() as cursor:
#     cursor.execute(f"SELECT COUNT(*) FROM {tablename};")
#     total_rows = cursor.fetchone()[0]
#     print(f"Table {dbconfig['database']}.{tablename} has {total_rows} rows")    

# # (Optional) Check the last inserted ID
#     # Get the last inserted id
#     cursor.execute("SELECT LAST_INSERT_ID()")
#     last_id = cursor.fetchone()[0]
#     print(f"The last inserted ID was: {last_id}")

