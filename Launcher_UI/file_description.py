import os
import pefile
import time
import datetime
import mimetypes
from pathlib import Path

def extract_version_info(file_path):
    """Извлекает информацию о версии из PE файла"""
    try:
        # Загружаем PE файл
        pe = pefile.PE(file_path)

        # Словарь для хранения информации о версии
        string_version_info = {}

        # Проверяем, есть ли атрибут FileInfo
        if hasattr(pe, 'FileInfo') and len(pe.FileInfo) > 0:
            for fileinfo in pe.FileInfo[0]:
                if fileinfo.Key.decode() == 'StringFileInfo':
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            string_version_info[entry[0].decode()] = entry[1].decode()

        # Если данных о версии нет, возвращаем None
        return string_version_info if string_version_info else None

    except Exception as e:
        print(f"Ошибка обработки файла {file_path}: {e}")
        return None

def safe_pe_info_extraction(file_path):
    """Безопасно извлекает информацию о PE файле, обрабатывая все возможные ошибки"""
    try:
        version_info = extract_version_info(file_path)
        if version_info:
            # Определяем важные поля для отображения
            important_fields = [
                'FileDescription', 'ProductName', 'CompanyName', 
                'FileVersion', 'ProductVersion', 'LegalCopyright'
            ]
            
            result = []
            for field in important_fields:
                if field in version_info and version_info[field]:
                    result.append(f"{field}: {version_info[field]}")
            
            return result
    except Exception as e:
        print(f"Ошибка при получении информации о версии PE файла: {e}")
    
    return []

def get_file_type_info(file_path):
    """Определяет тип файла на основе расширения и mime-типа"""
    try:
        # Получаем расширение файла
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Определяем MIME-тип
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Словарь для более понятного описания типов файлов
        file_type_map = {
            '.exe': 'Исполняемый файл Windows',
            '.dll': 'Библиотека динамической компоновки Windows',
            '.sys': 'Системный файл Windows',
            '.bat': 'Пакетный файл Windows',
            '.cmd': 'Командный файл Windows',
            '.ps1': 'Скрипт PowerShell',
            '.py': 'Скрипт Python',
            '.jar': 'Java Архив',
            '.msi': 'Установщик Windows',
            '.reg': 'Файл реестра Windows',
            '.txt': 'Текстовый файл',
            '.docx': 'Документ Microsoft Word',
            '.xlsx': 'Таблица Microsoft Excel',
            '.pdf': 'Документ Adobe PDF',
            '.zip': 'Архив ZIP',
            '.rar': 'Архив RAR',
            '.7z': 'Архив 7-Zip',
            '.iso': 'Образ ISO',
            '.img': 'Образ диска',
            '.mp3': 'Аудиофайл MP3',
            '.mp4': 'Видеофайл MP4',
            '.jpg': 'Изображение JPEG',
            '.png': 'Изображение PNG',
            '.bmp': 'Изображение BMP',
            '.xml': 'XML-файл',
            '.html': 'HTML-файл',
            '.js': 'JavaScript файл',
            '.css': 'Файл CSS',
            '.json': 'Файл JSON',
            '.db': 'Файл базы данных',
            '.ini': 'Файл конфигурации',
            '.cfg': 'Файл конфигурации',
            '.conf': 'Файл конфигурации'
        }
        
        # Если есть в словаре - возвращаем из словаря
        if file_ext in file_type_map:
            return file_type_map[file_ext]
        # Если есть mime-тип, используем его
        elif mime_type:
            return f"Тип файла: {mime_type}"
        # Иначе просто возвращаем расширение
        else:
            return f"Файл{file_ext}"
    except Exception as e:
        print(f"Ошибка при определении типа файла: {e}")
        return "Неизвестный тип файла"

def get_text_file_preview(file_path, max_lines=3, max_line_length=60):
    """Извлекает первые строки текстового файла для предпросмотра"""
    try:
        preview_lines = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                # Обрезаем слишком длинные строки
                trimmed_line = line.strip()
                if len(trimmed_line) > max_line_length:
                    trimmed_line = trimmed_line[:max_line_length] + "..."
                if trimmed_line:  # Добавляем только непустые строки
                    preview_lines.append(trimmed_line)
        
        if preview_lines:
            return ["Содержимое:"] + preview_lines
        return []
    except Exception as e:
        print(f"Ошибка при чтении текстового файла: {e}")
        return []

def format_file_info(file_path):
    """Форматирует информацию о файле в виде текста, с улучшенной обработкой ошибок"""
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return f"Файл не найден: {file_path}"
            
        # Получаем базовую информацию о файле
        file_name = os.path.basename(file_path)
        file_size_bytes = os.path.getsize(file_path)
        
        # Форматируем размер файла в удобочитаемом виде
        if file_size_bytes < 1024:
            file_size_str = f"{file_size_bytes} байт"
        elif file_size_bytes < 1024 * 1024:
            file_size_str = f"{file_size_bytes / 1024:.1f} КБ"
        else:
            file_size_str = f"{file_size_bytes / (1024 * 1024):.2f} МБ"
        
        # Получаем информацию о времени создания/модификации файла
        try:
            file_mtime = os.path.getmtime(file_path)
            modify_time = datetime.datetime.fromtimestamp(file_mtime).strftime('%d.%m.%Y %H:%M:%S')
        except Exception:
            modify_time = "Неизвестно"
        
        # Определяем тип файла
        file_type = get_file_type_info(file_path)
        
        # Начинаем формировать результат с базовой информацией (всегда доступно для любого типа файла)
        result = [
            f"Имя файла: {file_name}",
            f"Размер: {file_size_str}",
            f"Тип: {file_type}",
            f"Изменён: {modify_time}"
        ]
        
        # Определяем дополнительную информацию в зависимости от типа файла
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Список типов файлов, у которых можно извлечь метаданные
        extractable_metadata_formats = {
            # PE исполняемые файлы (используем PE)
            '.exe': 'pe',
            '.dll': 'pe',
            '.ocx': 'pe',
            '.sys': 'pe',
            
            # Скриптовые файлы (извлекаем комментарии)
            '.py': 'script',
            '.ps1': 'script',
            '.bat': 'script', 
            '.cmd': 'script',
            '.sh': 'script',
            
            # Текстовые файлы (показываем предпросмотр)
            '.txt': 'text',
            '.log': 'text',
            '.md': 'text',
            '.csv': 'text',
            '.ini': 'text',
            '.cfg': 'text',
            '.conf': 'text'
        }
        
        # Проверяем, поддерживается ли извлечение информации для этого типа файла
        if file_ext in extractable_metadata_formats:
            metadata_type = extractable_metadata_formats[file_ext]
            
            # PE файлы (exe, dll, ocx, sys)
            if metadata_type == 'pe':
                try:
                    # Пытаемся получить информацию из PE файла
                    pe_info = safe_pe_info_extraction(file_path)
                    if pe_info:
                        result.extend(pe_info)
                except Exception as e:
                    print(f"Не удалось прочитать информацию из PE файла: {e}")
            
            # Файлы скриптов - извлекаем комментарии
            elif metadata_type == 'script':
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_lines = [line.strip() for line in f.readlines()[:10] if line.strip()]
                        
                        # Ищем строки с комментариями, которые могут содержать описание
                        comment_chars = ['#', '//', '--', '/*', '\'', '"""', 'REM']
                        description_lines = []
                        
                        for line in first_lines:
                            for char in comment_chars:
                                if line.lstrip().startswith(char):
                                    description_lines.append(line)
                                    break
                        
                        if description_lines:
                            result.append("Описание из файла:")
                            for idx, line in enumerate(description_lines[:3]):  # Добавляем до 3 строк комментариев
                                result.append(f"  {line}")
                except Exception as e:
                    print(f"Не удалось прочитать содержимое скрипта: {e}")
            
            # Текстовые файлы - добавляем предпросмотр
            elif metadata_type == 'text':
                # Для текстовых файлов показываем первые строки
                if file_size_bytes < 1024 * 10:  # Только для файлов меньше 10КБ
                    preview = get_text_file_preview(file_path)
                    if preview:
                        result.extend(preview)
                else:
                    result.append("Файл слишком большой для предпросмотра")
        
        # Возвращаем отформатированный текст
        return "\n".join(result)
    
    except Exception as e:
        # В случае любой ошибки возвращаем базовую информацию о файле
        try:
            return f"Имя файла: {os.path.basename(file_path)}\nРазмер: Н/Д\nОшибка: {str(e)}"
        except:
            return f"Ошибка при получении информации о файле"
        
def get_file_description(file_path, base_directory=None):
    """Получает информацию о файле с полным путем к нему"""
    # Используем полный путь или относительный в зависимости от переданной базовой директории
    full_path = file_path
    if not os.path.isabs(file_path) and base_directory:
        full_path = os.path.join(base_directory, file_path)
    
    # Просто возвращаем информацию о файле без добавления заголовка
    return format_file_info(full_path)