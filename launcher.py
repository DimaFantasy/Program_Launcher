import os
import threading
import sys
import socket
import time
import argparse
import webbrowser
from pathlib import Path

from flask import Flask, Response
from markupsafe import escape

# Основные настройки
APPLICATION_NAME = "USB Bootable Tools Launcher v2"
VERSION = "2.1.0"

# Настройки сканирования
# Расширения файлов, которые считаются исполняемыми
EXECUTABLE_EXTENSIONS = ['.exe', '.bat', '.cmd', '.msi', '.com', '.app', '.py', '.ps1', '.jar', '.reg']
# Расширения файлов, которые следует игнорировать при сканировании
IGNORE_EXTENSIONS = ['.dll', '.ini', '.txt', '.dat', '.db', '.log', '.sys']
# Директории, которые следует исключить из сканирования
EXCLUDED_DIRS = ['launcher','__pycache__', 'venv', '.git', '.vscode', 'node_modules', 'tmp', 'backup']
# Имена файлов, которые следует исключить из сканирования
EXCLUDED_FILENAMES = ['uninstall.exe']

# Серверные настройки
# Путь к директории с шаблонами Flask
TEMPLATE_PATH = "launcher"
# Порт, на котором будет запущен веб-сервер
SERVER_PORT = 8100
# Максимальный порт для поиска (если предыдущие заняты)
MAX_PORT = 8200

app = Flask(__name__)

# Определяем директорию скрипта (где находится сам скрипт)
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Определяем рабочую директорию (откуда запущен скрипт или ярлык)
WORKING_DIRECTORY = os.getcwd()

# Проверяем, запущен ли скрипт из своей директории или из другого места
IS_RUNNING_FROM_ELSEWHERE = SCRIPT_DIRECTORY != WORKING_DIRECTORY

# Конфигурация
BASE_DIRECTORY = WORKING_DIRECTORY if IS_RUNNING_FROM_ELSEWHERE else SCRIPT_DIRECTORY
TEMPLATE_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, TEMPLATE_PATH)

# Проверка наличия директории с шаблонами
if not os.path.exists(TEMPLATE_DIRECTORY):
    print(f"ОШИБКА: Директория с шаблонами не найдена: {TEMPLATE_DIRECTORY}")
    print("Убедитесь, что вы запускаете приложение из корректной директории.")
    sys.exit(1)

# Добавляем директорию с модулями в путь
sys.path.append(TEMPLATE_DIRECTORY)

try:
    # Импортируем модули
    from program_operations import ProgramInfo, set_program_operations
    from file_operations import load_program_list as load_programs, save_program_list as save_programs
    from file_operations import set_base_directory as set_file_operations_base_directory
    from scan_operations import set_scan_base_directory, set_program_list
    from web_routes import init_web_routes
    from program_launcher import set_base_directory as set_launcher_base_directory
    from browser_utils import open_browser
    from templating import TemplateEngine
except ImportError as e:
    print(f"ОШИБКА: Не удалось импортировать необходимые модули: {e}")
    print("Убедитесь, что структура проекта не повреждена.")
    sys.exit(1)

# Глобальные переменные
EXECUTABLE = []
CATEGORY_ICONS = {}

# Инициализация HTML шаблонов
DEFAULT_ICON = '<i class="bi bi-app"></i>'
template_engine = TemplateEngine(TEMPLATE_DIRECTORY, DEFAULT_ICON)

def load_program_list():
    """Загружает список программ из файла list.txt"""
    global EXECUTABLE, CATEGORY_ICONS
    try:
        programs, category_icons = load_programs(ProgramInfo)
        EXECUTABLE = programs
        CATEGORY_ICONS = category_icons
        
        # Обновляем ссылки на глобальные переменные в модулях
        set_program_operations(EXECUTABLE)
        return True
    except Exception as e:
        print(f"ОШИБКА загрузки списка программ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def save_program_list():
    """Сохраняет список программ в файл list.txt"""
    try:
        print(f"Попытка сохранения списка программ в директории: {BASE_DIRECTORY}")
        result = save_programs(EXECUTABLE, BASE_DIRECTORY)
        if not result:
            print("Ошибка при сохранении списка программ. Попытка повторного сохранения...")
            # Пробуем сохранить еще раз с принудительным указанием директории
            result = save_programs(EXECUTABLE, BASE_DIRECTORY)
            print(f"Результат повторного сохранения: {result}")
        return result
    except Exception as e:
        print(f"ОШИБКА сохранения списка программ: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

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

def create_shortcut_if_needed(target_dir=None):
    """Создает ярлык программы в указанной директории, если запущен с аргументом командной строки"""
    if target_dir and os.path.isdir(target_dir):
        try:
            # Путь к иконке
            icon_path = os.path.join(SCRIPT_DIRECTORY, "launcher", "template", "icons", "launcher.ico")
            shortcut_path = os.path.join(target_dir, f"{APPLICATION_NAME}.lnk")
            
            # Создаем ярлык с рабочей директорией = target_dir
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = f'"{os.path.join(SCRIPT_DIRECTORY, "launcher.py")}"'
            shortcut.WorkingDirectory = target_dir
            shortcut.IconLocation = icon_path if os.path.exists(icon_path) else ""
            shortcut.WindowStyle = 1  # 1 = Normal window
            shortcut.Description = APPLICATION_NAME
            shortcut.Save()
            
            return True
        except Exception as e:
            return False
    return False

def parse_arguments():
    """Разбор аргументов командной строки"""
    parser = argparse.ArgumentParser(description='USB Bootable Tools Launcher')
    parser.add_argument('directory', nargs='?', help='Директория для создания ярлыка')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('--debug', action='store_true', help='Включить режим отладки')
    parser.add_argument('--no-browser', action='store_true', help='Не открывать браузер автоматически')
    return parser.parse_args()

def main():
    """Запускает программу и веб-сервер"""
    # Разбор аргументов командной строки
    args = parse_arguments()
    
    # Обработка режима отладки
    if args.debug:
        pass
    
    # Проверяем, нужно ли создать ярлык
    if args.directory:
        create_shortcut_if_needed(args.directory)
        # Если была указана директория, завершаем работу после создания ярлыка
        return
    
    if IS_RUNNING_FROM_ELSEWHERE:
        pass
    
    # Устанавливаем базовую директорию для всех модулей
    set_file_operations_base_directory(BASE_DIRECTORY)
    set_launcher_base_directory(SCRIPT_DIRECTORY)  # Для запуска программ используем пути из оригинальной директории
    set_scan_base_directory(BASE_DIRECTORY)
    
    # Загружаем список программ
    success = load_program_list()
    if not success:
        pass
    
    # Устанавливаем список программ для модуля сканирования
    set_program_list(EXECUTABLE, ProgramInfo, EXECUTABLE_EXTENSIONS, EXCLUDED_DIRS, EXCLUDED_FILENAMES)
    
    # Инициализируем веб-маршруты
    init_web_routes(app, EXECUTABLE, BASE_DIRECTORY, load_program_list, save_program_list)
    
    # Устанавливаем переменную окружения для подавления предупреждений Flask
    os.environ['WERKZEUG_SILENCE_LOGGING'] = '1'
    
    # Находим свободный порт
    available_port = find_available_port(SERVER_PORT, MAX_PORT)
    if available_port is None:
        print(f"ОШИБКА: Не удалось найти свободный порт в диапазоне {SERVER_PORT}-{MAX_PORT}")
        return
    else:
        print(f"Запуск сервера на порту: {available_port}")
    
    # Запуск сервера в отдельном потоке
    server_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=available_port, use_reloader=False), 
        daemon=True
    )
    server_thread.start()
    
    # Небольшая задержка перед открытием браузера (чтобы Flask успел запуститься)
    time.sleep(0.5)
    
    # Открываем браузер, если не указан флаг --no-browser
    if not args.no_browser:
        open_browser(available_port)
    
    # URL приложения для ручного открытия
    app_url = f"http://localhost:{available_port}"
    print(f"Сервер запущен. Доступ по ссылке: {app_url}")
    print("Нажмите Enter для остановки.")
    
    try:
        input()
    except KeyboardInterrupt:
        pass
    
    print("Завершение работы...")
    os._exit(0)

if __name__ == '__main__':
    main()
