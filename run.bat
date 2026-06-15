@echo off
echo ===================================================
echo Starting Mutual Fund FAQ Assistant...
echo ===================================================

echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /c "python -m backend.main"

echo Starting Frontend Server...
start "Frontend UI" cmd /c "cd frontend && python -m http.server 8080"

echo.
echo Application is running!
echo ---------------------------------------------------
echo Backend API available at: http://localhost:8000
echo Frontend UI available at: http://localhost:8080
echo ---------------------------------------------------
echo Press any key to shutdown servers...
pause > nul

taskkill /fi "WindowTitle eq FastAPI Backend" > nul
taskkill /fi "WindowTitle eq Frontend UI" > nul
echo Servers shutdown successfully.
