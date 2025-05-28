import logging

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        filename='data_analysis.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    ) 