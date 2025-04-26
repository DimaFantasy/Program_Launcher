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
    def __init__(self, path, category, description, is_favorite=False, is_hidden=False, header_color="#"):
        self.path = path
        self.category = category
        self.description = description
        self.is_favorite = is_favorite
        self.is_hidden = is_hidden
        self.header_color = header_color  # Новое поле для хранения цвета заголовка

def toggle_favorite(program_path, save_program_list_func):
    """Переключает статус избранного для программы"""
    # Очищаем путь от пробелов
    program_path = program_path.strip() if program_path else ""
    
    for program in EXECUTABLE:
        # Очищаем путь программы от пробелов для корректного сравнения
        clean_program_path = program.path.strip()
        
        if clean_program_path == program_path:
            program.is_favorite = not program.is_favorite
            save_program_list_func()
            return True, program.is_favorite
    return False, False

def change_description(program_path, new_description, save_program_list_func):
    """Изменяет описание программы"""
    # Очищаем путь от пробелов
    program_path = program_path.strip() if program_path else ""
    
    for program in EXECUTABLE:
        # Очищаем путь программы от пробелов для корректного сравнения
        clean_program_path = program.path.strip()
        
        if clean_program_path == program_path:
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
    
    # Очищаем путь от пробелов перед обработкой
    program_path_to_remove = program_path_to_remove.strip() if program_path_to_remove else ""
    
    # Нормализуем входной путь (например, к формату ОС)
    normalized_path_to_remove = os.path.normpath(program_path_to_remove)
    print(f"Нормализованный путь для удаления (входной): {normalized_path_to_remove}")
    
    print(f"Текущее количество программ: {len(EXECUTABLE)}")
    
    program_found = False
    index_to_remove = -1 # Индекс для удаления
    
    for i, program in enumerate(EXECUTABLE):
        # Очищаем путь программы от пробелов перед нормализацией
        clean_program_path = program.path.strip() if program.path else ""
        # Нормализуем путь из списка перед сравнением
        normalized_program_path_in_list = os.path.normpath(clean_program_path) 
        
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
            print(f"  - {p.path} (нормализованный: {os.path.normpath(p.path.strip() if p.path else '')})")
        print("--- Завершение удаления (не найдено) ---")
        return False # Возвращаем False, если программа не найдена

def remove_category(category_to_remove, save_func):
    """Удаляет все программы из указанной категории"""
    global EXECUTABLE
    
    # Очищаем категорию от пробелов
    category_to_remove = category_to_remove.strip() if category_to_remove else ""
    
    # Не разрешаем удалять категорию "Избранное"
    if category_to_remove.lower() == "избранное":
        print(f"Попытка удаления защищенной категории 'Избранное'")
        return False, "Категория 'Избранное' не может быть удалена"
    
    print(f"Удаление всех программ в категории: '{category_to_remove}'")
    initial_count = len(EXECUTABLE)
    
    # Создаем новый список для программ, которые не входят в удаляемую категорию
    programs_to_keep = []
    programs_to_remove = []
    
    # Сначала собираем все категории и логируем их для отладки
    all_categories = set()
    for prog in EXECUTABLE:
        original_category = getattr(prog, 'original_category', prog.category)
        if hasattr(prog, 'original_category'):
            clean_category = original_category.strip() if original_category else ""
            all_categories.add(clean_category)
        else:
            # Для совместимости - может быть у некоторых программ нет original_category
            from html_utils import unescape_html
            unescaped_category = unescape_html(prog.category)
            clean_category = unescaped_category.strip() if unescaped_category else ""
            all_categories.add(clean_category)
    
    print(f"Найденные категории в списке: {', '.join(all_categories)}")
    
    # Перебираем все программы и проверяем их категории
    for prog in EXECUTABLE:
        # Получаем оригинальную категорию без экранирования HTML
        original_category = getattr(prog, 'original_category', prog.category)
        
        # Определяем чистую категорию для сравнения
        if hasattr(prog, 'original_category'):
            # Если есть оригинальная категория, используем её и очищаем от пробелов
            clean_category = original_category.strip().lower() if original_category else ""
        else:
            # Для совместимости - может быть у некоторых программ нет original_category
            from html_utils import unescape_html
            unescaped_category = unescape_html(prog.category)
            # Очищаем от пробелов и приводим к нижнему регистру для регистронезависимого сравнения
            clean_category = unescaped_category.strip().lower() if unescaped_category else ""
        
        # Сравниваем категории (приводим к нижнему регистру для регистронезависимого сравнения)
        if clean_category == category_to_remove.lower():
            programs_to_remove.append(prog.path)  # Сохраняем путь для логирования
        else:
            programs_to_keep.append(prog)
    
    # Логируем найденные программы для удаления
    if programs_to_remove:
        print(f"Программы для удаления из категории '{category_to_remove}':")
        for path in programs_to_remove:
            print(f"  - {path}")
    
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
        print(f"Не найдено программ в категории '{category_to_remove}' для удаления")
        return False, f"Программы в категории '{category_to_remove}' не найдены"

def move_favorites_to_category(new_category, save_func):
    """Перемещает все избранные программы в указанную категорию"""
    global EXECUTABLE
    
    # Очищаем категорию от пробелов
    new_category = new_category.strip() if new_category else ""
    
    # Экранируем HTML в новой категории
    from html_utils import escape_html
    new_category_safe = escape_html(new_category)
    
    print(f"Перемещение избранных программ в категорию: {new_category}")
    
    # Счетчик перемещенных программ
    moved_count = 0
    
    # Перебираем все программы и изменяем категорию у избранных
    for program in EXECUTABLE:
        if program.is_favorite:
            # Сохраняем старую категорию для логирования
            old_category = getattr(program, 'original_category', program.category)
            
            # Обновляем категорию
            program.category = new_category_safe
            program.original_category = new_category
            
            print(f"Программа '{program.path}' перемещена из '{old_category}' в '{new_category}'")
            moved_count += 1
    
    if moved_count > 0:
        print(f"Всего перемещено программ: {moved_count}")
        # Сохраняем изменения
        result = save_func()
        return result, f"Перемещено {moved_count} программ в категорию '{new_category}'"
    else:
        return False, "В избранном нет программ для перемещения"

def toggle_hidden(program_path, save_program_list_func):
    """Переключает статус 'скрытый' для программы"""
    # Очищаем путь от пробелов
    program_path = program_path.strip() if program_path else ""
    
    found = False
    is_hidden = False
    is_favorite = False
    modified_program = None
    
    # Проверяем, находится ли программа в избранном и меняем её статус
    for program in EXECUTABLE:
        clean_program_path = program.path.strip()
        
        if clean_program_path == program_path:
            found = True
            is_favorite = program.is_favorite
            # Запоминаем текущее значение
            current_hidden_status = program.is_hidden
            # Инвертируем статус скрытия
            program.is_hidden = not current_hidden_status
            is_hidden = program.is_hidden
            modified_program = program
            break
    
    if found:
        # Если программа найдена, сохраняем изменения и проверяем результат
        try:
            print(f"Изменение статуса 'скрытый' для программы: {program_path}")
            print(f"Старый статус: {current_hidden_status}, Новый статус: {is_hidden}")
            print(f"Программа в избранном: {'Да' if is_favorite else 'Нет'}")
            
            # Для избранных программ используем дополнительную логику
            if is_favorite:
                print("Обрабатываем программу в избранном, используем специальную логику сохранения")
                # Форсируем дополнительное обновление атрибута
                if modified_program:
                    modified_program.is_hidden = is_hidden
                    print(f"Статус скрытия программы в избранном установлен на: {is_hidden}")
            
            # Вызываем функцию сохранения и проверяем результат
            save_result = save_program_list_func()
            print(f"Результат сохранения: {save_result}")
            
            # Если сохранение не удалось или программа в избранном, 
            # выполняем повторное сохранение для гарантии
            if not save_result or is_favorite:
                print("Выполняем принудительное повторное сохранение для надежности...")
                # Еще раз подтверждаем статус скрытия перед сохранением
                if modified_program:
                    modified_program.is_hidden = is_hidden
                # Повторное сохранение
                save_result = save_program_list_func()
                print(f"Результат повторного сохранения: {save_result}")
            
            return True, is_hidden
        except Exception as e:
            print(f"Ошибка при сохранении статуса скрытия: {str(e)}")
            import traceback
            traceback.print_exc()
            # В случае ошибки возвращаем оригинальное значение
            if modified_program:
                modified_program.is_hidden = current_hidden_status
            return False, current_hidden_status
    else:
        print(f"Программа не найдена для изменения статуса скрытия: {program_path}")
        return False, False