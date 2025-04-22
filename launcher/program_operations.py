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

def remove_program(program_path, save_program_list_func):
    """Удаляет программу из списка"""
    global EXECUTABLE
    original_count = len(EXECUTABLE)
    
    # Нормализуем путь для сравнения (заменяем обратные слеши на прямые)
    program_path_normalized = program_path.replace('\\', '/') # Use normalized path for comparison

    # Логируем для отладки
    print(f"--- Удаление программы ---")
    print(f"Получен путь для удаления: {program_path}")
    print(f"Нормализованный путь для удаления: {program_path_normalized}")
    print(f"Текущее количество программ: {original_count}")

    # Создаем новый список без удаляемой программы
    new_programs = []
    program_found = False
    for program in EXECUTABLE:
        # Логируем путь из списка для сравнения
        print(f"Сравнение с программой: {program.path}")
        if program.path == program_path_normalized:
            program_found = True
            print(f"  -> Найдено совпадение, программа будет удалена.")
        else:
            new_programs.append(program)
            print(f"  -> Нет совпадения.")

    # Обновляем глобальный список, если программа была найдена
    if program_found:
        EXECUTABLE[:] = new_programs # Update the global list in place
        removed = True
        print(f"Программа удалена: {program_path_normalized}")
        save_program_list_func()
    else:
        removed = False
        print(f"Программа не найдена для удаления: {program_path_normalized}")
        # Выводим все пути в списке для детальной отладки
        print("Текущие пути в списке EXECUTABLE:")
        for p in EXECUTABLE:
            print(f"  - {p.path}")

    print(f"--- Завершение удаления ---")
    return removed