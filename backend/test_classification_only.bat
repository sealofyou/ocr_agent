@echo off
cd backend
call conda activate ocr_agent
python -m pytest tests/test_classification.py -v --tb=short
pause
