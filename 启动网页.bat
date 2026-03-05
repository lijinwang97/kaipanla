@echo off
chcp 65001 >nul
title 开盘啦板块成分股 - 本地网页
cd /d "%~dp0"

echo ========================================
echo   开盘啦板块成分股实时数据 - 启动中
echo ========================================
echo.

REM 优先使用 python，若无则尝试 py（Windows 安装器）
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=python
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set PY_CMD=py -3
    ) else (
        echo [错误] 未检测到 Python，请先安装 Python 并勾选 "Add to PATH"。
        echo 下载地址: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo 正在启动网页服务，请稍候...
echo 启动成功后，浏览器将自动打开页面；若未打开，请手动访问: http://localhost:8501
echo 关闭本窗口即可停止服务。
echo.

"%PY_CMD%" -m streamlit run kaipanla_bankuai1.py --server.port 8501 --server.address 127.0.0.1

if %errorlevel% neq 0 (
    echo.
    echo [提示] 若提示缺少模块，请在本目录打开命令行并执行:
    echo   pip install -r requirements.txt
    echo.
)
pause
