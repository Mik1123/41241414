import sys
import pymysql
from PyQt6.QtWidgets import *

def get_connection():
    return pymysql.connect(host='localhost', user='root', password='root', database='restaurant_db', port=3307)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        layout = QVBoxLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("Логин")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        button = QPushButton("Войти")
        button.clicked.connect(self.login_check)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(button)
        self.setLayout(layout)
        self.resize(250, 150)
    
    def login_check(self):
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, password_hash, role_id FROM Users WHERE username = %s", (self.username.text(),))
        user = cursor.fetchone()
        connection.close()
        if not user or self.password.text() != user[1]:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return
        if user[2] == 1:
            self.admin = AdminPanel()
            self.admin.show()
        else:
            self.client = ClientPanel()
            self.client.show()
        self.close()

class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Админ")
        layout = QVBoxLayout()
        self.list = QListWidget()
        add = QPushButton("Добавить")
        add.clicked.connect(self.add_food)
        delete = QPushButton("Удалить")
        delete.clicked.connect(self.delete_food)
        exit_btn = QPushButton("Выход")
        exit_btn.clicked.connect(self.exit)
        layout.addWidget(self.list)
        layout.addWidget(add)
        layout.addWidget(delete)
        layout.addWidget(exit_btn)
        self.setLayout(layout)
        self.resize(350, 400)
        self.load()
    
    def load(self):
        self.list.clear()
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT item_id, name, price FROM MenuItems WHERE is_available = 1")
        self.items = cursor.fetchall()
        connection.close()
        for item in self.items:
            self.list.addItem(f"{item[1]} - {item[2]} руб")
    
    def add_food(self):
        name, ok = QInputDialog.getText(self, "Новое", "Название:")
        if ok and name:
            price, ok = QInputDialog.getDouble(self, "Цена", "Цена:")
            if ok:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute("INSERT INTO MenuItems (name, price, is_available) VALUES (%s, %s, 1)", (name, price))
                connection.commit()
                connection.close()
                self.load()
    
    def delete_food(self):
        row = self.list.currentRow()
        if row >= 0:
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("UPDATE MenuItems SET is_available = 0 WHERE item_id = %s", (self.items[row][0],))
            connection.commit()
            connection.close()
            self.load()
    
    def exit(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()

class ClientPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Клиент")
        layout = QVBoxLayout()
        self.list = QListWidget()
        exit_btn = QPushButton("Выход")
        exit_btn.clicked.connect(self.exit)
        layout.addWidget(QLabel("Меню:"))
        layout.addWidget(self.list)
        layout.addWidget(exit_btn)
        self.setLayout(layout)
        self.resize(350, 400)
        self.load()
    
    def load(self):
        self.list.clear()
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT name, price FROM MenuItems WHERE is_available = 1")
        items = cursor.fetchall()
        connection.close()
        for item in items:
            self.list.addItem(f"{item[0]} - {item[1]} руб")
    
    def exit(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()

app = QApplication(sys.argv)
start = LoginWindow()
start.show()
sys.exit(app.exec())
