@echo off
echo ========================================
echo 启动文本归档助手后端服务
echo ========================================
echo.

cd backend

echo 激活conda环境...
call conda activate ocr_agent

echo.
echo 启动后端服务器...
echo 服务地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.

python main.py

pause
