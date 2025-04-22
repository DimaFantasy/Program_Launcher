import os
from html_utils import escape_html, unescape_html

# Глобальные переменные
EXECUTABLE = None

def set_program_operations(programs):
    """Устанавливает глобальную переменную EXECUTABLE"""
    global EXECUTABLE
    EXECUTABLE = programs

class ProgramInfo:
    """Класс для хранения информации о программе"""
    def __init__(self, path, category, description, is_favorite=False):
        self.path = path
        self.category = category
        self.description = description
        self.is_favorite = is_favorite

def toggle_favorite(program_path, save_program_list_func):
    """Переключает статус избранного для программы"""
    for program in EXECUTABLE:
        if program.path == program_path:
            program.is_favorite = not program.is_favorite
            save_program_list_func()
            return True, program.is_favorite
    return False, False

def change_description(program_path, new_description, save_program_list_func):
    """Изменяет описание программы"""
    for program in EXECUTABLE:
        if program.path == program_path:
            # Сохраняем оригинальное описание (неэкранированное)
            if hasattr(program, 'original_description'):
                program.original_description = new_description
            program.description = escape_html(new_description)
            save_program_list_func()
            return True
    return False

def remove_program(program_path_to_remove, save_func):
    """Удаляет программу из списка"""
    global EXECUTABLE
    
    print("--- Удаление программы ---")
    print(f"Получен путь для удаления: {program_path_to_remove}")
    
    # Нормализуем входной путь (например, к формату ОС)
    normalized_path_to_remove = os.path.normpath(program_path_to_remove)
    print(f"Нормализованный путь для удаления (входной): {normalized_path_to_remove}")
    
    print(f"Текущее количество программ: {len(EXECUTABLE)}")
    
    program_found = False
    index_to_remove = -1 # Индекс для удаления
    
    for i, program in enumerate(EXECUTABLE):
        # Нормализуем путь из списка перед сравнением
        normalized_program_path_in_list = os.path.normpath(program.path) 
        
        print(f"Сравнение '{normalized_path_to_remove}' с '{normalized_program_path_in_list}' (из {program.path})")
        
        # Сравниваем нормализованные пути
        if normalized_program_path_in_list == normalized_path_to_remove:
            print(f"  -> Найдено совпадение! Индекс для удаления: {i}")
            index_to_remove = i
            program_found = True
            break # Выходим из цикла после нахождения
        else:
            print(f"  -> Нет совпадения.")

    if program_found:
        removed_program = EXECUTABLE.pop(index_to_remove)
        print(f"Программа по пути '{removed_program.path}' удалена из списка.") # Используем path вместо name
        print("Вызов функции сохранения...")
        result = save_func() # Вызываем сохранение
        print("--- Завершение удаления (успешно) ---")
        return result
    else:
        print(f"Программа не найдена для удаления: {normalized_path_to_remove}")
        # Вывод текущих путей для отладки
        print("Текущие пути в списке EXECUTABLE:")
        for p in EXECUTABLE:
            print(f"  - {p.path} (нормализованный: {os.path.normpath(p.path)})")
        print("--- Завершение удаления (не найдено) ---")
        return False # Возвращаем False, если программа не найдена