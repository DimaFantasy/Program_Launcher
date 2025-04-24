import os
import sys
import subprocess
import platform
import ctypes
import winreg  # Добавляем модуль winreg для работы с реестром напрямую через Python

MENU_NAME = "Создать ярлык Program Launcher"
COMMAND_KEY = "Program_Launcher.ShortcutCreator"
PYTHON_CMD = sys.executable
SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "launcher.py"))
# GUID для Windows 11
HANDLER_GUID = "{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"

def is_admin():
    """Проверяет, запущен ли скрипт с правами администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_windows_11_or_newer():
    """Определяет, является ли операционная система Windows 11 или новее"""
    try:
        if platform.system() != 'Windows':
            return False
        
        build_number = int(platform.version().split('.')[2])
        return build_number >= 22000
    except (IndexError, ValueError):
        return False

def get_icon_path():
    """Получает путь к иконке программы"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(root_dir, "launcher", "template", "icons", "launcher.ico")
    
    if not os.path.exists(icon_path):
        print(f"Предупреждение: Иконка {icon_path} не найдена.")
        return None
    
    return icon_path

# Новый метод регистрации контекстного меню через Python API
def register_menu_entry_winreg(key_path, menu_name, command, icon_path=None):
    """Регистрирует контекстное меню через Python winreg"""
    try:
        # Преобразуем путь реестра в компоненты
        if key_path.startswith("HKEY_CLASSES_ROOT\\"):
            hkey = winreg.HKEY_CLASSES_ROOT
            subkey = key_path[18:]  # Убираем HKEY_CLASSES_ROOT\\
        elif key_path.startswith("HKEY_CURRENT_USER\\"):
            hkey = winreg.HKEY_CURRENT_USER
            subkey = key_path[17:]  # Убираем HKEY_CURRENT_USER\\
        elif key_path.startswith("HKEY_LOCAL_MACHINE\\"):
            hkey = winreg.HKEY_LOCAL_MACHINE
            subkey = key_path[19:]  # Убираем HKEY_LOCAL_MACHINE\\
        else:
            print(f"Неподдерживаемый корневой ключ в {key_path}")
            return False
            
        # Создаем основной ключ
        key = winreg.CreateKey(hkey, subkey)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, menu_name)
        
        # Добавляем иконку, если указана
        if icon_path and os.path.exists(icon_path):
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
        
        # Создаем подключ command
        cmd_key = winreg.CreateKey(hkey, f"{subkey}\\command")
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)
        
        # Закрываем ключи
        winreg.CloseKey(cmd_key)
        winreg.CloseKey(key)
        
        return True
    except Exception as e:
        print(f"Ошибка при регистрации меню {key_path}: {e}")
        return False

# Новый метод удаления ключа реестра через Python API
def unregister_menu_entry_winreg(key_path):
    """Удаляет контекстное меню с использованием Python winreg"""
    try:
        # Преобразуем путь реестра в компоненты
        if key_path.startswith("HKEY_CLASSES_ROOT\\"):
            hkey = winreg.HKEY_CLASSES_ROOT
            subkey = key_path[18:]  # Убираем HKEY_CLASSES_ROOT\\
        elif key_path.startswith("HKEY_CURRENT_USER\\"):
            hkey = winreg.HKEY_CURRENT_USER
            subkey = key_path[17:]  # Убираем HKEY_CURRENT_USER\\
        elif key_path.startswith("HKEY_LOCAL_MACHINE\\"):
            hkey = winreg.HKEY_LOCAL_MACHINE
            subkey = key_path[19:]  # Убираем HKEY_LOCAL_MACHINE\\
        else:
            print(f"Неподдерживаемый корневой ключ в {key_path}")
            return True  # Пропускаем неизвестные пути
            
        # Проверяем существование ключа
        try:
            winreg.OpenKey(hkey, subkey)
        except FileNotFoundError:
            # Ключ не существует, пропускаем его удаление
            return True
            
        # Удаляем подключ command, если он существует
        try:
            winreg.DeleteKey(hkey, f"{subkey}\\command")
        except FileNotFoundError:
            pass  # Игнорируем, если ключа нет
            
        # Удаляем основной ключ
        try:
            winreg.DeleteKey(hkey, subkey)
        except OSError as e:
            if e.winerror == 5:  # Отказано в доступе
                print(f"Отказано в доступе при удалении {key_path}. Требуются права администратора.")
            else:
                print(f"Ошибка при удалении {key_path}: {e}")
            return False
            
        return True
    except Exception as e:
        print(f"Ошибка при удалении меню {key_path}: {e}")
        return False

def register_menu_entry(key_path, menu_name, command, icon_path=None):
    """Централизованная функция для регистрации контекстного меню"""
    # Сначала пробуем через winreg
    if register_menu_entry_winreg(key_path, menu_name, command, icon_path):
        return True
    
    # Если не получилось через winreg, используем reg.exe как запасной вариант
    try:
        commands = [
            f'reg add "{key_path}" /ve /t REG_SZ /d "{menu_name}" /f',
            f'reg add "{key_path}\\command" /ve /t REG_SZ /d "{command}" /f'
        ]
        
        if icon_path and os.path.exists(icon_path):
            commands.insert(1, f'reg add "{key_path}" /v "Icon" /t REG_SZ /d "{icon_path}" /f')
            
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)
        return True
    except Exception as e:
        print(f"Ошибка при регистрации меню {key_path}: {e}")
        return False

def unregister_menu_entry(key_path):
    """Централизованная функция для удаления контекстного меню"""
    # Сначала пробуем через winreg
    if unregister_menu_entry_winreg(key_path):
        return True
    
    # Если не получилось через winreg, используем reg.exe как запасной вариант
    # Проверяем существование ключа перед удалением
    check_cmd = f'reg query "{key_path}" >nul 2>&1'
    result = subprocess.run(check_cmd, shell=True)
    if result.returncode != 0:
        # Ключ не существует, пропускаем его удаление
        return True
    
    try:
        # Сначала удаляем подключ command, если он существует
        check_command = f'reg query "{key_path}\\command" >nul 2>&1'
        if subprocess.run(check_command, shell=True).returncode == 0:
            subprocess.run(f'reg delete "{key_path}\\command" /f', shell=True, stderr=subprocess.DEVNULL)
        
        # Затем удаляем основной ключ
        subprocess.run(f'reg delete "{key_path}" /f', shell=True, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"Ошибка при удалении меню {key_path}: {e}")
        return False

def direct_register_menu():
    """Напрямую регистрирует контекстное меню через вызов reg.exe"""
    try:
        # Проверяем наличие SCRIPT_PATH
        if not os.path.exists(SCRIPT_PATH):
            print(f"ОШИБКА: Файл {SCRIPT_PATH} не найден!")
            return False
            
        is_win11 = is_windows_11_or_newer()
        icon_path = get_icon_path()
        
        # Команды для запуска скрипта
        directory_command = f'"{PYTHON_CMD}" "{SCRIPT_PATH}" "%1"'
        background_command = f'"{PYTHON_CMD}" "{SCRIPT_PATH}" "%V"'
        
        # Регистрируем в HKEY_CLASSES_ROOT
        register_menu_entry(
            f"HKEY_CLASSES_ROOT\\Directory\\shell\\{COMMAND_KEY}", 
            MENU_NAME, 
            directory_command, 
            icon_path
        )
        
        register_menu_entry(
            f"HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\{COMMAND_KEY}", 
            MENU_NAME, 
            background_command, 
            icon_path
        )
        
        # Для Windows 11 добавляем инструкцию
        if is_win11:
            print("Обнаружена Windows 11 - пункт меню будет доступен через 'Показать дополнительные параметры'")
        
        return True
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")
        return False

def direct_unregister_menu():
    """Удаляет контекстное меню через reg.exe"""
    try:
        is_win11 = is_windows_11_or_newer()
        
        # Ключи для удаления (стандартные для всех версий Windows)
        keys = [
            f"HKEY_CLASSES_ROOT\\Directory\\shell\\{COMMAND_KEY}",
            f"HKEY_CLASSES_ROOT\\Directory\\Background\\shell\\{COMMAND_KEY}"
        ]
        
        # Если Windows 11, добавляем ключи HKCU
        if is_win11:
            keys.extend([
                f"HKEY_CURRENT_USER\\Software\\Classes\\Directory\\shell\\{COMMAND_KEY}",
                f"HKEY_CURRENT_USER\\Software\\Classes\\Directory\\Background\\shell\\{COMMAND_KEY}"
            ])
            
            # Удаляем обработчик команд для Windows 11
            subprocess.run(
                f'reg delete "HKEY_CURRENT_USER\\Software\\Classes\\CLSID\\{HANDLER_GUID}" /f >nul 2>&1', 
                shell=True
            )
        
        # Удаляем все ключи
        for key in keys:
            unregister_menu_entry(key)
        
        return True
    except Exception as e:
        print(f"Ошибка при удалении: {e}")
        return False

def install_dependencies():
    """Устанавливает необходимые зависимости"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
        return True
    except Exception as e:
        print(f"Ошибка при установке зависимостей: {e}")
        return False

def unregister_win11_all():
    """Удаляет все записи меню Windows 11"""
    try:
        # Удаляем все возможные ключи Windows 11
        keys_to_delete = [
            "HKEY_CURRENT_USER\\Software\\Classes\\Directory\\Background\\shell\\ProgramLauncherW11",
            "HKEY_CURRENT_USER\\Software\\Classes\\Directory\\shell\\ProgramLauncherW11",
            "HKEY_CURRENT_USER\\Software\\Classes\\Directory\\ContextMenus\\ProgramLauncherMenu",
            f"HKEY_CURRENT_USER\\Software\\Classes\\CLSID\\{HANDLER_GUID}",
            f"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CommandStore\\shell\\{COMMAND_KEY}"
        ]
        
        for key in keys_to_delete:
            subprocess.run(f'reg delete "{key}" /f >nul 2>&1', shell=True)
        
        return True
    except Exception as e:
        print(f"Ошибка при удалении меню Windows 11: {e}")
        return False

def install_context_menu():
    """Регистрирует контекстное меню для папок в проводнике Windows"""
    if not is_admin():
        print("ВНИМАНИЕ: Для правильной работы контекстного меню требуются права администратора!")
        print("Пожалуйста, запустите install.bat от имени администратора")
        return False
    
    # Проверяем наличие файла launcher.py
    if not os.path.exists(SCRIPT_PATH):
        print(f"ОШИБКА: Файл {SCRIPT_PATH} не найден!")
        print(f"Ожидаемый путь: {SCRIPT_PATH}")
        return False
        
    try:
        # Удаляем все существующие записи
        print("Удаление существующих записей контекстного меню...")
        direct_unregister_menu()
        unregister_win11_all()
        
        is_win11 = is_windows_11_or_newer()
        print(f"Обнаружена операционная система: Windows {11 if is_win11 else 10}")
        
        # Устанавливаем стандартное меню
        print("Установка контекстного меню...")
        result = direct_register_menu()
        
        if result:
            print("Контекстное меню успешно зарегистрировано")
            print("Примечание: Для применения изменений может потребоваться перезапуск проводника")
        else:
            print("Не удалось зарегистрировать контекстное меню")
            
        return result
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")
        return False

def remove_context_menu():
    """Удаляет контекстное меню из проводника Windows"""
    try:
        print("Удаление контекстного меню...")
        direct_unregister_menu()
        unregister_win11_all()
        print("Контекстное меню успешно удалено")
        return True
    except Exception as e:
        print(f"Ошибка при удалении: {e}")
        return False

# Обработка команд установки/удаления
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            print("Установка Shortcut Creator...")
            install_dependencies()
            install_context_menu()
        elif sys.argv[1] == "uninstall":
            print("Удаление Shortcut Creator...")
            remove_context_menu()
    else:
        print("Используйте: setup.py install или setup.py uninstall")