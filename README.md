# AI_main

这是一个AI桌宠项目，使其成为智能的AI桌宠Agent\
此桌宠集成了基本的
1. 脚本集成
2. MCP集成可自主扩展
3. 记忆模块集成（递归式记忆系统）
4. 其它图形扩展

# 项目结构
AiWife/\
├── Main.py                # 主程序入口，PyQt5桌宠主逻辑\
├── MorMain.py             # 系统核心，信号/线程/数据库/命令处理\
├── AIchat.py              # AI对话与API调用封装\
├── System_prompt.txt      # AI系统提示词与行为约束\
├── memory.db              # 缓存/短期记忆数据库\
├── Key.txt                # API Key、模型、URL配置\
├── requirements.txt       # 依赖包列表\
├── start_with_monitor.py  # 启动主程序+记忆监控的脚本\
├── MEMORY_MONITOR_README.md # 记忆监控说明文档\
├── SQL/
│   ├── memory_monitor.py      # 记忆监控与多级记忆管理\
│   ├── Read_0.py              # 读取缓存记忆（memory.db）\
│   ├── Read_1.py              # 读取摘要记忆（memory_summary.db）\
│   ├── Read_2.py              # 读取长期记忆（long_memory.db）\
│   ├── print_memory_db.py     # 打印memory.db内容\
│   ├── print_all_summaries.py # 打印memory_summary内容\
│   ├── print_long_memory.py   # 打印long_memory内容\
│   ├── clear_all_databases.py # 清空所有记忆数据库\
│   ├── ...（其它测试/维护脚本）\
│   ├── memory_summary.db      # 摘要记忆数据库\
│   ├── long_memory.db         # 长期记忆数据库\
├── MCP/                   # MCP协议相关实现\
├── 12306-mcp/             # 12306火车票MCP服务\
├── core/                  # 其它核心模块\
├── 日志/                  # 日志与Linux相关脚本\
├── gif/                   # 动画资源\
└── ...（其它文件/目录）

# 主要文件介绍
1. Main.py
PyQt5桌宠主入口，负责UI、主线程、信号与AI交互。
2. MorMain.py
系统核心，负责数据库初始化、消息分发、命令执行、日志、CMD/MCP/Time等工具调用。
3. AIchat.py
封装AI对话、API请求、上下文管理，支持OpenAI/DashScope等API。
4. System_prompt.txt
详细定义AI角色、工具调用规范、记忆读取方式、MCP协议用法、行为约束等。
5. SQL/memory_monitor.py
记忆监控守护进程，负责多级记忆的自动摘要、升级、清理、AI总结。
6. SQL/Read_0.py / Read_1.py / Read_2.py
分别读取缓存、摘要、长期记忆数据库，输出JSON供AI分析。
SQL/clear_all_databases.py
一键清空所有记忆数据库并重置自增ID。
7. Key.txt
存储API Key、模型名、API URL等敏感配置。

# 记忆系统设计架构
## 缓存记忆：每次对话/工具调用/提醒实时写入，满16k或50条自动AI摘要，升级为摘要记忆。
## 摘要记忆：缓存摘要满50条，自动AI进一步精炼，升级为长期记忆。
## 长期记忆：长期记忆满50条，AI全局总结，清空原有内容，仅保留AI总结。
## 重要记忆：可由AI/用户手动标记，随时可被主AI读取分析。

# MCP扩展与内部工具调用
MCP（Model Context Protocol）扩展\
统一接口：所有外部服务（如12306、文件系统、网络爬虫）都可通过MCP协议暴露为AI可调用的“工具”。\
调用格式：\
MCP{server:tool:{"参数":"值"}}\
典型流程：\
查询MCP服务器列表：MCP{mcp_list_servers()}\
查询工具列表：MCP{mcp_list_tools()}\
调用具体服务：如火车票查询、文件操作等\
安全隔离：每个MCP服务独立进程，AI只能调用允许的接口。\
内部工具调用\
Rcte工具：\
直接调用本地Python脚本或命令，格式为：\
Rcte{import os; os.system("py SQL/Read_0.py")}\
Time工具：\
定时提醒，格式为：\
Time{提醒内容, 秒数, 次数}\
Cmd工具：\
持久化本地命令行线程，适合文件操作、SSH等。\
调用规范：\
工具调用必须顶格，不能有自然语言混杂\
一次对话只能调用一种类型的工具\
MCP、Rcte、Time、Cmd不能混用\
MCP参数必须为JSON格式，且用双引号
