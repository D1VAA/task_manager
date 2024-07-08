import logging
import os

from datetime import datetime

LOG_FILE = 'gerenciador_de_tarefas.log'
LOG_MAX_SIZE = 1024 * 1024 * 5  # 5MB
LOG_BACKUP_COUNT = 3

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)

logger.setLevel(logging.DEBUG)

# Rotação de logs
def rotate_logs():
    try:
        if os.path.exists(LOG_FILE):
            backup_dir = os.path.dirname(LOG_FILE)
            backup_name = os.path.basename(LOG_FILE) + '.' + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

            # Move o arquivo de log atual para um backup
            os.rename(LOG_FILE, os.path.join(backup_dir, backup_name))

            # Exclui backups antigos
            for filename in os.listdir(backup_dir):
                if filename.startswith(os.path.basename(LOG_FILE) + '.') and len(os.listdir(backup_dir)) >= LOG_BACKUP_COUNT:
                    os.remove(os.path.join(backup_dir, filename))
    except PermissionError:
        logger.warning('Falha ao rotacionar logs. Arquivo provavelmente em uso.')

rotate_logs()  # Rotacionar logs na inicialização