"""阶段 5D：开发修复任务工作流入口。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from crewai import Agent, Crew, Process, Task

from agents import create_developer_agent
from schemas import (
    ArchitecturePlan,
    CodeManifest,
    FinalRepairReport,
    RepairRequest,
    RepairRoundSummary,
    RequirementDocument,
    TestReport,
)
from tasks import create_repair_task
from tools.artifact_writer import save_code_manifest, save_final_repair_report, save_test_report
from tools.file_io import read_json_file
from tools.repair_context import (
    build_repair_request,
    load_current_code_manifest,
    load_repair_request_from_artifacts,
)
from tools.test_runner import DEFAULT_SNAKE_PROJECT_ROOT, run_predefined_test_cases
from workflow.run_demo import _get_task_model, ensure_llm_configured


@dataclass(frozen=True)
class RepairTaskBuildResult:
    """开发修复任务的构建结果。"""

    developer: Agent
    repair_task: Task
    repair_request: RepairRequest


@dataclass(frozen=True)
class RepairRoundRecord:
    """单轮修复尝试记录。"""

    round_index: int
    before_report: TestReport
    repaired_manifest: CodeManifest | None
    after_report: TestReport | None


@dataclass(frozen=True)
class RepairLoopResult:
    """自动修复循环结果。"""

    passed: bool
    rounds_used: int
    max_rounds: int
    initial_report: TestReport
    final_report: TestReport
    final_source_paths: list[str]
    final_repair_report: FinalRepairReport
    records: list[RepairRoundRecord]


RepairExecutor = Callable[[RepairRequest, int], CodeManifest]


def build_repair_task_from_artifacts() -> RepairTaskBuildResult:
    """从当前产物构建开发修复任务。

    这个函数只构建任务，不执行大模型。真正执行和最多 2 轮修复循环会放到后续阶段。
    """

    repair_request = load_repair_request_from_artifacts()
    developer = create_developer_agent()
    repair_task = create_repair_task(developer, repair_request)

    return RepairTaskBuildResult(
        developer=developer,
        repair_task=repair_task,
        repair_request=repair_request,
    )


def execute_repair_task(repair_request: RepairRequest, round_index: int = 1) -> CodeManifest:
    """真实执行开发修复任务，并返回修复后的源码清单。"""

    ensure_llm_configured()

    developer = create_developer_agent()
    repair_task = create_repair_task(developer, repair_request)
    crew = Crew(
        agents=[developer],
        tasks=[repair_task],
        process=Process.sequential,
        verbose=True,
    )

    crew.kickoff()
    return _get_task_model(repair_task.output, CodeManifest)


def run_auto_repair_loop(
    requirement: RequirementDocument,
    architecture: ArchitecturePlan,
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
    max_rounds: int = 2,
    repair_executor: RepairExecutor | None = None,
) -> RepairLoopResult:
    """执行最多 max_rounds 轮自动修复循环。"""

    if max_rounds < 0:
        raise ValueError("max_rounds 不能小于 0。")

    executor = repair_executor or execute_repair_task
    records: list[RepairRoundRecord] = []
    current_project_root = project_root
    current_report = _run_and_save_tests(project_root)
    initial_report = current_report

    if current_report.passed:
        final_source_paths = _load_final_source_paths(project_root)
        final_repair_report = _build_final_repair_report(
            initial_report=initial_report,
            final_report=current_report,
            records=records,
            rounds_used=0,
            max_rounds=max_rounds,
            final_source_paths=final_source_paths,
        )
        save_final_repair_report(final_repair_report)
        return RepairLoopResult(
            passed=True,
            rounds_used=0,
            max_rounds=max_rounds,
            initial_report=initial_report,
            final_report=current_report,
            final_source_paths=final_source_paths,
            final_repair_report=final_repair_report,
            records=records,
        )

    for round_index in range(1, max_rounds + 1):
        current_code = load_current_code_manifest(project_root)
        repair_request = build_repair_request(
            requirement=requirement,
            architecture=architecture,
            current_code=current_code,
            test_report=current_report,
        )
        repaired_manifest = executor(repair_request, round_index)
        save_code_manifest(repaired_manifest)

        current_project_root = repaired_manifest.project_root
        after_report = _run_and_save_tests(current_project_root)
        records.append(
            RepairRoundRecord(
                round_index=round_index,
                before_report=current_report,
                repaired_manifest=repaired_manifest,
                after_report=after_report,
            )
        )

        current_report = after_report
        if current_report.passed:
            final_source_paths = _manifest_paths(repaired_manifest)
            final_repair_report = _build_final_repair_report(
                initial_report=initial_report,
                final_report=current_report,
                records=records,
                rounds_used=round_index,
                max_rounds=max_rounds,
                final_source_paths=final_source_paths,
            )
            save_final_repair_report(final_repair_report)
            return RepairLoopResult(
                passed=True,
                rounds_used=round_index,
                max_rounds=max_rounds,
                initial_report=initial_report,
                final_report=current_report,
                final_source_paths=final_source_paths,
                final_repair_report=final_repair_report,
                records=records,
            )

    final_source_paths = _load_final_source_paths(current_project_root)
    final_repair_report = _build_final_repair_report(
        initial_report=initial_report,
        final_report=current_report,
        records=records,
        rounds_used=max_rounds,
        max_rounds=max_rounds,
        final_source_paths=final_source_paths,
    )
    save_final_repair_report(final_repair_report)
    return RepairLoopResult(
        passed=False,
        rounds_used=max_rounds,
        max_rounds=max_rounds,
        initial_report=initial_report,
        final_report=current_report,
        final_source_paths=final_source_paths,
        final_repair_report=final_repair_report,
        records=records,
    )


def run_auto_repair_loop_from_artifacts(
    project_root: str | Path = DEFAULT_SNAKE_PROJECT_ROOT,
    max_rounds: int = 2,
    repair_executor: RepairExecutor | None = None,
) -> RepairLoopResult:
    """从已落盘产物读取需求和架构，并执行自动修复循环。"""

    requirement = RequirementDocument.model_validate(
        read_json_file("outputs/requirements.json")
    )
    architecture = ArchitecturePlan.model_validate(
        read_json_file("outputs/architecture.json")
    )

    return run_auto_repair_loop(
        requirement=requirement,
        architecture=architecture,
        project_root=project_root,
        max_rounds=max_rounds,
        repair_executor=repair_executor,
    )


def _run_and_save_tests(project_root: str | Path) -> TestReport:
    """运行本地 Test Runner，并保存主测试报告。"""

    report = run_predefined_test_cases(project_root)
    save_test_report(report)
    return report


def _build_final_repair_report(
    initial_report: TestReport,
    final_report: TestReport,
    records: list[RepairRoundRecord],
    rounds_used: int,
    max_rounds: int,
    final_source_paths: list[str],
) -> FinalRepairReport:
    """根据自动修复循环结果生成最终报告模型。"""

    round_results = [
        RepairRoundSummary(
            round_index=record.round_index,
            before_passed=record.before_report.passed,
            before_failed_count=record.before_report.failed_count,
            after_passed=record.after_report.passed if record.after_report else None,
            after_failed_count=record.after_report.failed_count if record.after_report else None,
            repaired_file_paths=(
                _manifest_paths(record.repaired_manifest)
                if record.repaired_manifest
                else []
            ),
            summary=_build_round_summary(record),
        )
        for record in records
    ]
    status = "通过" if final_report.passed else "未通过"

    return FinalRepairReport(
        initial_report=initial_report,
        round_results=round_results,
        final_passed=final_report.passed,
        rounds_used=rounds_used,
        max_rounds=max_rounds,
        unresolved_defects=final_report.defects,
        final_source_paths=final_source_paths,
        summary=(
            f"自动修复流程最终{status}。"
            f"初始失败 {initial_report.failed_count} 项，"
            f"执行修复 {rounds_used} 轮，"
            f"最终失败 {final_report.failed_count} 项。"
        ),
    )


def _build_round_summary(record: RepairRoundRecord) -> str:
    """生成单轮修复摘要。"""

    if not record.after_report:
        return "本轮未产生修复后测试报告。"

    status = "通过" if record.after_report.passed else "未通过"
    return (
        f"第 {record.round_index} 轮修复后测试{status}，"
        f"失败数量从 {record.before_report.failed_count} 变为 "
        f"{record.after_report.failed_count}。"
    )


def _manifest_paths(manifest: CodeManifest) -> list[str]:
    """提取源码清单中的文件路径。"""

    return [file.path for file in manifest.files]


def _load_final_source_paths(project_root: str | Path) -> list[str]:
    """读取当前源码文件路径，用于最终报告。"""

    return _manifest_paths(load_current_code_manifest(project_root))
