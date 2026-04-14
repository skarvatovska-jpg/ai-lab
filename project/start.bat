@echo off
echo ===================================
echo Starting Career-TwinNavigatorBot
echo ===================================
echo.

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

if not exist .env (
    echo ERROR: .env file not found!
    echo Create .env based on env.example
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting bot...
python main.py

pause

