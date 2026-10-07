@echo off
echo ========================================================
echo   Starting CentrAlign Autonomous AI Task Worker Suite
echo ========================================================
echo [1/2] Launching Mock Enterprise ERP on http://localhost:8000...
start "CentrAlign Mock ERP Portal" cmd /k ".venv\Scripts\python.exe run_mock_erp.py"
timeout /t 3 /nobreak > nul

echo [2/2] Launching Streamlit AI Assistant on http://localhost:8501...
start "CentrAlign Streamlit AI Assistant" cmd /k ".venv\Scripts\streamlit.exe run ui\dashboard.py"

echo.
echo ========================================================
echo   Both services are running!
echo   - Enterprise ERP Portal:  http://localhost:8000/dashboard
echo   - AI Assistant Dashboard: http://localhost:8501
echo ========================================================
echo You can close this window now. The servers will keep running in their own windows.
pause
