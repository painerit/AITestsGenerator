import tkinter as tk
from ui.widgets import ScrollTextFrame
from api.ai_client import AIClient
import requests
from config import Config
import time
from datetime import datetime
import tkinter.ttk as ttk
from tkinter import filedialog


class MainWindow(tk.Toplevel):
    def __init__(self, parent, access_token, user_id):
        super().__init__(parent)
        self.geometry(Config().MAIN_WINDOW_SIZE)
        self.title(Config().WINDOW_TITLE)
        self.access_token = access_token
        self.user_id = user_id
        self.ai_client = AIClient()
        self.config = Config()
        self.selected_item = None
        
        # Основной контейнер
        self.main_container = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        left_container = tk.PanedWindow(self.main_container, orient=tk.VERTICAL, width=350)
        self.main_container.add(left_container)
        self._setup_history_panel(left_container)
        self.load_history()  # Загружаем историю при старте
        self._setup_templates_panel(left_container)
        self.load_templates()
        self._setup_chat_panel()     # Правая панель с чатом
        
    def _setup_history_panel(self, parent):
        """Левая панель с историей запросов"""
        self.history_frame = tk.Frame(parent, width=350, bg='#f0f0f0')
        parent.add(self.history_frame)
        
        # Заголовок
        tk.Label(self.history_frame, text="История запросов", 
                bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Контейнер для элементов истории с прокруткой
        self.history_container = tk.Frame(self.history_frame, bg='white')
        self.history_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Вертикальный скроллбар
        self.scrollbar = tk.Scrollbar(self.history_container)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas для скроллируемой области
        self.canvas = tk.Canvas(
            self.history_container,
            yscrollcommand=self.scrollbar.set,
            bg='white'
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        
        # Фрейм для элементов внутри Canvas
        self.history_items_frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0, 0), window=self.history_items_frame, anchor='nw')
        
        # Привязка обновления скролла
        self.history_items_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )

    def _setup_templates_panel(self, parent):
        """Нижняя панель с шаблонами"""
        self.templates_frame = tk.Frame(parent, bg="#f0f0f0")
        parent.add(self.templates_frame)
        # Заголовок
        tk.Label(self.templates_frame, text="Шаблоны", 
                bg='#f0f0f0', font=('Arial', 10, 'bold')).pack(pady=10)
        
        # Контейнер для элементов истории с прокруткой
        self.templates_container = tk.Frame(self.templates_frame, bg='white')
        self.templates_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.templates_frame.pack_propagate(False)  # Запрет изменения размера

        # Вертикальный скроллбар
        self.scrollbar = tk.Scrollbar(self.templates_container)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas для скроллируемой области
        self.canvas = tk.Canvas(
            self.templates_container,
            yscrollcommand=self.scrollbar.set,
            bg='white'
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        
        # Фрейм для элементов внутри Canvas
        self.templates_items_frame = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0, 0), window=self.templates_items_frame, anchor='nw')
        
        # Привязка обновления скролла
        self.templates_items_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )

    def _setup_chat_panel(self):
        """Правая панель с чатом и полями ввода"""
        self.chat_frame = tk.Frame(self.main_container)
        self.main_container.add(self.chat_frame, stretch="always")

        # Верхняя панель с кнопкой Logout
        top_bar = tk.Frame(self.chat_frame, bg='#f0f0f0')
        top_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Кнопка Logout
        ttk.Button(
            top_bar,
            text="Выход",
            command=self._logout,
            style="Logout.TButton"
        ).pack(side=tk.RIGHT, padx=10)

        # Контейнер для полей ввода
        input_container = tk.Frame(self.chat_frame)
        input_container.pack(fill=tk.X, padx=10, pady=10)

        # Поля ввода
        self._create_dropdown(input_container, "Элемент программы:", ["класс", "структура", "функция"])
        self._create_input_field(input_container, "Язык программирования:")
        self._create_input_field(input_container, "Дополнительная информация:")
        self._create_input_field(input_container, "Вид тестов:")

        # Поле для кода
        self.code_input = ScrollTextFrame(
            self.chat_frame,
            "Код:",
            height=10,
            is_editable=True
        )
        self.code_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.response_frame = ScrollTextFrame(
            self.chat_frame,
            "Ответ нейросети:",
            height=15,
            is_editable=False
        )
        self.response_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Кнопка отправки
        btn_frame = tk.Frame(self.chat_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            btn_frame,
            text="Экспорт в шаблон",
            command=self._save_as_template,
            style="Export.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Сгенерировать тесты",
            command=self._handle_request,
            style="Send.TButton"
        ).pack(side=tk.RIGHT)
        ttk.Button(
            btn_frame,
            text="Экспорт в TXT",
            command=self._export_to_txt,
            style="Export.TButton"
        ).pack(side=tk.RIGHT, padx=5)

    def _create_dropdown(self, parent, label_text, values):
        """Создание выпадающего списка"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text=label_text).pack(side=tk.LEFT, padx=5)
        
        self.element_type = tk.StringVar()
        dropdown = ttk.Combobox(
            frame, 
            textvariable=self.element_type,
            values=values,
            state="readonly"
        )
        dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        dropdown.current(0)

    def _create_input_field(self, parent, label_text):
        """Создание текстового поля"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(frame, text=label_text).pack(side=tk.LEFT, padx=5)
        
        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Сохраняем ссылки на поля
        if "Язык" in label_text:
            self.language_entry = entry
        elif "Дополнительная" in label_text:
            self.additional_info_entry = entry
        elif "Вид тестов" in label_text:
            self.test_type_entry = entry

    def _handle_request(self):
        """Обработка отправки запроса"""
        
        try:
            element = self.element_type.get()
            language = self.language_entry.get()
            additional_info = self.additional_info_entry.get()
            test_type = self.test_type_entry.get()
            code = self.code_input.get_content()
            prompt = (
                f"Ты - Senior-разработчик на языке {language} с 10+ стажем.\n"
                f"Напиши {test_type}, которые обеспечат максимальное покрытие кода, будут выполняться максимально быстро, будут проходить только в случае отсутствия ошибок в коде и будут понятны человеку, с содержанием программных комментариев.\n"
                f"Твой ответ - код из исходного файла тестов на {language}, без пояснений.\n" 
                f"Сам(а) {element}: {code}\n"
                f"Дополнительная информация: {additional_info}"
            )
            ai_response = self.ai_client.send_request(prompt)
            self.response_frame.set_content(ai_response)
            # Получаем данные из полей
            data = {
                "additional_info": self.additional_info_entry.get(),
                "code": self.code_input.get_content(),
                "element_type": self.element_type.get(),
                "language": self.language_entry.get(),
                "response_text": ai_response,
                "test_type": self.test_type_entry.get()
            }
            # if not all([self.element_type, language, test_type, code]):
            #     tk.messagebox.showwarning("Ошибка", "Заполните все обязательные поля")
            #     return
            
            # Сохраняем запрос в историю на сервере
            save_response = requests.post(
                f"{Config().API_BASE_URL}/history",
                json=data,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

            if save_response.status_code != 201:
                raise Exception(f"Ошибка сохранения: {save_response.text}")

            # Оптимизация: добавляем запрос локально без перезагрузки всей истории
            new_item = {
                "id": save_response.json()["record_id"],
                "element_type": self.element_type.get(),
                "language": self.language_entry.get(),
                "additional_info": self.additional_info_entry.get(),
                "test_type": self.test_type_entry.get(),
                "code": self.code_input.get_content(),
                "response": ai_response,
                "created_at": save_response.json().get("created_at", datetime.now().isoformat())
            }
            self.history.insert(0, new_item)  # Добавляем в начало списка
            self._update_history_list()  # Обновляем виджет

        except Exception as e:
            self.response_frame.set_content(f"Error: {str(e)}")
            tk.messagebox.showerror("Ошибка", str(e))

    def _save_as_template(self):
        """Обработка отправки шаблона"""
        
        try:

            # Получаем данные из полей
            data = {
                "additional_info": self.additional_info_entry.get(),
                "code": self.code_input.get_content(),
                "element_type": self.element_type.get(),
                "language": self.language_entry.get(),
                "test_type": self.test_type_entry.get()
            }
            # if not all([self.element_type, language, test_type, code]):
            #     tk.messagebox.showwarning("Ошибка", "Заполните все обязательные поля")
            #     return
            
            # Сохраняем запрос в историю на сервере
            save_response = requests.post(
                f"{Config().API_BASE_URL}/templates",
                json=data,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

            if save_response.status_code != 201:
                raise Exception(f"Ошибка сохранения: {save_response.text}")

            # Оптимизация: добавляем запрос локально без перезагрузки всей истории
            new_item = {
                "id": save_response.json()["template_id"],
                "element_type": self.element_type.get(),
                "language": self.language_entry.get(),
                "additional_info": self.additional_info_entry.get(),
                "test_type": self.test_type_entry.get(),
                "code": self.code_input.get_content(),
                "created_at": save_response.json().get("created_at", datetime.now().isoformat())
            }
            self.templates.insert(0, new_item)  # Добавляем в начало списка
            self._update_templates_list()  # Обновляем виджет

        except Exception as e:
            self.response_frame.set_content(f"Error: {str(e)}")
            tk.messagebox.showerror("Ошибка", str(e))

    def _update_history_list(self):
        """Обновление списка истории с кнопками удаления"""
        for widget in self.history_items_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.history):
            item_frame = tk.Frame(self.history_items_frame, bg='white')
            item_frame.pack(fill=tk.X, pady=2, padx=5)

            # Левая часть: кликабельная текстовая область
            text_frame = tk.Frame(item_frame, bg='white')
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Правая часть: кнопка удаления (не кликабельная для выделения)
            button_frame = tk.Frame(item_frame, bg='white')
            button_frame.pack(side=tk.RIGHT)

            # Обработчик клика только для текстовой области
            text_frame.bind("<Button-1>", 
                lambda e, r_id=item['id']: self._on_history_select(r_id))

            # Текст элемента
            language = f" {item['language'][:10]}..." if len(item['language']) > 10 else item['language']
            test_type = f" {item['test_type'][:15]}..." if len(item['test_type']) > 15 else item['test_type']
            date_str = item['created_at'][:10] if 'created_at' in item else 'N/A'
            
            label = tk.Label(
                text_frame,
                text=f"{language}, {test_type} ({date_str})",
                bg='white',
                anchor='w',
                width=30
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            label.bind("<Button-1>", 
                lambda e, r_id=item['id']: self._on_history_select(r_id))

            # Кнопка удаления (в отдельном фрейме)
            delete_btn = tk.Button(
                button_frame,
                text="×",
                fg='red',
                command=lambda r_id=item['id']: self._delete_history_item(r_id),
                relief='flat',
                font=('Arial', 12, 'bold'),
                width=3
            )
            delete_btn.pack(side=tk.RIGHT, padx=5)

            # Выделение выбранного элемента
            if self.selected_item == item['id']:
                text_frame.config(bg='#e0e0e0')
                label.config(bg='#e0e0e0')
   
    def _update_templates_list(self):
        """Обновление списка истории с кнопками удаления"""
        for widget in self.templates_items_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.templates):
            item_frame = tk.Frame(self.templates_items_frame, bg='white')
            item_frame.pack(fill=tk.X, pady=2, padx=5)

            # Левая часть: кликабельная текстовая область
            text_frame = tk.Frame(item_frame, bg='white')
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Правая часть: кнопка удаления (не кликабельная для выделения)
            button_frame = tk.Frame(item_frame, bg='white')
            button_frame.pack(side=tk.RIGHT)

            # Обработчик клика только для текстовой области
            text_frame.bind("<Button-1>", 
                lambda e, t_id=item['id']: self._on_templates_select(t_id))

            # Текст элемента
            language = f" {item['language'][:10]}..." if len(item['language']) > 10 else item['language']
            test_type = f" {item['test_type'][:15]}..." if len(item['test_type']) > 15 else item['test_type']
            date_str = item['created_at'][:10] if 'created_at' in item else 'N/A'
            
            label = tk.Label(
                text_frame,
                text=f"{language}, {test_type} ({date_str})",
                bg='white',
                anchor='w',
                width=30
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            label.bind("<Button-1>", 
                lambda e, r_id=item['id']: self._on_templates_select(r_id))

            # Кнопка удаления (в отдельном фрейме)
            delete_template_btn = tk.Button(
                button_frame,
                text="×",
                fg='red',
                command=lambda t_id=item['id']: self._delete_template_item(t_id),
                relief='flat',
                font=('Arial', 12, 'bold'),
                width=3
            )
            delete_template_btn.pack(side=tk.RIGHT, padx=5)

            # Выделение выбранного элемента
            if self.selected_item == item['id']:
                text_frame.config(bg='#e0e0e0')
                label.config(bg='#e0e0e0')
  
    def _delete_history_item(self, record_id):
        """Обработка удаления элемента истории"""
        try:
            url = f"{Config().API_BASE_URL}/history/{record_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                self.history = [item for item in self.history if item['id'] != record_id]
                self._update_history_list()
                tk.messagebox.showinfo("Успех", "Запрос удален из истории")
            else:
                tk.messagebox.showerror("Ошибка", f"Ошибка удаления: {response.text}")
                
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Не удалось удалить запрос: {str(e)}")

    def _delete_template_item(self, template_id):
        """Обработка удаления шаблона"""
        try:
            url = f"{Config().API_BASE_URL}/templates/{template_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                self.templates = [item for item in self.templates if item['id'] != template_id]
                self._update_templates_list()
                tk.messagebox.showinfo("Успех", "Шаблон удален")
            else:
                tk.messagebox.showerror("Ошибка", f"Ошибка удаления: {response.text}")
                
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Не удалось удалить шаблон: {str(e)}")

    def _on_history_select(self, record_id):
        """Обработка выбора элемента истории"""
        self.selected_item = record_id
        self._update_history_list()  # Обновляем список для выделения
        selected_item = next((item for item in self.history if item['id'] == record_id), None)
        if selected_item:
            self._display_history_item(selected_item)

    def _on_templates_select(self, template_id):
        """Обработка выбора элемента истории"""
        self.selected_item = template_id
        self._update_templates_list()  # Обновляем список для выделения
        selected_item = next((item for item in self.templates if item['id'] == template_id), None)
        if selected_item:
            self._display_template_item(selected_item)

    def _display_history_item(self, item):
        """Отображение выбранного элемента истории"""
        try:
            # Установка значений в поля ввода
            self.element_type.set(item.get("element_type", ""))
            
            # Для Entry: Очистка и вставка текста (индекс 0, текст)
            self.language_entry.delete(0, tk.END)
            self.language_entry.insert(0, item.get("language", ""))  # Правильный вызов
            
            self.additional_info_entry.delete(0, tk.END)
            self.additional_info_entry.insert(0, item.get("additional_info", ""))
            
            self.test_type_entry.delete(0, tk.END)
            self.test_type_entry.insert(0, item.get("test_type", ""))
            
            # Для многострочных полей
            self.code_input.set_content(item.get("code", ""))
            self.response_frame.set_content(item.get("response", ""))
            
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")

    def _display_template_item(self, item):
        """Отображение выбранного элемента шаблонов"""
        try:
            # Установка значений в поля ввода
            self.element_type.set(item.get("element_type", ""))
            
            # Для Entry: Очистка и вставка текста (индекс 0, текст)
            self.language_entry.delete(0, tk.END)
            self.language_entry.insert(0, item.get("language", ""))  # Правильный вызов
            
            self.additional_info_entry.delete(0, tk.END)
            self.additional_info_entry.insert(0, item.get("additional_info", ""))
            
            self.test_type_entry.delete(0, tk.END)
            self.test_type_entry.insert(0, item.get("test_type", ""))
            
            # Для многострочных полей
            self.code_input.set_content(item.get("code", ""))
            self.response_frame.clear()
            
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Ошибка при загрузке: {str(e)}")
    
    def _logout(self):
        self.destroy()  # Закрываем MainWindow
        self.master.deiconify()  # Показываем скрытое окно авторизации

    def load_history(self):
        try:
            response = requests.get(
                f"{Config().API_BASE_URL}/history",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                self.history = response.json()
                self._update_history_list()
                self.canvas.update_idletasks() 
            else:
                tk.messagebox.showerror("Ошибка", f"Код {response.status_code}: {response.text}")
                
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Ошибка соединения: {str(e)}")

    def load_templates(self):
        try:
            response = requests.get(
                f"{Config().API_BASE_URL}/templates",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                self.templates = response.json()
                self._update_templates_list()
                self.canvas.update_idletasks() 
            else:
                tk.messagebox.showerror("Ошибка", f"Код {response.status_code}: {response.text}")
                
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Ошибка соединения: {str(e)}")

    def _export_to_txt(self):
        """Экспорт содержимого ответа в текстовый файл"""
        try:
            content = self.response_frame.get_content()
            if not content:
                tk.messagebox.showwarning("Пусто", "Нет данных для экспорта")
                return
            
            # Диалог выбора файла
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
            )
            
            if not file_path:
                return  # Пользователь отменил сохранение
            
            # Сохранение в файл
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            tk.messagebox.showinfo("Успех", f"Файл сохранен:\n{file_path}")
            
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Не удалось экспортировать:\n{str(e)}")