@echo off
echo ===================================
echo Career-TwinNavigatorBot - Setup
echo ===================================
echo.

REM Creating virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists.
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ===================================
echo Setup completed!
echo ===================================
echo.
echo Next steps:
echo 1. Create .env file with your API keys
echo 2. Copy env.example to .env
echo 3. Fill in BOT_TOKEN and OPENAI_API_KEY
echo.
echo After that run: python main.py
echo.
pause

