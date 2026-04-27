# 开发指南


## 目录

- [开发指南](#开发指南)
  - [目录](#目录)
  - [1. 项目架构](#1-项目架构)
  - [2. 基础使用](#2-基础使用)
    - [2.1 交互式命令](#21-交互式命令)
    - [2.2 入口点](#22-入口点)
    - [2.3 BPS 数据管道](#23-bps-数据管道)
  - [3. 扩展能力](#3-扩展能力)
    - [3.1 添加自定义工具](#31-添加自定义工具)
    - [3.2 添加 MCP 工具](#32-添加-mcp-工具)
    - [3.3 自定义存储](#33-自定义存储)
    - [3.4 初始化 Claude Skills（推荐）](#34-初始化-claude-skills推荐)
    - [3.5 添加新的Skill](#35-添加新的skill)
    - [3.6 自定义系统提示词](#36-自定义系统提示词)
  - [4. 故障排查](#4-故障排查)
    - [4.1 常见问题](#41-常见问题)
    - [4.2 调试技巧](#42-调试技巧)

---

## 1. 项目架构

```
bps-stat-agent/
├── mini_agent/                    # 核心源代码
│   ├── agent.py                   # 主 Agent 循环（Token 管理、工具执行）
│   ├── cli.py                     # CLI 入口点（交互式 + 非交互式）
│   ├── config.py                  # Pydantic 配置加载（YAML + 环境变量）
│   ├── colors.py                  # ANSI 终端颜色常量
│   ├── logger.py                  # JSON 结构化 Agent 运行日志
│   ├── retry.py                   # 异步重试（指数退避）
│   ├── setup_wizard.py            # 交互式设置向导（bpsagent setup）
│   ├── health.py                  # HTTP 健康检查服务器（/health、/ready、/metrics）
│   ├── metrics.py                 # Prometheus 指标（可选，优雅降级）
│   ├── tracing.py                 # OpenTelemetry 追踪（可选，优雅降级）
│   ├── logging_config.py          # 集中式 JSON 结构化日志
│   │
│   ├── bps_api.py                 # BPS WebAPI 客户端（59 端点）
│   ├── bps_mcp_server.py          # FastMCP 服务器（62 个工具）
│   ├── bps_models.py              # BPSResourceType 枚举 + BPSResolvedResource
│   ├── bps_orchestrator.py        # AllStats 优先搜索 → 解析 → 检索
│   ├── bps_resolution.py          # 将搜索结果分类为资源类型
│   ├── bps_data_retriever.py      # 表格搜索 → 获取 → HTML 解析管道
│   ├── bps_resource_retriever.py  # 统一检索（含回退链）
│   ├── bps_normalization.py       # 规范化响应构建器
│   ├── allstats_client.py         # Playwright 浏览器自动化（AllStats 搜索）
│   │
│   ├── llm/                       # LLM 抽象层
│   │   ├── base.py                # 抽象 LLMClientBase (ABC)
│   │   ├── llm_wrapper.py         # 统一 LLMClient（提供商路由）
│   │   ├── anthropic_client.py    # Anthropic SDK（thinking、tool_use、缓存）
│   │   └── openai_client.py       # OpenAI SDK（reasoning、tool_calls）
│   │
│   ├── schema/                    # Pydantic 数据模型
│   │   └── schema.py              # Message、ToolCall、LLMResponse、TokenUsage
│   │
│   ├── tools/                     # 工具实现
│   │   ├── base.py                # Tool ABC + ToolResult
│   │   ├── bash_tool.py           # BashTool（前台/后台）、BashOutputTool、BashKillTool
│   │   ├── file_tools.py          # ReadTool、WriteTool、EditTool
│   │   ├── note_tool.py           # SessionNoteTool + RecallNoteTool
│   │   ├── skill_tool.py          # GetSkillTool（渐进式披露）
│   │   ├── skill_loader.py        # SkillLoader（YAML 前置解析器）
│   │   └── mcp_loader.py          # MCPTool + MCPServerConnection
│   │
│   ├── acp/                       # Agent Client Protocol 桥接
│   │   ├── __init__.py            # BPSStatACPAgent
│   │   └── server.py              # ACP 服务器入口点
│   │
│   ├── utils/                     # 工具函数
│   │   └── terminal_utils.py      # 显示宽度计算（ANSI/emoji/CJK）
│   │
│   ├── config/                    # 配置文件
│   │   ├── config-example.yaml    # 完整注释配置模板
│   │   ├── mcp-example.json       # MCP 服务器配置模板
│   │   └── system_prompt.md       # 系统提示词（印尼语/英语双语）
│   │
│   └── skills/                    # Agent 技能（git 子模块）
│       └── bps-master/            # BPS 领域技能（含工具文档）
│
├── tests/                         # 418+ 个测试
├── examples/                      # 6 个使用示例
├── docs/                          # 开发与生产指南
├── scripts/                       # 安装脚本（macOS/Linux/Windows）
├── pyproject.toml                 # 包定义
├── Dockerfile                     # 多阶段 Docker 构建
├── docker-compose.yml             # 3 个服务（CLI、MCP、ACP）
├── Makefile                       # 20 个开发目标
├── .github/workflows/ci.yml      # CI 管道（lint、test、security、build）
├── ruff.toml                      # Linter 配置
├── .env.example                   # 环境变量模板
└── README.md
```

## 2. 基础使用

### 2.1 交互式命令

在交互模式（通过 `bpsagent` 启动）下运行 Agent 时，您可以使用以下命令：

| 命令                   | 说明                                             |
| ---------------------- | ------------------------------------------------ |
| `/exit`, `/quit`, `/q` | 退出 Agent 并显示会话统计信息                    |
| `/help`                | 显示帮助信息和可用命令                           |
| `/clear`               | 清除消息历史并开始新会话                         |
| `/history`             | 显示当前会话的消息数量                           |
| `/stats`               | 显示会话统计信息（步数、工具调用、使用的 Token） |
| `/log [filename]`      | 显示日志文件或读取特定日志文件                   |

### 2.2 入口点

| 命令 | 说明 |
|------|------|
| `bpsagent setup` | 交互式设置向导（安装后首先运行） |
| `bpsagent` | 交互式 CLI Agent，用于查询 BPS 数据 |
| `bpsagent --task "query"` | 非交互式模式，执行单个查询 |
| `bpsagent --workspace DIR` | 指定自定义工作目录 |
| `bps-mcp-server` | 通过 STDIO 运行的 MCP 服务器（62 个工具） |
| `bpsagent-acp` | ACP 服务器，用于 Agent 间通信 |

### 2.3 BPS 数据管道

Agent 使用 **AllStats 优先回退管道** 进行数据检索：

```
查询 → BPSOrchestrator.answer_query()
  ├── 1. AllStatsClient.search() [Playwright 浏览器自动化]
  │     └── Cloudflare 绕过（反检测、新上下文重试）
  ├── 2. _select_best_result() [相关性评分]
  ├── 3. classify_search_result() → BPSResolvedResource
  │     └── 映射为: TABLE, PUBLICATION, PRESSRELEASE, NEWS, INFOGRAPHIC 等
  ├── 4. BPSResourceRetriever.retrieve()
  │     ├── TABLE → get_static_table_detail() → HTML 解析 → 结构化数据
  │     │     └── 回退: 关键词搜索 → 重新选择 → 重试详情
  │     ├── PUBLICATION → get_publication_detail() → BPSMaterial (PDF/封面)
  │     ├── PRESSRELEASE → get_press_release_detail() → BPSMaterial
  │     └── OTHER → search_result_only（仅元数据）
  └── 5. build_normalized_response() → 带溯源的规范化响应
```

## 3. 扩展能力

### 3.1 添加自定义工具

#### 步骤

1.  在 `mini_agent/tools/` 目录下创建一个新的 Python 文件。
2.  在文件中定义一个新类，并继承 `Tool` 基类。
3.  在类中实现所需的属性和方法。
4.  在 Agent 初始化时注册你的新工具。

#### 示例

```python
# mini_agent/tools/my_tool.py
from mini_agent.tools.base import Tool, ToolResult
from typing import Dict, Any

class MyTool(Tool):
    @property
    def name(self) -> str:
        """工具的唯一名称，需保持独一无二。"""
        return "my_tool"
    
    @property
    def description(self) -> str:
        """工具用途的详细描述，帮助 LLM 理解其功能。"""
        return "我的自定义工具，用于完成特定任务"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """参数模式（JSON Schema 格式）。"""
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "第一个参数"
                },
                "param2": {
                    "type": "integer",
                    "description": "第二个参数",
                    "default": 10
                }
            },
            "required": ["param1"]
        }
    
    async def execute(self, param1: str, param2: int = 10) -> ToolResult:
        """
        工具执行的核心逻辑。
        
        Args:
            param1: 参数一。
            param2: 参数二，包含默认值。
        
        Returns:
            返回一个 ToolResult 对象。
        """
        try:
            # 在此实现你的逻辑
            result = f"处理了 {param1}，param2={param2}"
            
            return ToolResult(
                success=True,
                content=result
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content=f"错误: {str(e)}"
            )

# 在 cli.py 或 Agent 的初始化代码中
from mini_agent.tools.my_tool import MyTool

# 创建 Agent 实例时，将新工具加入列表
tools = [
    ReadTool(workspace_dir),
    WriteTool(workspace_dir),
    MyTool(),  # 添加您的自定义工具
]

agent = Agent(
    llm=llm,
    tools=tools,
    max_steps=50
)
```

### 3.2 添加 MCP 工具

编辑 `mcp.json` 文件，即可添加新的 MCP 服务器：

```json
{
  "mcpServers": {
    "my_custom_mcp": {
      "description": "我的自定义 MCP 服务器",
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@my-org/my-mcp-server"],
      "env": {
        "API_KEY": "your-api-key"
      },
      "disabled": false,
      "notes": {
        "description": "这是一个自定义 MCP 服务器。",
        "api_key_url": "https://example.com/api-keys"
      }
    }
  }
}
```

### 3.3 自定义存储

您可以替换 `SessionNoteTool` 的默认存储实现，以对接不同的数据后端：

```python
# 默认实现：JSON 文件
class SessionNoteTool:
    def __init__(self, memory_file: str = "./workspace/.agent_memory.json"):
        self.memory_file = Path(memory_file)
    
    async def _save_notes(self, notes: List[Dict]):
        with open(self.memory_file, 'w') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)

# 扩展示例：使用 PostgreSQL 存储
class PostgresNoteTool(Tool):
    def __init__(self, db_url: str):
        self.db = PostgresDB(db_url)
    
    async def _save_notes(self, notes: List[Dict]):
        await self.db.execute(
            "INSERT INTO notes (content, category, timestamp) VALUES ($1, $2, $3)",
            notes
        )

# 扩展示例：使用向量数据库存储
class MilvusNoteTool(Tool):
    def __init__(self, milvus_host: str):
        self.vector_db = MilvusClient(host=milvus_host)
    
    async def _save_notes(self, notes: List[Dict]):
        # 生成内容的嵌入向量
        embeddings = await self.get_embeddings([n["content"] for n in notes])
        
        # 将笔记和向量存入向量数据库
        await self.vector_db.insert(
            collection="agent_notes",
            data=notes,
            embeddings=embeddings
        )
```

### 3.4 初始化 Claude Skills（推荐）

本项目通过 Git Submodule 的方式集成了 Claude 官方技能库。首次克隆项目后，请执行以下命令来初始化技能库：

```bash
# 初始化并拉取技能库子模块
git submodule update --init --recursive
```

Skills 库提供了超过20种专业能力，能让 Agent 如同行业专家般处理复杂任务：

- 📄 **文档处理**：轻松创建和编辑 PDF、DOCX、XLSX、PPTX 等格式的文档。
- 🎨 **设计创作**：生成富有创意的艺术作品、海报和 GIF 动画。
- 🧪 **开发与测试**：支持 Web 自动化测试 (Playwright) 和 MCP 服务器开发。
- 🏢 **企业应用**：高效处理内部沟通、品牌指南应用和主题定制等任务。

✨ **这是本项目的核心亮点之一。**

**更多信息：**

- [Claude Skills 官方文档](https://docs.claude.com/zh-CN/docs/agents-and-tools/agent-skills)
- [Anthropic 博客：为真实世界装备智能体](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 3.5 添加新的Skill

您可以按照以下步骤创建自定义 Skill：

```bash
# 在 skills/ 目录下为您的新技能创建一个目录
mkdir skills/my-custom-skill
cd skills/my-custom-skill

# 创建技能描述文件 SKILL.md
cat > SKILL.md << 'EOF'
---
name: my-custom-skill
description: 这是一个自定义技能，用于处理特定任务。
---

# 概述

该技能主要提供以下功能：
- 功能 1
- 功能 2

# 使用方法

1. 第一步...
2. 第二步...

# 最佳实践

- 实践 1
- 实践 2

# 常见问题

问：问题 1
答：答案 1
EOF
```

完成以上步骤后，Agent 将在下次启动时自动加载并识别这项新技能。

### 3.6 自定义系统提示词

系统提示词文件 (`system_prompt.md`) 定义了 Agent 的核心行为、能力边界和工作指南。您可以根据具体应用场景，对其进行深度定制。

#### 可定制内容包括：

1.  **核心能力**：添加或修改工具的描述，以影响 Agent 的工具选择。
2.  **工作指南**：定义特定的工作流程或决策偏好。
3.  **领域专业知识**：注入特定领域的知识，提升 Agent 的专业性。
4.  **沟通风格**：调整 Agent 与用户交互时的语气和风格。
5.  **任务优先级**：设定处理任务时的优先级和策略。

完成修改后，请重启 Agent 以使新配置生效。

## 4. 故障排查

### 4.1 常见问题

#### API 密钥配置错误

```bash
# 错误消息
Error: Invalid API key

# 解决方法
1. 检查 `config.yaml` 文件中的 API 密钥是否填写正确。
2. 确保密钥前后没有多余的空格或引号。
3. 确认该 API 密钥是否仍在有效期内。
```

#### 依赖安装失败

```bash
# 错误消息
uv sync failed

# 解决方法
1. 升级 uv 至最新版本：`uv self update`
2. 清理 uv 缓存：`uv cache clean`
3. 再次尝试同步依赖：`uv sync`
```

#### MCP 工具加载失败

```bash
# 错误消息
Failed to load MCP server

# 解决方法
1. 检查 `mcp.json` 文件中的服务器配置是否正确。
2. 确保您的开发环境已安装 Node.js (大部分 MCP 工具的运行需要)。
3. 确认所需服务的 API 密钥已正确配置。
4. 运行 MCP 测试并查看详细日志：`pytest tests/test_mcp.py -v -s`
```

### 4.2 调试技巧

#### 启用 Debug 日志

```python
# 在 cli.py 或相关测试文件的开头添加以下代码：
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### 使用 Python 调试器

```python
# 在需要暂停执行的代码行处插入断点：
import pdb; pdb.set_trace()

# 或者使用 ipdb 以获得更佳的调试体验：
import ipdb; ipdb.set_trace()
```

#### 监控工具调用

```python
# 在 Agent 代码中添加日志，以便实时查看工具的调用详情：
logger.debug(f"工具调用: {tool_call.name}")
logger.debug(f"工具参数: {tool_call.arguments}")
logger.debug(f"工具结果: {result.content[:200]}")
```

