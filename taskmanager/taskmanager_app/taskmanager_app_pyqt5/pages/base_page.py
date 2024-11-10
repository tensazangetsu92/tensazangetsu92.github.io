import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QMessageBox

from .collection_page import CollectionPage  # Импорт класса CollectionPage
import subprocess
import os
import requests


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.start_django_server()  # Запуск сервера Django
        self.initUI()
        self.load_collections()

    def start_django_server(self):
        django_command = [r"C:\Users\alex\PycharmProjects\TaskManager\.venv\Scripts\python.exe",
                          r"C:\Users\alex\PycharmProjects\TaskManager\taskmanager\manage.py", "runserver", '--noreload']

        try:
            if os.name == 'nt':  # Windows
                self.server_process = subprocess.Popen(django_command, creationflags=subprocess.CREATE_NO_WINDOW,
                                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:  # Linux / macOS
                self.server_process = subprocess.Popen(django_command, preexec_fn=os.setsid)
        except Exception as e:
            print(f"Ошибка при запуске сервера Django: {str(e)}")

    def initUI(self):
        self.setWindowTitle('Django + PyQt5 Task Manager')
        self.setFixedSize(600, 700)
        self.confirmation_dialog = None

        # Стек виджетов для переключения страниц
        self.stack = QStackedWidget(self)

        # Создаем главную страницу
        self.main_page = QWidget()
        layout = QVBoxLayout(self.main_page)

        # Поле для ввода названия новой коллекции
        self.collection_input = QLineEdit(self.main_page)
        self.collection_input.setObjectName('collection_input')
        self.collection_input.setPlaceholderText("Enter collection name")
        self.collection_input.returnPressed.connect(self.add_collection)
        layout.addWidget(self.collection_input)

        # Кнопка для добавления новой коллекции
        add_collection_button = QPushButton('Add Collection', self.main_page)
        add_collection_button.clicked.connect(self.add_collection)
        add_collection_button.setMinimumHeight(70)
        layout.addWidget(add_collection_button)

        # Метка для отображения статуса
        self.status_label = QLabel('Status will be displayed here')
        self.status_label.setObjectName('status_label')
        layout.addWidget(self.status_label)

        # Список для отображения коллекций
        self.collection_list = QListWidget(self.main_page)
        self.collection_list.itemDoubleClicked.connect(self.open_collection_page)
        layout.addWidget(self.collection_list)

        self.stack.addWidget(self.main_page)  # Добавляем главную страницу в стек
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stack)  # Устанавливаем стек в основной layout

        if getattr(sys, 'frozen', False):
            static_css_path = os.path.join(Path(__file__).resolve().parent.parent.parent, "css_pages","base_page_css.css")
        else:
            static_css_path = os.path.join(Path(__file__).resolve().parent.parent.parent, "static",
                                           "css_pages", "base_page_css.css")

        with open(static_css_path, "r", encoding='utf-8') as file:
            self.setStyleSheet(file.read())

    def load_collections(self):
        try:
            response = requests.get('http://127.0.0.1:8000/myapp/show_collections/')  # Замените URL на ваш
            if response.status_code == 200:
                collections = response.json()
                self.collection_list.clear()  # Очищаем список перед обновлением

                for collection in collections:
                    list_item = QListWidgetItem(self.collection_list)
                    list_item.setData(Qt.UserRole, collection['id'])  # ID коллекции
                    list_item.setData(Qt.UserRole + 1, collection['collection_name'])  # Название коллекции

                    item_widget = QWidget()
                    item_widget.setMinimumHeight(60)
                    item_widget.setObjectName("item_widget")
                    layout = QHBoxLayout()

                    collection_label = QLabel(collection['collection_name'])

                    delete_button = QPushButton('Delete collection', self)
                    delete_button.clicked.connect(lambda _, id=collection['id']: self.delete_collection(id))
                    delete_button.setMinimumHeight(60)

                    layout.addWidget(collection_label)
                    layout.addStretch()
                    layout.addWidget(delete_button)
                    item_widget.setLayout(layout)

                    list_item.setSizeHint(item_widget.sizeHint())  # Устанавливаем размер элемента списка
                    self.collection_list.setItemWidget(list_item, item_widget)

                if self.collection_list.count() > 0:
                    self.collection_list.setCurrentRow(0)  # Устанавливаем текущий элемент на первый
                    self.collection_list.setFocus()  # Устанавливаем фокус на QListWidget

            else:
                self.status_label.setText(f"Error loading collections: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.status_label.setText(f"Error loading collections: {str(e)}")

    def add_collection(self):
        collection_name = self.collection_input.text()
        if collection_name:
            data = {'collection_name': collection_name}
            response = requests.post('http://127.0.0.1:8000/myapp/add_collection/', json=data)

            if response.status_code == 201:
                self.status_label.setText('Collection added successfully!')
                self.load_collections()  # Обновляем список коллекций
                self.collection_input.setText('')
                self.collection_list.setCurrentRow(self.collection_list.count() - 1)
                self.collection_list.setFocus()
            else:
                self.status_label.setText(f"Error: {response.status_code}")
        else:
            self.status_label.setText('Please enter a collection name!')

    def delete_collection(self, collection_id):
        # Создаем окно подтверждения
        self.confirmation_dialog = QMessageBox(self)
        self.confirmation_dialog.setWindowTitle("Delete Confirmation")
        self.confirmation_dialog.setText("Are you sure you want to delete this collection?")

        # Создаем свои кнопки и добавляем их в нужном порядке
        no_button = self.confirmation_dialog.addButton("No", QMessageBox.RejectRole)
        yes_button = self.confirmation_dialog.addButton("Yes", QMessageBox.AcceptRole)

        # Показываем диалог и обрабатываем ответ
        self.confirmation_dialog.exec_()

        if self.confirmation_dialog.clickedButton() == yes_button:
            try:
                if collection_id:
                    response = requests.delete(f'http://127.0.0.1:8000/myapp/delete_collection/{collection_id}/')
                    if response.status_code == 204:  # 204 No Content
                        self.status_label.setText('Collection deleted successfully!')
                        self.load_collections()  # Обновляем список коллекций
                    else:
                        self.status_label.setText(f"Error: {response.status_code}")
                else:
                    self.status_label.setText('No collection ID provided!')
            except requests.exceptions.RequestException as e:
                self.status_label.setText(f"Error deleting collection: {str(e)}")
        else:
            # Если пользователь нажал "Нет", ничего не делаем
            self.status_label.setText('Collection deletion cancelled.')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            current_item = self.collection_list.currentItem()
            if current_item:
                self.open_collection_page(current_item)
        elif self.confirmation_dialog and self.confirmation_dialog.isVisible():
            # Проверяем, активен ли диалог подтверждения и нажата ли клавиша Enter
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.confirmation_dialog.done(QMessageBox.Yes)
                self.confirmation_dialog = None  # Сбрасываем флаг после обработки

    def closeEvent(self, event):
        # Убираем ссылку на диалог при закрытии окна
        if self.confirmation_dialog:
            self.confirmation_dialog.close()
            self.confirmation_dialog = None
        if self.server_process:
            self.server_process.terminate()  # Останавливаем сервер
        event.accept()

    def open_collection_page(self, item):
        """Переход на страницу с деталями выбранной коллекции."""
        collection_id = item.data(Qt.UserRole)  # Извлекаем ID коллекции
        collection_name = item.data(Qt.UserRole + 1)  # Извлекаем название коллекции

        collection_page = CollectionPage(collection_id, collection_name, self.stack, self)
        self.stack.addWidget(collection_page)
        self.stack.setCurrentWidget(collection_page)


if __name__ == "__main__":
    app = QApplication([])
    window = App()
    window.show()
    app.exec_()
