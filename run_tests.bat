@echo off
echo ========================================
echo 运行文本归档助手测试
echo ========================================
echo.

cd backend

echo 激活conda环境...
call conda activate ocr_agent

echo.
echo 运行单元测试...
python -m pytest tests/test_auth.py tests/test_upload.py tests/test_ocr.py tests/test_classification.py -v --tb=short

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.

pause
