"""工作流产物保存工具。

这里负责把 Agent 的结构化输出保存成项目文件：

- Markdown 文档方便人阅读
- JSON 文件方便程序继续处理
- HTML/CSS/JavaScript 源码文件方便浏览器运行
"""

from __future__ import annotations

from pathlib import Path

from schemas import (
    ArchitecturePlan,
    CodeManifest,
    FinalRepairReport,
    RequirementDocument,
    TestReport,
)
from tools.file_io import write_json_file, write_model_json_file, write_text_file


def save_requirement_document(document: RequirementDocument) -> list[Path]:
    """保存产品经理输出的需求文档。"""

    markdown = [
        f"# {document.app_name} 需求文档",
        "",
        "## 应用概述",
        "",
        document.summary,
        "",
        "## 目标用户",
        "",
        *[f"- {user}" for user in document.target_users],
        "",
        "## 功能点",
        "",
    ]

    for feature in document.features:
        markdown.extend(
            [
                f"### {feature.name}",
                "",
                f"- 优先级：{feature.priority}",
                f"- 说明：{feature.description}",
                "",
            ]
        )

    markdown.extend(["## 用户交互", ""])
    markdown.extend(
        f"- {interaction.action} -> {interaction.expected_result}"
        for interaction in document.user_interactions
    )

    markdown.extend(["", "## 验收标准", ""])
    markdown.extend(f"- {item.criterion}" for item in document.acceptance_criteria)

    return [
        write_text_file("outputs/requirements.md", "\n".join(markdown) + "\n"),
        write_model_json_file("outputs/requirements.json", document),
    ]


def save_architecture_plan(plan: ArchitecturePlan) -> list[Path]:
    """保存架构师输出的技术方案。"""

    markdown = [
        "# 架构方案",
        "",
        "## 技术栈",
        "",
        *[f"- {item}" for item in plan.tech_stack],
        "",
        "## 文件设计",
        "",
    ]

    for file_design in plan.files:
        markdown.extend(
            [
                f"### {file_design.path}",
                "",
                file_design.responsibility,
                "",
            ]
        )

    markdown.extend(["## 模块设计", ""])
    for module in plan.modules:
        deps = "、".join(module.dependencies) if module.dependencies else "无"
        markdown.extend(
            [
                f"### {module.name}",
                "",
                f"- 职责：{module.responsibility}",
                f"- 依赖：{deps}",
                "",
            ]
        )

    markdown.extend(["## 数据流", ""])
    markdown.extend(f"- {item}" for item in plan.data_flow)

    markdown.extend(["", "## 实现注意事项", ""])
    markdown.extend(f"- {item}" for item in plan.implementation_notes)

    return [
        write_text_file("outputs/architecture.md", "\n".join(markdown) + "\n"),
        write_model_json_file("outputs/architecture.json", plan),
    ]


def save_code_manifest(manifest: CodeManifest) -> list[Path]:
    """保存开发工程师输出的代码清单和源码文件。"""

    written_files: list[Path] = []

    for generated_file in manifest.files:
        written_files.append(write_text_file(generated_file.path, generated_file.content))

    manifest_without_full_source = {
        "project_name": manifest.project_name,
        "project_root": manifest.project_root,
        "entry_point": manifest.entry_point,
        "run_instruction": manifest.run_instruction,
        "files": [
            {
                "path": file.path,
                "purpose": file.purpose,
                "language": file.language,
            }
            for file in manifest.files
        ],
    }

    written_files.append(
        write_json_file("outputs/file_manifest.json", manifest_without_full_source)
    )
    written_files.append(write_model_json_file("outputs/code_manifest.full.json", manifest))

    return written_files


def _build_test_report_markdown(report: TestReport) -> str:
    """把测试报告模型转换成 Markdown 文本。"""
    markdown = [
        "# 测试报告",
        "",
        f"- 是否通过：{report.passed}",
        f"- 用例总数：{report.total}",
        f"- 通过数量：{report.passed_count}",
        f"- 失败数量：{report.failed_count}",
        "",
        "## 测试用例结果",
        "",
    ]

    for case in report.cases:
        status = "通过" if case.passed else "失败"
        markdown.extend(
            [
                f"### {case.name}",
                "",
                f"- 状态：{status}",
                f"- 预期：{case.expected}",
                f"- 实际：{case.actual}",
                f"- 说明：{case.detail}",
                "",
            ]
        )

    markdown.extend(["## 缺陷列表", ""])
    if report.defects:
        for defect in report.defects:
            markdown.extend(
                [
                    f"### {defect.case_name}",
                    "",
                    f"- 严重程度：{defect.severity}",
                    f"- 缺陷说明：{defect.description}",
                    f"- 修复建议：{defect.suggestion}",
                    "",
                ]
            )
    else:
        markdown.append("无")

    markdown.extend(["", "## 总结", "", report.summary])

    return "\n".join(markdown) + "\n"


def save_test_report(report: TestReport) -> list[Path]:
    """保存测试工程师输出的测试报告。"""

    return [
        write_text_file("reports/test_report.md", _build_test_report_markdown(report)),
        write_model_json_file("reports/test_report.json", report),
    ]


def save_static_test_report(report: TestReport) -> list[Path]:
    """保存阶段 5A 的本地静态测试报告。"""

    return [
        write_text_file(
            "reports/static_test_report.md",
            _build_test_report_markdown(report),
        ),
        write_model_json_file("reports/static_test_report.json", report),
    ]


def save_final_repair_report(report: FinalRepairReport) -> list[Path]:
    """保存阶段 5F 的自动修复最终报告。"""

    markdown = [
        "# 自动修复最终报告",
        "",
        "## 初始测试结果",
        "",
        f"- 是否通过：{report.initial_report.passed}",
        f"- 用例总数：{report.initial_report.total}",
        f"- 通过数量：{report.initial_report.passed_count}",
        f"- 失败数量：{report.initial_report.failed_count}",
        "",
        "## 修复轮次结果",
        "",
    ]

    if report.round_results:
        for round_result in report.round_results:
            after_passed = (
                "未执行"
                if round_result.after_passed is None
                else str(round_result.after_passed)
            )
            after_failed_count = (
                "未执行"
                if round_result.after_failed_count is None
                else str(round_result.after_failed_count)
            )
            markdown.extend(
                [
                    f"### 第 {round_result.round_index} 轮修复",
                    "",
                    f"- 修复前是否通过：{round_result.before_passed}",
                    f"- 修复前失败数量：{round_result.before_failed_count}",
                    f"- 修复后是否通过：{after_passed}",
                    f"- 修复后失败数量：{after_failed_count}",
                    "- 修复源码路径：",
                    *[f"  - {path}" for path in round_result.repaired_file_paths],
                    f"- 摘要：{round_result.summary}",
                    "",
                ]
            )
    else:
        markdown.extend(["没有执行修复轮次，初始测试已经通过。", ""])

    markdown.extend(
        [
            "## 最终结果",
            "",
            f"- 最终是否通过：{report.final_passed}",
            f"- 实际修复轮数：{report.rounds_used}",
            f"- 最大修复轮数：{report.max_rounds}",
            "",
            "## 未修复缺陷",
            "",
        ]
    )

    if report.unresolved_defects:
        for defect in report.unresolved_defects:
            markdown.extend(
                [
                    f"### {defect.case_name}",
                    "",
                    f"- 严重程度：{defect.severity}",
                    f"- 缺陷说明：{defect.description}",
                    f"- 修复建议：{defect.suggestion}",
                    "",
                ]
            )
    else:
        markdown.extend(["无", ""])

    markdown.extend(["## 最终源码路径", ""])
    markdown.extend(f"- {path}" for path in report.final_source_paths)
    markdown.extend(["", "## 总结", "", report.summary])

    return [
        write_text_file("reports/final_repair_report.md", "\n".join(markdown) + "\n"),
        write_model_json_file("reports/final_repair_report.json", report),
    ]


def save_demo_artifacts(
    requirement: RequirementDocument,
    architecture: ArchitecturePlan,
    code_manifest: CodeManifest,
    test_report: TestReport,
) -> list[Path]:
    """保存一次完整 Demo 的全部产物。"""

    written_files: list[Path] = []
    written_files.extend(save_requirement_document(requirement))
    written_files.extend(save_architecture_plan(architecture))
    written_files.extend(save_code_manifest(code_manifest))
    written_files.extend(save_test_report(test_report))
    return written_files
