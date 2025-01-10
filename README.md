# Workout Dashboard

## Project Description
The Workout Dashboard is a web application designed to help users track and manage their workout routines. It provides features such as logging exercises, tracking progress, and visualizing workout data.

[Google Document with project notes](https://docs.google.com/document/d/1lj6R9rybGuRNgUUzizTrjVLj5xpU9R1nWajcMkRqpwI/edit?usp=drive_link)

Link to download a user's own [MapMyRun workout history](https://www.mapmyfitness.com/workout/export/csv) (*requires sign-in*). 

## Features
- Exercise logging with customizable workout classification
- Progress tracking with charts and statistics
- Responsive design for mobile and desktop use

## Installation 
1. Clone the repository:
    ```bash
    git clone https://github.com/dagny/build-workout-dashboard.git
    ```
2. Navigate to the project directory:
    ```bash
    cd build-workout-dashboard
    ```
3. Install Poetry if you haven't already:
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
- Make note of whether $HOME was successfully modified; if not, poetry may be installed in another location. For example, for my mac poetry is here:
    ```bash
    ~/.local/bin/poetry
    ```
4. Create and activate a virtual environment for the project. For example, I typically use venv and am using the name ".st-db":
    ```bash
    python3 -m venv .st-db    
    source .st-db/bin/activate
    ```
5. Within the virtual environment, install dependencies using Poetry:
    ```bash
    poetry install                  #If dev
    ```
    or
    ```bash
    poetry install --no-dev         #If prod
    ```
6. Run "init.py" from main project directory to CREATE DATABASE & TABLES
    ```bash
    poetry run python init.py
    ```
**TODO** - Make an "init.sh" that calls "init.py" and "build_workout_dashgboard/update_db.py" and use that instead  

7. Run build_workout_dashboard/update_db.py from main project directory to UPDATE DATA
    ```bash
    poetry run python build_workout_dashboard/update_db.py
    ```

8. Run "dashboard.py" from main project directory to SHOW DASHBOARD:
    ```bash
    poetry run python dashboard.py
    ```

## Usage
1. Open your browser and navigate to `http://localhost:8501`.
2. Create an account or log in if you already have one.
3. Start logging your workouts and track your progress!

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any questions or feedback, please contact [barbs@balex.com](mailto:barbs@balex.com).

