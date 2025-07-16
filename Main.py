import sys
import os
import queue
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QLineEdit, QPushButton, QLabel, QScrollArea, QSizePolicy,
                            QFrame, QGridLayout)
from PyQt5.QtCore import QTimer, Qt, QObject, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QTextCursor, QPalette, QColor, QKeySequence

# 导入核心功能模块
from MorMain import MorSystem, process_user_message
from AIchat import AIWife
from PyQt5.QtGui import QMovie

class MessageBroker(QObject):
    """用于线程间通信的信号代理"""
    system_message = pyqtSignal(str)
    ai_response = pyqtSignal(str)
    user_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    status_update = pyqtSignal(str)

class ChatGUI(QMainWindow):
    def __init__(self, ai, system):
        super().__init__()
        self.ai = ai
        self.system = system
        self.broker = MessageBroker()
        self.base_font_size = 10  # 基础字体大小
        self.base_window_size = QSize(400, 500)  # 基础窗口大小
        self.init_ui()
        self.setup_workers()
        
        # 连接信号
        self.broker.system_message.connect(self.display_system_message)
        self.broker.ai_response.connect(self.display_ai_message)
        self.broker.user_message.connect(self.process_user_input)
        self.broker.error_occurred.connect(self.display_error)
        self.broker.status_update.connect(self.update_status)
        
        # 启动初始化序列
        QTimer.singleShot(100, self.run_init_sequence)
        
        # 初始化完成标志
        self.initialization_complete = False

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("AI Companion System")
        self.setGeometry(500, 100, self.base_window_size.width(), self.base_window_size.height())
        
        # 设置主窗口背景为透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowMinMaxButtonsHint)
        
        # 主布局
        main_widget = QWidget()
        self.main_layout = QGridLayout(main_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)  # 减小整体边距
        self.main_layout.setSpacing(3)  # 减小整体间距
        
        # 设置主部件透明
        main_widget.setAttribute(Qt.WA_TranslucentBackground)
        
        # === 状态栏 - 减小高度 ===
        self.status_label = QLabel("系统正在初始化...")
        self.status_label.setStyleSheet("""
            background-color: rgba(240, 240, 240, 180);
            color: #333;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 9pt;
            min-height: 20px;
            max-height: 20px;
        """)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.main_layout.addWidget(self.status_label, 0, 0, 1, 2)
        
        # === 聊天区域 ===
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Arial", self.base_font_size))
        self.chat_display.setStyleSheet("""
            background-color: white;
            color: #333333;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            padding: 8px;
        """)
        
        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setWidget(self.chat_display)
        chat_scroll.setStyleSheet("background: transparent; border: none;")
        chat_layout.addWidget(chat_scroll)
        
        # 将聊天区域添加到网格布局的第1行第0列
        self.main_layout.addWidget(chat_container, 1, 0, 2, 1)
        
        # === 右上角正方形区域 ===
        self.square_container = QFrame()
        self.square_container.setStyleSheet("""
            background-color: white;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
        """)
        self.square_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                # 创建用于显示GIF的标签
        self.gif_label = QLabel(self.square_container)
        self.gif_label.setAlignment(Qt.AlignCenter)

        # 设置GIF
        gif_path = os.path.join("gif", "01.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setText("GIF未找到")

        # 将GIF标签添加到容器中
        square_layout = QVBoxLayout(self.square_container)
        square_layout.setContentsMargins(0, 0, 0, 0)
        square_layout.addWidget(self.gif_label)
        self.main_layout.addWidget(self.square_container, 1, 1)
        
        # === 输入区域 ===
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(3)  # 减小内部间距
        
        self.user_input = QLineEdit()
        self.user_input.setFont(QFont("Arial", self.base_font_size))
        self.user_input.setStyleSheet("""
            background-color: white;
            color: #333333;
            border: 1px solid #d0d0d0;
            border-radius: 5px;
            padding: 8px;
        """)
        self.user_input.returnPressed.connect(self.send_message)
        
        send_button = QPushButton("发送")
        send_button.setFont(QFont("Arial", self.base_font_size, QFont.Bold))
        send_button.setStyleSheet("""
            background-color: rgba(74, 134, 232, 180);
            color: white;
            padding: 6px 12px;
            border-radius: 3px;
        """)
        send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.user_input)  # 移除了"输入消息:"标签以减少高度
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(send_button)
        input_layout.addLayout(button_layout)
        
        # 将输入区域添加到第3行第0列
        self.main_layout.addWidget(input_container, 3, 0, 1, 1)  # 跨越1列
        
        self.setCentralWidget(main_widget)
        
        # 系统计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_system_messages)
        self.timer.start(500)
        
        self.broker.status_update.emit("系统就绪，等待输入")

    def resizeEvent(self, event):
        """窗口大小改变时调整正方形尺寸"""
        super().resizeEvent(event)
        window_size = self.size()
        square_size = min(window_size.height() * 0.25, window_size.height() * 0.25)
        self.square_container.setFixedSize(int(square_size), int(square_size))

    def keyPressEvent(self, event):
        """处理键盘快捷键"""
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Plus:  # Ctrl + "+" 放大
                self.zoom_in()
            elif event.key() == Qt.Key_Minus:  # Ctrl + "-" 缩小
                self.zoom_out()
        super().keyPressEvent(event)

    def zoom_in(self):
        """放大窗口和字体"""
        self.base_font_size += 1
        self.resize(self.width() * 1.1, self.height() * 1.1)
        self.update_font_sizes()

    def zoom_out(self):
        """缩小窗口和字体"""
        if self.base_font_size > 8:  # 最小字体大小限制
            self.base_font_size -= 1
            self.resize(self.width() * 0.9, self.height() * 0.9)
            self.update_font_sizes()

    def update_font_sizes(self):
        """更新所有控件的字体大小"""
        self.chat_display.setFont(QFont("Arial", self.base_font_size))
        self.user_input.setFont(QFont("Arial", self.base_font_size))
        self.status_label.setStyleSheet(f"""
            background-color: rgba(240, 240, 240, 180);
            color: #333;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: {self.base_font_size-1}pt;
            min-height: 20px;
            max-height: 20px;
        """)

    # 以下方法保持不变...
    def setup_workers(self):
        """设置后台工作线程"""
        self.message_worker = threading.Thread(target=self.handle_system_messages)
        self.message_worker.daemon = True
        self.message_worker.start()
        
        self.ai_thread_pool = []
        for _ in range(3):
            thread = threading.Thread(target=self.ai_processing_worker)
            thread.daemon = True
            thread.start()
            self.ai_thread_pool.append(thread)
        
        self.error_handler = threading.Thread(target=self.error_handling_worker)
        self.error_handler.daemon = True
        self.error_handler.start()

    def send_message(self):
        """发送用户消息"""
        user_text = self.user_input.text().strip()
        if user_text:
            self.display_user_message(user_text)
            self.user_input.clear()
            self.broker.user_message.emit(user_text)

    def display_ai_message(self, message):
        """显示AI回复"""
        if message and not message.startswith("NULL"):
            formatted_message = message.replace('\n', '<br>')
            self.chat_display.append(f'<div style="color:#e60073; margin-bottom:12px;"><b>Nike:</b> {formatted_message}</div>')
            self.scroll_to_bottom()

    def display_user_message(self, message):
        """显示用户消息"""
        formatted_message = message.replace('\n', '<br>')
        self.chat_display.append(f'<div style="color:#1a75ff; margin-bottom:8px;"><b>你:</b> {formatted_message}</div>')
        self.scroll_to_bottom()

    def display_system_message(self, message):
        """显示系统消息"""
        if "初始化完成" in message or "设置提醒" in message:
            formatted_message = message.replace('\n', '<br>')
            self.chat_display.append(f'<div style="color:#009900; margin-bottom:5px;"><i>系统:</i> {formatted_message}</div>')
            self.scroll_to_bottom()

    def display_error(self, error):
        """显示错误消息"""
        formatted_message = error.replace('\n', '<br>')
        self.chat_display.append(f'<div style="color:#ff0000; margin-bottom:12px;"><b>错误:</b> {formatted_message}</div>')
        self.scroll_to_bottom()

    def update_status(self, status):
        """更新状态栏"""
        self.status_label.setText(status)

    def scroll_to_bottom(self):
        """滚动到聊天底部"""
        self.chat_display.moveCursor(QTextCursor.End)
        self.chat_display.ensureCursorVisible()

    def run_init_sequence(self):
        """执行初始化序列"""
        def init_worker():
            try:
                init_file = "Init.txt"
                if os.path.exists(init_file):
                    self.broker.status_update.emit("执行初始化序列...")
                    with open(init_file, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                response = process_user_message(line, self.ai, self.system)
                                if response:
                                    self.broker.ai_response.emit(response)
                                time.sleep(0.5)
                    self.broker.status_update.emit("初始化完成，系统就绪")
                    self.broker.system_message.emit("初始化完成")
                else:
                    self.broker.status_update.emit("未找到初始化文件")
            except Exception as e:
                self.broker.error_occurred.emit(f"初始化错误: {str(e)}")
            finally:
                self.initialization_complete = True
                QTimer.singleShot(1000, lambda: self.broker.user_message.emit("额头太高了"))
        
        init_thread = threading.Thread(target=init_worker)
        init_thread.daemon = True
        init_thread.start()

    def process_user_input(self, user_input):
        """处理用户输入"""
        def process():
            try:
                response = process_user_message(user_input, self.ai, self.system)
                self.broker.ai_response.emit(response)
            except Exception as e:
                self.broker.error_occurred.emit(f"处理消息时出错: {str(e)}")
        
        thread = threading.Thread(target=process)
        thread.daemon = True
        thread.start()

    def check_system_messages(self):
        """检查系统消息队列"""
        try:
            while not self.system.message_queue.empty():
                msg = self.system.message_queue.get()
                self.broker.system_message.emit(msg)
                self.broker.user_message.emit(msg)
        except Exception as e:
            self.broker.error_occurred.emit(f"系统消息处理错误: {str(e)}")

    def handle_system_messages(self):
        """后台处理系统消息"""
        while self.system.running:
            try:
                time.sleep(0.3)
            except Exception as e:
                self.broker.error_occurred.emit(f"系统处理线程错误: {str(e)}")
                time.sleep(1)

    def ai_processing_worker(self):
        """AI处理工作线程"""
        while True:
            time.sleep(1)

    def error_handling_worker(self):
        """错误处理工作线程"""
        while True:
            time.sleep(5)

    def closeEvent(self, event):
        """关闭窗口时的清理工作"""
        self.system.shutdown()
        self.broker.status_update.emit("系统关闭中...")
        self.timer.stop()
        time.sleep(0.5)
        event.accept()
        
    def mousePressEvent(self, event):
        """支持拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """支持拖动窗口"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

# 以下main()函数保持不变...
def load_key_config():
    """从Key.txt加载API密钥配置"""
    config = {}
    try:
        with open("Key.txt", 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        required_keys = ['api_key', 'api_url', 'model']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Key.txt中缺少必需的配置项: {key}")
        return config
    except FileNotFoundError:
        raise FileNotFoundError("找不到Key.txt配置文件")
    except Exception as e:
        raise RuntimeError(f"加载Key.txt配置出错: {str(e)}")

def main():
    try:
        key_config = load_key_config()
        print(f"成功加载API配置: {key_config}")
    except Exception as e:
        print(f"致命错误: {str(e)}")
        sys.exit(1)
    
    ai = AIWife()
    ai.api_key = key_config['api_key']
    ai.api_url = key_config['api_url']
    ai.model = key_config['model']
    
    system = MorSystem(ai)
    
    try:
        with open("System_prompt.txt", 'r', encoding='utf-8') as f:
            system_prompt = f.read()
            ai.set_system_prompt(system_prompt)
            system._log_entry("SYSTEM", "系统提示词已加载", "SYSTEM")
    except FileNotFoundError:
        print("警告: 未找到系统提示词文件 System_prompt.txt")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMainWindow {
            background: transparent;
        }
        QWidget {
            background: transparent;
            color: #333333;
        }
        QPushButton {
            background-color: rgba(74, 134, 232, 180);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: rgba(59, 125, 224, 200);
        }
        QPushButton:pressed {
            background-color: rgba(45, 98, 184, 200);
        }
        QLineEdit {
            background-color: white;
            color: #333333;
            border: 1px solid #d0d0d0;
            padding: 8px;
            border-radius: 5px;
        }
        QLabel {
            color: #333333;
            background: transparent;
        }
        QScrollArea {
            border: none;
            background: transparent;
        }
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: rgba(100, 100, 100, 100);
            min-height: 20px;
            border-radius: 4px;
        }
    """)
    
    window = ChatGUI(ai, system)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()