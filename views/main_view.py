from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QCheckBox, 
                            QComboBox, QTextEdit, QMessageBox, QTabWidget, 
                            QScrollArea, QLineEdit, QFrame, QTableWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.presenter = None  # Инициализируем presenter как None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Анализ данных')
        self.setGeometry(100, 100, 1200, 800)
        self.setup_styles()
        
        # Создание центрального виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Верхняя панель
        self.setup_top_panel(layout)
        
        # Вкладки
        self.setup_tabs(layout)
        
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
                padding: 4px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
                min-width: 200px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QCheckBox {
                color: #333333;
                padding: 4px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QTabWidget::pane {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
            QTabBar::tab:hover:!selected {
                background-color: #F5F5F5;
            }
            QTextEdit {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background-color: white;
                padding: 12px;
                font-family: 'Consolas', monospace;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
    def setup_top_panel(self, layout):
        top_panel = QFrame()
        top_panel.setFrameStyle(QFrame.Shape.StyledPanel)
        top_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton {
                padding: 5px 10px;
                min-width: 110px;
            }
            QLineEdit {
                padding: 5px;
                min-width: 160px;
            }
            QComboBox {
                padding: 5px;
                min-width: 130px;
            }
            QLabel {
                padding: 3px;
            }
        """)
        
        top_layout = QHBoxLayout(top_panel)
        top_layout.setSpacing(8)
        top_layout.setContentsMargins(8, 8, 8, 8)
        
        # Кнопка загрузки файла
        self.load_btn = QPushButton('Загрузить датасет')
        top_layout.addWidget(self.load_btn)
        
        # Кнопки экспорта
        self.export_html_btn = QPushButton('Экспорт в HTML')
        self.export_html_btn.clicked.connect(self.export_to_html)
        top_layout.addWidget(self.export_html_btn)
        
        self.export_text_btn = QPushButton('Экспорт в текст')
        self.export_text_btn.clicked.connect(self.export_to_text)
        top_layout.addWidget(self.export_text_btn)
        
        # Настройка символов для нулей
        zero_container = QWidget()
        zero_layout = QVBoxLayout(zero_container)
        zero_layout.setSpacing(1)
        zero_layout.setContentsMargins(0, 0, 0, 0)
        
        zero_label = QLabel('Символы для нулей:')
        self.zero_values_input = QLineEdit()
        self.zero_values_input.setPlaceholderText('Введите символы через запятую')
        self.zero_values_input.setText(','.join(['', ' ', '-', 'NA', 'N/A', 'null', 'NULL', 'NaN', 'nan']))
        
        zero_hint = QLabel('Символы для нулей разделяйте запятыми')
        zero_hint.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 9px;
                font-weight: normal;
            }
        """)
        
        zero_layout.addWidget(zero_label)
        zero_layout.addWidget(self.zero_values_input)
        zero_layout.addWidget(zero_hint)
        
        top_layout.addWidget(zero_container)
        
        # Чекбоксы для опций
        self.normalize_cb = QCheckBox('Нормализовать данные')
        self.normalize_cb.setToolTip("Нормализует числовые данные (среднее = 0, стд. откл. = 1)")
        top_layout.addWidget(self.normalize_cb)
        
        # Выбор типа кодирования
        encoding_label = QLabel('Кодирование:')
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(['Без кодирования', 'Числовое кодирование', 'One-Hot кодирование'])
        self.encoding_combo.setToolTip(
            "Без кодирования: оставляет данные как есть\n"
            "Числовое кодирование: преобразует категории в числа\n"
            "One-Hot кодирование: создает бинарные колонки для каждой категории"
        )
        top_layout.addWidget(encoding_label)
        top_layout.addWidget(self.encoding_combo)
        
        # Кнопка сохранения
        self.save_btn = QPushButton('Сохранить датасет')
        top_layout.addWidget(self.save_btn)
        
        layout.addWidget(top_panel)
        
    def setup_tabs(self, layout):
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Вкладка с df.info()
        self.info_tab = QWidget()
        self.info_layout = QVBoxLayout(self.info_tab)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_layout.addWidget(self.info_text)
        self.tabs.addTab(self.info_tab, "Информация (df.info)")
        
        # Вкладка с df.describe()
        self.describe_tab = QWidget()
        self.describe_layout = QVBoxLayout(self.describe_tab)
        self.describe_text = QTextEdit()
        self.describe_text.setReadOnly(True)
        self.describe_layout.addWidget(self.describe_text)
        self.tabs.addTab(self.describe_tab, "Статистика (df.describe)")
        
        # Вкладка с корреляциями
        self.corr_tab = QWidget()
        self.corr_layout = QVBoxLayout(self.corr_tab)
        self.corr_text = QTextEdit()
        self.corr_text.setReadOnly(True)
        self.corr_layout.addWidget(self.corr_text)
        self.tabs.addTab(self.corr_tab, "Корреляции (df.corr)")
        
        # Вкладка с уникальными значениями
        self.unique_tab = QWidget()
        self.unique_layout = QVBoxLayout(self.unique_tab)
        self.unique_text = QTextEdit()
        self.unique_text.setReadOnly(True)
        self.unique_layout.addWidget(self.unique_text)
        self.tabs.addTab(self.unique_tab, "Уникальные значения (df.unique)")
        
        # Вкладка с value counts
        self.value_counts_tab = QWidget()
        self.value_counts_layout = QVBoxLayout(self.value_counts_tab)
        self.value_counts_text = QTextEdit()
        self.value_counts_text.setReadOnly(True)
        self.value_counts_layout.addWidget(self.value_counts_text)
        self.tabs.addTab(self.value_counts_tab, "Частота значений (df.value_counts)")
        
        # Вкладка с графиками
        self.graphs_tab = QWidget()
        self.graphs_layout = QVBoxLayout(self.graphs_tab)
        
        # Создаем скролл-область для графиков
        self.graphs_scroll = QScrollArea()
        self.graphs_scroll.setWidgetResizable(True)
        self.graphs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.graphs_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Создаем контейнер для графиков
        self.graphs_content = QWidget()
        self.graphs_content_layout = QVBoxLayout(self.graphs_content)
        self.graphs_content_layout.setSpacing(30)
        self.graphs_content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Устанавливаем минимальную ширину контейнера
        self.graphs_content.setMinimumWidth(800)
        
        self.graphs_scroll.setWidget(self.graphs_content)
        self.graphs_layout.addWidget(self.graphs_scroll)
        self.tabs.addTab(self.graphs_tab, "Графики")
        
    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)
        
    def show_warning(self, title, message):
        QMessageBox.warning(self, title, message)
        
    def show_info(self, title, message):
        QMessageBox.information(self, title, message)
        
    def get_open_file_name(self):
        return QFileDialog.getOpenFileName(
            self,
            "Выберите датасет",
            "",
            "Все файлы (*);;CSV файлы (*.csv);;Excel файлы (*.xlsx *.xls);;Текстовые файлы (*.txt *.tsv)"
        )
        
    def get_save_file_name(self):
        return QFileDialog.getSaveFileName(
            self,
            "Сохранить датасет",
            "",
            "CSV файлы (*.csv);;Excel файлы (*.xlsx);;Текстовые файлы (*.txt)"
        )
        
    def clear_graphs(self):
        for i in reversed(range(self.graphs_content_layout.count())): 
            self.graphs_content_layout.itemAt(i).widget().setParent(None)
            
    def add_graph(self, fig):
        canvas = FigureCanvas(fig)
        canvas.setMinimumHeight(400)
        self.graphs_content_layout.addWidget(canvas)
        
    def show_plots(self, plots):
        """Отображение графиков"""
        self.plots_text.delete(1.0, tk.END)
        
        # Создаем фигуру с автоматической настройкой размера
        fig = plt.figure(figsize=(12, 8))
        fig.tight_layout(pad=3.0)  # Добавляем отступы
        
        for i, plot in enumerate(plots, 1):
            plt.subplot(2, 2, i)
            plot()
            plt.tight_layout()  # Автоматическая настройка отступов
        
        # Сохраняем график во временный файл
        temp_file = "temp_plot.png"
        plt.savefig(temp_file, bbox_inches='tight', dpi=300)
        plt.close()
        
        # Отображаем график
        self.plots_text.image_create(tk.END, image=tk.PhotoImage(file=temp_file))
        os.remove(temp_file)  # Удаляем временный файл 

    def create_export_buttons(self):
        """Создание кнопок для экспорта"""
        export_layout = QHBoxLayout()
        
        # Кнопка экспорта в HTML
        html_btn = QPushButton("Экспорт в HTML")
        html_btn.clicked.connect(self.export_to_html)
        export_layout.addWidget(html_btn)
        
        # Кнопка экспорта в текст
        text_btn = QPushButton("Экспорт в текст")
        text_btn.clicked.connect(self.export_to_text)
        export_layout.addWidget(text_btn)
        
        return export_layout
        
    def export_to_html(self):
        """Экспорт данных в HTML"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как HTML", "", "HTML files (*.html)"
        )
        if file_name:
            try:
                self.presenter.export_to_html(file_name)
                QMessageBox.information(self, "Успех", "Данные успешно экспортированы в HTML")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
                
    def export_to_text(self):
        """Экспорт данных в текст"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как текст", "", "Text files (*.txt)"
        )
        if file_name:
            try:
                self.presenter.export_to_text(file_name)
                QMessageBox.information(self, "Успех", "Данные успешно экспортированы в текст")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def create_widgets(self):
        """Создание виджетов"""
        # Создаем вкладки
        self.tabs = QTabWidget()
        
        # Вкладка с данными
        data_tab = QWidget()
        data_layout = QVBoxLayout()
        
        # Кнопки загрузки и экспорта
        buttons_layout = QHBoxLayout()
        
        # Кнопка загрузки
        load_btn = QPushButton("Загрузить данные")
        load_btn.clicked.connect(self.load_data)
        buttons_layout.addWidget(load_btn)
        
        # Добавляем кнопки экспорта
        export_layout = self.create_export_buttons()
        buttons_layout.addLayout(export_layout)
        
        data_layout.addLayout(buttons_layout)
        
        # Таблица с данными
        self.table = QTableWidget()
        data_layout.addWidget(self.table)
        
        data_tab.setLayout(data_layout)
        self.tabs.addTab(data_tab, "Данные")
        
        # Вкладка с графиками
        plots_tab = QWidget()
        plots_layout = QVBoxLayout()
        
        # Область для отображения графиков
        self.plots_text = QTextEdit()
        self.plots_text.setReadOnly(True)
        plots_layout.addWidget(self.plots_text)
        
        plots_tab.setLayout(plots_layout)
        self.tabs.addTab(plots_tab, "Графики")
        
        # Добавляем вкладки в главное окно
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def set_presenter(self, presenter):
        """Установка презентера"""
        self.presenter = presenter 