import sys
from PyQt6.QtWidgets import QApplication
from views.main_view import MainView
from presenters.data_presenter import DataPresenter
from utils.logger import setup_logging

def main():
    # Настройка логирования
    setup_logging()
    
    # Создание приложения
    app = QApplication(sys.argv)
    
    # Создание и настройка главного окна
    view = MainView()
    presenter = DataPresenter(view)
    view.set_presenter(presenter)  # Устанавливаем презентер
    
    # Показ окна
    view.show()
    
    # Запуск приложения
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 