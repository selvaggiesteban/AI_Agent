@echo off
echo ========================================
echo  CAMPANA EMAIL MARKETING
echo  Servicio Tecnico de Computadoras
echo ========================================
echo.
echo  Cuentas: 12 Gmail
echo  Horario: 7:00 - 13:00
echo  Delay: Senoide 1-10 min
echo.
echo  Presiona Ctrl+C para detener
echo ========================================
echo.
python "%~dp0campaign_sender.py"
pause
