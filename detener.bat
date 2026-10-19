@echo off
title Apagar FideliPass
cd /d "%~dp0"
echo ===================================================
echo   Apagando Servidor FideliPass...
echo ===================================================
powershell -NoProfile -Command "$conn = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue; if ($conn) { Stop-Process -Id $conn.OwningProcess -Force; Write-Host 'Servidor detenido con exito. Puerto 5000 libre.' -ForegroundColor Green } else { Write-Host 'El servidor ya no esta en ejecucion.' -ForegroundColor Yellow }"
timeout /t 3 >nul
