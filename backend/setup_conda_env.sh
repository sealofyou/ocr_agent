#!/bin/bash
# 创建conda环境并安装依赖

echo "========================================"
echo "文本归档助手 - Conda环境配置"
echo "========================================"
echo ""

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo "[错误] 未找到conda命令，请先安装Anaconda或Miniconda"
    exit 1
fi

echo "[1/4] 创建conda环境: ocr_agent (Python 3.10)"
conda create -n ocr_agent python=3.10 -y
if [ $? -ne 0 ]; then
    echo "[错误] 创建conda环境失败"
    exit 1
fi

echo ""
echo "[2/4] 激活conda环境"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate ocr_agent
if [ $? -ne 0 ]; then
    echo "[错误] 激活conda环境失败"
    exit 1
fi

echo ""
echo "[3/4] 安装Python依赖包（使用中科大镜像源）"
pip install -i https://pypi.mirrors.ustc.edu.cn/simple -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 安装依赖包失败"
    exit 1
fi

echo ""
echo "[4/4] 验证安装"
python verify_setup.py
if [ $? -ne 0 ]; then
    echo "[警告] 验证过程中发现问题，请检查上述输出"
fi

echo ""
echo "========================================"
echo "环境配置完成！"
echo "========================================"
echo ""
echo "下一步操作："
echo "1. 激活环境: conda activate ocr_agent"
echo "2. 初始化数据库: python init_db.py"
echo "3. 运行测试: pytest"
echo "4. 启动服务: uvicorn main:app --reload"
echo ""
