import toml
import pandas as pd
import numpy as np
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import re
import os


# Function to create database and table
def setup_database(cursor):
    """
    Function to create database and table if they don't exist
    """
    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS sweat")
    cursor.execute("USE sweat")
    
    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_summary (
        id INT AUTO_INCREMENT PRIMARY KEY,
        workout_date DATETIME,
        activity_type VARCHAR(50),
        kcal_burned BIGINT,
        distance_mi FLOAT,
        duration_sec FLOAT,
        avg_pace FLOAT,
        max_pace FLOAT,
        steps BIGINT,
        link VARCHAR(100),
        workout_id VARCHAR(20)
    )
    """)

# Custom date parsing function
def parse_date(date_string):
    """Function to parse date strings in various formats"""
    date_formats = [
        '%b. %d, %Y',  # Aug. 1, 2024
        '%d-%b-%y',    # 31-Jul-24
        '%d-%b-%Y',    # 31-Jul-2024
        '%B %d, %Y',   # July 31, 2024
        '%d-%m-%y',    # 20-06-23
        '%Y-%m-%d'     # 2024-08-01 (in case you have any in this format)
    ]   
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass    
    return None

        
# Function to clean data
def clean_data(df):
    """
    Function to clean data including:
        - drop unnecessary columns, 
        - drop rows with zero workout time, 
        - replace NaN values with None, 
        - date parsing for "Workout Date", and
        - rename columns to be more descriptive of units
    """

    initial_row_count = len(df)
    
    # Nix columns that I don't care about so I won't bother cleaning them
    ignore_cols = ['Date Submitted', 'Avg Speed (mi/h)', 'Max Speed (mi/h)', 'Avg Heart Rate', 'Notes','Source' ]
    df = df.drop(columns=ignore_cols)
    
    # Drop rows where 'Workout Time (seconds)' is 0
    df = df[df['Workout Time (seconds)'] != 0]
    rows_dropped = initial_row_count - len(df)   
    print(f"Dropped {rows_dropped} rows with zero workout time.")

    # Replace 'nan' with None for numeric columns
    numeric_columns = ['Calories Burned (kcal)', 'Distance (mi)', 'Workout Time (seconds)', 
                       'Avg Pace (min/mi)', 'Max Pace (min/mi)', 'Steps']
    for col in numeric_columns:
        df.loc[df[col].isna(), col] = None
    
    # Replace empty strings with None for string columns
    string_columns = ['Activity Type', 'Link']
    for col in string_columns:
        df.loc[df[col] == '', col] = None

    # Custom date parsing
    date_formats, invalid_dates  = {}, []   
    df['Workout Date'] = df['Workout Date'].apply(lambda x: parse_date(str(x)))
    
    for index, row in df.iterrows():
        date_string = str(row['Workout Date'])
        if isinstance(row['Workout Date'], pd._libs.tslibs.nattype.NaTType):
            invalid_dates.append((index, date_string))
        else:
            date_format = re.sub(r'\d+', '%', date_string)
            if date_format in date_formats:
                date_formats[date_format] += 1
            else:
                date_formats[date_format] = 1
    
    # Drop rows with invalid dates
    df = df.dropna(subset=['Workout Date'])
    rows_dropped_invalid_date = len(invalid_dates)
    
    print(f"Dropped {rows_dropped_invalid_date} rows with invalid dates.")
    print(f"Final number of rows: {len(df)}")
    
    # Replace NaN values with None
    df = df.where(pd.notnull(df), None)

    # Replace infinite values with None
    df = df.replace([np.inf, -np.inf], None)

    # Reset the index after dropping rows
    df = df.reset_index(drop=True)
    
    # Rename columns to match our database schema
    column_mapping = {
        'Workout Date': 'workout_date',
        'Activity Type': 'activity_type',
        'Calories Burned (kcal)': 'kcal_burned',
        'Distance (mi)': 'distance_mi',
        'Workout Time (seconds)': 'duration_sec',
        'Avg Pace (min/mi)': 'avg_pace',
        'Max Pace (min/mi)': 'max_pace',
        'Steps': 'steps',
        'Link': 'link'
    }
    df = df.rename(columns=column_mapping)
    
    return df


def extract_workout_id(url):
    match = re.search(r'/workout/(\d+)', url)
    if match:
        return match.group(1)
    else:
        return 'unsure'  # or you could return a specific value to indicate no match was found


def enrich_data(df):
    """
    Enrich the data with additional columns
    """
    # Extract workout ID from Link
    df['workout_id'] = df['link'].apply(extract_workout_id)
    
    # TODO -- More enrichment here, e.g.
    # df['workout_year'] = pd.to_datetime(df['workout_date']).dt.year
    # df['is_long_workout'] = df['duration_sec'] > 3600

    return df

def insert_data_NEW(cursor, df):
    """
    Insert dataframe rows into cursor's database table
    """

    # Get column names
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    
    # Prepare the SQL query
    sql = f"INSERT INTO workout_summary ({columns}) VALUES ({placeholders})"
    
    # Convert DataFrame to list of tuples
    data = [tuple(x) for x in df.replace({np.nan: None}).values]
    
    try:
        cursor.executemany(sql, data)
        return cursor.rowcount
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        print(f"Failed SQL: {sql}")
        print("Failed data sample:")
        for row in data[:5]:  # Print first 5 rows of data
            print(row)
        raise

