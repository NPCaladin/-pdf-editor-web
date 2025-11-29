@echo off
chcp 65001 >nul
echo PDF 편집기 실행 파일 생성 중...
echo.

REM 배치 파일이 있는 디렉토리로 이동
cd /d "%~dp0"

REM main.py 파일 존재 확인
if not exist "main.py" (
    echo 오류: main.py 파일을 찾을 수 없습니다.
    echo 배치 파일과 main.py가 같은 폴더에 있는지 확인해주세요.
    pause
    exit /b 1
)

REM PyInstaller 설치 확인
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치 중...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo PyInstaller 설치에 실패했습니다.
        pause
        exit /b 1
    )
)

echo.
echo 실행 파일 생성 중...
echo.

REM PyInstaller로 실행 파일 생성
REM --onefile: 단일 실행 파일로 생성
REM --windowed: 콘솔 창 없이 실행 (GUI 앱)
REM --name: 실행 파일 이름
python -m PyInstaller --onefile --windowed --name "서울자가김부장용PDF편집기 Ver 1.3" --clean main.py

if errorlevel 1 (
    echo.
    echo 오류가 발생했습니다.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 실행 파일 생성 완료!
echo.
echo 실행 파일 위치: dist\서울자가김부장용PDF편집기 Ver 1.3.exe
echo.
echo 전체 경로: %CD%\dist\서울자가김부장용PDF편집기 Ver 1.3.exe
echo ========================================
echo.
echo dist 폴더를 열까요? (Y/N)
set /p open_folder=
if /i "%open_folder%"=="Y" (
    explorer dist
)
pause

