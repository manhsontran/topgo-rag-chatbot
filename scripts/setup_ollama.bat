@echo off
echo ========================================
echo   TopGo RAG Chatbot - Ollama Setup
echo ========================================
echo.
echo Kiem tra Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1

if %errorlevel% neq 0 (
    echo [!] Ollama chua chay!
    echo.
    echo Vui long:
    echo 1. Cai dat Ollama: https://ollama.ai/download/windows
    echo 2. Chay Ollama (tu dong khoi dong sau khi cai)
    echo 3. Chay lai script nay
    pause
    exit /b 1
)

echo [OK] Ollama dang chay!
echo.

echo Kiem tra model qwen2:1.5b...
ollama list | findstr "qwen2:1.5b" >nul 2>&1

if %errorlevel% neq 0 (
    echo [!] Model chua co, dang download...
    echo    (Co the mat 5-10 phut, tuy toc do mang)
    echo.
    ollama pull qwen2:1.5b
    if %errorlevel% neq 0 (
        echo [X] Loi khi download model!
        pause
        exit /b 1
    )
    echo [OK] Download thanh cong!
) else (
    echo [OK] Model da co!
)

echo.
echo ========================================
echo   Setup hoan tat!
echo ========================================
echo.
echo De chay chatbot:
echo   1. Chay API:  python run_api.py
echo   2. Chay UI:   streamlit run app.py
echo.
pause
