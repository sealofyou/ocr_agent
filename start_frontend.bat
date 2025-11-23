@echo off
echo ========================================
echo 启动文本归档助手前端服务
echo ========================================
echo.

cd frontend

echo 检查依赖...
if not exist "node_modules" (
    echo 首次运行，正在安装依赖...
    call npm install
)

echo.
echo 启动前端开发服务器...
echo 服务地址: http://localhost:5173
echo.

call npm run dev

pause
