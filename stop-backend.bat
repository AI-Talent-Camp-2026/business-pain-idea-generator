@echo off
chcp 65001 >nul
echo ========================================
echo    Остановка Backend сервисов
echo ========================================
echo.

echo Остановка FastAPI и Worker процессов...
echo.

REM Убиваем процессы по заголовку окна
taskkill /F /FI "WINDOWTITLE eq FastAPI*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Worker*" >nul 2>&1

REM Резервный вариант - убить все uvicorn
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /v ^| findstr /i "uvicorn"') do (
    taskkill /F /PID %%a >nul 2>&1
)

for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /v ^| findstr /i "run_worker"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ========================================
echo    Backend сервисы остановлены
echo ========================================
pause
