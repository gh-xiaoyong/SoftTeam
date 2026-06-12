"""验证阶段 5B 测试 Runner。"""

from __future__ import annotations

import shutil
import unittest

from tools.file_io import resolve_project_path, write_text_file
from tools.test_runner import read_generated_project_files, run_predefined_test_cases


class TestRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        """准备独立临时目录，避免测试污染真实 generated 产物。"""

        self.tmp_root = resolve_project_path("tmp/test-runner")
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

    def tearDown(self) -> None:
        if self.tmp_root.exists():
            shutil.rmtree(self.tmp_root)

    def test_read_generated_project_files(self) -> None:
        """Runner 应能读取生成项目中的 HTML/CSS/JS 文件。"""

        project_root = "tmp/test-runner/read"
        write_text_file(f"{project_root}/index.html", "<html></html>\n")
        write_text_file(f"{project_root}/style.css", "body { margin: 0; }\n")
        write_text_file(f"{project_root}/script.js", "console.log('ok');\n")

        files = read_generated_project_files(project_root)

        self.assertEqual(files.html, "<html></html>\n")
        self.assertIn("margin", files.css)
        self.assertIn("console.log", files.javascript)
        self.assertEqual(files.html_path.name, "index.html")
        self.assertEqual(files.css_path.name, "style.css")
        self.assertEqual(files.js_path.name, "script.js")

    def test_run_predefined_test_cases_returns_test_report(self) -> None:
        """Runner 应执行预定义用例并返回统一 TestReport。"""

        project_root = "tmp/test-runner/report"
        write_text_file(
            f"{project_root}/index.html",
            """<!doctype html>
<html lang="zh-CN">
<head><link rel="stylesheet" href="style.css"></head>
<body>
  <canvas id="game"></canvas>
  <div id="score">0</div>
  <button id="restart">重新开始</button>
  <script src="script.js"></script>
</body>
</html>
""",
        )
        write_text_file(f"{project_root}/style.css", "#game { width: 400px; }\n")
        write_text_file(
            f"{project_root}/script.js",
            """let score = 0;
let gameOver = false;
document.addEventListener("keydown", (event) => {
  if (event.key === "ArrowUp" || event.key === "ArrowDown") {
    event.preventDefault();
  }
});
function checkCollision(head) {
  return head.x < 0 || head.y < 0 || head.x >= tileCount || snake.some((part) => part.x === head.x);
}
function addScore() {
  score += 10;
  document.getElementById("score").textContent = String(score);
}
""",
        )

        report = run_predefined_test_cases(project_root)

        self.assertTrue(report.passed)
        self.assertEqual(report.total, 10)
        self.assertIn("阶段 5B Test Runner", report.summary)


if __name__ == "__main__":
    unittest.main()
