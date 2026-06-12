"""CrewAI Task 创建工厂。

阶段 4B 只负责创建任务对象，不执行 Crew。
任务之间通过 `context` 建立上下游关系。
"""

from __future__ import annotations

from crewai import Agent, Task

from config import supports_native_response_format
from schemas import ArchitecturePlan, CodeManifest, RepairRequest, RequirementDocument, TestReport


def _structured_output_kwargs(schema: type) -> dict[str, type]:
    """根据模型能力决定是否使用 CrewAI 原生结构化输出。"""

    if supports_native_response_format():
        return {"output_pydantic": schema}

    return {}


def _json_only_instruction(schema_name: str) -> str:
    """给不支持原生结构化输出的模型补充 JSON 输出要求。"""

    return (
        f"\n\n请只输出一个合法 JSON 对象，不要输出 Markdown 代码块，不要输出解释文字。"
        f"JSON 内容必须符合 {schema_name} 的字段要求。"
        "如果字段要求是对象数组，数组元素必须是对象，不能用字符串代替。"
    )


REQUIREMENT_JSON_SHAPE = """
字段结构要求：
{
  "target_users": ["用户群体"],
  "features": [
    {"name": "功能名", "description": "功能说明", "priority": "high"}
  ],
  "user_interactions": [
    {"action": "用户动作", "expected_result": "预期结果"}
  ],
  "acceptance_criteria": [
    {"criterion": "验收标准"}
  ]
}
"""


ARCHITECTURE_JSON_SHAPE = """
字段结构要求：
{
  "files": [
    {"path": "文件路径", "responsibility": "文件职责"}
  ],
  "modules": [
    {"name": "模块名", "responsibility": "模块职责", "dependencies": ["依赖模块"]}
  ],
  "data_flow": ["数据流说明"],
  "implementation_notes": ["实现注意事项"]
}
"""


CODE_MANIFEST_JSON_SHAPE = """
字段结构要求：
{
  "files": [
    {
      "path": "generated/snake-game/index.html",
      "purpose": "文件用途",
      "language": "html",
      "content": "完整源码"
    }
  ]
}
"""


TEST_REPORT_JSON_SHAPE = """
字段结构要求：
{
  "cases": [
    {"name": "用例名", "passed": true, "expected": "预期", "actual": "实际", "detail": "说明"}
  ],
  "defects": [
    {"case_name": "用例名", "severity": "medium", "description": "缺陷说明", "suggestion": "修复建议"}
  ]
}
"""


def create_requirement_task(agent: Agent, user_request: str) -> Task:
    """创建需求分析任务。"""

    return Task(
        name="需求分析任务",
        description=(
            "请分析用户输入的 Web 应用需求，并整理成结构化需求文档。\n\n"
            f"用户原始需求：\n{user_request}\n\n"
            "请重点明确：应用名称、目标用户、核心功能、用户交互、验收标准。"
        ),
        expected_output=(
            "输出一个结构化需求文档，字段需要覆盖 app_name、summary、target_users、"
            "features、user_interactions、acceptance_criteria。"
            + REQUIREMENT_JSON_SHAPE
            + _json_only_instruction("RequirementDocument")
        ),
        agent=agent,
        context=[],
        **_structured_output_kwargs(RequirementDocument),
    )


def create_architecture_task(agent: Agent, requirement_task: Task) -> Task:
    """创建架构设计任务。"""

    return Task(
        name="架构设计任务",
        description=(
            "请基于产品经理输出的需求文档，设计一个简单、可运行、可测试的前端技术方案。\n\n"
            "技术方案应该适合生成纯 HTML/CSS/JavaScript 项目，不引入复杂框架。"
        ),
        expected_output=(
            "输出一个结构化架构方案，字段需要覆盖 tech_stack、files、modules、"
            "data_flow、implementation_notes。"
            + ARCHITECTURE_JSON_SHAPE
            + _json_only_instruction("ArchitecturePlan")
        ),
        agent=agent,
        context=[requirement_task],
        **_structured_output_kwargs(ArchitecturePlan),
    )


def create_development_task(
    agent: Agent,
    requirement_task: Task,
    architecture_task: Task,
) -> Task:
    """创建代码生成任务。"""

    return Task(
        name="代码生成任务",
        description=(
            "请基于需求文档和架构方案，生成一个可运行的纯前端 Web 应用。\n\n"
            "必须生成 index.html、style.css、script.js 三个文件。"
            "每个文件都需要给出完整源码内容，后续流程会把这些内容写入磁盘。\n\n"
            "请固定使用以下相对路径：\n"
            "- generated/snake-game/index.html\n"
            "- generated/snake-game/style.css\n"
            "- generated/snake-game/script.js\n\n"
            "project_root 必须是 generated/snake-game，entry_point 必须是 "
            "generated/snake-game/index.html。"
        ),
        expected_output=(
            "输出一个结构化代码清单，字段需要覆盖 project_name、project_root、entry_point、"
            "files、run_instruction。files 中每个文件必须包含 path、purpose、language、content。"
            + CODE_MANIFEST_JSON_SHAPE
            + _json_only_instruction("CodeManifest")
        ),
        agent=agent,
        context=[requirement_task, architecture_task],
        **_structured_output_kwargs(CodeManifest),
    )


def create_test_task(agent: Agent, development_task: Task) -> Task:
    """创建测试验证任务。"""

    return Task(
        name="测试验证任务",
        description=(
            "请基于开发工程师生成的代码清单，按照预定义测试点检查 Web 应用是否满足需求。\n\n"
            "测试点包括：页面入口、样式引用、脚本引用、游戏区域、分数显示、"
            "方向控制、食物逻辑、碰撞结束、重新开始。"
        ),
        expected_output=(
            "输出一个结构化测试报告，字段需要覆盖 passed、total、passed_count、"
            "failed_count、cases、defects、summary。若有失败项，defects 必须说明缺陷和修复建议。"
            + TEST_REPORT_JSON_SHAPE
            + _json_only_instruction("TestReport")
        ),
        agent=agent,
        context=[development_task],
        **_structured_output_kwargs(TestReport),
    )


def create_repair_task(agent: Agent, repair_request: RepairRequest) -> Task:
    """创建开发修复任务。"""

    repair_context_json = repair_request.model_dump_json(indent=2)

    return Task(
        name="开发修复任务",
        description=(
            "请基于本地 Test Runner 生成的结构化缺陷报告修复当前前端源码。\n\n"
            "修复输入包含：原始需求、架构方案、当前源码、测试报告、缺陷列表。\n"
            "请优先做最小必要改动，不要重写无关功能，不要改变既有文件路径。\n\n"
            "修复输入 JSON：\n"
            f"{repair_context_json}\n\n"
            "修复要求：\n"
            "- 必须输出修复后的完整源码文件清单。\n"
            "- 必须保留 project_root 为当前项目根目录。\n"
            "- 必须包含 index.html、style.css、script.js 三个文件。\n"
            "- 每个文件必须包含完整 content，不能只输出补丁片段。\n"
            "- 如果缺陷列表为空，请返回当前源码，不要制造额外变化。"
        ),
        expected_output=(
            "输出一个修复后的 CodeManifest，字段需要覆盖 project_name、project_root、"
            "entry_point、files、run_instruction。files 中每个文件必须包含 "
            "path、purpose、language、content。"
            + CODE_MANIFEST_JSON_SHAPE
            + _json_only_instruction("CodeManifest")
        ),
        agent=agent,
        context=[],
        **_structured_output_kwargs(CodeManifest),
    )


def create_all_tasks(agents: dict[str, Agent], user_request: str) -> dict[str, Task]:
    """根据 4 个 Agent 创建完整顺序任务链。"""

    requirement_task = create_requirement_task(
        agent=agents["product_manager"],
        user_request=user_request,
    )
    architecture_task = create_architecture_task(
        agent=agents["architect"],
        requirement_task=requirement_task,
    )
    development_task = create_development_task(
        agent=agents["developer"],
        requirement_task=requirement_task,
        architecture_task=architecture_task,
    )
    test_task = create_test_task(
        agent=agents["tester"],
        development_task=development_task,
    )

    return {
        "requirement": requirement_task,
        "architecture": architecture_task,
        "development": development_task,
        "test": test_task,
    }
