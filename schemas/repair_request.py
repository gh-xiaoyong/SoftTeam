"""开发修复任务的结构化输入。"""

from pydantic import BaseModel, Field

from schemas.architecture import ArchitecturePlan
from schemas.code_manifest import CodeManifest
from schemas.requirement import RequirementDocument
from schemas.test_report import DefectReport, TestReport


class RepairRequest(BaseModel):
    """开发 Agent 执行修复时需要的完整上下文。"""

    requirement: RequirementDocument = Field(description="原始需求文档")
    architecture: ArchitecturePlan = Field(description="架构方案")
    current_code: CodeManifest = Field(description="当前源码文件清单，包含完整源码内容")
    test_report: TestReport = Field(description="本地 Test Runner 生成的测试报告")
    defects: list[DefectReport] = Field(description="需要开发 Agent 修复的缺陷列表")
