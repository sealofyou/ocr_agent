@echo off
echo ========================================
echo 安装和配置Ollama（Windows原生LLM工具）
echo ========================================
echo.

echo Ollama是Windows原生支持的LLM推理工具
echo 下载地址: https://ollama.com/download/windows
echo.
echo 请按照以下步骤操作：
echo.
echo 1. 访问 https://ollama.com/download/windows
echo 2. 下载并安装Ollama for Windows
echo 3. 安装完成后，运行以下命令：
echo.
echo    ollama pull qwen2:7b
echo.
echo 4. 启动Ollama服务（通常会自动启动）
echo.
echo 5. 测试API：
echo    curl http://localhost:11434/api/generate -d "{\"model\":\"qwen2:7b\",\"prompt\":\"你好\"}"
echo.
echo ========================================
echo.

pause

echo.
echo 是否现在打开Ollama下载页面？ (Y/N)
set /p open_browser=
if /i "%open_browser%"=="Y" (
    start https://ollama.com/download/windows
)

echo.
echo 安装完成后，运行 start_ollama_llm.bat 启动服务
echo.

pause
