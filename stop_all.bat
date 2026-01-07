@echo off
echo ================================
echo Stopping TopGo RAG Chatbot
echo ================================
echo.

echo [STOPPING] Streamlit...
taskkill /F /IM streamlit.exe 2>nul
if "%ERRORLEVEL%"=="0" (echo [OK] Streamlit stopped) else (echo [INFO] Streamlit was not running)

echo.
echo [STOPPING] Uvicorn/FastAPI...
taskkill /F /FI "WINDOWTITLE eq FastAPI*" 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul
echo [OK] FastAPI stopped

echo.
echo [STOPPING] Ollama...
taskkill /F /IM ollama_runners.exe 2>nul
taskkill /F /IM ollama.exe 2>nul
if "%ERRORLEVEL%"=="0" (echo [OK] Ollama stopped) else (echo [INFO] Ollama was not running)

echo.
echo ================================
echo All services stopped!
echo ================================
pause
