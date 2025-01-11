@echo off
REM Update script for virtual environment, pip packages, and gallery-dl repo

REM Check if venv exists, if not, create it
if not exist venv (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate the virtual environment
echo Activating the virtual environment...
call venv\Scripts\activate

REM Update pip packages in requirements.txt
echo Updating pip packages from requirements.txt...
pip install --quiet --upgrade -r requirements.txt

REM Clone or update the gallery-dl repository
if not exist gallery-dl (
    echo Cloning gallery-dl repository...
    git clone https://github.com/mikf/gallery-dl
) else (
    echo Updating gallery-dl repository...
    cd gallery-dl
    git pull
    cd ..
)

REM Install or update gallery-dl as a pip package
echo Installing or updating gallery-dl pip package...
cd gallery-dl
pip install --quiet --upgrade .
cd ..

REM Deactivate the virtual environment
echo Deactivating the virtual environment...
deactivate

echo Update process complete.
pause
