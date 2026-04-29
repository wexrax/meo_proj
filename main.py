import tkinter as tk
from tkinter import messagebox, filedialog
import json
import re
from datetime import datetime

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.entries = []  # список словарей

        # --- Поля ввода ---
        tk.Label(root, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(root, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Температура (°C):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.temp_entry = tk.Entry(root, width=15)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="Описание:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.desc_entry = tk.Entry(root, width=30)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5)

        self.precip_var = tk.BooleanVar()
        self.precip_check = tk.Checkbutton(root, text="Осадки", variable=self.precip_var)
        self.precip_check.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # --- Кнопки ---
        tk.Button(root, text="Добавить запись", command=self.add_entry).grid(row=4, column=0, columnspan=2, pady=10)

        # --- Список записей ---
        tk.Label(root, text="Записи:").grid(row=5, column=0, columnspan=2)
        self.listbox = tk.Listbox(root, width=60, height=15)
        self.listbox.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        # --- Фильтры ---
        filter_frame = tk.LabelFrame(root, text="Фильтры", padx=5, pady=5)
        filter_frame.grid(row=7, column=0, columnspan=2, pady=10, sticky="ew")

        tk.Label(filter_frame, text="Дата:").grid(row=0, column=0)
        self.filter_date = tk.Entry(filter_frame, width=12)
        self.filter_date.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Температура >").grid(row=0, column=2)
        self.filter_temp = tk.Entry(filter_frame, width=8)
        self.filter_temp.grid(row=0, column=3, padx=5)
        tk.Label(filter_frame, text="°C").grid(row=0, column=4)

        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=0, column=5, padx=5)
        tk.Button(filter_frame, text="Сбросить", command=self.show_all).grid(row=0, column=6, padx=5)

        # --- Меню сохранения/загрузки ---
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Сохранить как JSON", command=self.save_to_json)
        file_menu.add_command(label="Загрузить из JSON", command=self.load_from_json)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        root.config(menu=menubar)

    def validate_date(self, date_str):
        """Проверка формата ДД.ММ.ГГГГ и реальной даты."""
        if not re.fullmatch(r'\d{2}\.\d{2}\.\d{4}', date_str):
            return False
        try:
            datetime.strptime(date_str, '%d.%m.%Y')
            return True
        except ValueError:
            return False

    def validate_temp(self, temp_str):
        try:
            float(temp_str)
            return True
        except ValueError:
            return False

    def add_entry(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        # Проверки
        if not date:
            messagebox.showerror("Ошибка", "Введите дату")
            return
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ДД.ММ.ГГГГ и быть корректной (например, 31.12.2023)")
            return
        if not temp:
            messagebox.showerror("Ошибка", "Введите температуру")
            return
        if not self.validate_temp(temp):
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        entry = {
            "date": date,
            "temperature": float(temp),
            "description": desc,
            "precipitation": precip
        }
        self.entries.append(entry)
        self.refresh_listbox()
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена")

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def refresh_listbox(self, entries_list=None):
        if entries_list is None:
            entries_list = self.entries
        self.listbox.delete(0, tk.END)
        for entry in entries_list:
            precip_str = "да" if entry["precipitation"] else "нет"
            line = f"{entry['date']} | {entry['temperature']}°C | {entry['description']} | Осадки: {precip_str}"
            self.listbox.insert(tk.END, line)

    def show_all(self):
        self.filter_date.delete(0, tk.END)
        self.filter_temp.delete(0, tk.END)
        self.refresh_listbox()

    def apply_filter(self):
        date_filter = self.filter_date.get().strip()
        temp_filter = self.filter_temp.get().strip()

        filtered = self.entries[:]

        if date_filter:
            if not self.validate_date(date_filter):
                messagebox.showerror("Ошибка", "Некорректный формат даты фильтра (ДД.ММ.ГГГГ)")
                return
            filtered = [e for e in filtered if e["date"] == date_filter]

        if temp_filter:
            try:
                threshold = float(temp_filter)
            except ValueError:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом")
                return
            filtered = [e for e in filtered if e["temperature"] > threshold]

        self.refresh_listbox(filtered)

    def save_to_json(self):
        if not self.entries:
            messagebox.showinfo("Информация", "Нет записей для сохранения")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.entries, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Сохранено", f"Записи сохранены в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Простейшая валидация структуры
            if not isinstance(data, list):
                raise ValueError("Ожидается список записей")
            for item in data:
                if not all(k in item for k in ("date", "temperature", "description", "precipitation")):
                    raise ValueError("Некорректная структура записи")
            self.entries = data
            self.refresh_listbox()
            messagebox.showinfo("Загружено", f"Загружено {len(self.entries)} записей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
