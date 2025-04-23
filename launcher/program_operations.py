import os
from html_utils import escape_html, unescape_html

# Глобальные переменные
EXECUTABLE = None

def set_program_operations(programs):
    """Устанавливает глобальную переменную EXECUTABLE"""
    global EXECUTABLE
    EXECUTABLE = programs

def clear_favorites(save_func):
    """Удаляет все программы из избранного"""
    global EXECUTABLE
    
    print("Удаление всех файлов из избранного...")
    initial_count = len(EXECUTABLE)
    
    # Создаем новый список программ, исключая те, которые в избранном
    programs_to_keep = [prog for prog in EXECUTABLE if not prog.is_favorite]
    
    # Подсчитываем количество удаленных программ
    removed_count = initial_count - len(programs_to_keep)
    print(f"Удалено {removed_count} программ из избранного")
    
    # Заменяем список программ
    EXECUTABLE.clear()
    EXECUTABLE.extend(programs_to_keep)
    
    if removed_count > 0:
        print("Сохранение изменений...")
        result = save_func()  # Сохраняем изменения
        print(f"Результат сохранения: {result}")
        return result, f"Удалено {removed_count} программ из избранного"
    else:
        return False, "В избранном нет программ"

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
        
        # print(f"Сравнение '{normalized_path_to_remove}' с '{normalized_program_path_in_list}' (из {program.path})")
        
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

def remove_category(category_to_remove, save_func):
    """Удаляет все программы из указанной категории"""
    global EXECUTABLE
    
    # Не разрешаем удалять категорию "Избранное"
    if category_to_remove.lower() == "избранное":
        print(f"Попытка удаления защищенной категории 'Избранное'")
        return False, "Категория 'Избранное' не может быть удалена"
    
    print(f"Удаление всех программ в категории: {category_to_remove}")
    initial_count = len(EXECUTABLE)
    
    # Создаем новый список для программ, которые не входят в удаляемую категорию
    programs_to_keep = []
    
    for prog in EXECUTABLE:
        # Получаем оригинальную категорию без экранирования HTML
        original_category = getattr(prog, 'original_category', prog.category)
        if hasattr(prog, 'original_category'):
            # Если есть оригинальная категория, используем её
            if original_category != category_to_remove:
                programs_to_keep.append(prog)
        else:
            # Для совместимости - может быть у некоторых программ нет original_category
            from html_utils import unescape_html
            unescaped_category = unescape_html(prog.category)
            if unescaped_category != category_to_remove:
                programs_to_keep.append(prog)
    
    # Заменяем глобальный список на отфильтрованный
    EXECUTABLE.clear()
    EXECUTABLE.extend(programs_to_keep)
    
    removed_count = initial_count - len(EXECUTABLE)
    print(f"Удалено {removed_count} программ из категории '{category_to_remove}'")
    
    if removed_count > 0:
        print("Вызываем функцию сохранения...")
        result = save_func()  # Сохраняем изменения
        print(f"Результат сохранения: {result}")
        return result, f"Удалено {removed_count} программ из категории '{category_to_remove}'"
    else:
        return False, f"Программы в категории '{category_to_remove}' не найдены"