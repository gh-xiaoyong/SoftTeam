"""验证阶段 5F 自动修复最终报告。"""

from __future__ import annotations

import shutil
import unittest

from schemas import CodeManifest, GeneratedFile, RepairRequest
from tools.file_io import read_json_file, resolve_project_path, write_text_file
from workflow.mock_demo import build_mock_architecture, build_mock_requirement
from workflow.repair import run_auto_repair_loop


class FinalRepairReportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_root = resolve_project_path("tmp/final-repair-report")
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

        self.requirement = build_mock_requirement()
        self.architecture = build_mock_architecture()

    def tearDown(self) -> None:
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

    def test_final_report_records_two_failed_repair_rounds(self) -> None:
        """最终报告应记录初始测试、两轮修复、未修复缺陷和源码路径。"""

        project_root = "tmp/final-repair-report/two-failed-rounds"
        self._write_broken_project(project_root)

        def repair_executor(_request: RepairRequest, _round_index: int) -> CodeManifest:
            return self._broken_manifest(project_root)

        result = run_auto_repair_loop(
            requirement=self.requirement,
            architecture=self.architecture,
            project_root=project_root,
            max_rounds=2,
            repair_executor=repair_executor,
        )
        report = read_json_file("reports/final_repair_report.json")

        self.assertFalse(result.passed)
        self.assertEqual(report["initial_report"]["failed_count"], result.initial_report.failed_count)
        self.assertEqual(len(report["round_results"]), 2)
        self.assertEqual(report["round_results"][0]["round_index"], 1)
        self.assertEqual(report["round_results"][1]["round_index"], 2)
        self.assertFalse(report["final_passed"])
        self.assertEqual(report["rounds_used"], 2)
        self.assertEqual(report["max_rounds"], 2)
        self.assertGreater(len(report["unresolved_defects"]), 0)
        self.assertIn(f"{project_root}/index.html", report["final_source_paths"])

    def _write_broken_project(self, project_root: str) -> None:
        write_text_file(
            f"{project_root}/index.html",
            "<html><body><h1>贪吃蛇</h1></body></html>\n",
        )

    def _broken_manifest(self, project_root: str) -> CodeManifest:
        return CodeManifest(
            project_name="broken-snake",
            project_root=project_root,
            entry_point=f"{project_root}/index.html",
            run_instruction="打开 index.html",
            files=[
                GeneratedFile(
                    path=f"{project_root}/index.html",
                    purpose="入口页面",
                    language="html",
                    content="<html><body><h1>贪吃蛇</h1></body></html>\n",
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
