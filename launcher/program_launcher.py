import os
import subprocess
import time
import urllib.parse
from flask import Response, request

# Проверка наличия дополнительных модулей
try:
    import win32gui
    import win32con
    import win32process
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False
    print("Pywin32 не установлен. Окна программ не будут активироваться автоматически.")

# Проверка наличия pywinauto
try:
    from pywinauto.application import Application
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    print("Pywinauto не установлен. Будут использоваться стандартные методы активации окон.")

# Глобальная переменная для хранения базовой директории
BASE_DIRECTORY = None

def set_base_directory(directory):
    """Установка базовой директории для использования в функциях модуля"""
    global BASE_DIRECTORY
    BASE_DIRECTORY = directory
    print(f"База директория установлена: {BASE_DIRECTORY}")
    return BASE_DIRECTORY

def launch_program(program_path, base_directory=None):
    """Запускает программу по указанному пути"""
    if not program_path:
        return Response("Ошибка: не указан путь к программе", content_type='text/plain; charset=utf-8')
    
    try:
        # Decode URL-encoded path
        program_path = urllib.parse.unquote(program_path)
        # Determine if path is absolute or relative
        if os.path.isabs(program_path):
            full_path = os.path.normpath(program_path)
        else:
            # Используем переданную базовую директорию или глобальную
            base_dir = base_directory or BASE_DIRECTORY
            if not base_dir:
                return Response("Ошибка: не задана базовая директория", content_type='text/plain; charset=utf-8')
            full_path = os.path.normpath(os.path.join(base_dir, program_path))
        
        print(f"Attempting to launch: {full_path}")
        
        if not os.path.exists(full_path):
            result = f"Ошибка: файл {full_path} не найден"
            print(result)
            return Response(result, content_type='text/plain; charset=utf-8')
        
        # Определяем расширение файла
        file_extension = os.path.splitext(full_path)[1].lower()
        
        # Получаем директорию файла
        file_directory = os.path.dirname(full_path)
        
        # Особая обработка для cmd и bat файлов
        if file_extension in ['.cmd', '.bat']:
            # Переходим в директорию файла и запускаем его с правильным путем
            # Используем команду cd, чтобы перейти в директорию файла перед запуском
            filename = os.path.basename(full_path)
            command = f'cmd /c "cd /d "{file_directory}" && {filename}"'
            use_shell = True
        else:
            # Для остальных типов файлов используем стандартный подход
            command = f'"{full_path}"'
            use_shell = True
        
        process = subprocess.Popen(command, shell=use_shell)
        result = f"Запущена программа: {os.path.basename(program_path)}"
        print(result)
        
        # Bring the launched program to the foreground
        # Для cmd и bat файлов не пытаемся активировать окно, 
        # так как они запускаются в командной строке
        if file_extension not in ['.cmd', '.bat']:
            activate_window(full_path)
        
        return Response(result, content_type='text/plain; charset=utf-8')
    
    except Exception as e:
        result = f"Ошибка запуска программы: {str(e)}"
        print(result)
        return Response(result, content_type='text/plain; charset=utf-8')

def open_folder(program_path, base_directory=None):
    """Открывает папку с программой (устаревшая версия)"""
    if not program_path:
        return Response("Ошибка: не указан путь к программе", content_type='text/plain; charset=utf-8')
    
    try:
        program_path = urllib.parse.unquote(program_path)
        # Используем переданную базовую директорию или глобальную
        base_dir = base_directory or BASE_DIRECTORY
        if not base_dir:
            return Response("Ошибка: не задана базовая директория", content_type='text/plain; charset=utf-8')
        full_path = os.path.normpath(os.path.join(base_dir, program_path) if not os.path.isabs(program_path) else program_path)
        
        folder_path = os.path.dirname(full_path)
        if not os.path.exists(folder_path):
            return Response(f"Ошибка: папка {folder_path} не найдена", content_type='text/plain; charset=utf-8')
        
        # Открываем папку
        subprocess.Popen(f'explorer "{folder_path}"')
        
        return Response(f"Открыта папка: {folder_path}", content_type='text/plain; charset=utf-8')
    
    except Exception as e:
        return Response(f"Ошибка открытия папки: {str(e)}", content_type='text/plain; charset=utf-8')


def handle_open_folder():
    """Маршрут Flask для открытия папки с программой и активации окна проводника"""
    program_path = request.args.get('path')
    if not program_path:
        return Response("Ошибка: не указан путь к программе", content_type='text/plain; charset=utf-8')
    
    try:
        # Decode URL-encoded path
        program_path = urllib.parse.unquote(program_path)
        # Determine if path is absolute or relative
        if os.path.isabs(program_path):
            full_path = os.path.normpath(program_path)
        else:
            # Проверяем наличие базовой директории
            if not BASE_DIRECTORY:
                return Response("Ошибка: не задана базовая директория", content_type='text/plain; charset=utf-8')
            full_path = os.path.normpath(os.path.join(BASE_DIRECTORY, program_path))
        
        folder_path = os.path.dirname(full_path)
        print(f"Attempting to open folder: {folder_path}")
        
        if not os.path.exists(folder_path):
            result = f"Ошибка: папка {folder_path} не найдена"
            print(result)
            return Response(result, content_type='text/plain; charset=utf-8')
        
        # Открытие папки с помощью explorer
        subprocess.Popen(f'explorer "{folder_path}"')
        result = f"Открыта папка: {folder_path}"
        print(result)
        
        # Активируем окно проводника
        if PYWIN32_AVAILABLE:
            folder_name = os.path.basename(folder_path)
            max_attempts = 8
            attempt = 0
            hwnd = None
            
            while attempt < max_attempts and hwnd is None:
                time.sleep(0.6)  # Ожидаем открытия проводника
                def enum_explorer_windows(h, windows):
                    window_text = win32gui.GetWindowText(h)
                    if (win32gui.IsWindowVisible(h) and 
                        ("explorer" in window_text.lower() or 
                         folder_name.lower() in window_text.lower() or
                         "проводник" in window_text.lower())):
                        windows.append(h)
                
                explorer_windows = []
                win32gui.EnumWindows(enum_explorer_windows, explorer_windows)
                hwnd = explorer_windows[0] if explorer_windows else None
                attempt += 1
            
            if hwnd:
                try:
                    # Сначала пробуем pywinauto, если доступен
                    if PYWINAUTO_AVAILABLE:
                        try:
                            # Используем pywинаuto для активации окна проводника
                            app_instance = Application().connect(handle=hwnd)
                            app_instance.window(handle=hwnd).set_focus()
                            print(f"Explorer window activated using pywinauto: {win32gui.GetWindowText(hwnd)}")
                        except Exception as e:
                            print(f"Ошибка при активации проводника через pywинаuto: {str(e)}")
                            # Если не удалось, используем стандартные методы
                            raise
                    else:
                        # Если pywinauto недоступен, сразу переходим к стандартным методам
                        raise ImportError("pywinauto not available")
                        
                except Exception:
                    # Запасной вариант: комбинированный метод активации окна проводника
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    
                    time.sleep(0.2)
                    
                    win32gui.SetForegroundWindow(hwnd)
                    win32gui.BringWindowToTop(hwnd)
                    win32gui.SetActiveWindow(hwnd)
                    
                    time.sleep(0.1)
                    
                    win32gui.SetForegroundWindow(hwnd)
                    
                    print(f"Explorer window activated using standard methods: {win32gui.GetWindowText(hwnd)}")
            else:
                print(f"Could not find Explorer window for {folder_name} after {max_attempts} attempts")
        
        return Response(result, content_type='text/plain; charset=utf-8')
    
    except Exception as e:
        result = f"Ошибка открытия папки: {str(e)}"
        print(result)
        return Response(result, content_type='text/plain; charset=utf-8')

def activate_window(full_path):
    """Активирует окно программы после запуска"""
    if not PYWIN32_AVAILABLE:
        return
        
    try:
        program_name = os.path.splitext(os.path.basename(full_path))[0]
        max_attempts = 10  # Увеличиваем количество попыток
        attempt = 0
        hwnd = None
        
        # Программа уже должна быть запущена в launch_program, не запускаем её снова
        
        while attempt < max_attempts and hwnd is None:
            time.sleep(0.7)  # Увеличиваем интервал ожидания для тяжелых программ
            def enum_windows_callback(h, windows):
                # Проверяем несколько условий для нахождения окна
                if not win32gui.IsWindowVisible(h):
                    return
                
                window_text = win32gui.GetWindowText(h).lower()
                
                # 1. Проверка по имени программы
                if program_name.lower() in window_text:
                    windows.append(h)
                    return
                
                # 2. Проверка по процессам с похожим именем
                try:
                    # Получаем ID процесса для текущего окна
                    _, found_pid = win32process.GetWindowThreadProcessId(h)
                    
                    # Проверяем, что окно принадлежит процессу с похожим именем
                    try:
                        import psutil
                        process = psutil.Process(found_pid)
                        if program_name.lower() in process.name().lower():
                            windows.append(h)
                            return
                    except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                except:
                    pass
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            hwnd = windows[0] if windows else None
            attempt += 1
        
        if hwnd:
            try:
                # Сначала пробуем pywinauto, если доступен
                if PYWINAUTO_AVAILABLE:
                    try:
                        # Используем pywинаuto для активации окна
                        app_instance = Application().connect(handle=hwnd)
                        app_instance.window(handle=hwnd).set_focus()
                        print(f"Window activated using pywinauto: {win32gui.GetWindowText(hwnd)}")
                    except Exception as e:
                        print(f"Ошибка при активации через pywинаuto: {str(e)}")
                        # Если не удалось, используем стандартные методы
                        raise
                else:
                    # Если pywинаuto недоступен, сразу переходим к стандартным методам
                    raise ImportError("pywinauto not available")
                    
            except Exception:
                # Запасной вариант: комбинированный метод активации окна
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Восстанавливаем, если свернуто
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)     # Показываем окно
                
                time.sleep(0.2)
                
                win32gui.SetForegroundWindow(hwnd)
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetActiveWindow(hwnd)
                
                time.sleep(0.1)
                
                win32gui.SetForegroundWindow(hwnd)
                
                print(f"Window activated using standard methods: {win32gui.GetWindowText(hwnd)}")
        else:
            print(f"Could not find window for {program_name} after {max_attempts} attempts")
    except Exception as e:
        print(f"Ошибка при активации окна: {str(e)}")

def _get_child_pids(parent_pid):
    """Получает список ID дочерних процессов для указанного родительского процесса"""
    try:
        import psutil
        children = []
        try:
            parent = psutil.Process(parent_pid)
            children = parent.children(recursive=True)
            return [child.pid for child in children]
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return []
    except ImportError:
        # Если psutil не установлен, возвращаем пустой список
        print("psutil не установлен, невозможно получить список дочерних процессов")
        return []