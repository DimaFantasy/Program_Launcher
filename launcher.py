import os
import threading
import sys
import socket

from flask import Flask, Response
from markupsafe import escape

# Основные настройки
APPLICATION_NAME = "USB Bootable Tools Launcher v2"

# Настройки сканирования
# Расширения файлов, которые считаются исполняемыми
EXECUTABLE_EXTENSIONS = ['.exe', '.bat', '.cmd', '.msi', '.com', '.app', '.py', '.ps1', '.jar']
# Расширения файлов, которые следует игнорировать при сканировании
IGNORE_EXTENSIONS = ['.dll', '.ini', '.txt', '.dat', '.db', '.log', '.sys']
# Директории, которые следует исключить из сканирования
EXCLUDED_DIRS = ['__pycache__', 'venv', '.git', '.vscode', 'node_modules', 'tmp']
# Имена файлов, которые следует исключить из сканирования
EXCLUDED_FILENAMES = ['uninstall.exe', 'setup.exe', 'installer.exe', 'install.exe', 'updater.exe']

# Серверные настройки
# Путь к директории с шаблонами Flask
TEMPLATE_PATH = "launcher"
# Порт, на котором будет запущен веб-сервер
SERVER_PORT = 8100
# Максимальный порт для поиска (если предыдущие заняты)
MAX_PORT = 8200

app = Flask(__name__)

# Конфигурация
BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIRECTORY = os.path.join(BASE_DIRECTORY, TEMPLATE_PATH)

# Добавляем директорию с модулями в путь
sys.path.append(TEMPLATE_DIRECTORY)

# Импортируем модули
from program_operations import ProgramInfo, set_program_operations
from file_operations import load_program_list as load_programs, save_program_list as save_programs
from file_operations import set_base_directory as set_file_operations_base_directory
from scan_operations import set_scan_base_directory, set_program_list
from web_routes import init_web_routes
from program_launcher import set_base_directory as set_launcher_base_directory
from browser_utils import open_browser
from templating import TemplateEngine

# Глобальные переменные
EXECUTABLE = []
CATEGORY_ICONS = {}

# Инициализация HTML шаблонов
DEFAULT_ICON = '<i class="bi bi-app"></i>'
template_engine = TemplateEngine(TEMPLATE_DIRECTORY, DEFAULT_ICON)

def load_program_list():
    """Загружает список программ из файла list.txt"""
    global EXECUTABLE, CATEGORY_ICONS
    programs, category_icons = load_programs(ProgramInfo)
    EXECUTABLE = programs
    CATEGORY_ICONS = category_icons
    
    # Обновляем ссылки на глобальные переменные в модулях
    set_program_operations(EXECUTABLE)

def save_program_list():
    """Сохраняет список программ в файл list.txt"""
    return save_programs(EXECUTABLE)

@app.route('/')
def index():
    """Отображает главную страницу приложения"""
    return template_engine.generate_main_page(APPLICATION_NAME, EXECUTABLE, CATEGORY_ICONS)

def is_port_available(port):
    """Проверяет, доступен ли указанный порт"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return True
        except socket.error:
            return False

def find_available_port(start_port, max_port):
    """Ищет доступный порт, начиная с указанного и до максимального значения"""
    for port in range(start_port, max_port + 1):
        if is_port_available(port):
            return port
    return None

def main():
    """Запускает программу и веб-сервер"""
    print("Загрузка программы...")
    
    # Устанавливаем базовую директорию для всех модулей
    set_file_operations_base_directory(BASE_DIRECTORY)
    set_launcher_base_directory(BASE_DIRECTORY)
    set_scan_base_directory(BASE_DIRECTORY)
    
    # Загружаем список программ
    load_program_list()
    
    # Устанавливаем список программ для модуля сканирования
    set_program_list(EXECUTABLE, ProgramInfo, EXECUTABLE_EXTENSIONS, EXCLUDED_DIRS, EXCLUDED_FILENAMES)
    
    # Инициализируем веб-маршруты
    init_web_routes(app, EXECUTABLE, BASE_DIRECTORY, load_program_list, save_program_list)
    
    # Устанавливаем переменную окружения для подавления предупреждений Flask
    os.environ['WERKZEUG_SILENCE_LOGGING'] = '1'
    
    # Находим свободный порт
    available_port = find_available_port(SERVER_PORT, MAX_PORT)
    if available_port is None:
        print(f"Не удалось найти свободный порт в диапазоне {SERVER_PORT}-{MAX_PORT}")
        return
    else:
        print(f"Используется порт: {available_port}")
    
    # Запуск сервера в отдельном потоке
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=available_port, use_reloader=False), daemon=True).start()
    
    # Открываем браузер
    open_browser(available_port)
    
    print(f"Сервер запущен на порту {available_port}. Нажмите Enter для остановки.")
    input()
    os._exit(0)

if __name__ == '__main__':
    main()
