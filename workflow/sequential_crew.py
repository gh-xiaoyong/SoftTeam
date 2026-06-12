"""顺序 Crew 编排。

阶段 4C 只负责把 4 个 Agent 和 4 个 Task 组装成顺序执行的 Crew。
默认不调用 `kickoff()`，因此不会触发大模型请求。
"""

from __future__ import annotations

from dataclasses import dataclass

from crewai import Agent, Crew, Process, Task

from agents import create_all_agents
from tasks import create_all_tasks


@dataclass(frozen=True)
class CrewBuildResult:
    """构建顺序 Crew 后返回的对象集合。"""

    crew: Crew
    agents: dict[str, Agent]
    tasks: dict[str, Task]


def build_sequential_crew(user_request: str, verbose: bool = True) -> CrewBuildResult:
    """根据用户需求构建一个顺序执行的 Crew。

    这里不执行 Crew，只返回已经组装好的对象。
    执行动作会放到后续阶段处理。
    """

    agents = create_all_agents()
    tasks = create_all_tasks(agents=agents, user_request=user_request)

    crew = Crew(
        name="Mini Soft Team",
        agents=list(agents.values()),
        tasks=list(tasks.values()),
        process=Process.sequential,
        verbose=verbose,
    )

    return CrewBuildResult(
        crew=crew,
        agents=agents,
        tasks=tasks,
    )


def describe_crew_plan(result: CrewBuildResult) -> str:
    """生成当前 Crew 编排的文本说明，方便命令行查看。"""

    lines = [
        "Mini Soft Team 顺序 Crew 编排",
        "=" * 32,
        f"Crew 名称：{result.crew.name}",
        f"执行模式：{result.crew.process.value}",
        "",
        "Agent 列表：",
    ]

    for key, agent in result.agents.items():
        lines.append(f"- {key}: {agent.role}")

    lines.extend(["", "Task 顺序："])

    for index, task in enumerate(result.tasks.values(), start=1):
        context_count = len(task.context or [])
        lines.append(
            f"{index}. {task.name} | 执行角色：{task.agent.role} | 上游任务数：{context_count}"
        )

    return "\n".join(lines)

