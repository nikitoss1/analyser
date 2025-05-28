import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging
import io
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tempfile
import base64
from io import BytesIO

class DataModel:
    def __init__(self):
        self.df = None
        self.zero_values = ['', ' ', '-', 'NA', 'N/A', 'null', 'NULL', 'NaN', 'nan']
        
    def load_data(self, file_name):
        """Загрузка данных из файла"""
        try:
            self.current_file = file_name
            logging.info(f"Начинаем загрузку файла: {file_name}")
            
            # Определяем разделитель на основе расширения файла
            if file_name.endswith('.tsv'):
                sep = '\t'
            elif file_name.endswith('.txt'):
                # Читаем первую строку для определения разделителя
                with open(file_name, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                sep = self._detect_separator(first_line)
                if sep is None:
                    raise ValueError("Не удалось определить разделитель в файле")
            else:
                sep = None
            
            # Сначала пробуем прочитать файл как CSV с кавычками
            try:
                if file_name.endswith('.csv'):
                    self.df = pd.read_csv(file_name, 
                                        quoting=1,  # QUOTE_ALL
                                        encoding='utf-8',
                                        skipinitialspace=True)
                elif file_name.endswith(('.xlsx', '.xls', '.xlsm', '.xlsb')):
                    self.df = pd.read_excel(file_name)
                    # Для Excel файлов пропускаем проверку количества колонок
                    logging.info(f"DataFrame создан, размер: {self.df.shape}")
                    
                    # Проверяем заполненность данных
                    total_cells = self.df.size
                    non_empty_cells = sum(
                        sum(1 for x in self.df[col] if pd.notna(x) and str(x).strip() not in self.zero_values)
                        for col in self.df.columns
                    )
                    fill_ratio = (non_empty_cells / total_cells) * 100
                    logging.info(f"Заполненность данных: {fill_ratio:.2f}%")
                    
                    if fill_ratio < 50:
                        raise ValueError("В файле слишком много пустых значений")
                    
                    return True
                elif file_name.endswith('.tsv'):
                    self.df = pd.read_csv(file_name, sep='\t', encoding='utf-8')
                else:
                    self.df = pd.read_csv(file_name, sep=sep, encoding='utf-8')
                
                logging.info(f"DataFrame создан, размер: {self.df.shape}")
                
                # Сначала проверяем заполненность данных
                total_cells = self.df.size
                # Считаем только непустые значения (не NaN, не пустая строка, не пробел)
                non_empty_cells = sum(
                    sum(1 for x in self.df[col] if pd.notna(x) and str(x).strip() not in self.zero_values)
                    for col in self.df.columns
                )
                fill_ratio = (non_empty_cells / total_cells) * 100
                logging.info(f"Заполненность данных: {fill_ratio:.2f}%")
                
                if fill_ratio < 50:
                    raise ValueError("В файле слишком много пустых значений")
                
                # Затем проверяем количество колонок
                expected_cols = len(self.df.columns)
                
                # Читаем файл как текст для проверки
                with open(file_name, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Проверяем каждую строку
                invalid_rows = []
                for i, line in enumerate(lines[1:], 1):
                    # Используем csv.reader для корректной обработки кавычек
                    import csv
                    from io import StringIO
                    reader = csv.reader(StringIO(line), delimiter=sep if sep else ',')
                    values = next(reader)
                    actual_cols = len(values)
                    
                    if actual_cols != expected_cols:
                        invalid_rows.append(i + 1)
                        logging.warning(f"Строка {i + 1}: ожидалось {expected_cols} колонок, найдено {actual_cols}")
                
                # Если найдены строки с неправильным количеством колонок, отклоняем файл
                if invalid_rows:
                    error_msg = f"Файл содержит строки с неправильным количеством колонок: {invalid_rows}"
                    logging.error(error_msg)
                    raise ValueError(error_msg)
                
                return True
                
            except pd.errors.ParserError as e:
                # Если не удалось прочитать с кавычками, пробуем без них
                logging.warning(f"Ошибка при чтении CSV с кавычками: {str(e)}")
                if file_name.endswith('.csv'):
                    self.df = pd.read_csv(file_name, 
                                        encoding='utf-8',
                                        skipinitialspace=True)
                    
                    logging.info(f"DataFrame создан, размер: {self.df.shape}")
                    
                    # Сначала проверяем заполненность данных
                    total_cells = self.df.size
                    # Считаем только непустые значения (не NaN, не пустая строка, не пробел)
                    non_empty_cells = sum(
                        sum(1 for x in self.df[col] if pd.notna(x) and str(x).strip() not in self.zero_values)
                        for col in self.df.columns
                    )
                    fill_ratio = (non_empty_cells / total_cells) * 100
                    logging.info(f"Заполненность данных: {fill_ratio:.2f}%")
                    
                    if fill_ratio < 50:
                        raise ValueError("В файле слишком много пустых значений")
                    
                    # Затем проверяем количество колонок
                    expected_cols = len(self.df.columns)
                    
                    # Читаем файл как текст для проверки
                    with open(file_name, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Проверяем каждую строку
                    invalid_rows = []
                    for i, line in enumerate(lines[1:], 1):
                        values = [v.strip() for v in line.strip().split(',')]
                        # Удаляем пустые значения в конце
                        while values and not values[-1]:
                            values.pop()
                        actual_cols = len(values)
                        
                        if actual_cols != expected_cols:
                            invalid_rows.append(i + 1)
                            logging.warning(f"Строка {i + 1}: ожидалось {expected_cols} колонок, найдено {actual_cols}")
                    
                    # Если найдены строки с неправильным количеством колонок, отклоняем файл
                    if invalid_rows:
                        error_msg = f"Файл содержит строки с неправильным количеством колонок: {invalid_rows}"
                        logging.error(error_msg)
                        raise ValueError(error_msg)
                    
                    return True
            
        except Exception as e:
            logging.error(f"Ошибка при загрузке файла: {str(e)}")
            raise
    
    
    def _detect_separator(self, first_line):
        """Определение разделителя в файле"""
        separators = {
            '\t': '\t',
            '~': '~',
            '#': '#',
            ',': ',',
            ';': ';',
            ' ': ' '
        }
        
        # Сначала проверяем на табуляцию
        if '\t' in first_line:
            return '\t'
            
        # Проверяем каждый разделитель
        for sep, pattern in separators.items():
            if sep in first_line:
                # Проверяем, что разделитель действительно разделяет значения
                parts = first_line.split(sep)
                if len(parts) > 1 and all(part.strip() for part in parts):
                    return pattern
        
        # Если разделитель не найден, пробуем определить по количеству колонок
        for sep, pattern in separators.items():
            parts = first_line.split(sep)
            if len(parts) > 1:
                return pattern
                
        return None
    
    def _validate_data(self):
        """Валидация загруженных данных"""
        if self.df is None or self.df.empty:
            raise ValueError("Датасет пуст")
            
        if len(self.df.columns) < 2:
            raise ValueError("В файле слишком мало колонок")
            
        if len(self.df) < 2:
            raise ValueError("В файле слишком мало строк")
            
        if any(col.strip() == '' for col in self.df.columns):
            raise ValueError("В файле обнаружены пустые заголовки")
            
        return True
    
    def preprocess_data(self, normalize=False, encoding_type='Без кодирования'):
        """Предобработка данных"""
        if self.df is None:
            return
            
        # Очистка данных
        for col in self.df.columns:
            # Заменяем нулевые значения на NaN для последующей обработки
            self.df[col] = self.df[col].replace(self.zero_values, np.nan)
        
        # Удаление дубликатов
        initial_shape = self.df.shape
        self.df = self.df.drop_duplicates()
        logging.info(f"Удалено {initial_shape[0] - self.df.shape[0]} дублирующихся строк")
        
        # Заполнение пропущенных значений
        for col in self.df.columns:
            if self.df[col].isnull().sum() > 0:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    # Для числовых признаков используем медиану
                    median_val = self.df[col].median()
                    self.df[col] = self.df[col].fillna(median_val)
                    logging.info(f"Заполнены пропуски в числовом признаке {col} медианой: {median_val}")
                else:
                    # Для категориальных признаков используем моду
                    mode_val = self.df[col].mode().iloc[0]
                    self.df[col] = self.df[col].fillna(mode_val)
                    logging.info(f"Заполнены пропуски в категориальном признаке {col} модой: {mode_val}")
        
        # Нормализация
        if normalize:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                scaler = StandardScaler()
                self.df[numeric_cols] = scaler.fit_transform(self.df[numeric_cols])
                logging.info("Данные нормализованы с помощью StandardScaler")
        
        # Кодирование
        if encoding_type != 'Без кодирования':
            categorical_cols = self.df.select_dtypes(include=['object']).columns
            if encoding_type == 'Числовое кодирование':
                for col in categorical_cols:
                    self.df[col] = pd.Categorical(self.df[col]).codes
                logging.info("Применено числовое кодирование")
            elif encoding_type == 'One-Hot кодирование':
                valid_cols = [col for col in categorical_cols if self.df[col].nunique() <= 10]
                if valid_cols:
                    # Преобразуем в числовые 1/0 вместо True/False
                    self.df = pd.get_dummies(self.df, columns=valid_cols).astype(int)
                    logging.info(f"Применено one-hot кодирование к колонкам: {valid_cols}")

    def get_data_info(self):
        """Получение информации о данных, включая форму (shape)"""
        if self.df is None:
            return None

        buffer = io.StringIO()

        # Сначала записываем info()
        self.df.info(buf=buffer)

        # Затем добавляем shape — тоже записываем в buffer
        shape_str = f"\nРазмерность: {self.df.shape[0]} строк × {self.df.shape[1]} столбцов\n"
        buffer.write(shape_str)

        return buffer.getvalue()
    
    
    def get_data_describe(self):
        """Получение статистического описания данных"""
        if self.df is None:
            return None
        return self.df.describe()
    
    def get_correlations(self):
        """Получение корреляций"""
        if self.df is None:
            return None, None
            
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return None, None
            
        pearson_corr = numeric_df.corr()
        spearman_corr = numeric_df.corr(method='spearman')
        return pearson_corr, spearman_corr
    
    def get_unique_values(self) -> dict:
        """Уникальные значения по каждому столбцу (все элементы без усечения)"""
        if self.df is None:
            return None

        result = {}
        with pd.option_context('display.max_rows', None):
            for col in self.df.columns:
                # Оборачиваем в Series, чтобы использовать to_string()
                uniques = pd.Series(self.df[col].unique())
                result[col] = uniques.to_string(index=False)
        return result
    
    def get_value_counts(self):
        """Получение частот значений (все строки без обрезки)"""
        if self.df is None:
            return None

        result: Dict[str, str] = {}
        # временно снимаем ограничение на число строк при выводе
        with pd.option_context('display.max_rows', None):
            for col in self.df.columns:
                counts: pd.Series = self.df[col].value_counts(dropna=False)
                # .to_string() вернёт строку в том же формате,
                # что и counts, но со всеми строками
                result[col] = counts.to_string()

        return result
    def save_data(self, file_name):
        """Сохранение данных"""
        if self.df is None:
            raise ValueError("Нет данных для сохранения")
            
        try:
            if file_name.endswith('.csv'):
                # Перезаписываем пустые строки на NaN и сохраняем
                df_to_save = self.df.replace(r'^\s*$', pd.NA, regex=True)
                df_to_save.to_csv(file_name, index=False, na_rep='')
            elif file_name.endswith(('.xls', '.xlsx')):
                engine = 'openpyxl' if file_name.endswith('.xlsx') else 'xlwt'
                self.df.to_excel(file_name, index=False, engine=engine)
            else:
                self.df.to_csv(file_name, sep='\t', index=False)
            logging.info(f"Датасет сохранён в {file_name}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении файла: {str(e)}")
            raise
    
    def export_to_html(self, file_name):
        """Экспорт данных в HTML формат"""
        if self.df is None:
            raise ValueError("Нет данных для экспорта")
            
        try:
            # Создаем временную директорию для графиков
            temp_dir = tempfile.mkdtemp()
            plots_dir = os.path.join(temp_dir, 'plots')
            os.makedirs(plots_dir, exist_ok=True)
            
            # Создаем графики
            plots_html = []
            numeric_df = self.df.select_dtypes(include=['number'])
            
            # Тепловая карта корреляций
            pearson_corr, _ = self.get_correlations()
            if pearson_corr is not None:
                plt.figure(figsize=(10, 8))
                sns.heatmap(pearson_corr, annot=True, cmap='coolwarm', fmt='.2f')
                plt.title('Тепловая карта корреляций')
                plt.tight_layout()
                
                # Сохраняем график
                plot_path = os.path.join(plots_dir, 'correlation_heatmap.png')
                plt.savefig(plot_path, bbox_inches='tight', dpi=300)
                plt.close()
                
                # Добавляем в HTML
                with open(plot_path, 'rb') as f:
                    plot_data = base64.b64encode(f.read()).decode('utf-8')
                plots_html.append(f"""
                    <div class="plot-container">
                        <h3>Тепловая карта корреляций</h3>
                        <img src="data:image/png;base64,{plot_data}" alt="Тепловая карта корреляций">
                    </div>
                """)
            
            # Гистограммы и бокс-плоты для числовых колонок
            for col in numeric_df.columns:
                # Гистограмма
                plt.figure(figsize=(10, 5))
                sns.histplot(data=numeric_df, x=col, kde=True)
                plt.title(f'Распределение {col}')
                plt.tight_layout()
                
                plot_path = os.path.join(plots_dir, f'hist_{col}.png')
                plt.savefig(plot_path, bbox_inches='tight', dpi=300)
                plt.close()
                
                with open(plot_path, 'rb') as f:
                    plot_data = base64.b64encode(f.read()).decode('utf-8')
                plots_html.append(f"""
                    <div class="plot-container">
                        <h3>Распределение {col}</h3>
                        <img src="data:image/png;base64,{plot_data}" alt="Гистограмма {col}">
                    </div>
                """)
                
                # Бокс-плот
                plt.figure(figsize=(10, 5))
                sns.boxplot(data=numeric_df, y=col)
                plt.title(f'Бокс-плот {col}')
                plt.tight_layout()
                
                plot_path = os.path.join(plots_dir, f'box_{col}.png')
                plt.savefig(plot_path, bbox_inches='tight', dpi=300)
                plt.close()
                
                with open(plot_path, 'rb') as f:
                    plot_data = base64.b64encode(f.read()).decode('utf-8')
                plots_html.append(f"""
                    <div class="plot-container">
                        <h3>Бокс-плот {col}</h3>
                        <img src="data:image/png;base64,{plot_data}" alt="Бокс-плот {col}">
                    </div>
                """)
            
            # Создаем HTML отчет
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2, h3 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f5f5f5; }}
                    .info {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                    .describe {{ margin: 20px 0; }}
                    .plot-container {{ 
                        margin: 20px 0;
                        padding: 15px;
                        background-color: white;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .plot-container img {{
                        max-width: 100%;
                        height: auto;
                        display: block;
                        margin: 10px auto;
                    }}
                </style>
            </head>
            <body>
                <h1>Отчет по анализу данных</h1>
                
                <h2>Информация о датасете</h2>
                <div class="info">
                    {self.get_data_info().replace('\n', '<br>')}
                </div>
                
                <h2>Размерность массива</h2>
                <div class="info">
                    {self.df.shape}
                </div>
                
                <h2>Статистическое описание</h2>
                <div class="describe">
                    {self.get_data_describe().to_html()}
                </div>
                
                <h2>Корреляции (Пирсон)</h2>
                {self.get_correlations()[0].to_html()}
                
                <h2>Корреляции (Спирмен)</h2>
                {self.get_correlations()[1].to_html()}
                
                <h2>Уникальные значения</h2>
                {self._format_unique_values_html()}
                
                <h2>Частоты значений</h2>
                {self._format_value_counts_html()}
                
                <h2>Графики</h2>
                {''.join(plots_html)}
            </body>
            </html>
            """
            
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            # Удаляем временную директорию
            import shutil
            shutil.rmtree(temp_dir)
                
            logging.info(f"Данные экспортированы в HTML файл: {file_name}")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка при экспорте в HTML: {str(e)}")
            raise
            
    def export_to_text(self, file_name):
        """Экспорт данных в текстовый формат"""
        if self.df is None:
            raise ValueError("Нет данных для экспорта")
            
        try:
            # Создаем текстовый отчет
            text_content = f"""
Отчет по анализу данных
=======================

Информация о датасете:
----------------------
{self.get_data_info()}

Размерность датасета
----------------------
{self.df.shape}

Статистическое описание:
-----------------------
{self.get_data_describe()}

Корреляции (Пирсон):
-------------------
{self.get_correlations()[0]}

Корреляции (Спирмен):
--------------------
{self.get_correlations()[1]}

Уникальные значения:
------------------
{self._format_unique_values_text()}

Частоты значений:
---------------
{self._format_value_counts_text()}
            """
            
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(text_content)
                
            logging.info(f"Данные экспортированы в текстовый файл: {file_name}")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка при экспорте в текстовый формат: {str(e)}")
            raise
            
    def _format_unique_values_html(self):
        """Форматирование уникальных значений для HTML"""
        unique_values = self.get_unique_values()
        if unique_values is None:
            return "<p>Нет данных</p>"
            
        html = "<div class='unique-values'>"
        for col, values in unique_values.items():
            html += f"<h3>{col}</h3>"
            html += "<ul>"
            for val in values:
                html += f"<li>{val}</li>"
            html += "</ul>"
        html += "</div>"
        return html
        
    def _format_value_counts_html(self):
        html = "<div class='value-counts'>"
        for col, counts in self.get_value_counts().items():
            html += f"<h3>{col}</h3>"
            if isinstance(counts, pd.Series):
                # если Series — выводим табличку
                html += counts.to_frame().to_html()
            else:
                # если это уже строка — оборачиваем в <pre> для сохранения форматирования
                html += f"<pre>{counts}</pre>"
        html += "</div>"
        return html
        
    def _format_unique_values_text(self):
        """Форматирование уникальных значений для текста"""
        unique_values = self.get_unique_values()
        if unique_values is None:
            return "Нет данных"
            
        text = ""
        for col, values in unique_values.items():
            text += f"\n{col}:\n"
            for val in values:
                text += f"  {val}\n"
        return text
        
    def _format_value_counts_text(self):
        """Форматирование частот значений для текста"""
        value_counts = self.get_value_counts()
        if value_counts is None:
            return "Нет данных"
            
        text = ""
        for col, counts in value_counts.items():
            text += f"\n{col}:\n"
            if isinstance(counts, pd.Series):
                text += counts.to_string() + "\n"
            else:
                text += str(counts) + "\n"
        return text