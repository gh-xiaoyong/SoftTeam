"""自动修复流程的最终报告结构。"""

from pydantic import BaseModel, Field

from schemas.test_report import DefectReport, TestReport


class RepairRoundSummary(BaseModel):
    """单轮修复结果摘要。"""

    round_index: int = Field(description="修复轮次，从 1 开始")
    before_passed: bool = Field(description="本轮修复前测试是否通过")
    before_failed_count: int = Field(description="本轮修复前失败数量")
    after_passed: bool | None = Field(default=None, description="本轮修复后测试是否通过")
    after_failed_count: int | None = Field(default=None, description="本轮修复后失败数量")
    repaired_file_paths: list[str] = Field(default_factory=list, description="本轮修复输出的源码路径")
    summary: str = Field(description="本轮修复摘要")


class FinalRepairReport(BaseModel):
    """最多 2 轮自动修复后的最终交付报告。"""

    initial_report: TestReport = Field(description="初始测试结果")
    round_results: list[RepairRoundSummary] = Field(description="每轮修复结果")
    final_passed: bool = Field(description="最终是否通过")
    rounds_used: int = Field(description="实际执行的修复轮数")
    max_rounds: int = Field(description="允许的最大修复轮数")
    unresolved_defects: list[DefectReport] = Field(default_factory=list, description="最终仍未修复的缺陷")
    final_source_paths: list[str] = Field(default_factory=list, description="最终源码文件路径")
    summary: str = Field(description="最终报告摘要")
