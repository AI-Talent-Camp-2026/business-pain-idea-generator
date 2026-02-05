@echo off
chcp 65001 >nul
cd /d "%~dp0frontend"
npx live-server --port=8080
