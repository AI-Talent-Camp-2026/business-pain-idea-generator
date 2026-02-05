@echo off
rem chcp 65001 >nul
echo ========================================
echo    Перезапуск Backend сервисов
echo    (FastAPI + Worker)
echo ========================================
echo.

cd /d "%~dp0backend"

echo [1/4] Остановка существующих процессов...
echo.

REM Убиваем процессы uvicorn (FastAPI)
taskkill /F /FI "WINDOWTITLE eq FastAPI*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq uvicorn*" >nul 2>&1

REM Убиваем процессы worker
taskkill /F /FI "WINDOWTITLE eq Worker*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq run_worker*" >nul 2>&1

REM Небольшая пауза для завершения процессов
timeout /t 2 /nobreak >nul

echo [2/4] Активация виртуального окружения...
call venv\Scripts\activate.bat

echo [3/4] Запуск FastAPI сервера (порт 8000)...
start "FastAPI Server" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000"

REM Пауза перед запуском worker
timeout /t 3 /nobreak >nul

echo [4/4] Запуск Worker...
start "Worker Process" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python -m src.workers.run_worker"

echo.
echo ========================================
echo    Сервисы запущены!
echo ========================================
echo.
echo FastAPI: http://127.0.0.1:8000
echo Docs:    http://127.0.0.1:8000/docs
echo Health:  http://127.0.0.1:8000/health
echo.
echo Открыты 2 новых окна:
echo   - FastAPI Server
echo   - Worker Process
echo.
echo Для остановки закройте эти окна или
echo запустите этот скрипт снова.
echo ========================================
pause
