# 生产环境指南

> BPS Stat Agent 的部署、运维与监控指南。

## 目录

- [1. 概述](#1-概述)
- [2. Docker 快速开始](#2-docker-快速开始)
- [3. Docker Compose](#3-docker-compose)
- [4. Makefile 参考](#4-makefile-参考)
- [5. 配置](#5-配置)
- [6. 可观测性](#6-可观测性)
  - [6.1 结构化日志](#61-结构化日志)
  - [6.2 Prometheus 指标](#62-prometheus-指标)
  - [6.3 OpenTelemetry 链路追踪](#63-opentelemetry-链路追踪)
  - [6.4 健康检查](#64-健康检查)
- [7. CI/CD 流水线](#7-cicd-流水线)
- [8. 安全加固](#8-安全加固)
- [9. 资源限制](#9-资源限制)
- [10. Kubernetes 部署](#10-kubernetes-部署)
- [11. 升级方向](#11-升级方向)
- [12. 生产环境检查清单](#12-生产环境检查清单)

---

## 1. 概述

BPS Stat Agent 提供了生产级的基础设施支持：

| 能力              | 实现方式                                                                       |
| ----------------- | ------------------------------------------------------------------------------ |
| **容器镜像**      | 多阶段 Dockerfile（构建阶段 + 运行阶段），基于 python:3.11-slim，非 root 用户  |
| **编排**          | docker-compose.yml 支持 3 种服务配置（cli/mcp/acp），含资源限制                |
| **构建自动化**    | Makefile 提供 20+ 目标，覆盖安装、检查、测试、构建、Docker 和运行              |
| **CI/CD**         | GitHub Actions — 代码检查、测试、安全审计、构建（Python 3.11/3.12 矩阵）       |
| **日志**          | 集中式 JSON 日志输出到 stdout（兼容 12-Factor 规范）                           |
| **指标**          | Prometheus 指标（Agent 运行次数、LLM 请求、Token 用量、工具调用）              |
| **链路追踪**      | OpenTelemetry 分布式链路追踪，支持 OTLP 导出                                  |
| **健康检查**      | 后台线程提供 HTTP 端点（/health、/ready、/metrics）                            |
| **安全**          | Bash 工具默认禁用、非 root 容器、密钥不打入镜像                               |

---

## 2. Docker 快速开始

```bash
# 1. 克隆并进入项目目录
git clone https://github.com/juliochwd/bps-stat-agent.git
cd bps-stat-agent

# 2. 创建环境变量文件
cp .env.example .env
# 编辑 .env — 至少设置一个 LLM API Key

# 3. 复制配置文件
mkdir -p config
cp mini_agent/config/config-example.yaml config/config.yaml
# 编辑 config/config.yaml — 设置 api_key、model、provider

# 4. 构建镜像
docker compose build

# 5. 运行（选择一种模式）
docker compose --profile cli run --rm agent          # 交互式 CLI
docker compose --profile mcp up -d                   # MCP 服务器（后台运行）
docker compose --profile acp up -d                   # ACP 服务器（后台运行）
```

### Dockerfile 架构

镜像采用**多阶段构建**以最小化最终镜像体积：

| 阶段        | 基础镜像            | 用途                                                       |
| ----------- | ------------------- | ---------------------------------------------------------- |
| `builder`   | python:3.11-slim    | 安装 uv、同步依赖、编译 wheel 包                          |
| `runtime`   | python:3.11-slim    | 从 builder 复制虚拟环境、安装 Playwright chromium、运行    |

主要特性：
- **uv** 包管理器（从 `ghcr.io/astral-sh/uv:latest` 复制），实现快速、可复现的安装
- **层缓存优化** — 先复制 `pyproject.toml` 和 `uv.lock`，再复制源码，以获得最佳缓存命中率
- **Playwright chromium** 在运行阶段安装，包含操作系统依赖
- **非 root 用户** `agent`，拥有独立的主目录 `/home/agent`
- **HEALTHCHECK** 内置于镜像中（每 30 秒执行一次 import 冒烟测试）

---

## 3. Docker Compose

`docker-compose.yml` 定义了三个服务，通过 **profiles** 激活：

| 服务          | Profile | 命令                 | 说明                           |
| ------------- | ------- | -------------------- | ------------------------------ |
| `agent`       | `cli`   | `bps-stat-agent`     | 交互式 CLI 会话               |
| `mcp-server`  | `mcp`   | `bps-mcp-server`     | MCP 服务器（stdio，长驻进程） |
| `acp-server`  | `acp`   | `bps-stat-agent-acp` | ACP 服务器（长驻进程）        |

### 使用方式

```bash
# 交互式 CLI（一次性运行）
docker compose --profile cli run --rm agent

# 后台启动 MCP 服务器
docker compose --profile mcp up -d

# 后台启动 ACP 服务器
docker compose --profile acp up -d

# 查看日志
docker compose logs -f

# 停止所有服务
docker compose down
```

### 环境变量

API Key 通过环境变量传入。compose 文件支持两种方式：

1. **宿主机环境变量** — 运行前 export `ANTHROPIC_AUTH_TOKEN`、`OPENAI_API_KEY` 或 `MINIMAX_API_KEY`
2. **`.env` 文件** — 在项目根目录创建 `.env` 文件（可选，非必需）

### 数据卷

| 挂载路径                                       | 用途                           |
| ---------------------------------------------- | ------------------------------ |
| `./config:/home/agent/.bps-stat-agent/config:ro` | 配置目录（只读）             |
| `./workspace:/app/workspace`                   | Agent 工作目录（读写）        |
| 命名卷用于日志                                 | 持久化日志存储                 |
| `tmpfs /tmp`（1GB）                            | 临时文件（非持久化）           |

### 资源限制

每个服务均受以下约束：
- **CPU**：最多 2 核，保留 0.5 核
- **内存**：最多 2GB，保留 512MB
- **临时磁盘**：`/tmp` 挂载 1GB tmpfs

---

## 4. Makefile 参考

运行 `make help` 查看所有目标。概览如下：

| 分类            | 目标            | 说明                                             |
| --------------- | --------------- | ------------------------------------------------ |
| **安装**        | `install`       | 安装生产依赖（锁定版本）                         |
|                 | `install-dev`   | 安装全部依赖 + 开发组 + Playwright               |
|                 | `setup`         | 首次完整安装（install-dev + 初始化配置）          |
| **代码质量**    | `lint`          | 使用 ruff 检查源码和测试                          |
|                 | `format`        | 使用 ruff 自动格式化代码                          |
|                 | `check`         | 运行 lint + 测试（质量门禁）                      |
| **测试**        | `test`          | 运行测试（排除实时/网络测试）                     |
|                 | `test-cov`      | 运行测试并生成覆盖率报告                          |
|                 | `test-live`     | 仅运行 BPS 实时集成测试                           |
|                 | `test-all`      | 运行全部测试（单元测试 + 实时测试）               |
| **构建**        | `build`         | 构建 sdist 和 wheel 包                            |
|                 | `clean`         | 清理构建产物和缓存                                |
| **Docker**      | `docker-build`  | 通过 compose 构建 Docker 镜像                     |
|                 | `docker-up`     | 后台启动服务（MCP profile）                       |
|                 | `docker-down`   | 停止并移除所有容器                                |
|                 | `docker-logs`   | 追踪所有服务的日志                                |
| **运行**        | `run`           | 启动交互式 CLI                                    |
|                 | `run-mcp`       | 启动 MCP 服务器                                   |
|                 | `run-acp`       | 启动 ACP 服务器                                   |
|                 | `run-task`      | 执行指定任务：`make run-task TASK="..."`          |

---

## 5. 配置

### 配置文件位置（按优先级排序）

1. `mini_agent/config/config.yaml` — 开发环境（当前目录）
2. `~/.bps-stat-agent/config/config.yaml` — 用户配置目录
3. `<package>/mini_agent/config/config.yaml` — 包安装目录

### 环境变量（`.env`）

将 `.env.example` 复制为 `.env` 并设置相应的值：

```bash
# LLM API Key（必填 — 选择其一）
ANTHROPIC_AUTH_TOKEN=your-key
# OPENAI_API_KEY=your-key
# MINIMAX_API_KEY=your-key

# BPS WebAPI Key（访问 BPS 数据时必填）
BPS_API_KEY=your-key

# 可选
LOG_LEVEL=INFO
LOG_JSON_OUTPUT=false
```

### 配置 YAML — 日志与链路追踪部分

```yaml
# ===== Logging Configuration =====
logging:
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR
  json_output: false      # true for production (JSON to stdout), false for development
  # log_file: null        # Optional: path to additional log file

# ===== Tracing Configuration =====
tracing:
  enabled: false          # Enable OpenTelemetry tracing
  exporter: "none"        # "none", "console", or "otlp"
  # otlp_endpoint: "http://localhost:4317"  # OTLP gRPC endpoint
```

---

## 6. 可观测性

可观测性功能为**可选项** — Agent 无需这些功能也能正常运行。按需安装对应的扩展包：

```bash
pip install bps-stat-agent[metrics]        # Prometheus 指标
pip install bps-stat-agent[tracing]        # OpenTelemetry 链路追踪
pip install bps-stat-agent[observability]  # 以上全部
```

如果未安装可选依赖包，所有指标/追踪操作将变为**静默空操作** — 不会报错，也不会产生额外开销。

### 6.1 结构化日志

**模块**：`mini_agent/logging_config.py`

集中式日志系统遵循 12-Factor 应用原则 — 所有日志输出到 **stdout**。

| 模式        | 格式                                            | 适用场景    |
| ----------- | ----------------------------------------------- | ----------- |
| 生产环境    | `json_output: true` — 每行一条结构化 JSON       | 日志聚合器（ELK、Loki、CloudWatch） |
| 开发环境    | `json_output: false` — 人类可读的文本格式       | 本地开发 |

JSON 日志条目示例：
```json
{
  "timestamp": "2025-01-15T10:30:00.123456+00:00",
  "level": "INFO",
  "logger": "mini_agent.agent",
  "message": "Agent run completed",
  "module": "agent",
  "function": "run",
  "line": 142
}
```

高频日志组件（`httpx`、`httpcore`、`urllib3`、`asyncio`）会被自动抑制到 WARNING 级别。

### 6.2 Prometheus 指标

**模块**：`mini_agent/metrics.py`

依赖：`pip install bps-stat-agent[metrics]`

共暴露 10 个指标，覆盖三个领域：

| 指标名称                        | 类型      | 标签                            | 说明                           |
| ------------------------------- | --------- | ------------------------------- | ------------------------------ |
| `agent_runs_total`              | Counter   | `status`                        | Agent 运行总次数               |
| `agent_steps_total`             | Counter   | —                               | 执行的总步数                   |
| `agent_run_duration_seconds`    | Histogram | —                               | Agent 运行耗时                 |
| `agent_active_runs`             | Gauge     | —                               | 当前活跃的运行数               |
| `llm_requests_total`            | Counter   | `provider`, `model`, `status`   | LLM API 请求总数               |
| `llm_request_duration_seconds`  | Histogram | `provider`, `model`             | LLM 请求延迟                   |
| `llm_tokens_total`              | Counter   | `provider`, `model`, `type`     | Token 消耗量（prompt/completion）|
| `llm_retries_total`             | Counter   | `provider`, `model`             | LLM 重试次数                   |
| `tool_calls_total`              | Counter   | `tool_name`, `status`           | 工具执行次数                   |
| `tool_call_duration_seconds`    | Histogram | `tool_name`                     | 工具执行延迟                   |

指标通过健康检查服务器的 `/metrics` 端点暴露（参见 [6.4](#64-健康检查)）。

**Prometheus 抓取配置**：
```yaml
scrape_configs:
  - job_name: "bps-stat-agent"
    static_configs:
      - targets: ["agent-host:8080"]
    metrics_path: /metrics
```

### 6.3 OpenTelemetry 链路追踪

**模块**：`mini_agent/tracing.py`

依赖：`pip install bps-stat-agent[tracing]`

提供跨 Agent 运行、LLM 调用和工具执行的分布式链路追踪。三个便捷函数用于创建带有正确属性的 Span：

| 函数               | Span 名称        | 属性                                    |
| ------------------ | ---------------- | --------------------------------------- |
| `trace_agent_run`  | `agent.run`      | `agent.run_id`                          |
| `trace_llm_call`   | `llm.generate`   | `llm.provider`, `llm.model`            |
| `trace_tool_call`  | `tool.execute`   | `tool.name`, `tool.argument_keys`       |

支持的导出器：

| 导出器    | 配置                                      | 后端                           |
| --------- | ----------------------------------------- | ------------------------------ |
| `none`    | `exporter: "none"`（默认）                | 禁用                           |
| `console` | `exporter: "console"`                     | 输出到 stdout（调试用）        |
| `otlp`    | `exporter: "otlp"` + `otlp_endpoint`     | Jaeger、Zipkin、Grafana Tempo  |

环境变量覆盖：`OTEL_EXPORTER`、`OTEL_EXPORTER_OTLP_ENDPOINT`。

### 6.4 健康检查

**模块**：`mini_agent/health.py`

一个轻量级 HTTP 服务器以**后台线程**的方式与主 Agent 进程并行运行。

| 端点       | 用途                                       | 响应                                    |
| ---------- | ------------------------------------------ | --------------------------------------- |
| `/health`  | 存活探针 — 进程是否存活？                  | `200`，包含运行时间、版本、时间戳       |
| `/ready`   | 就绪探针 — 是否可以接受请求？              | `200` 或 `503`，取决于就绪检查结果      |
| `/metrics` | Prometheus 指标（需安装对应依赖）          | `200` 返回指标文本，或 `404`            |

代码中的使用方式：
```python
from mini_agent.health import start_health_server, stop_health_server

start_health_server(port=8080)
# ... Agent 运行 ...
stop_health_server()
```

**Docker HEALTHCHECK**（内置于 Dockerfile 中）：
```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import mini_agent; print(mini_agent.__version__)"]
```

---

## 7. CI/CD 流水线

每次向 `main`/`master` 推送代码或提交 PR 时，会触发两个 GitHub Actions 工作流：

### CI 流水线（`.github/workflows/ci.yml`）

```
lint → test → security → build
```

| 任务       | Python 矩阵   | 说明                                                     |
| ---------- | ------------- | -------------------------------------------------------- |
| **lint**   | 3.11, 3.12    | `ruff check` + `ruff format --check`                    |
| **test**   | 3.11, 3.12    | `pytest` 含覆盖率（排除实时测试），上传 XML 报告         |
| **security** | 3.12        | `pip-audit --strict --desc` 检查依赖漏洞                 |
| **build**  | 3.12          | `uv build` — 生成 sdist + wheel，上传为构建产物          |

任务按顺序执行：test 依赖 lint，build 依赖 test + security。

### Docker 构建（`.github/workflows/docker.yml`）

| 任务             | 说明                                                         |
| ---------------- | ------------------------------------------------------------ |
| **docker-build** | 构建 Docker 镜像（不推送），使用 BuildKit 层缓存             |

两个工作流均使用 `concurrency` 分组，在新推送时自动取消正在进行的运行。

---

## 8. 安全加固

### Bash 工具默认禁用

`enable_bash` 设置在 `config-example.yaml` 和代码（`config.py`）中默认为 `false`。除非显式启用，否则 Agent 无法执行任意 Shell 命令：

```yaml
tools:
  enable_bash: false  # 默认值 — 仅在确实需要时才启用
```

### 非 root 容器

Dockerfile 创建了专用的 `agent` 用户和用户组：
```dockerfile
RUN groupadd --system agent && \
    useradd --system --gid agent --create-home --home-dir /home/agent agent
USER agent
```

Agent 进程、Playwright 浏览器数据、工作目录和日志均归属于该非 root 用户。

### 密钥不打入镜像

`.dockerignore` 排除了以下文件：
- `.env`、`.env.*` — 包含 API Key 的环境变量文件
- `config.yaml` — 可能包含 `api_key`
- `mcp.json` — 可能包含 MCP 工具凭据

密钥在运行时通过环境变量或挂载的配置卷（只读）注入。

### 文件系统权限

```bash
# 限制工作目录权限
mkdir -p /app/workspace
chown agent:agent /app/workspace
chmod 750 /app/workspace

# 限制配置目录权限
chmod 700 /etc/agent
chmod 600 /etc/agent/*.yaml
```

---

## 9. 资源限制

### CPU 与内存

所有 Docker Compose 服务均施加相同的限制：

```yaml
deploy:
  resources:
    limits:
      cpus: "2"        # 最多 2 个 CPU 核心
      memory: 2G       # 最多 2GB 内存
    reservations:
      cpus: "0.5"      # 保证至少 0.5 核
      memory: 512M     # 保证至少 512MB
```

### 磁盘

临时文件通过 tmpfs 进行约束：

```yaml
tmpfs:
  - /tmp:size=1G       # 临时文件最多 1GB
```

日志存储在命名 Docker 卷中（`agent-logs`、`mcp-logs`、`acp-logs`），以便在容器重启后持久保留。

---

## 10. Kubernetes 部署

健康检查端点可直接映射为 K8s 探针：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bps-stat-agent
spec:
  template:
    spec:
      containers:
        - name: agent
          image: bps-stat-agent:latest
          ports:
            - containerPort: 8080
              name: health
          livenessProbe:
            httpGet:
              path: /health
              port: health
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: health
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: 500m
              memory: 512Mi
          securityContext:
            runAsNonRoot: true
            runAsUser: 999
            readOnlyRootFilesystem: false  # Playwright needs writable dirs
          env:
            - name: ANTHROPIC_AUTH_TOKEN
              valueFrom:
                secretKeyRef:
                  name: agent-secrets
                  key: anthropic-token
```

如需 Prometheus 指标抓取，添加标准注解：

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

---

## 11. 升级方向

以下领域是当前基础设施之外的未来改进方向：

### 高级上下文管理
- 引入分布式文件系统，实现上下文的统一持久化管理和备份
- 使用更精确的 Token 计算方法
- 丰富消息压缩策略（保留最近 N 条、固定元信息、召回系统等）

### 模型回退机制
- 建立包含多个账号和提供商的模型池
- 引入自动健康检测、故障节点移除、熔断等策略
- 跨提供商自动回退（如 Anthropic → OpenAI）

### 模型幻觉检测
- 对工具调用的输入参数进行安全性检查
- 对工具调用结果进行反思，验证其合理性

---

## 12. 生产环境检查清单

### 首次部署前

- [ ] 在 `.env` 或 K8s Secrets 中设置 LLM API Key
- [ ] 如需访问 BPS 数据，设置 BPS API Key
- [ ] 复制并自定义 `config-example.yaml` → `config.yaml`
- [ ] 确认 `enable_bash: false`，除非确实需要
- [ ] 构建 Docker 镜像：`make docker-build`
- [ ] 运行测试：`make test`

### 可观测性

- [ ] 生产环境设置 `logging.json_output: true`
- [ ] 如使用 Prometheus，安装指标扩展：`pip install bps-stat-agent[metrics]`
- [ ] 如使用 OpenTelemetry，安装追踪扩展：`pip install bps-stat-agent[tracing]`
- [ ] 配置 Prometheus 抓取目标，指向 8080 端口的 `/metrics`
- [ ] 如使用分布式追踪，配置追踪导出器（`otlp`）和端点

### 容器安全

- [ ] 确认容器以非 root 用户运行（`USER agent`）
- [ ] 密钥通过环境变量或挂载卷注入，不打入镜像
- [ ] 配置卷以只读方式挂载（`:ro`）
- [ ] `.dockerignore` 排除了 `.env`、`config.yaml`、`mcp.json`

### 资源限制

- [ ] 已设置 CPU 和内存限制（默认：2 CPU、2GB）
- [ ] 已为 `/tmp` 配置 tmpfs（默认：1GB）
- [ ] 已配置日志卷以实现持久化

### CI/CD

- [ ] GitHub Actions CI 通过（lint、test、security、build）
- [ ] Docker 构建工作流通过
- [ ] 覆盖率报告已上传

### Kubernetes（如适用）

- [ ] 存活探针 → `/health`
- [ ] 就绪探针 → `/ready`
- [ ] 密钥存储在 K8s Secret 对象中
- [ ] 已配置资源请求和限制
- [ ] 安全上下文中设置 `runAsNonRoot: true`
