from config import Config
from tkinter import ttk, messagebox
import tkinter as tk
from config import Config
from api.auth_client import AuthClient
from ui.main_window import MainWindow 
from api.auth_client import AuthError

class AuthWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.auth_client = AuthClient()
        self.title(Config().WINDOW_TITLE)
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Основной контейнер
        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both", padx=20, pady=20)
        
        self._create_login_frame()
        self._create_register_frame()
        self.show_login()

    def handle_login(self):
        try:
            username = self.login_username.get()
            password = self.login_password.get()
            
            if not username or not password:
                raise ValueError("Заполните все поля")
            
            response = self.auth_client.login(username, password)
            if "access_token" in response and "user" in response:
                self.withdraw()  # Скрываем окно авторизации
                MainWindow(
                    self,  # Передаем себя как родителя
                    response['access_token'],
                    response['user']['id']
                )
            else:
                messagebox.showerror("Ошибка", "Неверные учетные данные")
        
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _create_login_frame(self):
        self.login_frame = tk.Frame(self.container)
        
        # Элементы логина
        tk.Label(self.login_frame, text="Логин:").pack(pady=5)
        self.login_username = tk.Entry(self.login_frame)
        self.login_username.pack(pady=5)
        
        tk.Label(self.login_frame, text="Пароль:").pack(pady=5)
        self.login_password = tk.Entry(self.login_frame, show="*")
        self.login_password.pack(pady=5)
        
        # Кнопка входа
        tk.Button(
            self.login_frame,
            text="Войти",
            command=self.handle_login  
        ).pack(pady=10)
        
        # Ссылка на регистрацию
        register_label = tk.Frame(self.login_frame)
        register_label.pack(pady=5)
        tk.Label(register_label, text="Нет аккаунта?").pack(side="left")
        ttk.Button(
            register_label,
            text="Зарегистрироваться",
            command=self.show_register,
            style="Link.TButton"
        ).pack(side="left", padx=5)
    
    def handle_register(self):
        try:
            username = self.register_username.get()
            email = self.register_email.get()
            password = self.register_password.get()
            
            if not all([username, email, password]):
                raise ValueError("Заполните все поля")
            
            # Регистрация
            self.auth_client.register(username, email, password)
            
            # Очистка полей и возврат на страницу логина
            self.register_username.delete(0, tk.END)
            self.register_email.delete(0, tk.END)
            self.register_password.delete(0, tk.END)
            
            messagebox.showinfo("Успех", "Регистрация выполнена! Теперь вы можете войти.")
            self.show_login()
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _create_register_frame(self):
        self.register_frame = tk.Frame(self.container)
        
        # Элементы
        tk.Label(self.register_frame, text="Логин:").pack(pady=5)
        self.register_username = tk.Entry(self.register_frame)
        self.register_username.pack(pady=5)
        
        tk.Label(self.register_frame, text="Email:").pack(pady=5)
        self.register_email = tk.Entry(self.register_frame)
        self.register_email.pack(pady=5)
        
        tk.Label(self.register_frame, text="Пароль:").pack(pady=5)
        self.register_password = tk.Entry(self.register_frame, show="*")
        self.register_password.pack(pady=5)
        
        # Кнопки
        btn_frame = tk.Frame(self.register_frame)
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Назад",
            command=self.show_login
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="Зарегистрироваться",
            command=self.handle_register
        ).pack(side="left", padx=5)
    
    def show_login(self):
        self.register_frame.pack_forget()
        self.login_frame.pack(expand=True, fill="both")
        self.title(Config().LOGIN_TITLE)
    
    def show_register(self):
        self.login_frame.pack_forget()
        self.register_frame.pack(expand=True, fill="both")
        self.title(Config().REG_TITLE)
