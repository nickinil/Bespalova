import json
import os
import random
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "task_history.json"

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Генератор случайных задач")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        # Предопределённые задачи с типами
        self.predefined_tasks = [
            {"task": "Прочитать статью по Python", "type": "учёба"},
            {"task": "Прочитать статью по машинному обучению", "type": "учёба"},
            {"task": "Сделать зарядку 15 минут", "type": "спорт"},
            {"task": "Пробежка 3 км", "type": "спорт"},
            {"task": "Отправить отчёт по работе", "type": "работа"},
            {"task": "Провести совещание", "type": "работа"},
            {"task": "Выучить 10 новых слов на английском", "type": "учёба"},
            {"task": "Йога на 20 минут", "type": "спорт"},
            {"task": "Завершить проект", "type": "работа"},
            {"task": "Почитать книгу 30 минут", "type": "учёба"},
            {"task": "Отжимания 30 раз", "type": "спорт"},
            {"task": "Составить план на неделю", "type": "работа"},
            {"task": "Решить задачу на LeetCode", "type": "учёба"},
            {"task": "Приседания 50 раз", "type": "спорт"},
            {"task": "Позвонить клиентам", "type": "работа"}
        ]

        self.task_history = []
        self.load_data()

        # Создание интерфейса
        self.create_main_frame()
        self.create_task_display_frame()
        self.create_filter_frame()
        self.create_history_frame()
        self.create_add_task_frame()

        self.refresh_history_display()

    def create_main_frame(self):
        """Основной фрейм с генерацией задачи"""
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(pady=20)

        tk.Label(frame, text="Генератор случайных задач", font=("Arial", 18, "bold"), 
                 bg="#f0f0f0", fg="#333").pack(pady=10)

        self.generate_btn = tk.Button(frame, text="🎲 Сгенерировать задачу", command=self.generate_random_task,
                                        bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                        padx=20, pady=10, cursor="hand2")
        self.generate_btn.pack(pady=10)

    def create_task_display_frame(self):
        """Фрейм для отображения текущей задачи"""
        frame = tk.LabelFrame(self.root, text="Текущая задача", font=("Arial", 12, "bold"),
                               bg="white", padx=10, pady=10)
        frame.pack(fill="x", padx=20, pady=10)

        self.current_task_label = tk.Label(frame, text="Нажмите кнопку для генерации задачи",
                                            font=("Arial", 14), bg="white", fg="#666", wraplength=700)
        self.current_task_label.pack(pady=20)

    def create_filter_frame(self):
        """Фрейм для фильтрации"""
        frame = tk.LabelFrame(self.root, text="Фильтрация истории", font=("Arial", 12, "bold"),
                               bg="white", padx=10, pady=10)
        frame.pack(fill="x", padx=20, pady=10)

        filter_frame = tk.Frame(frame, bg="white")
        filter_frame.pack()

        tk.Label(filter_frame, text="Фильтр по типу:", font=("Arial", 10), bg="white").pack(side="left", padx=5)

        self.filter_type_var = tk.StringVar(value="Все")
        types = ["Все", "учёба", "спорт", "работа"]
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, 
                                          values=types, width=15, state="readonly")
        self.filter_combo.pack(side="left", padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_history_display())

        self.clear_filter_btn = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter,
                                           bg="#FF9800", fg="white", cursor="hand2")
        self.clear_filter_btn.pack(side="left", padx=10)

    def create_history_frame(self):
        """Фрейм для отображения истории"""
        frame = tk.LabelFrame(self.root, text="История сгенерированных задач", font=("Arial", 12, "bold"),
                               bg="white", padx=10, pady=10)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Создание списка с прокруткой
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.history_listbox = tk.Listbox(frame, font=("Arial", 10), yscrollcommand=scrollbar.set,
                                          selectmode=tk.SINGLE, height=12)
        self.history_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Кнопки управления историей
        button_frame = tk.Frame(frame, bg="white")
        button_frame.pack(pady=10)

        self.delete_selected_btn = tk.Button(button_frame, text="🗑️ Удалить выбранную задачу",
                                              command=self.delete_selected_task,
                                              bg="#f44336", fg="white", cursor="hand2")
        self.delete_selected_btn.pack(side="left", padx=5)

        self.clear_all_btn = tk.Button(button_frame, text="🚮 Очистить всю историю",
                                        command=self.clear_all_history,
                                        bg="#9E9E9E", fg="white", cursor="hand2")
        self.clear_all_btn.pack(side="left", padx=5)

        self.save_btn = tk.Button(button_frame, text="💾 Сохранить историю",
                                   command=self.save_data,
                                   bg="#2196F3", fg="white", cursor="hand2")
        self.save_btn.pack(side="left", padx=5)

    def create_add_task_frame(self):
        """Фрейм для добавления новых задач"""
        frame = tk.LabelFrame(self.root, text="Добавить новую задачу", font=("Arial", 12, "bold"),
                               bg="white", padx=10, pady=10)
        frame.pack(fill="x", padx=20, pady=10)

        input_frame = tk.Frame(frame, bg="white")
        input_frame.pack()

        tk.Label(input_frame, text="Название задачи:", font=("Arial", 10), bg="white").grid(row=0, column=0, padx=5, pady=5)
        self.new_task_entry = tk.Entry(input_frame, width=40, font=("Arial", 10))
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Тип задачи:", font=("Arial", 10), bg="white").grid(row=0, column=2, padx=5, pady=5)
        self.new_task_type_var = tk.StringVar(value="учёба")
        type_combo = ttk.Combobox(input_frame, textvariable=self.new_task_type_var,
                                   values=["учёба", "спорт", "работа"], width=12, state="readonly")
        type_combo.grid(row=0, column=3, padx=5, pady=5)

        self.add_task_btn = tk.Button(input_frame, text="➕ Добавить задачу", command=self.add_custom_task,
                                       bg="#8BC34A", fg="white", cursor="hand2")
        self.add_task_btn.grid(row=0, column=4, padx=10, pady=5)

    def generate_random_task(self):
        """Генерация случайной задачи"""
        # Объединяем предопределённые задачи с пользовательскими
        all_tasks = self.predefined_tasks.copy()
        
        # Добавляем пользовательские задачи из истории (уникальные)
        custom_tasks = []
        for item in self.task_history:
            task_data = {"task": item["task"], "type": item["type"]}
            if task_data not in custom_tasks and task_data not in all_tasks:
                custom_tasks.append(task_data)
        
        all_tasks.extend(custom_tasks)
        
        if not all_tasks:
            messagebox.showwarning("Внимание", "Нет доступных задач. Добавьте хотя бы одну задачу!")
            return

        selected_task = random.choice(all_tasks)
        
        # Добавляем в историю
        task_entry = {
            "task": selected_task["task"],
            "type": selected_task["type"],
            "timestamp": self.get_timestamp()
        }
        self.task_history.append(task_entry)
        
        # Отображаем текущую задачу
        self.current_task_label.config(text=f"📌 {selected_task['task']}", fg="#4CAF50", font=("Arial", 14, "bold"))
        
        # Обновляем отображение истории
        self.refresh_history_display()
        self.save_data()
        
        # Показываем уведомление
        messagebox.showinfo("Сгенерировано", f"Ваша задача:\n{selected_task['task']}")

    def add_custom_task(self):
        """Добавление пользовательской задачи"""
        task_text = self.new_task_entry.get().strip()
        task_type = self.new_task_type_var.get()

        # Проверка на пустую строку
        if not task_text:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return

        # Проверка на существующую задачу
        for task in self.predefined_tasks:
            if task["task"].lower() == task_text.lower():
                messagebox.showwarning("Предупреждение", "Такая задача уже существует!")
                return

        # Добавляем в предопределённые задачи
        self.predefined_tasks.append({"task": task_text, "type": task_type})
        
        # Очищаем поле ввода
        self.new_task_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена в список!")
        
        # Обновляем текущую задачу (опционально)
        self.current_task_label.config(text="Нажмите кнопку для генерации задачи", fg="#666")

    def delete_selected_task(self):
        """Удаление выбранной задачи из истории"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите задачу для удаления!")
            return

        index = selection[0]
        filtered_history = self.get_filtered_history()
        
        if index < len(filtered_history):
            task_to_delete = filtered_history[index]
            # Находим и удаляем из полной истории
            for i, task in enumerate(self.task_history):
                if task["task"] == task_to_delete["task"] and task["timestamp"] == task_to_delete["timestamp"]:
                    del self.task_history[i]
                    break
            
            self.refresh_history_display()
            self.save_data()
            messagebox.showinfo("Успех", "Задача удалена из истории!")

    def clear_all_history(self):
        """Очистка всей истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.task_history = []
            self.refresh_history_display()
            self.save_data()
            messagebox.showinfo("Успех", "История очищена!")

    def reset_filter(self):
        """Сброс фильтра"""
        self.filter_type_var.set("Все")
        self.refresh_history_display()

    def get_filtered_history(self):
        """Получение отфильтрованной истории"""
        filter_type = self.filter_type_var.get()
        if filter_type == "Все":
            return self.task_history.copy()
        else:
            return [task for task in self.task_history if task["type"] == filter_type]

    def refresh_history_display(self):
        """Обновление отображения истории"""
        self.history_listbox.delete(0, tk.END)
        
        filtered_history = self.get_filtered_history()
        
        if not filtered_history:
            self.history_listbox.insert(tk.END, "📭 История пуста")
            return
        
        for task in reversed(filtered_history):  # Показываем последние сверху
            display_text = f"[{task['timestamp']}] [{task['type'].upper()}] {task['task']}"
            self.history_listbox.insert(tk.END, display_text)
            
            # Раскрашиваем элементы по типам
            last_index = self.history_listbox.size() - 1
            if task['type'] == 'учёба':
                self.history_listbox.itemconfig(last_index, fg='blue')
            elif task['type'] == 'спорт':
                self.history_listbox.itemconfig(last_index, fg='green')
            elif task['type'] == 'работа':
                self.history_listbox.itemconfig(last_index, fg='red')

    def get_timestamp(self):
        """Получение текущей временной метки"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load_data(self):
        """Загрузка истории из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.task_history = json.load(f)
            except:
                self.task_history = []
        else:
            # Добавляем примеры для демонстрации
            self.task_history = [
                {"task": "Прочитать статью по Python", "type": "учёба", "timestamp": "2026-04-28 10:30:00"},
                {"task": "Сделать зарядку 15 минут", "type": "спорт", "timestamp": "2026-04-27 09:15:00"},
                {"task": "Отправить отчёт по работе", "type": "работа", "timestamp": "2026-04-26 14:20:00"}
            ]

    def save_data(self):
        """Сохранение истории в JSON"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.task_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()