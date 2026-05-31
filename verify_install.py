#!/usr/bin/env python3
"""知识库框架安装验证脚本 — 验证依赖、目录结构和关键文件完整性"""
import sys
import os
import subprocess
import importlib
from pathlib import Path

class VerifyReport:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def ok(self, msg):
        self.passed.append(msg)
        print(f"  [OK] {msg}")

    def fail(self, msg, fix=None):
        self.failed.append(msg)
        print(f"  [FAIL] {msg}")
        if fix:
            print(f"         → {fix}")

    def warn(self, msg):
        self.warnings.append(msg)
        print(f"  [WARN] {msg}")

    def summary(self):
        print(f"\n{'='*50}")
        print(f"验证结果: {len(self.passed)} 通过 | {len(self.failed)} 失败 | {len(self.warnings)} 警告")
        if self.failed:
            print("\n请先修复失败项，再运行本脚本确认。")
            return 1
        else:
            print("\n验证通过！项目可正常运行。")
            return 0


def main():
    report = VerifyReport()
    print("通用知识库框架 V2.0 — 安装验证")
    print(f"工作目录: {os.getcwd()}")
    print(f"Python: {sys.version}")
    print()

    # 1. Python 版本
    if sys.version_info >= (3, 8):
        report.ok(f"Python {sys.version_info.major}.{sys.version_info.minor} >= 3.8")
    else:
        report.fail("Python 版本过低", "升级至 Python 3.8+")

    # 2. 核心依赖
    required = [
        ("flask", "Flask", True),
        ("numpy", "numpy", True),
        ("yaml", "PyYAML", True),
        ("mcp", "mcp", True),
        ("pytest", "pytest", False),
    ]
    for import_name, pkg_name, critical in required:
        try:
            m = importlib.import_module(import_name)
            ver = getattr(m, "__version__", "unknown")
            report.ok(f"依赖 {pkg_name} ({ver})")
        except ImportError:
            if critical:
                report.fail(f"缺失关键依赖: {pkg_name}", "pip install -r requirements.txt")
            else:
                report.warn(f"可选依赖缺失: {pkg_name}")

    # 3. 目录结构
    expected_dirs = [
        "00-快速开始",
        "01-收件箱",
        "02-对话记录",
        "03-资产库",
        "04-输出成果",
        "05-知识沉淀",
        "06-参考资料",
        "07-项目文档",
        "99-归档",
        ".workbuddy/scripts",
    ]
    for d in expected_dirs:
        if Path(d).exists():
            report.ok(f"目录 {d}/")
        else:
            report.fail(f"缺失目录: {d}/", "运行 00-快速开始/setup.bat 初始化")

    # 4. 关键文件
    expected_files = [
        ("README.md", True),
        ("requirements.txt", True),
        (".env.example", False),
        ("app.py", True),
        ("mcp_server.py", False),
    ]
    for f, critical in expected_files:
        if Path(f).exists():
            report.ok(f"文件 {f}")
        else:
            if critical:
                report.fail(f"缺失关键文件: {f}", "确认项目完整性")
            else:
                report.warn(f"可选文件缺失: {f}")

    # 5. .env 检查
    if Path(".env").exists():
        report.ok("已配置 .env 环境文件")
    else:
        report.warn("未配置 .env 环境文件 — API 密钥和高级功能不可用")
        print("         → 复制 .env.example 为 .env 并填入实际值")

    # 6. 测试套件
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--co", "-q"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            last = lines[-1] if lines else "unknown"
            report.ok(f"测试套件: {last}")
        else:
            report.warn("测试套件加载异常")
    except Exception as e:
        report.warn(f"测试套件验证失败: {e}")

    # 7. Flask 运行能力
    try:
        import flask  # noqa: F401
        report.ok("Flask 可正常导入")
    except ImportError:
        report.fail("Flask 导入失败", "pip install Flask")

    return report.summary()


if __name__ == "__main__":
    sys.exit(main())
