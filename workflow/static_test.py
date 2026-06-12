"""阶段 5A：本地静态测试工作流。"""

from __future__ import annotations

from pathlib import Path

from tools.artifact_writer import save_static_test_report
from tools.static_test_runner import DEFAULT_SNAKE_PROJECT_ROOT, run_static_snake_tests


def run_snake_static_tests(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
) -> list[Path]:
    """执行贪吃蛇静态测试，并把测试报告保存到 reports 目录。"""

    report = run_static_snake_tests(project_root)
    return save_static_test_report(report)
