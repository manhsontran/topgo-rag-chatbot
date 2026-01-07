@echo off
echo ================================
echo Starting TopGo RAG Chatbot
echo ================================
echo.

REM Check if Ollama is already running
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama is already running
) else (
    echo [STARTING] Ollama server...
    start "Ollama Server" /MIN cmd /c "ollama serve"
    timeout /t 3 >nul
    echo [OK] Ollama started
)

echo.
echo [STARTING] FastAPI Backend (port 8000)...
start "FastAPI Backend" cmd /k "uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 >nul

echo.
echo [STARTING] Streamlit Frontend (port 8501)...
start "Streamlit Frontend" cmd /k "streamlit run app.py"
timeout /t 2 >nul

echo.
echo ================================
echo All services started!
echo ================================
echo.
echo Services:
echo   - Ollama LLM:        http://localhost:11434
echo   - FastAPI Backend:   http://localhost:8000
echo   - API Docs:          http://localhost:8000/docs
echo   - Streamlit UI:      http://localhost:8501
echo.
echo Press any key to exit (services will keep running)...
pause >nul
