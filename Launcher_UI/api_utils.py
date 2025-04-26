"""
Модуль для обработки API-запросов и унифицированной обработки ошибок
"""
import json
import traceback
from functools import wraps
from flask import jsonify, request, Response

def handle_api_error(exception, context=""):
    """
    Обрабатывает исключения в API и возвращает соответствующий ответ
    
    Args:
        exception: Исключение, которое произошло
        context: Контекст, в котором произошла ошибка (необязательно)
    
    Returns:
        Response: Ответ с сообщением об ошибке
    """
    error_message = str(exception)
    error_trace = traceback.format_exc()
    
    print(f"Ошибка {context}: {error_message}")
    print(error_trace)
    
    # Формируем сообщение об ошибке
    if context:
        message = f"Произошла ошибка {context}: {error_message}"
    else:
        message = f"Произошла ошибка: {error_message}"
    
    # Возвращаем ответ с сообщением об ошибке
    return Response(message, content_type='text/plain; charset=utf-8')

def get_validated_param(param_name, required=True, default=None):
    """
    Получает и валидирует параметр из запроса
    
    Args:
        param_name: Имя параметра
        required: Является ли параметр обязательным (по умолчанию True)
        default: Значение по умолчанию, если параметр отсутствует и не обязателен
    
    Returns:
        str: Значение параметра
    
    Raises:
        ValueError: Если параметр обязательный, но отсутствует
    """
    param_value = request.args.get(param_name)
    
    if param_value is None and required:
        raise ValueError(f"Не указан обязательный параметр: {param_name}")
    
    if param_value is None and not required:
        return default
    
    # Проверяем, не является ли путь уже декодированным
    try:
        import urllib.parse
        # Если значение содержит %, возможно, оно закодировано
        if param_value and '%' in param_value:
            # Декодируем URL-закодированные параметры
            decoded_value = urllib.parse.unquote(param_value)
            print(f"Параметр {param_name} декодирован: {decoded_value}")
            return decoded_value
    except Exception as e:
        print(f"Ошибка при декодировании параметра {param_name}: {str(e)}")
    
    return param_value

def validate_params(required_params):
    """
    Декоратор для проверки наличия обязательных параметров в запросе
    
    Args:
        required_params: Список обязательных параметров
    
    Returns:
        Декоратор для проверки параметров
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'Отсутствуют данные'}), 400
            
            missing_params = [param for param in required_params if param not in data]
            if missing_params:
                return jsonify({
                    'success': False, 
                    'error': f'Отсутствуют обязательные параметры: {", ".join(missing_params)}'
                }), 400
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_error_handler(f):
    """
    Декоратор для обработки исключений в API-маршрутах
    
    Args:
        f: Функция для декорирования
    
    Returns:
        Декорированная функция с обработкой ошибок
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    return decorated_function

def json_response(data=None, success=True, error=None, status_code=200):
    """
    Создает унифицированный JSON-ответ для API
    
    Args:
        data: Данные для отправки клиенту
        success: Признак успешности операции
        error: Текст ошибки (если есть)
        status_code: HTTP-код ответа
    
    Returns:
        Flask Response с JSON-данными
    """
    response = {
        'success': success
    }
    
    if data is not None:
        response['data'] = data
        
    if error is not None:
        response['error'] = error
        
    return jsonify(response), status_code