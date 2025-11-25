@echo off
echo ========================================
echo 启动Ollama LLM服务
echo ========================================
echo.

echo 检查Ollama是否已安装...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Ollama未安装
    echo 请运行 setup_ollama.bat 安装Ollama
    pause
    exit /b 1
)

echo.
echo Ollama版本:
ollama --version

echo.
echo 检查qwen2:7b模型是否已下载...
ollama list | findstr qwen2 >nul 2>&1
if errorlevel 1 (
    echo.
    echo 模型未找到，正在下载qwen2:7b...
    echo 这可能需要几分钟...
    ollama pull qwen2:7b
)

echo.
echo ========================================
echo Ollama服务已就绪！
echo ========================================
echo.
echo API地址: http://localhost:11434
echo 模型: qwen2:7b
echo.
echo 测试命令:
echo   curl http://localhost:11434/api/generate -d "{\"model\":\"qwen2:7b\",\"prompt\":\"你好\"}"
echo.
echo Ollama会在后台自动运行
echo 查看运行的模型: ollama list
echo 停止模型: ollama stop qwen2:7b
echo.

pause
