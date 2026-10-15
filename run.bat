@echo off
title ARCTUS - FP&A Stress Testing Platform
echo ================================================================
echo   ARCTUS - Institutional FP&A Stress-Testing Platform
echo   Launching Unified Runtime (Streamlit UI + Flask REST API)
echo ================================================================
if exist ".\.venv\Scripts\python.exe" (
    ".\.venv\Scripts\python.exe" run.py
) else (
    python run.py
)
pause
