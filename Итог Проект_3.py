import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os

# ------------------ Генератор ------------------
def generate_password(length, use_digits, use_letters, use_symbols):
    chars = ''
    if use_digits:
        chars += string.digits
    if use_letters:
        chars += string.ascii_letters
    if use_symbols:
        chars += string.punctuation
    if not chars:
        return "Выберите хотя бы один тип символов"
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

# ------------------ Работа с JSON ------------------
HISTORY_FILE = "password_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def add_to_history(password, length, use_digits, use_letters, use_symbols):
    history = load_history()
    record = {
        "password": password,
        "length": length,
        "digits": use_digits,
        "letters": use_letters,
        "symbols": use_symbols
    }
    history.append(record)
    save_history(history)
    return history

# ------------------ GUI ------------------
class PasswordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Переменные
        self.password_length = tk.IntVar(value=12)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        # Верхняя панель настроек
        settings_frame = ttk.LabelFrame(root, text="Настройки пароля", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky="w")
        self.length_scale = ttk.Scale(settings_frame, from_=4, to=32, variable=self.password_length, orient="horizontal")
        self.length_scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.length_label = ttk.Label(settings_frame, text="12")
        self.length_label.grid(row=0, column=2, padx=5)
        self.length_scale.config(command=lambda x: self.length_label.config(text=str(int(float(x)))))

        ttk.Checkbutton(settings_frame, text="Цифры (0-9)", variable=self.use_digits).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(settings_frame, text="Буквы (A-z)", variable=self.use_letters).grid(row=1, column=1, sticky="w")
        ttk.Checkbutton(settings_frame, text="Спецсимволы (!@#$...)", variable=self.use_symbols).grid(row=1, column=2, sticky="w")

        # Кнопка генерации
        self.generate_btn = ttk.Button(root, text="Сгенерировать пароль", command=self.generate)
        self.generate_btn.pack(pady=10)

        # Поле результата
        result_frame = ttk.LabelFrame(root, text="Сгенерированный пароль", padding=10)
        result_frame.pack(fill="x", padx=10, pady=5)
        self.result_entry = ttk.Entry(result_frame, font=("Courier", 12))
        self.result_entry.pack(fill="x", padx=5, pady=5)
        self.copy_btn = ttk.Button(result_frame, text="Копировать в буфер", command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=5)

        # Таблица истории
        history_frame = ttk.LabelFrame(root, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(history_frame, columns=("password", "length", "chars"), show="headings")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("length", text="Длина")
        self.tree.heading("chars", text="Использованные символы")
        self.tree.column("password", width=250)
        self.tree.column("length", width=60)
        self.tree.column("chars", width=250)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопки управления историей
        btn_frame = ttk.Frame(history_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Обновить таблицу", command=self.refresh_history).pack(side="left", padx=5)

        # Загружаем историю при старте
        self.refresh_history()

        # Проверка минимальной длины при генерации будет в методе generate

    def generate(self):
        length = int(self.password_length.get())
        digits = self.use_digits.get()
        letters = self.use_letters.get()
        symbols = self.use_symbols.get()

        # Проверка: длина
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля — 4 символа")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля — 32 символа")
            return

        # Проверка: хотя бы один тип символов
        if not (digits or letters or symbols):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return

        pwd = generate_password(length, digits, letters, symbols)
        self.result_entry.delete(0, tk.END)
        self.result_entry.insert(0, pwd)

        # Сохраняем в историю
        chars_types = []
        if digits: chars_types.append("цифры")
        if letters: chars_types.append("буквы")
        if symbols: chars_types.append("спецсимволы")
        add_to_history(pwd, length, digits, letters, symbols)
        self.refresh_history()

    def copy_to_clipboard(self):
        pwd = self.result_entry.get()
        if pwd:
            self.root.clipboard_clear()
            self.root.clipboard_append(pwd)
            messagebox.showinfo("Скопировано", "Пароль скопирован в буфер обмена")

    def refresh_history(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        history = load_history()
        for rec in history:
            chars_desc = []
            if rec["digits"]: chars_desc.append("цифры")
            if rec["letters"]: chars_desc.append("буквы")
            if rec["symbols"]: chars_desc.append("спец.")
            desc = ", ".join(chars_desc) if chars_desc else "нет"
            self.tree.insert("", "end", values=(rec["password"], rec["length"], desc))

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю паролей?"):
            save_history([])
            self.refresh_history()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordApp(root)
    root.mainloop()
