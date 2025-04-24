import os
import sys
import winreg  # Встроенный модуль Python, не требует установки

# Константы для установки
MENU_NAME = "Создать ярлык Program Launcher"
COMMAND_KEY = "Program_Launcher_SC"  # Ключ из reg-файла
PYTHON_CMD = "python.exe"  # Использование python.exe без пути, как в install.reg
SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "launcher.py"))
ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "launcher", "template", "icons", "launcher.ico"))

def install_context_menu():
    """Регистрирует контекстное меню для папок в проводнике Windows"""
    try:
        print(f"Путь к Python: {PYTHON_CMD}")
        print(f"Путь к скрипту: {SCRIPT_PATH}")
        print(f"Путь к иконке: {ICON_PATH}")
        
        # Команды для запуска скрипта
        directory_command = f'"{PYTHON_CMD}" "{SCRIPT_PATH}" "%1"'
        background_command = f'"{PYTHON_CMD}" "{SCRIPT_PATH}" "%V"'
        
        # Удаляем старые ключи перед установкой
        remove_context_menu()
        
        success = True
        
        # Регистрируем ключ для Directory\shell
        try:
            # Создаем основной ключ
            dir_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"Directory\\shell\\{COMMAND_KEY}")
            winreg.SetValueEx(dir_key, "", 0, winreg.REG_SZ, MENU_NAME)
            winreg.SetValueEx(dir_key, "Icon", 0, winreg.REG_SZ, f"{ICON_PATH},0")
            
            # Создаем ключ command
            dir_cmd_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"Directory\\shell\\{COMMAND_KEY}\\command")
            winreg.SetValueEx(dir_cmd_key, "", 0, winreg.REG_SZ, directory_command)
            
            winreg.CloseKey(dir_cmd_key)
            winreg.CloseKey(dir_key)
            print("- Успешно установлено меню для папок")
        except Exception as e:
            print(f"- Ошибка при установке меню для папок: {e}")
            success = False
            
        # Регистрируем ключ для Directory\Background\shell
        try:
            # Создаем основной ключ
            bg_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"Directory\\Background\\shell\\{COMMAND_KEY}")
            winreg.SetValueEx(bg_key, "", 0, winreg.REG_SZ, MENU_NAME)
            winreg.SetValueEx(bg_key, "Icon", 0, winreg.REG_SZ, f"{ICON_PATH},0")
            
            # Создаем ключ command
            bg_cmd_key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"Directory\\Background\\shell\\{COMMAND_KEY}\\command")
            winreg.SetValueEx(bg_cmd_key, "", 0, winreg.REG_SZ, background_command)
            
            winreg.CloseKey(bg_cmd_key)
            winreg.CloseKey(bg_key)
            print("- Успешно установлено меню для фона папок")
        except Exception as e:
            print(f"- Ошибка при установке меню для фона папок: {e}")
            success = False
        
        if success:
            print("\nКонтекстное меню успешно установлено")
            print("Обновите проводник Windows, чтобы увидеть изменения (Диспетчер задач -> Проводник -> Перезапустить)")
        else:
            print("\nВозникли ошибки при установке меню. Попробуйте запустить от имени администратора.")
            
        return success
    except Exception as e:
        print(f"Ошибка при установке контекстного меню: {e}")
        return False

def remove_context_menu():
    """Удаляет контекстное меню из проводника Windows"""
    try:
        success = True
        
        # Удаляем ключ для Directory\shell
        try:
            # Сначала удаляем подключ command
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"Directory\\shell\\{COMMAND_KEY}\\command")
            # Затем удаляем основной ключ
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"Directory\\shell\\{COMMAND_KEY}")
            print(f"- Удален ключ Directory\\shell\\{COMMAND_KEY}")
        except:
            # Игнорируем ошибки, если ключи не существуют
            pass
            
        # Удаляем ключ для Directory\Background\shell
        try:
            # Сначала удаляем подключ command
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"Directory\\Background\\shell\\{COMMAND_KEY}\\command")
            # Затем удаляем основной ключ
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, f"Directory\\Background\\shell\\{COMMAND_KEY}")
            print(f"- Удален ключ Directory\\Background\\shell\\{COMMAND_KEY}")
        except:
            # Игнорируем ошибки, если ключи не существуют
            pass
        
        print("Контекстное меню успешно удалено")
        return success
    except Exception as e:
        print(f"Ошибка при удалении контекстного меню: {e}")
        return False

# Обработка команд установки/удаления
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            success = install_context_menu()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "uninstall":
            success = remove_context_menu()
            sys.exit(0 if success else 1)
    else:
        print("Используйте: setup.py install или setup.py uninstall")
        sys.exit(1)