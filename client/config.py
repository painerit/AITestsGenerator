import tkinter.ttk as ttk

class Config:
    # API Settings
    AI_API_KEY = "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"
    AI_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = "deepseek/deepseek-chat:free"
    
    # Auth API
    API_BASE_URL = "http://localhost:5000/api"
    AUTH_API_URL = "http://localhost:5000/api/auth"
    
    # UI Settings
    WINDOW_TITLE = "Test Assistant"
    LOGIN_TITLE = "Вход"
    REG_TITLE = "Регистрация"
    MAIN_WINDOW_SIZE = "1280x900"
    AUTH_WINDOW_SIZE = "400x300"
    FONT = ('Arial', 10)
    PRIMARY_COLOR = "#4CAF50"
    SECONDARY_COLOR = "#45a049"

    @staticmethod
    def configure_styles():
        style = ttk.Style()
        style.configure('History.TFrame', background='#f0f0f0')
        style.configure('HistoryItem.TFrame', background='white')
        style.configure('Delete.TButton', 
                      foreground='red', 
                      font=('Arial', 12, 'bold'),
                      borderwidth=0)
        style.configure('TopBar.TFrame', background='#f0f0f0')
        style.configure(
            "Logout.TButton",
            foreground="red",          # Цвет текста
            background="#f0f0f0",      # Цвет фона
            font=("Arial", 10, "bold"),
            padding=5,
            borderwidth=0
        )
        # Цвет при наведении
        style.map("Logout.TButton", 
                background=[("active", "#ff6666")])
        style.configure(
            "Send.TButton",
            foreground="#333333",  # Темно-серый текст
            background="white",     # Белый фон
            font=("Arial", 10, "bold"),
            borderwidth=1,
            relief="groove"         # Небольшая граница
        )
        style.configure("Export.TButton", 
                      foreground="blue",
                      font=("Arial", 10, "bold"),
                      padding=5)