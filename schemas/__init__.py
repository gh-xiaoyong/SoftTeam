"""结构化交接数据模型包。

这些模型定义了 4 类 Agent 之间的交接格式。
后续每个 Agent 的输出都应该尽量落到这些结构里，而不是只返回散乱文本。
"""

from schemas.architecture import ArchitecturePlan, FileDesign, ModuleDesign
from schemas.code_manifest import CodeManifest, GeneratedFile
from schemas.final_repair_report import FinalRepairReport, RepairRoundSummary
from schemas.requirement import (
    AcceptanceCriterion,
    FeatureRequirement,
    RequirementDocument,
    UserInteraction,
)
from schemas.repair_request import RepairRequest
from schemas.test_report import DefectReport, TestCaseResult, TestReport

__all__ = [
    "AcceptanceCriterion",
    "ArchitecturePlan",
    "CodeManifest",
    "DefectReport",
    "FeatureRequirement",
    "FileDesign",
    "FinalRepairReport",
    "GeneratedFile",
    "ModuleDesign",
    "RequirementDocument",
    "RepairRequest",
    "RepairRoundSummary",
    "TestCaseResult",
    "TestReport",
    "UserInteraction",
]
