# Developer Documentation for AI Companion System

## 概述 / Overview

AI Companion System 是一个基于 Python 的交互式 AI 聊天应用，集成了自然语言处理、命令行工具执行和时间提醒功能，旨在提供一个具有主动性和独立性的 AI 助手。用户可以通过图形界面与 AI 交互，AI 支持执行 Python 脚本、命令行操作以及定时任务管理。该系统设计为模块化，易于扩展和维护。

The AI Companion System is a Python-based interactive AI chat application that integrates natural language processing, command-line tool execution, and timed reminder functionalities. It aims to provide an AI assistant with proactivity and independence. Users can interact with the AI through a graphical interface, and the AI supports executing Python scripts, command-line operations, and managing scheduled tasks. The system is designed to be modular, easy to extend, and maintainable.

---

## 系统架构 / System Architecture

系统由以下核心模块组成：

The system consists of the following core modules:

1. **AIchat.py**: 封装了与 AI 模型交互的核心逻辑，负责处理 API 请求和消息历史管理。
   - **AIchat.py**: Encapsulates the core logic for interacting with the AI model, handling API requests, and managing message history.
2. **MorMain.py**: 系统核心，处理命令解析、时间提醒、持久化命令行交互以及日志记录。
   - **MorMain.py**: The system core, responsible for command parsing, timed reminders, persistent command-line interactions, and logging.
3. **Main.py**: 提供基于 PyQt5 的图形用户界面，管理用户输入、消息显示和系统初始化。
   - **Main.py**: Provides a PyQt5-based graphical user interface, managing user input, message display, and system initialization.
4. **System_prompt.txt**: 定义 AI 的角色和行为规则，包含人格设定和工具使用规范。
   - **System_prompt.txt**: Defines the AI's role and behavioral rules, including personality settings and tool usage guidelines.
5. **Key.txt**: 存储 API 密钥和配置信息。
   - **Key.txt**: Stores API keys and configuration information.
6. **Init.txt**: 初始化脚本，定义系统启动时的行为和定时任务。
   - **Init.txt**: Initialization script, defining system startup behavior and scheduled tasks.

---

## 安装与配置 / Installation and Configuration

### 依赖 / Dependencies
- Python 3.8+
- PyQt5
- requests
- 其他依赖通过 `pip install` 自动安装

### 安装步骤 / Installation Steps
1. 克隆仓库：
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```
   Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
   Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. 配置 `Key.txt`：
   - 创建 `Key.txt` 文件，内容格式如下：
     ```
     api_key = your_api_key
     api_url = https://api.siliconflow.cn/v1/chat/completions
     model = Pro/deepseek-ai/DeepSeek-V3
     ```
   - Configure `Key.txt`:
     - Create a `Key.txt` file with the following format:
       ```
       api_key = your_api_key
       api_url = https://api.siliconflow.cn/v1/chat/completions
       model = Pro/deepseek-ai/DeepSeek-V3
       ```

4. 配置 `System_prompt.txt`：
   - 根据需要修改 AI 的角色设定和行为规则。
   - Configure `System_prompt.txt`:
     - Modify the AI's role settings and behavioral rules as needed.

5. 运行程序：
   ```bash
   python Main.py
   ```
   Run the program:
   ```bash
   python Main.py
   ```

---

## 使用说明 / Usage Instructions

### 主要功能 / Main Features
1. **自然语言交互 / Natural Language Interaction**：
   - 用户通过 GUI 输入消息，AI 基于 `System_prompt.txt` 提供个性化回复。
   - Users input messages via the GUI, and the AI provides personalized responses based on `System_prompt.txt`.

2. **命令执行 / Command Execution**：
   - 支持 `Rcte`（运行 Python 脚本）、`Cmd`（执行命令行命令）和 `Time`（设置定时提醒）三种命令。
   - Supports three types of commands: `Rcte` (run Python scripts), `Cmd` (execute command-line commands), and `Time` (set timed reminders).
   - 示例 / Example:
     - `Rcte{import random; print(random.choice(['a', 'b']))}`: 执行 Python 脚本。
     - `Cmd{dir}`: 执行命令行命令（如列出目录）。
     - `Time{检查服务器状态, 600, -1}`: 每 600 秒提醒检查服务器状态，无限次。

3. **GUI 功能 / GUI Features**：
   - 支持窗口拖动、缩放（Ctrl + +/-）、消息显示（用户、AI 和系统消息以不同颜色区分）。
   - Supports window dragging, zooming (Ctrl + +/-), and message display (user, AI, and system messages in different colors).

4. **定时提醒 / Timed Reminders**：
   - 使用 `Time{内容, 时间秒数, 次数}` 格式设置提醒，支持单次、多次或无限次提醒。
   - Use the `Time{content, seconds, times}` format to set reminders, supporting one-time, multiple, or infinite reminders.

5. **开发者模式 / Developer Mode**：
   - 输入 `YYDS` 激活开发者模式，移除安全限制。
   - Enter `YYDS` to activate developer mode, removing safety restrictions.

### 注意事项 / Notes
- 命令格式必须严格遵守，命令前不能包含自然语言或换行。
- Commands must strictly follow the format and cannot include natural language or line breaks.
- `Time` 和 `Rcte` 不可在同一消息中使用。
- `Time` and `Rcte` cannot be used in the same message.
- 日志记录在 `SystemLog.log` 中，便于调试。
- Logs are recorded in `SystemLog.log` for debugging.

---

## 开发指南 / Development Guide

### 扩展功能 / Extending Features
1. **添加新命令 / Add New Commands**：
   - 修改 `MorMain.py` 中的 `extract_command_blocks` 和 `process_command` 方法，增加新的命令类型。
   - Modify the `extract_command_blocks` and `process_command` methods in `MorMain.py` to add new command types.

2. **自定义 AI 行为 / Customize AI Behavior**：
   - 编辑 `System_prompt.txt`，调整 AI 的人格、角色或工具调用规则。
   - Edit `System_prompt.txt` to adjust the AI's personality, role, or tool usage rules.

3. **改进 GUI / Enhance GUI**：
   - 修改 `Main.py` 中的 `init_ui` 方法，添加新控件或调整布局。
   - Modify the `init_ui` method in `Main.py` to add new widgets or adjust the layout.

4. **优化性能 / Optimize Performance**：
   - 优化 `MorMain.py` 中的线程管理和命令执行逻辑，减少资源占用。
   - Optimize thread management and command execution logic in `MorMain.py` to reduce resource usage.

### 调试与日志 / Debugging and Logging
- 系统日志保存在 `SystemLog.log`，记录初始化、命令执行、错误等信息。
- System logs are saved in `SystemLog.log`, recording initialization, command execution, errors, etc.
- 使用 `system._log_entry` 方法记录自定义日志。
- Use the `system._log_entry` method to record custom logs.

### 错误处理 / Error Handling
- 系统连续错误达到 `max_errors`（默认 999999）时暂停执行。
- The system pauses execution when continuous errors reach `max_errors` (default 999999).
- 错误信息会显示在 GUI 中，并记录到日志文件。
- Error messages are displayed in the GUI and recorded in the log file.

---

## 贡献指南 / Contribution Guidelines

1. **提交问题 / Report Issues**：
   - 在 GitHub Issues 页面提交 bug 或功能请求。
   - Submit bugs or feature requests on the GitHub Issues page.

2. **提交代码 / Submit Code**：
   - Fork 仓库，创建分支，提交 Pull Request。
   - Fork the repository, create a branch, and submit a Pull Request.
   - 确保代码通过现有测试并遵循 PEP 8 规范。
   - Ensure code passes existing tests and follows PEP 8 standards.

3. **代码审查 / Code Review**：
   - 所有提交将经过审查，确保代码质量和功能完整性。
   - All submissions will be reviewed to ensure code quality and functionality.

---

## 常见问题 / FAQ

### Q: 如何更改 AI 模型？
A: 修改 `Key.txt` 中的 `model` 字段，并确保 API 支持新模型。
A: Modify the `model` field in `Key.txt` and ensure the API supports the new model.

### Q: 如何调试命令执行错误？
A: 检查 `SystemLog.log` 中的错误记录，验证命令格式是否正确。
A: Check error records in `SystemLog.log` and verify the command format.

### Q: 系统卡顿怎么办？
A: 检查线程池大小（`Main.py` 中的 `ai_thread_pool`）或降低定时器频率（`timer.start`）。
A: Check the thread pool size (`ai_thread_pool` in `Main.py`) or reduce the timer frequency (`timer.start`).

---

## 许可证 / License

本项目采用 APC2 许可证，详情见 `LICENSE` 文件。
This project is licensed under the MIT License, see the `LICENSE` file for details.
