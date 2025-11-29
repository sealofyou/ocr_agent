"""验证项目设置"""
import sys
import os

def check_imports():
    """检查关键模块是否可以导入"""
    print("检查模块导入...")
    
    modules = [
        "fastapi",
        "sqlalchemy",
        "pydantic_settings",
        "pytest",
        "hypothesis",
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - 未安装")
            failed.append(module)
    
    return len(failed) == 0


def check_files():
    """检查关键文件是否存在"""
    print("\n检查文件结构...")
    
    files = [
        "app/core/config.py",
        "app/db/base.py",
        "app/models/user.py",
        "app/models/schedule.py",
        "app/models/memo.py",
        "tests/conftest.py",
        "tests/test_models.py",
        "pytest.ini",
        "init_db.py",
    ]
    
    missing = []
    for file in files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - 不存在")
            missing.append(file)
    
    return len(missing) == 0


def check_config():
    """检查配置"""
    print("\n检查配置...")
    
    try:
        from app.core.config import settings
        print(f"  ✓ 项目名称: {settings.PROJECT_NAME}")
        print(f"  ✓ 数据库URL: {settings.DATABASE_URL}")
        print(f"  ✓ API版本: {settings.API_V1_STR}")
        return True
    except Exception as e:
        print(f"  ✗ 配置加载失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("手写管理助手 - 项目设置验证")
    print("=" * 50)
    
    checks = [
        ("模块导入", check_imports),
        ("文件结构", check_files),
        ("配置加载", check_config),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n{name}检查失败: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("验证结果:")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n✓ 所有检查通过！项目设置正确。")
        print("\n下一步:")
        print("1. 安装依赖: pip install -r requirements.txt 或 uv sync")
        print("2. 初始化数据库: python init_db.py")
        print("3. 运行测试: pytest")
        print("4. 启动服务: uvicorn main:app --reload")
        return 0
    else:
        print("\n✗ 部分检查失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
