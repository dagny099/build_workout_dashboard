from build_workout_dashboard.utilities import *
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

# Establish myssql connection (no database specified)
print("Connecting to MySQL database...")
print(dbConfig)
connection = mysql.connector.connect(**dbConfig)
cursor = connection.cursor()

print("Databases visible to your user:")
cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()                  # Fetch all results
databases = [item[0] for item in databases]    # Convert tuple responses to a list
for db in databases:           
    print(db)
print("-----------------------------\n")


# INITIALIZE DATABASE, if it doesn't exist 
dbConfig['database'] = "sweat"

if dbConfig['database'] not in databases:
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbConfig['database']};")    
    print(f"Created database: {dbConfig['database']};")  

# INITIALIZE TABLE, if it doesn't exist
setup_database(cursor, dbConfig)

# Get list of existing workout_ids in Db
cursor = connection.cursor()
cursor.execute(f"USE {dbConfig['database']}")
cursor.execute("SELECT workout_id FROM workout_summary")
existing_workout_ids = [row[0] for row in cursor.fetchall()]

# ----------------------------------------------
# IMPORT DATA INTO DATABASE

# 1a- Read CSV file with all data
print(f'\nReading data from {input_filepath}')
df = pd.read_csv(input_filepath)

## 1b- Preprocessing
df = clean_data(df)         # Clean data
df = enrich_data(df)        # Enrich data (for now, just extract workoutID)

## 2- Filter out rows that already exist in the database
newDf = df[~df['workout_id'].isin(existing_workout_ids)]
print(f"\nNumber of rows to import: {newDf.shape[0]}\n")

## 3- Import into database (see config in pyproject.toml)
try:
    # Establish MySQL connection
    if 'connection' not in locals():
        print("Connecting to MySQL database...")
        print(dbConfig)
        connection = mysql.connector.connect(**dbConfig)

    # If connection was lost, either reconnect OR re-establish cursor
    if not(connection.is_connected()):
        cursor = connection.cursor()        

    # Insert data
    rows_affected = insert_data_NEW(cursor, newDf)

    # Commit changes
    connection.commit()

    print(f"Data import completed. {rows_affected} rows were inserted.")

    # Get the last inserted id
    cursor.execute("SELECT LAST_INSERT_ID()")
    last_id = cursor.fetchone()[0]
    print(f"The last inserted ID was: {last_id}")

    # Get the total number of rows in the table
    cursor.execute("SELECT COUNT(*) FROM workout_summary")
    total_rows = cursor.fetchone()[0]
    print(f"Total rows in the table after insert: {total_rows}")

except Error as e:
    print(f"Error: {e}")
    print(f"Error Code: {e.errno}")
    print(f"SQLSTATE: {e.sqlstate}")
    print(f"Message: {e.msg}")
    
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
        
        