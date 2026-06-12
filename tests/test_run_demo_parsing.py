"""验证 DeepSeek JSON 输出的本地兼容解析。"""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from schemas import RequirementDocument, TestReport
from workflow.run_demo import _get_task_model


class RunDemoParsingTest(unittest.TestCase):
    def test_requirement_output_accepts_simplified_lists(self) -> None:
        """模型把对象列表简化成字符串列表时，也能被规范化为需求文档。"""

        task_output = SimpleNamespace(
            pydantic=None,
            raw="""{
              "app_name": "贪吃蛇游戏",
              "summary": "实现一个浏览器贪吃蛇游戏",
              "target_users": "所有浏览器用户，适合休闲娱乐",
              "features": [
                "使用方向键控制蛇移动（上、下、左、右）",
                "蛇吃到食物后分数增加并变长"
              ],
              "user_interactions": [
                "按下方向键改变蛇的移动方向",
                "点击重新开始按钮重置游戏"
              ],
              "acceptance_criteria": [
                "页面能正常打开",
                "撞墙后游戏结束"
              ]
            }""",
        )

        document = _get_task_model(task_output, RequirementDocument)

        self.assertEqual(document.target_users, ["所有浏览器用户，适合休闲娱乐"])
        self.assertEqual(document.features[0].name, "使用方向键控制蛇移动（上、下、左、右）")
        self.assertEqual(document.features[0].priority, "medium")
        self.assertEqual(document.user_interactions[0].action, "按下方向键改变蛇的移动方向")
        self.assertEqual(document.acceptance_criteria[0].criterion, "页面能正常打开")

    def test_test_report_numeric_passed_is_normalized(self) -> None:
        """测试报告把 passed 输出成数字时，应按统计字段推断为布尔值。"""

        task_output = SimpleNamespace(
            pydantic=None,
            raw="""{
              "passed": 9,
              "total": 9,
              "passed_count": 9,
              "failed_count": 0,
              "cases": [
                {
                  "name": "页面入口存在",
                  "passed": 1,
                  "expected": "index.html 存在",
                  "actual": "index.html 存在",
                  "detail": "通过"
                }
              ],
              "defects": [],
              "summary": "全部通过"
            }""",
        )

        report = _get_task_model(task_output, TestReport)

        self.assertIs(report.passed, True)
        self.assertIs(report.cases[0].passed, True)


if __name__ == "__main__":
    unittest.main()
