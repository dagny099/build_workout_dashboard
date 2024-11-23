## Automate Visiting a URL in a Browser and Typing Stuff and Moving Files
# Visit a website and change name before saving
# Check if file exists and move it if it doesn't

import pyautogui
import webbrowser
import time
import os
import shutil
import pandas as pd

wait_time = 6

def move_file_if_not_stored(new_downloaded_file, final_file_location):
    tcx_file_is_stored = True
    if os.path.exists(new_downloaded_file):
        if not(os.path.exists(final_file_location)):
            shutil.move(new_downloaded_file, final_file_location)
            print(f"Moved file into:  {final_file_location}")
            return tcx_file_is_stored
        else:
            print(f"{final_file_location} ALREADY EXISTS")
            return tcx_file_is_stored
    else:
        if os.path.exists(f"{final_file_location}"):
            print(f"{final_file_location} ALREADY EXISTS")
            return tcx_file_is_stored
        else:
            print(f"{new_downloaded_file} WAS NOT DOWNLOADED")
            return False

# Setup Location Defaults
filename = '/Users/barbaraihidalgo-sotelo/Downloads/user2632022_workout_history.csv'
project_folder = '/Users/barbaraihidalgo-sotelo/PROJECTS/build_workout_dashboard'

workoutExportURL = f"https://www.mapmyfitness.com/workout/export/csv"

patternstrip = 'http://www.mapmyfitness.com/workout/'


data_folder = project_folder + '/workouts_timedata'
os.makedirs(data_folder, exist_ok=True)

### 1. Download the latest user_workout_history to get all workout IDs
# PRE-REQUISITE:  You have to sign in before this will work

if not(os.path.exists(filename)):
    webbrowser.open(workoutExportURL)

    # (Optional, if you want to download the file automatically)
    # time.sleep(15)
    # pyautogui.press('enter')

### 2. Load workout_summary table & Sort if you want, by Workout Time

# Read the user_workout_history to get a list of all workout ids
df = pd.read_csv(filename)
df = df[df['Workout Time (seconds)']>1].sort_values(by='Workout Time (seconds)')
all_workouts = df['Link'].str.strip(patternstrip).tolist()

# Check which workout_IDs already exist in the folder and remove those from the list to download
gotem = [id.strip('.tcx') for id in os.listdir(data_folder)]
ids2download = [id for id in all_workouts if id not in gotem]

### 3. Loop through a list of workout IDs and download a renamed file locally
for workoutid in ids2download:
    locationDataURL = f"https://www.mapmyfitness.com/workout/export/{workoutid}/tcx"
    
    webbrowser.open(locationDataURL)
    time.sleep(wait_time)   # 5 sec seems a little long for the short files, but will def be too short for long runs & anomalies
    
    pyautogui.write([l for l in str(workoutid)], interval = 0.2)
    pyautogui.press('enter')
    time.sleep(1)

    # Check for the file and move
    move_file_if_not_stored(f"/Users/barbaraihidalgo-sotelo/Downloads/{workoutid}.tcx" , f"{data_folder}/{workoutid}.tcx" )
