"""
Модуль сканирования для нахождения и управления программами.
"""
import os
import time
import threading
from program_operations import ProgramInfo, remove_program
from html_utils import escape_html
from file_description import extract_version_info, format_file_info

# Глобальные переменные для отслеживания статуса сканирования
scan_status = {
    "running": False,
    "progress": 0,
    "total_files": 0,
    "scanned_files": 0,
    "new_programs": 0,
    "missing_files": 0,
    "removed_files": 0,
    "last_file": "",
    "start_time": 0,
    "end_time": 0
}

# Глобальные переменные
EXECUTABLE = None
BASE_DIRECTORY = None
SOFT_DIRECTORY = None
# Переменные, которые будут установлены через функцию set_program_list
_executable_extensions = None
_ignore_extensions = None
_excluded_dirs = None
_excluded_filenames = None

def set_scan_base_directory(base_dir):
    """Устанавливает базовую директорию для сканирования"""
    global BASE_DIRECTORY, SOFT_DIRECTORY
    BASE_DIRECTORY = base_dir
    SOFT_DIRECTORY = os.path.join(base_dir, 'SOFT')

def set_program_list(programs, program_info_class=None, exts=None, excluded_dirs=None, excluded_files=None, ignore_exts=None):
    """Устанавливает список программ и параметры для сканирования"""
    global EXECUTABLE, _executable_extensions, _excluded_dirs, _excluded_filenames, _ignore_extensions
    EXECUTABLE = programs
    
    # Обновляем параметры, если они предоставлены
    if exts:
        _executable_extensions = exts
    if excluded_dirs:
        _excluded_dirs = excluded_dirs
    if excluded_files:
        _excluded_filenames = excluded_files
    
    # Устанавливаем игнорируемые расширения, гарантируя, что это список
    _ignore_extensions = ignore_exts if ignore_exts is not None else []

def get_scan_status():
    """Возвращает текущий статус сканирования"""
    global scan_status
    
    # Формируем сообщение о статусе
    if scan_status["running"]:
        status_message = f"Сканирование... {scan_status['progress']}%"
    else:
        if scan_status["end_time"] > 0:
            duration = scan_status["end_time"] - scan_status["start_time"]
            status_message = f"Сканирование завершено за {duration:.1f} сек"
        else:
            status_message = "Сканирование не запущено"
    
    # Готовим лог для отображения
    log_lines = []
    if scan_status["running"]:
        log_lines.append(f"Найдено файлов: {scan_status['total_files']}")
        log_lines.append(f"Обработано: {scan_status['scanned_files']}")
        log_lines.append(f"Новых программ: {scan_status['new_programs']}")
        log_lines.append(f"Последний файл: {scan_status['last_file']}")
    elif scan_status["end_time"] > 0:
        log_lines.append(f"Всего найдено файлов: {scan_status.get('total_found_files', 0)}")
        log_lines.append(f"В списке файлов: {scan_status.get('total_in_list', 0)}")
        log_lines.append(f"Ложных ссылок в списке: {scan_status['missing_files']}")
        log_lines.append(f"Новых найденых файлов: {scan_status['new_programs']}")
        
        duration = scan_status["end_time"] - scan_status["start_time"]
        log_lines.append(f"Время выполнения: {duration:.1f} сек")
    
    return {
        "running": scan_status["running"],
        "finished": not scan_status["running"] and scan_status["end_time"] > 0,
        "progress": scan_status["progress"],
        "status": status_message,
        "log": log_lines,
        "found_files": scan_status["new_programs"],
        "missing_files": scan_status["missing_files"],
        "removed_files": scan_status["removed_files"],
        "last_file": scan_status["last_file"],
        "total_files": scan_status["total_files"],
        "scanned_files": scan_status["scanned_files"]
    }

def start_scan_in_thread(save_program_list_func):
    """Запускает сканирование в отдельном потоке"""
    global scan_status
    
    # Проверяем, не запущено ли уже сканирование
    if scan_status["running"]:
        return "Сканирование уже запущено"
    
    # Запускаем сканирование в отдельном потоке
    scan_thread = threading.Thread(target=scan_process, args=(save_program_list_func,))
    scan_thread.daemon = True
    scan_thread.start()
    
    return "Сканирование запущено"

def scan_process(save_program_list_func):
    """Основной процесс сканирования"""
    global scan_status, EXECUTABLE
    
    # Инициализируем статус сканирования
    scan_status["running"] = True
    scan_status["progress"] = 0
    scan_status["total_files"] = 0
    scan_status["scanned_files"] = 0
    scan_status["new_programs"] = 0
    scan_status["missing_files"] = 0
    scan_status["removed_files"] = 0 # Сбрасываем при каждом сканировании
    scan_status["last_file"] = ""
    scan_status["start_time"] = time.time()
    scan_status["end_time"] = 0
    scan_status["missing_paths"] = [] # Сбрасываем при каждом сканировании

    try:
        # Проверка базовых условий
        if not BASE_DIRECTORY or not SOFT_DIRECTORY:
            raise ValueError("Не установлена базовая директория")

        if not os.path.exists(SOFT_DIRECTORY):
            # Исправлено: ValueValueError -> ValueError
            raise ValueError(f"Директория SOFT не найдена: {SOFT_DIRECTORY}")

        if EXECUTABLE is None:
            raise ValueError("Список программ не инициализирован")

        # --- Подсчет существующих файлов ДО обновления списка ---
        existing_files_before_scan = 0
        for program in EXECUTABLE:
            full_path = os.path.join(BASE_DIRECTORY, program.path)
            if os.path.isfile(full_path):
                existing_files_before_scan += 1
        # --- Конец блока подсчета ---

        # 1. Сканирование директории и поиск новых программ
        found_programs = find_executable_files()

        # 2. Сравнение со списком и обновление (добавление новых)
        new_programs_count = update_program_list(found_programs, save_program_list_func)

        # 3. Проверка существующих файлов (поиск отсутствующих, но без удаления)
        # missing_paths сохраняются в scan_status["missing_paths"]
        missing_files_count, _ = check_missing_files(save_program_list_func) # removed_count здесь всегда 0

        # Формируем итоговую информацию
        total_found = len(found_programs)

        # Выводим информацию в нужном формате
        print("\n----------------")
        print(f"Всего найдено исполняемых файлов: {total_found}")
        # Используем значение, посчитанное до обновления
        print(f"В списке существующих файлов (до сканирования): {existing_files_before_scan}")
        print(f"Всего в списке файлов (после сканирования): {len(EXECUTABLE)}") # Общее количество после добавления новых
        print(f"Ложных ссылок в списке (найдено): {missing_files_count}")
        print(f"Новых найденых файлов: {new_programs_count}")
        if missing_files_count > 0:
             print(f"Обнаружено {missing_files_count} отсутствующих файлов. Нажмите 'Сохранить', чтобы удалить их из списка.")
        else:
             print("Отсутствующие файлы не обнаружены.")
        print("----------------\n")

        # Обновляем статистику для отображения на веб-странице
        scan_status["total_found_files"] = total_found
        # Используем значение, посчитанное до обновления
        scan_status["total_in_list"] = existing_files_before_scan
        scan_status["total_all_in_list"] = len(EXECUTABLE) # Общее количество после добавления
        scan_status["missing_files"] = missing_files_count # Количество найденных отсутствующих
        scan_status["new_programs"] = new_programs_count # Количество добавленных новых

        # Завершение сканирования
        scan_status["running"] = False
        scan_status["end_time"] = time.time()
        duration = scan_status["end_time"] - scan_status["start_time"]

        result_message = (
            f"Всего найдено исполняемых файлов: {total_found}\n"
            f"В списке существующих файлов (до сканирования): {existing_files_before_scan}\n"
            f"Всего в списке файлов (после сканирования): {len(EXECUTABLE)}\n"
            f"Ложных ссылок в списке (найдено): {missing_files_count}\n"
            f"Новых найденых файлов: {new_programs_count}\n"
            f"Время выполнения: {duration:.1f} сек\n"
            f"----------------\n"
        )
        if missing_files_count > 0:
            result_message += f"Обнаружено {missing_files_count} отсутствующих файлов. Нажмите 'Сохранить', чтобы удалить их из списка."
        else:
            result_message += "Отсутствующие файлы не обнаружены."

        return result_message

    except Exception as e:
        # В случае ошибки обновляем статус
        scan_status["running"] = False
        scan_status["end_time"] = time.time()
        import traceback
        print(f"Ошибка при сканировании: {str(e)}")
        print(traceback.format_exc())
        return f"Ошибка при сканировании: {str(e)}"

def find_executable_files():
    """Находит исполняемые файлы в директории SOFT"""
    global scan_status
    
    found_programs = []
    
    # Подсчитываем общее количество файлов для прогресса
    file_count = sum(len(files) for _, _, files in os.walk(SOFT_DIRECTORY))
    scan_status["total_files"] = file_count
    
    # Сканируем директорию
    for root, dirs, files in os.walk(SOFT_DIRECTORY):
        # Пропускаем исключенные директории
        dirs[:] = [d for d in dirs if d not in _excluded_dirs]
        
        for file in files:
            # Обновляем статус сканирования
            scan_status["scanned_files"] += 1
            scan_status["last_file"] = file
            
            # Вычисляем прогресс
            if scan_status["total_files"] > 0:
                scan_status["progress"] = int((scan_status["scanned_files"] / scan_status["total_files"]) * 100)
            
            # Пропускаем файлы из списка исключений
            if file in _excluded_filenames:
                continue
                
            # Проверяем расширение файла
            _, ext = os.path.splitext(file.lower())
            if ext in _ignore_extensions:
                continue
                
            if ext in _executable_extensions:
                file_path = os.path.join(root, file)
                
                # Получаем относительный путь
                rel_path = os.path.relpath(file_path, BASE_DIRECTORY)
                rel_path = rel_path.replace('\\', '/')  # Нормализуем для Windows
                
                # Добавляем в список найденных программ
                found_programs.append(rel_path)
    
    return found_programs

def update_program_list(found_paths, save_program_list_func):
    """Обновляет список программ на основе найденных файлов"""
    global EXECUTABLE, scan_status

    # Получаем существующие пути программ
    existing_paths = [program.path for program in EXECUTABLE]

    # Находим новые программы (есть в found_paths, но нет в existing_paths)
    new_paths = [path for path in found_paths if path not in existing_paths]

    new_count = 0

    # Добавляем новые программы в список
    for path in new_paths:
        # Определяем категорию на основе пути
        path_parts = path.split('/')
        category = "Прочее"
        # Исправлено: 'и' на 'and'
        if len(path_parts) > 1 and path_parts[0].lower() == "soft":
            category = path_parts[1] if len(path_parts) > 2 else "Прочее"

        # Получаем полный путь к файлу
        
        full_path = os.path.join(BASE_DIRECTORY, path)
        
        # --- Используем format_file_info для получения описания --- 
        description = format_file_info(full_path)
        if not description or description.startswith("Файл не найден") or description.startswith("Ошибка"):
            # Если format_file_info не вернула полезной информации, используем имя файла
            file_name = os.path.basename(path)
            description = f"Программа {file_name}"
        # --- Конец использования format_file_info --- 

        # Экранируем HTML для безопасного отображения КАТЕГОРИИ
        category_safe = escape_html(category)
        # НЕ экранируем описание здесь, сделаем это при рендеринге
        description_safe = description # Store the raw description with newlines
        
        # Создаем новый объект программы
        program = ProgramInfo(path, category_safe, description_safe) # Use raw description here
        program.original_category = category
        program.original_description = description # Сохраняем неэкранированное полное описание
        
        # Добавляем программу в список
        EXECUTABLE.append(program)
        new_count += 1
        scan_status["new_programs"] += 1
    
    # Возвращаем количество новых программ
    return new_count

def check_missing_files(save_program_list_func):
    """Проверяет существующие программы и находит отсутствующие, но не удаляет их автоматически"""
    global EXECUTABLE, scan_status

    if not EXECUTABLE:
        return 0, 0

    missing_paths = []
    
    # Сначала находим все отсутствующие файлы
    for program in EXECUTABLE:
        try:
            # Получаем полный путь
            full_path = os.path.join(BASE_DIRECTORY, program.path)
            
            # Проверяем существование файла
            if not os.path.isfile(full_path):
                missing_paths.append(program.path)
        except Exception as e:
            print(f"Ошибка при проверке файла {program.path}: {str(e)}")
    
    # Количество отсутствующих файлов
    missing_count = len(missing_paths)
    
    # НЕ удаляем файлы автоматически, только отмечаем их как отсутствующие
    # Пользователь должен нажать "Сохранить", чтобы применить изменения
    
    # Обновляем статистику
    scan_status["missing_files"] = missing_count
    scan_status["removed_files"] = 0  # Не удаляем автоматически
    
    # Сохраняем пути отсутствующих файлов для использования при нажатии "Сохранить"
    scan_status["missing_paths"] = missing_paths
    
    return missing_count, 0

def apply_scan_changes(save_program_list_func):
    """Применяет изменения, обнаруженные при сканировании (удаляет отсутствующие файлы)"""
    global EXECUTABLE, scan_status

    # Получаем список путей отсутствующих файлов из статуса
    missing_paths_to_remove = scan_status.get("missing_paths", [])

    # Проверяем, есть ли что удалять
    if not missing_paths_to_remove:
        return "Нет изменений для применения (отсутствующие файлы не найдены)."

    # Создаем новый список, исключая отсутствующие программы
    original_count = len(EXECUTABLE)
    programs_to_keep = [p for p in EXECUTABLE if p.path not in missing_paths_to_remove]

    # Обновляем глобальный список EXECUTABLE
    EXECUTABLE[:] = programs_to_keep
    removed_count = original_count - len(EXECUTABLE)

    # Сохраняем изменения в файл
    try:
        save_program_list_func()
    except Exception as e:
        print(f"Ошибка при сохранении списка программ после удаления: {e}")
        return f"Ошибка при сохранении списка: {e}"

    # Обновляем статистику
    scan_status["removed_files"] = removed_count # Записываем, сколько было удалено
    scan_status["missing_files"] = 0 # После удаления их больше нет в списке как "отсутствующих"
    scan_status["missing_paths"] = [] # Очищаем список путей для удаления

    print(f"Удалено {removed_count} записей из списка программ.")
    return f"Удалено {removed_count} ложных ссылок на файлы из списка."