@echo off

REM Check if the virtual environment exists
if not exist .venv (
    echo Virtual environment not found. Please create it first.
    echo Run install.bat first.
    pause
    exit /b
)

REM Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Start the Crew AI terminal application
echo Starting SyllaBot Pro - Streamlit application...
echo To stop the Streamlit application, press Ctrl+C in this window.
echo.
echo.
REM set PYTHONWARNINGS=ignore
streamlit run course.py

REM Reminder message
echo.
echo.
echo Generated (inbetween)files are located in the "course_latest" folder.
echo A history of generated files is kept in the "course_history" folder.
echo.

pause
