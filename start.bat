@echo off
title Modulos Agency - Auto Install & Start
color 0A

echo ========================================
echo    MODULOS AGENCY WEBSITE
echo    Auto Install & Start Script
echo ========================================
echo.

:: ============================================
:: STEP 1: CHECK PYTHON
:: ============================================
echo [1/6] Checking Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python not found!
    echo Please install Python from: https://python.org/
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)
echo [OK] Python found: 
python --version
echo.

:: ============================================
:: STEP 2: CHECK VIRTUAL ENVIRONMENT
:: ============================================
echo [2/6] Setting up virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created!
) else (
    echo [OK] Virtual environment already exists.
)
echo.

:: ============================================
:: STEP 3: ACTIVATE VIRTUAL ENVIRONMENT
:: ============================================
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate venv!
    pause
    exit /b 1
)
echo [OK] Virtual environment activated!
echo.

:: ============================================
:: STEP 4: CHECK AND INSTALL REQUIREMENTS
:: ============================================
echo [4/6] Checking requirements...
if exist "requirements.txt" (
    echo Installing/Updating packages...
    pip install --upgrade pip
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Installation failed!
        pause
        exit /b 1
    )
    echo [OK] All packages installed!
) else (
    echo [WARNING] requirements.txt not found!
    echo Installing default packages...
    pip install Flask>=3.0.3 Flask-SQLAlchemy>=3.1.1 Flask-Login>=0.6.3 Flask-Bcrypt>=1.0.1 Flask-Mail>=0.10.0 itsdangerous>=2.2.0 python-dotenv>=1.0.1 requests>=2.32.3
)
echo.

:: ============================================
:: STEP 5: CHECK DATABASE
:: ============================================
echo [5/6] Checking database...
if exist "instance\modulos.db" (
    echo [OK] Database found.
) else (
    echo [INFO] Database not found. Creating...
    if exist "init_db.py" (
        python init_db.py
        echo [OK] Database created!
    ) else (
        echo [WARNING] init_db.py not found.
        echo Please create database manually.
    )
)
echo.

:: ============================================
:: STEP 6: START FLASK SERVER
:: ============================================
echo [6/6] Starting Flask server...
echo.
echo ========================================
echo    SERVER STARTING...
echo    URL: http://127.0.0.1:5000
echo    Press CTRL+C to stop
echo ========================================
echo.

python run.py

:: If run.py fails, try alternative
if %errorlevel% neq 0 (
    echo.
    echo [INFO] Trying alternative: python app/__init__.py
    python app/__init__.py
)

pause