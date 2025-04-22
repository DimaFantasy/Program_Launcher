import os
import pefile

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

def format_file_info(file_path):
    """Форматирует информацию о файле в виде текста"""
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return f"Файл не найден: {file_path}"
            
        # Получаем базовую информацию о файле
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # размер в МБ
        
        # Проверяем, является ли файл исполняемым (PE)
        is_executable = file_path.lower().endswith(('.exe', '.dll', '.ocx', '.sys'))
        
        result = []
        result.append(f"Имя файла: {os.path.basename(file_path)}")
        result.append(f"Размер: {file_size:.2f} МБ")
        
        # Если это исполняемый файл, пытаемся получить дополнительную информацию
        if is_executable:
            try:
                version_info = extract_version_info(file_path)
                if version_info:
                    # Определяем важные поля для отображения
                    important_fields = [
                        'FileDescription', 'ProductName', 'CompanyName', 
                        'FileVersion', 'ProductVersion', 'LegalCopyright'
                    ]
                    
                    for field in important_fields:
                        if field in version_info and version_info[field]:
                            result.append(f"{field}: {version_info[field]}")
            except Exception as e:
                print(f"Ошибка при получении информации о версии: {e}")
        
        # Возвращаем отформатированный текст
        return "\n".join(result)
    
    except Exception as e:
        return f"Ошибка при получении информации о файле: {e}"
        
def get_file_description(file_path, base_directory=None):
    """Получает информацию о файле с полным путем к нему"""
    # Используем полный путь или относительный в зависимости от переданной базовой директории
    full_path = file_path
    if not os.path.isabs(file_path) and base_directory:
        full_path = os.path.join(base_directory, file_path)
    
    # Просто возвращаем информацию о файле без добавления заголовка
    return format_file_info(full_path)