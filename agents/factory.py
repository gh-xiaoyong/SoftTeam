"""CrewAI Agent 创建工厂。

阶段 4A 只负责创建 4 类 Agent，不创建 Task，也不执行 Crew。
这样可以单独验证 Agent 定义是否清晰、CrewAI 对象是否能正常构造。
"""

from __future__ import annotations

from crewai import Agent

from config import create_configured_llm


def _create_agent(role: str, goal: str, backstory: str) -> Agent:
    """按统一配置创建 Agent。"""

    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        allow_delegation=False,
        verbose=True,
        llm=create_configured_llm(),
    )


def create_product_manager_agent() -> Agent:
    """创建产品经理 Agent。"""

    return _create_agent(
        role="产品经理",
        goal=(
            "把用户输入的简单 Web 应用需求整理成结构化需求文档，"
            "明确功能点、用户交互和验收标准。"
        ),
        backstory=(
            "你是一名注重交付边界的产品经理。"
            "你擅长把模糊需求拆成清晰、可验证、适合下游工程实现的需求说明。"
        ),
    )


def create_architect_agent() -> Agent:
    """创建架构师 Agent。"""

    return _create_agent(
        role="架构师",
        goal=(
            "根据产品需求设计简单、可实现、可测试的前端技术方案，"
            "明确文件拆分、核心模块和数据流。"
        ),
        backstory=(
            "你是一名务实的软件架构师。"
            "你偏向使用最小可行技术栈，避免过度设计，并保证方案方便开发和测试。"
        ),
    )


def create_developer_agent() -> Agent:
    """创建开发工程师 Agent。"""

    return _create_agent(
        role="开发工程师",
        goal=(
            "根据需求文档和架构方案生成可运行的 HTML、CSS、JavaScript 项目文件，"
            "并能根据缺陷报告进行小范围修复。"
        ),
        backstory=(
            "你是一名偏前端的开发工程师。"
            "你重视代码可读性、可运行性和文件结构清晰度，修复缺陷时优先做最小必要改动。"
        ),
    )


def create_tester_agent() -> Agent:
    """创建测试工程师 Agent。"""

    return _create_agent(
        role="测试工程师",
        goal=(
            "根据预定义测试用例检查生成的 Web 应用，"
            "输出清晰的测试结果和可回传给开发工程师的缺陷报告。"
        ),
        backstory=(
            "你是一名关注用户路径和验收标准的测试工程师。"
            "你会优先验证核心功能是否可用，并把失败现象描述成开发工程师能直接处理的问题。"
        ),
    )


def create_all_agents() -> dict[str, Agent]:
    """一次性创建本项目需要的 4 个 Agent。"""

    return {
        "product_manager": create_product_manager_agent(),
        "architect": create_architect_agent(),
        "developer": create_developer_agent(),
        "tester": create_tester_agent(),
    }
