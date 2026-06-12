"""架构师 Agent 输出的结构化技术方案。"""

from pydantic import BaseModel, Field


class FileDesign(BaseModel):
    """计划生成的单个项目文件。"""

    path: str = Field(description="文件路径，例如：generated/snake-game/index.html")
    responsibility: str = Field(description="文件职责，例如：页面结构、样式、交互逻辑")


class ModuleDesign(BaseModel):
    """应用中的一个逻辑模块。"""

    name: str = Field(description="模块名称，例如：游戏主循环")
    responsibility: str = Field(description="模块职责")
    dependencies: list[str] = Field(default_factory=list, description="依赖的其他模块")


class ArchitecturePlan(BaseModel):
    """架构师交给开发工程师的技术方案。"""

    tech_stack: list[str] = Field(description="技术栈，例如：HTML、CSS、JavaScript")
    files: list[FileDesign] = Field(description="文件设计列表")
    modules: list[ModuleDesign] = Field(description="模块设计列表")
    data_flow: list[str] = Field(description="核心数据流说明")
    implementation_notes: list[str] = Field(description="开发时需要注意的实现细节")

