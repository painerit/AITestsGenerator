import tkinter as tk
from tkinter import scrolledtext
from config import Config
from config import Config

class ScrollTextFrame(tk.Frame):
    def __init__(self, master, label_text, height, is_editable=True):
        super().__init__(master)
        self.config = Config()
        self.is_editable = is_editable
        
        self.label = tk.Label(self, text=label_text, font=self.config.FONT)
        self.text_widget = scrolledtext.ScrolledText(
            self, 
            wrap=tk.WORD,
            width=80,
            height=height,
            font=self.config.FONT,
            state=tk.NORMAL if self.is_editable else tk.DISABLED
        )
        self._setup_ui()

    def _setup_ui(self):
        self.label.pack(anchor="w")
        self.text_widget.pack(pady=(0, 10), expand=True)
        
    def clear(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        
    def get_content(self):
        return self.text_widget.get(1.0, tk.END).strip()
        
    def set_content(self, text):
        self.clear()
        self.text_widget.insert(tk.END, text)
        if not self.is_editable:
            self.text_widget.config(state=tk.DISABLED)
    def set_content(self, text):
        """Установка текста в виджет"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, text)
        self.text_widget.config(state=tk.DISABLED if not self.is_editable else tk.NORMAL)
    def get_content(self):
        """Получение содержимого текстового поля"""
        return self.text_widget.get("1.0", tk.END).strip()