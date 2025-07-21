# AI_main

这是一个AI桌宠项目，使其成为智能的AI桌宠Agent\
此桌宠集成了基本的
1. 脚本集成
2. MCP集成可自主扩展
3. 记忆模块集成（递归式记忆系统）
4. 其它图形扩展

# 项目结构
AiWife/
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
