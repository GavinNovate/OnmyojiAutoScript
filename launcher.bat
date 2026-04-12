@echo off
setlocal
cd /d "%~dp0"

set "SERVER_TEST_URL=http://127.0.0.1:22288/test"

echo [1/3] 检查 server 是否可访问...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri '%SERVER_TEST_URL%' -TimeoutSec 3; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"

if %errorlevel%==0 (
    echo ✓ server 已运行，跳过启动 oas/osa
) else (
    echo 未检测到 server，尝试启动 OAS...
    if exist "oas.exe" (
        start "" "oas.exe"
    ) else if exist "osa.exe" (
        start "" "osa.exe"
    ) else (
        echo 未找到 oas.exe 或 osa.exe，请确认本 bat 位于程序根目录
        exit /b 1
    )

    echo 等待 5 秒让 server 初始化...
    timeout /t 5 /nobreak >nul
)

echo [2/3] 启动 launcher.py...
python launcher.py

echo [3/3] 完成
endlocal
