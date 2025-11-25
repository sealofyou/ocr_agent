@echo off
echo ========================================
echo 停止Parallax LLM推理服务器
echo ========================================
echo.

echo 停止容器...
docker stop parallax-server

echo.
echo 删除容器...
docker rm parallax-server

echo.
echo ========================================
echo Parallax服务器已停止并删除
echo ========================================
echo.

pause
