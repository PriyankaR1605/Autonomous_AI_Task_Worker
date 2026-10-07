# CentrAlign Autonomous AI Task Worker - PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting CentrAlign Autonomous AI Task Worker Suite   " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Start Mock ERP
Write-Host "[1/2] Launching Mock Enterprise ERP on http://localhost:8000..." -ForegroundColor Green
Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "run_mock_erp.py" -WindowStyle Normal

Start-Sleep -Seconds 3

# 2. Start Streamlit Dashboard
Write-Host "[2/2] Launching Streamlit AI Assistant on http://localhost:8501..." -ForegroundColor Green
Start-Process -FilePath ".venv\Scripts\streamlit.exe" -ArgumentList "run ui/dashboard.py" -WindowStyle Normal

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Both services are running in separate processes!      " -ForegroundColor Green
Write-Host "  - Enterprise ERP Portal:  http://localhost:8000/dashboard" -ForegroundColor White
Write-Host "  - AI Assistant Dashboard: http://localhost:8501         " -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
