# Mini Soft Team

这是一个基于 CrewAI 的迷你软件开发团队 Demo。

项目模拟 4 类 Agent 协作完成一个简单 Web 应用开发流程：

- 产品经理：把用户需求整理成结构化需求文档。
- 架构师：根据需求输出技术方案。
- 开发工程师：生成 HTML/CSS/JavaScript 项目文件，并根据缺陷报告修复源码。
- 测试工程师：输出测试判断；最终测试结论由本地 Test Runner 做确定性检查。

验证场景是自动生成一个贪吃蛇 HTML 游戏。

## 当前能力

项目目前已经完成端到端 Demo：

```text
用户需求
→ 产品需求文档
→ 架构方案
→ HTML/CSS/JavaScript 源码
→ 本地 Test Runner 测试
→ 结构化缺陷报告
→ 开发 Agent 修复任务
→ 最多 2 轮自动修复
→ 最终自动修复报告
```

主要产物：

- `outputs/requirements.md`
- `outputs/architecture.md`
- `outputs/file_manifest.json`
- `outputs/code_manifest.full.json`
- `generated/snake-game/index.html`
- `generated/snake-game/style.css`
- `generated/snake-game/script.js`
- `reports/test_report.md`
- `reports/test_report.json`
- `reports/final_repair_report.md`
- `reports/final_repair_report.json`

完整开发记录见：

- `docs/development-log.md`
- `docs/experience.md`

## 环境准备

建议始终使用项目虚拟环境运行命令：

```powershell
D:\projects\softTeam\.venv\Scripts\python.exe
```

如果你在项目根目录，也可以写成：

```powershell
.venv\Scripts\python.exe
```

安装依赖：

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

本项目已验证当前虚拟环境中安装了 CrewAI。

## 环境变量配置

项目支持 DeepSeek 的 OpenAI-compatible API。

复制 `.env.example` 为 `.env`，并填入真实密钥：

```text
DEEPSEEK_API_KEY=你的DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

`.env` 已加入 `.gitignore`，不要把真实密钥提交到仓库。

如果需要使用 OpenAI-compatible 通用变量，也可以配置：

```text
OPENAI_API_KEY=你的 API Key
OPENAI_API_BASE=https://api.deepseek.com
OPENAI_MODEL_NAME=deepseek-v4-flash
```

当前项目对 DeepSeek 做了兼容处理：

- DeepSeek 下不使用 CrewAI 原生 `output_pydantic` response_format。
- Prompt 要求模型输出 JSON。
- 本地代码提取 JSON 并用 Pydantic 校验。
- 对 LLM 常见的简写 JSON 做本地规范化。

## Mock 模式和真实模式

### Mock 模式

Mock 模式不调用大模型，使用本地固定数据生成完整贪吃蛇 Demo。

适合：

- 没有 API Key 时验证工程链路。
- 学习项目产物结构。
- 测试本地 Test Runner 和自动修复报告。

运行：

```powershell
.venv\Scripts\python.exe main.py --mock-demo
```

### 真实模式

真实模式会调用 CrewAI 和配置好的模型，让 4 个 Agent 顺序执行。

适合：

- 验证 DeepSeek/CrewAI Agent 链路。
- 观察真实模型输出和本地结构化解析。
- 生成由模型产出的需求、架构和源码。

运行前需要配置 `.env`。

运行：

```powershell
.venv\Scripts\python.exe main.py --run-demo
```

真实模式生成源码后，最终测试报告仍然由本地 Test Runner 生成，而不是只依赖测试 Agent 的自然语言判断。

## 常用命令

查看顺序 Crew 编排，不调用模型：

```powershell
.venv\Scripts\python.exe main.py
```

生成 Mock 贪吃蛇 Demo：

```powershell
.venv\Scripts\python.exe main.py --mock-demo
```

真实执行 CrewAI Demo：

```powershell
.venv\Scripts\python.exe main.py --run-demo
```

执行阶段 5A 静态测试，写入 `reports/static_test_report.*`：

```powershell
.venv\Scripts\python.exe main.py --static-test
```

执行正式 Test Runner，写入 `reports/test_report.*`：

```powershell
.venv\Scripts\python.exe main.py --test-runner
```

只构建开发修复任务，不调用模型：

```powershell
.venv\Scripts\python.exe main.py --build-repair-task
```

执行最多 2 轮自动修复循环，并生成最终报告：

```powershell
.venv\Scripts\python.exe main.py --auto-repair
```

## 推荐完整运行流程

如果只是验证本地端到端流程：

```powershell
.venv\Scripts\python.exe main.py --mock-demo
.venv\Scripts\python.exe main.py --auto-repair
```

如果要走真实 Agent 流程：

```powershell
.venv\Scripts\python.exe main.py --run-demo
.venv\Scripts\python.exe main.py --auto-repair
```

本地预览页面：

```powershell
cd generated\snake-game
..\..\.venv\Scripts\python.exe -m http.server 8765 --bind 127.0.0.1
```

浏览器打开：

```text
http://127.0.0.1:8765/index.html
```

## 自动修复机制

自动修复流程由 `--auto-repair` 触发。

执行逻辑：

```text
运行 Test Runner
如果通过：结束，修复轮数为 0
如果失败：生成结构化 defects
构造 RepairRequest
开发 Agent 输出修复后的 CodeManifest
保存修复后的源码
再次运行 Test Runner
最多修复 2 轮
生成 final_repair_report
```

`RepairRequest` 包含：

- 原始需求
- 架构方案
- 当前源码
- 测试报告
- 缺陷列表

最终报告路径：

```text
reports/final_repair_report.md
reports/final_repair_report.json
```

最终报告会记录：

- 初始测试结果
- 第 1 轮修复结果
- 第 2 轮修复结果
- 最终是否通过
- 未修复缺陷
- 最终源码路径

## 测试

编译检查：

```powershell
.venv\Scripts\python.exe -m compileall schemas tools tasks workflow tests main.py
```

完整相关测试：

```powershell
.venv\Scripts\python.exe -m unittest tests.test_static_test_runner tests.test_test_runner tests.test_workflow_test_runner_integration tests.test_repair_task tests.test_auto_repair_loop tests.test_final_repair_report tests.test_run_demo_parsing -v
```

注意：部分集成测试会写入 `reports/test_report.*`。测试完成后如果要恢复演示状态，运行：

```powershell
.venv\Scripts\python.exe main.py --mock-demo
.venv\Scripts\python.exe main.py --auto-repair
```

## 目录结构

```text
agents/      CrewAI Agent 工厂
tasks/       CrewAI Task 工厂
schemas/     Agent 之间的结构化交接模型
tools/       文件读写、测试 Runner、报告保存、修复上下文工具
workflow/    顺序 Crew、Demo、测试、修复循环编排
tests/       单元测试和集成测试
outputs/     需求、架构、代码清单等中间产物
generated/   生成的前端项目源码
reports/     测试报告和最终自动修复报告
docs/        开发记录和经验文档
```

## 已知注意事项

- Windows 下建议始终显式使用 `.venv\Scripts\python.exe`。
- 不要并行运行会读写同一份报告的命令，例如测试和 `--auto-repair`。
- 浏览器验证本地页面时，优先使用 `python -m http.server`，不要直接依赖 `file://`。
- DeepSeek 的 OpenAI-compatible API 不等于支持所有 OpenAI 高级结构化输出能力，本项目已使用本地 JSON 解析和 Pydantic 校验做兼容。
