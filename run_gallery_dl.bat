@echo off
REM Initialize virtual environment and run the Python program

REM Check if venv exists, if not, create it
if not exist venv (
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install --quiet -r requirements.txt

REM Run the Python script
python gallery_dl_menu.py

REM Deactivate the virtual environment
deactivate
