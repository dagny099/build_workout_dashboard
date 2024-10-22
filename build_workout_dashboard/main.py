from build_workout_dashboard.utilities import *

# Load the pyproject.toml file
with open("pyproject.toml", "r") as f:
    config = toml.load(f)

dbConfig = config['tool']['project']['database']
input_filepath = config['tool']['poetry']['name'].replace('-', '_') + os.path.sep + config['tool']['project']['input_filename']

## 0 - DISPLAY DATABASES VISIBLE TO THIS USER:
connection = mysql.connector.connect(**dbConfig)
cursor = connection.cursor()

cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()   # Fetch all results
print("Databases visible to your user:")
for db in databases:            # Print the databases
    print(db[0])
print("-----------------------------\n")


## 1a- Read CSV file with all data
print(f'Reading data from {input_filepath}')
df = pd.read_csv(input_filepath)

## 1b- Preprocessing
df = clean_data(df)         # Clean data
df = enrich_data(df)        # Enrich data (for now, just extract workoutID)

## 2- Import into database (see config in pyproject.toml)
try:
    # Establish MySQL connection
    connection = mysql.connector.connect(**dbConfig)

    if connection.is_connected():
        cursor = connection.cursor()

        # Setup database and table
        setup_database(cursor)

        # Insert data
        rows_affected = insert_data_NEW(cursor, df)

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
        