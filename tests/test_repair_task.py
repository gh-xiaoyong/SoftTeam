"""验证阶段 5D 开发修复任务。"""

from __future__ import annotations

import shutil
import unittest

from agents import create_developer_agent
from schemas import (
    ArchitecturePlan,
    CodeManifest,
    FileDesign,
    GeneratedFile,
    ModuleDesign,
    RequirementDocument,
)
from tasks import create_repair_task
from tools.file_io import resolve_project_path, write_text_file
from tools.repair_context import build_repair_request, load_current_code_manifest
from tools.test_runner import run_predefined_test_cases
from workflow.mock_demo import run_mock_snake_demo
from workflow.repair import build_repair_task_from_artifacts


class RepairTaskTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_root = resolve_project_path("tmp/repair-task")
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

    def tearDown(self) -> None:
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

    def test_load_current_code_manifest_reads_current_source_files(self) -> None:
        """修复上下文应读取磁盘上的当前源码。"""

        project_root = "tmp/repair-task/source"
        write_text_file(f"{project_root}/index.html", "<html></html>\n")
        write_text_file(f"{project_root}/style.css", "body { margin: 0; }\n")
        write_text_file(f"{project_root}/script.js", "console.log('repair');\n")

        manifest = load_current_code_manifest(project_root)

        self.assertEqual(manifest.project_root, project_root)
        self.assertEqual(len(manifest.files), 3)
        self.assertEqual(manifest.files[0].path, f"{project_root}/index.html")
        self.assertIn("console.log", manifest.files[2].content)

    def test_create_repair_task_contains_structured_repair_input(self) -> None:
        """开发修复任务应包含需求、架构、当前源码、测试报告和缺陷列表。"""

        project_root = "tmp/repair-task/broken"
        write_text_file(
            f"{project_root}/index.html",
            "<html><body><h1>贪吃蛇</h1></body></html>\n",
        )
        current_code = CodeManifest(
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
        requirement = RequirementDocument(
            app_name="贪吃蛇游戏",
            summary="实现一个可运行的贪吃蛇 HTML 游戏。",
            target_users=["浏览器用户"],
            features=[],
            user_interactions=[],
            acceptance_criteria=[],
        )
        architecture = ArchitecturePlan(
            tech_stack=["HTML", "CSS", "JavaScript"],
            files=[
                FileDesign(path=f"{project_root}/index.html", responsibility="页面结构"),
            ],
            modules=[
                ModuleDesign(name="游戏逻辑", responsibility="实现移动、碰撞和计分"),
            ],
            data_flow=[],
            implementation_notes=[],
        )
        test_report = run_predefined_test_cases(project_root)
        repair_request = build_repair_request(
            requirement=requirement,
            architecture=architecture,
            current_code=current_code,
            test_report=test_report,
        )
        developer = create_developer_agent()

        task = create_repair_task(developer, repair_request)

        self.assertEqual(task.name, "开发修复任务")
        self.assertEqual(task.agent.role, "开发工程师")
        self.assertGreater(len(repair_request.defects), 0)
        self.assertIn("style.css 文件存在", task.description)
        self.assertIn("当前源码", task.description)
        self.assertIn("CodeManifest", task.expected_output)

    def test_build_repair_task_from_artifacts(self) -> None:
        """工作流入口应能从已落盘产物构建修复任务。"""

        run_mock_snake_demo()

        result = build_repair_task_from_artifacts()

        self.assertEqual(result.developer.role, "开发工程师")
        self.assertEqual(result.repair_task.name, "开发修复任务")
        self.assertEqual(result.repair_request.current_code.project_root, "generated/snake-game")
        self.assertEqual(len(result.repair_request.current_code.files), 3)


if __name__ == "__main__":
    unittest.main()
