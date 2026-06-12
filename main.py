"""Mini Soft Team Demo 的程序入口。

默认只打印顺序 Crew 编排。
传入 `--run-demo` 时，会真实执行贪吃蛇 Agent 链路并保存产物。
"""

from __future__ import annotations

import argparse
import sys

from workflow import (
    build_sequential_crew,
    build_repair_task_from_artifacts,
    describe_crew_plan,
    run_auto_repair_loop_from_artifacts,
    run_mock_snake_demo,
    run_snake_demo,
    run_snake_static_tests,
    run_snake_test_runner,
)


DEFAULT_USER_REQUEST = "实现一个贪吃蛇 HTML 游戏，支持方向键控制、计分、碰撞结束和重新开始。"


def configure_console_encoding() -> None:
    """在 Windows 控制台下尽量使用 UTF-8 输出。"""

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description="Mini Soft Team Demo")
    parser.add_argument(
        "--run-demo",
        action="store_true",
        help="真实执行贪吃蛇 Demo，并保存中间产物和源码文件。",
    )
    parser.add_argument(
        "--mock-demo",
        action="store_true",
        help="不调用大模型，生成一组本地 Mock 贪吃蛇产物，用于验证保存链路。",
    )
    parser.add_argument(
        "--static-test",
        action="store_true",
        help="执行阶段 5A 本地静态测试，并保存 reports/static_test_report.*。",
    )
    parser.add_argument(
        "--test-runner",
        action="store_true",
        help="执行阶段 5B 测试 Runner，并保存 reports/test_report.*。",
    )
    parser.add_argument(
        "--build-repair-task",
        action="store_true",
        help="构建阶段 5D 开发修复任务，但不调用大模型执行。",
    )
    parser.add_argument(
        "--auto-repair",
        action="store_true",
        help="执行阶段 5E 自动修复循环，最多修复 2 轮。",
    )
    return parser.parse_args()


def main() -> None:
    configure_console_encoding()

    args = parse_args()

    if args.run_demo:
        try:
            written_files = run_snake_demo()
        except RuntimeError as error:
            print(f"执行失败：{error}")
            raise SystemExit(1) from error

        print("贪吃蛇 Demo 执行完成，已写入以下文件：")
        for file_path in written_files:
            print(f"- {file_path}")
        return

    if args.mock_demo:
        written_files = run_mock_snake_demo()
        print("Mock 贪吃蛇 Demo 已生成，写入以下文件：")
        for file_path in written_files:
            print(f"- {file_path}")
        return

    if args.static_test:
        written_files = run_snake_static_tests()
        print("阶段 5A 静态测试已完成，写入以下报告文件：")
        for file_path in written_files:
            print(f"- {file_path}")
        return

    if args.test_runner:
        written_files = run_snake_test_runner()
        print("阶段 5B Test Runner 已完成，写入以下报告文件：")
        for file_path in written_files:
            print(f"- {file_path}")
        return

    if args.build_repair_task:
        result = build_repair_task_from_artifacts()
        print("阶段 5D 开发修复任务已构建：")
        print(f"- 执行角色：{result.developer.role}")
        print(f"- 任务名称：{result.repair_task.name}")
        print(f"- 当前源码文件数：{len(result.repair_request.current_code.files)}")
        print(f"- 缺陷数量：{len(result.repair_request.defects)}")
        return

    if args.auto_repair:
        try:
            result = run_auto_repair_loop_from_artifacts(max_rounds=2)
        except RuntimeError as error:
            print(f"执行失败：{error}")
            raise SystemExit(1) from error

        print("阶段 5E 自动修复循环已完成：")
        print(f"- 最终是否通过：{result.passed}")
        print(f"- 已执行修复轮数：{result.rounds_used}")
        print(f"- 最终失败数量：{result.final_report.failed_count}")
        print(f"- 最终报告：reports/test_report.md")
        print(f"- 自动修复总报告：reports/final_repair_report.md")
        return

    result = build_sequential_crew(DEFAULT_USER_REQUEST)
    print(describe_crew_plan(result))


if __name__ == "__main__":
    main()
