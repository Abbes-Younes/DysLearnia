@echo off
REM Start Ollama server so Dyslernia can use your local model (e.g. qwen3.5).
REM Run this before starting the backend if Ollama is not already running.

set "OLLAMA_EXE=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
if exist "%OLLAMA_EXE%" (
    echo Starting Ollama server...
    start "" "%OLLAMA_EXE%" serve
    timeout /t 3 /nobreak >nul
    echo Ollama should be running at http://localhost:11434
) else (
    where ollama >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo Starting Ollama server...
        start "" ollama serve
        timeout /t 3 /nobreak >nul
        echo Ollama should be running at http://localhost:11434
    ) else (
        echo Ollama not found. Install from https://ollama.com/download
        echo Then run: ollama pull qwen3.5
        exit /b 1
    )
)
exit /b 0
