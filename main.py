import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class Quest:
    def __init__(self, title, description, quest_id=None, genre=None, difficulty=None):
        self.id = quest_id
        self.title = title
        self.description = description
        self.genre = genre
        self.difficulty = difficulty
        self.locations = []

    def add_location(self, location):
        self.locations.append(location)

    def add_task(self, task):
        if self.locations:
            self.locations[-1].add_task(task)
        else:
            print("Сначала создайте локацию!")

    def export(self):
        export_quest_to_pdf(self)


class Location:
    def __init__(self, name, description, location_id=None):
        self.id = location_id
        self.name = name
        self.description = description
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_info(self):
        return f"Локация: {self.name}\nОписание: {self.description}\nЗадания: {[task.title for task in self.tasks]}"


class Task:
    def __init__(self, title, description, task_id=None):
        self.id = task_id
        self.title = title
        self.description = description
        self.hints = []

    def add_hint(self, hint):
        self.hints.append(hint)

    def get_info(self):
        return f"Задание: {self.title}\nОписание: {self.description}\nПодсказки: {[hint.text for hint in self.hints]}"


class Hint:
    def __init__(self, text, hint_id=None):
        self.id = hint_id
        self.text = text

    def get_text(self):
        return self.text


def create_database():
    """Создает базу данных и таблицы"""
    conn = sqlite3.connect('quests.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            genre TEXT,
            difficulty TEXT,
            is_premade INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY,
            quest_id INTEGER,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY (quest_id) REFERENCES quests (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            location_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            FOREIGN KEY (location_id) REFERENCES locations (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hints (
            id INTEGER PRIMARY KEY,
            task_id INTEGER,
            text TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


def create_premade_quests():
    """Создает готовые квесты в базе данных"""
    conn = sqlite3.connect('quests.db')
    cursor = conn.cursor()

    # Удаляем старые готовые квесты
    cursor.execute('DELETE FROM quests WHERE is_premade = 1')

    # Квест 1: Детективное расследование
    cursor.execute('''
        INSERT INTO quests (title, description, genre, difficulty, is_premade)
        VALUES (?, ?, ?, ?, 1)
    ''', ("Тайна старого особняка",
          "Вы - частный детектив, получивший письмо от таинственного незнакомца. Вас приглашают расследовать исчезновение хозяина старинного особняка.",
          "Детектив", "Средний"))
    quest1_id = cursor.lastrowid

    # Локации для квеста 1
    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest1_id, "Вход в особняк", "Величественные дубовые двери, покрытые резьбой."))
    loc1_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc1_id, "Поговорить с дворецким", "Расспросите дворецкого о хозяине"))
    task1_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)',
                   (task1_id, "Дворецкий упоминает грозу в ночь исчезновения"))

    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc1_id, "Осмотреть прихожую", "Найдите улики в прихожей"))
    task2_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)', (task2_id, "На полу есть странные следы грязи"))

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest1_id, "Кабинет хозяина", "Просторная комната в викторианском стиле."))
    loc2_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc2_id, "Изучить документы", "Просмотрите бумаги на столе"))
    task3_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)', (task3_id, "Среди бумаг есть завещание"))

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest1_id, "Подвал", "Темное и сырое помещение"))
    loc3_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc3_id, "Обыскать подвал", "Найдите все, что может помочь"))
    task4_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)', (task4_id, "За ящиками есть потайная дверь"))

    # Квест 2: Фэнтези
    cursor.execute('''
        INSERT INTO quests (title, description, genre, difficulty, is_premade)
        VALUES (?, ?, ?, ?, 1)
    ''', ("Потерянный амулет дракона",
          "В королевстве эльфов украден древний амулет, поддерживающий магический баланс мира.",
          "Фэнтези", "Сложный"))
    quest2_id = cursor.lastrowid

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest2_id, "Зачарованный лес", "Древний лес, где тропинки постоянно меняются"))
    loc4_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc4_id, "Найти тропу к гномам", "Нужно найти верную дорогу через лес"))
    task5_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)', (task5_id, "Ориентируйтесь по мху на деревьях"))

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest2_id, "Подземелья гномов", "Огромные пещеры, освещенные кристаллами"))
    loc5_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc5_id, "Разгадать загадку стража", "Каменный голем задает загадки"))
    task6_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)',
                   (task6_id, "Что можно держать, не касаясь? (Голос)"))

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest2_id, "Логово дракона", "Величественная пещера на вершине горы"))
    loc6_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc6_id, "Убедить дракона", "Дракон не отдаст амулет просто так"))
    task7_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)',
                   (task7_id, "Объясните дракону, что без амулета магия исчезнет"))

    # Квест 3: Научная фантастика
    cursor.execute('''
        INSERT INTO quests (title, description, genre, difficulty, is_premade)
        VALUES (?, ?, ?, ?, 1)
    ''', ("Сбой на космической станции",
          "Вы - бортовой инженер на орбитальной станции. Вся электроника вышла из строя.",
          "Научная фантастика", "Легкий"))
    quest3_id = cursor.lastrowid

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest3_id, "Инженерный отсек", "Комната с панелями управления"))
    loc7_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc7_id, "Восстановить питание", "Нужно перезагрузить главный реактор"))
    task8_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)',
                   (task8_id, "Проверьте автоматические выключатели"))

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest3_id, "Лаборатория", "Исследовательский отсек с колбами и приборами"))
    loc8_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc8_id, "Найти антидот", "Создайте антидот от распространяющегося газа"))
    task9_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)', (task9_id, "В компьютере есть формула антидота"))

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest3_id, "Медицинский отсек", "Стерильное помещение с медоборудованием"))
    loc9_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc9_id, "Спасти команду", "Приведите членов экипажа в чувство"))
    task10_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)',
                   (task10_id, "Используйте антидот в системе вентиляции"))

    # Квест 4: Хоррор
    cursor.execute('''
        INSERT INTO quests (title, description, genre, difficulty, is_premade)
        VALUES (?, ?, ?, ?, 1)
    ''', ("Проклятие заброшенной школы",
          "Группа подростков решила провести ночь в заброшенной школе. Один из них исчез.",
          "Хоррор", "Средний"))
    quest4_id = cursor.lastrowid

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest4_id, "Главный коридор", "Длинный темный коридор с классами"))
    loc10_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc10_id, "Найти дневник", "В дневнике ученика может быть ключ к разгадке"))
    task11_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)', (task11_id, "Дневник в классе истории"))

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest4_id, "Кабинет директора", "Красиво обставленная комната"))
    loc11_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc11_id, "Исследовать архив", "В сейфе директора хранятся документы"))
    task12_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)', (task12_id, "Код от сейфа - 1903"))

    # Квест 5: Постапокалипсис
    cursor.execute('''
        INSERT INTO quests (title, description, genre, difficulty, is_premade)
        VALUES (?, ?, ?, ?, 1)
    ''', ("Выживание в Пустоши",
          "Мир после ядерной войны. Вы ищете древнее убежище с довоенными технологиями.",
          "Постапокалипсис", "Сложный"))
    quest5_id = cursor.lastrowid

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest5_id, "Разрушенный город", "Руины мегаполиса"))
    loc12_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc12_id, "Найти карту убежища", "У старого торговца есть карта"))
    task13_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)', (task13_id, "Торговец в бывшем метро"))

    cursor.execute('INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)',
                   (quest5_id, "Убежище 77", "Легендарное убежище для спасения человечества"))
    loc13_id = cursor.lastrowid
    cursor.execute('INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)',
                   (loc13_id, "Взломать главный компьютер", "Доступ к архивам закрыт"))
    task14_id = cursor.lastrowid
    cursor.execute('INSERT INTO hints (task_id, text) VALUES (?, ?)', (task14_id, "Пароль - Apocalypse2099"))

    conn.commit()
    conn.close()


def load_all_quests():
    """Загружает список всех квестов из БД"""
    conn = sqlite3.connect('quests.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, description, genre, difficulty, created_at, is_premade FROM quests ORDER BY created_at DESC')
    quests = cursor.fetchall()
    conn.close()
    return quests


def load_premade_quests():
    """Загружает только готовые квесты"""
    conn = sqlite3.connect('quests.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, description, genre, difficulty, created_at, is_premade FROM quests WHERE is_premade = 1 ORDER BY id')
    quests = cursor.fetchall()
    conn.close()
    return quests


def load_user_quests():
    """Загружает только пользовательские квесты"""
    conn = sqlite3.connect('quests.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, description, genre, difficulty, created_at, is_premade FROM quests WHERE is_premade = 0 ORDER BY created_at DESC')
    quests = cursor.fetchall()
    conn.close()
    return quests


def load_quest_by_id(quest_id):
    """Загружает полный квест по ID из БД"""
    conn = sqlite3.connect('quests.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, description, genre, difficulty, is_premade FROM quests WHERE id = ?', (quest_id,))
    quest_data = cursor.fetchone()

    if not quest_data:
        conn.close()
        return None

    quest = Quest(quest_data[1], quest_data[2], quest_data[0], quest_data[3], quest_data[4])

    cursor.execute('SELECT id, name, description FROM locations WHERE quest_id = ?', (quest_id,))
    locations_data = cursor.fetchall()

    for loc_data in locations_data:
        location = Location(loc_data[1], loc_data[2], loc_data[0])

        cursor.execute('SELECT id, title, description FROM tasks WHERE location_id = ?', (loc_data[0],))
        tasks_data = cursor.fetchall()

        for task_data in tasks_data:
            task = Task(task_data[1], task_data[2], task_data[0])

            cursor.execute('SELECT id, text FROM hints WHERE task_id = ?', (task_data[0],))
            hints_data = cursor.fetchall()

            for hint_data in hints_data:
                hint = Hint(hint_data[1], hint_data[0])
                task.add_hint(hint)

            location.add_task(task)

        quest.add_location(location)

    conn.close()
    return quest


def save_user_quest_to_db(quest):
    """Сохраняет пользовательский квест в БД"""
    conn = sqlite3.connect('quests.db')
    cursor = conn.cursor()

    if quest.id is None:
        cursor.execute('''
            INSERT INTO quests (title, description, genre, difficulty, is_premade) 
            VALUES (?, ?, ?, ?, 0)
        ''', (quest.title, quest.description, quest.genre, quest.difficulty))
        quest.id = cursor.lastrowid
    else:
        cursor.execute('SELECT is_premade FROM quests WHERE id = ?', (quest.id,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            cursor.execute('''
                INSERT INTO quests (title, description, genre, difficulty, is_premade) 
                VALUES (?, ?, ?, ?, 0)
            ''', (quest.title, quest.description, quest.genre, quest.difficulty))
            quest.id = cursor.lastrowid
        else:
            cursor.execute('''
                UPDATE quests SET title = ?, description = ?, genre = ?, difficulty = ? WHERE id = ?
            ''', (quest.title, quest.description, quest.genre, quest.difficulty, quest.id))
            cursor.execute('DELETE FROM locations WHERE quest_id = ?', (quest.id,))

    for location in quest.locations:
        cursor.execute('''
            INSERT INTO locations (quest_id, name, description) VALUES (?, ?, ?)
        ''', (quest.id, location.name, location.description))
        location.id = cursor.lastrowid

        for task in location.tasks:
            cursor.execute('''
                INSERT INTO tasks (location_id, title, description) VALUES (?, ?, ?)
            ''', (location.id, task.title, task.description))
            task.id = cursor.lastrowid

            for hint in task.hints:
                cursor.execute('''
                    INSERT INTO hints (task_id, text) VALUES (?, ?)
                ''', (task.id, hint.text))

    conn.commit()
    conn.close()


def delete_user_quest(quest_id):
    """Удаляет пользовательский квест из БД"""
    conn = sqlite3.connect('quests.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM quests WHERE id = ? AND is_premade = 0', (quest_id,))
    conn.commit()
    conn.close()


def export_quest_to_pdf(quest):
    """Экспорт квеста в PDF"""
    c = canvas.Canvas(f"{quest.title}.pdf", pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"Квест: {quest.title}")

    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Жанр: {quest.genre or 'Не указан'}")
    c.drawString(50, 710, f"Сложность: {quest.difficulty or 'Не указана'}")
    c.drawString(50, 690, f"Описание: {quest.description}")

    y = 650
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Структура квеста:")
    y -= 30

    c.setFont("Helvetica", 11)
    for location in quest.locations:
        if y < 100:
            c.showPage()
            y = 750
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "Структура квеста (продолжение):")
            y -= 30
            c.setFont("Helvetica", 11)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"📍 Локация: {location.name}")
        y -= 20
        c.setFont("Helvetica", 11)
        c.drawString(60, y, f"Описание: {location.description}")
        y -= 20

        for task in location.tasks:
            if y < 100:
                c.showPage()
                y = 750
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y, f"📍 Локация: {location.name} (продолжение)")
                y -= 20

            c.setFont("Helvetica-Bold", 11)
            c.drawString(70, y, f"📝 Задание: {task.title}")
            y -= 15
            c.setFont("Helvetica", 10)
            c.drawString(80, y, f"{task.description}")
            y -= 15

            if task.hints:
                c.setFont("Helvetica-Oblique", 10)
                for hint in task.hints:
                    if y < 80:
                        c.showPage()
                        y = 750
                    c.drawString(90, y, f"💡 Подсказка: {hint.text}")
                    y -= 12
            y -= 10

    c.save()


class QuestApp:
    def __init__(self, master):
        self.master = master
        master.title("Система создания квестов")
        master.geometry("600x700")

        self.current_quest = None
        self.current_location = None

        # Создаем БД при запуске
        create_database()

        # Создаем готовые квесты
        create_premade_quests()

        # Показываем главное меню
        self.show_main_menu()

    def show_main_menu(self):
        """Показывает главное меню выбора"""
        for widget in self.master.winfo_children():
            widget.destroy()

        title_label = tk.Label(self.master, text="Система создания квестов",
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=20)

        new_quest_btn = tk.Button(self.master, text="➕ Создать новый квест",
                                  command=self.create_new_quest_interface,
                                  font=("Arial", 12), bg="green", fg="white",
                                  width=30, height=2)
        new_quest_btn.pack(pady=10)

        load_quest_btn = tk.Button(self.master, text="📂 Мои квесты",
                                   command=self.show_user_quests,
                                   font=("Arial", 12), bg="blue", fg="white",
                                   width=30, height=2)
        load_quest_btn.pack(pady=10)

        premade_quests_btn = tk.Button(self.master, text="✨ Готовые квесты",
                                       command=self.show_premade_quests,
                                       font=("Arial", 12), bg="purple", fg="white",
                                       width=30, height=2)
        premade_quests_btn.pack(pady=10)

        # Статистика
        user_quests = load_user_quests()
        premade_quests = load_premade_quests()

        stats_frame = tk.Frame(self.master)
        stats_frame.pack(pady=20)

        stats_label = tk.Label(stats_frame,
                               text=f"📊 Статистика:\nСоздано квестов: {len(user_quests)}\nГотовых квестов: {len(premade_quests)}",
                               font=("Arial", 10), fg="gray", justify=tk.LEFT)
        stats_label.pack()

    def show_premade_quests(self):
        """Показывает список готовых квестов"""
        for widget in self.master.winfo_children():
            widget.destroy()

        title_label = tk.Label(self.master, text="✨ Готовые квесты",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        description_label = tk.Label(self.master,
                                     text="Готовые квесты для игры (только для просмотра)",
                                     font=("Arial", 10), fg="gray")
        description_label.pack(pady=5)

        premade_quests = load_premade_quests()

        if not premade_quests:
            no_quests_label = tk.Label(self.master, text="Нет готовых квестов",
                                       font=("Arial", 12), fg="red")
            no_quests_label.pack(pady=20)
            back_btn = tk.Button(self.master, text="◀ Назад", command=self.show_main_menu,
                                 font=("Arial", 10))
            back_btn.pack(pady=10)
            return

        frame = tk.Frame(self.master)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Arial", 11),
                             height=15, width=60)

        quest_ids = []
        for quest in premade_quests:
            display_text = f"⭐ {quest[1]} | Жанр: {quest[3]} | Сложность: {quest[4]}"
            listbox.insert(tk.END, display_text)
            quest_ids.append(quest[0])

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        def view_selected():
            selection = listbox.curselection()
            if selection:
                quest_id = quest_ids[selection[0]]
                quest = load_quest_by_id(quest_id)
                if quest:
                    self.current_quest = quest
                    self.show_quest_preview()
                else:
                    messagebox.showerror("Ошибка", "Не удалось загрузить квест")
            else:
                messagebox.showwarning("Внимание", "Выберите квест из списка")

        def copy_selected():
            selection = listbox.curselection()
            if selection:
                quest_id = quest_ids[selection[0]]
                quest = load_quest_by_id(quest_id)
                if quest:
                    new_quest = Quest(
                        f"Копия: {quest.title}",
                        quest.description,
                        genre=quest.genre,
                        difficulty=quest.difficulty
                    )

                    for location in quest.locations:
                        new_location = Location(location.name, location.description)
                        for task in location.tasks:
                            new_task = Task(task.title, task.description)
                            for hint in task.hints:
                                new_task.add_hint(Hint(hint.text))
                            new_location.add_task(new_task)
                        new_quest.add_location(new_location)

                    save_user_quest_to_db(new_quest)
                    messagebox.showinfo("Успех", "Квест скопирован в 'Мои квесты'!")
                    self.show_main_menu()
                else:
                    messagebox.showerror("Ошибка", "Не удалось скопировать квест")
            else:
                messagebox.showwarning("Внимание", "Выберите квест из списка")

        view_btn = tk.Button(self.master, text="👁️ Просмотреть",
                             command=view_selected, font=("Arial", 11),
                             bg="green", fg="white", width=15)
        view_btn.pack(side=tk.LEFT, padx=10, pady=10)

        copy_btn = tk.Button(self.master, text="📋 Скопировать в мои квесты",
                             command=copy_selected, font=("Arial", 11),
                             bg="orange", fg="white", width=25)
        copy_btn.pack(side=tk.LEFT, padx=10, pady=10)

        back_btn = tk.Button(self.master, text="◀ Назад", command=self.show_main_menu,
                             font=("Arial", 10))
        back_btn.pack(side=tk.RIGHT, padx=10, pady=10)

    def show_user_quests(self):
        """Показывает список пользовательских квестов"""
        for widget in self.master.winfo_children():
            widget.destroy()

        title_label = tk.Label(self.master, text="📂 Мои квесты",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        description_label = tk.Label(self.master,
                                     text="Ваши созданные квесты (для редактирования)",
                                     font=("Arial", 10), fg="gray")
        description_label.pack(pady=5)

        user_quests = load_user_quests()

        if not user_quests:
            no_quests_label = tk.Label(self.master, text="У вас пока нет созданных квестов",
                                       font=("Arial", 12), fg="red")
            no_quests_label.pack(pady=20)

            create_btn = tk.Button(self.master, text="➕ Создать новый квест",
                                   command=self.create_new_quest_interface,
                                   font=("Arial", 11), bg="green", fg="white")
            create_btn.pack(pady=10)

            back_btn = tk.Button(self.master, text="◀ Назад", command=self.show_main_menu,
                                 font=("Arial", 10))
            back_btn.pack(pady=10)
            return

        frame = tk.Frame(self.master)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Arial", 11),
                             height=15, width=60)

        quest_ids = []
        for quest in user_quests:
            display_text = f"{quest[1]} | Жанр: {quest[3] or 'Не указан'} | Сложность: {quest[4] or 'Не указана'}"
            listbox.insert(tk.END, display_text)
            quest_ids.append(quest[0])

        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        def edit_selected():
            selection = listbox.curselection()
            if selection:
                quest_id = quest_ids[selection[0]]
                quest = load_quest_by_id(quest_id)
                if quest:
                    self.current_quest = quest
                    self.show_quest_editor()
                else:
                    messagebox.showerror("Ошибка", "Не удалось загрузить квест")
            else:
                messagebox.showwarning("Внимание", "Выберите квест из списка")

        def delete_selected():
            selection = listbox.curselection()
            if selection:
                if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот квест?"):
                    quest_id = quest_ids[selection[0]]
                    delete_user_quest(quest_id)
                    messagebox.showinfo("Успех", "Квест удален")
                    self.show_user_quests()
            else:
                messagebox.showwarning("Внимание", "Выберите квест из списка")

        edit_btn = tk.Button(self.master, text="✏️ Редактировать",
                             command=edit_selected, font=("Arial", 11),
                             bg="blue", fg="white", width=15)
        edit_btn.pack(side=tk.LEFT, padx=10, pady=10)

        delete_btn = tk.Button(self.master, text="🗑️ Удалить",
                               command=delete_selected, font=("Arial", 11),
                               bg="red", fg="white", width=15)
        delete_btn.pack(side=tk.LEFT, padx=10, pady=10)

        back_btn = tk.Button(self.master, text="◀ Назад", command=self.show_main_menu,
                             font=("Arial", 10))
        back_btn.pack(side=tk.RIGHT, padx=10, pady=10)

    def show_quest_preview(self):
        """Показывает предпросмотр квеста (только для чтения)"""
        for widget in self.master.winfo_children():
            widget.destroy()

        title_frame = tk.Frame(self.master, bg="lightblue", relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        quest_title = tk.Label(title_frame,
                               text=f"📖 {self.current_quest.title}",
                               font=("Arial", 16, "bold"), bg="lightblue")
        quest_title.pack(pady=5)

        info_frame = tk.Frame(title_frame, bg="lightblue")
        info_frame.pack(pady=5)

        if self.current_quest.genre:
            genre_label = tk.Label(info_frame, text=f"Жанр: {self.current_quest.genre}",
                                   font=("Arial", 10), bg="lightblue")
            genre_label.pack(side=tk.LEFT, padx=10)

        if self.current_quest.difficulty:
            diff_label = tk.Label(info_frame, text=f"Сложность: {self.current_quest.difficulty}",
                                  font=("Arial", 10), bg="lightblue")
            diff_label.pack(side=tk.LEFT, padx=10)

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)
        back_btn = tk.Button(button_frame, text="◀ Назад",
                             command=self.show_premade_quests,
                             bg="gray", fg="white", font=("Arial", 10))
        back_btn.pack(side=tk.LEFT, padx=5)

        copy_btn = tk.Button(button_frame, text="📋 Скопировать в мои квесты",
                             command=self.copy_current_quest,
                             bg="orange", fg="white", font=("Arial", 10))
        copy_btn.pack(side=tk.LEFT, padx=5)

        export_btn = tk.Button(button_frame, text="📄 Экспорт в PDF",
                               command=self.export_quest,
                               bg="red", fg="white", font=("Arial", 10))
        export_btn.pack(side=tk.LEFT, padx=5)

        self.info_text = tk.Text(self.master, height=25, width=70, font=("Arial", 10),
                                 bg="lightyellow", state="normal")
        self.info_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.update_info()
        self.info_text.config(state="disabled")

    def copy_current_quest(self):
        """Копирует текущий квест в пользовательские"""
        if self.current_quest:
            new_quest = Quest(
                f"Копия: {self.current_quest.title}",
                self.current_quest.description,
                genre=self.current_quest.genre,
                difficulty=self.current_quest.difficulty
            )

            for location in self.current_quest.locations:
                new_location = Location(location.name, location.description)
                for task in location.tasks:
                    new_task = Task(task.title, task.description)
                    for hint in task.hints:
                        new_task.add_hint(Hint(hint.text))
                    new_location.add_task(new_task)
                new_quest.add_location(new_location)

            save_user_quest_to_db(new_quest)
            messagebox.showinfo("Успех", "Квест скопирован в 'Мои квесты'!")
            self.show_main_menu()

    def create_new_quest_interface(self):
        """Показывает интерфейс создания нового квеста"""
        for widget in self.master.winfo_children():
            widget.destroy()

        title_label = tk.Label(self.master, text="Создание нового квеста",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        frame = tk.Frame(self.master)
        frame.pack(pady=20, padx=20)

        tk.Label(frame, text="Название квеста:", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        self.new_title_entry = tk.Entry(frame, width=40, font=("Arial", 11))
        self.new_title_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Описание квеста:", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=5)
        self.new_description_entry = tk.Text(frame, width=40, height=5, font=("Arial", 11))
        self.new_description_entry.grid(row=1, column=1, pady=5)

        tk.Label(frame, text="Жанр (необязательно):", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=5)
        self.new_genre_entry = tk.Entry(frame, width=40, font=("Arial", 11))
        self.new_genre_entry.grid(row=2, column=1, pady=5)

        tk.Label(frame, text="Сложность (необязательно):", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=5)
        self.new_difficulty_combo = ttk.Combobox(frame, values=["Легкий", "Средний", "Сложный"], width=37)
        self.new_difficulty_combo.grid(row=3, column=1, pady=5)

        def create_and_continue():
            title = self.new_title_entry.get()
            description = self.new_description_entry.get("1.0", tk.END).strip()
            genre = self.new_genre_entry.get() or None
            difficulty = self.new_difficulty_combo.get() or None

            if title and description:
                self.current_quest = Quest(title, description, genre=genre, difficulty=difficulty)
                save_user_quest_to_db(self.current_quest)
                messagebox.showinfo("Успех", "Квест создан!")
                self.show_quest_editor()
            else:
                messagebox.showwarning("Внимание", "Пожалуйста, заполните название и описание квеста!")

        create_btn = tk.Button(self.master, text="✅ Создать и продолжить",
                               command=create_and_continue, font=("Arial", 11),
                               bg="green", fg="white", width=25)
        create_btn.pack(pady=10)

        back_btn = tk.Button(self.master, text="◀ Назад", command=self.show_main_menu,
                             font=("Arial", 10))
        back_btn.pack(pady=5)

    def show_quest_editor(self):
        """Показывает основной редактор квеста"""
        for widget in self.master.winfo_children():
            widget.destroy()

        info_frame = tk.Frame(self.master, bg="lightgray", relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        quest_info = tk.Label(info_frame,
                              text=f"Текущий квест: {self.current_quest.title}",
                              font=("Arial", 14, "bold"), bg="lightgray")
        quest_info.pack(pady=5)

        if self.current_quest.genre or self.current_quest.difficulty:
            details_frame = tk.Frame(info_frame, bg="lightgray")
            details_frame.pack(pady=5)

            if self.current_quest.genre:
                genre_label = tk.Label(details_frame, text=f"Жанр: {self.current_quest.genre}",
                                       font=("Arial", 10), bg="lightgray")
                genre_label.pack(side=tk.LEFT, padx=10)

            if self.current_quest.difficulty:
                diff_label = tk.Label(details_frame, text=f"Сложность: {self.current_quest.difficulty}",
                                      font=("Arial", 10), bg="lightgray")
                diff_label.pack(side=tk.LEFT, padx=10)

        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        add_location_btn = tk.Button(button_frame, text="📍 Добавить локацию",
                                     command=self.add_location,
                                     bg="blue", fg="white", font=("Arial", 10), width=18)
        add_location_btn.grid(row=0, column=0, padx=5)

        add_task_btn = tk.Button(button_frame, text="📝 Добавить задание",
                                 command=self.add_task,
                                 bg="orange", fg="white", font=("Arial", 10), width=18)
        add_task_btn.grid(row=0, column=1, padx=5)

        add_hint_btn = tk.Button(button_frame, text="💡 Добавить подсказку",
                                 command=self.add_hint,
                                 bg="purple", fg="white", font=("Arial", 10), width=18)
        add_hint_btn.grid(row=0, column=2, padx=5)

        export_btn = tk.Button(button_frame, text="📄 Экспорт в PDF",
                               command=self.export_quest,
                               bg="red", fg="white", font=("Arial", 10), width=18)
        export_btn.grid(row=1, column=0, columnspan=3, pady=5)

        save_btn = tk.Button(button_frame, text="💾 Сохранить квест",
                             command=self.save_current_quest,
                             bg="green", fg="white", font=("Arial", 10), width=18)
        save_btn.grid(row=2, column=0, columnspan=3, pady=5)

        back_to_menu_btn = tk.Button(button_frame, text="🏠 Главное меню",
                                     command=self.return_to_menu,
                                     bg="gray", fg="white", font=("Arial", 10), width=18)
        back_to_menu_btn.grid(row=3, column=0, columnspan=3, pady=5)

        self.info_text = tk.Text(self.master, height=20, width=70, font=("Arial", 10))
        self.info_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.update_info()

    def save_current_quest(self):
        """Сохраняет текущий квест в БД"""
        save_user_quest_to_db(self.current_quest)
        messagebox.showinfo("Успех", "Квест успешно сохранен!")
        self.update_info()

    def return_to_menu(self):
        """Возврат в главное меню с сохранением"""
        if self.current_quest:
            answer = messagebox.askyesno("Сохранение",
                                         "Сохранить изменения перед выходом?")
            if answer:
                save_user_quest_to_db(self.current_quest)
        self.show_main_menu()

    def add_location(self):
        """Добавляет новую локацию"""
        name = simpledialog.askstring("Локация", "Введите название локации:",
                                      parent=self.master)
        if not name:
            return

        description = simpledialog.askstring("Локация", "Введите описание локации:",
                                             parent=self.master)
        if not description:
            return

        location = Location(name, description)
        self.current_quest.add_location(location)
        self.current_location = location
        self.update_info()
        messagebox.showinfo("Успех", "Локация добавлена!")

    def add_task(self):
        """Добавляет новое задание в текущую локацию"""
        if not self.current_quest.locations:
            messagebox.showwarning("Внимание", "Сначала создайте локацию!")
            return

        if not self.current_location or self.current_location not in self.current_quest.locations:
            locations_names = [loc.name for loc in self.current_quest.locations]
            choice = simpledialog.askstring("Выбор локации",
                                            f"Выберите локацию из списка:\n{', '.join(locations_names)}")
            if choice:
                for loc in self.current_quest.locations:
                    if loc.name == choice:
                        self.current_location = loc
                        break
            else:
                return

        title = simpledialog.askstring("Задание", "Введите название задания:")
        if not title:
            return

        description = simpledialog.askstring("Задание", "Введите описание задания:")
        if not description:
            return

        task = Task(title, description)
        self.current_location.add_task(task)
        self.update_info()
        messagebox.showinfo("Успех", "Задание добавлено!")

    def add_hint(self):
        """Добавляет подсказку к последнему заданию"""
        if not self.current_location or not self.current_location.tasks:
            messagebox.showwarning("Внимание", "Сначала создайте задание!")
            return

        hint_text = simpledialog.askstring("Подсказка", "Введите текст подсказки:")
        if hint_text:
            hint = Hint(hint_text)
            self.current_location.tasks[-1].add_hint(hint)
            self.update_info()
            messagebox.showinfo("Успех", "Подсказка добавлена!")

    def export_quest(self):
        """Экспортирует квест в PDF"""
        if self.current_quest:
            try:
                self.current_quest.export()
                messagebox.showinfo("Успех", f"Квест экспортирован в {self.current_quest.title}.pdf")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать квест: {str(e)}")

    def update_info(self):
        """Обновляет отображение информации о квесте"""
        if not hasattr(self, 'info_text'):
            return

        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)

        if self.current_quest:
            self.info_text.insert(tk.END, f"📖 КВЕСТ: {self.current_quest.title}\n")
            self.info_text.insert(tk.END, f"{'=' * 60}\n")
            self.info_text.insert(tk.END, f"Описание: {self.current_quest.description}\n\n")

            if self.current_quest.genre:
                self.info_text.insert(tk.END, f"Жанр: {self.current_quest.genre}\n")
            if self.current_quest.difficulty:
                self.info_text.insert(tk.END, f"Сложность: {self.current_quest.difficulty}\n\n")

            if not self.current_quest.locations:
                self.info_text.insert(tk.END, "⚠️ Нет добавленных локаций\n")
                self.info_text.insert(tk.END, "Нажмите 'Добавить локацию' для начала\n")
            else:
                self.info_text.insert(tk.END, f"🏰 ЛОКАЦИИ ({len(self.current_quest.locations)}):\n\n")

                for i, location in enumerate(self.current_quest.locations, 1):
                    self.info_text.insert(tk.END, f"  {i}. {location.name}\n")
                    self.info_text.insert(tk.END, f"     {location.description}\n")

                    if location.tasks:
                        self.info_text.insert(tk.END, f"     📌 ЗАДАНИЯ:\n")
                        for j, task in enumerate(location.tasks, 1):
                            self.info_text.insert(tk.END, f"        {j}. {task.title}\n")
                            self.info_text.insert(tk.END, f"           {task.description}\n")

                            if task.hints:
                                self.info_text.insert(tk.END, f"           💡 Подсказки:\n")
                                for k, hint in enumerate(task.hints, 1):
                                    self.info_text.insert(tk.END, f"              {k}. {hint.text}\n")
                            else:
                                self.info_text.insert(tk.END, f"           (нет подсказок)\n")
                    else:
                        self.info_text.insert(tk.END, f"     (нет заданий)\n")
                    self.info_text.insert(tk.END, "\n")

        self.info_text.config(state="disabled")
if __name__ == "__main__":
    root = tk.Tk()
    app = QuestApp(root)
    root.mainloop()