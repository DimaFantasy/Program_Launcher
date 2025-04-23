import os
import json
import traceback
from flask import request, Response, jsonify, abort
from file_description import get_file_description
from file_operations import rename_category, change_file_category
from api_utils import handle_api_error, get_validated_param

# Глобальные переменные
app = None
EXECUTABLE = None
BASE_DIRECTORY = None
load_program_list_func = None
save_program_list_func = None

def init_web_routes(flask_app, programs, base_dir, load_programs, save_programs):
    """Инициализация глобальных переменных для маршрутов"""
    global app, EXECUTABLE, BASE_DIRECTORY, load_program_list_func, save_program_list_func
    app = flask_app
    EXECUTABLE = programs
    BASE_DIRECTORY = base_dir
    load_program_list_func = load_programs
    save_program_list_func = save_programs
    
    print("--- [DEBUG][web_routes] init_web_routes вызвана ---")
    print(f"--- [DEBUG][web_routes] Получен список EXECUTABLE: {'Да' if EXECUTABLE is not None else 'Нет'}, Длина: {len(EXECUTABLE) if EXECUTABLE is not None else 'N/A'} ---")
    print(f"--- [DEBUG][web_routes] Получена функция save_program_list: {'Да' if callable(save_program_list_func) else 'Нет'} ---")
    
    # Регистрируем маршруты
    register_routes()
    
    print("Web маршруты инициализированы")

def register_routes():
    """Регистрирует все маршруты API"""
    # Импортируем зависимости, переименовывая remove_program для избежания конфликта
    from program_operations import toggle_favorite, change_description, remove_program as remove_program_from_list
    from program_operations import remove_category as remove_category_from_list, clear_favorites as clear_favorites_list
    from scan_operations import start_scan_in_thread, get_scan_status
    from program_launcher import launch_program, handle_open_folder
    
    # Маршрут для запуска программы
    @app.route('/launch')
    def api_launch_program():
        """Запускает программу по указанному пути"""
        try:
            program_path = get_validated_param('path')
            # Нормализуем путь перед передачей для унификации (например, обработка '\' и '/')
            normalized_path = os.path.normpath(program_path)
            return launch_program(normalized_path, BASE_DIRECTORY)
        except Exception as e:
            return handle_api_error(e, "при запуске программы")
    
    # Маршрут для открытия папки с программой
    @app.route('/open_folder')
    def api_open_folder():
        """Открывает папку с программой"""
        return handle_open_folder()
    
    @app.route('/toggle_favorite')
    def api_toggle_favorite():
        """Переключает статус избранного для программы"""
        try:
            program_path = get_validated_param('path')
            # Нормализуем путь перед передачей в toggle_favorite для корректного поиска/сравнения
            normalized_path = os.path.normpath(program_path)
            
            # Передаем нормализованный путь
            success, is_favorite = toggle_favorite(normalized_path, save_program_list_func)
            
            if success:
                status = "добавлена в избранное" if is_favorite else "удалена из избранного"
                return Response(f"Программа {os.path.basename(program_path)} {status}", content_type='text/plain; charset=utf-8')
            else:
                return Response(f"Ошибка: программа не найдена: {program_path}", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при изменении статуса избранного")

    @app.route('/reload')
    def reload_programs():
        """Перезагружает список программ из файла"""
        load_program_list_func()
        return Response("Список программ перезагружен", content_type='text/plain; charset=utf-8')

    @app.route('/start_scan')
    def api_start_scan():
        """Запускает процесс сканирования в отдельном потоке"""
        try:
            print("Начинаем сканирование программ...")
            return Response(start_scan_in_thread(save_program_list_func), content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при запуске сканирования программ")

    @app.route('/scan_programs')
    def api_scan_programs():
        """Альтернативный маршрут для запуска сканирования (для обратной совместимости)"""
        return api_start_scan()

    @app.route('/change_description')
    def api_change_description():
        """Изменяет описание программы"""
        try:
            program_path = get_validated_param('path')
            new_description = get_validated_param('description', required=False) or ""
            
            if change_description(program_path, new_description, save_program_list_func):
                return Response(f"Описание программы {os.path.basename(program_path)} обновлено", content_type='text/plain; charset=utf-8')
            else:
                return Response(f"Ошибка: программа не найдена: {program_path}", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при изменении описания")

    @app.route('/get_file_info')
    def api_get_file_info():
        """Получает информацию о файле и возвращает её клиенту"""
        try:
            program_path = get_validated_param('path')
            
            # Найдем программу в списке
            target_program = None
            for program in EXECUTABLE:
                if program.path == program_path:
                    target_program = program
                    break
            
            if not target_program:
                return Response(json.dumps({"error": f"Программа не найдена: {program_path}"}), 
                              content_type='application/json; charset=utf-8')
            
            # Получаем информацию о файле
            file_info = get_file_description(program_path, BASE_DIRECTORY)
            
            # Возвращаем информацию о файле клиенту
            return Response(
                json.dumps({
                    "success": True,
                    "message": f"Информация о файле получена для {os.path.basename(program_path)}",
                    "file_info": file_info,
                    "program_name": os.path.basename(program_path)
                }), 
                content_type='application/json; charset=utf-8'
            )
        except Exception as e:
            return handle_api_error(e, "при получении информации о файле")

    @app.route('/rename_category')
    def api_rename_category():
        """Переименовывает категорию для всех программ в этой категории"""
        try:
            old_category = get_validated_param('old_category')
            new_category = get_validated_param('new_category')
            
            # Проверяем, что категория не "Избранное"
            if old_category.lower() == "избранное":
                return Response("Категорию 'Избранное' нельзя переименовать", content_type='text/plain; charset=utf-8')
                
            # Используем функцию из модуля file_operations для переименования категории
            changed_count, _ = rename_category(EXECUTABLE, old_category, new_category, BASE_DIRECTORY)
            
            if changed_count > 0:
                # После переименования категории в файле, просто перезагружаем список программ
                load_program_list_func()
                
                return Response(f"Категория '{old_category}' переименована в '{new_category}'. Изменено программ: {changed_count}", 
                                content_type='text/plain; charset=utf-8')
            else:
                return Response(f"Программы в категории '{old_category}' не найдены", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при переименовании категории")

    @app.route('/change_category')
    def api_change_category():
        """Изменяет категорию программы"""
        try:
            program_path = get_validated_param('path')
            new_category = get_validated_param('category')
            
            print(f"Получен запрос на изменение категории. Путь: {program_path}, Новая категория: {new_category}")
            
            # Используем функцию из модуля file_operations для изменения категории программы
            success, _ = change_file_category(EXECUTABLE, program_path, new_category, BASE_DIRECTORY)
            
            if success:
                print(f"Категория успешно изменена. Перезагружаем список программ.")
                # После изменения категории в файле, перезагружаем список программ
                load_program_list_func()
                return Response(f"Программа {os.path.basename(program_path)} перемещена в категорию {new_category}", 
                                content_type='text/plain; charset=utf-8')
            else:
                print(f"Ошибка: программа не найдена: {program_path}")
                return Response(f"Ошибка: программа не найдена: {program_path}", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при изменении категории")

    @app.route('/remove_program')
    def api_remove_program():
        """API для удаления программы из списка"""
        try:
            program_path = get_validated_param('path')
            # Получаем имя файла для сообщения
            program_name = os.path.basename(program_path)
            
            # Явно нормализуем путь перед передачей
            normalized_path = os.path.normpath(program_path)
            print(f"--- [DEBUG][web_routes] Нормализованный путь для удаления: {normalized_path} ---")
            
            # Используем переименованную функцию с нормализованным путем
            if remove_program_from_list(normalized_path, save_program_list_func):
                return Response(f"Программа {program_name} удалена из списка", content_type='text/plain; charset=utf-8')
            else:
                # Используем исходный program_path для сообщения об ошибке
                return Response(f"Ошибка: программа не найдена: {program_path}", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при удалении программы")

    @app.route('/scan_status')
    def api_scan_status():
        """Возвращает текущий статус сканирования"""
        try:
            return Response(json.dumps(get_scan_status()), content_type='application/json; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при получении статуса сканирования")

    @app.route('/apply_scan_changes')
    def api_apply_scan_changes():
        """Применяет изменения, обнаруженные при сканировании"""
        try:
            from scan_operations import apply_scan_changes
            result = apply_scan_changes(save_program_list_func)
            return Response(result, content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при применении изменений сканирования")

    @app.route('/remove/<int:program_index>', methods=['DELETE', 'GET'])
    def remove_program(program_index):
        """Обрабатывает запрос на удаление программы."""
        print(f"\n--- [DEBUG][web_routes] Запрос на удаление программы с индексом: {program_index} ---")
        
        if EXECUTABLE is None:
            print("--- [DEBUG][web_routes] Ошибка: Список программ (EXECUTABLE) не инициализирован! ---")
            return jsonify({"status": "error", "message": "Server error: Program list not available"}), 500
            
        if save_program_list_func is None:
            print("--- [DEBUG][web_routes] Ошибка: Функция сохранения (save_program_list_func) не инициализирована! ---")
            return jsonify({"status": "error", "message": "Server error: Save function not available"}), 500

        try:
            # Проверяем корректность индекса
            if 0 <= program_index < len(EXECUTABLE):
                removed_program = EXECUTABLE.pop(program_index)
                print(f"--- [DEBUG][web_routes] Программа '{removed_program.name}' удалена из списка (индекс {program_index}) ---")
                print(f"--- [DEBUG][web_routes] Длина списка ПОСЛЕ удаления: {len(EXECUTABLE)} ---")
                
                # Вызываем функцию сохранения, переданную из launcher.py
                print("--- [DEBUG][web_routes] Вызов функции сохранения (save_program_list_func)... ---")
                save_success = save_program_list_func() 
                if save_success:
                     print("--- [DEBUG][web_routes] Функция сохранения сообщила об успехе ---")
                     return jsonify({"status": "success", "message": "Program removed"})
                else:
                     print("--- [DEBUG][web_routes] Функция сохранения сообщила об ошибке ---")
                     # Важно: Возможно, стоит вернуть программу обратно в список или обработать ошибку иначе
                     # EXECUTABLE.insert(program_index, removed_program) # Пример отката
                     return jsonify({"status": "error", "message": "Failed to save changes"}), 500
            else:
                print(f"--- [DEBUG][web_routes] Ошибка: Неверный индекс ({program_index}), длина списка: {len(EXECUTABLE)} ---")
                abort(404, description="Program index out of bounds") # Используем abort для стандартной ошибки
                
        except Exception as e:
            print(f"--- [DEBUG][web_routes] Исключение при удалении: {e} ---")
            # В случае непредвиденной ошибки
            return jsonify({"status": "error", "message": f"An error occurred: {e}"}), 500

    @app.route('/remove_category')
    def api_remove_category():
        """Удаляет все программы из указанной категории"""
        try:
            category = get_validated_param('category')
            
            # Проверка проводится внутри remove_category_from_list
            success, message = remove_category_from_list(category, save_program_list_func)
            
            if success:
                # Перезагружаем список программ ПОСЛЕ удаления и сохранения
                # Этот шаг может быть необязательным, так как EXECUTABLE уже изменен
                # load_program_list_func()
                return Response(message, content_type='text/plain; charset=utf-8')
            else:
                return Response(f"Ошибка: {message}", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при удалении категории")

    @app.route('/clear_favorites')
    def api_clear_favorites():
        """Удаляет все программы из избранного"""
        try:
            success, message = clear_favorites_list(save_program_list_func)
            
            if success:
                return Response(message, content_type='text/plain; charset=utf-8')
            else:
                return Response(f"Информация: {message}", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при очистке избранного")