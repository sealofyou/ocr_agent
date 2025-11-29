@echo off
echo ========================================
echo 运行备忘录排序和筛选属性测试
echo ========================================
echo.

echo 激活conda环境...
call conda activate ocr_agent

echo.
echo 运行属性测试...
python -m pytest tests/property_tests/test_memo_sorting_filtering.py -v -m property --tb=short

echo.
echo ========================================
echo 测试完成！
echo ========================================
echo.

pause
