@echo off
REM Start Streamlit Web Application
REM LinkedIn Sourcing Agent - Professional Web Interface

echo 🎯 Starting LinkedIn Sourcing Agent Web Application...
echo =======================================================

REM Check if virtual environment is activated
if defined VIRTUAL_ENV (
    echo ✅ Virtual environment detected: %VIRTUAL_ENV%
) else (
    echo ⚠️  Warning: No virtual environment detected
    echo    Consider activating your virtual environment first:
    echo    .venv\Scripts\activate
)

REM Check if dependencies are installed
echo 📦 Checking dependencies...
python -c "import streamlit, plotly, pandas" 2>nul
if %errorlevel% equ 0 (
    echo ✅ Core dependencies found
) else (
    echo ❌ Missing dependencies. Installing...
    pip install streamlit plotly pandas
)

REM Set environment variables for demo mode
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_SERVER_ADDRESS=0.0.0.0

echo.
echo 🚀 Launching Streamlit application...
echo    URL: http://localhost:8501
echo    Docs: Check the sidebar for help
echo.
echo Press Ctrl+C to stop the server
echo =======================================================

REM Start Streamlit
streamlit run streamlit_app.py
