# 开发经验记录

本文档专门记录项目开发和调试过程中遇到的问题。

它和 `docs/development-log.md` 的区别是：

- `development-log.md` 记录每个阶段做了什么。
- `experience.md` 记录开发过程中踩到的问题、排查过程和经验总结。

## 1. 当前 shell 的 Python 不是项目虚拟环境

### 现象

运行：

```bash
python -c "import crewai; print(crewai.__version__)"
```

报错：

```text
ModuleNotFoundError: No module named 'crewai'
```

但你说明项目虚拟环境 `softTeam` 已经装好了 CrewAI。

### 排查

运行：

```bash
where.exe python
```

发现当前 shell 默认使用的是 Codex 自己的 Python 环境，而不是项目目录下的 `.venv`。

随后检查项目目录，发现存在：

```text
D:\projects\softTeam\.venv
```

使用这个解释器验证：

```bash
D:\projects\softTeam\.venv\Scripts\python.exe -c "import crewai; print(crewai.__version__)"
```

可以正常识别 CrewAI。

### 解决方式

后续所有验证命令都显式使用项目虚拟环境：

```bash
D:\projects\softTeam\.venv\Scripts\python.exe
```

### 经验

Windows 下多个 Python 环境很常见，不要只看 `python` 命令能不能运行。

开发项目前应先确认：

```bash
where.exe python
python -c "import sys; print(sys.executable)"
```

如果项目有 `.venv`，验证命令最好显式使用 `.venv\Scripts\python.exe`。

## 2. 默认 Python 环境没有 pip

### 现象

尝试安装依赖：

```bash
python -m pip install -r requirements.txt
```

报错：

```text
No module named pip
```

### 原因

当前 shell 默认的 Python 是 Codex 运行环境，不是项目虚拟环境。这个环境里没有启用 pip。

### 解决方式

停止在默认 Python 环境安装依赖，改用项目 `.venv`。

### 经验

遇到依赖问题时，先确认“正在给哪个 Python 安装包”。

不要急着反复安装，先确认解释器路径。

## 3. CrewAI 导入较慢，短超时可能误判失败

### 现象

使用 10 秒超时检查 CrewAI 版本时，命令先输出：

```text
1.14.6
```

但随后被判定为 timeout。

### 原因

CrewAI 首次导入可能加载较多模块，耗时超过了短超时时间。

### 解决方式

后续检查 CrewAI 接口时，把超时时间提高到 30 秒：

```bash
D:\projects\softTeam\.venv\Scripts\python.exe -c "from crewai import Agent; import inspect; print(inspect.signature(Agent))"
```

### 经验

对重型框架做导入检查时，10 秒不一定够。

如果已经看到有效输出，但命令被 timeout，需要区分：

- 代码是否真的失败
- 还是工具超时时间太短

## 4. CrewAI Task 的 context 默认值不是空列表

### 现象

阶段 4B 验证任务上下文数量时运行：

```python
len(task.context or [])
```

报错：

```text
TypeError: object of type '_NotSpecified' has no len()
```

### 原因

CrewAI 的 `Task.context` 默认值不是 `None`，也不是空列表，而是内部的 `NOT_SPECIFIED` 标记。

第一个任务没有上游任务，如果不显式传 `context=[]`，读取时容易遇到这个内部标记。

### 解决方式

在需求分析任务中显式设置：

```python
context=[]
```

### 经验

不要假设第三方库的默认值就是 `None` 或空列表。

如果后续代码需要统一处理上下文数量，最好让自己的工厂函数输出稳定结构。

## 5. 代码清单缺少 content 字段

### 现象

阶段 4B 定义代码生成任务时发现：`CodeManifest` 只能描述文件路径、用途和语言，但无法保存文件源码。

原模型类似：

```text
GeneratedFile
├─ path
├─ purpose
└─ language
```

这只能说明“有哪些文件”，不能让后续工具把源码写入磁盘。

### 解决方式

给 `GeneratedFile` 增加：

```python
content: str
```

更新后模型变成：

```text
GeneratedFile
├─ path
├─ purpose
├─ language
└─ content
```

### 经验

设计结构化交接格式时，要考虑下游是否真的能使用它完成工作。

“文件清单”和“可落盘源码”不是同一个东西。后续要写文件，就必须有源码内容。

## 6. 真实 CrewAI 执行需要模型密钥

### 现象

阶段 4D 检查环境变量时发现：

```text
OPENAI_API_KEY=False
```

如果直接运行真实 Crew：

```bash
.venv\Scripts\python.exe main.py --run-demo
```

就会因为没有模型配置而无法调用大模型。

### 解决方式

在 `workflow/run_demo.py` 中增加预检：

```python
ensure_llm_configured()
```

如果没有 `OPENAI_API_KEY`，直接给出清晰提示：

```text
未检测到 OPENAI_API_KEY。请先在环境变量或 .env 文件中配置模型密钥。
```

同时增加 `--mock-demo`，用于本地无密钥时验证产物保存链路。

### 经验

真实 Agent 执行和工程链路验证应该拆开。

可以用两种模式：

- 真实模式：验证 LLM + Agent 链路。
- Mock 模式：验证 Schema + 文件保存 + 页面产物。

这样即使暂时没有模型密钥，也能继续开发和验证工程部分。

## 7. 浏览器插件不允许直接访问 file://

### 现象

尝试用浏览器打开本地 HTML：

```text
file:///D:/projects/softTeam/generated/snake-game/index.html
```

浏览器插件拒绝访问，提示该 URL 被安全策略阻止。

### 原因

浏览器自动化环境限制直接访问 `file://` 本地文件，避免越权读取本地文件系统。

### 解决方式

改用本地静态 HTTP 服务：

```bash
cd generated\snake-game
..\..\.venv\Scripts\python.exe -m http.server 8765 --bind 127.0.0.1
```

然后访问：

```text
http://127.0.0.1:8765/index.html
```

验证完成后关闭本地服务。

### 经验

验证本地前端页面时，优先用本地 HTTP 服务，而不是直接打开 `file://`。

这也更接近真实 Web 页面运行方式。

## 8. 浏览器只读环境不支持直接读取 canvas getContext

### 现象

尝试在浏览器检查 canvas 是否非空：

```javascript
const canvas = document.querySelector("#game");
const ctx = canvas.getContext("2d");
```

报错：

```text
TypeError: canvas.getContext is not a function
```

### 原因

当前浏览器插件的只读页面执行环境不是完整的页面 JS 环境，DOM 对象能力有限。

### 解决方式

放弃用 `getContext()` 做像素检查，改为检查更稳定的信号：

- 页面标题
- `h1` 文本
- `canvas` 是否存在
- 分数元素是否存在
- 重新开始按钮是否存在
- 控制台是否有错误

### 经验

自动化验证不要依赖当前工具环境不稳定的 API。

先验证关键 DOM 和控制台错误，复杂交互测试可以放到后续 Playwright 测试 Runner 中实现。

## 9. 为什么阶段 4D 增加了 Mock Demo

### 背景

阶段 4D 的理想目标是：

```text
CrewAI Agent 链路
→ 结构化输出
→ 保存需求文档
→ 保存架构文档
→ 保存源码文件
→ 保存测试报告
```

但当前环境没有模型密钥，真实 Agent 无法执行。

### 处理方式

没有强行伪装真实执行，而是明确拆成：

```text
--run-demo   真实 CrewAI 执行，需要 OPENAI_API_KEY
--mock-demo  本地示例数据执行，不调用大模型
```

### 经验

遇到外部依赖不可用时，不要让整个项目停住。

应该把问题拆开：

- 外部依赖是否可用
- 本地工程链路是否可用

Mock 模式可以保证本地工程链路继续推进。

## 10. 接入 DeepSeek 时要兼容 CrewAI 的 LLM 配置方式

### 现象

用户希望接入 `deepseek-v4-flash`。

项目原来只检查：

```text
OPENAI_API_KEY
```

但这不够清晰，因为现在接入的是 DeepSeek。

### 处理方式

新增 `config/llm.py`，统一读取：

```text
DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL
DEEPSEEK_MODEL
```

同时保留兼容变量：

```text
OPENAI_API_KEY
OPENAI_API_BASE
OPENAI_MODEL_NAME
```

Agent 创建时统一注入：

```python
llm=create_configured_llm()
```

### 经验

不要把模型配置散落在 Agent、Workflow 和命令行入口里。

应该单独建一个配置模块，让后续切换模型时只改一处。

同时，`.env` 里不应该直接写入真实密钥到代码仓库。即使当前目录不是 Git 仓库，也应该提前加 `.gitignore` 忽略 `.env`。

## 11. DeepSeek 不适合直接使用 CrewAI 的 output_pydantic

### 现象

接入 DeepSeek 后运行真实 Demo，接口可以连通，但 CrewAI 调用失败：

```text
Error code: 400 - {'error': {'message': 'This response_format type is unavailable now'}}
```

### 原因

CrewAI 的 `Task(output_pydantic=...)` 会走 OpenAI 原生结构化输出路径，底层会传 `response_format`。

DeepSeek 的 OpenAI-compatible 接口当前不支持 CrewAI 触发的这种 `response_format` 类型。

### 解决方式

在 `config/llm.py` 中新增：

```python
supports_native_response_format()
```

当模型或 Base URL 包含 `deepseek` 时，任务不再设置 `output_pydantic`。

改为：

```text
Prompt 要求模型只输出 JSON
→ workflow/run_demo.py 从 raw 文本中提取 JSON
→ 使用 Pydantic model_validate() 做本地校验
```

### 经验

OpenAI-compatible 不等于所有 OpenAI 高级能力都兼容。

尤其是：

- 原生结构化输出
- beta parse API
- 特定 response_format 类型

这些能力在不同模型供应商里差异很大。更稳的做法是：

- 模型只负责输出 JSON 文本。
- 本地代码负责 JSON 提取和 Pydantic 校验。

## 12. Windows 控制台可能无法输出 CrewAI 日志中的表情符号

### 现象

真实运行 CrewAI 时，控制台出现类似错误：

```text
'gbk' codec can't encode character
```

### 原因

Windows PowerShell 默认编码可能是 GBK，而 CrewAI 的日志里可能包含表情符号或其他 Unicode 字符。

GBK 无法编码这些字符，就会在日志输出阶段报错。

### 解决方式

在 `main.py` 启动时增加：

```python
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
```

### 经验

如果项目需要输出中文、表情符号或第三方库的富文本日志，Windows 下最好主动把输出流设置成 UTF-8。

## 13. LLM 输出 JSON 字段名正确，但字段类型可能不符合 Schema

### 现象

真实运行 DeepSeek 后，需求分析任务输出的 JSON 字段名是对的，但字段类型不符合 Pydantic Schema。

例如 Schema 期望：

```json
{
  "target_users": ["用户"],
  "features": [
    {
      "name": "方向键控制",
      "description": "玩家可以用方向键控制蛇移动",
      "priority": "high"
    }
  ]
}
```

但模型实际可能输出：

```json
{
  "target_users": "所有浏览器用户，适合休闲娱乐",
  "features": [
    "使用方向键控制蛇移动",
    "蛇吃到食物后分数增加"
  ]
}
```

于是 Pydantic 报错：

```text
target_users Input should be a valid list
features.0 Input should be a valid dictionary
```

### 原因

Prompt 只说“符合 RequirementDocument”，但没有把对象数组的内部结构写得足够明确。

LLM 会倾向于输出人类看起来合理的简写 JSON，但这种简写不一定符合严格 Schema。

### 解决方式

做了两层修复：

1. 加强 Prompt
   - 明确写出 `features`、`user_interactions`、`acceptance_criteria` 等字段的对象结构。
   - 明确要求“对象数组里的元素必须是对象，不能用字符串代替”。

2. 增加本地规范化层
   - 在 `workflow/run_demo.py` 中增加 `_normalize_model_data()`。
   - 如果模型输出字符串，就自动转换成对应对象。
   - 再交给 Pydantic 做最终校验。

### 回归测试

新增：

```text
tests/test_run_demo_parsing.py
```

验证字符串简写能被转换成标准 `RequirementDocument`。

运行：

```bash
.venv\Scripts\python.exe -m unittest tests.test_run_demo_parsing -v
```

结果：

```text
OK
```

### 经验

只要求 LLM “输出 JSON”还不够。

如果下游有严格 Schema，必须同时做：

- Prompt 中明确 JSON 结构。
- 本地代码做容错规范化。
- Pydantic 做最终校验。

这样既能利用 LLM 的灵活性，也能保住工程系统的稳定性。

## 14. 测试报告的 passed 字段可能被模型输出成数字

### 现象

测试报告解析时报错：

```text
ValidationError: TestReport
passed
Input should be a valid boolean, unable to interpret input_value=9
```

### 原因

Schema 中 `passed` 表示整体是否通过，应该是布尔值：

```json
{
  "passed": true
}
```

但模型把它理解成了通过数量，输出成：

```json
{
  "passed": 9
}
```

### 解决方式

在 `workflow/run_demo.py` 的测试报告规范化逻辑中增加：

- `_to_int()`
- `_to_bool()`
- `_normalize_report_passed()`

处理规则：

- `true`、`通过`、`1` 转成 `True`
- `false`、`失败`、`0` 转成 `False`
- 如果顶层 `passed` 是类似 `9` 这样的非布尔数字，则不直接强转
- 改用 `failed_count == 0 and passed_count == total` 推断整体是否通过

### 回归测试

在 `tests/test_run_demo_parsing.py` 中新增：

```text
test_test_report_numeric_passed_is_normalized
```

验证 `passed: 9` 可以被规范化成 `True`。

### 经验

字段名本身可能有歧义。

`passed` 对人来说可能表示：

- 是否通过
- 通过数量

所以对 LLM 输出的 JSON，不能只看字段名对不对，还要对字段语义做防御式处理。

## 15. 有依赖关系的验证命令不能并行执行

### 现象

阶段 5A 验证静态测试报告时，我把两个命令并行执行了：

```bash
.venv\Scripts\python.exe main.py --static-test
Get-Content reports\static_test_report.md
```

结果 `--static-test` 输出显示报告已经写入：

```text
reports/static_test_report.md
reports/static_test_report.json
```

但读取命令同时失败：

```text
Cannot find path 'D:\projects\softTeam\reports\static_test_report.md' because it does not exist.
```

### 原因

这不是静态测试器失败，而是命令执行顺序有问题。

读取报告依赖前一个命令先完成写入，所以这两个命令不能并行。并行执行时，读取命令可能抢在文件创建之前运行，于是出现“刚写入却读不到”的假失败。

### 解决方式

改成顺序执行：

```bash
.venv\Scripts\python.exe main.py --static-test
Get-Content -Encoding UTF8 reports\static_test_report.md
```

顺序执行后确认报告存在，内容正常：

```text
用例总数：10
通过数量：10
失败数量：0
```

### 经验

并行工具适合互不依赖的读取、搜索、编译等操作。

如果后一个命令依赖前一个命令的输出文件，就必须顺序执行。否则会制造假错误，浪费排查时间。

## 16. 模块导出名要和实际实现保持一致

### 现象

阶段 5B 新增 `tools/test_runner.py` 后，检查 `tools/__init__.py` 时发现它已经导出了这些名字：

```python
GeneratedProjectFiles
read_generated_project_files
run_and_save_test_report
run_predefined_test_cases
```

但最初新增的 `tools/test_runner.py` 中实际函数名是：

```python
run_predefined_tests
run_and_save_predefined_tests
```

如果不处理，后续执行：

```python
from tools import run_predefined_test_cases
```

就会因为导出名和实现名不一致而失败。

### 原因

阶段开发过程中，文件之间的接口名没有一次性对齐。

这类问题很常见：单个文件本身能编译，但包级导出已经引用了另一个名字。真正导入包时才会暴露。

### 解决方式

在 `tools/test_runner.py` 中补齐更明确的阶段 5B 接口：

```python
read_generated_project_files()
run_predefined_test_cases()
run_and_save_test_report()
```

同时保留较短的内部函数：

```python
run_predefined_tests()
run_and_save_predefined_tests()
```

这样既能满足外部导出，又保持内部调用简洁。

### 经验

新增模块后不要只跑单个文件测试，还要验证包级导入。

推荐至少跑：

```bash
.venv\Scripts\python.exe -m compileall tools workflow tests main.py
.venv\Scripts\python.exe -m unittest ...
```

如果项目有 `__init__.py` 统一导出函数，尤其要检查导出名和实现名是否一致。

## 17. 会写主报告的集成测试需要恢复工作区状态

### 现象

阶段 5C 新增了一个集成测试：模拟真实 CrewAI 流程中“测试 Agent 自评通过，但开发产物缺少 `style.css`、`script.js` 和游戏区域”的情况。

这个测试会调用真实的保存流程，因此会写入：

```text
reports/test_report.md
reports/test_report.json
```

测试本身通过后，主测试报告会暂时停留在失败状态。

### 原因

这个集成测试不是纯内存测试。它有意验证完整流程：

```text
保存源码
→ 本地 Test Runner 读取源码
→ 写入主测试报告
```

所以它会影响项目里的真实报告文件。

### 解决方式

集成测试跑完后，重新运行：

```bash
.venv\Scripts\python.exe main.py --mock-demo
```

因为阶段 5C 已经把 Mock Demo 也接入了本地 Test Runner，所以这条命令会重新生成可运行贪吃蛇源码，并恢复通过状态的主报告。

恢复后确认：

```text
用例总数：10
通过数量：10
失败数量：0
```

### 经验

集成测试如果会写项目主产物，就要在验证结束后恢复演示状态。

更通用的做法有两种：

- 测试使用 `tmp/` 下的独立目录，避免碰真实产物。
- 如果必须验证真实主报告路径，测试后运行恢复命令，保证工作区留给下一阶段时是干净、可演示的状态。

## 18. CrewAI 构造 Agent 时出现弃用警告

### 现象

阶段 5D 测试开发修复任务时，测试通过，但控制台出现 CrewAI 的弃用警告：

```text
DeprecationWarning: function_calling_llm is deprecated and will be removed in a future release.
DeprecationWarning: deprecated
```

### 原因

这些警告来自 CrewAI 内部的 Agent 初始化逻辑，不是本项目代码直接调用了这些弃用参数。

当前项目创建 Agent 时只传入了：

```python
role
goal
backstory
allow_delegation
verbose
llm
```

警告说明 CrewAI 当前版本内部还保留了一些即将迁移的字段检查。

### 处理方式

本阶段没有为了消除警告而改 Agent 创建逻辑。

原因：

- 测试结果是通过的。
- 警告来自第三方库内部。
- 当前改动目标是实现修复任务，不应该顺手做无关框架适配。

### 经验

弃用警告和运行错误要区分处理。

如果是项目代码直接使用了弃用 API，就应该尽早迁移。

如果是第三方库内部警告，可以先记录，后续升级 CrewAI 时再集中处理。不要为了“清屏”而做没有把握的改动。

## 19. 自动修复命令不要和写报告的测试并行执行

### 现象

阶段 5E 验证时，我一开始把完整测试和自动修复命令并行执行：

```bash
.venv\Scripts\python.exe -m unittest ...
.venv\Scripts\python.exe main.py --auto-repair
```

这次没有失败，但这是一个潜在竞态。

### 原因

完整测试里包含集成测试和自动修复循环测试，它们会写入：

```text
reports/test_report.md
reports/test_report.json
```

而 `--auto-repair` 也会读取和写入同一份主测试报告。

如果并行执行，就可能出现：

- 自动修复读取到测试过程中的临时失败报告。
- 测试刚写完失败报告，自动修复又覆盖成通过报告。
- 最终状态取决于哪个进程最后写文件。

### 解决方式

改成顺序执行：

```bash
.venv\Scripts\python.exe -m unittest tests.test_auto_repair_loop -v
.venv\Scripts\python.exe main.py --mock-demo
.venv\Scripts\python.exe main.py --auto-repair
```

顺序执行后结果稳定：

```text
最终是否通过：True
已执行修复轮数：0
最终失败数量：0
```

### 经验

只读命令可以并行。

会读写同一份产物的命令不要并行，尤其是：

- `reports/test_report.json`
- `outputs/code_manifest.full.json`
- `generated/snake-game/*`

自动修复流程对“当前测试报告”和“当前源码”很敏感，验证时应该用顺序命令保证状态清楚。

## 20. 最终修复报告不要复用单次测试报告结构

### 现象

阶段 5F 需要记录：

```text
初始测试结果
第 1 轮修复结果
第 2 轮修复结果
最终是否通过
未修复缺陷
最终源码路径
```

一开始容易想到直接扩展 `TestReport`，但 `TestReport` 本质上只描述“一次测试运行”。

### 原因

自动修复最终报告描述的是一条流程时间线：

```text
初始测试
→ 修复第 1 轮
→ 修复第 2 轮
→ 最终状态
```

它和单次测试报告不是同一种数据。

如果强行复用 `TestReport`，字段语义会变模糊：

- `passed` 是初始测试通过，还是最终通过？
- `cases` 是哪一轮的用例？
- `defects` 是本轮缺陷，还是最终未修复缺陷？

### 解决方式

新增独立 Schema：

```python
RepairRoundSummary
FinalRepairReport
```

最终写入：

```text
reports/final_repair_report.md
reports/final_repair_report.json
```

普通测试报告仍然保留在：

```text
reports/test_report.md
reports/test_report.json
```

### 经验

当一个数据结构的生命周期和语义变了，就应该新增模型，而不是硬塞字段。

`TestReport` 表达“一次测试”，`FinalRepairReport` 表达“修复流程结果”。分开后，后续阅读和扩展都更稳。

## 21. README 要随着项目阶段同步升级成使用手册

### 现象

阶段 6 开始时，`README.md` 仍然主要停留在阶段 4D：

- 说明了 Mock Demo 和真实 Demo。
- 没有完整描述阶段 5 的 Test Runner。
- 没有描述自动修复循环。
- 没有描述最终自动修复报告。
- 命令分散在不同阶段，不像一个完整使用手册。

### 原因

项目是按教学阶段逐步开发的，README 在早期更像阶段说明。

但到阶段 6，项目已经形成完整 Demo，README 的职责应该变化：

```text
阶段说明
→ 项目使用手册
```

### 解决方式

重写 README，补充：

- 项目当前能力。
- 环境准备。
- `.env` 配置方式。
- Mock 模式和真实模式区别。
- 常用命令总览。
- 推荐完整运行流程。
- 自动修复机制说明。
- 产物路径。
- 测试命令。
- 已知注意事项。

### 经验

教学项目的文档最好分层：

- `README.md`：面向使用和展示，告诉别人怎么跑。
- `docs/development-log.md`：面向学习过程，记录每阶段怎么搭起来。
- `docs/experience.md`：面向排错复盘，记录踩坑和经验。

三类文档不要互相替代。README 太像流水账会难用，经验文档太像教程会难查。

## 22. 浏览器验收要区分初始 DOM 和交互后的真实状态

### 现象

阶段 7 浏览器验收真实 CrewAI 生成的贪吃蛇页面时，初始 DOM 快照里出现：

```text
heading "游戏结束"
button "重新开始"
```

这看起来像页面一打开就处于游戏结束状态。

### 排查

继续检查页面关键元素：

```json
{
  "title": "贪吃蛇游戏",
  "hasCanvas": true,
  "canvasWidth": "400",
  "canvasHeight": "400",
  "hasScore": true,
  "hasRestartButton": true,
  "errorLogs": []
}
```

然后点击“重新开始”按钮，并发送方向键。

交互后检查：

```json
{
  "hasGameOverText": false,
  "score": "0",
  "errorLogs": []
}
```

### 原因

真实模型生成的页面把“游戏结束”遮罩写在 DOM 中，初始快照能看到这段文本。

但交互后逻辑能正常隐藏遮罩并进入游戏状态。

### 经验

浏览器验收不要只看初始 DOM 文本。

要结合：

- 关键元素是否存在。
- 控制台是否有错误。
- 用户关键操作后状态是否变化。

对于游戏和交互页面，至少要验证一次主交互路径，例如点击重新开始、按方向键、检查错误日志。
## 23. 上传 GitHub 前先检查 `.gitignore`，不要把学习文档误忽略

### 现象

准备把项目上传到 GitHub 时，发现当前目录还不是 Git 仓库，并且 `.gitignore` 中写了：

```text
docs/
```

这会导致 `docs/development-log.md` 和 `docs/experience.md` 被 Git 忽略。

### 原因

早期配置 `.gitignore` 时只考虑了减少提交文件数量，没有区分“临时文件”和“项目交付物”。
但在这个教学项目里，`docs/` 不是临时目录，而是记录开发阶段、调试问题和学习经验的核心产物。

### 解决方式

把 `.gitignore` 调整为：

```text
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
tmp/
```

这样可以：

- 排除真实 API Key 所在的 `.env`。
- 排除本地虚拟环境 `.venv/`。
- 排除 Python 缓存和临时目录。
- 保留 `docs/`、`generated/`、`outputs/`、`reports/` 等项目结果。

### 经验

上传 GitHub 前一定要做三件事：

1. 用 `git status --ignored` 查看哪些文件会被提交、哪些文件会被忽略。
2. 用 `git check-ignore -v 文件路径` 确认敏感文件确实被忽略。
3. 用 `rg` 搜索 `sk-`、`API_KEY`、`token` 等关键词，避免真实密钥进入仓库。

这个检查不只是“安全操作”，也是项目专业度的一部分。
## 24. Git 写操作不要并行执行，容易触发 `index.lock`

### 现象

第一次准备提交代码时，同时执行了 `git add .` 和 `git status --ignored`，结果 `git add` 报错：

```text
fatal: Unable to create '.git/index.lock': File exists.
Another git process seems to be running in this repository
```

### 原因

Git 的部分命令会读写 `.git/index`。
当两个 Git 进程同时访问索引时，Git 会创建 `index.lock` 防止仓库状态被写坏。

这次不是仓库损坏，而是并行执行命令导致的锁竞争。

### 解决方式

先检查是否真的还有 Git 进程：

```bash
Get-Process git -ErrorAction SilentlyContinue
```

再检查锁文件是否还存在：

```bash
Test-Path .git\index.lock
```

确认没有残留进程且锁文件已经消失后，重新顺序执行 Git 命令。

### 经验

可以并行读取普通文件，但 Git 写操作要顺序执行。

例如这些命令不要并行：

- `git add`
- `git commit`
- `git merge`
- `git rebase`
- `git checkout`

Git 状态相关命令看起来很轻，但和写操作并发时也可能碰到索引锁。
