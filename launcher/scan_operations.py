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
    "total_files_walked": 0, # Общее количество файлов, просмотренных при сканировании директорий
    "scanned_files": 0, # Количество файлов, обработанных на этапе сканирования директорий
    "current_weighted_done": 0, # Текущий взвешенный прогресс выполнения операций
    "total_weighted_ops": 0, # Общий вес всех операций сканирования
    "new_programs": 0, # Счетчик новых программ, найденных во время текущего сканирования
    "missing_files": 0, # Счетчик отсутствующих файлов, обнаруженных во время текущего сканирования
    "removed_files": 0, # Счетчик файлов, удаленных из списка после подтверждения
    "last_file": "", # Последний обработанный файл or этап
    "start_time": 0,
    "end_time": 0,
    "missing_paths": [], # Список путей отсутствующих файлов для последующего удаления
    # Статистика для финального отчета
    "total_found_files": 0, # Общее количество исполняемых файлов, найденных на диске
    "initial_list_length": 0, # Количество программ в списке до начала сканирования
    "existing_before_scan": 0, # Количество программ из списка, которые существовали на диске до сканирования
    "missing_after_scan": 0, # Количество программ из списка, которые отсутствуют на диске после сканирования
    "new_programs_added": 0, # Количество новых программ, добавленных в список
    "final_list_length": 0, # Количество программ в списке после завершения сканирования
    "log": [] # Лог сообщений о ходе сканирования
}

# Вес для операции чтения информации о файле (format_file_info), т.к. она может быть медленной
WEIGHT_FORMAT_INFO = 5

# Глобальные переменные
EXECUTABLE = None
BASE_DIRECTORY = None
# Убираем SOFT_DIRECTORY, будем использовать BASE_DIRECTORY напрямую
# SOFT_DIRECTORY = None
# Переменные, которые будут установлены через функцию set_program_list
_executable_extensions = None
_ignore_extensions = None
_excluded_dirs = None
_excluded_filenames = None

def set_scan_base_directory(base_dir):
    """Устанавливает базовую директорию для сканирования"""
    global BASE_DIRECTORY # Убираем SOFT_DIRECTORY
    BASE_DIRECTORY = base_dir
    # SOFT_DIRECTORY = os.path.join(base_dir, 'SOFT') # Убираем эту строку

def set_program_list(programs, program_info_class=None, exts=None, excluded_dirs=None, excluded_files=None, ignore_exts=None):
    """Устанавливает список программ и параметры для сканирования"""
    global EXECUTABLE, _executable_extensions, _excluded_dirs, _excluded_filenames, _ignore_extensions
    EXECUTABLE = programs
    
    # Обновляем параметры,  if они предоставлены
    if exts:
        _executable_extensions = exts
    if excluded_dirs:
        _excluded_dirs = excluded_dirs
    if excluded_files:
        _excluded_filenames = excluded_files
    
    # Устанавливаем игнорируемые расширения, гарантируя, что это список
    _ignore_extensions = ignore_exts if ignore_exts is not None else []

def _calculate_progress(done, total):
    """Рассчитывает прогресс в процентах."""
    if total <= 0:
        return 0
    return min(100, int((done / total) * 100))

def get_scan_status():
    """Возвращает текущий статус сканирования"""
    global scan_status
    
    # Формируем сообщение о статусе
    if scan_status["running"]:
        status_message = f"Сканирование... {scan_status['progress']}%"
        # Добавляем последний файл/этап для информативности
        if scan_status['last_file']:
             status_message += f" ({scan_status['last_file']})"
    else:
        if (scan_status["end_time"] > 0):
            duration = scan_status["end_time"] - scan_status["start_time"]
            status_message = f"Сканирование завершено за {duration:.1f} сек"
        else:
            status_message = "Сканирование not запущено"
    
    # Готовим лог для отображения
    log_lines = list(scan_status.get("log", [])) # Копируем лог
    if scan_status["running"]:
        # Показываем информацию о прогрессе во время сканирования
        log_lines.append(f"Файлов в списке (до сканирования): {scan_status.get('initial_list_length', 0)}")
        log_lines.append(f"Найдено новых программ (пока): {scan_status['new_programs']}")
        log_lines.append(f"Последний этап/файл: {scan_status['last_file']}")
    elif scan_status["end_time"] > 0:
        # Показываем финальную статистику
        log_lines.append(f"Найдено файлов на диске: {scan_status.get('total_found_files', 0)}")
        log_lines.append(f"Файлов в списке (до сканирования): {scan_status.get('initial_list_length', 0)}")
        log_lines.append(f"Из них существует на диске: {scan_status.get('existing_before_scan', 0)}")
        log_lines.append(f"Отсутствует на диске (после сканирования): {scan_status.get('missing_after_scan', 0)}")
        log_lines.append(f"Добавлено новых файлов в список: {scan_status.get('new_programs_added', 0)}")
        log_lines.append(f"Всего в списке файлов (после сканирования): {scan_status.get('final_list_length', 0)}")
        duration = scan_status["end_time"] - scan_status["start_time"]
        log_lines.append(f"Время выполнения: {duration:.1f} сек")
    
    return {
        "running": scan_status["running"],
        "finished": not scan_status["running"] and scan_status["end_time"] > 0,
        "progress": scan_status["progress"],
        "status": status_message,
        "log": log_lines,
        # Эти поля используются в JS для обновления счетчика в заголовке модального окна
        "found_files": scan_status.get('new_programs_added', scan_status['new_programs']), # Показываем добавленные or текущие новые
        "missing_files": scan_status.get('missing_after_scan', scan_status['missing_files']), # Показываем отсутствующие после сканирования or текущие
        "removed_files": scan_status["removed_files"],
        "last_file": scan_status["last_file"],
        # Используем total_files_walked для отображения общего числа просмотренных файлов
        "total_files": scan_status.get("total_files_walked", 0),
        "scanned_files": scan_status.get("scanned_files", 0) # Файлы, обработанные на этапе поиска
    }

def start_scan_in_thread(save_program_list_func):
    """Запускает сканирование в отдельном потоке"""
    global scan_status
    
    # Проверяем, not запущено ли уже сканирование
    if scan_status["running"]:
        return "Сканирование уже запущено"
    
    # Запускаем сканирование в отдельном потоке
    scan_thread = threading.Thread(target=scan_process, args=(save_program_list_func,))
    scan_thread.daemon = True
    scan_thread.start()
    
    return "Сканирование запущено"

def scan_process(save_program_list_func):
    """Основной процесс сканирования с взвешенным прогрессом"""
    global scan_status, EXECUTABLE

    # --- Инициализация статуса сканирования ---
    scan_status.update({
        "running": True, "progress": 0, "total_files_walked": 0, "scanned_files": 0,
        "current_weighted_done": 0, "total_weighted_ops": 0, "new_programs": 0,
        "missing_files": 0, "removed_files": 0, "last_file": "Инициализация...",
        "start_time": time.time(), "end_time": 0, "missing_paths": [],
        "total_found_files": 0, "initial_list_length": 0, "existing_before_scan": 0,
        "missing_after_scan": 0, "new_programs_added": 0, "final_list_length": 0,
        "log": ["Запуск сканирования..."]
    })

    try:
        # --- Проверка базовых условий ---
        if not BASE_DIRECTORY: raise ValueError("Не установлена базовая директория")
        if EXECUTABLE is None: raise ValueError("Список программ not инициализирован")

        # --- Подготовка ---
        initial_list_length = len(EXECUTABLE) # N_initial
        scan_status["initial_list_length"] = initial_list_length
        scan_status["log"].append(f"Файлов в списке: {initial_list_length}")

        existing_files_before_scan = sum(1 for p in EXECUTABLE if os.path.isfile(os.path.join(BASE_DIRECTORY, p.path))) # E_before
        scan_status["existing_before_scan"] = existing_files_before_scan
        scan_status["log"].append(f"Существующих файлов в списке: {existing_files_before_scan}")

        # --- Этап 1: Поиск исполняемых файлов (сканирование диска) ---
        scan_status["last_file"] = "Поиск файлов на диске..."
        # find_executable_files возвращает найденные пути и количество просмотренных файлов (N_walk)
        found_programs, total_files_walked = find_executable_files()
        scan_status["total_files_walked"] = total_files_walked
        scan_status["scanned_files"] = total_files_walked # Обновляем счетчик просмотренных файлов
        total_found = len(found_programs) # F_disk
        scan_status["total_found_files"] = total_found
        scan_status["log"].append(f"Найдено исполняемых файлов на диске: {total_found}")

        # --- Расчет общего веса операций и начального прогресса ---
        existing_paths = {program.path for program in EXECUTABLE} # Используем set для ускорения поиска
        new_paths = [path for path in found_programs if path not in existing_paths]
        total_new = len(new_paths) # N_new

        # Рассчитываем общий вес операций: вес 1 для сканирования файла и проверки существования, вес W для анализа нового файла
        scan_status["total_weighted_ops"] = total_files_walked + (total_new * WEIGHT_FORMAT_INFO) + initial_list_length

        # Обновляем выполненный вес после первого этапа (сканирования диска)
        scan_status["current_weighted_done"] = total_files_walked # Вес этапа сканирования = количеству файлов
        scan_status["progress"] = _calculate_progress(
            scan_status["current_weighted_done"], scan_status["total_weighted_ops"]
        )
        scan_status["last_file"] = "Анализ новых файлов..." if total_new > 0 else "Проверка отсутствующих файлов..."

        # --- Этап 2: Обновление списка программ (анализ новых файлов) ---
        # update_program_list принимает new_paths и вес, обновляет прогресс внутри
        new_programs_count = update_program_list(new_paths, save_program_list_func, WEIGHT_FORMAT_INFO) # N_new_added
        scan_status["new_programs_added"] = new_programs_count
        scan_status["log"].append(f"Добавлено новых файлов в список: {new_programs_count}")
        
        # Сохраняем список программ после добавления новых файлов
        if new_programs_count > 0:
            try:
                save_program_list_func()
                scan_status["log"].append(f"Список программ сохранен (добавлено {new_programs_count} файлов)")
            except Exception as e:
                scan_status["log"].append(f"Ошибка при сохранении списка: {str(e)}")
                print(f"Ошибка при сохранении списка: {str(e)}")
        
        scan_status["last_file"] = "Проверка отсутствующих файлов..."

        # --- Этап 3: Проверка отсутствующих файлов ---
        # check_missing_files обновляет прогресс внутри (вес 1 для каждой проверки)
        missing_files_count, _ = check_missing_files(save_program_list_func) # M_after
        scan_status["missing_after_scan"] = missing_files_count
        scan_status["log"].append(f"Обнаружено отсутствующих файлов (в списке): {missing_files_count}")

        # --- Финальная статистика ---
        # Правильно рассчитываем количество файлов после сканирования:
        # Текущее количество существующих файлов + добавленные новые
        list_length_after_scan = existing_files_before_scan + new_programs_count

        # Обновляем статистику для отображения в логе и на веб-странице
        scan_status["total_found_files"] = total_found # F_disk
        scan_status["initial_list_length"] = initial_list_length # L_before
        scan_status["existing_before_scan"] = existing_files_before_scan # E_before
        scan_status["missing_after_scan"] = missing_files_count # M_after
        scan_status["new_programs_added"] = new_programs_count # N_new
        scan_status["final_list_length"] = list_length_after_scan # L_after

        # Убираем старые/ненужные ключи, если они есть
        scan_status.pop("total_in_list", None)
        scan_status.pop("total_all_in_list", None)

        # Формируем содержательный лог о результатах сканирования
        duration = time.time() - scan_status["start_time"]
        
        # Обновляем лог с информацией о результатах в логичном порядке
        # Важно: эти сообщения уже добавлены ранее в процессе - не дублируем их
        # scan_status["log"].append(f"Запуск сканирования...")
        # scan_status["log"].append(f"Файлов в списке: {initial_list_length}")
        # scan_status["log"].append(f"Существующих файлов в списке: {existing_files_before_scan}")
        # scan_status["log"].append(f"Найдено исполняемых файлов на диске: {total_found}")
        # scan_status["log"].append(f"Добавлено новых файлов в список: {new_programs_count}")
        
        # Завершающие итоги (в отдельном блоке в конце лога)
        scan_status["log"].append("--- Итоги сканирования ---")
        scan_status["log"].append(f"Найдено файлов на диске: {total_found}")
        scan_status["log"].append(f"Всего в списке файлов после сканирования: {list_length_after_scan}")
        if missing_files_count > 0:
            scan_status["log"].append(f"Обнаружено отсутствующих файлов: {missing_files_count}")
            scan_status["log"].append(f"Для удаления отсутствующих файлов нажмите кнопку 'Сохранить'")
        
        # Сообщение о завершении сканирования (всегда в конце)
        scan_status["log"].append(f"Сканирование завершено за {duration:.1f} сек.")

        # Выводим информацию в нужном формате в консоль для отладки
        print("\n----------------")
        print(f"Найдено файлов на диске: {total_found}")
        print(f"Файлов в списке (до сканирования): {initial_list_length}")
        print(f"Из них существует на диске: {existing_files_before_scan}")
        print(f"Отсутствует на диске (после сканирования): {missing_files_count}")
        print(f"Добавлено новых файлов в список: {new_programs_count}")
        print(f"Всего в списке файлов (после сканирования): {list_length_after_scan}")
        if missing_files_count > 0:
            print(f"Обнаружено {missing_files_count} отсутствующих файлов. Нажмите 'Сохранить', чтобы удалить их из списка.")
        else:
            print("Отсутствующие файлы не обнаружены.")
        print(f"Время выполнения: {duration:.1f} сек.")
        print("----------------\n")

        # Обновляем статистику для отображения на веб-странице
        scan_status["total_found_files"] = total_found # F_disk
        scan_status["initial_list_length"] = initial_list_length # L_before
        scan_status["existing_before_scan"] = existing_files_before_scan # E_before
        scan_status["missing_after_scan"] = missing_files_count # M_after
        scan_status["new_programs_added"] = new_programs_count # N_new
        scan_status["final_list_length"] = list_length_after_scan # L_after

        # Убираем старые/ненужные ключи,  if они есть
        scan_status.pop("total_in_list", None)
        scan_status.pop("total_all_in_list", None)

        # Формируем сообщение для return (не используется напрямую в UI логе)
        result_message = (
            f"Найдено файлов на диске: {total_found}\n"
            f"Файлов в списке (до сканирования): {initial_list_length}\n"
            f"Из них существует на диске: {existing_files_before_scan}\n"
            f"Отсутствует на диске (после сканирования): {missing_files_count}\n"
            f"Добавлено новых файлов в список: {new_programs_count}\n"
            f"Всего в списке файлов (после сканирования): {list_length_after_scan}\n"
            f"Время выполнения: {duration:.1f} сек\n"
            f"----------------\n"
        )
        if missing_files_count > 0:
            result_message += f"Обнаружено {missing_files_count} отсутствующих файлов. Нажмите 'Сохранить', чтобы удалить их из списка."
        else:
            result_message += "Отсутствующие файлы not обнаружены."

        return result_message

    except Exception as e:
        # В случае ошибки обновляем статус
        import traceback
        print(f"Ошибка при сканировании: {str(e)}")
        print(traceback.format_exc())
        # Добавляем ошибку в лог статуса
        scan_status["log"] = scan_status.get("log", []) + [f"Ошибка: {str(e)}"]
        return f"Ошибка при сканировании: {str(e)}"
    finally:
        # Этот блок выполнится всегда
        scan_status["running"] = False
        if scan_status["end_time"] == 0:
             scan_status["end_time"] = time.time()
        # Гарантируем 100% прогресс при завершении
        scan_status["progress"] = 100
        scan_status["last_file"] = "Завершено"

def find_executable_files():
    """Находит исполняемые файлы в базовой директории.
    Возвращает список относительных путей и общее количество просмотренных файлов."""
    global scan_status # Доступ к статусу для обновления last_file и scanned_files

    found_programs = []
    files_walked_count = 0

    if not BASE_DIRECTORY or not os.path.isdir(BASE_DIRECTORY):
        print(f"Предупреждение: Базовая директория not найдена or not является директорией: {BASE_DIRECTORY}")
        return [], 0

    # Используем os.scandir для потенциального ускорения
    try:
        for entry in os.scandir(BASE_DIRECTORY):
            if entry.is_dir():
                # Рекурсивно обходим поддиректории
                # Пропускаем исключенные директории, но НЕ исключаем launcher безусловно
                if entry.name in _excluded_dirs:
                    continue
                # Рекурсивный вызов для поддиректорий
                sub_programs, sub_walked = _scan_directory_recursive(entry.path)
                found_programs.extend(sub_programs)
                files_walked_count += sub_walked
            elif entry.is_file():
                # Обрабатываем файлы только в поддиректориях, not в корне BASE_DIRECTORY
                files_walked_count += 1
                scan_status["scanned_files"] = files_walked_count # Обновляем счетчик просмотренных
                scan_status["last_file"] = entry.name # Показываем текущий файл
                # Пропускаем файлы в корневой директории (уже обработано выше)
    except OSError as e:
        print(f"Ошибка при сканировании директории {BASE_DIRECTORY}: {e}")
        scan_status["log"].append(f"Ошибка доступа к {BASE_DIRECTORY}: {e}")


    return found_programs, files_walked_count

def _scan_directory_recursive(current_dir):
    """Рекурсивно сканирует директорию."""
    global scan_status
    found_programs = []
    files_walked_count = 0

    try:
        for entry in os.scandir(current_dir):
            full_path = entry.path
            if entry.is_dir():
                if entry.name in _excluded_dirs:
                    continue
                # Рекурсивный вызов
                sub_programs, sub_walked = _scan_directory_recursive(full_path)
                found_programs.extend(sub_programs)
                files_walked_count += sub_walked
            elif entry.is_file():
                files_walked_count += 1
                scan_status["scanned_files"] = scan_status.get("scanned_files", 0) + 1 # Инкрементируем глобальный счетчик
                scan_status["last_file"] = entry.name # Показываем текущий файл

                # Пропускаем файлы из списка исключений
                if entry.name in _excluded_filenames:
                    continue

                # Проверяем расширение файла
                _, ext = os.path.splitext(entry.name.lower())
                if ext in _ignore_extensions:
                    continue

                if ext in _executable_extensions:
                    # Получаем относительный путь
                    rel_path = os.path.relpath(full_path, BASE_DIRECTORY)
                    rel_path = rel_path.replace('\\\\', '/') # Нормализуем для Windows/Linux
                    found_programs.append(rel_path)
    except OSError as e:
        print(f"Ошибка при сканировании директории {current_dir}: {e}")
        scan_status["log"].append(f"Ошибка доступа к {current_dir}: {e}")


    return found_programs, files_walked_count

def update_program_list(new_paths, save_program_list_func, weight_format_info):
    """Обновляет список программ на основе найденных файлов, обновляя взвешенный прогресс."""
    global EXECUTABLE, scan_status

    new_count = 0

    for path in new_paths:
        # Обновляем статус - какой файл обрабатывается
        current_file_name = os.path.basename(path)
        scan_status["last_file"] = current_file_name

        # --- Получение информации о файле (потенциально медленная операция) ---
        full_path = os.path.join(BASE_DIRECTORY, path)
        description = format_file_info(full_path)
        # --- Конец получения информации ---

        # Определяем категорию
        category = extract_category_from_path(full_path, BASE_DIRECTORY)

        if not description or description.startswith("Файл not найден") or description.startswith("Ошибка"):
            description = f"Программа {current_file_name}" # Используем имя файла как fallback

        category_safe = escape_html(category)
        # not экранируем описание здесь, сохраняем как есть
        description_raw = description

        program = ProgramInfo(path, category_safe, description_raw) # Сохраняем неэкранированное описание
        program.original_category = category
        program.original_description = description_raw # Сохраняем для возможного редактирования

        EXECUTABLE.append(program)
        new_count += 1
        scan_status["new_programs"] += 1 # Обновляем счетчик новых программ по ходу

        # --- Обновление прогресса ---
        scan_status["current_weighted_done"] += weight_format_info # Используем вес для этой операции
        scan_status["progress"] = _calculate_progress(
            scan_status["current_weighted_done"], scan_status["total_weighted_ops"]
        )
        # --- Конец обновления прогресса ---

    return new_count

def check_missing_files(save_program_list_func):
    """Проверяет существующие программы, находит отсутствующие и обновляет взвешенный прогресс."""
    global EXECUTABLE, scan_status

    if not EXECUTABLE:
        return 0, 0

    missing_paths = []
    # Создаем копию списка путей для безопасной итерации (хотя мы not меняем список здесь)
    programs_to_check = list(EXECUTABLE)

    for program in programs_to_check:
        # Обновляем статус - какой файл проверяется
        scan_status["last_file"] = os.path.basename(program.path)

        try:
            full_path = os.path.join(BASE_DIRECTORY, program.path)
            # --- Проверка существования файла (вес 1) ---
            exists = os.path.isfile(full_path)
            # --- Конец проверки ---

            if not exists:
                missing_paths.append(program.path)
        except Exception as e:
            print(f"Ошибка при проверке файла {program.path}: {str(e)}")
            # Считаем файл отсутствующим при ошибке доступа
            missing_paths.append(program.path)
            scan_status["log"].append(f"Ошибка проверки {program.path}: {e}")


        # --- Обновление прогресса ---
        scan_status["current_weighted_done"] += 1 # Вес 1 для проверки существования
        scan_status["progress"] = _calculate_progress(
            scan_status["current_weighted_done"], scan_status["total_weighted_ops"]
        )
        # --- Конец обновления прогресса ---

    missing_count = len(missing_paths)

    # не удаляем файлы автоматически, только сохраняем список отсутствующих
    scan_status["missing_files"] = missing_count # Общее количество отсутствующих для статуса
    scan_status["removed_files"] = 0 # Сбрасываем счетчик удаленных (удаление происходит в apply_scan_changes)
    scan_status["missing_paths"] = missing_paths # Сохраняем для использования в apply_scan_changes

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

    # Обновляем статистику после успешного удаления и сохранения
    scan_status["removed_files"] = removed_count
    scan_status["missing_files"] = 0 # После удаления их больше нет в списке как "отсутствующих"
    scan_status["missing_paths"] = [] # Очищаем список путей для удаления
    scan_status["missing_after_scan"] = 0 # Обнуляем и эту статистику
    scan_status["final_list_length"] = len(EXECUTABLE) # Обновляем итоговую длину списка

    print(f"Удалено {removed_count} записей из списка программ.")
    return f"Удалено {removed_count} ложных ссылок на файлы из списка."

def extract_category_from_path(file_path, root_directory):
    """
    Извлекает категорию из пути к файлу.
    Категория - это первая папка с конца в пути к файлу относительно корневой директории.
    Если файл находится в корне, возвращает "найдено".
    """
    # Очищаем пути от пробелов
    file_path = file_path.strip() if file_path else ""
    root_directory = root_directory.strip() if root_directory else ""
    
    # Получаем относительный путь от корневой директории
    rel_path = os.path.relpath(file_path, root_directory)
    path_parts = rel_path.split(os.sep)
    
    # Если путь содержит более одного элемента (не в корне)
    if len(path_parts) > 1:
        # Берем первую папку из пути (не считая имени файла) и очищаем от пробелов
        return path_parts[0].strip()
    else:
        # Если файл в корне, возвращаем "найдено"
        return "найдено"

def scan_directory(directory, program_list, program_info_class, extensions, excluded_dirs, excluded_filenames):
    """
    Сканирует директорию на наличие исполняемых файлов.
    
    Args:
        directory (str): Путь к директории для сканирования
        program_list (list): Список программ
        program_info_class (class): Класс для создания объектов программ
        extensions (list): Список расширений файлов, которые считаются исполняемыми
        excluded_dirs (list): Список директорий, которые следует исключить из сканирования
        excluded_filenames (list): Список имен файлов, которые следует исключить из сканирования
    
    Returns:
        list: Обновленный список программ
    """
    # ...existing code...
    
    for root, dirs, files in os.walk(directory):
        # Исключаем директории, которые следует пропустить
        dirs[:] = [d for d in dirs if d.lower() not in [e.lower() for e in excluded_dirs]]
        
        for file in files:
            # Проверяем, не исключено ли имя файла
            if file.lower() in [e.lower() for e in excluded_filenames]:
                continue
                
            # Проверяем расширение файла
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext not in extensions:
                continue
                
            # Полный путь к файлу
            file_path = os.path.join(root, file)
            
            # Проверяем, есть ли такой файл уже в списке
            duplicate = False
            for prog in program_list:
                if prog.path == file_path:
                    duplicate = True
                    break
            
            if duplicate:
                continue
            
            # Определяем категорию программы по пути к файлу
            category = extract_category_from_path(file_path, directory)
            
            # Создаем новый объект программы и добавляем его в список
            new_program = program_info_class(
                name=os.path.splitext(file)[0],
                path=file_path,
                category=category,
                description="",
                icon=""
            )
            program_list.append(new_program)
    
    return program_list