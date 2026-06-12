"""工作流编排包。"""

from workflow.sequential_crew import CrewBuildResult, build_sequential_crew, describe_crew_plan
from workflow.mock_demo import run_mock_snake_demo
from workflow.run_demo import SNAKE_GAME_REQUEST, run_snake_demo
from workflow.static_test import run_snake_static_tests
from workflow.test_runner import run_snake_test_runner
from workflow.repair import (
    RepairLoopResult,
    RepairRoundRecord,
    RepairTaskBuildResult,
    build_repair_task_from_artifacts,
    run_auto_repair_loop_from_artifacts,
)

__all__ = [
    "CrewBuildResult",
    "SNAKE_GAME_REQUEST",
    "build_sequential_crew",
    "describe_crew_plan",
    "run_mock_snake_demo",
    "run_snake_demo",
    "run_snake_static_tests",
    "run_snake_test_runner",
    "RepairTaskBuildResult",
    "RepairRoundRecord",
    "RepairLoopResult",
    "build_repair_task_from_artifacts",
    "run_auto_repair_loop_from_artifacts",
]
