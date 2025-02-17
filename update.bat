@echo off
REM Script to run gallery-dl --update and wait for input to close

REM Check if venv exists, if not, create it
if not exist venv (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate the virtual environment
echo Activating the virtual environment...
call venv\Scripts\activate

REM Run gallery-dl update command
echo Running gallery-dl --update...
gallery-dl --update

REM Deactivate the virtual environment
echo Deactivating the virtual environment...
deactivate

echo Update process complete. Press any key to exit.
pause
