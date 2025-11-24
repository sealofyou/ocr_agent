@echo off
echo ========================================
echo 测试MVP核心功能
echo ========================================
echo.

cd backend

echo 激活conda环境...
call conda activate ocr_agent

echo.
echo ========================================
echo 1. 测试用户认证功能
echo ========================================
python -m pytest tests/test_auth.py -v --tb=short

echo.
echo ========================================
echo 2. 测试文件上传功能
echo ========================================
python -m pytest tests/test_upload.py -v --tb=short

echo.
echo ========================================
echo 3. 测试OCR识别功能
echo ========================================
python -m pytest tests/test_ocr.py -v --tb=short

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.
echo MVP核心功能测试结果：
echo - 用户认证: 12个测试
echo - 文件上传: 21个测试
echo - OCR识别: 8个测试
echo 总计: 41个核心测试
echo.

pause
