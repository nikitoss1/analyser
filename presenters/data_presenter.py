import logging
import io
import seaborn as sns
import matplotlib.pyplot as plt
from models.data_model import DataModel

class DataPresenter:
    def __init__(self, view):
        self.view = view
        self.model = DataModel()
        self.setup_connections()
        
    def setup_connections(self):
        """Установка связей между сигналами и слотами"""
        self.view.load_btn.clicked.connect(self.load_data)
        self.view.save_btn.clicked.connect(self.save_data)
        self.view.zero_values_input.textChanged.connect(self.update_zero_values)
        
    def update_zero_values(self):
        """Обновление списка символов для нулей"""
        text = self.view.zero_values_input.text()
        self.model.zero_values = [x.strip() for x in text.split(',') if x.strip()]
        logging.info(f"Обновлены символы для нулей: {self.model.zero_values}")
        
    def load_data(self):
        """Загрузка данных"""
        self.view.zero_values_input.textChanged.connect(self.update_zero_values)
        file_name, _ = self.view.get_open_file_name()
        if not file_name:
            return
            
        try:
            self.model.load_data(file_name)
            self.analyze_data()
        except ValueError as e:
            self.view.show_error("Ошибка", str(e))
        except Exception as e:
            self.view.show_error("Ошибка", f"Ошибка при загрузке файла:\n{str(e)}")
            
    def save_data(self):
        """Сохранение данных"""
        if self.model.df is None:
            self.view.show_warning("Внимание", "Нет данных для сохранения!")
            return
            
        file_name, _ = self.view.get_save_file_name()
        if not file_name:
            return
            
        try:
            self.model.save_data(file_name)
            self.view.show_info("Успех", "Датасет успешно сохранён!")
        except Exception as e:
            self.view.show_error("Ошибка", f"Ошибка при сохранении файла: {str(e)}")
            
    def analyze_data(self):
        self.view.zero_values_input.textChanged.connect(self.update_zero_values)
        """Анализ данных"""
        if self.model.df is None:
            self.view.show_warning("Внимание", "Пожалуйста, сначала загрузите датасет!")
            return
            
        try:
            # Предобработка данных
            self.model.preprocess_data(
                normalize=self.view.normalize_cb.isChecked(),
                encoding_type=self.view.encoding_combo.currentText()
            )
            
            # Очистка предыдущих графиков
            self.view.clear_graphs()
            
            # Вывод df.info()
            info_text = self.model.get_data_info()
            if info_text:
                self.view.info_text.setText(info_text)
            
            # Вывод df.describe()
            describe_df = self.model.get_data_describe()
            if self.view.normalize_cb.isChecked():
                describe_df = describe_df.round(4)
            self.view.describe_text.setText(str(describe_df))
            
            # Анализ корреляций
            pearson_corr, spearman_corr = self.model.get_correlations()
            if pearson_corr is not None:
                corr_report = []
                corr_report.append("=== ЛИНЕЙНЫЕ КОРРЕЛЯЦИИ ===")
                corr_pairs = []
                
                for i in range(len(pearson_corr.columns)):
                    for j in range(i+1, len(pearson_corr.columns)):
                        corr_pairs.append((
                            pearson_corr.columns[i],
                            pearson_corr.columns[j],
                            pearson_corr.iloc[i, j]
                        ))
                
                corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                for pair in corr_pairs[:5]:
                    corr_report.append(f"{pair[0]} - {pair[1]}: {pair[2]:.3f}")
                
                corr_report.append("\n=== НЕЛИНЕЙНЫЕ КОРРЕЛЯЦИИ (СПИРМЕН) ===")
                spearman_pairs = []
                
                for i in range(len(spearman_corr.columns)):
                    for j in range(i+1, len(spearman_corr.columns)):
                        spearman_pairs.append((
                            spearman_corr.columns[i],
                            spearman_corr.columns[j],
                            spearman_corr.iloc[i, j]
                        ))
                
                spearman_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                for pair in spearman_pairs[:5]:
                    corr_report.append(f"{pair[0]} - {pair[1]}: {pair[2]:.3f}")
                
                self.view.corr_text.setText("\n".join(corr_report))
                
                # Построение тепловой карты
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111)
                sns.heatmap(pearson_corr, annot=True, cmap='coolwarm', ax=ax, fmt='.2f',
                           annot_kws={'size': 8}, cbar_kws={'label': 'Корреляция'})
                plt.title('Тепловая карта корреляций', pad=20, fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.yticks(rotation=0)
                plt.tight_layout()
                self.view.add_graph(fig)
                
                # Построение гистограмм и бокс-плотов
                numeric_df = self.model.df.select_dtypes(include=['number'])
                for col in numeric_df.columns:
                    # Гистограмма
                    fig = plt.figure(figsize=(10, 5))
                    ax = fig.add_subplot(111)
                    sns.histplot(data=numeric_df, x=col, ax=ax, kde=True)
                    ax.set_title(f'Распределение {col}', pad=20, fontsize=12)
                    ax.set_xlabel(col, fontsize=10)
                    ax.set_ylabel('Частота', fontsize=10)
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    self.view.add_graph(fig)
                    
                    # Бокс-плот
                    fig = plt.figure(figsize=(10, 5))
                    ax = fig.add_subplot(111)
                    sns.boxplot(data=numeric_df, y=col, ax=ax)
                    ax.set_title(f'Бокс-плот {col}', pad=20, fontsize=12)
                    ax.set_ylabel(col, fontsize=10)
                    plt.tight_layout()
                    self.view.add_graph(fig)
            
            # Заполнение вкладки с уникальными значениями
            unique_values = self.model.get_unique_values()
            if unique_values:
                unique_report = []
                for col, values in unique_values.items():
                    unique_report.append(f"\n=== {col} ===")
                    unique_report.append(f"Количество уникальных значений: {len(values)}")
                    unique_report.append("Значения:")
                    unique_report.append(str(values))
                self.view.unique_text.setText("\n".join(unique_report))
            
            # Заполнение вкладки с value counts
            value_counts = self.model.get_value_counts()
            if value_counts:
                value_counts_report = []
                for col, counts in value_counts.items():
                    value_counts_report.append(f"\n=== {col} ===")
                    value_counts_report.append(str(counts))
                self.view.value_counts_text.setText("\n".join(value_counts_report))
            
            logging.info("Анализ данных завершён")
            
        except Exception as e:
            error_msg = f"Ошибка при анализе данных: {str(e)}"
            self.view.show_error("Ошибка", error_msg)
            logging.error(error_msg)
            
    def export_to_html(self, file_name):
        """Экспорт данных в HTML"""
        self.model.export_to_html(file_name)
        
    def export_to_text(self, file_name):
        """Экспорт данных в текст"""
        self.model.export_to_text(file_name) 