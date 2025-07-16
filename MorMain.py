import subprocess
import sys
import threading
import time
import os
import queue
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict, Any
from AIchat import AIWife

class MorSystem:
    """重构后的System处理器，支持交互式CMD和实时消息反馈"""
    
    def __init__(self, ai_instance: AIWife, log_file: str = "SystemLog.log"):
        self.ai = ai_instance
        self.error_count = 0
        self.max_errors = 999999
        self.lock = threading.Lock()
        self.log_file = log_file
        self.reminder_queue = queue.Queue()
        self.running = True
        self.message_queue = queue.Queue()
        self.cmd_message_queue = queue.Queue()  # 专用于CMD交互消息的队列
        
        # CMD控制台相关属性
        self.cmd_process = None
        self.cmd_thread = None
        self.cmd_output_queue = queue.Queue()
        self.cmd_input_queue = queue.Queue()
        self.cmd_working_directory = os.getcwd()
        self.cmd_history = []
        self.cmd_active = False
        self.cmd_encoding = 'utf-8'
        self.last_cmd_output = ""  # 记录最后一条CMD输出
        self.cmd_waiting_input = False  # 标记CMD是否在等待输入
        self.last_cmd_flush_time = time.time()  # 上次发送CMD消息的时间
        self.cmd_buffer = []  # 用于存储10秒内的CMD消息

        self._init_log_file()
        self._start_reminder_checker()
        self._init_cmd_console()
        self._start_cmd_monitor()  # 启动CMD监控线程
    
    def _init_log_file(self):
        """初始化日志文件"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n=== System Session Started at {datetime.now()} ===\n")
    
    def _log_entry(self, entry_type: str, content: str, source: str = "SYSTEM"):
        """写入日志条目"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{entry_type}] [{source}] {content}\n"
        
        with self.lock:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_msg)
    
    def _init_cmd_console(self):
        """初始化持久化CMD控制台"""
        encoding = self.cmd_encoding
        
        try:
            if sys.platform == "win32":
                # Windows下设置UTF-8编码
                self.cmd_process = subprocess.Popen(
                    ["cmd.exe"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,  # 分离stderr以便更好处理错误
                    cwd=self.cmd_working_directory,
                    bufsize=0,  # 无缓冲
                    text=True,
                    encoding=encoding,
                    errors='replace'
                )
            else:
                # Linux/Mac使用bash
                self.cmd_process = subprocess.Popen(
                    ["/bin/bash", "-i"],  # 交互模式
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.cmd_working_directory,
                    bufsize=0,
                    text=True,
                    encoding=encoding,
                    errors='replace'
                )
            
            # 启动线程读取CMD输出
            self.cmd_active = True
            self.cmd_thread = threading.Thread(target=self._read_cmd_output)
            self.cmd_thread.daemon = True
            self.cmd_thread.start()
            
            self._log_entry("DEBUG", "CMD控制台初始化完成", "CMD")
        except Exception as e:
            self._log_entry("ERROR", f"初始化CMD控制台失败: {str(e)}", "CMD")
            self.cmd_active = False
    
    def _start_cmd_monitor(self):
        """启动CMD监控线程，实时处理交互需求，但每10秒整合一次输出"""
        def monitor():
            while self.cmd_active:
                try:
                    current_time = time.time()
                    # 每10秒检查一次或等待输入时立即处理
                    flush_interval = 10  # 10秒发送一次
                    
                    # 检查是否有新输出
                    if not self.cmd_output_queue.empty():
                        output = self.cmd_output_queue.get_nowait()
                        self.cmd_buffer.append(output)
                        
                        # 检测是否需要用户输入
                        if re.search(r'\[Y/n\]|\? \(yes/no\)|continue\?|confirm:', output, re.IGNORECASE):
                            self.cmd_waiting_input = True
                    
                    # 处理缓冲区：每10秒发送一次或需要立即处理
                    if (current_time - self.last_cmd_flush_time >= flush_interval and self.cmd_buffer) or self.cmd_waiting_input:
                        combined_message = "\n".join(self.cmd_buffer)
                        
                        if self.cmd_waiting_input:
                            self.cmd_message_queue.put(f"[CMD等待输入] {combined_message}")
                        else:
                            self.cmd_message_queue.put(f"[CMD输出] {combined_message}")
                        
                        self.cmd_buffer = []  # 清空缓冲区
                        self.last_cmd_flush_time = current_time
                        self.cmd_waiting_input = False  # 重置等待输入标志
                    
                    time.sleep(0.3)  # 降低CPU使用率
                except Exception as e:
                    self._log_entry("ERROR", f"CMD监控线程错误: {str(e)}", "CMD")
                    time.sleep(1)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def _read_cmd_output(self):
        """读取CMD控制台输出（分离stdout和stderr）"""
        self._log_entry("DEBUG", "CMD输出读取线程启动", "CMD")
        
        def read_stream(stream, stream_type):
            """读取指定流的内容"""
            while self.cmd_active:
                try:
                    line = stream.readline()
                    if line:
                        formatted_line = f"[{stream_type}] {line.strip()}"
                        self.cmd_output_queue.put(formatted_line)
                except Exception as e:
                    self._log_entry("ERROR", f"读取CMD{stream_type}错误: {str(e)}", "CMD")
        
        # 启动单独的线程读取stdout和stderr
        threading.Thread(target=read_stream, args=(self.cmd_process.stdout, "STDOUT"), daemon=True).start()
        threading.Thread(target=read_stream, args=(self.cmd_process.stderr, "STDERR"), daemon=True).start()
    
    def _send_cmd_command(self, command: str):
        """向CMD控制台发送命令"""
        if self.cmd_process and self.cmd_process.stdin:
            try:
                self.cmd_process.stdin.write(command + "\n")
                self.cmd_process.stdin.flush()
                self.cmd_history.append(command.strip())
                self._log_entry("DEBUG", f"发送CMD命令: {command.strip()}", "CMD")
                self.cmd_waiting_input = False  # 重置等待输入标志
            except Exception as e:
                self._log_entry("ERROR", f"发送CMD命令失败: {str(e)}", "CMD")
    
    def _execute_code(self, code: str) -> Tuple[str, bool]:
        """执行代码并返回结果和是否成功"""
        try:
            with open("temp_execution.py", "w", encoding='utf-8') as f:
                f.write(code)
            
            result = subprocess.run(
                [sys.executable, "temp_execution.py"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            
            os.remove("temp_execution.py")
            
            if result.returncode == 0:
                return result.stdout.strip(), True
            else:
                return f"执行错误:\n{result.stderr}", False
        except Exception as e:
            return f"执行异常: {str(e)}", False
    
    def _install_dependencies(self, packages: list) -> Tuple[str, bool]:
        """安装Python依赖包"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install"] + packages,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                return "依赖安装成功", True
            else:
                return f"安装失败:\n{result.stderr}", False
        except Exception as e:
            return f"安装异常: {str(e)}", False
    
    def _set_reminder(self, content: str, delay_seconds: int, times: int = 1):
        """设置时间提醒并记录日志"""
        reminder_time = datetime.now() + timedelta(seconds=delay_seconds)
        time_str = reminder_time.strftime("%Y-%m-%d %H:%M:%S")
        
        if times == 0 or times == -1:  # 无限次提醒
            log_msg = f"设置提醒: '{content}' 在 {delay_seconds}秒后 ({time_str})，无限次提醒"
            self.reminder_queue.put((reminder_time, content, delay_seconds, -1))
        elif times == 1:  # 单次提醒
            log_msg = f"设置提醒: '{content}' 在 {delay_seconds}秒后 ({time_str})"
            self.reminder_queue.put((reminder_time, content, delay_seconds, 1))
        else:  # 有限次提醒
            log_msg = f"设置提醒: '{content}' 在 {delay_seconds}秒后 ({time_str})，共 {times}次"
            self.reminder_queue.put((reminder_time, content, delay_seconds, times))
            
        self._log_entry("TIME", log_msg, "REMINDER")
        self.message_queue.put(log_msg)
    
    def _start_reminder_checker(self):
        """提醒检查线程，正确处理无限次提醒"""
        def reminder_worker():
            while self.running:
                try:
                    now = datetime.now()
                    temp_queue = queue.Queue()
                    
                    while not self.reminder_queue.empty():
                        item = self.reminder_queue.get()
                        if not item:  # 空项检查
                            continue
                            
                        # 解包元组
                        reminder_time, content, interval, remaining = item
                        
                        if reminder_time <= now:
                            # 触发提醒
                            self._log_entry("REMINDER", f"触发提醒: '{content}'", "REMINDER")
                            self.message_queue.put(f"[System提醒] {content}")
                            
                            # 处理无限次提醒
                            if remaining == -1:  # 无限次提醒
                                next_time = now + timedelta(seconds=interval)
                                temp_queue.put((next_time, content, interval, -1))
                            elif remaining > 1:  # 有限次且还有剩余次数
                                next_time = now + timedelta(seconds=interval)
                                temp_queue.put((next_time, content, interval, remaining - 1))
                            # 剩余次数为1时不重新安排
                        
                        else:
                            temp_queue.put(item)
                    
                    # 更新主队列
                    while not temp_queue.empty():
                        self.reminder_queue.put(temp_queue.get())
                    time.sleep(0.5)
                        
                except Exception as e:
                    self._log_entry("ERROR", f"提醒线程错误: {str(e)}", "SYSTEM")
                    time.sleep(5)
        
        threading.Thread(target=reminder_worker, daemon=True).start()
    
    def execute_cmd_command(self, command: str) -> Tuple[str, bool]:
        """在持久化CMD控制台中执行命令"""
        try:
            self._log_entry("COMMAND", f"执行CMD命令: {command}", "CMD")
            
            if not self.cmd_active or not self.cmd_process:
                self._log_entry("WARNING", "CMD控制台未初始化，尝试重新初始化", "CMD")
                self._init_cmd_console()
                if not self.cmd_active:
                    return "CMD控制台初始化失败", False

            # 发送命令
            self._send_cmd_command(command)
            
            # 等待命令执行完成或需要交互
            start_time = time.time()
            while not self.cmd_waiting_input and time.time() - start_time < 10:
                time.sleep(0.1)
            
            # 如果等待输入，返回特殊标识
            if self.cmd_waiting_input:
                return f"[等待输入] {self.last_cmd_output}", True
            
            # 返回最后输出
            return self.last_cmd_output, True
        except Exception as e:
            error_msg = f"CMD命令执行出错: {str(e)}"
            self._log_entry("ERROR", error_msg, "CMD")
            return error_msg, False
    
    def process_command(self, command: str, command_type: str = "Rcte") -> Tuple[Optional[str], bool]:
        """处理System命令"""
        if self.error_count >= self.max_errors:
            self._log_entry("ERROR", "System错误次数过多，已暂停执行", "SYSTEM")
            return "System错误次数过多，请检查系统状态", False
            
        self._log_entry("COMMAND", f"执行命令: {command}", "SYSTEM")
        
        # 根据命令类型处理
        if command_type == "Cmd":
            result, success = self.execute_cmd_command(command)
            self._log_entry("RESULT", f"CMD结果: {result}", "SYSTEM")
            return result, success
        
        # 安装依赖的指令
        if "pip install" in command:
            packages = []
            for line in command.split('\n'):
                if "pip install" in line:
                    packages.extend(line.replace("pip install", "").strip().split())
            
            if packages:
                result, success = self._install_dependencies(packages)
                self._log_entry("RESULT", f"安装结果: {result}", "SYSTEM")
                if not success:
                    self.error_count += 1
                return result, success
            
        # 执行普通代码
        result, success = self._execute_code(command)
        self._log_entry("RESULT", f"执行结果: {result}", "SYSTEM")
        
        if not success:
            self.error_count += 1
        
        if self.error_count >= self.max_errors:
            self._log_entry("ERROR", "System连续错误达到上限，已暂停执行", "SYSTEM")
            return "System连续错误达到上限，已暂停执行", False
            
        return result, success
        
    def shutdown(self):
        """关闭系统"""
        self.running = False
        self.cmd_active = False
        
        # 关闭CMD进程
        if self.cmd_process:
            try:
                self.cmd_process.stdin.write("exit\n")
                self.cmd_process.stdin.flush()
                time.sleep(0.5)
                self.cmd_process.terminate()
            except Exception as e:
                self._log_entry("ERROR", f"关闭CMD进程失败: {str(e)}", "CMD")
            finally:
                self.cmd_process = None
        
        self._log_entry("SYSTEM", "系统关闭", "SYSTEM")

def extract_command_blocks(message: str) -> Tuple[str, List[Dict]]:
    """
    从消息中提取命令块并清理消息
    返回: (清理后的消息, 命令块列表)
    """
    # 命令类型和对应的起始标记
    command_types = {
        "Rcte": "Rcte{",
        "Time": "Time{",
        "Cmd": "Cmd{"
    }
    
    cleaned_message = message
    commands = []
    
    # 查找所有命令块
    for cmd_type, start_tag in command_types.items():
        start_idx = 0
        while True:
            # 查找命令开始位置
            cmd_start = cleaned_message.find(start_tag, start_idx)
            if cmd_start == -1:
                break
                
            # 查找命令结束位置
            cmd_end = cleaned_message.find("}", cmd_start + len(start_tag))
            if cmd_end == -1:
                break
                
            # 提取命令内容
            cmd_content = cleaned_message[cmd_start + len(start_tag):cmd_end].strip()
            
            # 记录命令
            commands.append({
                "type": cmd_type,
                "content": cmd_content,
                "start": cmd_start,
                "end": cmd_end + 1  # 包含结束大括号
            })
            
            # 从消息中移除命令块
            cleaned_message = cleaned_message[:cmd_start] + cleaned_message[cmd_end + 1:]
            
            # 更新搜索起始位置
            start_idx = cmd_start
    
    return cleaned_message, commands

def process_user_message(user_input: str, ai: AIWife, system: MorSystem) -> str:
    """处理用户消息，支持自然语言中的命令并正确处理执行结果"""
    system._log_entry("USER", f"User input: {user_input}", "USER")
    
    # 优先处理CMD消息
    cmd_processed = False
    cmd_response = ""
    
    # 检查并处理10秒内的CMD消息
    if not system.cmd_message_queue.empty():
        cmd_msg = system.cmd_message_queue.get_nowait()
        system._log_entry("CMD", f"处理CMD消息: {cmd_msg}", "SYSTEM")
        
        # 将CMD消息作为系统消息处理
        system.message_queue.put(cmd_msg)
        
        # 如果需要输入，通知AI
        if "[CMD等待输入]" in cmd_msg:
            ai.chat(cmd_msg)  # 让AI知道需要响应
            cmd_processed = True
            cmd_response = cmd_msg
    
    # 如果有未处理的用户输入
    if user_input and not cmd_processed:
        ai_response = ai.chat(user_input)
        system._log_entry("AI", f"Initial AI response: {ai_response}", "AI")
        
        # 提取并移除命令块
        cleaned_response, commands = extract_command_blocks(ai_response)
        
        # 如果没有命令，直接返回清理后的响应
        if not commands:
            return cleaned_response if not cleaned_response.startswith("NULL") else ""
        
        # 处理所有命令并收集结果
        command_results = []
        for command in commands:
            try:
                if command["type"] == "Time":
                    # 解析时间命令
                    parts = [p.strip() for p in command["content"].split(',')]
                    
                    if len(parts) == 2:
                        content, delay_seconds = parts[0], int(parts[1])
                        times = 1
                    elif len(parts) == 3:
                        content, delay_seconds = parts[0], int(parts[1])
                        times = int(parts[2])
                    else:
                        result = "时间命令格式错误: 应为 Time{内容,秒数[,次数]}"
                        system._log_entry("ERROR", result, "SYSTEM")
                        command_results.append(result)
                        continue
                    
                    # 设置时间提醒
                    system._set_reminder(content, delay_seconds, times)
                    command_results.append("提醒设置成功")
                else:
                    # 执行命令并获取结果
                    result, success = system.process_command(command["content"], command["type"])
                    command_results.append(result)
            except Exception as e:
                error_msg = f"处理{command['type']}命令出错: {str(e)}"
                system._log_entry("ERROR", error_msg, "SYSTEM")
                command_results.append(error_msg)
        
        # 将命令执行结果反馈给AI
        command_feedback = "\n".join(command_results)
        feedback_prompt = f"命令执行结果:\n{command_feedback}\n\n请根据以上结果生成最终响应"
        
        # 将命令执行结果发送给AI
        final_response = ai.chat(feedback_prompt)
        system._log_entry("AI", f"Final AI response: {final_response}", "AI")
        
        # 返回最终响应
        return final_response if not final_response.startswith("NULL") else ""
    
    # 如果只有CMD消息没有用户输入
    return cmd_response if cmd_response else "NULL"