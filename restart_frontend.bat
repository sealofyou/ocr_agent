@echo off
echo ========================================
echo 重启前端服务
echo ========================================
echo.

echo 停止前端服务...
taskkill /f /im node.exe 2>nul

echo.
echo 等待2秒...
timeout /t 2 /nobreak >nul

cd frontend

echo.
echo 启动前端服务...
echo 服务地址: http://localhost:5173
echo.

start cmd /k "npm run dev"

echo.
echo 前端服务已在新窗口中启动！
echo 请在浏览器中访问: http://localhost:5173
echo.
pause
