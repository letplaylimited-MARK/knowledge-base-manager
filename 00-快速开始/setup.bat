@echo off
echo ========================================
echo    通用知识库框架 V2.0
echo    初始化脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 检查并安装依赖...
pip install -r requirements.txt --quiet

REM 初始化目录
echo [2/3] 初始化目录结构...
mkdir 01-收件箱\待处理 2>nul
mkdir 02-对话记录\工作项目 2>nul
mkdir 04-输出成果\报告 2>nul
mkdir 06-参考资料 2>nul
mkdir 07-项目文档 2>nul

REM 更新索引
echo [3/3] 更新知识索引...
python .workbuddy\scripts\update_index.py

echo.
echo ========================================
echo    初始化完成！
echo ========================================
echo.
echo 接下来请：
echo 1. 阅读 README.md 了解项目
echo 2. 查看 快速上手指南.md 开始使用
echo.
pause