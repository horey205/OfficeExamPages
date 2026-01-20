@echo off
chcp 65001
cls
echo ========================================================
echo        지적공무원 기출문제 관리자 서버 시작
echo ========================================================
echo.
echo [1] 서버를 실행합니다...
echo [2] 브라우저에서 admin 페이지를 엽니다.
echo.
echo ⚠️  주의: 작업을 마칠 때까지 이 창을 절대 끄지 마세요!
echo.

:: 브라우저 먼저 실행 (서버가 켜질 때까지 약간의 시간차 고려)
timeout /t 2 /nobreak >nul
start http://localhost:8000/admin.html

:: 파이썬 서버 실행
python server.py

pause
