@echo off
echo ========================================
echo LLM环境检查
echo ========================================
echo.

echo [1/5] 检查Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Docker未安装或未运行
    echo   请安装Docker Desktop: https://www.docker.com/products/docker-desktop
) else (
    echo ✓ Docker已安装
    docker --version
)

echo.
echo [2/5] 检查Docker容器...
docker ps | findstr parallax-server >nul 2>&1
if errorlevel 1 (
    echo ✗ Parallax容器未运行
    echo   运行 start_qwen_llm.bat 启动服务
) else (
    echo ✓ Parallax容器正在运行
    docker ps | findstr parallax-server
)

echo.
echo [3/5] 检查Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Ollama未安装
    echo   可选：访问 https://ollama.com/download/windows 安装
) else (
    echo ✓ Ollama已安装
    ollama --version
)

echo.
echo [4/5] 检查LLM API...
curl -s http://localhost:8000/v1/models >nul 2>&1
if errorlevel 1 (
    echo ✗ Parallax API (端口8000) 不可用
) else (
    echo ✓ Parallax API (端口8000) 可用
)

curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo ✗ Ollama API (端口11434) 不可用
) else (
    echo ✓ Ollama API (端口11434) 可用
)

echo.
echo [5/5] 检查后端配置...
if exist backend\.env (
    echo ✓ backend\.env 文件存在
    findstr "LLM_API_URL" backend\.env >nul 2>&1
    if errorlevel 1 (
        echo ✗ LLM_API_URL 未配置
    ) else (
        echo ✓ LLM配置已设置
        findstr "LLM_API_URL" backend\.env
    )
) else (
    echo ✗ backend\.env 文件不存在
    echo   从 backend\.env.example 复制并配置
)

echo.
echo ========================================
echo 检查完成
echo ========================================
echo.

echo 推荐操作:
echo.

docker ps | findstr parallax-server >nul 2>&1
if errorlevel 1 (
    echo 1. 运行 start_qwen_llm.bat 启动LLM服务
)

if not exist backend\.env (
    echo 2. 复制 backend\.env.example 到 backend\.env
)

echo 3. 运行 backend\test_llm_classification.py 测试分类
echo 4. 运行 start_backend.bat 启动后端服务
echo.

pause
