"""
Модуль для работы с HTML-форматированием и безопасностью
"""
import html

def escape_html(text):
    """
    Экранирует специальные символы HTML для безопасного отображения
    
    Args:
        text: Текст для экранирования
        
    Returns:
        str: Экранированный текст
    """
    if not text:
        return ""
    return html.escape(str(text))

def unescape_html(text):
    """
    Разэкранирует специальные символы HTML
    
    Args:
        text: Экранированный текст
        
    Returns:
        str: Исходный текст
    """
    if not text:
        return ""
    return html.unescape(str(text))

def format_description(description):
    """
    Форматирует описание программы для отображения в HTML
    
    Args:
        description: Текст описания
        
    Returns:
        str: Отформатированный HTML
    """
    if not description:
        return ""
        
    # Экранируем HTML
    safe_desc = escape_html(description)
    
    # Заменяем переносы строк на HTML-теги <br>
    formatted = safe_desc.replace('\n', '<br>')
    
    return formatted