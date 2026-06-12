"""产品经理 Agent 输出的结构化需求文档。"""

from pydantic import BaseModel, Field


class FeatureRequirement(BaseModel):
    """单个功能点的需求描述。"""

    name: str = Field(description="功能名称，例如：方向键控制")
    description: str = Field(description="功能说明，描述这个功能要解决什么问题")
    priority: str = Field(description="优先级，可取值建议为 high、medium、low")


class UserInteraction(BaseModel):
    """用户和页面之间的一次交互。"""

    action: str = Field(description="用户动作，例如：按下方向键")
    expected_result: str = Field(description="动作触发后的预期结果")


class AcceptanceCriterion(BaseModel):
    """验收标准，用来判断需求是否完成。"""

    criterion: str = Field(description="可验证的验收条件")


class RequirementDocument(BaseModel):
    """产品经理交给架构师的需求文档。"""

    app_name: str = Field(description="应用名称")
    summary: str = Field(description="一句话描述应用目标")
    target_users: list[str] = Field(description="目标用户")
    features: list[FeatureRequirement] = Field(description="功能点列表")
    user_interactions: list[UserInteraction] = Field(description="用户交互列表")
    acceptance_criteria: list[AcceptanceCriterion] = Field(description="验收标准列表")

