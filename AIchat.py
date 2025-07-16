import subprocess
import sys
import threading
import time
import os
import queue
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict

import requests

class AIWife:
    """AI聊天功能封装类"""
    
    def __init__(self, 
                 api_key: str = "",
                 system_prompt: str = "",
                 temperature: float = 0.7,
                 max_tokens: int = 1024,
                 model: str = "Pro/deepseek-ai/DeepSeek-V3",
                 api_url: str = "https://api.siliconflow.cn/v1/chat/completions"):
        """
        初始化AI聊天实例
        
        参数:
            api_key: API密钥
            system_prompt: 系统提示词
            temperature: 生成文本的随机性(0-1)
            max_tokens: 最大生成token数
            model: 使用的模型名称
            api_url: API端点URL
        """
        self.messages: List[Dict[str, str]] = []
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model
        self.api_url = api_url
        self.max_response_tokens = 10000  # 单次回复最大token限制
        
        # 初始化系统提示
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
    
    def set_api_key(self, key: str):
        """设置API密钥"""
        self.api_key = key.strip()
    
    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self.system_prompt = prompt
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = prompt
        else:
            self.messages.insert(0, {"role": "system", "content": prompt})
    
    def set_max_tokens(self, max_tokens: int) -> Tuple[int, str]:
        """
        设置最大token数
        
        返回:
            (实际设置的值, 警告信息)
        """
        if max_tokens <= 0:
            self.max_tokens = 8049
            return self.max_tokens, "已重置为默认值8049"
        if max_tokens > self.max_response_tokens:
            self.max_tokens = self.max_response_tokens
            return self.max_tokens, f"超过单次回复最大限制，已设置为{self.max_response_tokens}"
        self.max_tokens = max_tokens
        return self.max_tokens, ""
    
    def set_temperature(self, temperature: float):
        """设置温度参数(0-1)"""
        self.temperature = max(0.0, min(1.0, temperature))
    
    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.messages.append({"role": role, "content": content})
    
    def clear_history(self):
        """清空聊天历史"""
        if self.messages and self.messages[0]["role"] == "system":
            self.messages = [self.messages[0]]
        else:
            self.messages = []
    
    def get_response(self, user_message: str) -> str:
        """
        获取AI回复
        
        参数:
            user_message: 用户消息
            
        返回:
            AI回复内容或错误信息
        """
        if not self.api_key:
            return "错误：请先设置API密钥"
            
        self.add_message("user", user_message)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "text"}
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            ai_response = response.json()['choices'][0]['message']['content']
            self.add_message("assistant", ai_response)
            return ai_response
        except Exception as e:
            return f"API请求失败: {str(e)}"
    
    def chat(self, user_message: str) -> str:
        """与get_response功能相同，提供更简洁的接口"""
        return self.get_response(user_message)