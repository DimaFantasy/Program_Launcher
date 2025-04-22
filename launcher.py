import os
import threading
import sys

from flask import Flask, Response
from markupsafe import escape

# Основные настройки
APPLICATION_NAME = "USB Bootable Tools Launcher v2"

# Настройки сканирования
EXECUTABLE_EXTENSIONS = ['.exe', '.bat', '.cmd', '.msi', '.com', '.app', '.py', '.ps1', '.jar']
IGNORE_EXTENSIONS = ['.dll', '.ini', '.txt', '.dat', '.db', '.log', '.sys']
EXCLUDED_DIRS = ['__pycache__', 'venv', '.git', '.vscode', 'node_modules', 'tmp']
EXCLUDED_FILENAMES = ['uninstall.exe', 'setup.exe', 'installer.exe', 'install.exe', 'updater.exe']

# Настройки отметки файлов
MARK_MISSING_FILES = True  # Отмечать отсутствующие файлы "[не найдено]"
MAX_MISSING_FILES = 0  # 0 = без ограничений

# Серверные настройки
TEMPLATE_PATH = "launcher"
SERVER_PORT = 8077

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
    
    # Запуск сервера в отдельном потоке
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=SERVER_PORT, use_reloader=False), daemon=True).start()
    
    # Открываем браузер
    open_browser(SERVER_PORT)
    
    print(f"Сервер запущен на порту {SERVER_PORT}. Нажмите Enter для остановки.")
    input()
    os._exit(0)

if __name__ == '__main__':
    main()
