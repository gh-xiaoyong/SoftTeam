"""阶段 5B：正式测试 Runner。

Test Runner 是后续自动修复流程的固定入口：

1. 读取生成的 HTML/CSS/JavaScript 项目文件。
2. 执行预定义测试用例。
3. 输出统一的 TestReport。
4. 保存到 reports/test_report.md 和 reports/test_report.json。

当前阶段复用阶段 5A 的静态测试规则。这样可以先形成稳定的测试报告入口，
后续再逐步把浏览器交互测试、截图检查等能力加入 Runner。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from schemas import TestReport
from tools.artifact_writer import save_test_report
from tools.file_io import resolve_project_path
from tools.static_test_runner import DEFAULT_SNAKE_PROJECT_ROOT, run_static_snake_tests


@dataclass(frozen=True)
class GeneratedProjectFiles:
    """生成项目的源码文件快照。"""

    project_root: Path
    html_path: Path
    css_path: Path
    js_path: Path
    html: str
    css: str
    javascript: str


def read_generated_project_files(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
) -> GeneratedProjectFiles:
    """读取生成项目中的 HTML/CSS/JavaScript 文件。"""

    root = resolve_project_path(project_root)
    html_path = root / "index.html"
    css_path = root / "style.css"
    js_path = root / "script.js"

    return GeneratedProjectFiles(
        project_root=root,
        html_path=html_path,
        css_path=css_path,
        js_path=js_path,
        html=_read_optional_text(html_path),
        css=_read_optional_text(css_path),
        javascript=_read_optional_text(js_path),
    )


def run_predefined_tests(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
) -> TestReport:
    """执行预定义测试用例，并返回结构化测试报告。"""

    read_generated_project_files(project_root)
    report = run_static_snake_tests(project_root)
    return report.model_copy(
        update={
            "summary": _build_runner_summary(
                project_root=project_root,
                passed=report.passed,
                passed_count=report.passed_count,
                failed_count=report.failed_count,
            )
        }
    )


def run_predefined_test_cases(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
) -> TestReport:
    """执行预定义测试用例。

    这个函数名更贴近阶段 5B 的目标描述，保留 `run_predefined_tests`
    是为了让调用处可以使用更短的名字。
    """

    return run_predefined_tests(project_root)


def run_and_save_predefined_tests(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
) -> list[Path]:
    """执行预定义测试用例，并保存主测试报告。"""

    report = run_predefined_tests(project_root)
    return save_test_report(report)


def run_and_save_test_report(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
) -> list[Path]:
    """执行预定义测试用例，并写入 reports/test_report.*。"""

    return run_and_save_predefined_tests(project_root)


def _read_optional_text(path: Path) -> str:
    """读取源码文件；文件不存在时返回空字符串，让测试报告继续生成。"""

    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _build_runner_summary(
    project_root: str | Path,
    passed: bool,
    passed_count: int,
    failed_count: int,
) -> str:
    """生成阶段 5B 测试 Runner 的报告总结。"""

    status = "通过" if passed else "未通过"
    return (
        f"阶段 5B Test Runner 执行{status}。"
        f"测试目录：{project_root}；通过 {passed_count} 项，失败 {failed_count} 项。"
    )
