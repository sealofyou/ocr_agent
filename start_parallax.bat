@echo off
echo ========================================
echo 启动Parallax LLM推理服务器
echo ========================================
echo.

echo 拉取Parallax Docker镜像...
docker pull gradientservice/parallax:latest

echo.
echo 启动Parallax容器（端口8000）...
echo 注意：如果您的GPU不是Blackwell/Ampere/Hopper架构，请修改此脚本
echo.

REM 启动容器，映射端口8000到主机
docker run -d ^
  --name parallax-server ^
  --gpus all ^
  -p 8000:8000 ^
  gradientservice/parallax:latest ^
  bash -c "parallax serve --model Qwen/Qwen2-VL-7B-Instruct --host 0.0.0.0 --port 8000"

echo.
echo 等待服务启动...
timeout /t 10

echo.
echo 检查容器状态...
docker ps -a | findstr parallax-server

echo.
echo ========================================
echo Parallax服务器已启动！
echo API地址: http://localhost:8000
echo ========================================
echo.
echo 查看日志: docker logs parallax-server
echo 停止服务: docker stop parallax-server
echo 删除容器: docker rm parallax-server
echo.

pause
