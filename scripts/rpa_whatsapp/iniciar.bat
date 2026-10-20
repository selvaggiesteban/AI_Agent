@echo off
echo ============================================
echo   RPA WhatsApp Web - Inicio Rapido
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instale Python 3.8+
    pause
    exit /b 1
)

REM Instalar dependencias
echo [*] Instalando dependencias...
pip install -r requirements.txt
echo.

REM Opciones de ejecucion
echo Seleccione modo de ejecucion:
echo   1. Modo CDP (recomendado) - Chrome con depuracion remota
echo   2. Modo Normal - Abre Chrome con sesion guardada
echo   3. Salir
echo.
set /p opcion="Opcion (1-3): "

if "%opcion%"=="1" goto modo_cdp
if "%opcion%"=="2" goto modo_normal
goto fin

:modo_cdp
echo.
echo [!] Instrucciones:
echo   1. Cierre Chrome completamente
echo   2. Abra Chrome con: chrome.exe --remote-debugging-port=9222
echo   3. Inicie sesion en WhatsApp Web
echo   4. Presione Enter aqui para continuar
echo.
pause
python whatsapp_rpa_cdp.py
goto fin

:modo_normal
python whatsapp_rpa.py
goto fin

:fin
pause
