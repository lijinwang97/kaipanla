@echo off
title Kaipanla - Local Web
cd /d "%~dp0"

echo.
echo ========================================
echo   Starting Kaipanla (Streamlit)...
echo ========================================
echo.
echo Dir: %CD%
echo.

where py >nul 2>&1
if %errorlevel% equ 0 (
  set PY_CMD=py -3
  goto :run
)
where python >nul 2>&1
if %errorlevel% equ 0 (
  set PY_CMD=python
  goto :run
)
echo [ERROR] Python not found. Install Python and add to PATH.
echo https://www.python.org/downloads/
echo.
pause
exit /b 1

:run
echo Using: %PY_CMD%
echo.
echo Starting Streamlit... Open browser: http://localhost:8501
echo Close this window to stop the server.
echo.

%PY_CMD% -u -m streamlit run kaipanla_bankuai1.py --server.port 8501 --server.address 127.0.0.1 --server.headless true

if not %errorlevel% equ 0 (
  echo.
  echo If missing modules, run in this folder: pip install -r requirements.txt
  echo.
)
pause
