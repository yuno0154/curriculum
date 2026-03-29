@echo off
chcp 65001 > nul
echo.
echo ==========================================
echo   과목명 추출 스크립트 (subject_only)
echo ==========================================
echo.
"d:\project\성취기준 추출 프로그램\.venv\Scripts\python.exe" extractor_subject_only.py
echo.
echo ------------------------------------------
echo 작업이 완료되었습니다.
pause
