import os
import shutil
import json
from html_utils import escape_html, unescape_html

# Глобальная переменная для хранения базовой директории
BASE_DIRECTORY = None

def set_base_directory(directory):
    """Установка базовой директории для использования в функциях модуля"""
    global BASE_DIRECTORY
    # Убираем пробелы в начале и конце пути, если они есть
    BASE_DIRECTORY = directory.strip() if directory else None
    print(f"База директория для file_operations установлена: {BASE_DIRECTORY}")
    return BASE_DIRECTORY

def load_program_list(program_class=None, base_directory=None):
    """Загружает список программ из файла list.txt"""
    programs = []
    category_icons = {}
    
    # Используем переданную базовую директорию или глобальную
    base_dir = base_directory or BASE_DIRECTORY
    if not base_dir:
        print("Ошибка: не задана базовая директория")
        return [], {}
    
    # Убираем пробелы в начале и конце пути, если они есть
    base_dir = base_dir.strip()
        
    list_path = os.path.join(base_dir, 'list.txt')
    
    if not os.path.exists(list_path):
        print("Файл list.txt не найден! Создаем пустой файл.")
        try:
            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(list_path), exist_ok=True)
            # Создаем пустой файл
            with open(list_path, 'w', encoding='utf-8') as f:
                pass
            print(f"Создан пустой файл list.txt в {list_path}")
        except Exception as e:
            print(f"Ошибка при создании файла list.txt: {str(e)}")
        return [], {}
    
    # Пробуем разные кодировки
    for encoding in ['utf-8-sig', 'utf-8', 'cp1251', 'utf-16']:
        try:
            with open(list_path, 'r', encoding=encoding) as f:
                print(f"Чтение файла list.txt в кодировке {encoding}")
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # Определяем тип разделителя для избранного
                        is_favorite = False
                        
                        # Ищем разделители с учетом пробелов до и после
                        # Обрабатываем случаи где может быть любое количество пробелов до и после ||
                        if "||*||" in line:
                            is_favorite = True
                            parts = line.split("||*||", 1)
                            path = parts[0].strip()
                            rest = parts[1].strip() if len(parts) > 1 else ""
                        elif "||-||" in line:
                            parts = line.split("||-||", 1)
                            path = parts[0].strip()
                            rest = parts[1].strip() if len(parts) > 1 else ""
                        else:
                            # Поиск стандартного разделителя '||' с учетом пробелов
                            import re
                            matches = re.split(r'\s*\|\|\s*', line, 2)  # Разбиваем по || с любым количеством пробелов вокруг
                            
                            if len(matches) < 3:
                                print(f"Предупреждение: строка {line_num} имеет неверный формат: {line}")
                                continue
                                
                            path = matches[0].strip()
                            category = matches[1].strip()
                            description = matches[2].strip() if len(matches) > 2 else "Без описания"
                            rest = None
                        
                        # Обрабатываем новый формат (с ||*|| или ||-||)
                        if rest is not None:
                            # Разделяем оставшуюся часть по разделителю '||' с учетом пробелов
                            import re
                            parts = re.split(r'\s*\|\|\s*', rest, 1)  # Разбиваем по || с любым количеством пробелов
                            
                            if len(parts) > 1:
                                category = parts[0].strip()
                                description = parts[1].strip()
                            else:
                                category = rest.strip()
                                description = "Без описания"
                        
                        # Восстанавливаем переносы строк в описании
                        description = description.replace('\\n', '\n')
                        
                        # Экранируем HTML только в категории
                        category_safe = escape_html(category)
                        
                        if program_class:
                            # Создаем объект с экранированной категорией и НЕэкранированным описанием
                            program = program_class(path, category_safe, description, is_favorite)
                            program.original_category = category
                            program.original_description = description # Сохраняем оригинальное описание
                            programs.append(program)
                        else:
                            # Создаем словарь с экранированными и оригинальными значениями
                            programs.append({
                                'path': path,
                                'category': category_safe,
                                'description': description,
                                'is_favorite': is_favorite,
                                'original_category': category,
                                'original_description': description
                            })
                        
                        # Собираем уникальные категории для иконок (используем оригинальные значения)
                        category_lower = category.lower()
                        if category_lower not in category_icons:
                            category_icons[category_lower] = '<i class="bi bi-app"></i>'  # Иконка по умолчанию
                    except Exception as e:
                        print(f"Ошибка при обработке строки {line_num}: {line}")
                        print(f"Ошибка: {str(e)}")
                        continue
            
            print(f"Загружено {len(programs)} программ из list.txt")
            break
        except UnicodeDecodeError:
            continue
    else:
        print("Не удалось прочитать файл list.txt ни с одной из поддерживаемых кодировок")
    
    return programs, category_icons

def save_program_list(programs, base_directory=None):
    """Сохраняет список программ в файл list.txt"""
    # Используем переданную базовую директорию или глобальную
    base_dir = base_directory or BASE_DIRECTORY
    if not base_dir:
        print("Ошибка: не задана базовая директория")
        return False
    
    # Убираем пробелы в начале и конце пути, если они есть
    base_dir = base_dir.strip()
        
    list_path = os.path.join(base_dir, 'list.txt')
    
    try:
        print(f"Сохранение {len(programs)} программ в {list_path}") # Добавлено логирование

        with open(list_path, 'w', encoding='utf-8') as f:
            for program in programs:
                # Получаем оригинальные (неэкранированные) значения для сохранения
                if isinstance(program, dict):
                    path = program['path'].strip()
                    # Используем оригинальные значения, если они есть
                    category = program.get('original_category', program['category']).strip()
                    description = program.get('original_description', program['description'])
                    is_favorite = program.get('is_favorite', False)
                else:
                    path = program.path.strip()
                    # Используем оригинальные значения, если они есть
                    category = getattr(program, 'original_category', program.category).strip()
                    description = getattr(program, 'original_description', program.description)
                    is_favorite = getattr(program, 'is_favorite', False)
                
                # Если категория или описание были экранированы, восстанавливаем исходные значения
                category = unescape_html(category)
                description = unescape_html(description)
                
                # Убираем лишние пробелы в начале и конце важных полей
                category = category.strip()
                # Не обрезаем description.strip() полностью, так как могут быть намеренные пробелы внутри
                # Но убираем пробелы в начале
                description = description.lstrip()
                
                # Используем новый формат маркировки избранного
                favorite_mark = "||*||" if is_favorite else "||-||"
                # Корректное экранирование переносов строк для записи в файл
                escaped_description = description.replace('\r', '').replace('\n', '\\n') 
                
                # Используем точный формат без лишних пробелов: path||*||category||description
                f.write(f"{path}{favorite_mark}{category}||{escaped_description}\n")
        
        print(f"Список программ успешно сохранен в {list_path}")
        return True
    except Exception as e:
        print(f"Ошибка при сохранении списка программ: {str(e)}")
        return False

def rename_category(programs, old_category, new_category, base_directory):
    """
    Переименовывает категорию для всех программ в этой категории
    
    Args:
        programs: Список программ
        old_category: Старое название категории
        new_category: Новое название категории
        base_directory: Базовая директория
        
    Returns:
        tuple: (количество измененных программ, обновленный список программ)
    """
    changed_count = 0
    
    # Убираем пробелы в начале и конце
    old_category = old_category.strip() if old_category else ""
    new_category = new_category.strip() if new_category else ""
    base_directory = base_directory.strip() if base_directory else ""
    
    # Экранируем HTML в новой категории
    new_category_safe = escape_html(new_category)
    
    # Создаем копию списка, чтобы не изменять его во время итерации
    updated_programs = []
    
    try:
        print(f"Переименование категории с '{old_category}' на '{new_category}'")
        print(f"Всего программ в списке: {len(programs)}")
        
        for program in programs:
            # Убираем экранирование из категории для сравнения
            original_category = unescape_html(program.category)
            
            # Если категория совпадает, изменяем ее
            if original_category.strip() == old_category:
                # Обновляем категорию в объекте программы (и экранированную, и оригинальную)
                program.category = new_category_safe
                program.original_category = new_category
                changed_count += 1
                print(f"Обновлена категория программы: {program.path}")
            
            updated_programs.append(program)
        
        print(f"Изменено программ: {changed_count}")
        
        # Обновляем глобальный список программ
        for i in range(len(programs)):
            if i < len(updated_programs):
                programs[i] = updated_programs[i]
        
        # Если были изменения, сохраняем список в файл
        if changed_count > 0:
            save_program_list(programs, base_directory)
            print(f"Список программ сохранен после переименования категории")
        
        # Возвращаем результаты
        return changed_count, updated_programs
    except Exception as e:
        print(f"Ошибка при переименовании категории: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0, programs

def change_file_category(programs, program_path, new_category, base_directory):
    """
    Изменяет категорию для конкретной программы
    
    Args:
        programs: Список программ
        program_path: Путь к программе
        new_category: Новая категория
        base_directory: Базовая директория
        
    Returns:
        tuple: (успех операции, обновленный список программ)
    """
    # Убираем пробелы в начале и конце
    program_path = program_path.strip() if program_path else ""
    new_category = new_category.strip() if new_category else ""
    base_directory = base_directory.strip() if base_directory else ""
    
    # Экранируем HTML в новой категории
    new_category_safe = escape_html(new_category)
    
    # Сохраняем оригинальное значение категории для использования при сохранении
    original_new_category = new_category
    
    # Создаем копию списка, чтобы не изменять его во время итерации
    updated_programs = []
    
    try:
        # Находим программу в списке и изменяем категорию
        found = False
        print(f"Ищем программу с путем: {program_path}")
        print(f"Всего программ в списке: {len(programs)}")
        
        for program in programs:
            # Очищаем путь программы от пробелов для корректного сравнения
            clean_program_path = program.path.strip()
            
            if clean_program_path == program_path:
                print(f"Найдена программа: {program.path}")
                # Обновляем категорию в объекте программы
                program.category = new_category_safe
                program.original_category = original_new_category
                found = True
                print(f"Категория изменена на: {new_category_safe}")
            
            updated_programs.append(program)
        
        # Обновляем глобальный список программ
        for i in range(len(programs)):
            if i < len(updated_programs):
                programs[i] = updated_programs[i]
        
        if found:
            # Сохраняем список в файл
            save_program_list(programs, base_directory)
            print(f"Список программ сохранен после изменения категории")
            return True, updated_programs
        else:
            print(f"Программа не найдена: {program_path}")
            return False, programs
    except Exception as e:
        print(f"Ошибка при изменении категории программы: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, programs