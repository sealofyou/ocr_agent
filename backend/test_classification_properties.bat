@echo off
cd backend
call conda activate ocr_agent
python -m pytest tests/property_tests/test_classification_properties.py -v --tb=short
pause
