import os
import json
import urllib.parse
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
    from program_operations import move_favorites_to_category as move_favorites_to_category_func
    from program_operations import toggle_hidden
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

    @app.route('/cancel_scan_changes')
    def api_cancel_scan_changes():
        """Отменяет изменения, обнаруженные при сканировании"""
        try:
            from scan_operations import cancel_scan_changes
            result = cancel_scan_changes()
            return Response(result, content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при отмене изменений сканирования")

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
            # Получаем параметр категории и очищаем его от пробелов
            category = get_validated_param('category')
            print(f"Получен запрос на удаление категории: '{category}'")
            
            # Проверка проводится внутри remove_category_from_list
            success, message = remove_category_from_list(category, save_program_list_func)
            
            if success:
                print(f"Успешно удалена категория '{category}': {message}")
                return Response(message, content_type='text/plain; charset=utf-8')
            else:
                print(f"Ошибка или отсутствие программ при удалении категории '{category}': {message}")
                return Response(f"Информация: {message}", content_type='text/plain; charset=utf-8')
        except Exception as e:
            # Расширенное логирование для отладки
            print(f"Ошибка при удалении категории: {str(e)}")
            import traceback
            print(traceback.format_exc())
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

    @app.route('/move_favorites')
    def api_move_favorites():
        """Перемещает все программы из избранного в указанную категорию"""
        try:
            new_category = get_validated_param('category')
            
            success, message = move_favorites_to_category_func(new_category, save_program_list_func)
            
            if success:
                return Response(message, content_type='text/plain; charset=utf-8')
            else:
                return Response(f"Информация: {message}", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при перемещении избранных программ")

    @app.route('/toggle_hidden')
    def api_toggle_hidden():
        """Переключает статус 'скрытый' для программы"""
        try:
            program_path = get_validated_param('path')
            is_favorite = request.args.get('favorite', '').lower() == 'true'
            
            # Нормализуем путь перед передачей для корректного поиска/сравнения
            normalized_path = os.path.normpath(program_path)
            
            print(f"Запрос на переключение статуса скрытия для программы: {normalized_path}")
            print(f"Программа в избранном: {'Да' if is_favorite else 'Нет'}")
            
            # Передаем нормализованный путь
            success, is_hidden = toggle_hidden(normalized_path, save_program_list_func)
            
            if success:
                status = "скрыта" if is_hidden else "отображена"
                return Response(f"Программа {os.path.basename(program_path)} {status}", content_type='text/plain; charset=utf-8')
            else:
                return Response(f"Ошибка: программа не найдена: {program_path}", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при изменении статуса скрытия")

    @app.route('/save_changes')
    def api_save_changes():
        """Принудительно сохраняет текущее состояние программ"""
        try:
            force = request.args.get('force', '').lower() == 'true'
            
            if not save_program_list_func:
                return Response("Ошибка: Функция сохранения не инициализирована", 
                               content_type='text/plain; charset=utf-8')
            
            print(f"Принудительное сохранение изменений (force={force})")
            result = save_program_list_func()
            
            if result:
                return Response("Изменения успешно сохранены", content_type='text/plain; charset=utf-8')
            else:
                return Response("Ошибка при сохранении изменений", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при принудительном сохранении изменений")

    @app.route('/shutdown')
    def api_shutdown():
        """Останавливает сервер и закрывает приложение"""
        try:
            import threading
            import os
            
            # Показываем сообщение
            print("Получен запрос на завершение работы сервера")
            
            # Функция для принудительного завершения приложения с небольшой задержкой
            def shutdown_server():
                # Ждем небольшую задержку, чтобы запрос успел отправить ответ
                import time
                time.sleep(1)
                # Принудительно завершаем процесс
                os._exit(0)
            
            # Запускаем поток для завершения работы сервера
            threading.Thread(target=shutdown_server, daemon=True).start()
            
            return Response("Сервер останавливается...", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при остановке сервера")

    @app.route('/change_header_color')
    def change_header_color():
        """Изменяет цвет заголовка программы, категории или избранного"""
        try:
            # Получаем параметры из запроса
            item_path = request.args.get('path')
            header_color = request.args.get('color', '#')  # Цвет по умолчанию - '#'
            item_type = request.args.get('type', 'program')  # Тип по умолчанию - 'program'
            apply_to_all = request.args.get('apply_to_all', '0') == '1'  # Применить ко всем программам в категории
            
            if not item_path:
                return "Не указан путь к программе или название категории"
            
            # Декодируем URL-закодированный путь
            try:
                if '%' in item_path:
                    item_path = urllib.parse.unquote(item_path)
                    print(f"Путь после декодирования: {item_path}")
            except Exception as e:
                print(f"Ошибка при декодировании пути: {str(e)}")
                # Продолжаем с оригинальным путем
            
            # Очищаем путь от лишних пробелов
            item_path = item_path.strip()
            
            # Флаг для отслеживания, работаем ли мы с избранным
            is_favorites_mode = item_type == 'favorites' or (item_type == 'category' and item_path.lower() == 'избранное')
            
            print(f"Тип элемента: {item_type}")
            print(f"Работаем с избранным: {is_favorites_mode}")
            
            if item_type == 'category' or is_favorites_mode:
                # Обработка изменения цвета категории или всех избранных
                category_name = item_path
                programs_updated = 0
                category_color_updated = False
                
                print(f"Изменение цвета для {'избранного' if is_favorites_mode else 'категории'}: {category_name}")
                print(f"Новый цвет: {header_color}")
                print(f"Применить ко всем программам: {apply_to_all}")
                
                # Обновляем цвета программ
                for program in EXECUTABLE:
                    should_update = False
                    
                    if is_favorites_mode:
                        # Если работаем с избранным, обновляем все избранные программы
                        should_update = program.is_favorite
                        if should_update:
                            print(f"Найдена избранная программа: {program.path}")
                    else:
                        # Иначе обновляем программы из указанной категории
                        # Используем оригинальную категорию (без экранирования HTML)
                        original_category = getattr(program, 'original_category', program.category)
                        from html_utils import unescape_html
                        if hasattr(program, 'original_category'):
                            program_category = original_category
                        else:
                            program_category = unescape_html(program.category)
                        
                        # Проверяем, принадлежит ли программа к данной категории
                        should_update = program_category.lower() == category_name.lower()
                        if should_update:
                            print(f"Найдена программа из категории {category_name}: {program.path}")
                    
                    # Если нужно обновить эту программу
                    if should_update:
                        # Всегда обновляем цвет всех программ в категории
                        program.header_color = header_color
                        programs_updated += 1
                        print(f"Обновлен цвет программы: {program.path}, Избранное: {getattr(program, 'is_favorite', False)}, Новый цвет: {header_color}")
                        category_color_updated = True
                
                if programs_updated > 0:
                    # Сохраняем изменения
                    result = save_program_list_func()
                    if result:
                        entity_type = "избранного" if is_favorites_mode else f"категории '{category_name}'"
                        return f"Цвет {entity_type} изменен на '{header_color}'. Обновлено программ: {programs_updated}"
                    else:
                        return "Ошибка при сохранении изменений"
                else:
                    if is_favorites_mode:
                        return "Программы в избранном не найдены"
                    else:
                        return f"Программы в категории '{category_name}' не найдены"
            else:
                # Обработка изменения цвета отдельной программы
                print(f"Изменение цвета заголовка для программы: {item_path}")
                print(f"Новый цвет заголовка: {header_color}")
                
                # Нормализуем путь перед поиском
                normalized_path = os.path.normpath(item_path)
                
                # Ищем программу в списке
                found = False
                for program in EXECUTABLE:
                    if os.path.normpath(program.path.strip()) == normalized_path:
                        # Устанавливаем новый цвет заголовка
                        program.header_color = header_color
                        found = True
                        print(f"Программа найдена, цвет заголовка изменен на: {header_color}")
                        break
                
                if not found:
                    print(f"Программа не найдена: {item_path}")
                    return "Программа не найдена"
                
                # Сохраняем изменения
                result = save_program_list_func()
                if result:
                    return f"Цвет заголовка для '{os.path.basename(item_path)}' изменен на '{header_color}'"
                else:
                    return "Ошибка при сохранении изменений"
            
        except Exception as e:
            print(f"Ошибка при изменении цвета: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Ошибка: {str(e)}"

    @app.route('/api/programs')
    def api_get_programs():
        """API для получения списка программ с возможностью фильтрации по категории или избранным"""
        try:
            # Получаем параметры фильтрации
            category = request.args.get('category', '').strip()
            favorites = request.args.get('favorites', '').lower() == 'true'
            
            # Фильтруем программы
            filtered_programs = []
            for program in EXECUTABLE:
                # Получаем оригинальную категорию программы
                original_category = getattr(program, 'original_category', program.category)
                from html_utils import unescape_html
                
                if hasattr(program, 'original_category'):
                    program_category = original_category
                else:
                    program_category = unescape_html(program.category)
                
                # Проверяем условия фильтрации
                if favorites and program.is_favorite:
                    # Добавляем программу, если она в избранном и запрошены избранные
                    filtered_programs.append(program)
                elif category and program_category.lower() == category.lower():
                    # Добавляем программу, если она в запрошенной категории
                    filtered_programs.append(program)
                elif not category and not favorites:
                    # Добавляем программу, если нет фильтрации
                    filtered_programs.append(program)
            
            # Подготавливаем данные для передачи
            program_list = []
            for idx, program in enumerate(filtered_programs):
                # Формируем простой идентификатор для программы
                program_id = f"prog_{idx}"
                
                program_info = {
                    "id": program_id,
                    "name": os.path.basename(program.path),
                    "path": program.path,
                    "category": getattr(program, 'original_category', program.category),
                    "description": getattr(program, 'description', ''),
                    "is_favorite": getattr(program, 'is_favorite', False),
                    "is_hidden": getattr(program, 'is_hidden', False),
                    "header_color": getattr(program, 'header_color', '#')
                }
                program_list.append(program_info)
            
            response_data = {
                "programs": program_list,
                "total": len(program_list)
            }
            
            return Response(json.dumps(response_data), content_type='application/json; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при получении списка программ")

    @app.route('/remove_programs', methods=['POST'])
    def api_remove_programs():
        """Удаляет несколько программ по указанным путям"""
        try:
            # Получаем данные из тела запроса
            data = request.get_json()
            
            if not data or 'paths' not in data:
                return Response("Ошибка: не указаны пути к программам", status=400, content_type='text/plain; charset=utf-8')
            
            paths = data['paths']
            if not paths or not isinstance(paths, list):
                return Response("Ошибка: некорректный формат списка путей", status=400, content_type='text/plain; charset=utf-8')
            
            # Счетчик удаленных программ
            removed_count = 0
            
            # Удаляем программы по одной
            for path in paths:
                # Нормализуем путь
                normalized_path = os.path.normpath(path.strip())
                
                # Пытаемся удалить программу
                if remove_program_from_list(normalized_path, save_program_list_func):
                    removed_count += 1
            
            # Возвращаем результат
            if removed_count > 0:
                return Response(f"Удалено программ: {removed_count}", content_type='text/plain; charset=utf-8')
            else:
                return Response("Не удалось удалить ни одной программы", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при массовом удалении программ")

    @app.route('/remove_from_favorites', methods=['POST'])
    def api_remove_from_favorites():
        """Удаляет программы из избранного по указанным путям"""
        try:
            # Получаем данные из тела запроса
            data = request.get_json()
            
            if not data or 'paths' not in data:
                return Response("Ошибка: не указаны пути к программам", status=400, content_type='text/plain; charset=utf-8')
            
            paths = data['paths']
            if not paths or not isinstance(paths, list):
                return Response("Ошибка: некорректный формат списка путей", status=400, content_type='text/plain; charset=utf-8')
            
            # Счетчик обработанных программ
            removed_count = 0
            
            # Удаляем программы из избранного
            for path in paths:
                # Нормализуем путь
                normalized_path = os.path.normpath(path.strip())
                
                # Ищем программу в списке
                for program in EXECUTABLE:
                    if os.path.normpath(program.path.strip()) == normalized_path and program.is_favorite:
                        # Удаляем из избранного
                        program.is_favorite = False
                        removed_count += 1
                        break
            
            # Сохраняем изменения, если были удаления
            if removed_count > 0:
                save_program_list_func()
                return Response(f"Удалено из избранного программ: {removed_count}", content_type='text/plain; charset=utf-8')
            else:
                return Response("Не удалось удалить ни одной программы из избранного", content_type='text/plain; charset=utf-8')
        except Exception as e:
            return handle_api_error(e, "при удалении из избранного")