# 开发记录

本文档记录每一个小开发阶段，方便你按顺序理解这个项目是怎么搭起来的。

## 阶段 1 - 项目骨架

### 目标

在实现 CrewAI Agent 之前，先创建最小可运行的项目结构。

这个阶段暂时不需要生成代码，只需要有一个清晰的程序入口，以及和后续职责对应的目录结构。

### 新增文件

- `main.py`
  - 新增 Python 程序入口。
  - 打印未来计划实现的工作流步骤。
  - 目前使用占位文本，还没有接入真实 CrewAI 逻辑。

- `requirements.txt`
  - 记录后续计划使用的运行依赖：
    - `crewai`
    - `pydantic`
    - `python-dotenv`

- `agents/__init__.py`
  - 标记 `agents` 是一个 Python 包。
  - 后续会在这里放 4 类 Agent 的定义。

- `tasks/__init__.py`
  - 标记 `tasks` 是一个 Python 包。
  - 后续会在这里放 CrewAI 任务定义。

- `schemas/__init__.py`
  - 标记 `schemas` 是一个 Python 包。
  - 后续会在这里放结构化交接格式。

- `tools/__init__.py`
  - 标记 `tools` 是一个 Python 包。
  - 后续会在这里放文件写入和测试执行工具。

- `README.md`
  - 说明项目目标和当前状态。

- `docs/development-log.md`
  - 记录每个开发阶段的学习笔记。

### 为什么先做这个

在写 Agent Prompt 或 CrewAI 任务之前，我们需要先确定项目结构。
四个主要目录会直接对应后续系统设计：

- `agents`：谁来做事
- `tasks`：每个 Agent 做什么事
- `schemas`：Agent 之间传递什么结构化数据
- `tools`：工作流能调用哪些本地能力

这样后续每次新增功能时，都能清楚知道代码应该放在哪里。

### 如何验证

运行：

```bash
python main.py
```

预期输出：

```text
Mini Soft Team 工作流骨架
================================
1. 产品经理分析用户需求
2. 架构师生成技术方案
3. 开发工程师生成项目文件
4. 测试工程师验证生成的应用
5. 测试失败时，开发工程师根据缺陷报告进行修复
```

### 下一阶段

定义结构化交接数据模型：

- 产品需求文档
- 架构方案
- 代码文件清单
- 测试报告

## 约定 - 中文优先

从本阶段开始，项目文档和代码注释尽可能使用中文。

原因是这个项目本身用于学习和讲解，多 Agent 协作流程的关键不只是代码能跑，还要让每一步的设计意图清楚可读。

## 阶段 2 - 结构化交接数据模型

### 目标

定义 4 类 Agent 之间传递的数据格式。

这一阶段仍然不接入 CrewAI，也不生成 HTML 游戏。我们先解决一个更基础的问题：每个 Agent 到底应该把什么内容交给下一个 Agent。

### 为什么要先定义 Schema

如果 Agent 之间只传递自然语言文本，流程会很难稳定：

- 产品经理可能漏掉验收标准。
- 架构师可能没有明确文件职责。
- 开发工程师可能生成了文件，但没有告诉测试工程师入口在哪里。
- 测试工程师可能只写“测试失败”，但没有给开发工程师足够的修复信息。

所以我们先定义结构化数据模型，让每一步的交接更像工程项目里的“合同”。

### 新增文件

- `schemas/requirement.py`
  - 定义产品经理输出的 `RequirementDocument`。
  - 包含应用名称、目标用户、功能点、用户交互和验收标准。

- `schemas/architecture.py`
  - 定义架构师输出的 `ArchitecturePlan`。
  - 包含技术栈、文件设计、模块设计、数据流和实现注意事项。

- `schemas/code_manifest.py`
  - 定义开发工程师输出的 `CodeManifest`。
  - 说明生成了哪些文件、入口文件在哪里、如何运行。

- `schemas/test_report.py`
  - 定义测试工程师输出的 `TestReport`。
  - 包含测试用例结果、失败缺陷和测试总结。

- `schemas/__init__.py`
  - 统一导出所有 Schema，方便后续代码直接从 `schemas` 包导入。

### 关键设计

本阶段使用 Pydantic 的 `BaseModel` 定义数据结构。

原因：

- 字段清晰，可读性好。
- 后续可以校验 Agent 输出。
- 后续可以方便地转成 JSON。
- 可以给每个字段写说明，方便 Prompt 约束输出格式。

例如产品经理输出不是一段散文，而是这个结构：

```text
RequirementDocument
├─ app_name
├─ summary
├─ target_users
├─ features
├─ user_interactions
└─ acceptance_criteria
```

测试工程师输出也不是简单说“失败了”，而是：

```text
TestReport
├─ passed
├─ total
├─ passed_count
├─ failed_count
├─ cases
├─ defects
└─ summary
```

其中 `defects` 会在后续自动修复阶段回传给开发工程师。

### 如何验证

运行：

```bash
python -m compileall main.py schemas
```

这个命令会检查 Python 文件能否正常编译。

如果输出里没有报错，说明本阶段新增的 Schema 文件语法正确。

本阶段还额外验证了当前环境中的 Pydantic 版本：

```bash
python -c "import pydantic; print(pydantic.__version__)"
```

当前验证结果是：

```text
2.13.1
```

然后创建了一个最小的 `RequirementDocument` 示例，确认模型可以正常导入、实例化并转成 JSON。

### 下一阶段

实现文件读写工具。

下一阶段会让系统具备这些基础能力：

- 创建输出目录
- 写入 Markdown 文档
- 写入 JSON 文件
- 写入 HTML/CSS/JavaScript 文件
- 读取已有源码，供后续修复流程使用

## 阶段 3 - 文件读写工具

### 目标

实现后续 Agent 写入中间产物和源码文件时需要用到的基础文件能力。

这一阶段仍然不接入 CrewAI。我们只做一件事：把“读写文件”这件基础能力封装好。

### 为什么要单独做文件工具

后续流程里会产生很多文件：

- `requirements.md`
- `architecture.md`
- `file_manifest.json`
- `test_report.md`
- `generated/snake-game/index.html`
- `generated/snake-game/style.css`
- `generated/snake-game/script.js`

如果每个 Agent 或任务都自己写 `open()`、自己拼路径，代码会变乱，也容易把文件写错位置。

所以本阶段把这些能力集中到 `tools/file_io.py`：

- 路径解析
- 自动创建父目录
- 写入文本文件
- 读取文本文件
- 写入 JSON 文件
- 读取 JSON 文件
- 写入 Pydantic 模型
- 列出项目文件

### 新增文件

- `tools/file_io.py`
  - 新增项目文件读写工具。
  - 所有路径都基于项目根目录解析。
  - 写文件时自动创建父目录。
  - 文本统一使用 UTF-8 编码。
  - JSON 使用 `ensure_ascii=False`，保证中文正常保存。

### 修改文件

- `tools/__init__.py`
  - 统一导出 `file_io.py` 中的工具函数。
  - 后续代码可以直接从 `tools` 包导入。

- `README.md`
  - 更新当前阶段状态。
  - 增加阶段 3 的验证命令。

### 关键设计

`resolve_project_path()` 只接受项目内的相对路径，不接受绝对路径。

原因是后续 Agent 生成文件时，我们希望所有产物都在当前项目目录内，例如：

```text
generated/snake-game/index.html
reports/test_report.md
```

如果允许绝对路径，Agent 可能会把文件写到项目外面，后续测试和交付都会变得不可控。

### 工具函数说明

- `write_text_file(path, content)`
  - 写入文本文件。
  - 适合写 Markdown、HTML、CSS、JavaScript。

- `read_text_file(path)`
  - 读取文本文件。
  - 后续自动修复时，开发 Agent 需要读取已有源码。

- `write_json_file(path, data)`
  - 写入 JSON 文件。
  - 适合保存 `file_manifest.json`。

- `read_json_file(path)`
  - 读取 JSON 文件。

- `write_model_json_file(path, model)`
  - 把 Pydantic 模型写成 JSON。
  - 适合保存阶段 2 定义的结构化产物。

- `list_project_files(directory)`
  - 列出某个项目目录下的文件。
  - 后续测试 Agent 可以用它检查生成文件是否完整。

### 如何验证

运行：

```bash
python -m compileall tools
```

还可以用一个临时目录做真实读写验证：

```bash
python -c "from tools import write_text_file, read_text_file; write_text_file('tmp/stage3.txt', '阶段3验证'); print(read_text_file('tmp/stage3.txt'))"
```

预期输出：

```text
阶段3验证
```

本阶段实际运行结果符合预期。验证过程中临时写入了 `tmp/stage3-check.txt`，读取成功后已删除该临时文件。

### 下一阶段

开始进入阶段 4，但阶段 4 会继续拆小。

## 阶段 4 拆分计划

阶段 4 原目标是“接入 CrewAI Agent 和顺序任务链”。这个目标太大，里面同时包含 Agent 定义、Task 定义、流程编排、文件产物保存和一次 Demo 运行。

为了降低理解难度，阶段 4 拆成 4 个小阶段。

### 阶段 4A - 创建 4 个 Agent 的工厂函数

目标：只定义 4 个 Agent，不创建任务，也不运行 Crew。

要做的事：

- 创建产品经理 Agent。
- 创建架构师 Agent。
- 创建开发工程师 Agent。
- 创建测试工程师 Agent。
- 给每个 Agent 写清楚：
  - role
  - goal
  - backstory
  - 是否允许委派
  - 是否 verbose

验证方式：

- 能从 `agents` 包导入 4 个创建函数。
- 能成功构造 4 个 Agent 对象。

### 阶段 4B - 创建 4 个 Task 的工厂函数

目标：只定义任务，不跑完整流程。

要做的事：

- 创建需求分析任务。
- 创建架构设计任务。
- 创建代码生成任务。
- 创建测试验证任务。
- 每个 Task 明确：
  - description
  - expected_output
  - agent
  - context

验证方式：

- 能成功构造 4 个 Task 对象。
- Task 的上下游依赖关系清楚。

### 阶段 4C - 实现顺序任务链编排

目标：把 Agent 和 Task 串成一个顺序 Crew。

要做的事：

- 在 `main.py` 或单独的 workflow 文件里创建 Crew。
- 设置执行模式为顺序执行。
- 输入一个简单需求。
- 暂时不做自动修复。

验证方式：

- 程序可以启动 Crew。
- 至少能看到每个 Agent 按顺序执行。

### 阶段 4D - 跑通贪吃蛇需求并保存中间产物

目标：用“贪吃蛇游戏”跑一次完整 Agent 链路。

要做的事：

- 输入贪吃蛇需求。
- 保存产品经理输出到 `requirements.md`。
- 保存架构师输出到 `architecture.md`。
- 保存开发工程师生成的源码文件。
- 保存测试工程师的初步测试报告。

验证方式：

- `generated/snake-game/` 下出现 HTML/CSS/JavaScript 文件。
- `reports/` 下出现测试报告。
- 页面可以被浏览器打开。

### 为什么这样拆

CrewAI 项目最容易失控的地方，是一开始就把 Agent、Task、文件写入、测试、自动修复全部混在一起。

拆成 4A 到 4D 后，每一步只验证一个核心问题：

- 4A：Agent 能不能被创建。
- 4B：Task 能不能被创建。
- 4C：Agent 和 Task 能不能按顺序跑。
- 4D：流程产物能不能落盘，并形成可运行 Demo。

这样如果出错，我们能快速知道问题出在 Agent 定义、任务依赖、Crew 编排，还是文件产物保存。

## 阶段 4A - 创建 4 个 Agent 的工厂函数

### 目标

创建产品经理、架构师、开发工程师、测试工程师 4 类 CrewAI Agent。

这一阶段只验证 Agent 能否被创建，不定义 Task，不执行 Crew，也不调用大模型。

### 新增文件

- `agents/factory.py`
  - 新增 4 个 Agent 创建函数：
    - `create_product_manager_agent()`
    - `create_architect_agent()`
    - `create_developer_agent()`
    - `create_tester_agent()`
  - 新增 `create_all_agents()`，用于一次性创建 4 个 Agent。

### 修改文件

- `agents/__init__.py`
  - 统一导出 Agent 工厂函数。

- `README.md`
  - 更新当前阶段状态。
  - 增加阶段 4A 的验证命令。

### Agent 职责设计

本阶段每个 Agent 都定义了 3 个核心字段：

- `role`
  - Agent 的角色名称。

- `goal`
  - Agent 当前要完成的核心目标。

- `backstory`
  - Agent 的行为背景，用来约束它的工作风格。

此外，4 个 Agent 都设置：

```python
allow_delegation=False
verbose=True
```

原因：

- `allow_delegation=False`
  - 当前项目是固定的顺序任务链，不希望 Agent 自己再把任务委派给其他 Agent。

- `verbose=True`
  - 后续运行 Crew 时可以看到更详细的执行过程，方便学习和调试。

### 为什么不在这一阶段创建 Task

Agent 只回答“谁来做事”。

Task 回答“具体做什么事、输入是什么、输出是什么”。

如果把 Agent 和 Task 一起写，初学时容易混淆两个概念。所以阶段 4A 只完成 Agent，阶段 4B 再做 Task。

### 如何验证

因为当前 shell 默认的 `python` 不是项目虚拟环境，所以验证时显式使用：

```bash
.venv\Scripts\python.exe
```

验证命令：

```bash
.venv\Scripts\python.exe -m compileall agents
```

以及：

```bash
.venv\Scripts\python.exe -c "from agents import create_all_agents; agents = create_all_agents(); print(list(agents.keys()))"
```

预期输出包含：

```text
['product_manager', 'architect', 'developer', 'tester']
```

本阶段实际验证输出：

```text
['product_manager', 'architect', 'developer', 'tester']
['产品经理', '架构师', '开发工程师', '测试工程师']
```

说明 4 个 CrewAI Agent 对象已经可以正常创建。

### 下一阶段

阶段 4B：创建 4 个 Task 的工厂函数。

下一阶段会定义：

- 需求分析任务
- 架构设计任务
- 代码生成任务
- 测试验证任务

但仍然不做自动修复。

## 阶段 4B - 创建 4 个 Task 的工厂函数

### 目标

创建需求分析、架构设计、代码生成、测试验证 4 个 CrewAI Task。

这一阶段只验证 Task 能否被创建，不执行 Crew，也不调用大模型。

### 新增文件

- `tasks/factory.py`
  - 新增 4 个任务创建函数：
    - `create_requirement_task()`
    - `create_architecture_task()`
    - `create_development_task()`
    - `create_test_task()`
  - 新增 `create_all_tasks()`，用于一次性创建完整顺序任务链。

### 修改文件

- `tasks/__init__.py`
  - 统一导出 Task 工厂函数。

- `schemas/code_manifest.py`
  - 给 `GeneratedFile` 增加 `content` 字段。
  - 原因是代码生成任务后续不只要告诉我们“有哪些文件”，还要提供每个文件的完整源码内容，文件写入工具才能真正落盘。

- `README.md`
  - 更新当前阶段状态。
  - 增加阶段 4B 的验证命令。

### Task 上下游关系

本阶段的任务链是：

```text
需求分析任务
  ↓
架构设计任务
  ↓
代码生成任务
  ↓
测试验证任务
```

在 CrewAI 里，这个上下游关系通过 `context` 参数表达：

- 架构设计任务依赖需求分析任务。
- 代码生成任务依赖需求分析任务和架构设计任务。
- 测试验证任务依赖代码生成任务。

### 为什么使用 output_pydantic

每个任务都绑定了阶段 2 定义的结构化模型：

- 需求分析任务 → `RequirementDocument`
- 架构设计任务 → `ArchitecturePlan`
- 代码生成任务 → `CodeManifest`
- 测试验证任务 → `TestReport`

这样后续 Crew 执行时，我们可以尽量要求 Agent 输出能被解析成稳定结构，而不是一大段不可控文本。

### 如何验证

验证命令：

```bash
.venv\Scripts\python.exe -m compileall tasks schemas
```

以及：

```bash
.venv\Scripts\python.exe -c "from agents import create_all_agents; from tasks import create_all_tasks; agents = create_all_agents(); tasks = create_all_tasks(agents, '做一个贪吃蛇游戏'); print(list(tasks.keys())); print([task.name for task in tasks.values()])"
```

预期输出包含：

```text
['requirement', 'architecture', 'development', 'test']
['需求分析任务', '架构设计任务', '代码生成任务', '测试验证任务']
```

本阶段实际验证输出：

```text
['requirement', 'architecture', 'development', 'test']
['需求分析任务', '架构设计任务', '代码生成任务', '测试验证任务']
[0, 1, 2, 1]
```

最后一行表示每个任务的上游上下文数量：

- 需求分析任务：0 个上游任务
- 架构设计任务：1 个上游任务
- 代码生成任务：2 个上游任务
- 测试验证任务：1 个上游任务

### 下一阶段

阶段 4C：实现顺序任务链编排。

下一阶段会创建 Crew，把 4 个 Agent 和 4 个 Task 按顺序串起来，但仍然先不做自动修复。

## 阶段 4C - 实现顺序任务链编排

### 目标

把阶段 4A 的 4 个 Agent 和阶段 4B 的 4 个 Task 组装成一个顺序执行的 Crew。

这一阶段默认不执行 `crew.kickoff()`，因此不会触发大模型请求。我们只验证编排关系是否正确。

### 新增文件

- `workflow/__init__.py`
  - 导出顺序 Crew 编排相关函数。

- `workflow/sequential_crew.py`
  - 新增 `build_sequential_crew()`。
  - 新增 `describe_crew_plan()`。
  - 新增 `CrewBuildResult`，统一返回 Crew、Agent 字典和 Task 字典。

### 修改文件

- `main.py`
  - 从原来的占位流程打印，升级成真实构建顺序 Crew。
  - 当前只打印 Crew 编排计划，不执行任务。

- `README.md`
  - 更新当前阶段状态。
  - 增加阶段 4C 的验证命令。

### 当前编排结构

```text
Crew: Mini Soft Team
Process: sequential

1. 需求分析任务     -> 产品经理
2. 架构设计任务     -> 架构师
3. 代码生成任务     -> 开发工程师
4. 测试验证任务     -> 测试工程师
```

### 为什么新增 workflow 包

`agents` 只负责创建 Agent。

`tasks` 只负责创建 Task。

`workflow` 负责把 Agent 和 Task 组装成可执行流程。

这样职责边界更清楚：

- Agent 定义变了，改 `agents`。
- Task 描述变了，改 `tasks`。
- 执行顺序或流程策略变了，改 `workflow`。

### 为什么暂时不 kickoff

`crew.kickoff()` 会真正调用大模型，需要模型配置、API Key、网络和输出解析都准备好。

阶段 4C 的目标不是验证大模型质量，而是验证工程编排是否正确。所以这一阶段先做到：

- Crew 能创建。
- Process 是 `sequential`。
- Agent 顺序正确。
- Task 顺序正确。
- Task 上下游数量正确。

### 如何验证

运行：

```bash
.venv\Scripts\python.exe -m compileall agents tasks workflow main.py
```

验证顺序 Crew：

```bash
.venv\Scripts\python.exe -c "from workflow import build_sequential_crew; result = build_sequential_crew('做一个贪吃蛇游戏'); print(result.crew.process.value); print([task.name for task in result.crew.tasks])"
```

也可以直接运行：

```bash
.venv\Scripts\python.exe main.py
```

预期能看到 Crew 名称、执行模式、Agent 列表和 Task 顺序。

本阶段实际对象级验证输出：

```text
sequential
['产品经理', '架构师', '开发工程师', '测试工程师']
['需求分析任务', '架构设计任务', '代码生成任务', '测试验证任务']
[0, 1, 2, 1]
```

本阶段实际运行 `main.py` 输出：

```text
Mini Soft Team 顺序 Crew 编排
================================
Crew 名称：Mini Soft Team
执行模式：sequential

Agent 列表：
- product_manager: 产品经理
- architect: 架构师
- developer: 开发工程师
- tester: 测试工程师

Task 顺序：
1. 需求分析任务 | 执行角色：产品经理 | 上游任务数：0
2. 架构设计任务 | 执行角色：架构师 | 上游任务数：1
3. 代码生成任务 | 执行角色：开发工程师 | 上游任务数：2
4. 测试验证任务 | 执行角色：测试工程师 | 上游任务数：1
```

### 下一阶段

阶段 4D：用贪吃蛇需求跑通一次 Agent 链路并保存中间产物。

下一阶段会开始处理真实执行和产物落盘，但仍然不做自动修复闭环。

## 阶段 4D - 贪吃蛇需求执行入口与产物保存

### 目标

用贪吃蛇需求跑通一次开发链路，并把中间产物和源码文件保存到磁盘。

本阶段做了两条路径：

- 真实模式：`--run-demo`
  - 使用 CrewAI 执行真实 Agent 链路。
  - 需要配置模型密钥。

- Mock 模式：`--mock-demo`
  - 不调用大模型。
  - 使用固定的结构化示例数据验证产物保存链路。
  - 用于本地无密钥时学习和检查文件输出。

### 新增文件

- `tools/artifact_writer.py`
  - 负责把结构化模型保存成 Markdown、JSON 和源码文件。
  - 保存内容包括：
    - 需求文档
    - 架构方案
    - 代码文件清单
    - HTML/CSS/JavaScript 源码
    - 测试报告

- `workflow/run_demo.py`
  - 新增真实贪吃蛇 Demo 执行入口。
  - 调用 `build_sequential_crew()` 构建 Crew。
  - 调用 `crew.kickoff()` 执行真实 Agent 链路。
  - 从每个任务的 `TaskOutput.pydantic` 中提取结构化结果。
  - 调用产物保存器写入文件。

- `workflow/mock_demo.py`
  - 新增本地 Mock 贪吃蛇 Demo。
  - 构造固定的 `RequirementDocument`、`ArchitecturePlan`、`CodeManifest`、`TestReport`。
  - 用同一套产物保存器写入文件。

### 修改文件

- `main.py`
  - 新增 `--run-demo` 参数。
  - 新增 `--mock-demo` 参数。
  - 默认仍然只打印 Crew 编排计划，不执行大模型。

- `workflow/__init__.py`
  - 导出 `run_snake_demo()` 和 `run_mock_snake_demo()`。

- `tools/__init__.py`
  - 导出产物保存函数。

- `tasks/factory.py`
  - 强化代码生成任务的输出路径约束。
  - 要求固定生成：
    - `generated/snake-game/index.html`
    - `generated/snake-game/style.css`
    - `generated/snake-game/script.js`

- `README.md`
  - 更新阶段 4D 状态。
  - 增加真实模式和 Mock 模式的运行说明。

### 为什么要加 Mock 模式

当前环境没有检测到 `OPENAI_API_KEY`，真实执行 `crew.kickoff()` 会失败。

但阶段 4D 除了验证大模型执行，还要验证很重要的一件事：结构化产物能否正确保存成文件。

所以本阶段增加 Mock 模式，把问题拆开：

- `--run-demo` 验证真实 CrewAI Agent 执行。
- `--mock-demo` 验证产物保存链路和最终文件结构。

这不是替代真实 Agent，而是一个本地教学和调试入口。

### 真实模式运行

先在环境变量或 `.env` 文件中配置：

```text
OPENAI_API_KEY=你的密钥
```

然后运行：

```bash
.venv\Scripts\python.exe main.py --run-demo
```

如果没有配置密钥，程序会给出明确提示：

```text
执行失败：未检测到 OPENAI_API_KEY。请先在环境变量或 .env 文件中配置模型密钥，然后再运行 `.venv\Scripts\python.exe main.py --run-demo`。
```

### Mock 模式运行

运行：

```bash
.venv\Scripts\python.exe main.py --mock-demo
```

本阶段实际输出：

```text
Mock 贪吃蛇 Demo 已生成，写入以下文件：
- D:\projects\softTeam\outputs\requirements.md
- D:\projects\softTeam\outputs\requirements.json
- D:\projects\softTeam\outputs\architecture.md
- D:\projects\softTeam\outputs\architecture.json
- D:\projects\softTeam\generated\snake-game\index.html
- D:\projects\softTeam\generated\snake-game\style.css
- D:\projects\softTeam\generated\snake-game\script.js
- D:\projects\softTeam\outputs\file_manifest.json
- D:\projects\softTeam\outputs\code_manifest.full.json
- D:\projects\softTeam\reports\test_report.md
- D:\projects\softTeam\reports\test_report.json
```

### 浏览器验证

浏览器插件不允许直接访问 `file://` 本地文件，所以本阶段使用本地静态服务验证页面。

启动服务：

```bash
cd generated\snake-game
..\..\.venv\Scripts\python.exe -m http.server 8765 --bind 127.0.0.1
```

访问：

```text
http://127.0.0.1:8765/index.html
```

浏览器检查结果：

```json
{
  "pageInfo": {
    "h1": "贪吃蛇",
    "hasCanvas": true,
    "hasRestart": true,
    "score": "0",
    "status": "使用方向键开始移动",
    "title": "贪吃蛇游戏"
  },
  "errorLogs": []
}
```

说明页面能正常打开，关键元素存在，并且没有控制台错误。

验证结束后，本地静态服务已关闭。

### 当前产物列表

```text
outputs/requirements.md
outputs/requirements.json
outputs/architecture.md
outputs/architecture.json
outputs/file_manifest.json
outputs/code_manifest.full.json
generated/snake-game/index.html
generated/snake-game/style.css
generated/snake-game/script.js
reports/test_report.md
reports/test_report.json
```

### 下一阶段

阶段 5：实现测试与自动修复闭环。

下一阶段会重点做：

- 用预定义测试用例检查生成页面。
- 把失败项整理成缺陷报告。
- 把缺陷报告回传给开发 Agent。
- 最多自动修复 2 轮。

## 模型配置 - DeepSeek V4 Flash

### 目标

把项目的真实 CrewAI 执行模型切换到 DeepSeek 的 OpenAI-compatible API。

### 新增文件

- `.env`
  - 保存本地模型配置。
  - 当前包含 DeepSeek API Key 占位符，需要替换成真实密钥。

- `.env.example`
  - 提供配置模板。

- `.gitignore`
  - 忽略 `.env`，避免密钥进入版本管理。

- `config/__init__.py`
  - 导出配置读取函数。

- `config/llm.py`
  - 从 `.env` 或环境变量读取模型配置。
  - 创建 CrewAI `LLM` 对象。
  - 未配置真实密钥时不主动创建 DeepSeek LLM，保证默认查看编排计划不失败。

### 修改文件

- `agents/factory.py`
  - 创建 Agent 时统一注入 `create_configured_llm()`。

- `workflow/run_demo.py`
  - 把原来的 `OPENAI_API_KEY` 检查改成通用模型配置检查。
  - 支持 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`。
  - `.env` 中的 OpenAI 兼容变量默认保持注释，避免占位符污染运行环境。

- `README.md`
  - 增加 DeepSeek 模型配置说明。

### 当前配置

```text
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

根据 DeepSeek 官方 API 文档，DeepSeek 支持 OpenAI-compatible API，OpenAI 格式的 Base URL 是 `https://api.deepseek.com`，模型名包含 `deepseek-v4-flash`。

参考：DeepSeek API Docs - Your First API Call

```text
https://api-docs.deepseek.com/
```

### 如何使用

把 `.env` 中的占位符：

```text
请替换为你的DeepSeek_API_Key
```

替换为你的真实 DeepSeek API Key。

然后运行：

```bash
.venv\Scripts\python.exe main.py --run-demo
```

### DeepSeek 结构化输出兼容处理

真实运行时发现 DeepSeek 返回：

```text
This response_format type is unavailable now
```

原因是 CrewAI 的 `Task(output_pydantic=...)` 会触发 OpenAI 原生结构化输出路径。

为兼容 DeepSeek，本项目做了调整：

- `config/llm.py`
  - 新增 `supports_native_response_format()`。
  - 当模型或 Base URL 包含 `deepseek` 时，返回 `False`。

- `tasks/factory.py`
  - DeepSeek 下不再设置 `output_pydantic`。
  - 改为在 `expected_output` 中要求模型只输出 JSON。

- `workflow/run_demo.py`
  - 如果任务输出没有 `pydantic`，就从 `raw` 文本中提取 JSON。
  - 再用 Pydantic 的 `model_validate()` 做本地校验。

这样既保留了结构化数据模型，又避免依赖 DeepSeek 暂不支持的原生 `response_format` 类型。

本地验证结果：

```text
base_url: https://api.deepseek.com
model: deepseek-v4-flash
supports_native_response_format: False
Task output_pydantic: [None, None, None, None]
```

### LLM 简写 JSON 的兼容修复

真实运行时又发现一个问题：模型输出字段名正确，但字段类型不一定符合 Schema。

例如 `features` 本来应该是对象数组：

```json
[
  {"name": "功能名", "description": "功能说明", "priority": "high"}
]
```

但模型可能输出字符串数组：

```json
[
  "使用方向键控制蛇移动",
  "蛇吃到食物后分数增加"
]
```

为解决这个问题，做了两处改动：

- `tasks/factory.py`
  - 给每个任务补充更明确的 JSON 字段结构说明。
  - 明确对象数组不能用字符串代替。

- `workflow/run_demo.py`
  - 增加 `_normalize_model_data()`。
  - 对需求、架构、代码清单、测试报告做本地规范化。
  - 再用 Pydantic 做最终校验。

新增回归测试：

```text
tests/test_run_demo_parsing.py
```

验证命令：

```bash
.venv\Scripts\python.exe -m unittest tests.test_run_demo_parsing -v
```

验证结果：

```text
OK
```

### 测试报告 passed 字段兼容修复

真实运行时发现测试报告中 `passed` 字段可能被模型输出成数字，例如：

```json
{
  "passed": 9,
  "total": 9,
  "passed_count": 9,
  "failed_count": 0
}
```

但 `TestReport.passed` 期望的是布尔值。

修复内容：

- `workflow/run_demo.py`
  - 新增 `_to_int()`。
  - 新增 `_to_bool()`。
  - 新增 `_normalize_report_passed()`。
  - 对整体 `passed` 字段根据 `failed_count`、`passed_count`、`total` 进行推断。

- `tests/test_run_demo_parsing.py`
  - 新增 `test_test_report_numeric_passed_is_normalized()`。

验证结果：

```text
Ran 2 tests
OK
```

## 阶段 5A - 预定义静态测试用例

### 目标

实现第一版本地测试能力。

这一阶段先不启动浏览器，也不执行 JavaScript，只做静态检查。目的不是证明游戏 100% 可玩，而是先建立一个稳定、可重复的测试入口，检查生成项目是否具备贪吃蛇游戏的基本结构。

### 本阶段完成的 10 个静态用例

- 检查 `index.html` 是否存在。
- 检查 `style.css` 是否存在。
- 检查 `script.js` 是否存在。
- 检查 HTML 是否正确引用 CSS 和 JS。
- 检查是否有游戏区域。
- 检查是否有分数显示。
- 检查是否有重新开始按钮。
- 检查 JS 是否包含方向键监听。
- 检查 JS 是否包含碰撞检测。
- 检查 JS 是否包含计分逻辑。

### 新增文件

- `tools/static_test_runner.py`
  - 新增 `run_static_snake_tests()`。
  - 读取 `generated/snake-game/index.html`、`style.css`、`script.js`。
  - 使用 Python 标准库 `HTMLParser` 解析 HTML。
  - 每条检查生成一个 `TestCaseResult`。
  - 失败检查会同步生成 `DefectReport`，为后续自动修复阶段做准备。

- `workflow/static_test.py`
  - 新增 `run_snake_static_tests()`。
  - 负责调用静态测试器，并把报告保存到 `reports` 目录。

- `tests/test_static_test_runner.py`
  - 新增通过场景测试。
  - 新增失败场景测试。
  - 失败场景会确认缺陷列表数量和失败用例数量一致。

### 修改文件

- `tools/artifact_writer.py`
  - 抽出 `_build_test_report_markdown()`，避免测试报告 Markdown 生成逻辑重复。
  - 新增 `save_static_test_report()`，保存：
    - `reports/static_test_report.md`
    - `reports/static_test_report.json`

- `tools/__init__.py`
  - 导出 `run_static_snake_tests()` 和 `save_static_test_report()`。

- `workflow/__init__.py`
  - 导出 `run_snake_static_tests()`。

- `main.py`
  - 新增命令行参数：

```bash
.venv\Scripts\python.exe main.py --static-test
```

运行后会执行阶段 5A 静态测试，并生成静态测试报告。

### 为什么先做静态测试

自动化测试可以分层推进。

阶段 5A 先做静态测试，是因为它成本低、结果稳定、容易理解：

- 不依赖浏览器。
- 不依赖大模型。
- 不依赖网络。
- 不需要真实运行游戏循环。
- 可以快速发现文件缺失、引用错误、核心逻辑缺失。

后续阶段再继续升级到浏览器行为测试，例如模拟按键、检查分数变化、触发游戏结束等。

### 当前静态测试报告

本阶段运行：

```bash
.venv\Scripts\python.exe main.py --static-test
```

生成：

```text
reports/static_test_report.md
reports/static_test_report.json
```

当前 `generated/snake-game` 的实际测试结果：

```text
用例总数：10
通过数量：10
失败数量：0
整体结果：通过
```

### 本阶段验证命令

语法编译检查：

```bash
.venv\Scripts\python.exe -m compileall tools workflow tests main.py
```

静态测试器单元测试：

```bash
.venv\Scripts\python.exe -m unittest tests.test_static_test_runner -v
```

DeepSeek 输出解析回归测试：

```bash
.venv\Scripts\python.exe -m unittest tests.test_run_demo_parsing -v
```

本阶段实际验证结果：

```text
test_static_tests_pass_for_complete_snake_project ... ok
test_static_tests_return_defects_for_incomplete_project ... ok

Ran 2 tests
OK
```

旧解析测试也通过：

```text
Ran 2 tests
OK
```

### 下一阶段

阶段 5B 可以继续做“测试失败时的缺陷反馈格式”。

因为阶段 5A 已经能把失败检查转换成 `DefectReport`，下一步就可以把这些缺陷整理成开发 Agent 能读懂的修复输入。

## 阶段 5B - 正式 Test Runner

### 目标

实现项目的正式测试 Runner。

阶段 5A 已经有了静态测试规则，但它更像“规则集合”。阶段 5B 要把这些规则包装成一个固定入口：

```text
读取生成项目源码
→ 执行预定义测试用例
→ 输出 TestReport
→ 写入 reports/test_report.md 和 reports/test_report.json
```

后续自动修复流程会依赖这个主测试报告，而不是临时报告。

### 新增文件

- `tools/test_runner.py`
  - 新增 `GeneratedProjectFiles`，表示生成项目的源码快照。
  - 新增 `read_generated_project_files()`，读取：
    - `index.html`
    - `style.css`
    - `script.js`
  - 新增 `run_predefined_test_cases()`，执行预定义测试用例并返回 `TestReport`。
  - 新增 `run_and_save_test_report()`，执行测试并写入主测试报告：
    - `reports/test_report.md`
    - `reports/test_report.json`

- `workflow/test_runner.py`
  - 新增 `run_snake_test_runner()`，作为工作流层入口。

- `tests/test_test_runner.py`
  - 验证 Runner 能读取 HTML/CSS/JS。
  - 验证 Runner 能执行预定义用例并返回 `TestReport`。

### 修改文件

- `tools/__init__.py`
  - 导出阶段 5B 的 Runner 函数和 `GeneratedProjectFiles`。

- `workflow/__init__.py`
  - 导出 `run_snake_test_runner()`。

- `main.py`
  - 新增命令行参数：

```bash
.venv\Scripts\python.exe main.py --test-runner
```

运行后会执行阶段 5B Runner，并写入主测试报告。

### 为什么 5B 复用 5A 的规则

阶段 5A 的价值是把 10 条静态测试规则实现稳定。

阶段 5B 的价值不是重复写一遍检查逻辑，而是建立正式测试入口。它复用 5A 的规则，然后把结果保存为后续流程统一使用的主报告：

```text
reports/test_report.md
reports/test_report.json
```

这样后续阶段可以继续在 Runner 内部增加浏览器交互测试，而不用改变外部调用方式。

### 当前 Test Runner 输出

运行：

```bash
.venv\Scripts\python.exe main.py --test-runner
```

实际输出：

```text
阶段 5B Test Runner 已完成，写入以下报告文件：
- D:\projects\softTeam\reports\test_report.md
- D:\projects\softTeam\reports\test_report.json
```

当前 `generated/snake-game` 的测试结果：

```text
用例总数：10
通过数量：10
失败数量：0
整体结果：通过
```

报告总结：

```text
阶段 5B Test Runner 执行通过。测试目录：generated/snake-game；通过 10 项，失败 0 项。
```

### 本阶段验证命令

编译检查：

```bash
.venv\Scripts\python.exe -m compileall tools workflow tests main.py
```

单元测试：

```bash
.venv\Scripts\python.exe -m unittest tests.test_static_test_runner tests.test_test_runner tests.test_run_demo_parsing -v
```

实际结果：

```text
Ran 6 tests
OK
```

### 下一阶段

阶段 5C 可以开始做“失败报告回传给开发 Agent”。

现在 `reports/test_report.json` 中已经包含：

- `passed`
- `cases`
- `defects`
- `summary`

如果测试失败，`defects` 就可以作为开发 Agent 的修复输入。

## 阶段 5C - 把 Test Runner 接入 Demo 流程

### 目标

让完整 Demo 的最终测试报告来自本地 Test Runner，而不是只依赖测试 Agent 的自然语言判断。

阶段 4D 时，流程是：

```text
CrewAI 测试 Agent 输出 TestReport
→ 直接保存 reports/test_report.md/json
```

这有一个风险：测试 Agent 可能说“通过”，但源码文件实际上缺失、引用错误或核心逻辑不完整。

阶段 5C 改成：

```text
CrewAI 生成需求、架构、源码
→ 先把源码写入 generated/snake-game
→ 本地 Test Runner 读取 HTML/CSS/JS
→ 执行预定义测试用例
→ 生成最终 reports/test_report.md/json
```

这样最终测试结论由本地确定性规则产生。

### 修改文件

- `workflow/run_demo.py`
  - 真实 `--run-demo` 流程不再把测试 Agent 的 `TestReport` 作为最终报告。
  - 流程现在会：
    - 保存需求文档。
    - 保存架构方案。
    - 保存开发 Agent 生成的源码。
    - 调用 `run_predefined_test_cases(code_manifest.project_root)`。
    - 保存本地 Runner 生成的 `reports/test_report.md/json`。

- `workflow/mock_demo.py`
  - Mock Demo 也接入同一套 Test Runner。
  - 删除旧的 `build_mock_test_report()`，避免主流程继续依赖手写的假测试报告。

- `tests/test_workflow_test_runner_integration.py`
  - 新增集成测试：
    - 验证 Mock Demo 的最终报告来自本地 Runner。
    - 模拟真实 CrewAI 流程中“测试 Agent 自称通过，但开发产物缺文件”的情况。
    - 最终报告应由本地 Runner 判定失败，并生成结构化 `defects`。

### 关键设计

测试 Agent 仍然可以存在于 CrewAI 顺序链路中，用于模拟团队角色分工。

但最终可交付报告以本地 Test Runner 为准。

原因是：

- Agent 判断适合做分析和补充说明。
- 本地 Runner 适合做稳定、可重复的工程检查。
- 自动修复流程需要结构化、可复现的失败信号。

### 失败时的结构化缺陷报告

如果本地 Runner 检查失败，`reports/test_report.json` 会包含：

```json
{
  "passed": false,
  "failed_count": 失败数量,
  "defects": [
    {
      "case_name": "失败用例名",
      "severity": "严重程度",
      "description": "实际失败原因",
      "suggestion": "建议修复方向"
    }
  ]
}
```

这正好是后续阶段自动修复要传给开发 Agent 的输入。

### 本阶段验证命令

编译检查：

```bash
.venv\Scripts\python.exe -m compileall workflow tools tests main.py
```

单元测试和集成测试：

```bash
.venv\Scripts\python.exe -m unittest tests.test_static_test_runner tests.test_test_runner tests.test_workflow_test_runner_integration tests.test_run_demo_parsing -v
```

实际结果：

```text
Ran 8 tests
OK
```

恢复并验证 Demo 产物：

```bash
.venv\Scripts\python.exe main.py --mock-demo
```

当前主报告：

```text
reports/test_report.md
reports/test_report.json
```

当前结果：

```text
用例总数：10
通过数量：10
失败数量：0
整体结果：通过
```

### 下一阶段

阶段 5D 可以开始做“把缺陷报告回传给开发 Agent”。

现在缺陷已经能稳定生成，下一步要做的是：

- 读取 `reports/test_report.json`。
- 如果 `passed=false`，提取 `defects`。
- 构造修复任务输入。
- 让开发 Agent 根据缺陷报告修改源码。

## 阶段 5D - 实现开发修复任务

### 目标

实现“测试失败后交给开发 Agent 的单次修复任务”。

这一阶段只做修复任务本身，不做最多 2 轮自动修复循环。原因是循环还需要处理：

- 执行修复任务。
- 保存修复后的源码。
- 再次运行 Test Runner。
- 判断是否继续下一轮。
- 控制最多修复 2 次。

这些会放到后续阶段。阶段 5D 先把修复任务的输入和输出定义清楚。

### 修复任务输入

新增结构化输入：

```text
RepairRequest
├─ requirement     原始需求文档
├─ architecture    架构方案
├─ current_code    当前源码文件清单
├─ test_report     本地 Test Runner 测试报告
└─ defects         缺陷列表
```

这个结构对应用户要求的输入：

- 原始需求
- 架构方案
- 当前源码
- 测试报告
- 缺陷列表

### 修复任务输出

开发 Agent 输出：

```text
CodeManifest
```

也就是修复后的源码文件清单。继续使用 `CodeManifest` 的原因是：

- 代码生成阶段已经使用这个结构。
- 保存源码工具已经支持这个结构。
- 后续修复循环可以直接保存修复后的 HTML/CSS/JS。
- 不需要再为“修复输出”设计另一套文件格式。

### 新增文件

- `schemas/repair_request.py`
  - 新增 `RepairRequest`。
  - 明确定义开发修复任务需要的完整上下文。

- `tools/repair_context.py`
  - 新增 `build_repair_request()`。
  - 新增 `load_current_code_manifest()`。
    - 从磁盘读取当前 `index.html`、`style.css`、`script.js`。
    - 组装成 `CodeManifest`。
  - 新增 `load_repair_request_from_artifacts()`。
    - 从 `outputs/requirements.json` 读取需求。
    - 从 `outputs/architecture.json` 读取架构。
    - 从当前源码目录读取源码。
    - 从 `reports/test_report.json` 读取测试报告。
    - 最终组装成 `RepairRequest`。

- `workflow/repair.py`
  - 新增 `RepairTaskBuildResult`。
  - 新增 `build_repair_task_from_artifacts()`。
  - 这个函数只构建修复任务，不执行大模型。

- `tests/test_repair_task.py`
  - 验证当前源码能被读取成 `CodeManifest`。
  - 验证开发修复任务包含结构化修复输入。
  - 验证工作流入口能从已落盘产物构建修复任务。

### 修改文件

- `schemas/__init__.py`
  - 导出 `RepairRequest`。

- `tasks/factory.py`
  - 新增 `create_repair_task()`。
  - 修复任务由开发工程师 Agent 执行。
  - 输入是 `RepairRequest`。
  - 输出是修复后的 `CodeManifest`。

- `tasks/__init__.py`
  - 导出 `create_repair_task()`。

- `tools/__init__.py`
  - 导出修复上下文工具函数。

- `workflow/__init__.py`
  - 导出 `RepairTaskBuildResult` 和 `build_repair_task_from_artifacts()`。

- `main.py`
  - 新增命令行参数：

```bash
.venv\Scripts\python.exe main.py --build-repair-task
```

这个命令只构建修复任务，不调用大模型执行。

### 为什么读取磁盘上的当前源码

修复任务需要的是“当前源码”，不是“最初生成时的源码”。

如果后续自动修复已经改过一次文件，`outputs/code_manifest.full.json` 可能不是最新内容。为了让修复任务拿到真实当前状态，阶段 5D 的 `load_current_code_manifest()` 会直接读取：

```text
generated/snake-game/index.html
generated/snake-game/style.css
generated/snake-game/script.js
```

这样后续每轮修复都能基于最新源码继续工作。

### 当前命令验证

运行：

```bash
.venv\Scripts\python.exe main.py --build-repair-task
```

当前输出：

```text
阶段 5D 开发修复任务已构建：
- 执行角色：开发工程师
- 任务名称：开发修复任务
- 当前源码文件数：3
- 缺陷数量：0
```

这里缺陷数量是 0，是因为当前 Mock 贪吃蛇 Demo 已经通过 10 条本地测试。

### 本阶段验证命令

编译检查：

```bash
.venv\Scripts\python.exe -m compileall schemas tools tasks workflow tests main.py
```

阶段 5D 单元测试：

```bash
.venv\Scripts\python.exe -m unittest tests.test_repair_task -v
```

实际结果：

```text
Ran 3 tests
OK
```

### 下一阶段

阶段 5E 可以开始做“自动修复循环”。

下一阶段要把这些步骤串起来：

```text
运行 Test Runner
→ 如果失败，构建 RepairRequest
→ 执行开发修复任务
→ 保存修复后的 CodeManifest
→ 再次运行 Test Runner
→ 最多重复 2 轮
```

## 阶段 5E - 最多 2 轮自动修复循环

### 目标

实现测试失败后的自动修复闭环。

流程是：

```text
运行 Test Runner
→ 如果通过：结束
→ 如果失败：生成结构化缺陷报告
→ 开发 Agent 根据 RepairRequest 修复源码
→ 保存修复后的 CodeManifest
→ 再次运行 Test Runner
→ 最多修复 2 轮
```

### 修改文件

- `workflow/repair.py`
  - 新增 `RepairRoundRecord`，记录每一轮修复前报告、修复后源码、修复后报告。
  - 新增 `RepairLoopResult`，记录最终是否通过、使用了几轮修复、最终测试报告和每轮记录。
  - 新增 `execute_repair_task()`，真实执行开发修复任务。
  - 新增 `run_auto_repair_loop()`，执行最多 `max_rounds` 轮修复循环。
  - 新增 `run_auto_repair_loop_from_artifacts()`，从已落盘产物读取需求和架构后执行修复循环。

- `workflow/__init__.py`
  - 导出 `RepairRoundRecord`、`RepairLoopResult` 和 `run_auto_repair_loop_from_artifacts()`。

- `main.py`
  - 新增命令行参数：

```bash
.venv\Scripts\python.exe main.py --auto-repair
```

- `tests/test_auto_repair_loop.py`
  - 新增自动修复循环测试：
    - 初始测试通过时不调用修复任务。
    - 第一轮修复成功后立即停止。
    - 持续失败时最多修复 2 轮。

### 核心实现逻辑

`run_auto_repair_loop()` 的核心逻辑是：

```text
先运行 Test Runner
如果 passed=true，返回成功，rounds_used=0

如果 failed：
  第 1 轮：
    读取当前源码
    构造 RepairRequest
    执行开发修复任务
    保存修复后的 CodeManifest
    再跑 Test Runner
    如果通过，结束

  第 2 轮：
    重复上面步骤
    如果仍失败，返回失败
```

### 为什么支持注入 repair_executor

真实修复需要调用大模型，不适合放进单元测试。

所以 `run_auto_repair_loop()` 支持传入：

```python
repair_executor
```

测试时可以用假的修复函数模拟：

- 一轮修好。
- 两轮仍失败。
- 初始通过时不应被调用。

真实运行时不传 `repair_executor`，默认使用 `execute_repair_task()` 调用开发 Agent。

### 模型密钥检查

如果初始测试已经通过，自动修复循环不会调用大模型，因此不需要模型密钥。

如果测试失败，需要执行开发 Agent 修复任务，`execute_repair_task()` 会先检查模型配置。

这样可以避免“明明不用修复，却因为没配 API Key 失败”的尴尬情况。

### 当前命令验证

先恢复 Mock Demo：

```bash
.venv\Scripts\python.exe main.py --mock-demo
```

再运行自动修复：

```bash
.venv\Scripts\python.exe main.py --auto-repair
```

当前 Mock Demo 已经通过测试，所以自动修复输出：

```text
阶段 5E 自动修复循环已完成：
- 最终是否通过：True
- 已执行修复轮数：0
- 最终失败数量：0
- 最终报告：reports/test_report.md
```

### 本阶段验证命令

编译检查：

```bash
.venv\Scripts\python.exe -m compileall schemas tools tasks workflow tests main.py
```

阶段 5E 单元测试：

```bash
.venv\Scripts\python.exe -m unittest tests.test_auto_repair_loop -v
```

完整相关测试：

```bash
.venv\Scripts\python.exe -m unittest tests.test_static_test_runner tests.test_test_runner tests.test_workflow_test_runner_integration tests.test_repair_task tests.test_auto_repair_loop tests.test_run_demo_parsing -v
```

实际结果：

```text
Ran 14 tests
OK
```

### 当前状态

到阶段 5E，测试与修复闭环已经具备完整骨架：

```text
本地测试 Runner
→ 结构化 TestReport
→ 结构化 defects
→ RepairRequest
→ 开发修复任务
→ 最多 2 轮修复循环
```

后续可以继续增强真实修复执行的稳定性，比如保存每轮修复历史、记录每轮缺陷快照、给 DeepSeek 输出增加更强的 CodeManifest 规范化。

## 阶段 5F - 生成自动修复最终报告

### 目标

生成一份面向最终交付的自动修复总报告。

普通 `reports/test_report.md` 只表示“最后一次测试结果”。阶段 5F 要补充一份更完整的过程报告，记录：

- 初始测试结果。
- 第 1 轮修复结果。
- 第 2 轮修复结果。
- 最终是否通过。
- 未修复缺陷。
- 最终源码路径。

### 新增文件

- `schemas/final_repair_report.py`
  - 新增 `RepairRoundSummary`。
  - 新增 `FinalRepairReport`。
  - 用结构化方式表达自动修复流程的最终报告。

- `tests/test_final_repair_report.py`
  - 验证最终报告能记录两轮失败修复。
  - 验证报告中包含初始测试、两轮修复结果、未修复缺陷和最终源码路径。

### 修改文件

- `schemas/__init__.py`
  - 导出 `FinalRepairReport` 和 `RepairRoundSummary`。

- `tools/artifact_writer.py`
  - 新增 `save_final_repair_report()`。
  - 写入：
    - `reports/final_repair_report.md`
    - `reports/final_repair_report.json`

- `tools/__init__.py`
  - 导出 `save_final_repair_report()`。

- `workflow/repair.py`
  - `RepairLoopResult` 新增：
    - `initial_report`
    - `max_rounds`
    - `final_source_paths`
    - `final_repair_report`
  - 自动修复循环结束时，统一生成并保存最终报告。

- `main.py`
  - `--auto-repair` 输出中增加最终总报告路径：

```text
reports/final_repair_report.md
```

### 最终报告路径

阶段 5F 生成：

```text
reports/final_repair_report.md
reports/final_repair_report.json
```

其中 Markdown 给人阅读，JSON 给程序继续处理。

### 当前报告内容

当前 Mock Demo 初始测试已经通过，所以没有执行修复轮次。

当前 `reports/final_repair_report.md` 摘要：

```text
初始测试结果：通过
实际修复轮数：0
最大修复轮数：2
最终是否通过：True
未修复缺陷：无
最终源码路径：
- generated/snake-game/index.html
- generated/snake-game/style.css
- generated/snake-game/script.js
```

### 本阶段验证命令

编译检查：

```bash
.venv\Scripts\python.exe -m compileall schemas tools workflow tests main.py
```

阶段 5F 单元测试：

```bash
.venv\Scripts\python.exe -m unittest tests.test_final_repair_report -v
```

完整相关测试：

```bash
.venv\Scripts\python.exe -m unittest tests.test_static_test_runner tests.test_test_runner tests.test_workflow_test_runner_integration tests.test_repair_task tests.test_auto_repair_loop tests.test_final_repair_report tests.test_run_demo_parsing -v
```

实际结果：

```text
Ran 15 tests
OK
```

### 最终命令验证

恢复 Mock Demo：

```bash
.venv\Scripts\python.exe main.py --mock-demo
```

执行自动修复循环并生成最终报告：

```bash
.venv\Scripts\python.exe main.py --auto-repair
```

当前输出：

```text
阶段 5E 自动修复循环已完成：
- 最终是否通过：True
- 已执行修复轮数：0
- 最终失败数量：0
- 最终报告：reports/test_report.md
- 自动修复总报告：reports/final_repair_report.md
```

### 当前阶段状态

到阶段 5F，阶段 5 的“测试与自动修复闭环”已经具备完整交付形态：

```text
确定性测试 Runner
→ 结构化缺陷报告
→ 开发修复任务
→ 最多 2 轮自动修复
→ 最终自动修复报告
```

## 阶段 6 - 完善 README 和经验文档

### 目标

把项目文档从“阶段开发记录”补齐为“可运行、可展示、可复盘”的交付文档。

阶段 6 不改核心业务代码，主要完善：

- 完整运行流程。
- 环境变量配置方式。
- Mock 模式和真实模式区别。
- 自动修复机制说明。
- 阶段 5 遇到的问题和经验记录。

### 修改文件

- `README.md`
  - 重写为完整使用手册。
  - 补充当前项目能力。
  - 补充环境准备和 `.env` 配置。
  - 补充 Mock 模式和真实模式区别。
  - 补充常用命令总览。
  - 补充推荐完整运行流程。
  - 补充自动修复机制说明。
  - 补充测试命令和目录结构。

- `docs/experience.md`
  - 新增经验 20：最终修复报告不要复用单次测试报告结构。
  - 新增经验 21：README 要随着项目阶段同步升级成使用手册。

- `docs/development-log.md`
  - 记录阶段 6 的文档改动。

### README 当前覆盖内容

README 现在包含：

- 项目简介。
- 当前能力。
- 环境准备。
- 环境变量配置。
- Mock 模式说明。
- 真实模式说明。
- 常用命令。
- 推荐完整运行流程。
- 自动修复机制。
- 测试命令。
- 目录结构。
- 已知注意事项。

### 推荐运行流程

本地无模型验证：

```bash
.venv\Scripts\python.exe main.py --mock-demo
.venv\Scripts\python.exe main.py --auto-repair
```

真实 Agent 流程：

```bash
.venv\Scripts\python.exe main.py --run-demo
.venv\Scripts\python.exe main.py --auto-repair
```

### 当前文档分工

- `README.md`
  - 面向使用和展示。
  - 解决“这个项目怎么跑”的问题。

- `docs/development-log.md`
  - 面向学习过程。
  - 解决“这个项目每一步怎么搭起来”的问题。

- `docs/experience.md`
  - 面向排错复盘。
  - 解决“开发过程中踩过哪些坑”的问题。

### 验证方式

阶段 6 是文档阶段，不新增业务代码。

本阶段检查重点：

- README 是否覆盖完整运行流程。
- README 是否说明环境变量配置。
- README 是否说明 Mock 和真实模式区别。
- README 是否说明自动修复机制。
- `docs/experience.md` 是否继续记录阶段 5 后续经验。

## 阶段 7 - 最终验收

### 目标

对整个项目做最终验收，确认本地链路、真实 Agent 链路、测试 Runner、浏览器页面和最终产物都可用。

验收内容：

- 用 Mock Demo 验证本地链路。
- 用真实 CrewAI Demo 验证 Agent 链路。
- 用 Test Runner 验证生成页面。
- 浏览器打开贪吃蛇页面。
- 检查最终产物：
  - 页面源码
  - 需求文档
  - 架构文档
  - 测试报告
  - 经验文档

### Mock Demo 验收

运行：

```bash
.venv\Scripts\python.exe main.py --mock-demo
.venv\Scripts\python.exe main.py --auto-repair
```

结果：

```text
最终是否通过：True
已执行修复轮数：0
最终失败数量：0
```

说明本地工程链路可用。

### 真实 CrewAI Demo 验收

运行：

```bash
.venv\Scripts\python.exe main.py --run-demo
```

结果：

```text
Crew Execution Completed
贪吃蛇 Demo 执行完成
```

真实 CrewAI 链路已生成需求文档、架构文档、源码文件和测试报告。

### Test Runner 验收

运行：

```bash
.venv\Scripts\python.exe main.py --test-runner
.venv\Scripts\python.exe main.py --auto-repair
```

最终结果：

```text
test_report: True 10 10 0
final_report: True 0 2
```

说明：

- 10 条本地测试全部通过。
- 自动修复未执行，因为初始测试已经通过。
- 未发现未修复缺陷。

### 浏览器验收

启动本地服务：

```bash
cd generated\snake-game
..\..\.venv\Scripts\python.exe -m http.server 8765 --bind 127.0.0.1
```

访问：

```text
http://127.0.0.1:8765/index.html
```

浏览器检查结果：

```json
{
  "title": "贪吃蛇游戏",
  "hasCanvas": true,
  "canvasWidth": "400",
  "canvasHeight": "400",
  "hasScore": true,
  "scoreText": "0",
  "hasRestartButton": true,
  "restartText": "重新开始",
  "errorLogs": []
}
```

交互检查：

- 点击“重新开始”按钮后，游戏结束文本消失。
- 发送方向键后没有控制台错误。

### 新增验收报告

新增：

- `reports/acceptance_report.md`
- `reports/acceptance_report.json`

这两份报告记录最终验收命令、结果、浏览器检查和产物清单。

### 最终产物

页面源码：

- `generated/snake-game/index.html`
- `generated/snake-game/style.css`
- `generated/snake-game/script.js`

需求文档：

- `outputs/requirements.md`
- `outputs/requirements.json`

架构文档：

- `outputs/architecture.md`
- `outputs/architecture.json`

测试报告：

- `reports/test_report.md`
- `reports/test_report.json`
- `reports/final_repair_report.md`
- `reports/final_repair_report.json`
- `reports/acceptance_report.md`
- `reports/acceptance_report.json`

经验文档：

- `docs/experience.md`
- `docs/development-log.md`

### 验收结论

阶段 7 验收通过。

当前项目已经具备：

```text
4-Agent CrewAI 顺序开发流程
→ 结构化中间产物
→ HTML/CSS/JavaScript 项目生成
→ 本地确定性 Test Runner
→ 结构化缺陷报告
→ 最多 2 轮自动修复
→ 最终测试报告和验收报告
```
## 阶段 8：上传 GitHub

### 本阶段目标

把本地项目初始化为 Git 仓库，并连接到远程仓库：

```text
https://github.com/gh-xiaoyong/SoftTeam.git
```

### 本阶段改动

#### 1. 初始化 Git 仓库

当前项目目录原本还不是 Git 仓库，因此需要先执行：

```bash
git init
```

初始化后，本地默认分支为 `main`。

#### 2. 调整 `.gitignore`

原来的 `.gitignore` 忽略了 `docs/`，这会导致开发日志和经验文档无法上传。

调整后忽略内容为：

```text
.env
.venv/
__pycache__/
*.pyc
.pytest_cache/
tmp/
```

这样既能保护真实密钥和虚拟环境，又能保留项目文档、生成源码和测试报告。

#### 3. 上传前安全检查

上传前执行了敏感信息检查：

```bash
rg -n "sk-|DEEPSEEK_API_KEY|OPENAI_API_KEY|api[_-]?key|password|token" -g "!.venv/**" -g "!tmp/**"
```

检查结果只包含文档中的变量名、占位符和配置说明，没有发现真实 API Key。

#### 4. 连接 GitHub 远程仓库

远程仓库地址：

```text
https://github.com/gh-xiaoyong/SoftTeam.git
```

后续使用 `origin` 作为远程名称。

### 本阶段经验

项目上传 GitHub 时，不要只关注“能不能 push 成功”，还要关注：

- `.env` 是否被忽略。
- `.venv/` 是否被忽略。
- 重要文档是否没有被误忽略。
- README、源码、测试、报告是否都在提交范围内。

这一步相当于把本地 Demo 整理成可以展示、可以复盘、可以继续迭代的项目。
