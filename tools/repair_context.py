"""开发修复任务的上下文组装工具。"""

from __future__ import annotations

from pathlib import Path

from schemas import (
    ArchitecturePlan,
    CodeManifest,
    GeneratedFile,
    RepairRequest,
    RequirementDocument,
    TestReport,
)
from tools.file_io import read_json_file
from tools.test_runner import DEFAULT_SNAKE_PROJECT_ROOT, read_generated_project_files


def build_repair_request(
    requirement: RequirementDocument,
    architecture: ArchitecturePlan,
    current_code: CodeManifest,
    test_report: TestReport,
) -> RepairRequest:
    """把修复所需的上下文组装成结构化输入。"""

    return RepairRequest(
        requirement=requirement,
        architecture=architecture,
        current_code=current_code,
        test_report=test_report,
        defects=test_report.defects,
    )


def load_current_code_manifest(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
) -> CodeManifest:
    """从磁盘读取当前 HTML/CSS/JS 源码，并组装成 CodeManifest。"""

    files = read_generated_project_files(project_root)
    root = str(project_root).replace("\\", "/")

    return CodeManifest(
        project_name=Path(root).name,
        project_root=root,
        entry_point=f"{root}/index.html",
        run_instruction=f"在浏览器中打开 {root}/index.html",
        files=[
            GeneratedFile(
                path=f"{root}/index.html",
                purpose="页面结构",
                language="html",
                content=files.html,
            ),
            GeneratedFile(
                path=f"{root}/style.css",
                purpose="页面样式",
                language="css",
                content=files.css,
            ),
            GeneratedFile(
                path=f"{root}/script.js",
                purpose="游戏逻辑",
                language="javascript",
                content=files.javascript,
            ),
        ],
    )


def load_repair_request_from_artifacts(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
) -> RepairRequest:
    """从已落盘产物中读取修复任务输入。"""

    requirement = RequirementDocument.model_validate(
        read_json_file("outputs/requirements.json")
    )
    architecture = ArchitecturePlan.model_validate(
        read_json_file("outputs/architecture.json")
    )
    current_code = load_current_code_manifest(project_root)
    test_report = TestReport.model_validate(read_json_file("reports/test_report.json"))

    return build_repair_request(
        requirement=requirement,
        architecture=architecture,
        current_code=current_code,
        test_report=test_report,
    )
