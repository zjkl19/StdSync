@echo off
REM ==========================================================
REM StdSync 打包脚本
REM 作用：使用 PyInstaller 生成单文件可执行程序 StdSync.exe
REM 用法：双击或在命令行执行 build.bat
REM ==========================================================

:: 安装依赖（确保已激活虚拟环境）
pip install -r requirements.txt

:: 调用 PyInstaller
pyinstaller --onefile --noconsole main.py -n StdSync

echo.
echo --------------------------------------------
echo  打包完成，文件位于 dist\\StdSync.exe
echo --------------------------------------------
pause
