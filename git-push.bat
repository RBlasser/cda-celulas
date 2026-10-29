@echo off
setlocal enabledelayedexpansion
title Git Commit and Push - CDA Celulas

:: Asegurar que el script se ejecute siempre desde la raiz del repositorio
cd /d "%~dp0"

echo ===============================================================================
echo             CAJA DE AHORROS - CELULAS DE INNOVACION (GIT SYNC)
echo ===============================================================================
echo Directorio: %CD%
echo Rama actual:
git branch --show-current
echo ===============================================================================
echo.

:: Verificar que Git este en PATH
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git no esta disponible en el PATH del sistema.
    pause
    exit /b 1
)

:: Mostrar estado actual
echo [1/4] Verificando estado del repositorio...
git status -s
echo.

:: Comprobar si hay cambios o archivos no rastreados
git status --porcelain | findstr /R "." >nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] No hay cambios pendientes ni archivos nuevos para commitear.
    echo El repositorio local ya se encuentra completamente al dia.
    echo.
    set /p PULL_OPTION="Desea sincronizar con 'git pull origin main'? (S/N): "
    if /i "!PULL_OPTION!"=="S" (
        echo Sincronizando con remoto...
        git pull origin main
    )
    goto fin
)

:: Obtener mensaje de commit
set "MSG=%*"
if not defined MSG (
    echo [2/4] Ingrese el mensaje del commit:
    echo (Presione ENTER directamente para generar mensaje automatico)
    set /p "MSG=> "
)

if not defined MSG (
    set "MSG=chore: actualizacion de celulas %DATE% %TIME%"
)

echo.
echo [INFO] Mensaje de commit: "!MSG!"
echo.

:: Paso 3: git add
echo [3/4] Agregando todos los cambios (git add -A)...
git add -A
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Fallo al ejecutar 'git add -A'. Revise archivos bloqueados o permisos.
    goto fin_error
)

:: Paso 4: git commit
echo.
echo [4/5] Creando commit local...
git commit -m "!MSG!"
if %ERRORLEVEL% neq 0 (
    echo [ADVERTENCIA] No se genero un nuevo commit (posiblemente sin diferencias).
)

:: Paso 5: git push
echo.
echo [5/5] Enviando cambios al repositorio remoto (git push origin main)...
git push origin main
if %ERRORLEVEL% neq 0 (
    echo.
    echo ===============================================================================
    echo [ERROR] Ocurrio un problema al hacer push hacia GitHub.
    echo Verifique su conexion a red o credenciales de acceso al repositorio.
    echo ===============================================================================
    goto fin_error
)

echo.
echo ===============================================================================
echo [EXITO] Cambios enviados y sincronizados exitosamente con GitHub (origin/main)!
echo ===============================================================================
goto fin

:fin_error
pause
exit /b 1

:fin
echo.
pause
exit /b 0
