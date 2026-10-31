@echo off
title Copiloto Formalizacion PP - Caja de Ahorros
echo ======================================================================
echo   Iniciando Copiloto de Formalizacion de Prestamos Personales CDA...
echo ======================================================================
python run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] No se pudo iniciar la aplicacion. Verifique dependencias con:
    echo pip install -r requirements.txt
    echo.
    pause
)
