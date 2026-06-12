"""CrewAI 任务工厂包。"""

from tasks.factory import (
    create_all_tasks,
    create_architecture_task,
    create_development_task,
    create_requirement_task,
    create_repair_task,
    create_test_task,
)

__all__ = [
    "create_all_tasks",
    "create_architecture_task",
    "create_development_task",
    "create_requirement_task",
    "create_repair_task",
    "create_test_task",
]
