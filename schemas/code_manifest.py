"""开发工程师 Agent 输出的代码文件清单。"""

from pydantic import BaseModel, Field


class GeneratedFile(BaseModel):
    """开发工程师生成的单个源码文件。"""

    path: str = Field(description="文件路径")
    purpose: str = Field(description="文件用途")
    language: str = Field(description="文件语言或类型，例如：html、css、javascript")
    content: str = Field(default="", description="文件完整源码内容")


class CodeManifest(BaseModel):
    """开发工程师交给测试工程师的代码文件清单。"""

    project_name: str = Field(description="生成项目名称")
    project_root: str = Field(description="生成项目根目录")
    entry_point: str = Field(description="页面入口文件")
    files: list[GeneratedFile] = Field(description="生成文件列表")
    run_instruction: str = Field(description="如何运行或打开项目")
