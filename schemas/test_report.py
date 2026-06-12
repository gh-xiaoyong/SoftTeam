"""测试工程师 Agent 输出的结构化测试报告。"""

from pydantic import BaseModel, Field


class TestCaseResult(BaseModel):
    """单个测试用例的执行结果。"""

    name: str = Field(description="测试用例名称")
    passed: bool = Field(description="是否通过")
    expected: str = Field(description="预期结果")
    actual: str = Field(description="实际结果")
    detail: str = Field(default="", description="补充说明")


class DefectReport(BaseModel):
    """测试失败时反馈给开发工程师的缺陷描述。"""

    case_name: str = Field(description="关联的测试用例名称")
    severity: str = Field(description="严重程度，可取值建议为 high、medium、low")
    description: str = Field(description="缺陷说明")
    suggestion: str = Field(description="建议修复方向")


class TestReport(BaseModel):
    """测试工程师输出的测试报告。"""

    passed: bool = Field(description="整体是否通过")
    total: int = Field(description="测试用例总数")
    passed_count: int = Field(description="通过数量")
    failed_count: int = Field(description="失败数量")
    cases: list[TestCaseResult] = Field(description="测试用例结果列表")
    defects: list[DefectReport] = Field(default_factory=list, description="缺陷列表")
    summary: str = Field(description="测试总结")

