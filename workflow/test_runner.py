"""阶段 5B：测试 Runner 工作流入口。"""

from __future__ import annotations

from pathlib import Path

from tools.test_runner import DEFAULT_SNAKE_PROJECT_ROOT, run_and_save_test_report


def run_snake_test_runner(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
) -> list[Path]:
    """执行贪吃蛇项目测试 Runner，并保存主测试报告。"""

    return run_and_save_test_report(project_root)
