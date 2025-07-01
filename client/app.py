from config import Config
from ui.auth_window import AuthWindow
import tkinter as tk

def main():
    Config.configure_styles() 
    auth_app = AuthWindow()
    auth_app.mainloop()

if __name__ == "__main__":
    main()