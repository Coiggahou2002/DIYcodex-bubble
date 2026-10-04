@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul && (py -3 app\launch.py & goto :eof)
where python >nul 2>nul && (python app\launch.py & goto :eof)
echo 未找到 Python 3，请先安装 Python 3.9 或以上版本（python.org，安装时勾选 Add to PATH）。详见 README。
pause
