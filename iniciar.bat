@echo off
title FideliPass Server
cd /d "%~dp0"
echo ===================================================
echo   Iniciando FideliPass (Apple ^& Google Wallet)
echo ===================================================
echo Abriendo en tu navegador: http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
python app.py
pause
