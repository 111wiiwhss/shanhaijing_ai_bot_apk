#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
山海经异变AI代练 - 简化版Kivy应用
"""

import os
import sys
import logging
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from kivy.core.window import Window

# 设置中文字体支持
from kivy.resources import resource_add_path, resource_find

class LogConsole(ScrollView):
    """日志控制台"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_text = TextInput(
            text="欢迎使用山海经异变AI代练\n",
            readonly=True,
            background_color=(0.1, 0.1, 0.1, 1),
            foreground_color=(0.8, 0.8, 0.8, 1),
            font_size=14,
            multiline=True
        )
        self.add_widget(self.log_text)
    
    def add_log(self, message):
        """添加日志信息"""
        self.log_text.text += f"{message}\n"
        self.log_text.scroll_y = 0

class ConfigPanel(GridLayout):
    """配置面板"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.padding = 10
        self.spacing = 10
        
        # 游戏URL配置
        self.add_widget(Label(text="游戏URL:"))
        self.game_url = TextInput(
            text="https://game.weixin.qq.com/cgi-bin/h5/static/thirdparty/shanhaijing/index.html",
            multiline=False,
            font_size=14
        )
        self.add_widget(self.game_url)
        
        # 自动合成配置
        self.add_widget(Label(text="自动合成:"))
        self.auto_synthesize = TextInput(
            text="True",
            multiline=False,
            font_size=14
        )
        self.add_widget(self.auto_synthesize)
        
        # 自动收奖配置
        self.add_widget(Label(text="自动收奖:"))
        self.auto_collect_rewards = TextInput(
            text="True",
            multiline=False,
            font_size=14
        )
        self.add_widget(self.auto_collect_rewards)
        
        # 自动刷幸运配置
        self.add_widget(Label(text="自动刷幸运:"))
        self.auto_brush_luck = TextInput(
            text="True",
            multiline=False,
            font_size=14
        )
        self.add_widget(self.auto_brush_luck)
        
        # 自动看广告配置
        self.add_widget(Label(text="自动看广告:"))
        self.auto_watch_ads = TextInput(
            text="True",
            multiline=False,
            font_size=14
        )
        self.add_widget(self.auto_watch_ads)

class MainInterface(BoxLayout):
    """主界面"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # 标题
        self.title = Label(
            text="山海经异变AI代练",
            font_size=24,
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.title)
        
        # 控制按钮
        self.control_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.start_btn = Button(
            text="启动AI代练",
            background_color=(0.2, 0.7, 0.2, 1),
            font_size=16
        )
        self.start_btn.bind(on_press=self.start_ai_bot)
        self.control_layout.add_widget(self.start_btn)
        
        self.stop_btn = Button(
            text="停止AI代练",
            background_color=(0.7, 0.2, 0.2, 1),
            font_size=16
        )
        self.stop_btn.bind(on_press=self.stop_ai_bot)
        self.control_layout.add_widget(self.stop_btn)
        
        self.add_widget(self.control_layout)
        
        # 标签页
        self.tab_panel = TabbedPanel(size_hint_y=None, height=400)
        
        # 配置标签
        self.config_tab = TabbedPanelItem(text="配置")
        self.config_panel = ConfigPanel()
        self.config_tab.add_widget(self.config_panel)
        self.tab_panel.add_widget(self.config_tab)
        
        # 日志标签
        self.log_tab = TabbedPanelItem(text="日志")
        self.log_console = LogConsole()
        self.log_tab.add_widget(self.log_console)
        self.tab_panel.add_widget(self.log_tab)
        
        self.add_widget(self.tab_panel)
        
        # 状态显示
        self.status_label = Label(
            text="状态: 未运行",
            font_size=16,
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.status_label)
        
        # AI机器人状态
        self.ai_bot_running = False
        
        # 初始化日志
        self.log_console.add_log("应用已启动，等待操作...")
    
    def start_ai_bot(self, instance):
        """启动AI代练机器人"""
        if not self.ai_bot_running:
            self.status_label.text = "状态: 正在启动..."
            self.log_console.add_log("正在启动AI代练机器人...")
            
            # 模拟启动过程
            Clock.schedule_once(self._start_ai_bot, 1.0)
    
    def _start_ai_bot(self, dt):
        """实际启动AI机器人"""
        self.ai_bot_running = True
        self.status_label.text = "状态: 运行中"
        self.log_console.add_log("AI代练机器人已启动")
        
        # 模拟AI机器人工作
        Clock.schedule_interval(self._simulate_ai_work, 2.0)
    
    def _simulate_ai_work(self, dt):
        """模拟AI机器人工作"""
        if self.ai_bot_running:
            self.log_console.add_log("AI代练机器人正在工作...")
    
    def stop_ai_bot(self, instance):
        """停止AI代练机器人"""
        if self.ai_bot_running:
            self.status_label.text = "状态: 正在停止..."
            self.log_console.add_log("正在停止AI代练机器人...")
            
            # 取消模拟工作
            Clock.unschedule(self._simulate_ai_work)
            
            # 模拟停止过程
            Clock.schedule_once(self._stop_ai_bot, 1.0)
        else:
            self.log_console.add_log("AI代练机器人未运行")
    
    def _stop_ai_bot(self, dt):
        """实际停止AI机器人"""
        self.ai_bot_running = False
        self.status_label.text = "状态: 已停止"
        self.log_console.add_log("AI代练机器人已停止")

class ShanhaijingApp(App):
    """山海经AI代练应用"""
    
    def build(self):
        """构建应用界面"""
        Window.size = (400, 600)  # 设置默认窗口大小
        return MainInterface()

if __name__ == "__main__":
    # 设置中文字体
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    
    # 启动应用
    ShanhaijingApp().run()
