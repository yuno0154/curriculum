@echo off
echo 성취기준 검색 대시보드 서버를 실행합니다...
echo 브라우저에서 http://localhost:8000 접속 후 대시보드를 확인하세요.
echo.
cd /d "%~dp0"
"d:\project\성취기준 추출 프로그램\.venv\Scripts\python.exe" server.py
pause
