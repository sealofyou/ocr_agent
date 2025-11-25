@echo off
echo ========================================
echo 启动Qwen3-VL-4B LLM服务
echo ========================================
echo.

echo 检查Docker是否运行...
docker ps >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)

echo.
echo 检查是否已有运行的容器...
docker ps | findstr parallax-server >nul 2>&1
if not errorlevel 1 (
    echo 警告: parallax-server容器已在运行
    echo 是否要重启？ (Y/N)
    set /p restart=
    if /i "%restart%"=="Y" (
        echo 停止旧容器...
        docker stop parallax-server
        docker rm parallax-server
    ) else (
        echo 使用现有容器
        goto :check_health
    )
)

echo.
echo 拉取Parallax镜像（如果需要）...
docker pull gradientservice/parallax:latest

echo.
echo 启动Parallax容器...
echo 模型: Qwen/Qwen2-VL-7B-Instruct
echo 端口: 8000
echo.

REM 尝试GPU模式
echo 尝试使用GPU模式启动...
docker run -d ^
  --name parallax-server ^
  --gpus all ^
  -p 8000:8000 ^
  gradientservice/parallax:latest ^
  bash -c "parallax serve --model Qwen/Qwen3-VL-4B-Instruct --host 0.0.0.0 --port 8000"

if errorlevel 1 (
    echo.
    echo GPU模式失败，尝试CPU模式...
    docker run -d ^
      --name parallax-server ^
      -p 8000:8000 ^
      gradientservice/parallax:latest ^
      bash -c "parallax serve --model Qwen/Qwen3-VL-4B-Instruct --host 0.0.0.0 --port 8000 --device cpu"
)

:check_health
echo.
echo 等待服务启动（这可能需要几分钟，首次启动需要下载模型）...
echo.

REM 等待30秒
timeout /t 30 /nobreak

echo.
echo 检查容器状态...
docker ps | findstr parallax-server

echo.
echo 查看最近的日志...
docker logs --tail 20 parallax-server

echo.
echo ========================================
echo Parallax LLM服务已启动！
echo ========================================
echo.
echo API地址: http://localhost:8000
echo 模型: Qwen/Qwen3-VL-4B-Instruct
echo.
echo 有用的命令:
echo   查看日志: docker logs -f parallax-server
echo   检查状态: docker ps ^| findstr parallax
echo   停止服务: docker stop parallax-server
echo   删除容器: docker rm parallax-server
echo.
echo 测试LLM分类:
echo   cd backend
echo   conda activate ocr_agent
echo   python test_llm_classification.py
echo.

pause
