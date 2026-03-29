@echo off
chcp 65001 > nul
echo.
echo ==========================================
echo   전체 성취기준 추출 엔진 (Main)
echo ==========================================
echo.
"d:\project\성취기준 추출 프로그램\.venv\Scripts\python.exe" extractor.py
echo.
echo ------------------------------------------
echo 추출 작업이 모두 완료되었습니다.
echo '성취기준_추출결과.xlsx' 및 'data.json'이 생성되었습니다.
pause
