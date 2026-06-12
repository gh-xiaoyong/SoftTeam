"""验证阶段 5C：Demo 流程接入本地 Test Runner。"""

from __future__ import annotations

import shutil
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from schemas import (
    CodeManifest,
    GeneratedFile,
    TestCaseResult,
    TestReport,
)
from tools.file_io import read_json_file, resolve_project_path
from workflow.mock_demo import build_mock_architecture, build_mock_requirement, run_mock_snake_demo
from workflow.run_demo import run_snake_demo


class WorkflowTestRunnerIntegrationTest(unittest.TestCase):
    def tearDown(self) -> None:
        tmp_root = resolve_project_path("tmp/stage5c")
        if tmp_root.exists():
            shutil.rmtree(tmp_root)

    def test_mock_demo_writes_report_from_local_runner(self) -> None:
        """Mock Demo 的最终报告应来自本地 Test Runner。"""

        run_mock_snake_demo()

        report = read_json_file("reports/test_report.json")

        self.assertTrue(report["passed"])
        self.assertEqual(report["total"], 10)
        self.assertIn("阶段 5B Test Runner", report["summary"])

    def test_real_demo_uses_local_runner_defects_instead_of_agent_report(self) -> None:
        """即使测试 Agent 说通过，最终报告也应以本地 Runner 的缺陷为准。"""

        broken_manifest = CodeManifest(
            project_name="broken-snake",
            project_root="tmp/stage5c/broken-snake",
            entry_point="tmp/stage5c/broken-snake/index.html",
            run_instruction="打开 index.html",
            files=[
                GeneratedFile(
                    path="tmp/stage5c/broken-snake/index.html",
                    purpose="故意缺少样式、脚本和游戏区域的入口文件",
                    language="html",
                    content="<html><body><h1>贪吃蛇</h1></body></html>\n",
                )
            ],
        )
        agent_report = TestReport(
            passed=True,
            total=1,
            passed_count=1,
            failed_count=0,
            cases=[
                TestCaseResult(
                    name="测试 Agent 自评",
                    passed=True,
                    expected="全部通过",
                    actual="全部通过",
                    detail="这个结果不应该成为最终测试结论。",
                )
            ],
            defects=[],
            summary="测试 Agent 判断通过。",
        )
        fake_tasks = {
            "requirement": SimpleNamespace(output=SimpleNamespace(pydantic=build_mock_requirement())),
            "architecture": SimpleNamespace(output=SimpleNamespace(pydantic=build_mock_architecture())),
            "development": SimpleNamespace(output=SimpleNamespace(pydantic=broken_manifest)),
            "test": SimpleNamespace(output=SimpleNamespace(pydantic=agent_report)),
        }
        fake_build_result = SimpleNamespace(
            crew=SimpleNamespace(kickoff=lambda: None),
            tasks=fake_tasks,
        )

        with patch("workflow.run_demo.ensure_llm_configured", return_value=None), patch(
            "workflow.run_demo.build_sequential_crew",
            return_value=fake_build_result,
        ):
            run_snake_demo()

        report = read_json_file("reports/test_report.json")
        failed_case_names = {case["name"] for case in report["cases"] if not case["passed"]}

        self.assertFalse(report["passed"])
        self.assertGreater(report["failed_count"], 0)
        self.assertGreater(len(report["defects"]), 0)
        self.assertIn("style.css 文件存在", failed_case_names)
        self.assertIn("script.js 文件存在", failed_case_names)
        self.assertIn("阶段 5B Test Runner", report["summary"])


if __name__ == "__main__":
    unittest.main()
