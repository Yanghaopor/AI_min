# AIWife - 智能AI伴侣系统

## 项目概述

AIWife是一个基于Python和PyQt5开发的智能AI伴侣系统，集成了大语言模型、MCP协议、持久化命令行、时间管理等功能。系统设计为一个具有独立人格的AI助手，能够自主执行任务、管理时间、调用外部服务，并提供友好的图形用户界面。

### 核心特性

- 🤖 **智能AI对话**: 基于DeepSeek-V3模型的自然语言交互
- 🔧 **MCP协议集成**: 支持Model Context Protocol，可扩展外部服务
- 🚄 **12306火车票服务**: 集成12306-mcp，支持车票查询和预订
- ⏰ **时间管理系统**: 支持定时提醒和任务调度
- 💻 **持久化命令行**: 提供持久化的CMD控制台
- 🎨 **现代化GUI**: 基于PyQt5的透明窗口界面
- 🔄 **多线程架构**: 异步处理，响应迅速

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AIWife 系统架构                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   GUI层     │    │   AI层      │    │  System层   │     │
│  │  (PyQt5)    │◄──►│ (AIWife)    │◄──►│ (MorSystem) │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  界面管理   │    │  对话管理   │    │  工具管理   │     │
│  │  事件处理   │    │  记忆存储   │    │  时间管理   │     │
│  │  用户交互   │    │  上下文管理 │    │  CMD控制台  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │           │
│         └───────────────────┼───────────────────┘           │
│                             ▼                               │
│                    ┌─────────────────┐                     │
│                    │   MCP集成层     │                     │
│                    │ (mcp_integration)│                     │
│                    └─────────────────┘                     │
│                             │                               │
│                             ▼                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ 12306-mcp   │    │ 其他MCP服务 │    │  文件系统   │     │
│  │ (火车票)    │    │ (可扩展)    │    │  网络服务   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件说明

#### 1. GUI层 (Main.py)
- **ChatGUI**: 主窗口界面，提供聊天界面和用户交互
- **MessageBroker**: 线程间通信的信号代理
- **透明窗口**: 支持置顶显示的现代化界面

#### 2. AI层 (AIchat.py)
- **AIWife类**: AI对话核心，管理API调用和对话历史
- **支持多种模型**: 默认使用DeepSeek-V3
- **上下文管理**: 维护对话历史和系统提示

#### 3. System层 (MorMain.py)
- **MorSystem类**: 系统核心，管理所有工具和服务
- **CMD控制台**: 持久化的命令行环境
- **时间管理**: 定时提醒和任务调度
- **MCP集成**: 统一管理MCP服务

#### 4. MCP集成层
- **mcp_integration.py**: MCP服务管理器
- **mcp_client.py**: MCP协议客户端
- **mcp_manager.py**: AI友好的管理接口

## 安装指南

### 系统要求

- Python 3.8+
- Windows 10/11 (主要支持)
- 网络连接 (用于AI API调用)

### 1. 克隆项目

```bash
git clone <repository-url>
cd AiWife
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- PyQt5 (GUI框架)
- requests (HTTP请求)
- 其他标准库

### 3. 配置API密钥

编辑 `Key.txt` 文件，添加您的AI API密钥：

```
your_api_key_here
```

### 4. 启动系统

```bash
python Main.py
```

## MCP功能配置

### MCP服务安装

大部分MCP服务只需要在配置文件中添加即可，无需手动安装。

#### 1. 编辑MCP配置文件

编辑 `MCP/MCP/MCP.json` 文件，添加您需要的MCP服务：

```json
[
    {
        "mcpServers": {
            "12306-mcp": {
                "command": "npx",
                "args": ["-y", "12306-mcp"],
                "description": "12306火车票查询和预订服务"
            },
            "playwright": {
                "url": "http://localhost:8931/sse",
                "description": "浏览器自动化服务"
            },
            "filesystem": {
                "url": "http://localhost:8080",
                "description": "文件系统操作服务"
            }
        }
    }
]
```

#### 2. 服务类型说明

**命令行服务** (如12306-mcp):
```json
{
    "command": "npx",
    "args": ["-y", "service-name"],
    "description": "服务描述"
}
```

**HTTP服务** (如playwright):
```json
{
    "url": "http://localhost:port/path",
    "description": "服务描述"
}
```

#### 3. 自动安装

系统启动时会自动：
- 检测配置文件中的服务
- 尝试连接和启动服务
- 缓存可用工具列表

### 12306火车票服务 (特殊说明)

12306-mcp是一个需要npm安装的服务，但系统会自动处理：

```bash
# 系统会自动执行以下命令
npx -y 12306-mcp
```

无需手动安装，只需在MCP.json中配置即可。

### 常用MCP服务列表

以下是一些常用的MCP服务，您可以直接添加到配置文件中：

#### 交通服务
- **12306-mcp**: 火车票查询和预订
- **flight-search**: 航班查询
- **public-transport**: 公共交通信息

#### 工具服务
- **playwright**: 浏览器自动化
- **filesystem**: 文件系统操作
- **git**: Git版本控制
- **docker**: Docker容器管理

#### 数据服务
- **weather**: 天气查询
- **news**: 新闻资讯
- **calendar**: 日历管理
- **email**: 邮件处理

#### 配置示例

```json
{
    "mcpServers": {
        "12306-mcp": {
            "command": "npx",
            "args": ["-y", "12306-mcp"],
            "description": "火车票查询服务"
        },
        "playwright": {
            "url": "http://localhost:8931/sse",
            "description": "浏览器自动化"
        },
        "weather": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-weather"],
            "description": "天气查询服务"
        }
    }
}
```

### 验证MCP服务

运行测试脚本验证MCP功能：

```bash
python query_tickets.py
```

## 使用指南

### 基础对话

启动系统后，您可以直接与AI对话：

```
用户: 你好
AI: 你好主人，我是Nike，有什么可以帮助您的吗？
```

### 车票查询

AI会自动调用12306-mcp服务：

```
用户: 帮我查询明天从北京到上海的车票
AI: 好的，我来帮您查询明天从北京到上海的车票。
MCP{12306-mcp:get-current-date:{}}
MCP{12306-mcp:get-station-code-by-names:{"stationNames":"北京|上海"}}
MCP{12306-mcp:get-tickets:{"date":"2025-07-21","fromStation":"BJP","toStation":"SHH","trainFilterFlags":"","sortFlag":"startTime","sortReverse":false,"limitedNum":5}}
```

### 时间管理

AI可以设置定时提醒：

```
用户: 30分钟后提醒我开会
AI: Time{30分钟后提醒您开会,1800}
```

### 系统命令

AI可以执行系统命令：

```
用户: 查看当前目录文件
AI: Cmd{dir}
```

## 扩展开发

### 添加新的MCP服务

#### 1. 使用现有MCP服务 (推荐)

大部分情况下，您只需要在 `MCP/MCP/MCP.json` 中添加配置即可：

```json
{
    "service-name": {
        "command": "npx",
        "args": ["-y", "service-name"],
        "description": "服务描述"
    }
}
```

或者对于HTTP服务：

```json
{
    "service-name": {
        "url": "http://localhost:port/path",
        "description": "服务描述"
    }
}
```

#### 2. 创建自定义MCP服务器 (高级)

如果您需要创建自己的MCP服务，参考 `12306-mcp` 目录结构：

```
your-mcp-service/
├── package.json
├── src/
│   ├── index.ts
│   └── types.ts
├── build/
└── README.md
```

在 `src/index.ts` 中实现MCP服务器：

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

const server = new McpServer({
    name: 'your-service',
    version: '1.0.0'
});

// 注册工具
server.setRequestHandler('tools/list', async () => {
    return {
        tools: [
            {
                name: 'your_tool',
                description: '工具描述',
                inputSchema: {
                    type: 'object',
                    properties: {
                        // 参数定义
                    }
                }
            }
        ]
    };
});

// 处理工具调用
server.setRequestHandler('tools/call', async (request) => {
    const { name, arguments: args } = request.params;
    
    if (name === 'your_tool') {
        // 实现工具逻辑
        return {
            content: [
                {
                    type: 'text',
                    text: '工具执行结果'
                }
            ]
        };
    }
});
```

#### 3. 配置到AIWife

在 `MCP/MCP/MCP.json` 中添加配置：

```json
{
    "your-service": {
        "command": "node",
        "args": ["path/to/your-service/build/index.js"],
        "description": "您的MCP服务描述"
    }
}
```

#### 4. 更新系统提示

在 `System_prompt.txt` 中添加新服务的使用说明：

```
# 您的MCP服务
1. 服务器名称：your-service
2. 功能：服务功能描述
3. 可用工具：
   - your_tool: 工具描述
4. 使用示例：
   MCP{your-service:your_tool:{"param": "value"}}
```

### 扩展AI功能

#### 1. 添加新的工具类型

在 `MorMain.py` 中添加新的工具处理：

```python
def process_command(self, command: str, command_type: str = "Rcte"):
    if command_type == "YourTool":
        return self._execute_your_tool(command)
    # ... 其他工具处理
```

#### 2. 扩展GUI功能

在 `Main.py` 中添加新的界面元素：

```python
def init_ui(self):
    # 添加新的界面组件
    self.your_widget = QWidget()
    # ... 界面初始化代码
```

### 数据库扩展

系统包含SQL目录下的记忆管理系统：

- `memory_database.py`: 数据库操作
- `knowledge_manager.py`: 知识管理
- `memory_integration.py`: 记忆集成

可以扩展这些模块来支持更多数据类型和查询功能。

## 开发工具

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 测试脚本

- `query_tickets.py`: 测试12306-mcp功能
- `tsety/test_mcp_integration.py`: 测试MCP集成
- `SQL/standalone_test.py`: 测试记忆系统

### 配置文件

- `Init.txt`: 系统初始化配置
- `System_prompt.txt`: AI系统提示词
- `Key.txt`: API密钥配置
- `MCP/MCP/MCP.json`: MCP服务器配置

## 故障排除

### 常见问题

#### 1. MCP服务连接失败

**症状**: AI无法调用MCP工具
**解决**: 
- 检查 `MCP/MCP/MCP.json` 配置文件是否正确
- 确认服务配置格式正确（command/args 或 url）
- 对于命令行服务，确保系统已安装Node.js
- 对于HTTP服务，确保服务正在运行

#### 2. API调用失败

**症状**: AI无法回复
**解决**:
- 检查API密钥是否正确
- 验证网络连接
- 确认API配额是否充足

#### 3. GUI显示异常

**症状**: 界面显示不正常
**解决**:
- 检查PyQt5安装
- 验证显示器设置
- 重启应用程序

### 日志文件

系统日志保存在 `SystemLog.log` 文件中，包含：
- 系统启动信息
- 错误和警告
- CMD命令执行记录
- MCP调用日志

## 贡献指南

### 代码规范

- 使用Python类型注解
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 编写单元测试

### 提交规范

- 使用清晰的提交信息
- 一个提交只包含一个功能或修复
- 在提交前运行测试

### 问题报告

报告问题时请包含：
- 操作系统版本
- Python版本
- 错误日志
- 重现步骤

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

---

**AIWife** - 让AI成为您的智能伴侣 🚀 
