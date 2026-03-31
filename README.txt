================================================================
         DiabetesCare Dashboard — README
         Diabetes Self-Management Streamlit App
================================================================

OVERVIEW
--------
DiabetesCare Dashboard is a Python-based web application built with
Streamlit that helps diabetes patients self-manage their condition.
It allows users to log meals, track blood glucose readings, view
analytics charts, receive clinical alerts, and manage their profile.

The app auto-seeds 30 days of realistic synthetic data on first
launch so all charts and analytics are immediately populated.


FEATURES
--------
  - Dashboard         : Daily summary with gauge charts and metric cards
  - Food Log          : Log meals from a 25-item USDA-style food database
  - Blood Glucose Log : Log BG readings with instant alert classification
  - Analytics Charts  : Weekly (7-day) and Monthly (30-day) charts:
                          > Average BG trend line chart
                          > Daily calorie & carb intake bar chart
                          > Diabetes status donut/pie chart
  - Alerts & Guidance : Active alerts + ADA/NICE clinical reference
  - Patient Profile   : Set personal targets (calories, carbs, diabetes type)


ALERT THRESHOLDS (ADA / NICE Guidelines)
-----------------------------------------
  BG < 70 mg/dL       -> Hypoglycemia      (Blue)
  BG 70–179 mg/dL     -> Normal            (Green)
  BG 180–239 mg/dL    -> Mild Hyperglycemia (Yellow)
  BG 240–299 mg/dL    -> Check Ketones     (Orange)
  BG >= 300 mg/dL     -> Severe / DKA Risk (Red)


REQUIREMENTS
------------
  - Python 3.8 or higher
  - streamlit
  - pandas
  - plotly

  See requirements.txt for exact versions.


INSTALLATION
------------
  1. Make sure Python is installed:
       python --version

  2. Install dependencies:
       pip install -r requirements.txt

  3. Place diabetes_app.py in your desired folder.


HOW TO RUN
----------
  Open a terminal, navigate to the folder containing diabetes_app.py,
  then run:

       streamlit run diabetes_app.py

  The app will open automatically in your browser at:
       http://localhost:8501

  If it does not open automatically, copy and paste the URL above
  into your browser manually.


ALTERNATIVE RUN COMMAND (if streamlit is not in PATH)
------------------------------------------------------
       python -m streamlit run diabetes_app.py


RUNNING ON A DIFFERENT PORT
----------------------------
       streamlit run diabetes_app.py --server.port 8502


FILE STRUCTURE
--------------
  DiabetesApp/
  |-- diabetes_app.py       <- Main application file
  |-- requirements.txt      <- Python dependencies
  |-- README.txt            <- This file
  |-- diabetes_care.db      <- SQLite database (auto-created on first run)


DATABASE
--------
  The app uses a local SQLite database (diabetes_care.db) that is
  created automatically in the same folder as the script.
  It contains three tables:

  food_logs       : Stores all meal entries with nutrients
  bg_logs         : Stores all blood glucose readings
  patient_profile : Stores user profile and daily targets

  On the very first run, the app seeds this database with 30 days
  of realistic synthetic data so charts are immediately meaningful.


COMMON ISSUES & FIXES
----------------------
  Problem                        Fix
  ------------------------------ -------------------------------------------
  streamlit: command not found   Use: python -m streamlit run diabetes_app.py
  ModuleNotFoundError            Run: pip install -r requirements.txt
  Port already in use            Add: --server.port 8502 to the run command
  Browser does not open          Manually go to: http://localhost:8501
  Slow first load                Normal — seeding 30 days of data on startup


DISCLAIMER
----------
  This application is for informational and educational purposes only.
  It is NOT a substitute for professional medical advice, diagnosis,
  or treatment. Always consult your qualified healthcare provider
  before making any changes to your diet, medication, or treatment plan.

  Blood glucose thresholds and medication guidance are based on
  publicly available ADA (American Diabetes Association) and NICE
  (National Institute for Health and Care Excellence) guidelines.


BUILT WITH
----------
  - Streamlit   https://streamlit.io
  - Pandas      https://pandas.pydata.org
  - Plotly      https://plotly.com/python
  - SQLite3     https://docs.python.org/3/library/sqlite3.html

================================================================
                     End of README
================================================================
