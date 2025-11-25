"""测试运行脚本"""
import sys
import pytest


def run_all_tests():
    """运行所有测试"""
    print("运行所有测试...")
    return pytest.main(["-v", "tests/"])


def run_unit_tests():
    """只运行单元测试"""
    print("运行单元测试...")
    return pytest.main(["-v", "-m", "unit", "tests/"])


def run_property_tests():
    """只运行属性测试"""
    print("运行属性测试...")
    return pytest.main(["-v", "-m", "property", "tests/"])


def run_integration_tests():
    """只运行集成测试"""
    print("运行集成测试...")
    return pytest.main(["-v", "-m", "integration", "tests/"])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "unit":
            sys.exit(run_unit_tests())
        elif test_type == "property":
            sys.exit(run_property_tests())
        elif test_type == "integration":
            sys.exit(run_integration_tests())
        else:
            print(f"未知的测试类型: {test_type}")
            print("可用选项: unit, property, integration, 或不指定参数运行所有测试")
            sys.exit(1)
    else:
        sys.exit(run_all_tests())
